import 'package:flutter/material.dart';

import '../l10n/generated/app_localizations.dart';
import 'router.dart';
import 'theme/app_theme.dart';

class SuperCalculatorApp extends StatelessWidget {
  const SuperCalculatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'SuperCalculator - Next Era',
      theme: buildAppTheme(Brightness.light),
      darkTheme: buildAppTheme(Brightness.dark),
      themeMode: ThemeMode.system,
      routerConfig: appRouter,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      debugShowCheckedModeBanner: false,
    );
  }
}
