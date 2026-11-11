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

``orbital-two-body-rendezvous``'s SKILL.md was retired by TJC-23.5: its
never-improvise-a-rejected-input and never-claim-burn-targeting/maneuver/
optimization authority boundaries are no longer prose an LLM must follow
voluntarily -- the input-rejection half is now structurally enforced by
``scripts/two_body_tool_bridge.py``'s ``run_bridge`` propagating
``propagate_cartesian_state``'s own ``ValueError`` unchanged (non-finite
inputs, non-positive mu/steps, the zero-radius singularity), exercised
directly by ``tests/test_two_body_tool_bridge.py``'s
``test_run_bridge_rejects_invalid_inputs_without_improvising_a_result``
(TJC-23.5's own red/green coverage, not duplicated here). The
never-claim-unsupported-capabilities and GMAT-verification-handoff halves
are now carried by the registered ``propagate_two_body_coast`` pi tool's
own ``description``/``promptGuidelines`` strings
(``.pi/extensions/two-body-rendezvous-tool/index.ts``) rather than a
Markdown skill file, so they too are no longer part of this module's
prose-only skill-layer coverage.
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parents[1] / ".pi/skills"

MODEL_SELECTOR = SKILLS_DIR / "orbital-model-selector/SKILL.md"

# orbital-problem-formalizer's SKILL.md was retired by TJC-23.2: see the
# module docstring above.
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
#
# orbital-two-body-rendezvous's SKILL.md was retired by TJC-23.5: see the
# module docstring above.
ALL_SKILLS = (MODEL_SELECTOR,)


def test_every_referenced_skill_file_exists():
    """Guard against a stale path if a skill is ever renamed or moved."""
    for skill in ALL_SKILLS:
        assert skill.is_file(), f"missing skill file: {skill}"


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


# test_two_body_skill_requires_the_deterministic_implementation_and_refuses_to_improvise
# and the two-body case of test_every_solver_skill_hands_off_to_gmat_verification_before_pass
# were retired along with orbital-two-body-rendezvous/SKILL.md by TJC-23.5: see
# the module docstring above for where their invariants now live. No skill
# remains in this module's deterministic-solver-calling category, so this
# module keeps no parametrized hands-off-to-GMAT test either.
