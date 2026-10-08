import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/compute/calculation_models.dart';
import '../../core/compute/computation.dart';
import '../../core/history/history_repository.dart';
import '../../core/ui/feature_widgets.dart';

String _calendarDefaultDate([int offsetDays = 0]) {
  final date = DateTime.now().toUtc().add(Duration(days: offsetDays));
  final year = date.year.toString().padLeft(4, '0');
  final month = date.month.toString().padLeft(2, '0');
  final day = date.day.toString().padLeft(2, '0');
  return '$year-$month-$day';
}

class AdvancedToolsPage extends ConsumerStatefulWidget {
  const AdvancedToolsPage({super.key});

  @override
  ConsumerState<AdvancedToolsPage> createState() => _AdvancedToolsPageState();
}

class _AdvancedToolsPageState extends ConsumerState<AdvancedToolsPage> {
  final _real = TextEditingController(text: '1');
  final _imaginary = TextEditingController(text: '2');
  final _real2 = TextEditingController(text: '3');
  final _imaginary2 = TextEditingController(text: '4');
  final _integer = TextEditingController(text: '360');
  final _integer2 = TextEditingController(text: '48');
  final _modulus = TextEditingController(text: '1009');
  final _distributionX = TextEditingController(text: '1.96');
  final _distributionParameter = TextEditingController(text: '0,1');
  final _financePrincipal = TextEditingController(text: '250000');
  final _financeRate = TextEditingController(text: '0.045');
  final _financePeriods = TextEditingController(text: '360');
  final _financeCompounds = TextEditingController(text: '12');
  final _financeYears = TextEditingController(text: '10');
  final _financeCashFlows = TextEditingController(text: '-1000,300,400,500');
  final _financeSalvage = TextEditingController(text: '10000');
  final _financeYear = TextEditingController(text: '1');
  final _financeCoupon = TextEditingController(text: '0.05');
  final _financeMarket = TextEditingController(text: '0.04');
  final _financeContribution = TextEditingController(text: '1000');
  final _probabilityN = TextEditingController(text: '10');
  final _probabilityR = TextEditingController(text: '3');
  final _probabilityA = TextEditingController(text: '0.6');
  final _probabilityB = TextEditingController(text: '0.5');
  final _probabilityIntersection = TextEditingController(text: '0.2');
  final _calendarDate = TextEditingController(text: _calendarDefaultDate());
  final _calendarDate2 = TextEditingController(text: _calendarDefaultDate(30));
  final _calendarDays = TextEditingController(text: '7');
  final _customDefinitions = TextEditingController(text: 'f=x^2+1');
  final _customExpression = TextEditingController(text: 'f(3)');
  final _tableExpression = TextEditingController(text: 'sin(x)');
  final _tableStart = TextEditingController(text: '-3.14');
  final _tableEnd = TextEditingController(text: '3.14');
  final _tableRows = TextEditingController(text: '21');
  String _complexOperation = 'add';
  String _integerOperation = 'factor';
  int _bitwiseWidth = 32;
  String _distribution = 'normal';
  String _probabilityOperation = 'combination';
  String _calendarOperation = 'weekday';
  String _financeOperation = 'loan';
  String? _complexResult;
  String? _integerResult;
  CalcDistributionResult? _distributionResult;
  String? _financeResult;
  String? _probabilityResult;
  String? _calendarResult;
  String? _customResult;
  String? _tableResult;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    for (final controller in <TextEditingController>[
      _real,
      _imaginary,
      _real2,
      _imaginary2,
      _integer,
      _integer2,
      _modulus,
      _distributionX,
      _distributionParameter,
      _financePrincipal,
      _financeRate,
      _financePeriods,
      _financeCompounds,
      _financeYears,
      _financeCashFlows,
      _financeSalvage,
      _financeYear,
      _financeCoupon,
      _financeMarket,
      _financeContribution,
      _probabilityN,
      _probabilityR,
      _probabilityA,
      _probabilityB,
      _probabilityIntersection,
      _calendarDate,
      _calendarDate2,
      _calendarDays,
      _customDefinitions,
      _customExpression,
      _tableExpression,
      _tableStart,
      _tableEnd,
      _tableRows,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FeaturePageFrame(
      title: nextEraText(context, 'Advanced tools', '高级工具'),
      icon: Icons.science_outlined,
      subtitle: nextEraText(
        context,
        'Complex numbers, number theory, distributions, finance and custom functions share the same replaceable computation layer.',
        '复数、数论、分布、金融和自定义函数共用可替换的计算层。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          _complexCard(context),
          const SizedBox(height: 16),
          _numberTheoryCard(context),
          const SizedBox(height: 16),
          _distributionCard(context),
          const SizedBox(height: 16),
          _financeCard(context),
          const SizedBox(height: 16),
          _probabilityCard(context),
          const SizedBox(height: 16),
          _calendarCard(context),
          const SizedBox(height: 16),
          _customFunctionCard(context),
          if (_busy) ...<Widget>[
            const SizedBox(height: 16),
            const LinearProgressIndicator(),
          ],
          if (_error != null) ...<Widget>[
            const SizedBox(height: 16),
            ResultCard(value: '', error: _error),
          ],
        ],
      ),
    );
  }

  Widget _complexCard(BuildContext context) {
    return FeatureCard(
      title: nextEraText(context, 'Complex numbers', '复数'),
      icon: Icons.blur_circular,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FormRow(
            children: <Widget>[
              _numberField(_real, 'z₁ real', 'z₁ 实部'),
              _numberField(_imaginary, 'z₁ imag', 'z₁ 虚部'),
              _numberField(_real2, 'z₂ real', 'z₂ 实部'),
              _numberField(_imaginary2, 'z₂ imag', 'z₂ 虚部'),
            ],
          ),
          const SizedBox(height: 12),
          FormRow(
            children: <Widget>[
              DropdownButtonFormField<String>(
                initialValue: _complexOperation,
                decoration: InputDecoration(
                  labelText: nextEraText(context, 'Operation', '运算'),
                ),
                items:
                    <String>[
                          'add',
                          'subtract',
                          'multiply',
                          'divide',
                          'power',
                          'sin',
                          'cos',
                          'tan',
                          'exp',
                          'log',
                          'sqrt',
                          'conjugate',
                        ]
                        .map(
                          (value) => DropdownMenuItem(
                            value: value,
                            child: Text(value),
                          ),
                        )
                        .toList(growable: false),
                onChanged: (value) =>
                    setState(() => _complexOperation = value ?? 'add'),
              ),
              FilledButton.icon(
                onPressed: _busy ? null : _calculateComplex,
                icon: const Icon(Icons.calculate_outlined),
                label: Text(nextEraText(context, 'Calculate', '计算')),
              ),
            ],
          ),
          if (_complexResult != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              _complexResult!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _numberTheoryCard(BuildContext context) {
    return FeatureCard(
      title: nextEraText(context, 'Number theory and bitwise', '数论与位运算'),
      icon: Icons.numbers,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FormRow(
            children: <Widget>[
              _numberField(_integer, 'n', 'n'),
              _numberField(_integer2, 'm', 'm'),
              _numberField(_modulus, 'modulus', '模数'),
              DropdownButtonFormField<String>(
                initialValue: _integerOperation,
                decoration: InputDecoration(
                  labelText: nextEraText(context, 'Operation', '运算'),
                ),
                items:
                    <String>[
                          'factor',
                          'prime',
                          'gcd',
                          'lcm',
                          'fibonacci',
                          'modPow',
                          'totient',
                          'bitwise and',
                          'bitwise or',
                          'bitwise xor',
                          'bitwise not',
                          'bitwise shl',
                          'bitwise shr',
                        ]
                        .map(
                          (value) => DropdownMenuItem(
                            value: value,
                            child: Text(value),
                          ),
                        )
                        .toList(growable: false),
                onChanged: (value) =>
                    setState(() => _integerOperation = value ?? 'factor'),
              ),
              DropdownButtonFormField<int>(
                initialValue: _bitwiseWidth,
                decoration: InputDecoration(
                  labelText: nextEraText(context, 'Bit width', '位宽'),
                ),
                items: <int>[8, 16, 32]
                    .map(
                      (value) => DropdownMenuItem<int>(
                        value: value,
                        child: Text('$value'),
                      ),
                    )
                    .toList(growable: false),
                onChanged: (value) =>
                    setState(() => _bitwiseWidth = value ?? 32),
              ),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _busy ? null : _calculateInteger,
            icon: const Icon(Icons.functions),
            label: Text(nextEraText(context, 'Run number theory', '运行数论运算')),
          ),
          if (_integerResult != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              _integerResult!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _distributionCard(BuildContext context) {
    final result = _distributionResult;
    return FeatureCard(
      title: nextEraText(context, 'Probability distributions', '概率分布'),
      icon: Icons.stacked_bar_chart,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FormRow(
            children: <Widget>[
              DropdownButtonFormField<String>(
                initialValue: _distribution,
                decoration: InputDecoration(
                  labelText: nextEraText(context, 'Distribution', '分布'),
                ),
                items:
                    <String>['normal', 't', 'chi2', 'f', 'binomial', 'poisson']
                        .map(
                          (value) => DropdownMenuItem(
                            value: value,
                            child: Text(value),
                          ),
                        )
                        .toList(growable: false),
                onChanged: (value) =>
                    setState(() => _distribution = value ?? 'normal'),
              ),
              _numberField(_distributionX, 'x / probability', 'x / 概率'),
              TextField(
                controller: _distributionParameter,
                decoration: InputDecoration(
                  labelText: nextEraText(context, 'Parameters', '参数'),
                  helperText: nextEraText(
                    context,
                    'normal: μ,σ; t: ν; binomial: n,p',
                    'normal：μ,σ；t：ν；二项：n,p',
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _busy ? null : _calculateDistribution,
            icon: const Icon(Icons.area_chart),
            label: Text(
              nextEraText(
                context,
                'Evaluate PDF / CDF / PPF',
                '计算 PDF / CDF / PPF',
              ),
            ),
          ),
          if (result != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              'pdf = ${_format(result.pdf)}\ncdf = ${_format(result.cdf)}\nppf(input) = ${_format(result.ppf)}',
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _financeCard(BuildContext context) {
    return FeatureCard(
      title: nextEraText(context, 'Finance', '金融计算'),
      icon: Icons.account_balance,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          DropdownButtonFormField<String>(
            initialValue: _financeOperation,
            decoration: InputDecoration(
              labelText: nextEraText(context, 'Operation', '运算'),
            ),
            items:
                <String>[
                      'loan',
                      'compound',
                      'npv',
                      'irr',
              'depreciation',
              'bond',
              'retirement',
            ]
                    .map(
                      (value) => DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      ),
                    )
                    .toList(growable: false),
            onChanged: (value) =>
                setState(() => _financeOperation = value ?? 'loan'),
          ),
          const SizedBox(height: 12),
          FormRow(
            children: <Widget>[
              _numberField(_financePrincipal, 'Principal / face', '本金 / 面值'),
              _numberField(_financeRate, 'Annual / market rate', '年利率 / 市场利率'),
              _numberField(_financePeriods, 'Periods / life', '期数 / 年限'),
              _numberField(_financeCompounds, 'Compounds/year', '每年复利次数'),
              _numberField(_financeYears, 'Years', '年数'),
            ],
          ),
          const SizedBox(height: 12),
          FormRow(
            children: <Widget>[
              _numberField(_financeCashFlows, 'Cash flows', '现金流'),
              _numberField(_financeSalvage, 'Salvage value', '残值'),
              _numberField(_financeYear, 'Year', '年份'),
              _numberField(_financeCoupon, 'Coupon rate', '票面利率'),
              _numberField(_financeMarket, 'Bond market rate', '债券市场利率'),
              _numberField(_financeContribution, 'Monthly contribution', '每月投入'),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            nextEraText(
              context,
              'Cash flows use comma-separated values, for example -1000,300,400,500.',
              '现金流使用逗号分隔，例如 -1000,300,400,500。',
            ),
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _busy ? null : _calculateFinance,
            icon: const Icon(Icons.payments_outlined),
            label: Text(nextEraText(context, 'Calculate', '计算')),
          ),
          if (_financeResult != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              _financeResult!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _probabilityCard(BuildContext context) {
    return FeatureCard(
      title: nextEraText(context, 'Probability', '概率计算'),
      icon: Icons.percent,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          DropdownButtonFormField<String>(
            initialValue: _probabilityOperation,
            decoration: InputDecoration(
              labelText: nextEraText(context, 'Operation', '运算'),
            ),
            items:
                <String>[
                      'combination',
                      'permutation',
                      'binomial',
                      'complement',
                      'union',
                      'conditional',
                      'bayes',
                    ]
                    .map(
                      (value) => DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      ),
                    )
                    .toList(growable: false),
            onChanged: (value) =>
                setState(() => _probabilityOperation = value ?? 'combination'),
          ),
          const SizedBox(height: 12),
          FormRow(
            children: <Widget>[
              _numberField(_probabilityN, 'n', 'n'),
              _numberField(_probabilityR, 'r / k', 'r / k'),
              _numberField(_probabilityA, 'P(A) / prior', 'P(A) / 先验'),
              _numberField(_probabilityB, 'P(B) / likelihood', 'P(B) / 似然'),
              _numberField(
                _probabilityIntersection,
                'P(A and B) / evidence',
                'P(A 且 B) / 证据',
              ),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _busy ? null : _calculateProbability,
            icon: const Icon(Icons.calculate_outlined),
            label: Text(nextEraText(context, 'Calculate probability', '计算概率')),
          ),
          if (_probabilityResult != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              _probabilityResult!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _calendarCard(BuildContext context) {
    return FeatureCard(
      title: nextEraText(context, 'Calendar', '万年历'),
      icon: Icons.calendar_month,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          DropdownButtonFormField<String>(
            initialValue: _calendarOperation,
            decoration: InputDecoration(
              labelText: nextEraText(context, 'Operation', '运算'),
            ),
            items: <String>['weekday', 'difference', 'add']
                .map(
                  (value) => DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  ),
                )
                .toList(growable: false),
            onChanged: (value) =>
                setState(() => _calendarOperation = value ?? 'weekday'),
          ),
          const SizedBox(height: 12),
          FormRow(
            children: <Widget>[
              TextField(
                controller: _calendarDate,
                decoration: InputDecoration(
                  labelText: nextEraText(context, 'Date', '日期'),
                  hintText: 'YYYY-MM-DD',
                ),
              ),
              TextField(
                controller: _calendarDate2,
                decoration: InputDecoration(
                  labelText: nextEraText(context, 'Second date', '第二个日期'),
                  hintText: 'YYYY-MM-DD',
                ),
              ),
              _numberField(_calendarDays, 'Days', '天数'),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _busy ? null : _calculateCalendar,
            icon: const Icon(Icons.event_available_outlined),
            label: Text(nextEraText(context, 'Calculate date', '计算日期')),
          ),
          if (_calendarResult != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              _calendarResult!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _customFunctionCard(BuildContext context) {
    return FeatureCard(
      title: nextEraText(
        context,
        'Custom functions and table seed',
        '自定义函数与函数表',
      ),
      icon: Icons.functions,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          TextField(
            controller: _customDefinitions,
            decoration: InputDecoration(
              labelText: nextEraText(context, 'Definitions', '定义'),
              helperText: nextEraText(
                context,
                'Use f=x^2+1; g=sin(x)',
                '使用 f=x^2+1；g=sin(x)',
              ),
            ),
            style: const TextStyle(fontFamily: 'monospace'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _customExpression,
            decoration: InputDecoration(
              labelText: nextEraText(context, 'Expression', '表达式'),
            ),
            style: const TextStyle(fontFamily: 'monospace'),
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _busy ? null : _evaluateCustom,
            icon: const Icon(Icons.play_arrow),
            label: Text(
              nextEraText(context, 'Evaluate custom function', '计算自定义函数'),
            ),
          ),
          if (_customResult != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              _customResult!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
          const SizedBox(height: 20),
          Text(
            nextEraText(context, 'Function table', '函数表'),
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _tableExpression,
            decoration: InputDecoration(
              labelText: nextEraText(context, 'f(x)', 'f(x)'),
              helperText: nextEraText(
                context,
                'Generate a CSV-ready numeric table for plotting or export.',
                '生成可用于绘图或导出的 CSV 数值表。',
              ),
            ),
            style: const TextStyle(fontFamily: 'monospace'),
          ),
          const SizedBox(height: 8),
          FormRow(
            children: <Widget>[
              _numberField(_tableStart, 'Start', '起点'),
              _numberField(_tableEnd, 'End', '终点'),
              _numberField(_tableRows, 'Rows', '行数'),
            ],
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 12,
            runSpacing: 8,
            children: <Widget>[
              OutlinedButton.icon(
                onPressed: _busy ? null : _buildFunctionTable,
                icon: const Icon(Icons.table_chart_outlined),
                label: Text(nextEraText(context, 'Generate table', '生成函数表')),
              ),
              OutlinedButton.icon(
                onPressed: _tableResult == null
                    ? null
                    : () async {
                        await Clipboard.setData(
                          ClipboardData(text: _tableResult!),
                        );
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                nextEraText(context, 'CSV copied.', 'CSV 已复制。'),
                              ),
                            ),
                          );
                        }
                      },
                icon: const Icon(Icons.copy_outlined),
                label: Text(nextEraText(context, 'Copy CSV', '复制 CSV')),
              ),
            ],
          ),
          if (_tableResult != null) ...<Widget>[
            const SizedBox(height: 12),
            SelectableText(
              _tableResult!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _numberField(TextEditingController controller, String en, String zh) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: nextEraText(context, en, zh)),
      keyboardType: const TextInputType.numberWithOptions(
        decimal: true,
        signed: true,
      ),
    );
  }

  Future<void> _calculateComplex() async {
    final values = <double?>[
      double.tryParse(_real.text),
      double.tryParse(_imaginary.text),
      double.tryParse(_real2.text),
      double.tryParse(_imaginary2.text),
    ];
    if (values.any((value) => value == null)) {
      return _showError('Enter four finite complex components.');
    }
    await _runBusy(() async {
      final result = await ref
          .read(calcBackendProvider)
          .complexOperation(
            _complexOperation,
            ComplexValue(values[0]!, values[1]!),
            ComplexValue(values[2]!, values[3]!),
          );
      _complexResult =
          '$result\n|z| = ${result.magnitude.toStringAsPrecision(10)}\narg(z) = ${result.phase.toStringAsPrecision(10)}';
    },
      historyExpression: 'complex $_complexOperation',
      historyResult: () => _complexResult,
    );
  }

  Future<void> _calculateInteger() async {
    final n = BigInt.tryParse(_integer.text.trim());
    final m = BigInt.tryParse(_integer2.text.trim());
    final modulus = BigInt.tryParse(_modulus.text.trim());
    if (n == null || m == null || modulus == null) {
      return _showError('Enter integer inputs.');
    }
    await _runBusy(() async {
      _integerResult = switch (_integerOperation) {
        'factor' => DartComputation.formatFactors(
          DartComputation.factorInteger(n),
        ),
        'prime' => DartComputation.isPrime(n) ? 'prime' : 'not prime',
        'gcd' => '${DartComputation.gcd(n, m)}',
        'lcm' => '${DartComputation.lcm(n, m)}',
        'fibonacci' => '${DartComputation.fibonacci(n.toInt())}',
        'modPow' => '${DartComputation.modPow(n, m, modulus)}',
        'totient' => '${DartComputation.eulerTotient(n)}',
        _ => _formatBitwise(
          DartComputation.bitwise(
            _integerOperation.replaceFirst('bitwise ', ''),
            n.toInt(),
            m.toInt(),
            _bitwiseWidth,
          ),
          _bitwiseWidth,
        ),
      };
    },
      historyExpression: '$_integerOperation: ${_integer.text}',
      historyResult: () => _integerResult,
    );
  }

  String _formatBitwise(int value, int width) {
    final binary = value.toRadixString(2).padLeft(width, '0');
    final octal = value.toRadixString(8);
    final hexadecimal = value.toRadixString(16).toUpperCase();
    return 'bin = $binary\noct = $octal\ndec = $value\nhex = 0x$hexadecimal';
  }

  String? _distributionSummary() {
    final result = _distributionResult;
    if (result == null) return null;
    return 'pdf = ${_format(result.pdf)}; cdf = ${_format(result.cdf)}; ppf = ${_format(result.ppf)}';
  }

  Future<void> _calculateDistribution() async {
    final x = double.tryParse(_distributionX.text.trim());
    if (x == null) {
      return _showError('Enter x or a probability.');
    }
    final values = _distributionParameter.text
        .split(RegExp(r'[,;\s]+'))
        .where((value) => value.isNotEmpty)
        .map(double.tryParse)
        .toList();
    if (values.any((value) => value == null)) {
      return _showError('Parameters must be numeric.');
    }
    final parameters = switch (_distribution) {
      'normal' => <String, double>{
        'mu': values.isNotEmpty ? values[0]! : 0,
        'sigma': values.length > 1 ? values[1]! : 1,
      },
      't' => <String, double>{'nu': values.isNotEmpty ? values[0]! : 5},
      'chi2' => <String, double>{'k': values.isNotEmpty ? values[0]! : 3},
      'f' => <String, double>{
        'd1': values.isNotEmpty ? values[0]! : 5,
        'd2': values.length > 1 ? values[1]! : 10,
      },
      'binomial' => <String, double>{
        'n': values.isNotEmpty ? values[0]! : 20,
        'p': values.length > 1 ? values[1]! : .5,
      },
      _ => <String, double>{'lambda': values.isNotEmpty ? values[0]! : 5},
    };
    await _runBusy(() async {
      _distributionResult = await ref
          .read(calcBackendProvider)
          .distribution(_distribution, x, parameters);
    },
      historyExpression: '$_distribution distribution at x=$x',
      historyResult: _distributionSummary,
    );
  }

  Future<void> _calculateProbability() async {
    final n = int.tryParse(_probabilityN.text.trim());
    final r = int.tryParse(_probabilityR.text.trim());
    final a = double.tryParse(_probabilityA.text.trim());
    final b = double.tryParse(_probabilityB.text.trim());
    final intersection = double.tryParse(_probabilityIntersection.text.trim());
    if (n == null ||
        r == null ||
        a == null ||
        b == null ||
        intersection == null) {
      return _showError('Enter valid probability inputs.');
    }
    await _runBusy(() async {
      final result = switch (_probabilityOperation) {
        'combination' => 'C($n, $r) = ${DartComputation.combination(n, r)}',
        'permutation' => 'P($n, $r) = ${DartComputation.permutation(n, r)}',
        'binomial' =>
          'P(X=$r) = ${DartComputation.binomialProbability(n: n, k: r, p: a).toStringAsPrecision(12)}\nmean = ${DartComputation.binomialMean(n, a).toStringAsPrecision(12)}\nvariance = ${DartComputation.binomialVariance(n, a).toStringAsPrecision(12)}',
        'complement' =>
          'P(not A) = ${DartComputation.complementProbability(a).toStringAsPrecision(12)}',
        'union' =>
          'P(A or B) = ${DartComputation.unionProbability(eventA: a, eventB: b, intersection: intersection).toStringAsPrecision(12)}',
        'conditional' =>
          'P(A | B) = ${DartComputation.conditionalProbability(intersection: intersection, given: b).toStringAsPrecision(12)}',
        'bayes' =>
          'P(A | evidence) = ${DartComputation.bayesProbability(prior: a, likelihood: b, evidence: intersection).toStringAsPrecision(12)}',
        _ => '',
      };
      _probabilityResult = result;
    },
      historyExpression: 'probability $_probabilityOperation',
      historyResult: () => _probabilityResult,
    );
  }

  Future<void> _calculateCalendar() async {
    await _runBusy(() async {
      _calendarResult = switch (_calendarOperation) {
        'weekday' => _weekdayLabel(
          context,
          DartComputation.calendarWeekday(_calendarDate.text),
        ),
        'difference' =>
          '${DartComputation.calendarDateDifference(_calendarDate.text, _calendarDate2.text)} days',
        'add' => DartComputation.calendarAddDays(
          _calendarDate.text,
          int.parse(_calendarDays.text.trim()),
        ),
        _ => '',
      };
    },
      historyExpression: 'calendar $_calendarOperation: ${_calendarDate.text}',
      historyResult: () => _calendarResult,
    );
  }

  String _weekdayLabel(BuildContext context, int weekday) {
    const english = <String>[
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
      'Sunday',
    ];
    const chinese = <String>['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    return nextEraText(context, english[weekday - 1], chinese[weekday - 1]);
  }

  Future<void> _calculateFinance() async {
    final principal = double.tryParse(_financePrincipal.text.trim());
    final rate = double.tryParse(_financeRate.text.trim());
    final periods = int.tryParse(_financePeriods.text.trim());
    final compounds = int.tryParse(_financeCompounds.text.trim());
    final years = double.tryParse(_financeYears.text.trim());
    final salvage = double.tryParse(_financeSalvage.text.trim());
    final year = int.tryParse(_financeYear.text.trim());
    final coupon = double.tryParse(_financeCoupon.text.trim());
    final market = double.tryParse(_financeMarket.text.trim());
    final contribution = double.tryParse(_financeContribution.text.trim());
    final cashFlows = _financeCashFlows.text
        .split(RegExp(r'[,;\s]+'))
        .where((value) => value.trim().isNotEmpty)
        .map(double.tryParse)
        .toList(growable: false);
    if (principal == null ||
        rate == null ||
        periods == null ||
        compounds == null ||
        years == null ||
        salvage == null ||
        year == null ||
        coupon == null ||
        market == null ||
        contribution == null ||
        cashFlows.any((value) => value == null)) {
      return _showError('Enter valid finance inputs.');
    }
    await _runBusy(() async {
      _financeResult = switch (_financeOperation) {
        'loan' => _formatFinanceLoan(principal, rate, periods),
        'compound' =>
          'future value = ${DartComputation.compoundInterest(principal: principal, annualRate: rate, compoundsPerYear: compounds, years: years).toStringAsPrecision(12)}',
        'npv' =>
          'NPV = ${DartComputation.npv(rate, cashFlows.whereType<double>().toList()).toStringAsPrecision(12)}',
        'irr' =>
          'IRR = ${_formatNullable(DartComputation.irr(cashFlows.whereType<double>().toList()))}',
        'depreciation' =>
          'annual depreciation = ${DartComputation.straightLineDepreciation(principal, salvage, periods, year).toStringAsPrecision(12)}',
        'bond' =>
          'bond price = ${DartComputation.bondPrice(faceValue: principal, couponRate: coupon, marketRate: market, periods: periods).toStringAsPrecision(12)}',
        'retirement' =>
          'future value = ${DartComputation.retirementFutureValue(initialBalance: principal, monthlyContribution: contribution, annualRate: rate, years: years).toStringAsPrecision(12)}',
        _ => '',
      };
    },
      historyExpression: 'finance $_financeOperation',
      historyResult: () => _financeResult,
    );
  }

  String _formatFinanceLoan(double principal, double rate, int periods) {
    final payment = DartComputation.loanPayment(
      principal: principal,
      annualRate: rate,
      periods: periods,
    );
    final total = payment * periods;
    return 'payment / month = ${payment.toStringAsPrecision(12)}\ntotal paid = ${total.toStringAsPrecision(12)}';
  }

  String _formatNullable(double? value) =>
      value == null ? 'not found' : '${(value * 100).toStringAsPrecision(10)}%';

  Future<void> _evaluateCustom() async {
    final definitions = <String, String>{};
    for (final item in _customDefinitions.text.split(RegExp(r'[;\n]+'))) {
      final pair = item.split('=');
      if (pair.length == 2 && pair[0].trim().isNotEmpty) {
        definitions[pair[0].trim()] = pair[1].trim();
      }
    }
    if (definitions.isEmpty) {
      return _showError('Add at least one definition such as f=x^2+1.');
    }
    await _runBusy(() async {
      final value = DartComputation.evaluateCustom(
        _customExpression.text,
        definitions,
      );
      if (!value.isFinite) {
        throw const FormatException(
          'Custom function returned a non-finite value.',
        );
      }
      _customResult = value.toStringAsPrecision(12);
    },
      historyExpression: _customExpression.text,
      historyResult: () => _customResult,
    );
  }

  Future<void> _buildFunctionTable() async {
    final start = double.tryParse(_tableStart.text);
    final end = double.tryParse(_tableEnd.text);
    final rows = int.tryParse(_tableRows.text);
    if (start == null || end == null || rows == null || rows < 2) {
      return _showError('Enter a valid range and at least two rows.');
    }
    await _runBusy(() async {
      final csv = DartComputation.functionTableCsv(
        _tableExpression.text,
        start,
        end,
        rows,
      );
      if (csv.isEmpty) {
        throw const FormatException('The function table inputs are invalid.');
      }
      _tableResult = csv;
    },
      historyExpression: 'table ${_tableExpression.text}',
      historyResult: () => _tableResult,
    );
  }

  Future<void> _runBusy(
    Future<void> Function() action, {
    String? historyExpression,
    String? Function()? historyResult,
  }) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    var completed = false;
    try {
      await action();
      completed = true;
    } on FormatException catch (error) {
      _error = error.message;
    } catch (_) {
      _error = 'The operation could not be completed.';
    }
    if (mounted) {
      setState(() => _busy = false);
      if (completed && historyExpression != null && historyResult != null) {
        final result = historyResult();
        if (result != null && result.isNotEmpty) {
          recordCalculationHistory(
            ref,
            expression: historyExpression,
            result: result,
            backend: 'Dart computation',
          );
        }
      }
    }
  }

  Future<void> _showError(String message) async {
    if (mounted) setState(() => _error = message);
  }

  String _format(double? value) =>
      value == null ? '—' : value.toStringAsPrecision(12);
}
