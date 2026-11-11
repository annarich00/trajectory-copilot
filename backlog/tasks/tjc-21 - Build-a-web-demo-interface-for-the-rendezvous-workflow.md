---
id: TJC-21
title: Build a web demo interface for the /rendezvous workflow
status: To Do
assignee: []
created_date: '2026-11-10 13:36'
updated_date: '2026-11-10 13:52'
labels:
  - web-demo
dependencies:
  - TJC-16.5
references:
  - >-
    https://github.com/16S893-AI-for-engineering-research/annarich00/blob/main/src/pages/walkthrough-tjc-16-pi-demo.html
documentation:
  - docs/web-demo-cases.md
priority: medium
type: feature
ordinal: 72000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-16.5 shows each plot live, but only in the pi terminal. For the advisor demo (and for an operator-style evaluation) the workflow should be walkable in a browser, step by step, in the style of the course walkthrough page. This parent groups the follow-on work. Phase 1 is a static GitHub Pages replay of stored runs. Phase 2 is a local live backend that drives pi with this project. Out of scope: any public hosted live site, rate limiting, access control, or server-side GMAT installs. All decisions and constraints are in docs/web-interface-decisions.md; read it before working any child task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Phase 2 child tasks are Done and a live /rendezvous run can be driven from the browser on the local machine
- [ ] #2 No child task changes the behavior of src/workflow.py::run_rendezvous_workflow or the TJC-16.5 artifact outputs
- [ ] #3 Phase 1 child tasks are Done and the static replay of the three demo cases (Demo A, B, C) is published on GitHub Pages
<!-- AC:END -->
