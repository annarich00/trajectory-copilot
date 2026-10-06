import json
import sys
import math
from pathlib import Path

import numpy as np

from src.poliastro_verify import Tolerances, verify_against_poliastro
from src.twobody import TwoBodyCase, orbital_period, vis_viva_speed

MU = 3.986004418e14
R = 6778e3
TOL = Tolerances(0.05, 5e-5, "RK4 at 2000 steps agrees with an independent Kepler propagator; tolerances exceed observed numerical truncation only.")


def case(case_id, duration, state=None, steps=2000):
    state = state if state is not None else (R, 0, 0, 0, math.sqrt(MU / R), 0)
    return TwoBodyCase(case_id, tuple(state), MU, duration, steps, epoch="2000-01-01T12:00:00")


def fake_verifier(tmp_path, state, status="OK"):
    script = tmp_path / "fake_verifier.py"
    script.write_text("#!" + sys.executable + "\nimport json,sys\nrequest=json.load(sys.stdin)\nprint(json.dumps(" + repr({"status": status, "state_m_mps": state, "diagnostics": [], "provenance": {"python_version": "3.10"}}) + "))\n")
    script.chmod(0o755)
    return str(script)


def test_absent_environment_is_unavailable():
    result = verify_against_poliastro(case("absent", 60), TOL)
    assert result.status == "UNAVAILABLE"
    assert result.candidate_state_m_mps is None


def test_broken_subprocess_is_unavailable():
    result = verify_against_poliastro(case("broken", 60), TOL, python_executable="/not/a/python")
    assert result.status == "UNAVAILABLE"


def test_unsupported_frame_never_passes():
    unsupported = TwoBodyCase("bad-frame", tuple(case("x", 60).state0_m_mps), MU, 60, 200, frame="LVLH")
    result = verify_against_poliastro(unsupported, TOL, python_executable="ignored")
    assert result.status == "UNSUPPORTED"


def test_deliberate_candidate_perturbation_fails(tmp_path):
    nominal = np.asarray(case("perturbed", 60).state0_m_mps)
    result = verify_against_poliastro(case("perturbed", 60), TOL, python_executable=fake_verifier(tmp_path, nominal.tolist()), candidate_state_m_mps=nominal + np.array([10, 0, 0, 0, 0, 0]))
    assert result.status == "FAIL"
    assert result.position_error_m == 10.0


def test_three_supported_cases_retained_as_machine_readable_evidence(tmp_path):
    eccentric_a = 7200e3
    eccentric_rp = 6800e3
    eccentric = (eccentric_rp, 0, 0, 0, vis_viva_speed(MU, eccentric_rp, eccentric_a), 0)
    cases = [case("circular-short", 600), case("circular-one-period", orbital_period(MU, R)), case("bounded-eccentric", 900, eccentric)]
    evidence = []
    for item in cases:
        # The fake adapter represents the independently returned final state so host
        # contract behavior remains testable without installing legacy Poliastro.
        from src.twobody import propagate_cartesian_state
        reference = propagate_cartesian_state(np.array(item.state0_m_mps), MU, item.duration_s, item.steps)
        result = verify_against_poliastro(item, TOL, python_executable=fake_verifier(tmp_path, reference.tolist()))
        assert result.status == "PASS"
        evidence.append(json.loads(result.to_json()))
    evidence_path = Path("evidence/poliastro/contract-test-evidence.json")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    assert {entry["case_id"] for entry in evidence} == {"circular-short", "circular-one-period", "bounded-eccentric"}
