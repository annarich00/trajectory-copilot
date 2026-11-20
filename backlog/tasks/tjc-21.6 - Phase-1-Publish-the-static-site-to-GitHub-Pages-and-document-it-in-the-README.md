---
id: TJC-21.6
title: 'Phase 1: Publish the static site to GitHub Pages and document it in the README'
status: In Progress
assignee:
  - '@worker'
created_date: '2026-11-10 13:37'
updated_date: '2026-11-20 22:10'
labels:
  - web-demo
dependencies:
  - TJC-21.4
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: medium
type: task
ordinal: 78000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The repo needs something visible for the advisor and as a project record. Pages serves static files only, so this task is about build, deploy and links, not features. Course PDFs and lecture material that sit near the repo must not be published.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The site is served from GitHub Pages for annarich00/trajectory-copilot and its URL is in the README
- [ ] #2 The published files include no API keys, absolute local paths, course PDFs or lecture material
- [ ] #3 The published page works from a fresh browser with no local server
- [ ] #4 The README explains what the site shows and states that it replays recorded runs
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 Project owner has opened the result in a browser, checked it against the acceptance criteria, and approved it before the task is marked Done
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a minimal Pages entry point that opens the retained recorded-run demo. 2. Add a GitHub Pages workflow that publishes only the entry point, demo files, embedded data, and the two required Plotly HTML artifacts. 3. Link the Pages URL from the root README and verify the deploy payload contains no absolute paths, keys, or retired-site files.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Pages deployment: a minimal index redirects to the standalone replay; the workflow publishes only the index, demo HTML/JS/data, and the two required 3D artifact HTML files. The root README links https://annarich00.github.io/trajectory-copilot/. Local payload rehearsal confirmed no /home paths, API-key patterns, or private-key headers. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_run_manifest_contract.py -> 43 passed.

README cleanup: removed the retired CW-to-GMAT early vertical-slice section and its local command from the GitHub-displayed README at the owner’s request; the recorded-demo section remains the project-facing demo guidance.
<!-- SECTION:NOTES:END -->
