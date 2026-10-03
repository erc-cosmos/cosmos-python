#!/usr/bin/env python3
"""Update COSMOS helper files in explicitly named repositories. Python 3.11+."""
import argparse
import os
import shutil
from pathlib import Path
import subprocess
import sys
from template_sync import plan_update, apply_update

SOURCE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repositories', nargs='+', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='Preview all changes without writing target files')
    parser.add_argument('--adopt', action='store_true', help='Register older installations with matching helper scripts')
    parser.add_argument('--sync', action='store_true', help='Also bootstrap Pixi and install each saved environment in locked mode')
    args = parser.parse_args()
    targets = list(dict.fromkeys(p.expanduser().resolve() for p in args.repositories))
    plans = []
    errors = []
    # Conflicts in any target prevent the whole batch from starting.
    for target in targets:
        try:
            changes = plan_update(SOURCE, target, args.adopt)
            plans.append((target, changes))
            print(f'{target}: '+(', '.join(changes) if changes else 'already current'))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'{target}: {exc}')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        print('No repositories updated.', file=sys.stderr)
        return 1
    if args.dry_run:
        print('Preview only; no target files changed.')
        return 0
    for target, changes in plans:
        try:
            backup = apply_update(target, changes)
            if backup:
                print(f'Updated {target}. Backup: {backup}')
            if args.sync:
                env = os.environ.copy()
                if os.name == 'nt':
                    shell = shutil.which('powershell') or shutil.which('pwsh')
                    if not shell:
                        raise ValueError('PowerShell not found')
                    prefix = [shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File']
                    commands = [prefix+[str(target/'bootstrap.ps1')], prefix+[str(target/'cosmos.ps1'), 'setup']]
                else:
                    commands = [['bash', str(target/'bootstrap.sh')], ['bash', str(target/'cosmos.sh'), 'setup']]
                for command in commands:
                    subprocess.run(command, cwd=target, env=env, check=True)
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            print(f'Update failed for {target}: {exc}. Files may already be updated. Fix the error and rerun with --sync; earlier targets may already be updated.', file=sys.stderr)
            return 1
    print('Helpers and saved environments are installed.' if args.sync else 'Helpers are current. In each target, run bootstrap then locked setup to apply them locally.')
    print('Dependencies and Python versions were not upgraded; review changes and run project tests.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
