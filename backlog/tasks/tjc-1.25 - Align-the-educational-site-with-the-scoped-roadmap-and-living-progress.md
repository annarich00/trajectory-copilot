---
id: TJC-1.25
title: Align the educational site with the scoped roadmap and living progress
status: Done
assignee:
  - '@annarich00'
created_date: '2026-10-01 19:40'
updated_date: '2026-10-02 14:59'
labels: []
dependencies:
  - TJC-1.24
references:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
modified_files:
  - site/README.md
  - site/index.html
  - site/data/project-progress.js
  - site/js/lib.js
  - site/js/pages/progress.js
  - site/js/pages/overview.js
  - site/js/pages/research.js
  - site/js/pages/project-map.js
  - site/js/pages/cw-lvlh.js
  - site/js/pages/cw-stm.js
  - site/js/pages/targeting.js
  - site/js/pages/verification.js
  - tools/sync_site_data.py
  - tools/compare_upstream.py
parent_task_id: TJC-1
priority: high
type: docs
ordinal: 2200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The recovered site describes an older roadmap in which optimization was planned and GMAT was future work. Reframe it around the approved narrow rendezvous scope and make it the living demonstration surface that each completed task updates. Keep it static, offline, and dependency-free; do not introduce a framework or build step.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Overview, research, project-map, and roadmap content reflect the scoped natural-language → formalization → CW/two-body → GMAT numerical plus screenshot verification workflow
- [x] #2 General optimization, Pareto analysis, learned CW-validity boundaries, and other semester non-goals are visibly labeled deferred or excluded rather than planned next work
- [x] #3 A project-progress page lists active, completed, and deferred Backlog work and links each completed task to affected code, derivation pages, and verification evidence
- [x] #4 A documented task-completion checklist requires updating site status/content, synchronizing displayed authoritative files, and smoke-testing changed routes before a task is marked Done
- [x] #5 Detailed physics pages provide a consistent structure for assumptions, derivation, symbol definitions, source-code mapping, tests/evidence, limitations, and links to verbatim `reference/SOURCE.md` and deterministic Python
- [x] #6 The site remains launchable through `./run_site.sh` at `127.0.0.1:4173` with no external runtime assets or network requests
- [x] #7 A dependency-free synchronization/check command refreshes authoritative `site/data/` mirrors from repository files and fails clearly when displayed copies drift from their sources
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
1. Inventory the existing routes, source mirrors, upstream provenance rules, and approved semester scope.
2. Align navigation and overview/research/project-map/roadmap language to the narrow rendezvous workflow and explicit non-goals without claiming future components work.
3. Add a static living progress data model/page with truthful task states, TJC-1.24/TJC-1.26 backfill, evidence links, and TJC-1.25 commit subject.
4. Add a reusable detailed-physics teaching contract and apply it across current relevant pages while labeling unaudited gaps for TJC-1.2 through TJC-1.6.
5. Add dependency-free authoritative mirror sync/check tooling and documentation, excluding pedagogical physics.js from authority.
6. Narrowly document approved local site alignment differences in compare_upstream while retaining strict upstream drift checks.
7. Run syntax, sync, provenance, pytest, offline/static scans, and local server route/artifact smoke checks; inspect the final diff.
8. Finalize every AC/DoD with evidence and produce one clean atomic TJC-1.25 commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the approved static/offline alignment without changing authoritative physics. Added a living progress model/page with TJC-1.26 and TJC-1.24 backfill plus TJC-1.25 traceability; reframed overview/research/project-map around the required rendezvous→CW/two-body→GMAT screenshot→explanation flow; visibly excluded optimization/Pareto/learned thresholds/general mission planning; introduced a reusable physics teaching contract on CW/LVLH, STM, targeting, and verification pages; and documented later audit ownership. Added tools/sync_site_data.py with 18 explicit authoritative source mappings and a non-mutating drift check; site/js/physics.js is intentionally excluded. compare_upstream now accepts only the enumerated local site-alignment differences while authoritative source/test/reference drift remains strict.

Validation: mirror check passed (18 mappings); compare_upstream --check reported zero unaccounted differences; all JS files passed node --check; both `.venv/bin/python -m pytest -q` and explicit `-q tests` passed (6 tests); local server returned HTTP 200 with non-empty bodies for /, CSS, shared JS, every changed/new page module, progress data, SOURCE.md, and cw.py; external runtime asset/request scan found none; git diff --check, artifact scan, and credential-pattern scan passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aligned the dependency-free educational site with the approved narrow semester roadmap and established a truthful living progress/demo surface. Added strict source-mirror synchronization/checking, approved-local provenance handling, shared detailed-physics teaching contracts, maintenance documentation, and evidence-linked task backfill. Verified offline site assets/routes, source drift checks, JS syntax, and both pytest invocations.
<!-- SECTION:FINAL_SUMMARY:END -->
