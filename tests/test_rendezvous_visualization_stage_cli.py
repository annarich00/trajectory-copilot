"""Tests for scripts/rendezvous_visualization_stage.py (TJC-16.5).

The thin CLI that ``.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md`` (the
rendezvous orchestration skill TJC-23.6 re-expressed from the retired
``.pi/prompts/rendezvous.md``) calls between its visible steps, so each
visualization artifact path can be reported as soon as it exists even
though the CW GMAT step runs through the separate ``run_gmat_verification`` pi
tool rather than ``run_rendezvous_workflow``. It holds no plotting or physics
logic; it forwards to ``src/workflow_visualization.py``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.rendezvous_visualization_stage import main  # noqa: E402
from src import gmat_verify  # noqa: E402

CW_CASE = {
    "case_id": "stage_cli_case",
    "mu_m3_s2": 398600441800000.0,
    "reference_radius_m": 6728000.0,
    "initial_relative_state": [15.0, -200.0, 0.0, -0.14, 0.0, 0.0],
    "final_relative_state": [0.0] * 6,
    "transfer_time_s": 1373.0298005070088,
    "pos_tol_m": 1.0,
    "vel_tol_mps": 0.001,
}


def _run(capsys, stage: str, output_dir: Path, *extra: str) -> tuple[int, dict]:
    code = main([stage, "--case-json", json.dumps(CW_CASE), "--output-dir", str(output_dir), *extra])
    return code, json.loads(capsys.readouterr().out)


def test_scene_then_trajectory_stages_print_generated_records(tmp_path, capsys):
    code, scene = _run(capsys, "scene", tmp_path)
    assert code == 0
    assert scene["stage"] == "relative_position_3d_scene" and scene["status"] == "generated"
    assert Path(scene["paths"][0]).is_file()

    code, trajectory = _run(capsys, "trajectory", tmp_path)
    assert code == 0
    assert trajectory["stage"] == "trajectory_burns_plot" and trajectory["status"] == "generated"
    assert Path(trajectory["paths"][0]).stat().st_size > 0


def test_comparison_stage_without_gmat_output_reports_not_generated(tmp_path, capsys):
    code, comparison = _run(capsys, "comparison", tmp_path, "--comparison-status", "INCOMPLETE")
    assert code == 0
    assert comparison["status"] == "not_generated"
    assert comparison["paths"] == []
    assert "INCOMPLETE" in comparison["reason"]


def test_comparison_stage_uses_gmat_trajectory_report_from_same_output_dir(tmp_path, capsys):
    (tmp_path / "d_trajectory.txt").write_text(
        "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
        "0 1.5e-05 -2e-04 0 -1.4e-04 0 0\n1373.0298005070088 0 0 0 0 0 0\n"
    )
    code, comparison = _run(capsys, "comparison", tmp_path, "--comparison-status", "PASS")
    assert code == 0
    assert comparison["status"] == "generated"
    assert len(comparison["paths"]) == 2 and all(Path(path).is_file() for path in comparison["paths"])


def test_missing_required_field_is_an_explicit_error_not_a_crash(tmp_path, capsys):
    code = main(["scene", "--case-json", json.dumps({"case_id": "x"}), "--output-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert code == 2 and "missing required field" in out["error"]


def test_cli_entrypoint_runs_as_a_script(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/rendezvous_visualization_stage.py"), "scene",
         "--case-json", json.dumps(CW_CASE), "--output-dir", str(tmp_path)],
        capture_output=True, text=True, timeout=120, cwd=ROOT,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["status"] == "generated"


PROMPT = (ROOT / ".pi/skills/rendezvous-pipeline-orchestrator/SKILL.md").read_text()


def test_rendezvous_prompt_reports_artifacts_in_pipeline_order_and_keeps_existing_constraints():
    """TJC-16.5 AC4/AC5: the skill names each stage CLI in pipeline order (scene, trajectory,
    run_gmat_verification, comparison) and keeps its pre-existing step/handoff wording."""
    positions = [
        PROMPT.index("rendezvous_visualization_stage.py scene"),
        PROMPT.index("rendezvous_visualization_stage.py trajectory"),
        PROMPT.index("explicitly calling the `run_gmat_verification` pi tool"),
        PROMPT.index("rendezvous_visualization_stage.py comparison"),
    ]
    assert positions == sorted(positions)
    assert "not_generated" in PROMPT and "`reason`" in PROMPT
    # Pre-existing constraints, unchanged.
    for kept in (
        "then call the\n   `formalize_rendezvous_problem` pi tool",
        "Do not solve anything or call any Python in this step.",
        "`src/workflow.py::run_rendezvous_workflow(...)` directly with",
        "./GMAT-R2026a -r <path to the generated GUI preview script>",
        "exactly this: state plainly that an interactive GMAT window cannot be",
    ):
        assert kept in PROMPT
