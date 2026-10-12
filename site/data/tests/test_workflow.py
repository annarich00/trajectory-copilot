"""Tests for the connected rendezvous workflow entry point (TJC-1.16).

Covers every required distinct outcome in TJC-1.16's acceptance criteria:
happy-path VERIFIED (AC1), a needs-clarification short-circuit with no
physics/model-selection/GMAT execution (AC2), a CW-invalid case routed to
the bounded two-body fallback that still receives GMAT verification (AC3),
and NUMERICAL_DISAGREEMENT / missing-GMAT / GMAT execution error / malformed
GMAT output / screenshot failure / unsupported / out-of-scope as distinct,
clearly labeled non-authoritative outcomes (AC4). AC5's required record
fields (facts, assumptions, model-selection reasoning, tool inputs/outputs,
tolerances, artifact paths, trust statement) are asserted on the returned
``WorkflowResult``/``to_dict()`` shape directly.

Uses the same stand-in/monkeypatch patterns as
``tests/test_cw_gmat_slice.py``/``tests/test_model_selector.py``: a
"definitely-not-gmat" executable name for MISSING_GMAT, and monkeypatched
``check_gmat_available``/``run_gmat_script`` stand-ins for the other GMAT
outcomes, so no real GMAT installation is required.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.run_cw_gmat_slice as slice_runner  # noqa: E402
from src import gmat_verify, workflow  # noqa: E402
from src.cw import mean_motion  # noqa: E402
from src.model_selector import ModelSelectionCase  # noqa: E402
from src.workflow import RendezvousCase, run_rendezvous_workflow  # noqa: E402

MU_EARTH = 398600441800000.0
LEO_RADIUS_M = 6728000.0


def _cw_ready_case(case_id: str = "test_cw_case") -> RendezvousCase:
    """A fully-supported, READY_TO_SOLVE CW case matching the proven quarter-period benchmark."""
    n = mean_motion(MU_EARTH, LEO_RADIUS_M)
    period = 2 * math.pi / n
    transfer_s = 0.25 * period
    model_case = ModelSelectionCase(
        circularity="supported",
        frame="supported",
        other_physics="supported",
        maneuver_assumptions="supported",
        reference_radius_m=LEO_RADIUS_M,
        relative_separation_m=200.0,
        transfer_time_s=transfer_s,
        mean_motion_rad_s=n,
    )
    return RendezvousCase(
        case_id=case_id,
        readiness="READY_TO_SOLVE",
        model_selection_case=model_case,
        mu_m3_s2=MU_EARTH,
        reference_radius_m=LEO_RADIUS_M,
        initial_relative_state=[15.0, -200.0, 0.0, -0.14, 0.0, 0.0],
        final_relative_state=[0.0] * 6,
        transfer_time_s=transfer_s,
        pos_tol_m=1.0,
        vel_tol_mps=0.001,
        dv_tol_mps=0.001,
    )


def _two_body_ready_case(case_id: str = "test_two_body_case") -> RendezvousCase:
    """A clearly CW-invalid, bounded-two-body-fallback case (large GEO-scale separation)."""
    leo_radius_m = 6778000.0
    offset_m = 1_000_000.0
    duration_s = 900.0
    from src.twobody import vis_viva_speed

    chaser_radius_m = leo_radius_m + offset_m
    chaser_speed = vis_viva_speed(MU_EARTH, chaser_radius_m, chaser_radius_m)
    state0 = [chaser_radius_m, 0.0, 0.0, 0.0, chaser_speed, 0.0]
    model_case = ModelSelectionCase(
        circularity="supported",
        frame="supported",
        other_physics="violated",
        maneuver_assumptions="supported",
        reference_radius_m=leo_radius_m,
        relative_separation_m=offset_m,
        transfer_time_s=duration_s,
        mean_motion_rad_s=mean_motion(MU_EARTH, leo_radius_m),
        inertial_cartesian_state=state0,
        mu_m3_s2=MU_EARTH,
        coast_duration_s=duration_s,
        rk4_steps=2000,
    )
    return RendezvousCase(
        case_id=case_id,
        readiness="READY_TO_SOLVE",
        model_selection_case=model_case,
        inertial_cartesian_state=state0,
        mu_m3_s2=MU_EARTH,
        coast_duration_s=duration_s,
        rk4_steps=2000,
    )


def _unsupported_ready_case(case_id: str = "test_unsupported_case") -> RendezvousCase:
    """A READY_TO_SOLVE case whose assumptions select UNSUPPORTED (fits neither contract)."""
    n = mean_motion(MU_EARTH, LEO_RADIUS_M)
    model_case = ModelSelectionCase(
        circularity="supported",
        frame="supported",
        other_physics="supported",
        maneuver_assumptions="supported",
        locality="violated",
        reference_radius_m=LEO_RADIUS_M,
        relative_separation_m=200.0,
        transfer_time_s=100.0,
        mean_motion_rad_s=n,
        is_coast_only_request=False,  # fails the bounded two-body coast contract too
    )
    return RendezvousCase(case_id=case_id, readiness="READY_TO_SOLVE", model_selection_case=model_case)


def _singular_infeasible_ready_case(case_id: str = "test_singular_infeasible_case") -> RendezvousCase:
    """A READY_TO_SOLVE, model-selector-qualified CW case whose fixed transfer
    time (n*t = 2*pi) makes Phi_rv exactly singular and the requested terminal
    position unreachable (``src.cw.two_burn_targeting`` status
    "singular-infeasible"), matching ``test_cw.py::
    test_solve_cw_rendezvous_singular_infeasible_boundary_fails_explicitly``'s
    case but driven through the full connected workflow rather than
    ``solve_cw_rendezvous`` directly."""
    n = 0.001
    reference_radius_m = (MU_EARTH / n**2) ** (1.0 / 3.0)
    t_final = 2 * math.pi / n
    initial_relative_state = [0.0] * 6
    final_relative_state = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    model_case = ModelSelectionCase(
        circularity="supported",
        frame="supported",
        other_physics="supported",
        maneuver_assumptions="supported",
        reference_radius_m=reference_radius_m,
        relative_separation_m=1.0,
        transfer_time_s=t_final,
        mean_motion_rad_s=n,
        initial_relative_state=initial_relative_state,
        final_relative_state=final_relative_state,
    )
    return RendezvousCase(
        case_id=case_id,
        readiness="READY_TO_SOLVE",
        model_selection_case=model_case,
        mu_m3_s2=MU_EARTH,
        reference_radius_m=reference_radius_m,
        initial_relative_state=initial_relative_state,
        final_relative_state=final_relative_state,
        transfer_time_s=t_final,
    )


# ---------------------------------------------------------------------------
# AC1: fully supported request traverses the entire pipeline and returns
# VERIFIED or an explicit NOT VERIFIED reason -- never silently a pass.
# ---------------------------------------------------------------------------


def test_happy_path_cw_case_without_gmat_is_not_verified_with_explicit_reason(tmp_path):
    """No GMAT installed in this environment: MISSING_GMAT, not a false pass."""
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.readiness == "READY_TO_SOLVE"
    assert result.verified is False
    assert result.outcome == "MISSING_GMAT"
    assert "NOT VERIFIED" in result.verification_status
    assert result.model_selection.selection == "CW rendezvous"
    assert (tmp_path / "generated_cw_rendezvous.script").is_file()
    assert "solver succeeded" in result.trust_statement
    data = result.to_dict()
    assert data["unified_verification_report"] is not None
    assert data["artifacts"]["generated_script"].endswith("generated_cw_rendezvous.script")


def test_happy_path_cw_case_with_fake_gmat_run_is_verified(tmp_path, monkeypatch):
    """A fully supported CW case traverses formalization-readiness -> model selection ->
    deterministic solution -> GMAT verification -> screenshot artifact -> explanation and
    returns a genuine VERIFIED outcome, matching the already-proven CW/GMAT slice case."""
    monkeypatch.setattr(
        slice_runner, "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(True, "/stand-in/gmat", "GMAT stand-in", "ok"),
    )

    def fake_run(executable, script_path, timeout_s=180.0):
        output_dir = script_path.parent
        for key in ("init", "postburn1"):
            (output_dir / f"d_{key}.txt").write_text(
                "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n0 0 0 0 0 0 0\n"
            )
        (output_dir / "d_trajectory.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "0 1.5e-05 -2e-04 0 -1.4e-04 0 0\n1373.0298005070088 0 0 0 0 0 0\n"
        )
        (output_dir / "d_final.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "1373.0298005070088 0 0 0 0 0 0\n"
        )
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    monkeypatch.setattr(slice_runner, "run_gmat_script", fake_run)
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.verified is True
    assert result.outcome == "VERIFIED"
    assert result.verification_status == "VERIFIED"
    assert "independently verified" in result.trust_statement
    data = result.to_dict()
    assert data["unified_verification_report"]["comparison"]["status"] == "PASS"
    assert data["artifacts"]["trajectory_screenshot"].endswith("trajectory.svg")
    assert Path(data["artifacts"]["trajectory_screenshot"]).is_file()


# ---------------------------------------------------------------------------
# AC2: an ambiguous/needs-clarification case stops BEFORE any physics/
# model-selection/GMAT execution and returns focused clarification
# questions, never a fabricated solve.
# ---------------------------------------------------------------------------


def test_needs_clarification_short_circuits_before_any_physics_or_model_selection(tmp_path, monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("physics/model-selection must not run for a NEEDS_CLARIFICATION case")

    monkeypatch.setattr(workflow, "select_model", _fail)
    monkeypatch.setattr(slice_runner, "solve_cw_rendezvous", _fail)
    monkeypatch.setattr(slice_runner, "check_gmat_available", _fail)
    monkeypatch.setattr(workflow, "check_gmat_available", _fail)
    monkeypatch.setattr(workflow, "propagate_cartesian_state", _fail)

    case = RendezvousCase(
        case_id="ambiguous_case",
        readiness="NEEDS_CLARIFICATION",
        clarification_questions=(
            "Which central body is the reference orbit around?",
            "What is the complete initial relative position and velocity?",
        ),
    )
    result = run_rendezvous_workflow(case, output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.readiness == "NEEDS_CLARIFICATION"
    assert result.outcome == "NEEDS_CLARIFICATION"
    assert result.verified is False
    assert result.model_selection is None
    assert result.verification_report is None
    assert len(result.clarification_questions) == 2
    assert "Which central body" in result.clarification_questions[0]
    assert not any(tmp_path.iterdir())  # no GMAT script, no screenshot: nothing was executed


def test_out_of_scope_short_circuits_before_any_physics_or_model_selection(tmp_path, monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("physics/model-selection must not run for an OUT_OF_SCOPE case")

    monkeypatch.setattr(workflow, "select_model", _fail)
    monkeypatch.setattr(slice_runner, "solve_cw_rendezvous", _fail)

    case = RendezvousCase(
        case_id="geo_phasing_case", readiness="OUT_OF_SCOPE",
        out_of_scope_reason="GEO phasing maneuver with three spacecraft is outside the two-spacecraft, "
        "circular-LEO, impulsive LVLH rendezvous class.",
    )
    result = run_rendezvous_workflow(case, output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.readiness == "OUT_OF_SCOPE"
    assert result.outcome == "OUT_OF_SCOPE"
    assert result.verified is False
    assert "OUT_OF_SCOPE" in result.verification_status
    assert "GEO phasing" in result.trust_statement
    assert not any(tmp_path.iterdir())


# ---------------------------------------------------------------------------
# AC3: a CW-invalid (but otherwise supported) case routes to the two-body
# fallback and that fallback still receives GMAT verification, not a skip.
# ---------------------------------------------------------------------------


def test_cw_invalid_case_routes_to_two_body_fallback_with_gmat_verification_attempted(tmp_path):
    """GMAT verification is genuinely attempted for the two-body path (a generated script and
    screenshot are produced, and GMAT availability is actually checked), not silently skipped,
    even though no real GMAT is installed here (MISSING_GMAT, not a false pass)."""
    result = run_rendezvous_workflow(_two_body_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.model_selection.selection == "bounded two-body fallback"
    assert result.model_selection.deterministic_tool == "src.twobody.propagate_cartesian_state"
    assert result.outcome == "MISSING_GMAT"
    assert result.verified is False
    data = result.to_dict()
    assert data["artifacts"]["generated_script"].endswith("generated_two_body_coast.script")
    assert Path(data["artifacts"]["generated_script"]).is_file()
    assert data["unified_verification_report"]["solver"]["name"] == "point-mass-two-body-fixed-step-rk4-coast"


def test_cw_invalid_case_two_body_fallback_verified_with_fake_gmat_run(tmp_path, monkeypatch):
    """With a real (stand-in) GMAT run that matches the two-body propagation, the fallback
    reaches a genuine VERIFIED outcome, proving GMAT verification is a real step, not a skip."""
    monkeypatch.setattr(
        workflow, "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(True, "/stand-in/gmat", "GMAT stand-in", "ok"),
    )

    case = _two_body_ready_case()
    state0 = np.asarray(case.inertial_cartesian_state, dtype=float)
    from src.twobody import propagate_cartesian_state

    final_state = propagate_cartesian_state(state0, case.mu_m3_s2, case.coast_duration_s, steps=case.rk4_steps)

    def fake_run(executable, script_path, timeout_s=180.0):
        output_dir = script_path.parent
        x_km, y_km, z_km = (final_state[:3] / 1000.0).tolist()
        vx, vy, vz = (final_state[3:] / 1000.0).tolist()
        header = "ElapsedSecs EarthMJ2000Eq.X EarthMJ2000Eq.Y EarthMJ2000Eq.Z EarthMJ2000Eq.VX EarthMJ2000Eq.VY EarthMJ2000Eq.VZ\n"
        row = f"{case.coast_duration_s} {x_km} {y_km} {z_km} {vx} {vy} {vz}\n"
        (output_dir / "d_final.txt").write_text(header + row)
        (output_dir / "d_trajectory.txt").write_text(header + f"0 {x_km} {y_km} {z_km} {vx} {vy} {vz}\n" + row)
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    monkeypatch.setattr(workflow, "run_gmat_script", fake_run)
    result = run_rendezvous_workflow(case, output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.model_selection.selection == "bounded two-body fallback"
    assert result.verified is True
    assert result.outcome == "VERIFIED"
    assert "independently verified" in result.trust_statement


# ---------------------------------------------------------------------------
# AC4: NUMERICAL_DISAGREEMENT, missing/invalid screenshot, GMAT execution
# failure (missing GMAT / nonzero exit / malformed output), and an
# unsupported/out-of-scope request each produce distinct, clearly labeled
# non-authoritative outcomes.
# ---------------------------------------------------------------------------


def test_numerical_disagreement_is_distinct_outcome(tmp_path, monkeypatch):
    monkeypatch.setattr(
        slice_runner, "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(True, "/stand-in/gmat", "GMAT stand-in", "ok"),
    )

    def fake_run(executable, script_path, timeout_s=180.0):
        output_dir = script_path.parent
        for key in ("init", "postburn1"):
            (output_dir / f"d_{key}.txt").write_text(
                "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n0 0 0 0 0 0 0\n"
            )
        (output_dir / "d_trajectory.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "0 0 0 0 0 0 0\n1373.0298005070088 0 0 0 0 0 0\n"
        )
        # Perturb the final state far beyond the configured tolerances.
        (output_dir / "d_final.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "1373.0298005070088 500.0 0.0 0.0 0.0 0.0 0.0\n"
        )
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    monkeypatch.setattr(slice_runner, "run_gmat_script", fake_run)
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.verified is False
    assert result.outcome == "NUMERICAL_DISAGREEMENT"
    assert "NUMERICAL_DISAGREEMENT" in result.verification_status


def test_missing_gmat_is_distinct_outcome(tmp_path):
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.outcome == "MISSING_GMAT"
    assert result.verified is False


def test_singular_infeasible_cw_targeting_is_distinct_outcome_before_any_gmat_call(tmp_path, monkeypatch):
    """A model-selector-qualified CW case (AC2's singular-targeting routing) whose
    fixed transfer time makes the CW boundary condition itself unreachable fails
    as CW_TARGETING_INFEASIBLE before any GMAT availability check, script, or
    screenshot is produced -- distinct from MISSING_GMAT/NUMERICAL_DISAGREEMENT,
    which both require a solver success first."""
    def _fail(*args, **kwargs):
        raise AssertionError("GMAT must not be invoked when CW targeting itself is infeasible")

    monkeypatch.setattr(slice_runner, "check_gmat_available", _fail)
    monkeypatch.setattr(slice_runner, "run_gmat_script", _fail)

    case = _singular_infeasible_ready_case()
    model_selection_preview = workflow.select_model(case.model_selection_case)
    assert model_selection_preview.selection == "CW rendezvous"
    assert model_selection_preview.qualified is True  # singular targeting qualifies the decision (AC2)

    result = run_rendezvous_workflow(case, output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.outcome == "CW_TARGETING_INFEASIBLE"
    assert result.verified is False
    assert "CW targeting infeasible" in result.verification_status
    data = result.to_dict()
    report = data["unified_verification_report"]
    assert report["solver"]["feasible"] is False
    assert report["gmat"]["attempted"] is False
    assert report["screenshot"]["ok"] is False
    assert data["artifacts"]["trajectory_screenshot"] is None
    assert not any(tmp_path.iterdir())  # no GMAT script or screenshot file was ever written


def test_gmat_execution_error_is_distinct_outcome(tmp_path, monkeypatch):
    monkeypatch.setattr(
        slice_runner, "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(True, "/stand-in/gmat", "GMAT stand-in", "ok"),
    )
    monkeypatch.setattr(
        slice_runner, "run_gmat_script",
        lambda executable, script_path, timeout_s=180.0: gmat_verify.GMATRunResult(
            True, 1, "", "simulated GMAT interpreter error", False, "GMAT exited with status 1."
        ),
    )
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.verified is False
    assert result.outcome == "EXECUTION_ERROR"


def test_malformed_gmat_output_is_distinct_outcome(tmp_path, monkeypatch):
    monkeypatch.setattr(
        slice_runner, "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(True, "/stand-in/gmat", "GMAT stand-in", "ok"),
    )

    def fake_run(executable, script_path, timeout_s=180.0):
        output_dir = script_path.parent
        for key in ("init", "postburn1", "trajectory"):
            (output_dir / f"d_{key}.txt").write_text("header line only, no data\n")
        (output_dir / "d_final.txt").write_text("not,a,valid,gmat,report\n1 2 three 4 5 6 7\n")
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    monkeypatch.setattr(slice_runner, "run_gmat_script", fake_run)
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.verified is False
    assert result.outcome == "MALFORMED_OUTPUT"


def test_screenshot_failure_is_distinct_outcome(tmp_path, monkeypatch):
    monkeypatch.setattr(
        slice_runner, "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(True, "/stand-in/gmat", "GMAT stand-in", "ok"),
    )

    def fake_run(executable, script_path, timeout_s=180.0):
        output_dir = script_path.parent
        for key in ("init", "postburn1"):
            (output_dir / f"d_{key}.txt").write_text(
                "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n0 0 0 0 0 0 0\n"
            )
        (output_dir / "d_trajectory.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "0 1.5e-05 -2e-04 0 -1.4e-04 0 0\n1373.0298005070088 0 0 0 0 0 0\n"
        )
        (output_dir / "d_final.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "1373.0298005070088 0 0 0 0 0 0\n"
        )
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    def corrupt_svg_writer(path, trajectory_states_si):
        Path(path).write_text("")

    monkeypatch.setattr(slice_runner, "run_gmat_script", fake_run)
    monkeypatch.setattr(slice_runner, "write_svg", corrupt_svg_writer)
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.verified is False
    assert result.outcome == "SCREENSHOT_FAILURE"


def test_unsupported_request_is_distinct_outcome_with_no_physics_or_gmat(tmp_path, monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("no physics or GMAT call must happen for an UNSUPPORTED selection")

    monkeypatch.setattr(slice_runner, "solve_cw_rendezvous", _fail)
    monkeypatch.setattr(workflow, "check_gmat_available", _fail)
    monkeypatch.setattr(workflow, "propagate_cartesian_state", _fail)

    result = run_rendezvous_workflow(_unsupported_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.model_selection.selection == "UNSUPPORTED"
    assert result.outcome == "UNSUPPORTED"
    assert result.verified is False
    assert result.verification_report is None
    assert not any(tmp_path.iterdir())


def test_needs_more_information_selection_requests_no_physics_or_gmat(tmp_path, monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("no physics or GMAT call must happen for a NEEDS MORE INFORMATION selection")

    monkeypatch.setattr(slice_runner, "solve_cw_rendezvous", _fail)
    monkeypatch.setattr(workflow, "check_gmat_available", _fail)

    model_case = ModelSelectionCase()  # every required item left "unknown"
    case = RendezvousCase(case_id="underspecified_case", readiness="READY_TO_SOLVE", model_selection_case=model_case)
    result = run_rendezvous_workflow(case, output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    assert result.model_selection.selection == "NEEDS MORE INFORMATION"
    assert result.outcome == "NEEDS MORE INFORMATION"
    assert result.verified is False
    assert not any(tmp_path.iterdir())


# ---------------------------------------------------------------------------
# AC5: the recorded result includes facts/assumptions, model-selection
# reasoning, exact tool inputs/outputs, numeric tolerances, artifact paths,
# and a trust statement distinguishing solver success from independent GMAT
# verification.
# ---------------------------------------------------------------------------


def test_result_record_includes_all_ac5_required_fields(tmp_path):
    result = run_rendezvous_workflow(_cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat")
    data = result.to_dict()
    # Assumptions and model-selection reasoning.
    assert len(data["model_selection"]["assumptions"]) > 0
    assert len(data["model_selection"]["reasons"]) > 0
    assert data["model_selection"]["deterministic_tool"] == "src.cw.two_burn_targeting"
    # Exact tool inputs/outputs and tolerances travel inside the unified report.
    report = data["unified_verification_report"]
    assert report["comparison"]["tolerances"] == {"position_m": 1.0, "velocity_mps": 0.001, "delta_v_mps": 0.001}
    assert report["comparison"]["cw_final_state_m_mps"] is not None
    # Artifact paths.
    assert data["artifacts"]["generated_script"]
    assert data["artifacts"]["trajectory_screenshot"]
    assert data["artifacts"]["report_files"]["final"]
    # Trust statement distinguishes solver success from independent GMAT verification.
    assert "GMAT" in result.trust_statement
    assert ("solver" in result.trust_statement.lower() or "deterministic solver" in result.trust_statement)
