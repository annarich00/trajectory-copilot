---
id: TJC-1.19
title: Return a unified numerical and visual verification report
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-12 16:49'
labels: []
dependencies:
  - TJC-1.21
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Define the operator-facing verification contract around GMAT. Numerical comparison, tolerance outcome, trajectory screenshot, model-selection reasoning, discrepancy status, and trust guidance must be returned together rather than scattered across repository files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The structured result includes GMAT version/run identity, compared states or trajectory quantities, units, tolerances, measured discrepancies, and PASS/WARNING/FAIL status
- [x] #2 The result includes a directly accessible screenshot artifact reference with media type, path or URI, caption, and case/run association
- [x] #3 Missing numerical output, failed GMAT execution, or missing screenshot cannot produce PASS
- [x] #4 The human-readable report distinguishes solver success from independent verification success and explains likely discrepancy causes when supported by evidence
- [x] #5 Tests cover agreement, tolerance warning, disagreement, GMAT failure, and missing/corrupt screenshot cases
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #5 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #6 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #7 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/verification_report.py with ScreenshotArtifact + UnifiedVerificationReport frozen dataclasses and assemble_verification_report(...), which takes the already-computed GMATAvailability/GMATRunResult/GMATComparisonResult/ScreenshotResult pieces plus CW solution metadata and (a) assembles every AC1 field (GMAT version/run identity, compared states, units, tolerances, measured discrepancies, PASS/WARNING/FAIL status) and AC2 field (screenshot media type/path/caption/case+run association) together, and (b) hard-enforces AC3 by raising ValueError if a caller tries to claim PASS without a passing numeric comparison, successful GMAT execution, parsed GMAT output, and a valid screenshot all simultaneously present.
2. Add UnifiedVerificationReport.to_human_readable() satisfying AC4: explicitly distinguishes 'CW/two-body solver succeeded' (targeting conveged) from 'GMAT independently verified it' (comparison PASS), and explains likely discrepancy causes (small-margin WARNING/FAIL -> numerical/integrator precision; large-margin FAIL -> probable frame/unit/convention mismatch).
3. Wire scripts/run_cw_gmat_slice.py to call assemble_verification_report(...) at every exit path (CW_TARGETING_INFEASIBLE, MISSING_GMAT, EXECUTION_ERROR, MALFORMED_OUTPUT, NUMERICAL_DISAGREEMENT, SCREENSHOT_FAILURE, VERIFIED) and embed the resulting dict under a new top-level 'unified_verification_report' key in verification_result.json, plus write a sibling verification_report.txt with the human-readable text and reference its path -- without changing any existing top-level field name/shape the current 18 tests depend on.
4. Add tests/test_verification_report.py covering: assemble success (PASS) incl. invariant enforcement raising on inconsistent PASS claims; WARNING; FAIL (disagreement); each GMAT-failure mode (MISSING_GMAT/EXECUTION_ERROR/MALFORMED_OUTPUT) refusing PASS; missing/corrupt screenshot refusing PASS; and to_human_readable() content assertions (solver-vs-GMAT distinction, discrepancy-cause text). Extend tests/test_cw_gmat_slice.py minimally to assert the new unified_verification_report key/shape is present in each existing failure-mode fixture without removing any existing assertion.
5. Update site/js/pages/cw-gmat-slice.js with a new section describing the unified report structure (fields, status enum, screenshot artifact contract) and the solver-vs-verification distinction; add src/verification_report.py and tests/test_verification_report.py to tools/sync_site_data.py MAPPINGS and run it; add a new TJC-1.19 entry at the top of site/data/project-progress.js Completed list without touching existing entries.
6. Run .venv/bin/python -m pytest -q (expect no regressions, all new tests passing); smoke-check ./run_site.sh on an unused port and curl the changed route; run tools/sync_site_data.py --check and tools/compare_upstream.py --check.
7. Backlog finalization (--check-ac 1-5, --check-dod 1-7, --append-notes, --final-summary, -s Done), then git add -A (scoped) + commit TJC-1.19: <summary>, amending if finalization edits land after the first commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added src/verification_report.py (UnifiedVerificationReport dataclass + ScreenshotArtifact + assemble_verification_report()). Wired into every exit path of scripts/run_cw_gmat_slice.py via a new _finish() helper, embedding the result under a new unified_verification_report key in verification_result.json and writing a sibling verification_report.txt. AC3 is re-enforced at construction time: assemble_verification_report() raises ValueError if verified=True is requested without GMAT attempted+exit 0+parsed final state+PASS comparison+valid screenshot all simultaneously true. AC4's to_human_readable() explicitly separates 'the CW solver succeeded' from 'GMAT independently verified it' and explains WARNING (likely numerical/integrator precision) vs FAIL (likely frame/unit mismatch) discrepancy causes. Added tests/test_verification_report.py (23 new tests: PASS/WARNING/FAIL, each of MISSING_GMAT/EXECUTION_ERROR/MALFORMED_OUTPUT, missing/corrupt screenshot refusing PASS via ValueError, and human-readable-text assertions) and extended the existing 6 outcome fixtures in tests/test_cw_gmat_slice.py with unified_verification_report assertions, preserving every original assertion. Test command: .venv/bin/python -m pytest -q -> 91 passed (68 pre-existing + 23 new), including the real end-to-end GmatConsole-R2026a run reaching a real VERIFIED unified report. Updated site/js/pages/cw-gmat-slice.js with a new section 7 describing the unified report fields/invariant/human-readable distinction; added src/verification_report.py and tests/test_verification_report.py to tools/sync_site_data.py MAPPINGS and ran it (36 mappings synchronized, --check clean); added a new TJC-1.19 entry at the top of site/data/project-progress.js Completed list without touching the existing TJC-2/TJC-1.21/TJC-1.14/TJC-1.15/TJC-1.26 entries. ./run_site.sh smoke-checked on port 4295: /, /js/pages/cw-gmat-slice.js, /data/src/verification_report.py, /data/tests/test_verification_report.py, /data/project-progress.js all returned HTTP 200. tools/compare_upstream.py --check reports 'content-different unaccounted: none'. examples/ and evaluations/ were deliberately left untouched per the stated scope boundary (parallel TJC-1.9 benchmark-fixture work).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added src/verification_report.py: a single assemble_verification_report() entry point and UnifiedVerificationReport frozen dataclass that formalizes scripts/run_cw_gmat_slice.py's prior ad hoc verification_result.json dict assembly into one explicit, always-fully-populated structure. Every outcome now carries together: GMAT version/run identity, compared CW/GMAT final states with declared units and tolerances, measured position/velocity discrepancies and the PASS/WARNING/FAIL/INCOMPLETE comparison status (AC1), and a screenshot artifact reference with explicit media_type (image/svg+xml or image/png), path, caption, and case_id/run_id association (AC2). The construction-time invariant re-enforces AC3: requesting verified=True without GMAT actually attempted, exiting 0, producing a parsed final state, comparing PASS, and having a valid screenshot raises ValueError immediately. UnifiedVerificationReport.to_human_readable() satisfies AC4 by explicitly distinguishing 'the CW solver succeeded' from 'GMAT independently verified it' and explaining likely discrepancy causes (WARNING -> likely numerical/integrator precision; FAIL -> likely frame/unit/convention mismatch). Wired into every one of scripts/run_cw_gmat_slice.py's 7 exit paths without changing any pre-existing top-level JSON field. Verified with .venv/bin/python -m pytest -q: 91 passed (68 pre-existing regression tests unchanged + 23 new tests in tests/test_verification_report.py covering AC5's required agreement/warning/disagreement/each-GMAT-failure-mode/missing-corrupt-screenshot cases), including a real end-to-end GmatConsole-R2026a run reaching a genuine VERIFIED unified report. Site updated (new cw-gmat-slice.js section, sync_site_data.py mappings, project-progress.js TJC-1.19 entry); ./run_site.sh smoke-checked (HTTP 200 on all changed/new routes); tools/sync_site_data.py --check and tools/compare_upstream.py --check both report no unaccounted drift.
<!-- SECTION:FINAL_SUMMARY:END -->
