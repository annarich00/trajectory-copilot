'use strict';

window.TCPages['verification'] = async function (root) {
  const verifySrc = await TC.fetchText('data/src/verify.py');
  const tbSrc = await TC.fetchText('data/src/twobody.py');

  const compareSym = TC.extractPySymbol(verifySrc, 'compare_cw_two_body');
  const chiefSym = TC.extractPySymbol(verifySrc, '_chief_circular_state');
  const basisSym = TC.extractPySymbol(verifySrc, '_lvlh_basis');
  const relToAbsSym = TC.extractPySymbol(verifySrc, '_rel_lvlh_to_absolute');
  const absToRelSym = TC.extractPySymbol(verifySrc, '_absolute_to_rel_lvlh');
  const validateSym = TC.extractPySymbol(verifySrc, 'validate_against_two_body');
  const keplerSym = TC.extractPySymbol(tbSrc, 'kepler_propagate_state');

  root.innerHTML = `
    ${TC.pageHeader('Verification Layers', 'Internal CW-versus-two-body comparison, planned pinned Poliastro implementation cross-check, and required GMAT numerical plus visual verification.')}
    ${TC.teachingContract({
      assumptions: 'Central-body two-body gravity, circular chief construction, repository LVLH convention, and declared numerical tolerances.',
      symbols: '<code>μ</code>: gravitational parameter; <code>r,v</code>: inertial state; <code>r̂,t̂,ĥ</code>: LVLH basis.',
      mapping: '<code>reference/SOURCE.md §§A,B,D</code> → <code>src/twobody.py</code> and <code>src/verify.py</code>.',
      evidence: '<code>tests/test_twobody.py</code> and <code>tests/test_validation.py</code>; full transformation path remains incompletely tested.',
      limitations: 'TJC-1.5 owns fallback hardening, TJC-1.6 owns frame-transform verification, and TJC-1.7 owns the pinned Poliastro cross-check. Poliastro and GMAT verification are not implemented yet.'
    })}

    <h2>Three distinct verification layers</h2>
    <table>
      <tr><th>Layer</th><th>What it checks</th><th>Current status</th></tr>
      <tr><td>Repository two-body path</td><td>Checks CW linearization against the project’s nonlinear point-mass RK4 implementation.</td><td>Implemented but incompletely audited/tested.</td></tr>
      <tr><td>Pinned Poliastro</td><td>Checks <code>src/twobody.py</code> against a separate like-for-like implementation in archived Poliastro 0.17.0, isolated under Python 3.10.</td><td>Architecture defined by TJC-1.27; adapter/environment planned in TJC-1.7.</td></tr>
      <tr><td>GMAT</td><td>Required end-to-end numerical propagation and returned trajectory screenshot.</td><td>Planned; not yet integrated.</td></tr>
    </table>
    ${TC.callout('info', 'Pinned external implementation', '<p>Poliastro is pinned to immutable commit <code>c7d12e9b715d3fd60f2be233af707d5b97617d39</code> and must run outside the core environment because v0.17.0 requires Python &lt;3.11 and legacy scientific dependencies. It is archived, so it is evidence—not a universal oracle. <a href="data/docs/poliastro-verification-architecture.md">Read the full request/result and future-model policy →</a></p>')}

    <h2>The current internal architecture</h2>
    <div class="chain">
      <div class="node">CW relative state (LVLH)</div><div class="arr">↓</div>
      <div class="node">LVLH → inertial (chief + deputy absolute states)</div><div class="arr">↓</div>
      <div class="node">nonlinear two-body RK4 propagation (BOTH bodies)</div><div class="arr">↓</div>
      <div class="node">inertial → LVLH</div><div class="arr">↓</div>
      <div class="node">compare against CW's own linear prediction</div>
    </div>

    <h2>Why this is stronger than comparing CW to itself</h2>
    <p>A naive "verification" might call <code>propagate_relative_state()</code> twice with slightly different
    code paths and declare agreement — but that only checks for internal consistency of the same linear model,
    not whether the linear model is <em>correct</em>. If <code>cw_stm()</code> itself had a sign error, calling
    it twice would agree with itself perfectly while being wrong.</p>
    <p><code>validate_against_two_body()</code> in <code>src/verify.py</code> instead builds a genuinely
    independent reference: it converts the CW relative state into two separate, absolute, inertial Cartesian
    states (a chief and a deputy), and propagates <strong>both</strong> of them forward using
    <code>kepler_propagate_state()</code> — a nonlinear RK4 integration of <code>r̈ = −μr/|r|³</code> that has no
    CW linearization baked into it at all. Only after that does it convert back into the LVLH relative frame
    for comparison. Disagreement between the two paths reflects genuine CW linearization error, not a
    self-consistency artifact.</p>

    <h2>Walking through src/verify.py</h2>

    <h3>Step 1 — Build a chief orbit consistent with n and μ</h3>
    ${TC.codeRef('src/verify.py', '_chief_circular_state')}
    ${TC.authorityBanner('Exact, unmodified text from src/verify.py.')}
    ${chiefSym ? TC.codeBlock(chiefSym.code, chiefSym.startLine) : ''}
    <p>Places the chief on the inertial X-axis with velocity along inertial Y, consistent with the given mean
    motion. This defines a concrete, absolute circular orbit that corresponds to the abstract <code>n</code>
    used throughout the CW math.</p>

    <h3>Step 2 — Define the LVLH basis in inertial coordinates</h3>
    ${TC.codeRef('src/verify.py', '_lvlh_basis')}
    ${TC.authorityBanner('Exact, unmodified text from src/verify.py.')}
    ${basisSym ? TC.codeBlock(basisSym.code, basisSym.startLine) : ''}
    <p>Builds the rotation matrix (r̂, t̂, ĥ) — radial, along-track, cross-track unit vectors in the inertial
    frame — directly from the chief's instantaneous position and velocity, using the orbit-normal
    <code>r × v</code> for the cross-track direction. This is what makes the LVLH↔inertial conversion exact
    rather than approximate, for a circular reference orbit.</p>

    <h3>Step 3 — Convert the CW relative state into two absolute states</h3>
    ${TC.codeRef('src/verify.py', '_rel_lvlh_to_absolute')}
    ${TC.authorityBanner('Exact, unmodified text from src/verify.py.')}
    ${relToAbsSym ? TC.codeBlock(relToAbsSym.code, relToAbsSym.startLine) : ''}
    <p>Converts the relative position/velocity (in LVLH) into an absolute inertial deputy position/velocity,
    properly accounting for the rotating-frame velocity term (<code>ω × r_rel</code>, where ω = n·ĥ) — this is
    the Coriolis correction needed because LVLH is a rotating frame and inertial dynamics are not.</p>

    <h3>Step 4 — Propagate BOTH bodies nonlinearly</h3>
    ${TC.codeRef('src/twobody.py', 'kepler_propagate_state')}
    ${TC.authorityBanner('Exact, unmodified text from src/twobody.py \u2014 classic 4th-order Runge-Kutta integration of the true nonlinear two-body gravity law.')}
    ${keplerSym ? TC.codeBlock(keplerSym.code, keplerSym.startLine) : ''}
    <p>Both the chief and deputy absolute states are propagated independently with this same nonlinear
    integrator. Neither call knows anything about CW, Hill's equations, or linearization — it is pure
    <code>F = ma</code> under central gravity.</p>

    <h3>Step 5 — Convert back to LVLH and compare</h3>
    ${TC.codeRef('src/verify.py', '_absolute_to_rel_lvlh')}
    ${TC.authorityBanner('Exact, unmodified text from src/verify.py.')}
    ${absToRelSym ? TC.codeBlock(absToRelSym.code, absToRelSym.startLine) : ''}
    ${TC.codeRef('src/verify.py', 'compare_cw_two_body')}
    ${TC.authorityBanner('Exact, unmodified text from src/verify.py.')}
    ${compareSym ? TC.codeBlock(compareSym.code, compareSym.startLine) : ''}

    <h3>The orchestrating function</h3>
    ${TC.codeRef('src/verify.py', 'validate_against_two_body')}
    ${TC.authorityBanner('Exact, unmodified text from src/verify.py \u2014 this is the authoritative independent-verification pipeline. It is implemented but, as noted below, has no dedicated automated test.')}
    ${validateSym ? TC.codeBlock(validateSym.code, validateSym.startLine) : ''}

    ${TC.callout('warn', 'Test coverage gap', `<p><code>compare_cw_two_body()</code> alone is tested
      (<code>tests/test_validation.py::test_model_validity_warning_triggers</code>), but
      <code>validate_against_two_body()</code> \u2014 the full LVLH\u2192inertial\u2192two-body\u2192LVLH pipeline \u2014 has
      <strong>no dedicated automated test</strong> in this repository. ${TC.badge('partial', 'PARTIAL')}</p>`)}

    <h2>See it live</h2>
    <p>The <a href="#/experiment">CW vs Two-Body Experiment</a> page runs a pedagogical browser mirror of this
    exact pipeline interactively, including the GEO-scale failure case where CW and two-body diverge
    dramatically.</p>
  `;
};
