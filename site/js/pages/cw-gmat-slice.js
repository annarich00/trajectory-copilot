'use strict';

window.TCPages['cw-gmat-slice'] = async function (root) {
  const [caseText, runner, verifyModule, reportModule, verifyTests, reportTests, exampleSvg, exampleResult] = await Promise.all([
    TC.fetchText('data/examples/cw_gmat_vertical_slice.yaml'),
    TC.fetchText('data/scripts/run_cw_gmat_slice.py'),
    TC.fetchText('data/src/gmat_verify.py'),
    TC.fetchText('data/src/verification_report.py'),
    TC.fetchText('data/tests/test_cw_gmat_slice.py'),
    TC.fetchText('data/tests/test_verification_report.py'),
    TC.fetchText('data/examples/cw_gmat_slice_example/trajectory.svg'),
    TC.fetchText('data/examples/cw_gmat_slice_example/verification_result.json'),
  ]);
  root.innerHTML = `
    ${TC.pageHeader('GMAT rendezvous verification', 'One reproducible circular-LEO CW rendezvous case, run end-to-end through headless GMAT R2026a: structured input to deterministic CW targeting, a generated/executed GMAT script, parsed numerical output, tolerance comparison, and a returned trajectory artifact.')}

    ${TC.callout('warn', 'Verification boundary', '<p>GMAT remains an independent verifier for the already-supported CW rendezvous contract only &mdash; no optimization, perturbed/high-fidelity dynamics, CR3BP/cislunar, or broad mission planning. A result is <code>verified: true</code> only when GMAT actually ran, its final-state report parsed cleanly, and the parsed state agreed with the CW analytical final state within tolerance. Any one of five distinct failure modes below, plus an earlier CW-targeting-infeasible case, is reported instead of a false pass.</p>')}

    <h2>Reproduce</h2>
    <pre class="code">.venv/bin/python scripts/run_cw_gmat_slice.py --gmat GmatConsole-R2026a</pre>
    <p>Set <code>GMAT_EXECUTABLE</code> or pass <code>--gmat</code> for the configured noninteractive executable. GMAT availability is confirmed by actually invoking <code>&lt;executable&gt; --version</code> and checking for a recognizable GMAT banner, not by <code>shutil.which</code> alone. Omitting <code>--output-dir</code> (as above) writes every artifact to the persistent, discoverable default location described below, not an ephemeral temp directory.</p>

    ${TC.callout('info', 'Where to find the produced artifact (TJC-2)', `<p>By default, every real run writes its generated GMAT script, parsed ReportFile logs, trajectory screenshot/plot, and <code>verification_result.json</code> to <code class="mono">artifacts/cw_gmat_slice/</code> at the repository root &mdash; not only a caller-supplied or temp directory. See <code class="mono">artifacts/cw_gmat_slice/README.md</code> for the exact persistence convention (only that README is tracked in git; actual per-run outputs are gitignored to avoid bloating history). <code>verification_result.json</code> itself also carries this location as an explicit <code>artifact_storage_convention</code> field, and a <code>trajectory_artifact</code> field with the direct path to whichever artifact was actually produced.</p><p>One small, permanently committed example run (shown below) lives at <code class="mono">examples/cw_gmat_slice_example/</code> so it is always available here without needing GMAT installed.</p>`)}

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
      <li>Generate the GMAT script for numeric verification, then attempt a real GMAT GUI (OrbitView/OpenFrames) trajectory screenshot <strong>before</strong> falling back to a deterministic SVG plot (see &sect;5). Both are produced even if GMAT later turns out to be unavailable, so a <code>MISSING_GMAT</code> run still returns traceable evidence.</li>
      <li>Confirm GMAT availability by invoking <code>&lt;executable&gt; --version</code>; a missing or non-running executable is <code>MISSING_GMAT</code>.</li>
      <li>Execute the generated script noninteractively via <code>subprocess.run([executable, script_path], timeout=...)</code>, capturing stdout/stderr/exit status/timeout. A nonzero exit or timeout is <code>EXECUTION_ERROR</code>.</li>
      <li>Parse the final-state and trajectory <code>ReportFile</code> text output, validating a 7-field header and well-shaped numeric rows before converting GMAT's km/km-s back to SI m/m-s. Any missing/empty/wrong-shape/non-numeric report is <code>MALFORMED_OUTPUT</code>.</li>
      <li>Validate the trajectory screenshot/plot artifact as non-empty and well-formed (PNG for a real GMAT GUI render, SVG for the fallback). A missing/empty/malformed artifact is <code>SCREENSHOT_FAILURE</code>.</li>
      <li>Compare the parsed GMAT final state to the CW analytical final state at configured position/velocity tolerances. A <code>WARNING</code> or <code>FAIL</code> comparison status is <code>NUMERICAL_DISAGREEMENT</code>.</li>
      <li>Only when every step above succeeded and the comparison is <code>PASS</code> is the result <code>verified: true</code>.</li>
    </ol>

    <h2>4. Parsed outputs and tolerance logic</h2>
    <p>The report reserves explicit provisional tolerances: final position <strong>1 m</strong>, final velocity <strong>0.001 m/s</strong>, and total maneuver delta-v <strong>0.001 m/s</strong>. <code>src/gmat_verify.py::compare_gmat_final_state</code> returns one of three structured statuses: <code>PASS</code> (within tolerance), <code>WARNING</code> (within a configurable multiple of tolerance &mdash; a bounded disagreement, not a pass), or <code>FAIL</code> (beyond that margin). Both <code>WARNING</code> and <code>FAIL</code> surface as the <code>NUMERICAL_DISAGREEMENT</code> failure mode in the final result; neither is ever reported as verified.</p>

    <h2>5. Screenshot capture: real GMAT GUI attempt, then SVG fallback (TJC-2)</h2>
    <p><code>src/gmat_verify.py::attempt_gmat_gui_screenshot</code> genuinely attempts a real GMAT GUI (OrbitView/OpenFrames) render <strong>before</strong> the SVG fallback is used: it launches the GMAT GUI binary (<code>GMAT-R2026a</code>, as opposed to the console-mode <code>GmatConsole-R2026a</code> used for numeric verification) against a generated <code>OrbitView</code> preview script under the configured <code>DISPLAY</code>, waits for it to render, and grabs the screen &mdash; only ever reporting success when a real, non-blank image is actually observed.</p>
    <p><strong>Investigated and documented blocker (reproducible evidence, not an assumption):</strong> in this project's sandboxed WSLg environment, a real X display genuinely exists (<code class="mono">DISPLAY=:0</code>), and <code>GMAT-R2026a</code> genuinely launches under it and maps real OrbitView/OpenFrames windows (confirmed via a window-tree inspection showing real, viewable child windows) &mdash; this is not a crash. However, every attempt to externally capture that rendered content returned a uniformly blank image (confirmed at multiple wait durations, with identical results to a capture taken with no GMAT process running at all), and direct X11 <code>XGetImage</code> calls against the mapped windows failed outright. No system screenshot utility is installed, and installing one requires <code>sudo</code>, which is unavailable in this environment. The sandbox's compositor does not expose the rendered buffer to standard external X11 screen-capture mechanisms.</p>
    <p>Every run therefore currently falls back to a deterministic SVG plot of the relative trajectory (<code>scripts/run_cw_gmat_slice.py::write_svg</code>), overlaid with the parsed GMAT trajectory report points when GMAT output is available. The structured result's <code>screenshot_source</code> field (<code>"gmat_gui"</code> or <code>"svg_fallback"</code>) always records which artifact was actually produced, so this never has to be inferred or assumed from the file extension alone. <code>src/gmat_verify.py::validate_screenshot</code>/<code>validate_gui_screenshot</code> check the artifact exists, is non-empty, and is well-formed, returning the artifact's path and non-empty status as explicit fields of <code>verification_result.json</code>.</p>

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

    <h2>Example committed artifact</h2>
    <p>A permanently committed example run (<code class="mono">examples/cw_gmat_slice_example/</code>) reaches a real <code>VERIFIED</code> result (position error ~0.0079 m, velocity error ~1.17e-5 m/s). Its trajectory artifact, produced by the SVG fallback described above:</p>
    <div style="background:#fff;border-radius:6px;padding:8px;display:inline-block">${exampleSvg}</div>
    ${TC.codeBlock(exampleResult, 1)}

    <h2>7. Unified verification report (TJC-1.19)</h2>
    <p>Every run above, regardless of which outcome it reaches, now also assembles one explicit <code>src/verification_report.py::UnifiedVerificationReport</code> dataclass (embedded as the <code>unified_verification_report</code> key of <code>verification_result.json</code>, and written separately as a plain-text operator report at <code>verification_report.txt</code>) instead of only the ad hoc, scattered dict fields built up field-by-field across the runner's branches. One structure always carries, together:</p>
    <ul>
      <li>GMAT version/run identity (<code class="mono">gmat_executable</code>, <code class="mono">gmat_version_banner</code>, <code class="mono">gmat_attempted</code>, <code class="mono">gmat_exit_status</code>);</li>
      <li>compared states, declared units, and configured tolerances (<code class="mono">cw_final_state_m_mps</code>, <code class="mono">gmat_final_state_m_mps</code>, <code class="mono">units</code>, <code class="mono">tolerances</code>);</li>
      <li>measured discrepancies and the <code class="mono">PASS</code>/<code class="mono">WARNING</code>/<code class="mono">FAIL</code>/<code class="mono">INCOMPLETE</code> comparison status; and</li>
      <li>a directly accessible <code class="mono">screenshot</code> artifact reference with an explicit <code class="mono">media_type</code> (<code>image/svg+xml</code> or <code>image/png</code>), <code class="mono">path</code>, <code class="mono">caption</code>, and <code class="mono">case_id</code>/<code class="mono">run_id</code> association, so it is always clear which run this screenshot belongs to.</li>
    </ul>
    <p><strong>The never-a-false-PASS invariant is re-enforced, not merely assumed, at this layer too:</strong> <code class="mono">assemble_verification_report</code> raises <code>ValueError</code> immediately if a caller ever requests <code>verified=True</code> while GMAT was not attempted, exited nonzero, produced no parsed final state, compared as anything other than <code>PASS</code>, or has an invalid screenshot &mdash; so missing numerical output, failed GMAT execution, or a missing/corrupt screenshot can never be threaded through into a false pass at the report-assembly layer either.</p>
    <p><strong>The human-readable report distinguishes solver success from independent GMAT verification (AC4):</strong> <code class="mono">UnifiedVerificationReport.to_human_readable()</code> explicitly separates "the CW solver itself succeeded at computing a candidate" from "GMAT independently verified it," and explains likely discrepancy causes when the evidence supports it &mdash; a bounded <code>WARNING</code>-level tolerance overrun reads as likely ordinary numerical/integrator precision, while a large-margin <code>FAIL</code> reads as more likely a frame/unit/state-ordering mismatch. Example excerpt from a real <code>VERIFIED</code> run:</p>
    ${TC.codeBlock(`SOLVER: The clohessy-wiltshire-linearized-fixed-duration-two-impulse solver SUCCEEDED at computing a candidate solution (status='unique'). Phi_rv is well-conditioned; returned the unique inverse solution.

INDEPENDENT VERIFICATION: GMAT independently verified the candidate solution. Position error 7.941e-03 m and velocity error 1.168e-05 m/s are both within tolerance (position tolerance 1.0 m, velocity tolerance 0.001 m/s). A solver success alone does NOT by itself constitute this independent verification -- this GMAT comparison is what does.`, 0)}

    <h2>Authoritative source mirrors</h2>
    ${TC.authorityBanner('Exact synchronized source mirrors; Python remains authoritative. This browser does not execute it.')}
    <details><summary style="cursor:pointer;color:var(--accent)">src/gmat_verify.py (script generation, execution, parsing, comparison, screenshot validation, real-GUI screenshot attempt)</summary>
      ${TC.codeBlock(verifyModule, 1)}
    </details>
    <details><summary style="cursor:pointer;color:var(--accent)">src/verification_report.py (TJC-1.19 unified report assembly and human-readable rendering)</summary>
      ${TC.codeBlock(reportModule, 1)}
    </details>
    <details><summary style="cursor:pointer;color:var(--accent)">scripts/run_cw_gmat_slice.py (orchestration entry point)</summary>
      ${TC.codeBlock(runner, 1)}
    </details>
    <details><summary style="cursor:pointer;color:var(--accent)">tests/test_cw_gmat_slice.py (failure-mode tests, screenshot-source tests, the real end-to-end GMAT run)</summary>
      ${TC.codeBlock(verifyTests, 1)}
    </details>
    <details><summary style="cursor:pointer;color:var(--accent)">tests/test_verification_report.py (TJC-1.19 unified report assembly/formatting tests)</summary>
      ${TC.codeBlock(reportTests, 1)}
    </details>
  `;
};
