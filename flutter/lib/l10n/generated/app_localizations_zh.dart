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
  String get welcomeTitle => '一个工作台，清晰探索数学';

  @override
  String get welcomeBody =>
      'SuperCalculator - Next Era 将函数与多曲线绘图、参数控制、交点标记和自由坐标标点，与微积分、方程、ODE、数据、矩阵和金融计算统一起来。';

  @override
  String get openPlotter => '打开绘图工作台';

  @override
  String get migrationStatus => 'Next Era v6.0.0';

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
  String get featureComingSoon => '此能力属于 Next Era 功能集，将持续接入原生与可替换计算后端。';

  @override
  String get aboutBody =>
      'SuperCalculator - Next Era 使用 Flutter 应用壳、可替换的原生与 Dart 计算后端，并保留共享 C 核心及旧平台能力。';

  @override
  String versionLabel(Object version) {
    return '版本 $version';
  }

  @override
  String get version => '6.0.0';

  @override
  String plotPoints(Object count) {
    return '已采样 $count 个点';
  }

  @override
  String accessibilityPlotSummary(Object count, Object expression) {
    return '表达式 $expression 的函数图，共有 $count 个有效采样点。';
  }
}
