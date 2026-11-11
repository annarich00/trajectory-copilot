"""Static guard for the GMAT-example review step in the rendezvous orchestration
skill ``.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md`` (TJC-15, re-expressed
from the retired ``.pi/prompts/rendezvous.md`` by TJC-23.6).

No model is run. These tests read the committed skill instructions and check that
the new step sits after the GMAT tool call and before the final outcome report,
that it hands the generated script and mission type to the ``gmat-example-reviewer``
subagent, that its verdict is advisory/stylistic only (never changes
FAIL/VERIFIED), that an unavailable/erroring subagent is reported as
skipped/unavailable without blocking the numerical result, and that the
no-corpus-entry mission-type choice is documented.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT = (ROOT / ".pi/skills/rendezvous-pipeline-orchestrator/SKILL.md").read_text()


def _step(number: int) -> str:
    """Return the text of top-level numbered step ``number`` (column-0 ``N. ``)."""
    pattern = re.compile(rf"^{number}\. (.*?)(?=^\d+\. |\Z)", re.DOTALL | re.MULTILINE)
    match = pattern.search(PROMPT)
    assert match, f"step {number} not found in rendezvous skill"
    return match.group(0)


def test_review_step_sits_between_gmat_tool_call_and_final_report():
    gmat_call = PROMPT.index("explicitly calling the `run_gmat_verification` pi tool")
    review = PROMPT.index("gmat-example-reviewer")
    final_report = PROMPT.index("Report the final `outcome`, `verified`")
    assert gmat_call < review < final_report
    assert "gmat-example-reviewer" in _step(4)
    assert _step(5).startswith("5. Report the final `outcome`")
    assert "interactive" in _step(6) or "GMAT GUI" in _step(6)


def test_review_step_hands_script_and_mission_type_to_subagent_tool():
    step = _step(4)
    assert "`subagent` tool" in step
    assert 'agentScope: "project"' in step or "agentScope" in step
    assert "generated GMAT script" in step
    assert "mission type" in step
    assert "generated_cw_rendezvous.script" in step
    assert 'artifacts["generated_script"]' in step


def test_review_step_documents_no_corpus_entry_choice_without_fabrication():
    step = _step(4)
    assert "NO CORPUS ENTRY" in step
    assert "research/gmat_example_corpus/corpus.json" in step
    assert "no rendezvous" in step.lower() or "no rendezvous/relative-motion" in step
    # No silent nearest-neighbour substitution of the real mission type.
    assert "do not substitute" in step.lower()
    assert "orbit_transfer" in step  # named only as the example of what must not be substituted


def test_review_verdict_is_advisory_stylistic_and_never_overrides_numerical_outcome():
    step = _step(4)
    assert "advisory" in step.lower() and "stylistic" in step.lower()
    assert "never changes" in step or "must never change" in step
    assert "FAIL" in step and "VERIFIED" in step
    assert "alongside" in step and "not instead of" in step
    assert "src/gmat_verify.py" in step
    # The final report step carries the labelled verdict next to the numerical result.
    final = _step(5)
    assert "advisory" in final.lower()
    assert "review" in final.lower()


def test_review_step_is_non_blocking_when_subagent_unavailable_or_errors():
    step = _step(4)
    lowered = step.lower()
    assert "unavailable" in lowered and "skipped" in lowered
    assert "errors" in lowered or "error" in lowered
    assert "still" in lowered and "numerical" in lowered
    assert "do not block" in lowered or "never block" in lowered
    assert "review skipped" in lowered or "skipped/unavailable" in lowered


def test_review_step_skips_when_no_gmat_script_was_generated():
    step = _step(4).lower()
    assert "no script" in step or "not generated" in step


def test_single_spacecraft_coast_exception_and_other_steps_remain():
    assert "single-spacecraft inertial-Cartesian coast request" in PROMPT
    assert "do not proceed to step 2" in PROMPT
    # Cross references were renumbered along with the new step: the final summary is step 5.
    assert "step-5 summary" in PROMPT
    assert "step-4 summary" not in PROMPT
    assert "step 3-4" not in PROMPT


def test_review_step_forbids_self_authored_verdicts():
    step = _step(4)
    assert "Never write, echo" in step
    assert "actually returned by a real `gmat-example-reviewer` subagent call" in step
