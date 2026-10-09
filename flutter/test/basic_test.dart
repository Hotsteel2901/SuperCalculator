import 'package:flutter_test/flutter_test.dart';

import 'package:supercalculator_next_era/core/backend/calc_backend.dart';

void main() {
  test('Dart fallback evaluates the first vertical slice', () async {
    const backend = DartCalcBackend();
    final result = await backend.evaluate('x^2 + 1', 3);

    expect(result.isSuccess, isTrue);
    expect(result.value, closeTo(10, 1e-12));
  });

  test('Dart fallback supports functions and postfix factorial', () async {
    const backend = DartCalcBackend();
    final trigonometric = await backend.evaluate('sin(pi / 2)', 0);
    final factorial = await backend.evaluate('5!', 0);

    expect(trigonometric.value, closeTo(1, 1e-12));
    expect(factorial.value, closeTo(120, 1e-12));
  });

  test('Dart fallback preserves discontinuities in array sampling', () async {
    const backend = DartCalcBackend();
    final values = await backend.evaluateArray('1 / x', <double>[-1, 0, 1]);

    expect(values[0], closeTo(-1, 1e-12));
    expect(values[1], isNull);
    expect(values[2], closeTo(1, 1e-12));
  });

  test('Dart fallback rejects division by zero', () async {
    const backend = DartCalcBackend();
    final result = await backend.evaluate('1 / 0', 0);

    expect(result.isSuccess, isFalse);
    expect(result.error, isNotNull);
  });
}
