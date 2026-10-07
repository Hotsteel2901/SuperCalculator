import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../features/calculus/calculus_page.dart';
import '../features/data_analysis/data_analysis_page.dart';
import '../features/equations/equations_page.dart';
import '../features/home/home_page.dart';
import '../features/history/history_page.dart';
import '../features/linear_algebra/linear_algebra_page.dart';
import '../features/ode/ode_page.dart';
import '../features/plotting/plot_page.dart';
import '../features/signals/signals_page.dart';
import '../features/statistics/statistics_page.dart';
import '../features/tools/tools_page.dart';
import 'shell/app_shell.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/home',
  routes: <RouteBase>[
    ShellRoute(
      builder: (BuildContext context, GoRouterState state, Widget child) {
        return AppShell(location: state.uri.path, child: child);
      },
      routes: <RouteBase>[
        GoRoute(path: '/home', builder: (_, _) => const HomePage()),
        GoRoute(path: '/plotting', builder: (_, _) => const PlotPage()),
        GoRoute(path: '/calculus', builder: (_, _) => const CalculusPage()),
        GoRoute(path: '/equations', builder: (_, _) => const EquationsPage()),
        GoRoute(path: '/ode', builder: (_, _) => const OdePage()),
        GoRoute(path: '/signals', builder: (_, _) => const SignalsPage()),
        GoRoute(
          path: '/data-analysis',
          builder: (_, _) => const DataAnalysisPage(),
        ),
        GoRoute(path: '/statistics', builder: (_, _) => const StatisticsPage()),
        GoRoute(
          path: '/linear-algebra',
          builder: (_, _) => const LinearAlgebraPage(),
        ),
        GoRoute(path: '/tools', builder: (_, _) => const ToolsPage()),
        GoRoute(path: '/history', builder: (_, _) => const HistoryPage()),
      ],
    ),
  ],
);
