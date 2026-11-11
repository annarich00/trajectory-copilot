"""Tests for the ``propagate_two_body_coast`` pi tool's Python bridge script
(TJC-23.5).

``scripts/two_body_tool_bridge.py`` is the thin CLI layer the
``.pi/extensions/two-body-rendezvous-tool`` pi extension shells out to: it
reshapes the tool's structured JSON input straight into
``src/twobody.py::propagate_cartesian_state``'s existing call signature and
relays the final SI inertial Cartesian state plus stable metadata. These
tests confirm that reshaping/relaying is faithful and that invalid inputs
are rejected explicitly, not improvised -- the propagation physics itself
is already covered by ``tests/test_twobody.py``.

Mirrors ``tests/test_gmat_tool_bridge.py``'s bridge-script test pattern.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.two_body_tool_bridge import BridgeInputError, run_bridge  # noqa: E402
from src.twobody import propagate_cartesian_state  # noqa: E402

MU_EARTH = 3.986004418e14
RADIUS_M = 6778e3
CIRCULAR_SPEED_MPS = math.sqrt(MU_EARTH / RADIUS_M)
CIRCULAR_STATE = [RADIUS_M, 0.0, 0.0, 0.0, CIRCULAR_SPEED_MPS, 0.0]

VALID_CASE = {
    "initial_state_m_mps": CIRCULAR_STATE,
    "mu_m3_s2": MU_EARTH,
    "duration_s": 60.0,
    "steps": 200,
    "epoch": "2026-01-01T00:00:00Z",
}


def test_run_bridge_matches_propagate_cartesian_state_directly():
    """A normal coast propagation through the bridge must match calling
    ``propagate_cartesian_state`` directly, with the stable metadata attached."""
    result = run_bridge(VALID_CASE)
    expected = propagate_cartesian_state(
        np.array(CIRCULAR_STATE), MU_EARTH, 60.0, steps=200,
    )
    np.testing.assert_allclose(result["final_state_m_mps"], expected, rtol=0, atol=1e-6)
    assert result["frame"] == "inertial-cartesian"
    assert result["central_body"] == "Earth"
    assert result["dynamics"] == "point-mass-two-body"
    assert result["integrator"] == "fixed-step-rk4"
    assert result["epoch"] == "2026-01-01T00:00:00Z"


def test_run_bridge_without_epoch_reports_none_not_a_missing_key():
    case = dict(VALID_CASE)
    del case["epoch"]
    result = run_bridge(case)
    assert result["epoch"] is None


def test_run_bridge_requires_structured_fields_not_free_text():
    incomplete = {"initial_state_m_mps": CIRCULAR_STATE, "mu_m3_s2": MU_EARTH}
    with pytest.raises(BridgeInputError, match="missing required field"):
        run_bridge(incomplete)


@pytest.mark.parametrize(
    ("case", "match"),
    [
        (dict(VALID_CASE, mu_m3_s2=0.0), "mu must be"),
        (dict(VALID_CASE, mu_m3_s2=-1.0), "mu must be"),
        (dict(VALID_CASE, steps=0), "steps must be"),
        (dict(VALID_CASE, duration_s=math.nan), "dt must be finite"),
        (dict(VALID_CASE, initial_state_m_mps=[0.0] * 6), "r0 must be nonzero"),
    ],
)
def test_run_bridge_rejects_invalid_inputs_without_improvising_a_result(case, match):
    """AC2: non-finite inputs, non-positive mu/steps, and the zero-radius
    singularity are rejected explicitly by propagating ``ValueError`` through,
    never silently coerced into a fabricated final state."""
    with pytest.raises(ValueError, match=match):
        run_bridge(case)


def test_cli_prints_result_json_and_exits_zero_for_a_valid_case():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "two_body_tool_bridge.py")],
        input=json.dumps(VALID_CASE), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert len(payload["final_state_m_mps"]) == 6
    assert payload["frame"] == "inertial-cartesian"


def test_cli_reports_rejected_invalid_input_as_explicit_error_not_a_crash():
    """The zero-radius singularity is reported as a structured error with a
    nonzero exit, not an uncaught traceback or a fabricated state."""
    case = dict(VALID_CASE, initial_state_m_mps=[0.0] * 6)
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "two_body_tool_bridge.py")],
        input=json.dumps(case), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert "error" in payload
    assert "nonzero" in payload["error"]


def test_cli_reports_invalid_json_input_as_explicit_error_not_a_crash():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "two_body_tool_bridge.py")],
        input="not valid json", capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert "error" in payload
