#!/usr/bin/env python3
"""Thin CLI bridge between the ``run_gmat_verification`` pi tool (TJC-12) and
the already-audited GMAT execution/parsing/comparison pipeline.

This script performs NO GMAT script generation, execution, parsing, or
comparison logic of its own. It only:

1. reads one structured case (the same fields
   ``src/workflow.py::RendezvousCase``'s CW path requires -- case identity,
   physical state, and tolerances) as JSON from stdin or ``--case-json``;
2. reshapes that case into the exact dict shape
   ``scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification``
   already accepts (the same reusable core ``src/workflow.py::_run_cw_path``
   calls); and
3. prints the resulting ``UnifiedVerificationReport.to_dict()`` (plus the
   enclosing ``run_cw_rendezvous_gmat_verification`` result dict) as one
   JSON object to stdout, unmodified -- the PASS/WARNING/FAIL/INCOMPLETE
   comparison status and MISSING_GMAT/EXECUTION_ERROR/MALFORMED_OUTPUT/
   NUMERICAL_DISAGREEMENT/SCREENSHOT_FAILURE/CW_TARGETING_INFEASIBLE
   failure_mode vocabulary pass through exactly as
   ``src/verification_report.py``/``src/gmat_verify.py`` already define
   them. ``verified``/``failure_mode`` are never recomputed, reinterpreted,
   or overridden here.

This is the Python-side half of the ``.pi/extensions/gmat-verification-tool``
pi extension (TJC-12): the TypeScript tool's ``execute()`` shells out to this
script via ``pi.exec`` and relays its stdout JSON verbatim as the tool
result, rather than reimplementing or forking any GMAT logic in TypeScript.

Required input JSON fields (mirrors ``src/workflow.py::RendezvousCase``'s
CW-path fields exactly):

- ``case_id`` (str)
- ``mu_m3_s2`` (float)
- ``reference_radius_m`` (float)
- ``initial_relative_state`` (6 floats, LVLH ``[x, y, z, x_dot, y_dot, z_dot]``)
- ``transfer_time_s`` (float)

Optional input JSON fields (defaults mirror ``RendezvousCase``'s own
defaults):

- ``final_relative_state`` (6 floats, default ``[0, 0, 0, 0, 0, 0]``)
- ``pos_tol_m`` (float, default ``1.0``)
- ``vel_tol_mps`` (float, default ``0.001``)
- ``dv_tol_mps`` (float, default ``0.001``)
- ``output_dir`` (str, default a fresh temp directory)
- ``gmat_executable`` (str, default ``"GmatConsole-R2026a"``)
- ``gmat_gui_executable`` (str, default ``"GMAT-R2026a"``)
- ``attempt_gui_screenshot`` (bool, default ``false`` -- off by default here
  because a real GUI capture is slow/environment-dependent; opt in
  explicitly when a reachable display is actually wanted)

Usage::

    echo '{"case_id": "...", "mu_m3_s2": ..., ...}' | \\
        .venv/bin/python scripts/gmat_tool_bridge.py

    .venv/bin/python scripts/gmat_tool_bridge.py --case-json '{"case_id": ...}'
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.run_cw_gmat_slice as slice_runner  # noqa: E402

REQUIRED_FIELDS = ("case_id", "mu_m3_s2", "reference_radius_m", "initial_relative_state", "transfer_time_s")


class BridgeInputError(ValueError):
    """Raised when the structured case JSON is missing a required field or malformed.

    Kept distinct from any GMAT failure mode (``MISSING_GMAT``,
    ``EXECUTION_ERROR``, etc.): this is a tool-input validation error, caught
    by ``main()`` and reported as ``{"error": "..."}`` on stdout with a
    nonzero exit status, never silently treated as a GMAT outcome.
    """


def build_slice_case(structured_case: dict) -> dict:
    """Reshape the tool's structured case into ``run_cw_rendezvous_gmat_verification``'s
    expected dict shape (the same shape ``src/workflow.py::_run_cw_path`` builds).
    """
    missing = [field for field in REQUIRED_FIELDS if field not in structured_case]
    if missing:
        raise BridgeInputError(f"missing required field(s): {missing}")

    initial_relative_state = structured_case["initial_relative_state"]
    if not isinstance(initial_relative_state, (list, tuple)) or len(initial_relative_state) != 6:
        raise BridgeInputError("initial_relative_state must be an array of exactly 6 numbers")

    final_relative_state = structured_case.get("final_relative_state", [0.0] * 6)
    if not isinstance(final_relative_state, (list, tuple)) or len(final_relative_state) != 6:
        raise BridgeInputError("final_relative_state must be an array of exactly 6 numbers")

    return {
        "case_id": structured_case["case_id"],
        "input_path": f"run_gmat_verification tool (case_id={structured_case['case_id']!r})",
        "mu": structured_case["mu_m3_s2"],
        "radius_m": structured_case["reference_radius_m"],
        "state0": list(initial_relative_state),
        "target": list(final_relative_state),
        "transfer_s": structured_case["transfer_time_s"],
        "pos_tol": structured_case.get("pos_tol_m", 1.0),
        "vel_tol": structured_case.get("vel_tol_mps", 0.001),
        "dv_tol": structured_case.get("dv_tol_mps", 0.001),
    }


def run_bridge(structured_case: dict) -> dict:
    """Run one complete CW-to-GMAT verification for ``structured_case`` and
    return the exact result dict ``run_cw_rendezvous_gmat_verification``
    produces (including ``unified_verification_report``), unmodified.
    """
    slice_case = build_slice_case(structured_case)

    output_dir = structured_case.get("output_dir")
    if output_dir is None:
        # mkdtemp (not TemporaryDirectory) deliberately leaves this directory
        # on disk after the call returns: the result dict's artifact paths
        # (generated script, ReportFile output, screenshot) must stay valid
        # for the caller to inspect afterwards, exactly as
        # run_cw_gmat_slice.py's own output_dir convention leaves its
        # artifacts in place rather than deleting them on completion.
        output_dir = tempfile.mkdtemp(prefix="gmat_tool_bridge_")
    output_dir = Path(output_dir)

    gmat_executable = structured_case.get("gmat_executable", "GmatConsole-R2026a")
    gmat_gui_executable = structured_case.get("gmat_gui_executable", "GMAT-R2026a")
    attempt_gui_screenshot = bool(structured_case.get("attempt_gui_screenshot", False))

    result, _returncode = slice_runner.run_cw_rendezvous_gmat_verification(
        slice_case,
        output_dir,
        gmat_executable=gmat_executable,
        gmat_gui_executable=gmat_gui_executable,
        skip_gui_screenshot=not attempt_gui_screenshot,
        timeout_s=float(structured_case.get("timeout_s", 180.0)),
    )
    result["output_dir"] = str(output_dir)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case-json", default=None,
        help="structured case JSON (if omitted, read from stdin)",
    )
    args = parser.parse_args(argv)

    raw = args.case_json if args.case_json is not None else sys.stdin.read()
    try:
        structured_case = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"invalid JSON input: {exc}"}))
        return 2

    try:
        result = run_bridge(structured_case)
    except BridgeInputError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    print(json.dumps(result))
    return 0 if result.get("verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
