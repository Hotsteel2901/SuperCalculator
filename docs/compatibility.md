# Compatibility matrix

The target matrix is Android, iOS, Windows, Linux, macOS and Web. M0 only creates the
Flutter application shell; native artifact packaging is an M2/M7 deliverable.

For each release, CI records:

- Flutter and Dart versions;
- Android ABI and minimum SDK;
- Windows architecture;
- Linux architecture;
- macOS Intel/Apple Silicon status;
- iOS unsigned build status and signing requirements;
- Web browser and Wasm status;
- light/dark, large text and keyboard/assistive technology checks.

The current Android application ID is `com.supercalc`. The default migration plan
keeps it so an installed legacy APK can be upgraded. Product-visible naming is
`SuperCalculator - Next Era`.
