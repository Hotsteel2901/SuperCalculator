import 'dart:math' as math;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/calc_backend.dart';
import '../../core/backend/providers.dart';
import '../../core/history/history_repository.dart';
import '../../core/plot/plot_point.dart';

final calculatorControllerProvider =
    NotifierProvider<CalculatorController, CalculatorState>(
      CalculatorController.new,
    );

class CalculatorState {
  const CalculatorState({
    required this.expression,
    required this.secondaryExpression,
    required this.xText,
    required this.mode,
    required this.backend,
    this.parameterStart = 0,
    this.parameterEnd = 2 * math.pi,
    this.value,
    this.error,
    this.isCalculating = false,
    this.points = const <PlotPoint>[],
    this.intersectionPoints = const <PlotPoint>[],
    this.markedPoints = const <PlotPoint>[],
    this.parameters = const <String, double>{},
  });

  const CalculatorState.initial()
    : expression = 'sin(x)',
      secondaryExpression = 'cos(x)',
      xText = '0',
      mode = 'function',
      backend = 'Dart fallback',
      parameterStart = 0,
      parameterEnd = 2 * math.pi,
      value = null,
      error = null,
      isCalculating = false,
      points = const <PlotPoint>[],
      intersectionPoints = const <PlotPoint>[],
      markedPoints = const <PlotPoint>[],
      parameters = const <String, double>{};

  final String expression;
  final String secondaryExpression;
  final String xText;
  final String mode;
  final String backend;
  final double parameterStart;
  final double parameterEnd;
  final double? value;
  final String? error;
  final bool isCalculating;
  final List<PlotPoint> points;
  final List<PlotPoint> intersectionPoints;
  final List<PlotPoint> markedPoints;
  final Map<String, double> parameters;

  CalculatorState copyWith({
    String? expression,
    String? secondaryExpression,
    String? xText,
    String? mode,
    String? backend,
    double? parameterStart,
    double? parameterEnd,
    double? value,
    bool clearValue = false,
    String? error,
    bool clearError = false,
    bool? isCalculating,
    List<PlotPoint>? points,
    List<PlotPoint>? intersectionPoints,
    List<PlotPoint>? markedPoints,
    Map<String, double>? parameters,
  }) {
    return CalculatorState(
      expression: expression ?? this.expression,
      secondaryExpression: secondaryExpression ?? this.secondaryExpression,
      xText: xText ?? this.xText,
      mode: mode ?? this.mode,
      backend: backend ?? this.backend,
      parameterStart: parameterStart ?? this.parameterStart,
      parameterEnd: parameterEnd ?? this.parameterEnd,
      value: clearValue ? null : value ?? this.value,
      error: clearError ? null : error ?? this.error,
      isCalculating: isCalculating ?? this.isCalculating,
      points: points ?? this.points,
      intersectionPoints: intersectionPoints ?? this.intersectionPoints,
      markedPoints: markedPoints ?? this.markedPoints,
      parameters: parameters ?? this.parameters,
    );
  }
}

class CalculatorController extends Notifier<CalculatorState> {
  @override
  CalculatorState build() => const CalculatorState.initial();

  void setExpression(String value) {
    state = state.copyWith(
      expression: value,
      clearError: true,
      intersectionPoints: const <PlotPoint>[],
    );
  }

  void setSecondaryExpression(String value) {
    state = state.copyWith(
      secondaryExpression: value,
      clearError: true,
      intersectionPoints: const <PlotPoint>[],
    );
  }

  void setParameter(String name, double value) {
    if (name.isEmpty || !value.isFinite) return;
    final parameters = <String, double>{...state.parameters, name: value};
    state = state.copyWith(parameters: parameters, clearError: true);
  }

  List<String> parameterNames({String? expression, String? secondary}) {
    final source =
        '${expression ?? state.expression} ${secondary ?? state.secondaryExpression}';
    final known = <String>{
      'x',
      'y',
      't',
      'theta',
      'pi',
      'e',
      'sin',
      'cos',
      'tan',
      'asin',
      'acos',
      'atan',
      'sinh',
      'cosh',
      'tanh',
      'sqrt',
      'cbrt',
      'abs',
      'exp',
      'ln',
      'log',
      'log10',
      'floor',
      'ceil',
      'round',
      'sign',
      'min',
      'max',
      'mod',
    };
    final names = <String>{};
    for (final match in RegExp(r'[A-Za-z_][A-Za-z0-9_]*').allMatches(source)) {
      final name = match.group(0)!;
      if (!known.contains(name.toLowerCase())) names.add(name);
    }
    final result = names.toList()..sort();
    return result;
  }

  String _withParameters(String expression) {
    var result = expression;
    final names = parameterNames(expression: expression, secondary: '');
    for (final name in names) {
      final value = state.parameters[name] ?? 1.0;
      if (!value.isFinite) continue;
      result = result.replaceAll(
        RegExp(r'\b' + RegExp.escape(name) + r'\b'),
        '(${value.toStringAsPrecision(15)})',
      );
    }
    return result;
  }

  String _withPlotVariable(String expression) {
    return expression.replaceAll(RegExp(r'\b(?:t|theta)\b'), 'x');
  }

  void setX(String value) {
    state = state.copyWith(xText: value, clearError: true);
  }

  void setParameterRange(double start, double end) {
    if (!start.isFinite || !end.isFinite || start >= end) {
      state = state.copyWith(
        error: 'The parameter range must be finite and increasing.',
      );
      return;
    }
    state = state.copyWith(
      parameterStart: start,
      parameterEnd: end,
      clearError: true,
    );
  }

  void setMode(String value) {
    state = state.copyWith(
      mode: value,
      clearError: true,
      points: const <PlotPoint>[],
      intersectionPoints: const <PlotPoint>[],
    );
  }

  Future<void> evaluate() async {
    final backend = ref.read(calcBackendProvider);
    final mode = state.mode;
    final rawExpression = state.expression.trim();
    final rawSecondary = state.secondaryExpression.trim();
    final parameterizedExpression = _withParameters(rawExpression);
    final parameterizedSecondary = _withParameters(rawSecondary);
    final expression = mode == 'parametric' || mode == 'polar'
        ? _withPlotVariable(parameterizedExpression)
        : parameterizedExpression;
    final secondary = mode == 'parametric'
        ? _withPlotVariable(parameterizedSecondary)
        : parameterizedSecondary;
    final parsedX = double.tryParse(state.xText.trim());
    final x = parsedX ?? 0;
    if (rawExpression.isEmpty) {
      state = state.copyWith(
        error: 'Expression cannot be empty.',
        clearValue: true,
      );
      return;
    }
    if (mode == 'function' && (parsedX == null || !parsedX.isFinite)) {
      state = state.copyWith(
        error: 'The x argument must be a finite number.',
        clearValue: true,
      );
      return;
    }

    state = state.copyWith(
      backend: backend.name,
      isCalculating: true,
      clearError: true,
      clearValue: true,
      points: const <PlotPoint>[],
      intersectionPoints: const <PlotPoint>[],
    );

    try {
      if (mode == 'function') {
        final result = await backend.evaluate(expression, x);
        final xs = List<double>.generate(
          481,
          (index) => (-10 + index / 24).toDouble(),
          growable: false,
        );
        final ys = await backend.evaluateArray(expression, xs);
        final points = _pointsFromArrays(xs, ys);
        state = state.copyWith(
          backend: result.backend,
          value: result.value,
          error: result.error,
          isCalculating: false,
          points: points,
        );
        if (result.value != null) {
          ref
              .read(calculationHistoryProvider.notifier)
              .add(
                expression: rawExpression,
                result: result.value!.toStringAsPrecision(12),
                backend: result.backend,
              );
        }
        return;
      }

      final points = await _sampleSpecialMode(
        backend,
        mode,
        expression,
        secondary,
        parameterStart: state.parameterStart,
        parameterEnd: state.parameterEnd,
      );
      var intersectionPoints = const <PlotPoint>[];
      if (mode == 'multi') {
        try {
          intersectionPoints = await _intersectionPoints(backend, expression);
        } on FormatException {
          // Keep valid curves visible even when one invalid curve cannot
          // participate in the intersection query.
        }
      }
      state = state.copyWith(
        backend: backend.name,
        isCalculating: false,
        points: points,
        intersectionPoints: intersectionPoints,
        error: points.isEmpty ? 'The plot could not be evaluated.' : null,
      );
      if (points.isNotEmpty) {
        ref
            .read(calculationHistoryProvider.notifier)
            .add(
              expression: '$mode: $rawExpression',
              result: '${points.length} plotted points',
              backend: backend.name,
            );
      }
    } on FormatException catch (error) {
      state = state.copyWith(
        isCalculating: false,
        error: error.message,
        clearValue: true,
      );
    } catch (_) {
      state = state.copyWith(
        isCalculating: false,
        error: 'The expression could not be evaluated.',
        clearValue: true,
      );
    }
  }

  Future<List<PlotPoint>> _intersectionPoints(
    CalcBackend backend,
    String expression,
  ) async {
    final expressions = expression
        .split(RegExp(r'[;\n]+'))
        .map((value) => value.trim())
        .where((value) => value.isNotEmpty)
        .toList(growable: false);
    if (expressions.length < 2) return const <PlotPoint>[];

    final result = <PlotPoint>[];
    for (var left = 0; left < expressions.length - 1; left++) {
      for (var right = left + 1; right < expressions.length; right++) {
        final roots = await backend.intersections(
          expressions[left],
          expressions[right],
          -10,
          10,
          samples: 512,
          tolerance: 1e-7,
        );
        if (roots.isEmpty) continue;
        final ys = await backend.evaluateArray(expressions[left], roots);
        for (var index = 0; index < roots.length; index++) {
          final x = roots[index];
          final y = index < ys.length ? ys[index] : null;
          if (!x.isFinite || y == null || !y.isFinite) continue;
          final point = PlotPoint(x, y);
          final duplicate = result.any(
            (existing) =>
                (existing.x - x).abs() < 1e-6 && (existing.y - y).abs() < 1e-6,
          );
          if (!duplicate) result.add(point);
        }
      }
    }
    result.sort((a, b) => a.x.compareTo(b.x));
    return result;
  }

  Future<void> findIntersections() async {
    final backend = ref.read(calcBackendProvider);
    final expression = _withParameters(state.expression.trim());
    if (state.mode != 'multi') {
      state = state.copyWith(
        error: 'Choose multi-curve mode to query intersections.',
      );
      return;
    }
    state = state.copyWith(isCalculating: true, clearError: true);
    try {
      final points = await _intersectionPoints(backend, expression);
      state = state.copyWith(
        isCalculating: false,
        intersectionPoints: points,
        error: points.isEmpty ? 'No finite intersections were found.' : null,
      );
    } catch (_) {
      state = state.copyWith(
        isCalculating: false,
        error: 'The intersections could not be evaluated.',
      );
    }
  }

  void addMarkedPoint(PlotPoint point) {
    if (!point.isFinite) return;
    final duplicate = state.markedPoints.any(
      (existing) =>
          (existing.x - point.x).abs() < 1e-6 &&
          (existing.y - point.y).abs() < 1e-6,
    );
    if (duplicate) return;
    state = state.copyWith(
      markedPoints: <PlotPoint>[...state.markedPoints, point],
    );
  }

  void removeNearestMarkedPoint(PlotPoint point, {double tolerance = .5}) {
    if (state.markedPoints.isEmpty) return;
    var nearest = -1;
    var distance = double.infinity;
    for (var index = 0; index < state.markedPoints.length; index++) {
      final current = state.markedPoints[index];
      final dx = current.x - point.x;
      final dy = current.y - point.y;
      final candidate = math.sqrt(dx * dx + dy * dy);
      if (candidate < distance) {
        distance = candidate;
        nearest = index;
      }
    }
    if (nearest < 0 || distance > tolerance) return;
    final points = [...state.markedPoints]..removeAt(nearest);
    state = state.copyWith(markedPoints: points);
  }

  Future<List<PlotPoint>> _sampleSpecialMode(
    CalcBackend backend,
    String mode,
    String expression,
    String secondary, {
    double parameterStart = -math.pi,
    double parameterEnd = math.pi,
  }) async {
    if (mode == 'multi') {
      final expressions = expression
          .split(RegExp(r'[;\n]+'))
          .map((value) => value.trim())
          .where((value) => value.isNotEmpty)
          .toList(growable: false);
      if (expressions.isEmpty) return const <PlotPoint>[];
      final xs = List<double>.generate(
        481,
        (index) => (-10 + index / 24).toDouble(),
        growable: false,
      );
      final points = <PlotPoint>[];
      for (final item in expressions) {
        final values = await backend.evaluateArray(item, xs);
        final curve = _pointsFromArrays(xs, values);
        if (!curve.any((point) => point.isFinite)) continue;
        points
          ..addAll(curve)
          ..add(const PlotPoint(double.nan, double.nan));
      }
      return points;
    }
    if (mode == 'parametric') {
      final ts = List<double>.generate(
        721,
        (index) =>
            parameterStart + (parameterEnd - parameterStart) * index / 720,
        growable: false,
      );
      final xs = await backend.evaluateArray(expression, ts);
      final ys = await backend.evaluateArray(secondary, ts);
      return List<PlotPoint>.generate(ts.length, (index) {
        final x = xs[index];
        final y = ys[index];
        return x != null && y != null && x.isFinite && y.isFinite
            ? PlotPoint(x, y)
            : const PlotPoint(double.nan, double.nan);
      }, growable: false);
    }
    if (mode == 'polar') {
      final angles = List<double>.generate(
        721,
        (index) =>
            parameterStart + (parameterEnd - parameterStart) * index / 720,
        growable: false,
      );
      final radii = await backend.evaluateArray(expression, angles);
      return List<PlotPoint>.generate(angles.length, (index) {
        final radius = radii[index];
        if (radius == null || !radius.isFinite) {
          return const PlotPoint(double.nan, double.nan);
        }
        return PlotPoint(
          radius * math.cos(angles[index]),
          radius * math.sin(angles[index]),
        );
      }, growable: false);
    }

    if (mode == 'surface' || mode == 'contour') {
      final samples = await backend.sampleSurface(
        expression,
        -10,
        10,
        -10,
        10,
        rows: 45,
        columns: 45,
      );
      if (mode == 'surface') {
        // Preserve all three coordinates. The painter applies an interactive
        // projection so the same sampled surface can be rotated and zoomed on
        // touch, pointer and keyboard-driven desktop layouts.
        return samples
            .map((sample) => PlotPoint(sample.x, sample.y, z: sample.value))
            .toList(growable: false);
      }
      final finite = samples
          .map((sample) => sample.value)
          .where((value) => value.isFinite)
          .toList(growable: false);
      if (finite.isEmpty) return const <PlotPoint>[];
      final low = finite.reduce((a, b) => math.min(a, b).toDouble());
      final high = finite.reduce((a, b) => math.max(a, b).toDouble());
      final span = (high - low).abs();
      if (span < 1e-12) return const <PlotPoint>[];
      final points = <PlotPoint>[];
      for (final sample in samples) {
        final normalized = (sample.value - low) / span * 8;
        if ((normalized - normalized.round()).abs() < .08) {
          points.add(PlotPoint(sample.x, sample.y));
        }
      }
      return points;
    }
    if (mode == 'direction') {
      final vectors = await backend.sampleDirectionField(
        expression,
        -10,
        10,
        -10,
        10,
        rows: 20,
        columns: 20,
      );
      final points = <PlotPoint>[];
      for (final vector in vectors) {
        points
          ..add(
            PlotPoint(vector.x - vector.dx * .35, vector.y - vector.dy * .35),
          )
          ..add(
            PlotPoint(vector.x + vector.dx * .35, vector.y + vector.dy * .35),
          )
          ..add(const PlotPoint(double.nan, double.nan));
      }
      return points;
    }
    if (mode == 'vector') {
      final vectors = await backend.sampleVectorField(
        expression,
        secondary,
        -10,
        10,
        -10,
        10,
        rows: 20,
        columns: 20,
      );
      final points = <PlotPoint>[];
      for (final vector in vectors) {
        points
          ..add(
            PlotPoint(vector.x - vector.dx * .35, vector.y - vector.dy * .35),
          )
          ..add(
            PlotPoint(vector.x + vector.dx * .35, vector.y + vector.dy * .35),
          )
          ..add(const PlotPoint(double.nan, double.nan));
      }
      return points;
    }

    final implicit = await backend.sampleImplicit(
      expression,
      -10,
      10,
      -10,
      10,
      rows: 121,
      columns: 121,
      levelTolerance: 10 / 120 * 1.5,
    );
    return implicit
        .map((sample) => PlotPoint(sample.x, sample.y))
        .toList(growable: false);
  }

  List<PlotPoint> _pointsFromArrays(List<double> xs, List<double?> ys) {
    final points = <PlotPoint>[];
    for (var index = 0; index < xs.length; index++) {
      final y = ys[index];
      if (y != null && y.isFinite) {
        points.add(PlotPoint(xs[index], y));
      } else {
        points.add(const PlotPoint(double.nan, double.nan));
      }
    }
    return points;
  }

  void clear() {
    state = const CalculatorState.initial();
  }
}
