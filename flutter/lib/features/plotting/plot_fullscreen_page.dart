import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/plot/interactive_plot_view.dart';
import '../../core/ui/feature_widgets.dart';
import 'calculator_controller.dart';

/// Secondary, immersive plot page.
///
/// Mirrors the native full-screen plot activity: the inline preview stays in
/// the scrollable form, and this page is opened explicitly to enlarge the plot
/// and keep interacting with it (markers, pinch zoom, pan, 3D rotation).
class PlotFullscreenPage extends ConsumerStatefulWidget {
  const PlotFullscreenPage({
    super.key,
    this.initialZoom = 1,
    this.initialPan = Offset.zero,
    this.initialYaw = -.65,
    this.initialPitch = .55,
  });

  final double initialZoom;
  final Offset initialPan;
  final double initialYaw;
  final double initialPitch;

  @override
  ConsumerState<PlotFullscreenPage> createState() => _PlotFullscreenPageState();
}

class _PlotFullscreenPageState extends ConsumerState<PlotFullscreenPage> {
  final GlobalKey<InteractivePlotViewState> _viewKey =
      GlobalKey<InteractivePlotViewState>();

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(calculatorControllerProvider);
    final controller = ref.read(calculatorControllerProvider.notifier);
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      backgroundColor: scheme.surface,
      appBar: AppBar(
        title: Text(nextEraText(context, 'Full-screen plot', '全屏绘图')),
        actions: <Widget>[
          IconButton(
            tooltip: nextEraText(context, 'Reset view', '重置视图'),
            onPressed: () => _viewKey.currentState?.resetView(),
            icon: const Icon(Icons.center_focus_strong),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: InteractivePlotView(
            key: _viewKey,
            points: state.points,
            mode: state.mode,
            scheme: scheme,
            intersectionPoints: state.intersectionPoints,
            markedPoints: state.markedPoints,
            onMarkPoint: controller.addMarkedPoint,
            onRemoveMarkPoint: (point) =>
                controller.removeNearestMarkedPoint(point),
            borderRadius: BorderRadius.circular(16),
            initialZoom: widget.initialZoom,
            initialPan: widget.initialPan,
            initialYaw: widget.initialYaw,
            initialPitch: widget.initialPitch,
          ),
        ),
      ),
    );
  }
}
