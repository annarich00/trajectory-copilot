'use strict';

window.TCPages['project-map'] = async function (root) {
  root.innerHTML = `
    ${TC.pageHeader('Project Map & Roadmap', 'Delivery order for the narrow semester workflow; status details live on the progress page.')}
    <div class="roadmap">
      <div class="roadmap-col"><h4>1 · PRESERVE</h4><div class="roadmap-item">Recovered baseline and dependency-free educational site: complete (TJC-1.26, TJC-1.24, TJC-1.25).</div></div>
      <div class="roadmap-col"><h4>2 · PROVE</h4><div class="roadmap-item">Single CW-to-GMAT vertical slice with numerical comparison and returned screenshot: planned, not working yet (TJC-1.20).</div></div>
      <div class="roadmap-col"><h4>3 · HARDEN</h4><div class="roadmap-item">GMAT execution/report contract, then reference, formalization, model selection, CW, two-body, and frame transformations (TJC-1.21, 1.2–1.6, 1.12, 1.14).</div></div>
      <div class="roadmap-col"><h4>4 · INTEGRATE & EVALUATE</h4><div class="roadmap-item">Reconnect the supported workflow, run four-category benchmark and direct-LLM comparison, publish reproducible scoped findings.</div></div>
    </div>
    <h2>Required end-to-end artifact flow</h2>
    <div class="chain"><div class="node">Natural language</div><div class="arr">↓</div><div class="node">Structured problem</div><div class="arr">↓</div><div class="node">Assumption-based CW assessment</div><div class="arr">↓</div><div class="node">Deterministic CW or bounded two-body fallback</div><div class="arr">↓</div><div class="node">GMAT numerical comparison + trajectory screenshot</div><div class="arr">↓</div><div class="node">Explanation</div></div>
    <h2>Not on the semester roadmap</h2>
    <p>Optimization/Pareto fronts, learned CW-validity boundaries, broad validity sweeps, CR3BP, cislunar or generalized mission planning, and broad high-fidelity dynamics are deferred/excluded. Existing <code>src/optimization.py</code> is preserved historical baseline code, not a promise to connect a solver.</p>
    ${TC.callout('warn', 'Current gap', '<p>GMAT has not yet been integrated. Current two-body comparison code is not a substitute for the required GMAT numerical-plus-screenshot verification contract.</p>')}
    <p><a href="#/progress">Open task-by-task progress and evidence →</a></p>
  `;
};
