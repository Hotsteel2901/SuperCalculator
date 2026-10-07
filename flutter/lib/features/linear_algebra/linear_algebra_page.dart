import 'package:flutter/material.dart';

import '../../l10n/generated/app_localizations.dart';
import '../home/feature_placeholder_page.dart';

class LinearAlgebraPage extends StatelessWidget {
  const LinearAlgebraPage({super.key});

  @override
  Widget build(BuildContext context) {
    return FeaturePlaceholderPage(
      title: AppLocalizations.of(context).linearAlgebra,
      icon: Icons.grid_4x4,
    );
  }
}
