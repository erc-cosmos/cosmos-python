# COSMOS Python

## Download

```sh
mkdir -p ~/github.com/erc-cosmos
git clone https://github.com/erc-cosmos/cosmos-python.git ~/github.com/erc-cosmos/cosmos-python
cd ~/github.com/erc-cosmos/cosmos-python
```

Follow either setup option below. These commands are for Mac/Linux; see the
[Windows instructions](GUIDE.md#windows-instructions) for PowerShell.

## Option 1: install Python 3.14 for standalone use

From the cosmos-python directory:

```sh
bash install.sh
source ./activate.sh
pixi run --locked python
```

To run a script instead of opening Python interactively:

```sh
pixi run --locked python /path/to/your_script.py
```

Repeat `source ./activate.sh` in each new terminal.

## Option 2: install Python for another repository

Clone or create the project directory first, then run:

```sh
bash ~/github.com/erc-cosmos/cosmos-python/setup-repo.sh /path/to/my-repo
cd /path/to/my-repo
source ./activate.sh
pixi run --locked python your_script.py
```

Replace the example paths with your own. Add `--python 3.12` to the setup command
if the project needs that Python version. Then add its packages as described below.

For a project already configured by a colleague, run `bash install.sh` inside
that project instead of running `setup-repo.sh` again.

## Add or change packages

From the standalone cosmos-python directory or your project directory:

```sh
bash cosmos.sh add
```

Enter the package name and exact version. Leave the source blank for conda-forge,
or enter `pypi` for a package unavailable there.

To change or remove requirements manually, edit `pixi.toml` and run:

```sh
bash update.sh
```

For shared projects, run the tests and commit `pixi.toml` and `pixi.lock` together.

## Get updates

For standalone use, run inside cosmos-python:

```sh
git pull --ff-only
bash install.sh
```

To update the setup tools in another repository:

```sh
git -C ~/github.com/erc-cosmos/cosmos-python pull --ff-only
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/my-repo --dry-run
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/my-repo --sync
```

For older installations without `.cosmos-python.json`, add `--adopt` to both
update commands. Run the project's tests and review the changes before committing.

## Ask an agent to configure a project

Use this prompt with an authorized agent, replacing the paths:

> Read `/path/to/cosmos-python/AGENTS.md` and use it to set up
> `/path/to/my-repo`. Add its dependencies and run its tests. Preserve existing
> work; do not commit or push.

See the [guide](GUIDE.md) for extra options, troubleshooting, and background.
