---
id: TJC-23
title: Migrate rendezvous skills and prompt to pi tool calls
status: To Do
assignee: []
created_date: '2026-11-11 14:44'
updated_date: '2026-11-11 14:47'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 85000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The rendezvous pipeline currently relies on the LLM applying free-form .pi/skills/*.md instructions (orbital-problem-formalizer, orbital-model-selector, cw-rendezvous, orbital-two-body-rendezvous) and a .pi/prompts/rendezvous.md slash-prompt that orchestrates them, plus run_gmat_verification as the one existing registered pi tool. The user wants the same explicit, auditable tool-call pattern already used for GMAT verification extended across the whole pipeline: the unused gmat-rendezvous-verification skill (superseded by the run_gmat_verification tool contract and not referenced by the /rendezvous pipeline) removed, the four currently-used skills turned into registered pi tools, and the /rendezvous prompt itself first turned into a skill and then that skill (like the others) turned into a tool call, so prompts and skills are both retired in favor of tool calls. This is a material architecture change to the AGENTS.md-documented standing pipeline order and needs explicit plan review before implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The gmat-rendezvous-verification skill directory is removed and no longer referenced by the active rendezvous pipeline docs
- [ ] #2 Each of orbital-problem-formalizer, orbital-model-selector, cw-rendezvous (orbital-targeting-planner), and orbital-two-body-rendezvous has an equivalent registered pi tool and its skill file is retired
- [ ] #3 The /rendezvous prompt's orchestration is re-expressed as a skill and then as a registered pi tool call, so no skill or prompt step remains in the pipeline
- [ ] #4 AGENTS.md's standing rendezvous-routing rule and any other pipeline documentation are updated to reference the new tools instead of the retired skills/prompt
- [ ] #5 Existing CW/GMAT verification behavior (src/workflow.py, run_gmat_verification) is unchanged and still passes its existing tests
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
