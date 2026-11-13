(function () {
  const demos = window.TCDemoRuns;
  const params = new URLSearchParams(location.search);
  const DELAY_MS = Math.max(0, Number(params.get('delay')) || 1500);

  const el = (id) => document.getElementById(id);
  const demoSelect = el('demo-select');
  const operatorBtn = el('mode-operator');
  const developerBtn = el('mode-developer');
  const playBtn = el('play-pause');
  const nextBtn = el('next-step');
  const allBtn = el('show-all');
  const restartBtn = el('restart');
  const log = el('chat-log');
  const meta = el('run-meta');

  let current = 'demoA';
  let mode = 'operator';
  let shown = 0;
  let playing = true;
  let timer = null;
  let finalShown = false;
  let currentRun = null;

  function esc(text) {
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function userMessage(demo) {
    const request = demo.run?.request || demo.request || `Load ${demo.label} from its saved run artifacts.`;
    return `<div class="msg user"><div class="who">Operator request</div><p>${esc(request)}</p></div>`;
  }

  function artifactMarkup(artifact) {
    if (!artifact) return '';
    const details = [`<p><strong>Artifact:</strong> <code>${esc(artifact.path || artifact.name)}</code></p>`];
    if (artifact.media_type && artifact.media_type.startsWith('image/')) {
      details.push(
        `<img class="artifact-img" alt="${esc(artifact.name || artifact.path)}" src="${esc(artifact.path)}" style="max-width:100%;height:auto" />`,
        `<p class="artifact-missing warn" hidden>Artifact file not available to this page: ${esc(artifact.path)}. The recorded status is unchanged and no substitute image is shown.</p>`
      );
    }
    return details.join('');
  }

  function stepMessage(step, index, open) {
    const body = mode === 'developer' ? (step.developer || step.operator || '') : (step.operator || step.developer || '');
    const reason = step.reason ? `<p><strong>Reason:</strong> ${esc(step.reason)}</p>` : '';
    let details = '';
    if (step.artifacts && step.artifacts.length) {
      details += step.artifacts.map(artifactMarkup).join('');
    } else if (step.artifact) {
      details += artifactMarkup(step.artifact);
    }
    if (mode === 'developer') {
      if (step.result) details += `<pre>${esc(JSON.stringify(step.result, null, 2))}</pre>`;
      if (step.raw) details += `<p><strong>Raw events:</strong> ${esc(step.raw.join(', '))}</p>`;
    }
    if (!details) details = '<p class="muted">No further details were recorded for this step.</p>';
    const cls = `msg agent step ${esc(step.status)}${open ? ' open' : ''}`;
    return `<div class="${cls}" data-index="${index}" role="button" tabindex="0" aria-expanded="${open ? 'true' : 'false'}">
      <div class="who">Agent</div>
      <h3>${esc(step.title || step.name)}</h3>
      <p><span class="status">${esc(step.status)}</span>${esc(body)}</p>
      ${reason}
      <div class="details">${details}</div>
      <div class="hint">Click to ${open ? 'hide' : 'show'} details</div>
    </div>`;
  }

  function finalMessage(demo) {
    const stop = demo.stop ? `<p><span class="warn">${esc(demo.stop.state)}</span> — ${esc(demo.stop.reason)}</p>` : '';
    return `<div class="msg agent final"><div class="who">Agent</div><h3>Result</h3>
      <p><strong>${esc(demo.label)}</strong> finishes with <strong>${esc(demo.recordedOutcome)}</strong>. Verification: <strong>${esc(demo.verificationStatus)}</strong>.</p>${stop}</div>`;
  }

  const opened = new Set();

  function loadRun(demo) {
    if (demo.run) return Promise.resolve(demo.run);
    if (!demo.runDir) return Promise.resolve(null);
    return fetch(`${demo.runDir}/run_summary.json`)
      .then((response) => {
        if (!response.ok) throw new Error(`Unable to load ${demo.runDir}/run_summary.json`);
        return response.json();
      })
      .catch(() => fetch(`${demo.runDir}/run_manifest.json`).then((response) => {
        if (!response.ok) throw new Error(`Unable to load ${demo.runDir}/run_manifest.json`);
        return response.json();
      }));
  }

  function normalizeRun(demo, run) {
    const manifest = run && run.manifest ? run.manifest : run;
    const summary = run && run.summary ? run.summary : run;
    const steps = (summary && summary.steps) || (manifest && manifest.steps) || [];
    return {
      label: demo.label,
      recordedOutcome: summary?.outcome || manifest?.outcome || demo.recordedOutcome || 'UNKNOWN',
      verificationStatus: summary?.verification_status || manifest?.verification_status || demo.verificationStatus || 'UNKNOWN',
      expected: summary?.expected || manifest?.expected || demo.expected || 'UNKNOWN',
      request: summary?.request || manifest?.request || demo.request || '',
      steps,
      stop: summary?.stop || manifest?.stop || demo.stop || null,
    };
  }

  function metaText(run, demo) {
    return `${demo.label} · expected ${run.expected} · recorded ${run.recordedOutcome} · step ${Math.min(shown, run.steps.length)} of ${run.steps.length} · mode: ${mode}`;
  }

  function render(scroll) {
    const demo = demos[current];
    const run = currentRun || { request: demo.request, expected: demo.expected, recordedOutcome: demo.recordedOutcome, verificationStatus: demo.verificationStatus, steps: demo.steps || [], stop: demo.stop || null };
    const parts = [userMessage({ ...demo, ...run })];
    run.steps.slice(0, shown).forEach((s, i) => parts.push(stepMessage(s, i, opened.has(i))));
    if (shown >= run.steps.length) { parts.push(finalMessage({ ...demo, ...run })); finalShown = true; } else { finalShown = false; }
    log.innerHTML = parts.join('');
    meta.textContent = metaText(run, demo);
    operatorBtn.classList.toggle('active', mode === 'operator');
    developerBtn.classList.toggle('active', mode === 'developer');
    playBtn.textContent = playing && !finalShown ? 'Pause' : 'Play';
    nextBtn.disabled = finalShown;
    if (scroll) { const last = log.lastElementChild; if (last && last.scrollIntoView) last.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
  }

  function stop() { if (timer) { clearTimeout(timer); timer = null; } }

  function schedule() {
    stop();
    const run = currentRun || demos[current];
    if (!playing || shown >= run.steps.length) return;
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
    opened.clear();
    playing = keepPlaying !== false;
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
    const img = event.target;
    if (img && img.classList && img.classList.contains('artifact-img')) {
      img.hidden = true;
      const note = img.nextElementSibling;
      if (note) note.hidden = false;
    }
  }, true);

  demoSelect.addEventListener('change', () => { current = demoSelect.value; restart(true); });
  operatorBtn.addEventListener('click', () => { mode = 'operator'; render(false); });
  developerBtn.addEventListener('click', () => { mode = 'developer'; render(false); });
  playBtn.addEventListener('click', () => {
    const run = currentRun || demos[current];
    if (shown >= run.steps.length) { restart(true); return; }
    playing = !playing;
    if (playing) schedule(); else stop();
    render(false);
  });
  nextBtn.addEventListener('click', () => { playing = false; stop(); reveal(1); });
  allBtn.addEventListener('click', () => { playing = false; stop(); reveal((currentRun || demos[current]).steps.length); });
  restartBtn.addEventListener('click', () => restart(true));

  restart(true);
})();
