# COSMOS Python environments

A reusable Pixi starter for COSMOS projects. Each repository gets its own Python
and packages; collaborators reproduce that repository's saved environment.
No existing Python, Conda, or administrator access is required.

## Get cosmos-python

Clone the public repository before using the commands below:

```sh
mkdir -p ~/github.com/erc-cosmos
git clone https://github.com/erc-cosmos/cosmos-python.git ~/github.com/erc-cosmos/cosmos-python
```

For an existing clone, get published updates with:

```sh
git -C ~/github.com/erc-cosmos/cosmos-python pull --ff-only
```

The repository contains configuration and setup tools. Pixi itself, installed
Python environments, and downloaded caches are created locally and excluded
from Git.

## Quick start: add this to a repository

```sh
bash ~/github.com/erc-cosmos/cosmos-python/setup-repo.sh /path/to/my-repo
```

The target directory must already exist. See [automatic setup](#set-up-a-new-repository-automatically)
for Windows, Python version selection, preview mode, and private repositories.

## Quick start: update an existing installation

First obtain the newer `cosmos-python` files. Then preview and apply the update:

```sh
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh \
  ~/github.com/erc-cosmos/probabilistic-segmentation --dry-run

bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh \
  ~/github.com/erc-cosmos/probabilistic-segmentation --sync
```

`--sync` updates the helper scripts and installs the required Pixi and the project's
saved environment. It preserves the project's Python and package requirements.
`probabilistic-segmentation` is already registered; older installations without
`.cosmos-python.json` need `--adopt` once. New installations register automatically.

After updating, run the project's tests. For this repository:

```sh
cd ~/github.com/erc-cosmos/probabilistic-segmentation
source ./activate.sh
pixi run --locked test
```

Review and commit the changed helper files and `.cosmos-python.json` when ready.
See [the full update instructions](#update-repositories-when-cosmos-python-changes)
for Windows, multiple repositories, conflicts, and recovery.

## First use

Open a terminal in this directory (or the repository that receives this starter).

Mac or Linux:

```sh
bash bootstrap.sh
bash cosmos.sh setup
bash cosmos.sh run python --version
bash cosmos.sh run python your_script.py
```

Windows (PowerShell, x64):

```powershell
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 setup
powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 run python --version
powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 run python your_script.py
```

The execution-policy option applies to that process only. Organisation policy may
still prohibit scripts; ask your IT team if so. Windows ARM is not included.
Both Apple Silicon and Intel Macs, plus Linux x64, are included in the lockfile.

Bootstrap downloads the official, versioned Pixi installer and installs Pixi 0.81.0
inside `.tools/` in this project. It does not change your system Python or shell
profile. It is safe to rerun. Downloads require internet access. Environment files
live in `.pixi/`; the package cache lives in `.cache/`. These are all ignored by Git.
This intentionally uses a local Pixi copy per repository for a self-contained setup.

`setup` and `run` use the saved lockfile and refuse to silently change versions.
Run Python through the helper so you use this environment. Commands run from the
Pixi workspace root; use absolute paths for scripts or data outside it.

## Add or pin a package

Run `bash cosmos.sh add` on Mac/Linux, or
`powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 add` on Windows.

Answer three prompts: package name, exact version, and source. Leave the source
blank for conda-forge. For example, `numpy`, `1.26.4`, and a blank source pins NumPy
to that release. Use `pypi` only for packages unavailable from conda-forge. The
command edits the package list, resolves all supported platforms, and installs
the result. Run it again to change a pin. A missing or incompatible version gives
an error; choose a compatible version and retry. Review changes before sharing.

Alternatively, open `pixi.toml` in a text editor. Under `[dependencies]`, use one
line per package:

```toml
numpy = "==1.26.4"
pandas = "==2.2.3"
```

These are syntax examples, not recommendations for every project. Delete a line
to remove a package, or change its version. `python = "3.11.*"` permits Python
3.11 patch releases; the lockfile records the exact one. Use `"==3.11.14"` for
an exact Python requirement if the project needs it. A `"*"` package requirement
allows any version when updating, but the lockfile still fixes a specific build
for normal setup. Put PyPI-only packages under `[pypi-dependencies]`. Never put
the same package in both sections. Do not edit `pixi.lock` by hand.

## Apply edited requirements

Mac/Linux: `bash update.sh`

Windows: `powershell -ExecutionPolicy Bypass -File .\update.ps1`

This reconciles the entire environment with `pixi.toml`, updates `pixi.lock` as
needed, and installs locally. It preserves existing locked versions where
possible. It is the command to use after editing, adding, or removing requirements.

To deliberately refresh **all** dependencies to newer versions allowed by the
requirements, use `bash cosmos.sh upgrade` or
`powershell -ExecutionPolicy Bypass -File .\cosmos.ps1 upgrade`.
Exact pins remain fixed until you edit them. Updating dependencies is separate
from updating the Pixi tool itself.

After either operation, run the project's tests or representative analysis.
Commit **both `pixi.toml` and `pixi.lock`** together. Colleagues pull the changes
and run `setup`; they should not regenerate the lockfile merely to run the code.
If resolving or installing fails, do not publish that change as a working setup.
Restore both files from a known working Git revision and run `setup` to roll back.

## Set up a new repository automatically

Clone or create the target repository first. You can run these commands yourself
for a private repository without opening it in this chat.

### Mac/Linux

From any directory, run:

```sh
bash ~/github.com/erc-cosmos/cosmos-python/setup-repo.sh /path/to/my-repo
```

Quote paths containing spaces. The command installs the starter files, merges
ignore rules, installs project-local Pixi, and creates the Python environment.
It bootstraps its own Python if needed; no preinstalled Python is required.
The workspace name is derived from the target directory name.

Then work in your repository:

```sh
cd /path/to/my-repo
source ./activate.sh
pixi run python --version
# After adding your project's packages:
pixi run python foo.py
pixi run pytest
```

To select a different Python minor version:

```sh
bash ~/github.com/erc-cosmos/cosmos-python/setup-repo.sh /path/to/my-repo --python 3.12
```

### Windows

Use PowerShell, adjusting the path to your local cosmos-python directory:

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\github.com\erc-cosmos\cosmos-python\setup-repo.ps1" -Repository "C:\work\my-repo"
cd C:\work\my-repo
. .\activate.ps1
pixi run python --version
```

Use `-PythonVersion 3.12` to choose another Python minor version. If policy blocks
activation, start an allowed PowerShell session, for example
`powershell -ExecutionPolicy Bypass`, then dot-source `activate.ps1`. Organisation
policy still applies. Both Windows scripts and setup instructions are supplied;
Windows runtime validation is pending.

### Preview and file-only setup

Add `--dry-run` (Windows: `-DryRun`) to list the planned files without changing the
target. Add `--files-only` (Windows: `-FilesOnly`) to create the files but defer
downloading and installing the target environment. In that case, later run
bootstrap and update from the target directory.

The launchers may bootstrap cosmos-python's own tool and Python even for these
modes. If you already have Python 3.11+, you can avoid all launcher bootstrapping:

```sh
python3 ~/github.com/erc-cosmos/cosmos-python/setup_repo.py /path/to/my-repo --dry-run
```

The Python script's `--dry-run` and `--files-only` modes perform no downloads.

### What is installed and preserved

The installer adds `pixi.toml`, the bootstrap/update/command/activation scripts,
and `PYTHON-ENVIRONMENT.md` to the target. It also adds `COSMOS-TOOLS.md` and
`.cosmos-python.json` for future template updates. For the default Python 3.11, it also
copies the starter lockfile. For another Python version, it generates a fresh
lockfile during installation. Existing README and package metadata remain intact;
`.gitignore` gets only missing local-file rules appended.

It refuses existing setup filenames, `.tools/`, `.pixi/`, or Pixi configuration in
`pyproject.toml` before changing anything. Running it twice therefore stops rather
than overwriting your customized environment. Use `setup` or `update` for an
already configured repository. If installation fails after files are created,
fix the reported issue and run bootstrap followed by update in the target;
those files are preserved so you can troubleshoot.

This is a **Python-only starter**, not automatic dependency discovery. Edit the
new `pixi.toml` or run `cosmos.sh add` / `cosmos.ps1 add` to add the project's
requirements. Then run update, validate the project's code, and commit the
configuration and lockfile together. Existing requirements files are not imported.
For installable Python projects, consider an editable local dependency under
`[pypi-dependencies]`, using the actual project name:
`your-package = { path = ".", editable = true }`.

Each repository has its own environment and can use a different Python version.
No repository is cloned, committed, or pushed by this installer. Private code
stays local; tool and dependency downloads still use GitHub/package servers.

### Native Pixi commands

`source ./activate.sh` (Windows: `. .\activate.ps1`) makes this project's Pixi
available in the current terminal, without editing your shell profile. Repeat
activation in new terminals. Run commands from the target repository.
Use `pixi run python foo.py` or `pixi run pytest` after installing the required
packages. Standard `pixi run` can update a stale lockfile; use
`pixi run --locked python foo.py` / `pixi run --locked pytest` for strict
reproduction. The existing cosmos run helpers always use locked mode.

## Why Pixi and what is reproducible

Pixi manages Python itself, Python packages, and native tools with a multi-platform
lockfile. A quick inspection found SciPy/pandas requirements in `prob-seg` and
native build tools (`cmake`) in `cosmodoit`, so it is a suitable starting point.
`uv` is also a good option for a purely Python project, but Pixi fits the mixed
scientific-tooling requirements here. This was a preliminary inspection, not a
compatibility audit of all repositories.

The lockfile records platform-specific packages and builds. It does not promise
identical floating-point results across operating systems, CPUs, or GPUs. Record
data versions, random seeds, external programs and drivers as needed for research.
A successful cross-platform solve does not prove the application runs on Windows;
validate representative code on each supported platform before claiming support.

To change the Pixi release, update `VERSION` in `cosmos.sh`, `$Version` in
`cosmos.ps1`, and `requires-pixi` in `pixi.toml` together, then rerun bootstrap,
update, and the project checks.

References: [installation](https://pixi.sh/latest/installation/),
[locked installation](https://pixi.sh/latest/reference/cli/pixi/install/),
[updating dependencies](https://pixi.sh/latest/reference/cli/pixi/update/).

## Validation of this starter

Verified on the development Mac: bootstrap and repeat bootstrap, locked setup,
Python execution, interactive PyPI pinning, version changes, package removal, and
rejection of a stale lockfile without modifying it. Generated the lockfile for all
four declared platforms. Windows PowerShell scripts were reviewed but have not
been executed on Windows; Intel Mac and Linux runtime checks also remain pending.

Repository installer verification: seven filesystem tests passed, covering conflict
protection, preservation of existing files, ignore merging, custom Python handling,
and rollback after a creation conflict. A complete installation into a temporary
path containing spaces passed on this Mac, including preview mode, a relative
target path, and native locked Pixi execution after both bash and zsh activation.
PowerShell runtime validation remains pending.

To run the installer checks with the starter environment:

```sh
bash cosmos.sh run python -m unittest discover -s tests -v
```

## Ask an agent to configure another repository

[AGENTS.md](AGENTS.md) provides the complete workflow, including discovering the
project's dependencies, configuring Python, installing, testing, and documenting
limitations. Use the conventional filename `AGENTS.md` so agents can discover it.
When working from another repository, explicitly reference this file because
instructions in a sibling directory may not be loaded automatically.

Example prompt (replace both paths):

> Read `/path/to/cosmos-python/AGENTS.md` and follow it to set up COSMOS Python in
> `/path/to/my-repo`. Discover and add this project's actual dependencies, generate
> the lockfile, and run its available tests. Preserve existing work. Keep all
> changes local; do not commit or push.

For private repositories, give this prompt only to an agent/environment authorized
to access that code. Alternatively, follow the local terminal instructions above
without involving an agent.

## Update repositories when cosmos-python changes

The starter now includes a built-in template updater; no Cookiecutter or extra
Python package is needed. New installations record template version 1.1.0 and
helper-file checksums in `.cosmos-python.json`. Commit that metadata with the
setup scripts. Content checksums detect changes even if a release number was not
bumped, but maintainers should increment `template-version.txt` for releases.

First obtain the updated, trusted cosmos-python files (for a Git checkout, pull
its published changes). Then explicitly update the repositories you choose:

```sh
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/repo --dry-run
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/repo --sync
```

Supply several paths to update a batch, including paths with spaces:

```sh
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh \
  /path/to/repo-one "/path/to/repo two" --sync
```

Windows, in a PowerShell session that permits the scripts:

```powershell
& "$HOME\github.com\erc-cosmos\cosmos-python\update-repos.ps1" -Repositories @('C:\work\repo-one', 'C:\work\repo two') -DryRun
& "$HOME\github.com\erc-cosmos\cosmos-python\update-repos.ps1" -Repositories @('C:\work\repo-one', 'C:\work\repo two') -Sync
```

The launcher uses cosmos-python's own Python 3.11 runtime. With an existing Python
3.11+ you can run `python3 /path/to/cosmos-python/update_repos.py ...` directly;
that avoids launcher bootstrapping and requires no downloads for the update itself.
Relative paths are resolved from your terminal's current directory.

### Register installations made before update tracking

Run the same command once with `--adopt` (Windows: `-Adopt`):

```sh
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/old-repo --adopt --dry-run
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/old-repo --adopt --sync
```

Adoption verifies all eight existing helper scripts exactly match this template
before recording their baseline. It preserves the project's manifest, lockfile,
and custom environment documentation. If helpers differ, it stops: register using
the matching older starter with update-tracking support first, or carefully
reconcile your scripts with the current template. Do not fabricate checksums or
use adoption to overwrite local changes. New installations need no adoption.

### What gets updated

The managed files are bootstrap.sh/.ps1, cosmos.sh/.ps1, update.sh/.ps1,
activate.sh/.ps1, and COSMOS-TOOLS.md. `.cosmos-python.json` records the new baseline.
`PYTHON-ENVIRONMENT.md`, README, dependencies, Python version, tasks, platform list,
lockfile, and ignore rules remain project-owned. Updates do not import new defaults
from the generic manifest. The only manifest change allowed is migrating
`workspace.requires-pixi` to match a newer bootstrap, if it still matches the
previously recorded value. Complex/manual version-constraint changes stop for review.

A locally edited or deleted managed file is a conflict. The updater reports the
files and changes nothing in that batch. Compare them with the trusted starter,
reconcile intentionally, then retry; no automatic merge markers are inserted.
Keep project-specific instructions in PYTHON-ENVIRONMENT.md and avoid customizing
managed scripts when a manifest setting or Pixi task can express the change.

Updates make backups in each target's `.cache/cosmos-python-updates/<id>/`,
including the previous metadata. The command prints the location. To undo, restore
the backed-up files to the target root and remove files listed under `created` in
RESTORE.json; do not copy RESTORE.json itself. File writes are atomic individually
and ordinary write failures restore already changed files in that repository.
A crash/power loss can require restoring the backup manually. Batch conflicts
prevent all writes; an I/O failure in a later repository does not undo earlier
successful repositories, which are reported as updated.

### Apply the updated tools to each machine

To update helpers and apply the saved environments in one command, add `--sync`
(Windows: `-Sync`):

```sh
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/repo --sync
```

This runs bootstrap and locked setup in each target after updating its helpers.
It also works for an already-current target. Downloads may be needed. If installation
fails, file changes remain; fix the reported issue and rerun `--sync`. With
`--dry-run`, no installation is performed.

If you omitted `--sync`, run bootstrap and setup manually in each target:

```sh
bash bootstrap.sh
bash cosmos.sh setup
source ./activate.sh
pixi run --locked test  # if this project defines a test task
```

With `--sync`, bootstrap and setup have already run; activate and run the tests.
Windows: without `-Sync`, run bootstrap.ps1, then cosmos.ps1 setup; in either case,
run the project's test command.
Bootstrap installs the template's Pixi version and locked setup recreates the
saved environment. Review the diff and commit the helper changes and metadata;
collaborators pull and run bootstrap/setup. If a newer tool cannot read the saved
lockfile, report the error and perform an explicit, reviewed lock migration.

Updating the template does **not** upgrade research dependencies. To change Python
or library versions, edit that repository's requirements, run update.sh/.ps1, and
validate/commit the new lockfile separately. No automatic background jobs, Git
pulls, commits, pushes, or scanning of other repositories happen. Only explicitly
supplied paths are processed. Existing arbitrary Python/venv installations that
were not set up with COSMOS are not managed by this tool.
