import 'package:flutter/material.dart';

import '../../l10n/generated/app_localizations.dart';
import '../home/feature_placeholder_page.dart';

class SignalsPage extends StatelessWidget {
  const SignalsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return FeaturePlaceholderPage(
      title: AppLocalizations.of(context).signals,
      icon: Icons.graphic_eq,
    );
  }
}
