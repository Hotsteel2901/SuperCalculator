import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/design_tokens.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final tokens = SuperCalcDesignTokens.of(context);
    final scheme = Theme.of(context).colorScheme;

    return CustomScrollView(
      slivers: <Widget>[
        SliverAppBar.large(
          title: Text(l10n.appTitle),
          actions: <Widget>[
            IconButton(
              tooltip: l10n.about,
              onPressed: () => _showAbout(context),
              icon: const Icon(Icons.info_outline),
            ),
          ],
        ),
        SliverPadding(
          padding: EdgeInsets.all(tokens.pagePadding),
          sliver: SliverList(
            delegate: SliverChildListDelegate(<Widget>[
              Card(
                color: scheme.primaryContainer,
                child: Padding(
                  padding: EdgeInsets.all(tokens.pagePadding),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        l10n.welcomeTitle,
                        style: Theme.of(context).textTheme.headlineMedium
                            ?.copyWith(
                              color: scheme.onPrimaryContainer,
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      SizedBox(height: tokens.controlGap),
                      Text(
                        l10n.welcomeBody,
                        style: Theme.of(context).textTheme.bodyLarge
                            ?.copyWith(color: scheme.onPrimaryContainer),
                      ),
                      SizedBox(height: tokens.cardGap),
                      FilledButton.icon(
                        onPressed: () => context.go('/plotting'),
                        icon: const Icon(Icons.show_chart),
                        label: Text(l10n.openPlotter),
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: tokens.cardGap),
              Text(
                l10n.migrationStatus,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: tokens.controlGap),
              Wrap(
                spacing: tokens.cardGap,
                runSpacing: tokens.cardGap,
                children: <Widget>[
                  const _StatusChip(
                    label: 'Material 3',
                    icon: Icons.palette_outlined,
                  ),
                  const _StatusChip(
                    label: 'C FFI',
                    icon: Icons.memory_outlined,
                  ),
                  const _StatusChip(
                    label: 'Riverpod',
                    icon: Icons.account_tree_outlined,
                  ),
                  const _StatusChip(
                    label: 'WebAssembly',
                    icon: Icons.language_outlined,
                  ),
                ],
              ),
              SizedBox(height: tokens.pagePadding),
              _FeatureGrid(tokens: tokens),
            ]),
          ),
        ),
      ],
    );
  }

  void _showAbout(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    showAboutDialog(
      context: context,
      applicationName: l10n.appTitle,
      applicationVersion: l10n.versionLabel('0.1.0'),
      applicationIcon: const Icon(Icons.calculate_outlined),
      children: <Widget>[Text(l10n.aboutBody)],
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.label, required this.icon});

  final String label;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Chip(avatar: Icon(icon, size: 18), label: Text(label));
  }
}

class _FeatureGrid extends StatelessWidget {
  const _FeatureGrid({required this.tokens});

  final SuperCalcDesignTokens tokens;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final features = <_FeatureCardData>[
      _FeatureCardData(l10n.plotting, Icons.show_chart, '/plotting'),
      _FeatureCardData(l10n.calculus, Icons.functions, '/calculus'),
      _FeatureCardData(l10n.equations, Icons.account_tree, '/equations'),
      _FeatureCardData(l10n.ode, Icons.device_hub, '/ode'),
      _FeatureCardData(l10n.signals, Icons.graphic_eq, '/signals'),
      _FeatureCardData(l10n.dataAnalysis, Icons.insights, '/data-analysis'),
      _FeatureCardData(l10n.statistics, Icons.bar_chart, '/statistics'),
      _FeatureCardData(l10n.linearAlgebra, Icons.grid_4x4, '/linear-algebra'),
      _FeatureCardData(l10n.tools, Icons.build, '/tools'),
      _FeatureCardData(nextEraText(context, 'History', '历史'), Icons.history, '/history'),
    ];

    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final columns = constraints.maxWidth >= tokens.expandedBreakpoint
            ? 3
            : constraints.maxWidth >= tokens.mediumBreakpoint
            ? 2
            : 1;
        final width =
            (constraints.maxWidth - (columns - 1) * tokens.cardGap) / columns;
        return Wrap(
          spacing: tokens.cardGap,
          runSpacing: tokens.cardGap,
          children: features
              .map(
                (item) => SizedBox(
                  width: width,
                  child: Card(
                    child: InkWell(
                      onTap: () => context.go(item.path),
                      borderRadius: BorderRadius.circular(tokens.cornerLarge),
                      child: Padding(
                        padding: EdgeInsets.all(tokens.pagePadding),
                        child: Row(
                          children: <Widget>[
                            Icon(
                              item.icon,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            SizedBox(width: tokens.controlGap),
                            Expanded(child: Text(item.label)),
                            const Icon(Icons.arrow_forward),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              )
              .toList(growable: false),
        );
      },
    );
  }
}

class _FeatureCardData {
  const _FeatureCardData(this.label, this.icon, this.path);

  final String label;
  final IconData icon;
  final String path;
}
