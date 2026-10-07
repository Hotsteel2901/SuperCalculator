// GENERATED-LIKE COMPATIBILITY STUB
//
// The canonical source is lib/l10n/app_*.arb. Running `flutter gen-l10n`
// replaces this file with the Flutter-generated implementation. Keeping this
// small checked-in implementation makes the scaffold usable before the SDK is
// installed in a contributor environment.

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

class AppLocalizations {
  const AppLocalizations(this.locale);

  final Locale locale;

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ];

  static const List<Locale> supportedLocales = <Locale>[Locale('en'), Locale('zh')];

  static AppLocalizations of(BuildContext context) {
    final value = Localizations.of<AppLocalizations>(context, AppLocalizations);
    assert(value != null, 'AppLocalizations is not available in this context.');
    return value!;
  }

  bool get isChinese => locale.languageCode.toLowerCase() == 'zh';

  String get appTitle => 'SuperCalculator - Next Era';
  String get home => isChinese ? '首页' : 'Home';
  String get plotting => isChinese ? '绘图' : 'Plotting';
  String get calculus => isChinese ? '微积分' : 'Calculus';
  String get equations => isChinese ? '方程' : 'Equations';
  String get ode => isChinese ? '微分方程' : 'ODE';
  String get signals => isChinese ? '信号处理' : 'Signals';
  String get dataAnalysis => isChinese ? '数据分析' : 'Data';
  String get statistics => isChinese ? '统计概率' : 'Statistics';
  String get linearAlgebra => isChinese ? '线性代数' : 'Linear algebra';
  String get tools => isChinese ? '工具' : 'Tools';
  String get settings => isChinese ? '设置' : 'Settings';
  String get about => isChinese ? '关于' : 'About';
  String get welcomeTitle => isChinese ? '更清晰地探索数学' : 'A clearer way to explore mathematics';
  String get welcomeBody => isChinese
      ? '采用 Material 3 Expressive 的跨平台科学计算器，共享原生计算核心。'
      : 'A Material 3 Expressive scientific calculator with a shared native computation core.';
  String get openPlotter => isChinese ? '打开绘图器' : 'Open plotter';
  String get migrationStatus => isChinese ? 'Flutter 迁移进行中' : 'Flutter migration in progress';
  String get expression => isChinese ? '表达式' : 'Expression';
  String get argumentX => isChinese ? 'x 值' : 'x value';
  String get evaluate => isChinese ? '计算' : 'Evaluate';
  String get clear => isChinese ? '清空' : 'Clear';
  String get quickExamples => isChinese ? '快速示例' : 'Quick examples';
  String get result => isChinese ? '结果' : 'Result';
  String get plotPreview => isChinese ? '绘图预览' : 'Plot preview';
  String get backend => isChinese ? '计算后端' : 'Backend';
  String get nativeFfi => isChinese ? '原生 FFI' : 'Native FFI';
  String get wasm => 'WebAssembly';
  String get dartFallback => isChinese ? 'Dart 回退' : 'Dart fallback';
  String get ready => isChinese ? '就绪' : 'Ready';
  String get computing => isChinese ? '计算中…' : 'Computing…';
  String get invalidExpression => isChinese ? '无法计算此表达式。' : 'Could not evaluate this expression.';
  String get noResult => isChinese ? '输入表达式后点击计算。' : 'Enter an expression and evaluate it.';
  String get featureComingSoon => isChinese
      ? '此功能已经加入迁移矩阵，将按阶段逐步接入。'
      : 'This feature is included in the migration matrix and is being connected incrementally.';
  String get aboutBody => isChinese
      ? 'SuperCalculator - Next Era 使用一个 Flutter 应用替代旧 Tkinter 和 Java UI，同时保留 C 计算核心。'
      : 'SuperCalculator - Next Era replaces the legacy Tkinter and Java UI with one Flutter application while preserving the C computation core.';
  String get version => '0.1.0';
  String versionLabel(String version) => isChinese ? '版本 $version' : 'Version $version';
  String plotPoints(int count) => isChinese ? '已采样 $count 个点' : '$count sampled points';
  String accessibilityPlotSummary(String expression, int count) => isChinese
      ? '表达式 $expression 的函数图，共有 $count 个有效采样点。'
      : 'Function plot for $expression, with $count finite samples.';
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) =>
      AppLocalizations.supportedLocales.any((item) => item.languageCode == locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) =>
      SynchronousFuture<AppLocalizations>(AppLocalizations(_resolve(locale)));

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;

  Locale _resolve(Locale locale) => locale.languageCode == 'zh' ? const Locale('zh') : const Locale('en');
}
