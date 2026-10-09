// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'SuperCalculator - Next Era';

  @override
  String get home => 'Home';

  @override
  String get plotting => 'Plotting';

  @override
  String get calculus => 'Calculus';

  @override
  String get equations => 'Equations';

  @override
  String get ode => 'ODE';

  @override
  String get signals => 'Signals';

  @override
  String get dataAnalysis => 'Data';

  @override
  String get statistics => 'Statistics';

  @override
  String get linearAlgebra => 'Linear algebra';

  @override
  String get tools => 'Tools';

  @override
  String get settings => 'Settings';

  @override
  String get about => 'About';

  @override
  String get welcomeTitle => 'One fast workbench for exploring mathematics';

  @override
  String get welcomeBody =>
      'SuperCalculator - Next Era brings function and multi-curve plotting, parameter controls, intersection markers and free coordinate points together with calculus, equations, ODE, data, matrices and finance.';

  @override
  String get openPlotter => 'Open plotting workbench';

  @override
  String get migrationStatus => 'Next Era v6.0.0';

  @override
  String get expression => 'Expression';

  @override
  String get argumentX => 'x value';

  @override
  String get evaluate => 'Evaluate';

  @override
  String get clear => 'Clear';

  @override
  String get quickExamples => 'Quick examples';

  @override
  String get result => 'Result';

  @override
  String get plotPreview => 'Plot preview';

  @override
  String get backend => 'Backend';

  @override
  String get nativeFfi => 'Native FFI';

  @override
  String get wasm => 'WebAssembly';

  @override
  String get dartFallback => 'Dart fallback';

  @override
  String get ready => 'Ready';

  @override
  String get computing => 'Computing…';

  @override
  String get invalidExpression => 'Could not evaluate this expression.';

  @override
  String get noResult => 'Enter an expression and evaluate it.';

  @override
  String get featureComingSoon =>
      'This capability is part of the Next Era feature set and will keep gaining native and replaceable backend implementations.';

  @override
  String get aboutBody =>
      'SuperCalculator - Next Era uses a Flutter application shell with replaceable native and Dart computation backends, while preserving the shared C core and the legacy platform capability set.';

  @override
  String versionLabel(Object version) {
    return 'Version $version';
  }

  @override
  String get version => '6.0.0';

  @override
  String plotPoints(Object count) {
    return '$count sampled points';
  }

  @override
  String accessibilityPlotSummary(Object count, Object expression) {
    return 'Function plot for $expression, with $count finite samples.';
  }
}
