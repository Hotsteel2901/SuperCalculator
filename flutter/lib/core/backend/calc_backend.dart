import 'dart:math' as math;

class CalcEvaluation {
  const CalcEvaluation({
    required this.value,
    required this.backend,
    this.error,
  });

  const CalcEvaluation.failure({required this.backend, required String message})
    : value = null,
      error = message;

  final double? value;
  final String backend;
  final String? error;

  bool get isSuccess => value != null && error == null;
}

abstract interface class CalcBackend {
  String get name;

  Future<CalcEvaluation> evaluate(String expression, double x);

  Future<List<double?>> evaluateArray(String expression, List<double> xs);

  void dispose();
}

class DartCalcBackend implements CalcBackend {
  const DartCalcBackend({this.displayName = 'Dart fallback'});

  final String displayName;

  @override
  String get name => displayName;

  @override
  Future<CalcEvaluation> evaluate(String expression, double x) async {
    try {
      final value = _ExpressionParser(expression, x: x).parse();
      if (!value.isFinite) {
        return CalcEvaluation.failure(
          backend: name,
          message: 'The expression produced a non-finite value.',
        );
      }
      return CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    } catch (_) {
      return CalcEvaluation.failure(
        backend: name,
        message: 'The expression could not be evaluated.',
      );
    }
  }

  @override
  Future<List<double?>> evaluateArray(
    String expression,
    List<double> xs,
  ) async {
    final values = <double?>[];
    for (final x in xs) {
      final result = await evaluate(expression, x);
      values.add(result.value);
    }
    return values;
  }

  @override
  void dispose() {}
}

/// Small, deliberately bounded fallback parser used by the app shell and Web
/// before the native/Wasm artifact is present. The C parser remains the source
/// of truth for the full expression language.
class _ExpressionParser {
  _ExpressionParser(this.source, {required this.x});

  final String source;
  final double x;
  int position = 0;

  double parse() {
    final value = _parseExpression();
    _skipSpaces();
    if (position != source.length) {
      throw FormatException('Unexpected input at position $position.');
    }
    return value;
  }

  double _parseExpression() {
    var value = _parseTerm();
    while (true) {
      _skipSpaces();
      if (_match('+')) {
        value += _parseTerm();
      } else if (_match('-')) {
        value -= _parseTerm();
      } else {
        return value;
      }
    }
  }

  double _parseTerm() {
    var value = _parsePower();
    while (true) {
      _skipSpaces();
      if (_match('*')) {
        value *= _parsePower();
      } else if (_match('/')) {
        final divisor = _parsePower();
        if (divisor.abs() < 1e-15) {
          throw const FormatException('Division by zero.');
        }
        value /= divisor;
      } else if (_match('%') || _matchWord('mod')) {
        final divisor = _parsePower();
        if (divisor.abs() < 1e-15) {
          throw const FormatException('Modulo by zero.');
        }
        value %= divisor;
      } else {
        return value;
      }
    }
  }

  double _parsePower() {
    final base = _parseUnary();
    _skipSpaces();
    if (_match('^')) {
      return math.pow(base, _parsePower()).toDouble();
    }
    return base;
  }

  double _parseUnary() {
    _skipSpaces();
    if (_match('+')) return _parseUnary();
    if (_match('-')) return -_parseUnary();
    return _parsePostfix();
  }

  double _parsePostfix() {
    var value = _parsePrimary();
    while (true) {
      _skipSpaces();
      if (!_match('!')) return value;
      if (value < 0 || value.floorToDouble() != value || value > 170) {
        throw const FormatException(
          'Factorial requires an integer from 0 to 170.',
        );
      }
      var result = 1.0;
      for (var index = 2; index <= value.toInt(); index++) {
        result *= index;
      }
      value = result;
    }
  }

  double _parsePrimary() {
    _skipSpaces();
    if (_match('(')) {
      final value = _parseExpression();
      _expect(')');
      return value;
    }

    if (position < source.length && _isDigit(source[position])) {
      return _parseNumber();
    }

    final identifier = _parseIdentifier();
    if (identifier == null) {
      throw FormatException(
        'Expected a number, variable, or function at position $position.',
      );
    }
    if (identifier == 'x') return x;
    if (identifier == 'pi') return math.pi;
    if (identifier == 'e') return math.e;

    _skipSpaces();
    _expect('(');
    final argument = _parseExpression();
    _expect(')');
    return switch (identifier) {
      'sin' => math.sin(argument),
      'cos' => math.cos(argument),
      'tan' => math.tan(argument),
      'log' => math.log(argument) / math.ln10,
      'ln' => math.log(argument),
      'exp' => math.exp(argument),
      'sqrt' => math.sqrt(argument),
      'abs' => argument.abs(),
      'floor' => argument.floorToDouble(),
      'ceil' => argument.ceilToDouble(),
      _ => throw FormatException('Unknown function $identifier.'),
    };
  }

  double _parseNumber() {
    final start = position;
    while (position < source.length && _isDigit(source[position])) {
      position++;
    }
    if (position < source.length && source[position] == '.') {
      position++;
      while (position < source.length && _isDigit(source[position])) {
        position++;
      }
    }
    if (position < source.length &&
        (source[position] == 'e' || source[position] == 'E')) {
      position++;
      if (position < source.length &&
          (source[position] == '+' || source[position] == '-')) {
        position++;
      }
      while (position < source.length && _isDigit(source[position])) {
        position++;
      }
    }
    return double.parse(source.substring(start, position));
  }

  String? _parseIdentifier() {
    _skipSpaces();
    if (position >= source.length || !_isIdentifierStart(source[position])) {
      return null;
    }
    final start = position++;
    while (position < source.length && _isIdentifierPart(source[position])) {
      position++;
    }
    return source.substring(start, position).toLowerCase();
  }

  bool _match(String character) {
    if (source.startsWith(character, position)) {
      position += character.length;
      return true;
    }
    return false;
  }

  bool _matchWord(String word) {
    final before = position;
    _skipSpaces();
    if (source.startsWith(word, position)) {
      final end = position + word.length;
      if (end == source.length || !_isIdentifierPart(source[end])) {
        position = end;
        return true;
      }
    }
    position = before;
    return false;
  }

  void _expect(String character) {
    _skipSpaces();
    if (!_match(character)) {
      throw FormatException('Expected "$character" at position $position.');
    }
  }

  void _skipSpaces() {
    while (position < source.length && source[position].trim().isEmpty) {
      position++;
    }
  }

  bool _isDigit(String character) =>
      character.codeUnitAt(0) >= 48 && character.codeUnitAt(0) <= 57;
  bool _isIdentifierStart(String character) =>
      (character.codeUnitAt(0) >= 65 && character.codeUnitAt(0) <= 90) ||
      (character.codeUnitAt(0) >= 97 && character.codeUnitAt(0) <= 122) ||
      character == '_';
  bool _isIdentifierPart(String character) =>
      _isIdentifierStart(character) || _isDigit(character);
}
