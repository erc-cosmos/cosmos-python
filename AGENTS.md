# Agent instructions: set up COSMOS Python in another repository

This directory provides both a standalone Python distribution and a reusable
project environment installer. For standalone use, run install.sh / install.ps1
in this clone, activate, and use `pixi run --locked python`. A target repository
is needed only when the user wants to set up a separate project environment.
When asked to set it up in another repository, complete dependency discovery,
installation, and validation; copying the Python-only starter is not completion.
Read this README and the target's applicable agent instructions before editing.
For a separate project, use the target path provided by the user; ask if missing.
Do not ask for a target when the user requests standalone installation.
Do not assume the target needs probabilistic-segmentation's dependencies.

## Scope and existing work

- Inspect the target's version-control status and relevant configuration first.
  Preserve unrelated changes, existing documentation, IDE settings, data, and secrets.
- Work only in repositories the user has authorized. If they want a private repo
  kept out of the chat, provide local instructions instead of reading its contents.
- Setup is local. Do not create a remote repository, commit, push, publish packages,
  or send code elsewhere unless the user requests it.
- Use the available filesystem/network permission mechanism if access is needed.
- This AGENTS.md belongs to the starter. Do not copy it over the target's own
  agent instructions. Add any useful target-specific notes without overwriting them.

## 1. Discover actual requirements

Inspect README/setup instructions, pyproject.toml, requirements files, environment
files, CI configuration, test configuration, source imports, and notebook imports.
Distinguish standard-library imports and local modules from external packages.
Check import-to-package name differences (for example sklearn/scikit-learn).

Identify:

- Supported Python versions and the intended operating systems.
- Runtime libraries and required native tools.
- Testing tools and plugins (for example pytest-xdist for pytest's `-n` option).
- Notebook dependencies if notebooks are an intended use case.
- Optional development tools and genuinely optional integrations.
- External datasets, credentials, services, drivers, and machine-specific paths.

Choose a compatible Python version based on this evidence. Do not automatically
use the newest release. Explain restrictive version ranges; preserve known-working
constraints and use the lockfile to record exact direct and indirect versions.
Do not interpret a `python>=...` line in requirements.txt as a PyPI package.

## 2. Install or adapt the starter

For an unconfigured target, use the installer in this directory. From any working
directory on Mac/Linux (replace the absolute paths):

```sh
bash /path/to/cosmos-python/setup-repo.sh /path/to/target --dry-run
bash /path/to/cosmos-python/setup-repo.sh /path/to/target --python 3.11 --files-only
```

On Windows:

```powershell
powershell -ExecutionPolicy Bypass -File C:\path\cosmos-python\setup-repo.ps1 -Repository C:\path\target -DryRun
powershell -ExecutionPolicy Bypass -File C:\path\cosmos-python\setup-repo.ps1 -Repository C:\path\target -PythonVersion 3.11 -FilesOnly
```

`--files-only` lets you add the actual dependencies before downloading the target's
Python environment. The launchers may first bootstrap their own Python runtime.
With an existing Python 3.11+ runtime, setup_repo.py can be invoked directly.

If the target already has starter files or Pixi configuration, inspect and adapt
that configuration in place. The installer intentionally refuses overwrites.
Never delete an existing environment/configuration just to bypass that check.
Do not replace an existing pyproject.toml with a generic template.

## 3. Configure dependencies and usable commands

- Edit the target's pixi.toml (or existing Pixi configuration in pyproject.toml).
  Prefer conda-forge for Python and native scientific dependencies; use
  pypi-dependencies for packages unavailable there. Avoid duplicate packages across
  package managers. Do not copy another project's package list without evidence.
- For installable Python projects, prefer an editable local package dependency
  where appropriate so its declared dependencies remain authoritative.
- If an unpackaged project's scripts need the repository root on the import path,
  configure `PYTHONPATH = "$PIXI_PROJECT_ROOT"` under `[activation.env]`.
- Keep writable plotting/cache directories local when required, e.g.
  `MPLCONFIGDIR = "$PIXI_PROJECT_ROOT/.cache/matplotlib"` and
  `XDG_CACHE_HOME = "$PIXI_PROJECT_ROOT/.cache"` under `[activation.env]`.
- Define a `test` task with explicit paths when generic pytest discovery would
  collect notebooks or unrelated scripts. If data-dependent tests cannot run,
  provide clearly documented `test` and `test-all` tasks. Do not silently skip
  failures or change assertions to manufacture passing tests.
- Support native commands after `source ./activate.sh` or `. .\activate.ps1`:
  `pixi run python foo.py`, `pixi run pytest`, and/or `pixi run test`.
  Pixi requires `run`. Use `--locked` in reproducibility checks; bare `pixi run`
  may regenerate a stale lockfile. Do not create a custom command named pixi.
- Preserve the installer-generated ignore rules for .tools/, .pixi/, and .cache/.
  Do not distribute installed environments or caches.

## 4. Resolve, install, and validate

In the target, run bootstrap and update. Mac/Linux:

```sh
bash bootstrap.sh
bash update.sh
bash cosmos.sh setup
source ./activate.sh
pixi run --locked python --version
pixi run --locked test
```

Use the equivalent .ps1 scripts on Windows. If a shell has PIXI_LOCKED or
PIXI_FROZEN set, clear those variables for the intentional update step only.
Resolve for the declared platforms; if a required package cannot support one,
investigate and document the limitation rather than silently dropping that platform.

Run imports of the main dependencies, the meaningful existing tests, and a small
representative execution using synthetic data where possible. Avoid executing
notebooks that perform external writes or require undisclosed private inputs.
Report observed failures and warnings accurately. Investigate whether failures
come from missing dependencies, existing code bugs, missing data, or platform
limits. Keep unrelated algorithm refactoring outside environment setup.

Verify that locked setup and execution work after the final dependency change.
A multi-platform lockfile is not proof of successful runtime testing on every OS.
Do not claim unavailable tests passed. Where feasible, record the exact checks,
pass counts, exclusions, and outstanding platform validation in target documentation.

## 5. Document and hand over

Update the target's PYTHON-ENVIRONMENT.md with project-specific package choices,
setup/activation/run/test commands, dependency update instructions, and external
requirements. Add a short link from its existing README where appropriate.
Explain which dependency files are authoritative; avoid two independently edited
lists, while preserving packaging metadata and existing workflows deliberately.

Deliver the manifest and generated lockfile together. Tell the user that maintainers
update and validate them together, while collaborators run setup from the saved
lockfile. Report files changed, checks passed, known limitations, and whether any
remote publication happened. The default is local changes only.

## Maintaining cosmos-python itself

Keep the reusable template (`templates/pixi.toml` and `templates/pixi.lock`)
Python-only. Root manifest/lockfile customization belongs to the standalone
environment and must not leak into generated projects. Project-specific packages
belong in the target. The tooling runtime in cosmos-python must stay Python 3.11+. Keep Mac/Linux and Windows launchers aligned, preserve overwrite protection,
and update README and templates/PYTHON-ENVIRONMENT.md for workflow changes.
The bootstrap Pixi version and both root/template requires-pixi constraints must
agree. Update the corresponding lockfile whenever either manifest changes.
Run relevant checks after installer changes:

```sh
bash cosmos.sh run python -m unittest discover -s tests -v
```

For installer changes, also test an end-to-end setup in a disposable directory
with a space in its path, plus preview/no-overwrite behaviour. Never use an existing
research checkout as a destructive test fixture. State if Windows was not tested.

## Updating an existing installation from a newer starter

Use update-repos.sh / update-repos.ps1, first with preview mode. Supply only target
paths authorized by the user; do not scan private repositories or set up background
jobs. New setups include `.cosmos-python.json`; commit it with the managed helpers.
For older installations, use --adopt / -Adopt only when their helper scripts match
the baseline. Inspect conflicts rather than deleting metadata or overwriting scripts.

Template updates preserve project requirements and lockfiles; only the recorded
Pixi tool constraint may migrate automatically. Do not substitute the starter's
Python version or dependencies into an established research environment. After
updating, run bootstrap and locked setup, then relevant tests. Report backups,
conflicts, and any untested platforms. Template publication and Git commits/pushes
still require the user's request. See GUIDE.md for batch and recovery behaviour.

When changing managed files, increment template-version.txt, keep metadata schema
compatibility, and run both installer and update tests. Test preservation of
project files, conflict refusal, legacy adoption, and tool-version migration.
COSMOS-TOOLS.md is centrally managed; PYTHON-ENVIRONMENT.md is project-owned.
