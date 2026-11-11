
<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.53.0 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**At the beginning of each conversation in this project, run `backlog instructions overview` before answering or taking action. Re-read it only if you have not read it yet in the current conversation.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->

## Git task commits

Follow [`docs/task-commit-policy.md`](docs/task-commit-policy.md) for the required one-task, one-commit workflow, including exact task-ID subject prefixes, Backlog finalization by amend, and branch/worktree isolation for parallel work.

## Test-first (TDD) evidence

Follow [`docs/testing-policy.md`](docs/testing-policy.md) for the required red-then-green pytest evidence for any new test added going forward.

## Rendezvous request routing (standing rule)

This rule is always active for this project, not only when a session explicitly
invokes the `/rendezvous` prompt template. If a user makes a rendezvous-shaped
request in ordinary conversation -- two spacecraft, a chief/chaser or
target/chaser relative-motion ask, a maneuver/delta-v/transfer request between
orbiting bodies -- route it through the same required pipeline that
`/rendezvous` enforces, in the same order, with no step skipped or
shortcut straight to a solver module:

orbital-problem-formalizer -> orbital-model-selector ->
`src/workflow.py::run_rendezvous_workflow` -> GMAT verification.

`.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md` is the single source of truth for the exact,
detailed steps and wording of this pipeline; read it rather than relying on
this summary, and do not duplicate or fork its step text here. This section
only exists to make the same ordering binding even when `/rendezvous` itself
was not typed.

Stop condition (mirrors `.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md` step 1): if the
`orbital-problem-formalizer` result is `NEEDS CLARIFICATION` or genuinely
`OUT OF SCOPE` (not `READY TO SOLVE`), halt there -- report that result and do
not proceed to model selection or to any solver call.

A documented before/after example for this rule is recorded in Backlog task
TJC-13's implementation notes (`backlog task view TJC-13 --plain`).
