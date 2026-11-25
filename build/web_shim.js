// Stand-in for the dashboard's data and drawing API, so the report runs as a plain web page.
window.dash = (() => {
  const DATA = JSON.parse(document.getElementById('bx-data').textContent);
  const draws = new Map();
  const ready = [];
  const visible = (el) => !el.closest('[hidden]');
  const paint = (name, el) => {
    const fn = draws.get(name); if (!fn) return;
    try { fn(el); el.__f = fn; } catch (e) { console.error(name, e); }
  };
  // charts well below the screen wait until they come near; opening a page used to draw all of its charts at once
  const later = 'IntersectionObserver' in window ? new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    later.unobserve(e.target); paint(e.target.dataset.draw, e.target);
  }), { rootMargin: '900px 0px' }) : null;
  // force: an explicit redraw (a sort, a filter). Otherwise an element is drawn once, and a chart again if its width
  // changed. Only charts are measured, all of them before anything is drawn: measuring after each draw would lay the
  // whole page out again every time.
  const run = (name, force) => {
    const fn = draws.get(name);
    if (!fn) return;
    const todo = [], far = new Set();
    document.querySelectorAll(`[data-draw="${name}"]`).forEach((el) => {
      if (!visible(el)) return;
      const chart = el.classList.contains('bx-chart'), w = chart ? el.clientWidth : 0;
      if (!force && el.__f === fn && el.__w === w) return;
      if (later && !force && chart && !el.__f && el.getBoundingClientRect().top > innerHeight + 900) far.add(el);
      el.__w = w; todo.push(el);
    });
    todo.forEach((el) => { if (far.has(el)) { if (!el.style.minHeight) el.style.minHeight = '300px'; later.observe(el); } else paint(name, el); });
  };
  const runAll = () => { for (const n of draws.keys()) run(n, false); };
  let queued = false;
  const schedule = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; runAll(); }); };
  return {
    colors: ['var(--series-1)', 'var(--series-2)', 'var(--series-3)', 'var(--series-4)', 'var(--series-5)', 'var(--series-6)', 'var(--series-7)', 'var(--series-8)'],
    data(id) {
      const d = DATA[id];
      return d ? { status: 'ok', data: d, columns: Object.keys(d[0] || {}), meta: [], refreshing: false } : { status: 'missing', data: [], meta: [], refreshing: false };
    },
    draw(name, fn) { if (fn) draws.set(name, fn); else run(name, true); },
    onData(fn) { ready.push(fn); },
    setLink(id) { try { history.replaceState(null, '', '#' + id); } catch (e) { /* file:// may refuse */ } },
    params() { return {}; }, setParams() {}, resetParams() {}, refresh() {},
    start() {
      ready.forEach((fn) => { try { fn(); } catch (e) { console.error(e); } });
      runAll();
      new MutationObserver(schedule).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['hidden'] });
      let t = null;
      window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(runAll, 150); });
    }
  };
})();
