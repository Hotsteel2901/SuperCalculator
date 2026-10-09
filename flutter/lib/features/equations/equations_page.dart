import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/history/history_repository.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class EquationsPage extends ConsumerStatefulWidget {
  const EquationsPage({super.key});

  @override
  ConsumerState<EquationsPage> createState() => _EquationsPageState();
}

class _EquationsPageState extends ConsumerState<EquationsPage> {
  final _expression = TextEditingController(text: 'x^2 - 2');
  final _secondExpression = TextEditingController(text: 'x');
  final _guess = TextEditingController(text: '1');
  final _systemY = TextEditingController(text: '1');
  final _minimum = TextEditingController(text: '-10');
  final _maximum = TextEditingController(text: '10');
  String? _result;
  String? _error;
  bool _busy = false;
  bool _extremumMinimum = true;

  @override
  void dispose() {
    _expression.dispose();
    _secondExpression.dispose();
    _guess.dispose();
    _systemY.dispose();
    _minimum.dispose();
    _maximum.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FeaturePageFrame(
      title: AppLocalizations.of(context).equations,
      icon: Icons.account_tree,
      subtitle: nextEraText(
        context,
        'Use bounded Newton iterations and scan an interval for every sign-changing root.',
        '使用有界牛顿迭代，并扫描区间寻找所有变号根。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Root finder', '求根器'),
            icon: Icons.radar,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _expression,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'f(x) = 0', 'f(x) = 0'),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _secondExpression,
                  decoration: InputDecoration(
                    labelText: nextEraText(
                      context,
                      'g(x) or g(x,y)',
                      'g(x) 或 g(x,y)',
                    ),
                    helperText: nextEraText(
                      context,
                      'Used for intersections and 2D systems.',
                      '用于曲线交点和二维方程组。',
                    ),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    TextField(
                      controller: _guess,
                      decoration: InputDecoration(
                        labelText: nextEraText(
                          context,
                          'Initial guess',
                          '初始猜测',
                        ),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                    ),
                    TextField(
                      controller: _minimum,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Minimum', '最小值'),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                    ),
                    TextField(
                      controller: _maximum,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Maximum', '最大值'),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                    ),
                    TextField(
                      controller: _systemY,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'System y₀', '方程组 y₀'),
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
                      onPressed: _busy ? null : _solve,
                      icon: const Icon(Icons.bolt),
                      label: Text(nextEraText(context, 'Solve', '求解')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : _scanRoots,
                      icon: const Icon(Icons.search),
                      label: Text(nextEraText(context, 'Scan roots', '扫描全部根')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : _findIntersections,
                      icon: const Icon(Icons.merge_type),
                      label: Text(
                        nextEraText(context, 'Intersections', '曲线交点'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : _solveSystem,
                      icon: const Icon(Icons.grid_3x3),
                      label: Text(
                        nextEraText(context, 'Solve 2D system', '求解二维方程组'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : _tangent,
                      icon: const Icon(Icons.show_chart),
                      label: Text(
                        nextEraText(context, 'Tangent / normal', '切线 / 法线'),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy
                          ? null
                          : () {
                              setState(() => _extremumMinimum = true);
                              _findExtremum();
                            },
                      icon: const Icon(Icons.arrow_downward),
                      label: Text(nextEraText(context, 'Minimum', '最小值')),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy
                          ? null
                          : () {
                              setState(() => _extremumMinimum = false);
                              _findExtremum();
                            },
                      icon: const Icon(Icons.arrow_upward),
                      label: Text(nextEraText(context, 'Maximum', '最大值')),
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
                nextEraText(context, 'No root computed yet.', '尚未计算根。'),
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

  Future<void> _solve() async {
    final guess = parseMathNumber(_guess.text);
    final minimum = parseMathNumber(_minimum.text);
    final maximum = parseMathNumber(_maximum.text);
    if (guess == null || minimum == null || maximum == null) {
      _invalidInput();
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    final result = await ref
        .read(calcBackendProvider)
        .solve(
          _expression.text,
          guess: guess,
          minimum: minimum,
          maximum: maximum,
        );
    if (!mounted) {
      return;
    }
    setState(() {
      _busy = false;
      _result = result.value == null
          ? null
          : 'x = ${result.value!.toStringAsPrecision(12)}';
      _error = result.error;
    });
    if (result.value != null) {
      recordCalculationHistory(
        ref,
        expression: '${_expression.text} = 0',
        result: 'x = ${result.value!.toStringAsPrecision(12)}',
        backend: result.backend,
      );
    }
  }

  Future<void> _scanRoots() async {
    final minimum = parseMathNumber(_minimum.text);
    final maximum = parseMathNumber(_maximum.text);
    if (minimum == null || maximum == null || minimum >= maximum) {
      _invalidInput();
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    final backend = ref.read(calcBackendProvider);
    try {
      final roots = await backend.scanRoots(
        _expression.text,
        minimum,
        maximum,
        samples: 1024,
      );
      if (!mounted) return;
      final rootsText = roots.isEmpty
          ? null
          : roots.map((root) => root.toStringAsPrecision(10)).join(', ');
      setState(() {
        _busy = false;
        _result =
            rootsText ??
            nextEraText(context, 'No roots found in the interval.', '区间内未找到根。');
      });
      if (rootsText != null) {
        recordCalculationHistory(
          ref,
          expression: 'scan roots: ${_expression.text}',
          result: rootsText,
          backend: backend.name,
        );
      }
    } on FormatException catch (error) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = error.message;
        });
      }
    }
    return;
  }

  Future<void> _findIntersections() async {
    final minimum = parseMathNumber(_minimum.text);
    final maximum = parseMathNumber(_maximum.text);
    if (minimum == null || maximum == null || minimum >= maximum) {
      _invalidInput();
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final backend = ref.read(calcBackendProvider);
      final roots = await backend.intersections(
        _expression.text,
        _secondExpression.text,
        minimum,
        maximum,
      );
      if (!mounted) {
        return;
      }
      final intersectionsText = roots.isEmpty
          ? null
          : roots
                .map((root) => 'x = ${root.toStringAsPrecision(10)}')
                .join(', ');
      setState(() {
        _busy = false;
        _result =
            intersectionsText ??
            nextEraText(context, 'No intersections found.', '未找到交点。');
      });
      if (intersectionsText != null) {
        recordCalculationHistory(
          ref,
          expression: '${_expression.text} = ${_secondExpression.text}',
          result: intersectionsText,
          backend: backend.name,
        );
      }
    } on FormatException catch (error) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = error.message;
        });
      }
    }
  }

  Future<void> _solveSystem() async {
    final x = parseMathNumber(_guess.text);
    final y = parseMathNumber(_systemY.text);
    if (x == null || y == null) {
      _invalidInput();
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final solution = await ref
          .read(calcBackendProvider)
          .solveSystem2d(_expression.text, _secondExpression.text, x: x, y: y);
      if (!mounted) {
        return;
      }
      final solutionText = solution == null
          ? null
          : 'x = ${solution['x']!.toStringAsPrecision(12)}, y = ${solution['y']!.toStringAsPrecision(12)}';
      setState(() {
        _busy = false;
        _result = solutionText;
        _error = solution == null
            ? nextEraText(
                context,
                'The 2D system did not converge.',
                '二维方程组未收敛。',
              )
            : null;
      });
      if (solutionText != null) {
        recordCalculationHistory(
          ref,
          expression: '${_expression.text} = 0; ${_secondExpression.text} = 0',
          result: solutionText,
          backend: ref.read(calcBackendProvider).name,
        );
      }
    } on FormatException catch (error) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = error.message;
        });
      }
    }
  }

  Future<void> _findExtremum() async {
    final minimum = parseMathNumber(_minimum.text);
    final maximum = parseMathNumber(_maximum.text);
    if (minimum == null || maximum == null || minimum >= maximum) {
      _invalidInput();
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final backend = ref.read(calcBackendProvider);
      final point = await backend.extremum(
        _expression.text,
        minimum,
        maximum,
        minimum: _extremumMinimum,
      );
      if (!mounted) return;
      final result = point.value == null
          ? null
          : '${_extremumMinimum ? 'minimum' : 'maximum'} at x = '
                '${point.value!.toStringAsPrecision(12)}';
      setState(() {
        _busy = false;
        _result = result;
        _error = point.error;
      });
      if (result != null) {
        recordCalculationHistory(
          ref,
          expression:
              '${_extremumMinimum ? 'min' : 'max'} ${_expression.text} '
              'on [$minimum, $maximum]',
          result: result,
          backend: point.backend,
        );
      }
    } on FormatException catch (error) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = error.message;
      });
    }
  }

  Future<void> _tangent() async {
    final x = parseMathNumber(_guess.text);
    if (x == null) {
      _invalidInput();
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final backend = ref.read(calcBackendProvider);
      final value = await backend.tangentAndNormal(_expression.text, x);
      if (!mounted) {
        return;
      }
      final normal = value?['normalSlope'];
      final tangentText = value == null
          ? null
          : 'point = (${x.toStringAsPrecision(10)}, ${value['y']!.toStringAsPrecision(10)})\n'
                'tangent slope = ${value['slope']!.toStringAsPrecision(10)}\n'
                'normal slope = ${normal!.isFinite ? normal.toStringAsPrecision(10) : "vertical"}';
      setState(() {
        _busy = false;
        _result = tangentText;
        _error = value == null
            ? nextEraText(
                context,
                'The tangent could not be evaluated.',
                '无法计算切线。',
              )
            : null;
      });
      if (tangentText != null) {
        recordCalculationHistory(
          ref,
          expression: 'tangent/normal: ${_expression.text} at x=$x',
          result: tangentText,
          backend: backend.name,
        );
      }
    } on FormatException catch (error) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = error.message;
        });
      }
    }
  }

  void _invalidInput() {
    setState(() {
      _error = nextEraText(
        context,
        'Enter a valid interval and numeric guess.',
        '请输入有效区间和数字猜测。',
      );
      _result = null;
    });
  }
}
