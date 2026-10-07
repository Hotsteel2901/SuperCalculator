import 'package:flutter/foundation.dart';

import 'calculation_models.dart';
import 'computation.dart';

/// Isolate boundary for deterministic Dart fallback work.
///
/// Flutter's Web implementation executes `compute` without spawning a native
/// isolate, while Android, iOS, desktop and tests use a worker isolate. Keeping
/// the request objects small makes the boundary replaceable by a worker pool or
/// a native task queue later without changing feature pages.
class ComputationDispatcher {
  const ComputationDispatcher._();

  static Future<List<double?>> evaluateArray(
    String expression,
    List<double> xs,
  ) => compute(_evaluateArrayTask, _ArrayTask(expression: expression, xs: xs));

  static Future<CalcEvaluationValue> evaluate(
    String expression,
    double x, {
    double y = 0,
  }) =>
      compute(_evaluateTask, _EvaluateTask(expression: expression, x: x, y: y));

  static Future<double?> derivative(
    String expression,
    double x, {
    double? step,
    bool second = false,
  }) => compute(
    _derivativeTask,
    _DerivativeTask(expression: expression, x: x, step: step, second: second),
  );

  static Future<double?> integrate(
    String expression,
    double a,
    double b, {
    double tolerance = 1e-8,
  }) => compute(
    _integrateTask,
    _IntegrateTask(expression: expression, a: a, b: b, tolerance: tolerance),
  );

  static Future<double?> solve(
    String expression, {
    double guess = 0,
    double minimum = -100,
    double maximum = 100,
    double tolerance = 1e-10,
    int maxIterations = 100,
  }) => compute(
    _solveTask,
    _SolveTask(
      expression: expression,
      guess: guess,
      minimum: minimum,
      maximum: maximum,
      tolerance: tolerance,
      maxIterations: maxIterations,
    ),
  );

  static Future<CalcOdeSolution> ode(
    String expression, {
    required double x0,
    required double y0,
    required double xEnd,
    int steps = 200,
  }) => compute(
    _odeTask,
    _OdeTask(expression: expression, x0: x0, y0: y0, xEnd: xEnd, steps: steps),
  );

  static Future<CalcSpectrum> spectrum(
    String expression, {
    required double a,
    required double b,
    int samples = 1024,
  }) => compute(
    _spectrumTask,
    _SpectrumTask(expression: expression, a: a, b: b, samples: samples),
  );

  static Future<CalcStatistics> statistics(List<double> values) =>
      compute(_statisticsTask, values);

  static Future<CalcRegression> linearRegression(
    List<double> xs,
    List<double> ys,
  ) => compute(_regressionTask, _RegressionTask(xs: xs, ys: ys));
}

class CalcEvaluationValue {
  const CalcEvaluationValue({required this.value, this.error});

  final double? value;
  final String? error;
}

class _ArrayTask {
  const _ArrayTask({required this.expression, required this.xs});

  final String expression;
  final List<double> xs;
}

List<double?> _evaluateArrayTask(_ArrayTask task) =>
    DartComputation.evaluateArray(task.expression, task.xs);

class _EvaluateTask {
  const _EvaluateTask({
    required this.expression,
    required this.x,
    required this.y,
  });

  final String expression;
  final double x;
  final double y;
}

CalcEvaluationValue _evaluateTask(_EvaluateTask task) {
  try {
    final value = DartComputation.evaluate(task.expression, task.x, task.y);
    return value.isFinite
        ? CalcEvaluationValue(value: value)
        : const CalcEvaluationValue(
            error: 'The expression produced a non-finite value.',
          );
  } on FormatException catch (error) {
    return CalcEvaluationValue(error: error.message);
  } catch (_) {
    return const CalcEvaluationValue(
      error: 'The expression could not be evaluated.',
    );
  }
}

class _DerivativeTask {
  const _DerivativeTask({
    required this.expression,
    required this.x,
    required this.step,
    required this.second,
  });

  final String expression;
  final double x;
  final double? step;
  final bool second;
}

double? _derivativeTask(_DerivativeTask task) => DartComputation.derivative(
  task.expression,
  task.x,
  step: task.step,
  second: task.second,
);

class _IntegrateTask {
  const _IntegrateTask({
    required this.expression,
    required this.a,
    required this.b,
    required this.tolerance,
  });

  final String expression;
  final double a;
  final double b;
  final double tolerance;
}

double? _integrateTask(_IntegrateTask task) => DartComputation.integrate(
  task.expression,
  task.a,
  task.b,
  tolerance: task.tolerance,
);

class _SolveTask {
  const _SolveTask({
    required this.expression,
    required this.guess,
    required this.minimum,
    required this.maximum,
    required this.tolerance,
    required this.maxIterations,
  });

  final String expression;
  final double guess;
  final double minimum;
  final double maximum;
  final double tolerance;
  final int maxIterations;
}

double? _solveTask(_SolveTask task) => DartComputation.solve(
  task.expression,
  guess: task.guess,
  minimum: task.minimum,
  maximum: task.maximum,
  tolerance: task.tolerance,
  maxIterations: task.maxIterations,
);

class _OdeTask {
  const _OdeTask({
    required this.expression,
    required this.x0,
    required this.y0,
    required this.xEnd,
    required this.steps,
  });

  final String expression;
  final double x0;
  final double y0;
  final double xEnd;
  final int steps;
}

CalcOdeSolution _odeTask(_OdeTask task) => DartComputation.ode(
  task.expression,
  x0: task.x0,
  y0: task.y0,
  xEnd: task.xEnd,
  steps: task.steps,
);

class _SpectrumTask {
  const _SpectrumTask({
    required this.expression,
    required this.a,
    required this.b,
    required this.samples,
  });

  final String expression;
  final double a;
  final double b;
  final int samples;
}

CalcSpectrum _spectrumTask(_SpectrumTask task) => DartComputation.spectrum(
  task.expression,
  a: task.a,
  b: task.b,
  samples: task.samples,
);

CalcStatistics _statisticsTask(List<double> values) =>
    DartComputation.statistics(values);

class _RegressionTask {
  const _RegressionTask({required this.xs, required this.ys});

  final List<double> xs;
  final List<double> ys;
}

CalcRegression _regressionTask(_RegressionTask task) =>
    DartComputation.linearRegression(task.xs, task.ys);
