import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';

import 'package:supercalculator_next_era/core/compute/computation.dart';

void main() {
  test('all plot samplers return finite, bounded vector data', () {
    final surface = DartComputation.sampleSurface(
      'x^2 + y^2',
      -1,
      1,
      -1,
      1,
      rows: 9,
      columns: 9,
    );
    expect(surface, hasLength(81));
    expect(surface.every((point) => point.value.isFinite), isTrue);
    expect(
      surface.firstWhere((point) => point.x == 0 && point.y == 0).value,
      closeTo(0, 1e-12),
    );

    final direction = DartComputation.sampleDirectionField(
      'y',
      -1,
      1,
      -1,
      1,
      rows: 5,
      columns: 5,
    );
    expect(direction, hasLength(25));
    expect(
      direction.every((vector) => vector.dx.isFinite && vector.dy.isFinite),
      isTrue,
    );

    final vector = DartComputation.sampleVectorField(
      '-y',
      'x',
      -1,
      1,
      -1,
      1,
      rows: 5,
      columns: 5,
    );
    expect(vector, hasLength(24));
    expect(
      vector.every((item) => item.dx.isFinite && item.dy.isFinite),
      isTrue,
    );

    final implicit = DartComputation.sampleImplicit(
      'x^2 + y^2 - 1',
      -1.2,
      1.2,
      -1.2,
      1.2,
      rows: 61,
      columns: 61,
      levelTolerance: .08,
    );
    expect(implicit, isNotEmpty);
    expect(implicit.every((point) => point.value.isFinite), isTrue);
  });

  test('root scanning handles tangent roots and discontinuities', () {
    final tangent = DartComputation.scanRoots(
      '(x - 0.123)^2',
      -1,
      1,
      samples: 1024,
      tolerance: 1e-8,
    );
    expect(tangent, hasLength(1));
    expect(tangent.single, closeTo(.123, 1e-5));

    expect(
      DartComputation.scanRoots('1/x', -1, 1, samples: 512),
      isEmpty,
    );
    expect(
      DartComputation.scanRoots('x^2 - 1', -2, 2),
      containsAllInOrder(<double>[-1, 1]),
    );
  });

  test('ODE methods, FFT and convolution retain stable boundaries', () {
    for (final method in <String>[
      'Euler',
      'Improved-Euler',
      'Midpoint',
      'RK4',
      'RKF45',
    ]) {
      final solution = DartComputation.odeMethod(
        'y',
        x0: 0,
        y0: 1,
        xEnd: 1,
        steps: 100,
        method: method,
      );
      expect(solution.ys.last, isNotNull, reason: method);
      expect(solution.ys.last!.isFinite, isTrue, reason: method);
    }
    expect(
      DartComputation.odeMethod(
        'y',
        x0: 0,
        y0: 1,
        xEnd: 1,
        steps: 0,
        method: 'RK4',
      ).isEmpty,
      isTrue,
    );

    final spectrum = DartComputation.spectrum(
      'sin(2*pi*5*x)',
      a: 0,
      b: 1,
      samples: 300,
    );
    expect(spectrum.length, 257); // next power of two is 512.
    expect(spectrum.frequencies[spectrum.dominantIndex], closeTo(5, 1e-12));
    expect(
      DartComputation.convolution(<double>[1, 2], <double>[3, 4]),
      <double>[3, 10, 8],
    );
    expect(
      () => DartComputation.convolution(<double>[double.nan], <double>[1]),
      throwsA(isA<FormatException>()),
    );
  });

  test('regression, dense matrices and bitwise widths reject bad inputs', () {
    final regression = DartComputation.nonlinearRegression(
      'exponential',
      <double>[0, 1, 2],
      <double>[1, math.e, math.e * math.e],
    );
    expect(regression.rSquared, closeTo(1, 1e-10));
    expect(regression.ys, hasLength(3));
    expect(
      DartComputation.polynomialRegression(
        <double>[0, 1, 2, 3],
        <double>[1, 4, 9, 16],
        degree: 2,
      ).evaluate(4),
      closeTo(25, 1e-8),
    );
    expect(
      () => DartComputation.parseMatrix('1,NaN;3,4'),
      throwsA(isA<FormatException>()),
    );
    expect(DartComputation.bitwise('and', 0xff, 0x0f, 8), 0x0f);
    expect(DartComputation.bitwise('not', 0, 8, 8), 0xff);
    expect(DartComputation.bitwise('shl', 1, 8, 8), 0x01);
    expect(
      () => DartComputation.bitwise('and', 1, 1, 24),
      throwsA(isA<FormatException>()),
    );
  });

  test('finance and preset assets are deterministic and executable', () {
    expect(
      DartComputation.loanPayment(
        principal: 1200,
        annualRate: 0,
        periods: 12,
      ),
      closeTo(100, 1e-12),
    );
    expect(
      DartComputation.retirementFutureValue(
        initialBalance: 0,
        monthlyContribution: 100,
        annualRate: 0,
        years: 1,
      ),
      closeTo(1200, 1e-12),
    );
    expect(DartComputation.irr(<double>[-100, 110]), closeTo(.1, 1e-8));
    expect(
      () => DartComputation.loanPayment(
        principal: -1,
        annualRate: .1,
        periods: 12,
      ),
      throwsA(isA<FormatException>()),
    );

    final document = jsonDecode(
      File('assets/presets/function_presets.json').readAsStringSync(),
    ) as Map<String, dynamic>;
    final presets = (document['presets'] as List).cast<Map<String, dynamic>>();
    expect(document['verifiedCount'], presets.length);
    expect(document['advertisedCount'], lessThanOrEqualTo(presets.length));
    final labels = <String>{};
    for (final preset in presets) {
      final label = preset['label'];
      final expression = preset['expression'];
      expect(label, isA<String>());
      expect(expression, isA<String>());
      expect(labels.add(label as String), isTrue);
      final compiled = ExpressionEngine.compile(expression as String);
      expect(compiled.evaluate(x: .25, y: .5).isFinite, isTrue, reason: label);
    }
    final parameterPresets =
        (document['parameterPresets'] as List).cast<Map<String, dynamic>>();
    expect(parameterPresets, isNotEmpty);
    expect(
      parameterPresets.every(
        (preset) =>
            preset['mode'] is String && preset['expression'] is String,
      ),
      isTrue,
    );
  });

  test('statistics keeps a one-point sample well-defined', () {
    final statistics = DartComputation.statistics(<double>[4]);
    expect(statistics.count, 1);
    expect(statistics.median, 4);
    expect(statistics.q1.isNaN, isTrue);
    expect(statistics.q3.isNaN, isTrue);
  });
}
