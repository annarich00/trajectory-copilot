---
description: Run a rendezvous request through the full formalizer -> model-selector -> deterministic-solver -> GMAT-verification pipeline, in that exact order, with no step skipped or silently reordered.
argument-hint: "<natural-language rendezvous request>"
---
A rendezvous request follows. Run it through the complete required pipeline,
in this exact order, and do not skip, reorder, or silently combine any step:

1. Reason over the request yourself to derive each formalization field's
   value and provenance label (specified/derived/assumed/missing/ambiguous/
   contradictory/unit-inconsistent/out of scope), then call the
   `formalize_rendezvous_problem` pi tool (registered by
   `.pi/extensions/orbital-problem-formalizer-tool/`) with those field
   values to validate and render its full required output (Scope through
   Readiness). The formalizer itself is scoped only to two-spacecraft
   LVLH-relative rendezvous requests, so a single-spacecraft inertial-Cartesian coast request (no second
   spacecraft, no relative frame, no targeting objective) correctly comes
   back `OUT OF SCOPE` *for the formalizer* -- in that specific case,
   proceed anyway, directly to the `orbital-two-body-rendezvous` skill via
   step 2's model selection, per `reference/SOURCE.md` §C and
   `evaluations/benchmark/case_c_two_body.json`'s own committed precedent.
   For every other `NEEDS CLARIFICATION` or genuinely out-of-scope case
   (not a single-spacecraft coast), stop here and report that status --
   do not proceed to step 2.
2. Reason over the formalizer's output yourself to assess each of the six
   required items (circularity/locality/duration-regime/frame/other-physics/
   maneuver-assumptions as supported/violated/boundary/unknown), then call
   the `select_rendezvous_model` pi tool (registered by
   `.pi/extensions/orbital-model-selector-tool/`) with those assessments to
   combine them into the resulting selection (`CW rendezvous`,
   `bounded two-body fallback`, `UNSUPPORTED`, or `NEEDS MORE INFORMATION`)
   and the named deterministic tool handoff. Show the full six-item
   assessment table and the resulting selection.
   Do not solve anything or call any Python in this step.
   Visualization artifacts (TJC-16.5) are produced and reported live, one per
   pipeline stage, in this order: (a) the 3D relative-position scene right
   after this step and before the GMAT-verification step, (b) the
   trajectory/burns plot right after the deterministic solve and before GMAT
   execution, and (c) the verification comparison plot right after GMAT
   execution and parsing. State each artifact's path to the operator in the step-5 summary.
3. Construct the matching `src/workflow.py::RendezvousCase` object from the
   exact values recorded in steps 1-2 (do not re-derive or re-guess any
   value already produced above). Do not call `src/cw.py` or `src/twobody.py`
   directly outside the paths below, and do not report any numeric burn,
   delta-v, or final state as a result until a real, GMAT-verified call has
   actually run:
   - If step 2 selected `CW rendezvous`:
     1. Before any GMAT call, run the 3D scene stage and report its
        `paths` to the operator immediately and save for the final summary:
        `.venv/bin/python scripts/rendezvous_visualization_stage.py scene --case-json '<the same structured case fields used for the tool call below>' --output-dir <output_dir>`
        then, still before GMAT, the trajectory/burns stage (it re-runs the
        same deterministic `solve_cw_rendezvous` on the same inputs and plots
        it) and report its `paths` immediately too:
        `.venv/bin/python scripts/rendezvous_visualization_stage.py trajectory --case-json '<same fields>' --output-dir <output_dir>`.
        Report only the artifact path/status here -- still no numeric burn,
        delta-v, or final state until the GMAT-verified call below has run.
     2. Perform the GMAT-verification step
     by explicitly calling the `run_gmat_verification` pi tool (registered
     by the project-local `.pi/extensions/gmat-verification-tool/` extension)
     with the structured `case_id`/`mu_m3_s2`/`reference_radius_m`/
     `initial_relative_state`/`final_relative_state`/`transfer_time_s`/
     `pos_tol_m`/`vel_tol_mps`/`dv_tol_mps` fields from the `RendezvousCase`
     object above, and `gmat_executable="GmatConsole-R2026a"`. Call this
     tool explicitly -- as its own visible, auditable step in the
     transcript -- rather than only letting GMAT execution happen invisibly
     inside `run_rendezvous_workflow`. Treat the tool's returned
     `verified`/`verification_status`/`failure_mode` and embedded
     `unified_verification_report` as the authoritative GMAT verification
     result for this case. Pass the same `<output_dir>` as the tool's
     `output_dir` so the plot stages and GMAT share one directory.
     3. Immediately after that tool call returns, run the comparison stage
        and report its `paths` at once, before the step-5 summary:
        `.venv/bin/python scripts/rendezvous_visualization_stage.py comparison --case-json '<same fields>' --output-dir <output_dir> --comparison-status <unified_verification_report.comparison.status>`.
        Then report the existing GMAT screenshot path
        (`trajectory_screenshot` from the tool result), unchanged.
   - If step 2 selected `bounded two-body fallback` (not covered by the
     `run_gmat_verification` tool, which wraps only the CW path): call
     `src/workflow.py::run_rendezvous_workflow(...)` directly with
     `gmat_executable="GmatConsole-R2026a"`, exactly as before. That call
     also records the same three stages in
     `artifacts["visualization_artifacts"]` (and via its `on_artifact`
     callback), and for this path each is `not_generated` with a concrete
     `reason` (no relative state, no burns, no solver state history). Report
     each of those `not_generated` stages and its `reason` as it is
     produced; never substitute an approximate plot.
   - A stage whose record has `status` `"not_generated"` (e.g. CW targeting
     infeasible, GMAT never ran so the comparison is `INCOMPLETE`) must be
     reported to the operator as `not_generated` together with its `reason`,
     in pipeline order, never silently skipped and never replaced with a
     fabricated plot.
4. GMAT-example review (TJC-15). Right after the real GMAT call in step 3
   has returned -- and before the final report in step 5 -- hand the script
   that call generated to the project-local `gmat-example-reviewer` subagent
   (`.pi/agents/gmat-example-reviewer.md`) by calling the `subagent` tool, for
   example `subagent({ agent: "gmat-example-reviewer", task: "<task text>",
   async: false, options: { agentScope: "project" } })`. The task text must give
   the subagent both of its required inputs: (a) the generated GMAT script
   path -- `<output_dir>/generated_cw_rendezvous.script` on the CW path (the
   `output_dir` passed to the `run_gmat_verification` tool and returned in its
   result), or `artifacts["generated_script"]` from
   `run_rendezvous_workflow(...)` on the bounded two-body fallback path -- and
   (b) the mission type of the original request, stated in plain words.
   Mission type to pass: the real one, not a flattering neighbour. For a CW
   rendezvous that is "two-spacecraft Clohessy-Wiltshire (CW) LVLH-relative
   rendezvous between a chief and a deputy". The corpus
   `research/gmat_example_corpus/corpus.json` has no rendezvous/relative-motion
   entry (recorded in `docs/gmat-example-reviewer-example-run.md`), so
   `NO CORPUS ENTRY` is the expected, honest verdict for CW rendezvous: report
   it as-is. Do not substitute a different corpus mission type (for example
   `orbit_transfer`) to obtain a SATISFACTORY/DIVERGENT verdict, and do not
   fabricate a comparison. For the single-spacecraft coast exception in step 1
   pass "single-spacecraft two-body coast / orbit propagation" and let the
   reviewer map it to a corpus mission type only if unambiguous; relay
   whatever verdict it returns, including `NO CORPUS ENTRY`.
   Skip this step, noting "no script generated" in the report, when step 3
   produced no GMAT script (for example `CW_TARGETING_INFEASIBLE`).
   The subagent's verdict is advisory and stylistic only (script format,
   structure and convention). It is reported alongside, not instead of, the
   numerical outcome, and it must never change `FAIL` to `VERIFIED` or
   `VERIFIED` to `FAIL` (or alter `verified`, `verification_status`, or the
   `unified_verification_report`) on its own: the PASS/WARNING/FAIL/INCOMPLETE
   numerical contract in `src/gmat_verify.py` and `src/verification_report.py`
   is the only source of `VERIFIED`/`FAIL`. If the `subagent` tool is
   unavailable, the `gmat-example-reviewer` agent cannot be discovered, or the
   subagent errors or returns nothing usable, do not block or retry
   indefinitely and do not withhold the result: still complete the workflow, still
   report the numerical result in step 5, and state explicitly "GMAT-example
   review skipped/unavailable" with the one-line reason. Never write, echo,
   paraphrase, or imitate a review verdict yourself (for example by
   printing text from a shell command): a verdict may be reported only if it
   was actually returned by a real `gmat-example-reviewer` subagent call.
5. Report the final `outcome`, `verified`, `verification_status`, and
   `trust_statement` from that real call, plus the artifact paths (including
   a recap, in pipeline order, of the visualization artifacts already
   reported above). State
   plainly whether this is `VERIFIED` (solver succeeded AND GMAT
   independently confirmed it) or merely a solver-only result. Then add the
   step-4 review as a separate, clearly labelled item -- "GMAT-example review
   (advisory, stylistic; does not affect VERIFIED/FAIL)" -- containing the
   subagent's verdict block verbatim, or the skipped/unavailable (or "no
   script generated") note from step 4. The numerical result comes first and
   is stated independently of the review.
6. If the user separately asks to "pull up," "open," "see," or "visualize"
   the GMAT GUI interactively (as opposed to asking for the screenshot
   artifact already produced in step 3 and reported in step 5), give the user this exact
   command to run themselves in their own terminal:

   ```bash
   cd /home/anna_ford/opt/GMAT/R2026a/bin
   ./GMAT-R2026a -r <path to the generated GUI preview script>
   ```

   Fill in `<path to the generated GUI preview script>` with the actual
   script path from this run's `artifacts` (the GUI preview script, not the
   console-mode verification script), regenerating it first if it does not
   already exist for this case.

   If the user requests you to run it, use subagents to attempt to launch
   `GMAT-R2026a` with the GUI process yourself with a timeout of 30 seconds.

Request:
$ARGUMENTS
