#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FLUTTER_DIR="${ROOT_DIR}/flutter"

if ! command -v flutter >/dev/null 2>&1; then
  echo 'Flutter SDK not found. Install the stable SDK before generating platform folders.' >&2
  exit 2
fi

# Flutter owns the platform runners. This is intentionally separate from the
# source scaffold so the exact stable SDK can generate its current templates.
flutter create \
  --no-pub \
  --project-name supercalculator_next_era \
  --org com.supercalc \
  --platforms=android,ios,windows,linux,macos,web \
  "${FLUTTER_DIR}"

printf '\nPlatform folders generated. Review the diff before committing.\n'
