#!/usr/bin/env python3
"""Compare maintained files with the recovered upstream workspace."""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

EXCLUDED_PARTS = {'.git', '.venv', '.pytest_cache', '__pycache__', 'node_modules'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo', '.swp', '.tmp'}
EXCLUDED_NAMES = {'.coverage', 'nohup.out'}
PROTECTED_PREFIXES = ('backlog/', 'docs/', 'tools/')
PROTECTED_FILES = {'.gitignore', 'AGENTS.md', 'README.md', 'pytest.ini', 'requirements-dev.txt'}
POST_IMPORT_EDITS = {'site/js/pages/project-map.js'}

def manifest(root: Path) -> dict[str, str]:
    result = {}
    for path in root.rglob('*'):
        if not path.is_file(): continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in rel.parts): continue
        if path.suffix in EXCLUDED_SUFFIXES or path.name in EXCLUDED_NAMES: continue
        result[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--upstream', default='/home/anna_ford/trajectory-copilot')
    parser.add_argument('--check', action='store_true', help='fail for unaccounted upstream differences')
    args = parser.parse_args()
    upstream, local = manifest(Path(args.upstream)), manifest(Path.cwd())
    upstream_only = sorted(upstream.keys() - local.keys())
    different = sorted(p for p in upstream.keys() & local.keys() if upstream[p] != local[p])
    accepted_different = sorted(set(different) & POST_IMPORT_EDITS)
    unaccounted = sorted((set(upstream_only) | set(different)) - POST_IMPORT_EDITS)
    local_only = sorted(local.keys() - upstream.keys())
    protected = [p for p in local_only if p in PROTECTED_FILES or p.startswith(PROTECTED_PREFIXES)]
    other_local = sorted(set(local_only) - set(protected))
    shared = sorted(p for p in upstream.keys() & local.keys() if upstream[p] == local[p])
    print(f'upstream maintained: {len(upstream)}')
    print(f'local maintained: {len(local)}')
    print(f'shared checksum matches: {len(shared)}')
    print('upstream-only: ' + (', '.join(upstream_only) or 'none'))
    print('content-different accepted post-import edits: ' + (', '.join(accepted_different) or 'none'))
    print('content-different unaccounted: ' + (', '.join(unaccounted) or 'none'))
    print('protected local-only: ' + (', '.join(protected) or 'none'))
    print('other local-only: ' + (', '.join(other_local) or 'none'))
    print('excluded: .git, .venv, .pytest_cache, __pycache__, node_modules, bytecode, coverage, swap/temp/process artifacts')
    if args.check and unaccounted:
        return 1
    return 0
if __name__ == '__main__': raise SystemExit(main())
