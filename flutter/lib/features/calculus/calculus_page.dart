import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/history/history_repository.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class CalculusPage extends ConsumerStatefulWidget {
  const CalculusPage({super.key});

  @override
  ConsumerState<CalculusPage> createState() => _CalculusPageState();
}

class _CalculusPageState extends ConsumerState<CalculusPage> {
  final _expression = TextEditingController(text: 'sin(x)');
  final _secondExpression = TextEditingController(text: '0');
  final _x = TextEditingController(text: '1');
  final _a = TextEditingController(text: '0');
  final _b = TextEditingController(text: 'pi');
  final _order = TextEditingController(text: '4');
  String? _result;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _expression.dispose();
    _secondExpression.dispose();
    _x.dispose();
    _a.dispose();
    _b.dispose();
    _order.dispose();
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
                TextField(
                  controller: _secondExpression,
                  decoration: InputDecoration(
                    labelText: nextEraText(
                      context,
                      'g(x) for area between curves',
                      '曲线面积的 g(x)',
                    ),
                    hintText: '0',
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
                    TextField(
                      controller: _order,
                      decoration: InputDecoration(
                        labelText: nextEraText(
                          context,
                          'Taylor order',
                          'Taylor 阶数',
                        ),
                      ),
                      keyboardType: TextInputType.number,
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
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('limit'),
                      icon: const Icon(Icons.call_missed_outlined),
                      label: Text(nextEraText(context, 'Limit', '极限')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('minimum'),
                      icon: const Icon(Icons.vertical_align_bottom),
                      label: Text(nextEraText(context, 'Minimum x', '最小值 x')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('maximum'),
                      icon: const Icon(Icons.vertical_align_top),
                      label: Text(nextEraText(context, 'Maximum x', '最大值 x')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('area'),
                      icon: const Icon(Icons.compare_arrows),
                      label: Text(
                        nextEraText(context, 'Area between', '曲线间面积'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('taylor'),
                      icon: const Icon(Icons.functions),
                      label: Text(
                        nextEraText(context, 'Taylor series', 'Taylor 展开'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('arc'),
                      icon: const Icon(Icons.timeline),
                      label: Text(nextEraText(context, 'Arc length', '弧长')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('disk'),
                      icon: const Icon(Icons.circle_outlined),
                      label: Text(nextEraText(context, 'Disk volume', '圆盘体积')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('washer'),
                      icon: const Icon(Icons.donut_large),
                      label: Text(
                        nextEraText(context, 'Washer volume', '垫圈体积'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => _run('shell'),
                      icon: const Icon(Icons.rotate_90_degrees_ccw),
                      label: Text(nextEraText(context, 'Shell volume', '壳体积')),
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
    try {
      if (operation == 'taylor') {
        final order = int.tryParse(_order.text.trim());
        if (order == null || order < 0 || order > 12) {
          if (mounted) {
            setState(() {
              _busy = false;
              _error = nextEraText(
                context,
                'Taylor order must be between 0 and 12.',
                'Taylor 阶数必须在 0 到 12 之间。',
              );
            });
          }
          return;
        }
        final coefficients = await backend.taylorCoefficients(
          _expression.text,
          x,
          order,
        );
        if (!mounted) return;
        final formatted = coefficients
            ?.asMap()
            .entries
            .map(
              (entry) =>
                  'c${entry.key} = ${entry.value?.toStringAsPrecision(12) ?? 'undefined'}',
            )
            .join('\n');
        setState(() {
          _busy = false;
          _result = formatted;
          _error = coefficients == null
              ? nextEraText(context, 'Taylor series failed.', 'Taylor 展开失败。')
              : null;
        });
        if (formatted != null) {
          recordCalculationHistory(
            ref,
            expression: 'Taylor(${_expression.text}, x=$x, order=$order)',
            result: formatted,
            backend: backend.name,
          );
        }
        return;
      }
      final result = switch (operation) {
        'integral' => await backend.integrate(_expression.text, a, b),
        'limit' => await backend.limit(_expression.text, x),
        'minimum' => await backend.extremum(_expression.text, a, b),
        'maximum' => await backend.extremum(
          _expression.text,
          a,
          b,
          minimum: false,
        ),
        'area' => await backend.areaBetweenCurves(
          _expression.text,
          _secondExpression.text,
          a,
          b,
        ),
        'arc' => await backend.arcLength(_expression.text, a, b),
        'disk' => await backend.volumeDisk(_expression.text, a, b),
        'washer' => await backend.volumeWasher(
          _expression.text,
          _secondExpression.text,
          a,
          b,
        ),
        'shell' => await backend.volumeShell(_expression.text, a, b),
        _ => await backend.derivative(
          _expression.text,
          x,
          second: operation == 'second',
        ),
      };
      if (!mounted) {
        return;
      }
      setState(() {
        _busy = false;
        _result = result.value?.toStringAsPrecision(12);
        _error = result.error;
      });
      if (result.value != null) {
        recordCalculationHistory(
          ref,
          expression: '${operation.toUpperCase()}: ${_expression.text}',
          result: result.value!.toStringAsPrecision(12),
          backend: result.backend,
        );
      }
    } on FormatException catch (error) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = error.message;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = nextEraText(
            context,
            'The calculus operation failed.',
            '微积分运算失败。',
          );
        });
      }
    }
  }
}
