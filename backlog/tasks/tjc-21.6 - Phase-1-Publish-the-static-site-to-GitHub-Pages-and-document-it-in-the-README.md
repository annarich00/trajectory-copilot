---
id: TJC-21.6
title: 'Phase 1: Publish the static site to GitHub Pages and document it in the README'
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:43'
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
