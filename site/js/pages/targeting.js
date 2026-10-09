'use strict';

window.TCPages['targeting'] = async function (root) {
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const sym = TC.extractPySymbol(cwSrc, 'two_burn_targeting');

  root.innerHTML = `
    ${TC.pageHeader('Two-Burn Targeting, Step by Step', 'A full walkthrough of two_burn_targeting() in src/cw.py — the function that actually solves a rendezvous problem.')}
    ${TC.teachingContract({
      assumptions: 'Impulsive fixed-duration two-burn CW transfer; singular cases are tested for column-space reachability, not silently retimed.',
      symbols: '<code>r0,v0</code>: initial state; <code>rf,vf</code>: requested terminal state; <code>Δv0,Δv1</code>: impulsive burns.',
      mapping: '<code>reference/SOURCE.md §C</code> → <code>src/cw.py::two_burn_targeting</code> and <code>check_phi_rv_conditioning</code>.',
      evidence: '<code>tests/test_cw.py::test_cw_rendezvous_benchmark</code>, GEO P=1/2/3, and integer-period infeasibility tests.',
      limitations: 'The SVD policy is fixed-duration linear CW targeting only; it does not validate long/multi-revolution geometry or optimize transfer time.'
    })}

    <p>Goal: given an initial relative state, find the first burn Δv0 that puts the deputy on a trajectory
    arriving exactly at a target final state at time <code>t_final</code>, then find the second burn Δv1 that
    kills any residual relative velocity so the deputy stops there instead of flying past.</p>

    ${TC.codeRef('src/cw.py', 'two_burn_targeting')}
    ${TC.authorityBanner('Exact, unmodified text of <code>two_burn_targeting()</code> from <code>src/cw.py</code> — this is the authoritative implementation being explained step by step below.')}
    ${sym ? TC.codeBlock(sym.code, sym.startLine) : ''}

    <h2>Step-by-step derivation</h2>

    <div class="panel">
      <h3 style="margin-top:0">Step 1 — Initial state</h3>
      <p><strong>What the computer does:</strong> reads <code>state0 = [r0, v0]</code>, a 6-vector, and
      <code>target_final_state</code> (defaults to the origin with zero velocity — i.e. full rendezvous).</p>
      <p><strong>What it means physically:</strong> "Where is the chaser right now, relative to the target, and
      how fast is it moving relative to the target? Where do we want it to end up?"</p>
    </div>

    <div class="panel">
      <h3 style="margin-top:0">Step 2 — Build Φ(t_final) and partition it</h3>
      <div class="formula">phi = cw_stm(n, t_final)<br/>phi_rr, phi_rv = phi[:3,:3], phi[:3,3:]<br/>phi_vr, phi_vv = phi[3:,:3], phi[3:,3:]</div>
      <p><strong>What the computer does:</strong> calls <code>cw_stm()</code> once for the whole transfer
      duration, then slices the 6×6 result into the four 3×3 blocks explained in
      <a href="#/cw-stm">CW STM Explorer</a>.</p>
      <p><strong>What it means physically:</strong> "If I do nothing (no burns), how would my current position
      and velocity map forward in time to a final position and velocity?" Each block answers one piece of that
      question.</p>
    </div>

    <div class="panel">
      <h3 style="margin-top:0">Step 3 — Solve for Δv0 using Φrv</h3>
      <div class="formula">b = rf_des − Φrr·r0<br/>Φrv·v0⁺ = b; Δv0 = v0⁺ − v0</div>
      <p><strong>What the computer does:</strong> rearranges <code>r(t) = Φrr·r0 + Φrv·v0⁺ = rf_des</code>.
      A well-conditioned full-rank Φrv uses the unique inverse solve. A singular or ill-conditioned Φrv is
      evaluated with SVD: the code tests whether <code>b</code> lies in the Φrv column space using its documented
      rank/residual tolerances. A reachable rank-deficient case returns the pseudoinverse minimum-norm
      <code>v0⁺</code>, explicitly non-unique; an unreachable case returns metadata and no maneuver. It never
      changes the requested transfer time (see <a href="#/singularity">Why the Singularity Matters</a>).</p>
      <p><strong>What it means physically:</strong> "Given where I'll end up if I coast with my current
      velocity, what one-time velocity change right now would instead put me exactly where I want to be at
      t_final?" This is a two-point boundary value problem solved in closed form thanks to CW linearity.</p>
    </div>

    <div class="panel">
      <h3 style="margin-top:0">Step 4 — Propagate the post-burn state forward</h3>
      <div class="formula">v0_plus = v0 + Δv0<br/>vf_minus = Φvr·r0 + Φvv·v0_plus</div>
      <p><strong>What the computer does:</strong> computes the velocity the deputy will have <em>just before</em>
      the second burn, using the velocity-output blocks Φvr/Φvv with the post-first-burn velocity.</p>
      <p><strong>What it means physically:</strong> "Having made that first burn, and having coasted all the way
      to t_final, how fast am I actually moving when I arrive?" (Position is guaranteed correct by construction
      of Δv0 — but velocity on arrival is whatever the dynamics produce, which is generally not what we want.)</p>
    </div>

    <div class="panel">
      <h3 style="margin-top:0">Step 5 — Compute Δv1 (the terminal burn)</h3>
      <div class="formula">Δv1 = vf_des − vf_minus</div>
      <p><strong>What the computer does:</strong> the difference between the desired final velocity and the
      velocity the deputy actually arrives with.</p>
      <p><strong>What it means physically:</strong> "Null out my arrival velocity (or match whatever final
      relative velocity was requested) so I don't drift away again." This is the classic two-impulse
      rendezvous: burn once to aim, coast, burn again to stop.</p>
    </div>

    <div class="panel">
      <h3 style="margin-top:0">Step 6 — Final state</h3>
      <div class="formula">rf = Φrr·r0 + Φrv·v0_plus<br/>vf = vf_minus + Δv1<br/>return Δv0, Δv1, [rf, vf]</div>
      <p><strong>What the computer does:</strong> recomputes <code>rf</code> (will equal <code>rf_des</code> by
      construction) and adds Δv1 to get the true final velocity (will equal <code>vf_des</code> by
      construction), then returns all three results.</p>
      <p><strong>What it means physically:</strong> this is the full prediction of the maneuver: how much fuel
      (via Δv) is spent at each burn, and confirmation that the resulting trajectory actually satisfies the
      terminal constraint.</p>
    </div>

    <h2>Live walkthrough with the repository's own benchmark case</h2>
    <p>Below is the exact scenario from <code>tests/test_cw.py::test_cw_rendezvous_benchmark</code>: a chaser
    starting 15 m radially outward, 200 m behind along-track, closing at 0.14 m/s radially inward, targeting
    full rendezvous after a quarter-orbit transfer at 350 km altitude.</p>
    ${TC.mirrorBanner('cw.py :: two_burn_targeting')}
    <div class="panel" id="walkthrough-panel"></div>
  `;

  const mu = 3.986004418e14;
  const r0 = 6378e3 + 350e3;
  const n = TCPhysics.meanMotion(mu, r0);
  const T = 2 * Math.PI / n;
  const tFinal = 0.25 * T;
  const state0 = [15.0, -200.0, 0.0, -0.14, 0.0, 0.0];
  const res = TCPhysics.twoBurnTargeting(state0, n, tFinal);
  const st = res.steps;

  root.querySelector('#walkthrough-panel').innerHTML = `
    <table>
      <tr><th>Quantity</th><th>Value</th><th>Meaning</th></tr>
      <tr><td>n</td><td class="mono">${TC.fmt(n,6)} rad/s</td><td>Mean motion at 350 km altitude</td></tr>
      <tr><td>t_final = T/4</td><td class="mono">${TC.fmt(tFinal,2)} s</td><td>Quarter-orbit transfer, well away from any CW singularity</td></tr>
      <tr><td>r0, v0</td><td class="mono">${TC.vecStr(st.r0)} m, ${TC.vecStr(st.v0)} m/s</td><td>Initial relative state</td></tr>
      <tr><td>Φrr·r0</td><td class="mono">${TC.vecStr(st.phiRrR0)}</td><td>Where coasting-only dynamics would carry the initial position</td></tr>
      <tr><td>Φrv·v0</td><td class="mono">${TC.vecStr(st.phiRvV0)}</td><td>Position contribution from initial velocity, uncorrected</td></tr>
      <tr><td>rhs = rf_des − Φrr·r0 − Φrv·v0</td><td class="mono">${TC.vecStr(st.rhs)}</td><td>Position shortfall that Δv0 must correct for, through Φrv</td></tr>
      <tr><td><strong>Δv0</strong></td><td class="mono">${TC.vecStr(res.dv0)} m/s, |Δv0|=${TC.fmt(TCPhysics.vNorm(res.dv0),4)} m/s</td><td>First (targeting) burn</td></tr>
      <tr><td>v0⁺ = v0 + Δv0</td><td class="mono">${TC.vecStr(st.v0Plus)} m/s</td><td>Velocity immediately after burn 1</td></tr>
      <tr><td>vf⁻ (pre-burn-2 velocity)</td><td class="mono">${TC.vecStr(st.vfMinus)} m/s</td><td>Velocity on arrival, before correction</td></tr>
      <tr><td><strong>Δv1</strong></td><td class="mono">${TC.vecStr(res.dv1)} m/s, |Δv1|=${TC.fmt(TCPhysics.vNorm(res.dv1),4)} m/s</td><td>Second (circularizing) burn</td></tr>
      <tr><td><strong>Final state</strong></td><td class="mono">${TC.vecStr(res.finalState)}</td><td>Should equal target_final_state = zeros(6) to numerical precision</td></tr>
    </table>
    ${TC.callout('good', 'Same scenario as tests/test_cw.py::test_cw_rendezvous_benchmark', `<p>The pytest
      test asserts <code>norm(dv0) &lt; 1.0</code>, <code>norm(dv1) &lt; 1.0</code>, and
      <code>norm(final_state[:3]) &lt; 1e-6</code>, <code>norm(final_state[3:]) &lt; 1e-6</code> — that is the
      authoritative result, produced by running the actual Python. The numbers displayed above are a
      <strong>pedagogical browser mirror</strong> (hand-ported JS, not the Python) using the same inputs, shown
      only to illustrate the algorithm's steps interactively; they are not a substitute for running
      <code>pytest</code> and should not be read as independently verifying it.</p>`)}
  `;
};
