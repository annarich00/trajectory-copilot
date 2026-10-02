'use strict';

window.TCPages['project-map'] = async function (root) {
  root.innerHTML = `
    ${TC.pageHeader('Project Map', 'The actual current state of the repository, organized into four honest categories, with links into the relevant lesson/source/test.')}

    <div class="roadmap">
      <div class="roadmap-col">
        <h4>${TC.badge('tested', 'CURRENTLY IMPLEMENTED')}</h4>
        <div class="roadmap-item"><a href="#/physics-basics">mean_motion(), orbital_period()</a><br/>src/cw.py, src/twobody.py</div>
        <div class="roadmap-item"><a href="#/cw-stm">cw_stm(), propagate_relative_state()</a><br/>src/cw.py — tested via tests/test_cw.py</div>
        <div class="roadmap-item"><a href="#/targeting">two_burn_targeting()</a><br/>src/cw.py — tested by test_cw_rendezvous_benchmark</div>
        <div class="roadmap-item"><a href="#/singularity">check_phi_rv_conditioning() / CWSingularTransferError</a><br/>src/cw.py — tested by test_cw_exact_one_orbit_targeting_is_rejected</div>
        <div class="roadmap-item"><a href="#/source-explorer">validate_cw_use() (partial heuristics)</a><br/>src/cw.py — tested by test_cw_validation_basic</div>
        <div class="roadmap-item"><a href="#/verification">compare_cw_two_body()</a><br/>src/verify.py — tested by test_model_validity_warning_triggers</div>
        <div class="roadmap-item"><a href="#/source-explorer">kepler_propagate_state() / propagate_cartesian_state()</a><br/>src/twobody.py — smoke-tested only</div>
        <div class="roadmap-item"><a href="#/llm-vs-code">orbital-problem-formalizer skill</a><br/>.pi/skills/ — 3 recorded behavioral evaluations</div>
        <div class="roadmap-item"><a href="#/llm-vs-code">orbital-model-selector, orbital-targeting-planner skills</a><br/>.pi/skills/ — guidance text, no automated eval harness</div>
      </div>

      <div class="roadmap-col">
        <h4>${TC.badge('partial', 'NEXT TO VERIFY')}</h4>
        <div class="roadmap-item"><a href="#/verification">validate_against_two_body()</a><br/>Implemented, but has NO dedicated automated test — the full LVLH↔inertial↔two-body round trip is currently only exercised by this website's pedagogical mirror and by hand during development.</div>
        <div class="roadmap-item"><a href="#/test-classification">orbital_period(), vis_viva_speed() numeric correctness</a><br/>Only software-consistency tests exist (positive/finite checks) — no test asserts a specific numeric period/speed value against a known-correct answer.</div>
        <div class="roadmap-item"><a href="#/model-validity">GEO-scale / non-circular-orbit rejection in validate_cw_use()</a><br/>Guidance exists in skills and reference/SOURCE.md; not yet encoded as deterministic checks in src/cw.py beyond the simple separation-ratio heuristic.</div>
        <div class="roadmap-item"><a href="#/failure-museum">5-way information taxonomy (Finding 5)</a><br/>baseline_comparison.md proposes classifying every quantity as required operator input / derivable / modeling assumption / optional constraint / model-validity concern — not yet encoded as an explicit rule in the formalizer skill, so it depends on the LLM applying the distinction correctly each time.</div>
      </div>

      <div class="roadmap-col">
        <h4>${TC.badge('planned', 'NEXT TO BUILD')}</h4>
        <div class="roadmap-item"><a href="#/source-explorer">A solver connected to src/optimization.py</a><br/>RendezvousOptimizationProblem templates exist as data only; no code path calls a numeric optimizer or even two_burn_targeting() from them.</div>
        <div class="roadmap-item"><a href="#/llm-vs-code">A unified PASS/WARNING/FAIL decision object</a><br/>Currently the targeting solver's exception and the verifier's warning tuple are two separate signals with no shared schema for an agent to branch on.</div>
        <div class="roadmap-item"><a href="#/failure-museum">Automatic verification triggering</a><br/>two_burn_targeting() does not automatically call validate_against_two_body() — a caller must remember to invoke it.</div>
        <div class="roadmap-item"><a href="#/failure-museum">Frame-consistency / coordinate-convention checking (Failure 4)</a><br/>No automated check exists to catch a self-consistent-but-wrong coordinate assumption; this remains entirely an LLM-formalization responsibility today.</div>
        <div class="roadmap-item">Automated regression harness for evaluations/formalizer/*.txt<br/>These are currently manually-recorded transcripts, not an automated CI-style eval suite.</div>
      </div>

      <div class="roadmap-col">
        <h4>${TC.badge('planned', 'FUTURE RESEARCH')}</h4>
        <div class="roadmap-item">Higher-fidelity propagation (J2, drag, SRP, third-body)<br/>Mentioned as a model tier in .pi/skills/orbital-model-selector/SKILL.md and reference/SOURCE.md; no code exists for it yet.</div>
        <div class="roadmap-item">Comparison against GMAT or another independent high-fidelity tool<br/>baseline_comparison.md (Test 3, Research Significance) explicitly names this as a future direction: a CW-generated solution should eventually be checked against a higher-fidelity two-body model and, ultimately, GMAT.</div>
        <div class="roadmap-item">Constrained rendezvous optimization experiment (ΔV vs. transfer time)<br/>baseline_comparison.md's "Next Experiment" proposes testing whether the agent recognizes ΔV and transfer time as competing objectives, distinguishes available ΔV capability (a constraint) from required ΔV (an output), and can reason about a Pareto front — not yet run.</div>
        <div class="roadmap-item"><a href="#/research">Formal evaluation of the central research question</a><br/>Whether requiring formalization before solving measurably reduces incorrect assumptions and improves downstream trajectory reliability — stated as the explicit open question in baseline_comparison.md.</div>
      </div>
    </div>

    <h2>TJC-1.24 synchronization progress</h2>
    <div class="callout callout-info">
      <strong>TJC-1.24: synchronized upstream workspace and educational site</strong><br/>
      Commit: <code>TJC-1.24: synchronize upstream educational site</code><br/>
      Outcome: imported the dependency-free site and launcher; authoritative shared Python, tests, skills,
      examples, evaluations, and reference files matched upstream by checksum. Verification: baseline pytest,
      manifest check, and offline HTTP smoke checks passed. Limitation: the broader roadmap/status language on
      this recovered site remains intentionally unchanged and is delegated to TJC-1.25.
    </div>
    <p><strong>Authority boundary:</strong> Python and repository files displayed under <code>site/data/</code>
    are verbatim read-only mirrors of authoritative repository content. Interactive JavaScript physics remains
    a clearly labeled pedagogical browser mirror and is not verification evidence.</p>

    <h2>How to use this map</h2>
    <p>This is not a promise of future features — it is an honest accounting of exactly what exists today
    (left two columns) versus what is designed-for-but-not-built (right two columns), grounded entirely in the
    actual files in this repository as of this site's generation. Every item links to the lesson, source file,
    or test that substantiates its classification.</p>

    <h2>One-page summary of this entire site</h2>
    <div class="chain">
      <div class="node">Human Operator</div><div class="arr">↓</div>
      <div class="node">Problem Formalizer <span class="badge badge-llm">LLM</span></div><div class="arr">↓</div>
      <div class="node">Model Selector <span class="badge badge-llm">LLM</span></div><div class="arr">↓</div>
      <div class="node">Targeting Planner <span class="badge badge-llm">LLM</span></div><div class="arr">↓</div>
      <div class="node">Deterministic Physics Solver <span class="badge badge-det">src/cw.py</span></div><div class="arr">↓</div>
      <div class="node">Independent Verification <span class="badge badge-ver">src/verify.py + twobody.py</span></div><div class="arr">↓</div>
      <div class="node">PASS / WARNING / FAIL</div>
    </div>
    <p><a href="#/overview">← Back to Overview</a></p>
  `;
};
