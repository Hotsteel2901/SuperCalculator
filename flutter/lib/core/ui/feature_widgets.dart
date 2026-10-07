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
          padding: EdgeInsets.all(MediaQuery.sizeOf(context).width < 600 ? 16 : 24),
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
    final points = series.expand((item) => item).where((item) {
      return item.x.isFinite && item.y.isFinite;
    }).toList(growable: false);
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
