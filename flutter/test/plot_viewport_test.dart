import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:supercalculator_next_era/core/plot/plot_point.dart';
import 'package:supercalculator_next_era/core/plot/plot_viewport.dart';

void main() {
  const plotRect = Rect.fromLTWH(0, 0, 200, 100);

  test('screen and data coordinates round-trip in the visible axes', () {
    const viewport = PlotViewport(xMin: -4, xMax: 6, yMin: -3, yMax: 7);
    const point = PlotPoint(1.5, -1.25);

    final screen = viewport.dataToScreen(point, plotRect);
    final restored = viewport.screenToData(screen, plotRect);

    expect(restored, isNotNull);
    expect(restored!.x, closeTo(point.x, 1e-12));
    expect(restored.y, closeTo(point.y, 1e-12));
  });

  test('a drag pans the coordinate axes without shrinking the viewport', () {
    final moved = PlotViewport.initial.panByPixels(
      const Offset(50, 25),
      plotRect,
    );

    expect(moved.xMin, closeTo(-15, 1e-12));
    expect(moved.xMax, closeTo(5, 1e-12));
    expect(moved.yMin, closeTo(-5, 1e-12));
    expect(moved.yMax, closeTo(15, 1e-12));
    expect(moved.xSpan, closeTo(PlotViewport.initial.xSpan, 1e-12));
    expect(moved.ySpan, closeTo(PlotViewport.initial.ySpan, 1e-12));
  });

  test('zoom keeps the data point under the focal position fixed', () {
    const focal = Offset(50, 75);
    final anchor = PlotViewport.initial.screenToData(focal, plotRect)!;
    final zoomed = PlotViewport.initial.zoomAt(2, focal, plotRect);
    final restored = zoomed.dataToScreen(anchor, plotRect);

    expect(restored.dx, closeTo(focal.dx, 1e-12));
    expect(restored.dy, closeTo(focal.dy, 1e-12));
    expect(zoomed.xSpan, closeTo(10, 1e-12));
    expect(zoomed.ySpan, closeTo(10, 1e-12));
  });

  test('a combined pinch and drag follows the gesture focal point', () {
    const start = Offset(100, 50);
    const current = Offset(130, 65);
    final anchor = PlotViewport.initial.screenToData(start, plotRect)!;
    final transformed = PlotViewport.initial.transformGesture(
      startViewport: PlotViewport.initial,
      startFocalPoint: start,
      currentFocalPoint: current,
      scale: 2,
      plotRect: plotRect,
    );

    final newPosition = transformed.dataToScreen(anchor, plotRect);
    expect(newPosition.dx, closeTo(current.dx, 1e-12));
    expect(newPosition.dy, closeTo(current.dy, 1e-12));
    expect(transformed.xSpan, closeTo(10, 1e-12));
    expect(transformed.ySpan, closeTo(10, 1e-12));
  });

  test('zoom and pan remain bounded even after extreme input', () {
    final zoomed = PlotViewport.initial.zoomAt(
      1e100,
      plotRect.center,
      plotRect,
    );
    final moved = zoomed.panByPixels(const Offset(1e100, -1e100), plotRect);

    expect(zoomed.isValid, isTrue);
    expect(moved.isValid, isTrue);
    expect(moved.xSpan, greaterThanOrEqualTo(PlotViewport.minimumSpan));
    expect(moved.ySpan, lessThanOrEqualTo(PlotViewport.maximumSpan));
  });
}
