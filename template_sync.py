"""Versioned, conflict-aware updates of COSMOS helper files (stdlib only)."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import tomllib
import uuid

STATE = '.cosmos-python.json'
HELPERS = ('bootstrap.sh', 'bootstrap.ps1', 'cosmos.sh', 'cosmos.ps1',
           'update.sh', 'update.ps1', 'activate.sh', 'activate.ps1')
# Keep the eight original helpers as the legacy adoption baseline.
INSTALLERS = ('install.sh', 'install.ps1')
MANAGED = (*HELPERS, *INSTALLERS, 'COSMOS-TOOLS.md')


def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def read(path):
    if path.is_symlink():
        raise ValueError(f'Refusing symlink: {path}')
    if path.exists() and not path.is_file():
        raise ValueError(f'Expected a regular file: {path}')
    return path.read_bytes() if path.exists() else None


def snapshot(source):
    files = {name: (source / name).read_bytes() for name in (*HELPERS, *INSTALLERS)}
    files['COSMOS-TOOLS.md'] = (source / 'templates/COSMOS-TOOLS.md').read_bytes()
    version = (source / 'template-version.txt').read_text().strip()
    constraint = tomllib.loads((source / 'templates/pixi.toml').read_text())['workspace']['requires-pixi']
    return files, version, constraint


def state_bytes(files, version, constraint):
    return (json.dumps({'schema': 1, 'template_version': version, 'requires_pixi': constraint,
                        'files': {name: digest(data) for name, data in files.items()}}, indent=2, sort_keys=True)+'\n').encode()


def read_state(content):
    state = json.loads(content)
    if state.get('schema') != 1 or not isinstance(state.get('files'), dict):
        raise ValueError('Unsupported COSMOS state format')
    if not isinstance(state.get('requires_pixi'), str):
        raise ValueError('Missing Pixi constraint in COSMOS state')
    for name, checksum in state['files'].items():
        if name not in MANAGED or (checksum is not None and not re.fullmatch('[0-9a-f]{64}', str(checksum))):
            raise ValueError('Invalid managed-file entry in COSMOS state')
    return state


def plan_update(source, target, adopt=False):
    if not target.is_dir() or target.resolve() == source.resolve():
        raise ValueError('Choose an existing target directory other than cosmos-python')
    incoming, version, constraint = snapshot(source)
    original_state = read(target / STATE)
    if original_state is None:
        if not adopt:
            raise ValueError('No COSMOS state file. For an older installation, use --adopt once.')
        # Never guess an old baseline for modified scripts.
        mismatches = [name for name in HELPERS if read(target / name) != incoming[name]]
        if mismatches:
            raise ValueError('Cannot adopt: helpers differ from this template or are absent: '+', '.join(mismatches)+
                             '. Register against the matching older cosmos-python checkout first.')
        old = {'files': {name: digest(read(target / name)) for name in HELPERS},
               'requires_pixi': constraint}
    else:
        old = read_state(original_state)
    changes = {}
    conflicts = []
    for name, new in incoming.items():
        current = read(target / name)
        base = old['files'].get(name)
        if current == new:
            continue
        if digest(current) != base:
            conflicts.append(name)
        else:
            changes[name] = (current, new)
    manifest = read(target / 'pixi.toml')
    if manifest is None:
        raise ValueError('Target pixi.toml is missing; this updater supports the COSMOS pixi.toml layout')
    target_constraint = tomllib.loads(manifest.decode())['workspace'].get('requires-pixi')
    if target_constraint != constraint:
        if target_constraint != old['requires_pixi']:
            conflicts.append('pixi.toml: locally customized requires-pixi')
        else:
            # Change only the tool requirement, preserving every project requirement.
            text = manifest.decode()
            lines = text.splitlines(keepends=True)
            in_workspace = False
            count = 0
            for i, line in enumerate(lines):
                if line.lstrip().startswith('['):
                    in_workspace = line.strip() == '[workspace]'
                if in_workspace and re.match(r'^\s*requires-pixi\s*=', line):
                    lines[i] = re.sub(r'([=]\s*)([\"\']).*?\2',
                                      lambda m: m[1]+json.dumps(constraint), line, count=1)
                    count += 1
            if count != 1:
                raise ValueError('Cannot safely update requires-pixi; edit it manually to '+constraint)
            updated = ''.join(lines).encode()
            if tomllib.loads(updated.decode())['workspace']['requires-pixi'] != constraint:
                raise ValueError('Could not update Pixi tool requirement safely')
            changes['pixi.toml'] = (manifest, updated)
    if conflicts:
        raise ValueError('Local changes conflict; no files updated: '+', '.join(conflicts)+
                         '. Compare with cosmos-python, reconcile the helpers, then retry.')
    new_state = state_bytes(incoming, version, constraint)
    if original_state != new_state:
        changes[STATE] = (original_state, new_state)
    return changes


def atomic_write(path, data, mode):
    descriptor, temporary = tempfile.mkstemp(prefix='.cosmos-write-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply_update(target, changes):
    if not changes:
        return None
    # Check the entire plan before any writes, including backup-directory links.
    for name, (before, _) in changes.items():
        if read(target / name) != before:
            raise ValueError(f'{name} changed since planning; retry')
    for path in [target / '.cache', target / '.cache/cosmos-python-updates']:
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError(f'Unsafe backup directory: {path}')
    backup = target / '.cache/cosmos-python-updates' / uuid.uuid4().hex
    backup.mkdir(parents=True)
    modes = {}
    for name, (before, _) in changes.items():
        modes[name] = (target/name).stat().st_mode & 0o777 if before is not None else (0o755 if name.endswith('.sh') else 0o644)
        if before is not None:
            (backup/name).write_bytes(before)
    (backup/'RESTORE.json').write_text(json.dumps({'created': [n for n, (b, _) in changes.items() if b is None],
                                                'modes': modes}, indent=2)+'\n')
    written = []
    try:
        for name, (before, after) in changes.items():
            if read(target/name) != before:
                raise ValueError(f'{name} changed during update')
            atomic_write(target/name, after, modes[name])
            written.append(name)
    except Exception:
        for name in reversed(written):
            before = changes[name][0]
            if before is None:
                (target/name).unlink()
            else:
                atomic_write(target/name, before, modes[name])
        raise
    return backup
