/**
 * lib.js — shared DOM/rendering helpers used by every page module.
 * No frameworks; just small utility functions.
 */
'use strict';

// Must exist before any js/pages/*.js module runs, since each page module
// assigns window.TCPages[route] = ... at load time (not inside a callback).
window.TCPages = window.TCPages || {};

const TC = (function () {
  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function el(html) {
    const t = document.createElement('template');
    t.innerHTML = html.trim();
    return t.content.firstChild;
  }

  async function fetchText(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error('Failed to fetch ' + path + ': ' + res.status);
    return await res.text();
  }

  function badge(kind, label) {
    const map = {
      tested: 'badge-tested',
      partial: 'badge-partial',
      planned: 'badge-planned',
      llm: 'badge-llm',
      det: 'badge-det',
      ver: 'badge-ver',
    };
    const cls = map[kind] || 'badge-tested';
    return `<span class="badge ${cls}">${esc(label)}</span>`;
  }

  // Render a code snippet with line numbers starting at `startLine`.
  // `highlightLines` optional array of absolute line numbers to emphasize (not implemented visually beyond bold).
  function codeBlock(code, startLine = 1) {
    const lines = code.split('\n');
    const rows = lines
      .map((line, i) => {
        const n = startLine + i;
        return `<span class="ln">${n}</span>${esc(line)}`;
      })
      .join('\n');
    return `<pre class="code">${rows}</pre>`;
  }

  function codeRef(file, fnName) {
    return `<div class="code-ref">Source: <code>${esc(file)}</code>${fnName ? ' — function <code>' + esc(fnName) + '()</code>' : ''}</div>`;
  }

  // Label for any number computed by site/js/physics.js in the browser.
  // ALWAYS use this (or mirrorBanner) around interactive/live results so the
  // reader cannot mistake a browser computation for a Python/pytest result.
  // `fnName` should name the exact Python function in src/*.py that the
  // browser code hand-ports (e.g. "cw.py :: two_burn_targeting").
  function mirrorTag(fnName) {
    return `<span class="mirror-tag" title="Computed in-browser by a hand-ported JS copy of this Python function. Not pytest output; not an independent verification.">PEDAGOGICAL BROWSER MIRROR of <code>${esc(fnName)}</code></span>`;
  }

  // A banner to place above any interactive panel that computes numbers in
  // JS. Explains clearly that this is not the authoritative Python result.
  function mirrorBanner(fnNames) {
    const list = Array.isArray(fnNames) ? fnNames : [fnNames];
    const items = list.map((f) => `<code>${esc(f)}</code>`).join(', ');
    return `<div class="mirror-banner">
      <strong>Pedagogical browser mirror.</strong> The numbers below are computed live in
      JavaScript (<code>site/js/physics.js</code>), hand-ported from ${items} in this
      repository's Python source. This is for interactive illustration only — it is
      <strong>not</strong> the authoritative implementation, and it is <strong>not</strong> an
      independent verification of the Python. The authoritative result comes only from running
      the actual Python code / <code>pytest</code> against <code>tests/</code>.
    </div>`;
  }

  // Extract a named top-level function/class body (by simple text search)
  // from already-fetched Python source text. Best-effort line-based slicer:
  // finds "def name(" or "class name" at col 0, and includes lines until the
  // next column-0 "def "/"class " or EOF.
  function extractPySymbol(src, name) {
    const lines = src.split('\n');
    const startRe = new RegExp(`^(def|class)\\s+${name}\\b`);
    let start = -1;
    for (let i = 0; i < lines.length; i++) {
      if (startRe.test(lines[i])) { start = i; break; }
    }
    if (start === -1) return null;
    let end = lines.length;
    for (let i = start + 1; i < lines.length; i++) {
      if (/^(def|class)\s+/.test(lines[i])) { end = i; break; }
    }
    // trim trailing blank lines
    while (end > start + 1 && lines[end - 1].trim() === '') end--;
    return { code: lines.slice(start, end).join('\n'), startLine: start + 1 };
  }

  function fmt(x, digits = 6) {
    if (!isFinite(x)) return String(x);
    if (Math.abs(x) >= 1e5 || (Math.abs(x) < 1e-4 && x !== 0)) {
      return x.toExponential(Math.max(0, digits - 2));
    }
    return x.toFixed(Math.max(0, digits));
  }

  function vecStr(v, digits = 5) {
    return '[' + v.map((x) => fmt(x, digits)).join(', ') + ']';
  }

  function mat3Str(M, digits = 5) {
    return M.map((row) => '  [' + row.map((x) => fmt(x, digits)).join(', ') + ']').join('\n');
  }

  function pageHeader(title, subtitle) {
    return `<h1 class="page-title">${esc(title)}</h1><p class="page-subtitle">${subtitle}</p>`;
  }

  function callout(kind, title, bodyHtml) {
    return `<div class="callout ${kind}"><div class="callout-title">${esc(title)}</div>${bodyHtml}</div>`;
  }

  // Banner marking a block of displayed code/output as the authoritative
  // Python source or actual pytest file content (as opposed to the browser
  // mirror). Use directly above verbatim source/test excerpts.
  function authorityBanner(label) {
    return `<div class="authority-banner"><strong>Authoritative source.</strong> ${esc(label)}</div>`;
  }

  function teachingContract({ assumptions, symbols, mapping, evidence, limitations }) {
    return `<section class="teaching-contract">
      <h2>Teaching contract</h2>
      <div class="grid-2">
        <div class="panel"><div class="panel-title">Assumptions & conventions</div><p>${assumptions}</p></div>
        <div class="panel"><div class="panel-title">Symbol definitions</div><p>${symbols}</p></div>
        <div class="panel"><div class="panel-title">Exact source mapping</div><p>${mapping}</p><p><a href="data/reference/SOURCE.md">Verbatim reference/SOURCE.md</a> · <a href="#/source-explorer">deterministic Python mirrors</a></p></div>
        <div class="panel"><div class="panel-title">Tests & evidence</div><p>${evidence}</p></div>
      </div>
      <div class="callout warn"><div class="callout-title">Limitations / audit boundary</div><p>${limitations}</p></div>
    </section>`;
  }

  // simple debounce
  function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  }

  return { esc, el, fetchText, badge, codeBlock, codeRef, mirrorTag, mirrorBanner, authorityBanner, teachingContract, extractPySymbol, fmt, vecStr, mat3Str, pageHeader, callout, debounce };
})();
