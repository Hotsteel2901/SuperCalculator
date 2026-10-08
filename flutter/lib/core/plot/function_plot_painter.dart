import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'plot_point.dart';

class FunctionPlotPainter extends CustomPainter {
  const FunctionPlotPainter({
    required this.points,
    required this.scheme,
    this.mode = 'function',
    this.zoom = 1,
    this.pan = Offset.zero,
    this.yaw = -.65,
    this.pitch = .55,
  });

  final List<PlotPoint> points;
  final ColorScheme scheme;
  final String mode;
  final double zoom;
  final Offset pan;
  final double yaw;
  final double pitch;

  @override
  void paint(Canvas canvas, Size size) {
    final background = Paint()..color = scheme.surfaceContainerLowest;
    canvas.drawRect(Offset.zero & size, background);
    if (size.width <= 1 || size.height <= 1) return;

    if (mode == 'surface') {
      _drawSurface(canvas, size);
      return;
    }
    _draw2d(canvas, size);
  }

  void _draw2d(Canvas canvas, Size size) {
    final finite = points
        .where((point) => point.x.isFinite && point.y.isFinite)
        .toList(growable: false);
    if (finite.isEmpty) {
      _drawGrid(canvas, size, -10, 10, -5, 5);
      return;
    }

    var xMin = -10.0;
    var xMax = 10.0;
    // Data-analysis and spectrum cards use this painter without a mode. Keep
    // the stable function range there; specialized plot modes use the same
    // coordinate contract as the calculator.
    if (mode == 'implicit' || mode == 'contour') {
      xMin = -10;
      xMax = 10;
    }
    var yMin = finite.map((point) => point.y).reduce((a, b) => math.min(a, b).toDouble());
    var yMax = finite.map((point) => point.y).reduce((a, b) => math.max(a, b).toDouble());
    if ((yMax - yMin).abs() < 1e-9) {
      yMin -= 1;
      yMax += 1;
    } else {
      final padding = (yMax - yMin) * .12;
      yMin -= padding;
      yMax += padding;
    }

    _drawGrid(canvas, size, xMin, xMax, yMin, yMax);
    if (mode == 'implicit' || mode == 'contour') {
      final pointPaint = Paint()
        ..color = scheme.primary
        ..style = PaintingStyle.fill;
      for (final point in finite) {
        final mapped = _map2d(point, size, xMin, xMax, yMin, yMax);
        canvas.drawCircle(mapped, 1.7 * math.sqrt(zoom.clamp(.5, 4)), pointPaint);
      }
      return;
    }

    final curvePaint = Paint()
      ..color = scheme.primary
      ..strokeWidth = mode == 'direction' || mode == 'vector' ? 1.4 : 2.4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final path = Path();
    PlotPoint? previous;
    for (final point in points) {
      if (!point.x.isFinite || !point.y.isFinite) {
        previous = null;
        continue;
      }
      final mapped = _map2d(point, size, xMin, xMax, yMin, yMax);
      if (previous == null ||
          (point.y - previous.y).abs() > (yMax - yMin) * 1.5) {
        path.moveTo(mapped.dx, mapped.dy);
      } else {
        path.lineTo(mapped.dx, mapped.dy);
      }
      previous = point;
    }
    canvas.drawPath(path, curvePaint);
  }

  void _drawSurface(Canvas canvas, Size size) {
    final finite = points
        .where((point) => point.x.isFinite && point.y.isFinite && point.z != null && point.z!.isFinite)
        .toList(growable: false);
    if (finite.isEmpty) {
      _drawGrid(canvas, size, -10, 10, -10, 10);
      return;
    }
    final zMin = finite.map((point) => point.z!).reduce((a, b) => math.min(a, b).toDouble());
    final zMax = finite.map((point) => point.z!).reduce((a, b) => math.max(a, b).toDouble());
    final zSpan = (zMax - zMin).abs() < 1e-9 ? 1.0 : zMax - zMin;
    final projected = <PlotPoint, _ProjectedPoint>{};
    for (final point in finite) {
      projected[point] = _projectSurface(point, size, zMin, zSpan);
    }

    final gridPaint = Paint()
      ..color = scheme.outlineVariant.withValues(alpha: .28)
      ..strokeWidth = 1;
    final pointPaint = Paint()..style = PaintingStyle.fill;
    final xs = finite.map((point) => point.x).toSet().toList()..sort();
    final ys = finite.map((point) => point.y).toSet().toList()..sort();
    final xIndex = <String, int>{
      for (var i = 0; i < xs.length; i++) _coordinateKey(xs[i]): i,
    };
    final yIndex = <String, int>{
      for (var i = 0; i < ys.length; i++) _coordinateKey(ys[i]): i,
    };
    final cells = <String, PlotPoint>{
      for (final point in finite)
        '${xIndex[_coordinateKey(point.x)]}:${yIndex[_coordinateKey(point.y)]}': point,
    };

    for (final point in finite) {
      final xi = xIndex[_coordinateKey(point.x)];
      final yi = yIndex[_coordinateKey(point.y)];
      if (xi == null || yi == null) continue;
      final right = cells['${xi + 1}:$yi'];
      final down = cells['$xi:${yi + 1}'];
      final from = projected[point]!.offset;
      if (right != null) {
        canvas.drawLine(from, projected[right]!.offset, gridPaint);
      }
      if (down != null) {
        canvas.drawLine(from, projected[down]!.offset, gridPaint);
      }
      final normalized =
          ((point.z! - zMin) / zSpan).clamp(0.0, 1.0).toDouble();
      pointPaint.color = HSVColor.fromAHSV(
        .9,
        220 - normalized * 180,
        .7,
        .65 + normalized * .3,
      ).toColor();
      canvas.drawCircle(from, 1.8 * math.sqrt(zoom.clamp(.5, 4)), pointPaint);
    }

    final labelPaint = Paint()
      ..color = scheme.outline
      ..strokeWidth = 1.2;
    final origin = _projectSurface(
      const PlotPoint(0, 0, z: 0),
      size,
      zMin,
      zSpan,
    ).offset;
    canvas.drawLine(
      origin,
      origin + const Offset(42, 0),
      labelPaint,
    );
    canvas.drawLine(
      origin,
      origin + const Offset(-24, -24),
      labelPaint,
    );
  }

  _ProjectedPoint _projectSurface(
    PlotPoint point,
    Size size,
    double zMin,
    double zSpan,
  ) {
    final nx = point.x / 10;
    final ny = point.y / 10;
    final nz = ((point.z ?? zMin) - zMin) / zSpan * 2 - 1;
    final cosYaw = math.cos(yaw);
    final sinYaw = math.sin(yaw);
    final rotatedX = nx * cosYaw - ny * sinYaw;
    final rotatedDepth = nx * sinYaw + ny * cosYaw;
    final cosPitch = math.cos(pitch);
    final sinPitch = math.sin(pitch);
    final vertical = nz * cosPitch - rotatedDepth * sinPitch;
    final depth = nz * sinPitch + rotatedDepth * cosPitch;
    final scale = math.min(size.width, size.height).toDouble() * .34 * zoom;
    return _ProjectedPoint(
      Offset(
        size.width / 2 + rotatedX * scale + pan.dx,
        size.height / 2 - vertical * scale + pan.dy,
      ),
      depth,
    );
  }

  String _coordinateKey(double value) => value.toStringAsFixed(7);

  void _drawGrid(
    Canvas canvas,
    Size size,
    double xMin,
    double xMax,
    double yMin,
    double yMax,
  ) {
    final grid = Paint()
      ..color = scheme.outlineVariant.withValues(alpha: .45)
      ..strokeWidth = 1;
    final axis = Paint()
      ..color = scheme.outline
      ..strokeWidth = 1.4;
    for (var value = -10.0; value <= 10.0; value += 2) {
      final start = _map2d(
        PlotPoint(value, yMin),
        size,
        xMin,
        xMax,
        yMin,
        yMax,
      );
      final end = _map2d(
        PlotPoint(value, yMax),
        size,
        xMin,
        xMax,
        yMin,
        yMax,
      );
      canvas.drawLine(start, end, grid);
    }
    for (var index = 0; index <= 10; index++) {
      final value = yMin + (yMax - yMin) * index / 10;
      final start = _map2d(
        PlotPoint(xMin, value),
        size,
        xMin,
        xMax,
        yMin,
        yMax,
      );
      final end = _map2d(
        PlotPoint(xMax, value),
        size,
        xMin,
        xMax,
        yMin,
        yMax,
      );
      canvas.drawLine(start, end, grid);
    }
    if (xMin <= 0 && xMax >= 0) {
      canvas.drawLine(
        _map2d(PlotPoint(0, yMin), size, xMin, xMax, yMin, yMax),
        _map2d(PlotPoint(0, yMax), size, xMin, xMax, yMin, yMax),
        axis,
      );
    }
    if (yMin <= 0 && yMax >= 0) {
      canvas.drawLine(
        _map2d(PlotPoint(xMin, 0), size, xMin, xMax, yMin, yMax),
        _map2d(PlotPoint(xMax, 0), size, xMin, xMax, yMin, yMax),
        axis,
      );
    }
  }

  Offset _map2d(
    PlotPoint point,
    Size size,
    double xMin,
    double xMax,
    double yMin,
    double yMax,
  ) {
    final base = Offset(
      (point.x - xMin) / (xMax - xMin) * size.width,
      (yMax - point.y) / (yMax - yMin) * size.height,
    );
    final center = Offset(size.width / 2, size.height / 2);
    return center + (base - center) * zoom + pan;
  }

  @override
  bool shouldRepaint(covariant FunctionPlotPainter oldDelegate) {
    return oldDelegate.points != points ||
        oldDelegate.scheme != scheme ||
        oldDelegate.mode != mode ||
        oldDelegate.zoom != zoom ||
        oldDelegate.pan != pan ||
        oldDelegate.yaw != yaw ||
        oldDelegate.pitch != pitch;
  }
}

class _ProjectedPoint {
  const _ProjectedPoint(this.offset, this.depth);

  final Offset offset;
  final double depth;
}
