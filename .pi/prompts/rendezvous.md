---
description: Run a rendezvous request through the full formalizer -> model-selector -> deterministic-solver -> GMAT-verification pipeline, in that exact order, with no step skipped or silently reordered.
argument-hint: "<natural-language rendezvous request>"
---
A rendezvous request follows. Run it through the complete required pipeline,
in this exact order, and do not skip, reorder, or silently combine any step:

1. Apply the `orbital-problem-formalizer` skill. Produce its full required
   Markdown output (Scope through Readiness). Stop here and report
   `NEEDS CLARIFICATION` or `OUT OF SCOPE` if the case is not
   `READY TO SOLVE` -- do not proceed to step 2 in that case.
2. Apply the `orbital-model-selector` skill against the formalizer's output.
   Show the full six-item assessment table and the resulting selection
   (`CW rendezvous`, `bounded two-body fallback`, `UNSUPPORTED`, or
   `NEEDS MORE INFORMATION`) and the named deterministic tool handoff.
   Do not solve anything or call any Python in this step.
3. Construct the matching `src/workflow.py::RendezvousCase` object from the
   exact values recorded in steps 1-2 (do not re-derive or re-guess any
   value already produced above), and call
   `src/workflow.py::run_rendezvous_workflow(...)` directly with
   `gmat_executable="GmatConsole-R2026a"`. Do not call `src/cw.py` or
   `src/twobody.py` directly outside of that function, and do not report any
   numeric burn, delta-v, or final state as a result until this real,
   GMAT-verified call has actually run.
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
