import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'function_plot_painter.dart';
import 'plot_point.dart';

/// Interactive, self-clipping plot surface shared by the inline preview and the
/// full-screen plot page.
///
/// The painter is clipped to this widget's bounds, so panning or zooming the
/// surface can never bleed over neighbouring widgets (an Android regression
/// where an unclipped [CustomPaint] overpainted the surrounding form).
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
  double _gestureZoomStart = 1;
  Offset _gesturePanStart = Offset.zero;
  Offset _gestureFocalStart = Offset.zero;
  late double _gestureYawStart = widget.initialYaw;
  late double _gesturePitchStart = widget.initialPitch;

  /// Current horizontal/vertical offset, exposed so a host can hand the exact
  /// view over to the full-screen page.
  Offset get pan => _pan;

  /// Current zoom factor.
  double get zoom => _zoom;

  /// Current 3D surface yaw.
  double get yaw => _yaw;

  /// Current 3D surface pitch.
  double get pitch => _pitch;

  /// Restores the view to the values supplied when this widget was created.
  void resetView() {
    setState(() {
      _zoom = widget.initialZoom;
      _pan = widget.initialPan;
      _yaw = widget.initialYaw;
      _pitch = widget.initialPitch;
    });
  }

  PlotPoint? _dataPointFromLocal(Offset local, Size size) {
    if (size.width <= 1 || size.height <= 1) return null;
    final finite = widget.points
        .where((point) => point.x.isFinite && point.y.isFinite)
        .toList(growable: false);
    var yMin = -5.0;
    var yMax = 5.0;
    if (finite.isNotEmpty) {
      yMin = finite
          .map((point) => point.y)
          .reduce((a, b) => math.min(a, b).toDouble());
      yMax = finite
          .map((point) => point.y)
          .reduce((a, b) => math.max(a, b).toDouble());
      if ((yMax - yMin).abs() < 1e-9) {
        yMin -= 1;
        yMax += 1;
      } else {
        final padding = (yMax - yMin) * .12;
        yMin -= padding;
        yMax += padding;
      }
    }
    final center = Offset(size.width / 2, size.height / 2);
    final base = center + (local - _pan - center) / _zoom;
    return PlotPoint(
      -10 + base.dx / size.width * 20,
      yMax - base.dy / size.height * (yMax - yMin),
    );
  }

  void _mark(Offset local, Size size) {
    if (widget.mode == 'surface') return;
    final callback = widget.onMarkPoint;
    if (callback == null) return;
    final point = _dataPointFromLocal(local, size);
    if (point != null && point.isFinite) callback(point);
  }

  void _remove(Offset local, Size size) {
    if (widget.mode == 'surface') return;
    final callback = widget.onRemoveMarkPoint;
    if (callback == null) return;
    final point = _dataPointFromLocal(local, size);
    if (point != null && point.isFinite) callback(point);
  }

  @override
  Widget build(BuildContext context) {
    final surface = LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final size = Size(constraints.maxWidth, constraints.maxHeight);
        return GestureDetector(
          behavior: HitTestBehavior.opaque,
          onDoubleTap: resetView,
          onTapUp: (details) => _mark(details.localPosition, size),
          onLongPressStart: (details) => _remove(details.localPosition, size),
          onScaleStart: (details) {
            _gestureZoomStart = _zoom;
            _gesturePanStart = _pan;
            _gestureFocalStart = details.focalPoint;
            _gestureYawStart = _yaw;
            _gesturePitchStart = _pitch;
          },
          onScaleUpdate: (details) {
            final delta = details.focalPoint - _gestureFocalStart;
            setState(() {
              _zoom = (_gestureZoomStart * details.scale)
                  .clamp(.5, 4.0)
                  .toDouble();
              if (widget.mode == 'surface') {
                _yaw = _gestureYawStart + delta.dx * .01;
                _pitch = (_gesturePitchStart - delta.dy * .01)
                    .clamp(-1.35, 1.35)
                    .toDouble();
              } else {
                _pan = _gesturePanStart + delta;
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
              zoom: _zoom,
              pan: _pan,
              yaw: _yaw,
              pitch: _pitch,
            ),
            child: const SizedBox.expand(),
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
