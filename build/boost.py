"""Last layer: performance and home-page design.

Performance (measured on an emulated phone, CPU 4x slower: the page kept the main thread ~68% busy with nobody
touching it, because several endless animations changed background-position, box-shadow, clip-path or an @property
angle, all of which repaint the page every frame):
- endless animations use transform/opacity only, so the compositor runs them without the main thread;
- phones and touch screens get still backgrounds;
- the hero's animations and SVG motion stop while the hero is off screen.

Design:
- home section bar: jump between the home sections, with the current one lit;
- phones: tiles, matches and awards in two columns, long findings folded, slimmer score rows;
- the #1 leaderboard card's photo fills the card; the footer links stay on one line.
"""

JUMPS = [('latest', 'Latest'), ('dashboard', 'Dashboard'), ('board', 'Leaderboard'), ('streaks', 'Final streaks'), ('awards', 'Awards'), ('exec', 'Summary'), ('leaderboard', 'Tables')]


def jump_html():
    return ('<nav class="jb" aria-label="Sections on this page"><div class="jb-in">'
            + ''.join(f'<button type="button" data-jump="{i}">{t}</button>' for i, t in JUMPS) + '</div></nav>')


BOOST_CSS = r"""
/* ================= performance ================= */
/* page backdrop grid: still (it sits at 13% opacity behind everything, and moving it repainted the whole screen) */
.hud-bg::before { animation: none !important; }
/* hero floor: the grid slides by transform inside a masked, tilted frame */
.fx-floor { animation: none !important; background: none !important; overflow: hidden; }
.fx-floor::before { content: ""; position: absolute; left: 0; right: 0; top: -72px; bottom: 0; will-change: transform;
  background-image: linear-gradient(rgba(0, 217, 255, .55) 1.5px, transparent 1.5px), linear-gradient(90deg, rgba(198, 255, 0, .38) 1.5px, transparent 1.5px); background-size: 72px 72px;
  animation: bo-floor 2.6s linear infinite; }
@keyframes bo-floor { to { transform: translateY(72px); } }
/* title glitch: fixed slices that only move and fade */
.ar-title .t1::before { clip-path: inset(30% 0 40% 0); animation-name: bo-glitch-a !important; }
.ar-title .t1::after { clip-path: inset(58% 0 16% 0); animation-name: bo-glitch-b !important; }
@keyframes bo-glitch-a { 0%, 90%, 100% { opacity: 0; transform: none; } 91% { opacity: .9; transform: translate(-4px, -1px); } 93% { opacity: .9; transform: translate(5px, 1px); } 95% { opacity: .9; transform: translate(-3px, 0); } 97% { opacity: .7; transform: translate(2px, 0); } }
@keyframes bo-glitch-b { 0%, 90%, 100% { opacity: 0; transform: none; } 91% { opacity: .85; transform: translate(4px, 1px); } 93% { opacity: .85; transform: translate(-5px, 0); } 95% { opacity: .85; transform: translate(3px, -1px); } 97% { opacity: .6; transform: translate(-2px, 0); } }
/* live dot: a ring that scales instead of a growing shadow */
.ar-live i { position: relative; animation: none !important; }
.ar-live i::after { content: ""; position: absolute; inset: 0; border-radius: 50%; background: rgba(198, 255, 0, .55); animation: bo-ping 2s ease-out infinite; }
@keyframes bo-ping { to { transform: scale(3.2); opacity: 0; } }
/* #1 card: the light runs round the frame by rotating a disc behind the frame's mask, not by repainting a gradient */
.ar-ring-b { animation: none !important; background: none !important; overflow: hidden; }
.ar-ring-b::before { content: ""; position: absolute; left: 50%; top: 50%; width: 220%; aspect-ratio: 1; margin: -110% 0 0 -110%; will-change: transform;
  background: conic-gradient(#FFD23F, #C6FF00 18%, #00D9FF 32%, rgba(0, 217, 255, 0) 45%, rgba(255, 210, 63, 0) 62%, #FFD23F 82%, #FFD23F); animation: bo-spin 6s linear infinite; }
@keyframes bo-spin { to { transform: rotate(360deg); } }
/* hero out of sight: stop everything in it */
.ar-hero.hero-off *, .ar-hero.hero-off *::before, .ar-hero.hero-off *::after { animation-play-state: paused !important; }
@media (max-width: 760px), (pointer: coarse) {
  body::before, .hud-bg::after, .ar-glow, .fx-floor::before, .ar-title .t1::before, .ar-title .t1::after, .ar-ring-b::before { animation: none !important; }
  .ar-glow { filter: none; opacity: .4; }
  .ar-sparks, .ar-court .shuttle { display: none; }
  .ar-court .ln, .ar-court .net-top, .ar-court .shuttle circle { filter: none; }
  .bx.ar-swap > .bx-sec:not([hidden]) { animation: bo-fade .25s ease-out both; }   /* a plain fade: the 3D swing re-rasters a whole page */
  .ar-js .ar-reveal.is-in, .ar-js .bx-card.is-in, .ar-js .bx-findings li.is-in { animation: bo-rise .45s ease-out var(--d, 0ms) backwards; }
}
@keyframes bo-fade { from { opacity: 0; } }
@keyframes bo-rise { from { opacity: 0; transform: translateY(22px); } }
/* cards far from the screen are not laid out or painted until they come near */
.bx-sec .bx-card, .sk-card, .bx-findings li, .bx-callout { content-visibility: auto; contain-intrinsic-size: auto 420px; }
.sk-card { contain-intrinsic-size: auto 720px; }
@media (prefers-reduced-motion: reduce) { .fx-floor::before, .ar-live i::after, .ar-ring-b::before { animation: none !important; } }

/* ================= home: section bar ================= */
html, body { overflow-x: clip; }   /* the 3D page swing may reach past the right edge for a moment */
.jb { position: sticky; top: 68px; z-index: 30; margin: -6px 0 0; padding: 8px 0; pointer-events: none; }
.jb-in { pointer-events: auto; display: flex; gap: 4px; width: fit-content; max-width: 100%; margin: 0 auto; padding: 5px; border-radius: 14px; overflow-x: auto; scrollbar-width: none;
  background: #0B0F17; border: 1px solid var(--ar-line2, rgba(255, 255, 255, .12)); box-shadow: 0 14px 34px -18px #000; }
.jb-in::-webkit-scrollbar { display: none; }
.jb button { flex: none; padding: 9px 14px 8px; border: 0; border-radius: 10px; cursor: pointer; white-space: nowrap; font: 700 11px/1 var(--ar-h, var(--m-display)); letter-spacing: .08em; text-transform: uppercase; color: var(--ar-mut); background: none; transition: color .2s ease, background-color .2s ease; }
.jb button:hover { color: var(--ar-fg); }
.jb button:focus-visible { outline: 2px solid var(--ar-cyan); outline-offset: -2px; }
.jb button.on { color: #0A0E14; background: var(--ar-lime); }
.ar-block, #exec, #leaderboard { scroll-margin-top: 130px; }

/* ================= #1 card: photo fills the card ================= */
@media (min-width: 981px) {
  .ar-card.is-champ { display: flex; flex-direction: column; }
  .ar-card.is-champ > .ar-card-ph { flex: 1 1 auto; aspect-ratio: auto !important; min-height: 420px; }
  .ar-card.is-champ > .ar-card-ph img { object-position: 50% 12%; }
  .ar-card.is-champ .ar-card-body { flex: 0 0 auto; }
}
/* ================= footer: links on one line ================= */
@media (min-width: 1101px) { .af-links { flex-wrap: nowrap; gap: 0; } .af-links a { padding: 8px 9px; font-size: 12.5px; white-space: nowrap; } .af-top { gap: 18px 14px; } }

/* ================= phones: a shorter home page ================= */
@media (max-width: 620px) {
  .ar-stat .ar-stack > * { width: 27px; height: 27px; }
  .jb { top: 66px; margin-inline: -6px; }
  .jb button { padding: 10px 12px 9px; font-size: 10.5px; }
  .rc-hl { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 10px; }
  .rc-hl-i { padding: 13px 14px; align-content: start; } .rc-hl-i b { font-size: 21px; } .rc-hl-i small { font-size: 9.5px; letter-spacing: .1em; padding-right: 22px; } .rc-hl-i > span:last-child { font-size: 11.5px; }
  .rc-hl-ic { right: 10px; top: 10px; } .rc-hl-ic .ar-ic { width: 18px; height: 18px; }
  .rc-ml { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 8px; }
  .rc-ml > .rc-m:last-child:nth-child(odd) { grid-column: 1 / -1; }
  .rc-m { grid-template-columns: minmax(0, 1fr); grid-template-areas: "l" "s" "w" "x"; padding: 9px 10px; gap: 3px; } .rc-m-s { justify-self: start; } .rc-m-w { font-size: 12.5px; line-height: 1.3; } .rc-m-x { font-size: 11.5px; line-height: 1.3; } .rc-m-l { font-size: 9.5px; }
  .ar-awards { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 10px; }
  .ar-aw { grid-template-columns: auto minmax(0, 1fr) !important; grid-template-areas: "ph ph" "l l" "n n" "v v" "w w" !important; padding: 14px 12px !important; gap: 5px 8px !important; align-content: start; }
  .ar-aw-ic { position: absolute; right: 10px; top: 10px; width: 30px; height: 30px; border-radius: 10px; } .ar-aw-ic .ar-ic { width: 16px; height: 16px; }
  .ar-aw-i { width: 46px; height: 46px; justify-self: start; } .ar-aw-pair { justify-self: start; } .ar-aw-pair .ar-aw-i { width: 42px; height: 42px; }
  .ar-aw-l { font-size: 10px; letter-spacing: .1em; line-height: 1.3; } .ar-aw-n { font-size: 15.5px; line-height: 1.2; } .ar-aw-v { font-size: 11.5px; line-height: 1.35; } .ar-aw-v b { font-size: 15px; }
  .ar-aw-why { font-size: 11px; line-height: 1.45; padding-top: 8px; }
  /* long findings fold to six lines */
  .bx-findings li.fold .bx-ft { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 6; overflow: hidden; }
  .fold-b { margin: 8px 0 2px; padding: 8px 14px; border-radius: 10px; cursor: pointer; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .1em; text-transform: uppercase; color: var(--ar-lime); background: rgba(198, 255, 0, .07); border: 1px solid rgba(198, 255, 0, .3); }
  /* best scores: the bar becomes the row's bottom edge */
  .bs .bs-row { grid-template-areas: "rk pl n" "rk when tot" !important; overflow: hidden; padding-bottom: 13px; }
  .bs .bs-row .sk-bar { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; border-radius: 0; }
}
@media (min-width: 621px) { .fold-b { display: none; } }
"""

BOOST_JS = r"""
(() => {
const root = document.documentElement;
const $ = (s, el = document) => el.querySelector(s); const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* hero out of sight (scrolled away or on another page): stop its animations and SVG motion */
const hero = $('.ar-hero');
const lite = matchMedia('(max-width: 760px), (pointer: coarse)').matches;
// the flying shuttle repaints the whole court every frame: on phones it rests mid-flight
const svgMotion = (on) => { $$('svg', hero).forEach((g) => { if (g.pauseAnimations) on && !lite ? g.unpauseAnimations() : g.pauseAnimations(); }); };
if (hero && lite) { $$('svg', hero).forEach((g) => { try { g.setCurrentTime(1.1); } catch (e) { /* not started */ } }); svgMotion(false); document.addEventListener('visibilitychange', () => svgMotion(true)); }
if (hero && 'IntersectionObserver' in window) {
  new IntersectionObserver((es) => {
    const on = es[es.length - 1].isIntersecting; hero.classList.toggle('hero-off', !on);
    if (!root.classList.contains('hud-modal-open')) svgMotion(on);
  }).observe(hero);
}

/* home section bar */
const bar = $('.jb'); const ex = $('#summary > h2'); if (ex && !ex.id) ex.id = 'exec';
if (bar) {
  const btn = $$('[data-jump]', bar); const strip = $('.jb-in', bar);
  const tgt = btn.map((b) => document.getElementById(b.dataset.jump));
  const off = () => ($('#ar-nav')?.offsetHeight || 62) + bar.offsetHeight + 6;
  let cur = -1, tick = 0, hold = 0;
  const mark = (i) => {
    if (i === cur) return; cur = i;
    btn.forEach((b, k) => { b.classList.toggle('on', k === i); if (k === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
    const b = btn[i]; if (b && strip.scrollWidth > strip.clientWidth) strip.scrollTo({ left: b.offsetLeft - (strip.clientWidth - b.offsetWidth) / 2, behavior: reduce ? 'auto' : 'smooth' });
  };
  // section positions are measured once in a while, not on every scroll step
  let tops = [], line = 0, at = -1e9;
  const measure = () => { at = performance.now(); line = off() + 40; tops = tgt.map((t) => (t ? t.getBoundingClientRect().top + scrollY : Infinity)); };
  const spy = () => {
    tick = 0; const now = performance.now(); if (now < hold || bar.closest('[hidden]')) return;
    if (now - at > 700) measure();
    let i = -1; const y = scrollY + line;
    tops.forEach((t, k) => { if (t <= y) i = k; });
    mark(i);
  };
  let rest = 0;
  addEventListener('scroll', () => { if (!tick) tick = requestAnimationFrame(spy); clearTimeout(rest); rest = setTimeout(() => { at = -1e9; spy(); }, 260); }, { passive: true });
  // a jump keeps correcting until the page has stopped moving; any scroll by the reader ends it
  let settle = 0; const stop = () => { if (settle) { clearInterval(settle); settle = 0; hold = 0; } };
  ['wheel', 'touchstart', 'keydown', 'pointerdown'].forEach((n) => addEventListener(n, stop, { passive: true }));
  bar.addEventListener('click', (e) => {
    const b = e.target.closest('[data-jump]'); if (!b) return;
    const i = btn.indexOf(b), t = tgt[i]; if (!t) return;
    stop(); hold = performance.now() + 4000; mark(i);
    const go = (smooth) => scrollTo({ top: t.getBoundingClientRect().top + scrollY - off(), behavior: smooth && !reduce ? 'smooth' : 'auto' });
    go(true);
    // content may still be settling on the way: land exactly on the heading
    let y = -1, n = 0, ok = 0;
    settle = setInterval(() => {
      const moving = Math.abs(scrollY - y) > 2; y = scrollY; if (++n > 18) return stop(); if (moving) { ok = 0; return; }
      const end = scrollY + innerHeight > root.scrollHeight - 4;
      const d = t.getBoundingClientRect().top - off(); if (Math.abs(d) > 6 && !(end && d > 0)) { go(false); ok = 0; y = scrollY; } else if (++ok > 4) stop();
    }, 180);
  });
  addEventListener('load', () => setTimeout(spy, 400));
}

/* the home cards skipped during loading are prepared one at a time while the phone is idle, so the first scroll finds them ready */
const idle = window.requestIdleCallback ? (f) => requestIdleCallback(f, { timeout: 1500 }) : (f) => setTimeout(f, 60);
addEventListener('load', () => setTimeout(() => {
  const q = $$('#summary .bx-card, #summary .sk-card, #summary .bx-findings li, #summary .bx-callout');
  const next = () => { const el = q.shift(); if (!el) return; el.style.contentVisibility = 'visible'; if (el.offsetParent) void el.offsetHeight; idle(next); };
  idle(next);
}, 500));

/* phones: fold long findings */
if (matchMedia('(max-width: 620px)').matches) {
  const fold = () => $$('.bx-findings li').forEach((li) => {
    const ft = $('.bx-ft', li); if (!ft || $('.fold-b', li) || !ft.offsetParent) return;
    li.classList.add('fold');
    if (ft.scrollHeight - ft.clientHeight < 24) { li.classList.remove('fold'); return; }
    const b = document.createElement('button'); b.type = 'button'; b.className = 'fold-b'; b.textContent = 'Read more'; b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', () => { const open = li.classList.toggle('fold') === false; b.textContent = open ? 'Show less' : 'Read more'; b.setAttribute('aria-expanded', String(open)); });
    ft.after(b);
  });
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => setTimeout(fold, 60));
}
})();
"""
