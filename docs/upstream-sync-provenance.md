# TJC-1.24 upstream synchronization provenance

- **Upstream:** `/home/anna_ford/trajectory-copilot/`
- **Synchronization timestamp:** 2026-10-02 UTC
- **Comparison command:** `python3 tools/compare_upstream.py --upstream /home/anna_ford/trajectory-copilot --check`
- **Compared content:** recursively discovered maintained regular files in both workspaces, hashed with SHA-256.
- **Excluded:** `.git`, `.venv`, `.pytest_cache`, `__pycache__`, `node_modules`, Python bytecode, coverage output, editor swap/temp files, and process output (`nohup.out`). Credentials and secrets are never accepted sync inputs.

## Reconciliation

Execution-time pre-import comparison found 64 upstream and 57 local maintained files. There were 43 upstream-only files: executable `run_site.sh` and the complete 42-file `site/` tree. All were deliberately imported. There were no content-different shared files. The comparison found 36 local-only files; all were retained as repository-specific setup/planning/provenance: `.gitignore`, `AGENTS.md`, `README.md`, `requirements-dev.txt`, the complete `backlog/` tree, and existing `docs/` records. No upstream deletion was mirrored. A local `pytest.ini` was then added with only `testpaths = tests`; this prevents pytest from executing verbatim display mirrors under `site/data/tests/` and preserves `tests/` as the sole authoritative test suite.

After import, `site/js/pages/project-map.js` is the sole accepted content difference: a minimal TJC-1.24 progress/provenance entry was added to satisfy this task while explicitly delegating broad roadmap alignment to TJC-1.25. `tools/compare_upstream.py` and this report are protected local-only synchronization records.

Shared authoritative source, tests, skills, examples, evaluations, `baseline_comparison.md`, and `reference/SOURCE.md` remain byte-identical to upstream. The `site/data/` source/reference copies were imported verbatim. The site labels these as authoritative-file display mirrors and labels `site/js/physics.js` as pedagogical, non-authoritative JavaScript.

## Verification evidence

- `.venv/bin/python -m pytest -q` and explicit `.venv/bin/python -m pytest -q tests`: passed with the same 6-test count.
- Comparison check: 63 shared checksum matches, no upstream-only files, one documented post-import edit, no unaccounted difference.
- `./run_site.sh`: served on `127.0.0.1:4173` using Node built-ins, with no npm install or internet assets.
- HTTP smoke checks returned 200 for the index, CSS, JavaScript, representative source/reference/data, and representative hash-route assets; route modules and index route registration were also checked.
- `git diff --check`, generated-artifact scan, and credential/secret scan passed.

## Limitation and follow-up

The recovered site's pre-existing broader roadmap statements may be stale relative to the Backlog plan. TJC-1.24 does not redesign them; TJC-1.25 owns comprehensive roadmap and living-progress alignment.
