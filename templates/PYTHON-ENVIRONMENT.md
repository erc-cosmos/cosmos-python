# Python environment

This repository uses Pixi, with its own Python and packages. No system Python is
needed. The starter initially includes only Python: a maintainer must add the
project's dependencies and validate its code before distributing it as ready to use.

## First setup (also for collaborators)

Mac/Linux, from this repository directory:

```sh
bash bootstrap.sh
bash cosmos.sh setup
source ./activate.sh
pixi run python --version
pixi run python foo.py
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 setup
. .\activate.ps1
pixi run python --version
pixi run python foo.py
```

Activation makes `pixi` available in this terminal; repeat it in new terminals.
If PowerShell policy blocks dot-sourcing, use an allowed session (for example
launch `powershell -ExecutionPolicy Bypass`) subject to organisation policy.
It does not activate Python directly or change your shell profile.

`foo.py` stands for your actual script. Once pytest is added to the environment,
`pixi run pytest` runs the tests. Pixi requires `run`; `pixi python` is not a native
command. To refuse automatic lockfile changes, use `pixi run --locked python foo.py`
and `pixi run --locked pytest`. The `cosmos.sh run` / `cosmos.ps1 run` helpers always
use locked mode. `pixi run` alone can update a stale lockfile.

If the installer used `--files-only`, first run bootstrap and update, as below,
to resolve and install the environment before using `setup`. A custom Python
version does not have a lockfile until this initial update succeeds.

## Add requirements and update

Edit `pixi.toml` locally. Under `[dependencies]`, each line describes a conda-forge
package, for example `numpy = "==1.26.4"` for an exact pin. Choose versions suitable
for this project. Python itself is listed there. Put packages unavailable from
conda-forge under `[pypi-dependencies]`, without duplicating the same package in
both sections. Or run `bash cosmos.sh add` (Windows: `cosmos.ps1 add`) for prompts.

After editing:

```sh
bash update.sh
source ./activate.sh
pixi run --locked python your_script.py
```

Windows: `powershell -ExecutionPolicy Bypass -File .\update.ps1`.
Run the project's tests, then commit the new scripts, ignore rules, this guide,
`pixi.toml`, and `pixi.lock`. Colleagues use `setup` to reproduce the saved versions.
For deliberate upgrades of all packages within the allowed version ranges, use
`bash cosmos.sh upgrade` / `cosmos.ps1 upgrade`.
If you previously set `PIXI_LOCKED=true` in your terminal, unset it before updating
(`unset PIXI_LOCKED` / `Remove-Item Env:PIXI_LOCKED -ErrorAction SilentlyContinue`).

Existing requirements files are not imported automatically. Review the project's
requirements and imports yourself. For a packaged project, consider an editable
local dependency under `[pypi-dependencies]`:
`your-package = { path = ".", editable = true }`, using its actual package name.
For an unpackaged project whose scripts cannot import the root package, add
`[activation.env]` and `PYTHONPATH = "$PIXI_PROJECT_ROOT"` to the manifest.

## Sharing and privacy

Each repository has its own manifest and lockfile. Do not commit `.tools/`, `.pixi/`,
or `.cache/`. The setup uses local files and does not upload code to a chat or
create GitHub repositories, commits, or pushes. Installation contacts GitHub and
package servers to download tools and dependencies; it is not offline.
Use your normal local credentials for private dependencies, never tokens embedded
in configuration. Keep private repository manifests and lockfiles private too.
The lockfile supports Apple Silicon/Intel Mac, Windows x64, and Linux x64, but
validate your actual application on each platform you intend to support.

## Keep the setup scripts up to date

See [COSMOS-TOOLS.md](COSMOS-TOOLS.md) for upgrading the helper scripts from a newer
cosmos-python checkout. Commit `.cosmos-python.json` with the scripts so future
updates can detect local modifications. This project guide and the dependency
manifest/lockfile are preserved by helper updates.
