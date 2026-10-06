# Poliastro verification architecture

## Decision

Trajectory CoPilot will keep its current deterministic solver in `src/twobody.py` small and dependency-light. A separately managed Poliastro process will act as an external reference implementation for supported two-body propagation cases. Poliastro is a verifier, not the production solver, and it does not authorize expanding the semester dynamics scope.

GMAT remains the required independent end-to-end verifier for the semester workflow, including numerical propagation and a returned trajectory screenshot. Poliastro adds a code-level two-body cross-check before or alongside GMAT; it does not replace GMAT.

## Upstream provenance and maintenance risk

The integration must pin the released Poliastro 0.17.0 source commit:

```text
repository: https://github.com/poliastro/poliastro
release: v0.17.0
commit: c7d12e9b715d3fd60f2be233af707d5b97617d39
license: MIT
```

Evidence consulted on 2026-10-06:

- GitHub repository metadata reports `archived: true`, MIT licensing, default branch `main`, and last source push on 2023-10-14: <https://api.github.com/repos/poliastro/poliastro>
- The immutable v0.17.0 `pyproject.toml` requires Python `>=3.8,<3.11` and declares Astropy `>=5.0,<6` plus NumPy, SciPy, Numba, Astroquery, Plotly, Pandas, and other dependencies: <https://raw.githubusercontent.com/poliastro/poliastro/c7d12e9b715d3fd60f2be233af707d5b97617d39/pyproject.toml>
- The release implementation exposes scalar time propagation through `Orbit.propagate(...)`: <https://raw.githubusercontent.com/poliastro/poliastro/c7d12e9b715d3fd60f2be233af707d5b97617d39/src/poliastro/twobody/orbit/scalar.py>

The core project currently uses a newer Python runtime, so Poliastro 0.17.0 must not be installed into `.venv` or added to `requirements-dev.txt`. Because the repository is archived and its dependency stack is legacy, the pinned environment is a reproducibility boundary, not a promise of ongoing upstream maintenance or universal correctness.

## Isolated execution boundary

TJC-1.7 will implement an optional verifier environment with these properties:

1. A dedicated Python 3.10 environment, separate from `.venv`, is created reproducibly (the installed `uv` tool may manage the interpreter).
2. A committed lock or fully pinned verification requirements file resolves Poliastro from immutable commit `c7d12e9b715d3fd60f2be233af707d5b97617d39` and records transitive versions.
3. Core modules, especially `src/twobody.py`, never import Poliastro or Astropy.
4. The main process calls a small verifier entry point in the isolated environment through a JSON stdin/stdout subprocess contract. Environment setup may require network access; a configured verification run must not silently download or update packages.
5. Missing interpreter, environment, package, or subprocess output returns `UNAVAILABLE`, never `PASS`.

This boundary prevents legacy Poliastro dependencies from constraining the production solver and makes the external implementation/version visible in every result.

## Verification request contract

A request must contain:

- schema version and case identifier;
- initial Cartesian position `[x, y, z]` in metres;
- initial Cartesian velocity `[vx, vy, vz]` in metres per second;
- positive gravitational parameter `mu` in m³/s² and central-body identifier;
- explicit inertial frame identifier and frame assumptions;
- epoch when the chosen Poliastro API requires or reports one;
- propagation duration in seconds;
- requested Poliastro propagator/method, fixed by verifier configuration rather than LLM invention;
- position and velocity tolerances with provenance/rationale.

The adapter performs explicit SI-to-Astropy-unit conversion. It constructs the equivalent Poliastro orbit, propagates the same physical duration under the same point-mass assumptions, converts the final vectors back to SI, and emits machine-readable JSON.

## Verification result contract

A result records:

- `PASS`, `WARNING`, `FAIL`, `UNSUPPORTED`, or `UNAVAILABLE`;
- candidate and Poliastro final Cartesian states in SI;
- component differences and Euclidean position/velocity errors;
- applied tolerances and whether each was satisfied;
- frame, central body, `mu`, epoch, duration, and method;
- Poliastro release, immutable commit, Python version, dependency-lock identifier, command exit status, and captured diagnostics;
- limitations and recommended next action.

`PASS` requires successful independent execution and both errors within declared tolerances. A process error, malformed output, unit/frame mismatch, unsupported dynamics, or absent environment cannot pass. Disagreement must remain visible for investigation; the adapter must not tune tolerances or alter initial conditions to force agreement.

## Initial verification cases

TJC-1.7 should cover the current point-mass implementation rather than add dynamics:

- circular LEO propagation over a short interval;
- circular LEO propagation over one orbital period;
- a bounded eccentric elliptic case supported by both implementations;
- zero-duration identity if both APIs define it consistently;
- deliberate candidate perturbation to prove the comparison fails;
- unavailable-environment and unsupported-frame/model outcomes.

The suite should separately retain analytical invariant checks for energy and angular momentum. Agreement with Poliastro is useful independent-implementation evidence, but shared assumptions or shared defects remain possible.

## Policy for future astrodynamics work

Every future deterministic astrodynamics capability must declare whether the pinned Poliastro version supports the same model, frame, inputs, and outputs:

- If supported, add a versioned Poliastro adapter case and verification evidence before presenting the result as verified.
- If only partially supported, report the exact overlapping comparison and return `WARNING` or `UNSUPPORTED` for the remainder.
- If unsupported, return `UNSUPPORTED` and require another named independent verifier; do not stretch Poliastro beyond its API or claim universal coverage.
- GMAT verification requirements remain in force for the semester end-to-end workflow.

This policy means “rely on Poliastro” means use it whenever it provides a like-for-like independent implementation—not treat an archived library as an oracle for every future orbital model.

## Implemented adapter and reproducibility procedure

The executable boundary is `verification/poliastro/adapter.py`; its host API is
`src/poliastro_verify.py::verify_against_poliastro`. Both use schema version `1.0`.
The host accepts `TwoBodyCase` SI Cartesian inputs, obtains the candidate from
`src/twobody.py`, sends JSON on stdin, and retains the parsed raw adapter JSON in
`raw_adapter_response`. The adapter converts metres, metres/second, and seconds
explicitly to Astropy quantities and returns SI values.

Provisioning is deliberately explicit and never occurs during a verification run:

```bash
uv venv --python 3.10 .poliastro-venv
uv pip install --python .poliastro-venv/bin/python -r verification/poliastro/requirements.lock
export TRAJECTORY_COPILOT_POLIASTRO_PYTHON="$PWD/.poliastro-venv/bin/python"
PYTHONPATH=. .venv/bin/pytest -q tests/test_poliastro_verify.py
```

`verification/poliastro/provenance.json` and the requirements file identify the
immutable release source. The core `.venv` and `requirements-dev.txt` remain free
of Poliastro and Astropy. A missing executable, import failure, malformed output,
or subprocess failure returns `UNAVAILABLE`; an unsupported frame/model returns
`UNSUPPORTED`; neither can pass. A deliberately perturbed candidate is retained
as `FAIL` rather than normalized.

The currently retained contract evidence is `evidence/poliastro/contract-test-evidence.json`.
It is generated with a deterministic subprocess stand-in so CI can test the
boundary without putting Poliastro in the core environment. It is not a claim of
a live Poliastro run. A provisioned external run is required for final independent
numerical evidence. GMAT is still separately required for end-to-end numerical
and visual verification.

### Recorded live external run (2026-10-06)

A disposable `/tmp/tjc-poliastro-venv` was provisioned with `uv venv --python
3.10` and the locked source requirement. Initial resolution selected NumPy 2.2.6,
which caused the archived adapter import error `module 'numpy' has no attribute
'product'`; the lock therefore constrains `numpy<2`, and the isolated environment
was reinstalled with NumPy 1.26.4. The three live pinned comparisons then passed:

| Case | Position error [m] | Velocity error [m/s] |
| --- | ---: | ---: |
| circular short (600 s) | 1.30e-08 | 4.07e-12 |
| circular one period | 9.70e-05 | 1.10e-07 |
| bounded eccentric (900 s) | 1.63e-08 | 3.00e-11 |

The declared 0.05 m and 5e-5 m/s tolerances are conservatively above those
measured RK4 differences. Complete raw versioned results, requests, candidate and
Poliastro states, and adapter provenance are retained in
`evidence/poliastro/live-poliastro-evidence.json`.
