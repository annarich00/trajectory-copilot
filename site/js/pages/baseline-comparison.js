'use strict';

window.TCPages['baseline-comparison'] = async function (root) {
  const [readme, report, respA, respB, respC, respD, wfA, wfB, wfC, wfD] = await Promise.all([
    TC.fetchText('data/evaluations/baseline_comparison/README.md'),
    TC.fetchText('data/evaluations/baseline_comparison/REPORT.md'),
    TC.fetchText('data/evaluations/baseline_comparison/case_a_baseline_llm_response.md'),
    TC.fetchText('data/evaluations/baseline_comparison/case_b_baseline_llm_response.md'),
    TC.fetchText('data/evaluations/baseline_comparison/case_c_baseline_llm_response.md'),
    TC.fetchText('data/evaluations/baseline_comparison/case_d_baseline_llm_response.md'),
    TC.fetchText('data/evaluations/baseline_comparison/case_a_workflow_result.json'),
    TC.fetchText('data/evaluations/baseline_comparison/case_b_workflow_result.json'),
    TC.fetchText('data/evaluations/baseline_comparison/case_c_workflow_result.json'),
    TC.fetchText('data/evaluations/baseline_comparison/case_d_workflow_result.json'),
  ]);
  const results = { a: JSON.parse(wfA), b: JSON.parse(wfB), c: JSON.parse(wfC), d: JSON.parse(wfD) };
  const responses = { a: respA, b: respB, c: respC, d: respD };

  function caseSection(letter, title) {
    const r = results[letter];
    const comparison = r.unified_verification_report ? r.unified_verification_report.comparison : null;
    return `
      <h3>Case (${letter}) — ${TC.esc(title)}</h3>
      <div class="result-grid">
        <div class="result-cell"><div class="label">Workflow outcome</div><div class="value">${TC.esc(r.outcome)}</div></div>
        <div class="result-cell"><div class="label">Verified</div><div class="value">${r.verified}</div></div>
        <div class="result-cell"><div class="label">Selection</div><div class="value">${r.model_selection ? TC.esc(r.model_selection.selection) : 'none (short-circuited)'}</div></div>
        <div class="result-cell"><div class="label">Qualified</div><div class="value">${r.model_selection ? r.model_selection.qualified : 'n/a'}</div></div>
        ${comparison ? `<div class="result-cell"><div class="label">GMAT comparison</div><div class="value">${TC.esc(comparison.status)} (pos err ${comparison.position_error_m} m)</div></div>` : ''}
      </div>
      <details><summary>Direct-LLM baseline response (verbatim, single-shot, no tool access)</summary><pre class="code">${TC.esc(responses[letter])}</pre></details>
      <details><summary>Full workflow result (verbatim <code>WorkflowResult.to_dict()</code>, real GMAT run)</summary><pre class="code">${TC.esc(JSON.stringify(r, null, 2))}</pre></details>
    `;
  }

  root.innerHTML = `
    ${TC.pageHeader('Direct-LLM Baseline vs. Complete Structured Workflow', 'TJC-1.22 — the four-category rendezvous benchmark run through a direct natural-language-to-LLM-answer baseline and the complete structured workflow. Not a claim of universal superiority; scoped to these four cases and this project\\'s narrow rendezvous class.')}

    ${TC.callout('warn', 'Honest methodology disclosure', '<p>This sandboxed environment has no live external LLM API access. The <strong>direct-LLM baseline side was produced by the same model implementing this task</strong>, in the same session, as a single-shot, un-scaffolded direct-answer exercise with no access to this project\\'s formalizer skill, model selector, deterministic solvers, or GMAT. See <code>evaluations/baseline_comparison/README.md</code>/<code>REPORT.md</code> for the full disclosure and why this is a legitimate design choice given this constraint, not a hidden limitation.</p>')}

    ${TC.callout('info', 'Where this lives', '<p>Methodology/report: <code>evaluations/baseline_comparison/README.md</code> / <code>REPORT.md</code>. Baseline responses: <code>case_*_baseline_llm_response.md</code>. Real workflow results (actual <code>src/workflow.py::run_rendezvous_workflow</code> runs, cases a/b/c against a real <code>GmatConsole-R2026a</code> installation): <code>case_*_workflow_result.json</code>, reproducible via <code>evaluations/baseline_comparison/run_workflow_cases.py</code>. Structural checks: <code>tests/test_baseline_comparison.py</code>.</p>')}

    <h2>Per-case results</h2>
    ${caseSection('a', 'straightforward CW')}
    ${caseSection('b', 'boundary CW (singular-but-reachable targeting)')}
    ${caseSection('c', 'CW-invalid / two-body fallback')}
    ${caseSection('d', 'ambiguous / incomplete')}

    <h2>Full report (methodology, scoring, aggregate summary, conclusions)</h2>
    ${TC.authorityBanner('Exact, unmodified mirror of evaluations/baseline_comparison/REPORT.md.')}
    <pre class="code">${TC.esc(report)}</pre>

    <h2>Directory README</h2>
    ${TC.authorityBanner('Exact, unmodified mirror of evaluations/baseline_comparison/README.md.')}
    <pre class="code">${TC.esc(readme)}</pre>

    <p><a href="#/benchmark">See also: Four-Category Rendezvous Benchmark →</a></p>
  `;
};
