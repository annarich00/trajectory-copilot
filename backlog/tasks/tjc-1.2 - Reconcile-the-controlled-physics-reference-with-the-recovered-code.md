---
id: TJC-1.2
title: Align the controlled reference and skills to the scoped rendezvous workflow
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
parent_task_id: TJC-1
priority: high
type: docs
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reconcile the recovered reference and Pi skills with the semester architecture. Keep the knowledge boundary focused on problem formulation, CW rendezvous, two-body fallback, model selection, and GMAT verification; remove claims or guidance that imply unsupported generalized astrodynamics or optimization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The controlled reference defines the CW equations, two-body assumptions, units, state ordering, and LVLH convention used by the recovered code
- [x] #2 CW applicability guidance evaluates circularity, locality/separation relative to orbital radius, duration/regime, frame definition, and other documented physical assumptions without declaring a universal learned threshold
- [x] #3 The active skill architecture is limited to problem formulation, CW rendezvous, two-body rendezvous, model selection, and verification, with equivalent naming permitted
- [x] #4 The verification skill requires GMAT numerical comparison and an accessible trajectory screenshot
- [x] #5 References clearly identify unsupported semester capabilities and future-work topics
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Update the site’s controlled-reference guide so each active physics/model-selection claim links to the relevant verbatim `reference/SOURCE.md` section and deterministic implementation.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the controlled reference, skill mirrors, site guides, source explorer, and deterministic implementations for claims outside the semester scope.
2. Rewrite the canonical reference and active skills to document the exact CW/LVLH and bounded two-body contracts, assumption-based selection, GMAT numerical-plus-screenshot verification, and unsupported/future work boundaries.
3. Synchronize browser mirrors and educational site/progress evidence, preserving their non-authoritative labels and traceability.
4. Run repository tests, dependency-free site checks and local changed-route smoke tests; record objective results, finalize Backlog, and create one TJC-1.2 commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented controlled reference §§A–F and five scoped skills (formulation, selection, fixed-duration CW, bounded two-body coast, GMAT verification). Removed active optimization/general-solver guidance and explicitly labeled unsupported/future capabilities.

Objective validation: `python3 tools/sync_site_data.py --check` passed (23 mappings); `node --check site/js/pages/source-explorer.js`, `model-validity.js`, and `verification.js` passed; `git diff --check` passed; `PORT=4174 ./run_site.sh` served offline and curl smoke checks returned HTTP 200 for /, all changed reference/skill mirrors, changed JS routes, and progress data; server was terminated.

Environment limitation: `.venv/bin/python` is absent and system `python3` lacks pytest, so the existing pytest suite could not be run; no Python implementation changed. `python3 tools/compare_upstream.py --check` was not run because it requires the unavailable pytest environment only insofar as the combined validation command stopped before it.

Final atomic commit: 36582c5 TJC-1.2: align controlled reference and scoped skills. Staged-file review contained only TJC-1.2 controlled reference, skills, synchronized mirrors, site pages/progress, sync mapping, and Backlog metadata. Post-commit clean-tree check completed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aligned the controlled reference and active Pi skills to the scoped rendezvous workflow. The reference now defines exact CW/LVLH/SI and bounded two-body coast contracts, assumption-based selection without universal thresholds, GMAT numerical-plus-accessible-screenshot PASS evidence, and explicit unsupported/future-work boundaries. Synced verbatim browser mirrors and updated site source/verification/progress surfaces. Offline site smoke, mirror check, JS syntax, and diff checks passed; pytest was unavailable because this worktree has no venv and system Python lacks pytest.
<!-- SECTION:FINAL_SUMMARY:END -->
