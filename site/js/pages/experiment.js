'use strict';

window.TCPages['experiment'] = async function (root) {
  root.innerHTML = `
    ${TC.pageHeader('CW vs Two-Body Experiment', 'An interactive comparison driven by a pedagogical browser mirror of validate_against_two_body() in src/verify.py.')}

    ${TC.mirrorBanner(['verify.py :: validate_against_two_body', 'cw.py :: propagate_relative_state', 'twobody.py :: propagate_cartesian_state'])}

    <p>This experiment lets you vary the parameters that <code>validate_against_two_body()</code> actually
    accepts: the initial relative state (6 numbers), mean motion (via reference altitude), transfer time, and
    gravitational parameter. These are the only knobs the real Python function exposes — <a href="#model-caveats">see below</a>
    for what is <em>not</em> supported and would require real code changes (not invented here).</p>

    <div class="panel">
      <h3 style="margin-top:0">Reference orbit</h3>
      <div class="control-row"><label>μ (m³/s²)</label><input type="number" id="ex-mu" value="398600441800000" /></div>
      <div class="control-row"><label>Reference altitude (km)</label>
        <input type="range" id="ex-alt" min="150" max="40000" step="10" value="350" />
        <span class="value-tag" id="ex-alt-val">350 km</span>
      </div>

      <h3>Initial relative state (LVLH)</h3>
      <div class="control-row"><label>x₀, y₀, z₀ (m)</label>
        <input type="number" id="ex-x0" value="15" style="width:90px"/>
        <input type="number" id="ex-y0" value="-200" style="width:90px"/>
        <input type="number" id="ex-z0" value="0" style="width:90px"/>
      </div>
      <div class="control-row"><label>ẋ₀, ẏ₀, ż₀ (m/s)</label>
        <input type="number" id="ex-vx0" value="-0.14" step="0.01" style="width:90px"/>
        <input type="number" id="ex-vy0" value="0" step="0.01" style="width:90px"/>
        <input type="number" id="ex-vz0" value="0" step="0.01" style="width:90px"/>
      </div>

      <h3>Transfer time</h3>
      <div class="control-row"><label>Fraction of one orbital period</label>
        <input type="range" id="ex-tfrac" min="0.01" max="1.5" step="0.01" value="0.25" />
        <span class="value-tag" id="ex-tfrac-val">0.25 T</span>
      </div>

      <h3>Tolerances (as used by compare_cw_two_body)</h3>
      <div class="control-row"><label>Position tolerance (m)</label><input type="number" id="ex-postol" value="50" style="width:90px"/></div>
      <div class="control-row"><label>Velocity tolerance (m/s)</label><input type="number" id="ex-veltol" value="0.05" step="0.01" style="width:90px"/></div>

      <div class="control-row">
        <button class="btn secondary" id="ex-preset-350">Load: 350 km rendezvous (repo benchmark)</button>
        <button class="btn secondary" id="ex-preset-geo">Load: GEO failure case (examples/geo_failure_case.yaml)</button>
      </div>

      <div class="result-grid" id="ex-results"></div>
      <div id="ex-warning"></div>
    </div>

    <h2>Reading the result</h2>
    <p><strong>Position/velocity difference</strong> is how far the linear CW prediction and the independent
    nonlinear two-body propagation disagree after the same transfer time, starting from the same initial
    relative state. For a genuinely local, small-separation, short-duration proximity scenario, this
    difference should be tiny (sub-meter, sub-mm/s) — CW is an excellent local approximation. As separation
    grows, transfer time grows, or the geometry leaves "local proximity ops" territory (e.g. GEO-scale), the
    difference grows — eventually enough to trip <code>compare_cw_two_body()</code>'s
    <strong>"MODEL VALIDITY WARNING"</strong>.</p>

    <h2 id="model-caveats">What this experiment does NOT support, and why</h2>
    ${TC.callout('warn', 'Only real, existing parameters are exposed', `
      <p>The controls above map exactly to the arguments of <code>validate_against_two_body(initial_state, n,
      dt, mu, pos_tol_m, vel_tol_mps)</code> in <code>src/verify.py</code>. The following were considered and
      <strong>deliberately not added</strong>, because the underlying Python does not support them:</p>
      <ul>
        <li><strong>Non-circular (eccentric) chief orbit.</strong> <code>_chief_circular_state()</code>
        hard-codes a circular reference orbit from <code>n</code> and <code>μ</code> alone. There is no
        eccentricity parameter anywhere in <code>src/verify.py</code> or <code>src/cw.py</code>.
        ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED')}</li>
        <li><strong>Perturbations (J2, drag, SRP, third-body).</strong> <code>kepler_propagate_state()</code>
        integrates pure point-mass <code>r̈ = −μr/|r|³</code> only. ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED')}</li>
        <li><strong>Continuous/finite-burn maneuvers during the comparison window.</strong> Both CW propagation
        and two-body propagation here are coast-only; burns are handled separately by
        <code>two_burn_targeting()</code> and are not part of <code>validate_against_two_body()</code>.
        ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED')}</li>
        <li><strong>Multi-revolution wraparound choice (n·t &gt; 2π handled, but no explicit "number of
        revs" input).</strong> You can set the transfer-time slider above 1.0 to explore this; the underlying
        trig functions handle it correctly, there's just no separate "revolutions" UI concept in the Python
        API.</li>
      </ul>
    `)}

    <h2>Independent verification runs beneath this experiment too</h2>
    <p>Every time you click a preset or move a slider, the numbers below are produced by the pedagogical
    browser mirror of <em>both</em> <code>propagate_relative_state()</code> (CW) <em>and</em>
    <code>propagate_cartesian_state()</code> (nonlinear two-body) independently, then compared — mirroring the
    actual verification architecture, not re-running CW against itself.</p>
  `;

  const muI = root.querySelector('#ex-mu');
  const altI = root.querySelector('#ex-alt');
  const altVal = root.querySelector('#ex-alt-val');
  const x0I = root.querySelector('#ex-x0'), y0I = root.querySelector('#ex-y0'), z0I = root.querySelector('#ex-z0');
  const vx0I = root.querySelector('#ex-vx0'), vy0I = root.querySelector('#ex-vy0'), vz0I = root.querySelector('#ex-vz0');
  const tFracI = root.querySelector('#ex-tfrac');
  const tFracVal = root.querySelector('#ex-tfrac-val');
  const posTolI = root.querySelector('#ex-postol');
  const velTolI = root.querySelector('#ex-veltol');
  const resultsEl = root.querySelector('#ex-results');
  const warningEl = root.querySelector('#ex-warning');

  function recompute() {
    const mu = parseFloat(muI.value);
    const altKm = parseFloat(altI.value);
    altVal.textContent = altKm.toFixed(0) + ' km';
    const r0 = 6378e3 + altKm * 1000;
    const n = TCPhysics.meanMotion(mu, r0);
    const T = 2 * Math.PI / n;
    const frac = parseFloat(tFracI.value);
    tFracVal.textContent = frac.toFixed(2) + ' T (' + TC.fmt(frac * T, 1) + ' s)';
    const dt = frac * T;

    const state0 = [parseFloat(x0I.value), parseFloat(y0I.value), parseFloat(z0I.value),
                     parseFloat(vx0I.value), parseFloat(vy0I.value), parseFloat(vz0I.value)];
    const posTol = parseFloat(posTolI.value);
    const velTol = parseFloat(velTolI.value);

    let result;
    try {
      result = TCPhysics.validateAgainstTwoBody(state0, n, dt, mu, posTol, velTol, 3000);
    } catch (e) {
      resultsEl.innerHTML = `<div class="result-cell flag-bad"><div class="label">Error</div><div class="value">${TC.esc(e.message)}</div></div>`;
      warningEl.innerHTML = '';
      return;
    }

    const relSepRatio = TCPhysics.vNorm(state0.slice(0, 3)) / r0;

    resultsEl.innerHTML = `
      <div class="result-cell"><div class="label">n</div><div class="value">${TC.fmt(n,6)} rad/s</div></div>
      <div class="result-cell"><div class="label">Separation / r₀</div><div class="value">${(relSepRatio*100).toExponential(2)}%</div></div>
      <div class="result-cell"><div class="label">CW r(t)</div><div class="value">${TC.vecStr(result.cwState.slice(0,3),4)}</div></div>
      <div class="result-cell"><div class="label">Two-body r(t)</div><div class="value">${TC.vecStr(result.twoBodyState.slice(0,3),4)}</div></div>
      <div class="result-cell flag-${result.posErrM > posTol ? 'bad' : 'good'}"><div class="label">Position difference</div><div class="value">${TC.fmt(result.posErrM,4)} m</div></div>
      <div class="result-cell flag-${result.velErrMps > velTol ? 'bad' : 'good'}"><div class="label">Velocity difference</div><div class="value">${TC.fmt(result.velErrMps,6)} m/s</div></div>
    `;

    if (result.warnings.length) {
      warningEl.innerHTML = TC.callout('bad', 'MODEL VALIDITY WARNING (browser-mirror equivalent of compare_cw_two_body)', `
        <p>The pedagogical mirror of <code>compare_cw_two_body()</code> flags this comparison because position
        or velocity disagreement exceeds the tolerances you set. Physically: CW's linearized prediction and the
        independent nonlinear two-body propagation have diverged beyond what should be trusted — this is
        exactly the signal <code>src/verify.py</code> is designed to raise before a human (or agent) trusts a
        CW-based plan.</p>
      `);
    } else {
      warningEl.innerHTML = TC.callout('good', 'Within tolerance', `<p>CW and the independent two-body
        propagation agree within the specified tolerances for this scenario — consistent with CW being a valid
        local approximation here.</p>`);
    }
  }

  [muI, altI, x0I, y0I, z0I, vx0I, vy0I, vz0I, tFracI, posTolI, velTolI].forEach((i) => i.addEventListener('input', recompute));

  root.querySelector('#ex-preset-350').addEventListener('click', () => {
    muI.value = 398600441800000; altI.value = 350;
    x0I.value = 15; y0I.value = -200; z0I.value = 0;
    vx0I.value = -0.14; vy0I.value = 0; vz0I.value = 0;
    tFracI.value = 0.25; posTolI.value = 50; velTolI.value = 0.05;
    recompute();
  });

  root.querySelector('#ex-preset-geo').addEventListener('click', () => {
    // Values from examples/geo_failure_case.yaml
    muI.value = 398600441800000; altI.value = (42164000 - 6378e3) / 1000;
    x0I.value = 0; y0I.value = 14000000; z0I.value = 0;
    vx0I.value = 0; vy0I.value = 0; vz0I.value = 0;
    tFracI.value = 0.25; posTolI.value = 50; velTolI.value = 0.05;
    recompute();
  });

  recompute();
};
