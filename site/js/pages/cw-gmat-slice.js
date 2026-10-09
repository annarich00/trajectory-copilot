'use strict';

window.TCPages['cw-gmat-slice'] = async function (root) {
  const [caseText, runner] = await Promise.all([
    TC.fetchText('data/examples/cw_gmat_vertical_slice.yaml'),
    TC.fetchText('data/scripts/run_cw_gmat_slice.py'),
  ]);
  root.innerHTML = `
    ${TC.pageHeader('CW-to-GMAT early vertical slice', 'One reproducible circular-LEO rendezvous path from structured input to deterministic targeting, generated GMAT invocation evidence, comparison contract, and returned plot artifact.')}
    ${TC.callout('warn', 'Verification boundary', '<p>The runner creates an SVG trajectory plot even when GMAT is unavailable. That plot and the CW result are not GMAT verification. The JSON report says <code>NOT VERIFIED</code> unless GMAT exits successfully and a parseable GMAT final state exists.</p>')}
    <h2>Reproduce</h2>
    <pre class="code">.venv/bin/python scripts/run_cw_gmat_slice.py --output-dir /tmp/cw-gmat-slice</pre>
    <p>Set <code>GMAT_EXECUTABLE=/path/to/GMAT</code> or pass <code>--gmat</code> for the documented noninteractive executable mechanism. Exit status, stdout, and stderr are returned in <code>verification_result.json</code>.</p>
    <h2>1. Structured circular-LEO input</h2>
    ${TC.authorityBanner('Exact synchronized input mirror; the YAML file is authoritative.')}
    ${TC.codeBlock(caseText, 1)}
    <h2>2. Deterministic CW solution and generated GMAT script</h2>
    <p>The runner uses <code>src/cw.py::two_burn_targeting</code> at a quarter orbital period (away from the documented half-period singularities), writes a GMAT script, and invokes the configured executable via a noninteractive subprocess.</p>
    <h2>3. Numerical comparison contract</h2>
    <p>The report reserves explicit provisional tolerances: final position <strong>1 m</strong>, final velocity <strong>0.001 m/s</strong>, and total maneuver delta-v <strong>0.001 m/s</strong>. Missing GMAT state values remain null; they are never silently replaced by CW values.</p>
    <h2>4. Returned trajectory artifact</h2>
    <p><code>trajectory.svg</code> is generated automatically and its non-empty status and path are fields of the JSON verification result. It is a deterministic CW fallback plot, not an undocumented repository artifact or GMAT screenshot claim.</p>
    <h2>Authoritative runner mirror</h2>
    ${TC.authorityBanner('Exact synchronized source mirror; Python remains authoritative. This browser does not execute it.')}
    ${TC.codeBlock(runner, 1)}
  `;
};
