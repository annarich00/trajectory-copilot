# Poliastro verification evidence

`contract-test-evidence.json` is retained machine-readable output from the host
comparison contract tests for circular short-duration, circular one-period, and
bounded eccentric SI inertial Cartesian cases. The test uses a deterministic
subprocess stand-in because this repository's core Python 3.14 environment must
not install the legacy Python 3.10-only Poliastro stack.

A real independent run requires a separately provisioned Python 3.10 environment
and `TRAJECTORY_COPILOT_POLIASTRO_PYTHON`; it will record raw adapter output in
`raw_adapter_response`, including the pinned release/commit. The stand-in output
is contract evidence, not a claim that Poliastro itself was executed here.
