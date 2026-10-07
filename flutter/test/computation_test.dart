import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';

import 'package:supercalculator_next_era/core/compute/computation.dart';
import 'package:supercalculator_next_era/core/compute/computation_dispatcher.dart';

void main() {
  test('compiled expression reuses one AST for array sampling', () {
    final expression = ExpressionEngine.compile('sin(pi / 2) + x^2');
    final values = expression.sample(<double>[0, 1, 2]);

    expect(values, hasLength(3));
    expect(values[0], closeTo(1, 1e-12));
    expect(values[2], closeTo(5, 1e-12));
  });

  test('adaptive Simpson integrates a polynomial', () {
    final value = DartComputation.integrate('x^2', 0, 1);
    expect(value, isNotNull);
    expect(value, closeTo(1 / 3, 1e-8));
  });

  test('heavy fallback work crosses the computation dispatcher', () async {
    final values = await ComputationDispatcher.evaluateArray('x^2', <double>[
      0,
      1,
      2,
    ]);
    final integral = await ComputationDispatcher.integrate('x^2', 0, 1);

    expect(values, <double?>[0, 1, 4]);
    expect(integral, closeTo(1 / 3, 1e-8));
  });

  test('limits, Taylor series and extrema remain deterministic', () {
    expect(
      DartComputation.limit('sin(x) / x', 0),
      closeTo(1, 1e-6),
    );
    final coefficients = DartComputation.taylorCoefficients('exp(x)', 0, 3);
    expect(coefficients, isNotNull);
    expect(coefficients![0], closeTo(1, 1e-6));
    expect(coefficients[1], closeTo(1, 1e-4));
    expect(
      DartComputation.findExtremum('x^2', -2, 2),
      closeTo(0, 1e-5),
    );
  });

  test('area, parametric sampling and two-variable systems work', () {
    expect(
      DartComputation.areaBetweenCurves('x', '0', 0, 1),
      closeTo(.5, 1e-6),
    );
    final curve = DartComputation.evaluateParametric(
      'cos(x)',
      'sin(x)',
      samples: 9,
    );
    expect(curve, hasLength(9));
    expect(curve.first['x'], closeTo(1, 1e-12));
    final system = DartComputation.solveSystem2d(
      'x^2 + y^2 - 1',
      'x - y',
      x: .7,
      y: .7,
    );
    expect(system, isNotNull);
    expect(system!['x'], closeTo(1 / math.sqrt(2), 1e-5));
  });

  test('bounded root solver finds both a Newton root and a bracketed root', () {
    final positive = DartComputation.solve('x^2 - 2', guess: 1);
    final negative = DartComputation.solve(
      'x^2 - 2',
      guess: -1,
      minimum: -2,
      maximum: 0,
    );

    expect(positive, closeTo(1.41421356237, 1e-8));
    expect(negative, closeTo(-1.41421356237, 1e-8));
  });

  test('RK4 solves the exponential initial value problem approximately', () {
    final solution = DartComputation.ode(
      'y',
      x0: 0,
      y0: 1,
      xEnd: 1,
      steps: 100,
    );

    expect(solution.ys.last, isNotNull);
    expect(solution.ys.last, closeTo(2.7182818, 1e-5));
  });

  test('FFT identifies a five hertz signal', () {
    final spectrum = DartComputation.spectrum(
      'sin(2*pi*5*x)',
      a: 0,
      b: 1,
      samples: 256,
    );
    final index = spectrum.dominantIndex;

    expect(index, greaterThan(0));
    expect(spectrum.frequencies[index], closeTo(5, 1e-12));
  });

  test('statistics and matrix operations remain deterministic', () {
    final statistics = DartComputation.statistics(<double>[1, 2, 2, 3, 4]);
    final matrix = DartComputation.parseMatrix('1,2;3,4');

    expect(statistics.mean, closeTo(2.4, 1e-12));
    expect(statistics.median, closeTo(2, 1e-12));
    expect(statistics.mode, 2);
    expect(DartComputation.matrixDeterminant(matrix), closeTo(-2, 1e-12));
    expect(
      DartComputation.matrixInverse(matrix).rows[0][0],
      closeTo(-2, 1e-12),
    );
  });

  test('base and unit conversion validate user input', () {
    expect(DartComputation.convertBase('FF', 16, 2), '11111111');
    expect(
      DartComputation.convertUnit('Length', 'm', 'ft', 1),
      closeTo(3.280839895, 1e-9),
    );
    expect(
      () => DartComputation.convertBase('2', 2, 10),
      throwsA(isA<FormatException>()),
    );
  });
}
