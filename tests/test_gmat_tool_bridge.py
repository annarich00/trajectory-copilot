"""Tests for the ``run_gmat_verification`` pi tool's Python bridge script (TJC-12).

``scripts/gmat_tool_bridge.py`` is the thin CLI layer the
``.pi/extensions/gmat-verification-tool`` pi extension shells out to: it
reshapes the tool's structured JSON input into
``scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification``'s
existing dict shape and relays its result (including the
``UnifiedVerificationReport.to_dict()`` shape) verbatim. These tests confirm
that reshaping/relaying is faithful -- not that GMAT verification itself
works differently here (that's already covered by
``tests/test_cw_gmat_slice.py``/``tests/test_workflow.py``).

Uses the same "definitely-not-gmat" stand-in executable pattern as
``tests/test_cw_gmat_slice.py::test_slice_reports_missing_gmat_without_false_verification``,
so no real GMAT installation is required.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gmat_tool_bridge import BridgeInputError, build_slice_case, run_bridge  # noqa: E402

CW_CASE = {
    "case_id": "bridge_test_case",
    "mu_m3_s2": 398600441800000.0,
    "reference_radius_m": 6728000.0,
    "initial_relative_state": [15.0, -200.0, 0.0, -0.14, 0.0, 0.0],
    "transfer_time_s": 1373.0298005070088,
    "pos_tol_m": 1.0,
    "vel_tol_mps": 0.001,
    "dv_tol_mps": 0.001,
    "gmat_executable": "definitely-not-gmat",
}


def test_build_slice_case_requires_structured_fields_not_free_text():
    """AC2: a case missing any required structured field is rejected explicitly,
    never silently coerced from free text."""
    incomplete = {"case_id": "x", "mu_m3_s2": 1.0}
    with pytest.raises(BridgeInputError, match="missing required field"):
        build_slice_case(incomplete)


def test_build_slice_case_reshapes_into_run_cw_gmat_slice_dict_shape():
    slice_case = build_slice_case(CW_CASE)
    assert slice_case["case_id"] == "bridge_test_case"
    assert slice_case["mu"] == CW_CASE["mu_m3_s2"]
    assert slice_case["radius_m"] == CW_CASE["reference_radius_m"]
    assert slice_case["state0"] == CW_CASE["initial_relative_state"]
    assert slice_case["target"] == [0.0] * 6  # defaulted, not supplied
    assert slice_case["transfer_s"] == CW_CASE["transfer_time_s"]
    assert slice_case["pos_tol"] == 1.0
    assert slice_case["vel_tol"] == 0.001
    assert slice_case["dv_tol"] == 0.001


def test_run_bridge_reports_missing_gmat_without_false_verification(tmp_path):
    """(AC3/AC6) Mirrors test_cw_gmat_slice.py's MISSING_GMAT case exactly: a
    stand-in GMAT executable produces a never-silently-passing result with
    the same failure_mode vocabulary, relayed verbatim by the bridge."""
    case = dict(CW_CASE, output_dir=str(tmp_path))
    result = run_bridge(case)
    assert result["verified"] is False
    assert result["failure_mode"] == "MISSING_GMAT"
    assert result["gmat"]["attempted"] is False
    assert "NOT VERIFIED" in result["verification_status"]
    unified = result["unified_verification_report"]
    assert unified["failure_mode"] == "MISSING_GMAT"
    assert unified["verified"] is False
    assert unified["comparison"]["status"] == "INCOMPLETE"
    assert (tmp_path / "generated_cw_rendezvous.script").stat().st_size > 0


def test_run_bridge_without_output_dir_still_leaves_inspectable_artifacts():
    """When the caller omits output_dir, the bridge creates one itself and
    reports it back, rather than silently discarding the generated script/
    screenshot artifacts a caller might want to inspect."""
    case = dict(CW_CASE)
    result = run_bridge(case)
    assert result["output_dir"]
    assert Path(result["output_dir"]).is_dir()
    assert Path(result["trajectory_artifact"]).is_file()


def test_cli_prints_unified_report_json_and_exits_nonzero_for_unverified(tmp_path):
    """End-to-end CLI invocation (as the TypeScript tool's ``pi.exec`` call
    will actually run it): JSON on stdin, JSON result on stdout, nonzero
    exit status for a NOT VERIFIED outcome -- never a false 0/PASS."""
    case = dict(CW_CASE, output_dir=str(tmp_path))
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gmat_tool_bridge.py")],
        input=json.dumps(case), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["failure_mode"] == "MISSING_GMAT"
    assert payload["verified"] is False


def test_cli_reports_invalid_json_input_as_explicit_error_not_a_crash():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gmat_tool_bridge.py")],
        input="not valid json", capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert "error" in payload
