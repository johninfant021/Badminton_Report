"""Arena visual system: dark esports theme layered over the report's existing styles."""

ARENA_CSS = r"""
/* =====================================================================
   ARENA — dark esports theme. Overrides the earlier layers' tokens, then
   restyles structure. Palette: bg #080B12, card #111722, lime #C6FF00,
   cyan #00D9FF, text #F5F7FA, muted #8993A4.
   ===================================================================== */
:root:root:root, :root:root:root[data-theme] {
  --ar-bg: #080B12; --ar-card: #111722; --ar-card2: #0D121B; --ar-lime: #C6FF00; --ar-cyan: #00D9FF; --ar-fg: #F5F7FA; --ar-mut: #8993A4;
  --ar-line: rgba(137, 147, 164, .14); --ar-line2: rgba(137, 147, 164, .22); --ar-red: #FF4D6D; --ar-gold: #FFD23F;
  --ar-glass: linear-gradient(180deg, rgba(23, 31, 46, .78), rgba(17, 23, 34, .78));
  --ar-shadow: 0 1px 0 rgba(255, 255, 255, .04) inset, 0 24px 48px -28px rgba(0, 0, 0, .9);
  --ar-ease: cubic-bezier(.2, .8, .2, 1);
  --m-bg: #080B12; --m-panel: #111722; --m-fg: #F5F7FA; --m-muted: #8993A4; --m-line: rgba(137, 147, 164, .14); --m-soft: rgba(255, 255, 255, .035);
  --m-ok: #C6FF00; --m-bad: #FF4D6D;
  --m-shadow: 0 1px 0 rgba(255, 255, 255, .04) inset, 0 24px 48px -28px rgba(0, 0, 0, .9);
  --m-shadow-sm: 0 1px 0 rgba(255, 255, 255, .04) inset, 0 8px 18px -12px rgba(0, 0, 0, .8);
  --m-shadow-hover: 0 1px 0 rgba(255, 255, 255, .05) inset, 0 30px 60px -28px rgba(0, 0, 0, .95);
  --g-fill: rgba(17, 23, 34, .78); --g-edge: rgba(137, 147, 164, .16); --g-hi: rgba(255, 255, 255, .05);
  --c-coral: #C6FF00; --c-violet: #00D9FF; --c-blue: #4D8DFF; --c-amber: #FFB020; --c-green: #2BF0A0; --c-pink: #FF4FD8;
  --c-cyan: #00D9FF; --c-lime: #C6FF00; --c-indigo: #8B7CFF; --c-slate: #8993A4; --gold: #FFD23F;
  --series-1: #C6FF00; --series-2: #00D9FF; --series-3: #B57BFF; --series-4: #FFB020; --series-5: #FF4FA3; --series-6: #4D8DFF; --series-7: #FF6B3D; --series-8: #2BF0A0;
  --color-border-line: rgba(137, 147, 164, .16); --color-warn: #FFB020; --color-ok: #C6FF00; --color-bad: #FF4D6D;
  --cds-chart-grid: rgba(137, 147, 164, .10); --cds-chart-axis: rgba(137, 147, 164, .28); --cds-chart-reference: #8993A4; --cds-chart-muted: rgba(137, 147, 164, .35);
  --cds-surface-popover: rgba(10, 14, 22, .96); --cds-border: rgba(0, 217, 255, .35); --cds-shadow-popover: 0 18px 40px rgba(0, 0, 0, .7), 0 0 0 1px rgba(0, 217, 255, .12);
  --cds-text-secondary: #8993A4;
  --m-display: "Orbitron", "Inter", ui-sans-serif, system-ui, sans-serif;
  --m-body: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  --m-mono: "Inter", ui-sans-serif, system-ui, sans-serif;
  --ar-h: "Orbitron", "Inter", sans-serif;
  color-scheme: dark;
}
html { background: var(--ar-bg); scroll-padding-top: 84px; }
body.bx-web { background: var(--ar-bg); color: var(--ar-fg); font-family: var(--m-body); font-feature-settings: "cv11", "ss01", "tnum"; padding: 0 0 72px; }
body.bx-web::before {
  background:
    radial-gradient(40% 30% at 85% 12%, rgba(0, 217, 255, .10), transparent 70%),
    radial-gradient(38% 30% at 10% 40%, rgba(198, 255, 0, .06), transparent 70%),
    radial-gradient(40% 34% at 70% 92%, rgba(0, 217, 255, .07), transparent 70%);
  filter: none;
}
body.bx-web::after {
  content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none; opacity: .5;
  background-image: linear-gradient(rgba(137, 147, 164, .05) 1px, transparent 1px), linear-gradient(90deg, rgba(137, 147, 164, .05) 1px, transparent 1px);
  background-size: 56px 56px; mask-image: radial-gradient(80% 60% at 50% 30%, #000 30%, transparent 85%);
}
::selection { background: rgba(198, 255, 0, .3); color: #fff; }
.bx-theme, .bx > .bx-hero, .bx > .bx-tabs, .bx-squad-wrap, #summary > .bx-kpis { display: none !important; }

/* ---------------- top navigation ---------------- */
.ar-nav { position: sticky; top: 0; z-index: 50; transition: background .3s ease, box-shadow .3s ease, border-color .3s ease; border-bottom: 1px solid transparent; }
.ar-nav.is-stuck, .ar-nav:has(.ar-menu.open) { background: rgba(8, 11, 18, .82); -webkit-backdrop-filter: blur(18px) saturate(1.4); backdrop-filter: blur(18px) saturate(1.4); border-bottom-color: var(--ar-line); box-shadow: 0 10px 30px -18px rgba(0, 0, 0, .9); }
.ar-nav-in { max-width: 1360px; margin: 0 auto; height: 68px; padding: 0 max(16px, env(safe-area-inset-left)); display: flex; align-items: center; gap: 22px; }
.ar-logo { display: inline-flex; align-items: center; gap: 10px; color: var(--ar-fg); text-decoration: none; font-family: var(--ar-h); font-weight: 800; font-size: 14px; letter-spacing: .14em; white-space: nowrap; }
.ar-logo b { color: var(--ar-lime); font-weight: 800; margin-left: .35em; }
.ar-logo-ic { width: 30px; height: 30px; padding: 5px; border-radius: 10px; color: #0a0f00; background: var(--ar-lime); box-shadow: 0 0 22px rgba(198, 255, 0, .45); }
.ar-links { position: relative; display: flex; align-items: center; gap: 2px; margin-left: auto; padding: 4px; border-radius: 14px; background: rgba(17, 23, 34, .6); border: 1px solid var(--ar-line); }
.ar-link {
  position: relative; z-index: 1; padding: 9px 13px; border-radius: 10px; color: var(--ar-mut); text-decoration: none;
  font-size: 13px; font-weight: 600; letter-spacing: .01em; white-space: nowrap; transition: color .2s ease;
}
.ar-link:hover { color: var(--ar-fg); }
.ar-link.is-on { color: #0a0f00; }
.ar-link:focus-visible, .ar-logo:focus-visible { outline: 2px solid var(--ar-cyan); outline-offset: 2px; }
.ar-ind {
  position: absolute; z-index: 0; top: 4px; bottom: 4px; left: 0; width: var(--w, 0); transform: translateX(var(--x, 0)); border-radius: 10px; opacity: 0;
  background: linear-gradient(135deg, #D8FF3D, var(--ar-lime)); box-shadow: 0 0 20px rgba(198, 255, 0, .45), inset 0 1px 0 rgba(255, 255, 255, .5);
  transition: transform .45s var(--ar-ease), width .45s var(--ar-ease), opacity .2s ease;
}
.ar-ind.on { opacity: 1; }
.ar-live { display: inline-flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--ar-mut); white-space: nowrap; }
.ar-live i { width: 8px; height: 8px; border-radius: 50%; background: var(--ar-lime); box-shadow: 0 0 0 0 rgba(198, 255, 0, .6); animation: ar-pulse 2s infinite; }
@keyframes ar-pulse { 70% { box-shadow: 0 0 0 9px rgba(198, 255, 0, 0); } 100% { box-shadow: 0 0 0 0 rgba(198, 255, 0, 0); } }
.ar-burger { display: none; width: 44px; height: 44px; margin-left: auto; border-radius: 12px; border: 1px solid var(--ar-line2); background: rgba(17, 23, 34, .8); cursor: pointer; padding: 0 12px; flex-direction: column; justify-content: center; gap: 5px; }
.ar-burger span { display: block; height: 2px; border-radius: 2px; background: var(--ar-fg); transition: transform .3s var(--ar-ease), opacity .2s ease; }
.ar-burger[aria-expanded=true] span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.ar-burger[aria-expanded=true] span:nth-child(2) { opacity: 0; }
.ar-burger[aria-expanded=true] span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }
.ar-menu { display: grid; gap: 4px; padding: 6px 16px 18px; max-width: 1360px; margin: 0 auto; }
.ar-menu[hidden] { display: none; }
.ar-menu .ar-link { padding: 14px 16px; font-size: 16px; border-radius: 12px; background: rgba(17, 23, 34, .7); border: 1px solid var(--ar-line); transition: color .2s ease; }
.ar-menu.open .ar-link { animation: ar-drop .38s var(--ar-ease) backwards; }
@keyframes ar-drop { from { opacity: 0; transform: translateY(-8px); } }
.ar-menu.open .ar-link:nth-child(2) { animation-delay: .03s; } .ar-menu.open .ar-link:nth-child(3) { animation-delay: .06s; }
.ar-menu.open .ar-link:nth-child(4) { animation-delay: .09s; } .ar-menu.open .ar-link:nth-child(5) { animation-delay: .12s; }
.ar-menu.open .ar-link:nth-child(6) { animation-delay: .15s; } .ar-menu.open .ar-link:nth-child(7) { animation-delay: .18s; }
.ar-menu.open .ar-link:nth-child(8) { animation-delay: .21s; }
.ar-menu .ar-link.is-on { color: #0a0f00; background: var(--ar-lime); border-color: transparent; }
@media (max-width: 1180px) { .ar-live { display: none; } }
@media (max-width: 1040px) { .ar-links { display: none; } .ar-burger { display: inline-flex; } }
@media (min-width: 1041px) { .ar-menu { display: none !important; } }

/* ---------------- hero ---------------- */
.ar-hero { position: relative; min-height: 100svh; margin-top: -68px; padding: 120px max(20px, env(safe-area-inset-left)) 110px; display: grid; align-items: center; overflow: hidden; isolation: isolate; }
.ar-hero[hidden] { display: none; }
.ar-hero-bg { position: absolute; inset: 0; z-index: -1; background: radial-gradient(120% 80% at 50% 110%, rgba(198, 255, 0, .10), transparent 60%), linear-gradient(180deg, #05070C 0%, #080B12 55%, #0A0F17 100%); }
.ar-glow { position: absolute; border-radius: 50%; filter: blur(70px); opacity: .55; }
.ar-glow.g1 { width: 46vw; height: 46vw; left: -12vw; top: -14vw; background: radial-gradient(circle, rgba(0, 217, 255, .35), transparent 65%); animation: ar-float 16s ease-in-out infinite alternate; }
.ar-glow.g2 { width: 40vw; height: 40vw; right: -10vw; top: 6vh; background: radial-gradient(circle, rgba(198, 255, 0, .22), transparent 65%); animation: ar-float 20s ease-in-out infinite alternate-reverse; }
@keyframes ar-float { to { transform: translate3d(4vw, 3vh, 0) scale(1.08); } }
.ar-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(0, 217, 255, .06) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 217, 255, .06) 1px, transparent 1px); background-size: 64px 64px; mask-image: radial-gradient(70% 60% at 50% 35%, #000, transparent 80%); }
.ar-court { position: absolute; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; opacity: .7; }
.ar-court .floor { fill: url(#ar-fl); }
.ar-court .ln { stroke: var(--ar-lime); stroke-width: 2.2; stroke-linecap: round; opacity: .55; filter: drop-shadow(0 0 6px rgba(198, 255, 0, .7)); stroke-dasharray: 1; stroke-dashoffset: 1; animation: ar-draw 2.2s var(--ar-ease) .2s forwards; }
.ar-court .net { fill: rgba(0, 217, 255, .035); stroke: rgba(0, 217, 255, .18); stroke-width: 1; }
.ar-court .net-top { stroke: var(--ar-cyan); stroke-width: 3; filter: drop-shadow(0 0 8px var(--ar-cyan)); }
.ar-court .arc { fill: none; stroke: rgba(245, 247, 250, .12); stroke-width: 1.5; stroke-dasharray: 3 9; }
.ar-court .shuttle circle { fill: #fff; filter: drop-shadow(0 0 10px #fff); }
.ar-court .shuttle path { stroke: rgba(255, 255, 255, .85); stroke-width: 2.4; stroke-linecap: round; }
@keyframes ar-draw { to { stroke-dashoffset: 0; } }
.ar-sparks i { position: absolute; left: calc(var(--i) * 7.3% + 2%); bottom: -10px; width: 3px; height: 3px; border-radius: 50%; background: var(--ar-lime); box-shadow: 0 0 8px var(--ar-lime); opacity: 0; animation: ar-spark 9s linear infinite; animation-delay: calc(var(--i) * -.67s); }
.ar-sparks i:nth-child(3n) { background: var(--ar-cyan); box-shadow: 0 0 8px var(--ar-cyan); }
@keyframes ar-spark { 0% { transform: translateY(0); opacity: 0; } 15% { opacity: .9; } 100% { transform: translateY(-85vh); opacity: 0; } }
.ar-hero-in { position: relative; width: 100%; max-width: 1280px; margin: 0 auto; display: grid; gap: 26px; }
.ar-kicker { margin: 0; display: inline-flex; align-items: center; gap: 10px; width: fit-content; padding: 7px 14px 7px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--ar-fg); background: rgba(17, 23, 34, .7); border: 1px solid rgba(198, 255, 0, .25); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.ar-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--ar-lime); box-shadow: 0 0 12px var(--ar-lime); }
.ar-title { margin: 0; font-family: var(--ar-h); font-weight: 900; line-height: .92; letter-spacing: .02em; font-size: clamp(46px, 10.5vw, 148px); display: grid; }
.ar-title .t1 { color: var(--ar-fg); text-shadow: 0 0 40px rgba(0, 217, 255, .25); }
.ar-title .t2 { background: linear-gradient(92deg, var(--ar-lime) 10%, #E9FF8A 45%, var(--ar-cyan) 95%); -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 0 28px rgba(198, 255, 0, .35)); }
.ar-sub { margin: 0; font-family: var(--ar-h); font-weight: 700; font-size: clamp(14px, 2vw, 22px); letter-spacing: .42em; color: var(--ar-mut); }
.ar-sub b { color: var(--ar-cyan); font-weight: 700; text-shadow: 0 0 18px rgba(0, 217, 255, .6); }
.ar-hero-row { display: flex; flex-wrap: wrap; align-items: stretch; gap: 18px; margin-top: 6px; }
.ar-hero-stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); flex: 1 1 520px; border-radius: 22px; overflow: hidden; background: var(--ar-glass); border: 1px solid var(--ar-line); -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px); box-shadow: var(--ar-shadow); }
.ar-hero-stats > div { padding: 20px 22px; display: grid; gap: 4px; border-right: 1px solid var(--ar-line); }
.ar-hero-stats > div:last-child { border-right: 0; }
.ar-hero-stats b { font-family: var(--ar-h); font-size: clamp(26px, 3.4vw, 42px); font-weight: 800; line-height: 1; color: var(--ar-fg); font-variant-numeric: tabular-nums; }
.ar-hero-stats > div:first-child b { color: var(--ar-lime); text-shadow: 0 0 22px rgba(198, 255, 0, .4); }
.ar-hero-stats span { font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--ar-mut); }
.ar-topcard { flex: 0 1 380px; display: flex; align-items: center; gap: 16px; padding: 12px 18px 12px 12px; cursor: pointer; text-align: left; color: var(--ar-fg); font-family: inherit;
  border-radius: 22px; background: linear-gradient(135deg, rgba(198, 255, 0, .14), rgba(17, 23, 34, .85) 55%); border: 1px solid rgba(198, 255, 0, .38); box-shadow: 0 0 0 1px rgba(198, 255, 0, .06), 0 20px 50px -24px rgba(198, 255, 0, .45); transition: transform .3s var(--ar-ease), box-shadow .3s ease; }
.ar-topcard:hover { transform: translateY(-3px); box-shadow: 0 0 0 1px rgba(198, 255, 0, .2), 0 26px 60px -22px rgba(198, 255, 0, .6); }
.ar-topcard-ph { width: 92px; height: 112px; border-radius: 16px; overflow: hidden; flex: none; box-shadow: 0 0 0 2px var(--ar-lime), 0 0 24px rgba(198, 255, 0, .4); }
.ar-topcard-ph img { width: 100%; height: 100%; object-fit: cover; }
.ar-topcard-tx { display: grid; gap: 4px; min-width: 0; }
.ar-tag { display: inline-flex; align-items: center; gap: 6px; width: fit-content; padding: 3px 9px; border-radius: 999px; font-size: 10.5px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: #1d1600; background: linear-gradient(135deg, #FFE26B, #FFC400); }
.ar-tag .ar-ic { width: 13px; height: 13px; }
.ar-topcard-n { font-family: var(--ar-h); font-size: 26px; font-weight: 800; letter-spacing: .04em; }
.ar-topcard-s { font-size: 12.5px; color: var(--ar-mut); font-variant-numeric: tabular-nums; }
.ar-topcard-r { font-size: 12.5px; color: var(--ar-mut); }
.ar-topcard-r b { color: var(--ar-lime); font-family: var(--ar-h); font-size: 15px; }
.ar-ctas { display: flex; flex-wrap: wrap; gap: 12px; }
.ar-cta { display: inline-flex; align-items: center; gap: 10px; padding: 16px 26px; border-radius: 14px; font-family: var(--ar-h); font-weight: 700; font-size: 13px; letter-spacing: .14em; text-transform: uppercase; text-decoration: none;
  color: #0a0f00; background: linear-gradient(135deg, #DBFF4D, var(--ar-lime)); box-shadow: 0 0 0 1px rgba(198, 255, 0, .4), 0 14px 40px -12px rgba(198, 255, 0, .7); transition: transform .25s var(--ar-ease), box-shadow .25s ease; }
.ar-cta .ar-ic { width: 18px; height: 18px; transition: transform .25s var(--ar-ease); }
.ar-cta:hover { transform: translateY(-2px); box-shadow: 0 0 0 1px rgba(198, 255, 0, .6), 0 18px 50px -12px rgba(198, 255, 0, .9); }
.ar-cta:hover .ar-ic { transform: translateX(4px); }
.ar-cta.ghost { color: var(--ar-fg); background: rgba(17, 23, 34, .7); box-shadow: inset 0 0 0 1px rgba(0, 217, 255, .4); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.ar-cta.ghost:hover { box-shadow: inset 0 0 0 1px var(--ar-cyan), 0 0 30px -6px rgba(0, 217, 255, .5); }
.ar-cta:focus-visible, .ar-topcard:focus-visible { outline: 2px solid var(--ar-cyan); outline-offset: 3px; }
.ar-scroll { position: absolute; left: 50%; bottom: 26px; transform: translateX(-50%); display: grid; justify-items: center; gap: 8px; color: var(--ar-mut); text-decoration: none; font-size: 10px; font-weight: 700; letter-spacing: .3em; text-transform: uppercase; }
.ar-mouse { width: 24px; height: 38px; border-radius: 14px; border: 2px solid rgba(245, 247, 250, .4); display: grid; justify-items: center; padding-top: 6px; }
.ar-mouse i { width: 3px; height: 8px; border-radius: 2px; background: var(--ar-lime); animation: ar-wheel 1.8s ease-in-out infinite; }
@keyframes ar-wheel { 0% { transform: translateY(0); opacity: 1; } 70% { transform: translateY(12px); opacity: 0; } 100% { opacity: 0; } }
/* hero entrance */
.ar-js:not(.ar-ready) .ar-hero-in > * { opacity: 0; }
.ar-ready .ar-hero-in > * { animation: ar-rise .9s var(--ar-ease) backwards; }
.ar-ready .ar-hero-in > :nth-child(2) { animation-delay: .08s; } .ar-ready .ar-hero-in > :nth-child(3) { animation-delay: .18s; }
.ar-ready .ar-hero-in > :nth-child(4) { animation-delay: .28s; } .ar-ready .ar-hero-in > :nth-child(5) { animation-delay: .38s; }
@keyframes ar-rise { from { opacity: 0; transform: translateY(18px); } }

/* ---------------- page frame ---------------- */
.bx { display: block !important; max-width: 1360px; margin: 0 auto; padding: 0 max(16px, env(safe-area-inset-left)); }
.bx > .bx-sec { margin-top: 56px; }
.bx > .bx-sec[hidden] { display: none !important; }
.bx.ar-swap > .bx-sec:not([hidden]) { animation: ar-in .55s var(--ar-ease) both; }
@keyframes ar-in { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.bx-sec { display: grid; gap: 22px; scroll-margin-top: 84px; }
.bx-sec, .ar-block, .bx-pr, .bx-pr-head { grid-template-columns: minmax(0, 1fr); }
.bx-sec > *, .ar-block > *, .bx-pr > *, .bx-pr-id, .bx-pr-id > * { min-width: 0; }
@media (min-width: 761px) { .bx-pr-head { grid-template-columns: auto minmax(0, 1fr) !important; } }
.bx-sec > h2, .bx-sec h2, .ar-h {
  margin: 10px 0 0; font-family: var(--ar-h); font-weight: 800; font-size: clamp(22px, 2.7vw, 32px); letter-spacing: .06em; text-transform: uppercase; line-height: 1.15; color: var(--ar-fg);
  display: flex; align-items: center; gap: 14px;
}
.bx-sec > h2::before, .bx-sec h2::before { content: ""; flex: none; width: 6px; height: 1.05em; border-radius: 3px; background: linear-gradient(180deg, var(--ar-lime), var(--ar-cyan)); box-shadow: 0 0 14px rgba(198, 255, 0, .5); border: 0; margin: 0; }
.ar-h::before { display: none; }
.ar-block { display: grid; gap: 20px; scroll-margin-top: 84px; }
.ar-block + .ar-block { margin-top: 30px; }
.ar-head { display: grid; gap: 6px; }
.ar-head-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.ar-eyebrow { margin: 0; font-size: 11.5px; font-weight: 700; letter-spacing: .22em; text-transform: uppercase; color: var(--ar-cyan); }
.ar-h { margin: 0; font-size: clamp(28px, 4vw, 46px); letter-spacing: .05em; }
.ar-story { margin: 0; max-width: 980px; font-size: 16.5px; line-height: 1.65; color: #C9D1DD; }
.ar-story b { color: var(--ar-fg); }
.ar-note { margin: 0; font-size: 12.5px; color: var(--ar-mut); }

/* ---------------- dashboard tiles ---------------- */
.ar-stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.ar-stat {
  position: relative; overflow: hidden; display: grid; align-content: start; gap: 6px; min-height: 168px; padding: 20px 20px 18px; border-radius: 20px; text-align: left; color: var(--ar-fg); font-family: inherit;
  background: var(--ar-glass); border: 1px solid var(--ar-line); box-shadow: var(--ar-shadow); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
  transition: transform .3s var(--ar-ease), border-color .3s ease, box-shadow .3s ease;
}
.ar-stat::after { content: ""; position: absolute; inset: auto -30% -60% auto; width: 70%; aspect-ratio: 1; border-radius: 50%; background: radial-gradient(circle, var(--acc-g), transparent 65%); opacity: .5; pointer-events: none; transition: opacity .3s ease; }
.ar-stat.ar-lime, .ar-perf { --acc: var(--ar-lime); --acc-g: rgba(198, 255, 0, .22); }
.ar-stat.ar-cyan { --acc: var(--ar-cyan); --acc-g: rgba(0, 217, 255, .22); }
.ar-stat:hover { transform: translateY(-4px); border-color: color-mix(in srgb, var(--acc) 55%, transparent); box-shadow: 0 0 0 1px color-mix(in srgb, var(--acc) 20%, transparent), 0 26px 50px -24px color-mix(in srgb, var(--acc) 60%, transparent); }
.ar-stat:hover::after { opacity: .9; }
.ar-stat-l { margin: 0; font-size: 11px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--ar-mut); }
.ar-stat-v { margin: 2px 0 0; font-family: var(--ar-h); font-size: clamp(34px, 3.6vw, 46px); font-weight: 800; line-height: 1; color: var(--acc); text-shadow: 0 0 24px color-mix(in srgb, var(--acc) 40%, transparent); font-variant-numeric: tabular-nums; }
.ar-stat-s { margin: 0; font-size: 12.5px; line-height: 1.45; color: var(--ar-mut); }
.ar-seg, .ar-share { display: flex; gap: 3px; height: 8px; margin-top: auto; padding-top: 0; }
.ar-seg i, .ar-share i { display: block; height: 8px; width: var(--w); border-radius: 4px; transform-origin: left; }
.ar-seg i.s0 { background: var(--ar-lime); box-shadow: 0 0 10px rgba(198, 255, 0, .5); } .ar-seg i.s1 { background: var(--ar-cyan); } .ar-seg i.s2 { background: #F5F7FA; }
.ar-share i { background: var(--pc); }
.is-in > .ar-seg i, .is-in > .ar-share i { animation: ar-grow 1.1s var(--ar-ease) .2s backwards; }
@keyframes ar-grow { from { transform: scaleX(0); } }
.ar-stack { display: flex; margin-top: auto; }
.ar-stack-i { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; margin-right: -9px; box-shadow: 0 0 0 2px var(--ar-card), 0 0 0 3.5px var(--pc); transition: transform .25s var(--ar-ease); }
.ar-stack-i:hover { transform: translateY(-4px) scale(1.08); z-index: 1; }
.ar-ring { position: absolute; top: 16px; right: 16px; width: 56px; height: 56px; transform: rotate(-90deg); }
.ar-ring circle { fill: none; stroke: rgba(137, 147, 164, .16); stroke-width: 5; }
.ar-ring circle.on { stroke: var(--acc); stroke-linecap: round; stroke-dasharray: 100; stroke-dashoffset: calc(100 - var(--v)); filter: drop-shadow(0 0 5px var(--acc)); }
.is-in > .ar-ring circle.on { animation: ar-ringin 1.4s var(--ar-ease) .2s backwards; }
@keyframes ar-ringin { from { stroke-dashoffset: 100; } }
.ar-perf { cursor: pointer; background: linear-gradient(150deg, rgba(198, 255, 0, .16), rgba(17, 23, 34, .85) 60%); border-color: rgba(198, 255, 0, .3); }
.ar-perf .ar-stat-v { font-size: clamp(24px, 2.6vw, 32px); color: var(--ar-fg); text-shadow: none; }
.ar-perf-ph { position: absolute; top: 14px; right: 14px; width: 62px; height: 62px; border-radius: 18px; overflow: hidden; box-shadow: 0 0 0 2px var(--ar-lime), 0 0 26px rgba(198, 255, 0, .45); }
.ar-perf-ph img { width: 100%; height: 100%; object-fit: cover; }
@media (max-width: 1100px) { .ar-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px) { .ar-stats { gap: 10px; } .ar-stat { min-height: 150px; padding: 16px; } .ar-ring { width: 44px; height: 44px; } .ar-perf-ph { width: 48px; height: 48px; } }

/* ---------------- leaderboard ---------------- */
.ar-seg-ctl { display: inline-flex; padding: 4px; gap: 2px; border-radius: 14px; background: rgba(17, 23, 34, .8); border: 1px solid var(--ar-line); }
.ar-seg-ctl button { border: 0; padding: 9px 14px; border-radius: 10px; font: 600 12.5px var(--m-body); letter-spacing: .03em; color: var(--ar-mut); background: transparent; cursor: pointer; transition: color .2s ease, background .25s ease; }
.ar-seg-ctl button:hover { color: var(--ar-fg); }
.ar-seg-ctl button[aria-pressed=true] { color: #001218; background: var(--ar-cyan); box-shadow: 0 0 18px rgba(0, 217, 255, .45); }
.ar-lb { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); grid-auto-rows: auto; gap: 14px; }
.ar-card {
  position: relative; display: flex; flex-direction: column; min-height: 400px; padding: 0; overflow: hidden; isolation: isolate; cursor: pointer; text-align: left; font-family: inherit; color: var(--ar-fg);
  border-radius: 22px; background: linear-gradient(180deg, #151C29, #0D121B); border: 1px solid color-mix(in srgb, var(--pc) 28%, var(--ar-line));
  box-shadow: var(--ar-shadow); transition: transform .35s var(--ar-ease), box-shadow .35s ease, border-color .35s ease;
}
.ar-card::before { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, transparent 22%, rgba(13, 18, 27, .7) 46%, #0D121B 62%); pointer-events: none; }
.ar-card::after { content: ""; position: absolute; inset: 0; z-index: 2; pointer-events: none; border-radius: inherit; background: linear-gradient(115deg, transparent 35%, rgba(255, 255, 255, .10) 50%, transparent 65%); transform: translateX(-120%); transition: transform .8s var(--ar-ease); }
.ar-card:hover { transform: translateY(-6px); border-color: var(--pc); box-shadow: 0 0 0 1px color-mix(in srgb, var(--pc) 35%, transparent), 0 30px 60px -26px var(--pc); }
.ar-card:hover::after { transform: translateX(120%); }
.ar-card:focus-visible { outline: 2px solid var(--pc); outline-offset: 3px; }
.ar-card-ph { position: absolute; inset: 0 0 auto 0; height: 62%; z-index: -2; }
.ar-card-ph img { width: 100%; height: 100%; object-fit: cover; object-position: center 20%; transition: transform .7s var(--ar-ease); }
.ar-card:hover .ar-card-ph img { transform: scale(1.06); }
.ar-card-top { display: flex; justify-content: space-between; align-items: flex-start; padding: 12px; }
.ar-rank { display: inline-flex; align-items: center; gap: 4px; padding: 5px 10px; border-radius: 10px; font-family: var(--ar-h); font-weight: 800; font-size: 15px; color: #fff;
  background: rgba(8, 11, 18, .72); -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); border: 1px solid color-mix(in srgb, var(--pc) 55%, transparent); box-shadow: 0 0 16px -4px var(--pc); }
.ar-rank .ar-ic { width: 16px; height: 16px; }
.ar-ovr { display: grid; justify-items: end; padding: 5px 9px; border-radius: 10px; background: rgba(8, 11, 18, .72); -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); border: 1px solid var(--ar-line2); line-height: 1; }
.ar-ovr b { font-family: var(--ar-h); font-size: 15px; font-weight: 800; color: var(--pc); }
.ar-ovr small { font-size: 8.5px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: var(--ar-mut); margin-top: 3px; }
.ar-card-body { margin-top: auto; display: grid; gap: 9px; padding: 0 14px 14px; }
.ar-card-n { font-family: var(--ar-h); font-weight: 800; font-size: 19px; letter-spacing: .04em; text-transform: uppercase; line-height: 1.1; text-shadow: 0 2px 14px rgba(0, 0, 0, .7); }
.ar-bdgs { display: flex; flex-wrap: wrap; gap: 5px; min-height: 0; }
.ar-bdgs:empty { display: none; }
.ar-bdg { display: inline-flex; align-items: center; gap: 5px; padding: 3px 8px 3px 6px; border-radius: 999px; font-size: 10.5px; font-weight: 700; letter-spacing: .04em; white-space: nowrap; color: var(--bc); background: color-mix(in srgb, var(--bc) 14%, transparent); border: 1px solid color-mix(in srgb, var(--bc) 40%, transparent); }
.ar-bdg .ar-ic { width: 12px; height: 12px; }
.b-champion { --bc: #FFD23F; } .b-rising { --bc: #00D9FF; } .b-improved { --bc: #C6FF00; } .b-streak { --bc: #FF8A3D; } .b-slump { --bc: #FF4D6D; } .b-pair { --bc: #B57BFF; }
.ar-card-g { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 10px; padding: 10px 0 0; border-top: 1px solid var(--ar-line); }
.ar-card-g span { display: grid; gap: 1px; }
.ar-card-g b { font-family: var(--ar-h); font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; }
.ar-card-g small { font-size: 9.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--ar-mut); }
.ar-bar { display: block; height: 6px; border-radius: 6px; background: rgba(137, 147, 164, .16); overflow: hidden; }
.ar-bar i { display: block; height: 100%; width: var(--v); border-radius: 6px; background: linear-gradient(90deg, color-mix(in srgb, var(--pc) 55%, transparent), var(--pc)); box-shadow: 0 0 12px var(--pc); transform-origin: left; }
.ar-card.is-in .ar-bar i { animation: ar-grow 1.2s var(--ar-ease) .25s backwards; }
.ar-card-f { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.ar-form { display: flex; gap: 4px; }
.ar-form i { width: 9px; height: 9px; border-radius: 3px; transform: rotate(45deg); }
.ar-form i.w { background: var(--ar-lime); box-shadow: 0 0 8px rgba(198, 255, 0, .7); }
.ar-form i.l { background: var(--ar-red); opacity: .85; }
.ar-trend { font-size: 10.5px; font-weight: 700; padding: 3px 8px; border-radius: 999px; color: var(--ar-mut); background: rgba(137, 147, 164, .12); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 62%; }
.ar-trend.t-improving { color: var(--ar-lime); background: rgba(198, 255, 0, .12); }
.ar-trend.t-recent, .ar-trend.t-declining { color: #FF8FA3; background: rgba(255, 77, 109, .14); }
/* champion */
.ar-card.is-champ { grid-column: span 2; grid-row: span 2; min-height: 0; border: 0; padding: 0; background: #0D121B; }
.ar-card.is-champ { box-shadow: 0 0 0 1px rgba(255, 210, 63, .4), 0 30px 80px -30px rgba(198, 255, 0, .55); }
.ar-card.is-champ > .ar-card-ph { height: 70%; }
.ar-card.is-champ .ar-card-body { padding: 0 22px 22px; gap: 12px; }
.ar-card.is-champ .ar-card-n { font-size: clamp(28px, 3vw, 40px); background: linear-gradient(92deg, #FFE26B, var(--ar-lime)); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: none; filter: drop-shadow(0 2px 12px rgba(0, 0, 0, .6)); }
.ar-card.is-champ .ar-card-g { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.ar-card.is-champ .ar-card-g b { font-size: 22px; }
.ar-card.is-champ .ar-rank { font-size: 18px; color: #1d1600; background: linear-gradient(135deg, #FFE26B, #FFC400); border-color: transparent; box-shadow: 0 0 24px rgba(255, 210, 63, .6); padding: 7px 12px; }
.ar-card.is-champ .ar-ovr b { font-size: 20px; color: var(--ar-lime); }
.ar-card.is-champ .ar-card-top { padding: 18px; }
.ar-card.is-champ .ar-card-ph::after { content: ""; position: absolute; inset: 0; background: radial-gradient(80% 60% at 50% 20%, transparent 40%, rgba(8, 11, 18, .45)); }
.ar-card.is-champ > .ar-card-body::before { content: "SEASON CHAMPION"; font-family: var(--ar-h); font-size: 11px; font-weight: 700; letter-spacing: .3em; color: #FFD23F; }
.ar-ring-b {
  position: absolute; inset: 0; z-index: 3; pointer-events: none; border-radius: inherit; padding: 2px;
  background: conic-gradient(from var(--ar-ang, 0deg), #FFD23F, #C6FF00 18%, #00D9FF 32%, rgba(0, 217, 255, 0) 45%, rgba(255, 210, 63, 0) 62%, #FFD23F 82%, #FFD23F);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0);
  animation: ar-spin 6s linear infinite;
}
@property --ar-ang { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
@keyframes ar-spin { to { --ar-ang: 360deg; } }
@media (max-width: 1240px) { .ar-lb { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 980px) { .ar-lb { grid-template-columns: repeat(3, minmax(0, 1fr)); } .ar-card.is-champ { grid-column: 1 / -1; grid-row: auto; min-height: 460px; } .ar-card.is-champ > .ar-card-ph { height: 100%; } .ar-card.is-champ::before { background: linear-gradient(180deg, transparent 30%, rgba(13, 18, 27, .85) 62%, #0D121B 85%); } }
@media (max-width: 680px) { .ar-lb { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; } .ar-card { min-height: 330px; } .ar-card-n { font-size: 15px; } .ar-card-g b { font-size: 13.5px; } .ar-card.is-champ .ar-card-g { grid-template-columns: 1fr 1fr; } .ar-seg-ctl { width: 100%; overflow-x: auto; } .ar-seg-ctl button { flex: 1; padding: 9px 10px; } .ar-trend { display: none; } }

/* ---------------- awards ---------------- */
.ar-awards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.ar-aw {
  position: relative; display: grid; grid-template-columns: auto 1fr auto; grid-template-areas: "ic l ph" "n n ph" "v v ph" "w w w"; align-items: center; gap: 6px 12px; padding: 18px; overflow: hidden; cursor: pointer;
  text-align: left; font-family: inherit; color: var(--ar-fg); border-radius: 20px; background: var(--ar-glass); border: 1px solid var(--ar-line); box-shadow: var(--ar-shadow);
  transition: transform .3s var(--ar-ease), border-color .3s ease, box-shadow .3s ease;
}
.ar-aw::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 3px; background: var(--bc); box-shadow: 0 0 16px var(--bc); }
.ar-aw:hover { transform: translateY(-4px); border-color: color-mix(in srgb, var(--bc) 55%, transparent); box-shadow: 0 26px 50px -26px var(--bc); }
.a-champion { --bc: #FFD23F; } .a-rising { --bc: #00D9FF; } .a-improved { --bc: #C6FF00; } .a-streak { --bc: #FF8A3D; } .a-slump { --bc: #FF4D6D; } .a-pair { --bc: #B57BFF; }
.ar-aw-ic { grid-area: ic; width: 38px; height: 38px; border-radius: 12px; display: grid; place-items: center; color: var(--bc); background: color-mix(in srgb, var(--bc) 14%, transparent); border: 1px solid color-mix(in srgb, var(--bc) 35%, transparent); box-shadow: 0 0 18px -6px var(--bc); }
.ar-aw-ic .ar-ic { width: 20px; height: 20px; }
.ar-aw-l { grid-area: l; font-family: var(--ar-h); font-size: 12px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--bc); }
.ar-aw-i { grid-area: ph; width: 64px; height: 64px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 0 2px var(--bc), 0 0 22px -4px var(--bc); }
.ar-aw-pair { grid-area: ph; display: flex; }
.ar-aw-pair .ar-aw-i { width: 52px; height: 52px; }
.ar-aw-pair .ar-aw-i + .ar-aw-i { margin-left: -14px; }
.ar-aw-n { grid-area: n; font-family: var(--ar-h); font-size: 18px; font-weight: 800; letter-spacing: .03em; }
.ar-aw-v { grid-area: v; font-size: 12.5px; color: var(--ar-mut); }
.ar-aw-v b { font-family: var(--ar-h); font-size: 17px; color: var(--ar-fg); margin-right: 4px; }
.ar-aw-why { grid-area: w; margin-top: 6px; padding-top: 10px; border-top: 1px solid var(--ar-line); font-size: 12px; line-height: 1.5; color: var(--ar-mut); }
@media (max-width: 1100px) { .ar-awards { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .ar-awards { grid-template-columns: 1fr; } }

/* ---------------- existing report components, reskinned ---------------- */
.bx-card, .bx-findings li, .bx-kpi, .bx-pick-b, .bx-pn-b, .bx-pr-verdict, .bx-callout {
  background: var(--ar-glass) !important; border: 1px solid var(--ar-line) !important; border-radius: 20px !important; box-shadow: var(--ar-shadow) !important;
  -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
}
.bx-card { transition: border-color .3s ease, box-shadow .3s ease, transform .3s var(--ar-ease); }
.bx-card:hover { border-color: rgba(0, 217, 255, .28) !important; box-shadow: 0 0 0 1px rgba(0, 217, 255, .08), 0 30px 60px -32px rgba(0, 217, 255, .35) !important; }
.bx-card::before, .bx-kpi::before { opacity: 0 !important; }
.bx-findings li::before { display: none !important; content: none !important; }
.bx-card-head h3 { font-family: var(--m-body) !important; font-weight: 750; font-size: 16px; letter-spacing: -.005em; color: var(--ar-fg); }
.bx-tag { font-family: var(--m-body) !important; font-size: 10px !important; font-weight: 700 !important; letter-spacing: .14em !important; text-transform: uppercase; border-radius: 999px !important; }
.bx-tag-m { color: var(--ar-lime) !important; background: rgba(198, 255, 0, .10) !important; border: 1px solid rgba(198, 255, 0, .3) !important; }
.bx-tag-e { color: var(--ar-cyan) !important; background: rgba(0, 217, 255, .10) !important; border: 1px solid rgba(0, 217, 255, .3) !important; }
.bx-note, .bx-prose, .bx-list li, .bx-findings li { color: #BCC5D3; }
.bx-prose b, .bx-list b, .bx-findings b, .bx-pr-verdict b, b[data-draw] { color: var(--ar-fg); }
b[data-draw="f"] { font-variant-numeric: tabular-nums; }
.bx-findings { counter-reset: arf; }
.bx-findings li { padding: 18px 20px 18px 66px !important; position: relative; line-height: 1.6; }
.bx-findings li::after { counter-increment: arf; content: "0" counter(arf); position: absolute; left: 18px; top: 16px; font-family: var(--ar-h); font-weight: 800; font-size: 20px; color: var(--ar-lime); text-shadow: 0 0 14px rgba(198, 255, 0, .5); }
.bx-callout { border-color: rgba(0, 217, 255, .3) !important; }
.bx-tw { border-radius: 14px; }
.bx-table thead th { background: rgba(8, 11, 18, .92) !important; color: var(--ar-mut) !important; font-size: 10.5px !important; font-weight: 700 !important; letter-spacing: .12em !important; text-transform: uppercase; border-bottom: 1px solid var(--ar-line2) !important; }
.bx-sort { color: inherit !important; font: inherit !important; letter-spacing: inherit !important; text-transform: inherit !important; }
th[aria-sort=ascending] .bx-sort, th[aria-sort=descending] .bx-sort { color: var(--ar-lime) !important; }
.bx-table td { border-bottom: 1px solid rgba(137, 147, 164, .08) !important; font-variant-numeric: tabular-nums; color: #D7DDE7; }
.bx-table tbody tr { transition: background .2s ease; }
.bx-table tbody tr:hover td { background: rgba(0, 217, 255, .05) !important; }
.bx-table td.num { font-weight: 600; }
.bx-stats > div { background: rgba(8, 11, 18, .55) !important; border: 1px solid var(--ar-line) !important; border-radius: 14px !important; transition: border-color .25s ease, transform .25s var(--ar-ease); }
.bx-stats > div:hover { border-color: color-mix(in srgb, var(--pc, var(--ar-cyan)) 50%, transparent) !important; transform: translateY(-2px); }
.bx-stats dt { font-family: var(--m-body) !important; font-size: 10px !important; letter-spacing: .14em !important; color: var(--ar-mut) !important; }
.bx-stats dd { font-family: var(--ar-h) !important; font-weight: 700 !important; color: var(--ar-fg) !important; letter-spacing: .02em; }
.bx-kpi-v, .bx-sw dt { font-family: var(--ar-h) !important; }
.bx-sw dt { font-size: 11px !important; letter-spacing: .14em !important; color: var(--ar-cyan) !important; }
.bx-awards dt { font-family: var(--ar-h) !important; font-size: 11px !important; letter-spacing: .14em !important; text-transform: uppercase; color: var(--ar-lime) !important; }
.bx-awards > div { background: rgba(8, 11, 18, .5) !important; border: 1px solid var(--ar-line) !important; border-radius: 16px !important; }
.bx-btn, .ar-btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; margin-top: 12px; padding: 11px 18px; border-radius: 12px; border: 1px solid rgba(0, 217, 255, .4); background: rgba(0, 217, 255, .08); color: var(--ar-fg); font: 600 13px var(--m-body); cursor: pointer; transition: background .2s ease, box-shadow .2s ease; }
.ar-btn:hover { background: rgba(0, 217, 255, .16); box-shadow: 0 0 20px -6px var(--ar-cyan); }
.bx-foot { margin-top: 56px; color: var(--ar-mut); }

/* ---------------- charts ---------------- */
.bx-chart { position: relative; }
.bx-chart svg text, .bx-tx { fill: #95A0B3 !important; font-family: var(--m-body) !important; font-weight: 500; }
.bx-chart svg .bx-lab, .bx-chart svg text.lab, .bx-chart svg text[font-weight="700"] { fill: var(--ar-fg) !important; }
.bx-chart svg line, .bx-chart svg path.domain { stroke-opacity: .9; }
.bx-tip { background: rgba(8, 11, 18, .96) !important; border: 1px solid rgba(0, 217, 255, .4) !important; border-radius: 12px !important; box-shadow: 0 18px 40px rgba(0, 0, 0, .7), 0 0 24px -8px rgba(0, 217, 255, .6) !important; color: var(--ar-fg) !important; font-family: var(--m-body) !important; -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.bx-tip-h { color: var(--ar-cyan) !important; font-family: var(--ar-h) !important; letter-spacing: .06em; }
.ar-js .bx-chart:not(.is-in) svg { clip-path: inset(0 100% 0 0); }
.ar-js .bx-chart.is-in:not(.ar-wiped) svg { animation: ar-wipe 1.3s var(--ar-ease) var(--d, 0ms) backwards; }
@keyframes ar-wipe { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
.bx-chart svg path[stroke-width="2.5"], .bx-chart svg path.line, .bx-chart svg .ln { filter: drop-shadow(0 0 4px currentColor); }

/* ---------------- reveal ---------------- */
.ar-js .ar-reveal:not(.is-in), .ar-js .bx-card:not(.is-in), .ar-js .bx-findings li:not(.is-in) { opacity: 0; }
.ar-js .ar-reveal.is-in, .ar-js .bx-card.is-in, .ar-js .bx-findings li.is-in { animation: ar-rise .75s var(--ar-ease) var(--d, 0ms) backwards; }

/* ---------------- players: chooser, identity header, profile widgets ---------------- */
.bx-pick-hint { color: var(--ar-cyan) !important; font-family: var(--m-body) !important; letter-spacing: .18em !important; }
.bx-pick { grid-template-columns: repeat(7, minmax(0, 1fr)) !important; gap: 10px !important; }
.bx-pick-b { flex-direction: column !important; align-items: center !important; text-align: center !important; padding: 16px 10px 14px !important; gap: 10px !important; border-color: color-mix(in srgb, var(--pc) 22%, var(--ar-line)) !important; transition: transform .3s var(--ar-ease), border-color .3s ease, box-shadow .3s ease !important; }
.bx-pick-b::after { display: none !important; }
.bx-pick-b:hover { transform: translateY(-4px) !important; border-color: var(--pc) !important; box-shadow: 0 22px 40px -24px var(--pc) !important; }
.bx-pick-b[aria-pressed=true] { background: linear-gradient(180deg, color-mix(in srgb, var(--pc) 22%, #111722), #111722) !important; border-color: var(--pc) !important; box-shadow: 0 0 0 1px var(--pc), 0 0 30px -6px var(--pc) !important; }
.bx-pk-av.has-ph { width: 64px !important; height: 64px !important; }
.bx-pk-body { align-items: center; }
.bx-pk-name { font-family: var(--ar-h) !important; font-size: 13px !important; letter-spacing: .06em; text-transform: uppercase; }
.bx-pk-stat { font-family: var(--m-body) !important; font-size: 11px !important; }
.bx-pk-cta { font-size: 11px !important; letter-spacing: .08em; text-transform: uppercase; color: var(--pc) !important; }
.bx-pick-b[aria-pressed=true] .bx-pk-cta { color: var(--ar-fg) !important; }
@media (max-width: 1100px) { .bx-pick { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; } }
@media (max-width: 560px) { .bx-pick { display: flex !important; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 6px; } .bx-pick-b { flex: 0 0 31% !important; scroll-snap-align: start; } .bx-pk-av.has-ph { width: 52px !important; height: 52px !important; } .bx-pk-cta { display: none; } }

.bx-pr-head { position: relative; display: grid !important; grid-template-columns: auto minmax(0, 1fr); gap: 28px !important; padding: 24px !important; border-radius: 26px !important; overflow: hidden;
  background: radial-gradient(70% 140% at 0% 0%, color-mix(in srgb, var(--pc) 30%, transparent), transparent 60%), linear-gradient(135deg, #141B28, #0C1119) !important;
  border: 1px solid color-mix(in srgb, var(--pc) 40%, var(--ar-line)) !important; box-shadow: 0 30px 70px -36px var(--pc), var(--ar-shadow) !important; }
.bx-pr-head::before { content: ""; position: absolute; inset: 0; pointer-events: none; background-image: linear-gradient(rgba(137, 147, 164, .06) 1px, transparent 1px), linear-gradient(90deg, rgba(137, 147, 164, .06) 1px, transparent 1px); background-size: 28px 28px; mask-image: linear-gradient(90deg, transparent, #000 50%, transparent); }
.bx-av.has-ph { width: 200px !important; height: 250px !important; border-radius: 22px !important; box-shadow: 0 0 0 2px var(--pc), 0 0 40px -6px var(--pc) !important; }
.bx-pr-id { display: grid; gap: 12px; align-content: center; position: relative; }
.bx-pr-name { font-family: var(--ar-h) !important; font-size: clamp(30px, 4.2vw, 54px) !important; font-weight: 900 !important; letter-spacing: .04em !important; text-transform: uppercase; color: var(--ar-fg); text-shadow: 0 0 30px color-mix(in srgb, var(--pc) 45%, transparent); margin: 0; }
.bx-pr-sub { color: var(--ar-mut) !important; font-size: 13px !important; margin: 0; }
.ar-id { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 8px; }
.ar-id > span { display: grid; gap: 4px; padding: 10px 12px; border-radius: 14px; background: rgba(8, 11, 18, .6); border: 1px solid var(--ar-line); white-space: nowrap; }
.ar-id small { font-size: 9.5px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--ar-mut); }
.ar-id b { font-family: var(--ar-h); font-size: 19px; font-weight: 800; color: var(--ar-fg); display: inline; }
.ar-id > span:first-child b { color: var(--pc); }
.ar-id > span:first-child { display: block; }
.ar-id > span:first-child small { display: block; margin-bottom: 4px; }
.ar-id-form { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.ar-id-form small { font-size: 10px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--ar-mut); }
.ar-form10 { display: flex; gap: 5px; }
.ar-form10 i { width: 26px; height: 26px; border-radius: 8px; display: grid; place-items: center; font-style: normal; font-family: var(--ar-h); font-size: 11px; font-weight: 800; }
.ar-form10 i.w { color: #0a0f00; background: var(--ar-lime); box-shadow: 0 0 12px -2px rgba(198, 255, 0, .7); }
.ar-form10 i.l { color: #fff; background: rgba(255, 77, 109, .22); border: 1px solid rgba(255, 77, 109, .5); }
@media (max-width: 1100px) { .ar-id { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .bx-pr-head { grid-template-columns: 1fr; padding: 16px !important; gap: 16px !important; }
  .bx-av.has-ph { width: 100% !important; height: auto !important; aspect-ratio: 4 / 3.2; }
  .bx-av.has-ph img { object-position: center 25%; }
  .ar-id { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .ar-form10 i { width: 22px; height: 22px; font-size: 10px; }
}
.bx-pr-verdict { padding: 20px 22px !important; font-size: 15.5px; line-height: 1.7; color: #C9D1DD; border-left: 3px solid var(--pc) !important; }
.ar-wk-svg { width: 100%; height: auto; display: block; overflow: visible; }
.ar-wk-svg .zero { stroke: rgba(137, 147, 164, .35); stroke-dasharray: 3 4; }
.ar-wk-svg rect { transform-box: fill-box; }
.ar-js .bx-card.is-in .ar-wk-svg rect { animation: ar-growy .9s var(--ar-ease) calc(var(--i) * 70ms + .15s) backwards; }
@keyframes ar-growy { from { transform: scaleY(0); } }
.ar-wk-svg .up rect { fill: var(--ar-lime); filter: drop-shadow(0 0 6px rgba(198, 255, 0, .55)); transform-origin: bottom; }
.ar-wk-svg .dn rect { fill: var(--ar-red); filter: drop-shadow(0 0 6px rgba(255, 77, 109, .5)); transform-origin: top; }
.ar-wk-svg text { font-family: var(--m-body); text-anchor: middle; }
.ar-wk-svg .v { font-family: var(--ar-h); font-size: 13px; font-weight: 700; fill: var(--ar-fg); }
.ar-wk-svg .rec { font-size: 11.5px; fill: var(--ar-mut); }
.ar-wk-svg .wk { font-size: 12px; font-weight: 700; fill: var(--ar-cyan); letter-spacing: .1em; }
.ar-mh-tw { max-height: none; }
.ar-mh-t td, .ar-mh-t th { white-space: nowrap; }
.ar-stage { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 999px; background: rgba(137, 147, 164, .12); color: #BCC5D3; }
.ar-stage.st-F { color: #1d1600; background: #FFD23F; }
.ar-stage.st-E { color: var(--ar-cyan); background: rgba(0, 217, 255, .12); }
.ar-res { font-family: var(--ar-h); font-size: 10.5px; font-weight: 800; letter-spacing: .1em; padding: 3px 8px; border-radius: 6px; }
.ar-res.w { color: #0a0f00; background: var(--ar-lime); }
.ar-res.l { color: #FF8FA3; background: rgba(255, 77, 109, .14); }
.ar-sw { border-color: color-mix(in srgb, var(--pc) 30%, var(--ar-line)) !important; }
.bx-pn-b { transition: transform .3s var(--ar-ease), border-color .3s ease !important; }
.bx-pn-b:hover { border-color: rgba(198, 255, 0, .4) !important; transform: translateY(-3px); }
.bx-pn-n { font-family: var(--ar-h) !important; letter-spacing: .04em; text-transform: uppercase; font-size: 16px !important; }

/* small screens: general */
@media (max-width: 640px) {
  .ar-hero { padding: 104px 16px 100px; min-height: 100svh; }
  .ar-hero-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .ar-hero-stats > div:nth-child(2) { border-right: 0; }
  .ar-hero-stats > div:nth-child(-n+2) { border-bottom: 1px solid var(--ar-line); }
  .ar-sub { letter-spacing: .28em; }
  .ar-topcard { flex: 1 1 100%; }
  .ar-cta { flex: 1 1 100%; justify-content: center; }
  .ar-scroll { display: none; }
  .bx > .bx-sec { margin-top: 36px; }
  .bx-findings li { padding: 16px 16px 16px 54px !important; }
  .bx-findings li::after { left: 14px; font-size: 17px; }
}
@media (prefers-reduced-motion: reduce) {
  .ar-glow, .ar-sparks i, .ar-live i, .ar-mouse i, .ar-ring-b { animation: none !important; }
  .ar-court .ln { animation: none; stroke-dashoffset: 0; }
  .ar-court .shuttle { display: none; }
  *, *::before, *::after { animation-duration: .001ms !important; animation-delay: 0s !important; }
  .ar-js .ar-reveal, .ar-js .bx-card, .ar-js .bx-findings li, .ar-js .ar-hero-in > * { opacity: 1 !important; }
  .ar-js .bx-chart svg, .ar-js .ar-bar i, .ar-js .ar-seg i, .ar-js .ar-share i, .ar-js .ar-wk-svg rect { clip-path: none !important; transform: none !important; }
}

/* ---------------- photo framing: large photos are shown whole, in 3:4 frames that match the images ---------------- */
.ar-card { min-height: 0 !important; }
.ar-card::before { display: none; }
.ar-card-ph { position: relative !important; inset: auto !important; width: 100%; height: auto !important; aspect-ratio: 3 / 4; z-index: 0 !important; overflow: hidden; flex: none; border-radius: 21px 21px 0 0; }
.ar-card-ph img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: center; }
.ar-card:hover .ar-card-ph img { transform: none; }
.ar-card-ph::after { content: ""; position: absolute; inset: auto 0 0 0; height: 18%; background: linear-gradient(180deg, rgba(13, 18, 27, 0), #0D121B); pointer-events: none; }
.ar-card-top { position: absolute; top: 0; left: 0; right: 0; z-index: 2; }
.ar-card-body { margin-top: 0 !important; padding-top: 10px !important; flex: 1 1 auto; align-content: start; }
.ar-card.is-champ > .ar-card-ph { height: auto !important; }
.ar-card.is-champ .ar-card-ph::after { inset: auto 0 0 0; height: 18%; background: linear-gradient(180deg, rgba(13, 18, 27, 0), #0D121B); }
.ar-card.is-champ .ar-card-body { align-content: end; }
.ar-topcard-ph { width: 96px !important; height: 128px !important; }
.bx-av.has-ph { width: 210px !important; height: 280px !important; }
.bx-av.has-ph img, .ar-topcard-ph img { object-fit: cover; object-position: center; }
/* executive summary: use the full width — two columns of finding cards on wide screens */
#summary > .bx-prose { max-width: none; }
#summary .bx-findings li { display: flex; flex-direction: column; gap: 14px; }
.bx-ft { flex: 1 1 auto; }
.bx-ff { display: flex; flex-wrap: wrap; gap: 10px 22px; padding-top: 12px; border-top: 1px solid var(--ar-line); }
.bx-ff-p { display: inline-flex; align-items: center; gap: 10px; min-width: 0; }
.bx-ff-av { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 2px solid var(--pc); box-shadow: 0 0 14px color-mix(in srgb, var(--pc) 45%, transparent); background: #0D121B; flex: none; }
.bx-ff-t { display: grid; line-height: 1.25; }
.bx-ff-t b { font-size: 14px; color: var(--ar-fg); }
.bx-ff-t small { font-size: 12px; color: var(--ar-mut); font-variant-numeric: tabular-nums; }
.bx-ff-t i { font-style: normal; font-weight: 700; color: var(--pc); }
@media (min-width: 1100px) {
  #summary .bx-findings { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; align-items: stretch; }
  #summary .bx-findings li { margin: 0 !important; }
}
@media (max-width: 980px) {
  .ar-card.is-champ { display: grid !important; grid-template-columns: minmax(0, 40%) minmax(0, 1fr); align-items: stretch; min-height: 0 !important; }
  .ar-card.is-champ > .ar-card-ph { border-radius: 21px 0 0 21px; align-self: center; }
  .ar-card.is-champ .ar-card-ph::after { inset: 0 0 0 auto; width: 22%; height: auto; background: linear-gradient(90deg, rgba(13, 18, 27, 0), #0D121B); }
  .ar-card.is-champ .ar-card-body { align-content: center; padding: 60px 18px 18px !important; }
}
@media (max-width: 680px) {
  .ar-card.is-champ { grid-template-columns: minmax(0, 44%) minmax(0, 1fr); }
  .ar-card.is-champ .ar-card-body { padding: 74px 12px 14px !important; gap: 8px; align-content: start; }
  .ar-card.is-champ .ar-card-n { font-size: 22px; }
  .ar-card.is-champ .ar-card-g { grid-template-columns: 1fr 1fr; }
  .ar-card.is-champ .ar-card-g b { font-size: 16px; }
}
@media (max-width: 760px) {
  .bx-av.has-ph { width: min(100%, 300px) !important; height: auto !important; aspect-ratio: 3 / 4; justify-self: center; }
  .bx-av.has-ph img { object-position: center; }
}
"""
