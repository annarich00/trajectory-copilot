from pathlib import Path


SKILL = Path(__file__).parents[1] / ".pi/skills/orbital-problem-formalizer/SKILL.md"
EVALUATIONS = Path(__file__).parents[1] / "evaluations/formalizer"


REQUIRED_SCHEMA_HEADINGS = (
    "### Scope",
    "### Participants",
    "### Reference Orbit",
    "### Relative Frame and State",
    "### Terminal Conditions",
    "### Timing and Maneuvers",
    "### Blocking Issues",
    "### Clarification Questions",
    "### Readiness",
    "### Formalization Summary",
)


def test_formalizer_schema_requires_scoped_inputs_and_provenance():
    skill = SKILL.read_text()

    for heading in REQUIRED_SCHEMA_HEADINGS:
        assert heading in skill
    for field in (
        "Central body",
        "Altitude",
        "Radius or orbital elements",
        "Initial relative position",
        "Initial relative velocity",
        "LVLH convention",
        "Time of flight",
        "Period count",
        "Maneuver assumptions",
        "Requested outputs",
    ):
        assert field in skill
    for label in (
        "`specified`",
        "`derived`",
        "`assumed`",
        "`missing`",
        "`ambiguous`",
        "`contradictory`",
        "`unit-inconsistent`",
    ):
        assert label in skill


def test_complete_scoped_request_has_no_blocking_issue():
    fixture = (EVALUATIONS / "test_02_cw_complete.txt").read_text()

    assert "EXPECTED READINESS:\nREADY TO SOLVE" in fixture
    assert "EXPECTED BLOCKING ISSUES:\nNone" in fixture
    assert "specified" in fixture
    assert "derived" in fixture


def test_incomplete_request_requires_focused_clarifications():
    fixture = (EVALUATIONS / "test_01_underspecified.txt").read_text()

    assert "EXPECTED READINESS:\nNEEDS CLARIFICATION" in fixture
    for question in (
        "Which central body",
        "What circular reference-orbit altitude",
        "Which LVLH axis/sign convention",
        "complete initial relative position and velocity",
    ):
        assert question in fixture


def test_contradictory_request_is_blocked_without_reconciliation():
    fixture = (EVALUATIONS / "test_04_contradictory.txt").read_text()

    assert "EXPECTED READINESS:\nNEEDS CLARIFICATION" in fixture
    assert "contradictory" in fixture
    assert "Do not reconcile the statements" in fixture


def test_unit_inconsistent_request_is_blocked_without_conversion():
    fixture = (EVALUATIONS / "test_05_unit_inconsistent.txt").read_text()

    assert "EXPECTED READINESS:\nNEEDS CLARIFICATION" in fixture
    assert "unit-inconsistent" in fixture
    assert "Do not convert or infer a correction" in fixture
