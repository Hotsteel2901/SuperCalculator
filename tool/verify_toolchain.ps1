$ErrorActionPreference = 'Stop'
if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
  throw 'Flutter SDK not found. Install the locked stable SDK before running Flutter checks.'
}
flutter --version
dart --version
flutter doctor -v
flutter pub get
flutter gen-l10n
flutter analyze
flutter test
