# Material 3 Expressive design system

The app uses Flutter stable Material 3 APIs and the checked-in `DynamicSchemeVariant.expressive`
color scheme variant. Flutter does not provide a single stable global Expressive theme
switch, so application-specific Expressive additions are implemented as
`SuperCalcDesignTokens`, a `ThemeExtension`.

Tokens cover layout breakpoints, spacing, control minimum sizes, corner shapes, plot
surface behavior and motion durations. Widgets must consume tokens rather than adding
one-off colors, dimensions or animation timings.

Accessibility is part of the component contract: every action has a semantic label,
plots expose a textual summary and data table path, curves are not distinguished only
by color, and reduced-motion behavior is handled by the shared motion policy.
