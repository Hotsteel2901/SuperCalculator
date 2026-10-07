import 'package:flutter/material.dart';

import '../../l10n/generated/app_localizations.dart';
import '../home/feature_placeholder_page.dart';

class CalculusPage extends StatelessWidget {
  const CalculusPage({super.key});

  @override
  Widget build(BuildContext context) {
    return FeaturePlaceholderPage(
      title: AppLocalizations.of(context).calculus,
      icon: Icons.functions,
    );
  }
}
