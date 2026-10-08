import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/history/history_repository.dart';
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
  final _degree = TextEditingController(text: '2');
  final _interpolationX = TextEditingController(text: '2.5');
  String _model = 'linear';
  String _interpolationMethod = 'linear';
  List<PlotPoint> _points = const <PlotPoint>[];
  List<PlotPoint> _fit = const <PlotPoint>[];
  String? _result;
  String? _csvExport;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _data.dispose();
    _degree.dispose();
    _interpolationX.dispose();
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
                FormRow(
                  children: <Widget>[
                    DropdownButtonFormField<String>(
                      initialValue: _model,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Fit model', '拟合模型'),
                      ),
                      items:
                          <String>[
                                'linear',
                                'polynomial',
                                'exponential',
                                'power',
                                'logarithmic',
                              ]
                              .map(
                                (value) => DropdownMenuItem(
                                  value: value,
                                  child: Text(value),
                                ),
                              )
                              .toList(growable: false),
                      onChanged: (value) =>
                          setState(() => _model = value ?? 'linear'),
                    ),
                    TextField(
                      controller: _degree,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Degree', '次数'),
                      ),
                      keyboardType: TextInputType.number,
                    ),
                    FilledButton.icon(
                      onPressed: _busy ? null : _fitLine,
                      icon: const Icon(Icons.auto_graph),
                      label: Text(nextEraText(context, 'Fit', '拟合')),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    DropdownButtonFormField<String>(
                      initialValue: _interpolationMethod,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Interpolation', '插值'),
                      ),
                      items:
                          <String>[
                                'nearest',
                                'linear',
                                'lagrange',
                                'newton',
                                'cubic-spline',
                                'hermite',
                              ]
                              .map(
                                (value) => DropdownMenuItem(
                                  value: value,
                                  child: Text(value),
                                ),
                              )
                              .toList(growable: false),
                      onChanged: (value) => setState(
                        () => _interpolationMethod = value ?? 'linear',
                      ),
                    ),
                    TextField(
                      controller: _interpolationX,
                      decoration: InputDecoration(
                        labelText: nextEraText(
                          context,
                          'x to interpolate',
                          '插值 x',
                        ),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: _busy ? null : _interpolate,
                      icon: const Icon(Icons.linear_scale),
                      label: Text(nextEraText(context, 'Interpolate', '插值计算')),
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
                nextEraText(
                  context,
                  'Enter data to fit a model.',
                  '输入数据后进行拟合。',
                ),
            error: _error,
          ),
          if (_csvExport != null) ...<Widget>[
            const SizedBox(height: 12),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: OutlinedButton.icon(
                onPressed: () async {
                  await Clipboard.setData(ClipboardData(text: _csvExport!));
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
                label: Text(
                  nextEraText(context, 'Copy fitted CSV', '复制拟合 CSV'),
                ),
              ),
            ),
          ],
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
      if (x != null && y != null && x.isFinite && y.isFinite) {
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
      _csvExport = null;
      _points = const <PlotPoint>[];
      _fit = const <PlotPoint>[];
    });
    try {
      final backend = ref.read(calcBackendProvider);
      final points = xs
          .asMap()
          .entries
          .map((entry) => PlotPoint(entry.value, ys[entry.key]))
          .toList(growable: false);
      List<double> fitXs;
      List<double> fitYs;
      double rSquared;
      String equation;
      if (_model == 'linear') {
        final regression = await backend.linearRegression(xs, ys);
        fitXs = regression.xs;
        fitYs = regression.ys;
        rSquared = regression.rSquared;
        equation = regression.equation;
      } else if (_model == 'polynomial') {
        final regression = await backend.polynomialRegression(
          xs,
          ys,
          degree: (int.tryParse(_degree.text) ?? 2).clamp(1, 12).toInt(),
        );
        fitXs = regression.xs;
        fitYs = regression.ys;
        rSquared = regression.rSquared;
        equation = regression.equation;
      } else {
        final regression = await backend.nonlinearRegression(_model, xs, ys);
        fitXs = regression.xs;
        fitYs = regression.ys;
        rSquared = regression.rSquared;
        equation = regression.equation;
      }
      final fittedCsv = StringBuffer('x,observed,fitted\n');
      for (var index = 0; index < xs.length; index++) {
        final fitted = _interpolateFitted(xs[index], fitXs, fitYs);
        fittedCsv
          ..write(xs[index].toStringAsPrecision(12))
          ..write(',')
          ..write(ys[index].toStringAsPrecision(12))
          ..write(',')
          ..writeln(fitted?.toStringAsPrecision(12) ?? '');
      }
      if (!mounted) {
        return;
      }
      final fittedText = rSquared.isFinite
          ? '$equation    R² = ${rSquared.toStringAsPrecision(8)}'
          : null;
      setState(() {
        _busy = false;
        _csvExport = fittedCsv.toString().trimRight();
        _points = points;
        _fit = fitXs
            .asMap()
            .entries
            .map((entry) => PlotPoint(entry.value, fitYs[entry.key]))
            .toList(growable: false);
        _result = fittedText;
        _error = rSquared.isFinite
            ? null
            : nextEraText(
                context,
                'The model could not be fitted.',
                '无法拟合该模型。',
              );
      });
      if (fittedText != null) {
        recordCalculationHistory(
          ref,
          expression: '$_model fit: ${_data.text}',
          result: fittedText,
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
    } catch (_) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = nextEraText(
            context,
            'The model could not be fitted.',
            '无法拟合该模型。',
          );
        });
      }
    }
  }

  double? _interpolateFitted(double x, List<double> fitXs, List<double> fitYs) {
    if (fitXs.isEmpty || fitXs.length != fitYs.length || !x.isFinite) {
      return null;
    }
    if (fitXs.length == 1) return fitYs.first;
    if (x <= fitXs.first) return fitYs.first;
    if (x >= fitXs.last) return fitYs.last;
    for (var index = 1; index < fitXs.length; index++) {
      if (x <= fitXs[index]) {
        final leftX = fitXs[index - 1];
        final rightX = fitXs[index];
        final width = rightX - leftX;
        if (width == 0) return fitYs[index];
        final fraction = (x - leftX) / width;
        return fitYs[index - 1] + fraction * (fitYs[index] - fitYs[index - 1]);
      }
    }
    return fitYs.last;
  }

  Future<void> _interpolate() async {
    final xs = <double>[];
    final ys = <double>[];
    for (final line in _data.text.split(RegExp(r'[\r\n]+'))) {
      final cells = line.trim().split(RegExp(r'[,;\t ]+'));
      if (cells.length < 2) {
        continue;
      }
      final x = double.tryParse(cells[0]);
      final y = double.tryParse(cells[1]);
      if (x != null && y != null && x.isFinite && y.isFinite) {
        xs.add(x);
        ys.add(y);
      }
    }
    final x = double.tryParse(_interpolationX.text);
    if (xs.length < 2 || x == null) {
      if (mounted) {
        setState(
          () => _error = nextEraText(
            context,
            'Enter valid points and an interpolation x.',
            '请输入有效点和插值 x。',
          ),
        );
      }
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final backend = ref.read(calcBackendProvider);
      final value = await backend.interpolate(_interpolationMethod, xs, ys, x);
      if (!mounted) {
        return;
      }
      final interpolationText = value == null
          ? null
          : 'f($x) = ${value.toStringAsPrecision(12)}';
      setState(() {
        _busy = false;
        _result = interpolationText;
        _error = value == null
            ? nextEraText(context, 'Interpolation failed.', '插值失败。')
            : null;
      });
      if (interpolationText != null) {
        recordCalculationHistory(
          ref,
          expression: '$_interpolationMethod interpolation at x=$x',
          result: interpolationText,
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
}
