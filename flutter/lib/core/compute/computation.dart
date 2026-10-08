import 'dart:math' as math;

import 'calculation_models.dart';

/// A small compiled expression engine used by Web and as the deterministic
/// fallback when a native library is not available.
///
/// The parser builds an AST once and reuses it for every sample. This avoids
/// reparsing a plot expression hundreds or thousands of times and keeps the
/// fallback close to the native array-evaluation path.
class ExpressionEngine {
  const ExpressionEngine._();

  static CompiledExpression compile(String source) {
    final parser = _ExpressionCompiler(source);
    final root = parser.parse();
    return CompiledExpression._(source, root);
  }

  /// Compiles an expression with user-defined one-argument functions.
  /// Definitions use the same syntax as the main expression, for example
  /// `{ "f": "x^2 + 1", "g": "sin(x)" }`.
  static CompiledExpression compileWithFunctions(
    String source,
    Map<String, String> definitions,
  ) {
    final parser = _ExpressionCompiler(source, definitions: definitions);
    final root = parser.parse();
    return CompiledExpression._(source, root);
  }

  static double evaluate(String source, {double x = 0, double y = 0}) {
    return compile(source).evaluate(x: x, y: y);
  }
}

class CompiledExpression {
  const CompiledExpression._(this.source, this._root);

  final String source;
  final _ExpressionNode _root;

  double evaluate({double x = 0, double y = 0}) => _root.evaluate(x, y);

  List<double?> sample(Iterable<double> xs, {double y = 0}) {
    return xs
        .map((x) {
          final value = evaluate(x: x, y: y);
          return value.isFinite ? value : null;
        })
        .toList(growable: false);
  }
}

abstract class _ExpressionNode {
  const _ExpressionNode();

  double evaluate(double x, double y);
}

class _NumberNode extends _ExpressionNode {
  const _NumberNode(this.value);

  final double value;

  @override
  double evaluate(double x, double y) => value;
}

class _VariableNode extends _ExpressionNode {
  const _VariableNode(this.name);

  final String name;

  @override
  double evaluate(double x, double y) => name == 'x' ? x : y;
}

class _UnaryNode extends _ExpressionNode {
  const _UnaryNode(this.operator, this.operand);

  final String operator;
  final _ExpressionNode operand;

  @override
  double evaluate(double x, double y) {
    final value = operand.evaluate(x, y);
    return operator == '-' ? -value : value;
  }
}

class _BinaryNode extends _ExpressionNode {
  const _BinaryNode(this.operator, this.left, this.right);

  final String operator;
  final _ExpressionNode left;
  final _ExpressionNode right;

  @override
  double evaluate(double x, double y) {
    final a = left.evaluate(x, y);
    final b = right.evaluate(x, y);
    switch (operator) {
      case '+':
        return a + b;
      case '-':
        return a - b;
      case '*':
        return a * b;
      case '/':
        return b.abs() < 1e-15 ? double.nan : a / b;
      case '%':
        return b.abs() < 1e-15 ? double.nan : a % b;
      case '^':
        if (a < 0 && b != b.roundToDouble()) {
          return double.nan;
        }
        if (a == 0 && b < 0) {
          return double.nan;
        }
        return math.pow(a, b).toDouble();
      default:
        return double.nan;
    }
  }
}

class _FactorialNode extends _ExpressionNode {
  const _FactorialNode(this.operand);

  final _ExpressionNode operand;

  @override
  double evaluate(double x, double y) {
    final value = operand.evaluate(x, y);
    if (value < 0 || value > 170 || value != value.floorToDouble()) {
      return double.nan;
    }
    var result = 1.0;
    for (var i = 2; i <= value.toInt(); i++) {
      result *= i;
    }
    return result;
  }
}

class _CustomFunctionNode extends _ExpressionNode {
  const _CustomFunctionNode(this.name, this.argument, this.body);

  final String name;
  final _ExpressionNode argument;
  final _ExpressionNode body;

  @override
  double evaluate(double x, double y) {
    final value = argument.evaluate(x, y);
    return value.isFinite ? body.evaluate(value, y) : double.nan;
  }
}

class _FunctionNode extends _ExpressionNode {
  const _FunctionNode(this.name, this.argument);

  final String name;
  final _ExpressionNode argument;

  @override
  double evaluate(double x, double y) {
    final value = argument.evaluate(x, y);
    switch (name) {
      case 'sin':
        return math.sin(value);
      case 'cos':
        return math.cos(value);
      case 'tan':
        return math.tan(value);
      case 'log':
        return value > 0 ? math.log(value) / math.ln10 : double.nan;
      case 'ln':
        return value > 0 ? math.log(value) : double.nan;
      case 'sqrt':
        return value >= 0 ? math.sqrt(value) : double.nan;
      case 'exp':
        return math.exp(value);
      case 'abs':
        return value.abs();
      case 'floor':
        return value.floorToDouble();
      case 'ceil':
        return value.ceilToDouble();
      case 'asin':
        return math.asin(value);
      case 'acos':
        return math.acos(value);
      case 'atan':
        return math.atan(value);
      case 'sinh':
        return (math.exp(value) - math.exp(-value)) / 2;
      case 'cosh':
        return (math.exp(value) + math.exp(-value)) / 2;
      case 'tanh':
        final positive = math.exp(2 * value);
        return (positive - 1) / (positive + 1);
      default:
        return double.nan;
    }
  }
}

class _ExpressionCompiler {
  _ExpressionCompiler(
    this.source, {
    this.definitions = const <String, String>{},
    Set<String>? compilingDefinitions,
  }) : _compilingDefinitions = <String>{...?compilingDefinitions};

  final String source;
  final Map<String, String> definitions;
  final Set<String> _compilingDefinitions;
  int position = 0;

  _ExpressionNode parse() {
    final node = _parseAdditive();
    _skipSpaces();
    if (position != source.length) {
      throw FormatException('Unexpected input at position $position.');
    }
    return node;
  }

  _ExpressionNode _parseAdditive() {
    var node = _parseMultiplicative();
    while (true) {
      _skipSpaces();
      if (_match('+')) {
        node = _BinaryNode('+', node, _parseMultiplicative());
      } else if (_match('-')) {
        node = _BinaryNode('-', node, _parseMultiplicative());
      } else {
        return node;
      }
    }
  }

  _ExpressionNode _parseMultiplicative() {
    var node = _parsePower();
    while (true) {
      _skipSpaces();
      if (_match('*')) {
        node = _BinaryNode('*', node, _parsePower());
      } else if (_match('/')) {
        node = _BinaryNode('/', node, _parsePower());
      } else if (_match('%') || _matchWord('mod')) {
        node = _BinaryNode('%', node, _parsePower());
      } else {
        return node;
      }
    }
  }

  _ExpressionNode _parsePower() {
    final node = _parseUnary();
    _skipSpaces();
    if (_match('^')) {
      return _BinaryNode('^', node, _parsePower());
    }
    return node;
  }

  _ExpressionNode _parseUnary() {
    _skipSpaces();
    if (_match('+')) {
      return _parseUnary();
    }
    if (_match('-')) {
      return _UnaryNode('-', _parseUnary());
    }
    return _parsePostfix();
  }

  _ExpressionNode _parsePostfix() {
    var node = _parsePrimary();
    while (true) {
      _skipSpaces();
      if (!_match('!')) {
        return node;
      }
      node = _FactorialNode(node);
    }
  }

  _ExpressionNode _parsePrimary() {
    _skipSpaces();
    if (_match('(')) {
      final node = _parseAdditive();
      _expect(')');
      return node;
    }
    if (position < source.length &&
        (_isDigit(source[position]) ||
            (source[position] == '.' &&
                position + 1 < source.length &&
                _isDigit(source[position + 1])))) {
      return _NumberNode(_parseNumber());
    }

    final identifier = _parseIdentifier();
    if (identifier == null) {
      throw FormatException('Expected a number at position $position.');
    }
    switch (identifier) {
      case 'x':
      case 'y':
        return _VariableNode(identifier);
      case 'pi':
        return const _NumberNode(math.pi);
      case 'e':
        return const _NumberNode(math.e);
    }

    _skipSpaces();
    _expect('(');
    final argument = _parseAdditive();
    _expect(')');
    final customBody = definitions[identifier];
    if (customBody != null) {
      if (!_compilingDefinitions.add(identifier)) {
        throw FormatException('Recursive custom function $identifier.');
      }
      try {
        final body = _ExpressionCompiler(
          customBody,
          definitions: definitions,
          compilingDefinitions: _compilingDefinitions,
        ).parse();
        return _CustomFunctionNode(identifier, argument, body);
      } finally {
        _compilingDefinitions.remove(identifier);
      }
    }
    const functions = <String>{
      'sin',
      'cos',
      'tan',
      'log',
      'ln',
      'sqrt',
      'exp',
      'abs',
      'floor',
      'ceil',
      'asin',
      'acos',
      'atan',
      'sinh',
      'cosh',
      'tanh',
    };
    if (!functions.contains(identifier)) {
      throw FormatException('Unknown function $identifier.');
    }
    return _FunctionNode(identifier, argument);
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
    try {
      return double.parse(source.substring(start, position));
    } on FormatException {
      throw FormatException('Invalid number at position $start.');
    }
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

  bool _match(String value) {
    if (source.startsWith(value, position)) {
      position += value.length;
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

  void _expect(String value) {
    _skipSpaces();
    if (!_match(value)) {
      throw FormatException('Expected "$value" at position $position.');
    }
  }

  void _skipSpaces() {
    while (position < source.length && source[position].trim().isEmpty) {
      position++;
    }
  }

  bool _isDigit(String value) {
    final code = value.codeUnitAt(0);
    return code >= 48 && code <= 57;
  }

  bool _isIdentifierStart(String value) {
    final code = value.codeUnitAt(0);
    return (code >= 65 && code <= 90) ||
        (code >= 97 && code <= 122) ||
        value == '_';
  }

  bool _isIdentifierPart(String value) =>
      _isIdentifierStart(value) || _isDigit(value);
}

class DartComputation {
  const DartComputation._();

  static double evaluate(String expression, double x, [double y = 0]) {
    return ExpressionEngine.compile(expression).evaluate(x: x, y: y);
  }

  static List<double?> evaluateArray(String expression, List<double> xs) {
    return ExpressionEngine.compile(expression).sample(xs);
  }

  static List<Map<String, double?>> functionTable(
    String expression,
    double start,
    double end,
    int rows,
  ) {
    if (!start.isFinite || !end.isFinite || rows < 2 || start > end) {
      return const <Map<String, double?>>[];
    }
    final function = ExpressionEngine.compile(expression);
    return List<Map<String, double?>>.generate(rows, (index) {
      final x = start + (end - start) * index / (rows - 1);
      final value = function.evaluate(x: x);
      return <String, double?>{'x': x, 'value': value.isFinite ? value : null};
    }, growable: false);
  }

  static String functionTableCsv(
    String expression,
    double start,
    double end,
    int rows,
  ) {
    final table = functionTable(expression, start, end, rows);
    if (table.isEmpty) return '';
    final buffer = StringBuffer('x,f(x)\n');
    for (final row in table) {
      buffer
        ..write(row['x']?.toStringAsPrecision(12) ?? '')
        ..write(',')
        ..writeln(row['value']?.toStringAsPrecision(12) ?? '');
    }
    return buffer.toString().trimRight();
  }

  static double evaluateCustom(
    String expression,
    Map<String, String> definitions, {
    double x = 0,
    double y = 0,
  }) {
    return ExpressionEngine.compileWithFunctions(
      expression,
      definitions,
    ).evaluate(x: x, y: y);
  }

  // ---------- Complex arithmetic ----------

  static ComplexValue complexPower(ComplexValue value, ComplexValue exponent) {
    if (value.real == 0 && value.imaginary == 0) {
      if (exponent.real > 0 && exponent.imaginary == 0) {
        return const ComplexValue(0, 0);
      }
      throw const FormatException('Zero cannot be raised to this power.');
    }
    final logarithm = complexLog(value);
    return complexExp(
      ComplexValue(
        exponent.real * logarithm.real -
            exponent.imaginary * logarithm.imaginary,
        exponent.real * logarithm.imaginary +
            exponent.imaginary * logarithm.real,
      ),
    );
  }

  static ComplexValue complexExp(ComplexValue value) {
    final scale = math.exp(value.real);
    return ComplexValue(
      scale * math.cos(value.imaginary),
      scale * math.sin(value.imaginary),
    );
  }

  static ComplexValue complexLog(ComplexValue value) {
    if (value.real == 0 && value.imaginary == 0) {
      throw const FormatException('Logarithm of zero is undefined.');
    }
    return ComplexValue(math.log(value.magnitude), value.phase);
  }

  static ComplexValue complexSqrt(ComplexValue value) {
    final magnitude = value.magnitude;
    final real = math.sqrt((magnitude + value.real) / 2);
    final imaginary = math.sqrt(math.max(0, (magnitude - value.real) / 2));
    return ComplexValue(real, value.imaginary < 0 ? -imaginary : imaginary);
  }

  static ComplexValue complexSin(ComplexValue value) => ComplexValue(
    math.sin(value.real) * _cosh(value.imaginary),
    math.cos(value.real) * _sinh(value.imaginary),
  );

  static ComplexValue complexCos(ComplexValue value) => ComplexValue(
    math.cos(value.real) * _cosh(value.imaginary),
    -math.sin(value.real) * _sinh(value.imaginary),
  );

  static double _sinh(double value) => (math.exp(value) - math.exp(-value)) / 2;

  static double _cosh(double value) => (math.exp(value) + math.exp(-value)) / 2;

  static ComplexValue complexTan(ComplexValue value) =>
      complexSin(value) / complexCos(value);

  // ---------- Integer and bitwise tools ----------

  static BigInt gcd(BigInt a, BigInt b) {
    var left = a.abs();
    var right = b.abs();
    while (right != BigInt.zero) {
      final remainder = left % right;
      left = right;
      right = remainder;
    }
    return left;
  }

  static BigInt lcm(BigInt a, BigInt b) {
    if (a == BigInt.zero || b == BigInt.zero) return BigInt.zero;
    return (a ~/ gcd(a, b) * b).abs();
  }

  static bool isPrime(BigInt value) {
    if (value < BigInt.from(2)) return false;
    if (value == BigInt.from(2)) return true;
    if (value.isEven) return false;
    for (
      var divisor = BigInt.from(3);
      divisor * divisor <= value;
      divisor += BigInt.two
    ) {
      if (value % divisor == BigInt.zero) return false;
    }
    return true;
  }

  static Map<BigInt, int> factorInteger(BigInt value) {
    if (value == BigInt.zero) {
      throw const FormatException('Zero has no finite prime factorization.');
    }
    var remaining = value.abs();
    final factors = <BigInt, int>{};
    var divisor = BigInt.two;
    while (divisor * divisor <= remaining) {
      while (remaining % divisor == BigInt.zero) {
        factors[divisor] = (factors[divisor] ?? 0) + 1;
        remaining ~/= divisor;
      }
      divisor = divisor == BigInt.two ? BigInt.from(3) : divisor + BigInt.two;
    }
    if (remaining > BigInt.one) {
      factors[remaining] = (factors[remaining] ?? 0) + 1;
    }
    return factors;
  }

  static BigInt modPow(BigInt base, BigInt exponent, BigInt modulus) {
    if (modulus <= BigInt.zero || exponent < BigInt.zero) {
      throw const FormatException(
        'Modulus must be positive and exponent non-negative.',
      );
    }
    var result = BigInt.one % modulus;
    var factor = base % modulus;
    var power = exponent;
    while (power > BigInt.zero) {
      if (power.isOdd) result = result * factor % modulus;
      factor = factor * factor % modulus;
      power >>= 1;
    }
    return result;
  }

  static BigInt eulerTotient(BigInt value) {
    if (value <= BigInt.zero) {
      throw const FormatException('Totient requires a positive integer.');
    }
    var result = value;
    for (final prime in factorInteger(value).keys) {
      result = result ~/ prime * (prime - BigInt.one);
    }
    return result;
  }

  static BigInt fibonacci(int index) {
    if (index < 0 || index > 100000) {
      throw const FormatException(
        'Fibonacci index must be between 0 and 100000.',
      );
    }
    var a = BigInt.zero;
    var b = BigInt.one;
    for (var i = 0; i < index; i++) {
      final next = a + b;
      a = b;
      b = next;
    }
    return a;
  }

  static int bitwise(String operation, int left, int right, int width) {
    if (![8, 16, 32].contains(width)) {
      throw const FormatException('Bit width must be 8, 16 or 32.');
    }
    final mask = width == 32 ? 0xffffffff : (1 << width) - 1;
    final a = left & mask;
    final b = right & mask;
    final value = switch (operation) {
      'and' => a & b,
      'or' => a | b,
      'xor' => a ^ b,
      'not' => ~a,
      'shl' => a << (right & (width - 1)),
      'shr' => a >> (right & (width - 1)),
      _ => throw const FormatException('Unknown bitwise operation.'),
    };
    return value & mask;
  }

  static double? derivative(
    String expression,
    double x, {
    double? step,
    bool second = false,
  }) {
    final function = ExpressionEngine.compile(expression);
    final h = step ?? 1e-6 * (x.abs() + 1);
    if (h == 0 || !h.isFinite) {
      return null;
    }
    final center = function.evaluate(x: x);
    final plus = function.evaluate(x: x + h);
    final minus = function.evaluate(x: x - h);
    if (![center, plus, minus].every((value) => value.isFinite)) {
      return null;
    }
    return second
        ? (plus - (2 * center) + minus) / (h * h)
        : (plus - minus) / (2 * h);
  }

  static double? integrate(
    String expression,
    double a,
    double b, {
    double tolerance = 1e-8,
  }) {
    if (!a.isFinite || !b.isFinite || tolerance <= 0) {
      return null;
    }
    if (a == b) {
      return 0;
    }
    if (a > b) {
      return null;
    }
    final function = ExpressionEngine.compile(expression);
    double value(double x) => function.evaluate(x: x);
    final fa = value(a);
    final fb = value(b);
    final middle = value((a + b) / 2);
    if (![fa, fb, middle].every((item) => item.isFinite)) {
      return null;
    }
    final whole = _simpson(a, b, fa, middle, fb);
    return _adaptiveSimpson(value, a, b, tolerance, whole, fa, middle, fb, 18);
  }

  static double? limit(
    String expression,
    double point, {
    double tolerance = 1e-8,
    int maxLevel = 10,
    String side = 'two-sided',
  }) {
    if (!point.isFinite || tolerance <= 0 || maxLevel < 1) return null;
    final function = ExpressionEngine.compile(expression);
    double? oneSided(double direction) {
      final level = maxLevel.clamp(1, 16).toInt();
      final table = List<List<double>>.generate(
        level,
        (_) => List<double>.filled(level, double.nan),
      );
      for (var index = 0; index < level; index++) {
        final h = .1 * math.pow(.5, index).toDouble();
        final value = function.evaluate(x: point + direction * h);
        if (!value.isFinite) return null;
        table[index][0] = value;
      }
      for (var order = 1; order < level; order++) {
        for (var index = 0; index < level - order; index++) {
          final factor = math.pow(2, order).toDouble();
          table[index][order] =
              (table[index + 1][order - 1] * factor - table[index][order - 1]) /
              (factor - 1);
        }
      }
      return table[0][level - 1];
    }

    if (side == 'left') return oneSided(-1);
    if (side == 'right') return oneSided(1);
    final left = oneSided(-1);
    final right = oneSided(1);
    if (left == null || right == null || (left - right).abs() > tolerance) {
      return null;
    }
    return (left + right) / 2;
  }

  static double? nthDerivative(
    String expression,
    double x,
    int order, {
    double step = 1e-4,
  }) {
    if (order < 0 || order > 12 || !step.isFinite || step <= 0) return null;
    final function = ExpressionEngine.compile(expression);
    double? difference(double at, int remaining) {
      if (remaining == 0) {
        final value = function.evaluate(x: at);
        return value.isFinite ? value : null;
      }
      final left = difference(at - step, remaining - 1);
      final right = difference(at + step, remaining - 1);
      if (left == null || right == null) return null;
      return (right - left) / (2 * step);
    }

    return difference(x, order);
  }

  static List<double?>? taylorCoefficients(
    String expression,
    double point,
    int order,
  ) {
    if (order < 0 || order > 12) return null;
    final function = ExpressionEngine.compile(expression);
    final coefficients = <double?>[];
    var factorial = 1.0;
    for (var index = 0; index <= order; index++) {
      if (index > 0) factorial *= index;
      final derivative = _nthDerivativeCompiled(function, point, index, 1e-4);
      coefficients.add(derivative == null ? null : derivative / factorial);
    }
    return coefficients;
  }

  static double? taylorEvaluate(
    String expression,
    double point,
    double x,
    int order,
  ) {
    final coefficients = taylorCoefficients(expression, point, order);
    if (coefficients == null) return null;
    final delta = x - point;
    var power = 1.0;
    var result = 0.0;
    for (final coefficient in coefficients) {
      if (coefficient == null) return null;
      result += coefficient * power;
      power *= delta;
    }
    return result;
  }

  static double? findExtremum(
    String expression,
    double start,
    double end, {
    bool minimum = true,
    double tolerance = 1e-8,
    int maxIterations = 100,
  }) {
    if (!start.isFinite || !end.isFinite || start >= end || tolerance <= 0) {
      return null;
    }
    final function = ExpressionEngine.compile(expression);
    const ratio = .6180339887498949;
    var left = start;
    var right = end;
    var first = right - ratio * (right - left);
    var second = left + ratio * (right - left);
    var firstValue = function.evaluate(x: first);
    var secondValue = function.evaluate(x: second);
    if (!firstValue.isFinite || !secondValue.isFinite) return null;
    bool better(double a, double b) => minimum ? a < b : a > b;
    for (var iteration = 0; iteration < maxIterations; iteration++) {
      if ((right - left).abs() <= tolerance) break;
      if (better(firstValue, secondValue)) {
        right = second;
        second = first;
        secondValue = firstValue;
        first = right - ratio * (right - left);
        firstValue = function.evaluate(x: first);
      } else {
        left = first;
        first = second;
        firstValue = secondValue;
        second = left + ratio * (right - left);
        secondValue = function.evaluate(x: second);
      }
      if (!firstValue.isFinite || !secondValue.isFinite) return null;
    }
    return (left + right) / 2;
  }

  static double? arcLength(
    String expression,
    double start,
    double end, {
    int samples = 2000,
  }) {
    if (start == end) return 0;
    if (start > end || samples < 1) return null;
    final function = ExpressionEngine.compile(expression);
    final step = (end - start) / samples;
    var length = 0.0;
    var previous = function.evaluate(x: start);
    if (!previous.isFinite) return null;
    for (var index = 1; index <= samples; index++) {
      final current = function.evaluate(x: start + index * step);
      if (!current.isFinite) return null;
      length += math.sqrt(
        step * step + (current - previous) * (current - previous),
      );
      previous = current;
    }
    return length;
  }

  static double? areaBetweenCurves(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    double tolerance = 1e-8,
  }) {
    if (start > end || tolerance <= 0) return null;
    final f = ExpressionEngine.compile(expressionF);
    final g = ExpressionEngine.compile(expressionG);
    double value(double x) {
      final left = f.evaluate(x: x);
      final right = g.evaluate(x: x);
      return left.isFinite && right.isFinite
          ? (left - right).abs()
          : double.nan;
    }

    if (start == end) return 0;
    final fa = value(start);
    final fb = value(end);
    final middle = value((start + end) / 2);
    if (![fa, fb, middle].every((item) => item.isFinite)) return null;
    return _adaptiveSimpson(
      value,
      start,
      end,
      tolerance,
      _simpson(start, end, fa, middle, fb),
      fa,
      middle,
      fb,
      18,
    );
  }

  static double? volumeDisk(
    String expression,
    double start,
    double end, {
    double tolerance = 1e-8,
  }) {
    final value = integrate(
      'pi * ($expression)^2',
      start,
      end,
      tolerance: tolerance,
    );
    return value;
  }

  static double? volumeWasher(
    String outerExpression,
    String innerExpression,
    double start,
    double end, {
    double tolerance = 1e-8,
  }) {
    final outer = ExpressionEngine.compile(outerExpression);
    final inner = ExpressionEngine.compile(innerExpression);
    if (start > end || tolerance <= 0) return null;
    double value(double x) {
      final a = outer.evaluate(x: x);
      final b = inner.evaluate(x: x);
      return a.isFinite && b.isFinite
          ? math.pi * (a * a - b * b).abs()
          : double.nan;
    }

    return _integrateFunction(value, start, end, tolerance);
  }

  static double? volumeShell(
    String expression,
    double start,
    double end, {
    double tolerance = 1e-8,
  }) {
    final function = ExpressionEngine.compile(expression);
    double value(double x) {
      final y = function.evaluate(x: x);
      return y.isFinite ? 2 * math.pi * x.abs() * y.abs() : double.nan;
    }

    return _integrateFunction(value, start, end, tolerance);
  }

  static List<Map<String, double>> evaluateParametric(
    String expressionX,
    String expressionY, {
    double start = 0,
    double end = 2 * math.pi,
    int samples = 500,
  }) {
    if (samples < 2 || start >= end) return const <Map<String, double>>[];
    final xs = ExpressionEngine.compile(expressionX);
    final ys = ExpressionEngine.compile(expressionY);
    return List<Map<String, double>>.generate(samples, (index) {
      final t = start + (end - start) * index / (samples - 1);
      return <String, double>{
        't': t,
        'x': xs.evaluate(x: t),
        'y': ys.evaluate(x: t),
      };
    }, growable: false);
  }

  static Map<String, double>? solveSystem2d(
    String expressionF,
    String expressionG, {
    double x = 0,
    double y = 0,
    double tolerance = 1e-10,
    int maxIterations = 100,
  }) {
    final f = ExpressionEngine.compile(expressionF);
    final g = ExpressionEngine.compile(expressionG);
    for (var iteration = 0; iteration < maxIterations; iteration++) {
      final fValue = f.evaluate(x: x, y: y);
      final gValue = g.evaluate(x: x, y: y);
      if (![fValue, gValue].every((value) => value.isFinite)) return null;
      if (math.max(fValue.abs(), gValue.abs()) <= tolerance) {
        return <String, double>{'x': x, 'y': y};
      }
      final scale = math.max(x.abs(), y.abs()).toDouble();
      final step = 1e-6 * (scale + 1);
      final fX =
          (f.evaluate(x: x + step, y: y) - f.evaluate(x: x - step, y: y)) /
          (2 * step);
      final fY =
          (f.evaluate(x: x, y: y + step) - f.evaluate(x: x, y: y - step)) /
          (2 * step);
      final gX =
          (g.evaluate(x: x + step, y: y) - g.evaluate(x: x - step, y: y)) /
          (2 * step);
      final gY =
          (g.evaluate(x: x, y: y + step) - g.evaluate(x: x, y: y - step)) /
          (2 * step);
      final determinant = fX * gY - fY * gX;
      if (!determinant.isFinite || determinant.abs() < 1e-14) return null;
      final deltaX = (fValue * gY - fY * gValue) / determinant;
      final deltaY = (fX * gValue - fValue * gX) / determinant;
      x -= deltaX;
      y -= deltaY;
      if (!x.isFinite || !y.isFinite) return null;
    }
    return null;
  }

  static List<double> scanRoots(
    String expression,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  }) {
    if (!start.isFinite ||
        !end.isFinite ||
        samples < 2 ||
        start >= end ||
        !tolerance.isFinite ||
        tolerance <= 0) {
      return const <double>[];
    }
    final function = ExpressionEngine.compile(expression);
    final xs = List<double>.generate(
      samples + 1,
      (index) => start + (end - start) * index / samples,
      growable: false,
    );
    final values = xs
        .map((x) => function.evaluate(x: x))
        .toList(growable: false);
    final roots = <double>[];
    final rootSeparation = math.max(
      1e-5,
      (end - start) / samples * .5,
    ).toDouble();
    void addRoot(double root) {
      if (!root.isFinite) return;
      final existingIndex = roots.indexWhere(
        (existing) => (existing - root).abs() <= rootSeparation,
      );
      if (existingIndex < 0) {
        roots.add(root);
      } else {
        // A sampled even-multiplicity root can be seen once as a near-zero
        // sample and again after Newton refinement. Keep the refined value.
        roots[existingIndex] = root;
      }
    }

    for (var index = 0; index < samples; index++) {
      final left = values[index];
      final right = values[index + 1];
      if (left.isFinite && left.abs() <= tolerance) {
        addRoot(xs[index]);
      }
      if (!left.isFinite || !right.isFinite || left.sign == right.sign) {
        continue;
      }
      var low = xs[index];
      var high = xs[index + 1];
      var lowValue = left;
      for (var iteration = 0; iteration < 80; iteration++) {
        final middle = (low + high) / 2;
        final middleValue = function.evaluate(x: middle);
        // A discontinuity must not be reported as a root. Keep the interval
        // only when the midpoint remains finite.
        if (!middleValue.isFinite) break;
        if (middleValue.abs() <= tolerance || (high - low).abs() <= tolerance) {
          low = middle;
          high = middle;
          break;
        }
        if (lowValue.sign != middleValue.sign) {
          high = middle;
        } else {
          low = middle;
          lowValue = middleValue;
        }
      }
      final candidate = (low + high) / 2;
      final residual = function.evaluate(x: candidate);
      if (residual.isFinite && residual.abs() <= tolerance * 10) {
        addRoot(candidate);
      }
    }

    // A root with even multiplicity does not change sign. Detect a finite
    // local minimum of |f| and let safeguarded Newton refine it, but verify
    // the residual so a shallow non-zero minimum is never advertised as a root.
    for (var index = 1; index < samples; index++) {
      final value = values[index];
      if (!value.isFinite ||
          value.abs() > math.max(tolerance * 100, 1e-4) ||
          !values[index - 1].isFinite ||
          !values[index + 1].isFinite ||
          value.abs() > values[index - 1].abs() ||
          value.abs() > values[index + 1].abs()) {
        continue;
      }
      final candidate = solve(
        expression,
        guess: xs[index],
        minimum: xs[index - 1],
        maximum: xs[index + 1],
        tolerance: tolerance * .001,
        maxIterations: 80,
      );
      if (candidate != null) {
        final residual = function.evaluate(x: candidate);
        if (residual.isFinite && residual.abs() <= tolerance * 10) {
          addRoot(candidate);
        }
      }
    }
    roots.sort();
    return roots;
  }

  static List<double> findIntersections(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  }) {
    return scanRoots(
      '($expressionF)-($expressionG)',
      start,
      end,
      samples: samples,
      tolerance: tolerance,
    );
  }

  static Map<String, double>? tangentAndNormal(
    String expression,
    double x, {
    double? step,
  }) {
    final y = evaluate(expression, x);
    final slope = derivative(expression, x, step: step);
    if (!y.isFinite || slope == null || !slope.isFinite) return null;
    final normalSlope = slope.abs() < 1e-14 ? double.infinity : -1 / slope;
    return <String, double>{
      'x': x,
      'y': y,
      'slope': slope,
      'normalSlope': normalSlope,
    };
  }

  static List<PlotPointValue> sampleSurface(
    String expression,
    double xMin,
    double xMax,
    double yMin,
    double yMax, {
    int rows = 40,
    int columns = 40,
  }) {
    if (rows < 2 || columns < 2 || xMin >= xMax || yMin >= yMax) {
      return const <PlotPointValue>[];
    }
    final compiled = ExpressionEngine.compile(expression);
    final points = <PlotPointValue>[];
    for (var row = 0; row < rows; row++) {
      final y = yMin + (yMax - yMin) * row / (rows - 1);
      for (var column = 0; column < columns; column++) {
        final x = xMin + (xMax - xMin) * column / (columns - 1);
        final z = compiled.evaluate(x: x, y: y);
        if (z.isFinite) points.add(PlotPointValue(x: x, y: y, value: z));
      }
    }
    return points;
  }

  static List<PlotPointValue> sampleImplicit(
    String expression,
    double xMin,
    double xMax,
    double yMin,
    double yMax, {
    int rows = 121,
    int columns = 121,
    double levelTolerance = .15,
  }) {
    if (rows < 2 ||
        columns < 2 ||
        xMin >= xMax ||
        yMin >= yMax ||
        !levelTolerance.isFinite ||
        levelTolerance <= 0) {
      return const <PlotPointValue>[];
    }
    final compiled = ExpressionEngine.compile(expression);
    final points = <PlotPointValue>[];
    for (var row = 0; row < rows; row++) {
      final y = yMin + (yMax - yMin) * row / (rows - 1);
      for (var column = 0; column < columns; column++) {
        final x = xMin + (xMax - xMin) * column / (columns - 1);
        final value = compiled.evaluate(x: x, y: y);
        if (value.isFinite && value.abs() <= levelTolerance) {
          points.add(PlotPointValue(x: x, y: y, value: value));
        }
      }
    }
    return points;
  }

  static List<PlotFieldVector> sampleDirectionField(
    String expression,
    double xMin,
    double xMax,
    double yMin,
    double yMax, {
    int rows = 20,
    int columns = 20,
  }) {
    if (rows < 1 || columns < 1 || xMin >= xMax || yMin >= yMax) {
      return const <PlotFieldVector>[];
    }
    final compiled = ExpressionEngine.compile(expression);
    final vectors = <PlotFieldVector>[];
    for (var row = 0; row < rows; row++) {
      final y = yMin + (yMax - yMin) * row / math.max(1, rows - 1).toDouble();
      for (var column = 0; column < columns; column++) {
        final x =
            xMin + (xMax - xMin) * column / math.max(1, columns - 1).toDouble();
        final slope = compiled.evaluate(x: x, y: y);
        if (!slope.isFinite) {
          continue;
        }
        final scale = 1 / math.sqrt(1 + slope * slope);
        vectors.add(PlotFieldVector(x: x, y: y, dx: scale, dy: slope * scale));
      }
    }
    return vectors;
  }

  static List<PlotFieldVector> sampleVectorField(
    String expressionX,
    String expressionY,
    double xMin,
    double xMax,
    double yMin,
    double yMax, {
    int rows = 20,
    int columns = 20,
  }) {
    final xFunction = ExpressionEngine.compile(expressionX);
    final yFunction = ExpressionEngine.compile(expressionY);
    final vectors = <PlotFieldVector>[];
    for (var row = 0; row < rows; row++) {
      final y = yMin + (yMax - yMin) * row / math.max(1, rows - 1).toDouble();
      for (var column = 0; column < columns; column++) {
        final x =
            xMin + (xMax - xMin) * column / math.max(1, columns - 1).toDouble();
        final dx = xFunction.evaluate(x: x, y: y);
        final dy = yFunction.evaluate(x: x, y: y);
        final magnitude = math.sqrt(dx * dx + dy * dy);
        if (!magnitude.isFinite || magnitude == 0) {
          continue;
        }
        vectors.add(
          PlotFieldVector(x: x, y: y, dx: dx / magnitude, dy: dy / magnitude),
        );
      }
    }
    return vectors;
  }

  static double? _integrateFunction(
    double Function(double) function,
    double start,
    double end,
    double tolerance,
  ) {
    if (start > end || tolerance <= 0) return null;
    if (start == end) return 0;
    final fa = function(start);
    final fb = function(end);
    final middle = function((start + end) / 2);
    if (![fa, fb, middle].every((value) => value.isFinite)) return null;
    return _adaptiveSimpson(
      function,
      start,
      end,
      tolerance,
      _simpson(start, end, fa, middle, fb),
      fa,
      middle,
      fb,
      18,
    );
  }

  static double? _nthDerivativeCompiled(
    CompiledExpression function,
    double x,
    int order,
    double step,
  ) {
    if (order == 0) {
      final value = function.evaluate(x: x);
      return value.isFinite ? value : null;
    }
    final left = _nthDerivativeCompiled(function, x - step, order - 1, step);
    final right = _nthDerivativeCompiled(function, x + step, order - 1, step);
    if (left == null || right == null) return null;
    return (right - left) / (2 * step);
  }

  static double? solve(
    String expression, {
    double guess = 0,
    double minimum = -100,
    double maximum = 100,
    double tolerance = 1e-10,
    int maxIterations = 100,
  }) {
    if (minimum >= maximum || tolerance <= 0 || maxIterations < 1) {
      return null;
    }
    final function = ExpressionEngine.compile(expression);
    var x = guess.clamp(minimum, maximum).toDouble();

    // First use safeguarded Newton steps from the user's guess. A bracket is
    // not assumed here: functions such as x squared minus 2 have the same
    // sign at both default bounds even though Newton converges immediately.
    for (var i = 0; i < maxIterations; i++) {
      final fx = function.evaluate(x: x);
      if (!fx.isFinite) return null;
      if (fx.abs() <= tolerance) return x;
      final h = 1e-6 * (x.abs() + 1);
      final fp = function.evaluate(x: x + h);
      final fm = function.evaluate(x: x - h);
      final derivative = fp.isFinite && fm.isFinite
          ? (fp - fm) / (2 * h)
          : double.nan;
      if (!derivative.isFinite || derivative.abs() <= 1e-14) break;
      final next = x - fx / derivative;
      if (!next.isFinite || next < minimum || next > maximum) break;
      x = next;
    }

    // If Newton did not converge, fall back to a true bracketed bisection.
    // This path is deliberately separate so it never invents a bracket from
    // two same-sign endpoints.
    var left = minimum;
    var right = maximum;
    var fLeft = function.evaluate(x: left);
    var fRight = function.evaluate(x: right);
    if (![fLeft, fRight].every((value) => value.isFinite)) return null;
    if (fLeft.abs() <= tolerance) return left;
    if (fRight.abs() <= tolerance) return right;
    if (fLeft.sign == fRight.sign) return null;
    for (var i = 0; i < maxIterations; i++) {
      final middle = (left + right) / 2;
      final fMiddle = function.evaluate(x: middle);
      if (!fMiddle.isFinite) return null;
      if (fMiddle.abs() <= tolerance || (right - left).abs() <= tolerance) {
        return middle;
      }
      if (fLeft.sign != fMiddle.sign) {
        right = middle;
        fRight = fMiddle;
      } else {
        left = middle;
        fLeft = fMiddle;
      }
    }
    return (left + right) / 2;
  }

  static CalcOdeSolution ode(
    String expression, {
    required double x0,
    required double y0,
    required double xEnd,
    int steps = 200,
  }) {
    if (steps < 1 || !x0.isFinite || !xEnd.isFinite || !y0.isFinite) {
      return const CalcOdeSolution(
        xs: <double>[],
        ys: <double?>[],
        method: 'RK4',
      );
    }
    final function = ExpressionEngine.compile(expression);
    final xs = <double>[x0];
    final ys = <double?>[y0];
    final h = (xEnd - x0) / steps;
    var x = x0;
    var y = y0;
    for (var i = 0; i < steps; i++) {
      double slope(double atX, double atY) => function.evaluate(x: atX, y: atY);
      final k1 = slope(x, y);
      final k2 = slope(x + h / 2, y + h * k1 / 2);
      final k3 = slope(x + h / 2, y + h * k2 / 2);
      final k4 = slope(x + h, y + h * k3);
      if (![k1, k2, k3, k4].every((value) => value.isFinite)) {
        break;
      }
      y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6;
      x = x0 + (i + 1) * h;
      xs.add(x);
      ys.add(y.isFinite ? y : null);
      if (!y.isFinite) {
        break;
      }
    }
    return CalcOdeSolution(xs: xs, ys: ys, method: 'RK4');
  }

  static CalcOdeSolution odeMethod(
    String expression, {
    required double x0,
    required double y0,
    required double xEnd,
    int steps = 200,
    String method = 'RK4',
  }) {
    if (steps < 1 || !x0.isFinite || !xEnd.isFinite || !y0.isFinite) {
      return const CalcOdeSolution(
        xs: <double>[],
        ys: <double?>[],
        method: 'invalid',
      );
    }
    final function = ExpressionEngine.compile(expression);
    final h = (xEnd - x0) / steps;
    var x = x0;
    var y = y0;
    final xs = <double>[x0];
    final ys = <double?>[y0];
    final normalized = method.toLowerCase();
    double slope(double atX, double atY) => function.evaluate(x: atX, y: atY);
    for (var index = 0; index < steps; index++) {
      final k1 = slope(x, y);
      if (!k1.isFinite) break;
      var next = double.nan;
      switch (normalized) {
        case 'euler':
          next = y + h * k1;
        case 'improved-euler':
        case 'heun':
          final predictor = y + h * k1;
          final k2 = slope(x + h, predictor);
          if (!k2.isFinite) break;
          next = y + h * (k1 + k2) / 2;
        case 'midpoint':
          final k2 = slope(x + h / 2, y + h * k1 / 2);
          if (!k2.isFinite) break;
          next = y + h * k2;
        case 'rkf45':
          final k2 = slope(x + h / 4, y + h * k1 / 4);
          final k3 = slope(
            x + 3 * h / 8,
            y + 3 * h * k1 / 32 + 9 * h * k2 / 32,
          );
          final k4 = slope(
            x + 12 * h / 13,
            y +
                1932 * h * k1 / 2197 -
                7200 * h * k2 / 2197 +
                7296 * h * k3 / 2197,
          );
          final k5 = slope(
            x + h,
            y +
                439 * h * k1 / 216 -
                8 * h * k2 +
                3680 * h * k3 / 513 -
                845 * h * k4 / 4104,
          );
          final k6 = slope(
            x + h / 2,
            y -
                8 * h * k1 / 27 +
                2 * h * k2 -
                3544 * h * k3 / 2565 +
                1859 * h * k4 / 4104 -
                11 * h * k5 / 40,
          );
          if (![k2, k3, k4, k5, k6].every((value) => value.isFinite)) break;
          next =
              y +
              h *
                  (16 * k1 / 135 +
                      6656 * k3 / 12825 +
                      28561 * k4 / 56430 -
                      9 * k5 / 50 +
                      2 * k6 / 55);
        case 'rk4':
        default:
          final k2 = slope(x + h / 2, y + h * k1 / 2);
          final k3 = slope(x + h / 2, y + h * k2 / 2);
          final k4 = slope(x + h, y + h * k3);
          if (![k2, k3, k4].every((value) => value.isFinite)) break;
          next = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6;
      }
      if (!next.isFinite) break;
      y = next;
      x = x0 + (index + 1) * h;
      xs.add(x);
      ys.add(y);
    }
    return CalcOdeSolution(xs: xs, ys: ys, method: method.toUpperCase());
  }

  static CalcSpectrum spectrum(
    String expression, {
    required double a,
    required double b,
    int samples = 1024,
  }) {
    if (b <= a || samples < 2) {
      return const CalcSpectrum(
        frequencies: <double>[],
        amplitudes: <double>[],
        phases: <double>[],
      );
    }
    final size = _nextPowerOfTwo(samples);
    final function = ExpressionEngine.compile(expression);
    final real = List<double>.generate(size, (index) {
      final x = a + (b - a) * index / size;
      final value = function.evaluate(x: x);
      return value.isFinite ? value : 0;
    });
    final mean = real.reduce((left, right) => left + right) / size;
    final imaginary = List<double>.filled(size, 0);
    for (var i = 0; i < real.length; i++) {
      real[i] -= mean;
    }
    _fft(real, imaginary);
    final count = size ~/ 2 + 1;
    final frequencies = <double>[];
    final amplitudes = <double>[];
    final phases = <double>[];
    for (var i = 0; i < count; i++) {
      frequencies.add(i / (b - a));
      var amplitude = math.sqrt(
        real[i] * real[i] + imaginary[i] * imaginary[i],
      );
      amplitude *= 2 / size;
      if (i == 0 || (size.isEven && i == size ~/ 2)) amplitude /= 2;
      amplitudes.add(amplitude);
      phases.add(math.atan2(imaginary[i], real[i]));
    }
    return CalcSpectrum(
      frequencies: frequencies,
      amplitudes: amplitudes,
      phases: phases,
    );
  }

  static List<double> convolution(List<double> left, List<double> right) {
    if (left.isEmpty || right.isEmpty) return const <double>[];
    if (left.any((value) => !value.isFinite) ||
        right.any((value) => !value.isFinite)) {
      throw const FormatException('Convolution inputs must be finite.');
    }
    final result = List<double>.filled(left.length + right.length - 1, 0);
    for (var i = 0; i < left.length; i++) {
      for (var j = 0; j < right.length; j++) {
        result[i + j] += left[i] * right[j];
      }
    }
    return result;
  }

  static CalcStatistics statistics(Iterable<double> source) {
    final values = source.where((value) => value.isFinite).toList()..sort();
    if (values.isEmpty) {
      return const CalcStatistics(
        count: 0,
        sum: 0,
        mean: double.nan,
        median: double.nan,
        minimum: double.nan,
        maximum: double.nan,
        range: double.nan,
        variance: double.nan,
        standardDeviation: double.nan,
        q1: double.nan,
        q3: double.nan,
        mode: null,
      );
    }
    final sum = values.fold<double>(0, (total, value) => total + value);
    final mean = sum / values.length;
    final variance = values.length < 2
        ? 0.0
        : values.fold<double>(
                0.0,
                (total, value) => total + (value - mean) * (value - mean),
              ) /
              (values.length - 1);
    final frequencies = <double, int>{};
    for (final value in values) {
      frequencies[value] = (frequencies[value] ?? 0) + 1;
    }
    final modeEntry = frequencies.entries.reduce(
      (left, right) => right.value > left.value ? right : left,
    );
    final mode = modeEntry.value > 1 ? modeEntry.key : null;
    return CalcStatistics(
      count: values.length,
      sum: sum,
      mean: mean,
      median: _median(values),
      minimum: values.first,
      maximum: values.last,
      range: values.last - values.first,
      variance: variance,
      standardDeviation: math.sqrt(variance),
      q1: _median(values.sublist(0, values.length ~/ 2)),
      q3: _median(values.sublist((values.length + 1) ~/ 2)),
      mode: mode,
    );
  }

  static CalcRegression linearRegression(List<double> xs, List<double> ys) {
    final points = <List<double>>[];
    for (var i = 0; i < xs.length && i < ys.length; i++) {
      if (xs[i].isFinite && ys[i].isFinite) {
        points.add(<double>[xs[i], ys[i]]);
      }
    }
    if (points.length < 2) {
      return const CalcRegression(
        slope: double.nan,
        intercept: double.nan,
        rSquared: double.nan,
        xs: <double>[],
        ys: <double>[],
      );
    }
    final meanX =
        points.fold<double>(0, (sum, point) => sum + point[0]) / points.length;
    final meanY =
        points.fold<double>(0, (sum, point) => sum + point[1]) / points.length;
    var xx = 0.0;
    var xy = 0.0;
    var total = 0.0;
    for (final point in points) {
      xx += (point[0] - meanX) * (point[0] - meanX);
      xy += (point[0] - meanX) * (point[1] - meanY);
      total += (point[1] - meanY) * (point[1] - meanY);
    }
    if (xx == 0) {
      return const CalcRegression(
        slope: double.nan,
        intercept: double.nan,
        rSquared: double.nan,
        xs: <double>[],
        ys: <double>[],
      );
    }
    final slope = xy / xx;
    final intercept = meanY - slope * meanX;
    var residual = 0.0;
    final fitXs = points.map((point) => point[0]).toList()..sort();
    final fitYs = fitXs.map((x) => slope * x + intercept).toList();
    for (final point in points) {
      final error = point[1] - (slope * point[0] + intercept);
      residual += error * error;
    }
    return CalcRegression(
      slope: slope,
      intercept: intercept,
      rSquared: total == 0 ? (residual == 0 ? 1 : 0) : 1 - residual / total,
      xs: fitXs,
      ys: fitYs,
    );
  }

  // ---------- Regression and interpolation ----------

  static CalcPolynomialRegression polynomialRegression(
    List<double> xs,
    List<double> ys, {
    int degree = 2,
  }) {
    final points = <List<double>>[];
    for (var index = 0; index < xs.length && index < ys.length; index++) {
      if (xs[index].isFinite && ys[index].isFinite) {
        points.add(<double>[xs[index], ys[index]]);
      }
    }
    if (degree < 1 || degree > 12 || points.length <= degree) {
      return const CalcPolynomialRegression(
        coefficients: <double>[],
        rSquared: double.nan,
        xs: <double>[],
        ys: <double>[],
      );
    }
    final size = degree + 1;
    final normal = List<List<double>>.generate(
      size,
      (_) => List<double>.filled(size + 1, 0),
    );
    for (final point in points) {
      final powers = List<double>.filled(2 * degree + 1, 1);
      for (var power = 1; power < powers.length; power++) {
        powers[power] = powers[power - 1] * point[0];
      }
      for (var row = 0; row < size; row++) {
        for (var column = 0; column < size; column++) {
          normal[row][column] += powers[row + column];
        }
        normal[row][size] += powers[row] * point[1];
      }
    }
    final coefficients = _solveAugmented(normal);
    if (coefficients == null) {
      return const CalcPolynomialRegression(
        coefficients: <double>[],
        rSquared: double.nan,
        xs: <double>[],
        ys: <double>[],
      );
    }
    final mean =
        points.fold<double>(0, (sum, point) => sum + point[1]) / points.length;
    var total = 0.0;
    var residual = 0.0;
    for (final point in points) {
      final predicted = _evaluatePolynomial(coefficients, point[0]);
      total += (point[1] - mean) * (point[1] - mean);
      residual += (point[1] - predicted) * (point[1] - predicted);
    }
    points.sort((a, b) => a[0].compareTo(b[0]));
    final minX = points.first[0];
    final maxX = points.last[0];
    final fitXs = List<double>.generate(
      120,
      (index) => minX + (maxX - minX) * index / 119,
      growable: false,
    );
    return CalcPolynomialRegression(
      coefficients: coefficients,
      rSquared: total == 0 ? (residual == 0 ? 1 : 0) : 1 - residual / total,
      xs: fitXs,
      ys: fitXs
          .map((value) => _evaluatePolynomial(coefficients, value))
          .toList(growable: false),
    );
  }

  static CalcModelRegression nonlinearRegression(
    String model,
    List<double> xs,
    List<double> ys,
  ) {
    final points = <List<double>>[];
    for (var index = 0; index < xs.length && index < ys.length; index++) {
      if (xs[index].isFinite && ys[index].isFinite) {
        points.add(<double>[xs[index], ys[index]]);
      }
    }
    if (points.length < 2) {
      return const CalcModelRegression(
        model: 'invalid',
        parameters: <String, double>{},
        rSquared: double.nan,
        xs: <double>[],
        ys: <double>[],
        equation: '',
      );
    }
    final transformedX = <double>[];
    final transformedY = <double>[];
    for (final point in points) {
      final x = point[0];
      final y = point[1];
      switch (model) {
        case 'exponential':
          if (y <= 0) {
            continue;
          }
          transformedX.add(x);
          transformedY.add(math.log(y));
        case 'power':
          if (x <= 0 || y <= 0) {
            continue;
          }
          transformedX.add(math.log(x));
          transformedY.add(math.log(y));
        case 'logarithmic':
          if (x <= 0) {
            continue;
          }
          transformedX.add(math.log(x));
          transformedY.add(y);
        default:
          throw const FormatException('Unknown regression model.');
      }
    }
    if (transformedX.length < 2) {
      return const CalcModelRegression(
        model: 'invalid',
        parameters: <String, double>{},
        rSquared: double.nan,
        xs: <double>[],
        ys: <double>[],
        equation: '',
      );
    }
    final linear = linearRegression(transformedX, transformedY);
    if (!linear.rSquared.isFinite) {
      return const CalcModelRegression(
        model: 'invalid',
        parameters: <String, double>{},
        rSquared: double.nan,
        xs: <double>[],
        ys: <double>[],
        equation: '',
      );
    }
    late final Map<String, double> parameters;
    late final String equation;
    double predict(double x) {
      switch (model) {
        case 'exponential':
          return math.exp(linear.intercept + linear.slope * x);
        case 'power':
          return math.exp(linear.intercept) *
              math.pow(x, linear.slope).toDouble();
        case 'logarithmic':
          return linear.intercept + linear.slope * math.log(x);
        default:
          return double.nan;
      }
    }

    switch (model) {
      case 'exponential':
        parameters = <String, double>{
          'a': math.exp(linear.intercept),
          'b': linear.slope,
        };
        equation = 'y = a·e^(b·x)';
      case 'power':
        parameters = <String, double>{
          'a': math.exp(linear.intercept),
          'b': linear.slope,
        };
        equation = 'y = a·x^b';
      case 'logarithmic':
        parameters = <String, double>{'a': linear.intercept, 'b': linear.slope};
        equation = 'y = a + b·ln(x)';
      default:
        parameters = const <String, double>{};
        equation = '';
    }
    final mean =
        points.fold<double>(0, (sum, point) => sum + point[1]) / points.length;
    var total = 0.0;
    var residual = 0.0;
    for (final point in points) {
      final predicted = predict(point[0]);
      if (!predicted.isFinite) {
        continue;
      }
      total += (point[1] - mean) * (point[1] - mean);
      residual += (point[1] - predicted) * (point[1] - predicted);
    }
    points.sort((a, b) => a[0].compareTo(b[0]));
    final validPoints = points
        .where((point) => predict(point[0]).isFinite)
        .toList();
    return CalcModelRegression(
      model: model,
      parameters: parameters,
      rSquared: total == 0 ? (residual == 0 ? 1 : 0) : 1 - residual / total,
      xs: validPoints.map((point) => point[0]).toList(growable: false),
      ys: validPoints.map((point) => predict(point[0])).toList(growable: false),
      equation: equation,
    );
  }

  static double? interpolate(
    String method,
    List<double> xs,
    List<double> ys,
    double x,
  ) {
    final points = <List<double>>[];
    for (var index = 0; index < xs.length && index < ys.length; index++) {
      if (xs[index].isFinite && ys[index].isFinite) {
        points.add(<double>[xs[index], ys[index]]);
      }
    }
    if (points.isEmpty || !x.isFinite) return null;
    points.sort((a, b) => a[0].compareTo(b[0]));
    if (method == 'nearest') {
      points.sort((a, b) => (a[0] - x).abs().compareTo((b[0] - x).abs()));
      return points.first[1];
    }
    if (method == 'linear') {
      if (x <= points.first[0]) return points.first[1];
      if (x >= points.last[0]) return points.last[1];
      for (var index = 1; index < points.length; index++) {
        if (x <= points[index][0]) {
          final left = points[index - 1];
          final right = points[index];
          final fraction = (x - left[0]) / (right[0] - left[0]);
          return left[1] + fraction * (right[1] - left[1]);
        }
      }
    }
    if (method == 'cubic-spline' && points.length >= 3) {
      // Natural cubic spline, solved once for the second derivatives.
      final n = points.length;
      final lower = List<double>.filled(n, 0);
      final diagonal = List<double>.filled(n, 1);
      final upper = List<double>.filled(n, 0);
      final rhs = List<double>.filled(n, 0);
      for (var i = 1; i < n - 1; i++) {
        final h0 = points[i][0] - points[i - 1][0];
        final h1 = points[i + 1][0] - points[i][0];
        lower[i] = h0 / 6;
        diagonal[i] = (h0 + h1) / 3;
        upper[i] = h1 / 6;
        rhs[i] =
            (points[i + 1][1] - points[i][1]) / h1 -
            (points[i][1] - points[i - 1][1]) / h0;
      }
      for (var i = 1; i < n; i++) {
        final factor = lower[i] / diagonal[i - 1];
        diagonal[i] -= factor * upper[i - 1];
        rhs[i] -= factor * rhs[i - 1];
      }
      final second = List<double>.filled(n, 0);
      for (var i = n - 2; i >= 0; i--) {
        second[i] = (rhs[i] - upper[i] * second[i + 1]) / diagonal[i];
      }
      var index = 0;
      while (index < n - 2 && x > points[index + 1][0]) {
        index++;
      }
      final left = points[index];
      final rightIndex = math.min(index + 1, n - 1).toInt();
      final right = points[rightIndex];
      final h = right[0] - left[0];
      if (h == 0) return null;
      final a = (right[0] - x) / h;
      final b = (x - left[0]) / h;
      return a * left[1] +
          b * right[1] +
          ((a * a * a - a) * second[index] +
                  (b * b * b - b) * second[rightIndex]) *
              h *
              h /
              6;
    }
    // Lagrange and Newton share the same barycentric evaluation for a stable
    // polynomial result; both names are retained as explicit user choices.
    if (method == 'lagrange' || method == 'newton' || method == 'polynomial') {
      var result = 0.0;
      for (var i = 0; i < points.length; i++) {
        var term = points[i][1];
        for (var j = 0; j < points.length; j++) {
          if (i == j) {
            continue;
          }
          final denominator = points[i][0] - points[j][0];
          if (denominator == 0) return null;
          term *= (x - points[j][0]) / denominator;
        }
        result += term;
      }
      return result;
    }
    if (method == 'hermite' && points.length >= 2) {
      // Piecewise cubic Hermite with finite-difference slopes.
      var index = 0;
      while (index < points.length - 2 && x > points[index + 1][0]) {
        index++;
      }
      final left = points[index];
      final right = points[index + 1];
      final h = right[0] - left[0];
      if (h == 0) return null;
      final leftSlope = index == 0
          ? (right[1] - left[1]) / h
          : (right[1] - points[index - 1][1]) /
                (right[0] - points[index - 1][0]);
      final rightSlope = index + 2 >= points.length
          ? (right[1] - left[1]) / h
          : (points[index + 2][1] - left[1]) / (points[index + 2][0] - left[0]);
      final t = (x - left[0]) / h;
      return (2 * t * t * t - 3 * t * t + 1) * left[1] +
          (t * t * t - 2 * t * t + t) * h * leftSlope +
          (-2 * t * t * t + 3 * t * t) * right[1] +
          (t * t * t - t * t) * h * rightSlope;
    }
    return null;
  }

  // ---------- Probability distributions ----------

  static CalcDistributionResult distribution(
    String name,
    double x,
    Map<String, double> parameters,
  ) {
    return CalcDistributionResult(
      name: name,
      x: x,
      pdf: distributionPdf(name, x, parameters),
      cdf: distributionCdf(name, x, parameters),
      ppf: distributionPpf(name, x, parameters),
    );
  }

  static double? distributionPdf(
    String name,
    double x,
    Map<String, double> parameters,
  ) {
    final normalized = name.toLowerCase();
    switch (normalized) {
      case 'normal':
        final sigma = parameters['sigma'] ?? 1;
        if (sigma <= 0) return null;
        final z = (x - (parameters['mu'] ?? 0)) / sigma;
        return math.exp(-z * z / 2) / (sigma * math.sqrt(2 * math.pi));
      case 't':
      case 'student-t':
        final degrees = parameters['nu'] ?? parameters['df'] ?? 1;
        if (degrees <= 0) return null;
        return math.exp(
          _logGamma((degrees + 1) / 2) -
              _logGamma(degrees / 2) -
              .5 * math.log(degrees * math.pi) -
              (degrees + 1) / 2 * math.log(1 + x * x / degrees),
        );
      case 'chi2':
      case 'chi-squared':
        final degrees = parameters['k'] ?? parameters['df'] ?? 1;
        if (degrees <= 0 || x < 0) return 0;
        return math.exp(
              (degrees / 2 - 1) * math.log(x == 0 ? 1e-300 : x) -
                  x / 2 -
                  _logGamma(degrees / 2),
            ) /
            2;
      case 'f':
        final d1 = parameters['d1'] ?? 1;
        final d2 = parameters['d2'] ?? 1;
        if (d1 <= 0 || d2 <= 0 || x <= 0) return x == 0 ? 0 : null;
        final a = d1 / 2;
        final b = d2 / 2;
        return math.exp(
          a * math.log(d1 / d2) +
              (a - 1) * math.log(x) -
              (a + b) * math.log(1 + d1 * x / d2) -
              _logBeta(a, b),
        );
      case 'binomial':
        final n = (parameters['n'] ?? 1).round();
        final p = parameters['p'] ?? .5;
        final k = x.round();
        if (n < 0 || p < 0 || p > 1 || k < 0 || k > n || x != k) return 0;
        return math.exp(
          _logCombination(n, k) +
              (p == 0
                  ? (k == 0 ? 0 : double.negativeInfinity)
                  : k * math.log(p)) +
              (p == 1
                  ? (n == k ? 0 : double.negativeInfinity)
                  : (n - k) * math.log(1 - p)),
        );
      case 'poisson':
        final lambda = parameters['lambda'] ?? parameters['lam'] ?? 1;
        final k = x.round();
        if (lambda < 0 || k < 0 || x != k) return 0;
        return math.exp(
          -lambda + k * math.log(lambda == 0 ? 1 : lambda) - _logGamma(k + 1),
        );
      default:
        return null;
    }
  }

  static double? distributionCdf(
    String name,
    double x,
    Map<String, double> parameters,
  ) {
    final normalized = name.toLowerCase();
    switch (normalized) {
      case 'normal':
        final sigma = parameters['sigma'] ?? 1;
        if (sigma <= 0) return null;
        return .5 *
            (1 + _erf((x - (parameters['mu'] ?? 0)) / sigma / math.sqrt(2)));
      case 't':
      case 'student-t':
        final degrees = parameters['nu'] ?? parameters['df'] ?? 1;
        if (degrees <= 0) return null;
        if (x == 0) return .5;
        final beta = _regularizedBeta(
          degrees / (degrees + x * x),
          degrees / 2,
          .5,
        );
        return x > 0 ? 1 - beta / 2 : beta / 2;
      case 'chi2':
      case 'chi-squared':
        final degrees = parameters['k'] ?? parameters['df'] ?? 1;
        return degrees > 0 && x >= 0
            ? _regularizedGamma(degrees / 2, x / 2)
            : 0;
      case 'f':
        final d1 = parameters['d1'] ?? 1;
        final d2 = parameters['d2'] ?? 1;
        if (d1 <= 0 || d2 <= 0 || x < 0) return 0;
        return _regularizedBeta(d1 * x / (d1 * x + d2), d1 / 2, d2 / 2);
      case 'binomial':
        final n = (parameters['n'] ?? 1).round();
        final p = parameters['p'] ?? .5;
        if (n < 0 || p < 0 || p > 1) return null;
        final end = math.min(n, x.floor());
        if (end < 0) return 0;
        var sum = 0.0;
        for (var k = 0; k <= end; k++) {
          sum += distributionPdf('binomial', k.toDouble(), parameters) ?? 0;
        }
        return sum.clamp(0, 1).toDouble();
      case 'poisson':
        final lambda = parameters['lambda'] ?? parameters['lam'] ?? 1;
        if (lambda < 0) return null;
        final end = x.floor();
        if (end < 0) return 0;
        var sum = 0.0;
        for (var k = 0; k <= end; k++) {
          sum += distributionPdf('poisson', k.toDouble(), parameters) ?? 0;
        }
        return sum.clamp(0, 1).toDouble();
      default:
        return null;
    }
  }

  static double? distributionPpf(
    String name,
    double probability,
    Map<String, double> parameters,
  ) {
    if (!probability.isFinite || probability < 0 || probability > 1) {
      return null;
    }
    final normalized = name.toLowerCase();
    if (normalized == 'binomial' || normalized == 'poisson') {
      var low = 0;
      var high = normalized == 'binomial'
          ? (parameters['n'] ?? 1).round()
          : math
                .max(
                  1,
                  ((parameters['lambda'] ?? parameters['lam'] ?? 1) * 8)
                      .round(),
                )
                .toInt();
      while ((distributionCdf(name, high.toDouble(), parameters) ?? 0) <
              probability &&
          high < 1000000) {
        high *= 2;
      }
      while (low < high) {
        final middle = (low + high) ~/ 2;
        if ((distributionCdf(name, middle.toDouble(), parameters) ?? 0) >=
            probability) {
          high = middle;
        } else {
          low = middle + 1;
        }
      }
      return low.toDouble();
    }
    if (probability == 0) {
      return normalized == 'normal' ? double.negativeInfinity : 0;
    }
    if (probability == 1) {
      return double.infinity;
    }
    var low =
        normalized == 'normal' || normalized == 't' || normalized == 'student-t'
        ? -12.0
        : 0.0;
    var high = 12.0;
    for (var iteration = 0; iteration < 100; iteration++) {
      final middle = (low + high) / 2;
      final value = distributionCdf(name, middle, parameters);
      if (value == null) return null;
      if (value < probability) {
        low = middle;
      } else {
        high = middle;
      }
    }
    return (low + high) / 2;
  }

  // ---------- Probability and discrete mathematics ----------

  static BigInt combination(int n, int k) {
    if (n < 0 || k < 0 || k > n) {
      throw const FormatException('Choose n and r with 0 ≤ r ≤ n.');
    }
    final reduced = math.min(k, n - k).toInt();
    var result = BigInt.one;
    for (var index = 1; index <= reduced; index++) {
      result = result * BigInt.from(n - reduced + index) ~/ BigInt.from(index);
    }
    return result;
  }

  static BigInt permutation(int n, int k) {
    if (n < 0 || k < 0 || k > n) {
      throw const FormatException('Choose n and r with 0 ≤ r ≤ n.');
    }
    var result = BigInt.one;
    for (var index = 0; index < k; index++) {
      result *= BigInt.from(n - index);
    }
    return result;
  }

  static double complementProbability(double probability) {
    _checkProbability(probability, 'Probability');
    return 1 - probability;
  }

  static double unionProbability({
    required double eventA,
    required double eventB,
    required double intersection,
  }) {
    _checkProbability(eventA, 'P(A)');
    _checkProbability(eventB, 'P(B)');
    _checkProbability(intersection, 'P(A and B)');
    if (intersection > math.min(eventA, eventB)) {
      throw const FormatException('The intersection exceeds an event.');
    }
    return eventA + eventB - intersection;
  }

  static double conditionalProbability({
    required double intersection,
    required double given,
  }) {
    _checkProbability(intersection, 'P(A and B)');
    _checkProbability(given, 'P(B)');
    if (given == 0 || intersection > given) {
      throw const FormatException(
        'P(B) must be positive and bound the intersection.',
      );
    }
    return intersection / given;
  }

  static double bayesProbability({
    required double prior,
    required double likelihood,
    required double evidence,
  }) {
    _checkProbability(prior, 'Prior');
    _checkProbability(likelihood, 'Likelihood');
    _checkProbability(evidence, 'Evidence');
    if (evidence == 0) {
      throw const FormatException('Evidence must be positive.');
    }
    final posterior = prior * likelihood / evidence;
    if (!posterior.isFinite || posterior < 0 || posterior > 1) {
      throw const FormatException('The inputs produce an invalid posterior.');
    }
    return posterior;
  }

  static double binomialProbability({
    required int n,
    required int k,
    required double p,
  }) {
    if (n < 0 || k < 0 || k > n || !p.isFinite || p < 0 || p > 1) {
      throw const FormatException('Binomial inputs are invalid.');
    }
    if ((p == 0 && k > 0) || (p == 1 && k < n)) return 0;
    if (p == 0) return 1;
    if (p == 1) return 1;
    final logValue =
        _logCombination(n, k) + k * math.log(p) + (n - k) * math.log(1 - p);
    return math.exp(logValue);
  }

  static double binomialMean(int n, double p) {
    if (n < 0 || !p.isFinite || p < 0 || p > 1) {
      throw const FormatException('Binomial inputs are invalid.');
    }
    return n * p;
  }

  static double binomialVariance(int n, double p) {
    if (n < 0 || !p.isFinite || p < 0 || p > 1) {
      throw const FormatException('Binomial inputs are invalid.');
    }
    return n * p * (1 - p);
  }

  static void _checkProbability(double value, String label) {
    if (!value.isFinite || value < 0 || value > 1) {
      throw FormatException('$label must be between 0 and 1.');
    }
  }

  // ---------- Calendar ----------

  static DateTime parseCalendarDate(String value) {
    final match = RegExp(r'^(\d{4})-(\d{2})-(\d{2})$').firstMatch(value.trim());
    if (match == null) {
      throw const FormatException('Use the date format YYYY-MM-DD.');
    }
    final date = DateTime.utc(
      int.parse(match.group(1)!),
      int.parse(match.group(2)!),
      int.parse(match.group(3)!),
    );
    if (date.year != int.parse(match.group(1)!) ||
        date.month != int.parse(match.group(2)!) ||
        date.day != int.parse(match.group(3)!)) {
      throw const FormatException('The calendar date is invalid.');
    }
    return date;
  }

  static int calendarWeekday(String value) => parseCalendarDate(value).weekday;

  static int calendarDateDifference(String start, String end) =>
      parseCalendarDate(end).difference(parseCalendarDate(start)).inDays;

  static String calendarAddDays(String value, int days) {
    final date = parseCalendarDate(value).add(Duration(days: days));
    return _formatCalendarDate(date);
  }

  static String _formatCalendarDate(DateTime date) {
    final year = date.year.toString().padLeft(4, '0');
    final month = date.month.toString().padLeft(2, '0');
    final day = date.day.toString().padLeft(2, '0');
    return '$year-$month-$day';
  }

  // ---------- Finance ----------

  static double loanPayment({
    required double principal,
    required double annualRate,
    required int periods,
  }) {
    if (!principal.isFinite ||
        !annualRate.isFinite ||
        principal < 0 ||
        annualRate < 0 ||
        periods < 1) {
      throw const FormatException('Principal, rate and periods are invalid.');
    }
    final rate = annualRate / 12;
    if (rate == 0) return principal / periods;
    return (principal * rate / (1 - math.pow(1 + rate, -periods))).toDouble();
  }

  static double compoundInterest({
    required double principal,
    required double annualRate,
    required int compoundsPerYear,
    required double years,
  }) {
    if (!principal.isFinite ||
        !annualRate.isFinite ||
        !years.isFinite ||
        principal < 0 ||
        compoundsPerYear < 1 ||
        years < 0 ||
        1 + annualRate / compoundsPerYear <= 0) {
      throw const FormatException('Compound-interest inputs are invalid.');
    }
    return (principal *
            math.pow(
              1 + annualRate / compoundsPerYear,
              compoundsPerYear * years,
            ))
        .toDouble();
  }

  static double npv(double rate, List<double> cashFlows) {
    if (!rate.isFinite ||
        rate <= -1 ||
        cashFlows.isEmpty ||
        cashFlows.any((value) => !value.isFinite)) {
      throw const FormatException(
        'Discount rate and cash flows must be finite and valid.',
      );
    }
    var result = 0.0;
    for (var index = 0; index < cashFlows.length; index++) {
      result += cashFlows[index] / math.pow(1 + rate, index).toDouble();
    }
    return result;
  }

  static double? irr(List<double> cashFlows) {
    if (cashFlows.length < 2 || cashFlows.any((value) => !value.isFinite)) {
      return null;
    }
    if (!cashFlows.any((value) => value < 0) ||
        !cashFlows.any((value) => value > 0)) {
      return null;
    }
    var low = -0.9999;
    var high = 10.0;
    var fLow = npv(low, cashFlows);
    var fHigh = npv(high, cashFlows);
    if (fLow.sign == fHigh.sign) return null;
    for (var iteration = 0; iteration < 200; iteration++) {
      final middle = (low + high) / 2;
      final fMiddle = npv(middle, cashFlows);
      if (fMiddle.abs() < 1e-10) return middle;
      if (fLow.sign == fMiddle.sign) {
        low = middle;
        fLow = fMiddle;
      } else {
        high = middle;
        fHigh = fMiddle;
      }
    }
    return (low + high) / 2;
  }

  static double straightLineDepreciation(
    double cost,
    double salvage,
    int years,
    int year,
  ) {
    if (!cost.isFinite ||
        !salvage.isFinite ||
        years < 1 ||
        year < 1 ||
        year > years ||
        cost < salvage) {
      throw const FormatException('Depreciation inputs are invalid.');
    }
    return math.max(0, (cost - salvage) / years).toDouble();
  }

  static double bondPrice({
    required double faceValue,
    required double couponRate,
    required double marketRate,
    required int periods,
  }) {
    if (!faceValue.isFinite ||
        !couponRate.isFinite ||
        !marketRate.isFinite ||
        periods < 1 ||
        faceValue < 0 ||
        1 + marketRate <= 0) {
      throw const FormatException('Bond inputs are invalid.');
    }
    final coupon = faceValue * couponRate;
    if (marketRate == 0) return faceValue + coupon * periods;
    return (coupon * (1 - math.pow(1 + marketRate, -periods)) / marketRate +
            faceValue * math.pow(1 + marketRate, -periods))
        .toDouble();
  }

  static double retirementFutureValue({
    required double initialBalance,
    required double monthlyContribution,
    required double annualRate,
    required double years,
  }) {
    if (!initialBalance.isFinite ||
        !monthlyContribution.isFinite ||
        !annualRate.isFinite ||
        !years.isFinite ||
        initialBalance < 0 ||
        monthlyContribution < 0 ||
        years < 0 ||
        annualRate / 12 <= -1) {
      throw const FormatException('Retirement inputs are invalid.');
    }
    final months = (years * 12).round();
    final monthlyRate = annualRate / 12;
    if (monthlyRate == 0) {
      return initialBalance + monthlyContribution * months;
    }
    final growth = math.pow(1 + monthlyRate, months).toDouble();
    return initialBalance * growth +
        monthlyContribution * ((growth - 1) / monthlyRate);
  }

  static String formatFactors(Map<BigInt, int> factors) => factors.entries
      .map(
        (entry) =>
            entry.value == 1 ? '${entry.key}' : '${entry.key}^${entry.value}',
      )
      .join(' × ');

  static String convertBase(String input, int fromBase, int toBase) {
    if (fromBase < 2 || fromBase > 36 || toBase < 2 || toBase > 36) {
      throw const FormatException('Base must be between 2 and 36.');
    }
    final normalized = input.trim();
    if (normalized.isEmpty) {
      throw const FormatException('Enter a number to convert.');
    }
    final negative = normalized.startsWith('-');
    final digits = negative || normalized.startsWith('+')
        ? normalized.substring(1)
        : normalized;
    final value = BigInt.tryParse(digits, radix: fromBase);
    if (value == null) {
      throw const FormatException('Invalid digits for the source base.');
    }
    final output = value.toRadixString(toBase).toUpperCase();
    return negative ? '-$output' : output;
  }

  static double convertUnit(
    String category,
    String from,
    String to,
    double value,
  ) {
    const factors = <String, Map<String, double>>{
      'Length': <String, double>{
        'm': 1,
        'km': 1000,
        'cm': .01,
        'mm': .001,
        'in': .0254,
        'ft': .3048,
      },
      'Weight': <String, double>{
        'kg': 1,
        'g': .001,
        'lb': .45359237,
        'oz': .028349523125,
      },
      'Time': <String, double>{'s': 1, 'min': 60, 'h': 3600, 'day': 86400},
      'Data': <String, double>{
        'B': 1,
        'KB': 1024,
        'MB': 1048576,
        'GB': 1073741824,
      },
      'Speed': <String, double>{
        'm/s': 1,
        'km/h': .2777777777777778,
        'mph': .44704,
      },
      'Angle': <String, double>{'rad': 1, 'deg': .017453292519943295},
      'Area': <String, double>{'m²': 1, 'km²': 1000000, 'ft²': .09290304},
      'Volume': <String, double>{
        'L': 1,
        'mL': .001,
        'm³': 1000,
        'gal': 3.785411784,
      },
    };
    if (category == 'Temperature') {
      final celsius = switch (from) {
        '°C' => value,
        '°F' => (value - 32) * 5 / 9,
        'K' => value - 273.15,
        _ => throw const FormatException('Unknown temperature unit.'),
      };
      return switch (to) {
        '°C' => celsius,
        '°F' => celsius * 9 / 5 + 32,
        'K' => celsius + 273.15,
        _ => throw const FormatException('Unknown temperature unit.'),
      };
    }
    final categoryFactors = factors[category];
    final fromFactor = categoryFactors?[from];
    final toFactor = categoryFactors?[to];
    if (fromFactor == null || toFactor == null) {
      throw const FormatException('Unknown unit.');
    }
    return value * fromFactor / toFactor;
  }

  static CalcMatrix parseMatrix(String input) {
    final normalized = input.trim();
    if (normalized.isEmpty) {
      throw const FormatException('Enter a non-empty matrix.');
    }
    final rows = <List<double>>[];
    for (final rawRow in normalized.split(';')) {
      final rowText = rawRow.trim();
      if (rowText.isEmpty) {
        throw const FormatException('Matrix rows cannot be empty.');
      }
      final cells = rowText.split(RegExp(r'[,\s]+'));
      final row = <double>[];
      for (final cell in cells) {
        final value = double.tryParse(cell);
        if (value == null || !value.isFinite) {
          throw const FormatException('Matrix entries must be finite numbers.');
        }
        row.add(value);
      }
      rows.add(row);
    }
    if (rows.isEmpty ||
        rows.first.isEmpty ||
        rows.any((row) => row.length != rows.first.length)) {
      throw const FormatException('Matrix rows must have equal columns.');
    }
    if (rows.length > 256 || rows.first.length > 256) {
      throw const FormatException('Matrix dimensions are limited to 256.');
    }
    return CalcMatrix(
      rows.map((row) => row.toList(growable: false)).toList(growable: false),
    );
  }

  static CalcMatrix matrixMultiply(CalcMatrix left, CalcMatrix right) {
    if (left.columnCount != right.rowCount) {
      throw const FormatException('Matrix dimensions do not match.');
    }
    return CalcMatrix(
      List<List<double>>.generate(
        left.rowCount,
        (row) => List<double>.generate(right.columnCount, (column) {
          var sum = 0.0;
          for (var i = 0; i < left.columnCount; i++) {
            sum += left.rows[row][i] * right.rows[i][column];
          }
          return sum;
        }, growable: false),
        growable: false,
      ),
    );
  }

  static double matrixDeterminant(CalcMatrix matrix) {
    if (matrix.rowCount != matrix.columnCount || matrix.rowCount == 0) {
      throw const FormatException('Determinant requires a square matrix.');
    }
    final a = matrix.rows.map((row) => row.toList()).toList();
    var determinant = 1.0;
    for (var column = 0; column < a.length; column++) {
      var pivot = column;
      for (var row = column + 1; row < a.length; row++) {
        if (a[row][column].abs() > a[pivot][column].abs()) {
          pivot = row;
        }
      }
      if (a[pivot][column].abs() < 1e-14) {
        return 0;
      }
      if (pivot != column) {
        final temp = a[pivot];
        a[pivot] = a[column];
        a[column] = temp;
        determinant = -determinant;
      }
      final value = a[column][column];
      determinant *= value;
      for (var row = column + 1; row < a.length; row++) {
        final factor = a[row][column] / value;
        for (var j = column + 1; j < a.length; j++) {
          a[row][j] -= factor * a[column][j];
        }
      }
    }
    return determinant;
  }

  static CalcMatrix matrixInverse(CalcMatrix matrix) {
    if (matrix.rowCount != matrix.columnCount || matrix.rowCount == 0) {
      throw const FormatException('Inverse requires a square matrix.');
    }
    final size = matrix.rowCount;
    final augmented = List<List<double>>.generate(
      size,
      (row) => <double>[
        ...matrix.rows[row],
        ...List<double>.generate(size, (column) => row == column ? 1 : 0),
      ],
    );
    for (var column = 0; column < size; column++) {
      var pivot = column;
      for (var row = column + 1; row < size; row++) {
        if (augmented[row][column].abs() > augmented[pivot][column].abs()) {
          pivot = row;
        }
      }
      if (augmented[pivot][column].abs() < 1e-14) {
        throw const FormatException('Matrix is singular.');
      }
      final row = augmented[pivot];
      augmented[pivot] = augmented[column];
      augmented[column] = row;
      final divisor = augmented[column][column];
      for (var j = 0; j < 2 * size; j++) {
        augmented[column][j] /= divisor;
      }
      for (var i = 0; i < size; i++) {
        if (i == column) {
          continue;
        }
        final factor = augmented[i][column];
        for (var j = 0; j < 2 * size; j++) {
          augmented[i][j] -= factor * augmented[column][j];
        }
      }
    }
    return CalcMatrix(
      augmented
          .map((row) => row.sublist(size).toList(growable: false))
          .toList(growable: false),
    );
  }

  static CalcMatrix matrixAdd(
    CalcMatrix left,
    CalcMatrix right, {
    bool subtract = false,
  }) {
    if (left.rowCount != right.rowCount ||
        left.columnCount != right.columnCount) {
      throw const FormatException('Matrix dimensions do not match.');
    }
    return CalcMatrix(
      List<List<double>>.generate(
        left.rowCount,
        (row) => List<double>.generate(
          left.columnCount,
          (column) =>
              left.rows[row][column] +
              (subtract ? -right.rows[row][column] : right.rows[row][column]),
          growable: false,
        ),
        growable: false,
      ),
    );
  }

  static CalcMatrix matrixRref(CalcMatrix matrix) {
    final values = matrix.rows.map((row) => row.toList()).toList();
    var pivotRow = 0;
    for (
      var column = 0;
      column < matrix.columnCount && pivotRow < matrix.rowCount;
      column++
    ) {
      var pivot = pivotRow;
      for (var row = pivotRow + 1; row < matrix.rowCount; row++) {
        if (values[row][column].abs() > values[pivot][column].abs()) {
          pivot = row;
        }
      }
      if (values[pivot][column].abs() < 1e-14) {
        continue;
      }
      final swap = values[pivot];
      values[pivot] = values[pivotRow];
      values[pivotRow] = swap;
      final divisor = values[pivotRow][column];
      for (var j = 0; j < matrix.columnCount; j++) {
        values[pivotRow][j] /= divisor;
      }
      for (var row = 0; row < matrix.rowCount; row++) {
        if (row == pivotRow) {
          continue;
        }
        final factor = values[row][column];
        for (var j = 0; j < matrix.columnCount; j++) {
          values[row][j] -= factor * values[pivotRow][j];
        }
      }
      pivotRow++;
    }
    return CalcMatrix(
      values.map((row) => row.toList(growable: false)).toList(growable: false),
    );
  }

  static int matrixRank(CalcMatrix matrix) {
    final rref = matrixRref(matrix);
    return rref.rows
        .where((row) => row.any((value) => value.abs() > 1e-10))
        .length;
  }

  static List<double> eigenvalues2x2(CalcMatrix matrix) {
    if (matrix.rowCount != 2 || matrix.columnCount != 2) {
      throw const FormatException(
        'This eigenvalue helper requires a 2×2 matrix.',
      );
    }
    final trace = matrix.rows[0][0] + matrix.rows[1][1];
    final determinant = matrixDeterminant(matrix);
    final discriminant = trace * trace - 4 * determinant;
    if (discriminant < 0) return const <double>[];
    final root = math.sqrt(discriminant);
    return <double>[(trace + root) / 2, (trace - root) / 2];
  }

  static SparseMatrix parseSparseMatrix(int rows, int columns, String input) {
    if (rows < 1 || columns < 1 || rows > 10000 || columns > 10000) {
      throw const FormatException(
        'Sparse matrix dimensions must be between 1 and 10000.',
      );
    }
    final entries = <SparseEntry>[];
    for (final token in input.split(';')) {
      final cells = token.trim().split(RegExp(r'[,\s]+'));
      if (token.trim().isEmpty) {
        continue;
      }
      if (cells.length != 3) {
        throw const FormatException('Sparse entries use row,column,value.');
      }
      final row = int.tryParse(cells[0]);
      final column = int.tryParse(cells[1]);
      final value = double.tryParse(cells[2]);
      if (row == null ||
          column == null ||
          value == null ||
          !value.isFinite ||
          row < 0 ||
          row >= rows ||
          column < 0 ||
          column >= columns) {
        throw const FormatException('Sparse entry is outside the matrix.');
      }
      entries.add(SparseEntry(row, column, value));
    }
    return SparseMatrix(rows: rows, columns: columns, entries: entries);
  }

  static List<double> sparseMatVec(SparseMatrix matrix, List<double> vector) {
    if (vector.length != matrix.columns ||
        vector.any((value) => !value.isFinite)) {
      throw const FormatException(
        'Vector dimension or finite values do not match matrix.',
      );
    }
    final result = List<double>.filled(matrix.rows, 0);
    for (final entry in matrix.entries) {
      result[entry.row] += entry.value * vector[entry.column];
    }
    return result;
  }

  static List<double>? conjugateGradient(
    SparseMatrix matrix,
    List<double> rhs, {
    List<double>? initial,
    int maxIterations = 1000,
    double tolerance = 1e-10,
  }) {
    if (matrix.rows != matrix.columns || rhs.length != matrix.rows) return null;
    if (initial != null && initial.length != matrix.columns) return null;
    final x = initial == null
        ? List<double>.filled(matrix.rows, 0)
        : List<double>.from(initial);
    List<double> subtract(List<double> a, List<double> b) =>
        List<double>.generate(
          a.length,
          (index) => a[index] - b[index],
          growable: false,
        );
    double dot(List<double> a, List<double> b) {
      var result = 0.0;
      for (var index = 0; index < a.length; index++) {
        result += a[index] * b[index];
      }
      return result;
    }

    var residual = subtract(rhs, sparseMatVec(matrix, x));
    var direction = List<double>.from(residual);
    var residualNorm = dot(residual, residual);
    for (var iteration = 0; iteration < maxIterations; iteration++) {
      final product = sparseMatVec(matrix, direction);
      final denominator = dot(direction, product);
      if (denominator.abs() < 1e-20) return null;
      final alpha = residualNorm / denominator;
      for (var index = 0; index < x.length; index++) {
        x[index] += alpha * direction[index];
        residual[index] -= alpha * product[index];
      }
      final nextNorm = dot(residual, residual);
      if (math.sqrt(nextNorm) <= tolerance) return x;
      final beta = nextNorm / residualNorm;
      for (var index = 0; index < direction.length; index++) {
        direction[index] = residual[index] + beta * direction[index];
      }
      residualNorm = nextNorm;
    }
    return null;
  }

  static int _nextPowerOfTwo(int value) {
    var result = 1;
    while (result < value && result < 1 << 15) {
      result <<= 1;
    }
    return result;
  }

  static void _fft(List<double> real, List<double> imaginary) {
    final n = real.length;
    for (var i = 1, j = 0; i < n; i++) {
      var bit = n >> 1;
      for (; (j & bit) != 0; bit >>= 1) {
        j ^= bit;
      }
      j ^= bit;
      if (i < j) {
        final realValue = real[i];
        real[i] = real[j];
        real[j] = realValue;
        final imaginaryValue = imaginary[i];
        imaginary[i] = imaginary[j];
        imaginary[j] = imaginaryValue;
      }
    }
    for (var length = 2; length <= n; length <<= 1) {
      final angle = -2 * math.pi / length;
      final wReal = math.cos(angle);
      final wImaginary = math.sin(angle);
      for (var start = 0; start < n; start += length) {
        var currentReal = 1.0;
        var currentImaginary = 0.0;
        final half = length ~/ 2;
        for (var i = 0; i < half; i++) {
          final even = start + i;
          final odd = even + half;
          final productReal =
              currentReal * real[odd] - currentImaginary * imaginary[odd];
          final productImaginary =
              currentReal * imaginary[odd] + currentImaginary * real[odd];
          final evenReal = real[even];
          final evenImaginary = imaginary[even];
          real[even] = evenReal + productReal;
          imaginary[even] = evenImaginary + productImaginary;
          real[odd] = evenReal - productReal;
          imaginary[odd] = evenImaginary - productImaginary;
          final nextReal = currentReal * wReal - currentImaginary * wImaginary;
          currentImaginary =
              currentReal * wImaginary + currentImaginary * wReal;
          currentReal = nextReal;
        }
      }
    }
  }

  static double _simpson(double a, double b, double fa, double fm, double fb) =>
      (b - a) * (fa + 4 * fm + fb) / 6;

  static double? _adaptiveSimpson(
    double Function(double) function,
    double a,
    double b,
    double tolerance,
    double whole,
    double fa,
    double fm,
    double fb,
    int depth,
  ) {
    final middle = (a + b) / 2;
    final leftMiddle = (a + middle) / 2;
    final rightMiddle = (middle + b) / 2;
    final fLeftMiddle = function(leftMiddle);
    final fRightMiddle = function(rightMiddle);
    if (!fLeftMiddle.isFinite || !fRightMiddle.isFinite) {
      return null;
    }
    final left = _simpson(a, middle, fa, fLeftMiddle, fm);
    final right = _simpson(middle, b, fm, fRightMiddle, fb);
    final delta = left + right - whole;
    if (depth <= 0 || delta.abs() <= 15 * tolerance) {
      return left + right + delta / 15;
    }
    final leftResult = _adaptiveSimpson(
      function,
      a,
      middle,
      tolerance / 2,
      left,
      fa,
      fLeftMiddle,
      fm,
      depth - 1,
    );
    final rightResult = _adaptiveSimpson(
      function,
      middle,
      b,
      tolerance / 2,
      right,
      fm,
      fRightMiddle,
      fb,
      depth - 1,
    );
    if (leftResult == null || rightResult == null) {
      return null;
    }
    return leftResult + rightResult;
  }

  static List<double>? _solveAugmented(List<List<double>> matrix) {
    final rows = matrix.length;
    if (rows == 0 || matrix.any((row) => row.length != rows + 1)) return null;
    for (var column = 0; column < rows; column++) {
      var pivot = column;
      for (var row = column + 1; row < rows; row++) {
        if (matrix[row][column].abs() > matrix[pivot][column].abs()) {
          pivot = row;
        }
      }
      if (matrix[pivot][column].abs() < 1e-14) return null;
      final swap = matrix[pivot];
      matrix[pivot] = matrix[column];
      matrix[column] = swap;
      final divisor = matrix[column][column];
      for (var j = column; j <= rows; j++) {
        matrix[column][j] /= divisor;
      }
      for (var row = 0; row < rows; row++) {
        if (row == column) {
          continue;
        }
        final factor = matrix[row][column];
        for (var j = column; j <= rows; j++) {
          matrix[row][j] -= factor * matrix[column][j];
        }
      }
    }
    return List<double>.generate(rows, (index) => matrix[index][rows]);
  }

  static double _evaluatePolynomial(List<double> coefficients, double x) {
    var result = 0.0;
    for (var index = coefficients.length - 1; index >= 0; index--) {
      result = result * x + coefficients[index];
    }
    return result;
  }

  static double _logGamma(double z) {
    const coefficients = <double>[
      676.5203681218851,
      -1259.1392167224028,
      771.32342877765313,
      -176.61502916214059,
      12.507343278686905,
      -0.13857109526572012,
      9.9843695780195716e-6,
      1.5056327351493116e-7,
    ];
    if (z < .5) {
      return math.log(math.pi) -
          math.log(math.sin(math.pi * z)) -
          _logGamma(1 - z);
    }
    var value = .99999999999980993;
    final shifted = z - 1;
    for (var index = 0; index < coefficients.length; index++) {
      value += coefficients[index] / (shifted + index + 1);
    }
    final t = shifted + coefficients.length - .5;
    return .5 * math.log(2 * math.pi) +
        (shifted + .5) * math.log(t) -
        t +
        math.log(value);
  }

  static double _logBeta(double a, double b) =>
      _logGamma(a) + _logGamma(b) - _logGamma(a + b);

  static double _erf(double x) {
    // Abramowitz and Stegun 7.1.26; maximum error is below 1.5e-7.
    final sign = x < 0 ? -1 : 1;
    final value = x.abs();
    final t = 1 / (1 + .3275911 * value);
    final polynomial =
        (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t -
                    .284496736) *
                t +
            .254829592) *
        t;
    return sign * (1 - polynomial * math.exp(-value * value));
  }

  static double _regularizedGamma(double shape, double value) {
    if (value <= 0) return 0;
    if (value < shape + 1) {
      var sum = 1 / shape;
      var term = sum;
      for (var index = 1; index < 1000; index++) {
        term *= value / (shape + index);
        sum += term;
        if (term.abs() < sum.abs() * 1e-14) break;
      }
      return sum *
          math.exp(-value + shape * math.log(value) - _logGamma(shape));
    }
    var b = value + 1 - shape;
    var c = 1 / 1e-300;
    var d = 1 / b;
    var h = d;
    for (var index = 1; index < 1000; index++) {
      final an = -index * (index - shape);
      b += 2;
      d = an * d + b;
      if (d.abs() < 1e-300) d = 1e-300;
      c = b + an / c;
      if (c.abs() < 1e-300) c = 1e-300;
      d = 1 / d;
      final delta = d * c;
      h *= delta;
      if ((delta - 1).abs() < 1e-14) break;
    }
    final upper =
        math.exp(-value + shape * math.log(value) - _logGamma(shape)) * h;
    return (1 - upper).clamp(0, 1).toDouble();
  }

  static double _regularizedBeta(double x, double a, double b) {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    final factor = math.exp(
      a * math.log(x) + b * math.log(1 - x) - _logBeta(a, b),
    );
    final fraction = x < (a + 1) / (a + b + 2)
        ? factor * _betaFraction(x, a, b) / a
        : 1 - factor * _betaFraction(1 - x, b, a) / b;
    return fraction.clamp(0, 1).toDouble();
  }

  static double _betaFraction(double x, double a, double b) {
    var qab = a + b;
    var qap = a + 1;
    var qam = a - 1;
    var c = 1.0;
    var d = 1 - qab * x / qap;
    if (d.abs() < 1e-300) d = 1e-300;
    d = 1 / d;
    var h = d;
    for (var index = 1; index <= 200; index++) {
      final m2 = 2 * index;
      var aa = index * (b - index) * x / ((qam + m2) * (a + m2));
      d = 1 + aa * d;
      if (d.abs() < 1e-300) d = 1e-300;
      c = 1 + aa / c;
      if (c.abs() < 1e-300) c = 1e-300;
      d = 1 / d;
      h *= d * c;
      aa = -(a + index) * (qab + index) * x / ((a + m2) * (qap + m2));
      d = 1 + aa * d;
      if (d.abs() < 1e-300) d = 1e-300;
      c = 1 + aa / c;
      if (c.abs() < 1e-300) c = 1e-300;
      d = 1 / d;
      final delta = d * c;
      h *= delta;
      if ((delta - 1).abs() < 3e-14) break;
    }
    return h;
  }

  static double _logCombination(int n, int k) =>
      _logGamma(n + 1) - _logGamma(k + 1) - _logGamma(n - k + 1);

  static double _median(List<double> values) {
    if (values.isEmpty) {
      return double.nan;
    }
    final middle = values.length ~/ 2;
    return values.length.isOdd
        ? values[middle]
        : (values[middle - 1] + values[middle]) / 2;
  }
}
