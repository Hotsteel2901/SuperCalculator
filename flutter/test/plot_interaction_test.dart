import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:supercalculator_next_era/app/theme/app_theme.dart';
import 'package:supercalculator_next_era/core/plot/interactive_plot_view.dart';
import 'package:supercalculator_next_era/core/plot/plot_point.dart';
import 'package:supercalculator_next_era/core/plot/plot_viewport.dart';
import 'package:supercalculator_next_era/core/ui/feature_widgets.dart';
import 'package:supercalculator_next_era/features/plotting/plot_fullscreen_page.dart';

void main() {
  testWidgets('interactive plot clips its painter to its bounds', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: SizedBox(
              height: 200,
              width: 300,
              child: InteractivePlotView(
                points: const <PlotPoint>[PlotPoint(0, 0), PlotPoint(1, 1)],
                mode: 'function',
                scheme: ThemeData().colorScheme,
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
      ),
    );

    final view = find.byType(InteractivePlotView);
    expect(view, findsOneWidget);
    expect(
      find.descendant(of: view, matching: find.byType(ClipRRect)),
      findsOneWidget,
    );
  });

  testWidgets('dragging pans the complete data-space coordinate viewport', (
    tester,
  ) async {
    final key = GlobalKey<InteractivePlotViewState>();
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: SizedBox(
              height: 200,
              width: 300,
              child: InteractivePlotView(
                key: key,
                points: const <PlotPoint>[
                  PlotPoint(-10, 0),
                  PlotPoint(0, 1),
                  PlotPoint(10, 0),
                ],
                mode: 'function',
                scheme: ThemeData().colorScheme,
              ),
            ),
          ),
        ),
      ),
    );

    final before = key.currentState!.viewport;
    await tester.drag(find.byType(InteractivePlotView), const Offset(60, 30));
    await tester.pumpAndSettle();

    final after = key.currentState!.viewport;
    expect(after.xMin, lessThan(before.xMin));
    expect(after.xMax, lessThan(before.xMax));
    expect(after.yMin, greaterThan(before.yMin));
    expect(after.yMax, greaterThan(before.yMax));
    expect(after.xSpan, closeTo(before.xSpan, 1e-9));
    expect(after.ySpan, closeTo(before.ySpan, 1e-9));
  });

  testWidgets('plot markers use the current axis range for coordinates', (
    tester,
  ) async {
    final key = GlobalKey<InteractivePlotViewState>();
    final marked = <PlotPoint>[];
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: SizedBox(
              height: 200,
              width: 300,
              child: InteractivePlotView(
                key: key,
                points: const <PlotPoint>[PlotPoint(0, 0)],
                mode: 'function',
                scheme: ThemeData().colorScheme,
                onMarkPoint: marked.add,
              ),
            ),
          ),
        ),
      ),
    );

    final bounds = tester.getTopLeft(find.byType(InteractivePlotView));
    final plotArea = PlotLayout.plotRectFor(const Size(300, 200));
    await tester.tapAt(bounds + plotArea.center);

    expect(marked, hasLength(1));
    expect(marked.single.x, closeTo(0, 1e-6));
    expect(marked.single.y, closeTo(0, 1e-6));
    expect(key.currentState!.viewport, PlotViewport.initial);
  });

  testWidgets('expandable chart opens a full-screen secondary page', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ExpandableChart(
            title: 'Spectrum',
            semanticsLabel: 'Spectrum preview',
            painter: LineSeriesPainter(
              series: const <List<PlotPoint>>[],
              scheme: ThemeData().colorScheme,
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.byIcon(Icons.fullscreen));
    await tester.pumpAndSettle();

    expect(find.byType(ChartFullscreenPage), findsOneWidget);
  });

  testWidgets('plot full-screen page hosts and preserves the plot viewport', (
    tester,
  ) async {
    const viewport = PlotViewport(
      xMin: -20,
      xMax: 20,
      yMin: -5,
      yMax: 5,
    );
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: buildAppTheme(Brightness.light),
          home: const PlotFullscreenPage(initialViewport: viewport),
        ),
      ),
    );

    expect(find.byType(InteractivePlotView), findsOneWidget);
    expect(find.byType(ClipRRect), findsWidgets);
    final plotState = tester.state<InteractivePlotViewState>(
      find.byType(InteractivePlotView),
    );
    expect(plotState.viewport, viewport);
  });
}
