"""Design polish layer, loaded last: layout fixes and finishing touches across the views.

- wide tables (.bx-wide) span the full row instead of squeezing into half of it
- scrollable tables fade at the edge that has more columns, so hidden columns are obvious
- ranking tables: the measure reads as a headline value with its detail below; on phones each
  row becomes a small card (rank, player, measure, then the reason underneath) instead of clipping
- dashboard tiles keep their labels clear of the ring / photo in the corner
- the player page's weekly chart stays in view beside a long match history
- section watermarks step aside on phones, where the heading wraps
- the trophy button waits until the hero has scrolled away on phones
- footer: brand, quick links, season numbers and a back-to-top button
"""

POLISH_CSS = r"""
/* ================= polish layer ================= */
.bx-wide { grid-column: 1 / -1; }

/* scrollable tables: fade the edge that hides more columns */
.bx-tw.sc-r { -webkit-mask-image: linear-gradient(90deg, #000 calc(100% - 56px), transparent); mask-image: linear-gradient(90deg, #000 calc(100% - 56px), transparent); }
.bx-tw.sc-l { -webkit-mask-image: linear-gradient(90deg, transparent, #000 40px); mask-image: linear-gradient(90deg, transparent, #000 40px); }
.bx-tw.sc-l.sc-r { -webkit-mask-image: linear-gradient(90deg, transparent, #000 40px, #000 calc(100% - 56px), transparent); mask-image: linear-gradient(90deg, transparent, #000 40px, #000 calc(100% - 56px), transparent); }

/* ranking tables: headline value + detail line */
.bx-grid-rank .bx-table td:nth-child(3) { min-width: 8.5em; }
.rk-m1 { display: block; font: 700 14.5px/1.25 var(--ar-h, var(--m-display)); letter-spacing: .02em; color: var(--ar-fg, inherit); white-space: nowrap; font-variant-numeric: tabular-nums; }
.rk-m2 { display: block; margin-top: 3px; font-size: 11.5px; line-height: 1.35; color: var(--ar-mut, inherit); font-weight: 500; }
.rk-nw { white-space: nowrap; }
.bx-grid-rank .bx-table td:last-child { line-height: 1.5; }

@media (max-width: 760px) {
  .bx-grid-rank .bx-tw { overflow: visible; -webkit-mask-image: none !important; mask-image: none !important; }
  .bx-grid-rank .bx-table { display: block; width: 100%; min-width: 0 !important; }
  .bx-grid-rank .bx-table thead { display: none; }
  .bx-grid-rank .bx-table tbody { display: block; }
  .bx-grid-rank .bx-table tr { display: grid; grid-template-columns: 30px auto minmax(0, 1fr); column-gap: 10px; row-gap: 8px; align-items: center; padding: 13px 12px; }
  .bx-grid-rank .bx-table tr + tr { border-top: 1px solid var(--ar-line, rgba(255, 255, 255, .08)); }
  .bx-grid-rank .bx-table td { display: block; padding: 0 !important; border: 0 !important; min-width: 0 !important; white-space: normal; background: none !important; }
  .bx-grid-rank .bx-table td:nth-child(2) { white-space: nowrap; }
  .bx-grid-rank .bx-table td:nth-child(3) { text-align: right; }
  .bx-grid-rank .bx-table td:nth-child(4) { grid-column: 2 / -1; font-size: 13px; line-height: 1.5; color: var(--ar-mut, inherit); }
}

/* dashboard tiles: labels clear of the ring / photo */
.ar-stat:has(> .ar-ring) .ar-stat-l, .ar-perf .ar-stat-l { padding-right: 66px; }
@media (max-width: 520px) { .ar-stat:has(> .ar-ring) .ar-stat-l, .ar-perf .ar-stat-l { padding-right: 52px; } }

/* player page: the weekly chart stays in view beside the match history */
@media (min-width: 1000px) {
  .ar-prof > .bx-card:first-child { align-self: start; position: sticky; top: 88px; }
}

/* phones: the outline watermark behind numbered section headings collides with the wrapped title */
@media (max-width: 700px) { .bx-sec > h2[data-idx] .hud-wm { display: none; } }

/* phones: trophy button hidden while the hero buttons are on screen */
html.fab-hero .wp-fab { opacity: 0; pointer-events: none; transform: translateY(12px); }

/* ---------------- footer ---------------- */
.bx-foot.af { position: relative; margin-top: 72px; padding: 0; border: 0; font-size: 13px; color: var(--ar-mut); }
.af-card { position: relative; overflow: hidden; display: grid; gap: 22px; padding: 28px 28px 22px; border-radius: 24px;
  background: radial-gradient(120% 140% at 0% 0%, rgba(198, 255, 0, .09), transparent 55%), radial-gradient(90% 120% at 100% 100%, rgba(0, 217, 255, .08), transparent 60%), var(--ar-glass, rgba(17, 23, 34, .8));
  border: 1px solid var(--ar-line, rgba(255, 255, 255, .08)); box-shadow: var(--ar-shadow, 0 30px 60px -30px #000); }
.af-card::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 2px; background: linear-gradient(90deg, var(--ar-lime), var(--ar-cyan) 50%, transparent); opacity: .8; }
.af-top { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 18px 24px; }
.af-brand { display: flex; align-items: center; gap: 12px; color: var(--ar-fg); text-decoration: none; }
.af-brand .af-ic { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; background: var(--ar-lime); color: #0A0E14; box-shadow: 0 0 22px rgba(198, 255, 0, .45); }
.af-brand .af-ic svg { width: 24px; height: 24px; }
.af-brand b { display: block; font: 800 17px/1.1 var(--ar-h, var(--m-display)); letter-spacing: .08em; }
.af-brand b em { font-style: normal; color: var(--ar-lime); }
.af-brand small { display: block; margin-top: 3px; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--ar-mut); }
.af-links { display: flex; flex-wrap: wrap; justify-content: center; gap: 4px; }
.af-links a { padding: 8px 10px; border-radius: 10px; color: var(--ar-fg); text-decoration: none; font-size: 13px; font-weight: 600; border: 1px solid transparent; transition: border-color .2s ease, background-color .2s ease, color .2s ease; }
.af-links a:hover, .af-links a:focus-visible { color: var(--ar-lime); border-color: rgba(198, 255, 0, .35); background: rgba(198, 255, 0, .06); }
.af-up { display: inline-flex; align-items: center; gap: 8px; padding: 10px 16px; border-radius: 12px; cursor: pointer; font: 700 12px/1 var(--ar-h, var(--m-display)); letter-spacing: .14em; text-transform: uppercase;
  color: var(--ar-fg); background: rgba(255, 255, 255, .03); border: 1px solid rgba(0, 217, 255, .35); transition: transform .2s ease, border-color .2s ease, color .2s ease; }
.af-up svg { width: 16px; height: 16px; transition: transform .2s ease; }
.af-up:hover { color: var(--ar-cyan); border-color: var(--ar-cyan); transform: translateY(-2px); }
.af-up:hover svg { transform: translateY(-2px); }
.af-stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.af-stats span { display: grid; gap: 4px; padding: 12px 14px; border-radius: 14px; background: rgba(5, 8, 13, .45); border: 1px solid rgba(255, 255, 255, .05); }
.af-stats b { font: 800 22px/1 var(--ar-h, var(--m-display)); color: var(--ar-fg); font-variant-numeric: tabular-nums; }
.af-stats small { font-size: 10.5px; letter-spacing: .16em; text-transform: uppercase; }
.af-src { margin: 0; font-size: 12px; line-height: 1.55; max-width: 110ch; }
@media (max-width: 1100px) { .af-top { grid-template-columns: 1fr auto; } .af-links { grid-column: 1 / -1; grid-row: 2; justify-content: flex-start; } }
@media (max-width: 700px) {
  .af-top { grid-template-columns: 1fr; } .af-links { grid-row: auto; }
  .af-card { padding: 22px 18px 18px; }
  .af-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .af-links { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); width: 100%; }
  .af-links a { background: rgba(255, 255, 255, .03); border-color: rgba(255, 255, 255, .06); }
  .af-up { width: 100%; justify-content: center; }
}
"""

POLISH_JS = r"""
(() => {
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

/* scrollable tables: mark which edges hide columns */
const ro = 'ResizeObserver' in window ? new ResizeObserver((es) => es.forEach((e) => edge(e.target.closest('.bx-tw') || e.target))) : null;
function edge(w) {
  if (!w || !w.classList || !w.classList.contains('bx-tw')) return;
  const max = w.scrollWidth - w.clientWidth;
  w.classList.toggle('sc-l', max > 2 && w.scrollLeft > 2);
  w.classList.toggle('sc-r', max > 2 && w.scrollLeft < max - 2);
}
$$('.bx-tw').forEach((w) => {
  w.addEventListener('scroll', () => edge(w), { passive: true });
  if (ro) { ro.observe(w); const t = w.querySelector('table'); if (t) ro.observe(t); }
  edge(w);
});

/* ranking tables: split the measure into a headline value and a detail line (tables redraw on sort) */
function splitCell(td) {
  if (!td || td.dataset.rk) return;
  const t = td.textContent.trim(); let a = t, b = '';
  const i = t.indexOf(' · ');
  if (i > 0) { a = t.slice(0, i); b = t.slice(i + 3); }
  else { const m = t.match(/^(.*?) \((.*)\)$/); if (m) { a = m[1]; b = m[2]; } }
  td.dataset.rk = '1';
  if (!b) return;
  td.textContent = '';
  const x = document.createElement('span'); x.className = 'rk-m1'; x.textContent = a;
  const y = document.createElement('span'); y.className = 'rk-m2';
  b.split(' · ').forEach((part, k) => {   // break only between items, never inside one
    if (k) y.append(' · ');
    const s = document.createElement('span'); s.className = 'rk-nw'; s.textContent = part; y.append(s);
  });
  td.append(x, y);
}
const doRank = (tb) => $$('tr', tb).forEach((tr) => splitCell(tr.children[2]));
$$('.bx-grid-rank tbody').forEach((tb) => {
  doRank(tb);
  new MutationObserver(() => doRank(tb)).observe(tb, { childList: true });
});

/* phones: trophy button waits until the hero is mostly scrolled away */
const hero = document.querySelector('.ar-hero');
const small = matchMedia('(max-width: 760px)');
let ticking = false;
function fab() {
  ticking = false;
  const on = small.matches && hero && hero.offsetParent !== null && scrollY < hero.offsetHeight * .7;
  document.documentElement.classList.toggle('fab-hero', !!on);
}
addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(fab); } }, { passive: true });
addEventListener('hashchange', () => setTimeout(fab, 60));
fab();

/* footer: back to top */
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-af-up]'); if (!b) return;
  e.preventDefault();
  scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
});
})();
"""
