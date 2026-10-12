"""Tests that the LLM-facing skill layer never supplies authoritative orbital
states or delta-v without deterministic tool output (TJC-1.8 AC4).

``.pi/skills/*/SKILL.md`` are the prompt-driven, LLM-facing instructions for
this workflow (``src/workflow.py``'s own docstring calls
``orbital-problem-formalizer`` "prompt-driven, not Python code"). Unlike
``tests/test_formalizer_schema.py`` (which checks the formalizer's required
output schema and provenance labels), this module checks the cross-skill
authority boundary: every skill that could report a numeric orbital result
explicitly delegates that computation to a named deterministic implementation
in ``src/`` and explicitly refuses to invent, improvise, or solve a result
itself, and no skill may call a result ``PASS`` without the deterministic
solver and GMAT numerical-plus-screenshot comparison chain.

``src/model_selector.py``, ``src/workflow.py``, and ``src/verification_report.py``
already enforce this invariant in code (see
``tests/test_model_selector.py``, ``tests/test_workflow.py``, and
``tests/test_verification_report.py``'s ``...raises`` tests); this module
closes the remaining gap by checking the natural-language skill layer itself,
which is not Python and so cannot be covered by those code-level tests.
"""

from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parents[1] / ".pi/skills"

FORMALIZER = SKILLS_DIR / "orbital-problem-formalizer/SKILL.md"
MODEL_SELECTOR = SKILLS_DIR / "orbital-model-selector/SKILL.md"
CW_TARGETING = SKILLS_DIR / "orbital-targeting-planner/SKILL.md"
TWO_BODY = SKILLS_DIR / "orbital-two-body-rendezvous/SKILL.md"
GMAT_VERIFICATION = SKILLS_DIR / "gmat-rendezvous-verification/SKILL.md"

ALL_SKILLS = (FORMALIZER, MODEL_SELECTOR, CW_TARGETING, TWO_BODY, GMAT_VERIFICATION)


def test_every_referenced_skill_file_exists():
    """Guard against a stale path if a skill is ever renamed or moved."""
    for skill in ALL_SKILLS:
        assert skill.is_file(), f"missing skill file: {skill}"


def test_formalizer_never_solves_or_invents_a_numerical_result():
    """The formalizer (the first LLM-facing stage) must restate the request as
    structured data without ever producing a numeric orbital state or burn."""
    text = FORMALIZER.read_text()
    assert "Never solve, derive a numerical value, select a model, or prescribe burns." in text
    assert "do not calculate a numerical result" in text
    assert "do not solve or calculate values" in text
    assert "Do not invent altitude, gravitational parameter, circularity, LVLH convention" in text


def test_model_selector_only_selects_a_named_deterministic_tool_and_never_computes_physics():
    """The model selector picks which deterministic implementation applies; it
    does not itself compute a state or delta-v, and it names the exact
    deterministic implementation handoff for every selection."""
    text = MODEL_SELECTOR.read_text()
    assert "`CW rendezvous`: deterministic, fixed-duration local two-impulse CW\n  targeting in `src/cw.py`" in text
    assert "`bounded two-body fallback`: deterministic inertial Cartesian point-mass\n  **coast propagation** in `src/twobody.py`" in text
    assert "without inventing a new model" in text
    assert "deterministic implementation handoff" in text
    assert "Do not declare CW valid from a single fixed percentage, orbit count, or\nlearned threshold." in text


def test_cw_targeting_skill_requires_the_deterministic_implementation_and_refuses_to_invent_inputs():
    """The CW-targeting skill must call src/cw.py's deterministic implementation
    for every numeric result and must not improvise inputs or substitute a
    least-squares approximation for a rejected singular transfer time."""
    text = CW_TARGETING.read_text()
    assert "Use `src/cw.py::mean_motion` and `two_burn_targeting`" in text
    assert "Do not invent any missing input or coordinate convention." in text
    assert (
        "Treat `CWSingularTransferError` as a rejected transfer time, not a reason\n"
        "   to approximate with a least-squares solution."
    ) in text
    assert "Report the two impulses and final state only as a CW result under the\n   recorded assumptions." in text


def test_two_body_skill_requires_the_deterministic_implementation_and_refuses_to_improvise():
    """The bounded two-body fallback skill must call src/twobody.py's
    deterministic implementation and must not improvise a result for rejected
    inputs or claim unsupported capabilities (targeting, burns, optimization)."""
    text = TWO_BODY.read_text()
    assert "Use `src/twobody.py::TwoBodyCase` and\n   `propagate_cartesian_state`" in text
    assert "do not improvise a result." in text
    assert "Do not claim burn targeting, maneuver execution, optimization, thrust," in text


@pytest.mark.parametrize("skill", (CW_TARGETING, TWO_BODY))
def test_every_solver_skill_hands_off_to_gmat_verification_before_pass(skill):
    """Both deterministic-solver-calling skills explicitly state that a result
    is never PASS without the separate GMAT verification handoff -- a solver
    skill's own candidate output is never, by itself, an authoritative/verified
    result."""
    text = skill.read_text()
    assert "gmat-rendezvous-verification" in text
    assert "never" in text.lower() or "not PASS" in text or "not verified" in text.lower()


def test_gmat_verification_skill_requires_both_numerical_comparison_and_screenshot_for_pass():
    """PASS requires GMAT numerical comparison AND an accessible screenshot
    together; any single missing/failed piece of evidence must not produce
    PASS (mirrors src/verification_report.py's assemble_verification_report
    constructor invariant, tested directly in
    tests/test_verification_report.py::test_verified_true_*_raises, for the
    LLM-facing instruction layer that precedes that code path)."""
    text = GMAT_VERIFICATION.read_text()
    assert "**GMAT numerical comparison:**" in text
    assert "**Accessible trajectory screenshot:**" in text
    assert (
        "GMAT execution failure, unavailable GMAT, missing/mismatched comparison data,\n"
        "a tolerance exceedance, or a missing/inaccessible screenshot cannot be\n"
        "reported as PASS."
    ) in text
    assert "`FAIL`, `UNAVAILABLE`,\nor `INCOMPLETE`" in text


def test_gmat_verification_skill_does_not_claim_gmat_is_already_integrated():
    """The verification skill is explicit that it defines the required
    evidence contract rather than asserting GMAT execution is already wired
    up -- it is not itself an authoritative claim of a verified result."""
    text = GMAT_VERIFICATION.read_text()
    assert "it does not claim that GMAT is integrated in the recovered\nrepository." in text
    assert "The current repository has no GMAT execution integration" in text
