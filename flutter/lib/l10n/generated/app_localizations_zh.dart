// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Chinese (`zh`).
class AppLocalizationsZh extends AppLocalizations {
  AppLocalizationsZh([String locale = 'zh']) : super(locale);

  @override
  String get appTitle => 'SuperCalculator - Next Era';

  @override
  String get home => '首页';

  @override
  String get plotting => '绘图';

  @override
  String get calculus => '微积分';

  @override
  String get equations => '方程';

  @override
  String get ode => '微分方程';

  @override
  String get signals => '信号处理';

  @override
  String get dataAnalysis => '数据分析';

  @override
  String get statistics => '统计概率';

  @override
  String get linearAlgebra => '线性代数';

  @override
  String get tools => '工具';

  @override
  String get settings => '设置';

  @override
  String get about => '关于';

  @override
  String get welcomeTitle => '更清晰地探索数学';

  @override
  String get welcomeBody => '采用 Material 3 Expressive 的跨平台科学计算器，共享原生计算核心。';

  @override
  String get openPlotter => '打开绘图器';

  @override
  String get migrationStatus => 'Flutter 迁移进行中';

  @override
  String get expression => '表达式';

  @override
  String get argumentX => 'x 值';

  @override
  String get evaluate => '计算';

  @override
  String get clear => '清空';

  @override
  String get quickExamples => '快速示例';

  @override
  String get result => '结果';

  @override
  String get plotPreview => '绘图预览';

  @override
  String get backend => '计算后端';

  @override
  String get nativeFfi => '原生 FFI';

  @override
  String get wasm => 'WebAssembly';

  @override
  String get dartFallback => 'Dart 回退';

  @override
  String get ready => '就绪';

  @override
  String get computing => '计算中…';

  @override
  String get invalidExpression => '无法计算此表达式。';

  @override
  String get noResult => '输入表达式后点击计算。';

  @override
  String get featureComingSoon => '此功能已经加入迁移矩阵，将按阶段逐步接入。';

  @override
  String get aboutBody =>
      'SuperCalculator - Next Era 使用一个 Flutter 应用替代旧 Tkinter 和 Java UI，同时保留 C 计算核心。';

  @override
  String versionLabel(Object version) {
    return '版本 $version';
  }

  @override
  String get version => '0.1.0';

  @override
  String plotPoints(Object count) {
    return '已采样 $count 个点';
  }

  @override
  String accessibilityPlotSummary(Object count, Object expression) {
    return '表达式 $expression 的函数图，共有 $count 个有效采样点。';
  }
}
