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
    return CompiledExpression(source, root);
  }

  static double evaluate(String source, {double x = 0, double y = 0}) {
    return compile(source).evaluate(x: x, y: y);
  }
}

class CompiledExpression {
  const CompiledExpression(this.source, this._root);

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
        return math.sinh(value);
      case 'cosh':
        return math.cosh(value);
      case 'tanh':
        return math.tanh(value);
      default:
        return double.nan;
    }
  }
}

class _ExpressionCompiler {
  _ExpressionCompiler(this.source);

  final String source;
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
    var left = minimum;
    var right = maximum;
    var fLeft = function.evaluate(x: left);
    var fRight = function.evaluate(x: right);
    for (var i = 0; i < maxIterations; i++) {
      final fx = function.evaluate(x: x);
      if (fx.isFinite && fx.abs() <= tolerance) {
        return x;
      }
      final h = 1e-6 * (x.abs() + 1);
      final fp = function.evaluate(x: x + h);
      final fm = function.evaluate(x: x - h);
      final derivative = fp.isFinite && fm.isFinite
          ? (fp - fm) / (2 * h)
          : double.nan;
      var next = double.nan;
      if (derivative.isFinite && derivative.abs() > 1e-14 && fx.isFinite) {
        next = x - fx / derivative;
      }
      if (!next.isFinite || next <= left || next >= right) {
        next = (left + right) / 2;
      }
      final fNext = function.evaluate(x: next);
      if (!fNext.isFinite) {
        return null;
      }
      if (fLeft.isFinite && fLeft.sign != fNext.sign) {
        right = next;
        fRight = fNext;
      } else if (fRight.isFinite && fRight.sign != fNext.sign) {
        left = next;
        fLeft = fNext;
      } else {
        if (next < x) {
          left = next;
          fLeft = fNext;
        } else {
          right = next;
          fRight = fNext;
        }
      }
      x = next;
      if ((right - left).abs() <= tolerance) {
        return x;
      }
    }
    return null;
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
        ? 0
        : values.fold<double>(
                0,
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
    final rows = input
        .trim()
        .split(';')
        .where((row) => row.trim().isNotEmpty)
        .map(
          (row) => row
              .trim()
              .split(RegExp(r'[,\s]+'))
              .map(double.parse)
              .toList(growable: false),
        )
        .toList(growable: false);
    if (rows.isEmpty || rows.any((row) => row.length != rows.first.length)) {
      throw const FormatException('Matrix rows must have equal columns.');
    }
    return CalcMatrix(rows);
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
