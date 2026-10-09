/* Static living-progress model. Update truthfully at each task completion. */
window.TCProjectProgress = {
  updated: '2026-10-09',
  commitSubject: 'TJC-1.2: align controlled reference and scoped skills',
  groups: [
    {
      label: 'Completed',
      items: [
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
        {id: 'TJC-1.12 / 1.14', title: 'Formalizer and model selection', outcome: 'Planned behind reference/alignment work.'},
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
