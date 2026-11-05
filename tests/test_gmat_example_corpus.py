"""Schema-validation tests for the GMAT example corpus (TJC-11).

``research/gmat_example_corpus/corpus.json`` is the stable, versioned contract
the planned GMAT-example reviewer subagent (TJC-14) loads at runtime. These
tests enforce that contract: required fields, the license rule (a
license-flagged entry can never be marked redistributable), coverage of every
TJC-10 collected script, and regeneration determinism.
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_gmat_example_corpus import build_corpus  # noqa: E402
from src.gmat_example_corpus import (  # noqa: E402
    CORPUS_RELATIVE_PATH,
    ENTRY_REQUIRED_FIELDS,
    SCHEMA_VERSION,
    validate_corpus,
)

CORPUS_PATH = ROOT / CORPUS_RELATIVE_PATH
RAW_DIR = ROOT / "research/gmat_examples_raw"
LOG_PATH = ROOT / "research/gmat_examples_log.md"
README_PATH = CORPUS_PATH.parent / "README.md"


@pytest.fixture()
def corpus() -> dict:
    return json.loads(CORPUS_PATH.read_text())


def _first(corpus: dict, redistributable: bool) -> dict:
    return next(e for e in corpus["entries"] if e["redistributable"] is redistributable)


def test_committed_corpus_is_schema_valid(corpus):
    assert corpus["schema_version"] == SCHEMA_VERSION
    assert validate_corpus(corpus, ROOT) == []


@pytest.mark.parametrize("field", ENTRY_REQUIRED_FIELDS)
def test_missing_required_entry_field_fails_validation(corpus, field):
    broken = copy.deepcopy(corpus)
    del broken["entries"][0][field]
    errors = validate_corpus(broken, ROOT)
    assert any(field in error for error in errors), errors


def test_missing_schema_version_fails_validation(corpus):
    broken = copy.deepcopy(corpus)
    del broken["schema_version"]
    assert validate_corpus(broken, ROOT)


def test_license_flagged_entry_marked_redistributable_fails_validation(corpus):
    broken = copy.deepcopy(corpus)
    flagged = _first(broken, redistributable=False)
    assert flagged["license"]["status"] == "unknown"
    flagged["redistributable"] = True
    flagged["content_path"] = flagged["raw_source_path"]  # isolate the license rule
    errors = validate_corpus(broken, ROOT)
    assert any("license is not clear" in error for error in errors), errors


def test_non_redistributable_entry_must_not_expose_content_path(corpus):
    broken = copy.deepcopy(corpus)
    flagged = _first(broken, redistributable=False)
    flagged["content_path"] = flagged["raw_source_path"]
    assert validate_corpus(broken, ROOT)


def test_redistributable_entry_content_hash_mismatch_fails_validation(corpus):
    broken = copy.deepcopy(corpus)
    _first(broken, redistributable=True)["content_sha256"] = "0" * 64
    assert any("sha256" in error for error in validate_corpus(broken, ROOT))


def test_unknown_mission_type_or_tag_fails_validation(corpus):
    broken = copy.deepcopy(corpus)
    broken["entries"][0]["mission_type"] = "not_a_mission_type"
    broken["entries"][1]["convention_tags"] = ["not_a_tag"]
    errors = validate_corpus(broken, ROOT)
    assert any("mission_type" in e for e in errors)
    assert any("convention_tags" in e for e in errors)


def test_duplicate_entry_ids_fail_validation(corpus):
    broken = copy.deepcopy(corpus)
    broken["entries"][1]["id"] = broken["entries"][0]["id"]
    assert any("duplicate" in e for e in validate_corpus(broken, ROOT))


def test_every_collected_script_is_represented(corpus):
    collected = {
        p.relative_to(ROOT).as_posix() for p in RAW_DIR.rglob("*.script")
    }
    assert len(collected) == 18
    assert {e["raw_source_path"] for e in corpus["entries"]} == collected


def test_entries_match_tjc10_log_urls_and_license_flags(corpus):
    log = LOG_PATH.read_text()
    log_entries = re.findall(
        r"- URL: (\S+)\n\s+- License: (.+)", log
    )
    assert len(log_entries) == 18
    by_url = {e["source_url"]: e for e in corpus["entries"]}
    assert set(by_url) == {url for url, _ in log_entries}
    for url, license_line in log_entries:
        entry = by_url[url]
        if license_line.startswith("Apache-2.0"):
            assert entry["license"]["status"] == "clear"
            assert entry["license"]["spdx_id"] == "Apache-2.0"
            assert entry["redistributable"] is True
        else:
            assert license_line.startswith("unknown/unclear")
            assert entry["license"]["status"] == "unknown"
            assert entry["redistributable"] is False
            assert entry["content_path"] is None


def test_redistributable_entries_point_at_existing_script_text(corpus):
    redistributable = [e for e in corpus["entries"] if e["redistributable"]]
    assert len(redistributable) == 12
    for entry in redistributable:
        assert (ROOT / entry["content_path"]).read_text().strip()


def test_corpus_regeneration_is_deterministic_and_matches_committed_file(corpus):
    assert build_corpus(ROOT) == corpus


def test_readme_records_schema_version_and_regeneration_command():
    readme = README_PATH.read_text()
    assert f"Schema version: {SCHEMA_VERSION}" in readme
    assert "scripts/build_gmat_example_corpus.py" in readme
