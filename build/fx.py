"""Gaming FX layer for the Arena page: custom HUD cursor, 3D tilt and glare on cards, neon border
spotlight on report cards, 3D hero depth (parallax, extruded and glitching title, moving grid floor),
3D scroll reveals and view switches, inertia smooth scrolling and a scroll progress bar.

Everything is progressive: touch screens get no cursor/tilt/inertia, and prefers-reduced-motion
turns the motion off. Loaded after arena.py so it can override the reveal animations.
"""

FX_CSS = r"""
/* =====================================================================
   FX — gaming 3D layer
   ===================================================================== */
/* ---------------- custom HUD cursor (mouse only) ---------------- */
html.fx-cur, html.fx-cur * { cursor: none !important; }
html.fx-cur :is(input:not([type=checkbox]):not([type=radio]):not([type=range]), textarea, [contenteditable="true"]) { cursor: text !important; }
.fx-cursor { position: fixed; inset: 0; z-index: 2147483000; pointer-events: none; opacity: 0; transition: opacity .25s ease; }
html.fx-cur .fx-cursor.is-live { opacity: 1; }
.fx-cursor.is-text { opacity: 0 !important; }
.fx-trail { position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 2147482999; pointer-events: none; }
.fx-dot { position: absolute; left: 0; top: 0; width: 6px; height: 6px; margin: -3px 0 0 -3px; border-radius: 50%; background: var(--ar-lime);
  box-shadow: 0 0 6px var(--ar-lime), 0 0 16px rgba(198, 255, 0, .7); transition: width .2s var(--ar-ease), height .2s var(--ar-ease), margin .2s var(--ar-ease), background .2s ease; will-change: transform; }
.fx-ring { position: absolute; left: 0; top: 0; width: 38px; height: 38px; will-change: transform, width, height; }
.fx-ring::before { content: ""; position: absolute; inset: 7px; border-radius: 50%; border: 1px dashed rgba(0, 217, 255, .55); animation: fx-spin 6s linear infinite; transition: opacity .2s ease, inset .2s ease; }
.fx-ring i { position: absolute; width: 9px; height: 9px; border: 2px solid var(--ar-lime); filter: drop-shadow(0 0 4px rgba(198, 255, 0, .8)); transition: border-color .2s ease, width .2s ease, height .2s ease; }
.fx-ring i:nth-child(1) { left: 0; top: 0; border-right: 0; border-bottom: 0; border-top-left-radius: 3px; }
.fx-ring i:nth-child(2) { right: 0; top: 0; border-left: 0; border-bottom: 0; border-top-right-radius: 3px; }
.fx-ring i:nth-child(3) { left: 0; bottom: 0; border-right: 0; border-top: 0; border-bottom-left-radius: 3px; }
.fx-ring i:nth-child(4) { right: 0; bottom: 0; border-left: 0; border-top: 0; border-bottom-right-radius: 3px; }
.fx-ring b { position: absolute; left: 0; top: -17px; font: 700 9px/1 var(--ar-h, var(--m-display)); letter-spacing: .22em; color: var(--ar-lime); text-shadow: 0 0 8px rgba(198, 255, 0, .8); opacity: 0; transform: translateY(4px); transition: opacity .2s ease, transform .2s ease; white-space: nowrap; }
.fx-cursor.is-lock .fx-ring::before { opacity: 0; }
.fx-cursor.is-lock .fx-ring i { width: 12px; height: 12px; }
.fx-cursor.is-lock .fx-ring b { opacity: 1; transform: none; }
.fx-cursor.is-lock .fx-dot { width: 4px; height: 4px; margin: -2px 0 0 -2px; }
.fx-cursor.is-big .fx-ring i { border-color: var(--ar-cyan); filter: drop-shadow(0 0 5px rgba(0, 217, 255, .9)); }
.fx-cursor.is-big .fx-ring::before { border-color: rgba(198, 255, 0, .5); }
.fx-cursor.is-down .fx-ring i { border-color: #fff; }
.fx-boom { position: fixed; left: 0; top: 0; z-index: 2147483001; pointer-events: none; width: 0; height: 0; }
.fx-boom::before { content: ""; position: absolute; left: -6px; top: -6px; width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--ar-lime); box-shadow: 0 0 14px var(--ar-lime); animation: fx-shock .55s cubic-bezier(.15, .7, .3, 1) forwards; }
.fx-boom i { position: absolute; left: -2px; top: -2px; width: 4px; height: 4px; border-radius: 1px; background: var(--c, var(--ar-lime)); box-shadow: 0 0 8px var(--c, var(--ar-lime));
  transform: rotate(var(--a)) translateX(0); animation: fx-shard .6s cubic-bezier(.1, .75, .3, 1) forwards; }
@keyframes fx-spin { to { transform: rotate(360deg); } }
@keyframes fx-shock { to { transform: scale(5.5); opacity: 0; border-width: 1px; } }
@keyframes fx-shard { 70% { opacity: 1; } to { transform: rotate(var(--a)) translateX(var(--r, 34px)) scale(.4); opacity: 0; } }

/* ---------------- scroll progress + view-switch warp ---------------- */
.fx-progress { position: fixed; left: 0; top: 0; z-index: 70; width: 100%; height: 3px; pointer-events: none; transform-origin: 0 50%; transform: scaleX(var(--p, 0));
  background: linear-gradient(90deg, var(--ar-cyan), var(--ar-lime)); box-shadow: 0 0 10px rgba(198, 255, 0, .8), 0 0 22px rgba(0, 217, 255, .5); }
.fx-progress::after { content: ""; position: absolute; right: -2px; top: -3px; width: 9px; height: 9px; border-radius: 50%; background: #fff; box-shadow: 0 0 10px #fff, 0 0 20px var(--ar-lime); transform: scaleX(calc(1 / max(var(--p, 1), .001))); opacity: var(--pd, 0); }
.fx-warp { position: fixed; inset: 0; z-index: 65; pointer-events: none; overflow: hidden; }
.fx-warp::before { content: ""; position: absolute; left: 0; right: 0; top: -35vh; height: 35vh; opacity: 0;
  background: linear-gradient(180deg, transparent, rgba(0, 217, 255, .07) 55%, rgba(198, 255, 0, .28) 96%, rgba(255, 255, 255, .8) 99%, transparent); }
.fx-warp::after { content: ""; position: absolute; inset: 0; opacity: 0; background: repeating-linear-gradient(180deg, rgba(0, 217, 255, .06) 0 1px, transparent 1px 4px); }
.fx-warp.go::before { animation: fx-sweep .65s cubic-bezier(.3, .6, .3, 1); }
.fx-warp.go::after { animation: fx-flash .65s ease-out; }
@keyframes fx-sweep { 0% { opacity: 1; transform: translateY(0); } 100% { opacity: .6; transform: translateY(140vh); } }
@keyframes fx-flash { 0% { opacity: 0; } 25% { opacity: 1; } 100% { opacity: 0; } }

/* ---------------- 3D tilt + glare ---------------- */
html.fx-3d .fx-tilt { position: relative; transition: transform .6s var(--ar-ease), border-color .3s ease, box-shadow .3s ease, background .3s ease !important; }
html.fx-3d .fx-tilt.fx-tilting { transition: transform .12s linear, border-color .3s ease, box-shadow .3s ease, background .3s ease !important;
  transform: perspective(900px) translate3d(0, -6px, 0) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)) scale(1.02) !important; z-index: 2; }
html.fx-3d .ar-hero-stats.fx-tilting { transform: perspective(1400px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)) !important; }
.fx-glare, html.fx-3d .ar-hero-stats::after { content: ""; position: absolute; inset: 0; z-index: 4; border-radius: inherit; pointer-events: none; opacity: 0; transition: opacity .35s ease;
  background: radial-gradient(circle at var(--gx, 50%) var(--gy, 50%), rgba(255, 255, 255, .22), rgba(198, 255, 0, .08) 28%, transparent 55%); mix-blend-mode: screen; }
.fx-tilting > .fx-glare, html.fx-3d .ar-hero-stats.fx-tilting::after { opacity: 1; }
html.fx-3d .ar-hero-stats { position: relative; }

/* ---------------- neon border spotlight on report cards ---------------- */
html.fx-3d .bx-card { position: relative; }
.fx-spot { position: absolute; inset: -1px; z-index: 1; border-radius: inherit; padding: 1px; pointer-events: none; opacity: 0; transition: opacity .4s ease;
  background: radial-gradient(380px circle at var(--sx, 50%) var(--sy, 0%), rgba(198, 255, 0, .9), rgba(0, 217, 255, .5) 35%, transparent 70%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0); }
.fx-spot::after { content: ""; position: absolute; inset: 1px; border-radius: inherit; }
.bx-card:hover > .fx-spot { opacity: 1; }
.fx-haze { position: absolute; inset: 0; z-index: 0; border-radius: inherit; pointer-events: none; opacity: 0; transition: opacity .4s ease;
  background: radial-gradient(520px circle at var(--sx, 50%) var(--sy, 0%), rgba(0, 217, 255, .07), transparent 60%); }
.bx-card:hover > .fx-haze { opacity: 1; }

/* ---------------- hero: depth, extruded title, glitch, grid floor ---------------- */
html.fx-3d .ar-hero-bg { perspective: 1000px; perspective-origin: 50% 30%; }
html.fx-3d .ar-court { transform-origin: 50% 100%; will-change: translate, rotate; }
html.fx-3d .ar-hero-in { perspective: 1100px; will-change: translate, opacity; }
.ar-title { transform-style: preserve-3d; will-change: rotate; }
.ar-title .t1 { position: relative;
  text-shadow: 0 1px 0 #cfd7e3, 0 2px 0 #b3bccb, 0 3px 0 #97a1b2, 0 4px 0 #7b8699, 0 5px 0 #5f6a7f, 0 6px 0 #455066, 0 7px 0 #2e374b, 0 12px 24px rgba(0, 0, 0, .65), 0 0 46px rgba(0, 217, 255, .28); }
.ar-title .t2 { filter: drop-shadow(0 1px 0 #a9d400) drop-shadow(0 1px 0 #8fb500) drop-shadow(0 1px 0 #759600) drop-shadow(0 1px 0 #5c7600) drop-shadow(0 2px 0 #3f5200)
  drop-shadow(0 12px 22px rgba(0, 0, 0, .6)) drop-shadow(0 0 30px rgba(198, 255, 0, .38)); }
.ar-title .t1::before, .ar-title .t1::after { content: attr(data-text); position: absolute; inset: 0; text-shadow: none; opacity: 0; pointer-events: none; mix-blend-mode: screen; }
.ar-title .t1::before { color: #00E5FF; animation: fx-glitch-a 7s steps(1) infinite 2.4s; }
.ar-title .t1::after { color: #FF2BD6; animation: fx-glitch-b 7s steps(1) infinite 2.4s; }
.ar-title:hover .t1::before { animation-duration: .9s; }
.ar-title:hover .t1::after { animation-duration: .9s; }
@keyframes fx-glitch-a {
  0%, 90%, 100% { opacity: 0; transform: none; clip-path: inset(0 0 0 0); }
  91% { opacity: .9; transform: translate(-4px, -1px); clip-path: inset(8% 0 62% 0); }
  93% { opacity: .9; transform: translate(5px, 1px); clip-path: inset(55% 0 18% 0); }
  95% { opacity: .9; transform: translate(-3px, 0); clip-path: inset(30% 0 40% 0); }
  97% { opacity: .7; transform: translate(2px, 0); clip-path: inset(78% 0 4% 0); }
}
@keyframes fx-glitch-b {
  0%, 90%, 100% { opacity: 0; transform: none; clip-path: inset(0 0 0 0); }
  91% { opacity: .85; transform: translate(4px, 1px); clip-path: inset(60% 0 12% 0); }
  93% { opacity: .85; transform: translate(-5px, 0); clip-path: inset(12% 0 66% 0); }
  95% { opacity: .85; transform: translate(3px, -1px); clip-path: inset(42% 0 30% 0); }
  97% { opacity: .6; transform: translate(-2px, 0); clip-path: inset(2% 0 84% 0); }
}
.fx-floor { position: absolute; left: -60%; right: -60%; bottom: -6%; height: 58%; pointer-events: none; opacity: .32; transform-origin: 50% 100%; transform: rotateX(68deg);
  background-image: linear-gradient(rgba(0, 217, 255, .55) 1.5px, transparent 1.5px), linear-gradient(90deg, rgba(198, 255, 0, .38) 1.5px, transparent 1.5px);
  background-size: 72px 72px; animation: fx-floor 2.6s linear infinite;
  -webkit-mask-image: linear-gradient(to top, #000 0%, rgba(0, 0, 0, .55) 45%, transparent 92%); mask-image: linear-gradient(to top, #000 0%, rgba(0, 0, 0, .55) 45%, transparent 92%); }
.fx-floor::after { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--ar-cyan), var(--ar-lime), var(--ar-cyan), transparent); box-shadow: 0 0 24px var(--ar-cyan); opacity: .6; }
@keyframes fx-floor { to { background-position: 0 72px, 0 0; } }

/* ---------------- 3D reveals, view switch, heading scan ---------------- */
.ar-js .ar-reveal.is-in, .ar-js .bx-card.is-in, .ar-js .bx-findings li.is-in { animation: fx-rise3d .95s var(--ar-ease) var(--d, 0ms) backwards; }
@keyframes fx-rise3d { from { opacity: 0; transform: perspective(1200px) translate3d(0, 54px, -110px) rotateX(18deg); } }
.bx.ar-swap > .bx-sec:not([hidden]) { animation: fx-swap .75s var(--ar-ease) both; transform-origin: 50% 0; }
@keyframes fx-swap { from { opacity: 0; transform: perspective(1600px) translate3d(0, 46px, -140px) rotateX(9deg); } to { opacity: 1; transform: none; } }
.bx-sec > h2 { position: relative; }
.bx-sec:not([hidden]) > h2::after { content: ""; position: absolute; left: 0; bottom: -6px; height: 2px; width: 100%; pointer-events: none; transform-origin: 0 50%;
  background: linear-gradient(90deg, var(--ar-lime), var(--ar-cyan) 40%, transparent 75%); box-shadow: 0 0 12px rgba(198, 255, 0, .6); animation: fx-scan 1.1s var(--ar-ease) .15s both; }
@keyframes fx-scan { from { transform: scaleX(0); opacity: 1; } 60% { opacity: 1; } to { transform: scaleX(1); opacity: .45; } }

/* ---------------- reduced motion ---------------- */
@media (prefers-reduced-motion: reduce) {
  .fx-floor, .fx-warp, .fx-boom, .fx-trail { display: none !important; }
  .ar-title .t1::before, .ar-title .t1::after { display: none; }
  .fx-ring::before { animation: none; }
}
"""

FX_JS = r"""
(() => {
const root = document.documentElement;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const mk = (tag, cls, parent = document.body, html = '') => { const d = document.createElement(tag); d.className = cls; d.setAttribute('aria-hidden', 'true'); d.innerHTML = html; parent.appendChild(d); return d; };
if (!reduce) root.classList.add('fx-3d');

/* ---------------- overlays ---------------- */
const bar = mk('div', 'fx-progress');
const warp = mk('div', 'fx-warp');
document.addEventListener('click', (e) => {
  if (reduce || !e.target.closest('[data-view], .ar-link, .bx-pn-b, .bx-pick-b')) return;
  warp.classList.remove('go'); void warp.offsetWidth; warp.classList.add('go');
}, true);

/* ---------------- render loop: runs only while something moves ---------------- */
let raf = 0, awake = 0;
const wake = () => { awake = performance.now(); if (!raf) raf = requestAnimationFrame(frame); };
const jobs = [];
function frame(t) {
  let busy = false;
  for (const j of jobs) busy = j(t) || busy;
  if (busy || t - awake < 900) raf = requestAnimationFrame(frame); else raf = 0;
}

/* ---------------- inertia smooth scroll (mouse wheel) ---------------- */
let sTarget = 0, sCur = 0, sSet = 0, sLast = 0, sOn = false;
const maxY = () => Math.max(0, root.scrollHeight - innerHeight);
const scrollsInside = (el, dy) => {
  for (; el && el.nodeType === 1 && el !== document.body && el !== root; el = el.parentElement) {
    if (el.scrollHeight <= el.clientHeight + 1) continue;
    const oy = getComputedStyle(el).overflowY;
    if (oy !== 'auto' && oy !== 'scroll' && oy !== 'overlay') continue;
    if (dy > 0 ? el.scrollTop + el.clientHeight < el.scrollHeight - 1 : el.scrollTop > 0) return true;
  }
  return false;
};
if (fine && !reduce) {
  addEventListener('wheel', (e) => {
    if (e.ctrlKey || e.metaKey || e.defaultPrevented || Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
    if (scrollsInside(e.target, e.deltaY)) return;
    e.preventDefault();
    if (!sOn) { sCur = sTarget = sSet = scrollY; sLast = 0; sOn = true; }
    const k = e.deltaMode === 1 ? 36 : (e.deltaMode === 2 ? innerHeight : 1);
    sTarget = clamp(sTarget + clamp(e.deltaY * k, -420, 420), 0, maxY());
    wake();
  }, { passive: false });
  // keys, the scrollbar or the page's own navigation take over immediately
  ['keydown', 'pointerdown', 'touchstart'].forEach((ev) => addEventListener(ev, () => { sOn = false; }, { passive: true }));
  jobs.push((t) => {
    if (!sOn) return false;
    if (Math.abs(scrollY - sSet) > 3) { sOn = false; return false; }
    const dt = Math.min(48, t - (sLast || t)); sLast = t;
    sCur += (sTarget - sCur) * (1 - Math.exp(-dt / 110));
    if (Math.abs(sTarget - sCur) < .5) sCur = sTarget;
    scrollTo({ top: sCur, behavior: 'instant' });
    sSet = scrollY;
    if (sCur === sTarget) { sOn = false; return false; }
    return true;
  });
}

/* ---------------- progress bar ---------------- */
let lastP = -1;
const progress = () => {
  const p = maxY() ? clamp(scrollY / maxY(), 0, 1) : 0;
  if (Math.abs(p - lastP) > .0005) { bar.style.setProperty('--p', p.toFixed(4)); bar.style.setProperty('--pd', p > .01 ? '1' : '0'); lastP = p; }
};
addEventListener('scroll', () => { progress(); wake(); }, { passive: true });
addEventListener('resize', progress, { passive: true });
progress();

/* ---------------- hero depth ---------------- */
const hero = $('#overview');
const hbg = hero && $('.ar-hero-bg', hero);
const court = hero && $('.ar-court', hero);
const hin = hero && $('.ar-hero-in', hero);
const title = hero && $('.ar-title', hero);
$$('.ar-title .t1, .ar-title .t2').forEach((s) => { s.dataset.text = s.textContent; });
if (hbg && !reduce) hbg.insertBefore(mk('div', 'fx-floor', hbg), court || null);
const layers = hero && !reduce ? [['.ar-glow.g1', 28, .45], ['.ar-glow.g2', -24, .3], ['.ar-grid', 10, .2], ['.ar-sparks', 36, .55], ['.fx-floor', -8, .1]]
  .map(([s, d, sy]) => [$(s, hero), d, sy]).filter((l) => l[0]) : [];
let mx = 0, my = 0, cx = 0, cy = 0, heroDone = false;
if (hero && !reduce) jobs.push(() => {
  cx += (mx - cx) * .08; cy += (my - cy) * .08;
  const moving = Math.abs(mx - cx) > .001 || Math.abs(my - cy) > .001;
  if (hero.hidden) return false;
  const h = hero.offsetHeight || innerHeight;
  const p = clamp(scrollY / h, 0, 1);
  if (p >= 1) { if (heroDone) return false; heroDone = true; } else heroDone = false;
  const x = fine ? cx : 0, y = fine ? cy : 0;
  for (const [el, d, sy] of layers) el.style.translate = `${(x * d).toFixed(2)}px ${(y * d + p * h * sy).toFixed(1)}px`;
  if (court) { court.style.translate = `${(x * 16).toFixed(2)}px ${(p * h * .18 + y * 6).toFixed(1)}px`; court.style.rotate = `x ${(p * 24 - y * 3).toFixed(2)}deg`; }
  if (hin) { hin.style.translate = `${(x * -10).toFixed(2)}px ${(p * h * -.16 + y * -6).toFixed(1)}px`; hin.style.opacity = clamp(1 - p * 1.25, 0, 1).toFixed(3); }
  if (title) { const m = Math.hypot(x, y); title.style.rotate = m < .002 ? 'none' : `${(y / m).toFixed(3)} ${(-x / m).toFixed(3)} 0 ${(m * 10).toFixed(2)}deg`; }
  return moving;
});

/* ---------------- cursor, tilt, spotlight, magnet (mouse only) ---------------- */
if (fine) {
  root.classList.add('fx-cur');
  const cur = mk('div', 'fx-cursor', document.body, '<div class="fx-ring"><i></i><i></i><i></i><i></i><b></b></div><div class="fx-dot"></div>');
  const ring = $('.fx-ring', cur), dot = $('.fx-dot', cur), tag = $('b', ring);
  const cv = reduce ? null : mk('canvas', 'fx-trail');
  const ctx = cv?.getContext('2d');
  const fit = () => { if (!cv) return; const r = devicePixelRatio || 1; cv.width = innerWidth * r; cv.height = innerHeight * r; ctx.setTransform(r, 0, 0, r, 0, 0); };
  fit(); addEventListener('resize', fit, { passive: true });
  let px = innerWidth / 2, py = innerHeight / 2, rx = px, ry = py, rw = 38, rh = 38, lockEl = null;
  const pts = [];
  const HOT = 'a[href], button, [role="button"], [data-goto-player], [data-view], [data-scroll], select, summary, label, input[type=checkbox], input[type=radio], th[data-k], th[aria-sort], .bx-th, [tabindex]:not([tabindex="-1"])';
  const TXT = 'input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=button]):not([type=submit]), textarea, [contenteditable="true"]';
  const label = (el) => el.closest('[data-goto-player]') ? 'SELECT' : (el.closest('[data-view], .ar-link') ? 'WARP' : (el.closest('th') ? 'SORT' : 'LOCK'));
  const TILT = '.ar-card, .ar-stat, .ar-aw, .ar-topcard, .bx-pick-b, .ar-hero-stats, .rc-champ, .rc-hl-i';
  const MAG = '.ar-cta, .ar-link, .ar-logo, .bx-theme, .ar-burger, .ar-seg-ctl button, .ar-scroll, .bx-pn-b';
  let tiltEl = null; const mags = new Map(); let magEl = null;
  const glare = (el) => { if (!el.classList.contains('ar-hero-stats') && !el.querySelector(':scope > .fx-glare')) mk('span', 'fx-glare', el); el.classList.add('fx-tilt'); };
  const spot = (el) => { if (!el.querySelector(':scope > .fx-spot')) { el.prepend(mk('span', 'fx-haze', el)); mk('span', 'fx-spot', el); } };

  addEventListener('pointermove', (e) => {
    if (e.pointerType && e.pointerType !== 'mouse') return;
    px = e.clientX; py = e.clientY; cur.classList.add('is-live');
    mx = clamp(px / innerWidth * 2 - 1, -1, 1); my = clamp(py / innerHeight * 2 - 1, -1, 1);
    if (cv) pts.push({ x: px, y: py, t: performance.now() });
    probe(e.target.nodeType === 1 ? e.target : e.target.parentElement);
    wake();
  }, { passive: true });
  // what is under the pointer: lock target, tilt card, magnet, spotlight
  function probe(tg) {
    if (!tg) return;
    cur.classList.toggle('is-text', !!tg.closest(TXT));
    const hot = tg.closest(HOT);
    if (hot) {
      const r = hot.getBoundingClientRect();
      if (r.width <= 560 && r.height <= 300) { lockEl = hot; cur.classList.add('is-lock'); cur.classList.remove('is-big'); tag.textContent = label(hot); }
      else { lockEl = null; cur.classList.remove('is-lock'); cur.classList.add('is-big'); }
    } else { lockEl = null; cur.classList.remove('is-lock', 'is-big'); }
    if (!reduce) {
      const t = tg.closest(TILT);
      if (t !== tiltEl) { tiltEl?.classList.remove('fx-tilting'); tiltEl = t; if (t) { glare(t); t.classList.add('fx-tilting'); } }
      if (t) {
        const r = t.getBoundingClientRect(); const ux = (px - r.left) / r.width, uy = (py - r.top) / r.height;
        const k = r.width > 600 ? 3 : (r.width > 340 || r.height > 300 ? 7 : 11);
        t.style.setProperty('--rx', ((.5 - uy) * k).toFixed(2) + 'deg'); t.style.setProperty('--ry', ((ux - .5) * k).toFixed(2) + 'deg');
        t.style.setProperty('--gx', (ux * 100).toFixed(1) + '%'); t.style.setProperty('--gy', (uy * 100).toFixed(1) + '%');
      }
      const m = tg.closest(MAG);
      magEl = m;
      if (m) {
        const r = m.getBoundingClientRect();
        const s = mags.get(m) || { x: 0, y: 0, tx: 0, ty: 0 };
        s.tx = clamp((px - (r.left + r.width / 2)) * .28, -9, 9); s.ty = clamp((py - (r.top + r.height / 2)) * .38, -7, 7);
        mags.set(m, s);
      }
    }
    const c = tg.closest('.bx-card');
    if (c) { spot(c); const r = c.getBoundingClientRect(); c.style.setProperty('--sx', (px - r.left).toFixed(0) + 'px'); c.style.setProperty('--sy', (py - r.top).toFixed(0) + 'px'); }
  }
  // scrolling moves the page under a still pointer: look again once per frame
  let reprobe = false;
  addEventListener('scroll', () => { if (cur.classList.contains('is-live')) { reprobe = true; wake(); } }, { passive: true });
  jobs.push(() => { if (reprobe) { reprobe = false; probe(document.elementFromPoint(px, py)); } return false; });
  document.addEventListener('pointerleave', () => { cur.classList.remove('is-live'); }, { passive: true });
  root.addEventListener('mouseleave', () => { cur.classList.remove('is-live'); tiltEl?.classList.remove('fx-tilting'); tiltEl = null; magEl = null; mx = my = 0; wake(); });
  addEventListener('blur', () => cur.classList.remove('is-live'));

  addEventListener('pointerdown', (e) => {
    if (e.pointerType !== 'mouse') return;
    cur.classList.add('is-down');
    if (reduce) return;
    const b = mk('div', 'fx-boom');
    b.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
    const cols = ['#C6FF00', '#00D9FF', '#FFFFFF'];
    b.innerHTML = Array.from({ length: 10 }, (_, i) => `<i style="--a:${i * 36 + Math.random() * 20}deg;--r:${26 + Math.random() * 22}px;--c:${cols[i % 3]}"></i>`).join('');
    setTimeout(() => b.remove(), 700);
  }, { passive: true });
  addEventListener('pointerup', () => cur.classList.remove('is-down'), { passive: true });

  jobs.push((t) => {
    let busy = false;
    // ring: chase the pointer, or wrap the locked target like a HUD reticle
    let tx = px, ty = py, tw = 38, th = 38;
    if (lockEl && lockEl.isConnected) { const r = lockEl.getBoundingClientRect(); tx = r.left + r.width / 2; ty = r.top + r.height / 2; tw = r.width + 14; th = r.height + 12; }
    const down = cur.classList.contains('is-down') ? .82 : 1;
    const f = .22;
    rx += (tx - rx) * f; ry += (ty - ry) * f; rw += (tw * down - rw) * f; rh += (th * down - rh) * f;
    ring.style.width = rw.toFixed(1) + 'px'; ring.style.height = rh.toFixed(1) + 'px';
    ring.style.transform = `translate3d(${(rx - rw / 2).toFixed(1)}px, ${(ry - rh / 2).toFixed(1)}px, 0)`;
    dot.style.transform = `translate3d(${px}px, ${py}px, 0)`;
    if (Math.abs(tx - rx) + Math.abs(ty - ry) + Math.abs(tw * down - rw) + Math.abs(th * down - rh) > .5) busy = true;
    // magnetic buttons
    mags.forEach((s, el) => {
      if (el !== magEl) { s.tx = 0; s.ty = 0; }
      s.x += (s.tx - s.x) * .18; s.y += (s.ty - s.y) * .18;
      el.style.translate = `${s.x.toFixed(2)}px ${s.y.toFixed(2)}px`;
      if (el !== magEl && Math.abs(s.x) < .05 && Math.abs(s.y) < .05) { el.style.translate = ''; mags.delete(el); } else busy = true;
    });
    // neon trail
    if (ctx) {
      const now = performance.now(), life = 220;
      while (pts.length && now - pts[0].t > life) pts.shift();
      ctx.clearRect(0, 0, innerWidth, innerHeight);
      if (pts.length > 1) {
        ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        for (let i = 1; i < pts.length; i++) {
          const a = 1 - (now - pts[i].t) / life;
          ctx.strokeStyle = `rgba(${Math.round(198 - 198 * (1 - a))}, ${Math.round(255 - 38 * (1 - a))}, ${Math.round(255 * (1 - a))}, ${(a * .75).toFixed(3)})`;
          ctx.lineWidth = 1 + a * 3.2; ctx.shadowBlur = 12 * a; ctx.shadowColor = '#C6FF00';
          ctx.beginPath(); ctx.moveTo(pts[i - 1].x, pts[i - 1].y); ctx.lineTo(pts[i].x, pts[i].y); ctx.stroke();
        }
        busy = true;
      }
    }
    return busy;
  });
  // the leaving card relaxes back with its CSS transition; clear its tilt values once it has
  document.addEventListener('pointerout', (e) => {
    const t = e.target.closest?.(TILT);
    if (t && !t.contains(e.relatedTarget)) { t.classList.remove('fx-tilting'); if (tiltEl === t) tiltEl = null; }
  }, { passive: true });
}
wake();
})();
"""
