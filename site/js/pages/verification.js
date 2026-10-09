'use strict';

window.TCPages['verification'] = async function (root) {
  const tbSrc = await TC.fetchText('data/src/twobody.py');
  const poliastroSrc = await TC.fetchText('data/src/poliastro_verify.py');
  const poliastroTest = await TC.fetchText('data/tests/test_poliastro_verify.py');
  const testSrc = await TC.fetchText('data/tests/test_twobody.py');
  const sourceMd = await TC.fetchText('data/reference/SOURCE.md');
  const propagation = TC.extractPySymbol(tbSrc, 'kepler_propagate_state');
  const poliastroContract = TC.extractPySymbol(poliastroSrc, 'verify_against_poliastro');
  const perturbationTest = TC.extractPySymbol(poliastroTest, 'test_deliberate_candidate_perturbation_fails');
  const contract = TC.extractPySymbol(tbSrc, 'TwoBodyCase');
  const unsupported = TC.extractPySymbol(tbSrc, 'unsupported_request');
  const energy = TC.extractPySymbol(tbSrc, 'specific_orbital_energy');
  const analyticalTest = TC.extractPySymbol(testSrc, 'test_circular_orbit_matches_analytical_state_after_one_period');
  const invariantTest = TC.extractPySymbol(testSrc, 'test_energy_and_angular_momentum_are_conserved_over_supported_duration');
  const invalidTest = TC.extractPySymbol(testSrc, 'test_cw_invalid_large_separation_case_has_deterministic_two_body_result');

  root.innerHTML = `
    ${TC.pageHeader('Two-Body Fallback and Verification', 'The bounded deterministic point-mass coast propagator used when CW assumptions do not hold; it is not a targeting or optimization solver.')}
    ${TC.teachingContract({
      assumptions: 'SI inertial Cartesian position/velocity; fixed central point mass; coast arc; fixed-step classical RK4.',
      symbols: '<code>r</code>: position [m]; <code>v</code>: velocity [m/s]; <code>μ</code>: gravitational parameter [m³/s²]; <code>h</code>: RK4 step [s].',
      mapping: '<code>reference/SOURCE.md §§C and E</code> → <code>src/twobody.py</code> → exact mirrored tests in <code>tests/test_twobody.py</code>; GMAT evidence contract → <code>.pi/skills/gmat-rendezvous-verification/SKILL.md</code>.',
      evidence: 'Circular one-period analytical return: 2 cm position and 2e-5 m/s velocity tolerance; energy and angular momentum invariant test over three periods.',
      limitations: 'No burns, rendezvous targeting, optimization, LVLH-relative input, J2, drag, third bodies, SRP, or thrust. The pinned Poliastro 0.17.0 adapter is an optional like-for-like point-mass cross-check, not a universal oracle. GMAT remains required end-to-end numerical and visual verification.'
    })}

    <h2>Supported fallback contract</h2>
    <table>
      <tr><th>Input</th><td>Six-element <code>[x,y,z,vx,vy,vz]</code> initial state in SI; positive <code>μ</code> [m³/s²]; finite duration [s]; positive fixed step count.</td></tr>
      <tr><th>Output</th><td>Final six-element state in the same SI inertial Cartesian frame.</td></tr>
      <tr><th>Stable metadata</th><td><code>frame="inertial-cartesian"</code>, <code>central_body="Earth"</code>, <code>dynamics="point-mass-two-body"</code>, <code>integrator="fixed-step-rk4"</code>; optional epoch is reserved for like-for-like external verification.</td></tr>
      <tr><th>Rejected input</th><td>Non-finite state/duration, non-positive μ or steps, and zero radius (the point-mass singularity) raise explicit <code>ValueError</code>.</td></tr>
      <tr><th>Outside scope</th><td><code>unsupported_request()</code> returns <code>UNSUPPORTED</code> for targeting, maneuver, optimization, thrust, and perturbation requests instead of inventing a result.</td></tr>
    </table>
    ${TC.codeRef('src/twobody.py', 'TwoBodyCase')}
    ${TC.authorityBanner('Exact, unmodified authoritative source mirror.')}
    ${contract ? TC.codeBlock(contract.code, contract.startLine) : ''}

    <h2>Point-mass state derivative</h2>
    <p>The coast state is <code>x = [r, v]</code>. The propagator evaluates <code>ṙ = v</code> and
    <code>v̇ = −μr / |r|³</code>. This nonlinear law is more general than CW for absolute point-mass coast arcs,
    but it does not by itself solve a rendezvous.</p>
    <h3>Classical RK4 stages</h3>
    <p>For <code>h = Δt / N</code>, the code computes <code>k1 = f(x)</code>, <code>k2 = f(x + h k1/2)</code>,
    <code>k3 = f(x + h k2/2)</code>, and <code>k4 = f(x + h k3)</code>, then advances
    <code>x + h(k1 + 2k2 + 2k3 + k4)/6</code>. Position and velocity stages are written separately.</p>
    ${TC.codeRef('src/twobody.py', 'kepler_propagate_state')}
    ${TC.authorityBanner('Exact, unmodified authoritative source mirror.')}
    ${propagation ? TC.codeBlock(propagation.code, propagation.startLine) : ''}

    <h2>Invariants and objective evidence</h2>
    <p>For this unperturbed model, specific energy <code>ε = |v|²/2 − μ/|r|</code> and specific angular momentum
    <code>h = r × v</code> should be constant up to numerical integration error. These are meaningful checks of
    the implemented force law and integration behavior, not evidence for omitted physical effects.</p>
    ${TC.codeRef('src/twobody.py', 'specific_orbital_energy')}
    ${energy ? TC.codeBlock(energy.code, energy.startLine) : ''}
    <h3>Reference, invariant, and CW-invalid cases</h3>
    <p>The test suite compares a circular LEO state after one analytical orbital period to its initial state,
    checks energy and angular momentum after three periods, and propagates a deterministic absolute state with
    a 1,000 km radial separation—a geometry intentionally outside local CW proximity assumptions.</p>
    ${analyticalTest ? TC.codeBlock(analyticalTest.code, analyticalTest.startLine) : ''}
    ${invariantTest ? TC.codeBlock(invariantTest.code, invariantTest.startLine) : ''}
    ${invalidTest ? TC.codeBlock(invalidTest.code, invalidTest.startLine) : ''}

    <h2>Required GMAT evidence (not yet integrated)</h2>
    <p><strong>Controlled contract:</strong> every candidate requires (1) GMAT numerical comparison of the same declared case in matched frame, epoch, state ordering, units, dynamics, and documented position/velocity tolerances, and (2) a non-empty accessible GMAT trajectory screenshot. Missing or inaccessible evidence, unavailable GMAT, or a tolerance exceedance is <em>not</em> PASS. This repository has no GMAT execution integration yet; the contract is defined in <code>reference/SOURCE.md §E</code> and the controlled verification skill.</p>

    <h2>External Poliastro cross-check</h2>
    <p><strong>TJC-1.7:</strong> <code>src/poliastro_verify.py</code> invokes a separately provisioned Python 3.10 subprocess using versioned JSON stdin/stdout. It compares the same SI inertial Cartesian point-mass coast state against pinned Poliastro 0.17.0 commit <code>c7d12e9b715d3fd60f2be233af707d5b97617d39</code>. Missing/broken environments return <code>UNAVAILABLE</code>; unsupported frames/models return <code>UNSUPPORTED</code>; disagreement remains <code>FAIL</code>. None can become PASS.</p>
    ${TC.codeRef('src/poliastro_verify.py', 'verify_against_poliastro')}
    ${poliastroContract ? TC.codeBlock(poliastroContract.code, poliastroContract.startLine) : ''}
    <p>Retained machine-readable contract evidence covers circular short, circular one-period, and bounded eccentric cases: <a href="../evidence/poliastro/contract-test-evidence.json">contract-test-evidence.json</a>. The evidence uses a deterministic subprocess stand-in because core Python does not install legacy Poliastro; it is not a live-Python/Poliastro claim. Provisioning, provenance, compatibility limits, and extension policy are in the <a href="data/docs/poliastro-verification-architecture.md">authoritative architecture</a>.</p>
    <h3>Failure visibility test</h3>
    ${perturbationTest ? TC.codeBlock(perturbationTest.code, perturbationTest.startLine) : ''}

    <h2>Explicit limitations</h2>
    ${TC.codeRef('src/twobody.py', 'unsupported_request')}
    ${unsupported ? TC.codeBlock(unsupported.code, unsupported.startLine) : ''}
    <p>The pinned Poliastro 0.17.0 process is a future external implementation cross-check, deliberately isolated
    from the core environment and not imported here. Read the authoritative
    <a href="data/docs/poliastro-verification-architecture.md">Poliastro verification architecture</a> for its
    request/result contract. GMAT remains required for end-to-end numerical and visual verification.</p>

    <h2>Authoritative reference section</h2>
    ${TC.authorityBanner('Exact, unmodified relevant physics reference is available in the complete source below.')}
    <details><summary>Open reference/SOURCE.md</summary><pre class="code">${TC.esc(sourceMd)}</pre></details>
  `;
};
