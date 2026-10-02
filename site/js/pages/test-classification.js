'use strict';

window.TCPages['test-classification'] = async function (root) {
  root.innerHTML = `
    ${TC.pageHeader('Software vs. Physical Tests', 'Not all tests in tests/ establish the same kind of truth. Some confirm the code runs and returns the right shape/type. Others confirm the physics itself behaves correctly or detects when it does not.')}

    <div class="callout">
      <div class="callout-title">The distinction</div>
      <p><strong>Software consistency test:</strong> "Does this function return a value of the expected shape,
      type, and basic sanity (finite, non-crashing, positive where expected)?" This says nothing about whether
      the number is physically correct — it would pass even if a sign error made the physics wrong, as long as
      the output still has the right shape and doesn't blow up.</p>
      <p><strong>Physical correctness / physical-property test:</strong> "Does the system actually satisfy a
      real physical relationship, invariant, or expected behavior derived from the physics itself?" (e.g. a
      specific known-singular configuration is rejected; a terminal condition is exactly satisfied; a model
      disagreement triggers a warning.)</p>
    </div>

    <h2>Classification of every test in tests/</h2>
    <table>
      <tr><th>Test</th><th>Classification</th><th>Why</th></tr>
      <tr>
        <td><code>test_cw.py::test_cw_rendezvous_benchmark</code></td>
        <td><span class="test-tag physical">Physical</span></td>
        <td>Checks that the two-impulse solution actually satisfies the rendezvous physics: Δv magnitudes are
        bounded/realistic (&lt; 1 m/s, consistent with a small proximity maneuver) AND the final relative state
        is numerically zero (true terminal rendezvous achieved). This is a physical-property assertion, not
        just a shape check.</td>
      </tr>
      <tr>
        <td><code>test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected</code></td>
        <td><span class="test-tag physical">Physical</span></td>
        <td>Encodes a physical/numerical-modeling fact: at <code>n·t = 2π</code>, the two-impulse targeting
        problem has no well-posed solution. The test establishes that the solver <em>recognizes this</em>
        rather than returning a number — this is a statement about the physics/math of CW, not merely "the
        function returns something."</td>
      </tr>
      <tr>
        <td><code>test_cw.py::test_cw_validation_basic</code></td>
        <td><span class="test-tag physical">Physical</span></td>
        <td>Checks that a textbook-valid proximity-operations scenario (small separation vs. orbit radius,
        reasonable transfer time) is correctly judged valid by the CW applicability heuristic — a statement
        about whether the physical assumptions underlying CW hold, not just about code execution.</td>
      </tr>
      <tr>
        <td><code>test_twobody.py::test_orbital_period_positive</code></td>
        <td><span class="test-tag software">Software</span></td>
        <td>Only checks <code>orbital_period(mu, a) &gt; 0</code>. Does NOT check the number is numerically
        correct (e.g. ≈ 5554 s for a 6778 km orbit) — a formula with a wrong constant factor (e.g. missing the
        2π) could still pass this test as long as it stayed positive.</td>
      </tr>
      <tr>
        <td><code>test_twobody.py::test_cartesian_propagation_runs</code></td>
        <td><span class="test-tag software">Software</span></td>
        <td>Only checks the output has shape <code>(6,)</code> and all entries are finite. Does NOT check that
        the propagated orbit is physically correct (e.g. conserves energy/angular momentum, matches a known
        analytic solution, or stays on a sensible trajectory) — purely a "did it crash or diverge" smoke test.</td>
      </tr>
      <tr>
        <td><code>test_validation.py::test_model_validity_warning_triggers</code></td>
        <td><span class="test-tag physical">Physical</span></td>
        <td>Checks the actual physical-validity decision logic: given two different states, does the system
        correctly recognize they disagree beyond tolerance and raise "MODEL VALIDITY WARNING"? This is testing
        a physical-judgment capability (detecting model breakdown), not just that a function runs.</td>
      </tr>
    </table>

    <h2>Why this distinction matters</h2>
    <p>A codebase can have 100% passing software-consistency tests and still be <em>completely wrong</em>
    physically — e.g. if <code>orbital_period()</code> had a bug that returned <code>mu * a</code> instead of
    <code>2π√(a³/μ)</code>, <code>test_orbital_period_positive</code> would still pass (the result is still
    positive), but every downstream computation using that period would be physically nonsensical.</p>
    <p>This repository's physical-property tests (<code>test_cw_rendezvous_benchmark</code>,
    <code>test_cw_exact_one_orbit_targeting_is_rejected</code>, <code>test_cw_validation_basic</code>,
    <code>test_model_validity_warning_triggers</code>) are the ones that actually give confidence the physics is
    right, or — just as importantly — that the system knows when it <em>can't</em> be confident. The
    software-consistency tests (<code>test_orbital_period_positive</code>,
    <code>test_cartesian_propagation_runs</code>) are necessary but not sufficient.</p>

    ${TC.callout('warn', 'A gap in the current test suite', `<p><strong>PLANNED \u2014 NOT YET IMPLEMENTED:</strong>
      there is currently no test that checks <code>orbital_period()</code> or <code>vis_viva_speed()</code>
      against a known numeric value (e.g. "a 6778 km circular orbit has a period of approximately 5554
      seconds"). Both <code>test_twobody.py</code> tests are software-consistency tests only; there is no
      physical-correctness test for the two-body module's basic formulas, even though
      <code>validate_against_two_body()</code> in <code>src/verify.py</code> depends on
      <code>propagate_cartesian_state()</code> being numerically correct, not just "finite."</p>`)}

    <p><a href="#/verification">Continue: Two-Body Verification Lesson →</a></p>
  `;
};
