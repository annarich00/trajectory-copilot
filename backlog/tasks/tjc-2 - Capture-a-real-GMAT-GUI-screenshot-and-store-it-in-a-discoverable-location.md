---
id: TJC-2
title: Capture a real GMAT GUI screenshot and store it in a discoverable location
status: To Do
assignee: []
created_date: '2026-10-12 13:23'
labels: []
dependencies:
  - TJC-1.21
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-1.21 confirmed that headless GmatConsole-R2026a cannot render OrbitView/OpenFrames graphics in this environment (missing OpenGL/texture plugins), so it substitutes a deterministic SVG line plot as the required trajectory screenshot artifact. The operator has asked for an actual GMAT-rendered GUI screenshot rather than this substitute, and for that artifact to be stored somewhere a user can easily find it rather than only in ephemeral temp/worktree directories. This task investigates whether a real GMAT GUI render is feasible in this environment (for example via a virtual framebuffer such as Xvfb) and, if so, implements it; if genuinely infeasible, it documents the concrete technical blocker as explicit evidence rather than assumption, and ensures the fallback artifact is at least persistently and discoverably stored.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The verification tool attempts a real GMAT GUI (OrbitView/OpenFrames) screenshot capture, for example via a virtual display, before falling back to the deterministic SVG plot
- [ ] #2 If a real GMAT GUI screenshot cannot be produced in this environment, the specific technical blocker (missing library/plugin/display capability) is captured as reproducible evidence (exact command, exit status, error output), not merely asserted
- [ ] #3 Whichever artifact is produced (real GMAT render or SVG fallback) is written to a persistent, well-known, discoverable location rather than only a caller-supplied or temp-only output directory
- [ ] #4 A user can find the produced artifact without reading source code: it is referenced from the educational site and/or the verification result output with a direct, working path or link
- [ ] #5 Tests cover both the real-GMAT-screenshot success path (when the environment allows it) and the fallback path, and distinguish which artifact type was actually produced in the structured result
<!-- AC:END -->
