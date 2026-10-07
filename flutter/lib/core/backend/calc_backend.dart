import '../compute/calculation_models.dart';
import '../compute/computation.dart';

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

  Future<CalcEvaluation> evaluate(String expression, double x, [double y = 0]);

  Future<List<double?>> evaluateArray(String expression, List<double> xs);

  Future<CalcEvaluation> derivative(
    String expression,
    double x, {
    double? step,
    bool second = false,
  });

  Future<CalcEvaluation> integrate(
    String expression,
    double a,
    double b, {
    double tolerance = 1e-8,
  });

  Future<CalcEvaluation> solve(
    String expression, {
    double guess = 0,
    double minimum = -100,
    double maximum = 100,
    double tolerance = 1e-10,
    int maxIterations = 100,
  });

  Future<CalcOdeSolution> solveOde(
    String expression, {
    required double x0,
    required double y0,
    required double xEnd,
    int steps = 200,
  });

  Future<CalcSpectrum> spectrum(
    String expression, {
    required double a,
    required double b,
    int samples = 1024,
  });

  Future<CalcStatistics> statistics(List<double> values);

  Future<CalcRegression> linearRegression(
    List<double> xs,
    List<double> ys,
  );

  Future<CalcMatrix> parseMatrix(String input);

  Future<CalcMatrix> multiplyMatrices(String left, String right);

  Future<double> determinant(String input);

  Future<CalcMatrix> inverseMatrix(String input);

  void dispose();
}

class DartCalcBackend implements CalcBackend {
  const DartCalcBackend({this.displayName = 'Dart fallback'});

  final String displayName;

  @override
  String get name => displayName;

  @override
  Future<CalcEvaluation> evaluate(
    String expression,
    double x, [
    double y = 0,
  ]) async {
    try {
      final value = DartComputation.evaluate(expression, x, y);
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
    try {
      return DartComputation.evaluateArray(expression, xs);
    } on FormatException {
      return List<double?>.filled(xs.length, null, growable: false);
    }
  }

  @override
  Future<CalcEvaluation> derivative(
    String expression,
    double x, {
    double? step,
    bool second = false,
  }) async {
    try {
      final value = DartComputation.derivative(
        expression,
        x,
        step: step,
        second: second,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'Derivative could not be evaluated.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> integrate(
    String expression,
    double a,
    double b, {
    double tolerance = 1e-8,
  }) async {
    try {
      final value = DartComputation.integrate(
        expression,
        a,
        b,
        tolerance: tolerance,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'Integral could not be evaluated.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> solve(
    String expression, {
    double guess = 0,
    double minimum = -100,
    double maximum = 100,
    double tolerance = 1e-10,
    int maxIterations = 100,
  }) async {
    try {
      final value = DartComputation.solve(
        expression,
        guess: guess,
        minimum: minimum,
        maximum: maximum,
        tolerance: tolerance,
        maxIterations: maxIterations,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'The equation solver did not converge.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcOdeSolution> solveOde(
    String expression, {
    required double x0,
    required double y0,
    required double xEnd,
    int steps = 200,
  }) async {
    return DartComputation.ode(
      expression,
      x0: x0,
      y0: y0,
      xEnd: xEnd,
      steps: steps,
    );
  }

  @override
  Future<CalcSpectrum> spectrum(
    String expression, {
    required double a,
    required double b,
    int samples = 1024,
  }) async {
    return DartComputation.spectrum(
      expression,
      a: a,
      b: b,
      samples: samples,
    );
  }

  @override
  Future<CalcStatistics> statistics(List<double> values) async =>
      DartComputation.statistics(values);

  @override
  Future<CalcRegression> linearRegression(
    List<double> xs,
    List<double> ys,
  ) async =>
      DartComputation.linearRegression(xs, ys);

  @override
  Future<CalcMatrix> parseMatrix(String input) async =>
      DartComputation.parseMatrix(input);

  @override
  Future<CalcMatrix> multiplyMatrices(String left, String right) async {
    return DartComputation.matrixMultiply(
      DartComputation.parseMatrix(left),
      DartComputation.parseMatrix(right),
    );
  }

  @override
  Future<double> determinant(String input) async =>
      DartComputation.matrixDeterminant(DartComputation.parseMatrix(input));

  @override
  Future<CalcMatrix> inverseMatrix(String input) async =>
      DartComputation.matrixInverse(DartComputation.parseMatrix(input));

  @override
  void dispose() {}
}
