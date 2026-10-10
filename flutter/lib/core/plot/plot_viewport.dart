import 'dart:math' as math;
import 'dart:ui' show Offset, Rect, Size;

import 'package:flutter/foundation.dart';

import 'plot_point.dart';

/// The visible data-space bounds of a two-dimensional plot.
///
/// Pan and zoom operate on these bounds rather than translating a finite bitmap
/// of grid lines. This keeps the coordinate plane complete while the graph is
/// moved through it, and makes the same math work for touch, mouse and trackpad
/// input on every Flutter target.
@immutable
class PlotViewport {
  const PlotViewport({
    required this.xMin,
    required this.xMax,
    required this.yMin,
    required this.yMax,
  });

  static const PlotViewport initial = PlotViewport(
    xMin: -10,
    xMax: 10,
    yMin: -10,
    yMax: 10,
  );

  static const double minimumSpan = 1e-7;
  static const double maximumSpan = 1e8;
  static const double maximumCenter = 1e12;

  final double xMin;
  final double xMax;
  final double yMin;
  final double yMax;

  double get xSpan => xMax - xMin;
  double get ySpan => yMax - yMin;

  bool get isValid =>
      xMin.isFinite &&
      xMax.isFinite &&
      yMin.isFinite &&
      yMax.isFinite &&
      xMin < xMax &&
      yMin < yMax &&
      xSpan >= minimumSpan &&
      ySpan >= minimumSpan &&
      xSpan <= maximumSpan &&
      ySpan <= maximumSpan;

  /// Converts a data coordinate to its position inside the plotting area.
  Offset dataToScreen(PlotPoint point, Rect plotRect) {
    if (!isValid || plotRect.width <= 0 || plotRect.height <= 0) {
      return plotRect.center;
    }
    return Offset(
      plotRect.left + (point.x - xMin) / xSpan * plotRect.width,
      plotRect.top + (yMax - point.y) / ySpan * plotRect.height,
    );
  }

  /// Converts a local screen position to a data coordinate.
  PlotPoint? screenToData(Offset localPosition, Rect plotRect) {
    if (!isValid ||
        plotRect.width <= 0 ||
        plotRect.height <= 0 ||
        !localPosition.dx.isFinite ||
        !localPosition.dy.isFinite) {
      return null;
    }
    return PlotPoint(
      xMin + (localPosition.dx - plotRect.left) / plotRect.width * xSpan,
      yMax - (localPosition.dy - plotRect.top) / plotRect.height * ySpan,
    );
  }

  /// Moves the visible coordinate range by a screen-space drag delta.
  ///
  /// The graph, zero axes and grid all remain aligned in data space. A drag to
  /// the right moves the plotted content right, so the visible x range shifts
  /// left; dragging down shifts the visible y range up.
  PlotViewport panByPixels(Offset delta, Rect plotRect) {
    if (!isValid || plotRect.width <= 0 || plotRect.height <= 0) return this;
    final xShift = delta.dx / plotRect.width * xSpan;
    final yShift = delta.dy / plotRect.height * ySpan;
    return _fromEdges(
      xMin: xMin - xShift,
      xMax: xMax - xShift,
      yMin: yMin + yShift,
      yMax: yMax + yShift,
    );
  }

  /// Zooms around [focalPoint], preserving the data coordinate under it.
  ///
  /// A factor greater than one zooms in. The x and y scales are independent,
  /// matching standard scientific plotting canvases and preserving the same
  /// behaviour when a chart is resized or shown full-screen.
  PlotViewport zoomAt(double factor, Offset focalPoint, Rect plotRect) {
    if (!factor.isFinite || factor <= 0 || !isValid) return this;
    final anchor = screenToData(focalPoint, plotRect);
    if (anchor == null) return this;
    final nextXSpan = _boundedSpan(xSpan / factor);
    final nextYSpan = _boundedSpan(ySpan / factor);
    final fx = (focalPoint.dx - plotRect.left) / plotRect.width;
    final fy = (focalPoint.dy - plotRect.top) / plotRect.height;
    return _fromEdges(
      xMin: anchor.x - fx * nextXSpan,
      xMax: anchor.x + (1 - fx) * nextXSpan,
      yMin: anchor.y - (1 - fy) * nextYSpan,
      yMax: anchor.y + fy * nextYSpan,
    );
  }

  /// Applies one scale gesture from its initial pointer location to its latest.
  ///
  /// Keeping the gesture-start viewport avoids cumulative rounding drift and
  /// correctly combines single-finger pan with two-finger focal-point zoom.
  PlotViewport transformGesture({
    required PlotViewport startViewport,
    required Offset startFocalPoint,
    required Offset currentFocalPoint,
    required double scale,
    required Rect plotRect,
  }) {
    if (!startViewport.isValid ||
        plotRect.width <= 0 ||
        plotRect.height <= 0 ||
        !scale.isFinite ||
        scale <= 0) {
      return this;
    }

    final anchor = startViewport.screenToData(startFocalPoint, plotRect);
    if (anchor == null) return this;
    final safeScale = scale.clamp(.0001, 10000).toDouble();
    final nextXSpan = _boundedSpan(startViewport.xSpan / safeScale);
    final nextYSpan = _boundedSpan(startViewport.ySpan / safeScale);
    final fx = (currentFocalPoint.dx - plotRect.left) / plotRect.width;
    final fy = (currentFocalPoint.dy - plotRect.top) / plotRect.height;
    return _fromEdges(
      xMin: anchor.x - fx * nextXSpan,
      xMax: anchor.x + (1 - fx) * nextXSpan,
      yMin: anchor.y - (1 - fy) * nextYSpan,
      yMax: anchor.y + fy * nextYSpan,
    );
  }

  static double _boundedSpan(double value) {
    if (!value.isFinite) return maximumSpan;
    return value.clamp(minimumSpan, maximumSpan).toDouble();
  }

  static double _boundedCenter(double value) {
    if (!value.isFinite) {
      return value.isNegative ? -maximumCenter : maximumCenter;
    }
    return value.clamp(-maximumCenter, maximumCenter).toDouble();
  }

  static double _precisionAwareSpan(double requested, double center) {
    // At very large coordinates, a sub-pixel span can be smaller than one
    // representable double-precision increment. Preserve a usable ordered
    // range instead of allowing zoom/pan math to collapse both endpoints.
    final precisionFloor = math
        .max(minimumSpan, center.abs() * 1e-15)
        .toDouble();
    return _boundedSpan(math.max(requested, precisionFloor).toDouble());
  }

  static PlotViewport _fromEdges({
    required double xMin,
    required double xMax,
    required double yMin,
    required double yMax,
  }) {
    if (![xMin, xMax, yMin, yMax].every((value) => value.isFinite)) {
      return initial;
    }
    final centerX = _boundedCenter((xMin + xMax) / 2);
    final centerY = _boundedCenter((yMin + yMax) / 2);
    final xSpan = _precisionAwareSpan(xMax - xMin, centerX);
    final ySpan = _precisionAwareSpan(yMax - yMin, centerY);
    return PlotViewport(
      xMin: centerX - xSpan / 2,
      xMax: centerX + xSpan / 2,
      yMin: centerY - ySpan / 2,
      yMax: centerY + ySpan / 2,
    );
  }

  @override
  bool operator ==(Object other) =>
      other is PlotViewport &&
      other.xMin == xMin &&
      other.xMax == xMax &&
      other.yMin == yMin &&
      other.yMax == yMax;

  @override
  int get hashCode => Object.hash(xMin, xMax, yMin, yMax);
}

/// Consistent space reserved for numeric axis labels around the plot itself.
class PlotLayout {
  const PlotLayout._();

  static Rect plotRectFor(Size size) {
    if (size.width <= 1 || size.height <= 1) return Offset.zero & size;
    final left = math.min(44.0, size.width * .22).toDouble();
    final right = math.min(10.0, size.width * .04).toDouble();
    final top = math.min(10.0, size.height * .08).toDouble();
    final bottom = math.min(26.0, size.height * .18).toDouble();
    return Rect.fromLTRB(
      left,
      top,
      math.max(left + 1, size.width - right).toDouble(),
      math.max(top + 1, size.height - bottom).toDouble(),
    );
  }
}
