import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/plot/plot_point.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class SignalsPage extends ConsumerStatefulWidget {
  const SignalsPage({super.key});

  @override
  ConsumerState<SignalsPage> createState() => _SignalsPageState();
}

class _SignalsPageState extends ConsumerState<SignalsPage> {
  final _expression = TextEditingController(text: 'sin(2*pi*5*x) + 0.5*sin(2*pi*12*x)');
  final _start = TextEditingController(text: '0');
  final _end = TextEditingController(text: '1');
  final _samples = TextEditingController(text: '1024');
  List<PlotPoint> _spectrum = const <PlotPoint>[];
  String? _result;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _expression.dispose();
    _start.dispose();
    _end.dispose();
    _samples.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FeaturePageFrame(
      title: AppLocalizations.of(context).signals,
      icon: Icons.graphic_eq,
      subtitle: nextEraText(
        context,
        'Use a radix-2 FFT for fast spectrum inspection and dominant-frequency detection.',
        '使用基 2 FFT 快速查看频谱并检测主频。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Spectrum analyzer', '频谱分析器'),
            icon: Icons.equalizer,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _expression,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'Signal f(t)', '信号 f(t)'),
                    helperText: nextEraText(
                      context,
                      'Use x as the time variable.',
                      '使用 x 作为时间变量。',
                    ),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    _field(_start, nextEraText(context, 'Start', '起点')),
                    _field(_end, nextEraText(context, 'End', '终点')),
                    _field(_samples, nextEraText(context, 'Samples', '采样数')),
                  ],
                ),
                FilledButton.icon(
                  onPressed: _busy ? null : _analyze,
                  icon: const Icon(Icons.waves),
                  label: Text(nextEraText(context, 'Analyze spectrum', '分析频谱')),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          ResultCard(
            value: _result ?? nextEraText(context, 'No spectrum computed yet.', '尚未计算频谱。'),
            error: _error,
          ),
          if (_busy) ...<Widget>[
            const SizedBox(height: 12),
            const LinearProgressIndicator(),
          ],
          if (_spectrum.isNotEmpty) ...<Widget>[
            const SizedBox(height: 16),
            FeatureCard(
              title: nextEraText(context, 'Amplitude spectrum', '幅度频谱'),
              icon: Icons.show_chart,
              child: SizedBox(
                height: 360,
                child: Semantics(
                  label: nextEraText(
                    context,
                    'Amplitude spectrum with ${_spectrum.length} frequency bins.',
                    '包含 ${_spectrum.length} 个频率 bin 的幅度频谱。',
                  ),
                  child: CustomPaint(
                    painter: LineSeriesPainter(
                      series: <List<PlotPoint>>[_spectrum],
                      scheme: Theme.of(context).colorScheme,
                    ),
                    child: const SizedBox.expand(),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _field(TextEditingController controller, String label) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
    );
  }

  Future<void> _analyze() async {
    final start = parseMathNumber(_start.text);
    final end = parseMathNumber(_end.text);
    final samples = int.tryParse(_samples.text.trim());
    if (start == null || end == null || samples == null || end <= start) {
      setState(() {
        _error = nextEraText(context, 'Enter a valid interval and sample count.', '请输入有效区间和采样数。');
      });
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
      _spectrum = const <PlotPoint>[];
    });
    final spectrum = await ref.read(calcBackendProvider).spectrum(
      _expression.text,
      a: start,
      b: end,
      samples: samples.clamp(2, 32768).toInt(),
    );
    if (!mounted) {
      return;
    }
    final points = <PlotPoint>[];
    for (var i = 0; i < spectrum.length; i++) {
      if (spectrum.amplitudes[i].isFinite) {
        points.add(PlotPoint(spectrum.frequencies[i], spectrum.amplitudes[i]));
      }
    }
    final dominant = spectrum.dominantIndex;
    setState(() {
      _busy = false;
      _spectrum = points;
      _result = dominant < 0
          ? null
          : nextEraText(
              context,
              'Dominant frequency: ${spectrum.frequencies[dominant].toStringAsPrecision(8)} Hz',
              '主频：${spectrum.frequencies[dominant].toStringAsPrecision(8)} Hz',
            );
      _error = points.isEmpty
          ? nextEraText(context, 'The signal could not be evaluated.', '无法计算该信号。')
          : null;
    });
  }
}
