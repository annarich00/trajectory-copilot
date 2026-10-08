---
id: TJC-1.3
title: Independently audit the CW state-transition implementation
status: Done
assignee:
  - '@pi'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-08 18:40'
labels: []
dependencies:
  - TJC-1.25
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: task
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The CW state-transition matrix is foundational and must be reviewed against an authoritative derivation rather than validated only by its own tests. Check each block, state ordering, signs, dimensions, time-zero behavior, and circular-chief assumptions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An audit note maps every implemented STM term to an independently cited equation
- [x] #2 The implementation uses the documented state ordering and LVLH convention consistently
- [x] #3 At t=0 the STM is identity within a stated numerical tolerance
- [x] #4 Any sign, unit, or equation defect found by the audit is corrected and covered by a regression test
- [x] #5 The CW assumptions and unsupported regimes are visible in code-facing documentation
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Update the CW STM lesson with a step-by-step derivation of every matrix block, symbol definitions, axis/sign conventions, and term-level links to `src/cw.py` and its tests.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the CW implementation, existing reference material, tests, site lessons, and relevant upstream conventions.
2. Independently map each CW state-transition-matrix block and state convention to cited equations; identify and correct any discrepancy without expanding the scoped model.
3. Add focused regression/property tests for identity, block terms, ordering, signs, and documented assumptions.
4. Update authoritative documentation and the CW STM educational lesson, synchronize mirrors, and run code/site/repository checks.
5. Record objective evidence, finalize Backlog, and make exactly one atomic TJC-1.3 commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Audit conclusion: src/cw.py::cw_stm matches Clohessy & Wiltshire (1960), Eqs. 1–3 and the circular-chief block solution in Schaub & Junkins (2018), §14.6, Eqs. 14.48–14.51; no STM equation defect found. Added docs/cw-stm-audit.md, explicit code/reference conventions, zero-time identity (atol 1e-15), and quarter-orbit all-block sign/unit regressions. Validation passed: .venv/bin/python -m pytest -q tests/test_cw.py (5 passed); .venv/bin/python -m pytest -q (21 passed); python3 tools/sync_site_data.py --check; python3 tools/compare_upstream.py --check; node --check site/js/pages/cw-stm.js and site/data/project-progress.js; git diff --check; offline ./run_site.sh/curl smoke served index, CW lesson, mirrored source/tests, and progress artifact.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed the independent circular-chief CW STM audit. The implementation matches cited equations; no sign, unit, ordering, or time-zero defect was found. Added durable audit/citations, focused identity and all-block regression tests, code-facing conventions/limits, synchronized mirrors, detailed CW STM educational lesson, and traceable site progress entry. Verified focused/full pytest, mirror and upstream checks, syntax/diff checks, and offline site smoke.
<!-- SECTION:FINAL_SUMMARY:END -->
