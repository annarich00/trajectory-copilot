---
id: TJC-1.12
title: Narrow and harden the rendezvous problem formalizer
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
type: feature
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Limit natural-language interpretation to the semester rendezvous class: two spacecraft, primarily circular LEO, impulsive maneuvers, a relative state, and a specified time of flight or period count. Preserve the recovered formalizer where it already works and make assumptions and clarification needs explicit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Structured output covers central body, reference orbit or altitude/elements, relative position and velocity, LVLH convention, time of flight or period count, maneuver assumptions, and requested outputs
- [x] #2 Every value is labeled as specified, derived, or assumed; missing and ambiguous fields remain explicit
- [x] #3 Materially missing frame, reference orbit, state, units, or timing prevents solution and yields focused clarification questions
- [x] #4 The formalizer does not invent altitude, gravitational parameter, circularity, coordinate convention, units, or terminal conditions
- [x] #5 Schema tests cover complete, incomplete, contradictory, and unit-inconsistent scoped requests
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
1. Inspect the recovered formalizer, schema, tests, and educational-site mirrors for the scoped rendezvous contract. 2. Narrow formalization to explicit two-spacecraft circular-LEO impulsive LVLH rendezvous inputs, preserving provenance and emitting blocking clarification questions rather than defaults. 3. Add complete, incomplete, contradictory, and unit-inconsistent schema/evaluation tests. 4. Update affected educational-site documentation/progress and run targeted, repository, site, and offline smoke checks. 5. Record objective evidence, finalize Backlog, and make one atomic TJC-1.12 commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a provenance-labeled scoped formalizer contract and four evaluation fixtures (complete, incomplete, contradictory, unit-inconsistent); synchronized affected skill, fixtures, and test mirror to the dependency-free site. Validation: formalizer schema/fixture assertion script passed; git diff --check, Python compilation, Node syntax checks, mirror check, and upstream comparison check passed; ./run_site.sh on 127.0.0.1:4174 returned HTTP 200 for index and changed skill/test/evaluation artifacts. Full pytest could not run because this worktree has no .venv and system Python lacks pytest and numpy; no dependency installation or network access was used.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardened the formalizer to the scoped two-spacecraft circular-LEO impulsive LVLH rendezvous class, with explicit provenance, blockers, and clarification questions that prevent invented material inputs. Added complete/incomplete/contradictory/unit-inconsistent schema fixtures and tests, synchronized site mirrors, and updated truthful progress evidence. Verified static checks and offline site smoke; full pytest remains unavailable in this dependency-free worktree.
<!-- SECTION:FINAL_SUMMARY:END -->
