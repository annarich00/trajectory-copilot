'use strict';

window.TCPages['physics-basics'] = async function (root) {
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const tbSrc = await TC.fetchText('data/src/twobody.py');
  const meanMotionSym = TC.extractPySymbol(cwSrc, 'mean_motion');
  const orbitalPeriodSym = TC.extractPySymbol(tbSrc, 'orbital_period');
  const visVivaSym = TC.extractPySymbol(tbSrc, 'vis_viva_speed');

  root.innerHTML = `
    ${TC.pageHeader('Learn the Physics — Orbital Motion Basics', 'The fundamental quantities that everything else in this repository is built on: gravitational parameter, orbital radius, mean motion, and orbital period.')}

    <h2>1. Gravitational parameter μ</h2>
    <p>μ (mu) is the standard gravitational parameter of the central body: μ = G·M, where G is the universal
    gravitational constant and M is the mass of the body being orbited (e.g. Earth). It has units of
    m³/s². Knowing μ and a spacecraft's position/velocity is enough to describe its two-body orbital motion —
    you never need G and M separately.</p>
    <p>For Earth, this repository consistently uses <code>μ = 3.986004418 × 10¹⁴ m³/s²</code> (see
    <code>tests/test_cw.py</code>, <code>tests/test_twobody.py</code>, and <code>examples/*.yaml</code>).</p>

    <h2>2. Orbital radius r₀</h2>
    <p>For a circular reference orbit, r₀ is the distance from the center of the Earth to the spacecraft —
    altitude plus Earth's radius. The repository's canonical example uses a 350&nbsp;km altitude circular orbit:
    r₀ = 6378&nbsp;km (Earth radius) + 350&nbsp;km = 6728&nbsp;km = 6.728×10⁶ m.</p>

    <h2>3. Mean motion n</h2>
    <p>Mean motion is the angular rate (rad/s) at which a body on a circular orbit of radius r₀ sweeps around
    the central body. It is the single most important derived quantity in this codebase — the entire CW
    state-transition matrix is parameterized by <code>n</code> and the transfer time <code>t</code> only
    through the product <code>n·t</code>.</p>
    <div class="formula">n = √(μ / r₀³)</div>
    <p><strong>Physical intuition:</strong> a bigger orbit (larger r₀) moves more slowly in angle per second
    (smaller n) — this is just Kepler's third law in disguise. A satellite skimming just above the Earth's
    surface has a much higher n than one in GEO.</p>

    <h3>Equation → code → test</h3>
    <div class="chain">
      <div class="node">n = √(μ/r₀³)</div><div class="arr">↓</div>
      <div class="node"><code>mean_motion()</code></div><div class="arr">↓</div>
      <div class="node"><code>src/cw.py</code></div><div class="arr">↓</div>
      <div class="node">used inside every test in <code>tests/test_cw.py</code></div>
    </div>
    ${TC.codeRef('src/cw.py', 'mean_motion')}
    ${TC.authorityBanner('The following is the exact, unmodified text of <code>mean_motion()</code> from <code>src/cw.py</code> — the authoritative implementation.')}
    ${meanMotionSym ? TC.codeBlock(meanMotionSym.code, meanMotionSym.startLine) : '<p>Not found.</p>'}
    <p>${TC.badge('tested', 'IMPLEMENTED / TESTED')} Exercised indirectly in every test in
    <code>tests/test_cw.py</code> (each test calls <code>mean_motion(mu, r0)</code> to get <code>n</code> before
    doing anything else). There is no dedicated <code>test_mean_motion()</code> unit test that checks the formula
    in isolation — it is only tested as a dependency of the targeting tests.</p>

    <h2>4. Orbital period T</h2>
    <p>The time for one full revolution. Directly follows from n:</p>
    <div class="formula">T = 2π / n &nbsp;&nbsp;(equivalently T = 2π√(r₀³/μ) for a circular orbit)</div>
    <p>For the repository's 350&nbsp;km example this works out to roughly <strong>91.5 minutes</strong> — a
    typical LEO period. This number matters a great deal later: the "exact one orbit" targeting case in
    <a href="#/singularity">Why the Singularity Matters</a> uses <code>t_final = 2π/n</code> exactly, i.e. one
    full period, and that is precisely where the CW targeting matrix becomes singular.</p>

    <h3>Equation → code → test</h3>
    <div class="chain">
      <div class="node">T = 2π√(a³/μ)</div><div class="arr">↓</div>
      <div class="node"><code>orbital_period()</code></div><div class="arr">↓</div>
      <div class="node"><code>src/twobody.py</code></div><div class="arr">↓</div>
      <div class="node"><code>tests/test_twobody.py::test_orbital_period_positive</code></div>
    </div>
    ${TC.codeRef('src/twobody.py', 'orbital_period')}
    ${TC.authorityBanner('Exact, unmodified text of <code>orbital_period()</code> from <code>src/twobody.py</code>.')}
    ${orbitalPeriodSym ? TC.codeBlock(orbitalPeriodSym.code, orbitalPeriodSym.startLine) : '<p>Not found.</p>'}
    ${TC.callout('warn', 'What the test actually checks', `<p><code>test_orbital_period_positive</code> only
      asserts <code>orbital_period(mu, a) &gt; 0</code>. This is a <strong>software sanity check</strong> (did the
      function run and return a positive number?), not a <strong>physical correctness check</strong> (it does
      not verify the numeric value against a known period, e.g. 92 minutes for a 6778&nbsp;km orbit). See
      <a href="#/test-classification">Software vs. Physical Tests</a> for why this distinction matters.</p>`)}

    <h2>5. Vis-viva equation (orbital speed at any radius)</h2>
    <p>For an elliptical (or circular) two-body orbit with semi-major axis a, the instantaneous speed at radius
    r is:</p>
    <div class="formula">v² = μ (2/r − 1/a)</div>
    <p>This is implemented but currently has <strong>no dedicated test</strong> in the repository.</p>
    ${TC.codeRef('src/twobody.py', 'vis_viva_speed')}
    ${TC.authorityBanner('Exact, unmodified text of <code>vis_viva_speed()</code> from <code>src/twobody.py</code>.')}
    ${visVivaSym ? TC.codeBlock(visVivaSym.code, visVivaSym.startLine) : '<p>Not found.</p>'}
    <p>${TC.badge('planned', 'IMPLEMENTED — NOT TESTED')} No test in <code>tests/</code> calls
    <code>vis_viva_speed()</code>.</p>

    <h2>Interactive: compute n and T</h2>
    ${TC.mirrorBanner(['cw.py :: mean_motion', 'twobody.py :: orbital_period'])}
    <div class="panel">
      <div class="control-row">
        <label for="pb-mu">μ (gravitational parameter, m³/s²)</label>
        <input type="number" id="pb-mu" value="398600441800000" step="1e9" />
      </div>
      <div class="control-row">
        <label for="pb-alt">Altitude above Earth surface (km)</label>
        <input type="range" id="pb-alt" min="150" max="40000" step="10" value="350" />
        <span class="value-tag" id="pb-alt-val">350 km</span>
      </div>
      <div class="result-grid" id="pb-results"></div>
      <p>${TC.mirrorTag('cw.py :: mean_motion() / twobody.py :: orbital_period()')}</p>
    </div>

    <footer class="site-footer">The authoritative implementations are <code>mean_motion()</code> in
    <code>src/cw.py</code> and <code>orbital_period()</code> in <code>src/twobody.py</code>. The sliders above
    call a hand-ported JavaScript copy of those two functions (<code>site/js/physics.js</code>) purely so this
    page can be interactive without a Python backend — see the mirror banner above.</footer>
  `;

  const EARTH_R = 6378e3;
  const muInput = root.querySelector('#pb-mu');
  const altInput = root.querySelector('#pb-alt');
  const altVal = root.querySelector('#pb-alt-val');
  const resultsEl = root.querySelector('#pb-results');

  function recompute() {
    const mu = parseFloat(muInput.value);
    const altKm = parseFloat(altInput.value);
    altVal.textContent = altKm.toFixed(0) + ' km';
    const r0 = EARTH_R + altKm * 1000;
    const n = TCPhysics.meanMotion(mu, r0);
    const T = TCPhysics.orbitalPeriod(mu, r0);
    resultsEl.innerHTML = `
      <div class="result-cell"><div class="label">r₀</div><div class="value">${TC.fmt(r0, 0)} m</div></div>
      <div class="result-cell"><div class="label">n (mean motion)</div><div class="value">${TC.fmt(n, 6)} rad/s</div></div>
      <div class="result-cell"><div class="label">T (period)</div><div class="value">${TC.fmt(T, 1)} s</div></div>
      <div class="result-cell"><div class="label">T (minutes)</div><div class="value">${(T / 60).toFixed(2)} min</div></div>
    `;
  }

  muInput.addEventListener('input', recompute);
  altInput.addEventListener('input', recompute);
  recompute();
};
