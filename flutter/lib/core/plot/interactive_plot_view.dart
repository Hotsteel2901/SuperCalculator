import 'dart:math' as math;

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

import 'function_plot_painter.dart';
import 'plot_point.dart';
import 'plot_viewport.dart';

/// Interactive, self-clipping plot surface shared by the inline preview and the
/// full-screen plot page.
///
/// A two-dimensional drag updates the visible data-coordinate range instead of
/// sliding a finite grid bitmap. The painter then lays out fresh grid lines and
/// tick labels across the whole viewport, just as the native chart does.
class InteractivePlotView extends StatefulWidget {
  const InteractivePlotView({
    required this.points,
    required this.mode,
    required this.scheme,
    this.intersectionPoints = const <PlotPoint>[],
    this.markedPoints = const <PlotPoint>[],
    this.onMarkPoint,
    this.onRemoveMarkPoint,
    this.borderRadius,
    this.initialViewport,
    this.initialZoom = 1,
    this.initialPan = Offset.zero,
    this.initialYaw = -.65,
    this.initialPitch = .55,
    super.key,
  });

  final List<PlotPoint> points;
  final String mode;
  final ColorScheme scheme;
  final List<PlotPoint> intersectionPoints;
  final List<PlotPoint> markedPoints;
  final ValueChanged<PlotPoint>? onMarkPoint;
  final ValueChanged<PlotPoint>? onRemoveMarkPoint;
  final BorderRadius? borderRadius;

  /// Initial 2D data range, also used to transfer the inline view to fullscreen.
  final PlotViewport? initialViewport;

  /// Initial camera values for the projected 3D surface mode.
  final double initialZoom;
  final Offset initialPan;
  final double initialYaw;
  final double initialPitch;

  @override
  State<InteractivePlotView> createState() => InteractivePlotViewState();
}

class InteractivePlotViewState extends State<InteractivePlotView> {
  late double _zoom = widget.initialZoom;
  late Offset _pan = widget.initialPan;
  late double _yaw = widget.initialYaw;
  late double _pitch = widget.initialPitch;
  late PlotViewport _viewport = _startingViewport;
  double _gestureZoomStart = 1;
  Offset _gestureFocalStart = Offset.zero;
  Offset _doubleTapFocalPoint = Offset.zero;
  late double _gestureYawStart = widget.initialYaw;
  late double _gesturePitchStart = widget.initialPitch;
  late PlotViewport _gestureViewportStart = _startingViewport;
  Rect _plotRect = Rect.zero;

  PlotViewport get _startingViewport {
    final candidate = widget.initialViewport;
    return candidate != null && candidate.isValid
        ? candidate
        : PlotViewport.initial;
  }

  /// Current horizontal/vertical translation for the projected 3D surface.
  Offset get pan => _pan;

  /// Current camera zoom for the projected 3D surface.
  ///
  /// In 2D mode this reports the zoom relative to the standard 20-unit range.
  double get zoom => widget.mode == 'surface'
      ? _zoom
      : (PlotViewport.initial.xSpan / _viewport.xSpan);

  /// Current 2D visible data-coordinate bounds.
  PlotViewport get viewport => _viewport;

  /// Current 3D surface yaw.
  double get yaw => _yaw;

  /// Current 3D surface pitch.
  double get pitch => _pitch;

  /// Restores the 2D axes or the 3D camera to its standard starting view.
  void resetView() {
    setState(() {
      _viewport = PlotViewport.initial;
      _zoom = widget.initialZoom;
      _pan = widget.initialPan;
      _yaw = widget.initialYaw;
      _pitch = widget.initialPitch;
    });
  }

  /// Sets the visible data range, for range dialogs and external controls.
  void setViewport(PlotViewport viewport) {
    if (!viewport.isValid) return;
    setState(() => _viewport = viewport);
  }

  /// Zooms around a local chart position. A null focus zooms around center.
  void zoomBy(double factor, {Offset? focalPoint}) {
    if (!factor.isFinite || factor <= 0) return;
    setState(() {
      if (widget.mode == 'surface') {
        _zoom = (_zoom * factor).clamp(.5, 4.0).toDouble();
      } else {
        _viewport = _viewport.zoomAt(
          factor,
          focalPoint ?? _plotRect.center,
          _plotRect,
        );
      }
    });
  }

  PlotPoint? _dataPointFromLocal(Offset local) {
    if (!_plotRect.contains(local)) return null;
    return _viewport.screenToData(local, _plotRect);
  }

  void _mark(Offset local) {
    if (widget.mode == 'surface') return;
    final callback = widget.onMarkPoint;
    if (callback == null) return;
    final point = _dataPointFromLocal(local);
    if (point != null && point.isFinite) callback(point);
  }

  void _remove(Offset local) {
    if (widget.mode == 'surface') return;
    final callback = widget.onRemoveMarkPoint;
    if (callback == null) return;
    final point = _dataPointFromLocal(local);
    if (point != null && point.isFinite) callback(point);
  }

  void _handlePointerSignal(PointerSignalEvent event) {
    if (event is! PointerScrollEvent ||
        !_plotRect.contains(event.localPosition)) {
      return;
    }

    // Registering at the plot's hit-test position gives it priority over the
    // surrounding scroll view, so a wheel over the graph zooms the graph rather
    // than unexpectedly scrolling the form beneath it.
    GestureBinding.instance.pointerSignalResolver.register(event, (resolved) {
      if (!mounted || resolved is! PointerScrollEvent) return;
      final delta = resolved.scrollDelta;
      if (widget.mode == 'surface') {
        final factor = math.exp(-delta.dy * .0015).clamp(.25, 4.0).toDouble();
        zoomBy(factor, focalPoint: resolved.localPosition);
      } else if (delta.dy.abs() >= delta.dx.abs()) {
        final factor = math.exp(-delta.dy * .0015).clamp(.25, 4.0).toDouble();
        zoomBy(factor, focalPoint: resolved.localPosition);
      } else {
        setState(() {
          _viewport = _viewport.panByPixels(Offset(-delta.dx, 0), _plotRect);
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final surface = LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final size = Size(constraints.maxWidth, constraints.maxHeight);
        _plotRect = PlotLayout.plotRectFor(size);
        return Listener(
          onPointerSignal: _handlePointerSignal,
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onDoubleTapDown: (details) {
              _doubleTapFocalPoint = details.localPosition;
            },
            onDoubleTap: () {
              if (_plotRect.contains(_doubleTapFocalPoint)) {
                zoomBy(1.5, focalPoint: _doubleTapFocalPoint);
              }
            },
            onTapUp: (details) => _mark(details.localPosition),
            onLongPressStart: (details) => _remove(details.localPosition),
            onScaleStart: (details) {
              _gestureZoomStart = _zoom;
              _gestureFocalStart = details.localFocalPoint;
              _gestureYawStart = _yaw;
              _gesturePitchStart = _pitch;
              _gestureViewportStart = _viewport;
            },
            onScaleUpdate: (details) {
              final focalPoint = details.localFocalPoint;
              setState(() {
                if (widget.mode == 'surface') {
                  final delta = focalPoint - _gestureFocalStart;
                  _zoom = (_gestureZoomStart * details.scale)
                      .clamp(.5, 4.0)
                      .toDouble();
                  _yaw = _gestureYawStart + delta.dx * .01;
                  _pitch = (_gesturePitchStart - delta.dy * .01)
                      .clamp(-1.35, 1.35)
                      .toDouble();
                } else {
                  _viewport = _viewport.transformGesture(
                    startViewport: _gestureViewportStart,
                    startFocalPoint: _gestureFocalStart,
                    currentFocalPoint: focalPoint,
                    scale: details.scale,
                    plotRect: _plotRect,
                  );
                }
              });
            },
            child: CustomPaint(
              painter: FunctionPlotPainter(
                points: widget.points,
                scheme: widget.scheme,
                mode: widget.mode,
                intersectionPoints: widget.intersectionPoints,
                markedPoints: widget.markedPoints,
                viewport: _viewport,
                zoom: _zoom,
                pan: _pan,
                yaw: _yaw,
                pitch: _pitch,
              ),
              child: const SizedBox.expand(),
            ),
          ),
        );
      },
    );

    final radius = widget.borderRadius;
    return radius == null
        ? ClipRect(clipBehavior: Clip.hardEdge, child: surface)
        : ClipRRect(
            borderRadius: radius,
            clipBehavior: Clip.hardEdge,
            child: surface,
          );
  }
}
