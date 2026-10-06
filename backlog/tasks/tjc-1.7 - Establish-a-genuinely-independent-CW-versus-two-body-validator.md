---
id: TJC-1.7
title: Verify deterministic two-body propagation against pinned Poliastro
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-06 15:27'
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
- [ ] #1 A reproducible isolated Python 3.10 verification environment installs a locked Poliastro 0.17.0 from immutable commit `c7d12e9b715d3fd60f2be233af707d5b97617d39` without adding Poliastro/Astropy to the core runtime environment
- [ ] #2 A subprocess adapter accepts the documented SI Cartesian request contract, performs explicit unit/frame conversions, invokes Poliastro propagation, and returns versioned machine-readable results and diagnostics
- [ ] #3 Circular short-duration, circular one-period, and bounded eccentric cases compare `src/twobody.py` against Poliastro with justified position/velocity tolerances and retained raw evidence
- [ ] #4 A deliberately perturbed result proves that out-of-tolerance disagreement returns FAIL rather than being hidden or normalized away
- [ ] #5 Missing environments, subprocess errors, incompatible frames/units, and models unsupported by pinned Poliastro return distinct UNAVAILABLE or UNSUPPORTED outcomes and can never produce PASS
- [ ] #6 Core `src/twobody.py` has no Poliastro import, future-verifier extension points are documented, and GMAT remains a separate required verification layer
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #2 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #3 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #4 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
- [ ] #5 Update the educational site with the Poliastro architecture, pinned provenance, like-for-like comparison evidence, compatibility limitations, and links to exact adapter/tests without presenting the archived library as universally authoritative.
- [ ] #6 Synchronize affected authoritative source/tests/docs mirrors, run the site offline, and smoke-check every changed route and verification artifact.
<!-- DOD:END -->
