// Stand-in for the dashboard's data and drawing API, so the report runs as a plain web page.
window.dash = (() => {
  const DATA = JSON.parse(document.getElementById('bx-data').textContent);
  const draws = new Map();
  const ready = [];
  const visible = (el) => !el.closest('[hidden]');
  const run = (name) => {
    const fn = draws.get(name);
    if (!fn) return;
    document.querySelectorAll(`[data-draw="${name}"]`).forEach((el) => {
      if (!visible(el)) return;
      try { fn(el); } catch (e) { console.error(name, e); }
    });
  };
  const runAll = () => { for (const n of draws.keys()) run(n); };
  let queued = false;
  const schedule = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; runAll(); }); };
  return {
    colors: ['var(--series-1)', 'var(--series-2)', 'var(--series-3)', 'var(--series-4)', 'var(--series-5)', 'var(--series-6)', 'var(--series-7)', 'var(--series-8)'],
    data(id) {
      const d = DATA[id];
      return d ? { status: 'ok', data: d, columns: Object.keys(d[0] || {}), meta: [], refreshing: false } : { status: 'missing', data: [], meta: [], refreshing: false };
    },
    draw(name, fn) { if (fn) draws.set(name, fn); else run(name); },
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
