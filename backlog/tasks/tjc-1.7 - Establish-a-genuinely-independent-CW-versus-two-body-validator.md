---
id: TJC-1.7
title: Verify deterministic two-body propagation against pinned Poliastro
status: Done
assignee:
  - '@pi'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-06 20:14'
labels: []
dependencies:
  - TJC-1.5
  - TJC-1.27
references:
  - 'https://github.com/poliastro/poliastro'
  - docs/poliastro-verification-architecture.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an external-reference verification layer for the existing point-mass propagator without expanding its physics or importing Poliastro into the core runtime. Run pinned Poliastro 0.17.0 at immutable commit c7d12e9b715d3fd60f2be233af707d5b97617d39 in an isolated compatible Python environment, compare like-for-like Cartesian propagation, and return structured evidence. Poliastro is archived and cannot be treated as a universal oracle; unsupported future models must be explicit and use another verifier. GMAT remains the required end-to-end numerical and visual verification layer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A reproducible isolated Python 3.10 verification environment installs a locked Poliastro 0.17.0 from immutable commit `c7d12e9b715d3fd60f2be233af707d5b97617d39` without adding Poliastro/Astropy to the core runtime environment
- [x] #2 A subprocess adapter accepts the documented SI Cartesian request contract, performs explicit unit/frame conversions, invokes Poliastro propagation, and returns versioned machine-readable results and diagnostics
- [x] #3 Circular short-duration, circular one-period, and bounded eccentric cases compare `src/twobody.py` against Poliastro with justified position/velocity tolerances and retained raw evidence
- [x] #4 A deliberately perturbed result proves that out-of-tolerance disagreement returns FAIL rather than being hidden or normalized away
- [x] #5 Missing environments, subprocess errors, incompatible frames/units, and models unsupported by pinned Poliastro return distinct UNAVAILABLE or UNSUPPORTED outcomes and can never produce PASS
- [x] #6 Core `src/twobody.py` has no Poliastro import, future-verifier extension points are documented, and GMAT remains a separate required verification layer
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #2 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #3 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #4 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
- [x] #5 Update the educational site with the Poliastro architecture, pinned provenance, like-for-like comparison evidence, compatibility limitations, and links to exact adapter/tests without presenting the archived library as universally authoritative.
- [x] #6 Synchronize affected authoritative source/tests/docs mirrors, run the site offline, and smoke-check every changed route and verification artifact.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the hardened two-body contract, existing verification code/tests, and the pinned Poliastro architecture to design the versioned JSON subprocess boundary.
2. Add reproducible isolated-environment provisioning and a locked provenance record without modifying the core .venv or importing Poliastro from production modules.
3. Implement the adapter and host comparison/reporting path for supported SI inertial Cartesian cases, including FAIL, UNAVAILABLE, and UNSUPPORTED behavior.
4. Add deterministic tests and retained comparison evidence for circular and bounded eccentric cases, update docs/site mirrors, run required checks and site smoke test.
5. Finalize Backlog with objective evidence and make exactly one atomic TJC-1.7 commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented isolated Python 3.10 adapter boundary and host contract. Provisioned /tmp/tjc-poliastro-venv with uv; initial NumPy 2.2.6 import failure ('numpy.product' missing) led to an explicit numpy<2 lock constraint and NumPy 1.26.4. Live pinned Poliastro 0.17.0 commit c7d12e9b715d3fd60f2be233af707d5b97617d39 comparisons passed: circular short 1.30e-08 m/4.07e-12 m/s, circular period 9.70e-05 m/1.10e-07 m/s, eccentric 1.63e-08 m/3.00e-11 m/s. PYTHONPATH=. .venv/bin/pytest -q: 19 passed; site mirrors check passed; offline site smoke passed.

Offline site smoke re-run passed for index, adapter mirror, and architecture mirror; server terminated.

Atomic commit subject: TJC-1.7: verify two-body propagation against pinned Poliastro. Final working tree clean.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented and live-verified the isolated pinned Poliastro subprocess comparison; finalized after atomic commit.
<!-- SECTION:FINAL_SUMMARY:END -->
