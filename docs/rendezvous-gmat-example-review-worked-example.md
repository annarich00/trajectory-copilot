# Worked example: `/rendezvous` with the GMAT-example review step (TJC-15)

`.pi/prompts/rendezvous.md` step 4 (added by TJC-15) hands the script generated
by the GMAT tool call (step 3) to the project-local `gmat-example-reviewer`
subagent (TJC-14) and step 5 reports its verdict next to, never instead of, the
numerical outcome. This page records one real end-to-end run of the chain
**request -> formalizer -> model selector -> `run_gmat_verification` tool call
-> GMAT-example review -> combined report**, and says precisely which parts of
that chain were and were not exercised. Static guard for the prompt step:
`tests/test_rendezvous_prompt_reviewer_step.py`.

## Design choices recorded here

* **Advisory only.** The review is labelled "GMAT-example review (advisory,
  stylistic; does not affect VERIFIED/FAIL)". `verified`, `verification_status`
  and the `unified_verification_report` come only from the GMAT tool /
  `src/gmat_verify.py` / `src/verification_report.py`, which TJC-15 does not
  touch.
* **Non-blocking.** If the `subagent` tool is missing, the agent is not
  discovered, or the subagent errors, the workflow still finishes and reports
  "GMAT-example review skipped/unavailable" with a reason. The prompt also
  forbids the main agent from writing or imitating a verdict itself.
* **Mission type for CW rendezvous.** The corpus
  (`research/gmat_example_corpus/corpus.json`) has no rendezvous /
  relative-motion entry (TJC-14 finding). The prompt therefore passes the *real*
  mission type ("two-spacecraft Clohessy-Wiltshire (CW) LVLH-relative
  rendezvous between a chief and a deputy") and accepts/reports
  `NO CORPUS ENTRY`. It deliberately does **not** pass a nearest-neighbour
  type such as `orbit_transfer` to get a SATISFACTORY/DIVERGENT verdict
  (TJC-14 Run B showed that works, but it is a comparison against a different
  mission type and would look like a real verdict).
* **Single-spacecraft coast exception (TJC-20).** Step 1's exception is
  unchanged; step 4 passes "single-spacecraft two-body coast / orbit
  propagation" there and relays whatever the reviewer returns.
* **No script, no review.** If step 3 generated no script (for example
  `CW_TARGETING_INFEASIBLE`), step 4 is skipped with "no script generated".

## How the example was produced (honest provenance)

Environment: worktree `class_example_traj_copilot-tjc-15`, real
`GmatConsole-R2026a`, `pi` headless with the project-local
`run_gmat_verification` tool loaded, model `MIT-parley` default
(`openai/gpt-5.4-mini`).

1. **Real full-chain run** of the prompt through `pi -p -a --mode json
   "/rendezvous <request>"` (request below, `--output-dir /tmp/tjc15_run2`).
   Formalizer, model selector, a real `run_gmat_verification` tool call and the
   final report all genuinely ran: `verified=true`, `PASS`, position error
   7.94e-3 m, velocity error 1.17e-5 m/s, `screenshot_source=svg_fallback`.
2. **Step 4 was NOT exercised through the `subagent` tool.** The headless
   `pi -p` session exposed no `subagent`/`subagents_enable` tool (checked: its
   system tool list is read/bash/edit/write/`run_gmat_verification`/walkthrough
   only; also with `-e .../pi-subagents`; the agent itself probed and reported
   neither tool exists). So in this real run the agent correctly took the
   AC3 fallback and reported "GMAT-example review skipped/unavailable: no
   subagent tool was available in this session" while still giving the
   VERIFIED numerical result. That is a real, unedited demonstration of the
   non-blocking path.
3. **The reviewer verdict shown below is a separate real run of the reviewer
   definition against the script generated in step 1**, using the same method
   as TJC-14 (`pi -p --no-session --no-context-files --no-skills
   --no-prompt-templates --system-prompt <agent file body> --tools
   read,grep,find,ls "<task>"`), *not* the `subagent` tool, so the agent's
   frontmatter / project-scope discovery was not exercised. The combined report
   in section "Combined report" is therefore a **composite**: report text from
   run 1 (verbatim apart from the review line) plus the reviewer block from
   run 3 pasted in where step 5 says to put it. It shows the intended final
   shape; it is not a single transcript.
4. **Reviewer variance.** The reviewer ran 3 times on the same script with the
   same task: 2 x `NO CORPUS ENTRY` (the intended verdict) and 1 x `DIVERGENT`
   whose divergences cite other-mission-type entries (and itself says the
   corpus has no CW rendezvous entry). The DIVERGENT sample is exactly the
   kind of unfaithful output the advisory/no-override design contains: it
   cannot change the numerical `VERIFIED`. Reviewer verdicts are LLM samples,
   not deterministic.
5. **An earlier, discarded attempt.** In a first run (before step 4 gained the
   "never write or imitate a verdict" rule) the agent, lacking a `subagent`
   tool, printed a fabricated "review" block via a shell `echo` and reported it
   as the review. That output is *not* used here; it is why the prompt now
   forbids self-authored verdicts (and why a static test guards that sentence).
6. **Visualization stages** (`scene`, `trajectory`, `comparison`) reported
   `not_generated` in this run because `plotly` is missing from the venv used
   (a known, pre-existing environment gap, unrelated to TJC-15), which the
   prompt's `not_generated` rule handles.

## Request

> Our chief satellite is in a circular orbit at 350 km altitude (radius 6728
> km, mu 398600441800000 m^3/s^2). The deputy is currently 15 m radial, -200 m
> along-track, 0 m cross-track from the chief, with relative velocity
> (-0.14, 0, 0) m/s in LVLH x-radial/y-along-track/z-normal. Rendezvous it with
> the chief (zero relative position and velocity) in one quarter of the chief's
> orbital period using two impulsive burns. Tolerances: 1 m, 0.001 m/s.

## Chain as recorded

| Step | What happened (run 1) |
|---|---|
| 1. Formalizer | `Scope: supported`, LVLH state/terminal conditions specified, derived period 5492.119 s, `Readiness: READY TO SOLVE` |
| 2. Model selector | 6-item table all `Supported`; `Selection: CW rendezvous` |
| 3. GMAT tool call | `run_gmat_verification` with the case fields (`transfer_time_s` 1373.0298005070088, `gmat_executable="GmatConsole-R2026a"`, `output_dir=/tmp/tjc15_run2`) -> `verified=true`, `verification_status=VERIFIED`, comparison `PASS`; script `/tmp/tjc15_run2/generated_cw_rendezvous.script` (identical to the committed `examples/cw_gmat_slice_example/generated_cw_rendezvous.script` except for the output-directory paths) |
| 4. Review | In run 1: `subagent` tool unavailable -> skipped/unavailable. Reviewer definition run separately on that script -> `NO CORPUS ENTRY` (below) |
| 5. Report | numerical result first, then the labelled advisory review item |

## Combined report (composite; see provenance above)

```
Final outcome (numerical, authoritative):
- outcome: VERIFIED
- verified: true
- verification_status: VERIFIED
- GMAT comparison: PASS (position error 0.00794 m, velocity error 1.17e-05 m/s;
  tolerances 1 m / 0.001 m/s)
- trust_statement: GMAT independently confirmed the CW candidate within tolerance
- Artifacts: /tmp/tjc15_run2/generated_cw_rendezvous.script,
  /tmp/tjc15_run2/trajectory.svg, /tmp/tjc15_run2/verification_report.txt
  (scene / trajectory / comparison plots: not_generated -- plotly unavailable)

GMAT-example review (advisory, stylistic; does not affect VERIFIED/FAIL):
GMAT example review (format/structure/convention only; not numerical or screenshot verification)
Verdict: NO CORPUS ENTRY
Script reviewed: /tmp/tjc15_run2/generated_cw_rendezvous.script
Mission type: two-spacecraft Clohessy-Wiltshire (CW) LVLH-relative rendezvous between a chief and a deputy
Corpus entries cited: none
Divergences:
- not assessed
Advisory (not a mission-type comparison): no same-mission-type corpus entries were found; the corpus mission types include orbit_transfer, lunar_transfer, lunar_impactor, lunar_swingby, finite_burn_propulsion, electric_propulsion, attitude_pointing, mars_orbit_constellation, station_keeping, leo_propagation, elliptical_orbit_propagation, sso_inclination_study, ground_station_contact, interplanetary_transfer, outer_planet_moon_exploration
Limits: Numerical correctness and trajectory screenshots are verified separately by the gmat-rendezvous-verification contract.
```

What run 1 itself actually printed for the review item (unedited, the real
fallback): `GMAT-example review (advisory, stylistic; does not affect
VERIFIED/FAIL): skipped/unavailable: no subagent tool was available in this
session`, followed by `Overall: VERIFIED by solver + independent GMAT
comparison.`

## Not exercised

* A real `subagent({ agent: "gmat-example-reviewer", ... agentScope: "project" })`
  call from inside the `/rendezvous` run (no `subagent` tool in headless `pi -p`).
  Use an interactive pi session with `pi-subagents` active to try it.
* The bounded two-body fallback path and the single-spacecraft coast exception
  through step 4 (static prompt text only).
* The `CW_TARGETING_INFEASIBLE` "no script generated" skip (static prompt text
  only).
