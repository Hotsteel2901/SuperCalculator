import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
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
  final _sparseRows = TextEditingController(text: '3');
  final _sparseColumns = TextEditingController(text: '3');
  final _sparseEntries = TextEditingController(text: '0,0,4;1,1,5;2,2,6');
  final _sparseVector = TextEditingController(text: '4,10,18');
  final _sparseInitial = TextEditingController(text: '0,0,0');
  String _operation = 'determinant';
  String _sparseOperation = 'spmv';
  String? _result;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _left.dispose();
    _right.dispose();
    _sparseRows.dispose();
    _sparseColumns.dispose();
    _sparseEntries.dispose();
    _sparseVector.dispose();
    _sparseInitial.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final operations = <String, String>{
      'determinant': nextEraText(context, 'Determinant A', 'det(A)'),
      'inverse': nextEraText(context, 'Inverse A', 'A 的逆矩阵'),
      'transpose': nextEraText(context, 'Transpose A', 'A 的转置'),
      'add': nextEraText(context, 'A + B', 'A + B'),
      'subtract': nextEraText(context, 'A − B', 'A − B'),
      'multiply': nextEraText(context, 'A × B', 'A × B'),
      'rref': nextEraText(context, 'RREF A', 'A 的最简阶梯形'),
      'rank': nextEraText(context, 'Rank A', 'A 的秩'),
      'eigenvalues': nextEraText(context, 'Eigenvalues A (2×2)', 'A 的特征值（2×2）'),
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
          const SizedBox(height: 16),
          FeatureCard(
            title: nextEraText(context, 'Sparse matrix tools', '稀疏矩阵工具'),
            icon: Icons.grain,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                Text(
                  nextEraText(
                    context,
                    'COO entries use row,column,value; separate entries with semicolons.',
                    'COO 格式为 行,列,值；使用分号分隔条目。',
                  ),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    _field(_sparseRows, 'Rows', '行数'),
                    _field(_sparseColumns, 'Columns', '列数'),
                    DropdownButtonFormField<String>(
                      initialValue: _sparseOperation,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Operation', '运算'),
                      ),
                      items: <String>['spmv', 'conjugate-gradient']
                          .map(
                            (value) => DropdownMenuItem<String>(
                              value: value,
                              child: Text(value),
                            ),
                          )
                          .toList(growable: false),
                      onChanged: (value) =>
                          setState(() => _sparseOperation = value ?? 'spmv'),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _sparseEntries,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'COO entries', 'COO 条目'),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    _field(_sparseVector, 'Vector b', '向量 b'),
                    _field(_sparseInitial, 'Initial x', '初始 x'),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : _calculateSparse,
                      icon: const Icon(Icons.functions),
                      label: Text(nextEraText(context, 'Run sparse', '执行稀疏运算')),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _field(TextEditingController controller, String en, String zh) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: nextEraText(context, en, zh)),
      keyboardType: const TextInputType.numberWithOptions(signed: true),
    );
  }

  Future<void> _calculateSparse() async {
    final rows = int.tryParse(_sparseRows.text.trim());
    final columns = int.tryParse(_sparseColumns.text.trim());
    final vector = _parseVector(_sparseVector.text);
    final initial = _parseVector(_sparseInitial.text);
    if (rows == null || columns == null || vector == null || initial == null) {
      return _showSparseError('Enter valid sparse dimensions and vectors.');
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final backend = ref.read(calcBackendProvider);
      final matrix = await backend.parseSparseMatrix(
        rows,
        columns,
        _sparseEntries.text,
      );
      final values = _sparseOperation == 'spmv'
          ? await backend.sparseMatVec(matrix, vector)
          : await backend.conjugateGradient(matrix, vector, initial);
      if (!mounted) return;
      setState(() {
        _busy = false;
        _result = values
            ?.map((value) => value.toStringAsPrecision(12))
            .join(', ');
        _error = values == null
            ? nextEraText(
                context,
                'Conjugate gradient did not converge.',
                '共轭梯度未收敛。',
              )
            : null;
      });
    } on FormatException catch (error) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = error.message;
      });
    } catch (_) {
      if (!mounted) return;
      _showSparseError(
        nextEraText(context, 'Sparse operation failed.', '稀疏运算失败。'),
      );
    }
  }

  List<double>? _parseVector(String input) {
    final values = input
        .split(RegExp(r'[,;\s]+'))
        .where((value) => value.trim().isNotEmpty)
        .map(double.tryParse)
        .toList(growable: false);
    return values.any((value) => value == null) ? null : values.cast<double>();
  }

  void _showSparseError(String message) {
    if (mounted) {
      setState(() {
        _busy = false;
        _error = message;
      });
    }
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
      } else if (_operation == 'add' || _operation == 'subtract') {
        final matrix = await backend.addMatrices(
          _left.text,
          _right.text,
          subtract: _operation == 'subtract',
        );
        _setResult(matrix.format());
      } else if (_operation == 'rref') {
        final matrix = await backend.rrefMatrix(_left.text);
        _setResult(matrix.format());
      } else if (_operation == 'rank') {
        _setResult('${await backend.matrixRank(_left.text)}');
      } else if (_operation == 'eigenvalues') {
        final values = await backend.eigenvalues2x2(_left.text);
        _setResult(
          values.map((value) => value.toStringAsPrecision(12)).join(', '),
        );
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
        _error = nextEraText(
          context,
          'The matrix operation failed.',
          '矩阵运算失败。',
        );
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
