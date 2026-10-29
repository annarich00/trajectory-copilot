# Session summary — 2026-10-28

Context handoff for the next agent session on Trajectory CoPilot. Read this
before starting work; it captures decisions and artifacts from a prior
session that are not yet reflected anywhere else as a single document.

## 1. Code categorized by evidentiary bar (professor's 4 categories)

The operator asked for the repo's code sorted into Throwaway / Scaffolding /
Infrastructure / Core per her professor's rubric (each category has its own
required evidence: "runs and looks right" / "ran end-to-end, watched it fail
or succeed" / "independent-reference test that fails without the fix" /
"re-run case, known limit, or independent data").

Saved as a diagram: **`code-category-map.svg`** (repo root). Summary:

- **Throwaway:** `src/optimization.py` — never imported anywhere, ties to
  deferred non-goal tasks TJC-1.17/1.18. Candidate to delete.
- **Scaffolding:** `scripts/run_cw_gmat_slice.py`,
  `scripts/generate_benchmark_gmat_evidence.py`,
  `evaluations/baseline_comparison/run_workflow_cases.py`,
  `tools/compare_upstream.py`, `tools/sync_site_data.py`, `run_site.sh`,
  `.pi/skills/*/SKILL.md`. Evidence: real end-to-end runs, watched, with
  committed example artifacts.
- **Infrastructure:** `src/cw.py` (audited vs. Clohessy & Wiltshire 1960 in
  `docs/cw-stm-audit.md`), `src/twobody.py` (cross-checked vs. pinned
  Poliastro 0.17.0), `src/verify.py` (LVLH↔inertial round-trip tests),
  `src/gmat_verify.py` (the real GMAT run is the independent reference),
  `src/verification_report.py`. Strongest category — real independent-
  reference tests that fail without the fix.
- **Core:** `src/model_selector.py`, `src/workflow.py`,
  `evaluations/benchmark/` (4 fixtures), `evaluations/baseline_comparison/
  REPORT.md`. **Operator flagged this as not fully developed yet.** Known
  gaps: TJC-1.23 (semester write-up) still To Do; the baseline comparison
  used the same model as both baseline and workflow (not an independent
  capability check); broader validity-regime/parameter-sweep work is
  explicitly deferred (TJC-1.10/1.11/1.13), so the "re-run case / independent
  data" bar for Core is only partly met today.

## 2. Dev log entries drafted (operator's own voice/format)

Two entries were drafted matching the operator's existing
`site/data/project-progress.js`-style voice (first person, specific numbers,
candid about limitations). **These were drafted in-chat and given to the
operator; they were not written into any file.** If asked to add them to the
dev log, use this content (lightly adapt dates/wording to match wherever she
actually logs these):

- **2026-10-22** — Wrote `.pi/prompts/rendezvous.md` (5-step fixed pipeline
  order: formalizer → model-selector → `run_rendezvous_workflow` → report →
  GUI-launch guardrail) and opened TJC-9 as a direct follow-up after noticing
  `run_rendezvous_workflow` hardcodes `skip_gui_screenshot=True` and never
  attempts the real GMAT GUI capture by default.
- **2026-10-22** — Confirmed the interactive GMAT GUI cannot be opened from
  this sandbox for two independent, non-retryable reasons (no `/dev/dri` DRM
  render-node path; WSLg/RDP never forwards the rendered buffer even when the
  window registers at the X11 level). Documented in
  `src/gmat_verify.py::attempt_gmat_gui_screenshot`'s docstring and wired into
  `.pi/prompts/rendezvous.md` step 5. Distinct from the *non-interactive*
  Xvfb screenshot capture (TJC-3, 2026-10-12), which still works fine.

Real commits behind these: `4c2b6c2` (prompt + sandbox-limitation doc +
TJC-9 creation) and `4027c7e` (TJC-3, Xvfb + asset-loading fix, 2026-10-12).

## 3. Backlog task sequencing (operator's explicit priority decision)

The operator wants **TJC-1.23 (Document scoped semester results and
reproducibility) to be the LAST task implemented** — it's meant to capture
the whole semester's work, and she still has more to do first.

Required order before TJC-1.23: **TJC-5 → TJC-6 → TJC-7 → TJC-9**, in that
order, then whatever else, then TJC-1.23 last.

This is now enforced two ways, both already applied in Backlog:

1. **Ordinals** (lower runs first): TJC-5=50000, TJC-6=51000, TJC-7=52000,
   TJC-9=53000, TJC-10=54000, TJC-11=55000, TJC-12=56000, TJC-13=57000,
   TJC-14=58000, TJC-15=59000, **TJC-1.23=60000** (last).
2. **Hard dependency**: TJC-1.23's `dependencies:` now includes
   `TJC-1.22, TJC-5, TJC-6, TJC-7, TJC-9` (TJC-1.22 was its original
   dependency and was preserved). Backlog will not allow TJC-1.23 to be
   picked up or marked Done until all of these are Done.

**Important gotcha hit this session:** `backlog task edit <id> --dep <ids>`
**replaces** the full dependency list, it does not append. When adding new
deps to an existing task, always re-list every dependency you want kept
(including pre-existing ones) in the same `--dep` command, or you will
silently drop existing dependencies. (This happened once here with
TJC-1.23's original `TJC-1.22` dependency; it was caught and restored in the
same session — confirm this is still correct the next time an edit touches
`--dep`.)

## 4. New Backlog tasks created this session (TJC-10 through TJC-15)

The operator had a classmate brainstorming session and proposed four
workflow additions, plus asked for a preceding research task. All six are
now in Backlog as `Low` priority, To Do, not required for the `TJC-1`
semester deliverable (they sit outside TJC-1.23's blocking chain).

Dependency chain:
```
TJC-10 (research corpus)
  -> TJC-11 (build schema-validated corpus file)
       -> TJC-14 (define GMAT-example subagent, reads TJC-11's corpus)
TJC-12 (expose GMAT execution as an LLM-callable tool)  [independent]
TJC-13 (standing rule reinforcing rendezvous skill order)  [independent]
TJC-14 + TJC-12 -> TJC-15 (wire tool-call -> subagent review -> combined report)
```

- **TJC-10** — Research and collect ≥10 open-source GMAT mission-script
  examples from the internet, spanning >1 mission type and >1 source repo,
  with URL/license/description recorded per entry. Raw files go under a new
  `research/gmat_examples_raw/` staging area — explicitly separate from
  `src/`/`examples/` so provenance never gets confused with this project's
  own audited code. License-unclear/incompatible sources must be flagged,
  not silently included. No existing `src/`/`scripts/`/`tests/`/`examples/`
  file may be modified by this task.
- **TJC-11** — Depends on TJC-10. Transforms the raw collection into one (or
  a few) versioned, schema-validated corpus file(s) (JSON, fields: source
  URL, license status, mission type, convention tags, description, content
  or stable path) that TJC-14's subagent can actually query. Schema
  validation must be automated (script or test) and must fail if a
  license-flagged entry is marked redistributable.
- **TJC-12** — Register GMAT execution as a genuine pi tool via a
  project-local extension (`pi.registerTool()`, see
  `docs/extensions.md`), wrapping the already-audited `src/gmat_verify.py`
  functions without duplicating their logic. Must preserve the existing
  PASS/WARNING/FAIL/INCOMPLETE/MISSING_GMAT distinctions — no new silent-PASS
  path. `.pi/prompts/rendezvous.md` step 3 should reference the new tool.
- **TJC-13** — Add a standing rule (AGENTS.md section, or a
  `before_agent_start` extension hook per the `claude-rules.ts` pattern in
  pi's examples) so a rendezvous-shaped request made in plain conversation
  (not via `/rendezvous`) still gets routed through the required
  formalizer → model-selector → workflow → GMAT order, instead of an agent
  shortcutting straight to `src/cw.py`/`src/twobody.py`. Must reference
  `.pi/prompts/rendezvous.md` as the source of truth, not duplicate its text.
- **TJC-14** — Depends on TJC-11. Defines a project-local pi subagent
  (`.pi/agents/gmat-example-reviewer.md`) that is a GMAT-scripting-formatting
  expert: given a generated GMAT script and the mission type, it consults
  TJC-11's corpus and reports whether the script's formatting/structure
  matches established open-source practice. Explicitly scoped to
  formatting/convention review only — must state plainly it is NOT a
  numerical verifier and does not replace
  `.pi/skills/gmat-rendezvous-verification/SKILL.md`'s PASS/FAIL contract.
  Must cite the specific corpus entries it compares against, and say so
  explicitly when the corpus has no entry for the requested mission type.
- **TJC-15** — Depends on TJC-12 AND TJC-14. The connector: after the main
  workflow agent calls the new GMAT tool (TJC-12) and gets a numerical
  verification result, it hands the generated script + mission context to
  the GMAT-example subagent (TJC-14) for a formatting review, then reports
  both — before declaring `VERIFIED`. Adds a new step to
  `.pi/prompts/rendezvous.md` between the existing steps 3 and 4. The
  subagent's verdict is explicitly advisory/stylistic only: it can never
  flip a FAIL to VERIFIED or vice versa, and if the subagent is unavailable
  the workflow must still complete and report the numerical result with the
  style review noted as skipped.

## 5. Open items / things to watch

- `code-category-map.svg` is currently **untracked** in git (confirmed via
  `git status` this session) — not yet committed to any task.
- This file (`SESSION_SUMMARY_2026-10-28.md`) is also untracked; it is a
  scratch handoff note, not an authoritative project doc. Fold anything
  durable from it into the right place (Backlog task notes, README, or the
  educational site) and delete or archive this file once its content has
  been absorbed, per the project's "don't leave stale docs lying around"
  convention.
- Current Backlog "To Do" queue, in the order the operator wants work done,
  is: **TJC-5 → TJC-6 → TJC-7 → TJC-9 → (TJC-10...TJC-15, any order, not
  blocking) → TJC-1.23 (last)**. Confirm this is still the operator's
  intended order before starting the next task, since priorities can shift
  between sessions.
