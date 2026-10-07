#!/usr/bin/env bash
set -euo pipefail

if ! command -v flutter >/dev/null 2>&1; then
  echo 'Flutter SDK not found. Install the locked stable SDK before running Flutter checks.' >&2
  exit 2
fi

flutter --version
dart --version
flutter doctor -v
flutter pub get
flutter gen-l10n
flutter analyze
flutter test
