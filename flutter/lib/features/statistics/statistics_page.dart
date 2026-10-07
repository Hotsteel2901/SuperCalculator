import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/compute/calculation_models.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class StatisticsPage extends ConsumerStatefulWidget {
  const StatisticsPage({super.key});

  @override
  ConsumerState<StatisticsPage> createState() => _StatisticsPageState();
}

class _StatisticsPageState extends ConsumerState<StatisticsPage> {
  final _data = TextEditingController(text: '1, 2, 2, 3, 4, 5, 8, 13');
  CalcStatistics? _statistics;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _data.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final statistics = _statistics;
    return FeaturePageFrame(
      title: AppLocalizations.of(context).statistics,
      icon: Icons.bar_chart,
      subtitle: nextEraText(
        context,
        'Descriptive statistics, quartiles and sample variance are computed without a UI-blocking dependency.',
        '描述统计、四分位数和样本方差无需额外 UI 依赖即可计算。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Data set', '数据集'),
            icon: Icons.data_array,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _data,
                  minLines: 3,
                  maxLines: 8,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'Numbers', '数字'),
                    helperText: nextEraText(
                      context,
                      'Separate values with commas, spaces or new lines.',
                      '使用逗号、空格或换行分隔数值。',
                    ),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: _busy ? null : _calculate,
                  icon: const Icon(Icons.calculate_outlined),
                  label: Text(nextEraText(context, 'Calculate statistics', '计算统计量')),
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
          if (statistics != null) FeatureCard(child: _table(context, statistics)),
        ],
      ),
    );
  }

  Widget _table(BuildContext context, CalcStatistics statistics) {
    final values = <List<String>>[
      <String>[
        nextEraText(context, 'Count', '数量'),
        '${statistics.count}',
      ],
      <String>[
        nextEraText(context, 'Sum', '总和'),
        _format(statistics.sum),
      ],
      <String>[
        nextEraText(context, 'Mean', '平均值'),
        _format(statistics.mean),
      ],
      <String>[
        nextEraText(context, 'Median', '中位数'),
        _format(statistics.median),
      ],
      <String>[
        nextEraText(context, 'Minimum / maximum', '最小值 / 最大值'),
        '${_format(statistics.minimum)} / ${_format(statistics.maximum)}',
      ],
      <String>[
        nextEraText(context, 'Range', '极差'),
        _format(statistics.range),
      ],
      <String>[
        nextEraText(context, 'Variance', '方差'),
        _format(statistics.variance),
      ],
      <String>[
        nextEraText(context, 'Std. deviation', '标准差'),
        _format(statistics.standardDeviation),
      ],
      <String>[
        nextEraText(context, 'Q1 / Q3 / IQR', 'Q1 / Q3 / IQR'),
        '${_format(statistics.q1)} / ${_format(statistics.q3)} / ${_format(statistics.iqr)}',
      ],
      <String>[
        nextEraText(context, 'Mode', '众数'),
        statistics.mode == null ? '—' : _format(statistics.mode!),
      ],
    ];
    return DataTable(
      columns: <DataColumn>[
        DataColumn(label: Text(nextEraText(context, 'Metric', '指标'))),
        DataColumn(label: Text(nextEraText(context, 'Value', '数值'))),
      ],
      rows: values
          .map(
            (row) => DataRow(
              cells: <DataCell>[DataCell(Text(row[0])), DataCell(Text(row[1]))],
            ),
          )
          .toList(growable: false),
    );
  }

  String _format(double value) => value.toStringAsPrecision(10);

  Future<void> _calculate() async {
    final values = _data.text
        .split(RegExp(r'[,;\s]+'))
        .where((item) => item.trim().isNotEmpty)
        .map(double.tryParse)
        .whereType<double>()
        .toList(growable: false);
    if (values.isEmpty) {
      setState(() {
        _error = nextEraText(context, 'No valid numbers were found.', '没有找到有效数字。');
        _statistics = null;
      });
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final result = await ref.read(calcBackendProvider).statistics(values);
    if (!mounted) {
      return;
    }
    setState(() {
      _busy = false;
      _statistics = result;
    });
  }
}
