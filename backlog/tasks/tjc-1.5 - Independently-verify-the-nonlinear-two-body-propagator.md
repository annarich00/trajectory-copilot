---
id: TJC-1.5
title: Harden the deterministic two-body rendezvous fallback
status: Done
assignee:
  - '@pi'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-06 19:31'
labels: []
dependencies:
  - TJC-1.25
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - docs/poliastro-verification-architecture.md
parent_task_id: TJC-1
priority: high
type: task
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Preserve the recovered nonlinear two-body propagator and make it sufficient for the explicitly supported rendezvous fallback cases when CW assumptions are not satisfied. This is a bounded propagation/solution path, not generalized targeting or trajectory optimization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The supported two-body fallback inputs, outputs, units, frames, and maneuver limitations are explicitly defined
- [x] #2 At least one scoped CW-invalid rendezvous case produces a deterministic two-body trajectory or propagation result suitable for GMAT verification
- [x] #3 A known two-body orbit agrees with an analytical or independent reference within declared position and velocity tolerances
- [x] #4 Specific orbital energy and angular momentum behavior are tested over representative supported durations
- [x] #5 Unsupported targeting, perturbations, or optimization requests return an explicit limitation rather than an improvised result
- [x] #6 The hardened current propagator exposes stable like-for-like Cartesian cases and metadata required by the pinned Poliastro verification adapter in TJC-1.7
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Update the two-body lesson with the point-mass equation, state derivative, RK4 stages, invariants, supported fallback semantics, and links to exact code/tests.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing two-body API, test suite, verification helpers, and site data to define the bounded fallback contract.
2. Harden the deterministic point-mass RK4 path and public metadata/limitation handling; add analytical and invariant tests, including a CW-invalid propagation case.
3. Update the two-body documentation and living site, synchronize authoritative mirrors, then run the required code, site, and repository checks.
4. Record objective evidence, finalize the task through Backlog, and create exactly one TJC-1.5 atomic commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented bounded SI inertial-Cartesian point-mass coast propagation with explicit validation, TwoBodyCase metadata, invariant helpers, and UNSUPPORTED responses for targeting/perturbation/optimization requests.

Objective verification: .venv/bin/python -m pytest -q => 14 passed in 0.74s; python3 tools/sync_site_data.py --check => 19 mappings match; python3 tools/compare_upstream.py --check => content-different unaccounted: none; git diff --check => passed.

Site smoke: started ./run_site.sh, fetched /, js/pages/verification.js, and data/src/twobody.py by curl at 127.0.0.1:4173, asserted expected fallback content, then terminated server.

The circular analytical test uses 2 cm position and 2e-5 m/s velocity tolerance after one period; energy/angular momentum are checked over three periods. A 1,000 km radial-separation absolute coast case is deterministic and intentionally CW-invalid.

Final atomic commit subject: TJC-1.5: harden deterministic two-body fallback. Post-commit status, staged-file check, and checks are clean.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardened the deterministic two-body fallback as a bounded SI inertial-Cartesian point-mass coast contract. Added analytical circular-orbit, invariant, CW-invalid deterministic propagation, metadata, unsupported-request, and invalid-input tests; updated the authoritative reference and synchronized two-body site lesson/progress evidence. Verified 14 pytest tests, site mirror synchronization, upstream comparison, diff check, and an offline site-server smoke check. Poliastro adapter work remains explicitly deferred to TJC-1.7; GMAT remains the required end-to-end verifier.
<!-- SECTION:FINAL_SUMMARY:END -->
