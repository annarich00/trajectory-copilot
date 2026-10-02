# Baseline provenance

## Import origin

The baseline was recovered on 2026-10-01 from:

```text
/home/anna_ford/trajectory-copilot
```

That directory is not a Git repository and contains no revision identifier or remote URL. Its latest source/test changes were dated 2026-10-01, immediately before the planning PDF was created. Its directory structure, module names, example names, skills, and reported six-test baseline match `Planning_Trajectory_Copilot.pdf`. For those reasons it was selected as the authoritative local baseline rather than recreated from the planning narrative.

A second directory, `/home/anna_ford/projects/trajectory-copilot`, was inspected. It contains generated GMAT scripts/outputs and a standalone test file but not the documented Python package, reference, skills, examples, or baseline tests. Those generated artifacts were not mixed into this baseline because GMAT integration is separately tracked by TJC-1.21.

## Imported artifacts

The import copied the following source artifacts while excluding virtual environments, pytest caches, and Python bytecode:

- `.pi/skills/`
- `skills/`
- `reference/`
- `src/`
- `tests/`
- `examples/`
- `evaluations/`
- `baseline_comparison.md`

`docs/baseline-checksums.md` records SHA-256 hashes of every imported file as it existed at the source location.

## Original environment and baseline result

The source's existing virtual environment reported:

```text
Python 3.12.14
numpy 2.5.3
pytest 9.1.1
```

Before import, the unsuppressed baseline command was:

```bash
cd /home/anna_ford/trajectory-copilot
.venv/bin/python -m pytest -q
```

Result:

```text
......                                                                   [100%]
6 passed in 0.52s
```

The clean-checkout setup and post-import test evidence are documented in the repository `README.md` and the TJC-1.1 implementation notes.
