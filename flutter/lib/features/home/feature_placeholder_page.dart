import 'package:flutter/material.dart';

import '../../app/theme/design_tokens.dart';
import '../../l10n/generated/app_localizations.dart';

class FeaturePlaceholderPage extends StatelessWidget {
  const FeaturePlaceholderPage({required this.title, required this.icon, super.key});

  final String title;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final tokens = SuperCalcDesignTokens.of(context);
    final scheme = Theme.of(context).colorScheme;
    return CustomScrollView(
      slivers: <Widget>[
        SliverAppBar.large(title: Text(title)),
        SliverFillRemaining(
          hasScrollBody: false,
          child: Center(
            child: Padding(
              padding: EdgeInsets.all(tokens.pagePadding),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 560),
                child: Card(
                  color: scheme.surfaceContainerLow,
                  child: Padding(
                    padding: EdgeInsets.all(tokens.pagePadding),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: <Widget>[
                        Icon(icon, size: 48, color: scheme.primary),
                        SizedBox(height: tokens.cardGap),
                        Text(title, style: Theme.of(context).textTheme.headlineSmall),
                        SizedBox(height: tokens.controlGap),
                        Text(
                          l10n.featureComingSoon,
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
