'use strict';

window.TCPages['singularity'] = async function (root) {
  const cwSrc = await TC.fetchText('data/src/cw.py');
  const targetSym = TC.extractPySymbol(cwSrc, 'two_burn_targeting');
  const testSrc = await TC.fetchText('data/tests/test_cw.py');
  const geoTest = TC.extractPySymbol(testSrc, 'test_cw_geo_integer_period_reachable_cases_use_minimum_norm_svd_solution');
  const infeasibleTest = TC.extractPySymbol(testSrc, 'test_cw_integer_period_unreachable_boundary_returns_metadata_not_exception');

  root.innerHTML = `
    ${TC.pageHeader('Singular CW Targeting: Reachable Is Not Unique', 'Integer-period Phi_rv singularities require a column-space feasibility test, not a blanket rejection or silent retiming.')}
    ${TC.teachingContract({
      assumptions: 'Fixed-duration, linear circular-chief CW targeting in the repository LVLH/RIC convention.',
      symbols: '<code>b = rf − Φrr r0</code>; <code>Φrv v0⁺ = b</code>; <code>Δv0 = v0⁺ − v0</code>.',
      mapping: '<code>reference/SOURCE.md</code> → <code>src/cw.py::two_burn_targeting</code>.',
      evidence: '<code>tests/test_cw.py</code> GEO P=1/2/3 reachable and generic integer-period unreachable regressions.',
      limitations: 'This policy does not alter transfer time, prove multi-revolution CW validity, or solve a general optimization problem.'
    })}

    <h2>Partitioned boundary equation</h2>
    <p>With the first burn applied at the initial time, the position block of the CW STM is</p>
    <div class="formula">rf = Φrr r0 + Φrv v0⁺<br/>Φrv v0⁺ = b, where b = rf − Φrr r0</div>
    <p>At an integer orbital period, Φrv loses rank. That prevents a unique inverse, but it does not by itself prove
    that the requested terminal position is impossible. The correct question is whether <code>b</code> belongs to
    the column space of Φrv.</p>

    <h2>Explicit SVD policy</h2>
    <div class="panel">
      <ol>
        <li>Compute an SVD of Φrv. Singular values at or below <code>1e-12 × σmax</code> are treated as zero.</li>
        <li>Project <code>b</code> onto the retained left-singular-vector column space.</li>
        <li>Accept reachability only when the residual is at most <code>1e-9 × max(1, ||b||)</code> metres.</li>
        <li>For a reachable singular case, return the SVD-pseudoinverse minimum-norm <code>v0⁺</code>; the result is
        marked <code>singular-reachable</code> and non-unique.</li>
        <li>For an unreachable singular case, return <code>singular-infeasible</code>, a human-readable reason, and
        no burns or terminal state. The requested duration is never changed.</li>
      </ol>
    </div>
    ${TC.callout('warn', 'Conditioning is still explicit', '<p>Well-conditioned full-rank systems are marked <code>unique</code> and use the direct solve. A condition number above <code>1e6</code> routes through the documented SVD reachability policy so a near-singular result is never presented as a unique inverse.</p>')}

    <h2>GEO regression evidence</h2>
    <p>The authoritative test starts at <code>r0 = [0, −100 km, 0]</code> and targets the origin at one, two, and
    three circular GEO periods. Each is singular but reachable, reaches the terminal position within 1 µm in the
    CW propagation assertion, and has decreasing total reported Δv as the period count increases.</p>
    ${TC.codeRef('tests/test_cw.py', 'test_cw_geo_integer_period_reachable_cases_use_minimum_norm_svd_solution')}
    ${TC.authorityBanner('Exact, unmodified test text from the authoritative Python test mirror.')}
    ${geoTest ? TC.codeBlock(geoTest.code, geoTest.startLine) : ''}

    <h2>Unreachable boundary behavior</h2>
    <p>A generic integer-period boundary with a radial terminal displacement outside the Φrv column space must not
    throw during a matrix inverse or fabricate a maneuver. It returns machine-readable
    <code>singular-infeasible</code> metadata instead.</p>
    ${TC.codeRef('tests/test_cw.py', 'test_cw_integer_period_unreachable_boundary_returns_metadata_not_exception')}
    ${TC.authorityBanner('Exact, unmodified test text from the authoritative Python test mirror.')}
    ${infeasibleTest ? TC.codeBlock(infeasibleTest.code, infeasibleTest.startLine) : ''}

    <h2>Authoritative implementation</h2>
    ${TC.codeRef('src/cw.py', 'two_burn_targeting')}
    ${TC.authorityBanner('Exact, unmodified text from src/cw.py. Browser pages are explanatory only; run pytest for authoritative evidence.')}
    ${targetSym ? TC.codeBlock(targetSym.code, targetSym.startLine) : ''}
  `;
};
