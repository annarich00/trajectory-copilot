---
id: TJC-1.21
title: 'Harden GMAT execution, comparison, and screenshot capture'
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-11 23:12'
labels: []
dependencies:
  - TJC-1.6
  - TJC-1.20
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn the proven vertical-slice integration into the narrow reusable verification tool. GMAT remains an independent verifier for supported CW and two-body rendezvous outputs and must always return numerical evidence plus a trajectory visualization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The tool validates the supported GMAT version/location and generates traceable scripts from structured problem and solution data
- [x] #2 It executes GMAT, captures logs/exit status, parses final position, velocity, maneuver delta-v, and trajectory/state history with explicit units
- [x] #3 It compares candidate and GMAT outputs using configured tolerances and returns structured PASS/WARNING/FAIL evidence
- [x] #4 It automatically captures a non-empty orbit/trajectory screenshot or plot and exposes that artifact directly in the returned result
- [x] #5 Missing GMAT, execution errors, malformed output, numerical disagreement, and screenshot failure are distinguishable and never reported as successful verification
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Update the GMAT verification lesson with script-generation mapping, execution flow, parsed outputs, tolerance logic, screenshot capture, artifact return, and failure-state examples.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reuse the proven GMAT script design (confirmed in this environment via real GmatConsole-R2026a runs) to add src/gmat_verify.py: check_gmat_available (invokes --version, checks banner), generate_gmat_script (SI->km/km-s, absolute ReportFile paths, Deputy in LVLH ObjectReferenced CoordinateSystem), run_gmat_script (subprocess+timeout, captures exit/stdout/stderr), parse_gmat_report (strict header/shape/numeric validation), compare_gmat_final_state (PASS/WARNING/FAIL), validate_screenshot (non-empty well-formed SVG).
2. Rewrite scripts/run_cw_gmat_slice.py to call src.cw.solve_cw_rendezvous then src/gmat_verify.py end-to-end, exposing failure_mode in {CW_TARGETING_INFEASIBLE, MISSING_GMAT, EXECUTION_ERROR, MALFORMED_OUTPUT, NUMERICAL_DISAGREEMENT, SCREENSHOT_FAILURE} or verified=true, with the SVG trajectory plot overlaid with real GMAT trajectory points when available.
3. Extend tests/test_cw_gmat_slice.py: keep missing-GMAT/infeasible-targeting tests, add monkeypatched EXECUTION_ERROR/MALFORMED_OUTPUT/NUMERICAL_DISAGREEMENT/SCREENSHOT_FAILURE tests, plus one real end-to-end run against GmatConsole-R2026a asserting the observed PASS.
4. Run pytest to green; sync site data (add src/gmat_verify.py + tests/test_cw_gmat_slice.py mappings); extend site/js/pages/cw-gmat-slice.js with script-generation mapping, execution flow, tolerance logic, screenshot handling, and the 5 failure modes; update site/data/project-progress.js with a new TJC-1.21 entry above TJC-1.14.
5. Smoke-check run_site.sh routes; run sync_site_data.py --check and compare_upstream.py --check; finalize Backlog AC/DoD with evidence; commit as TJC-1.21.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
GMAT found at /home/anna_ford/opt/GMAT/R2026a/bin/GmatConsole-R2026a, confirmed runnable (recognizable --version banner). Implemented src/gmat_verify.py (script gen/exec/parse/compare/screenshot validation) and rewrote scripts/run_cw_gmat_slice.py around it. Real end-to-end run against GmatConsole-R2026a for examples/cw_gmat_vertical_slice.yaml: exit 0, failure_mode=None, verified=true, comparison.status=PASS, position_error_m=0.00794, velocity_error_mps=1.17e-5 (tolerances 1 m / 0.001 m/s). .venv/bin/python -m pytest -q -> 62 passed (12 in tests/test_cw_gmat_slice.py, including the 5 monkeypatched failure-mode tests MISSING_GMAT/EXECUTION_ERROR/MALFORMED_OUTPUT/NUMERICAL_DISAGREEMENT/SCREENSHOT_FAILURE, the earlier CW_TARGETING_INFEASIBLE test, and the real GmatConsole-R2026a end-to-end test). python3 tools/sync_site_data.py --check -> match (32 mappings). python3 tools/compare_upstream.py --check -> exit 0, no unaccounted drift. ./run_site.sh smoke-checked on port 4199: /, /js/pages/cw-gmat-slice.js, /data/src/gmat_verify.py, /data/scripts/run_cw_gmat_slice.py, /data/tests/test_cw_gmat_slice.py, /data/project-progress.js all HTTP 200.

Final commit cc9502c (subject: 'TJC-1.21: harden GMAT execution, comparison, and screenshot capture'); project-progress.js updated to reference that hash and amended into the same commit per task-commit-policy.md.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added src/gmat_verify.py (GMAT availability check, traceable script generation with absolute ReportFile paths, subprocess execution+timeout capture, strict ReportFile parsing to SI units, PASS/WARNING/FAIL final-state comparison, non-empty well-formed-SVG screenshot validation) and rewrote scripts/run_cw_gmat_slice.py to orchestrate src.cw.solve_cw_rendezvous end-to-end through it. Verified with a real GmatConsole-R2026a run of examples/cw_gmat_vertical_slice.yaml: exit 0, GMAT final state vs. CW analytical final state position error 0.0079 m / velocity error 1.17e-5 m/s, both inside the 1 m / 0.001 m/s tolerances -> verified=true. All six distinct failure modes (CW_TARGETING_INFEASIBLE, MISSING_GMAT, EXECUTION_ERROR, MALFORMED_OUTPUT, NUMERICAL_DISAGREEMENT, SCREENSHOT_FAILURE) are independently reproduced by dedicated tests and never produce verified=true. .venv/bin/python -m pytest -q: 62 passed. python3 tools/sync_site_data.py --check and python3 tools/compare_upstream.py --check both exit 0 with no unaccounted drift. ./run_site.sh smoke-checked on port 4199 with all changed/new routes returning HTTP 200. Educational site's GMAT lesson (site/js/pages/cw-gmat-slice.js) and living-progress entry (site/data/project-progress.js) updated and traceable to commit cc9502c.
<!-- SECTION:FINAL_SUMMARY:END -->
