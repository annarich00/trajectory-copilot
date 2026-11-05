---
id: TJC-11
title: >-
  Build a subagent-readable GMAT example corpus file from the collected
  open-source scripts
status: Done
assignee:
  - '@worker'
created_date: '2026-10-28 13:33'
updated_date: '2026-11-05 16:50'
labels: []
dependencies:
  - TJC-10
priority: low
type: task
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up to TJC-10 (research/collection). TJC-10 collects raw open-source GMAT script examples with provenance but leaves them as loose files/notes under a research-staging location. This task is the second subagent's job: take that raw collection and transform it into one (or a small number of) structured, machine-readable file(s) -- e.g. a JSON array keyed by mission type/formatting convention, with fields for source URL, license, mission type, a short description, and the normalized script text or a pointer to it -- that the planned 'GMAT example subagent' (see the separate task defining that subagent) can actually load and search at runtime. The two tasks are deliberately separated: TJC-10 is open-ended internet research with no fixed output shape, while this task defines and enforces a fixed, validated schema so the consuming subagent has a stable contract instead of parsing arbitrary scraped text.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A versioned schema for the corpus file is defined and documented (fields: source URL, license/attribution status, mission type, formatting/convention tags, description, and the example content or a stable path to it)
- [x] #2 Every entry collected in TJC-10 that was not flagged as unknown/incompatible license is represented in the corpus file; entries flagged unknown/incompatible in TJC-10 are either excluded or explicitly marked non-redistributable in the corpus file, never silently included as if clear
- [x] #3 The corpus file is schema-validated by an automated check (a small script or test) that fails if a required field is missing or a license-flagged entry is marked redistributable
- [x] #4 The corpus file lives in a location the planned GMAT example subagent's definition can reference directly (coordinate the exact path with that task so the two do not drift)
- [x] #5 A short README alongside the corpus file documents how to regenerate/update it when TJC-10's collection is refreshed, and records the schema version
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-11:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define corpus path research/gmat_example_corpus/ (corpus.json + SCHEMA.md + README.md); coordinate with TJC-14 via implementation notes.
2. Red-first: write tests/test_gmat_example_corpus.py (schema validity of committed corpus, missing-required-field failure, license-flagged-redistributable failure, unflagged-entry coverage vs TJC-10 log/raw dir, content hash/path checks, regeneration determinism) and run it failing before the builder/validator exist.
3. Implement src/gmat_example_corpus.py (schema version, validate_corpus) and scripts/build_gmat_example_corpus.py (metadata table + auto-detected convention tags -> corpus.json). nasa/GMAT (Apache-2.0) entries: redistributable=true with stable content_path + sha256; license-unknown entries (B,C,D): redistributable=false, metadata only, no content/path.
4. Generate corpus.json, write SCHEMA.md and README.md (regeneration steps, schema version).
5. Run full suite (baseline 206 passed), record red/green + results, finalize AC/DoD, mark Done, one commit TJC-11: ... (amend for metadata).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Corpus path chosen (for TJC-14 to reference, do not drift): research/gmat_example_corpus/corpus.json (schema: research/gmat_example_corpus/SCHEMA.md, README: research/gmat_example_corpus/README.md, schema version 1.0.0). Redistributable entries expose script text via content_path; non-redistributable entries have content_path null (metadata only). Validator: src/gmat_example_corpus.py::validate_corpus; builder: scripts/build_gmat_example_corpus.py (--check for staleness).

Design decision: 12 nasa/GMAT Apache-2.0 entries redistributable=true; 6 license-unknown entries (sources B/C/D) kept as metadata-only (redistributable=false, content_path=null) rather than excluded, so TJC-14 can still cite mission type/tags/URL but never quotes their text. Raw copies remain under research/gmat_examples_raw/ from TJC-10 (unchanged).

TDD red: .venv/bin/python -m pytest tests/test_gmat_example_corpus.py -q (test written first, before src/gmat_example_corpus.py, scripts/build_gmat_example_corpus.py and corpus existed) -> collection ERROR: ModuleNotFoundError: No module named 'scripts.build_gmat_example_corpus' (1 error). Intermediate red after validator+builder but before corpus.json/README: 1 failed, 23 errors (FileNotFoundError corpus.json / README.md). Green: same command -> 24 passed in 0.35s. Mutation checks: disabling the redistributable-license rule made test_license_flagged_entry_marked_redistributable_fails_validation fail (after tightening it to isolate the license rule); disabling the missing-field check made 9 tests fail; both restored -> 24 passed.

Full suite (env: uv venv .venv + requirements-dev.txt, Python 3.12.14): baseline before changes 206 passed (2m45s). After: first run 1 failed, 229 passed -- tests/test_cw_gmat_slice.py::test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window failed (Xvfb screenshot, unrelated; passed 25/25 when rerun alone); second full run -> 230 passed in 152.13s. Running the suite rewrites evidence/poliastro/contract-test-evidence.json; reverted with git checkout, not part of this commit. scripts/build_gmat_example_corpus.py --check -> up to date.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added versioned (1.0.0) GMAT example corpus at research/gmat_example_corpus/corpus.json with SCHEMA.md and README.md (regeneration steps, schema version), validator src/gmat_example_corpus.py, builder scripts/build_gmat_example_corpus.py, and tests/test_gmat_example_corpus.py (24 tests, red-then-green recorded). All 18 TJC-10 scripts represented: 12 Apache-2.0 nasa/GMAT entries redistributable with content_path; 6 license-unknown entries metadata-only (redistributable=false, content_path=null). Verified: 24 new tests pass; full suite 230 passed (one unrelated flaky Xvfb screenshot failure on a first run, passed on rerun); builder --check up to date.
<!-- SECTION:FINAL_SUMMARY:END -->
