"""Static checks for the GMAT-example reviewer subagent definition (TJC-14).

``.pi/agents/gmat-example-reviewer.md`` is a project-local pi-subagents agent
file. These tests do not run a model; they check that the committed file
parses as ``--- frontmatter --- body`` and that its system prompt contains the
scope, non-verification, corpus-citation, no-entry and verdict-format
statements TJC-14's acceptance criteria require, and that the corpus path it
references is the real TJC-11 corpus file.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gmat_example_corpus import CORPUS_RELATIVE_PATH  # noqa: E402

AGENT_PATH = ROOT / ".pi/agents/gmat-example-reviewer.md"
SKILL_PATH = ".pi/skills/gmat-rendezvous-verification/SKILL.md"
WRITE_TOOLS = {"bash", "edit", "write"}


def _split_agent_file(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, flags=re.DOTALL)
    assert match, "agent file must be '---' frontmatter '---' followed by a system prompt"
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        assert sep, f"frontmatter line is not 'key: value': {line!r}"
        frontmatter[key.strip()] = value.strip()
    return frontmatter, match.group(2)


@pytest.fixture()
def agent() -> tuple[dict[str, str], str]:
    assert AGENT_PATH.is_file(), f"missing project-local agent definition: {AGENT_PATH}"
    return _split_agent_file(AGENT_PATH.read_text())


def test_frontmatter_names_the_agent_and_describes_review_only_scope(agent):
    frontmatter, body = agent
    assert frontmatter["name"] == "gmat-example-reviewer"
    description = frontmatter["description"].lower()
    assert "format" in description and "convention" in description
    assert "not" in description and "numerical" in description
    assert body.strip()


def test_tools_are_a_read_only_allowlist(agent):
    frontmatter, _ = agent
    tools = {tool.strip() for tool in frontmatter["tools"].split(",")}
    assert {"read", "grep"} <= tools
    assert not tools & WRITE_TOOLS


def test_prompt_scopes_to_formatting_structure_convention_review(agent):
    _, body = agent
    lowered = body.lower()
    assert "gmat scripting expert" in lowered
    for word in ("formatting", "structure", "convention"):
        assert word in lowered


def test_prompt_disclaims_numerical_and_screenshot_verification(agent):
    _, body = agent
    lowered = body.lower()
    assert "not a numerical" in lowered
    assert "screenshot" in lowered
    assert SKILL_PATH in body
    assert "sole source of pass/fail" in lowered
    assert re.search(r"never (report|emit|state)[^.]*\bpass\b", lowered)


def test_prompt_references_the_real_corpus_file_and_schema(agent):
    _, body = agent
    assert CORPUS_RELATIVE_PATH in body
    corpus_path = ROOT / CORPUS_RELATIVE_PATH
    assert corpus_path.is_file()
    corpus = json.loads(corpus_path.read_text())
    assert f'"{corpus["schema_version"]}"' in body or corpus["schema_version"] in body
    assert "research/gmat_example_corpus/SCHEMA.md" in body


def test_prompt_requires_citing_specific_corpus_entry_ids(agent):
    _, body = agent
    lowered = body.lower()
    assert "cite" in lowered
    assert "entry id" in lowered
    assert "unsourced" in lowered
    corpus = json.loads((ROOT / CORPUS_RELATIVE_PATH).read_text())
    cited_ids = [e["id"] for e in corpus["entries"] if e["id"] in body]
    assert cited_ids, "prompt/example guidance should name at least one real corpus entry id"
    assert set(cited_ids) <= {e["id"] for e in corpus["entries"]}


def test_prompt_requires_explicit_no_corpus_entry_statement(agent):
    _, body = agent
    assert "NO CORPUS ENTRY" in body
    lowered = body.lower()
    assert "fabricat" in lowered
    assert "mission_type" in body


def test_prompt_forbids_quoting_non_redistributable_entries(agent):
    _, body = agent
    assert "redistributable" in body
    assert "content_path" in body
    assert re.search(r"never (quote|reproduce)", body.lower())


def test_prompt_defines_short_structured_verdict(agent):
    _, body = agent
    assert "SATISFACTORY" in body and "DIVERGENT" in body
    for label in ("Verdict:", "Mission type:", "Corpus entries cited:", "Divergences:"):
        assert label in body
