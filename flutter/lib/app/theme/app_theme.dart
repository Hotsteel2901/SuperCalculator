import 'package:flutter/material.dart';

import 'design_tokens.dart';

ThemeData buildAppTheme(Brightness brightness) {
  final scheme = ColorScheme.fromSeed(
    seedColor: const Color(0xFF536DDE),
    brightness: brightness,
    dynamicSchemeVariant: DynamicSchemeVariant.expressive,
  );
  const tokens = SuperCalcDesignTokens.defaults();

  return ThemeData(
    useMaterial3: true,
    brightness: brightness,
    colorScheme: scheme,
    extensions: const <ThemeExtension<dynamic>>[tokens],
    visualDensity: VisualDensity.standard,
    scaffoldBackgroundColor: scheme.surface,
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.surfaceContainerLow,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(tokens.cornerMedium)),
        borderSide: BorderSide(color: scheme.outlineVariant),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(tokens.cornerMedium)),
        borderSide: BorderSide(color: scheme.outlineVariant),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(tokens.cornerMedium)),
        borderSide: BorderSide(color: scheme.primary, width: 2),
      ),
      contentPadding: EdgeInsets.symmetric(
        horizontal: tokens.controlGap,
        vertical: tokens.controlGap,
      ),
    ),
    cardTheme: CardThemeData(
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(tokens.cornerLarge)),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: Size(0, tokens.controlMinHeight),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.cornerMedium)),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: Size(0, tokens.controlMinHeight),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.cornerMedium)),
        ),
      ),
    ),
    navigationRailTheme: NavigationRailThemeData(
      backgroundColor: scheme.surfaceContainerLow,
      indicatorColor: scheme.secondaryContainer,
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: scheme.surfaceContainerLow,
      indicatorColor: scheme.secondaryContainer,
    ),
  );
}
