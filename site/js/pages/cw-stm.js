'use strict';

window.TCPages['cw-stm'] = async function (root) {
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const cwStmSym = TC.extractPySymbol(cwSrc, 'cw_stm');
  const propSym = TC.extractPySymbol(cwSrc, 'propagate_relative_state');

  const blocks = {
    rr: {
      label: 'Φrr',
      title: 'Position → Position',
      desc: 'Maps the initial relative position r(0) to its contribution to the final relative position r(t), with no velocity involved. Dimensions: 3×3, dimensionless (position in, position out).',
      code: `phi_rr = np.array([\n    [4 - 3 * c, 0.0, 0.0],\n    [6 * (s - nt), 1.0, 0.0],\n    [0.0, 0.0, c],\n])`,
      meaning: `The (1,1) term (4−3c) shows how an initial radial offset free-drifts in radius over time — note it is 1
      (no drift) at t=0 and oscillates since the radial motion is bounded. The (2,1) term 6(s−nt) is the famous
      secular along-track drift driven by a radial offset: for small nt, 6(s−nt) ≈ −nt·(nt)² grows like t³ at
      very short times but in general grows without bound in t for a fixed radial offset — this is why *any*
      sustained radial offset causes unbounded along-track drift unless corrected. The (3,3) term is simple
      harmonic z-motion, decoupled from in-plane motion.`,
      test: 'Exercised (not isolated) inside tests/test_cw.py::test_cw_rendezvous_benchmark via two_burn_targeting(), which calls cw_stm() internally.',
    },
    rv: {
      label: 'Φrv',
      title: 'Velocity → Position',
      desc: 'Maps the initial relative velocity v(0) to its contribution to the final relative position r(t). Dimensions: 3×3, units of time (s) (velocity in [m/s], position out [m]).',
      code: `phi_rv = np.array([\n    [s / n, 2 * (1 - c) / n, 0.0],\n    [2 * (c - 1) / n, (4 * s - 3 * nt) / n, 0.0],\n    [0.0, 0.0, s / n],\n])`,
      meaning: `This is the single most important block in the entire codebase. two_burn_targeting() must invert
      Φrv to solve for the initial impulsive Δv0 needed to hit a target position. When sin(n·t) → 0 — which
      happens at every integer multiple of half the orbital period (n·t = kπ) — the (1,1) and (3,3) entries of
      Φrv vanish, and the whole matrix becomes singular or nearly so. This is exactly the mechanism explored in
      "Why the Singularity Matters."`,
      test: 'tests/test_cw.py::test_cw_rendezvous_benchmark (well-conditioned case, quarter orbit) and test_cw_exact_one_orbit_targeting_is_rejected (singular case, full orbit) both exercise Φrv directly through check_phi_rv_conditioning().',
    },
    vr: {
      label: 'Φvr',
      title: 'Position → Velocity',
      desc: 'Maps the initial relative position r(0) to its contribution to the final relative velocity v(t). Dimensions: 3×3, units of 1/time (s⁻¹) (position in [m], velocity out [m/s]).',
      code: `phi_vr = np.array([\n    [3 * n * s, 0.0, 0.0],\n    [6 * n * (c - 1), 0.0, 0.0],\n    [0.0, 0.0, -n * s],\n])`,
      meaning: `Used in two_burn_targeting() to compute the velocity the deputy will have just before the second
      (terminal) burn: vf_minus = Φvr·r0 + Φvv·(v0+Δv0). Physically this answers "given where I started, how
      much velocity does that initial position alone contribute to my final velocity?" — the (2,1) term
      6n(c−1) is the velocity analogue of the secular drift seen in Φrr.`,
      test: 'Exercised inside two_burn_targeting(), tested via tests/test_cw.py::test_cw_rendezvous_benchmark final_state assertions.',
    },
    vv: {
      label: 'Φvv',
      title: 'Velocity → Velocity',
      desc: 'Maps the initial relative velocity v(0) to its contribution to the final relative velocity v(t). Dimensions: 3×3, dimensionless.',
      code: `phi_vv = np.array([\n    [c, 2 * s, 0.0],\n    [-2 * s, 4 * c - 3, 0.0],\n    [0.0, 0.0, c],\n])`,
      meaning: `This is the velocity-only "rotation + stretch" of the system: note the (1,1)/(2,2) sub-block looks
      like a rotation-ish mixing of x,y velocity (with Coriolis-driven asymmetry: 2s and −2s off-diagonal, 4c−3
      vs c on the diagonal), while z-velocity (3,3)=c just oscillates independently.`,
      test: 'Exercised inside two_burn_targeting() in both tests/test_cw.py tests (both the quarter-orbit success case and the one-orbit rejection case).',
    },
  };

  root.innerHTML = `
    ${TC.pageHeader('CW State-Transition Matrix (STM)', 'The CW equations are linear and time-invariant, so their exact solution can be written as a single 6×6 matrix Φ(t) applied to the initial state.')}
    ${TC.teachingContract({
      assumptions: 'The CW circular-chief, local-motion, LVLH assumptions stated on the preceding lesson apply.',
      symbols: '<code>Φrr, Φrv, Φvr, Φvv</code> map initial position/velocity to final position/velocity; <code>n</code> is mean motion and <code>t</code> elapsed time.',
      mapping: '<code>reference/SOURCE.md §B</code> → <code>src/cw.py::cw_stm</code> and <code>propagate_relative_state</code>.',
      evidence: '<code>tests/test_cw.py</code> benchmark and singular-transfer tests exercise these blocks.',
      limitations: 'TJC-1.3 owns independent sign, convention, and derivation audit. Browser values are pedagogical mirrors only.'
    })}

    <div class="formula" style="display:block;max-width:360px;">
      [ r(t) ]&nbsp;&nbsp; [ Φrr&nbsp;&nbsp;Φrv ]&nbsp; [ r(0) ]<br/>
      [ v(t) ] = [ Φvr&nbsp;&nbsp;Φvv ]&nbsp; [ v(0) ]
    </div>

    <p>Each block is 3×3. Click a block below to see its exact code, physical meaning, and the test(s) that
    exercise it.</p>

    <div class="stm-grid" id="stm-grid">
      <div class="stm-block" data-block="rr"><div class="block-label">Φrr</div><div class="block-matrix">position → position</div></div>
      <div class="stm-block" data-block="rv"><div class="block-label">Φrv</div><div class="block-matrix">velocity → position</div></div>
      <div class="stm-block" data-block="vr"><div class="block-label">Φvr</div><div class="block-matrix">position → velocity</div></div>
      <div class="stm-block" data-block="vv"><div class="block-label">Φvv</div><div class="block-matrix">velocity → velocity</div></div>
    </div>
    <div id="block-detail"></div>

    ${TC.codeRef('src/cw.py', 'cw_stm')}
    ${TC.authorityBanner('Exact, unmodified text of <code>cw_stm()</code> from <code>src/cw.py</code>.')}
    ${cwStmSym ? TC.codeBlock(cwStmSym.code, cwStmSym.startLine) : ''}

    <h2>Interactive: propagate a state</h2>
    <p>Enter an initial relative state and a transfer time to see how it evolves under the CW equations.</p>
    ${TC.codeRef('src/cw.py', 'propagate_relative_state')}
    ${TC.authorityBanner('Exact, unmodified text of <code>propagate_relative_state()</code> from <code>src/cw.py</code> — this is the authoritative implementation. The slider panel below uses a hand-ported JS copy of this function purely for interactivity.')}
    ${propSym ? TC.codeBlock(propSym.code, propSym.startLine) : ''}

    ${TC.mirrorBanner('cw.py :: propagate_relative_state (via cw_stm)')}
    <div class="panel">
      <div class="control-row"><label>μ (m³/s²)</label><input type="number" id="stm-mu" value="398600441800000" /></div>
      <div class="control-row"><label>Reference altitude (km)</label><input type="number" id="stm-alt" value="350" /></div>
      <div class="control-row"><label>x₀, y₀, z₀ (m)</label>
        <input type="number" id="stm-x0" value="15" style="width:70px"/>
        <input type="number" id="stm-y0" value="-200" style="width:70px"/>
        <input type="number" id="stm-z0" value="0" style="width:70px"/>
      </div>
      <div class="control-row"><label>ẋ₀, ẏ₀, ż₀ (m/s)</label>
        <input type="number" id="stm-vx0" value="-0.14" step="0.01" style="width:70px"/>
        <input type="number" id="stm-vy0" value="0" step="0.01" style="width:70px"/>
        <input type="number" id="stm-vz0" value="0" step="0.01" style="width:70px"/>
      </div>
      <div class="control-row">
        <label>Transfer time t</label>
        <input type="range" id="stm-t-frac" min="0.01" max="2" step="0.01" value="0.25" />
        <span class="value-tag" id="stm-t-label">0.25 T</span>
      </div>
      <div class="result-grid" id="stm-results"></div>
    </div>
  `;

  const gridEl = root.querySelector('#stm-grid');
  const detailEl = root.querySelector('#block-detail');

  function showBlock(key) {
    gridEl.querySelectorAll('.stm-block').forEach((e) => e.classList.toggle('selected', e.dataset.block === key));
    const b = blocks[key];
    detailEl.innerHTML = `
      <div class="detail-box">
        <h3 style="margin-top:0">${b.label} — ${TC.esc(b.title)}</h3>
        <p>${TC.esc(b.desc)}</p>
        <pre class="code">${TC.esc(b.code)}</pre>
        <h4>Physical meaning</h4>
        <p>${b.meaning}</p>
        <h4>Test coverage</h4>
        <p>${TC.esc(b.test)}</p>
      </div>
    `;
  }

  gridEl.querySelectorAll('.stm-block').forEach((e) => {
    e.addEventListener('click', () => showBlock(e.dataset.block));
  });
  showBlock('rr');

  // Interactive propagation
  const muI = root.querySelector('#stm-mu');
  const altI = root.querySelector('#stm-alt');
  const x0I = root.querySelector('#stm-x0'), y0I = root.querySelector('#stm-y0'), z0I = root.querySelector('#stm-z0');
  const vx0I = root.querySelector('#stm-vx0'), vy0I = root.querySelector('#stm-vy0'), vz0I = root.querySelector('#stm-vz0');
  const tFracI = root.querySelector('#stm-t-frac');
  const tLabel = root.querySelector('#stm-t-label');
  const resultsEl = root.querySelector('#stm-results');

  function recompute() {
    const mu = parseFloat(muI.value);
    const r0 = 6378e3 + parseFloat(altI.value) * 1000;
    const n = TCPhysics.meanMotion(mu, r0);
    const T = 2 * Math.PI / n;
    const frac = parseFloat(tFracI.value);
    tLabel.textContent = frac.toFixed(2) + ' T  (' + TC.fmt(frac * T, 1) + ' s)';
    const state0 = [parseFloat(x0I.value), parseFloat(y0I.value), parseFloat(z0I.value),
                     parseFloat(vx0I.value), parseFloat(vy0I.value), parseFloat(vz0I.value)];
    const t = frac * T;
    const stateT = TCPhysics.propagateRelativeState(state0, n, t);
    resultsEl.innerHTML = `
      <div class="result-cell"><div class="label">n</div><div class="value">${TC.fmt(n,6)} rad/s</div></div>
      <div class="result-cell"><div class="label">T</div><div class="value">${TC.fmt(T,1)} s</div></div>
      <div class="result-cell"><div class="label">r(t)</div><div class="value">${TC.vecStr(stateT.slice(0,3),4)} m</div></div>
      <div class="result-cell"><div class="label">v(t)</div><div class="value">${TC.vecStr(stateT.slice(3,6),4)} m/s</div></div>
    `;
  }
  [muI, altI, x0I, y0I, z0I, vx0I, vy0I, vz0I, tFracI].forEach((i) => i.addEventListener('input', recompute));
  recompute();
};
