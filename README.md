# Trajectory CoPilot

Trajectory CoPilot is a research prototype for translating natural-language orbital-operations requests into explicit trajectory problems, deterministic physics calculations, and independently checked operator-facing results.

The recovered baseline contains:

- Pi skills under `.pi/skills/`
- controlled physics material in `reference/SOURCE.md`
- CW, two-body, optimization, and verification modules in `src/`
- baseline tests in `tests/`
- representative YAML cases in `examples/`
- formalizer evaluation artifacts in `evaluations/`

## Reproducible setup

From a clean checkout on a system with Python 3.12 or newer:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

On Windows, replace `.venv/bin/python` with `.venv\\Scripts\\python.exe`.

The recovered baseline was originally exercised with Python 3.12.14, NumPy 2.5.3, and pytest 9.1.1. See `docs/baseline-provenance.md` for origin and baseline results.
