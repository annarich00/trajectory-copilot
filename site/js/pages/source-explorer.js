'use strict';

window.TCPages['source-explorer'] = async function (root) {
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const tbSrc = await TC.fetchText('data/src/twobody.py');
  const verifySrc = await TC.fetchText('data/src/verify.py');
  const optSrc = await TC.fetchText('data/src/optimization.py');
  const sourceMd = await TC.fetchText('data/reference/SOURCE.md');
  const formalizerSkill = await TC.fetchText('data/skills/formalizer.SKILL.md');
  const selectorSkill = await TC.fetchText('data/skills/model-selector.SKILL.md');
  const cwSkill = await TC.fetchText('data/skills/targeting-planner.SKILL.md');
  const twoBodySkill = await TC.fetchText('data/skills/two-body-rendezvous.SKILL.md');
  const gmatSkill = await TC.fetchText('data/skills/gmat-verification.SKILL.md');

  root.innerHTML = `
    ${TC.pageHeader('Source Code Explorer', 'Guided tour of every important source file in this repository, with annotations — not a rewrite.')}
    <div class="toc-inline">Jump to: <a href="#se-cw">src/cw.py</a> · <a href="#se-tb">src/twobody.py</a> ·
    <a href="#se-verify">src/verify.py</a> · <a href="#se-opt">src/optimization.py</a> ·
    <a href="#se-source">reference/SOURCE.md</a> · <a href="#se-skills">active skills</a></div>

    <h2 id="se-cw">src/cw.py</h2>
    <table>
      <tr><th>Problem solved</th><td>Clohessy-Wiltshire linearized relative motion: compute mean motion, the
        6×6 state-transition matrix, propagate relative states, check CW applicability, detect singular/
        ill-conditioned targeting problems, and solve two-impulse rendezvous targeting.</td></tr>
      <tr><th>Public functions</th><td class="mono">mean_motion, cw_stm, propagate_relative_state,
        validate_cw_use, check_phi_rv_conditioning, two_burn_targeting</td></tr>
      <tr><th>Public types</th><td class="mono">CWValidity (dataclass), CWSingularTransferError (exception)</td></tr>
      <tr><th>Data in</th><td>Scalars (μ, n, t), 3- and 6-vectors (positions/velocities/states) as
        <code>np.ndarray</code> or array-like.</td></tr>
      <tr><th>Data out</th><td>Scalars (n, condition number), 6×6 / 3×3 <code>np.ndarray</code> matrices,
        6-vectors, or a raised <code>CWSingularTransferError</code>.</td></tr>
      <tr><th>Assumptions</th><td>Circular (or near-circular) reference orbit; relative motion small enough for
        linearization; LVLH convention x=radial, y=along-track, z=cross-track (per reference/SOURCE.md).</td></tr>
      <tr><th>Tests</th><td class="mono">tests/test_cw.py (3 tests, all of them — see Test Explorer)</td></tr>
      <tr><th>Known limitations</th><td>Only two-impulse targeting (no continuous thrust, no multi-rev-aware
        targeting). <code>validate_cw_use()</code> implements only two numeric heuristics (separation ratio,
        transfer-time span) — it does not check for non-circular chief orbits or GEO-scale geometry.</td></tr>
    </table>
    <details open><summary style="cursor:pointer;color:var(--accent)">Full annotated source</summary>
      ${TC.authorityBanner('Exact, unmodified contents of src/cw.py.')}
      ${TC.codeBlock(cwSrc, 1)}
    </details>

    <h2 id="se-tb">src/twobody.py</h2>
    <table>
      <tr><th>Problem solved</th><td>Nonlinear two-body (point-mass gravity) orbital dynamics: orbital period,
        vis-viva speed, and Cartesian-state propagation via RK4 integration of <code>r̈ = −μr/|r|³</code>.</td></tr>
      <tr><th>Public functions</th><td class="mono">orbital_period, vis_viva_speed, kepler_propagate_state,
        propagate_cartesian_state, specific_orbital_energy, specific_angular_momentum, unsupported_request</td></tr>
      <tr><th>Public type</th><td class="mono">TwoBodyCase — stable SI Cartesian case metadata for a later like-for-like external verifier.</td></tr>
      <tr><th>Data in</th><td>Positive μ [m³/s²], finite duration [s], positive steps, and 3-vectors (r0, v0) or six-element SI inertial Cartesian state.</td></tr>
      <tr><th>Data out</th><td>Scalars (period, speed) or propagated position/velocity vectors / 6-vector
        state.</td></tr>
      <tr><th>Assumptions</th><td>Pure point-mass central gravity; no perturbations (no J2, drag, SRP,
        third-body); no thrust during the propagated interval; fixed-step RK4 (not adaptive).</td></tr>
      <tr><th>Tests</th><td class="mono">tests/test_twobody.py: circular analytical return, energy/angular-momentum invariants, CW-invalid deterministic coast case, metadata, unsupported request, and invalid-input tests.</td></tr>
      <tr><th>Known limitations</th><td>Coast propagation only: no burns, targeting, optimization, LVLH-relative input, perturbations, or adaptive integration. Poliastro is not imported; its isolated adapter is deferred to TJC-1.7.</td></tr>
    </table>
    <details><summary style="cursor:pointer;color:var(--accent)">Full annotated source</summary>
      ${TC.authorityBanner('Exact, unmodified contents of src/twobody.py.')}
      ${TC.codeBlock(tbSrc, 1)}
    </details>

    <h2 id="se-verify">src/verify.py</h2>
    <table>
      <tr><th>Problem solved</th><td>Independent verification of a CW relative-motion prediction against
        nonlinear two-body propagation, via LVLH↔inertial frame conversion of both a chief and deputy
        spacecraft.</td></tr>
      <tr><th>Public functions</th><td class="mono">compare_cw_two_body, validate_against_two_body</td></tr>
      <tr><th>Private helpers</th><td class="mono">_chief_circular_state, _lvlh_basis, _rel_lvlh_to_absolute,
        _absolute_to_rel_lvlh</td></tr>
      <tr><th>Public types</th><td class="mono">VerificationResult (dataclass: cw_state, two_body_state,
        position_error_m, velocity_error_mps, warnings)</td></tr>
      <tr><th>Data in</th><td>CW relative state, mean motion, transfer time, μ, position/velocity
        tolerances.</td></tr>
      <tr><th>Data out</th><td><code>VerificationResult</code>, including a <code>warnings</code> tuple that
        contains <code>"MODEL VALIDITY WARNING"</code> if tolerances are exceeded.</td></tr>
      <tr><th>Assumptions</th><td>Assumes a circular chief orbit consistent with the given <code>n</code> and
        <code>μ</code> (via <code>_chief_circular_state()</code>); depends on <code>twobody.py</code>'s pure
        point-mass propagation.</td></tr>
      <tr><th>Tests</th><td class="mono">tests/test_validation.py::test_model_validity_warning_triggers tests
        <code>compare_cw_two_body()</code> only. <code>validate_against_two_body()</code> \u2014 the full pipeline
        \u2014 has NO dedicated test. ${TC.badge('partial', 'PARTIAL')}</td></tr>
      <tr><th>Known limitations</th><td>No automated test of the full LVLH\u2192inertial\u2192two-body\u2192LVLH round
        trip; relies entirely on <code>twobody.py</code>'s untested-for-correctness RK4 propagation.</td></tr>
    </table>
    <details><summary style="cursor:pointer;color:var(--accent)">Full annotated source</summary>
      ${TC.authorityBanner('Exact, unmodified contents of src/verify.py.')}
      ${TC.codeBlock(verifySrc, 1)}
    </details>

    <h2 id="se-opt">src/optimization.py</h2>
    <table>
      <tr><th>Problem solved</th><td>Describes rendezvous optimization problem <em>templates</em> (objective +
        decision variables + constraints) as plain data — intended to connect the Targeting/Optimization
        Planner skill's output to a future numeric solver.</td></tr>
      <tr><th>Public functions</th><td class="mono">minimize_delta_v_problem, minimize_transfer_time_problem,
        delta_v_constrained_rendezvous_problem</td></tr>
      <tr><th>Public types</th><td class="mono">RendezvousOptimizationProblem (dataclass: objective,
        decision_variables, constraints, notes)</td></tr>
      <tr><th>Data in</th><td>For <code>delta_v_constrained_rendezvous_problem</code>: a Δv budget (m/s). The
        other two functions take no arguments.</td></tr>
      <tr><th>Data out</th><td>A <code>RendezvousOptimizationProblem</code> describing the problem shape — no
        numbers are solved for.</td></tr>
      <tr><th>Assumptions</th><td>None computational — this file contains no physics or numerical solving at
        all.</td></tr>
      <tr><th>Tests</th><td class="mono">NONE. There is no tests/test_optimization.py in this repository.
        ${TC.badge('planned', 'IMPLEMENTED — NOT TESTED')}</td></tr>
      <tr><th>Known limitations</th><td><strong>This file does not call any solver.</strong> It is a set of
        dataclass-returning template functions with no connection to <code>two_burn_targeting()</code> or any
        other numeric code. There is currently no code path from "optimization problem description" to "an
        actual numeric optimization run." ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED (solver integration)')}</td></tr>
    </table>
    <details><summary style="cursor:pointer;color:var(--accent)">Full annotated source</summary>
      ${TC.authorityBanner('Exact, unmodified contents of src/optimization.py.')}
      ${TC.codeBlock(optSrc, 1)}
    </details>

    <h2 id="se-skills">Active scoped skills</h2>
    <p>The active architecture is deliberately limited to formulation, assumption-based selection, fixed-duration CW rendezvous, bounded two-body coast fallback, and GMAT verification. The browser copies below are verbatim non-authoritative mirrors; the files under <code>.pi/skills/</code> are controlled text.</p>
    ${TC.authorityBanner('Exact, unmodified controlled-skill mirrors; implementation remains authoritative in src/.')}
    <details><summary>Problem formulation</summary><pre class="code">${TC.esc(formalizerSkill)}</pre></details>
    <details><summary>Model selection</summary><pre class="code">${TC.esc(selectorSkill)}</pre></details>
    <details><summary>CW rendezvous</summary><pre class="code">${TC.esc(cwSkill)}</pre></details>
    <details><summary>Bounded two-body fallback</summary><pre class="code">${TC.esc(twoBodySkill)}</pre></details>
    <details><summary>GMAT verification</summary><pre class="code">${TC.esc(gmatSkill)}</pre></details>

    <h2 id="se-source">reference/SOURCE.md</h2>
    <table>
      <tr><th>Problem solved</th><td>Not code — this is the physics reference document the orbital-mechanics
        skills are instructed to consult "instead of relying on pretrained memory" (per its own opening
        line).</td></tr>
      <tr><th>Sections</th><td>A. Frames, state ordering, and units · B. CW local rendezvous · C. bounded two-body coast fallback · D. assumption-based model selection · E. required GMAT verification evidence · F. future-work and unsupported boundary.</td></tr>
      <tr><th>Consumed by</th><td>The five controlled skills in <code>.pi/skills/</code> use its LVLH/state/unit contracts, assumption checklist, bounded fallback boundary, and GMAT numerical-plus-screenshot requirement.</td></tr>
      <tr><th>Tested?</th><td>Not applicable \u2014 this is prose documentation, not executable code. The
        singularity and validity claims it makes ARE indirectly exercised by
        <code>tests/test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected</code> and
        <code>test_cw_validation_basic</code>.</td></tr>
      <tr><th>Known limitations</th><td><code>validate_cw_use()</code> has only limited deterministic heuristics; full circularity/locality/duration/frame assessment is controlled-skill guidance. GMAT execution is required by the workflow but not integrated in this recovered repository.</td></tr>
    </table>
    <details><summary style="cursor:pointer;color:var(--accent)">Full document</summary>
      ${TC.authorityBanner('Exact, unmodified contents of reference/SOURCE.md.')}
      <pre class="code">${TC.esc(sourceMd)}</pre>
    </details>
  `;
};
