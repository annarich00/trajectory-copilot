'use strict';

window.TCPages.overview = async function (root) {
  const stages = [
    ['Natural-language rendezvous request', 'Operator states a supported target/chaser problem. Ambiguity must be surfaced, not silently filled.'],
    ['Structured problem', 'Formalizer now accepts only the scoped two-spacecraft circular-LEO impulsive LVLH class; it records provenance, blocking issues, and focused clarification questions without filling material inputs.'],
    ['Assumption-based CW applicability', 'Check circularity, locality, duration/regime, frame, and maneuver assumptions. This is not a learned universal threshold. Planned: TJC-1.14.'],
    ['Deterministic CW or bounded two-body fallback', 'Current Python contains CW and two-body primitives, but the scoped selection/orchestration path is not complete. Audits/hardening: TJC-1.3–1.6.'],
    ['GMAT numerical comparison + screenshot', 'Required independent evidence. Not implemented today; early vertical slice is TJC-1.20 and hardening is TJC-1.21. A missing screenshot cannot be called PASS.'],
    ['Human-readable explanation', 'Return assumptions, model choice, deterministic result, discrepancies, PASS/WARNING/FAIL, and a directly accessible trajectory image. Planned unified report: TJC-1.19.']
  ];
  root.innerHTML = `
    ${TC.pageHeader('Overview — Scoped Architecture', 'The approved semester workflow and the honest boundary between current deterministic components and planned integration.')}
    ${TC.callout('warn', 'Current capability boundary', '<p>The repository has deterministic CW/two-body/verification building blocks and educational demonstrations. It does <strong>not</strong> yet provide the complete orchestrated workflow, GMAT execution, numerical comparison, or returned trajectory screenshot.</p>')}
    <div class="chain">${stages.map(([title, body], i) => `<div class="node"><strong>${TC.esc(title)}</strong><br/><small>${TC.esc(body)}</small></div>${i < stages.length - 1 ? '<div class="arr">↓</div>' : ''}`).join('')}</div>
    <h2>Responsibility boundary</h2>
    <div class="grid-2">
      <div class="panel"><div class="panel-title">Language and judgment</div><p>Formalization and assumption-based model-selection artifacts state what is known, missing, derived, or assumed.</p></div>
      <div class="panel"><div class="panel-title">Deterministic computation</div><p><code>src/cw.py</code>, <code>src/twobody.py</code>, and <code>src/verify.py</code> produce repeatable numerical results. Interactive browser values are non-authoritative hand ports.</p></div>
    </div>
    <h2>Explicitly deferred / excluded</h2>
    <p>General trajectory optimization, transfer-time trade optimization, Pareto fronts, learned CW-validity boundaries, broad validity sweeps, CR3BP/n-body/cislunar dynamics, high-fidelity perturbation programs, multi-target operations, and general mission planning are semester non-goals—not “next to build.”</p>
    <p><a href="#/progress">See living project progress →</a> · <a href="#/project-map">See scoped roadmap →</a></p>
  `;
};
