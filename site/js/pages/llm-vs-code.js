'use strict';

window.TCPages['llm-vs-code'] = async function (root) {
  root.innerHTML = `
    ${TC.pageHeader('What the LLM Actually Does', 'A clear boundary between LLM reasoning/orchestration, deterministic code, and independent verification — essential for understanding what this architecture does and doesn\'t trust an LLM to do.')}

    <div class="grid-3">
      <div class="panel">
        <div class="panel-title">${TC.badge('llm', 'LLM responsibilities')}</div>
        <ul>
          <li>Interpret natural language</li>
          <li>Identify missing information</li>
          <li>Formalize the problem</li>
          <li>Select tools/models</li>
          <li>Construct solver inputs</li>
          <li>Interpret outputs</li>
          <li>Explain results</li>
          <li>Decide when clarification is needed</li>
        </ul>
        <p class="toc-inline">Implemented as prose instructions in
        <code>.pi/skills/orbital-problem-formalizer/SKILL.md</code>,
        <code>.pi/skills/orbital-model-selector/SKILL.md</code>,
        <code>.pi/skills/orbital-targeting-planner/SKILL.md</code>. Evidenced by behavioral transcripts in
        <code>evaluations/formalizer/*.txt</code> and <code>baseline_comparison.md</code>.</p>
      </div>
      <div class="panel">
        <div class="panel-title">${TC.badge('det', 'Deterministic code responsibilities')}</div>
        <ul>
          <li>Calculate orbital mechanics (n, T, v)</li>
          <li>Propagate states (CW linear STM; two-body RK4)</li>
          <li>Solve targeting equations (two_burn_targeting)</li>
          <li>Perform numerical optimization <span class="toc-inline">(PLANNED — src/optimization.py has no solver yet)</span></li>
          <li>Calculate errors</li>
          <li>Perform physical/numerical checks (condition number, singularity)</li>
        </ul>
        <p class="toc-inline">Implemented as Python in <code>src/cw.py</code>, <code>src/twobody.py</code>.
        Same inputs always produce the same outputs — no judgment calls, no language understanding.</p>
      </div>
      <div class="panel">
        <div class="panel-title">${TC.badge('ver', 'Independent verification responsibilities')}</div>
        <ul>
          <li>Independently propagate/check the result (nonlinear two-body, not CW-on-CW)</li>
          <li>Identify disagreement (position/velocity error vs. tolerance)</li>
          <li>Prevent false confidence (raise "MODEL VALIDITY WARNING" or reject outright)</li>
        </ul>
        <p class="toc-inline">Implemented in <code>src/verify.py</code>, <code>src/twobody.py</code>. See
        <a href="#/verification">Two-Body Verification Lesson</a>.</p>
      </div>
    </div>

    <h2>Why this separation matters</h2>
    <p>An LLM is good at language understanding and flexible judgment, but it has no reliable, repeatable
    mechanism for exact numerical computation — it can "recall" that CW has singularities near
    <code>n·t = kπ</code> if that fact happens to be well-represented in its training data, but it cannot
    <em>guarantee</em> catching every instance, especially for an unusual parameter combination it hasn't seen
    phrased quite that way before. A deterministic numerical check like
    <code>check_phi_rv_conditioning()</code>, by contrast, is <em>always</em> run, every time, with the same
    guaranteed behavior.</p>
    <p>Conversely, deterministic code has no way to interpret "the chaser is 200 meters behind the target" — it
    needs that already turned into a 6-vector relative state in a defined frame. That translation step
    requires language understanding and judgment the deterministic code does not (and should not) attempt.</p>

    <h2>Concrete example: the formalizer refusing to guess</h2>
    <p>From <code>evaluations/formalizer/test_01_underspecified.txt</code> — given only "The chaser is 200
    meters behind the target. Find a one-orbit rendezvous," the formalizer skill explicitly declined to invent
    a reference orbit, coordinate convention, or relative velocity, and classified the problem as <code>NEEDS
    MORE INFORMATION + MODEL VALIDITY CONCERN</code>. Per <code>baseline_comparison.md</code> (Test 1), it also
    explicitly noted that assuming "behind" corresponds to a specific CW/LVLH axis would itself be an
    unauthorized assumption, not a confirmed input — it surfaced that ambiguity rather than silently resolving
    it one way or the other.</p>
    ${TC.callout('good', 'This is the LLM doing its job correctly', `<p>Recognizing ambiguity and refusing to
      silently resolve it is squarely an LLM-reasoning responsibility — no deterministic code in this
      repository could make that judgment call, because the input is unstructured natural language.</p>`)}

    <h2>Concrete example: the solver refusing to guess</h2>
    <p>From <code>tests/test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected</code> — given a
    well-formed, fully-specified numeric targeting problem at exactly one orbital period, the deterministic
    solver (<code>two_burn_targeting()</code>) raises <code>CWSingularTransferError</code> rather than
    returning a numerically "valid-looking" but physically absurd Δv.</p>
    ${TC.callout('good', 'This is the deterministic code doing its job correctly', `<p>This is squarely a
      deterministic-code responsibility: it does not require language understanding, only a condition-number
      check applied consistently every single time. No amount of LLM judgment is a substitute for actually
      computing <code>cond(Φrv)</code>.</p>`)}

    <h2>Where the boundary is still soft in this repository</h2>
    <ul>
      <li>The model-selector skill's richer rejection rules (GEO-scale geometry, non-circular chief orbit,
      multi-rev phasing) are currently LLM-judgment-only — <code>validate_cw_use()</code> in code does not
      check for them. ${TC.badge('partial', 'PARTIAL')}</li>
      <li>There is no single orchestrated object joining the targeting solver's pass/fail state with the
      verification layer's pass/warn state into one "PASS / WARNING / FAIL" decision the LLM could branch on
      programmatically. ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED')}</li>
      <li><code>src/optimization.py</code> describes optimization problems as data but has no solver, so the
      "LLM constructs solver inputs → deterministic code solves" handoff is incomplete for anything beyond the
      closed-form two-impulse CW case. ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED')}</li>
    </ul>

    <p><a href="#/research">Continue: Research Connection →</a></p>
  `;
};
