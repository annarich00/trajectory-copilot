---
id: TJC-11
title: >-
  Build a subagent-readable GMAT example corpus file from the collected
  open-source scripts
status: To Do
assignee: []
created_date: '2026-10-28 13:33'
labels: []
dependencies:
  - TJC-10
priority: low
type: task
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up to TJC-10 (research/collection). TJC-10 collects raw open-source GMAT script examples with provenance but leaves them as loose files/notes under a research-staging location. This task is the second subagent's job: take that raw collection and transform it into one (or a small number of) structured, machine-readable file(s) -- e.g. a JSON array keyed by mission type/formatting convention, with fields for source URL, license, mission type, a short description, and the normalized script text or a pointer to it -- that the planned 'GMAT example subagent' (see the separate task defining that subagent) can actually load and search at runtime. The two tasks are deliberately separated: TJC-10 is open-ended internet research with no fixed output shape, while this task defines and enforces a fixed, validated schema so the consuming subagent has a stable contract instead of parsing arbitrary scraped text.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A versioned schema for the corpus file is defined and documented (fields: source URL, license/attribution status, mission type, formatting/convention tags, description, and the example content or a stable path to it)
- [ ] #2 Every entry collected in TJC-10 that was not flagged as unknown/incompatible license is represented in the corpus file; entries flagged unknown/incompatible in TJC-10 are either excluded or explicitly marked non-redistributable in the corpus file, never silently included as if clear
- [ ] #3 The corpus file is schema-validated by an automated check (a small script or test) that fails if a required field is missing or a license-flagged entry is marked redistributable
- [ ] #4 The corpus file lives in a location the planned GMAT example subagent's definition can reference directly (coordinate the exact path with that task so the two do not drift)
- [ ] #5 A short README alongside the corpus file documents how to regenerate/update it when TJC-10's collection is refreshed, and records the schema version
<!-- AC:END -->
