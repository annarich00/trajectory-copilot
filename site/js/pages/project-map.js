'use strict';

window.TCPages['project-map'] = async function (root) {
  root.innerHTML = `
    ${TC.pageHeader('Project Map & Roadmap', 'Delivery order for the narrow semester workflow; status details live on the progress page.')}
    <div class="roadmap">
      <div class="roadmap-col"><h4>1 · PRESERVE</h4><div class="roadmap-item">Recovered baseline and dependency-free educational site: complete (TJC-1.26, TJC-1.24, TJC-1.25).</div></div>
      <div class="roadmap-col"><h4>2 · PROVE</h4><div class="roadmap-item">Single CW-to-GMAT vertical slice with numerical comparison and returned screenshot: planned, not working yet (TJC-1.20).</div></div>
      <div class="roadmap-col"><h4>3 · HARDEN</h4><div class="roadmap-item">GMAT execution/report contract, then reference, formalization, model selection (complete, TJC-1.14), CW, two-body, frame transformations, and a pinned Poliastro implementation cross-check (TJC-1.21, 1.2–1.7, 1.12).</div></div>
      <div class="roadmap-col"><h4>4 · INTEGRATE & EVALUATE</h4><div class="roadmap-item">Reconnect the supported workflow, run four-category benchmark and direct-LLM comparison, publish reproducible scoped findings.</div></div>
    </div>
    <h2>Required end-to-end artifact flow</h2>
    <div class="chain"><div class="node">Natural language</div><div class="arr">↓</div><div class="node">Structured problem</div><div class="arr">↓</div><div class="node">Assumption-based CW assessment (TJC-1.14)</div><div class="arr">↓</div><div class="node">Deterministic CW or bounded two-body fallback</div><div class="arr">↓</div><div class="node">Pinned Poliastro cross-check when like-for-like support exists</div><div class="arr">↓</div><div class="node">GMAT numerical comparison + trajectory screenshot</div><div class="arr">↓</div><div class="node">Explanation</div></div>
    <h2>Not on the semester roadmap</h2>
    <p>Optimization/Pareto fronts, learned CW-validity boundaries, broad validity sweeps, CR3BP, cislunar or generalized mission planning, and broad high-fidelity dynamics are deferred/excluded. Existing <code>src/optimization.py</code> is preserved historical baseline code, not a promise to connect a solver.</p>
    ${TC.callout('warn', 'Current gap', '<p>GMAT has not yet been integrated. The pinned Poliastro adapter is also planned, not implemented. Current internal two-body comparison code substitutes for neither external cross-check nor the required GMAT numerical-plus-screenshot contract.</p>')}
    ${TC.callout('info', 'Poliastro boundary', '<p>Architecture is pinned to archived Poliastro 0.17.0 at commit <code>c7d12e9…</code> in an isolated Python 3.10 environment. It will verify like-for-like supported models; unsupported future dynamics must name another verifier. <a href="data/docs/poliastro-verification-architecture.md">Read the contract →</a></p>')}
    <p><a href="#/progress">Open task-by-task progress and evidence →</a></p>
  `;
};
