'use strict';

window.TCPages['research'] = async function (root) {
  const baseline = await TC.fetchText('data/baseline_comparison.md');

  root.innerHTML = `
    ${TC.pageHeader('Research Connection', 'How the software architecture in this repository connects to the research question motivating Trajectory CoPilot.')}

    <h2>Two architectures</h2>
    <div class="grid-2">
      <div class="panel">
        <div class="panel-title">Traditional LLM use</div>
        <div class="chain">
          <div class="node">Natural language</div><div class="arr">↓</div>
          <div class="node">Answer</div>
        </div>
        <p>The model reasons end-to-end from the prompt directly to a final answer, with no structural
        separation between understanding the problem, choosing a method, computing a number, and checking that
        number.</p>
      </div>
      <div class="panel">
        <div class="panel-title">Trajectory CoPilot</div>
        <div class="chain">
          <div class="node">Natural language</div><div class="arr">↓</div>
          <div class="node">Formal problem</div><div class="arr">↓</div>
          <div class="node">Model selection</div><div class="arr">↓</div>
          <div class="node">Deterministic physics</div><div class="arr">↓</div>
          <div class="node">Independent verification</div><div class="arr">↓</div>
          <div class="node">Human decision</div>
        </div>
        <p>Each arrow above is a real, separately-inspectable artifact in this repository: a skill's structured
        output, a model-selection rationale, a Python function call, a <code>VerificationResult</code>, and
        finally a human (or downstream agent) consuming all of the above.</p>
      </div>
    </div>

    <h2>What baseline_comparison.md tests</h2>
    <p>The experiment evaluates whether the <code>orbital-problem-formalizer</code> skill changes how an LLM
    handles astrodynamics problems with <em>different levels of specification</em> — not just whether it
    catches missing information, but whether it correctly behaves across three distinct regimes:</p>
    <ol>
      <li>An <strong>underspecified</strong> rendezvous problem (Test 1).</li>
      <li>A <strong>fully specified</strong> CW rendezvous problem (Test 2).</li>
      <li>A rendezvous problem where the <strong>requested model is inappropriate</strong> for the stated
      geometry (Test 3).</li>
    </ol>
    <p>All three tests are evaluated against an explicit <strong>Expected Behavior</strong> written before
    running the skill, then compared against the <strong>Actual Result</strong>. All three passed.</p>

    <table>
      <tr><th>Test</th><th>Expected Readiness</th><th>Actual Skill V1</th><th>Model Validity</th><th>Result</th></tr>
      <tr><td>Underspecified rendezvous</td><td>Needs more information</td><td>Needs more information + validity concern</td><td>Cannot establish CW applicability from available information</td><td style="color:var(--good)"><strong>PASS</strong></td></tr>
      <tr><td>Fully specified CW rendezvous</td><td>Ready to solve</td><td>Ready to solve</td><td>No validity concern</td><td style="color:var(--good)"><strong>PASS</strong></td></tr>
      <tr><td>Large-separation GEO/CW</td><td>Needs more information</td><td>Needs more information + validity concern</td><td>CW small-relative-motion assumption violated</td><td style="color:var(--good)"><strong>PASS</strong></td></tr>
    </table>

    <h2>Five findings</h2>
    <ol>
      <li><strong>The formalizer changes the agent's workflow.</strong> It creates a distinct step between
      natural-language input and trajectory generation — the agent constructs a structured representation
      (reference orbit, frame, state, timing, constraints, model, missing info, validity concerns) before
      attempting a solution. Demonstrated most clearly by Test 1.</li>
      <li><strong>The formalizer can prevent unsupported assumptions.</strong> In Test 1, quantities like the
      reference orbit, coordinate convention, and initial velocity were surfaced as missing rather than
      silently filled in. A physically plausible numerical answer can still be wrong if its underlying
      assumptions were never authorized by the operator.</li>
      <li><strong>The formalizer can distinguish missing information from derivable information.</strong> In
      Test 2, mean motion and orbital period were not explicitly supplied but were correctly treated as
      <em>derivable</em> from μ, Earth radius, and altitude — not as missing operator input. The problem was
      correctly classified <code>READY TO SOLVE</code> rather than blocked on quantities the solver can
      compute itself.</li>
      <li><strong>The formalizer can identify model-validity concerns independently of missing information.</strong>
      In Test 3, the user explicitly requested CW, but the formalizer recognized that a separation of roughly
      one-third of the GEO belt violates CW's small-relative-distance assumption — it did not simply obey the
      requested model. This is an early example of the agent acting as a <em>critical reviewer</em> of the
      requested model, not merely a mathematical executor.</li>
      <li><strong>"Ready to solve" should mean sufficiently specified, not that every quantity was explicitly
      provided.</strong> The three tests together motivate a five-way classification: (1) required operator
      input, (2) derivable quantity, (3) standard modeling assumption, (4) optional constraint, (5)
      model-validity concern — a more useful lens than simply counting present/absent fields.</li>
    </ol>

    <h2>Current research question</h2>
    <div class="callout">
      <p><em>"Does requiring the agent to formalize the orbital problem before solving it reduce incorrect
      assumptions and improve the reliability of the resulting trajectory?"</em></p>
    </div>
    <p>The three tests above support the premise — an explicit formalization layer measurably changed agent
    behavior in exactly the ways the research hypothesis predicts. The open question is whether that improved
    <em>problem formulation</em> translates into improved <em>trajectory-generation reliability</em> — which
    is precisely what the deterministic solver (<code>src/cw.py</code>) and independent verification
    (<code>src/verify.py</code>) layers in this repository exist to make testable.</p>

    <h2>Next experiment: constrained rendezvous optimization</h2>
    <p><code>baseline_comparison.md</code> proposes extending beyond the binary "ready to solve" question
    toward a constrained multi-objective rendezvous problem — minimizing both ΔV <em>and</em> transfer time —
    and testing whether the agent recognizes these as competing objectives, correctly distinguishes a
    spacecraft's available ΔV capability (an input constraint) from the ΔV a candidate trajectory requires (an
    output), and can construct or reason about a Pareto front. This would move the project from <em>"Can the
    agent correctly formalize an orbital problem?"</em> toward <em>"Can the agent correctly translate an
    operator's mission objective and constraints into a mathematically well-posed trajectory-design
    problem?"</em> ${TC.badge('planned', 'PLANNED — NOT YET IMPLEMENTED')}</p>

    <h2>Where deterministic physics and verification fit</h2>
    <p>The formalizer and model-selector are necessary but not sufficient: even a perfectly-formalized,
    correctly-model-selected problem still needs an actual numeric answer, and that answer still needs an
    independent check. <code>src/cw.py</code> + <code>src/verify.py</code> + <code>src/twobody.py</code> make
    the "deterministic physics → independent verification → human decision" half of the pipeline real, not
    just a diagram. The <a href="#/singularity">exact-one-orbit singularity</a> and the
    <a href="#/model-validity">GEO failure case</a> both demonstrate that "the LLM said it's fine" and "the
    solver returned a number" are each, independently, insufficient grounds for trust.</p>

    <h2>Raw source: baseline_comparison.md</h2>
    <details><summary style="cursor:pointer;color:var(--accent)">Show the full baseline comparison document</summary>
      ${TC.authorityBanner('Exact, unmodified contents of baseline_comparison.md.')}
      <pre class="code">${TC.esc(baseline)}</pre>
    </details>

    <p><a href="#/project-map">Continue: Project Map →</a></p>
  `;
};
