import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'plot_point.dart';
import 'plot_viewport.dart';

class FunctionPlotPainter extends CustomPainter {
  const FunctionPlotPainter({
    required this.points,
    required this.scheme,
    this.mode = 'function',
    this.intersectionPoints = const <PlotPoint>[],
    this.markedPoints = const <PlotPoint>[],
    this.viewport = PlotViewport.initial,
    this.zoom = 1,
    this.pan = Offset.zero,
    this.yaw = -.65,
    this.pitch = .55,
  });

  final List<PlotPoint> points;
  final ColorScheme scheme;
  final String mode;
  final List<PlotPoint> intersectionPoints;
  final List<PlotPoint> markedPoints;
  final PlotViewport viewport;

  /// Camera scale and translation are used only by the 3D surface projection.
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
    final plotRect = PlotLayout.plotRectFor(size);
    final visible = viewport.isValid ? viewport : PlotViewport.initial;
    _drawGrid(canvas, size, plotRect, visible);

    final finite = points
        .where((point) => point.x.isFinite && point.y.isFinite)
        .toList(growable: false);
    if (finite.isEmpty) return;

    canvas.save();
    canvas.clipRect(plotRect);
    if (mode == 'implicit' || mode == 'contour') {
      final pointPaint = Paint()
        ..color = scheme.primary
        ..style = PaintingStyle.fill;
      for (final point in finite) {
        final mapped = visible.dataToScreen(point, plotRect);
        canvas.drawCircle(mapped, 1.7, pointPaint);
      }
      _drawMarkers(canvas, plotRect, visible);
      canvas.restore();
      return;
    }

    final curvePaint = Paint()
      ..strokeWidth = mode == 'direction' || mode == 'vector' ? 1.4 : 2.4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final palette = <Color>[
      scheme.primary,
      scheme.tertiary,
      scheme.secondary,
      scheme.error,
      scheme.inversePrimary,
    ];
    final path = Path();
    var curveIndex = 0;
    PlotPoint? previous;
    void flushPath() {
      if (path.computeMetrics().isNotEmpty) {
        curvePaint.color = palette[curveIndex % palette.length];
        canvas.drawPath(path, curvePaint);
      }
    }

    for (var pointIndex = 0; pointIndex < points.length; pointIndex++) {
      final point = points[pointIndex];
      if (!point.x.isFinite || !point.y.isFinite) {
        flushPath();
        path.reset();
        previous = null;
        final nextIndex = pointIndex + 1;
        if (mode == 'multi' && nextIndex < points.length) {
          final next = points[nextIndex];
          // A curve boundary is the separator followed by the next curve's
          // first sample. Internal NaN samples preserve discontinuities but
          // must not change that curve's color.
          if (next.x.isFinite && (next.x + 10).abs() < 1e-9) {
            curveIndex++;
          }
        }
        continue;
      }
      final mapped = visible.dataToScreen(point, plotRect);
      if (previous == null ||
          (point.y - previous.y).abs() > visible.ySpan * 1.5) {
        path.moveTo(mapped.dx, mapped.dy);
      } else {
        path.lineTo(mapped.dx, mapped.dy);
      }
      previous = point;
    }
    flushPath();
    _drawMarkers(canvas, plotRect, visible);
    canvas.restore();
  }

  void _drawMarkers(Canvas canvas, Rect plotRect, PlotViewport visible) {
    final intersectionOuter = Paint()
      ..color = scheme.tertiary
      ..style = PaintingStyle.fill;
    final intersectionInner = Paint()
      ..color = scheme.onTertiary
      ..style = PaintingStyle.fill;
    for (final point in intersectionPoints.where((point) => point.isFinite)) {
      final mapped = visible.dataToScreen(point, plotRect);
      canvas.drawCircle(mapped, 7, intersectionOuter);
      canvas.drawCircle(mapped, 3, intersectionInner);
    }

    final markedOuter = Paint()
      ..color = scheme.error
      ..style = PaintingStyle.fill;
    final markedInner = Paint()
      ..color = scheme.onError
      ..style = PaintingStyle.fill;
    for (final point in markedPoints.where((point) => point.isFinite)) {
      final mapped = visible.dataToScreen(point, plotRect);
      canvas.drawCircle(mapped, 6, markedOuter);
      canvas.drawCircle(mapped, 2.5, markedInner);
    }
  }

  void _drawGrid(
    Canvas canvas,
    Size size,
    Rect plotRect,
    PlotViewport visible,
  ) {
    final grid = Paint()
      ..color = scheme.outlineVariant.withValues(alpha: .42)
      ..strokeWidth = 1;
    final axis = Paint()
      ..color = scheme.outline
      ..strokeWidth = 1.4;
    final labelStyle = TextStyle(
      color: scheme.onSurfaceVariant.withValues(alpha: .86),
      fontSize: 10,
      height: 1,
    );
    final xStep = _niceStep(visible.xSpan, plotRect.width / 76);
    final yStep = _niceStep(visible.ySpan, plotRect.height / 54);

    var xValue = (visible.xMin / xStep).ceilToDouble() * xStep;
    var drawn = 0;
    while (xValue <= visible.xMax && drawn < 120) {
      final x = visible.dataToScreen(PlotPoint(xValue, 0), plotRect).dx;
      canvas.drawLine(Offset(x, plotRect.top), Offset(x, plotRect.bottom), grid);
      final label = _tickLabel(xValue, xStep, labelStyle);
      final labelX = (x - label.width / 2)
          .clamp(0.0, math.max(0.0, size.width - label.width).toDouble())
          .toDouble();
      label.paint(canvas, Offset(labelX, plotRect.bottom + 4));
      drawn++;
      final nextValue = xValue + xStep;
      if (!nextValue.isFinite || nextValue <= xValue) break;
      xValue = nextValue;
    }

    var yValue = (visible.yMin / yStep).ceilToDouble() * yStep;
    drawn = 0;
    while (yValue <= visible.yMax && drawn < 120) {
      final y = visible.dataToScreen(PlotPoint(0, yValue), plotRect).dy;
      canvas.drawLine(Offset(plotRect.left, y), Offset(plotRect.right, y), grid);
      final label = _tickLabel(yValue, yStep, labelStyle);
      final labelX = math.max(0.0, plotRect.left - label.width - 4).toDouble();
      final labelY = (y - label.height / 2)
          .clamp(0.0, math.max(0.0, size.height - label.height).toDouble())
          .toDouble();
      label.paint(canvas, Offset(labelX, labelY));
      drawn++;
      final nextValue = yValue + yStep;
      if (!nextValue.isFinite || nextValue <= yValue) break;
      yValue = nextValue;
    }

    // Keep the origin axes visible only when their coordinate is in view.
    if (visible.xMin <= 0 && visible.xMax >= 0) {
      final x = visible.dataToScreen(const PlotPoint(0, 0), plotRect).dx;
      canvas.drawLine(Offset(x, plotRect.top), Offset(x, plotRect.bottom), axis);
    }
    if (visible.yMin <= 0 && visible.yMax >= 0) {
      final y = visible.dataToScreen(const PlotPoint(0, 0), plotRect).dy;
      canvas.drawLine(Offset(plotRect.left, y), Offset(plotRect.right, y), axis);
    }
  }

  double _niceStep(double span, double targetTickCount) {
    if (!span.isFinite || span <= 0) return 1;
    final count = targetTickCount.clamp(2.0, 14.0).toDouble();
    final raw = span / count;
    final exponent = (math.log(raw) / math.ln10).floor();
    final magnitude = math.pow(10, exponent).toDouble();
    final normalized = raw / magnitude;
    final multiplier = normalized < 1.5
        ? 1.0
        : normalized < 3.5
        ? 2.0
        : normalized < 7.5
        ? 5.0
        : 10.0;
    return multiplier * magnitude;
  }

  TextPainter _tickLabel(double value, double step, TextStyle style) {
    String text;
    final magnitude = value.abs();
    if (magnitude >= 1e5 || (magnitude > 0 && magnitude < 1e-3)) {
      text = value.toStringAsPrecision(2);
    } else {
      var decimals = 0;
      while (decimals < 8 &&
          ((step * math.pow(10, decimals)) -
                      (step * math.pow(10, decimals)).round())
                  .abs() >
              1e-7) {
        decimals++;
      }
      text = value.toStringAsFixed(decimals);
      if (text.contains('.')) {
        text = text.replaceFirst(RegExp(r'0+$'), '').replaceFirst(RegExp(r'\.$'), '');
      }
      if (text == '-0') text = '0';
    }
    final painter = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
      maxLines: 1,
    )..layout(maxWidth: 160);
    return painter;
  }

  void _drawSurface(Canvas canvas, Size size) {
    final finite = points
        .where(
          (point) =>
              point.x.isFinite &&
              point.y.isFinite &&
              point.z != null &&
              point.z!.isFinite,
        )
        .toList(growable: false);
    if (finite.isEmpty) {
      _drawGrid(
        canvas,
        size,
        PlotLayout.plotRectFor(size),
        PlotViewport.initial,
      );
      return;
    }
    final zMin = finite
        .map((point) => point.z!)
        .reduce((a, b) => math.min(a, b).toDouble());
    final zMax = finite
        .map((point) => point.z!)
        .reduce((a, b) => math.max(a, b).toDouble());
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
        '${xIndex[_coordinateKey(point.x)]}:${yIndex[_coordinateKey(point.y)]}':
            point,
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
      final normalized = ((point.z! - zMin) / zSpan).clamp(0.0, 1.0).toDouble();
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
    canvas.drawLine(origin, origin + const Offset(42, 0), labelPaint);
    canvas.drawLine(origin, origin + const Offset(-24, -24), labelPaint);
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

  @override
  bool shouldRepaint(covariant FunctionPlotPainter oldDelegate) {
    return oldDelegate.points != points ||
        oldDelegate.scheme != scheme ||
        oldDelegate.mode != mode ||
        oldDelegate.intersectionPoints != intersectionPoints ||
        oldDelegate.markedPoints != markedPoints ||
        oldDelegate.viewport != viewport ||
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
