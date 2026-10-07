import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/plot/plot_point.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class DataAnalysisPage extends ConsumerStatefulWidget {
  const DataAnalysisPage({super.key});

  @override
  ConsumerState<DataAnalysisPage> createState() => _DataAnalysisPageState();
}

class _DataAnalysisPageState extends ConsumerState<DataAnalysisPage> {
  final _data = TextEditingController(text: '0,1\n1,2.1\n2,3.9\n3,6.2\n4,8.1');
  List<PlotPoint> _points = const <PlotPoint>[];
  List<PlotPoint> _fit = const <PlotPoint>[];
  String? _result;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _data.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FeaturePageFrame(
      title: AppLocalizations.of(context).dataAnalysis,
      icon: Icons.insights,
      subtitle: nextEraText(
        context,
        'Paste CSV or TSV points to fit a line and inspect residual quality.',
        '粘贴 CSV 或 TSV 数据点，拟合直线并查看拟合质量。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Data and regression', '数据与回归'),
            icon: Icons.table_chart,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _data,
                  minLines: 5,
                  maxLines: 12,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'x,y data', 'x,y 数据'),
                    helperText: nextEraText(
                      context,
                      'One pair per line; comma, tab or semicolon is accepted.',
                      '每行一个点，支持逗号、制表符或分号。',
                    ),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: _busy ? null : _fitLine,
                  icon: const Icon(Icons.auto_graph),
                  label: Text(
                    nextEraText(context, 'Fit linear model', '拟合线性模型'),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          ResultCard(
            value:
                _result ??
                nextEraText(
                  context,
                  'Enter data to fit a model.',
                  '输入数据后进行拟合。',
                ),
            error: _error,
          ),
          if (_busy) ...<Widget>[
            const SizedBox(height: 12),
            const LinearProgressIndicator(),
          ],
          if (_points.isNotEmpty) ...<Widget>[
            const SizedBox(height: 16),
            FeatureCard(
              title: nextEraText(
                context,
                'Observed and fitted data',
                '观测值与拟合值',
              ),
              icon: Icons.scatter_plot,
              child: SizedBox(
                height: 360,
                child: CustomPaint(
                  painter: LineSeriesPainter(
                    series: <List<PlotPoint>>[_points, _fit],
                    scheme: Theme.of(context).colorScheme,
                  ),
                  child: const SizedBox.expand(),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Future<void> _fitLine() async {
    final xs = <double>[];
    final ys = <double>[];
    for (final line in _data.text.split(RegExp(r'[\r\n]+'))) {
      final cells = line.trim().split(RegExp(r'[,;\t ]+'));
      if (cells.length < 2) {
        continue;
      }
      final x = double.tryParse(cells[0]);
      final y = double.tryParse(cells[1]);
      if (x != null && y != null) {
        xs.add(x);
        ys.add(y);
      }
    }
    if (xs.length < 2) {
      setState(() {
        _error = nextEraText(
          context,
          'At least two valid points are required.',
          '至少需要两个有效数据点。',
        );
      });
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
      _points = const <PlotPoint>[];
      _fit = const <PlotPoint>[];
    });
    final regression = await ref
        .read(calcBackendProvider)
        .linearRegression(xs, ys);
    if (!mounted) {
      return;
    }
    final points = <PlotPoint>[];
    for (var i = 0; i < xs.length; i++) {
      points.add(PlotPoint(xs[i], ys[i]));
    }
    final fit = <PlotPoint>[];
    for (var i = 0; i < regression.xs.length; i++) {
      fit.add(PlotPoint(regression.xs[i], regression.ys[i]));
    }
    setState(() {
      _busy = false;
      _points = points;
      _fit = fit;
      _result = regression.rSquared.isFinite
          ? '${regression.equation}    R² = ${regression.rSquared.toStringAsPrecision(8)}'
          : null;
      _error = regression.rSquared.isFinite
          ? null
          : nextEraText(
              context,
              'The x values must not all be equal.',
              'x 值不能全部相同。',
            );
    });
  }
}
