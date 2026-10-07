import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/calc_backend.dart';
import '../../core/backend/providers.dart';
import '../../core/plot/plot_point.dart';

final calculatorControllerProvider =
    NotifierProvider<CalculatorController, CalculatorState>(
      CalculatorController.new,
    );

class CalculatorState {
  const CalculatorState({
    required this.expression,
    required this.xText,
    required this.backend,
    this.value,
    this.error,
    this.isCalculating = false,
    this.points = const <PlotPoint>[],
  });

  const CalculatorState.initial()
    : expression = 'sin(x)',
      xText = '0',
      backend = 'Dart fallback',
      value = null,
      error = null,
      isCalculating = false,
      points = const <PlotPoint>[];

  final String expression;
  final String xText;
  final String backend;
  final double? value;
  final String? error;
  final bool isCalculating;
  final List<PlotPoint> points;

  CalculatorState copyWith({
    String? expression,
    String? xText,
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
      xText: xText ?? this.xText,
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

  void setX(String value) {
    state = state.copyWith(xText: value, clearError: true);
  }

  Future<void> evaluate() async {
    final backend = ref.read(calcBackendProvider);
    final x = double.tryParse(state.xText.trim());
    if (x == null) {
      state = state.copyWith(error: 'x must be a number.', clearValue: true);
      return;
    }
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

    final result = await backend.evaluate(expression, x);
    final xs = List<double>.generate(
      241,
      (index) => (-10 + index / 12).toDouble(),
      growable: false,
    );
    final ys = await backend.evaluateArray(expression, xs);
    final points = <PlotPoint>[];
    for (var index = 0; index < xs.length; index++) {
      final y = ys[index];
      if (y != null && y.isFinite) {
        points.add(PlotPoint(xs[index], y));
      }
    }

    state = state.copyWith(
      backend: result.backend,
      value: result.value,
      error: result.error,
      isCalculating: false,
      points: points,
    );
  }

  void clear() {
    state = const CalculatorState.initial();
  }
}
