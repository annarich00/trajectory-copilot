'use strict';

window.TCPages['tests'] = async function (root) {
  const cwTestSrc = await TC.fetchText('data/tests/test_cw.py');
  const tbTestSrc = await TC.fetchText('data/tests/test_twobody.py');
  const valTestSrc = await TC.fetchText('data/tests/test_validation.py');
  const tests = [
    ['tests/test_cw.py', 'test_cw_rendezvous_benchmark', 'two_burn_targeting()', 'Well-conditioned CW two-impulse rendezvous regression.'],
    ['tests/test_cw.py', 'test_cw_exact_one_orbit_targeting_is_rejected', 'two_burn_targeting()', 'CW singularity rejects an undefined targeting result.'],
    ['tests/test_cw.py', 'test_cw_validation_basic', 'validate_cw_use()', 'CW applicability heuristic positive case.'],
    ['tests/test_twobody.py', 'test_circular_orbit_matches_analytical_state_after_one_period', 'propagate_cartesian_state()', 'Circular LEO returns to its analytical initial state after one period within declared position and velocity tolerances.'],
    ['tests/test_twobody.py', 'test_energy_and_angular_momentum_are_conserved_over_supported_duration', 'specific_orbital_energy(), specific_angular_momentum()', 'Point-mass coast invariants remain within numerical tolerances over three periods.'],
    ['tests/test_twobody.py', 'test_cw_invalid_large_separation_case_has_deterministic_two_body_result', 'propagate_cartesian_state()', 'A 1,000 km radial-separation absolute state, outside local CW assumptions, produces the same deterministic coast result twice.'],
    ['tests/test_twobody.py', 'test_like_for_like_case_metadata_is_stable_si_cartesian_contract', 'TwoBodyCase', 'Stable SI Cartesian metadata for TJC-1.7’s external verification adapter.'],
    ['tests/test_twobody.py', 'test_unsupported_targeting_request_is_explicit', 'unsupported_request()', 'Targeting requests return UNSUPPORTED rather than a fabricated solution.'],
    ['tests/test_twobody.py', 'test_invalid_propagation_inputs_are_rejected', 'propagate_cartesian_state()', 'Singular and invalid numerical inputs fail explicitly.'],
    ['tests/test_validation.py', 'test_model_validity_warning_triggers', 'compare_cw_two_body()', 'Comparison reports a model-validity warning for excessive disagreement.'],
  ];
  const sources = {'tests/test_cw.py': cwTestSrc, 'tests/test_twobody.py': tbTestSrc, 'tests/test_validation.py': valTestSrc};

  root.innerHTML = `
    ${TC.pageHeader('Test Explorer', 'Authoritative pytest cases mirrored from tests/. The browser does not run them.')}
    <p>${tests.length} named tests/groups across three files. The two-body set now includes analytical-reference,
    invariant, CW-invalid propagation, metadata, unsupported-request, and input-rejection evidence.</p>
    <div id="test-cards"></div>
    <h2>Run authoritative checks</h2>
    <pre class="code">.venv/bin/python -m pytest -q
python3 tools/sync_site_data.py --check
python3 tools/compare_upstream.py --check</pre>
    <p>Interactive results are a pedagogical JavaScript hand port only; pytest against these Python sources is authoritative.</p>
  `;
  const container = root.querySelector('#test-cards');
  for (const [file, name, func, concept] of tests) {
    const sym = TC.extractPySymbol(sources[file], name);
    container.appendChild(TC.el(`
      <div class="test-card"><h4>${TC.esc(name)}</h4><div class="test-meta mono">${TC.esc(file)}</div>
      <p><strong>Exercises:</strong> <code>${TC.esc(func)}</code></p><p>${TC.esc(concept)}</p>
      <details><summary>Show authoritative test source</summary>${TC.authorityBanner('Exact, unmodified text from ' + file + '.')}${sym ? TC.codeBlock(sym.code, sym.startLine) : '<p>Parameterized test group or symbol not found.</p>'}</details></div>
    `));
  }
};
