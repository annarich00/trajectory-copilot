'use strict';

window.TCPages['trace-problem'] = async function (root) {
  const mu = 3.986004418e14;
  const earthR = 6378e3;
  const altKm = 350;
  const r0 = earthR + altKm * 1000;
  const n = TCPhysics.meanMotion(mu, r0);
  const T = 2 * Math.PI / n;
  const tFinal = T; // "one orbital period" per the fully-specified eval case
  const tQuarter = 0.25 * T;
  const state0 = [15.0, -200.0, 0.0, -0.14, 0.0, 0.0];

  // Use the quarter-orbit (well-conditioned) case for the actual numeric
  // targeting trace, since the exact-one-orbit case is singular (see
  // Why the Singularity Matters) — note this explicitly.
  const targeting = TCPhysics.twoBurnTargeting(state0, n, tQuarter);
  const verify = TCPhysics.validateAgainstTwoBody(state0, n, tQuarter, mu, 50.0, 0.05, 3000);
  const validity = TCPhysics.validateCwUse(r0, state0.slice(0, 3), tQuarter, n);

  root.innerHTML = `
    ${TC.pageHeader('Trace a Problem — the 350 km Rendezvous Case', 'One complete worked example, end to end, grounded in the repository\'s own benchmark scenario.')}

    <div class="callout">
      <div class="callout-title">Natural-language starting point</div>
      <p><em>"The chaser is 15 m radially outward and 200 m behind the target along-track. Its relative
      velocity is 0.14 m/s radially inward. The target is in a circular orbit at 350 km altitude around Earth.
      Find a two-burn rendezvous."</em></p>
      <p class="toc-inline">This is the scenario from <code>evaluations/formalizer/test_02_cw_complete.txt</code>
      and <code>tests/test_cw.py::test_cw_rendezvous_benchmark</code> / <code>examples/rendezvous_case_01.yaml</code>.</p>
    </div>

    <h2>1. Problem specification (LLM: Problem Formalizer)</h2>
    <p>Per <code>evaluations/formalizer/test_02_cw_complete.txt</code>, the formalizer extracts: circular orbit
    at 350 km, Earth μ, LVLH frame (x radial out, y along-track, z cross-track), initial relative state,
    terminal condition = full rendezvous, timing = one orbital period, two-burn constraint, model = CW. It
    classifies this as <code>READY TO SOLVE</code> with <code>NO VALIDITY CONCERNS</code>. ${TC.badge('llm', 'LLM reasoning')}</p>

    <h2>2. State representation (LLM → deterministic handoff)</h2>
    <p>The natural-language description is converted into the exact 6-vector <code>src/cw.py</code> expects:</p>
    <div class="formula">state0 = [x₀, y₀, z₀, ẋ₀, ẏ₀, ż₀] = [${state0.join(', ')}]</div>
    <p>x₀=+15 ("radially outward"), y₀=−200 ("behind" = negative along-track, per the LVLH convention in
    <code>reference/SOURCE.md</code>), ẋ₀=−0.14 ("radially inward" = negative x velocity).</p>

    <h2>3. Mean motion (deterministic: mean_motion())</h2>
    ${TC.mirrorTag('cw.py :: mean_motion')}
    <div class="result-grid">
      <div class="result-cell"><div class="label">r₀</div><div class="value">${TC.fmt(r0,0)} m</div></div>
      <div class="result-cell"><div class="label">n</div><div class="value">${TC.fmt(n,6)} rad/s</div></div>
      <div class="result-cell"><div class="label">T</div><div class="value">${TC.fmt(T,1)} s (${(T/60).toFixed(1)} min)</div></div>
    </div>
    <p><strong>What the computer does:</strong> <code>n = sqrt(mu / r0**3)</code>. <strong>What it means
    physically:</strong> at 350 km altitude, the target circles the Earth roughly every 91.5 minutes.</p>

    <h2>4. CW validity check (deterministic: validate_cw_use())</h2>
    ${TC.mirrorTag('cw.py :: validate_cw_use')}
    <div class="panel">
      <p><strong>valid:</strong> <span style="color:${validity.valid ? 'var(--good)' : 'var(--bad)'}">${validity.valid}</span></p>
      <p><strong>warnings:</strong> ${validity.warnings.length ? validity.warnings.map(TC.esc).join('; ') : '(none)'}</p>
    </div>
    <p>Separation (${TC.fmt(TCPhysics.vNorm(state0.slice(0,3)),2)} m) is ≈0.003% of r₀ — well under the 1%
    heuristic threshold. CW is appropriate here. Contrast with <a href="#/model-validity">Model Validity</a>'s
    GEO failure case.</p>

    <h2>5. Transfer time decision</h2>
    <p>The natural-language spec says "after one orbital period" — i.e. <code>t_final = T = 2π/n ≈
    ${TC.fmt(T,1)} s</code>. <strong>Important real finding from this repository:</strong> that exact value is
    precisely the CW targeting singularity (see <a href="#/singularity">Why the Singularity Matters</a>) — at
    <code>n·t = 2π</code>, <code>sin(n·t) ≈ 0</code> and Φrv is ill-conditioned.
    <code>tests/test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected</code> confirms the real
    <code>two_burn_targeting()</code> raises <code>CWSingularTransferError</code> for this exact transfer
    time. For the rest of this trace (steps 6–11) we use the repository's actual well-conditioned benchmark
    transfer time instead — a <strong>quarter orbital period</strong>, t_final = T/4 ≈ ${TC.fmt(tQuarter,1)} s
    — exactly as <code>tests/test_cw.py::test_cw_rendezvous_benchmark</code> does, and note this substitution
    explicitly rather than silently using the singular value.</p>

    <h2>6. State-transition matrix (deterministic: cw_stm())</h2>
    ${TC.mirrorTag('cw.py :: cw_stm')}
    <p>See the full <a href="#/cw-stm">CW STM Explorer</a> for the block-by-block breakdown. At t_final=T/4,
    n·t = π/2, far from any singularity (sin(π/2)=1, well-conditioned).</p>

    <h2>7–9. Targeting: Δv0, Δv1 (deterministic: two_burn_targeting())</h2>
    ${TC.mirrorTag('cw.py :: two_burn_targeting')}
    <div class="result-grid">
      <div class="result-cell"><div class="label">Δv0</div><div class="value">${TC.vecStr(targeting.dv0,4)}</div></div>
      <div class="result-cell"><div class="label">|Δv0|</div><div class="value">${TC.fmt(TCPhysics.vNorm(targeting.dv0),4)} m/s</div></div>
      <div class="result-cell"><div class="label">Δv1</div><div class="value">${TC.vecStr(targeting.dv1,4)}</div></div>
      <div class="result-cell"><div class="label">|Δv1|</div><div class="value">${TC.fmt(TCPhysics.vNorm(targeting.dv1),4)} m/s</div></div>
    </div>
    <p>See the full derivation in <a href="#/targeting">Two-Burn Targeting, Step by Step</a>.</p>

    <h2>10. Final state</h2>
    <div class="result-grid">
      <div class="result-cell"><div class="label">r(t_final)</div><div class="value">${TC.vecStr(targeting.finalState.slice(0,3),6)} m</div></div>
      <div class="result-cell"><div class="label">v(t_final)</div><div class="value">${TC.vecStr(targeting.finalState.slice(3,6),6)} m/s</div></div>
    </div>
    <p>Both ≈0, confirming full rendezvous (position and velocity match) by construction of Δv0/Δv1.</p>

    <h2>11. Two-body verification (deterministic: validate_against_two_body())</h2>
    ${TC.mirrorTag('verify.py :: validate_against_two_body')}
    <div class="result-grid">
      <div class="result-cell flag-${verify.posErrM > 50 ? 'bad' : 'good'}"><div class="label">Position difference</div><div class="value">${TC.fmt(verify.posErrM,5)} m</div></div>
      <div class="result-cell flag-${verify.velErrMps > 0.05 ? 'bad' : 'good'}"><div class="label">Velocity difference</div><div class="value">${TC.fmt(verify.velErrMps,7)} m/s</div></div>
      <div class="result-cell"><div class="label">Warnings</div><div class="value">${verify.warnings.length ? verify.warnings.join(', ') : 'none'}</div></div>
    </div>
    <p>Sub-centimeter position disagreement between CW and independent nonlinear two-body propagation,
    confirming CW's linearization is an excellent approximation for this small-separation, moderate-duration
    case. ${TC.badge('ver', 'Independent verification')}</p>

    <h2>12. Test coverage for this exact scenario</h2>
    <table>
      <tr><th>Step</th><th>Covered by</th></tr>
      <tr><td>mean_motion() for this r0</td><td class="mono">Used (not isolated) by all tests/test_cw.py tests</td></tr>
      <tr><td>validate_cw_use() for this state</td><td class="mono">tests/test_cw.py::test_cw_validation_basic (same numbers)</td></tr>
      <tr><td>two_burn_targeting() at T/4</td><td class="mono">tests/test_cw.py::test_cw_rendezvous_benchmark (identical scenario)</td></tr>
      <tr><td>two_burn_targeting() at exactly T (singular)</td><td class="mono">tests/test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected</td></tr>
      <tr><td>validate_against_two_body() for this state</td><td class="mono" style="color:var(--bad)">NO TEST — PARTIAL, see Verification Lesson</td></tr>
    </table>

    <p class="toc-inline">All numeric values on this page are a pedagogical browser mirror of the Python
    functions named next to each result — see the badges above. The authoritative numbers come from running
    <code>pytest tests/test_cw.py -v</code> for the targeting steps.</p>
  `;
};
