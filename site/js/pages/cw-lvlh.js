'use strict';

window.TCPages['cw-lvlh'] = async function (root) {
  const sourceMd = await TC.fetchText('data/reference/SOURCE.md');

  root.innerHTML = `
    ${TC.pageHeader('CW / LVLH Lesson', 'Clohessy-Wiltshire (Hill\'s equations) describe how one spacecraft moves relative to another, in a rotating frame centered on a reference ("chief") spacecraft.')}
    ${TC.teachingContract({
      assumptions: 'Circular chief orbit, small relative separation, impulsive maneuvers, and the repository’s stated radial/along-track/cross-track LVLH convention.',
      symbols: '<code>x,y,z</code>: relative LVLH position; overdots: time derivatives; <code>n</code>: chief mean motion.',
      mapping: '<code>reference/SOURCE.md §B</code> → <code>src/cw.py::cw_stm</code> and <code>src/verify.py</code> frame helpers.',
      evidence: '<code>tests/test_validation.py</code> verifies basis handedness, transport, and both transform round trips at ≤2e−9 m / ≤2e−12 m/s; this browser lesson is pedagogical, not authoritative.',
      limitations: 'The transformation helpers require finite, nonzero chief position and non-collinear chief position/velocity. They use supplied circular-chief angular rate <code>n</code>; they do not validate circularity, perturbations, or CW applicability.'
    })}

    <h2>The two spacecraft</h2>
    <div class="grid-2">
      <div class="panel">
        <div class="panel-title">Chief (reference)</div>
        <p>The spacecraft whose circular orbit defines the rotating LVLH frame. In <code>src/verify.py</code>
        this is literally called <code>chief_pos</code> / <code>chief_vel</code>. CW assumes the chief orbit is
        circular (or very nearly so).</p>
      </div>
      <div class="panel">
        <div class="panel-title">Deputy / chaser</div>
        <p>The spacecraft whose motion <em>relative to the chief</em> we solve for. In <code>src/verify.py</code>
        this is <code>deputy_pos</code> / <code>deputy_vel</code>. The CW state vector describes exactly this
        relative motion.</p>
      </div>
    </div>

    <h2>The LVLH frame used by this repository</h2>
    <p>Per <code>reference/SOURCE.md</code>, the convention used throughout <code>src/cw.py</code> and
    <code>src/verify.py</code> is:</p>
    <table>
      <tr><th>Axis</th><th>Name</th><th>Direction</th></tr>
      <tr><td><code>x</code></td><td>Radial</td><td>Outward from the central body, through the chief spacecraft.</td></tr>
      <tr><td><code>y</code></td><td>Along-track</td><td>In the direction of chief's orbital motion.</td></tr>
      <tr><td><code>z</code></td><td>Cross-track</td><td>Completes a right-handed triad (orbit-normal direction).</td></tr>
    </table>
    ${TC.callout('warn', 'Why this must be stated explicitly', `<p><code>reference/SOURCE.md</code> itself warns:
      "Coordinate definitions must be stated explicitly because LVLH/RTN/RIC naming varies across sources."
      The <code>orbital-problem-formalizer</code> skill is specifically instructed: <em>"Do not silently choose a
      coordinate convention."</em> A frame mix-up (e.g. assuming "behind" means −y when the source meant +x) is
      a real failure mode — see <a href="#/failure-museum">Failure Museum, Failure 4</a>.</p>`)}

    <h2>Inertial ↔ LVLH state transformation</h2>
    <p><code>src/verify.py</code> constructs the inertial-column rotation <code>R = [r̂ t̂ ĥ]</code> as
    <code>r̂ = r<sub>c</sub>/|r<sub>c</sub>|</code>, <code>ĥ = (r<sub>c</sub> × v<sub>c</sub>)/|r<sub>c</sub> × v<sub>c</sub>|</code>,
    and <code>t̂ = ĥ × r̂</code>. Thus <code>r̂ × t̂ = ĥ</code>: it is orthonormal and right-handed.
    All positions are metres, velocities are m/s, and <code>n</code> is rad/s.</p>
    <div class="panel">
      <div class="formula">r<sub>d</sub> = r<sub>c</sub> + Rρ<br>v<sub>d</sub> = v<sub>c</sub> + Rρ̇ + ω × (Rρ), &nbsp; ω = n ĥ</div>
      <p><strong>LVLH → inertial.</strong> The relative state is deputy minus chief. The final cross-product is the
      rotating-frame transport term; a local derivative <code>ρ̇</code> is not by itself the inertial relative velocity.</p>
    </div>
    <div class="panel">
      <div class="formula">ρ = Rᵀ(r<sub>d</sub> − r<sub>c</sub>)<br>ρ̇ = Rᵀ[(v<sub>d</sub> − v<sub>c</sub>) − ω × (r<sub>d</sub> − r<sub>c</sub>)]</div>
      <p><strong>Inertial → LVLH.</strong> The inverse subtracts the same transport term before rotating. This is the
      sign-sensitive counterpart of the forward equation.</p>
    </div>
    <p>TJC-1.6 added focused numerical evidence in <code>tests/test_validation.py</code>: a representative basis
    has <code>RᵀR = I</code> and determinant +1; LVLH→inertial→LVLH recovers a state within 2e−12 in the tested
    units; inertial→LVLH→inertial recovers deputy position within 2e−9 m and velocity within 2e−12 m/s. A nonzero
    case confirms <code>ω × ρ</code> changes the inertial along-track velocity by +0.1 m/s. Zero-position and
    radial/zero-angular-momentum chiefs raise explicit errors rather than producing NaNs.</p>
    <p>See the authoritative source mirror <code>data/src/verify.py</code> and test mirror
    <code>data/tests/test_validation.py</code>; those mirrors are browser copies, not the source of truth.</p>

    <h2>The three Hill/CW equations of motion</h2>
    <p>With the LVLH convention above, linearizing Newtonian gravity about the circular chief orbit yields three
    coupled, linear, time-invariant differential equations (reference/SOURCE.md, Section B):</p>

    <div class="panel">
      <div class="formula">ẍ − 2n ẏ − 3n² x = 0</div>
      <p><strong>Radial equation.</strong> <code>−3n²x</code> is the net differential-gravity + centrifugal term:
      being farther out radially (+x) means weaker gravity pulling you back, but you're also moving slower than
      a circular orbit at your new radius would require, which produces an inward-pulling net restoring
      acceleration proportional to x. <code>−2nẏ</code> is the Coriolis term coupling radial motion to
      along-track velocity — radial drift bends into along-track motion because the frame itself is rotating at
      rate n.</p>
    </div>
    <div class="panel">
      <div class="formula">ÿ + 2n ẋ = 0</div>
      <p><strong>Along-track equation.</strong> No restoring term in y alone — along-track position doesn't
      directly pull you back. The <code>+2nẋ</code> Coriolis term means radial velocity directly drives
      along-track acceleration. This is why a radial burn produces along-track drift (an unintuitive but very
      real CW effect — "radial burns cause along-track motion over time").</p>
    </div>
    <div class="panel">
      <div class="formula">z̈ + n² z = 0</div>
      <p><strong>Cross-track equation.</strong> This one is <em>decoupled</em> from x and y entirely — it is
      simple harmonic motion at the orbital frequency n. Physically: cross-track motion is just a slightly
      inclined/offset orbital plane relative to the chief, which oscillates once per orbit. This decoupling is
      exactly why every 3×3 block in the CW STM (see <a href="#/cw-stm">CW STM Explorer</a>) is block-diagonal
      in its (·, z) row/column — in-plane (x,y) and out-of-plane (z) motion never mix under linear CW dynamics.</p>
    </div>

    <h3>Why Coriolis terms appear</h3>
    <p>The LVLH frame rotates with the chief at rate n. Newton's laws are only simple (F = ma) in an inertial
    frame. Writing the same physics in a frame that rotates introduces two extra fictitious-force terms:
    centrifugal (∝ position) and Coriolis (∝ velocity, coupling the two in-plane axes). The <code>−2nẏ</code>
    and <code>+2nẋ</code> terms are exactly this Coriolis coupling; the <code>−3n²x</code> coefficient folds
    together the centrifugal term with the linearized difference in gravitational acceleration between the
    chief's circular orbit and the deputy's slightly different radius.</p>

    <h3>Why the equations are linearized — and when that's valid</h3>
    <p>The true relative-motion equations are nonlinear (gravity depends on 1/r² of the deputy's actual,
    not approximate, position). CW/Hill's equations are obtained by Taylor-expanding gravity about the chief's
    position and keeping only first-order terms in the (small) relative position. This is only accurate when:</p>
    <ul>
      <li>the chief orbit is circular (or very nearly so),</li>
      <li>the relative separation is small compared with the orbital radius,</li>
      <li>the time horizon is short enough that the first-order approximation doesn't accumulate large error.</li>
    </ul>
    <p>These are exactly the conditions checked (partially) by <code>validate_cw_use()</code> in
    <code>src/cw.py</code> and discussed fully in <a href="#/model-validity">Model Validity</a>.</p>

    <h2>Equations → state-transition matrix</h2>
    <p>Because the three CW equations are linear and time-invariant, their solution can be written in closed
    form as a state-transition matrix (STM) Φ(t), which maps an initial relative state directly to the state at
    any later time without numerically integrating anything. This is what <code>cw_stm()</code> in
    <code>src/cw.py</code> implements, and it is the subject of the next lesson.</p>
    <p><a href="#/cw-stm" class="btn" style="display:inline-block;text-decoration:none;">Continue to the CW State-Transition Matrix →</a></p>

    <h2>Raw reference text (reference/SOURCE.md, Section B)</h2>
    <details>
      <summary style="cursor:pointer;color:var(--accent)">Show reference/SOURCE.md Clohessy-Wiltshire section (verbatim excerpt)</summary>
      <pre class="code">${TC.esc(sourceMd.split('## B. Clohessy-Wiltshire Dynamics')[1]?.split('## C.')[0] || '(section not found)')}</pre>
    </details>
  `;
};
