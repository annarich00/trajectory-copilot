# Web interface for the /rendezvous workflow: decisions

Status: decisions recorded from a design interview. No implementation exists yet.
Audience: the agent (or person) creating Backlog tasks for this work. Create
tasks with the `backlog` CLI per `AGENTS.md`; this file is the source of
decisions, not a task list.

## Stored demo cases

The first stored runs are Demo A (one period, expected NUMERICAL_DISAGREEMENT),
Demo B (quarter period, expected VERIFIED) and Demo C (two-body coast, expected
VERIFIED). Request text, expected outcomes and capture notes are in
`docs/web-demo-cases.md`. Do not confuse them with the benchmark cases in
`evaluations/benchmark/` or the "Case B" on the course walkthrough page; say
"Demo A/B/C".

## Goal

A web interface for the existing `/rendezvous` workflow so an operator can be
walked through a problem step by step at a high level. The layout model is the
course walkthrough page
`https://github.com/16S893-AI-for-engineering-research/annarich00/blob/main/src/pages/walkthrough-tjc-16-pi-demo.html`
(numbered steps, "Say this" narration, per-plot explanation, likely questions,
"what this does not show").

The end audience is a Space Force operator. The near-term audience is a course
advisor/professor who evaluates the project through an operator's eyes.

The interface is a chat, but it only handles requests in this project's
rendezvous workflow. It is not a general-purpose assistant.

## Relationship to existing tasks

This is **new follow-on work**, not a continuation of TJC-16.5. Create new
Backlog tasks for it; do not reopen TJC-16.5.

- **TJC-16 (parent) and TJC-16.1 to 16.5 are Done and are the foundation.**
  TJC-16.2 (3D scene), TJC-16.3 (trajectory/burns plot) and TJC-16.4
  (comparison plot) produce the artifacts. TJC-16.5 wired them into
  `src/workflow.py::run_rendezvous_workflow` and
  `.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md`
  so each artifact path is reported live in the terminal as its stage
  finishes (`on_artifact` callback, `artifacts["visualization_artifacts"]`,
  `scripts/rendezvous_visualization_stage.py`).
- **What this work adds:** a browser front end that shows those artifacts,
  operator/developer modes, a model picker, clarification and GMAT-missing
  flows, and stored-case replay. It consumes the TJC-16.5 outputs and does
  not change them.
- **Suggested dependencies for new tasks:** TJC-16.5 (and through it
  TJC-16.2, 16.3, 16.4), TJC-12 (the `run_gmat_verification` pi tool) and
  TJC-15 (GMAT tool call in the review flow). Confirm the exact IDs with
  `backlog task list` before linking.
- **Known gap inherited from TJC-16.5:** its notes say the full interactive
  `/rendezvous` pi session was not driven end to end; only the prompt's CLI
  commands and a direct `run_rendezvous_workflow` run were tested. The Phase 2
  live backend will be the first to drive the whole prompt through pi, so
  budget for surprises and verify it explicitly.
- **Two-body path:** TJC-16.5 records all three plot stages as
  `not_generated` with reasons for the bounded two-body path. The interface
  must show that status and reason, not fill the gap.

## Fixed pipeline the interface must reflect

Source of truth for step wording and order:
`.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md`. Do not
duplicate or fork its step text. In order:

1. `orbital-problem-formalizer` (stop if `NEEDS CLARIFICATION` or genuinely `OUT OF SCOPE`)
2. `orbital-model-selector`
3. 3D relative-position scene (artifact, before GMAT)
4. Trajectory/burns plot (artifact, after the deterministic solve, before GMAT)
5. `run_gmat_verification` pi tool (`.pi/extensions/gmat-verification-tool/`)
6. Comparison plot (artifact, after GMAT)
7. GMAT screenshot (existing artifact) and the final summary

## Decisions

| # | Area | Decision |
|---|---|---|
| D1 | Purpose | Live runner for the rendezvous workflow, plus stored example cases the user can view. |
| D2 | Scope of chat | Chat interface limited to the rendezvous workflow. |
| D3 | Models | Any model pi can reach. The user picks the model; the project's skills, tools and workflow still apply. |
| D4 | Operator mode | Curated. Explains at a high level what each step did and what each plot represents. Uses **fixed templates** filled with real result values. No model-generated narration, so no hallucinated physics. |
| D5 | Developer mode | Shows raw agent output and tool calls. Keys and machine-specific paths must be removed. |
| D6 | Mode toggle | Operator/developer toggle works on the static site too, by reading different parts of the same saved run. |
| D7 | `NEEDS CLARIFICATION` | The UI lists the topics that need clarification and prompts the user for them. |
| D8 | GMAT unavailable | The UI asks whether the user wants to install GMAT and whether they want step-by-step help. It shows install commands for the user to run on their own. The system never runs the install. The result is reported as `NOT VERIFIED` (never a faked PASS), consistent with `src/gmat_verify.py`. |
| D9 | Stored cases | Stored cases (the three owner-supplied demo cases in `docs/web-demo-cases.md`: Demo A, B and C) replay without any API key. |
| D10 | Keys | Live runs with a new problem use the operator's own provider key. Never write keys to logs, saved runs or developer-mode output. |
| D11 | Repository | Lives in `annarich00/trajectory-copilot` (this repo, `origin`), alongside the existing `site/`. |
| D12 | Deployment scope | Local demo plus the repo. A public hosted live site is out of scope for now. |
| D13 | Cost | Effectively $0. GitHub Pages and a local server are free; GMAT is already installed. The only variable cost is the user's own LLM usage on new live runs (not yet measured). |
| D14 | Public/hosted access | Out of scope. Rate limits, shared passwords, spend caps and session isolation for strangers are not required now. |

## In scope (two phases)

**Phase 1: static site (GitHub Pages)**
- Saved-run format, defined using the three demo cases in `docs/web-demo-cases.md`.
- Static operator-mode page for Demo A, B and C using fixed templates, in the style of the course walkthrough page.
- Operator/developer toggle (D6).
- Optional: one recorded `NEEDS CLARIFICATION` example. The visitor cannot type a free answer on Pages. A scripted "provide the missing values" button replays a saved continuation. Label stored runs "Recorded run" so nobody mistakes them for live processing.
- Pages shows the same missing-topics prompt as the live app for the recorded example (D7).

**Phase 2: local live backend**
- Local web server that drives pi with this project as its working directory (`pi --mode rpc`, or the SDK) and streams events to the same front end used in Phase 1.
- Model picker backed by `pi --list-models`.
- Real clarification: the user answers the listed topics and the pipeline continues (D7).
- GMAT-missing flow (D8).
- Visitor/operator supplies their own key (D10).

The Phase 1 saved-run format is the data contract Phase 2 must emit.

## Out of scope for now

- A public, hosted live site and anything it requires (rate limiting, access control, spend caps, per-visitor isolation).
- Any server-side execution of GMAT install commands.
- A general-purpose chat outside the rendezvous workflow.

These may be mentioned as future work.

## Constraints and guidance for task authors

- **Saved-run format** must hold: ordered steps, each step's status, artifact paths/metadata, structured results, raw agent events/tool calls (for developer mode), and an optional stop state with an optional continuation (for the clarification branch).
- **Structured data for templates.** GMAT results (`verified`, `verification_status`, `failure_mode`, `unified_verification_report`) and artifact paths are already JSON. The formalizer and model-selector outputs are Markdown prose. Decide whether to parse that Markdown or have those skills also emit a structured block. Until decided, show their text verbatim next to the templated explanation. Any change to skill output must keep `evaluations/` behavior intact.
- **Template honesty.** Templates must state limits the way the course page does (for example: the 3D target placement is illustrative; one case, run once; PASS means within the stated tolerances, not a proof). Do not write physics claims the code or reports do not support.
- **Not-generated stages.** A stage with status `not_generated` must be displayed as such with its `reason`. Never substitute another plot (see `.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md`).
- **Failure vocabulary.** Reuse the existing statuses and failure modes from `src/gmat_verify.py` and `src/verification_report.py` (PASS/WARNING/FAIL/INCOMPLETE; MISSING_GMAT, EXECUTION_ERROR, MALFORMED_OUTPUT, NUMERICAL_DISAGREEMENT, SCREENSHOT_FAILURE, CW_TARGETING_INFEASIBLE). Do not invent new ones.
- **Live agent tools.** Even for a local demo, restrict the live agent to workflow tools (formalizer, selector, workflow scripts, `run_gmat_verification`). Do not expose general shell access through the web UI.
- **Do not modify** `src/workflow.py::run_rendezvous_workflow` behavior to suit the UI; the UI consumes existing outputs.
- **Existing site.** `site/` and `run_site.sh` already serve an offline educational lab. Decide in a task whether the new UI extends it or lives in a new directory; the decisions above do not settle this.
- **Repo hygiene.** Do not commit the course PDFs or lecture material that sit outside this repo. Follow `docs/task-commit-policy.md` and `docs/testing-policy.md`.

## Open items

- Parse Markdown versus add structured output to the formalizer and selector (see above).
- Exact saved-run schema (Phase 1 first task).
- Developer-mode redaction rules: which fields and paths to strip.
- Whether the recorded clarification example is in the first version or only the success paths (Demo B and C).
- Extend `site/` or create a new directory.
- Real cost of one live run (check once in the provider dashboard).
- Per-step operator templates and the "likely questions" content: who writes and reviews them.
- Which models have been tested against the skills. Weaker models may behave differently; the interface should not imply every model was validated.

## Suggested first task

Define the saved-run format and capture Demo A, B and C (`docs/web-demo-cases.md`)
as stored runs, then build the static demo page on top of it.

## Verification notes

- Facts checked during the interview: GMAT R2026a is installed at `~/opt/GMAT/R2026a` (Apache 2.0 license file included); `origin` is `git@github.com:annarich00/trajectory-copilot.git`; `pi` supports `--mode rpc` and `--list-models`; the course walkthrough page content was read.
- Not verified: the actual cost and token usage of a live run; the RPC streaming behavior against this project's prompt and extension.
