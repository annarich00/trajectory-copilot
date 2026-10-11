---
id: TJC-1.14
title: Implement assumption-based CW or two-body model selection
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-11 22:46'
labels: []
dependencies:
  - TJC-1.2
  - TJC-1.12
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Select between the supported CW and two-body paths from the structured problem and documented physical assumptions. Do not depend on an empirical validity-map task or a single arbitrary separation threshold.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The selector evaluates reference-orbit circularity, local-motion assumptions, separation relative to orbital radius, duration/regime, frame definition, and supported maneuver assumptions
- [x] #2 Clearly suitable cases select CW and clearly unsuitable cases select the scoped two-body fallback
- [x] #3 Boundary cases return a qualified decision with the assumptions and verification sensitivity visible to the user
- [x] #4 Insufficient information yields clarification instead of a model choice
- [x] #5 Output records selected model, reasons, assumptions, concerns, and the deterministic tool to invoke
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #5 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #6 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #7 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Design a structured ModelSelectionCase input dataclass (circularity, locality/separation-vs-radius, duration/regime, frame/LVLH-convention, maneuver assumptions, plus optional CW targeting-conditioning fields) matching reference/SOURCE.md Section D and .pi/skills/orbital-model-selector/SKILL.md's required assessment items, without inventing new physics or thresholds.
2. Implement src/model_selector.py: a pure assumption-based evaluator select_model(case) returning a frozen ModelSelectionResult dataclass with selection in {CW rendezvous, bounded two-body fallback, qualified CW rendezvous via qualified=True, UNSUPPORTED, NEEDS MORE INFORMATION}, reasons, assumptions, concerns, and deterministic_tool (src.cw / src.twobody / none). Logic: (a) any required-item unknown/missing -> NEEDS MORE INFORMATION listing which items; (b) all CW items clearly supported and not boundary -> CW rendezvous selection pointing to src.cw.two_burn_targeting; (c) clear CW violation but it fits the bounded two-body coast contract (finite duration, inertial Cartesian state available, positive mu/steps, coast-only) -> bounded two-body fallback pointing to src.twobody.propagate_cartesian_state, else UNSUPPORTED; (d) mixed/boundary assumptions (e.g. near-threshold separation ratio, near multi-rev duration, near-singular Phi_rv conditioning) -> qualified CW decision carrying concerns/verification-sensitivity notes rather than a flat threshold cut. Never use a single numeric cutoff alone -- combine multiple factors per SOURCE.md D and SKILL.md's required-assessment list, and route to validate_cw_use()/two_burn_targeting() only as supporting signals, not the sole basis.
3. Add tests/test_model_selector.py covering: clearly-suitable CW case, clearly-unsuitable (large separation/non-circular/GEO-scale) routed to bounded two-body fallback, a boundary/ambiguous case producing a qualified decision with assumptions+concerns surfaced, a missing-information case producing NEEDS MORE INFORMATION (not a model choice), and an output-shape test asserting required record fields (selection, reasons, assumptions, concerns, deterministic_tool) are present for every outcome branch.
4. Run .venv/bin/python -m pytest -q; fix until green.
5. Update educational site: add site/js/pages/model-selector.js page (and nav link + script tag) documenting the selector contract, mirror new authoritative files via tools/sync_site_data.py mapping additions (src/model_selector.py, tests/test_model_selector.py), update site/data/project-progress.js with TJC-1.14 outcome/evidence, update overview.js/project-map.js stale 'Planned: TJC-1.14' references to reflect completion.
6. Run tools/sync_site_data.py then --check; smoke-check ./run_site.sh and curl the new/changed routes.
7. Finalize Backlog: --check-ac 1..5 with evidence, --check-dod 1..7, --append-notes, --final-summary, status Done.
8. git add -A (excluding .venv/__pycache__), commit 'TJC-1.14: <summary>', amend if finalization edits land after; verify clean tree and git log.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented src/model_selector.py: ModelSelectionCase/ModelSelectionResult dataclasses and select_model() combining circularity, locality, duration_regime, frame, other_physics, maneuver_assumptions (reference/SOURCE.md SSB.1/SSD, .pi/skills/orbital-model-selector/SKILL.md) plus an optional CW targeting-conditioning signal from src.cw.two_burn_targeting. Selection outcomes: CW rendezvous (clean or qualified=True on boundary/near-singular Phi_rv), bounded two-body fallback (routes only when src.twobody's coast contract is independently satisfied), UNSUPPORTED (violation without a satisfied two-body contract), and NEEDS MORE INFORMATION (any required item unknown; known violations become concerns, never an early model choice). No single numeric threshold decides a selection alone; locality/duration signals reuse the exact validate_cw_use() warning text as one supporting signal among six-plus required items. Added tests/test_model_selector.py (11 tests: clearly-CW, clearly-unsuitable->two-body, clearly-unsuitable->UNSUPPORTED, boundary/qualified with concerns, near-singular targeting qualification, missing-info with/without known violation, parametrized output-shape check across all branches). Full suite: .venv/bin/python -m pytest -q -> 46 passed (35 baseline + 11 new). Site: added site/js/pages/model-selector.js (nav link + script tag in site/index.html), extended tools/sync_site_data.py with src/model_selector.py and tests/test_model_selector.py mirrors, ran python3 tools/sync_site_data.py then --check (30 mappings synchronized/match), updated site/data/project-progress.js with the TJC-1.14 completed entry and evidence links, removed stale 'Planned: TJC-1.14' wording from site/js/pages/overview.js and project-map.js. Smoke-tested ./run_site.sh on port 4193/4194: index, model-selector route script, and all new data mirrors returned HTTP 200; verified the embedded SOURCE.md SSD excerpt slices correctly. tools/compare_upstream.py --check exits 0 (no unaccounted drift).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added src/model_selector.py, a deterministic assumption-based combinator that selects between CW rendezvous and the bounded two-body coast fallback (or returns a qualified decision / NEEDS MORE INFORMATION / UNSUPPORTED) from six required SOURCE.md SSB.1 assumption items plus an optional CW targeting-conditioning signal, never from one isolated numeric threshold. Added tests/test_model_selector.py (11 tests covering clearly-suitable, clearly-unsuitable (both to two-body and to UNSUPPORTED), boundary/qualified, near-singular targeting, missing-information, and output-shape cases). Verified with .venv/bin/python -m pytest -q (46 passed). Updated the educational site: new site/js/pages/model-selector.js route wired into site/index.html, tools/sync_site_data.py mirror mappings for the new source/test files, refreshed site/data/project-progress.js, and removed stale 'Planned: TJC-1.14' text from overview.js/project-map.js; verified via python3 tools/sync_site_data.py --check and an offline ./run_site.sh smoke test (HTTP 200 on index, the new route script, and all new data mirrors).
<!-- SECTION:FINAL_SUMMARY:END -->
