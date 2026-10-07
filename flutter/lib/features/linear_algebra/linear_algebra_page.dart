import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/compute/calculation_models.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class LinearAlgebraPage extends ConsumerStatefulWidget {
  const LinearAlgebraPage({super.key});

  @override
  ConsumerState<LinearAlgebraPage> createState() => _LinearAlgebraPageState();
}

class _LinearAlgebraPageState extends ConsumerState<LinearAlgebraPage> {
  final _left = TextEditingController(text: '1,2;3,4');
  final _right = TextEditingController(text: '5,6;7,8');
  String _operation = 'determinant';
  String? _result;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _left.dispose();
    _right.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final operations = <String, String>{
      'determinant': nextEraText(context, 'Determinant A', 'det(A)'),
      'inverse': nextEraText(context, 'Inverse A', 'A 的逆矩阵'),
      'transpose': nextEraText(context, 'Transpose A', 'A 的转置'),
      'multiply': nextEraText(context, 'A × B', 'A × B'),
    };
    return FeaturePageFrame(
      title: AppLocalizations.of(context).linearAlgebra,
      icon: Icons.grid_4x4,
      subtitle: nextEraText(
        context,
        'Dense matrix operations with pivoting and dimension checks.',
        '支持主元选取和维度检查的稠密矩阵运算。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Matrix workspace', '矩阵工作区'),
            icon: Icons.table_view,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _left,
                  minLines: 2,
                  maxLines: 5,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'Matrix A', '矩阵 A'),
                    helperText: nextEraText(
                      context,
                      'Rows use ; and cells use commas: 1,2;3,4',
                      '使用 ; 分隔行、逗号分隔元素：1,2;3,4',
                    ),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _right,
                  minLines: 2,
                  maxLines: 5,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'Matrix B', '矩阵 B'),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    DropdownButtonFormField<String>(
                      initialValue: _operation,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Operation', '运算'),
                      ),
                      items: operations.entries
                          .map(
                            (entry) => DropdownMenuItem<String>(
                              value: entry.key,
                              child: Text(entry.value),
                            ),
                          )
                          .toList(growable: false),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() => _operation = value);
                        }
                      },
                    ),
                    FilledButton.icon(
                      onPressed: _busy ? null : _calculate,
                      icon: const Icon(Icons.play_arrow),
                      label: Text(nextEraText(context, 'Run', '执行')),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (_busy) const LinearProgressIndicator(),
          if (_error != null) ...<Widget>[
            ResultCard(value: '', error: _error),
            const SizedBox(height: 16),
          ],
          if (_result != null)
            FeatureCard(
              title: nextEraText(context, 'Result', '结果'),
              icon: Icons.functions,
              child: SelectableText(
                _result!,
                style: const TextStyle(fontFamily: 'monospace'),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _calculate() async {
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final backend = ref.read(calcBackendProvider);
      if (_operation == 'determinant') {
        final value = await backend.determinant(_left.text);
        _setResult(value.toStringAsPrecision(12));
      } else if (_operation == 'inverse') {
        final matrix = await backend.inverseMatrix(_left.text);
        _setResult(matrix.format());
      } else if (_operation == 'transpose') {
        final matrix = await backend.parseMatrix(_left.text);
        _setResult(matrix.transpose.format());
      } else {
        final matrix = await backend.multiplyMatrices(_left.text, _right.text);
        _setResult(matrix.format());
      }
    } on FormatException catch (error) {
      if (!mounted) {
      return;
    }
      setState(() {
        _busy = false;
        _error = error.message;
      });
    } catch (_) {
      if (!mounted) {
      return;
    }
      setState(() {
        _busy = false;
        _error = nextEraText(context, 'The matrix operation failed.', '矩阵运算失败。');
      });
    }
  }

  void _setResult(String value) {
    if (!mounted) {
      return;
    }
    setState(() {
      _busy = false;
      _result = value;
    });
  }
}
