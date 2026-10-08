import 'dart:math' as math;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/compute/computation.dart';
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
    this.value,
    this.error,
    this.isCalculating = false,
    this.points = const <PlotPoint>[],
  });

  const CalculatorState.initial()
    : expression = 'sin(x)',
      secondaryExpression = 'cos(x)',
      xText = '0',
      mode = 'function',
      backend = 'Dart fallback',
      value = null,
      error = null,
      isCalculating = false,
      points = const <PlotPoint>[];

  final String expression;
  final String secondaryExpression;
  final String xText;
  final String mode;
  final String backend;
  final double? value;
  final String? error;
  final bool isCalculating;
  final List<PlotPoint> points;

  CalculatorState copyWith({
    String? expression,
    String? secondaryExpression,
    String? xText,
    String? mode,
    String? backend,
    double? value,
    bool clearValue = false,
    String? error,
    bool clearError = false,
    bool? isCalculating,
    List<PlotPoint>? points,
  }) {
    return CalculatorState(
      expression: expression ?? this.expression,
      secondaryExpression: secondaryExpression ?? this.secondaryExpression,
      xText: xText ?? this.xText,
      mode: mode ?? this.mode,
      backend: backend ?? this.backend,
      value: clearValue ? null : value ?? this.value,
      error: clearError ? null : error ?? this.error,
      isCalculating: isCalculating ?? this.isCalculating,
      points: points ?? this.points,
    );
  }
}

class CalculatorController extends Notifier<CalculatorState> {
  @override
  CalculatorState build() => const CalculatorState.initial();

  void setExpression(String value) {
    state = state.copyWith(expression: value, clearError: true);
  }

  void setSecondaryExpression(String value) {
    state = state.copyWith(secondaryExpression: value, clearError: true);
  }

  void setX(String value) {
    state = state.copyWith(xText: value, clearError: true);
  }

  void setMode(String value) {
    state = state.copyWith(
      mode: value,
      clearError: true,
      points: const <PlotPoint>[],
    );
  }

  Future<void> evaluate() async {
    final backend = ref.read(calcBackendProvider);
    final x = double.tryParse(state.xText.trim()) ?? 0;
    final expression = state.expression.trim();
    if (expression.isEmpty) {
      state = state.copyWith(
        error: 'Expression cannot be empty.',
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
    );

    try {
      if (state.mode == 'function') {
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
                expression: expression,
                result: result.value!.toStringAsPrecision(12),
                backend: result.backend,
              );
        }
        return;
      }

      final points = _sampleSpecialMode(
        state.mode,
        expression,
        state.secondaryExpression,
      );
      state = state.copyWith(
        backend: 'Dart sampling',
        isCalculating: false,
        points: points,
        error: points.isEmpty ? 'The plot could not be evaluated.' : null,
      );
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

  List<PlotPoint> _sampleSpecialMode(
    String mode,
    String expression,
    String secondary,
  ) {
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
        final values = DartComputation.evaluateArray(item, xs);
        points
          ..addAll(_pointsFromArrays(xs, values))
          ..add(const PlotPoint(double.nan, double.nan));
      }
      return points;
    }
    if (mode == 'parametric') {
      final ts = List<double>.generate(
        721,
        (index) => -math.pi + 2 * math.pi * index / 720,
        growable: false,
      );
      final xs = DartComputation.evaluateArray(expression, ts);
      final ys = DartComputation.evaluateArray(secondary, ts);
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
        (index) => 2 * math.pi * index / 720,
        growable: false,
      );
      final radii = DartComputation.evaluateArray(expression, angles);
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
      final samples = DartComputation.sampleSurface(
        expression,
        -10,
        10,
        -10,
        10,
        rows: 45,
        columns: 45,
      );
      if (mode == 'surface') {
        // Isometric projection keeps the Web/desktop preview lightweight while
        // preserving the full z=f(x,y) sample set for a future 3D renderer.
        return samples
            .map((sample) {
              final projectedX = sample.x + sample.y * .35;
              final projectedY = sample.value - sample.y * .25;
              return PlotPoint(projectedX, projectedY);
            })
            .toList(growable: false);
      }
      final finite = samples
          .map((sample) => sample.value)
          .where((value) => value.isFinite)
          .toList();
      if (finite.isEmpty) return const <PlotPoint>[];
      final level = finite.reduce((a, b) => a + b) / finite.length;
      return samples
          .where((sample) => (sample.value - level).abs() < .15)
          .map((sample) => PlotPoint(sample.x, sample.y))
          .toList(growable: false);
    }
    if (mode == 'direction') {
      final vectors = DartComputation.sampleDirectionField(
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
      final vectors = DartComputation.sampleVectorField(
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

    // Implicit curves are represented by a bounded contour sample. A small
    // tolerance is sufficient for the preview and keeps rendering responsive;
    // the native contour API remains available for a future high-resolution
    // export surface.
    final compiled = ExpressionEngine.compile(expression);
    final points = <PlotPoint>[];
    const grid = 121;
    const min = -10.0;
    const max = 10.0;
    const step = (max - min) / (grid - 1);
    for (var row = 0; row < grid; row++) {
      final y = min + row * step;
      for (var column = 0; column < grid; column++) {
        final x = min + column * step;
        final value = compiled.evaluate(x: x, y: y);
        if (value.isFinite && value.abs() < step * 1.5) {
          points.add(PlotPoint(x, y));
        }
      }
    }
    return points;
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
