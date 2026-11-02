---
id: TJC-13
title: >-
  Add a standing rule that reinforces the rendezvous skill-following order even
  outside the /rendezvous prompt
status: Done
assignee:
  - '@agent'
created_date: '2026-10-28 13:34'
updated_date: '2026-11-02 19:26'
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
- [x] #1 A written rule exists (either as a dedicated section in AGENTS.md, or as a project-local pi extension hook on before_agent_start per docs/extensions.md's claude-rules.ts pattern) that is always loaded/active, not only when /rendezvous is explicitly invoked
- [x] #2 The rule explicitly names the required order (orbital-problem-formalizer -> orbital-model-selector -> src/workflow.py::run_rendezvous_workflow -> GMAT verification) and instructs the agent to follow it for any rendezvous-shaped request, referencing .pi/prompts/rendezvous.md rather than duplicating its step text
- [x] #3 The rule explicitly states the same stop condition already in .pi/prompts/rendezvous.md step 1 (NEEDS CLARIFICATION / OUT OF SCOPE halts before model selection or solving)
- [x] #4 A documented before/after example shows a plain-conversation rendezvous request (no /rendezvous invocation) that previously could skip steps now visibly following the formalizer -> model-selector -> workflow order
- [x] #5 The rule does not change .pi/prompts/rendezvous.md's own content or any src/ module -- it is additive reinforcement, not a parallel or conflicting instruction set
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-13:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Chose AGENTS.md section over a .pi/extensions/ before_agent_start hook: AGENTS.md is already always loaded as project context for every session (confirmed via the BACKLOG.MD GUIDELINES block already present), so a new section there is simpler and lower-risk than writing/maintaining a TS extension hook (no new code, no extension-loading risk, no dependency on pi's extension system being enabled).
2. Add a new '## Rendezvous request routing (standing rule)' section to AGENTS.md (do not touch .pi/prompts/rendezvous.md or src/). The section: names the required order (orbital-problem-formalizer -> orbital-model-selector -> src/workflow.py::run_rendezvous_workflow -> GMAT verification); states it applies to ANY rendezvous-shaped request in plain conversation, not just /rendezvous; points to .pi/prompts/rendezvous.md as the source of truth for exact steps (no duplication of its step text); states the same stop condition (NEEDS CLARIFICATION / OUT OF SCOPE halts before model selection or solving).
3. Document a before/after example (plain-conversation rendezvous request with no /rendezvous invocation) showing previously-possible step-skipping vs. now-enforced pipeline order -- place it in Backlog implementation notes (--append-notes) referenced from the AGENTS.md section as 'documented in this task's implementation notes'.
4. Verify: AGENTS.md section present, .pi/prompts/rendezvous.md and src/ untouched (git diff), no backlog files touched besides TJC-13, nothing committed.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Decision: implemented AC1 as a new '## Rendezvous request routing (standing rule)' section in AGENTS.md (not a .pi/extensions/ before_agent_start hook). Justification: AGENTS.md is already always loaded as project context every session (evidenced by the existing always-present BACKLOG.MD GUIDELINES block in the same file), so adding a section there gets 'always active' for free with zero new code/runtime risk. A claude-rules.ts-style before_agent_start hook (examples/extensions/claude-rules.ts in the pi-coding-agent docs) would require writing and maintaining new TypeScript under .pi/extensions/, registering it, and trusting the extension-loading path at session start -- strictly more moving parts for the same guarantee, so it was not chosen.

Before/after example (AC4), documented here and referenced from AGENTS.md:

BEFORE (no standing rule, plain conversation, /rendezvous not invoked):
  User: "Our chaser is 500 m behind and 50 m below the target in a 450 km circular LEO orbit; find the two-impulse burn to rendezvous in one orbit."
  Agent (previously): recognizes this matches Clohessy-Wiltshire relative motion and jumps straight to calling src/cw.py's CW solver directly to produce a delta-v -- skipping problem formalization, model-selection justification, and GMAT verification, because /rendezvous was never typed so no rule required the pipeline.

AFTER (with the AGENTS.md standing rule in place, same request, still no /rendezvous invocation):
  Agent: recognizes the request as rendezvous-shaped per the standing rule, and even without /rendezvous being invoked, follows the required order:
    1. Applies orbital-problem-formalizer to the request, producing the full Scope..Readiness record (e.g. READY TO SOLVE, two spacecraft, circular LEO, impulsive, LVLH frame).
    2. Applies orbital-model-selector against that formalizer output, showing the six-item assessment table and selecting CW rendezvous (local circular-chief relative motion fits).
    3. Constructs the RendezvousCase from steps 1-2 and calls src/workflow.py::run_rendezvous_workflow(...) directly (not src/cw.py directly) with GMAT verification enabled.
    4. Reports outcome/verified/verification_status/trust_statement from that real run, stating plainly whether the result is VERIFIED or solver-only.
  If step 1 had instead returned NEEDS CLARIFICATION or OUT OF SCOPE, the agent halts there per the stop condition and does not proceed to model selection or any solver call, exactly mirroring /rendezvous step 1's semantics.

Scope note: only AGENTS.md was edited. .pi/prompts/rendezvous.md and all src/ modules are untouched (verified via git diff --stat), per AC5.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added an always-active '## Rendezvous request routing (standing rule)' section to AGENTS.md, which is already loaded as project context every session. The section names the required order (orbital-problem-formalizer -> orbital-model-selector -> src/workflow.py::run_rendezvous_workflow -> GMAT verification), applies it to any rendezvous-shaped plain-conversation request (not only /rendezvous), references .pi/prompts/rendezvous.md as the single source of truth without duplicating its step text, and states the same NEEDS CLARIFICATION/OUT OF SCOPE stop condition. A documented before/after example (plain-conversation rendezvous request, no /rendezvous invocation) is recorded in this task's Implementation Notes, showing the request now following the formalizer->selector->workflow order instead of jumping straight to src/cw.py. Verified via 'git diff --stat -- .pi/prompts/rendezvous.md src/' that both are untouched (empty diff), satisfying AC5; only AGENTS.md and this task's own Backlog metadata changed.
<!-- SECTION:FINAL_SUMMARY:END -->
