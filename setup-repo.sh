#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Capture relative repository paths in the caller's directory before Pixi changes cwd.
if [ "$#" -eq 0 ]; then
  echo 'Usage: bash setup-repo.sh REPOSITORY [--python 3.12] [--dry-run] [--files-only]'
  exit 1
fi
if [[ "$1" = /* ]] || [[ "$1" = -* ]]; then
  TARGET="$1"
else
  TARGET="$PWD/$1"
fi
shift
bash "$ROOT/bootstrap.sh"
bash "$ROOT/cosmos.sh" setup
bash "$ROOT/cosmos.sh" run python "$ROOT/setup_repo.py" "$TARGET" "$@"
