import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:supercalculator_next_era/app/theme/app_theme.dart';
import 'package:supercalculator_next_era/core/plot/interactive_plot_view.dart';
import 'package:supercalculator_next_era/core/plot/plot_point.dart';
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

  testWidgets('plot full-screen page hosts the interactive plot surface', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: buildAppTheme(Brightness.light),
          home: const PlotFullscreenPage(),
        ),
      ),
    );

    expect(find.byType(InteractivePlotView), findsOneWidget);
    expect(find.byType(ClipRRect), findsWidgets);
  });
}
