import 'package:flutter/material.dart';

import '../../l10n/generated/app_localizations.dart';
import '../home/feature_placeholder_page.dart';

class ToolsPage extends StatelessWidget {
  const ToolsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return FeaturePlaceholderPage(
      title: AppLocalizations.of(context).tools,
      icon: Icons.build,
    );
  }
}
