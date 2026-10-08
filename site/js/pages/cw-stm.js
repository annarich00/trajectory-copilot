'use strict';

window.TCPages['cw-stm'] = async function (root) {
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const testSrc = await TC.fetchText('data/tests/test_cw.py');
  const cwStmSym = TC.extractPySymbol(cwSrc, 'cw_stm');

  root.innerHTML = `
    ${TC.pageHeader('CW State-Transition Matrix (STM)', 'A step-by-step derivation and code map for the circular-chief Clohessy–Wiltshire state-transition matrix.')}
    ${TC.teachingContract({
      assumptions: 'Unperturbed two-body gravity; circular chief; small local relative motion and velocity; right-handed LVLH/RIC frame. This is not an eccentric-chief, global-phasing, perturbation, thrust-coast, or guaranteed long-duration model.',
      symbols: '<code>X=[x,y,z,ẋ,ẏ,ż]ᵀ</code>; x is radial outward, y is along-track/in-track in the chief direction of motion, z is orbit-normal; <code>n</code> is positive mean motion [rad/s], <code>θ=nt</code>, <code>s=sin θ</code>, and <code>c=cos θ</code>.',
      mapping: '<code>reference/SOURCE.md §A–B</code> → <code>docs/cw-stm-audit.md</code> → <code>src/cw.py::cw_stm</code>. The Python source is authoritative; this browser lesson is pedagogical.',
      evidence: '<code>tests/test_cw.py::test_cw_stm_identity_at_zero_time</code> and <code>test_cw_stm_blocks_match_cited_quarter_orbit_terms_and_units</code>.',
      limitations: 'The audit found no STM defect. Two-burn targeting singularity handling is separate TJC-1.4 scope; do not infer an arbitrary target-time solution from this lesson.'
    })}

    <h2>1. Start from the CW equations</h2>
    <p>For the stated axes, the circular-chief linearization is:</p>
    <div class="formula">ẍ − 2nẏ − 3n²x = 0<br>ÿ + 2nẋ = 0<br>z̈ + n²z = 0</div>
    <p>The x–y equations are coupled by the rotating-frame Coriolis terms. The z equation is an independent harmonic oscillator. The controlled reference is <code>reference/SOURCE.md §B</code>; the independent audit cites Clohessy &amp; Wiltshire (1960), Eqs. 1–3, and Schaub &amp; Junkins (2018), §14.6, Eqs. 14.48–14.51.</p>

    <h2>2. Assemble the state solution</h2>
    <p>Integrating those equations for initial state <code>X(0)</code> gives <code>X(t)=Φ(t)X(0)</code>, partitioned into position and velocity blocks:</p>
    <div class="formula" style="display:block;max-width:420px;">[ r(t) ]&nbsp;&nbsp; [ Φrr&nbsp;&nbsp;Φrv ]&nbsp; [ r(0) ]<br>[ v(t) ] = [ Φvr&nbsp;&nbsp;Φvv ]&nbsp; [ v(0) ]</div>
    <p>Each block is 3×3. Because position is metres and velocity is m/s, Φrr and Φvv are dimensionless, Φrv has seconds, and Φvr has s⁻¹.</p>

    <h2>3. Derive each block term</h2>
    <h3>Position from initial position: Φrr</h3>
    <div class="formula">Φrr = [[4−3c, 0, 0], [6(s−θ), 1, 0], [0, 0, c]]</div>
    <p>The radial solution supplies <code>4−3c</code>; integration of the in-plane coupling supplies the secular along-track term <code>6(s−θ)</code>; the y initial displacement persists as 1; and the uncoupled z oscillator supplies <code>c</code>. These are <code>phi_rr</code> in <code>cw_stm</code>.</p>
    <h3>Position from initial velocity: Φrv</h3>
    <div class="formula">Φrv = [[s/n, 2(1−c)/n, 0], [2(c−1)/n, (4s−3θ)/n, 0], [0, 0, s/n]]</div>
    <p>One integration of the velocity contribution gives the 1/n factors and therefore seconds. This is <code>phi_rv</code>. Its use in targeting is outside this task’s scope, but its terms and signs are directly regression-tested.</p>
    <h3>Velocity from initial position: Φvr</h3>
    <div class="formula">Φvr = [[3ns, 0, 0], [6n(c−1), 0, 0], [0, 0, −ns]]</div>
    <p>Differentiating the position solution gives the n factors (s⁻¹) and the z sign <code>−ns</code>. This is <code>phi_vr</code>.</p>
    <h3>Velocity from initial velocity: Φvv</h3>
    <div class="formula">Φvv = [[c, 2s, 0], [−2s, 4c−3, 0], [0, 0, c]]</div>
    <p>Differentiation yields the Coriolis-coupled off-diagonals <code>+2s</code> and <code>−2s</code>, plus the z oscillator <code>c</code>. This is <code>phi_vv</code>.</p>

    <h2>4. Time-zero and dimensions check</h2>
    <p>At <code>t=0</code>, θ=0, s=0, and c=1. Every off-diagonal block term vanishes, Φrr and Φvv become identity, so Φ(0)=I₆. The regression uses exact zero with absolute tolerance <code>1e-15</code>. The quarter-orbit regression separately checks every nonzero block term at θ=π/2 and makes sign/order mistakes visible.</p>

    <h2>5. Authoritative code and test mirrors</h2>
    ${TC.codeRef('src/cw.py', 'cw_stm')}
    ${TC.authorityBanner('Exact, synchronized source mirror; Python remains authoritative.')}
    ${cwStmSym ? TC.codeBlock(cwStmSym.code, cwStmSym.startLine) : ''}
    ${TC.codeRef('tests/test_cw.py', 'STM regression tests')}
    ${TC.authorityBanner('Exact, synchronized test mirror; the browser does not execute this test.')}
    ${TC.codeBlock(testSrc, 1)}

    <h2>Audit conclusion and limits</h2>
    <p><code>docs/cw-stm-audit.md</code> found no sign, term, state-ordering, dimension, or time-zero defect in <code>cw_stm</code>. The conclusion is limited to the cited circular-chief CW STM. Validate a real case’s circularity, locality, duration, frame, maneuvers, and perturbation requirements independently; the site is not a physics oracle.</p>
  `;
};
