'use strict';

window.TCPages['model-validity'] = async function (root) {
  const sourceMd = await TC.fetchText('data/reference/SOURCE.md');
  const geoYaml = await TC.fetchText('data/examples/geo_failure_case.yaml');
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const validateSym = TC.extractPySymbol(cwSrc, 'validate_cw_use');

  root.innerHTML = `
    ${TC.pageHeader('Model Validity', 'CW is a linearized local approximation. It is not universally applicable. This page explains why, grounded in reference/SOURCE.md and the repository\'s own GEO failure example.')}

    <h2>The assumption chain</h2>
    <div class="chain">
      <div class="node">small relative motion</div><div class="arr">↓</div>
      <div class="node">circular chief orbit</div><div class="arr">↓</div>
      <div class="node">local linearized dynamics</div><div class="arr">↓</div>
      <div class="node">appropriate time/geometry</div><div class="arr">↓</div>
      <div class="node">⇒ CW is valid</div>
    </div>
    <p>Per <code>reference/SOURCE.md</code> ("Validity limits"), CW degrades when:</p>
    <ul>
      <li>separation is large compared with the orbit radius,</li>
      <li>the transfer is long enough for linearization error to accumulate,</li>
      <li>the reference orbit is not circular,</li>
      <li>the geometry is global-scale rather than local-relative.</li>
    </ul>

    <h2>Missing information vs. model-validity concern — a central distinction</h2>
    ${TC.callout('warn', 'These are two different kinds of problems', `
      <p><strong>Missing information:</strong> the problem is well-posed in principle, but a required number or
      choice (e.g. transfer time, gravitational parameter, coordinate convention) was never provided. The fix
      is to ask for the missing value. This does not mean the chosen model is wrong — just incomplete.</p>
      <p><strong>Model-validity concern:</strong> even with all information supplied, the chosen dynamics model
      is the wrong tool for the physical regime described (e.g. CW requested for a GEO-scale separation). The
      fix is not "get more numbers" — it is "use a different model entirely." Supplying more decimal places of
      a GEO separation does not make CW valid.</p>
      <p>The <code>orbital-problem-formalizer</code> skill is explicitly designed to distinguish these two —
      see its <code>Missing Information</code> vs. <code>Model Validity Concerns</code> output sections in
      <code>.pi/skills/orbital-problem-formalizer/SKILL.md</code>.</p>
    `)}

    <h2>Live demonstration: the GEO failure case</h2>
    <p>The repository ships a concrete example of a scenario where CW should be rejected on validity grounds:</p>
    <pre class="code">${TC.esc(geoYaml)}</pre>
    <div class="code-ref">Source: <code>examples/geo_failure_case.yaml</code></div>

    <h3>Why this breaks the small-separation assumption</h3>
    <div class="panel" id="geo-calc"></div>

    <h3>What validate_cw_use() says about it</h3>
    ${TC.codeRef('src/cw.py', 'validate_cw_use')}
    ${TC.authorityBanner('Exact, unmodified text from src/cw.py.')}
    ${validateSym ? TC.codeBlock(validateSym.code, validateSym.startLine) : ''}
    ${TC.mirrorBanner('cw.py :: validate_cw_use')}
    <div class="panel" id="geo-validate"></div>

    ${TC.callout('bad', 'What this means physically', `<p>If the chaser is roughly one-third of the way around
      the GEO belt (~14,000 km of along-track separation on a ~42,164 km-radius orbit), that is not "a nearby
      spacecraft a few hundred meters away" — it's a different point on the same orbit, over 30% of the orbital
      radius away. The whole premise of CW — that gravity can be linearized about a single nearby reference
      point — breaks down. This is confirmed quantitatively on the <a href="#/experiment">CW vs Two-Body
      Experiment</a> page: loading the "GEO failure case" preset there shows the independent two-body
      propagation diverging from CW's prediction by millions of meters over a quarter orbit.</p>`)}

    <h2>What breaks, mechanically</h2>
    <table>
      <tr><th>Assumption</th><th>What breaks when violated</th></tr>
      <tr><td>Small separation vs. orbit radius</td><td>The Taylor expansion of gravity used to derive the CW
        equations assumes the deputy is close enough to the chief that higher-order (quadratic and above) terms
        in relative position are negligible. At GEO-belt-fraction separations, those higher-order terms are
        not small — they dominate.</td></tr>
      <tr><td>Circular chief orbit</td><td>The CW equations use a constant mean motion <code>n</code>. An
        eccentric chief orbit has a time-varying angular rate, which the fixed-<code>n</code> STM (<code>cw_stm()</code>)
        cannot represent at all — <code>src/cw.py</code> has no eccentricity parameter anywhere.</td></tr>
      <tr><td>Short/moderate transfer time</td><td>Linearization error compounds with every orbit; a
        multi-revolution transfer can accumulate meaningful nonlinear drift even for a modest initial
        separation. This is noted in <code>reference/SOURCE.md</code>'s "Multi-revolution limitations" section.</td></tr>
    </table>

    <h2>Current validity-checking in code vs. in skills</h2>
    <p>${TC.badge('partial', 'PARTIAL')} <code>validate_cw_use()</code> in <code>src/cw.py</code> only checks
    two numeric heuristics: separation/radius ratio &gt; 1% and transfer time &gt; ~2 orbital periods. It does
    <strong>not</strong> check for GEO-scale geometry, non-circular reference orbits, or multi-revolution
    phasing explicitly — those richer checks exist only as guidance text in
    <code>.pi/skills/orbital-model-selector/SKILL.md</code>, to be applied by an LLM reasoning over the
    formalized problem, not enforced deterministically in code today.</p>

    <p><a href="#/failure-museum">Continue: Failure Museum →</a></p>
  `;

  const mu = 3.986004418e14;
  const r0Geo = 42164000.0;
  const relPos = [0.0, 14000000.0, 0.0];
  const relNorm = TCPhysics.vNorm(relPos);
  const nGeo = TCPhysics.meanMotion(mu, r0Geo);
  const TGeo = 2 * Math.PI / nGeo;

  root.querySelector('#geo-calc').innerHTML = `
    <table>
      <tr><td>Reference orbit radius r₀ (GEO)</td><td class="mono">${TC.fmt(r0Geo,0)} m</td></tr>
      <tr><td>Relative separation |r_rel|</td><td class="mono">${TC.fmt(relNorm,0)} m</td></tr>
      <tr><td>Separation / r₀ ratio</td><td class="mono" style="color:var(--bad)">${(relNorm/r0Geo*100).toFixed(1)}%</td></tr>
      <tr><td>validate_cw_use() threshold</td><td class="mono">1% (ratio &gt; 0.01 triggers a warning)</td></tr>
      <tr><td>n (GEO)</td><td class="mono">${TC.fmt(nGeo,8)} rad/s</td></tr>
      <tr><td>T (GEO)</td><td class="mono">${TC.fmt(TGeo,1)} s ≈ ${(TGeo/3600).toFixed(2)} hr</td></tr>
    </table>
  `;

  const validity = TCPhysics.validateCwUse(r0Geo, relPos, 0.25 * TGeo, nGeo);
  root.querySelector('#geo-validate').innerHTML = `
    <p><strong>valid:</strong> <span style="color:${validity.valid ? 'var(--good)' : 'var(--bad)'}">${validity.valid}</span></p>
    <p><strong>warnings:</strong></p>
    <ul>${validity.warnings.map((w) => `<li>${TC.esc(w)}</li>`).join('') || '<li>(none)</li>'}</ul>
  `;
};
