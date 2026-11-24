"""Regression checks for the standalone demo page (TJC-21.4).

The page carries a Content-Security-Policy with ``script-src 'self'``, so any
inline <script> body is silently blocked by the browser and the demo never
renders. That was the real cause of the "Demo A/B/C do not load" report. These
checks keep that from regressing without needing a browser.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PAGE = Path(os.environ.get("DEMO_PAGE_UNDER_TEST", ROOT / "site/demo-visualization-pipeline.html"))
DATA = ROOT / "site/data/demo-runs.js"


def test_no_inline_script_body_under_script_src_self():
    html = PAGE.read_text()
    assert "script-src 'self'" in html
    for match in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", html, re.S):
        if "src=" not in match.group("attrs"):
            assert not match.group("body").strip(), "inline script is blocked by the page CSP"


def test_html_visualizations_offer_a_direct_open_link():
    """A reader can open a 3D scene directly when its embedded iframe is unavailable."""
    js = JS.read_text()
    assert "Open this 3D scene in a new tab" in js
    assert 'target="_blank"' in js


def test_pages_payload_includes_demo_d_relative_scene():
    """Demo D's inline scene needs its HTML artifact in the deployed Pages payload."""
    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text()
    scene = "artifacts/runs/earth-400km-15time-scan/relative_position_3d.html"
    assert f"mkdir -p _site/{scene.rsplit('/', 1)[0]}" in workflow
    assert f"cp {scene} _site/{scene.rsplit('/', 1)[0]}/" in workflow


def test_pages_deployment_uses_one_unique_artifact_per_run_attempt():
    """Retrying a Pages run must not make deploy-pages choose between duplicate artifacts."""
    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text()
    artifact_name = "github-pages-${{ github.run_attempt }}"

    assert workflow.count("actions/upload-pages-artifact@v3") == 1
    assert f"name: {artifact_name}" in workflow
    assert workflow.count(f"artifact_name: {artifact_name}") == 1


def test_page_script_and_data_are_referenced_and_exist():
    html = PAGE.read_text()
    for src in re.findall(r'<script src="([^"]+)"', html):
        assert (ROOT / "site" / src).is_file(), src


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_demo_data_file_parses_and_has_four_demos():
    code = (
        "const vm=require('vm');const fs=require('fs');const c={window:{}};vm.createContext(c);"
        f"vm.runInContext(fs.readFileSync({str(DATA)!r},'utf8'),c);"
        "console.log(Object.keys(c.window.TCDemoRuns).join(','))"
    )
    out = subprocess.run(["node", "-e", code], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "demoA,demoB,demoC,demoD"


# --- chat-style playback (TJC-21.4 scope change) ---------------------------------
JS = ROOT / "site/js/demo-visualization-pipeline.js"
CONTROL_IDS = ("chat-log", "play-pause", "next-step", "show-all", "restart")


def test_page_has_chat_log_and_playback_controls():
    html = PAGE.read_text()
    for control_id in CONTROL_IDS:
        assert f'id="{control_id}"' in html, control_id


def test_agent_playback_defaults_to_2500ms_without_changing_typing_timing():
    js = JS.read_text()
    assert "URLSearchParams" in js and "DELAY_MS" in js
    assert "|| 2500" in js
    assert "TYPING_DELAY_MS" in js and "|| 20" in js


def test_script_shows_request_as_a_user_message_then_agent_steps():
    js = JS.read_text()
    assert "msg user" in js and "msg agent" in js
    assert js.index("msg user") < js.index("msg agent")


def test_page_uses_a_concise_disclosure_for_current_recorded_run_outcomes():
    """The closed-by-default note accurately summarizes the reverified demos."""
    html = PAGE.read_text()
    assert '<details class="recording-info">' in html
    assert "About these recorded demos" in html
    assert "Demo A is NOT VERIFIED" in html
    assert "Demo B is VERIFIED" in html
    assert "20 m / 0.05 m/s" in html
    assert "Demo C is UNSUPPORTED" in html


def test_developer_mode_renders_visual_artifacts_without_textual_step_chrome():
    """Developer mode presents an image artifact as the image itself, rather
    than prepending its title, status, narrative, path, or raw JSON."""
    js = JS.read_text()
    assert "function developerImageMessage" in js
    assert "developerImageMessage(step, index)" in js


def test_demo_d_marks_every_selected_five_period_graph_with_a_scope_note():
    """Only the scan graph represents all candidates; every 5-period graph says so."""
    run = _load_site_demo_runs()["demoD"]["run"]
    plotted_steps = {step["name"]: step for step in run["steps"]}
    trajectory = plotted_steps["trajectory_burns_plot"]["artifacts"]
    comparison = plotted_steps["verification_comparison_plot"]["artifacts"]

    selected_note = "Shows only the selected five-period minimum candidate"
    assert trajectory[0]["scope_note"].startswith(selected_note)
    assert "scope_note" not in trajectory[1]
    assert all(artifact["scope_note"].startswith(selected_note) for artifact in comparison)
    assert "artifact-scope-note" in JS.read_text()


def test_relaxed_tolerance_follow_up_is_a_demo_d_agent_response_only():
    """The follow-up is recorded data for Demo D, never a global footer."""
    html = PAGE.read_text()
    runs = _load_site_demo_runs()

    assert 'id="relaxed-tolerance-follow-up"' not in html
    assert "relaxedToleranceFollowUpMessage" in JS.read_text()
    assert "relaxed_tolerance_follow_up" in runs["demoD"]["run"]
    assert "0.10 orbital periods (555.362 s)" in runs["demoD"]["run"]["relaxed_tolerance_follow_up"]
    for demo_id in ("demoA", "demoB", "demoC"):
        assert "relaxed_tolerance_follow_up" not in runs[demo_id]["run"]


def test_page_discloses_demo_d_artifact_scope():
    """Demo D's trajectory and comparison images must not be mistaken for all scan candidates."""
    html = PAGE.read_text()
    assert "Demo D trajectory/burn and GMAT-comparison visuals show only the selected five-period minimum candidate." in html
    assert "Its delta-v-versus-time plot contains all 15 evaluated transfer times." in html


def test_page_has_no_operator_mode_or_mode_toggle():
    """The owner chose the developer-oriented replay as the page's only view."""
    assert 'id="mode-operator"' not in PAGE.read_text()
    assert "mode === 'operator'" not in JS.read_text()


def test_sole_view_has_no_stale_mode_reference():
    """A removed mode toggle must not leave playback with an undefined variable."""
    assert "mode === 'developer'" not in JS.read_text()


def test_pipeline_steps_use_skill_or_tool_source_labels():
    """Recorded responses identify their producing skill, tool, or artifact stage."""
    js = JS.read_text()
    assert "function stepSourceLabel" in js
    assert "SKILL: RENDEZVOUS PIPELINE ORCHESTRATOR · TOOL: ORBITAL PROBLEM FORMALIZER" in js
    assert "TOOL: ORBITAL MODEL SELECTOR" in js
    assert "TOOL: GMAT VERIFICATION" in js


def test_recorded_calculation_table_follows_gmat_and_precedes_comparison_plots():
    """The table uses recorded solver/GMAT results and is inserted in pipeline order."""
    js = JS.read_text()
    assert "function calculationTableMessage" in js
    assert "solve_cw_rendezvous" in js
    assert "run_gmat_verification" in js
    assert "if (step.name === 'run_gmat_verification') parts.push(calculationTableMessage(run));" in js


def test_hosted_artifact_urls_preserve_the_github_pages_repository_base():
    """A project Pages URL must not resolve Demo D's artifact at the user-site root."""
    js = JS.read_text()
    assert "function artifactUrl" in js
    assert "if (location.protocol === 'file:') return `../${path}`;" in js
    assert "const repositoryBase = location.pathname.split('/').filter(Boolean)[0];" in js
    assert "return repositoryBase ? `/${repositoryBase}/${path}` : `/${path}`;" in js


def test_html_visualization_artifacts_render_inline_not_as_a_path_only():
    """The recorded Plotly scene is part of the replay, not an opaque path."""
    js = JS.read_text()
    assert "function artifactFrameMarkup" in js
    assert 'class="artifact-frame"' in js
    assert "sandbox=\"allow-scripts allow-same-origin\"" in js


def test_response_cards_do_not_show_a_reason_caption():
    """Stored reasons remain data, not a repeated presentation label."""
    assert '<strong>Reason:</strong>' not in JS.read_text()


def test_visualization_renderers_reserve_space_for_legends_and_titles():
    """Static artifacts must keep legends outside data axes and save their full bounds."""
    trajectory = (ROOT / "src/visualization_trajectory.py").read_text()
    comparison = (ROOT / "src/visualization_comparison.py").read_text()
    scene = (ROOT / "src/visualization.py").read_text()
    assert "bbox_to_anchor=(0.5, -0.16)" in trajectory
    assert 'bbox_inches="tight"' in comparison
    assert "legend=dict(orientation=\"h\"" in scene


def test_user_message_omits_the_rendezvous_command_prefix():
    """The stored command remains canonical, but readers see only its request."""
    js = JS.read_text()
    assert "function displayRequest" in js
    assert "replace(/^\\/rendezvous\\b\\s*/i, '')" in js


def test_replay_starts_blank_and_play_types_the_request_before_steps():
    """The request is a Play-triggered typing animation, not preloaded text."""
    js = JS.read_text()
    assert "const TYPING_DELAY_MS" in js
    assert "let typedRequestLength = 0;" in js
    assert "if (typedRequestLength < request.length)" in js
    assert "restart(false);" in js


def test_typed_user_request_does_not_restart_entrance_animation_or_scroll():
    """Each character update keeps the already-visible user bubble stable."""
    assert ".msg.user { animation: none; }" in PAGE.read_text()
    assert "typedRequestLength += 1;" in JS.read_text()
    assert "render(false);" in JS.read_text()


def test_first_agent_step_starts_when_request_typing_completes():
    """Completing the typing animation must not leave playback idle."""
    js = JS.read_text()
    assert "if (typedRequestLength >= request.length) { reveal(1); schedule(); }" in js



# --- embedded site data matches the three recorded runs (TJC-21.4) --------------
# These read site/data/demo-runs.js exactly the way the page does (as a script
# that assigns window.TCDemoRuns), so a regenerated data file that lost a
# demo's request text or structured results fails here rather than in a browser.

CANONICAL_STEP_NAMES = [
    "formalize_rendezvous_problem",
    "select_rendezvous_model",
    "relative_position_3d_scene",
    "solve_cw_rendezvous",
    "trajectory_burns_plot",
    "run_gmat_verification",
    "verification_comparison_plot",
]


def _load_site_demo_runs() -> dict:
    code = (
        "const vm=require('vm');const fs=require('fs');const c={window:{}};vm.createContext(c);"
        f"vm.runInContext(fs.readFileSync({str(DATA)!r},'utf8'),c);"
        "console.log(JSON.stringify(c.window.TCDemoRuns))"
    )
    out = subprocess.run(["node", "-e", code], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("demo_id", ["demoA", "demoB", "demoC", "demoD"])
def test_site_data_exposes_request_text_and_structured_step_results(demo_id: str):
    run = _load_site_demo_runs()[demo_id]["run"]

    assert run["request"].startswith("/rendezvous ")
    assert run["request"] == run["source_request_text"]
    assert run["request"] != run["case_id"]
    assert [step["name"] for step in run["steps"]] == CANONICAL_STEP_NAMES
    steps = {step["name"]: step for step in run["steps"]}
    assert steps["formalize_rendezvous_problem"]["result"]["readiness"] == "READY_TO_SOLVE"
    assert steps["select_rendezvous_model"]["result"]["selection"]
    assert run["verified"] is (demo_id == "demoB")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_site_data_demo_d_records_the_15_time_scan_and_unverified_minimum():
    run = _load_site_demo_runs()["demoD"]["run"]
    steps = {step["name"]: step for step in run["steps"]}

    assert run["outcome"] == "NUMERICAL_DISAGREEMENT"
    assert run["verified"] is False
    assert steps["solve_cw_rendezvous"]["result"]["transfer_time_s"] == pytest.approx(27768.121356261134)
    assert steps["solve_cw_rendezvous"]["result"]["total_delta_v_mps"] == pytest.approx(0.24008346049537377)
    assert steps["run_gmat_verification"]["result"]["comparison"]["position_error_m"] == pytest.approx(1391.2580999302322)
    scan = next(artifact for artifact in run["artifacts"] if artifact["name"] == "delta_v_vs_time")
    assert scan["media_type"] == "image/svg+xml"
    assert scan["path"].startswith("data:image/svg+xml;base64,")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_site_data_demo_c_claims_no_cw_two_body_or_gmat_verification():
    run = _load_site_demo_runs()["demoC"]["run"]

    assert run["outcome"] == "UNSUPPORTED"
    steps = {step["name"]: step for step in run["steps"]}
    assert steps["select_rendezvous_model"]["result"]["deterministic_tool"] is None
    for name in ("solve_cw_rendezvous", "run_gmat_verification"):
        assert steps[name]["status"] == "not_called", name
        assert steps[name]["reason"], name
        assert "result" not in steps[name], name
    for name in ("relative_position_3d_scene", "trajectory_burns_plot", "verification_comparison_plot"):
        assert steps[name]["status"] == "not_generated", name
        assert steps[name]["reason"], name
        assert not steps[name].get("artifact") and not steps[name].get("artifacts"), name
    assert "propagate_two_body_coast" not in json.dumps(run)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_site_data_records_the_reverified_gmat_outcomes_for_demo_a_and_b():
    runs = _load_site_demo_runs()
    demo_a = runs["demoA"]["run"]
    demo_b = runs["demoB"]["run"]

    assert demo_a["outcome"] == "NUMERICAL_DISAGREEMENT"
    assert demo_b["outcome"] == "VERIFIED"
    a_gmat = next(s for s in demo_a["steps"] if s["name"] == "run_gmat_verification")["result"]
    b_gmat = next(s for s in demo_b["steps"] if s["name"] == "run_gmat_verification")["result"]
    assert a_gmat["comparison"]["tolerances"] == {"position_m": 20, "velocity_mps": 0.05, "delta_v_mps": 0.001}
    assert b_gmat["verified"] is True
    assert b_gmat["comparison"]["status"] == "PASS"
