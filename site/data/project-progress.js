/* Static living-progress model. Update truthfully at each task completion. */
window.TCProjectProgress = {
  updated: '2026-10-06',
  commitSubject: 'TJC-1.27: define pinned Poliastro verification architecture',
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
          id: 'TJC-1.27', date: '2026-10-06', title: 'Define pinned Poliastro verification architecture',
          commit: 'TJC-1.27: define pinned Poliastro verification architecture', hash: 'this commit',
          outcome: 'Defined an isolated, version-pinned Poliastro cross-check for current and future like-for-like astrodynamics models without changing the core solver or replacing GMAT.',
          links: [['Architecture', 'data/docs/poliastro-verification-architecture.md'], ['Verification lesson', '#/verification'], ['Roadmap', '#/project-map']]
        }
      ]
    },
    {
      label: 'Active / ready',
      items: [
        {id: 'TJC-1.20', title: 'Build early CW-to-GMAT vertical slice with screenshot capture', outcome: 'Ready after this task; not implemented.'},
        {id: 'TJC-1.2', title: 'Align controlled reference and skills', outcome: 'Ready; current reference gaps remain.'},
        {id: 'TJC-1.3 / 1.4', title: 'Audit CW STM and two-burn targeting', outcome: 'Ready; site derivations are not audit findings.'},
        {id: 'TJC-1.5 / 1.6', title: 'Harden two-body fallback and verify frame transformations', outcome: 'Ready; current code remains unaudited.'},
        {id: 'TJC-1.7', title: 'Verify two-body propagation against pinned Poliastro', outcome: 'Planned after TJC-1.5; adapter and isolated verification environment are not implemented yet.'}
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
