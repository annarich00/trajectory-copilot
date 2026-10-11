'use strict';

window.TCPages['cw-gmat-slice'] = async function (root) {
  const [caseText, runner, verifyModule, verifyTests] = await Promise.all([
    TC.fetchText('data/examples/cw_gmat_vertical_slice.yaml'),
    TC.fetchText('data/scripts/run_cw_gmat_slice.py'),
    TC.fetchText('data/src/gmat_verify.py'),
    TC.fetchText('data/tests/test_cw_gmat_slice.py'),
  ]);
  root.innerHTML = `
    ${TC.pageHeader('GMAT rendezvous verification', 'One reproducible circular-LEO CW rendezvous case, run end-to-end through headless GMAT R2026a: structured input to deterministic CW targeting, a generated/executed GMAT script, parsed numerical output, tolerance comparison, and a returned trajectory artifact.')}

    ${TC.callout('warn', 'Verification boundary', '<p>GMAT remains an independent verifier for the already-supported CW rendezvous contract only &mdash; no optimization, perturbed/high-fidelity dynamics, CR3BP/cislunar, or broad mission planning. A result is <code>verified: true</code> only when GMAT actually ran, its final-state report parsed cleanly, and the parsed state agreed with the CW analytical final state within tolerance. Any one of five distinct failure modes below, plus an earlier CW-targeting-infeasible case, is reported instead of a false pass.</p>')}

    <h2>Reproduce</h2>
    <pre class="code">.venv/bin/python scripts/run_cw_gmat_slice.py --output-dir /tmp/cw-gmat-slice --gmat GmatConsole-R2026a</pre>
    <p>Set <code>GMAT_EXECUTABLE</code> or pass <code>--gmat</code> for the configured noninteractive executable. GMAT availability is confirmed by actually invoking <code>&lt;executable&gt; --version</code> and checking for a recognizable GMAT banner, not by <code>shutil.which</code> alone.</p>

    <h2>1. Structured circular-LEO input</h2>
    ${TC.authorityBanner('Exact synchronized input mirror; the YAML file is authoritative.')}
    ${TC.codeBlock(caseText, 1)}

    <h2>2. Script-generation mapping (structured data &rarr; GMAT script)</h2>
    <p><code>src/gmat_verify.py::generate_gmat_script</code> maps the case and the CW solution directly to GMAT script resources, with every unit conversion explicit (GMAT uses km / km-s natively):</p>
    <table>
      <tr><th>Structured field</th><th>GMAT resource</th></tr>
      <tr><td class="mono">radius_m</td><td class="mono">Chief.SMA (km), circular/equatorial Keplerian elements</td></tr>
      <tr><td class="mono">state0 (pre-burn-1 LVLH state, SI)</td><td class="mono">Deputy.X/Y/Z/VX/VY/VZ in a dedicated <code>LVLH</code> <code>ObjectReferenced</code> CoordinateSystem (<code>XAxis=R</code>, <code>ZAxis=N</code>) &mdash; no extra rotation needed</td></tr>
      <tr><td class="mono">dv0_mps, dv1_mps (CW burns, SI)</td><td class="mono">Burn1/Burn2.Element1-3, entered directly in the same LVLH CoordinateSystem</td></tr>
      <tr><td class="mono">transfer_time_s</td><td class="mono">Propagate Prop(Chief, Deputy) {Chief.ElapsedSecs = ...}</td></tr>
      <tr><td>point-mass, two-body dynamics assumption</td><td class="mono">ForceModel with GravityField.Earth.Degree/Order = 0 (no other force) &mdash; consistent with <code>src/cw.py</code>/<code>src/twobody.py</code></td></tr>
    </table>
    <p>Four dedicated <code>ReportFile</code> resources (<code>RFInit</code>, <code>RFPostBurn1</code>, <code>RFFinal</code>, <code>RFTrajectory</code>), each toggled <code>WriteReport = true/false</code> around one <code>Report</code> command, give clean isolated snapshots instead of one tangled continuous report. All four <code>ReportFile.Filename</code> values are written as absolute paths: GMAT writes relative <code>ReportFile</code> paths relative to its own <code>bin/</code> working directory, not the caller's current directory, so a relative path would silently miss the output directory.</p>
    <p>The <code>Deputy.LVLH.X/Y/Z/VX/VY/VZ</code> report columns are validated, not merely assumed, to match <code>src/cw.py</code>'s <code>[x, y, z, x_dot, y_dot, z_dot]</code> convention: the end-to-end comparison below is exactly that validation, run against real GMAT output.</p>

    <h2>3. Execution flow</h2>
    <ol>
      <li>Solve the CW rendezvous problem (<code>src/cw.py::solve_cw_rendezvous</code>). An infeasible boundary condition is reported as <code>CW_TARGETING_INFEASIBLE</code> immediately; no GMAT script or screenshot is generated.</li>
      <li>Generate the GMAT script and the required trajectory screenshot artifact from the structured problem/solution data (produced even if GMAT later turns out to be unavailable, so a <code>MISSING_GMAT</code> run still returns traceable evidence).</li>
      <li>Confirm GMAT availability by invoking <code>&lt;executable&gt; --version</code>; a missing or non-running executable is <code>MISSING_GMAT</code>.</li>
      <li>Execute the generated script noninteractively via <code>subprocess.run([executable, script_path], timeout=...)</code>, capturing stdout/stderr/exit status/timeout. A nonzero exit or timeout is <code>EXECUTION_ERROR</code>.</li>
      <li>Parse the final-state and trajectory <code>ReportFile</code> text output, validating a 7-field header and well-shaped numeric rows before converting GMAT's km/km-s back to SI m/m-s. Any missing/empty/wrong-shape/non-numeric report is <code>MALFORMED_OUTPUT</code>.</li>
      <li>Validate the trajectory screenshot/plot artifact as non-empty, well-formed SVG. A missing/empty/malformed artifact is <code>SCREENSHOT_FAILURE</code>.</li>
      <li>Compare the parsed GMAT final state to the CW analytical final state at configured position/velocity tolerances. A <code>WARNING</code> or <code>FAIL</code> comparison status is <code>NUMERICAL_DISAGREEMENT</code>.</li>
      <li>Only when every step above succeeded and the comparison is <code>PASS</code> is the result <code>verified: true</code>.</li>
    </ol>

    <h2>4. Parsed outputs and tolerance logic</h2>
    <p>The report reserves explicit provisional tolerances: final position <strong>1 m</strong>, final velocity <strong>0.001 m/s</strong>, and total maneuver delta-v <strong>0.001 m/s</strong>. <code>src/gmat_verify.py::compare_gmat_final_state</code> returns one of three structured statuses: <code>PASS</code> (within tolerance), <code>WARNING</code> (within a configurable multiple of tolerance &mdash; a bounded disagreement, not a pass), or <code>FAIL</code> (beyond that margin). Both <code>WARNING</code> and <code>FAIL</code> surface as the <code>NUMERICAL_DISAGREEMENT</code> failure mode in the final result; neither is ever reported as verified.</p>

    <h2>5. Screenshot capture and artifact return</h2>
    <p>Headless <code>GmatConsole-R2026a</code> cannot render <code>OrbitView</code>/OpenFrames graphics in this environment (its GUI/OpenFrames plugins fail to load in console mode), so the returned trajectory visualization is a deterministic SVG plot of the relative trajectory (<code>scripts/run_cw_gmat_slice.py::write_svg</code>), overlaid with the parsed GMAT trajectory report points when GMAT output is available, falling back to the CW-only trajectory otherwise. <code>src/gmat_verify.py::validate_screenshot</code> checks the artifact exists, is non-empty, and is well-formed SVG, returning the artifact's path and non-empty status as explicit fields of <code>verification_result.json</code>.</p>

    <h2>6. Five distinct failure modes (never a false pass)</h2>
    <table>
      <tr><th>failure_mode</th><th>Trigger</th><th>Distinguished from</th></tr>
      <tr><td class="mono">CW_TARGETING_INFEASIBLE</td><td>CW boundary condition itself is unreachable</td><td>reported before any GMAT script exists</td></tr>
      <tr><td class="mono">MISSING_GMAT</td><td>configured executable not found, or does not produce a recognizable GMAT <code>--version</code> banner</td><td><code>gmat.attempted = false</code>; never confused with an executable that ran and then failed</td></tr>
      <tr><td class="mono">EXECUTION_ERROR</td><td>GMAT ran but the mission script exited nonzero, or timed out</td><td><code>gmat.attempted = true</code>, nonzero/absent <code>exit_status</code>; distinct from a parse failure after a successful exit</td></tr>
      <tr><td class="mono">MALFORMED_OUTPUT</td><td>GMAT exited zero but a ReportFile is missing, empty, wrong-shaped, or non-numeric</td><td><code>gmat.exit_status == 0</code>; distinct from an execution failure</td></tr>
      <tr><td class="mono">NUMERICAL_DISAGREEMENT</td><td>parsed GMAT final state exceeds tolerance vs. CW (comparison <code>WARNING</code>/<code>FAIL</code>)</td><td>output parsed cleanly; distinct from a parse/shape failure</td></tr>
      <tr><td class="mono">SCREENSHOT_FAILURE</td><td>trajectory screenshot/plot artifact missing, empty, or not well-formed</td><td>everything numerical can otherwise pass; still never reported as verified</td></tr>
    </table>
    <p>Each failure mode is independently covered by a monkeypatched test in <code>tests/test_cw_gmat_slice.py</code>, plus one real end-to-end run against <code>GmatConsole-R2026a</code> for this benchmark case that asserts the actual observed GMAT exit status and numerical comparison, rather than assuming success.</p>

    <h2>Authoritative source mirrors</h2>
    ${TC.authorityBanner('Exact synchronized source mirrors; Python remains authoritative. This browser does not execute it.')}
    <details><summary style="cursor:pointer;color:var(--accent)">src/gmat_verify.py (script generation, execution, parsing, comparison, screenshot validation)</summary>
      ${TC.codeBlock(verifyModule, 1)}
    </details>
    <details><summary style="cursor:pointer;color:var(--accent)">scripts/run_cw_gmat_slice.py (orchestration entry point)</summary>
      ${TC.codeBlock(runner, 1)}
    </details>
    <details><summary style="cursor:pointer;color:var(--accent)">tests/test_cw_gmat_slice.py (the 5 failure-mode tests, plus the real end-to-end GMAT run)</summary>
      ${TC.codeBlock(verifyTests, 1)}
    </details>
  `;
};
