# Toolchain and Material 3 Expressive evidence

The migration baseline was checked against the Flutter repository's stable ref before
coding. The baseline records Flutter `3.47.6` and its embedded Dart `3.13.5`; CI
must print the actual installed versions and fail the upgrade review if they differ.
Do not infer a version from a package README or from the Flutter packages repository.

References used for API checks:

- Flutter stable `ColorScheme` source:
  <https://github.com/flutter/flutter/blob/stable/packages/flutter/lib/src/material/color_scheme.dart>
- Flutter stable `CardThemeData` source:
  <https://github.com/flutter/flutter/blob/stable/packages/flutter/lib/src/material/card_theme.dart>
- Flutter Material 3 docs:
  <https://docs.flutter.dev/ui/design/material>
- Material 3 Expressive migration checklist on Flutter main:
  <https://github.com/flutter/flutter/blob/master/docs/ecosystem/material_ui/Material-3-Expressive-component-migration-checklist.md>

The application therefore uses only stable Flutter APIs verified in the baseline:
`ThemeData(useMaterial3: true)`, `ColorScheme.fromSeed`,
`DynamicSchemeVariant.expressive`, `CardThemeData`, and Material navigation/widgets.
The project does not assume a global stable Expressive `ThemeData` mode or that the
standalone `material_ui` package is bundled in the Flutter SDK.
