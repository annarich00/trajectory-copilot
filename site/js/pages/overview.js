'use strict';

window.TCPages.overview = async function (root) {
  const stages = [
    {
      id: 'operator',
      kind: 'llm',
      kindLabel: 'Human',
      title: 'Human Operator',
      sub: 'Natural-language rendezvous/proximity-ops request',
      purpose: 'The entry point. A human describes a rendezvous or relative-motion problem in plain language, often with incomplete or ambiguous information.',
      inputs: 'Free text, e.g. "The chaser is 200 meters behind the target. Find a one-orbit rendezvous."',
      outputs: 'A natural-language problem statement, nothing else.',
      sourceFiles: 'None (no code) — this is the human-in-the-loop entry point.',
      skills: 'None yet — this is the trigger for the formalizer skill.',
      tests: 'None directly. Indirectly exercised by evaluations/formalizer/test_01_underspecified.txt.',
      status: 'implemented',
      statusLabel: 'IMPLEMENTED (process, not code)',
      limitations: 'No code enforces that this step happens before formalization; it is a workflow convention, not a software guard.',
    },
    {
      id: 'formalizer',
      kind: 'llm',
      kindLabel: 'LLM reasoning',
      title: 'Problem Formalizer',
      sub: 'Converts natural language into a structured problem spec',
      purpose: 'Extract mission objective, reference orbit, coordinate frame, initial/terminal state, timing, maneuver constraints, and requested dynamics model from the natural-language request — WITHOUT solving the problem or silently inventing missing values.',
      inputs: 'Natural-language problem statement.',
      outputs: 'Structured spec: Problem Type, Objective, Reference Orbit, Coordinate Frame, Initial/Terminal State, Timing, Maneuver Constraints, Dynamics Model, Missing Information, Model Validity Concerns, Readiness classification.',
      sourceFiles: '.pi/skills/orbital-problem-formalizer/SKILL.md',
      skills: 'orbital-problem-formalizer',
      tests: 'evaluations/formalizer/test_01_underspecified.txt, test_02_cw_complete.txt, test_03_cw_validity.txt (behavioral evaluations, not pytest unit tests).',
      status: 'partial',
      statusLabel: 'PARTIAL — skill exists and has 3 recorded evaluation transcripts; no automated regression harness runs them.',
      limitations: 'baseline_comparison.md (Finding 5) proposes a 5-way classification — required operator input, derivable quantity, standard modeling assumption, optional constraint, model-validity concern — that the formalizer skill text does not yet encode explicitly; it currently relies on the LLM applying this distinction correctly each time rather than a documented rule.',
    },
    {
      id: 'model-selector',
      kind: 'llm',
      kindLabel: 'LLM reasoning',
      title: 'Model Selector',
      sub: 'Chooses CW vs two-body vs higher-fidelity',
      purpose: 'Given the formalized spec, decide whether Clohessy-Wiltshire linearized relative motion is valid, or whether two-body (or higher-fidelity) propagation is required instead.',
      inputs: 'Formalized problem specification from the Problem Formalizer.',
      outputs: 'Selected model + assumption checks + violated assumptions + rationale + recommended verification method.',
      sourceFiles: '.pi/skills/orbital-model-selector/SKILL.md',
      skills: 'orbital-model-selector',
      tests: 'No automated tests target this skill directly. The underlying "CW rejection checks" it describes are partially mirrored in code by src/cw.py::validate_cw_use(), which is tested by tests/test_cw.py::test_cw_validation_basic.',
      status: 'partial',
      statusLabel: 'PARTIAL — skill text defines the decision rules; only a subset (separation ratio, transfer-time span) is enforced in code via validate_cw_use().',
      limitations: 'The skill’s richer rejection criteria (GEO-scale geometry, multi-rev phasing, non-circular chief orbit) are not encoded as deterministic checks in src/cw.py — only the LLM is expected to apply them currently.',
    },
    {
      id: 'targeting-planner',
      kind: 'llm',
      kindLabel: 'LLM reasoning',
      title: 'Targeting / Optimization Planner',
      sub: 'Turns the problem into an optimization formulation',
      purpose: 'Express the rendezvous problem as decision variables, constraints, an objective, and a recommended solver (e.g. closed-form CW STM targeting vs nonlinear least squares).',
      inputs: 'Formalized spec + selected dynamics model.',
      outputs: 'Problem class, decision variables, constraints, objective, solver recommendation.',
      sourceFiles: '.pi/skills/orbital-targeting-planner/SKILL.md, src/optimization.py',
      skills: 'orbital-targeting-planner',
      tests: 'No automated tests exist for src/optimization.py or this skill. There is no tests/test_optimization.py in the repository.',
      status: 'partial',
      statusLabel: 'PARTIAL — src/optimization.py defines problem *templates* (dataclasses describing objective/decision-variables/constraints) but contains no solver and is untested.',
      limitations: 'RendezvousOptimizationProblem is a plain data container; it does not call two_burn_targeting() or any numeric optimizer. There is no code path connecting optimization.py to cw.py today.',
    },
    {
      id: 'solver',
      kind: 'det',
      kindLabel: 'Deterministic physics',
      title: 'Deterministic Physics Solver',
      sub: 'cw_stm(), two_burn_targeting(), propagate_relative_state()',
      purpose: 'Numerically solve the CW two-impulse targeting problem: compute the state-transition matrix, partition it, solve for the initial Δv via linear algebra, propagate, and compute the terminal Δv.',
      inputs: 'Initial relative state (6-vector), mean motion n, transfer time, optional target final state.',
      outputs: 'Δv0, Δv1, final relative state (6-vector). Raises CWSingularTransferError if the targeting matrix is singular/ill-conditioned.',
      sourceFiles: 'src/cw.py (mean_motion, cw_stm, propagate_relative_state, validate_cw_use, check_phi_rv_conditioning, two_burn_targeting)',
      skills: 'None — this is pure deterministic numerical code, not an LLM skill.',
      tests: 'tests/test_cw.py: test_cw_rendezvous_benchmark, test_cw_exact_one_orbit_targeting_is_rejected, test_cw_validation_basic.',
      status: 'tested',
      statusLabel: 'IMPLEMENTED / TESTED',
      limitations: 'Only two-impulse CW targeting is implemented. No continuous-thrust, no J2/drag perturbations, no multi-revolution-aware targeting, no Lambert/nonlinear solver (optimization.py has no solver yet).',
    },
    {
      id: 'verification',
      kind: 'ver',
      kindLabel: 'Independent verification',
      title: 'Verification',
      sub: 'Independent nonlinear two-body check of the CW result',
      purpose: 'Take the CW relative state, convert to absolute inertial chief/deputy states, propagate BOTH bodies with nonlinear two-body RK4 (not the CW linear STM), convert back to LVLH, and compare against the CW prediction.',
      inputs: 'CW initial relative state, mean motion n, transfer time dt, gravitational parameter μ, tolerances.',
      outputs: 'VerificationResult: cw_state, two_body_state, position_error_m, velocity_error_mps, warnings (e.g. "MODEL VALIDITY WARNING").',
      sourceFiles: 'src/verify.py (compare_cw_two_body, validate_against_two_body, _chief_circular_state, _lvlh_basis, _rel_lvlh_to_absolute, _absolute_to_rel_lvlh), src/twobody.py (kepler_propagate_state, propagate_cartesian_state)',
      skills: 'None — deterministic verification code.',
      tests: 'tests/test_validation.py::test_model_validity_warning_triggers (compare_cw_two_body only). validate_against_two_body() itself (the full independent-propagation pipeline) has NO dedicated automated test.',
      status: 'partial',
      statusLabel: 'PARTIAL — compare_cw_two_body() is tested; validate_against_two_body() (the full LVLH→inertial→two-body→LVLH loop) is implemented but untested.',
      limitations: 'No test currently exercises validate_against_two_body() end-to-end, including the GEO-scale divergence case this site demonstrates live.',
    },
    {
      id: 'outcome',
      kind: 'ver',
      kindLabel: 'Decision gate',
      title: 'PASS / WARNING / FAIL',
      sub: 'Human decision point informed by verification',
      purpose: 'The verification comparison yields either agreement (PASS) or a "MODEL VALIDITY WARNING" (position/velocity error exceeds tolerance). CWSingularTransferError represents an outright FAIL/rejection earlier in the pipeline. A human or downstream agent decides what to do next.',
      inputs: 'VerificationResult.warnings, or a raised CWSingularTransferError.',
      outputs: 'A tri-state outcome: silently pass, explicit "MODEL VALIDITY WARNING" string, or a raised exception that must propagate (not be swallowed).',
      sourceFiles: 'src/verify.py (warnings list), src/cw.py (CWSingularTransferError)',
      skills: 'None — deterministic.',
      tests: 'tests/test_validation.py::test_model_validity_warning_triggers, tests/test_cw.py::test_cw_exact_one_orbit_targeting_is_rejected.',
      status: 'partial',
      statusLabel: 'PARTIAL — the warning/exception mechanisms exist and are tested in isolation; there is no single orchestrated "PASS/WARNING/FAIL" report object joining both signals.',
      limitations: 'PLANNED — NOT YET IMPLEMENTED: a unified decision object that an agent could branch on (e.g. {status: "FAIL", reason: ...}) spanning both the targeting solver and the verification step.',
    },
  ];

  root.innerHTML = `
    ${TC.pageHeader('Overview — Architecture', 'The full pipeline from a human operator\'s natural-language request to a verified (or rejected) numerical result. Click any stage below for details grounded in the actual repository.')}

    <div class="callout">
      <div class="callout-title">How to read this page</div>
      <p>Each stage is tagged by what kind of system performs it:</p>
      <p>${TC.badge('llm', 'LLM reasoning / orchestration')} — language understanding, judgment calls, problem framing.</p>
      <p>${TC.badge('det', 'Deterministic numerical physics')} — pure math/code, same inputs always give the same outputs.</p>
      <p>${TC.badge('ver', 'Independent verification')} — a second, independently-derived computation used to check the first.</p>
    </div>
    ${TC.callout('warn', 'A note on this website\'s own interactive demos', `<p>The "Deterministic numerical
      physics" and "Independent verification" stages below are implemented, in this repository, entirely in
      Python (<code>src/cw.py</code>, <code>src/twobody.py</code>, <code>src/verify.py</code>). Several lesson
      pages on this site (CW STM Explorer, Targeting Walkthrough, Singularity, Experiment) include sliders that
      recompute illustrative numbers live in JavaScript. Those sliders use a hand-ported
      <strong>pedagogical browser mirror</strong> of the Python (<code>site/js/physics.js</code>) — they are a
      teaching aid, not a reimplementation that this site treats as authoritative, and not an independent check
      on the Python. The Python source and <code>pytest tests/</code> remain the only authoritative
      implementation and test results.</p>`)}

    <div class="pipeline" id="pipeline"></div>
    <div id="detail"></div>
  `;

  const pipelineEl = root.querySelector('#pipeline');
  const detailEl = root.querySelector('#detail');

  function renderStage(s, i) {
    const kindBadge = TC.badge(s.kind, s.kindLabel);
    return TC.el(`
      <div class="pipeline-step" data-id="${s.id}">
        <div class="pipeline-kind-tag" style="background:transparent;">${kindBadge}</div>
        <div class="pipeline-step-title">${TC.esc(s.title)}</div>
        <div class="pipeline-step-sub">${TC.esc(s.sub)}</div>
      </div>
    `);
  }

  stages.forEach((s, i) => {
    pipelineEl.appendChild(renderStage(s, i));
    if (i < stages.length - 1) {
      pipelineEl.appendChild(TC.el(`<div class="pipeline-arrow">↓</div>`));
    }
  });

  function statusBadge(status, label) {
    const kindMap = { tested: 'tested', partial: 'partial', planned: 'planned' };
    return TC.badge(kindMap[status] || 'tested', label);
  }

  function showDetail(s) {
    root.querySelectorAll('.pipeline-step').forEach((e) => e.classList.toggle('selected', e.dataset.id === s.id));
    detailEl.innerHTML = `
      <div class="detail-box">
        <h3 style="margin-top:0">${TC.esc(s.title)} ${TC.badge(s.kind, s.kindLabel)}</h3>
        <p>${statusBadge(s.status, s.statusLabel)}</p>
        <p>${TC.esc(s.purpose)}</p>
        <table>
          <tr><th style="width:140px">Inputs</th><td>${TC.esc(s.inputs)}</td></tr>
          <tr><th>Outputs</th><td>${TC.esc(s.outputs)}</td></tr>
          <tr><th>Source files</th><td class="mono">${TC.esc(s.sourceFiles)}</td></tr>
          <tr><th>Skills involved</th><td>${TC.esc(s.skills)}</td></tr>
          <tr><th>Tests</th><td>${TC.esc(s.tests)}</td></tr>
          <tr><th>Known limitations</th><td>${TC.esc(s.limitations)}</td></tr>
        </table>
      </div>
    `;
  }

  pipelineEl.querySelectorAll('.pipeline-step').forEach((elm) => {
    elm.addEventListener('click', () => {
      const s = stages.find((x) => x.id === elm.dataset.id);
      showDetail(s);
    });
  });

  showDetail(stages[0]);

  root.insertAdjacentHTML('beforeend', `
    <h2>Why this separation matters</h2>
    <p>The LLM stages (formalizer, model selector, targeting planner) decide <em>what problem to solve</em> and
    <em>which tool to use</em>. They never compute an orbit. The deterministic solver (<code>src/cw.py</code>)
    computes the actual numbers. The verification stage (<code>src/verify.py</code> + <code>src/twobody.py</code>)
    is an independently-derived check — it does not simply call the CW function twice. See
    <a href="#/llm-vs-code">What the LLM Actually Does</a> for a full breakdown of this boundary, and
    <a href="#/singularity">Why the Singularity Matters</a> for a concrete case where the solver itself must say
    "no" rather than returning a wrong number.</p>
  `);
};
