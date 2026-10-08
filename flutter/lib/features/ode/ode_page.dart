import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/backend/providers.dart';
import '../../core/plot/plot_point.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class OdePage extends ConsumerStatefulWidget {
  const OdePage({super.key});

  @override
  ConsumerState<OdePage> createState() => _OdePageState();
}

class _OdePageState extends ConsumerState<OdePage> {
  final _expression = TextEditingController(text: 'y - x^2 + 1');
  final _x0 = TextEditingController(text: '0');
  final _y0 = TextEditingController(text: '0.5');
  final _xEnd = TextEditingController(text: '2');
  final _steps = TextEditingController(text: '200');
  String _method = 'RK4';
  List<PlotPoint> _points = const <PlotPoint>[];
  String? _result;
  String? _error;
  bool _busy = false;

  @override
  void dispose() {
    _expression.dispose();
    _x0.dispose();
    _y0.dispose();
    _xEnd.dispose();
    _steps.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FeaturePageFrame(
      title: AppLocalizations.of(context).ode,
      icon: Icons.device_hub,
      subtitle: nextEraText(
        context,
        'Solve dy/dx = f(x,y) with fourth-order Runge–Kutta and inspect the solution curve.',
        '使用四阶 Runge–Kutta 求解 dy/dx = f(x,y)，并查看解曲线。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Initial value problem', '初值问题'),
            icon: Icons.timeline,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _expression,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'f(x,y)', 'f(x,y)'),
                    helperText: nextEraText(
                      context,
                      'Example: y - x^2 + 1',
                      '示例：y - x^2 + 1',
                    ),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    _numberField(_x0, nextEraText(context, 'x₀', 'x₀')),
                    _numberField(_y0, nextEraText(context, 'y₀', 'y₀')),
                    _numberField(_xEnd, nextEraText(context, 'x end', '终点 x')),
                    _numberField(_steps, nextEraText(context, 'Steps', '步数')),
                    DropdownButtonFormField<String>(
                      initialValue: _method,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Method', '方法'),
                      ),
                      items:
                          <String>[
                                'RK4',
                                'Euler',
                                'Improved-Euler',
                                'Midpoint',
                                'RKF45',
                              ]
                              .map(
                                (value) => DropdownMenuItem(
                                  value: value,
                                  child: Text(value),
                                ),
                              )
                              .toList(growable: false),
                      onChanged: (value) =>
                          setState(() => _method = value ?? 'RK4'),
                    ),
                  ],
                ),
                FilledButton.icon(
                  onPressed: _busy ? null : _solve,
                  icon: const Icon(Icons.play_arrow),
                  label: Text(
                    nextEraText(context, 'Solve with RK4', '使用 RK4 求解'),
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
                  'Run the solver to see the curve.',
                  '运行求解器查看曲线。',
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
              title: nextEraText(context, 'Solution curve', '解曲线'),
              icon: Icons.show_chart,
              child: Semantics(
                label: nextEraText(
                  context,
                  'Runge–Kutta solution curve with ${_points.length} samples.',
                  '包含 ${_points.length} 个采样点的 Runge–Kutta 解曲线。',
                ),
                child: SizedBox(
                  height: 360,
                  child: CustomPaint(
                    painter: LineSeriesPainter(
                      series: <List<PlotPoint>>[_points],
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

  Widget _numberField(TextEditingController controller, String label) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      keyboardType: const TextInputType.numberWithOptions(
        decimal: true,
        signed: true,
      ),
    );
  }

  Future<void> _solve() async {
    final x0 = parseMathNumber(_x0.text);
    final y0 = parseMathNumber(_y0.text);
    final xEnd = parseMathNumber(_xEnd.text);
    final steps = int.tryParse(_steps.text.trim());
    if (x0 == null ||
        y0 == null ||
        xEnd == null ||
        steps == null ||
        steps < 1) {
      setState(() {
        _error = nextEraText(
          context,
          'Enter valid initial values.',
          '请输入有效初值。',
        );
      });
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
      _points = const <PlotPoint>[];
    });
    final solution = await ref
        .read(calcBackendProvider)
        .solveOde(
          _expression.text,
          x0: x0,
          y0: y0,
          xEnd: xEnd,
          steps: steps.clamp(1, 10000).toInt(),
          method: _method,
        );
    if (!mounted) {
      return;
    }
    final points = <PlotPoint>[];
    for (var i = 0; i < solution.xs.length && i < solution.ys.length; i++) {
      final y = solution.ys[i];
      if (y != null && y.isFinite) {
        points.add(PlotPoint(solution.xs[i], y));
      }
    }
    setState(() {
      _busy = false;
      _points = points;
      _result = points.isEmpty
          ? null
          : nextEraText(
              context,
              '${solution.method}: ${points.length} points',
              '${solution.method}：${points.length} 个点',
            );
      _error = points.isEmpty
          ? nextEraText(
              context,
              'The ODE could not be evaluated.',
              '无法计算该微分方程。',
            )
          : null;
    });
  }
}
