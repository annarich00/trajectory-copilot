---
id: TJC-1.24
title: Synchronize the updated upstream workspace and educational site
status: To Do
assignee: []
created_date: '2026-10-01 19:40'
updated_date: '2026-10-02 14:26'
labels: []
dependencies:
  - TJC-1.26
references:
  - /home/anna_ford/trajectory-copilot/
parent_task_id: TJC-1
priority: high
type: chore
ordinal: 2100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Before further implementation, reconcile this repository against `/home/anna_ford/trajectory-copilot`, the local workspace from which the baseline was recovered. At planning time, all already-imported authoritative files are byte-identical and the only source-only maintained artifacts are `run_site.sh` and `site/`; the worker must repeat the manifest/checksum comparison at execution time so any later upstream edits are also captured. Import upstream additions and modifications deliberately without overwriting this repository’s Backlog plan, scope documents, Git policy, or other local project-management artifacts. Preserve provenance and the distinction between authoritative code/reference files and pedagogical site mirrors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A repeatable manifest/checksum comparison covers maintained files in the upstream workspace and current repository while excluding `.git`, virtual environments, caches, bytecode, and generated process artifacts
- [ ] #2 Every upstream-only or content-different maintained file is either synchronized into the repository or listed with a documented reason for retaining the current version
- [ ] #3 Upstream deletions and local-only files are reviewed explicitly; synchronization does not blindly delete or overwrite Backlog tasks, scope documents, Git policy, provenance records, or repository-specific setup files
- [ ] #4 After synchronization, shared authoritative source, tests, skills, examples, evaluations, and `reference/SOURCE.md` match the accepted upstream versions by checksum
- [ ] #5 The updated `site/` tree and executable `run_site.sh` are present and `./run_site.sh` serves `http://127.0.0.1:4173` using only Node built-ins with no npm install or internet access
- [ ] #6 Baseline Python tests and a site smoke check for the main page, JavaScript, CSS, representative source/reference mirrors, and educational routes pass without suppressed failures
- [ ] #7 A provenance report records the upstream path, synchronization timestamp, compared/excluded paths, imported files, retained local differences, and post-sync verification evidence
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #5 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #6 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #7 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
