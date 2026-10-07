import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/compute/calculation_models.dart';
import '../../core/compute/computation.dart';
import '../../core/ui/feature_widgets.dart';

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
  final _customDefinitions = TextEditingController(text: 'f=x^2+1');
  final _customExpression = TextEditingController(text: 'f(3)');
  String _complexOperation = 'add';
  String _integerOperation = 'factor';
  String _distribution = 'normal';
  String? _complexResult;
  String? _integerResult;
  CalcDistributionResult? _distributionResult;
  String? _financeResult;
  String? _customResult;
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
      _customDefinitions,
      _customExpression,
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
                          'bitwise xor',
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
          FormRow(
            children: <Widget>[
              _numberField(_financePrincipal, 'Principal', '本金'),
              _numberField(_financeRate, 'Annual rate', '年利率'),
              _numberField(_financePeriods, 'Periods', '期数'),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _busy ? null : _calculateFinance,
            icon: const Icon(Icons.payments_outlined),
            label: Text(
              nextEraText(context, 'Calculate loan payment', '计算贷款还款'),
            ),
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
    if (values.any((value) => value == null))
      return _showError('Enter four finite complex components.');
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
    });
  }

  Future<void> _calculateInteger() async {
    final n = BigInt.tryParse(_integer.text.trim());
    final m = BigInt.tryParse(_integer2.text.trim());
    final modulus = BigInt.tryParse(_modulus.text.trim());
    if (n == null || m == null || modulus == null)
      return _showError('Enter integer inputs.');
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
        _ => '${DartComputation.bitwise('xor', n.toInt(), m.toInt(), 32)}',
      };
    });
  }

  Future<void> _calculateDistribution() async {
    final x = double.tryParse(_distributionX.text.trim());
    if (x == null) return _showError('Enter x or a probability.');
    final values = _distributionParameter.text
        .split(RegExp(r'[,;\\s]+'))
        .where((value) => value.isNotEmpty)
        .map(double.tryParse)
        .toList();
    if (values.any((value) => value == null))
      return _showError('Parameters must be numeric.');
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
    });
  }

  Future<void> _calculateFinance() async {
    final principal = double.tryParse(_financePrincipal.text);
    final rate = double.tryParse(_financeRate.text);
    final periods = int.tryParse(_financePeriods.text);
    if (principal == null || rate == null || periods == null)
      return _showError('Enter valid finance inputs.');
    await _runBusy(() async {
      final payment = DartComputation.loanPayment(
        principal: principal,
        annualRate: rate,
        periods: periods,
      );
      final total = payment * periods;
      _financeResult =
          'payment / month = ${payment.toStringAsPrecision(12)}\ntotal paid = ${total.toStringAsPrecision(12)}';
    });
  }

  Future<void> _evaluateCustom() async {
    final definitions = <String, String>{};
    for (final item in _customDefinitions.text.split(RegExp(r'[;\\n]+'))) {
      final pair = item.split('=');
      if (pair.length == 2 && pair[0].trim().isNotEmpty)
        definitions[pair[0].trim()] = pair[1].trim();
    }
    if (definitions.isEmpty)
      return _showError('Add at least one definition such as f=x^2+1.');
    await _runBusy(() async {
      final value = DartComputation.evaluateCustom(
        _customExpression.text,
        definitions,
      );
      if (!value.isFinite)
        throw const FormatException(
          'Custom function returned a non-finite value.',
        );
      _customResult = value.toStringAsPrecision(12);
    });
  }

  Future<void> _runBusy(Future<void> Function() action) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await action();
    } on FormatException catch (error) {
      _error = error.message;
    } catch (_) {
      _error = 'The operation could not be completed.';
    }
    if (mounted) setState(() => _busy = false);
  }

  Future<void> _showError(String message) async {
    if (mounted) setState(() => _error = message);
  }

  String _format(double? value) =>
      value == null ? '—' : value.toStringAsPrecision(12);
}
