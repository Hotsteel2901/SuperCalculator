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

  static Future<double?> limit(
    String expression,
    double point, {
    double tolerance = 1e-8,
    int maxLevel = 10,
    String side = 'two-sided',
  }) => compute(
    _limitTask,
    _LimitTask(
      expression: expression,
      point: point,
      tolerance: tolerance,
      maxLevel: maxLevel,
      side: side,
    ),
  );

  static Future<double?> nthDerivative(
    String expression,
    double point,
    int order, {
    double step = 1e-4,
  }) => compute(
    _nthDerivativeTask,
    _NthDerivativeTask(
      expression: expression,
      point: point,
      order: order,
      step: step,
    ),
  );

  static Future<double?> extremum(
    String expression,
    double start,
    double end, {
    bool minimum = true,
    double tolerance = 1e-8,
  }) => compute(
    _extremumTask,
    _ExtremumTask(
      expression: expression,
      start: start,
      end: end,
      minimum: minimum,
      tolerance: tolerance,
    ),
  );

  static Future<double?> areaBetweenCurves(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    double tolerance = 1e-8,
  }) => compute(
    _areaTask,
    _AreaTask(
      expressionF: expressionF,
      expressionG: expressionG,
      start: start,
      end: end,
      tolerance: tolerance,
    ),
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

  static Future<CalcPolynomialRegression> polynomialRegression(
    List<double> xs,
    List<double> ys, {
    int degree = 2,
  }) => compute(
    _polynomialRegressionTask,
    _PolynomialRegressionTask(xs: xs, ys: ys, degree: degree),
  );

  static Future<CalcModelRegression> nonlinearRegression(
    String model,
    List<double> xs,
    List<double> ys,
  ) => compute(
    _nonlinearRegressionTask,
    _NonlinearRegressionTask(model: model, xs: xs, ys: ys),
  );

  static Future<double?> interpolate(
    String method,
    List<double> xs,
    List<double> ys,
    double x,
  ) => compute(
    _interpolateTask,
    _InterpolateTask(method: method, xs: xs, ys: ys, x: x),
  );

  static Future<CalcDistributionResult> distribution(
    String name,
    double x,
    Map<String, double> parameters,
  ) => compute(
    _distributionTask,
    _DistributionTask(name: name, x: x, parameters: parameters),
  );

  static Future<List<double>> convolution(
    List<double> left,
    List<double> right,
  ) => compute(_convolutionTask, _ConvolutionTask(left: left, right: right));

  static Future<List<double>> scanRoots(
    String expression,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  }) => compute(
    _scanRootsTask,
    _ScanRootsTask(
      expression: expression,
      start: start,
      end: end,
      samples: samples,
      tolerance: tolerance,
    ),
  );

  static Future<List<double>> intersections(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  }) => compute(
    _intersectionsTask,
    _IntersectionsTask(
      expressionF: expressionF,
      expressionG: expressionG,
      start: start,
      end: end,
      samples: samples,
      tolerance: tolerance,
    ),
  );

  static Future<Map<String, double>?> solveSystem2d(
    String expressionF,
    String expressionG, {
    double x = 0,
    double y = 0,
    double tolerance = 1e-10,
    int maxIterations = 100,
  }) => compute(
    _systemTask,
    _SystemTask(
      expressionF: expressionF,
      expressionG: expressionG,
      x: x,
      y: y,
      tolerance: tolerance,
      maxIterations: maxIterations,
    ),
  );

  static Future<Map<String, double>?> tangentAndNormal(
    String expression,
    double x, {
    double? step,
  }) => compute(
    _tangentTask,
    _TangentTask(expression: expression, x: x, step: step),
  );
}

class _ScanRootsTask {
  const _ScanRootsTask({
    required this.expression,
    required this.start,
    required this.end,
    required this.samples,
    required this.tolerance,
  });

  final String expression;
  final double start;
  final double end;
  final int samples;
  final double tolerance;
}

List<double> _scanRootsTask(_ScanRootsTask task) => DartComputation.scanRoots(
  task.expression,
  task.start,
  task.end,
  samples: task.samples,
  tolerance: task.tolerance,
);

class _IntersectionsTask {
  const _IntersectionsTask({
    required this.expressionF,
    required this.expressionG,
    required this.start,
    required this.end,
    required this.samples,
    required this.tolerance,
  });

  final String expressionF;
  final String expressionG;
  final double start;
  final double end;
  final int samples;
  final double tolerance;
}

List<double> _intersectionsTask(_IntersectionsTask task) =>
    DartComputation.findIntersections(
      task.expressionF,
      task.expressionG,
      task.start,
      task.end,
      samples: task.samples,
      tolerance: task.tolerance,
    );

class _SystemTask {
  const _SystemTask({
    required this.expressionF,
    required this.expressionG,
    required this.x,
    required this.y,
    required this.tolerance,
    required this.maxIterations,
  });

  final String expressionF;
  final String expressionG;
  final double x;
  final double y;
  final double tolerance;
  final int maxIterations;
}

Map<String, double>? _systemTask(_SystemTask task) =>
    DartComputation.solveSystem2d(
      task.expressionF,
      task.expressionG,
      x: task.x,
      y: task.y,
      tolerance: task.tolerance,
      maxIterations: task.maxIterations,
    );

class _TangentTask {
  const _TangentTask({
    required this.expression,
    required this.x,
    required this.step,
  });

  final String expression;
  final double x;
  final double? step;
}

Map<String, double>? _tangentTask(_TangentTask task) =>
    DartComputation.tangentAndNormal(task.expression, task.x, step: task.step);

class _ConvolutionTask {
  const _ConvolutionTask({required this.left, required this.right});

  final List<double> left;
  final List<double> right;
}

List<double> _convolutionTask(_ConvolutionTask task) =>
    DartComputation.convolution(task.left, task.right);

class _PolynomialRegressionTask {
  const _PolynomialRegressionTask({
    required this.xs,
    required this.ys,
    required this.degree,
  });

  final List<double> xs;
  final List<double> ys;
  final int degree;
}

CalcPolynomialRegression _polynomialRegressionTask(
  _PolynomialRegressionTask task,
) =>
    DartComputation.polynomialRegression(task.xs, task.ys, degree: task.degree);

class _NonlinearRegressionTask {
  const _NonlinearRegressionTask({
    required this.model,
    required this.xs,
    required this.ys,
  });

  final String model;
  final List<double> xs;
  final List<double> ys;
}

CalcModelRegression _nonlinearRegressionTask(_NonlinearRegressionTask task) =>
    DartComputation.nonlinearRegression(task.model, task.xs, task.ys);

class _InterpolateTask {
  const _InterpolateTask({
    required this.method,
    required this.xs,
    required this.ys,
    required this.x,
  });

  final String method;
  final List<double> xs;
  final List<double> ys;
  final double x;
}

double? _interpolateTask(_InterpolateTask task) =>
    DartComputation.interpolate(task.method, task.xs, task.ys, task.x);

class _DistributionTask {
  const _DistributionTask({
    required this.name,
    required this.x,
    required this.parameters,
  });

  final String name;
  final double x;
  final Map<String, double> parameters;
}

CalcDistributionResult _distributionTask(_DistributionTask task) =>
    DartComputation.distribution(task.name, task.x, task.parameters);

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
            value: null,
            error: 'The expression produced a non-finite value.',
          );
  } on FormatException catch (error) {
    return CalcEvaluationValue(value: null, error: error.message);
  } catch (_) {
    return const CalcEvaluationValue(
      value: null,
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

class _LimitTask {
  const _LimitTask({
    required this.expression,
    required this.point,
    required this.tolerance,
    required this.maxLevel,
    required this.side,
  });

  final String expression;
  final double point;
  final double tolerance;
  final int maxLevel;
  final String side;
}

double? _limitTask(_LimitTask task) => DartComputation.limit(
  task.expression,
  task.point,
  tolerance: task.tolerance,
  maxLevel: task.maxLevel,
  side: task.side,
);

class _NthDerivativeTask {
  const _NthDerivativeTask({
    required this.expression,
    required this.point,
    required this.order,
    required this.step,
  });

  final String expression;
  final double point;
  final int order;
  final double step;
}

double? _nthDerivativeTask(_NthDerivativeTask task) =>
    DartComputation.nthDerivative(
      task.expression,
      task.point,
      task.order,
      step: task.step,
    );

class _ExtremumTask {
  const _ExtremumTask({
    required this.expression,
    required this.start,
    required this.end,
    required this.minimum,
    required this.tolerance,
  });

  final String expression;
  final double start;
  final double end;
  final bool minimum;
  final double tolerance;
}

double? _extremumTask(_ExtremumTask task) => DartComputation.findExtremum(
  task.expression,
  task.start,
  task.end,
  minimum: task.minimum,
  tolerance: task.tolerance,
);

class _AreaTask {
  const _AreaTask({
    required this.expressionF,
    required this.expressionG,
    required this.start,
    required this.end,
    required this.tolerance,
  });

  final String expressionF;
  final String expressionG;
  final double start;
  final double end;
  final double tolerance;
}

double? _areaTask(_AreaTask task) => DartComputation.areaBetweenCurves(
  task.expressionF,
  task.expressionG,
  task.start,
  task.end,
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
