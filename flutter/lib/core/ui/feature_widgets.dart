import 'package:flutter/material.dart';

import '../plot/plot_point.dart';

String nextEraText(BuildContext context, String english, String chinese) {
  return Localizations.localeOf(context).languageCode == 'zh'
      ? chinese
      : english;
}

double? parseMathNumber(String text) {
  final normalized = text.trim().toLowerCase();
  if (normalized == 'pi') {
    return 3.141592653589793;
  }
  if (normalized == '-pi') {
    return -3.141592653589793;
  }
  if (normalized == 'e') {
    return 2.718281828459045;
  }
  return double.tryParse(normalized);
}

class FeaturePageFrame extends StatelessWidget {
  const FeaturePageFrame({
    required this.title,
    required this.icon,
    required this.child,
    this.subtitle,
    super.key,
  });

  final String title;
  final IconData icon;
  final String? subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: <Widget>[
        SliverAppBar.large(
          title: Text(title),
          leading: Icon(icon),
          flexibleSpace: subtitle == null
              ? null
              : FlexibleSpaceBar(
                  titlePadding: const EdgeInsetsDirectional.only(
                    start: 72,
                    bottom: 16,
                    end: 16,
                  ),
                  background: Align(
                    alignment: AlignmentDirectional.bottomStart,
                    child: Padding(
                      padding: const EdgeInsetsDirectional.only(
                        start: 72,
                        bottom: 52,
                        end: 24,
                      ),
                      child: Text(
                        subtitle!,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                  ),
                ),
        ),
        SliverPadding(
          padding: EdgeInsets.all(
            MediaQuery.sizeOf(context).width < 600 ? 16 : 24,
          ),
          sliver: SliverToBoxAdapter(child: child),
        ),
      ],
    );
  }
}

class FeatureCard extends StatelessWidget {
  const FeatureCard({required this.child, super.key, this.title, this.icon});

  final Widget child;
  final String? title;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            if (title != null)
              Row(
                children: <Widget>[
                  if (icon != null) ...<Widget>[
                    Icon(icon, color: Theme.of(context).colorScheme.primary),
                    const SizedBox(width: 10),
                  ],
                  Expanded(
                    child: Text(
                      title!,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ),
                ],
              ),
            if (title != null) const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }
}

class ResultCard extends StatelessWidget {
  const ResultCard({required this.value, this.error, super.key});

  final String value;
  final String? error;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final hasError = error != null;
    return Semantics(
      liveRegion: true,
      child: Card(
        color: hasError ? scheme.errorContainer : scheme.secondaryContainer,
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Icon(
                hasError ? Icons.error_outline : Icons.check_circle_outline,
                color: hasError
                    ? scheme.onErrorContainer
                    : scheme.onSecondaryContainer,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  error ?? value,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: hasError
                        ? scheme.onErrorContainer
                        : scheme.onSecondaryContainer,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class FormRow extends StatelessWidget {
  const FormRow({required this.children, super.key});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 560) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: children
                .map(
                  (child) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: child,
                  ),
                )
                .toList(growable: false),
          );
        }
        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: children
              .map(
                (child) => Expanded(
                  child: Padding(
                    padding: const EdgeInsetsDirectional.only(end: 12),
                    child: child,
                  ),
                ),
              )
              .toList(growable: false),
        );
      },
    );
  }
}

/// Full-screen host for a static [CustomPainter] chart.
///
/// It is the Flutter counterpart of the native "Full Screen" plot activity:
/// the inline preview stays inside the scrollable form and this page is opened
/// explicitly to enlarge the chart without the surrounding controls.
class ChartFullscreenPage extends StatelessWidget {
  const ChartFullscreenPage({
    required this.painter,
    required this.title,
    super.key,
  });

  final CustomPainter painter;
  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: AppBar(title: Text(title)),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: CustomPaint(
              painter: painter,
              child: const SizedBox.expand(),
            ),
          ),
        ),
      ),
    );
  }
}

/// A clipped chart preview with a corner button that opens [ChartFullscreenPage].
///
/// Clipping keeps the painter from overpainting neighbouring widgets, and the
/// explicit full-screen entry point gives the enlarged secondary view the issue
/// asks for without making the inline preview pan or zoom the whole page.
class ExpandableChart extends StatelessWidget {
  const ExpandableChart({
    required this.title,
    required this.painter,
    this.height = 360,
    this.semanticsLabel,
    super.key,
  });

  final String title;
  final CustomPainter painter;
  final double height;
  final String? semanticsLabel;

  void _openFullScreen(BuildContext context) {
    Navigator.of(context, rootNavigator: true).push(
      MaterialPageRoute<void>(
        fullscreenDialog: true,
        builder: (_) => ChartFullscreenPage(painter: painter, title: title),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    Widget chart = CustomPaint(
      painter: painter,
      child: const SizedBox.expand(),
    );
    if (semanticsLabel != null) {
      chart = Semantics(label: semanticsLabel, child: chart);
    }
    return SizedBox(
      height: height,
      child: Stack(
        children: <Widget>[
          Positioned.fill(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: chart,
            ),
          ),
          Positioned(
            top: 4,
            right: 4,
            child: Material(
              color: scheme.surfaceContainerHighest.withValues(alpha: .82),
              shape: const CircleBorder(),
              clipBehavior: Clip.antiAlias,
              child: IconButton(
                tooltip: nextEraText(context, 'Full screen', '全屏'),
                onPressed: () => _openFullScreen(context),
                icon: const Icon(Icons.fullscreen),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class LineSeriesPainter extends CustomPainter {
  const LineSeriesPainter({required this.series, required this.scheme});

  final List<List<PlotPoint>> series;
  final ColorScheme scheme;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(
      Offset.zero & size,
      Paint()..color = scheme.surfaceContainerLowest,
    );
    final points = series
        .expand((item) => item)
        .where((item) {
          return item.x.isFinite && item.y.isFinite;
        })
        .toList(growable: false);
    if (points.isEmpty || size.width <= 1 || size.height <= 1) {
      return;
    }
    var minX = points.map((point) => point.x).reduce((a, b) => a < b ? a : b);
    var maxX = points.map((point) => point.x).reduce((a, b) => a > b ? a : b);
    var minY = points.map((point) => point.y).reduce((a, b) => a < b ? a : b);
    var maxY = points.map((point) => point.y).reduce((a, b) => a > b ? a : b);
    if (minX == maxX) {
      minX -= 1;
      maxX += 1;
    }
    if (minY == maxY) {
      minY -= 1;
      maxY += 1;
    }
    final xPadding = (maxX - minX) * .05;
    final yPadding = (maxY - minY) * .08;
    minX -= xPadding;
    maxX += xPadding;
    minY -= yPadding;
    maxY += yPadding;
    final grid = Paint()
      ..color = scheme.outlineVariant.withValues(alpha: .4)
      ..strokeWidth = 1;
    for (var i = 1; i < 5; i++) {
      final dx = size.width * i / 5;
      final dy = size.height * i / 5;
      canvas.drawLine(Offset(dx, 0), Offset(dx, size.height), grid);
      canvas.drawLine(Offset(0, dy), Offset(size.width, dy), grid);
    }
    final colors = <Color>[
      scheme.primary,
      scheme.tertiary,
      scheme.secondary,
      scheme.error,
    ];
    for (var seriesIndex = 0; seriesIndex < series.length; seriesIndex++) {
      final paint = Paint()
        ..color = colors[seriesIndex % colors.length]
        ..strokeWidth = 2.2
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round;
      final path = Path();
      var hasPoint = false;
      for (final point in series[seriesIndex]) {
        if (!point.x.isFinite || !point.y.isFinite) {
          hasPoint = false;
          continue;
        }
        final offset = Offset(
          (point.x - minX) / (maxX - minX) * size.width,
          (maxY - point.y) / (maxY - minY) * size.height,
        );
        if (hasPoint) {
          path.lineTo(offset.dx, offset.dy);
        } else {
          path.moveTo(offset.dx, offset.dy);
        }
        hasPoint = true;
      }
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant LineSeriesPainter oldDelegate) =>
      oldDelegate.series != series || oldDelegate.scheme != scheme;
}
