# Trajectory CoPilot

Trajectory CoPilot is a research prototype for translating natural-language orbital-operations requests into explicit trajectory problems, deterministic physics calculations, and independently checked operator-facing results.

The recovered baseline contains:

- Pi skills under `.pi/skills/`
- controlled physics material in `reference/SOURCE.md`
- CW, two-body, optimization, and verification modules in `src/`
- baseline tests in `tests/`
- representative YAML cases in `examples/`
- formalizer evaluation artifacts in `evaluations/`

## Recorded rendezvous demo

Open the [recorded rendezvous demo on GitHub Pages](https://annarich00.github.io/trajectory-copilot/) or, after cloning, open [`site/demo-visualization-pipeline.html`](site/demo-visualization-pipeline.html) directly. It replays three recorded rendezvous cases without a server or API key.

- **Demo A:** GMAT comparison is not verified (`NUMERICAL_DISAGREEMENT`).
- **Demo B:** GMAT comparison is verified at a 20 m position tolerance and 0.05 m/s velocity tolerance.
- **Demo C:** model selection is `UNSUPPORTED`, so it stops before a solve or GMAT verification.

## Reproducible setup

From a clean checkout on a system with Python 3.12 or newer:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

On Windows, replace `.venv/bin/python` with `.venv\\Scripts\\python.exe`.

The recovered baseline was originally exercised with Python 3.12.14, NumPy 2.5.3, and pytest 9.1.1. See `docs/baseline-provenance.md` for origin and baseline results.

This project intentionally uses plain `venv`/`pip` (not `uv`) for the core environment; see `docs/uv-adoption-decision.md` for the recorded decision and rationale, including why `uv` is used elsewhere in this repo for the isolated Poliastro verification environment only.
