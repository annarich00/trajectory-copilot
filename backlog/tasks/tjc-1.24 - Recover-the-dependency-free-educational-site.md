---
id: TJC-1.24
title: Synchronize the updated upstream workspace and educational site
status: Done
assignee:
  - '@annarich00'
created_date: '2026-10-01 19:40'
updated_date: '2026-10-02 14:39'
labels: []
dependencies:
  - TJC-1.26
references:
  - /home/anna_ford/trajectory-copilot/
modified_files:
  - docs/upstream-sync-provenance.md
  - pytest.ini
  - run_site.sh
  - site
  - tools/compare_upstream.py
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
- [x] #1 A repeatable manifest/checksum comparison covers maintained files in the upstream workspace and current repository while excluding `.git`, virtual environments, caches, bytecode, and generated process artifacts
- [x] #2 Every upstream-only or content-different maintained file is either synchronized into the repository or listed with a documented reason for retaining the current version
- [x] #3 Upstream deletions and local-only files are reviewed explicitly; synchronization does not blindly delete or overwrite Backlog tasks, scope documents, Git policy, provenance records, or repository-specific setup files
- [x] #4 After synchronization, shared authoritative source, tests, skills, examples, evaluations, and `reference/SOURCE.md` match the accepted upstream versions by checksum
- [x] #5 The updated `site/` tree and executable `run_site.sh` are present and `./run_site.sh` serves `http://127.0.0.1:4173` using only Node built-ins with no npm install or internet access
- [x] #6 Baseline Python tests and a site smoke check for the main page, JavaScript, CSS, representative source/reference mirrors, and educational routes pass without suppressed failures
- [x] #7 A provenance report records the upstream path, synchronization timestamp, compared/excluded paths, imported files, retained local differences, and post-sync verification evidence
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
1. Build and run a content-aware maintained-file manifest comparison against /home/anna_ford/trajectory-copilot, classifying exclusions, protected local-only artifacts, and every upstream-only/content-different file.
2. Deliberately import accepted upstream artifacts (including the dependency-free site and executable launcher), preserving authoritative files and repository-specific planning/setup artifacts.
3. Add a dependency-free repeatable sync checker and provenance report; minimally update the site progress content for TJC-1.24 without undertaking TJC-1.25 roadmap alignment.
4. Run baseline pytest, comparison check mode, offline site/server and route/static/source smoke checks, diff/generated-artifact/secret scans, and review the final diff.
5. Finalize every AC/DoD with evidence and create exactly one atomic TJC-1.24 commit, leaving a clean tree.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Execution-time SHA-256 comparison found 64 upstream and 57 local maintained files before import: 43 upstream-only files (run_site.sh plus the 42-file site tree), no content-different shared files, and 36 protected local-only setup/planning/provenance files. Imported all 43 upstream-only artifacts and preserved run_site.sh mode 755. Added tools/compare_upstream.py and docs/upstream-sync-provenance.md; final check reports 63 checksum-identical shared files, no upstream-only/unaccounted difference, one documented local post-import site edit, and protected local-only files.

Added pytest.ini with only testpaths = tests after the imported verbatim site/data/tests display mirrors caused recursive pytest import-name collisions; this keeps tests/ authoritative and display mirrors non-executable. Both `.venv/bin/python -m pytest -q` and `.venv/bin/python -m pytest -q tests` passed with 6 tests.

Offline site verification launched ./run_site.sh on 127.0.0.1:4173 and returned HTTP 200 for /, CSS, app/physics/project-map JavaScript, representative source/reference/test/skill/example/evaluation data files, and the project-map hash URL shell. Site content records TJC-1.24 and commit subject, checksum sync outcome, evidence, authority boundary, and TJC-1.25 limitation. git diff --check, generated/process-artifact scan, secret-pattern scan, and server-process check passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Synchronized executable run_site.sh and the complete dependency-free educational site from /home/anna_ford/trajectory-copilot, preserving all repository-specific planning/setup artifacts. Added a repeatable SHA-256 reconciliation checker, provenance report, and minimal traceable TJC-1.24 site progress entry while leaving broad roadmap alignment to TJC-1.25. Added minimal pytest testpaths configuration so display-only test mirrors are not collected. Verified 6 authoritative Python tests through both default and explicit commands, offline HTTP serving and representative routes/assets, checksum reconciliation, diff hygiene, and generated/secret/process scans.
<!-- SECTION:FINAL_SUMMARY:END -->
