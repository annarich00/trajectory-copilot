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

``orbital-problem-formalizer``'s SKILL.md was retired by TJC-23.2: its
never-solve/never-invent authority boundary is no longer prose an LLM must
follow voluntarily -- it is now structurally enforced by the registered
``formalize_rendezvous_problem`` pi tool (``formalizer.ts``'s
``validateFormalization``), which has no code path that computes a numeric
orbital state or burn, only validation and Markdown rendering of a
caller-supplied, already-reasoned specification. That tool is exercised
directly by ``formalizer.test.ts`` (TJC-23.2's own red/green coverage, not
duplicated here), so it is no longer part of this module's prose-only
skill-layer coverage.

``orbital-model-selector``'s SKILL.md was retired by TJC-23.3: its
never-invent-a-model/always-name-the-deterministic-handoff authority
boundary is likewise no longer prose an LLM must follow voluntarily -- it
is now structurally enforced by the registered ``select_rendezvous_model``
pi tool, which shells out to ``src/model_selector.py::select_model``: that
function has no code path that returns a selection without a
``deterministic_tool`` name (or an explicit ``UNSUPPORTED``/``NEEDS MORE
INFORMATION`` outcome with ``deterministic_tool=None``), and never computes
an orbital state or delta-v itself. That logic is exercised directly by
``tests/test_model_selector.py`` and the bridge-layer
``tests/test_model_selector_tool_bridge.py`` (TJC-23.3's own red/green
coverage, not duplicated here), so it is no longer part of this module's
prose-only skill-layer coverage.
"""

from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parents[1] / ".pi/skills"

TWO_BODY = SKILLS_DIR / "orbital-two-body-rendezvous/SKILL.md"

# orbital-problem-formalizer's SKILL.md was retired by TJC-23.2: see the
# module docstring above.
#
# orbital-model-selector's SKILL.md was retired by TJC-23.3: see the module
# docstring above.
#
# orbital-targeting-planner's SKILL.md was retired by TJC-23.4: its
# deterministic CW two-impulse targeting handoff is now the registered
# solve_cw_rendezvous pi tool (.pi/extensions/cw-rendezvous-tool), not a
# prompt-driven skill, so it is no longer part of this module's LLM-facing
# skill-layer authority-boundary coverage.
#
# gmat-rendezvous-verification's SKILL.md was retired by TJC-23.1: GMAT
# verification is actually performed by the registered run_gmat_verification
# pi tool (.pi/extensions/gmat-verification-tool), not by that unused skill,
# so it too is no longer part of this module's coverage.
ALL_SKILLS = (TWO_BODY,)


def test_every_referenced_skill_file_exists():
    """Guard against a stale path if a skill is ever renamed or moved."""
    for skill in ALL_SKILLS:
        assert skill.is_file(), f"missing skill file: {skill}"


def test_two_body_skill_requires_the_deterministic_implementation_and_refuses_to_improvise():
    """The bounded two-body fallback skill must call src/twobody.py's
    deterministic implementation and must not improvise a result for rejected
    inputs or claim unsupported capabilities (targeting, burns, optimization)."""
    text = TWO_BODY.read_text()
    assert "Use `src/twobody.py::TwoBodyCase` and\n   `propagate_cartesian_state`" in text
    assert "do not improvise a result." in text
    assert "Do not claim burn targeting, maneuver execution, optimization, thrust," in text


@pytest.mark.parametrize("skill", (TWO_BODY,))
def test_every_solver_skill_hands_off_to_gmat_verification_before_pass(skill):
    """The remaining deterministic-solver-calling skill explicitly states
    that a result is never PASS without the separate GMAT verification
    handoff (the registered ``run_gmat_verification`` pi tool, TJC-23.1) --
    a solver skill's own candidate output is never, by itself, an
    authoritative/verified result."""
    text = skill.read_text()
    assert "run_gmat_verification" in text
    assert "never" in text.lower() or "not PASS" in text or "not verified" in text.lower()
