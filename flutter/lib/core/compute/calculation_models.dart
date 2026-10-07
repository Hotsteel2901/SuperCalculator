import 'dart:math' as math;

import 'package:flutter/foundation.dart';

@immutable
class CalcOdeSolution {
  const CalcOdeSolution({
    required this.xs,
    required this.ys,
    required this.method,
  });

  final List<double> xs;
  final List<double?> ys;
  final String method;

  bool get isEmpty => xs.isEmpty;
}

@immutable
class CalcSpectrum {
  const CalcSpectrum({
    required this.frequencies,
    required this.amplitudes,
    required this.phases,
  });

  final List<double> frequencies;
  final List<double> amplitudes;
  final List<double> phases;

  int get length => frequencies.length;

  int get dominantIndex {
    if (amplitudes.isEmpty) {
      return -1;
    }
    var index = 0;
    for (var i = 1; i < amplitudes.length; i++) {
      if (amplitudes[i] > amplitudes[index]) {
        index = i;
      }
    }
    return index;
  }
}

@immutable
class CalcStatistics {
  const CalcStatistics({
    required this.count,
    required this.sum,
    required this.mean,
    required this.median,
    required this.minimum,
    required this.maximum,
    required this.range,
    required this.variance,
    required this.standardDeviation,
    required this.q1,
    required this.q3,
    required this.mode,
  });

  final int count;
  final double sum;
  final double mean;
  final double median;
  final double minimum;
  final double maximum;
  final double range;
  final double variance;
  final double standardDeviation;
  final double q1;
  final double q3;
  final double? mode;

  double get iqr => q3 - q1;
}

@immutable
class CalcRegression {
  const CalcRegression({
    required this.slope,
    required this.intercept,
    required this.rSquared,
    required this.xs,
    required this.ys,
  });

  final double slope;
  final double intercept;
  final double rSquared;
  final List<double> xs;
  final List<double> ys;

  String get equation {
    final sign = intercept < 0 ? '-' : '+';
    return 'y = ${slope.toStringAsPrecision(8)}x $sign '
        '${intercept.abs().toStringAsPrecision(8)}';
  }
}

@immutable
class CalcMatrix {
  const CalcMatrix(this.rows);

  final List<List<double>> rows;

  int get rowCount => rows.length;
  int get columnCount => rows.isEmpty ? 0 : rows.first.length;

  CalcMatrix get transpose {
    if (rows.isEmpty) {
      return const CalcMatrix(<List<double>>[]);
    }
    return CalcMatrix(
      List<List<double>>.generate(
        columnCount,
        (column) => List<double>.generate(
          rowCount,
          (row) => rows[row][column],
          growable: false,
        ),
        growable: false,
      ),
    );
  }

  String format({int precision = 8}) {
    return rows
        .map(
          (row) => row
              .map((value) => value.toStringAsPrecision(precision))
              .join(', '),
        )
        .join('\n');
  }
}

@immutable
class UnitCategory {
  const UnitCategory({required this.name, required this.units});

  final String name;
  final List<String> units;
}

/// A platform-neutral complex scalar. Keeping the value in the shared core
/// lets the UI and a future native complex-number ABI use the same vectors.
@immutable
class ComplexValue {
  const ComplexValue(this.real, this.imaginary);

  final double real;
  final double imaginary;

  double get magnitude => math.sqrt(real * real + imaginary * imaginary);
  double get phase => math.atan2(imaginary, real);

  ComplexValue operator +(ComplexValue other) =>
      ComplexValue(real + other.real, imaginary + other.imaginary);

  ComplexValue operator -(ComplexValue other) =>
      ComplexValue(real - other.real, imaginary - other.imaginary);

  ComplexValue operator *(ComplexValue other) => ComplexValue(
    real * other.real - imaginary * other.imaginary,
    real * other.imaginary + imaginary * other.real,
  );

  ComplexValue operator /(ComplexValue other) {
    final denominator = other.real * other.real + other.imaginary * other.imaginary;
    if (denominator == 0 || !denominator.isFinite) {
      throw const FormatException('Cannot divide by zero complex value.');
    }
    return ComplexValue(
      (real * other.real + imaginary * other.imaginary) / denominator,
      (imaginary * other.real - real * other.imaginary) / denominator,
    );
  }

  ComplexValue conjugate() => ComplexValue(real, -imaginary);

  @override
  String toString() {
    final sign = imaginary < 0 ? '-' : '+';
    return '${real.toStringAsPrecision(10)} $sign '
        '${imaginary.abs().toStringAsPrecision(10)}i';
  }
}

@immutable
class CalcPolynomialRegression {
  const CalcPolynomialRegression({
    required this.coefficients,
    required this.rSquared,
    required this.xs,
    required this.ys,
  });

  /// Coefficients are ordered from the constant term upward.
  final List<double> coefficients;
  final double rSquared;
  final List<double> xs;
  final List<double> ys;

  double evaluate(double x) {
    var result = 0.0;
    for (var index = coefficients.length - 1; index >= 0; index--) {
      result = result * x + coefficients[index];
    }
    return result;
  }

  String get equation {
    final terms = <String>[];
    for (var index = coefficients.length - 1; index >= 0; index--) {
      final coefficient = coefficients[index];
      if (coefficient.abs() < 1e-12) continue;
      final sign = coefficient < 0 ? '-' : terms.isEmpty ? '' : '+';
      final magnitude = coefficient.abs().toStringAsPrecision(7);
      final power = index == 0 ? '' : index == 1 ? 'x' : 'x^$index';
      terms.add('$sign$magnitude$power');
    }
    return terms.isEmpty ? 'y = 0' : 'y = ${terms.join(' ')}';
  }
}

@immutable
class CalcModelRegression {
  const CalcModelRegression({
    required this.model,
    required this.parameters,
    required this.rSquared,
    required this.xs,
    required this.ys,
    required this.equation,
  });

  final String model;
  final Map<String, double> parameters;
  final double rSquared;
  final List<double> xs;
  final List<double> ys;
  final String equation;
}

@immutable
class CalcDistributionResult {
  const CalcDistributionResult({
    required this.name,
    required this.x,
    required this.pdf,
    required this.cdf,
    required this.ppf,
  });

  final String name;
  final double x;
  final double? pdf;
  final double? cdf;
  final double? ppf;
}

@immutable
class SparseEntry {
  const SparseEntry(this.row, this.column, this.value);

  final int row;
  final int column;
  final double value;
}

@immutable
class SparseMatrix {
  const SparseMatrix({
    required this.rows,
    required this.columns,
    required this.entries,
  });

  final int rows;
  final int columns;
  final List<SparseEntry> entries;
}

@immutable
class PlotPointValue {
  const PlotPointValue({required this.x, required this.y, required this.value});

  final double x;
  final double y;
  final double value;
}

@immutable
class PlotFieldVector {
  const PlotFieldVector({
    required this.x,
    required this.y,
    required this.dx,
    required this.dy,
  });

  final double x;
  final double y;
  final double dx;
  final double dy;
}

@immutable
class CalcFinancialResult {
  const CalcFinancialResult({required this.values, required this.summary});

  final List<double> values;
  final String summary;
}
