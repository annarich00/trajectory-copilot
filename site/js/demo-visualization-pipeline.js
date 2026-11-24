(function () {
  const demos = window.TCDemoRuns;
  const params = new URLSearchParams(location.search);
  const DELAY_MS = Math.max(0, Number(params.get('delay')) || 2500);
  const TYPING_DELAY_MS = Math.max(0, Number(params.get('typingDelay')) || 20);

  // Let the page point at any run directory, not only the three fixed demo
  // slots: ?case=<case_id> tries artifacts/runs/<case_id> then
  // artifacts/runs/<case_id>/bridge (the gmat_tool_bridge.py default), and
  // ?runDir=<path> points at an exact directory. Either adds a "Custom run"
  // option and selects it immediately.
  const caseParam = params.get('case');
  const runDirParam = params.get('runDir');
  if (runDirParam || caseParam) {
    const runDirs = runDirParam
      ? [runDirParam]
      : [`artifacts/runs/${caseParam}`, `artifacts/runs/${caseParam}/bridge`];
    demos.custom = {
      id: 'custom',
      label: params.get('label') || caseParam || 'Custom run',
      runDirs,
      recordedLabel: 'Live run',
    };
  }

  const el = (id) => document.getElementById(id);
  const demoSelect = el('demo-select');
  const playBtn = el('play-pause');
  const nextBtn = el('next-step');
  const allBtn = el('show-all');
  const restartBtn = el('restart');
  const log = el('chat-log');
  const meta = el('run-meta');

  if (demos.custom && demoSelect && !demoSelect.querySelector('option[value="custom"]')) {
    const option = document.createElement('option');
    option.value = 'custom';
    option.textContent = demos.custom.label;
    demoSelect.appendChild(option);
  }

  let current = demos.custom ? 'custom' : 'demoA';
  if (demoSelect) demoSelect.value = current;
  let shown = 0;
  let playing = false;
  let typedRequestLength = 0;
  let timer = null;
  let finalShown = false;
  let currentRun = null;

  function esc(text) {
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function displayRequest(request) {
    return String(request).replace(/^\/rendezvous\b\s*/i, '');
  }

  function requestText(run, demo) {
    return displayRequest(run?.request || demo.run?.request || demo.request || `Load ${demo.label} from its saved run artifacts.`);
  }

  function userMessage(request) {
    return `<div class="msg user"><div class="who">Operator request</div><p>${esc(request)}</p></div>`;
  }

  const STEP_SOURCE_LABELS = Object.freeze({
    formalize_rendezvous_problem: 'SKILL: RENDEZVOUS PIPELINE ORCHESTRATOR · TOOL: ORBITAL PROBLEM FORMALIZER',
    select_rendezvous_model: 'TOOL: ORBITAL MODEL SELECTOR',
    relative_position_3d_scene: 'SKILL: RENDEZVOUS PIPELINE ORCHESTRATOR · ARTIFACT: 3D RELATIVE-POSITION SCENE',
    solve_cw_rendezvous: 'TOOL: CW RENDEZVOUS TARGETING',
    trajectory_burns_plot: 'SKILL: RENDEZVOUS PIPELINE ORCHESTRATOR · ARTIFACT: TRAJECTORY AND BURNS PLOT',
    run_gmat_verification: 'TOOL: GMAT VERIFICATION',
    verification_comparison_plot: 'SKILL: RENDEZVOUS PIPELINE ORCHESTRATOR · ARTIFACT: CW-TO-GMAT COMPARISON PLOT',
  });

  function stepSourceLabel(stepName) {
    return STEP_SOURCE_LABELS[stepName] || 'AGENT';
  }

  function isImageArtifact(artifact) {
    return artifact && artifact.media_type && artifact.media_type.startsWith('image/');
  }

  function imageMarkup(artifact) {
    const scopeNote = artifact.scope_note
      ? `<p class="artifact-scope-note">${esc(artifact.scope_note)}</p>`
      : '';
    return `<img class="artifact-img" alt="${esc(artifact.name || artifact.path)}" src="${esc(artifact.path)}" style="max-width:100%;height:auto" />
      ${scopeNote}
      <p class="artifact-missing warn" hidden>Artifact file not available to this page: ${esc(artifact.path)}. The recorded status is unchanged and no substitute image is shown.</p>`;
  }

  function artifactUrl(artifact) {
    const path = artifact.path || '';
    if (!path.startsWith('artifacts/')) return path;
    if (location.protocol === 'file:') return `../${path}`;
    const repositoryBase = location.pathname.split('/').filter(Boolean)[0];
    return repositoryBase ? `/${repositoryBase}/${path}` : `/${path}`;
  }

  function artifactFrameMarkup(artifact) {
    const path = artifactUrl(artifact);
    return `<iframe class="artifact-frame" title="${esc(artifact.name || 'Recorded visualization artifact')}" src="${esc(path)}" sandbox="allow-scripts allow-same-origin"></iframe>
      <p class="artifact-open-link"><a href="${esc(path)}" target="_blank" rel="noopener">Open this 3D scene in a new tab</a></p>
      <p class="artifact-missing warn" hidden>Artifact file not available to this page: ${esc(artifact.path)}. The recorded status is unchanged and no substitute visualization is shown.</p>`;
  }

  function artifactMarkup(artifact) {
    if (!artifact) return '';
    if (artifact.media_type === 'text/html') return artifactFrameMarkup(artifact);
    const details = [`<p><strong>Artifact:</strong> <code>${esc(artifact.path || artifact.name)}</code></p>`];
    if (isImageArtifact(artifact)) details.push(imageMarkup(artifact));
    return details.join('');
  }

  function developerImageMessage(step, index) {
    const artifacts = step.artifacts || (step.artifact ? [step.artifact] : []);
    return `<div class="msg agent developer-image" data-index="${index}">
      ${artifacts.filter(isImageArtifact).map(imageMarkup).join('')}
    </div>`;
  }

  function stepMessage(step, index, open) {
    const artifacts = step.artifacts || (step.artifact ? [step.artifact] : []);
    if (artifacts.some(isImageArtifact)) return developerImageMessage(step, index);
    const body = step.developer || step.operator || '';
    let details = '';
    if (step.artifacts && step.artifacts.length) {
      details += step.artifacts.map(artifactMarkup).join('');
    } else if (step.artifact) {
      details += artifactMarkup(step.artifact);
    }
    if (step.result) details += `<pre>${esc(JSON.stringify(step.result, null, 2))}</pre>`;
    if (step.raw) details += `<p><strong>Raw events:</strong> ${esc(step.raw.join(', '))}</p>`;
    if (!details) details = '<p class="muted">No further details were recorded for this step.</p>';
    const cls = `msg agent step ${esc(step.status)}${open ? ' open' : ''}`;
    return `<div class="${cls}" data-index="${index}" role="button" tabindex="0" aria-expanded="${open ? 'true' : 'false'}">
      <div class="who">${esc(stepSourceLabel(step.name))}</div>
      <h3>${esc(step.title || step.name)}</h3>
      <p><span class="status">${esc(step.status)}</span>${esc(body)}</p>
      <div class="details">${details}</div>
      <div class="hint">Click to ${open ? 'hide' : 'show'} details</div>
    </div>`;
  }

  function finalMessage(demo) {
    const stop = demo.stop ? `<p><span class="warn">${esc(demo.stop.state)}</span> — ${esc(demo.stop.reason)}</p>` : '';
    return `<div class="msg agent final"><div class="who">SKILL: RENDEZVOUS PIPELINE ORCHESTRATOR · RECORDED RUN SUMMARY</div><h3>Result</h3>
      <p><strong>${esc(demo.label)}</strong> finishes with <strong>${esc(demo.recordedOutcome)}</strong>. Verification: <strong>${esc(demo.verificationStatus)}</strong>.</p>${stop}</div>`;
  }

  function relaxedToleranceFollowUpMessage(text) {
    return `<section class="msg agent final"><div class="who">TOOL: GMAT VERIFICATION · RECORDED FOLLOW-UP</div><h3>Relaxed-tolerance GMAT check</h3><p>${esc(text)}</p></section>`;
  }

  function formatCalculationNumber(value) {
    if (!Number.isFinite(value)) return 'not recorded';
    const magnitude = Math.abs(value);
    if (magnitude && (magnitude < 0.0001 || magnitude >= 1e6)) return value.toExponential(3);
    return value.toFixed(6).replace(/\.0+$|(?<=\.[0-9]*?)0+$/, '');
  }

  function formatDeltaV(vector) {
    if (!Array.isArray(vector) || vector.length !== 3) return 'not recorded';
    return `[${vector.map(formatCalculationNumber).join(', ')}] m/s`;
  }

  function calculationTableMessage(run) {
    const steps = run.steps || [];
    const solve = steps.find((step) => step.name === 'solve_cw_rendezvous');
    const gmat = steps.find((step) => step.name === 'run_gmat_verification');
    if (!solve?.result || !gmat?.result) {
      const reason = solve?.reason || gmat?.reason || 'No deterministic solve and GMAT verification were recorded.';
      return `<section class="msg agent calculations"><div class="who">TOOL: CW RENDEZVOUS TARGETING · TOOL: GMAT VERIFICATION</div>
        <h3>Recorded calculations</h3><p class="muted">Not available for this demo: ${esc(reason)}</p></section>`;
    }
    const comparison = gmat.result.comparison || {};
    const rows = [
      ['Targeting status', solve.result.targeting_status],
      ['Transfer time', `${formatCalculationNumber(solve.result.transfer_time_s)} s`],
      ['Burn 1 Δv [radial, along-track, cross-track]', formatDeltaV(solve.result.dv0_mps)],
      ['Burn 2 Δv [radial, along-track, cross-track]', formatDeltaV(solve.result.dv1_mps)],
      ['Total Δv', `${formatCalculationNumber(solve.result.total_delta_v_mps)} m/s`],
      ['Targeting-matrix rank', formatCalculationNumber(solve.result.rank)],
      ['Targeting-matrix condition number', formatCalculationNumber(solve.result.condition_number)],
      ['GMAT comparison status', `${comparison.status || 'not recorded'}${gmat.result.failure_mode ? ` / ${gmat.result.failure_mode}` : ''}`],
      ['GMAT position error', `${formatCalculationNumber(comparison.position_error_m)} m`],
      ['GMAT velocity error', `${formatCalculationNumber(comparison.velocity_error_mps)} m/s`],
    ];
    const body = rows.map(([metric, value]) => `<tr><th scope="row">${esc(metric)}</th><td>${esc(value)}</td></tr>`).join('');
    return `<section class="msg agent calculations"><div class="who">TOOL: CW RENDEZVOUS TARGETING · TOOL: GMAT VERIFICATION</div>
      <h3>Recorded calculations</h3><div class="calculation-table-wrap"><table><tbody>${body}</tbody></table></div></section>`;
  }

  const opened = new Set();

  function loadRun(demo) {
    if (demo.run) return Promise.resolve({ run: demo.run, sourceDir: null });
    const dirs = demo.runDirs || (demo.runDir ? [demo.runDir] : []);
    if (!dirs.length) return Promise.resolve(null);
    return dirs.reduce(
      (chain, dir) => chain.catch(() => fetchRunFromDir(dir).then((run) => ({ run, sourceDir: dir }))),
      Promise.reject(new Error('no run directories configured')),
    );
  }

  function fetchRunFromDir(dir) {
    return fetch(`${dir}/run_summary.json`)
      .then((response) => {
        if (!response.ok) throw new Error(`Unable to load ${dir}/run_summary.json`);
        return response.json();
      })
      .catch(() => fetch(`${dir}/run_manifest.json`).then((response) => {
        if (!response.ok) throw new Error(`Unable to load ${dir}/run_manifest.json`);
        return response.json();
      }));
  }

  function normalizeRun(demo, loaded) {
    const run = loaded && loaded.run ? loaded.run : loaded;
    const sourceDir = (loaded && loaded.sourceDir) || demo.runDir || (demo.runDirs && demo.runDirs[0]) || null;
    const manifest = run && run.manifest ? run.manifest : run;
    const summary = run && run.summary ? run.summary : run;
    const steps = (summary && summary.steps) || (manifest && manifest.steps) || [];
    return {
      label: demo.label,
      recordedOutcome: summary?.outcome || manifest?.outcome || demo.recordedOutcome || 'UNKNOWN',
      verificationStatus: summary?.verification_status || manifest?.verification_status || demo.verificationStatus || 'UNKNOWN',
      expected: summary?.expected || manifest?.expected || demo.expected || null,
      request: summary?.request || manifest?.request || demo.request || '',
      steps,
      stop: summary?.stop || manifest?.stop || demo.stop || null,
      relaxedToleranceFollowUp: summary?.relaxed_tolerance_follow_up || manifest?.relaxed_tolerance_follow_up || null,
      sourceDir,
    };
  }

  function metaText(run, demo) {
    const dirNote = run.sourceDir ? ` · reading from ${run.sourceDir}` : '';
    // A recorded run stores what happened, not what was expected, so the
    // expected-outcome note is only shown when the run actually carries one.
    const expectedNote = run.expected ? ` · expected ${run.expected}` : '';
    const request = requestText(run, demo);
    const progress = typedRequestLength < request.length
      ? ' · request typing'
      : ` · step ${Math.min(shown, run.steps.length)} of ${run.steps.length}`;
    return `${demo.label}${expectedNote} · recorded ${run.recordedOutcome}${progress}${dirNote}`;
  }

  function render(scroll) {
    const demo = demos[current];
    const run = currentRun || { request: demo.request, expected: demo.expected, recordedOutcome: demo.recordedOutcome, verificationStatus: demo.verificationStatus, steps: demo.steps || [], stop: demo.stop || null };
    const request = requestText(run, demo);
    const requestIsComplete = typedRequestLength >= request.length;
    const parts = [];
    if (typedRequestLength > 0) parts.push(userMessage(request.slice(0, typedRequestLength)));
    if (requestIsComplete) run.steps.slice(0, shown).forEach((step, index) => {
      parts.push(stepMessage(step, index, opened.has(index)));
      if (step.name === 'run_gmat_verification') parts.push(calculationTableMessage(run));
    });
    if (requestIsComplete && shown >= run.steps.length) {
      parts.push(finalMessage({ ...demo, ...run }));
      if (run.relaxedToleranceFollowUp) parts.push(relaxedToleranceFollowUpMessage(run.relaxedToleranceFollowUp));
      finalShown = true;
    } else { finalShown = false; }
    log.innerHTML = parts.join('');
    meta.textContent = metaText(run, demo);
    playBtn.textContent = playing && !finalShown ? 'Pause' : 'Play';
    nextBtn.disabled = finalShown;
    if (scroll) { const last = log.lastElementChild; if (last && last.scrollIntoView) last.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
  }

  function stop() { if (timer) { clearTimeout(timer); timer = null; } }

  function schedule() {
    stop();
    const run = currentRun || demos[current];
    const request = requestText(run, demos[current]);
    if (!playing) return;
    if (typedRequestLength < request.length) {
      timer = setTimeout(() => {
        typedRequestLength += 1;
        render(false);
        if (typedRequestLength >= request.length) { reveal(1); schedule(); } else schedule();
      }, TYPING_DELAY_MS);
      return;
    }
    if (shown >= run.steps.length) return;
    timer = setTimeout(() => { reveal(1); schedule(); }, DELAY_MS);
  }

  function reveal(count) {
    const run = currentRun || demos[current];
    shown = Math.min(run.steps.length, shown + count);
    render(true);
  }

  function restart(keepPlaying) {
    stop();
    shown = 0;
    typedRequestLength = 0;
    opened.clear();
    playing = keepPlaying === true;
    currentRun = null;
    loadRun(demos[current]).then((run) => {
      currentRun = normalizeRun(demos[current], run || {});
      render(false);
      schedule();
    }).catch(() => {
      currentRun = normalizeRun(demos[current], {});
      render(false);
      schedule();
    });
  }

  log.addEventListener('click', (event) => {
    const msg = event.target.closest('.step');
    if (!msg) return;
    toggle(msg);
  });
  log.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const msg = event.target.closest('.step');
    if (!msg) return;
    event.preventDefault();
    toggle(msg);
  });
  function toggle(msg) {
    const i = Number(msg.dataset.index);
    if (opened.has(i)) opened.delete(i); else opened.add(i);
    render(false);
  }

  log.addEventListener('error', (event) => {
    const artifact = event.target;
    if (artifact && artifact.classList && (artifact.classList.contains('artifact-img') || artifact.classList.contains('artifact-frame'))) {
      artifact.hidden = true;
      const note = artifact.nextElementSibling;
      if (note) note.hidden = false;
    }
  }, true);

  demoSelect.addEventListener('change', () => { current = demoSelect.value; restart(false); });
  playBtn.addEventListener('click', () => {
    const run = currentRun || demos[current];
    const request = requestText(run, demos[current]);
    if (typedRequestLength >= request.length && shown >= run.steps.length) { restart(true); return; }
    playing = !playing;
    if (playing) schedule(); else stop();
    render(false);
  });
  nextBtn.addEventListener('click', () => {
    const run = currentRun || demos[current];
    const request = requestText(run, demos[current]);
    playing = false;
    stop();
    if (typedRequestLength < request.length) { typedRequestLength = request.length; render(false); return; }
    reveal(1);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowRight' || event.altKey || event.ctrlKey || event.metaKey) return;
    const target = event.target;
    if (target?.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(target?.tagName)) return;
    if (!nextBtn.disabled) { event.preventDefault(); nextBtn.click(); }
  });
  allBtn.addEventListener('click', () => {
    const run = currentRun || demos[current];
    playing = false;
    stop();
    typedRequestLength = requestText(run, demos[current]).length;
    reveal(run.steps.length);
  });
  restartBtn.addEventListener('click', () => restart(false));

  restart(false);
})();
