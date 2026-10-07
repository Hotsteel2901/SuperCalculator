import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class CalculusPage extends ConsumerStatefulWidget {
  const CalculusPage({super.key});

  @override
  ConsumerState<CalculusPage> createState() => _CalculusPageState();
}

class _CalculusPageState extends ConsumerState<CalculusPage> {
  final _expression = TextEditingController(text: 'sin(x)');
  final _x = TextEditingController(text: '1');
  final _a = TextEditingController(text: '0');
  final _b = TextEditingController(text: 'pi');
  String? _result;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _expression.dispose();
    _x.dispose();
    _a.dispose();
    _b.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final title = l10n.calculus;
    return FeaturePageFrame(
      title: title,
      icon: Icons.functions,
      subtitle: nextEraText(
        context,
        'Derivatives, integrals and numerical limits use the shared computation port.',
        '导数、积分和数值极限统一通过共享计算端口执行。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Calculus workspace', '微积分工作区'),
            icon: Icons.tune,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _expression,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'f(x)', 'f(x)'),
                    hintText: 'sin(x)',
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    TextField(
                      controller: _x,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Point x', '点 x'),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                    ),
                    TextField(
                      controller: _a,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Interval a', '区间 a'),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                    ),
                    TextField(
                      controller: _b,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Interval b', '区间 b'),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                    ),
                  ],
                ),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: <Widget>[
                    FilledButton.icon(
                      onPressed: _busy ? null : () => _run('derivative'),
                      icon: const Icon(Icons.trending_up),
                      label: Text(nextEraText(context, 'Derivative', '一阶导数')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('second'),
                      icon: const Icon(Icons.show_chart),
                      label: Text(
                        nextEraText(context, 'Second derivative', '二阶导数'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('integral'),
                      icon: const Icon(Icons.area_chart),
                      label: Text(
                        nextEraText(context, 'Adaptive integral', '自适应积分'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          ResultCard(
            value:
                _result ??
                nextEraText(context, 'Choose an operation.', '请选择一个运算。'),
            error: _error,
          ),
          if (_busy) ...<Widget>[
            const SizedBox(height: 12),
            const LinearProgressIndicator(),
          ],
        ],
      ),
    );
  }

  Future<void> _run(String operation) async {
    final x = parseMathNumber(_x.text);
    final a = parseMathNumber(_a.text);
    final b = parseMathNumber(_b.text);
    if (x == null || a == null || b == null) {
      setState(() {
        _error = nextEraText(
          context,
          'Enter valid numeric values. Use pi when needed.',
          '请输入有效数字，需要时可使用 pi。',
        );
        _result = null;
      });
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    final backend = ref.read(calcBackendProvider);
    final result = operation == 'integral'
        ? await backend.integrate(_expression.text, a, b)
        : await backend.derivative(
            _expression.text,
            x,
            second: operation == 'second',
          );
    if (!mounted) {
      return;
    }
    setState(() {
      _busy = false;
      _result = result.value?.toStringAsPrecision(12);
      _error = result.error;
    });
  }
}
