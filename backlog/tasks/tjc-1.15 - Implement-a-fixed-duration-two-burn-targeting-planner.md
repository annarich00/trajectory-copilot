---
id: TJC-1.15
title: Harden the deterministic CW rendezvous solution path
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-11 22:11'
labels: []
dependencies:
  - TJC-1.3
  - TJC-1.4
  - TJC-1.14
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Preserve and harden the recovered CW state-transition and two-burn targeting implementation for the supported fixed-time impulsive rendezvous problem. This task does not add transfer-time optimization or generalized trajectory optimization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A complete supported structured problem produces burn components, total delta-v, relative trajectory, final relative state, and time of flight through deterministic code
- [x] #2 The path exposes units, frame convention, assumptions, and solver status with every result
- [x] #3 Singular or ill-conditioned transfer times fail explicitly without least-squares fallback or silent time changes
- [x] #4 A well-specified LEO rendezvous fixture reproduces the audited CW result within declared tolerances
- [x] #5 The path rejects optimization and unsupported-dynamics requests rather than widening scope
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Update the CW solution walkthrough so a reader can trace one benchmark from structured inputs through mean motion, STM blocks, both burns, trajectory, final state, and test evidence.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add solve_cw_rendezvous() to src/cw.py: a single deterministic orchestration function composing mean_motion -> two_burn_targeting -> propagate_relative_state for one fixed-duration two-impulse CW rendezvous. 2. Add CWRendezvousSolution frozen dataclass exposing status/feasible/singular/non_unique/reason (surfaced from two_burn_targeting, no least-squares fallback, no silent t_final change), mean_motion_radps, transfer_time_s, dv0_mps/dv1_mps/total_delta_v_mps, trajectory_times_s/trajectory_states (sampled via propagate_relative_state over the post-burn-1 coast arc), final_state, condition_number/rank/reachability_residual_m, and declared units/frame/state_ordering/dynamics/assumptions metadata (module-level CW_RENDEZVOUS_ASSUMPTIONS tuple referencing reference/SOURCE.md Sec B.1). 3. Validate mu/reference_radius_m/t_final/trajectory_samples inputs explicitly (positive finite) before calling two_burn_targeting; propagate CWSingularTransferError unchanged for non-finite Phi_rv/rhs. 4. Add UnsupportedCWRequest dataclass + unsupported_cw_rendezvous_request() mirroring src/twobody.py::unsupported_request, giving a concrete AC5 rejection hook for optimization/unsupported-dynamics requests without widening solve_cw_rendezvous's fixed-duration CW-only signature. 5. Do not modify cw_stm/two_burn_targeting/check_phi_rv_conditioning math (already audited in TJC-1.3/TJC-1.4). 6. Extend tests/test_cw.py: reproduce the existing quarter-orbit LEO benchmark through solve_cw_rendezvous (AC1/AC4), assert exposed units/frame/assumptions/status metadata (AC2), cover singular-infeasible (no burns/no exception) and singular-reachable (SVD minimum-norm) paths via solve_cw_rendezvous (AC3), cover invalid-input rejection, and cover unsupported_cw_rendezvous_request (AC5). 7. Run .venv/bin/python -m pytest -q; all must pass. 8. Extend site/js/pages/targeting.js (or add a small new section) plus data mirrors (site/data/src/cw.py, site/data/tests/test_cw.py) to trace solve_cw_rendezvous for the same benchmark end to end; update site/data/project-progress.js with TJC-1.15 entry. 9. Smoke-check ./run_site.sh and the targeting route. 10. Backlog finalization: check ACs/DoD, append notes, final summary, status Done. 11. One atomic commit 'TJC-1.15: ...'; verify git status clean.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added solve_cw_rendezvous() to src/cw.py composing mean_motion -> two_burn_targeting -> propagate_relative_state into one deterministic orchestration call. Returns CWRendezvousSolution exposing status/feasible/singular/non_unique/reason (taken unchanged from two_burn_targeting; no least-squares fallback, no silent transfer-time change), burn components, total delta-v, sampled relative trajectory + times, final relative state, mean motion, transfer time, condition/rank/residual diagnostics, and declared units/frame/state_ordering/dynamics/assumptions metadata. Added unsupported_cw_rendezvous_request() (UnsupportedCWRequest) mirroring src/twobody.py's unsupported_request() pattern as the AC5 rejection hook for optimization/trade-study/non-CW-dynamics requests. No changes to cw_stm/two_burn_targeting/check_phi_rv_conditioning math (already audited under TJC-1.3/TJC-1.4). Extended tests/test_cw.py with 7 new tests covering AC1 (orchestration matches direct two_burn_targeting call), AC2 (units/frame/state_ordering/assumptions/status exposure), AC3 (singular-infeasible fails explicitly with None burns/trajectory and unchanged transfer_time_s; singular-reachable surfaces SVD minimum-norm non-unique metadata), AC4 (reproduces the audited 350km quarter-orbit LEO benchmark exactly, bit-for-bit vs the existing two_burn_targeting benchmark), input validation, and AC5 (unsupported_cw_rendezvous_request rejects optimization/Pareto/eccentric-chief/continuous-thrust requests). Full suite: .venv/bin/python -m pytest -q -> 41 passed. Updated educational site: targeting.js now traces solve_cw_rendezvous end to end for the same benchmark (code block, orchestration panel with status/burns/trajectory sample table, explicit-failure section, unsupported-request section); physics.js got a solveCwRendezvous pedagogical mirror (verified against the Python output via node, byte-for-byte matching dv0/dv1/final_state); site/data mirrors for src/cw.py and tests/test_cw.py resynced via tools/sync_site_data.py --check (28/28 match); project-progress.js updated with a truthful TJC-1.15 entry. Smoke-checked ./run_site.sh (PORT=4199): /, /js/pages/targeting.js, /js/physics.js, /data/project-progress.js, /data/src/cw.py, /data/tests/test_cw.py all returned HTTP 200. tools/compare_upstream.py --check shows no unaccounted content drift.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardened the deterministic CW rendezvous path by adding src/cw.py::solve_cw_rendezvous, a single orchestration function composing mean_motion -> two_burn_targeting -> propagate_relative_state, returning burns, total delta-v, a sampled relative trajectory, final relative state, and time of flight alongside declared units/frame/state-ordering/assumptions/solver status (CWRendezvousSolution). Singular/ill-conditioned transfer times surface two_burn_targeting's existing singular-infeasible/singular-reachable statuses verbatim: no least-squares fallback and no silent transfer-time change. Added unsupported_cw_rendezvous_request() as an explicit rejection path for optimization, trade-study, and non-CW-dynamics requests, matching the existing src/twobody.py::unsupported_request pattern. No changes were made to the already-audited cw_stm/two_burn_targeting physics (TJC-1.3/TJC-1.4). Added 7 tests to tests/test_cw.py covering AC1-AC5, including an exact reproduction of the audited 350 km quarter-orbit LEO benchmark through the new orchestration call. Full suite: 41/41 pytest passing. Updated the educational site's Two-Burn Targeting walkthrough with a solve_cw_rendezvous section (code block, live orchestration panel, explicit-failure and unsupported-request explanations), added a verified pedagogical physics.js mirror, resynced site/data mirrors, and updated project-progress.js. Smoke-checked ./run_site.sh and the targeting route (HTTP 200 for all changed assets).
<!-- SECTION:FINAL_SUMMARY:END -->
