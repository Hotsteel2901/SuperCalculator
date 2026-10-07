import '../compute/calculation_models.dart';
import '../compute/computation.dart';
import '../compute/computation_dispatcher.dart';

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

  Future<CalcEvaluation> limit(
    String expression,
    double point, {
    double tolerance = 1e-8,
    int maxLevel = 10,
    String side = 'two-sided',
  });

  Future<CalcEvaluation> nthDerivative(
    String expression,
    double point,
    int order, {
    double step = 1e-4,
  });

  Future<CalcEvaluation> extremum(
    String expression,
    double start,
    double end, {
    bool minimum = true,
    double tolerance = 1e-8,
  });

  Future<CalcEvaluation> areaBetweenCurves(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    double tolerance = 1e-8,
  });

  Future<List<double>> scanRoots(
    String expression,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  });

  Future<List<double>> intersections(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  });

  Future<Map<String, double>?> solveSystem2d(
    String expressionF,
    String expressionG, {
    double x = 0,
    double y = 0,
    double tolerance = 1e-10,
    int maxIterations = 100,
  });

  Future<Map<String, double>?> tangentAndNormal(
    String expression,
    double x, {
    double? step,
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

  Future<CalcRegression> linearRegression(List<double> xs, List<double> ys);

  Future<CalcPolynomialRegression> polynomialRegression(
    List<double> xs,
    List<double> ys, {
    int degree = 2,
  });

  Future<CalcModelRegression> nonlinearRegression(
    String model,
    List<double> xs,
    List<double> ys,
  );

  Future<double?> interpolate(
    String method,
    List<double> xs,
    List<double> ys,
    double x,
  );

  Future<CalcDistributionResult> distribution(
    String name,
    double x,
    Map<String, double> parameters,
  );

  Future<ComplexValue> complexOperation(
    String operation,
    ComplexValue left, [
    ComplexValue? right,
  ]);

  Future<CalcMatrix> parseMatrix(String input);

  Future<CalcMatrix> addMatrices(
    String left,
    String right, {
    bool subtract = false,
  });

  Future<CalcMatrix> rrefMatrix(String input);

  Future<int> matrixRank(String input);

  Future<List<double>> eigenvalues2x2(String input);

  Future<List<double>> convolution(List<double> left, List<double> right);

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
      return await ComputationDispatcher.evaluateArray(expression, xs);
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
      final value = await ComputationDispatcher.derivative(
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
      final value = await ComputationDispatcher.integrate(
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
  Future<CalcEvaluation> limit(
    String expression,
    double point, {
    double tolerance = 1e-8,
    int maxLevel = 10,
    String side = 'two-sided',
  }) async {
    try {
      final value = await ComputationDispatcher.limit(
        expression,
        point,
        tolerance: tolerance,
        maxLevel: maxLevel,
        side: side,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'The limit does not exist or is not finite.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> nthDerivative(
    String expression,
    double point,
    int order, {
    double step = 1e-4,
  }) async {
    try {
      final value = await ComputationDispatcher.nthDerivative(
        expression,
        point,
        order,
        step: step,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'The derivative could not be evaluated.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> extremum(
    String expression,
    double start,
    double end, {
    bool minimum = true,
    double tolerance = 1e-8,
  }) async {
    try {
      final value = await ComputationDispatcher.extremum(
        expression,
        start,
        end,
        minimum: minimum,
        tolerance: tolerance,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'No finite extremum was found in the interval.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> areaBetweenCurves(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    double tolerance = 1e-8,
  }) async {
    try {
      final value = await ComputationDispatcher.areaBetweenCurves(
        expressionF,
        expressionG,
        start,
        end,
        tolerance: tolerance,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'The area could not be evaluated.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<List<double>> scanRoots(
    String expression,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  }) => ComputationDispatcher.scanRoots(
    expression,
    start,
    end,
    samples: samples,
    tolerance: tolerance,
  );

  @override
  Future<List<double>> intersections(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    int samples = 512,
    double tolerance = 1e-8,
  }) => ComputationDispatcher.intersections(
    expressionF,
    expressionG,
    start,
    end,
    samples: samples,
    tolerance: tolerance,
  );

  @override
  Future<Map<String, double>?> solveSystem2d(
    String expressionF,
    String expressionG, {
    double x = 0,
    double y = 0,
    double tolerance = 1e-10,
    int maxIterations = 100,
  }) => ComputationDispatcher.solveSystem2d(
    expressionF,
    expressionG,
    x: x,
    y: y,
    tolerance: tolerance,
    maxIterations: maxIterations,
  );

  @override
  Future<Map<String, double>?> tangentAndNormal(
    String expression,
    double x, {
    double? step,
  }) => ComputationDispatcher.tangentAndNormal(expression, x, step: step);

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
      final value = await ComputationDispatcher.solve(
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
    return ComputationDispatcher.ode(
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
    return ComputationDispatcher.spectrum(
      expression,
      a: a,
      b: b,
      samples: samples,
    );
  }

  @override
  Future<CalcStatistics> statistics(List<double> values) =>
      ComputationDispatcher.statistics(values);

  @override
  Future<CalcRegression> linearRegression(List<double> xs, List<double> ys) =>
      ComputationDispatcher.linearRegression(xs, ys);

  @override
  Future<CalcPolynomialRegression> polynomialRegression(
    List<double> xs,
    List<double> ys, {
    int degree = 2,
  }) async =>
      ComputationDispatcher.polynomialRegression(xs, ys, degree: degree);

  @override
  Future<CalcModelRegression> nonlinearRegression(
    String model,
    List<double> xs,
    List<double> ys,
  ) async => ComputationDispatcher.nonlinearRegression(model, xs, ys);

  @override
  Future<double?> interpolate(
    String method,
    List<double> xs,
    List<double> ys,
    double x,
  ) async => ComputationDispatcher.interpolate(method, xs, ys, x);

  @override
  Future<CalcDistributionResult> distribution(
    String name,
    double x,
    Map<String, double> parameters,
  ) async => ComputationDispatcher.distribution(name, x, parameters);

  @override
  Future<ComplexValue> complexOperation(
    String operation,
    ComplexValue left, [
    ComplexValue? right,
  ]) async {
    final other = right ?? const ComplexValue(0, 0);
    return switch (operation) {
      'add' => left + other,
      'subtract' => left - other,
      'multiply' => left * other,
      'divide' => left / other,
      'power' => DartComputation.complexPower(left, other),
      'sin' => DartComputation.complexSin(left),
      'cos' => DartComputation.complexCos(left),
      'tan' => DartComputation.complexTan(left),
      'exp' => DartComputation.complexExp(left),
      'log' => DartComputation.complexLog(left),
      'sqrt' => DartComputation.complexSqrt(left),
      'conjugate' => left.conjugate(),
      _ => throw const FormatException('Unknown complex operation.'),
    };
  }

  @override
  Future<CalcMatrix> parseMatrix(String input) async =>
      DartComputation.parseMatrix(input);

  @override
  Future<CalcMatrix> addMatrices(
    String left,
    String right, {
    bool subtract = false,
  }) async => DartComputation.matrixAdd(
    DartComputation.parseMatrix(left),
    DartComputation.parseMatrix(right),
    subtract: subtract,
  );

  @override
  Future<CalcMatrix> rrefMatrix(String input) async =>
      DartComputation.matrixRref(DartComputation.parseMatrix(input));

  @override
  Future<int> matrixRank(String input) async =>
      DartComputation.matrixRank(DartComputation.parseMatrix(input));

  @override
  Future<List<double>> eigenvalues2x2(String input) async =>
      DartComputation.eigenvalues2x2(DartComputation.parseMatrix(input));

  @override
  Future<List<double>> convolution(
    List<double> left,
    List<double> right,
  ) async => DartComputation.convolution(left, right);

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
