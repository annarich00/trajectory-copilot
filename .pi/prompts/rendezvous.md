---
description: Run a rendezvous request through the full formalizer -> model-selector -> deterministic-solver -> GMAT-verification pipeline, in that exact order, with no step skipped or silently reordered.
argument-hint: "<natural-language rendezvous request>"
---
A rendezvous request follows. Run it through the complete required pipeline,
in this exact order, and do not skip, reorder, or silently combine any step:

1. Apply the `orbital-problem-formalizer` skill. Produce its full required
   Markdown output (Scope through Readiness). The formalizer itself is
   scoped only to two-spacecraft LVLH-relative rendezvous requests, so a
   single-spacecraft inertial-Cartesian coast request (no second
   spacecraft, no relative frame, no targeting objective) correctly comes
   back `OUT OF SCOPE` *for the formalizer* -- in that specific case,
   proceed anyway, directly to the `orbital-two-body-rendezvous` skill via
   step 2's model selection, per `reference/SOURCE.md` §C and
   `evaluations/benchmark/case_c_two_body.json`'s own committed precedent.
   For every other `NEEDS CLARIFICATION` or genuinely out-of-scope case
   (not a single-spacecraft coast), stop here and report that status --
   do not proceed to step 2.
2. Apply the `orbital-model-selector` skill against the formalizer's output.
   Show the full six-item assessment table and the resulting selection
   (`CW rendezvous`, `bounded two-body fallback`, `UNSUPPORTED`, or
   `NEEDS MORE INFORMATION`) and the named deterministic tool handoff.
   Do not solve anything or call any Python in this step.
3. Construct the matching `src/workflow.py::RendezvousCase` object from the
   exact values recorded in steps 1-2 (do not re-derive or re-guess any
   value already produced above). Do not call `src/cw.py` or `src/twobody.py`
   directly outside the paths below, and do not report any numeric burn,
   delta-v, or final state as a result until a real, GMAT-verified call has
   actually run:
   - If step 2 selected `CW rendezvous`: perform the GMAT-verification step
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
     result for this case.
   - If step 2 selected `bounded two-body fallback` (not covered by the
     `run_gmat_verification` tool, which wraps only the CW path): call
     `src/workflow.py::run_rendezvous_workflow(...)` directly with
     `gmat_executable="GmatConsole-R2026a"`, exactly as before.
4. Report the final `outcome`, `verified`, `verification_status`, and
   `trust_statement` from that real call, plus the artifact paths. State
   plainly whether this is `VERIFIED` (solver succeeded AND GMAT
   independently confirmed it) or merely a solver-only result.
5. If the user separately asks to "pull up," "open," "see," or "visualize"
   the GMAT GUI interactively (as opposed to asking for the screenshot
   artifact already produced in step 3-4), do NOT attempt to launch
   `GMAT-R2026a` or any GUI process yourself. This is a confirmed,
   non-retry-able sandbox limitation (see `src/gmat_verify.py::
   attempt_gmat_gui_screenshot`'s docstring for the full diagnosis: no GPU
   render-node path, and WSLg/RDP never forwards a rendered buffer to the
   user's real desktop even when a window registers). Instead, respond with
   exactly this: state plainly that an interactive GMAT window cannot be
   opened from inside this sandboxed session, and give the user this exact
   command to run themselves in their own terminal (not through you):

   ```bash
   cd /home/anna_ford/opt/GMAT/R2026a/bin
   ./GMAT-R2026a -r <path to the generated GUI preview script>
   ```

   Fill in `<path to the generated GUI preview script>` with the actual
   script path from this run's `artifacts` (the GUI preview script, not the
   console-mode verification script), regenerating it first if it does not
   already exist for this case.

Request:
$ARGUMENTS
