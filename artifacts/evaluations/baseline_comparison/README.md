# `evaluations/baseline_comparison/` — direct-LLM baseline vs. complete structured workflow (TJC-1.22)

This directory runs the four-category rendezvous benchmark
(`evaluations/benchmark/`, TJC-1.9) through two approaches and compares
them:

1. a **direct natural-language-to-LLM-answer baseline**: the request text
   handed to a general-purpose LLM with no access to this repository's
   formalizer skill, model selector, deterministic solvers, or GMAT; and
2. the **complete structured workflow**
   (`src/workflow.py::run_rendezvous_workflow`, TJC-1.16), which chains the
   formalizer's readiness check, `src/model_selector.py::select_model`, the
   deterministic CW/two-body solvers, and independent GMAT verification.

See `REPORT.md` for the full methodology, per-case analysis, aggregate
summary, and conclusions. This `README.md` only orients the directory
layout; `REPORT.md` is the authoritative deliverable for TJC-1.22's
acceptance criteria.

## Methodology summary (full detail in `REPORT.md`)

**No live external LLM API is available in this sandboxed worktree** (no
`anthropic`/`openai` packages, no API keys configured, and this agent is
expressly instructed not to attempt one). Instead, **the agent implementing
this task is itself the direct-LLM baseline**: for each of the four
benchmark requests, this same model (identified by the `PI_MODEL`/
`PI_PROVIDER` environment variables recorded in `REPORT.md`) read only the
request text — not `src/`, not any `.pi/skills/*/SKILL.md` file, not the
model selector, not GMAT — and produced a single-shot, un-scaffolded
natural-language answer exactly as a general-purpose LLM with astrodynamics
training but no access to this project's deterministic tools would. Each
such answer is recorded verbatim in `case_a_baseline_llm_response.md`
through `case_d_baseline_llm_response.md`, with its own disclosed
derivation shown as a "scratch work" appendix so a reviewer can see exactly
which numbers were produced by hand-reasoning rather than invoked tool
code — this scratch work is still the baseline side, not the workflow side.

This is a legitimate evaluation design choice given this environment's
constraints, not a limitation hidden from the reader: it tests the same
underlying model/architecture's un-scaffolded single-shot output against
its own scaffolded, tool-grounded output on identical inputs, which is
exactly the comparison TJC-1.22 asks for ("direct natural-language-to-LLM-
answer baseline" vs. "the complete structured workflow").

## Files

- `REPORT.md` — the full methodology, per-case analysis, aggregate summary,
  scoring table, and conclusions (AC1-AC5).
- `case_a_baseline_llm_response.md`, `case_b_baseline_llm_response.md`,
  `case_c_baseline_llm_response.md`, `case_d_baseline_llm_response.md` — the
  verbatim direct-LLM baseline response for each benchmark case.
- `case_a_workflow_result.json`, `case_b_workflow_result.json`,
  `case_c_workflow_result.json`, `case_d_workflow_result.json` — the exact
  `WorkflowResult.to_dict()` output from a real run of
  `src/workflow.py::run_rendezvous_workflow` for each case (cases a/b/c ran
  against a real `GmatConsole-R2026a` installation; case d short-circuits
  before any physics/GMAT call, matching `src/workflow.py`'s documented
  `NEEDS_CLARIFICATION` behavior).

## Reproduce the full-workflow side

```
.venv/bin/python evaluations/baseline_comparison/run_workflow_cases.py --gmat GmatConsole-R2026a
```

This regenerates `case_a_workflow_result.json` through
`case_d_workflow_result.json` by constructing each case's
`src/workflow.py::RendezvousCase` directly from the already-committed
`evaluations/benchmark/*` fixture values (not re-typed ad hoc numbers), and
calling `run_rendezvous_workflow` for real. Cases a/b/c independently
confirm the already-committed, already-audited GMAT evidence in
`examples/cw_gmat_slice_example/`, `examples/benchmark_case_b_boundary/`,
and `examples/benchmark_case_c_two_body/` (TJC-1.9) rather than replacing
it; this script does not modify any of those directories, `src/workflow.py`,
or any other already-audited module.

The direct-LLM baseline side (`case_*_baseline_llm_response.md`) has no
reproduction command: it is a one-shot natural-language exercise by the
implementing model in this session, as documented above and in `REPORT.md`.
