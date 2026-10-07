import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../backend/calc_backend.dart';

class FunctionPlotPainter extends CustomPainter {
  const FunctionPlotPainter({required this.points, required this.scheme});

  final List<PlotPoint> points;
  final ColorScheme scheme;

  @override
  void paint(Canvas canvas, Size size) {
    final background = Paint()..color = scheme.surfaceContainerLowest;
    canvas.drawRect(Offset.zero & size, background);
    if (size.width <= 1 || size.height <= 1) return;

    final gridPaint = Paint()
      ..color = scheme.outlineVariant.withValues(alpha: 0.45)
      ..strokeWidth = 1;
    final axisPaint = Paint()
      ..color = scheme.outline
      ..strokeWidth = 1.4;
    final curvePaint = Paint()
      ..color = scheme.primary
      ..strokeWidth = 2.4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    const xMin = -10.0;
    const xMax = 10.0;
    final finite = points.where((point) => point.y.isFinite).toList(growable: false);
    if (finite.isEmpty) {
      _drawGrid(canvas, size, gridPaint, axisPaint, xMin, xMax, -5, 5);
      return;
    }

    var yMin = finite.map((point) => point.y).reduce(math.min);
    var yMax = finite.map((point) => point.y).reduce(math.max);
    if ((yMax - yMin).abs() < 1e-9) {
      yMin -= 1;
      yMax += 1;
    } else {
      final padding = (yMax - yMin) * 0.12;
      yMin -= padding;
      yMax += padding;
    }

    _drawGrid(canvas, size, gridPaint, axisPaint, xMin, xMax, yMin, yMax);

    final path = Path();
    PlotPoint? previous;
    for (final point in points) {
      if (!point.y.isFinite) {
        previous = null;
        continue;
      }
      final mapped = _map(point, size, xMin, xMax, yMin, yMax);
      if (previous == null || (point.y - previous!.y).abs() > (yMax - yMin) * 1.5) {
        path.moveTo(mapped.dx, mapped.dy);
      } else {
        path.lineTo(mapped.dx, mapped.dy);
      }
      previous = point;
    }
    canvas.drawPath(path, curvePaint);
  }

  void _drawGrid(
    Canvas canvas,
    Size size,
    Paint grid,
    Paint axis,
    double xMin,
    double xMax,
    double yMin,
    double yMax,
  ) {
    for (var value = -10.0; value <= 10.0; value += 2) {
      final x = (value - xMin) / (xMax - xMin) * size.width;
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), grid);
    }
    for (var index = 0; index <= 10; index++) {
      final y = index / 10 * size.height;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), grid);
    }
    if (xMin <= 0 && xMax >= 0) {
      final x = (-xMin) / (xMax - xMin) * size.width;
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), axis);
    }
    if (yMin <= 0 && yMax >= 0) {
      final y = (yMax) / (yMax - yMin) * size.height;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), axis);
    }
  }

  Offset _map(PlotPoint point, Size size, double xMin, double xMax, double yMin, double yMax) {
    return Offset(
      (point.x - xMin) / (xMax - xMin) * size.width,
      (yMax - point.y) / (yMax - yMin) * size.height,
    );
  }

  @override
  bool shouldRepaint(covariant FunctionPlotPainter oldDelegate) {
    return oldDelegate.points != points || oldDelegate.scheme != scheme;
  }
}
