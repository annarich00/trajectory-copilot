---
id: TJC-22
title: Remove the unused gmat-rendezvous-verification skill
status: To Do
assignee: []
created_date: '2026-11-11 14:41'
labels: []
dependencies: []
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The /rendezvous prompt pipeline (.pi/prompts/rendezvous.md) never invokes the gmat-rendezvous-verification skill: GMAT verification is actually performed by the run_gmat_verification pi tool (.pi/extensions/gmat-verification-tool/), not by this skill. The skill survives only as prose cross-references inside the other three pipeline skills (orbital-model-selector, orbital-targeting-planner, orbital-two-body-rendezvous) and in docs (gmat-example-reviewer.md, architecture-graph.html, worked-example docs), creating a dangling pointer to a skill nothing actually loads. Removing it keeps the skill set matching what the pipeline really uses.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The .pi/skills/gmat-rendezvous-verification directory is deleted
- [ ] #2 References to gmat-rendezvous-verification in the other three skill files are updated to point at the real verification mechanism (the run_gmat_verification tool / src/gmat_verify.py contract) instead of a now-nonexistent skill
- [ ] #3 References in .pi/agents/gmat-example-reviewer.md are updated consistently
- [ ] #4 Mentions in docs (docs/gmat-example-reviewer-example-run.md, docs/rendezvous-gmat-example-review-worked-example.md, docs/architecture-graph.html) are updated or annotated so none silently points at a deleted skill
- [ ] #5 Existing tests still pass
<!-- AC:END -->
