'use strict';

window.TCPages.research = async function (root) {
  const baseline = await TC.fetchText('data/baseline_comparison.md');
  root.innerHTML = `
    ${TC.pageHeader('Research Connection', 'The approved question is evaluated only in the supported rendezvous regime and against explicit evidence.')}
    <div class="callout"><div class="callout-title">Research question</div><p><em>Can separating rendezvous formulation, model selection, deterministic computation, and independent GMAT verification improve reliability and transparency of LLM-generated rendezvous solutions?</em></p></div>
    <h2>Experiment contract</h2>
    <ol>
      <li>Benchmark straightforward CW cases.</li>
      <li>Include boundary cases without claiming a learned universal threshold.</li>
      <li>Include CW-invalid cases routed to the bounded two-body path.</li>
      <li>Include ambiguous/incomplete requests that require clarification.</li>
    </ol>
    <p>Compare the complete structured workflow with a direct natural-language-to-answer baseline. Evaluate formulation, ambiguity detection, model choice, numerical agreement, GMAT invocation, discrepancy handling, screenshot availability, and explanation quality.</p>
    ${TC.callout('warn', 'Evidence status', '<p>The recovered three formalizer transcripts are useful historical evidence, but they are not the final four-category benchmark and do not demonstrate GMAT integration. The complete experiment is planned in TJC-1.9, TJC-1.22, and TJC-1.23.</p>')}
    <h2>Why numerical + visual verification matters</h2>
    <p>A solver result is not authoritative merely because it is deterministic. The scoped contract requires GMAT execution evidence, tolerance-based numerical comparison, and a non-empty returned orbit/trajectory screenshot. Failures and disagreements remain distinguishable and cannot be reported as PASS.</p>
    <h2>Excluded hypotheses</h2>
    <p>This semester does not study generalized optimization, Pareto reasoning, learned validity boundaries, CR3BP/cislunar planning, or general astrodynamics question answering. Older source material may mention those directions; they are deferred historical context, not roadmap commitments.</p>
    <h2>Historical baseline document</h2>
    <details><summary>Show baseline_comparison.md verbatim</summary>${TC.authorityBanner('Verbatim historical repository document; its “next experiment” is not the approved semester roadmap.')}<pre class="code">${TC.esc(baseline)}</pre></details>
    <p><a href="#/project-map">Continue to the scoped project map →</a></p>
  `;
};
