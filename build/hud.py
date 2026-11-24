"""Esports HUD layer: a gaming restyle of the report sections (section banners, briefing boxes, HUD panels,
scoreboard tables, bullets, chips, page backdrop). HUD_JS adds the page backdrop and numbers the section banners.
The champions pop-up is in victory.py.
"""

HUD_CSS = r"""
/* =====================================================================
   HUD — esports restyle of the report sections
   ===================================================================== */
/* ---------------- page backdrop: perspective floor + slow scan ---------------- */
.hud-bg { position: fixed; inset: 0; z-index: -1; pointer-events: none; overflow: hidden; }
.hud-bg::before { content: ""; position: absolute; left: -50%; right: -50%; bottom: -8vh; height: 55vh; transform: perspective(420px) rotateX(70deg); transform-origin: 50% 100%; opacity: .13;
  background-image: linear-gradient(rgba(0, 217, 255, .9) 1px, transparent 1px), linear-gradient(90deg, rgba(198, 255, 0, .7) 1px, transparent 1px); background-size: 80px 80px;
  -webkit-mask-image: linear-gradient(to top, #000, transparent 85%); mask-image: linear-gradient(to top, #000, transparent 85%); animation: hud-floor 6s linear infinite; }
.hud-bg::after { content: ""; position: absolute; left: 0; right: 0; top: -20vh; height: 20vh; opacity: .5;
  background: linear-gradient(180deg, transparent, rgba(0, 217, 255, .035) 60%, rgba(198, 255, 0, .05) 98%, transparent); animation: hud-scan 11s linear infinite; }
@keyframes hud-floor { to { background-position: 0 80px, 0 0; } }
@keyframes hud-scan { to { transform: translateY(140vh); } }

/* ---------------- section banners ---------------- */
.bx-sec > h2[data-idx] { position: relative; overflow: hidden; isolation: isolate; padding: 26px 0 16px; margin-top: 6px; gap: 16px;
  font-size: clamp(26px, 3.3vw, 42px); letter-spacing: .07em; border-bottom: 1px solid var(--ar-line); text-shadow: 0 0 30px rgba(0, 217, 255, .25); }
.bx-sec > h2[data-idx]::before { content: attr(data-idx) !important; width: auto !important; height: auto !important; border-radius: 0 !important; box-shadow: 0 0 18px rgba(198, 255, 0, .45) !important;
  background: var(--ar-lime) !important; color: #0A0E15; font: 800 12px/1 var(--ar-h, var(--m-display)); letter-spacing: .18em; padding: 8px 14px 7px 10px; text-shadow: none;
  clip-path: polygon(0 0, 100% 0, calc(100% - 9px) 100%, 0 100%); align-self: center; }
.bx-sec:not([hidden]) > h2[data-idx]::after { bottom: 0 !important; }
.hud-wm { position: absolute; right: -6px; bottom: -.18em; z-index: -1; pointer-events: none; white-space: nowrap; font: 900 clamp(60px, 9vw, 132px)/1 var(--ar-h, var(--m-display));
  letter-spacing: .02em; color: transparent; -webkit-text-stroke: 1px rgba(0, 217, 255, .13); text-shadow: none; opacity: .9; }
.ar-head { position: relative; isolation: isolate; }
.ar-head .hud-wm { bottom: -.05em; -webkit-text-stroke-color: rgba(198, 255, 0, .10); }
@media (max-width: 700px) { .hud-wm { font-size: 64px; } .bx-sec > h2[data-idx] { padding-top: 18px; } }

/* ---------------- section intro = mission briefing ---------------- */
.bx-sec > p.bx-prose { position: relative; max-width: none; margin: 0; padding: 34px 24px 18px 26px; border-radius: 4px 18px 18px 4px; color: #C3CBD8;
  background: linear-gradient(90deg, rgba(0, 217, 255, .08), rgba(17, 23, 34, .55) 30%, rgba(17, 23, 34, .35)); border: 1px solid var(--ar-line); border-left: 3px solid var(--ar-cyan);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .03); }
.bx-sec > p.bx-prose::before { content: "// BRIEFING"; position: absolute; left: 26px; top: 12px; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .22em; color: var(--ar-cyan); }
.bx-sec > p.bx-prose b { color: #fff; }

/* ---------------- HUD panels ---------------- */
.bx-card, .bx-findings li, .bx-callout, .bx-pr-verdict { border-radius: 14px !important; }
.bx-card { position: relative; }
.bx-card::after, .bx-findings li > .bx-ft::after { content: ""; position: absolute; inset: -1px; pointer-events: none; border-radius: inherit; z-index: 2; opacity: .8;
  background: linear-gradient(var(--ar-lime), var(--ar-lime)) left top / 18px 2px no-repeat, linear-gradient(var(--ar-lime), var(--ar-lime)) left top / 2px 18px no-repeat,
    linear-gradient(var(--ar-cyan), var(--ar-cyan)) right bottom / 18px 2px no-repeat, linear-gradient(var(--ar-cyan), var(--ar-cyan)) right bottom / 2px 18px no-repeat; transition: opacity .3s ease; }
.bx-findings li > .bx-ft::after { display: none; }
.bx-card:hover::after { opacity: 1; filter: drop-shadow(0 0 6px rgba(198, 255, 0, .7)); }
.bx-card-head { padding-bottom: 12px; margin-bottom: 4px; border-bottom: 1px dashed rgba(137, 147, 164, .2); }
.bx-card-head h3 { display: flex; align-items: center; gap: 10px; font-family: var(--ar-h, var(--m-display)) !important; font-size: 13.5px !important; font-weight: 700 !important;
  letter-spacing: .1em !important; text-transform: uppercase; }
.bx-card-head h3::before { content: ""; flex: none; width: 8px; height: 10px; background: var(--ar-lime); clip-path: polygon(0 0, 100% 50%, 0 100%); filter: drop-shadow(0 0 4px var(--ar-lime)); }
.bx-tag { border-radius: 4px !important; clip-path: polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%); padding-left: 12px !important; padding-right: 12px !important; }
.bx-note { font-size: 12.5px; }

/* ---------------- scoreboard tables ---------------- */
.bx-tw { border: 1px solid rgba(0, 217, 255, .12); background: rgba(5, 8, 13, .55); }
.bx-table thead th { font-family: var(--ar-h, var(--m-display)) !important; font-size: 9.5px !important; letter-spacing: .16em !important; border-bottom: 2px solid rgba(0, 217, 255, .35) !important; }
.bx-table thead th .bx-sort { font: inherit !important; letter-spacing: inherit; color: inherit; text-transform: uppercase; }
.bx-table thead th[aria-sort="ascending"], .bx-table thead th[aria-sort="descending"] { color: var(--ar-lime) !important; }
.bx-table tbody tr:nth-child(even) td { background: rgba(255, 255, 255, .018); }
.bx-table tbody tr td:first-child { box-shadow: inset 0 0 0 transparent; transition: box-shadow .2s ease; }
.bx-table tbody tr:hover td { background: rgba(198, 255, 0, .045) !important; }
.bx-table tbody tr:hover td:first-child { box-shadow: inset 3px 0 0 var(--ar-lime); }
.bx-table td.num { font-family: var(--m-body); font-variant-numeric: tabular-nums; }

/* ---------------- bullets, callouts, awards ---------------- */
.bx-list { list-style: none !important; padding-left: 0 !important; display: grid; gap: 10px; }
.bx-list > li { position: relative; padding: 2px 0 10px 24px !important; border-bottom: 1px solid rgba(137, 147, 164, .08); list-style: none !important; }
.bx-list > li:last-child { border-bottom: 0; padding-bottom: 2px !important; }
.bx-list > li::before { content: "" !important; position: absolute; left: 4px; top: .62em; width: 8px; height: 8px; transform: rotate(45deg); border-radius: 1px;
  background: var(--ar-lime); box-shadow: 0 0 8px rgba(198, 255, 0, .7); display: block !important; }
.bx-list > li:nth-child(even)::before { background: var(--ar-cyan); box-shadow: 0 0 8px rgba(0, 217, 255, .7); }
.bx-list > li > b:first-child { color: #fff; }
.bx-callout { position: relative; padding-top: 36px !important; }
.bx-callout::before { content: "// FIELD GUIDE"; position: absolute; left: 20px; top: 13px; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .22em; color: var(--ar-cyan); }
.bx-awards > div { position: relative; border-left: 2px solid rgba(198, 255, 0, .5); padding-left: 14px; }
.bx-awards dt { font-family: var(--ar-h, var(--m-display)); text-transform: uppercase; letter-spacing: .12em; font-size: 11px; color: var(--ar-lime); }
.bx-pr-verdict { border-left: 3px solid var(--ar-lime) !important; }
.bx-foot { border-top: 1px solid var(--ar-line); padding-top: 18px; font-size: 12px; color: var(--ar-mut); }

/* ---------------- while the champions pop-up is open ---------------- */
html.hud-modal-open { overflow: hidden; }
html.hud-modal-open body > :not(.wp), html.hud-modal-open body > :not(.wp) *, html.hud-modal-open body > :not(.wp)::before, html.hud-modal-open body > :not(.wp)::after,
html.hud-modal-open .hud-bg::before, html.hud-modal-open .hud-bg::after { animation-play-state: paused !important; }
@media (prefers-reduced-motion: reduce) { .hud-bg::before, .hud-bg::after { animation: none !important; } }
"""

HUD_JS = r"""
(() => {
const root = document.documentElement;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

/* page backdrop */
const bg = document.createElement('div'); bg.className = 'hud-bg'; bg.setAttribute('aria-hidden', 'true'); document.body.prepend(bg);

/* section banners: running number + outline watermark */
let n = 0;
$$('.bx-sec > h2').forEach((h) => {
  n += 1; h.dataset.idx = String(n).padStart(2, '0') + ' //';
  const wm = document.createElement('span'); wm.className = 'hud-wm'; wm.setAttribute('aria-hidden', 'true');
  wm.textContent = h.textContent.trim().split(/\s+/)[0]; h.appendChild(wm);
});
$$('.ar-head').forEach((hd) => {
  const h = $('.ar-h', hd); if (!h) return;
  const wm = document.createElement('span'); wm.className = 'hud-wm'; wm.setAttribute('aria-hidden', 'true');
  wm.textContent = h.textContent.trim().split(/\s+/).pop(); hd.appendChild(wm);
});
})();
"""
