'use strict';

window.TCPages['singularity'] = async function (root) {
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const checkSym = TC.extractPySymbol(cwSrc, 'check_phi_rv_conditioning');
  const errSym = TC.extractPySymbol(cwSrc, 'CWSingularTransferError');
  const testSrc = await TC.fetchText('data/tests/test_cw.py');
  const testSym = TC.extractPySymbol(testSrc, 'test_cw_exact_one_orbit_targeting_is_rejected');

  root.innerHTML = `
    ${TC.pageHeader('Why the Singularity Matters', 'A numerical solver returning a number does not mean the physical problem has a valid solution. This is the central lesson of the exact-one-orbit CW targeting case.')}

    <h2>The setup</h2>
    <p>Take the repository's 350&nbsp;km rendezvous case, but set the transfer time to <em>exactly</em> one full
    orbital period:</p>
    <div class="formula">t = 2π / n &nbsp;&nbsp;(one full orbit)</div>
    <p>At this transfer time, <code>n·t = 2π</code>, so <code>sin(n·t) = sin(2π) = 0</code> (up to floating-point
    round-off). Recall from the <a href="#/cw-stm">CW STM Explorer</a> that the Φrv block (velocity→position) has
    <code>sin(n·t)/n</code> on its diagonal. When sin(n·t)→0, those diagonal terms collapse toward zero and Φrv
    loses rank — <code>two_burn_targeting()</code> must invert Φrv to solve for Δv0, and an unstable or singular
    inversion is numerically catastrophic.</p>

    <h2>Live demonstration: sweeping through the singularity</h2>
    <p>Below, a pedagogical browser mirror of <code>cw_stm()</code> and the targeting solve is evaluated at
    transfer times ranging from 0.90·T to 1.10·T (T = one orbital period). Watch <code>|Δv0|</code> explode as
    the fraction approaches exactly 1.0, then watch the mirror <strong>reject</strong> the problem outright right
    at the singularity, in the same way <code>CWSingularTransferError</code> does in the real Python code.</p>
    ${TC.mirrorBanner(['cw.py :: cw_stm', 'cw.py :: check_phi_rv_conditioning', 'cw.py :: two_burn_targeting'])}

    <div class="panel">
      <div class="control-row">
        <label>Sweep range around 1 orbit</label>
        <input type="range" id="sg-frac" min="0.90" max="1.10" step="0.0005" value="0.90" />
        <span class="value-tag" id="sg-frac-val">0.9000 T</span>
      </div>
      <div class="result-grid" id="sg-results"></div>
      <div id="sg-table-wrap"></div>
    </div>

    <h2>What happened in the (hypothetical) naive implementation</h2>
    <div class="chain">
      <div class="node">tiny numerical error in Φrv</div><div class="arr">↓</div>
      <div class="node">least-squares "solves" an ill-posed system anyway</div><div class="arr">↓</div>
      <div class="node">enormous computed Δv (e.g. ~10¹³ m/s)</div><div class="arr">↓</div>
      <div class="node">final_state still shows ≈0 (because the math is self-consistent)</div><div class="arr">↓</div>
      <div class="node">physically absurd trajectory — no real engine can deliver this Δv</div>
    </div>
    ${TC.callout('bad', 'The trap', `<p>A naive implementation using <code>numpy.linalg.pinv</code> or
      least-squares would happily return a number here. The <em>final_state</em> check would even look
      "correct" (near zero) because the math is internally consistent — the enormous Δv0 and compensating Δv1
      exactly cancel out in the simulated trajectory. The output looks like success. It is not: no spacecraft
      can execute a multi-trillion m/s burn. This narrative is illustrative, grounded in the actual numerical
      behavior of the CW equations themselves (reproducible by sweeping <code>t_final</code> toward
      <code>2π/n</code> in <code>src/cw.py</code>'s own <code>cw_stm()</code>/<code>np.linalg.cond</code>) —
      it does not describe a literal prior version of this repository's code, which this site has no record of.</p>`)}

    <h2>What the actual repository code does instead</h2>
    <div class="chain">
      <div class="node">ill-conditioned / singular Φrv detected</div><div class="arr">↓</div>
      <div class="node"><code>check_phi_rv_conditioning()</code> computes cond(Φrv), compares to 1e6 limit</div><div class="arr">↓</div>
      <div class="node"><code>CWSingularTransferError</code> raised</div><div class="arr">↓</div>
      <div class="node">solution rejected — caller must choose a different transfer time</div>
    </div>

    ${TC.codeRef('src/cw.py', 'CWSingularTransferError (class docstring)')}
    ${TC.authorityBanner('Exact, unmodified text of the <code>CWSingularTransferError</code> class and its docstring from <code>src/cw.py</code>.')}
    ${errSym ? TC.codeBlock(errSym.code, errSym.startLine) : ''}

    ${TC.codeRef('src/cw.py', 'check_phi_rv_conditioning')}
    ${TC.authorityBanner('Exact, unmodified text of <code>check_phi_rv_conditioning()</code> from <code>src/cw.py</code> — this is the authoritative singularity guard. The sweep demo above uses a hand-ported JS approximation of this same logic (with a cruder condition-number estimate; see site/js/physics.js) purely to animate the concept.')}
    ${checkSym ? TC.codeBlock(checkSym.code, checkSym.startLine) : ''}

    <h2>The test that locks in this behavior</h2>
    ${TC.codeRef('tests/test_cw.py', 'test_cw_exact_one_orbit_targeting_is_rejected')}
    ${TC.authorityBanner('Exact, unmodified text of the pytest test from tests/test_cw.py. Running this test with pytest — not this website — is the authoritative confirmation that CWSingularTransferError is raised.')}
    ${testSym ? TC.codeBlock(testSym.code, testSym.startLine) : ''}
    <p>${TC.badge('tested', 'IMPLEMENTED / TESTED')} This test calls <code>two_burn_targeting()</code> at
    <code>t_final = 2π/n</code> exactly and asserts (via <code>pytest.raises</code>) that
    <code>CWSingularTransferError</code> is raised. If a future change silently reintroduced a least-squares
    fallback, this test would fail — this is the regression guard against the exact failure mode illustrated
    above.</p>

    <h2>The core lesson</h2>
    ${TC.callout('warn', 'A numerical solver returning a number does not mean the physical problem has a valid solution.', `
      <p>Floating-point arithmetic will almost always produce <em>some</em> output for <code>A⁻¹b</code>, even
      when A is numerically singular — unless the code explicitly checks the condition number first and refuses
      to proceed. "The code ran without crashing" is not evidence that the result is physically meaningful.
      Verification and validity-checking (like <code>check_phi_rv_conditioning()</code>) are not optional
      extras — they are what separates a physics engine from a pile of linear algebra that happens to compile.</p>
    `)}
    <p>This is a direct motivation for Trajectory CoPilot's layered architecture: an LLM alone, asked to "solve"
    this exact-one-orbit case, has no inherent mechanism to detect that the underlying linear system is
    singular — it would need to either recall this specific CW fact from training data (unreliable) or defer to
    a deterministic numerical check (reliable). See <a href="#/research">Research Connection</a>.</p>
  `;

  const fracI = root.querySelector('#sg-frac');
  const fracVal = root.querySelector('#sg-frac-val');
  const resultsEl = root.querySelector('#sg-results');
  const tableWrap = root.querySelector('#sg-table-wrap');

  const mu = 3.986004418e14;
  const r0 = 6378e3 + 350e3;
  const n = TCPhysics.meanMotion(mu, r0);
  const T = 2 * Math.PI / n;
  const state0 = [15.0, -200.0, 0.0, -0.14, 0.0, 0.0];

  function recompute() {
    const frac = parseFloat(fracI.value);
    fracVal.textContent = frac.toFixed(4) + ' T';
    const t = frac * T;
    let dv0Norm, status, cond, errMsg;
    try {
      const phi = TCPhysics.cwStm(n, t);
      cond = TCPhysics.approxCond3(phi.phi_rv);
      const res = TCPhysics.twoBurnTargeting(state0, n, t);
      dv0Norm = TCPhysics.vNorm(res.dv0);
      status = dv0Norm > 100 ? 'warn' : 'good';
    } catch (e) {
      status = 'bad';
      errMsg = e.message;
    }

    resultsEl.innerHTML = `
      <div class="result-cell"><div class="label">n·t</div><div class="value">${TC.fmt(n*t,5)}</div></div>
      <div class="result-cell"><div class="label">sin(n·t)</div><div class="value">${TC.fmt(Math.sin(n*t),3)}</div></div>
      <div class="result-cell flag-${status}"><div class="label">${errMsg ? 'Status' : '|Δv0|'}</div>
        <div class="value">${errMsg ? 'REJECTED' : TC.fmt(dv0Norm,4) + ' m/s'}</div></div>
      <div class="result-cell"><div class="label">approx cond(Φrv)</div><div class="value">${isFinite(cond) ? cond.toExponential(2) : '∞'}</div></div>
    `;
    if (errMsg) {
      tableWrap.innerHTML = TC.callout('bad', 'Browser mirror throws (illustrative — not the real CWSingularTransferError)', `<p>The pedagogical JS mirror throws its own stand-in error class with a similar message:</p><p class="mono">${TC.esc(errMsg)}</p><p class="toc-inline">The actual <code>CWSingularTransferError</code> is a Python exception defined in <code>src/cw.py</code> and only ever raised by running that Python code (see test above).</p>`);
    } else {
      tableWrap.innerHTML = '';
    }
  }
  fracI.addEventListener('input', recompute);
  recompute();

  // Sweep table (static, computed once) to make the "explosion" visible without needing to drag precisely.
  const fracs = [0.90, 0.95, 0.99, 0.999, 0.9999, 0.99999, 1.0, 1.00001, 1.0001, 1.001, 1.01, 1.05];
  let rows = '';
  for (const f of fracs) {
    const t = f * T;
    let cell;
    try {
      const res = TCPhysics.twoBurnTargeting(state0, n, t);
      const mag = TCPhysics.vNorm(res.dv0);
      cell = `<td class="mono">${mag.toExponential(3)} m/s</td>`;
    } catch (e) {
      cell = `<td class="mono" style="color:var(--bad)">REJECTED (CWSingularTransferError)</td>`;
    }
    rows += `<tr><td>${f}</td><td class="mono">${TC.fmt(f*T,2)} s</td>${cell}</tr>`;
  }
  root.insertAdjacentHTML('beforeend', `
    <h3>Fixed sweep table (fraction of one orbital period → |Δv0|)</h3>
    ${TC.mirrorBanner('cw.py :: two_burn_targeting')}
    <table><tr><th>t / T</th><th>t (s)</th><th>|Δv0| or outcome (browser mirror)</th></tr>${rows}</table>
    <p class="toc-inline">Notice |Δv0| grows by many orders of magnitude as t/T → 1, then the exact-singular
    point is rejected outright rather than returning the (even larger) blow-up value. This table is a
    pedagogical browser mirror; the authoritative pass/fail behavior at exactly t/T=1 is established by
    <code>tests/test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected</code> running against the real
    Python <code>two_burn_targeting()</code>.</p>
  `);
};
