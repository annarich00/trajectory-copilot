/**
 * app.js — tiny hash-router + page registry.
 * Every page module registers itself on window.TCPages[routeName] = async (container) => {...}
 * (window.TCPages itself is initialized in lib.js, which loads before any page module.)
 */
'use strict';

(function () {
  const content = document.getElementById('content');
  const links = Array.from(document.querySelectorAll('.nav-link'));

  function setActive(route) {
    links.forEach((a) => a.classList.toggle('active', a.dataset.route === route));
  }

  async function render(route) {
    setActive(route);
    const renderer = window.TCPages[route];
    if (!renderer) {
      content.innerHTML = `<h1 class="page-title">Not found</h1><p>Unknown route: ${TC.esc(route)}</p>`;
      return;
    }
    content.innerHTML = '<p class="page-subtitle">Loading…</p>';
    try {
      await renderer(content);
      window.scrollTo(0, 0);
    } catch (err) {
      content.innerHTML = `<h1 class="page-title">Error rendering page</h1><pre class="code">${TC.esc(err.stack || String(err))}</pre>`;
    }
  }

  function currentRoute() {
    const h = location.hash.replace(/^#\/?/, '');
    return h || 'overview';
  }

  window.addEventListener('hashchange', () => render(currentRoute()));
  links.forEach((a) => {
    a.addEventListener('click', () => { location.hash = '#/' + a.dataset.route; });
  });

  render(currentRoute());
})();
