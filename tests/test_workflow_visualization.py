"""Tests for wiring the TJC-16.2/16.3/16.4 plots into run_rendezvous_workflow (TJC-16.5).

The three visualization artifacts must be generated in pipeline order and
each at its own stage boundary, not deferred to the end of the run:

- 3D relative-position scene: after formalization/model selection, BEFORE the
  deterministic CW solve (AC1);
- trajectory/burns plot: right after the solve, BEFORE any GMAT execution (AC2);
- CW-vs-GMAT comparison plot: right after GMAT execution and parsing (AC3).

Stages whose inputs do not exist for a given path (e.g. the bounded two-body
fallback has no relative state, no burns, and no solver state history) are
recorded as ``not_generated`` with a concrete reason, never faked.

Ordering is observed through a shared ``events`` list: spies on the CW
solve and the GMAT run append ``"solve"``/``"gmat_run"`` while the workflow's
``on_artifact`` callback appends each artifact stage at the moment it is
produced, so the assertions check real call order rather than file names.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.run_cw_gmat_slice as slice_runner  # noqa: E402
from src import gmat_verify, workflow  # noqa: E402
from src.workflow import run_rendezvous_workflow  # noqa: E402
from tests.test_workflow import (  # noqa: E402
    _cw_ready_case,
    _fake_cw_happy_path_run,
    _setup_cw_happy_path,
    _setup_two_body_happy_path,
    _singular_infeasible_ready_case,
    _two_body_ready_case,
)

SCENE = "relative_position_3d_scene"
TRAJECTORY = "trajectory_burns_plot"
COMPARISON = "verification_comparison_plot"


def _instrument_cw(monkeypatch, events: list) -> None:
    """Record 'solve' and 'gmat_run' in ``events`` around the real/fake CW pipeline calls."""
    real_solve = slice_runner.solve_cw_rendezvous

    def spy_solve(*args, **kwargs):
        events.append("solve")
        return real_solve(*args, **kwargs)

    monkeypatch.setattr(slice_runner, "solve_cw_rendezvous", spy_solve)
    real_run = slice_runner.run_gmat_script

    def spy_run(*args, **kwargs):
        events.append("gmat_run")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(slice_runner, "run_gmat_script", spy_run)


def test_cw_path_generates_each_plot_at_its_own_stage_boundary(tmp_path, monkeypatch):
    _setup_cw_happy_path(monkeypatch)
    events: list = []
    _instrument_cw(monkeypatch, events)

    result = run_rendezvous_workflow(
        _cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat",
        attempt_gui_screenshot=False, on_artifact=lambda record: events.append(record["stage"]),
    )

    assert result.verified is True
    assert events == [SCENE, "solve", TRAJECTORY, "gmat_run", COMPARISON]

    records = result.artifacts["visualization_artifacts"]
    assert [record["stage"] for record in records] == [SCENE, TRAJECTORY, COMPARISON]
    for record in records:
        assert record["status"] == "generated", record
        assert record["paths"] and all(Path(path).is_file() and Path(path).stat().st_size > 0 for path in record["paths"])
    assert records[0]["paths"][0].endswith(".html")
    assert records[1]["paths"][0].endswith(".png")
    assert len(records[2]["paths"]) == 2  # overlaid trajectory + error-history PNGs
    # The existing GMAT screenshot handoff is unchanged and still reported as before.
    assert result.artifacts["trajectory_screenshot"].endswith("trajectory.svg")
    # The comparison plot path is referenced from the unified report (TJC-16.4 field).
    assert result.artifacts["unified_verification_report"]["comparison_plot_path"] == records[2]["paths"][1]


def test_cw_comparison_plot_is_not_generated_when_gmat_never_ran(tmp_path):
    events: list = []
    result = run_rendezvous_workflow(
        _cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat",
        attempt_gui_screenshot=False, on_artifact=lambda record: events.append(record["stage"]),
    )
    assert result.outcome == "MISSING_GMAT"
    assert events == [SCENE, TRAJECTORY, COMPARISON]
    by_stage = {record["stage"]: record for record in result.artifacts["visualization_artifacts"]}
    assert by_stage[SCENE]["status"] == "generated"
    assert by_stage[TRAJECTORY]["status"] == "generated"
    assert by_stage[COMPARISON]["status"] == "not_generated"
    assert "INCOMPLETE" in by_stage[COMPARISON]["reason"]
    assert by_stage[COMPARISON]["paths"] == []


def test_singular_infeasible_cw_case_gets_scene_but_no_trajectory_or_comparison(tmp_path, monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("GMAT must not be invoked when CW targeting itself is infeasible")

    monkeypatch.setattr(slice_runner, "check_gmat_available", _fail)
    monkeypatch.setattr(slice_runner, "run_gmat_script", _fail)
    result = run_rendezvous_workflow(
        _singular_infeasible_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat",
    )
    assert result.outcome == "CW_TARGETING_INFEASIBLE"
    by_stage = {record["stage"]: record for record in result.artifacts["visualization_artifacts"]}
    assert by_stage[SCENE]["status"] == "generated"
    assert by_stage[TRAJECTORY]["status"] == "not_generated"
    assert "infeasible" in by_stage[TRAJECTORY]["reason"]
    assert by_stage[COMPARISON]["status"] == "not_generated"


def test_two_body_path_records_not_generated_with_concrete_reasons_in_stage_order(tmp_path, monkeypatch):
    case = _two_body_ready_case()
    _setup_two_body_happy_path(monkeypatch, case)
    events: list = []
    real_run = workflow.run_gmat_script

    def spy_run(*args, **kwargs):
        events.append("gmat_run")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(workflow, "run_gmat_script", spy_run)
    result = run_rendezvous_workflow(
        case, output_dir=tmp_path, gmat_executable="definitely-not-gmat", attempt_gui_screenshot=False,
        on_artifact=lambda record: events.append(record["stage"]),
    )
    assert result.verified is True
    assert events == [SCENE, TRAJECTORY, "gmat_run", COMPARISON]
    records = result.artifacts["visualization_artifacts"]
    assert [record["stage"] for record in records] == [SCENE, TRAJECTORY, COMPARISON]
    assert all(record["status"] == "not_generated" and record["paths"] == [] for record in records)
    assert "initial_relative_state" in records[0]["reason"]
    assert "burn" in records[1]["reason"]
    assert "state history" in records[2]["reason"]


def test_workflow_without_on_artifact_callback_still_records_artifacts(tmp_path):
    result = run_rendezvous_workflow(
        _cw_ready_case(), output_dir=tmp_path, gmat_executable="definitely-not-gmat", attempt_gui_screenshot=False,
    )
    assert [record["stage"] for record in result.to_dict()["artifacts"]["visualization_artifacts"]] == [
        SCENE, TRAJECTORY, COMPARISON,
    ]


@pytest.mark.skipif(
    gmat_verify.check_gmat_available("GmatConsole-R2026a").available is False,
    reason="GmatConsole-R2026a is not available/runnable in this environment",
)
def test_real_gmat_end_to_end_cw_case_produces_all_artifacts_in_pipeline_order(tmp_path):
    """Real GmatConsole-R2026a run (no fakes): scene -> solve -> trajectory plot -> GMAT -> comparison plot
    -> existing GMAT screenshot/plot handoff, with file mtimes corroborating the callback order."""
    events: list = []
    result = run_rendezvous_workflow(
        _cw_ready_case("real_gmat_e2e"), output_dir=tmp_path, gmat_executable="GmatConsole-R2026a",
        attempt_gui_screenshot=False, on_artifact=lambda record: events.append(record["stage"]),
    )
    assert result.verified is True and result.outcome == "VERIFIED"
    assert events == [SCENE, TRAJECTORY, COMPARISON]
    records = {record["stage"]: record for record in result.artifacts["visualization_artifacts"]}
    assert all(record["status"] == "generated" for record in records.values()), records

    mtime = lambda path: Path(path).stat().st_mtime_ns  # noqa: E731
    scene, trajectory = records[SCENE]["paths"][0], records[TRAJECTORY]["paths"][0]
    gmat_final = result.artifacts["report_files"]["final"]
    comparison = records[COMPARISON]["paths"][0]
    screenshot = result.artifacts["trajectory_screenshot"]
    assert mtime(scene) <= mtime(trajectory) <= mtime(gmat_final) <= mtime(comparison)
    assert Path(screenshot).is_file() and Path(screenshot).stat().st_size > 0
    # Comparison error history is real GMAT-vs-CW data and sits inside the declared tolerances.
    assert result.artifacts["unified_verification_report"]["comparison"]["status"] == "PASS"
