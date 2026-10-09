---
id: TJC-1.4
title: Audit CW two-burn targeting and singularity handling
status: Done
assignee:
  - '@pi'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-09 13:50'
labels: []
dependencies:
  - TJC-1.3
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The existing CW two-burn targeting path treats a singular or poorly conditioned Phi_rv block as automatically impossible. That is incorrect for reachable boundary conditions: at integer orbital periods the block is singular, but the desired terminal displacement can still lie in its column space and admit infinitely many initial-velocity solutions. Audit the partitioned STM equations and revise the bounded solver so it distinguishes infeasibility from singular-but-reachable targeting. Preserve explicit conditioning detection and do not disguise a singular solution as a unique inverse result. This task supersedes the prior blanket-rejection requirement for exact one-orbit cases while remaining limited to fixed-duration CW targeting, not general optimization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The targeting result exposes explicit metadata that distinguishes a nonsingular unique solution, singular but solvable, singular and non-unique, and singular and infeasible outcomes
- [x] #2 For nonsingular well-conditioned Phi_rv, targeting uses the unique solve and the propagated terminal position satisfies the requested boundary condition within declared tolerances
- [x] #3 For singular or near-singular Phi_rv, the solver computes b = rf - Phi_rr r0 and tests its reachability against the column space of Phi_rv using a documented SVD rank/residual tolerance
- [x] #4 A singular case with b outside the reachable column space returns a machine-readable singular-and-infeasible result with a human-readable reason, rather than an inversion exception or a fabricated maneuver
- [x] #5 A singular reachable case returns the SVD-pseudoinverse minimum-norm initial velocity, identifies the solution as singular and non-unique, and its CW propagation satisfies the terminal position condition within declared tolerances
- [x] #6 Circular GEO cases with r0 = [0, -100 km, 0] and rf = [0, 0, 0] succeed at one, two, and three orbital periods; terminal position is verified and the reported delta-v decreases as period count increases
- [x] #7 Tests cover a generic integer-period boundary condition outside the reachable subspace and prove it returns singular-and-infeasible rather than failing on matrix inversion
- [x] #8 Documentation explains why singular Phi_rv does not necessarily mean impossible rendezvous, including the column-space feasibility test, pseudoinverse minimum-norm policy, multiplicity, and scope limitations
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Update the targeting and singularity lessons with the partitioned STM derivation, burn equations, conditioning rationale, failure behavior, and links to exact code/tests.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing CW targeting implementation, its tests, and site mirrors to identify the bounded solver seam.
2. Implement explicit SVD-based reachability, conditioning, multiplicity, and minimum-norm singular solution metadata without changing transfer time.
3. Add GEO integer-period reachable and unreachable regression tests; update authoritative documentation and required educational mirrors/progress evidence.
4. Run unit, repository, site, and offline smoke checks; record objective evidence, finalize Backlog, and commit the task atomically.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented CWTargetingResult metadata and documented SVD rank (1e-12 relative) / residual (1e-9*max(1,||b||) m) reachability policy. `pytest -q tests/test_cw.py` passed (6); `pytest -q tests` passed (22); mirrors synchronized and checked; compare_upstream, JS syntax, diff check, and local offline site curl smoke checks passed. Site served through ./run_site.sh on 127.0.0.1:4174 and was terminated.

Final atomic commit: 647ec74 TJC-1.4: audit CW two-burn targeting and singularity handling. Verified staged contents task-only and final worktree clean.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented fixed-duration SVD column-space targeting outcomes: unique direct solutions, singular reachable non-unique minimum-norm solutions, and singular infeasible no-maneuver results. Verified GEO P=1/2/3 and unreachable integer-period regressions plus full repository/site checks.
<!-- SECTION:FINAL_SUMMARY:END -->
