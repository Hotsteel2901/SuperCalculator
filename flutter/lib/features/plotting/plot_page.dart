import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/theme/design_tokens.dart';
import '../../core/plot/function_plot_painter.dart';
import '../../core/presets/preset_catalog.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';
import 'calculator_controller.dart';

class _PlotPreset {
  const _PlotPreset(
    this.label,
    this.expression, [
    this.secondary,
    this.start = 0,
    this.end = 2 * 3.141592653589793,
  ]);

  final String label;
  final String expression;
  final String? secondary;
  final double start;
  final double end;
}

const _plotPresets = <String, List<_PlotPreset>>{
  'function': <_PlotPreset>[
    _PlotPreset('sin(x)', 'sin(x)'),
    _PlotPreset('cos(x)', 'cos(x)'),
    _PlotPreset('tan(x)', 'tan(x)'),
    _PlotPreset('x²', 'x^2'),
    _PlotPreset('x³', 'x^3'),
    _PlotPreset('sqrt(x)', 'sqrt(x)'),
    _PlotPreset('ln(x)', 'ln(x)'),
    _PlotPreset('log10(x)', 'log(x)'),
    _PlotPreset('exp(x)', 'exp(x)'),
    _PlotPreset('1/x', '1/x'),
    _PlotPreset('abs(x)', 'abs(x)'),
    _PlotPreset('sin(x)+cos(x)', 'sin(x)+cos(x)'),
    _PlotPreset('x·sin(x)', 'x*sin(x)'),
    _PlotPreset('damped sine', 'exp(-x)*sin(2*pi*x)'),
    _PlotPreset('x²/2-cos(x)', 'x^2/2-cos(x)'),
    _PlotPreset('factorial', 'x!'),
    _PlotPreset('floor(x)', 'floor(x)'),
    _PlotPreset('ceil(x)', 'ceil(x)'),
    _PlotPreset('x mod 1', 'x mod 1'),
    _PlotPreset('sin(x) mod 1', 'sin(x) mod 1'),
    _PlotPreset('3D paraboloid', 'x^2+y^2'),
    _PlotPreset('3D wave', 'sin(x)*cos(y)'),
    _PlotPreset('3D radial wave', 'sin(sqrt(x^2+y^2))'),
    _PlotPreset('FFT two tones', 'sin(2*pi*x)+0.5*sin(6*pi*x)'),
    _PlotPreset('FFT mixed tones', 'sin(5*x)+cos(10*x)'),
  ],
  'parametric': <_PlotPreset>[
    _PlotPreset('Circle', 'cos(x)', 'sin(x)'),
    _PlotPreset('Ellipse', '2*cos(x)', 'sin(x)'),
    _PlotPreset('Lissajous', 'sin(3*x+pi/2)', 'sin(2*x)'),
    _PlotPreset('Spiral', 'x*cos(x)', 'x*sin(x)', 0, 6 * 3.141592653589793),
    _PlotPreset('Cardioid', '2*cos(x)-cos(2*x)', '2*sin(x)-sin(2*x)'),
    _PlotPreset(
      'Heart',
      '16*sin(x)^3',
      '13*cos(x)-5*cos(2*x)-2*cos(3*x)-cos(4*x)',
    ),
    _PlotPreset('Astroid', '4*cos(x)^3', '4*sin(x)^3'),
    _PlotPreset('Hypotrochoid', '2*cos(x)+cos(2*x)', '2*sin(x)-sin(2*x)'),
    _PlotPreset(
      'Butterfly seed',
      'sin(x)*(exp(cos(x))-2*cos(4*x)-sin(x/12)^5)',
      'cos(x)*(exp(cos(x))-2*cos(4*x)-sin(x/12)^5)',
      0,
      12 * 3.141592653589793,
    ),
    _PlotPreset('Rose', 'cos(4*x)*cos(x)', 'cos(4*x)*sin(x)'),
  ],
  'polar': <_PlotPreset>[
    _PlotPreset('Circle', '1', null),
    _PlotPreset('Cardioid', '1+cos(x)', null),
    _PlotPreset('Rose 3', 'cos(3*x)', null),
    _PlotPreset('Rose 4', 'sin(4*x)', null),
    _PlotPreset('Clover', 'cos(2*x)', null),
    _PlotPreset('Spiral', 'x/(2*pi)', null, 0, 6 * 3.141592653589793),
    _PlotPreset('Archimedean spiral', 'x', null, 0, 6 * 3.141592653589793),
    _PlotPreset('Lemniscate', 'sqrt(abs(cos(2*x)))', null),
    _PlotPreset('Limacon', '1+0.5*cos(x)', null),
    _PlotPreset('Conchoid seed', '1/cos(x)', null),
    _PlotPreset('Butterfly', 'exp(sin(x))-2*cos(4*x)+sin((2*x-pi)/24)^5', null),
    _PlotPreset('Fermat spiral', 'sqrt(x)', null),
  ],
  'implicit': <_PlotPreset>[
    _PlotPreset('Circle', 'x^2+y^2-4'),
    _PlotPreset('Ellipse', 'x^2/9+y^2/4-1'),
    _PlotPreset('Hyperbola', 'x^2/4-y^2/4-1'),
    _PlotPreset('Parabola', 'y-x^2'),
    _PlotPreset('Saddle', 'x^2-y^2'),
    _PlotPreset('Astroid', 'x^2+y^2-1'),
    _PlotPreset('Lemniscate', '(x^2+y^2)^2-2*(x^2-y^2)'),
    _PlotPreset('Folium seed', 'x^3+y^3-3*x*y'),
  ],
  'surface': <_PlotPreset>[
    _PlotPreset('Paraboloid', 'x^2+y^2'),
    _PlotPreset('Saddle', 'x^2-y^2'),
    _PlotPreset('Gaussian', 'exp(-(x^2+y^2))'),
  ],
  'contour': <_PlotPreset>[
    _PlotPreset('Circle levels', 'x^2+y^2'),
    _PlotPreset('Paraboloid', 'x^2+y^2'),
    _PlotPreset('Saddle', 'x^2-y^2'),
    _PlotPreset('Gaussian', 'exp(-(x^2+y^2))'),
    _PlotPreset('Peaks seed', 'sin(x)*cos(y)'),
  ],
  'direction': <_PlotPreset>[
    _PlotPreset('Exponential growth', 'y'),
    _PlotPreset('Logistic', 'y*(1-y)'),
    _PlotPreset('Damped oscillator', 'y-x'),
    _PlotPreset('Lotka seed', 'x-y'),
    _PlotPreset('Slope field', 'sin(x)+cos(y)'),
    _PlotPreset('Linear field', 'x+y'),
    _PlotPreset('Cubic field', 'x^3-y'),
    _PlotPreset('Van der Pol seed', '(1-y^2)*x-y'),
  ],
  'vector': <_PlotPreset>[
    _PlotPreset('Rotation', '-y', 'x'),
    _PlotPreset('Sink', '-x', '-y'),
    _PlotPreset('Source', 'x', 'y'),
    _PlotPreset('Saddle', 'x', '-y'),
    _PlotPreset('Nonlinear swirl', 'y', '-x+x^3'),
  ],
};

class PlotPage extends ConsumerStatefulWidget {
  const PlotPage({super.key});

  @override
  ConsumerState<PlotPage> createState() => _PlotPageState();
}

class _PlotPageState extends ConsumerState<PlotPage> {
  late final TextEditingController _expressionController;
  late final TextEditingController _secondaryController;
  late final TextEditingController _xController;
  late final TextEditingController _parameterStartController;
  late final TextEditingController _parameterEndController;
  String? _selectedPreset;
  Map<String, List<_PlotPreset>> _availablePresets = _plotPresets;
  double _plotZoom = 1;
  Offset _plotPan = Offset.zero;
  double _plotYaw = -.65;
  double _plotPitch = .55;
  double _gestureZoomStart = 1;
  Offset _gesturePanStart = Offset.zero;
  Offset _gestureFocalStart = Offset.zero;
  double _gestureYawStart = -.65;
  double _gesturePitchStart = .55;

  void _updateParameterRange(CalculatorController controller) {
    final start = double.tryParse(_parameterStartController.text.trim());
    final end = double.tryParse(_parameterEndController.text.trim());
    if (start != null && end != null) {
      controller.setParameterRange(start, end);
    }
  }

  void _resetPlotView() {
    setState(() {
      _plotZoom = 1;
      _plotPan = Offset.zero;
      _plotYaw = -.65;
      _plotPitch = .55;
    });
  }

  @override
  void initState() {
    super.initState();
    final initial = ref.read(calculatorControllerProvider);
    _expressionController = TextEditingController(text: initial.expression);
    _secondaryController = TextEditingController(
      text: initial.secondaryExpression,
    );
    _xController = TextEditingController(text: initial.xText);
    _parameterStartController = TextEditingController(
      text: initial.parameterStart.toString(),
    );
    _parameterEndController = TextEditingController(
      text: initial.parameterEnd.toString(),
    );
    _loadPresetCatalog();
  }

  Future<void> _loadPresetCatalog() async {
    try {
      final definitions = await PresetCatalog.load();
      final loaded = <String, List<_PlotPreset>>{};
      for (final entry in definitions.entries) {
        loaded[entry.key] = entry.value
            .map(
              (preset) => _PlotPreset(
                preset.label,
                preset.expression,
                preset.secondary,
                preset.start,
                preset.end,
              ),
            )
            .toList(growable: false);
      }
      if (mounted && loaded.isNotEmpty) {
        setState(() => _availablePresets = loaded);
      }
    } on FormatException {
      // The checked-in fallback keeps the plot page usable if an asset is
      // unavailable in a restricted embedding or during a partial install.
    } on FlutterError {
      // Same compatibility fallback for a missing asset bundle.
    }
  }

  @override
  void dispose() {
    _expressionController.dispose();
    _secondaryController.dispose();
    _xController.dispose();
    _parameterStartController.dispose();
    _parameterEndController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final tokens = SuperCalcDesignTokens.of(context);
    final state = ref.watch(calculatorControllerProvider);
    final controller = ref.read(calculatorControllerProvider.notifier);
    final scheme = Theme.of(context).colorScheme;
    final presets =
        _availablePresets[state.mode] ?? const <_PlotPreset>[];
    final modes = <String, String>{
      'function': nextEraText(context, 'Function y=f(x)', '函数 y=f(x)'),
      'multi': nextEraText(context, 'Multi-curve overlay', '多曲线叠加'),
      'parametric': nextEraText(
        context,
        'Parametric x(t), y(t)',
        '参数曲线 x(t), y(t)',
      ),
      'polar': nextEraText(context, 'Polar r(t)', '极坐标 r(t)'),
      'implicit': nextEraText(context, 'Implicit f(x,y)=0', '隐式曲线 f(x,y)=0'),
      'surface': nextEraText(context, '3D surface z=f(x,y)', '三维曲面 z=f(x,y)'),
      'contour': nextEraText(context, 'Contour level set', '等高线'),
      'direction': nextEraText(context, 'Direction field', '方向场'),
      'vector': nextEraText(context, 'Vector field P,Q', '向量场 P,Q'),
    };

    return CustomScrollView(
      slivers: <Widget>[
        SliverAppBar.large(title: Text(l10n.plotting)),
        SliverPadding(
          padding: EdgeInsets.all(tokens.pagePadding),
          sliver: SliverList(
            delegate: SliverChildListDelegate(<Widget>[
              Card(
                child: Padding(
                  padding: EdgeInsets.all(tokens.pagePadding),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      DropdownButtonFormField<String>(
                        initialValue: state.mode,
                        decoration: InputDecoration(
                          labelText: nextEraText(context, 'Plot mode', '绘图模式'),
                        ),
                        items: modes.entries
                            .map(
                              (entry) => DropdownMenuItem<String>(
                                value: entry.key,
                                child: Text(entry.value),
                              ),
                            )
                            .toList(growable: false),
                        onChanged: (value) {
                          if (value != null) {
                            setState(() => _selectedPreset = null);
                            controller.setMode(value);
                          }
                        },
                      ),
                      if (presets.isNotEmpty) ...<Widget>[
                        SizedBox(height: tokens.controlGap),
                        DropdownButtonFormField<String>(
                          initialValue:
                              presets.any(
                                (preset) => preset.label == _selectedPreset,
                              )
                              ? _selectedPreset
                              : null,
                          decoration: InputDecoration(
                            labelText: nextEraText(context, 'Preset', '预设'),
                          ),
                          items: presets
                              .map(
                                (preset) => DropdownMenuItem<String>(
                                  value: preset.label,
                                  child: Text(preset.label),
                                ),
                              )
                              .toList(growable: false),
                          onChanged: (label) {
                            if (label == null) return;
                            final preset = presets.firstWhere(
                              (item) => item.label == label,
                            );
                            _expressionController.text = preset.expression;
                            controller.setExpression(preset.expression);
                            if (preset.secondary != null) {
                              _secondaryController.text = preset.secondary!;
                              controller.setSecondaryExpression(
                                preset.secondary!,
                              );
                            }
                            _parameterStartController.text =
                                preset.start.toString();
                            _parameterEndController.text =
                                preset.end.toString();
                            controller.setParameterRange(
                              preset.start,
                              preset.end,
                            );
                            setState(() => _selectedPreset = label);
                          },
                        ),
                      ],
                      SizedBox(height: tokens.controlGap),
                      Text(
                        state.mode == 'parametric'
                            ? nextEraText(context, 'x(t)', 'x(t)')
                            : state.mode == 'polar'
                            ? nextEraText(context, 'r(t)', 'r(t)')
                            : state.mode == 'implicit' ||
                                  state.mode == 'surface' ||
                                  state.mode == 'contour' ||
                                  state.mode == 'direction'
                            ? nextEraText(context, 'f(x,y)', 'f(x,y)')
                            : state.mode == 'vector'
                            ? nextEraText(context, 'P(x,y)', 'P(x,y)')
                            : l10n.expression,
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      SizedBox(height: tokens.controlGap),
                      TextField(
                        controller: _expressionController,
                        onChanged: controller.setExpression,
                        onSubmitted: (_) => controller.evaluate(),
                        keyboardType: TextInputType.text,
                        textInputAction: TextInputAction.go,
                        decoration: InputDecoration(
                          hintText: state.mode == 'parametric'
                              ? 'cos(x)'
                              : state.mode == 'polar'
                              ? '1 + cos(x)'
                              : 'sin(x)',
                        ),
                        style: const TextStyle(fontFamily: 'monospace'),
                      ),
                      if (state.mode == 'parametric' ||
                          state.mode == 'vector') ...<Widget>[
                        SizedBox(height: tokens.controlGap),
                        TextField(
                          controller: _secondaryController,
                          onChanged: controller.setSecondaryExpression,
                          decoration: InputDecoration(
                            labelText: nextEraText(context, 'y(t)', 'y(t)'),
                            hintText: 'sin(x)',
                          ),
                          style: const TextStyle(fontFamily: 'monospace'),
                        ),
                      ],
                      if (state.mode == 'parametric' || state.mode == 'polar') ...<Widget>[
                        SizedBox(height: tokens.controlGap),
                        FormRow(
                          children: <Widget>[
                            TextField(
                              controller: _parameterStartController,
                              onChanged: (_) => _updateParameterRange(controller),
                              decoration: InputDecoration(
                                labelText: nextEraText(context, 'Parameter start', '参数起点'),
                              ),
                              keyboardType: const TextInputType.numberWithOptions(
                                decimal: true,
                                signed: true,
                              ),
                            ),
                            TextField(
                              controller: _parameterEndController,
                              onChanged: (_) => _updateParameterRange(controller),
                              decoration: InputDecoration(
                                labelText: nextEraText(context, 'Parameter end', '参数终点'),
                              ),
                              keyboardType: const TextInputType.numberWithOptions(
                                decimal: true,
                                signed: true,
                              ),
                            ),
                          ],
                        ),
                      ],
                      SizedBox(height: tokens.controlGap),
                      Row(
                        children: <Widget>[
                          if (state.mode == 'function')
                            Expanded(
                              child: TextField(
                                controller: _xController,
                                onChanged: controller.setX,
                                keyboardType:
                                    const TextInputType.numberWithOptions(
                                      decimal: true,
                                    ),
                                decoration: InputDecoration(
                                  labelText: l10n.argumentX,
                                ),
                              ),
                            ),
                          if (state.mode == 'function')
                            SizedBox(width: tokens.controlGap),
                          FilledButton.icon(
                            onPressed: state.isCalculating
                                ? null
                                : controller.evaluate,
                            icon: const Icon(Icons.calculate_outlined),
                            label: Text(l10n.evaluate),
                          ),
                          SizedBox(width: tokens.controlGap),
                          IconButton(
                            tooltip: l10n.clear,
                            onPressed: controller.clear,
                            icon: const Icon(Icons.clear),
                          ),
                        ],
                      ),
                      SizedBox(height: tokens.controlGap),
                      Text(
                        l10n.quickExamples,
                        style: Theme.of(context).textTheme.labelLarge,
                      ),
                      SizedBox(height: tokens.controlGap),
                      Wrap(
                        spacing: tokens.controlGap,
                        runSpacing: tokens.controlGap,
                        children: <String>['sin(x)', 'x^2', 'exp(-x^2)', '1/x']
                            .map(
                              (example) => ActionChip(
                                label: Text(example),
                                onPressed: () {
                                  _expressionController.text = example;
                                  controller.setMode('function');
                                  controller.setExpression(example);
                                },
                              ),
                            )
                            .toList(growable: false),
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: tokens.cardGap),
              Semantics(
                liveRegion: true,
                child: Card(
                  color: state.error == null
                      ? scheme.secondaryContainer
                      : scheme.errorContainer,
                  child: Padding(
                    padding: EdgeInsets.all(tokens.pagePadding),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Icon(
                          state.error == null
                              ? Icons.check_circle_outline
                              : Icons.error_outline,
                          color: state.error == null
                              ? scheme.onSecondaryContainer
                              : scheme.onErrorContainer,
                        ),
                        SizedBox(width: tokens.controlGap),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text(
                                l10n.result,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              SizedBox(height: tokens.controlGap / 2),
                              Text(
                                state.isCalculating
                                    ? l10n.computing
                                    : state.error ??
                                          state.value?.toStringAsPrecision(
                                            10,
                                          ) ??
                                          l10n.noResult,
                                style: Theme.of(context).textTheme.bodyLarge,
                              ),
                              SizedBox(height: tokens.controlGap / 2),
                              Text('${l10n.backend}: ${state.backend}'),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              SizedBox(height: tokens.cardGap),
              Card(
                child: Padding(
                  padding: EdgeInsets.all(tokens.pagePadding),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      Text(
                        l10n.plotPreview,
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      SizedBox(height: tokens.controlGap),
                      Semantics(
                        label: l10n.accessibilityPlotSummary(
                          state.points.length,
                          state.expression,
                        ),
                        child: GestureDetector(
                          behavior: HitTestBehavior.opaque,
                          onDoubleTap: _resetPlotView,
                          onScaleStart: (details) {
                            _gestureZoomStart = _plotZoom;
                            _gesturePanStart = _plotPan;
                            _gestureFocalStart = details.focalPoint;
                            _gestureYawStart = _plotYaw;
                            _gesturePitchStart = _plotPitch;
                          },
                          onScaleUpdate: (details) {
                            final delta = details.focalPoint - _gestureFocalStart;
                            setState(() {
                              _plotZoom = (_gestureZoomStart * details.scale)
                                  .clamp(.5, 4.0)
                                  .toDouble();
                              if (state.mode == 'surface') {
                                _plotYaw = _gestureYawStart + delta.dx * .01;
                                _plotPitch = (_gesturePitchStart - delta.dy * .01)
                                    .clamp(-1.35, 1.35)
                                    .toDouble();
                              } else {
                                _plotPan = _gesturePanStart + delta;
                              }
                            });
                          },
                          child: SizedBox(
                            height: tokens.plotMinHeight,
                            child: CustomPaint(
                              painter: FunctionPlotPainter(
                                points: state.points,
                                scheme: scheme,
                                mode: state.mode,
                                zoom: _plotZoom,
                                pan: _plotPan,
                                yaw: _plotYaw,
                                pitch: _plotPitch,
                              ),
                              child: const SizedBox.expand(),
                            ),
                          ),
                        ),
                      ),
                      SizedBox(height: tokens.controlGap),
                      Row(
                        children: <Widget>[
                          Expanded(child: Text(l10n.plotPoints(state.points.length))),
                          TextButton.icon(
                            onPressed: _resetPlotView,
                            icon: const Icon(Icons.center_focus_strong),
                            label: Text(nextEraText(context, 'Reset view', '重置视图')),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ]),
          ),
        ),
      ],
    );
  }
}
