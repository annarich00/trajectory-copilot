'use strict';

window.TCPages.progress = async function (root) {
  const model = window.TCProjectProgress;
  const links = (item) => (item.links || []).map(([label, href]) => `<a href="${href}">${TC.esc(label)}</a>`).join(' · ');
  root.innerHTML = `
    ${TC.pageHeader('Project Progress', `Living, static progress surface. Evidence last reviewed ${TC.esc(model.updated)}; no runtime Backlog or internet request is made.`)}
    ${TC.callout('warn', 'Truthfulness contract', '<p>“Planned” means not implemented. GMAT execution, numerical comparison, and screenshot return are future scoped work. Status and evidence are updated only when a task finishes and local checks have run.</p>')}
    ${model.groups.map((group) => `
      <h2>${TC.esc(group.label)}</h2>
      <div class="grid-2">
        ${group.items.map((item) => `<div class="panel">
          <div class="panel-title">${TC.esc(item.id)}: ${TC.esc(item.title)}</div>
          <p>${TC.esc(item.outcome)}</p>
          ${item.date ? `<p><strong>Date:</strong> ${TC.esc(item.date)}</p>` : ''}
          ${item.commit ? `<p><strong>Commit:</strong> <code>${TC.esc(item.commit)}</code> (${TC.esc(item.hash)})</p>` : ''}
          ${links(item) ? `<p><strong>Evidence:</strong> ${links(item)}</p>` : ''}
        </div>`).join('')}
      </div>`).join('')}
    <h2>Maintenance checklist</h2>
    <ol>
      <li>Update this model and affected pages with the task’s truthful outcome, limitations, commit subject, and evidence links.</li>
      <li>Run <code>python3 tools/sync_site_data.py</code>, then <code>python3 tools/sync_site_data.py --check</code>.</li>
      <li>Keep <code>site/js/physics.js</code> labeled as a non-authoritative pedagogical hand port.</li>
      <li>Run repository tests and <code>tools/compare_upstream.py --check</code>.</li>
      <li>Launch <code>./run_site.sh</code>; smoke-check every changed route and artifact offline.</li>
      <li>Record objective evidence in Backlog before marking the task Done.</li>
    </ol>
    <p>See <a href="README.md">site/README.md</a> for commands and authority boundaries.</p>
  `;
};
