import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/design_tokens.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class AppShell extends StatelessWidget {
  const AppShell({required this.location, required this.child, super.key});

  final String location;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final tokens = SuperCalcDesignTokens.of(context);
    final destinations = <_Destination>[
      _Destination('/home', Icons.home_outlined, Icons.home, l10n.home),
      _Destination(
        '/plotting',
        Icons.show_chart_outlined,
        Icons.show_chart,
        l10n.plotting,
      ),
      _Destination(
        '/calculus',
        Icons.functions_outlined,
        Icons.functions,
        l10n.calculus,
      ),
      _Destination(
        '/equations',
        Icons.account_tree_outlined,
        Icons.account_tree,
        l10n.equations,
      ),
      _Destination(
        '/ode',
        Icons.device_hub_outlined,
        Icons.device_hub,
        l10n.ode,
      ),
      _Destination(
        '/signals',
        Icons.graphic_eq_outlined,
        Icons.graphic_eq,
        l10n.signals,
      ),
      _Destination(
        '/data-analysis',
        Icons.insights_outlined,
        Icons.insights,
        l10n.dataAnalysis,
      ),
      _Destination(
        '/statistics',
        Icons.bar_chart_outlined,
        Icons.bar_chart,
        l10n.statistics,
      ),
      _Destination(
        '/linear-algebra',
        Icons.grid_4x4_outlined,
        Icons.grid_4x4,
        l10n.linearAlgebra,
      ),
      _Destination('/tools', Icons.build_outlined, Icons.build, l10n.tools),
      _Destination(
        '/history',
        Icons.history_outlined,
        Icons.history,
        nextEraText(context, 'History', '历史'),
      ),
    ];
    final compactDestinations = <_Destination>[
      ...destinations.take(4),
      destinations.last,
    ];
    final selected = _selectedIndex(location, destinations);
    final compactSelected = _selectedIndex(location, compactDestinations);

    void navigate(int index) {
      if (index >= 0 && index < destinations.length) {
        context.go(destinations[index].path);
      }
    }

    void navigateCompact(int index) {
      if (index >= 0 && index < compactDestinations.length) {
        context.go(compactDestinations[index].path);
      }
    }

    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final useRail = constraints.maxWidth >= tokens.compactBreakpoint;
        final page = Scaffold(
          body: child,
          bottomNavigationBar: useRail
              ? null
              : NavigationBar(
                  selectedIndex: compactSelected,
                  onDestinationSelected: navigateCompact,
                  destinations: compactDestinations
                      .map(
                        (item) => NavigationDestination(
                          icon: Icon(item.icon),
                          selectedIcon: Icon(item.selectedIcon),
                          label: item.label,
                        ),
                      )
                      .toList(growable: false),
                ),
        );

        if (!useRail) {
          return page;
        }

        return Scaffold(
          body: Row(
            children: <Widget>[
              NavigationRail(
                selectedIndex: selected,
                onDestinationSelected: navigate,
                labelType: constraints.maxWidth >= tokens.mediumBreakpoint
                    ? NavigationRailLabelType.all
                    : NavigationRailLabelType.selected,
                groupAlignment: -0.9,
                leading: Padding(
                  padding: EdgeInsets.only(bottom: tokens.cardGap),
                  child: Semantics(
                    label: l10n.appTitle,
                    child: Icon(
                      Icons.calculate_outlined,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ),
                destinations: destinations
                    .map(
                      (item) => NavigationRailDestination(
                        icon: Icon(item.icon),
                        selectedIcon: Icon(item.selectedIcon),
                        label: Text(item.label),
                      ),
                    )
                    .toList(growable: false),
              ),
              const VerticalDivider(width: 1),
              Expanded(child: page),
            ],
          ),
        );
      },
    );
  }

  int _selectedIndex(String current, List<_Destination> destinations) {
    final index = destinations.indexWhere(
      (item) => current == item.path || current.startsWith('${item.path}/'),
    );
    return index < 0 ? 0 : index;
  }
}

class _Destination {
  const _Destination(this.path, this.icon, this.selectedIcon, this.label);

  final String path;
  final IconData icon;
  final IconData selectedIcon;
  final String label;
}
