#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bash "$ROOT/bootstrap.sh"
bash "$ROOT/cosmos.sh" setup
# Direct Python keeps the caller's cwd, so relative target paths work.
exec "$ROOT/.pixi/envs/default/bin/python" "$ROOT/update_repos.py" "$@"
