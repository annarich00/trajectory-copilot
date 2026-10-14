"""Structural checks for the TJC-1.22 baseline-vs-workflow comparison artifacts.

Mirrors ``tests/test_benchmark_fixtures.py``'s schema/structure-check
pattern (not a test that re-runs GMAT or the workflow itself): asserts
that ``evaluations/baseline_comparison/`` contains the required
methodology (``README.md``), report (``REPORT.md``), one direct-LLM
baseline response per benchmark case, and one real
``WorkflowResult.to_dict()`` artifact per case with the required
AC1-AC5 record shape (readiness/outcome/verified/model_selection/
trust_statement, and -- for the solvable cases -- a GMAT comparison and
screenshot result embedded in ``unified_verification_report``).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

COMPARISON_DIR = Path(__file__).parents[1] / "evaluations/baseline_comparison"

CASES = ("a", "b", "c", "d")
SOLVABLE_CASES = ("a", "b", "c")


def test_methodology_and_report_exist_and_disclose_the_baseline_design():
    readme = (COMPARISON_DIR / "README.md").read_text()
    report = (COMPARISON_DIR / "REPORT.md").read_text()
    for text in (readme, report):
        assert "direct-LLM baseline" in text
        assert "GmatConsole-R2026a" in text or "GMAT" in text
    # AC1-honesty requirement: the report must disclose that the baseline
    # side was produced by the implementing model itself, not a live
    # external LLM API, so a reviewer never mistakes this for a
    # third-party model comparison.
    assert "same model" in report or "implementing model" in report
    assert "PI_MODEL" in report and "PI_PROVIDER" in report


@pytest.mark.parametrize("letter", CASES)
def test_each_case_has_a_baseline_llm_response_file(letter):
    path = COMPARISON_DIR / f"case_{letter}_baseline_llm_response.md"
    assert path.is_file(), f"missing {path.name}"
    text = path.read_text()
    assert "Baseline response" in text
    assert "methodology" in text.lower() or "Methodology" in text


@pytest.mark.parametrize("letter", CASES)
def test_each_case_has_a_real_workflow_result_file(letter):
    path = COMPARISON_DIR / f"case_{letter}_workflow_result.json"
    assert path.is_file(), f"missing {path.name}"
    data = json.loads(path.read_text())
    for field in ("case_id", "readiness", "outcome", "verified", "verification_status",
                  "clarification_questions", "model_selection", "trust_statement"):
        assert field in data, f"case_{letter}_workflow_result.json missing {field!r}"


def test_case_d_workflow_result_short_circuits_before_any_physics():
    """AC1/AC5: the ambiguous case must stop at NEEDS_CLARIFICATION with no
    model selection, solver, or GMAT call attempted, matching
    src/workflow.py's documented short-circuit behavior."""
    data = json.loads((COMPARISON_DIR / "case_d_workflow_result.json").read_text())
    assert data["readiness"] == "NEEDS_CLARIFICATION"
    assert data["outcome"] == "NEEDS_CLARIFICATION"
    assert data["verified"] is False
    assert data["model_selection"] is None
    assert data["artifacts"] == {}
    assert data["clarification_questions"], "case (d) must carry the clarification questions"


@pytest.mark.parametrize("letter", SOLVABLE_CASES)
def test_solvable_cases_report_a_real_gmat_comparison_and_screenshot(letter):
    """AC2/AC3: every solvable case's workflow result must carry a real GMAT
    comparison status and a validated trajectory screenshot result -- not
    merely a solver success claimed as verified."""
    data = json.loads((COMPARISON_DIR / f"case_{letter}_workflow_result.json").read_text())
    report = data["unified_verification_report"]
    assert report is not None, f"case {letter} must carry a unified_verification_report"
    assert report["comparison"]["status"] == "PASS"
    assert report["screenshot"]["ok"] is True
    assert data["verified"] is True
    assert data["model_selection"] is not None


def test_boundary_case_is_qualified_with_surfaced_concerns():
    """AC4/AC5: case (b) must be a qualified CW decision, not a flat pass,
    matching evaluations/benchmark/case_b_boundary_cw.json's own contract."""
    data = json.loads((COMPARISON_DIR / "case_b_workflow_result.json").read_text())
    model_selection = data["model_selection"]
    assert model_selection["selection"] == "CW rendezvous"
    assert model_selection["qualified"] is True
    assert model_selection["concerns"], "a qualified decision must surface concerns"


def test_two_body_case_routes_to_bounded_fallback_with_violated_assumptions():
    """AC1/AC2: case (c) must route to the bounded two-body fallback with
    locality/other_physics explicitly recorded as violated."""
    data = json.loads((COMPARISON_DIR / "case_c_workflow_result.json").read_text())
    model_selection = data["model_selection"]
    assert model_selection["selection"] == "bounded two-body fallback"
    assumptions = dict(item.split(": ") for item in model_selection["assumptions"])
    assert assumptions["locality"] == "violated"
    assert assumptions["other_physics"] == "violated"


def test_report_covers_all_four_categories_with_per_case_and_aggregate_sections():
    """AC4: the report must have a distinct section for each case plus an
    aggregate/summary section spanning all four."""
    report = (COMPARISON_DIR / "REPORT.md").read_text()
    for marker in (
        "Case (a)", "Case (b)", "Case (c)", "Case (d)",
        "Aggregate summary", "Scoring",
    ):
        assert marker in report, f"REPORT.md missing expected section marker {marker!r}"


def test_report_states_conclusions_are_scoped_not_universal():
    """AC5: the report must explicitly scope its conclusions and avoid
    asserting broad astrodynamics validity."""
    report = (COMPARISON_DIR / "REPORT.md").read_text()
    assert "scoped to" in report.lower() or "not a claim about" in report.lower()
    assert "does not generalize across models" in report or "limitations" in report.lower()
