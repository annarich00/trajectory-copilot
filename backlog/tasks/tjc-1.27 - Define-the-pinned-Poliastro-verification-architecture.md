---
id: TJC-1.27
title: Define the pinned Poliastro verification architecture
status: Done
assignee:
  - '@annarich00'
created_date: '2026-10-06 15:26'
updated_date: '2026-10-06 15:29'
labels: []
dependencies:
  - TJC-1.25
references:
  - 'https://github.com/poliastro/poliastro'
documentation:
  - docs/poliastro-verification-architecture.md
modified_files:
  - docs/poliastro-verification-architecture.md
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
  - backlog/tasks/tjc-1 - Deliver-the-Trajectory-CoPilot-semester-project.md
  - >-
    backlog/tasks/tjc-1.5 -
    Independently-verify-the-nonlinear-two-body-propagator.md
  - >-
    backlog/tasks/tjc-1.7 -
    Establish-a-genuinely-independent-CW-versus-two-body-validator.md
  - >-
    backlog/tasks/tjc-1.8 -
    Expand-deterministic-physics-property-and-failure-tests.md
  - >-
    backlog/tasks/tjc-1.16 -
    Add-transfer-duration-sweep-and-delta-v-trade-study-support.md
  - >-
    backlog/tasks/tjc-1.27 -
    Define-the-pinned-Poliastro-verification-architecture.md
  - site/data/project-progress.js
  - site/js/pages/project-map.js
  - site/js/pages/verification.js
  - tools/sync_site_data.py
  - site/data/docs/poliastro-verification-architecture.md
parent_task_id: TJC-1
priority: high
type: spike
ordinal: 2300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Introduce Poliastro as an external reference implementation for validating Trajectory CoPilot’s deterministic two-body propagation without replacing or extending the current solver. Poliastro is an archived repository with legacy dependency constraints, while this project currently runs on a newer Python, so the integration boundary must be reproducible, isolated, version-pinned, and explicit about supported verification coverage before implementation begins.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The architecture records Poliastro repository status, license, immutable revision/version, supported Python range, and material dependency compatibility constraints with cited upstream files
- [x] #2 A reproducible isolated-environment strategy is defined so Poliastro is not imported by or added to the core deterministic solver runtime
- [x] #3 The verification contract defines input/output state, units, frame, central body/mu, epoch or time-of-flight semantics, tolerance evidence, provenance, and PASS/WARNING/FAIL/UNAVAILABLE outcomes
- [x] #4 The policy requires current and future astrodynamics results to use Poliastro verification when Poliastro supports the same physical model, and to return an explicit unsupported/unavailable result rather than imply universal coverage
- [x] #5 The Backlog dependency graph, semester scope, and educational-site roadmap identify the implementation task and distinguish Poliastro cross-checking from required GMAT numerical and visual verification
- [x] #6 The task is finalized in one atomic commit and leaves the repository clean
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Update the educational site with TJC-1.27’s architecture decision, compatibility limitations, affected roadmap, and links to objective upstream evidence.
- [x] #2 Run repository tests, site mirror/upstream checks, JavaScript syntax checks, and an offline smoke check of every changed route.
- [x] #3 Commit only TJC-1.27 planning, documentation, site, and Backlog changes in one atomic Git commit whose subject begins `TJC-1.27:`; amend finalization metadata into that commit and finish clean.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Record the upstream Poliastro repository status, revision choices, licensing, Python/dependency constraints, and the resulting trust/maintenance limitations.
2. Define an isolated optional verifier boundary and a structured state/tolerance/provenance contract that never changes the core two-body solver dependency set.
3. Re-scope TJC-1.7 as the implementation task, update downstream dependencies and semester scope, and add truthful educational-site progress/roadmap entries.
4. Run Backlog, site mirror, upstream comparison, Python, JavaScript, and offline site checks.
5. Finalize TJC-1.27 and commit all planning artifacts atomically.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Architecture decision: pin Poliastro v0.17.0 to immutable commit `c7d12e9b715d3fd60f2be233af707d5b97617d39` (MIT). GitHub metadata reports the repository archived and last source push 2023-10-14; the immutable release `pyproject.toml` requires Python >=3.8,<3.11, Astropy >=5,<6, and a legacy scientific stack. Therefore the implementation task must use a locked isolated Python 3.10 subprocess environment and must not add Poliastro/Astropy to the core `.venv` or import them from `src/twobody.py`.

Re-scoped TJC-1.7 as the implementation task and made it depend on TJC-1.5 and this architecture task. The complete workflow now waits for TJC-1.7. Updated parent/test criteria, semester scope, living progress, roadmap, and verification lesson. Added the architecture document as a synchronized authoritative site mirror.

Validation before commit: Backlog doctor passed; both pytest commands passed with 6 tests; site mirror check passed with 19 mappings; upstream comparison had zero unaccounted differences; all site JavaScript passed `node --check`; changed site routes/artifacts returned non-empty HTTP responses; offline runtime-asset scan and `git diff --check` passed. The first smoke shell completed HTTP checks but its final grep command had a shell-quoting error; the scan was rerun separately and passed.

Atomic task commit created with subject `TJC-1.27: define pinned Poliastro verification architecture`; final Backlog metadata is being amended into that same commit per policy. No Poliastro package or runtime dependency was installed by this architecture task.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Defined the pinned Poliastro external-verification architecture without changing the current deterministic solver or installing legacy dependencies. Recorded archived-upstream and Python compatibility constraints, selected immutable v0.17.0 commit c7d12e9b715d3fd60f2be233af707d5b97617d39, specified an isolated Python 3.10 subprocess contract and explicit verification outcomes, reactivated TJC-1.7 for implementation, connected downstream dependencies, and updated the scope and educational site. Verified Backlog integrity, 6 Python tests, 19 source mirrors, strict upstream reconciliation, JavaScript syntax, offline site routes, and diff hygiene.
<!-- SECTION:FINAL_SUMMARY:END -->
