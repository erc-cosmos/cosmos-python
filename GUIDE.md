# COSMOS Python guide

For everyday commands, start with the [README](README.md). This guide covers
Windows, advanced options, how updates work, and troubleshooting.

## Windows instructions

Use PowerShell and adjust the paths below to your machine. An internet connection
is required for initial downloads; you do not need Python installed beforehand.

### Install standalone Python

```powershell
New-Item -ItemType Directory -Force "$HOME\github.com\erc-cosmos" | Out-Null
git clone https://github.com/erc-cosmos/cosmos-python.git "$HOME\github.com\erc-cosmos\cosmos-python"
cd "$HOME\github.com\erc-cosmos\cosmos-python"
powershell -ExecutionPolicy Bypass -File .\install.ps1
. .\activate.ps1
pixi run --locked python --version
pixi run --locked python
```

To run an external script, use `pixi run --locked python C:\path\your_script.py`.
Add packages with `cosmos.ps1 add` as below, running from the cosmos-python directory.

### Install Python for a project

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\github.com\erc-cosmos\cosmos-python\setup-repo.ps1" -Repository "C:\work\my-repo"
```

Clone or create the target directory first. Add `-PythonVersion 3.12` to select a
Python minor version, `-DryRun` to preview, or `-FilesOnly` to defer installation.
The starter includes only Python; add the project's dependencies next.

### Add packages and run code

```powershell
cd C:\work\my-repo
powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 add
. .\activate.ps1
pixi run --locked python your_script.py
```

To apply edits to `pixi.toml`:

```powershell
powershell -ExecutionPolicy Bypass -File .\update.ps1
```

After cloning or pulling a project that already has a saved environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 setup
. .\activate.ps1
```

If policy blocks activation, start an allowed session with
`powershell -ExecutionPolicy Bypass` and dot-source `activate.ps1` there.
This option applies only to that process; organisation policy may still prohibit
scripts. Use your organisation's approved approach if so.

### Update existing installations

In a PowerShell session that permits the scripts:

```powershell
git -C "$HOME\github.com\erc-cosmos\cosmos-python" pull --ff-only
& "$HOME\github.com\erc-cosmos\cosmos-python\update-repos.ps1" -Repositories @('C:\work\repo-one', 'C:\work\repo two') -DryRun
& "$HOME\github.com\erc-cosmos\cosmos-python\update-repos.ps1" -Repositories @('C:\work\repo-one', 'C:\work\repo two') -Sync
```

For installations without `.cosmos-python.json`, add `-Adopt` to both commands.
Run each project's tests and review/commit the resulting helper and metadata changes.

## Standalone and project environments

The root `pixi.toml` and `pixi.lock` define the standalone distribution installed
inside your cosmos-python clone. The standalone default is Python 3.14; the
reusable project template also defaults to Python 3.14 unless a version is selected.
`install.sh` / `install.ps1` bootstraps Pixi and
installs that saved environment in one command; no existing Python is required.
It can be used interactively or to execute scripts outside a project. Activation
makes Pixi available; use `pixi run --locked python`, not an unrelated system Python.
For an editor, select `.pixi/envs/default/bin/python` on Mac/Linux or
`.pixi\envs\default\python.exe` on Windows. On Windows, prefer the Pixi wrapper for
execution so environment variables and native-library paths are activated correctly.

The project installer uses the separate Python-only template at
`templates/pixi.toml` and `templates/pixi.lock`. Adding personal packages to the
root standalone environment does not add them to future project environments.
Each project can choose its own Python version and packages; it does not depend
on the standalone environment at runtime after installation.

The installer/updater launchers use the standalone Python to run their tooling,
which requires Python 3.11 or later. Keep that requirement if using this clone to
manage projects, even when a target itself needs Python 3.9 or 3.10. If you change
root dependencies, run update before using the launchers again.

`install` always uses the saved lockfile and refuses inconsistent requirements;
use `update.sh` / `update.ps1` intentionally after editing requirements. For an
unchanged standalone checkout, pull and rerun install to apply published updates.
If you customized its root manifest/lockfile, preserve and reconcile those Git
changes before pulling; the installer does not overwrite them. Repository updater
commands target other repositories, not the cosmos-python clone itself.

A script's relative data paths are resolved in the Pixi workspace directory.
Pass explicit paths when running scripts stored elsewhere. An internet connection
is needed for downloads; this is a locally installed distribution, not a bundled
offline Python binary archive.

## What gets installed

Each repository gets its own Python environment. Bootstrap installs Pixi 0.81.0
inside `.tools/` without changing system Python or your shell profile. Environments
live in `.pixi/` and downloaded packages in `.cache/`. These directories are ignored
by Git. Activation exposes this project's Pixi in the current terminal only.

The installer adds the install, bootstrap, cosmos, update, and activation scripts, plus
`pixi.toml`, `PYTHON-ENVIRONMENT.md`, `COSMOS-TOOLS.md`, and `.cosmos-python.json`.
The workspace name comes from the target directory name. It appends missing ignore
rules while preserving existing README and package metadata.

For default Python 3.14, it copies the starter lockfile; another Python minor
version gets a new lockfile when installation runs. Existing requirements files
are not imported automatically. Project-specific packages must be added and tested.

The installer refuses existing setup filenames, `.tools/`, `.pixi/`, or Pixi
configuration in `pyproject.toml`. Re-running it does not overwrite an established
setup. Use the updater for existing installations, or deliberately merge any
pre-existing configuration.

## Package requirements and lockfiles

`pixi.toml` describes the environment you want. `pixi.lock` records the exact
resolved packages and builds for each platform. Commit them together.

Under `[dependencies]`, use conda-forge packages, including Python. For example:

```toml
python = "3.11.*"
numpy = "==1.26.4"
```

These are syntax examples; choose versions suitable for the project. `3.11.*`
allows Python 3.11 patch releases during updates. `==1.26.4` fixes an exact package
version. `*` permits any version during resolution; the saved lockfile still pins
the result for normal setup.

Use `[pypi-dependencies]` for packages unavailable from conda-forge. Do not list the
same package in both sections. For an installable Python project, an editable
local dependency can reuse its existing package metadata:

```toml
[pypi-dependencies]
your-package = { path = ".", editable = true }
```

Use the actual package name. Keep published package metadata in `pyproject.toml`;
avoid separately maintaining duplicate dependency lists. A Python-version line
in an older requirements.txt belongs in Pixi's Python requirement, not on PyPI.

`update.sh` reconciles edited requirements, preserving locked versions where
possible. To deliberately refresh all dependencies within the allowed ranges:

```sh
bash cosmos.sh upgrade
```

On Windows use `cosmos.ps1 upgrade`. Exact pins remain fixed until edited. Test
before committing any new lockfile. To roll back dependencies, restore both
manifest and lockfile from a known working revision and run `setup`.

`setup` and the cosmos `run` helpers use locked mode. Native `pixi run` can change a
stale lockfile; `pixi run --locked` refuses to do so. Pixi requires the word `run`:
`pixi python` is not a native command. Run commands from the project directory;
Pixi commands run from the workspace root. Use absolute paths for external files.

## Advanced setup options

Mac/Linux setup options are `--python 3.12`, `--dry-run`, and `--files-only`.
Windows equivalents are `-PythonVersion 3.12`, `-DryRun`, and `-FilesOnly`.
After file-only setup, add the requirements, then run bootstrap and update from
the target directory to create the environment and lockfile.

The shell/PowerShell launchers may bootstrap cosmos-python's own Python even in
preview or file-only mode. With an existing Python 3.11+ runtime, bypass that step:

```sh
python3 /path/to/cosmos-python/setup_repo.py /path/to/my-repo --dry-run
python3 /path/to/cosmos-python/setup_repo.py /path/to/my-repo --files-only
python3 /path/to/cosmos-python/update_repos.py /path/to/my-repo --dry-run
```

These direct preview/file-only operations do not download anything. Relative paths
are resolved from the caller's current directory. Quote paths containing spaces.

## How template updates work

New installations record the template version and helper-file checksums in
`.cosmos-python.json`. Keep that file under version control with the scripts.
Content checksums detect changes even if a release number was not bumped.

The updater manages install.sh/.ps1, bootstrap.sh/.ps1, cosmos.sh/.ps1, update.sh/.ps1,
activate.sh/.ps1, and COSMOS-TOOLS.md. Project notes in PYTHON-ENVIRONMENT.md, README,
Python/library requirements, tasks, platforms, lockfile, and ignore rules are
preserved. Generic manifest defaults are not copied into an existing project.

The only automatic manifest migration is `workspace.requires-pixi`, when its value
still matches the recorded previous template. This keeps a new bootstrap and the
required Pixi version aligned. Locally customized constraints stop for review.

`--sync` / `-Sync` runs bootstrap and locked setup after updating helpers. It also
works on an already-current target. It can download packages but does not upgrade
Python or libraries beyond the saved environment. Without it, run bootstrap and
setup manually. With `--dry-run` / `-DryRun`, no target files are written and no
target environment is installed.

Older installations need `--adopt` / `-Adopt` once. All eight helper scripts must
match the starter exactly before adoption records a baseline. If they differ,
register against a matching older starter with tracking support, or carefully
reconcile the scripts with the trusted template first. Do not fabricate checksums
or delete metadata to bypass conflict checks.

Updates only process explicitly supplied paths. They do not schedule background
jobs, pull Git changes, commit, push, or scan other repositories. Arbitrary Python
or venv installations outside the COSMOS workflow are not managed by the updater.

## Conflicts and recovery

A changed or deleted managed helper is a conflict. If any target has a conflict,
the updater changes none of the repositories in that batch. Compare the reported
files with the trusted starter, reconcile them deliberately, then retry. No merge
markers are inserted. Keep project customizations in the manifest or project guide
where possible, rather than modifying centrally managed helpers.

Before replacing files, the updater backs them up with the old metadata under
`.cache/cosmos-python-updates/<id>/` and prints that location. To undo an update:

1. Copy the backed-up files back to the repository root.
2. Remove files listed as newly created in `RESTORE.json`; do not copy that JSON
   file itself into the root.
3. Reapply the old bootstrap/setup if the Pixi tool version changed.

Individual file writes are atomic. Ordinary write failures roll back files already
changed in that target; a crash or power loss may require manual recovery. An I/O
failure in a later target does not undo earlier successful targets in a batch.
Backups cover configuration files, not installed environments.

If initial installation fails after writing files, fix the reported issue and run
bootstrap followed by update in the target. Do not rerun the installer: it protects
those existing files. If updater `--sync` fails, helper changes remain; fix the
error and rerun with `--sync`. If a newer Pixi cannot read the old lockfile, perform
an explicit, reviewed lockfile migration rather than silently upgrading packages.

## Private repositories

You can run all commands in your own terminal without opening private code in a
chat. Scripts have no chat-upload step. They contact GitHub and package servers
for downloads, so local execution is not offline execution. For private dependencies,
use your normal credential management; do not embed tokens in manifests or URLs.
Keep private manifests and lockfiles private because they may reveal package names
and locations. Give an agent access only when authorized, and explicitly reference
[AGENTS.md](AGENTS.md) when it is outside the agent's working directory.

## Why Pixi and the limits of reproducibility

Pixi manages Python, Python packages, and native tools with a multi-platform
lockfile. This suits scientific projects that combine compiled tools and Python
libraries. A purely Python project may also suit uv; each repository should choose
and validate its own environment rather than share one organisation-wide package set.

The starter declares Apple Silicon Mac, Intel Mac, Windows x64, and Linux x64.
Windows ARM is not included. Lockfile resolution does not prove runtime support
on every platform. Different CPUs, operating systems, and GPUs may produce different
floating-point results. Research workflows may also need recorded data versions,
random seeds, external software, drivers, and hardware details.

Mac bootstrap, installation, locked execution, dependency changes, and stale-lock
rejection have been verified. The 17 installer/updater checks passed, including
conflicts, preservation, adoption, tool-version migration, and rollback. Mac launcher
workflows with spaces in paths were verified. Fresh standalone Python 3.11
installation, execution of an external script, repeat installation, and a separate
Python 3.12 project were verified on 7 October 2026. Standalone customizations are
tested not to leak into generated projects, and version 1.1 installations can
receive the new installers through the updater. Windows scripts have been reviewed
but not executed on Windows; Intel Mac and Linux runtime checks remain pending.

## Maintaining the starter

Keep the reusable template in `templates/pixi.toml` Python-only; changes to the
standalone root manifest are separate from that template. When changing the Pixi release, update
`VERSION` in cosmos.sh, `$Version` in cosmos.ps1, and `requires-pixi` in both root and template pixi.toml files
together. Regenerate both lockfiles for any changed requirements. Bootstrap, update, and validate the resulting lockfile. Increment
`template-version.txt` for template releases, preserve metadata compatibility, and
follow [AGENTS.md](AGENTS.md) when changing the installer or updater.

Run checks from the cosmos-python directory:

```sh
bash cosmos.sh run python -m unittest discover -s tests -v
```

Upstream references: [Pixi installation](https://pixi.sh/latest/installation/),
[locked installation](https://pixi.sh/latest/reference/cli/pixi/install/), and
[dependency updates](https://pixi.sh/latest/reference/cli/pixi/update/).

Standalone Python was subsequently upgraded to 3.14.8 on 7 October 2026.
Locked installation and all 17 installer/updater tests passed on the development
Mac under Python 3.14. The separate project template now also defaults to Python 3.14. Existing project
environments keep their own Python version.
