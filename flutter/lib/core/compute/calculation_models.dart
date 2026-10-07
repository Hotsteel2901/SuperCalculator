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
