import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/theme/design_tokens.dart';
import '../../core/plot/function_plot_painter.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';
import 'calculator_controller.dart';

class PlotPage extends ConsumerStatefulWidget {
  const PlotPage({super.key});

  @override
  ConsumerState<PlotPage> createState() => _PlotPageState();
}

class _PlotPageState extends ConsumerState<PlotPage> {
  late final TextEditingController _expressionController;
  late final TextEditingController _secondaryController;
  late final TextEditingController _xController;

  @override
  void initState() {
    super.initState();
    final initial = ref.read(calculatorControllerProvider);
    _expressionController = TextEditingController(text: initial.expression);
    _secondaryController = TextEditingController(
      text: initial.secondaryExpression,
    );
    _xController = TextEditingController(text: initial.xText);
  }

  @override
  void dispose() {
    _expressionController.dispose();
    _secondaryController.dispose();
    _xController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final tokens = SuperCalcDesignTokens.of(context);
    final state = ref.watch(calculatorControllerProvider);
    final controller = ref.read(calculatorControllerProvider.notifier);
    final scheme = Theme.of(context).colorScheme;
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
                          if (value != null) controller.setMode(value);
                        },
                      ),
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
                        child: SizedBox(
                          height: tokens.plotMinHeight,
                          child: CustomPaint(
                            painter: FunctionPlotPainter(
                              points: state.points,
                              scheme: scheme,
                            ),
                            child: const SizedBox.expand(),
                          ),
                        ),
                      ),
                      SizedBox(height: tokens.controlGap),
                      Text(l10n.plotPoints(state.points.length)),
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
