---
id: TJC-1.16
title: Harden the complete workflow after the early vertical slice
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-12 19:08'
labels: []
dependencies:
  - TJC-1.7
  - TJC-1.12
  - TJC-1.14
  - TJC-1.15
  - TJC-1.19
  - TJC-1.21
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the thin CW/GMAT slice works, connect the narrowed formalizer, assumption-based model selector, deterministic CW and two-body paths, GMAT verification, screenshot artifact, discrepancy handling, and explanation into the semester prototype. Reuse the slice rather than replacing it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Supported complete requests traverse formalization, selection, deterministic solution, GMAT verification, screenshot return, and explanation
- [x] #2 Ambiguous requests stop before physics execution and return focused clarification questions
- [x] #3 CW-invalid supported cases route to the two-body fallback and still receive GMAT verification
- [x] #4 Numerical disagreement, missing screenshot, GMAT execution failure, and unsupported requests produce distinct non-authoritative outcomes
- [x] #5 Execution records specified facts, assumptions, model reasoning, tool inputs/outputs, tolerances, artifacts, and final trust statement
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
1. Refactor scripts/run_cw_gmat_slice.py: extract a reusable run_cw_rendezvous_gmat_verification(case_dict, output_dir, gmat_executable, gmat_gui_executable, skip_gui_screenshot, timeout_s) helper that performs the solve->script-gen->GMAT-run->parse->compare->screenshot->assemble-report pipeline and returns (result_dict, returncode) WITHOUT writing files; main() calls it then writes verification_result.json/verification_report.txt as before. CLI behavior/tests unchanged.
2. Add src/workflow.py with a StructuredCase dataclass (readiness: READY_TO_SOLVE/NEEDS_CLARIFICATION/OUT_OF_SCOPE, clarification_questions, plus the ModelSelectionCase-shaped fields needed for model_selector) and run_rendezvous_workflow(case) that: (a) short-circuits on NEEDS_CLARIFICATION/OUT_OF_SCOPE readiness before calling model_selector or any physics; (b) calls select_model; (c) for 'CW rendezvous' selection, calls the refactored run_cw_rendezvous_gmat_verification helper; (d) for 'bounded two-body fallback', propagates with src/twobody.py and runs an equivalent GMAT verification (reusing src/gmat_verify.py's generate/run/parse/compare, generating a simple inertial-frame report script analogous to scripts/generate_benchmark_gmat_evidence.py's two-body case) producing a UnifiedVerificationReport via assemble_verification_report; (e) for UNSUPPORTED/NEEDS MORE INFORMATION, returns an explicit non-authoritative result with no GMAT/physics execution; (f) always records facts/assumptions/model-selection reasoning/tool inputs-outputs/tolerances/artifact paths/trust statement.
3. Add tests/test_workflow.py covering: happy-path VERIFIED, needs-clarification short-circuit (asserts no cw/model_selector/gmat calls happen), CW-invalid routed to two-body with GMAT verification still attempted, NUMERICAL_DISAGREEMENT, missing-GMAT, GMAT execution error, malformed GMAT output, screenshot failure, unsupported/out-of-scope.
4. Run full test suite + tools/compare_upstream.py --check + tools/sync_site_data.py (if present) + run_site.sh smoke test of changed/added routes.
5. Update site/data mirrors (site/data/project-progress.js entry only for TJC-1.16, plus data/src|tests mirrors for new/changed files) keeping them non-authoritative.
6. Finalize Backlog (check ACs/DoD with evidence, final summary, Done) and make one atomic commit 'TJC-1.16: ...'.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation: refactored scripts/run_cw_gmat_slice.py's main() into a reusable run_cw_rendezvous_gmat_verification(case, output_dir, gmat_executable=, gmat_gui_executable=, skip_gui_screenshot=, timeout_s=) helper returning (result_dict, returncode) without writing files; main() now calls it then writes verification_result.json/verification_report.txt as before -- CLI behavior and all 18 existing tests/test_cw_gmat_slice.py tests unchanged (verified: ran that file alone, 18 passed). Added src/gmat_verify.py::generate_two_body_coast_script/parse_inertial_report (shared _parse_report_columns helper factored out of the existing parse_gmat_report) generalizing scripts/generate_benchmark_gmat_evidence.py's benchmark-case-c inertial-report logic for reuse. Added src/workflow.py: RendezvousCase/WorkflowResult dataclasses and run_rendezvous_workflow(case, output_dir=, gmat_executable=) implementing: (1) readiness short-circuit (NEEDS_CLARIFICATION/OUT_OF_SCOPE return before select_model or any physics/GMAT call -- enforced in tests via monkeypatch raising AssertionError if those paths are touched); (2) select_model dispatch; (3) CW path reuses run_cw_rendezvous_gmat_verification; (4) bounded-two-body-fallback path propagates with src.twobody.propagate_cartesian_state then runs its own GMAT verification cycle (check_gmat_available/run_gmat_script/parse_inertial_report/compare_gmat_final_state) assembled via assemble_verification_report -- never skipped; (5) UNSUPPORTED/NEEDS MORE INFORMATION return explicit non-authoritative results with zero physics/GMAT calls. Added tests/test_workflow.py (14 tests covering every required outcome branch: happy-path MISSING_GMAT and fake-GMAT VERIFIED, needs-clarification and out-of-scope short-circuits, CW-invalid routed to two-body fallback both with MISSING_GMAT and with fake-GMAT VERIFIED, NUMERICAL_DISAGREEMENT, EXECUTION_ERROR, MALFORMED_OUTPUT, SCREENSHOT_FAILURE, UNSUPPORTED, NEEDS MORE INFORMATION, and an AC5 record-shape test). Updated tools/sync_site_data.py MAPPINGS to add src/workflow.py and tests/test_workflow.py, ran it to sync site/data mirrors, and updated site/data/project-progress.js with a new TJC-1.16 entry (did not touch any other task's entry).

Verification commands run from repo root after python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt:
- .venv/bin/python -m pytest -q  -> '116 passed' (102 pre-existing + 14 new tests/test_workflow.py, zero regressions)
- .venv/bin/python -m pytest -q tests/test_cw_gmat_slice.py -> '18 passed' (confirms the run_cw_gmat_slice.py refactor preserved its existing CLI/test contract exactly)
- python3 tools/compare_upstream.py --check -> exit 0, 'content-different unaccounted: none'
- python3 tools/sync_site_data.py --check -> 'site data mirrors match (49 mappings)' (after running tools/sync_site_data.py once to pick up src/gmat_verify.py, scripts/run_cw_gmat_slice.py, src/workflow.py, tests/test_workflow.py)
- ./run_site.sh 4199 then curl-smoke: / (200), /index.html (200), /data/project-progress.js (200, contains 'TJC-1.16' x4), /data/src/workflow.py (200), /data/tests/test_workflow.py (200), /data/src/gmat_verify.py (200), /data/scripts/run_cw_gmat_slice.py (200), /js/pages/model-selector.js (200), /js/pages/cw-gmat-slice.js (200), /js/pages/targeting.js (200), /js/pages/progress.js (200); server then stopped.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Connected the narrowed formalizer's structured readiness check, src/model_selector.py's assumption-based model selection, the deterministic CW (src/cw.py) and bounded two-body (src/twobody.py) paths, and GMAT verification (src/gmat_verify.py, src/verification_report.py) into one workflow entrypoint, src/workflow.py::run_rendezvous_workflow. Reused rather than duplicated the existing vertical slice: refactored scripts/run_cw_gmat_slice.py's main() into a reusable run_cw_rendezvous_gmat_verification() helper (returns (result, returncode), no file writes) that both main() and src/workflow.py call. A NEEDS_CLARIFICATION/OUT_OF_SCOPE case returns immediately with no model-selection/physics/GMAT execution (AC2, verified by tests that raise AssertionError if those paths run). A CW selection reaches VERIFIED or an explicit NOT VERIFIED reason through the full solve->GMAT->screenshot->explanation pipeline (AC1). A CW-invalid-but-supported case routes to the two-body fallback and still receives a genuine GMAT verification attempt via new src/gmat_verify.py::generate_two_body_coast_script/parse_inertial_report support (AC3, verified both as MISSING_GMAT and as a fake-GMAT VERIFIED outcome). NUMERICAL_DISAGREEMENT, MISSING_GMAT, EXECUTION_ERROR, MALFORMED_OUTPUT, SCREENSHOT_FAILURE, and UNSUPPORTED/NEEDS MORE INFORMATION are each distinct, explicitly labeled, never-silently-passing outcomes (AC4). Every WorkflowResult.to_dict() carries assumptions, model-selection reasoning, exact tool inputs/outputs, tolerances, artifact paths, and a trust statement distinguishing solver success from independent GMAT verification (AC5). Added tests/test_workflow.py (14 tests, one per required branch). Verified: .venv/bin/python -m pytest -q -> 116 passed (102 pre-existing + 14 new, zero regressions); tests/test_cw_gmat_slice.py alone -> 18 passed (refactor preserved existing CLI/test contract); tools/compare_upstream.py --check -> exit 0, no unaccounted drift; tools/sync_site_data.py --check -> mirrors match after adding src/workflow.py/tests/test_workflow.py to its MAPPINGS and running the sync; ./run_site.sh smoke-tested changed/added routes and data files (all 200), server stopped afterward. Updated site/data/project-progress.js with a new TJC-1.16 entry only, leaving every other task's entry untouched.
<!-- SECTION:FINAL_SUMMARY:END -->
