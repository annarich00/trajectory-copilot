'use strict';

window.TCPages['tests'] = async function (root) {
  const cwTestSrc = await TC.fetchText('data/tests/test_cw.py');
  const tbTestSrc = await TC.fetchText('data/tests/test_twobody.py');
  const valTestSrc = await TC.fetchText('data/tests/test_validation.py');

  const tests = [
    {
      file: 'tests/test_cw.py', name: 'test_cw_rendezvous_benchmark',
      func: 'two_burn_targeting()', concept: 'Two-impulse CW rendezvous at a well-conditioned (quarter-orbit) transfer time.',
      expected: 'Δv0 and Δv1 are finite and small (< 1 m/s each); final relative position and velocity are ≈0 (< 1e-6).',
      why: 'This is the primary positive-case regression test for the entire targeting algorithm. It locks in that a realistic, well-posed rendezvous produces physically sane, bounded burns and an exact terminal match.',
      failureMeaning: 'If this failed, either cw_stm() has a sign/formula error, or two_burn_targeting()\'s algebra (Step 3–6 in the targeting walkthrough) is broken — any rendezvous computed by this code could not be trusted.',
      src: cwTestSrc,
    },
    {
      file: 'tests/test_cw.py', name: 'test_cw_exact_one_orbit_targeting_is_rejected',
      func: 'two_burn_targeting(), check_phi_rv_conditioning()', concept: 'CW targeting singularity at n·t = 2π (exact one orbital period).',
      expected: 'two_burn_targeting() raises CWSingularTransferError rather than returning a (physically meaningless) least-squares solution.',
      why: 'This is the regression guard for the entire "Why the Singularity Matters" lesson. Without it, a future refactor could silently reintroduce a least-squares fallback and start returning enormous, unflagged Δv values.',
      failureMeaning: 'If this failed (no exception raised), the solver would be silently returning physically absurd delta-v magnitudes (potentially 10¹³ m/s, as demonstrated on the Singularity page) as if they were valid answers — a textbook example of silent, dangerous failure.',
      src: cwTestSrc,
    },
    {
      file: 'tests/test_cw.py', name: 'test_cw_validation_basic',
      func: 'validate_cw_use()', concept: 'Basic CW applicability heuristic check for a realistic, valid scenario.',
      expected: 'validate_cw_use() returns valid=True (no warnings) for the 350 km / 15,200 m separation / 6000 s transfer case.',
      why: 'Confirms the heuristic validity-checker does not raise false alarms for a textbook-valid proximity-operations scenario.',
      failureMeaning: 'If this failed, validate_cw_use() would be incorrectly flagging legitimate CW use cases as invalid, which would (if wired into an agent workflow) cause the system to reject good solutions or demand unnecessary higher-fidelity propagation.',
      src: cwTestSrc,
    },
    {
      file: 'tests/test_twobody.py', name: 'test_orbital_period_positive',
      func: 'orbital_period()', concept: 'Basic sanity check on the Keplerian orbital period formula.',
      expected: 'orbital_period(mu, a) > 0 for a 6778 km semi-major axis.',
      why: 'The most minimal possible smoke test — confirms the function runs and returns a positive number.',
      failureMeaning: 'If this failed, orbital_period() would be returning zero, negative, or NaN — a sign of a sign error or type error, not a sign that the specific numeric value is right or wrong.',
      src: tbTestSrc,
      softwareOnly: true,
    },
    {
      file: 'tests/test_twobody.py', name: 'test_cartesian_propagation_runs',
      func: 'propagate_cartesian_state()', concept: 'RK4 two-body Cartesian propagation smoke test.',
      expected: 'propagate_cartesian_state() returns a (6,)-shaped array of all-finite numbers after a 60 s, 200-step integration.',
      why: 'Confirms the two-body RK4 integrator does not crash, diverge to NaN/Inf, or return the wrong shape for a simple circular-orbit input.',
      failureMeaning: 'If this failed, the independent two-body verification pipeline (src/verify.py) would be unusable — every CW-vs-two-body comparison in this codebase ultimately depends on this function working.',
      src: tbTestSrc,
      softwareOnly: true,
    },
    {
      file: 'tests/test_validation.py', name: 'test_model_validity_warning_triggers',
      func: 'compare_cw_two_body()', concept: 'Model-validity warning logic: does the comparison correctly flag disagreement between CW and an independent model?',
      expected: 'Given a synthetic CW state of all-zeros and a synthetic "two-body" state 100 m / 0.2 m/s away, with tolerances of 10 m / 0.05 m/s, the result\'s warnings tuple contains "MODEL VALIDITY WARNING".',
      why: 'This is the only test that exercises the verification/warning mechanism at all. It establishes that compare_cw_two_body() actually flags disagreement rather than silently passing it through.',
      failureMeaning: 'If this failed, the verification layer could receive two wildly different states (as would happen with a real CW breakdown, e.g. GEO-scale separation) and NOT raise any warning — defeating the entire purpose of independent verification.',
      src: valTestSrc,
    },
  ];

  root.innerHTML = `
    ${TC.pageHeader('Test Explorer', 'Every test currently in tests/. Not "3 passed" — what each test actually establishes, physically and computationally.')}
    <p>${tests.length} tests across 3 files: <code>tests/test_cw.py</code> (3), <code>tests/test_twobody.py</code> (2),
    <code>tests/test_validation.py</code> (1).</p>
    <div id="test-cards"></div>
  `;

  const container = root.querySelector('#test-cards');
  for (const t of tests) {
    const sym = TC.extractPySymbol(t.src, t.name);
    const card = TC.el(`
      <div class="test-card">
        <h4>${TC.esc(t.name)}</h4>
        <div class="test-meta mono">${TC.esc(t.file)}</div>
        <div class="chain">
          <div class="node">${TC.esc(t.name)}</div><div class="arr">↓</div>
          <div class="node">${TC.esc(t.func)}</div><div class="arr">↓</div>
          <div class="node">${TC.esc(t.concept)}</div>
        </div>
        <p><strong>Expected behavior / invariant:</strong> ${TC.esc(t.expected)}</p>
        <p><strong>Why this test matters:</strong> ${TC.esc(t.why)}</p>
        <p><strong>What a failure would mean:</strong> ${TC.esc(t.failureMeaning)}</p>
        <details><summary style="cursor:pointer;color:var(--accent)">Show test source</summary>
          ${TC.authorityBanner('Exact, unmodified text of this test from ' + t.file + '.')}
          ${sym ? TC.codeBlock(sym.code, sym.startLine) : '<p>Not found.</p>'}
        </details>
      </div>
    `);
    container.appendChild(card);
  }

  root.insertAdjacentHTML('beforeend', `
    <h2>Running these tests yourself</h2>
    <p>From the repository root (with a working Python + pytest environment):</p>
    <pre class="code">cd ~/trajectory-copilot
pytest tests/ -v</pre>
    <p class="toc-inline">This site cannot execute pytest itself (it is a static browser page with no backend
    test runner). <strong>Running the command above is the only authoritative way to know these tests
    pass.</strong> Interactive numeric demos elsewhere on this site (CW STM Explorer, Targeting Walkthrough,
    Singularity, Experiment pages) use a separate, hand-ported JavaScript "pedagogical browser mirror"
    (<code>site/js/physics.js</code>) of the same equations, built and spot-checked during site development —
    it is a visualization aid, not a test runner, and not an independent verification of
    <code>src/cw.py</code>/<code>src/twobody.py</code>/<code>src/verify.py</code>.</p>
    <p><a href="#/test-classification">Continue: Software vs. Physical Tests →</a></p>
  `);
};
