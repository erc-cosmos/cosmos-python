#!/usr/bin/env python3
"""Install the COSMOS starter in an existing local directory (Python 3.11+)."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
from template_sync import STATE, snapshot, state_bytes

SOURCE = Path(__file__).resolve().parent
COPY_FILES = (
    'bootstrap.sh', 'bootstrap.ps1', 'cosmos.sh', 'cosmos.ps1',
    'update.sh', 'update.ps1', 'activate.sh', 'activate.ps1',
)
IGNORE_LINES = ('.tools/', '.pixi/', '.cache/', '__pycache__/')


def plan(target, python_version):
    if not target.is_dir():
        raise ValueError('Target must be an existing directory. Clone or create it first.')
    if target == SOURCE:
        raise ValueError('Choose a target other than cosmos-python itself.')
    # Do all configuration checks before writing anything.
    reserved = (*COPY_FILES, 'pixi.toml', 'pixi.lock', 'PYTHON-ENVIRONMENT.md', 'COSMOS-TOOLS.md', STATE, '.pixi', '.tools')
    conflicts = [name for name in reserved if (target / name).exists() or (target / name).is_symlink()]
    if conflicts:
        raise ValueError('Existing setup files found; nothing changed: ' + ', '.join(conflicts))
    pyproject = target / 'pyproject.toml'
    if pyproject.exists():
        data = tomllib.loads(pyproject.read_text(encoding='utf-8'))
        if 'pixi' in data.get('tool', {}):
            raise ValueError('pyproject.toml already contains Pixi configuration; nothing changed.')
    ignore = target / '.gitignore'
    if ignore.is_symlink() or (ignore.exists() and not ignore.is_file()):
        raise ValueError('.gitignore must be a regular file, not a link or directory.')
    existing_ignore = ignore.read_bytes() if ignore.exists() else b''
    lines = existing_ignore.decode('utf-8').splitlines()
    missing = [line for line in IGNORE_LINES if line not in lines]
    suffix = b''
    if missing:
        prefix = b'\n' if existing_ignore and not existing_ignore.endswith(b'\n') else b''
        suffix = prefix + ('\n# COSMOS Python local files\n' + '\n'.join(missing) + '\n').encode()
    files = {name: (SOURCE / name).read_bytes() for name in COPY_FILES}
    name = re.sub(r'[^a-z0-9-]+', '-', target.name.lower()).strip('-') or 'cosmos-project'
    manifest = (SOURCE / 'pixi.toml').read_text(encoding='utf-8')
    manifest = manifest.replace('name = "cosmos-python"', f'name = "{name}"', 1)
    manifest = manifest.replace('python = "3.11.*"', f'python = "{python_version}.*"', 1)
    files['pixi.toml'] = manifest.encode()
    # Only carry over the generic lock if its Python requirement is unchanged.
    if python_version == '3.11':
        files['pixi.lock'] = (SOURCE / 'pixi.lock').read_bytes()
    files['PYTHON-ENVIRONMENT.md'] = (SOURCE / 'templates' / 'PYTHON-ENVIRONMENT.md').read_bytes()
    managed, version, constraint = snapshot(SOURCE)
    files['COSMOS-TOOLS.md'] = managed['COSMOS-TOOLS.md']
    files[STATE] = state_bytes(managed, version, constraint)
    return files, existing_ignore, suffix


def install_files(target, files, existing_ignore, suffix):
    written = []
    try:
        for name, content in files.items():
            path = target / name
            # Exclusive create: refuse to clobber even if a file appeared after preflight.
            with path.open('xb') as stream:
                written.append(path)
                stream.write(content)
            if name.endswith('.sh'):
                path.chmod(0o755)
        if suffix:
            ignore = target / '.gitignore'
            current = ignore.read_bytes() if ignore.exists() else b''
            if ignore.is_symlink() or current != existing_ignore:
                raise ValueError('.gitignore changed during setup; retry after reviewing it.')
            with ignore.open('ab') as stream:
                stream.write(suffix)
    except Exception:
        for path in reversed(written):
            path.unlink()
        raise


def install_environment(target):
    env = os.environ.copy()
    # The initial solve must not inherit a user's locked/frozen mode.
    env.pop('PIXI_LOCKED', None)
    env.pop('PIXI_FROZEN', None)
    if os.name == 'nt':
        shell = shutil.which('powershell') or shutil.which('pwsh')
        if not shell:
            raise ValueError('PowerShell not found. Files are ready; run bootstrap.ps1 and update.ps1 manually.')
        prefix = [shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File']
        commands = [prefix + [str(target / name)] for name in ('bootstrap.ps1', 'update.ps1')]
    else:
        commands = [['bash', str(target / name)] for name in ('bootstrap.sh', 'update.sh')]
    for command in commands:
        subprocess.run(command, cwd=target, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path, help='Existing local repository directory')
    parser.add_argument('--python', default='3.11', dest='python_version', metavar='3.MINOR',
                        help='Python minor version, e.g. 3.11 or 3.12 (default: 3.11)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without changing the target')
    parser.add_argument('--files-only', action='store_true', help='Write files without downloading/installing the target environment')
    args = parser.parse_args()
    if not re.fullmatch(r'3\.(?:[9]|[1-9][0-9])', args.python_version):
        parser.error('--python must be a Python 3 minor version >= 3.9, such as 3.11')
    target = args.repository.expanduser().resolve()
    try:
        files, existing_ignore, suffix = plan(target, args.python_version)
        print(f'Target: {target}', flush=True)
        for name in files:
            print(f'  Create {name}', flush=True)
        if suffix:
            print('  Append local-file rules to .gitignore', flush=True)
        if args.dry_run:
            print('Preview only: target unchanged.')
            return 0
        install_files(target, files, existing_ignore, suffix)
        if not args.files_only:
            try:
                install_environment(target)
            except (subprocess.CalledProcessError, OSError, ValueError) as exc:
                print(f'Files created, but installation failed: {exc}\n'
                      'Fix the reported issue, then run bootstrap and update in the target.\n'
                      'Do not rerun setup-repo: it will protect the files already created.', file=sys.stderr)
                return 1
        print('Starter ready. See PYTHON-ENVIRONMENT.md in the target repository.')
        print('This starts with Python only. Add this project\'s requirements and run its tests.')
        return 0
    except (OSError, ValueError) as exc:
        print(f'Setup stopped: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
