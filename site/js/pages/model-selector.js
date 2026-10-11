'use strict';

window.TCPages['model-selector'] = async function (root) {
  const [selectorSrc, selectorTest, skill, sourceMd] = await Promise.all([
    TC.fetchText('data/src/model_selector.py'),
    TC.fetchText('data/tests/test_model_selector.py'),
    TC.fetchText('data/skills/model-selector.SKILL.md'),
    TC.fetchText('data/reference/SOURCE.md'),
  ]);

  root.innerHTML = `
    ${TC.pageHeader('Assumption-Based Model Selection', 'How the workflow decides between CW rendezvous and the bounded two-body fallback — a documented multi-factor assessment, not a single numeric threshold.')}

    ${TC.callout('warn', 'What this is not', '<p>This selector does not learn a validity boundary from data, and it never selects a model from one isolated separation ratio or duration number. Per <code>reference/SOURCE.md</code> §D and <code>.pi/skills/orbital-model-selector/SKILL.md</code>, it combines six required assumption items plus an optional CW targeting-conditioning signal.</p>')}

    <details><summary style="cursor:pointer;color:var(--accent)">reference/SOURCE.md §D (assumption-based model selection)</summary>
      ${TC.authorityBanner('Exact, unmodified excerpt rendered from the full reference/SOURCE.md mirror below.')}
      <pre class="code">${TC.esc(sourceMd.slice(sourceMd.indexOf('## D. Assumption-based model selection'), sourceMd.indexOf('## E. Required GMAT verification evidence')))}</pre>
    </details>

    <h2>Required assessment items</h2>
    <table>
      <tr><th>Item</th><th>Question</th></tr>
      <tr><td class="mono">circularity</td><td>Is the chief/reference orbit circular or near-circular?</td></tr>
      <tr><td class="mono">locality</td><td>Is relative separation small relative to reference-orbit radius, not a global phasing arc?</td></tr>
      <tr><td class="mono">duration_regime</td><td>Is the fixed transfer duration compatible with local linearization?</td></tr>
      <tr><td class="mono">frame</td><td>Is the relative state in the explicit right-handed LVLH/RIC convention with <code>[x,y,z,x_dot,y_dot,z_dot]</code> ordering and SI units?</td></tr>
      <tr><td class="mono">other_physics</td><td>Are central-body dominance, negligible perturbations, and small relative velocity appropriate?</td></tr>
      <tr><td class="mono">maneuver_assumptions</td><td>Is impulsive-burn targeting suitable?</td></tr>
    </table>
    <p>An optional seventh signal, <code>targeting_conditioning</code>, is computed from
    <code>src/cw.py::two_burn_targeting</code>'s singular/ill-conditioned <code>Phi_rv</code> reporting when enough
    state is supplied. It only ever <em>qualifies</em> an otherwise-clean CW decision; it never selects or
    rejects a model by itself.</p>

    <h2>Four possible outcomes</h2>
    <div class="grid-2">
      <div class="panel"><div class="panel-title">CW rendezvous</div><p>All six required items are
        <code>supported</code> and nothing is <code>boundary</code>. Hands off to
        <code>src.cw.two_burn_targeting</code>.</p></div>
      <div class="panel"><div class="panel-title">Qualified CW rendezvous</div><p>All required items are known
        and none is <code>violated</code>, but at least one is <code>boundary</code> (including a reachable
        singular <code>Phi_rv</code>). Still CW, but <code>qualified=True</code> with concerns and a
        verification-sensitivity note that must stay visible to the user.</p></div>
      <div class="panel"><div class="panel-title">Bounded two-body fallback</div><p>At least one required item
        is clearly <code>violated</code>, and the case independently satisfies the bounded coast contract
        (finite six-element inertial Cartesian state, positive <code>mu</code>, finite duration, positive RK4
        step count, coast-only). Hands off to <code>src.twobody.propagate_cartesian_state</code>.</p></div>
      <div class="panel"><div class="panel-title">NEEDS MORE INFORMATION</div><p>Any required item is
        <code>unknown</code>. No model is selected, even if some other item is already known to be
        <code>violated</code> — that becomes a surfaced concern, not an early exit.</p></div>
    </div>
    <p>A fifth outcome, <code>UNSUPPORTED</code>, is returned when a required item is violated and the
    bounded two-body coast contract is also not satisfied (e.g. targeting, maneuvers, optimization, thrust, or
    perturbation requests).</p>

    <h2>Output record</h2>
    <p>Every call to <code>select_model()</code> returns a <code>ModelSelectionResult</code> with:</p>
    <ul>
      <li><code>selection</code> — one of the four semester-scoped outcomes above, or <code>UNSUPPORTED</code>;</li>
      <li><code>qualified</code> — <code>True</code> only for a boundary CW decision;</li>
      <li><code>reasons</code> — why this selection was reached;</li>
      <li><code>assumptions</code> — every required item's assessment, plus the optional targeting signal when computed;</li>
      <li><code>concerns</code> — violated/boundary items and verification-sensitivity notes;</li>
      <li><code>deterministic_tool</code> — the exact deterministic function to invoke next, or <code>None</code>; and</li>
      <li><code>missing_items</code> — populated only for <code>NEEDS MORE INFORMATION</code>.</li>
    </ul>

    <h2>Authoritative source</h2>
    ${TC.authorityBanner('Exact, unmodified contents of src/model_selector.py.')}
    ${TC.codeBlock(selectorSrc, 1)}

    <h2>Controlling skill</h2>
    ${TC.authorityBanner('Exact, unmodified mirror of .pi/skills/orbital-model-selector/SKILL.md.')}
    <pre class="code">${TC.esc(skill)}</pre>

    <h2>Tests</h2>
    <p><code>tests/test_model_selector.py</code> covers a clearly-suitable CW case, a clearly-unsuitable
    GEO-scale case routed to the two-body fallback, a clearly-unsuitable case with no two-body contract
    (<code>UNSUPPORTED</code>), a boundary/qualified decision with surfaced concerns, a near-singular
    targeting-conditioning qualification, missing-information clarification (with and without an
    already-known violation), and an output-shape check across every outcome branch.</p>
    ${TC.authorityBanner('Exact, unmodified contents of tests/test_model_selector.py.')}
    ${TC.codeBlock(selectorTest, 1)}

    <p><a href="#/model-validity">See also: Model Validity →</a></p>
  `;
};
