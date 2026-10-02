'use strict';

window.TCPages['failure-museum'] = async function (root) {
  const underspecTxt = await TC.fetchText('data/evaluations/test_01_underspecified.txt');
  const geoValidityTxt = await TC.fetchText('data/evaluations/test_03_cw_validity.txt');

  root.innerHTML = `
    ${TC.pageHeader('Failure Museum', 'Failure detection is a feature, not a failure of the agent. Five concrete, repository-grounded ways this system can — and should — say "no" or "wait."')}

    <h2>Failure 1 — Underspecified natural-language problem</h2>
    <div class="panel">
      <p><strong>Input:</strong> <em>"The chaser is 200 meters behind the target. Find a one-orbit
      rendezvous."</em> (<code>evaluations/formalizer/test_01_underspecified.txt</code>)</p>
      <p><strong>Why it's problematic:</strong> no reference orbit, no coordinate frame/convention, no
      relative velocity, and "200 meters behind" is itself ambiguous (behind in along-track? radial? which sign
      convention?).</p>
      <p><strong>What the agent should do:</strong> per the recorded evaluation, the
      <code>orbital-problem-formalizer</code> skill identified all of the missing items above and classified
      the problem <code>NEEDS MORE INFORMATION + MODEL VALIDITY CONCERN</code> — it explicitly did NOT attempt
      to solve the problem. Per <code>baseline_comparison.md</code> (Test 1), the model-validity concern here is
      not that CW is definitively invalid, but that applicability <em>cannot yet be established</em> because the
      reference orbit and coordinate convention are unknown — a distinct and more precise claim than simply
      flagging missing fields.</p>
      <p><strong>What the deterministic solver should do:</strong> nothing yet — there is no valid 6-vector
      state or mean motion to pass to <code>two_burn_targeting()</code>. The deterministic layer is never
      reached because the LLM layer correctly stops first.</p>
      <p><strong>How verification catches it:</strong> not applicable at this stage — verification only runs on
      a completed solve. This failure is caught entirely at the formalization step, before any numbers exist to
      verify.</p>
      <details><summary style="cursor:pointer;color:var(--accent)">Show recorded evaluation transcript</summary>
        <pre class="code">${TC.esc(underspecTxt)}</pre>
      </details>
    </div>

    <h2>Failure 2 — Exact one-orbit CW targeting (singularity)</h2>
    <div class="panel">
      <p><strong>Input:</strong> Fully-specified 350 km rendezvous (<code>examples/rendezvous_case_01.yaml</code>),
      but with <code>t_final</code> set to exactly one orbital period: <code>t = 2π/n</code>.</p>
      <p><strong>Why it's problematic:</strong> at this transfer time, <code>sin(n·t) → 0</code> and the Φrv
      block of the CW STM loses rank — the two-impulse targeting problem is mathematically ill-posed (see
      <a href="#/singularity">Why the Singularity Matters</a> for the full derivation and a live numeric
      sweep).</p>
      <p><strong>What the agent should do:</strong> if asked to target exactly one orbital period, recognize
      (or be told by the solver) that this specific duration is numerically singular and either choose a
      different transfer time or explain the constraint to the operator.</p>
      <p><strong>What the deterministic solver should do:</strong> <code>two_burn_targeting()</code> calls
      <code>check_phi_rv_conditioning()</code>, which raises <code>CWSingularTransferError</code> — this is
      exactly what <code>tests/test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected</code> confirms.
      ${TC.badge('tested', 'IMPLEMENTED / TESTED')}</p>
      <p><strong>How verification catches it:</strong> in this case, verification never even runs — the solver
      itself refuses to produce a result, which is the strongest possible failure signal (an exception, not a
      warning).</p>
    </div>

    <h2>Failure 3 — Large GEO-scale separation</h2>
    <div class="panel">
      <p><strong>Input:</strong> <code>examples/geo_failure_case.yaml</code> — GEO reference orbit (42,164 km
      radius), chaser 14,000,000 m away (along-track), requesting CW.</p>
      <p><strong>Why it's problematic:</strong> the separation is ~33% of the orbital radius — nowhere near the
      "small relative separation" CW requires. See <a href="#/model-validity">Model Validity</a> for the full
      breakdown.</p>
      <p><strong>What the agent should do:</strong> per <code>evaluations/formalizer/test_03_cw_validity.txt</code>,
      the formalizer flagged a model-validity concern because "a separation of ~1/3 of the GEO belt... strongly
      violates the fundamental small-relative-distance assumption underlying the linearized CW equations" —
      even though CW was explicitly requested.</p>
      <p><strong>What the deterministic solver should do:</strong> <code>validate_cw_use()</code> flags this
      with "Relative separation is large compared with orbit radius" (confirmed live on the Model Validity
      page). <code>two_burn_targeting()</code> itself, however, will still happily compute <em>a</em> Δv for
      this case if called directly — it has no built-in GEO-scale rejection; only
      <code>validate_cw_use()</code> catches it, and nothing forces that check to run first.
      ${TC.badge('partial', 'PARTIAL')}</p>
      <p><strong>How verification catches it:</strong> <code>validate_against_two_body()</code> on this case
      (demonstrated live on the <a href="#/experiment">CW vs Two-Body Experiment</a> page, "Load: GEO failure
      case" preset) shows the independent two-body propagation diverging from CW's prediction by <strong>millions
      of meters</strong> after a quarter orbit — triggering "MODEL VALIDITY WARNING."</p>
      <details><summary style="cursor:pointer;color:var(--accent)">Show recorded evaluation transcript</summary>
        <pre class="code">${TC.esc(geoValidityTxt)}</pre>
      </details>
    </div>

    <h2>Failure 4 — Bad/ambiguous coordinate convention</h2>
    <div class="panel">
      <p><strong>Input:</strong> any natural-language description using "behind," "ahead," "above," "below"
      without stating the frame. E.g. does "200 m behind" mean −y (along-track, this repo's convention) or
      some other axis entirely?</p>
      <p><strong>Why it's problematic:</strong> per <code>reference/SOURCE.md</code>: "Coordinate definitions
      must be stated explicitly because LVLH/RTN/RIC naming varies across sources." A sign or axis mix-up
      produces a <em>numerically valid but physically wrong</em> result — the solver has no way to detect this
      from the numbers alone, because a correctly-computed targeting solution for the wrong initial state is
      still internally self-consistent.</p>
      <p><strong>What the agent should do:</strong> the <code>orbital-problem-formalizer</code> skill is
      explicitly instructed: "Do not silently choose a coordinate convention." It should surface frame
      ambiguity as missing information rather than guessing.</p>
      <p><strong>What the deterministic solver should do:</strong> nothing — <code>src/cw.py</code> has no way
      to detect a frame-convention error; it trusts its inputs completely. This is a case where
      <strong>missing information</strong> (not a model-validity concern) must be caught upstream by the LLM
      layer, because no downstream numerical check can catch a correctly-computed answer to the wrong
      question.</p>
      <p><strong>How verification catches it:</strong> it generally does NOT. If both the CW propagation and
      the two-body verification are fed the same wrong initial state (consistent with the same wrong frame
      assumption), they will agree with each other — and both be wrong in the same way. This is an important
      limitation: independent verification catches <em>dynamics-model</em> errors, not <em>input-specification</em>
      errors. ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED (no automated frame-consistency check exists)')}</p>
    </div>

    <h2>Failure 5 — CW and two-body disagreement</h2>
    <div class="panel">
      <p><strong>Input:</strong> any scenario (not necessarily GEO-scale) where linearization error has
      accumulated enough to matter — e.g. a long multi-revolution transfer, or simply a borderline-large
      separation at a long transfer time.</p>
      <p><strong>Why it's problematic:</strong> CW predicts one answer; the independent nonlinear two-body
      integration predicts a measurably different one. Trusting the CW answer anyway risks a real maneuver
      based on physically inaccurate linearized dynamics.</p>
      <p><strong>What the agent should do:</strong> treat a "MODEL VALIDITY WARNING" as a hard stop requiring
      either a different model (two-body/higher-fidelity) or explicit human sign-off, not something to explain
      away.</p>
      <p><strong>What the deterministic solver should do:</strong> nothing automatically — <code>two_burn_targeting()</code>
      doesn't call the verification layer itself; a caller must invoke <code>validate_against_two_body()</code>
      separately. ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED (no automatic verification trigger)')}</p>
      <p><strong>How verification catches it:</strong> this IS the thing <code>compare_cw_two_body()</code> and
      <code>validate_against_two_body()</code> are built for — confirmed working by
      <code>tests/test_validation.py::test_model_validity_warning_triggers</code>. ${TC.badge('tested', 'IMPLEMENTED / TESTED (for compare_cw_two_body)')}</p>
    </div>

    ${TC.callout('good', 'The point of this museum', `<p>Every "failure" above is a case where some part of the
      system <strong>correctly refused to produce a false-confidence answer</strong> — a rejected solve, a
      flagged validity concern, a withheld solution pending more information, or a verification warning. The
      one true gap (Failure 4, frame ambiguity) is honestly the hardest: it shows a case where the current
      architecture has <em>no</em> automated safety net, and must rely entirely on the LLM formalization step
      getting it right the first time.</p>`)}

    <p><a href="#/research">Continue: Research Connection →</a></p>
  `;
};
