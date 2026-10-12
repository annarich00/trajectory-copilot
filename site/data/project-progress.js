/* Static living-progress model. Update truthfully at each task completion. */
window.TCProjectProgress = {
  updated: '2026-10-12',
  commitSubject: 'TJC-2: attempt real GMAT GUI screenshot and persist discoverable artifacts',
  groups: [
    {
      label: 'Completed',
      items: [
        {
          id: 'TJC-2', date: '2026-10-12', title: 'Capture a real GMAT GUI screenshot and store it in a discoverable location',
          commit: 'TJC-2: attempt real GMAT GUI screenshot and persist discoverable artifacts', hash: 'pending final commit',
          outcome: 'Added src/gmat_verify.py::attempt_gmat_gui_screenshot, which genuinely attempts a real GMAT GUI (OrbitView/OpenFrames) screenshot (launching GMAT-R2026a under the configured DISPLAY, waiting, and grabbing the screen) before scripts/run_cw_gmat_slice.py falls back to the deterministic SVG plot. Investigated real-display feasibility in this sandboxed WSLg environment: a reachable X display genuinely exists and GMAT-R2026a genuinely launches and maps real OrbitView/OpenFrames windows (confirmed via a python-xlib window-tree walk), but every external screen-capture attempt against that display returned a uniformly blank image regardless of wait duration, and direct XGetImage calls on the mapped windows raised X protocol errors; no screenshot utility is installed and installing one requires unavailable sudo. This exact reproducible evidence is documented in the function\'s docstring and recorded in the result\'s screenshot_source field ("gmat_gui" vs "svg_fallback"). Made the already-declared artifacts/cw_gmat_slice/ default output directory the actual persistent, discoverable location for real runs (tracked README.md documenting the gitignore convention for per-run outputs), added a small permanently-committed example run under examples/cw_gmat_slice_example/, and referenced both from the educational site and verification_result.json itself (artifact_storage_convention field). Extended tests/test_cw_gmat_slice.py with GUI-screenshot-path tests (including an environment-conditional real-attempt test with an explicit skip reason) and a screenshot_source-distinguishing test; all 68 repo tests pass.',
          links: [['GMAT verification page', '#/cw-gmat-slice'], ['Real-GUI screenshot attempt', 'data/src/gmat_verify.py'], ['Runner', 'data/scripts/run_cw_gmat_slice.py'], ['Tests', 'data/tests/test_cw_gmat_slice.py'], ['Example artifact', 'data/examples/cw_gmat_slice_example/verification_result.json']]
        },
        {
          id: 'TJC-1.21', date: '2026-10-11', title: 'Harden GMAT execution, comparison, and screenshot capture',
          commit: 'TJC-1.21: harden GMAT execution, comparison, and screenshot capture', hash: 'cc9502c',
          outcome: 'Added src/gmat_verify.py (script generation, GMAT availability/execution, ReportFile parsing, final-state comparison, screenshot validation) and rewrote scripts/run_cw_gmat_slice.py around it. The runner solves the CW rendezvous case, generates/executes a traceable GMAT script with absolute-path ReportFile output, parses GMAT final-state and trajectory reports back into SI units, compares against the CW analytical final state at configured tolerances, and validates a non-empty SVG trajectory artifact. Real end-to-end execution against GmatConsole-R2026a for the quarter-period 350 km LEO benchmark reaches a real PASS (position error ~0.0079 m, velocity error ~1.17e-5 m/s, both well inside the 1 m / 0.001 m/s tolerances). Six mutually distinguishable failure modes (CW_TARGETING_INFEASIBLE, MISSING_GMAT, EXECUTION_ERROR, MALFORMED_OUTPUT, NUMERICAL_DISAGREEMENT, SCREENSHOT_FAILURE) are each covered by a dedicated test and never silently reported as verified.',
          links: [['GMAT verification page', '#/cw-gmat-slice'], ['Authoritative verifier', 'data/src/gmat_verify.py'], ['Runner', 'data/scripts/run_cw_gmat_slice.py'], ['Tests', 'data/tests/test_cw_gmat_slice.py'], ['Case input', 'data/examples/cw_gmat_vertical_slice.yaml']]
        },
        {
          id: 'TJC-1.14', date: '2026-10-11', title: 'Implement assumption-based CW or two-body model selection',
          commit: 'TJC-1.14: implement assumption-based CW or two-body model selection', hash: 'pending final commit',
          outcome: 'Added src/model_selector.py, a deterministic multi-factor combinator over circularity, locality, duration/regime, frame, other-physics, and maneuver assumptions plus an optional CW targeting-conditioning signal from src/cw.py::two_burn_targeting. Clearly-supported cases select CW; clearly-violated cases route to the bounded two-body coast contract or UNSUPPORTED; boundary cases return a qualified CW decision with surfaced concerns and a verification-sensitivity note; any unknown required item returns NEEDS MORE INFORMATION rather than a model choice. No single numeric threshold is used alone.',
          links: [['Model selector page', '#/model-selector'], ['Authoritative source', 'data/src/model_selector.py'], ['Tests', 'data/tests/test_model_selector.py'], ['Selector skill', 'data/skills/model-selector.SKILL.md'], ['Reference §D', 'data/reference/SOURCE.md']]
        },
        {
          id: 'TJC-1.15', date: '2026-10-09', title: 'Harden deterministic CW rendezvous solution path',
          commit: 'TJC-1.15: harden deterministic CW rendezvous solution path', hash: '417908b',
          outcome: 'Added solve_cw_rendezvous(), a single deterministic orchestration function composing mean_motion -> two_burn_targeting -> propagate_relative_state, returning burn components, total delta-v, a sampled relative trajectory, final relative state, and time of flight together with declared units, frame, state ordering, assumptions, and solver status. Singular-infeasible/singular-reachable transfer times surface two_burn_targeting\u2019s structured status unchanged (no least-squares fallback, no silent transfer-time change). Added unsupported_cw_rendezvous_request() as an explicit rejection path for optimization/trade-study/non-CW-dynamics requests. Reproduces the audited quarter-orbit 350 km LEO benchmark exactly.',
          links: [['Authoritative CW source', 'data/src/cw.py'], ['Regression tests', 'data/tests/test_cw.py'], ['Targeting lesson', '#/targeting'], ['Reference', 'data/reference/SOURCE.md']]
        },
        {
          id: 'TJC-1.26', date: '2026-10-01', title: 'Establish initial checkpoint and atomic commits',
          commit: 'TJC-1.26: establish initial checkpoint and atomic commits', hash: '0f7e1ec',
          outcome: 'Created the known-good pre-site checkpoint and one-task/one-commit policy.',
          links: [['Commit policy', '../docs/task-commit-policy.md'], ['Baseline tests', '#/tests']]
        },
        {
          id: 'TJC-1.24', date: '2026-10-02', title: 'Synchronize upstream educational site',
          commit: 'TJC-1.24: synchronize upstream educational site', hash: '5f75a43',
          outcome: 'Recovered the dependency-free site and checksum-matched authoritative source/test/reference mirrors.',
          links: [['Site README', 'README.md'], ['Source explorer', '#/source-explorer'], ['Tests', '#/tests']]
        },
        {
          id: 'TJC-1.25', date: '2026-10-02', title: 'Align site with scoped roadmap and living progress',
          commit: 'TJC-1.25: align site with scoped roadmap and living progress', hash: 'fbe0801',
          outcome: 'Aligned scope and navigation, established this progress surface and teaching contract, and added strict mirror synchronization.',
          links: [['Overview', '#/overview'], ['Roadmap', '#/project-map'], ['Research', '#/research'], ['Maintenance', 'README.md']]
        },
        {
          id: 'TJC-1.2', date: '2026-10-09', title: 'Align controlled reference and scoped skills',
          commit: 'TJC-1.2: align controlled reference and scoped skills', hash: 'pending final commit',
          outcome: 'Rewrote the controlled reference around exact CW/LVLH/SI and bounded two-body coast contracts; replaced optimization guidance with five scoped skills for formulation, selection, CW, two-body, and GMAT verification. GMAT numerical comparison plus an accessible trajectory screenshot are mandatory PASS evidence, while GMAT execution remains unintegrated.',
          links: [['Controlled reference', 'data/reference/SOURCE.md'], ['Skill mirrors', '#/source-explorer'], ['CW implementation', 'data/src/cw.py'], ['Two-body implementation', 'data/src/twobody.py'], ['Tests', '#/tests']]
        },
        {
          id: 'TJC-1.20', date: '2026-10-09', title: 'Build early CW-to-GMAT vertical slice',
          commit: 'TJC-1.20: build CW-to-GMAT vertical slice', hash: 'ba5d0ae',
          outcome: 'Added a reproducible CW-to-GMAT vertical slice with generated GMAT input, captured execution evidence, numerical comparison fields, and returned trajectory artifact. Without GMAT it reports NOT VERIFIED rather than claiming a pass.',
          links: [['Slice runner', 'data/scripts/run_cw_gmat_slice.py'], ['Case input', 'data/examples/cw_gmat_vertical_slice.yaml'], ['Demo page', '#/cw-gmat-slice'], ['Tests', '#/tests']]
        },
        {
          id: 'TJC-1.12', date: '2026-10-09', title: 'Narrow and harden rendezvous problem formalizer',
          commit: 'TJC-1.12: narrow and harden rendezvous problem formalizer', hash: '81bf188',
          outcome: 'Restricted formalization to the supported rendezvous class, added field-level provenance and clarification blockers, and covered complete, incomplete, contradictory, and unit-inconsistent requests.',
          links: [['Formalizer skill', 'data/skills/formalizer.SKILL.md'], ['Schema tests', 'data/tests/test_formalizer_schema.py'], ['Overview', '#/overview']]
        },
        {
          id: 'TJC-1.6', date: '2026-10-09', title: 'Verify LVLH/inertial state transformations',
          commit: 'TJC-1.6: verify LVLH inertial state transformations', hash: '2c23f0b',
          outcome: 'Hardened LVLH/inertial conversions with explicit degenerate-state errors and verified right-handed basis, transport terms, and position/velocity round trips.',
          links: [['LVLH lesson', '#/cw-lvlh'], ['Authoritative transforms', 'data/src/verify.py'], ['Transform tests', 'data/tests/test_validation.py']]
        },
        {
          id: 'TJC-1.4', date: '2026-10-09', title: 'Handle singular CW two-burn targeting',
          commit: 'TJC-1.4: audit CW two-burn targeting and singularity handling', hash: 'a39017d',
          outcome: 'Replaced blanket singular-transfer rejection with explicit SVD column-space reachability. Singular reachable boundaries receive a minimum-norm non-unique solution; unreachable boundaries return explicit infeasible metadata without fabricated burns or transfer-time changes.',
          links: [['Targeting lesson', '#/targeting'], ['Singularity lesson', '#/singularity'], ['Authoritative CW source', 'data/src/cw.py'], ['Regression tests', 'data/tests/test_cw.py'], ['Reference', 'data/reference/SOURCE.md']]
        },
        {
          id: 'TJC-1.3', date: '2026-10-08', title: 'Audit CW state-transition implementation',
          commit: 'TJC-1.3: audit CW state-transition implementation', hash: 'pending final commit',
          outcome: 'Independently mapped every circular-chief CW STM block and term to cited equations; no implementation defect was found. Added zero-time identity and quarter-orbit block/sign/unit regressions, an audit note, code-facing conventions, and a detailed STM derivation lesson.',
          links: [['Audit note', '../docs/cw-stm-audit.md'], ['Authoritative STM', 'data/src/cw.py'], ['Regression tests', 'data/tests/test_cw.py'], ['CW STM lesson', '#/cw-stm']]
        },
        {
          id: 'TJC-1.27', date: '2026-10-06', title: 'Define pinned Poliastro verification architecture',
          commit: 'TJC-1.27: define pinned Poliastro verification architecture', hash: '50bd18d',
          outcome: 'Defined an isolated, version-pinned Poliastro cross-check for current and future like-for-like astrodynamics models without changing the core solver or replacing GMAT.',
          links: [['Architecture', 'data/docs/poliastro-verification-architecture.md'], ['Verification lesson', '#/verification'], ['Roadmap', '#/project-map']]
        },
        {
          id: 'TJC-1.7', date: '2026-10-06', title: 'Verify two-body propagation against pinned Poliastro',
          commit: 'TJC-1.7: verify two-body propagation against pinned Poliastro', hash: 'pending commit',
          outcome: 'Added a versioned JSON subprocess boundary, isolated Python 3.10 provenance, PASS/FAIL/UNAVAILABLE/UNSUPPORTED handling, and retained SI Cartesian contract evidence for circular and bounded eccentric coast cases. Live external execution remains optional because the core environment deliberately excludes archived Poliastro.',
          links: [['Architecture', 'data/docs/poliastro-verification-architecture.md'], ['Host adapter', 'data/src/poliastro_verify.py'], ['Tests', 'data/tests/test_poliastro_verify.py'], ['Evidence', '../evidence/poliastro/contract-test-evidence.json']]
        },
        {
          id: 'TJC-1.5', date: '2026-10-06', title: 'Harden deterministic two-body fallback',
          commit: 'TJC-1.5: harden deterministic two-body fallback', hash: 'this commit',
          outcome: 'Defined a bounded SI Cartesian point-mass coast contract, added analytical, invariant, CW-invalid, unsupported-request, and input-rejection tests, and reserved stable metadata for the later isolated Poliastro adapter.',
          links: [['Two-body lesson', '#/verification'], ['Authoritative source', 'data/src/twobody.py'], ['Tests', '#/tests'], ['Reference', 'data/reference/SOURCE.md']]
        }
      ]
    },
    {
      label: 'Active / ready',
      items: [
        {id: 'TJC-1.20', title: 'Build early CW-to-GMAT vertical slice with screenshot capture', outcome: 'Ready after this task; not implemented.'},
        {id: 'TJC-1.6', title: 'Verify frame transformations', outcome: 'Ready; full LVLH/inertial transformation audit remains separate work.'},
      ]
    },
    {
      label: 'Blocked / planned',
      items: [
        {id: 'TJC-1.21 / 1.19', title: 'Harden GMAT and unified report', outcome: 'Planned after the vertical slice; GMAT is not currently integrated.'},
        {id: 'TJC-1.16 / 1.9 / 1.22 / 1.23', title: 'Reconnect, benchmark, compare, report', outcome: 'Planned behind component hardening.'}
      ]
    },
    {
      label: 'Deferred / excluded from semester',
      items: [
        {id: 'Non-goal', title: 'Optimization and Pareto fronts', outcome: 'Excluded, not next to build.'},
        {id: 'Non-goal', title: 'Learned thresholds and broad validity sweeps', outcome: 'Excluded; selection is assumption-based.'},
        {id: 'Non-goal', title: 'CR3BP, cislunar, n-body, broad mission planning', outcome: 'Excluded from the supported rendezvous scope.'}
      ]
    }
  ]
};
