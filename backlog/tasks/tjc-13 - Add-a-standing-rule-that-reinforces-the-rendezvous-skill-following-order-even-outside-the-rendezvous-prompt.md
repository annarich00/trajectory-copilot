---
id: TJC-13
title: >-
  Add a standing rule that reinforces the rendezvous skill-following order even
  outside the /rendezvous prompt
status: To Do
assignee: []
created_date: '2026-10-28 13:34'
labels: []
dependencies: []
priority: low
type: task
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Second of the four classmate-brainstormed workflow additions. .pi/prompts/rendezvous.md already encodes the required formalizer -> model-selector -> workflow -> GMAT order, but it only applies when a session explicitly invokes that prompt template. The operator wants a standing reinforcement so a rendezvous-shaped request made in ordinary conversation (not via the /rendezvous template) still gets routed through the same required order instead of the agent shortcutting straight to src/cw.py or src/twobody.py. This is a prompting/rule addition, not new solver logic -- it must not restate or fork the pipeline steps already defined in .pi/prompts/rendezvous.md and the five .pi/skills/*/SKILL.md files; it should point to them as the single source of truth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A written rule exists (either as a dedicated section in AGENTS.md, or as a project-local pi extension hook on before_agent_start per docs/extensions.md's claude-rules.ts pattern) that is always loaded/active, not only when /rendezvous is explicitly invoked
- [ ] #2 The rule explicitly names the required order (orbital-problem-formalizer -> orbital-model-selector -> src/workflow.py::run_rendezvous_workflow -> GMAT verification) and instructs the agent to follow it for any rendezvous-shaped request, referencing .pi/prompts/rendezvous.md rather than duplicating its step text
- [ ] #3 The rule explicitly states the same stop condition already in .pi/prompts/rendezvous.md step 1 (NEEDS CLARIFICATION / OUT OF SCOPE halts before model selection or solving)
- [ ] #4 A documented before/after example shows a plain-conversation rendezvous request (no /rendezvous invocation) that previously could skip steps now visibly following the formalizer -> model-selector -> workflow order
- [ ] #5 The rule does not change .pi/prompts/rendezvous.md's own content or any src/ module -- it is additive reinforcement, not a parallel or conflicting instruction set
<!-- AC:END -->
