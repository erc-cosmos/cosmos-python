# COSMOS Python

## Get the setup tools

```sh
mkdir -p ~/github.com/erc-cosmos
git clone https://github.com/erc-cosmos/cosmos-python.git ~/github.com/erc-cosmos/cosmos-python
```

Use the commands below on Mac/Linux. For Windows, follow the
[PowerShell instructions](GUIDE.md#windows-instructions).

## Set up a repository

Clone or create your project directory first. Replace `/path/to/my-repo` with its
location, quoting paths that contain spaces.

```sh
bash ~/github.com/erc-cosmos/cosmos-python/setup-repo.sh /path/to/my-repo
```

To choose a Python version, add `--python 3.12`. To preview, add `--dry-run`.
Then [add the project's packages](#add-or-change-packages); the starter installs only Python.

## Run Python

From your project directory:

```sh
cd /path/to/my-repo
source ./activate.sh
pixi run --locked python your_script.py
```

Repeat activation in each new terminal. Replace `your_script.py` with your script.
To run tests, install pytest first and use your project's test command, for example:

```sh
pixi run --locked pytest tests
```

## Add or change packages

From your project directory, run:

```sh
bash cosmos.sh add
```

Enter the package name, exact version, and source. Leave the source blank for
conda-forge; use `pypi` for packages unavailable there.

Alternatively, edit `pixi.toml` to add, remove, or change packages, then apply it:

```sh
bash update.sh
```

Run your project's tests and commit **both `pixi.toml` and `pixi.lock`**.
Do not edit the lockfile by hand.

## Use an environment a colleague has already set up

Clone or pull the project, then run inside its directory:

```sh
bash bootstrap.sh
bash cosmos.sh setup
source ./activate.sh
pixi run --locked python your_script.py
```

## Update the setup tools in existing repositories

Get the latest tools, preview the changes, then apply them:

```sh
git -C ~/github.com/erc-cosmos/cosmos-python pull --ff-only
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/my-repo --dry-run
bash ~/github.com/erc-cosmos/cosmos-python/update-repos.sh /path/to/my-repo --sync
```

For an older installation without `.cosmos-python.json`, add `--adopt` to both
update commands. To update several repositories, list their paths before `--sync`.

Run each project's tests, review the changes, and commit the updated helpers and
`.cosmos-python.json`. If the updater reports a conflict, follow the
[recovery instructions](GUIDE.md#conflicts-and-recovery).

## Ask an agent to set up a repository

Give an authorized agent this prompt, replacing the paths:

> Read `/path/to/cosmos-python/AGENTS.md` and use it to set up
> `/path/to/my-repo`. Add the project's actual dependencies, generate its lockfile,
> and run the available tests. Preserve existing work. Do not commit or push.

For additional options, troubleshooting, and background, read the [guide](GUIDE.md).
