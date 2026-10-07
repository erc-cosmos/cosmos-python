#!/usr/bin/env bash
# Install the saved local Python environment; no existing Python is required.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bash "$ROOT/bootstrap.sh"
bash "$ROOT/cosmos.sh" setup
echo 'Python is ready. From this directory, run: source ./activate.sh'
echo 'Then run: pixi run --locked python --version'
