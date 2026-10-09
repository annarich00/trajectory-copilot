---
id: TJC-1.20
title: Build an early CW-to-GMAT vertical slice with screenshot capture
status: Done
assignee:
  - '@pi'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-09 13:49'
labels: []
dependencies:
  - TJC-1.25
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Immediately prove the riskiest end-to-end path using one recovered, well-specified CW rendezvous case. Reuse existing formalization/physics components as-is where possible: load or form the structured case, run deterministic CW targeting, generate and execute GMAT, compare results, capture a trajectory visualization, and return one combined report. Hardening and broader benchmark coverage come later.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 One well-specified circular-LEO CW case runs from structured input through deterministic CW solution and an automatically generated GMAT script
- [x] #2 The supported GMAT executable is invoked non-interactively or through a documented automatable mechanism and its exit status and outputs are captured
- [x] #3 The slice compares at least final position, final velocity, and maneuver delta-v using explicit units and provisional tolerances
- [x] #4 The run automatically produces a non-empty orbit/trajectory screenshot or plot and returns it in the verification result, not only as an undocumented repository file
- [x] #5 A single documented command reproduces the complete slice and reports failures without claiming verification
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Publish an early vertical-slice demo page that traces the selected case from input through CW code, generated GMAT script, numerical comparison, and returned trajectory screenshot.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the recovered CW solver, verification interfaces, examples, and static-site conventions to identify the smallest end-to-end seam.
2. Add one schema-backed circular-LEO case runner that deterministically solves CW targeting, emits a GMAT script, invokes a configurable GMAT executable non-interactively with captured evidence, compares state and delta-v using explicit provisional tolerances, and creates a returned trajectory plot artifact even when GMAT is unavailable.
3. Add focused tests and one documented reproduction command, then update the educational site and mirrored source material for the vertical-slice demo.
4. Run unit/repository/site/offline smoke checks, record objective evidence, finalize the task, and create one atomic TJC-1.20 commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the fixed 350 km circular-LEO quarter-orbit CW rendezvous vertical slice. The runner generates a GMAT script, invokes a configured GMAT executable through subprocess with captured exit/stdout/stderr, writes an SVG trajectory artifact and returned JSON report, and reports NOT VERIFIED when GMAT is missing/fails/unparseable. Objective validation: .venv/bin/python -m pytest -q (22 passed); offline smoke runner with --gmat definitely-not-gmat exited 1 and wrote a non-empty trajectory.svg plus NOT VERIFIED result; python3 tools/sync_site_data.py --check; python3 tools/compare_upstream.py --check; ./run_site.sh 4188 with curl smoke of index, new demo route JS, and runner mirror, then server terminated.

Final atomic commit 446dda5 (TJC-1.20: build CW-to-GMAT vertical slice) contains implementation, tests, site updates, synchronized mirrors, and Backlog finalization. git status --short was clean after amend.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TJC-1.20 CW-to-GMAT vertical slice and demo page. Verified deterministic CW targeting, generated GMAT script, noninteractive failure-safe GMAT invocation evidence, explicit comparison tolerances, non-empty returned SVG plot, and truthful NOT VERIFIED behavior without GMAT using 22 passing pytest tests plus offline site/mirror checks.
<!-- SECTION:FINAL_SUMMARY:END -->
