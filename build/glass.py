# 2026 layer: liquid-glass surfaces, bento headline tiles, mono labels, motion on section change and scroll.
NOISE = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")

GLASS = r"""
/* ---------- 2026 layer: liquid-glass surfaces over a soft colour field ---------- */
.bx { position: relative; isolation: isolate; }
.bx::before {
  content: ""; position: absolute; inset: -30px -30px auto; height: 1500px; z-index: -1; pointer-events: none;
  background:
    radial-gradient(34% 26% at 10% 6%, color-mix(in srgb, var(--c-violet) 22%, transparent), transparent 70%),
    radial-gradient(30% 22% at 90% 4%, color-mix(in srgb, var(--c-coral) 18%, transparent), transparent 70%),
    radial-gradient(34% 24% at 72% 44%, color-mix(in srgb, var(--c-cyan) 15%, transparent), transparent 70%),
    radial-gradient(30% 22% at 16% 72%, color-mix(in srgb, var(--c-green) 13%, transparent), transparent 70%);
}
.bx-card, .bx-kpi, .bx-findings li, .bx-tabs {
  background: var(--g-fill);
  -webkit-backdrop-filter: blur(20px) saturate(1.6); backdrop-filter: blur(20px) saturate(1.6);
  border: 1px solid var(--g-edge);
  box-shadow: inset 0 1px 0 var(--g-hi), var(--m-shadow);
}
.bx-card { border-radius: 24px; padding: 22px; }
.bx-card:hover { box-shadow: inset 0 1px 0 var(--g-hi), var(--m-shadow-hover); }
.bx-pr-verdict, .bx-callout, .bx-awards > div { box-shadow: inset 0 1px 0 var(--g-hi); }

/* type: tight display, mono labels */
.bx h2 { font-weight: 700; letter-spacing: -.042em; font-size: clamp(27px, 3.2vw, 36px); }
.bx-hero .bx-title { font-weight: 700; letter-spacing: -.05em; font-size: clamp(36px, 6.2vw, 70px); }
.bx-card-head h3 { font-weight: 650; letter-spacing: -.02em; }
.bx-nav-label, .bx-kpi-l, .bx-sort, .bx-sw dt, .bx-awards dt, .bx-stats dt, .bx-tag, .bx-hero .bx-eyebrow, .bx-chip-stat {
  font-family: var(--m-mono); text-transform: uppercase; letter-spacing: .07em; font-size: 10.5px;
}
.bx-kpi-l { font-size: 11px; display: block; }
.bx-kpi-l::before { display: inline-block; margin-right: 8px; vertical-align: 1px; }
.bx-table td.num, .bx-stats dd b[data-draw] { font-family: var(--m-mono); letter-spacing: -.01em; }
.bx-stats dd b[data-draw] { font-weight: 600; }
.bx-stats dt { font-size: 10px; }

/* header: moving aurora and film grain */
.bx-hero { border-radius: 30px; background-size: 140% 140%; }
.bx-hero::after { content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; opacity: .22; mix-blend-mode: overlay; background-image: NOISE; }
.bx-chip { border-radius: 16px; padding: 6px 14px 6px 6px; box-shadow: inset 0 1px 0 rgba(255, 255, 255, .14); }
.bx-chip-rank { border-radius: 10px; }
.bx-chip-txt { flex-direction: column; align-items: flex-start; gap: 0; line-height: 1.15; }
.bx-chip-stat { font-size: 10px; letter-spacing: .04em; }

/* bento headline tiles */
.bx-kpis { grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr)); gap: 14px; }
@media (min-width: 1100px) { .bx-kpis { grid-template-columns: 1.25fr 1fr 1fr 1fr; } }
.bx-kpi { display: flex; flex-direction: column; gap: 6px; min-height: 160px; border-radius: 24px; padding: 20px; }
.bx-kpi-v { font-size: 52px; font-weight: 700; letter-spacing: -.05em; }
.bx-kpi-viz { margin-top: auto; padding-top: 8px; min-height: 30px; }
.bx-kpi-viz[data-kind=ring] { position: absolute; top: 18px; right: 18px; margin: 0; padding: 0; width: 56px; height: 56px; min-height: 0; }
.bx-kpi:has(.bx-kpi-viz[data-kind=ring]) .bx-kpi-l, .bx-kpi:has(.bx-kpi-viz[data-kind=ring]) .bx-kpi-v { padding-right: 64px; }
.bx-kpi-viz svg { display: block; overflow: visible; }
.bx-kpi-viz .v-on { fill: var(--kc); }
.bx-kpi-viz .v-off { fill: color-mix(in srgb, var(--kc) 16%, transparent); }
.bx-kpi-viz .v-1 { fill-opacity: .62; }
.bx-kpi-viz .v-2 { fill-opacity: .36; }

/* navigation keeps its button look, now on glass */
.bx-tabs { border-radius: 22px; }
.bx-tab { min-height: 40px; border-radius: 14px; }
.bx-pick-b { min-height: 40px; }
.bx-sort { min-height: 34px; }
.bx-table th { background: color-mix(in srgb, var(--m-panel) 88%, transparent); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.bx-findings li { border-radius: 20px; }
.bx-pr-head { border-radius: 28px; isolation: isolate; }
.bx-pr-head::after { content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; opacity: .2; mix-blend-mode: overlay; background-image: NOISE; }
.bx-av { border-radius: 22px; }
:where(.bx) :focus-visible { outline: 2px solid var(--sc, var(--c-violet)); outline-offset: 2px; }

/* motion: sections rise on tab change, cards ease in on scroll */
@media (prefers-reduced-motion: no-preference) {
  .bx-sec:not([hidden]) { animation: bx-rise .45s cubic-bezier(.2, .7, .2, 1) both; }
  @keyframes bx-rise { from { opacity: .4; transform: translateY(12px); } to { opacity: 1; transform: none; } }
  .bx-hero { animation: bx-aurora 22s ease-in-out infinite alternate; }
  @keyframes bx-aurora { from { background-position: 0% 0%; } to { background-position: 100% 100%; } }
  @supports (animation-timeline: view()) {
    .bx-card, .bx-findings li { animation: bx-reveal linear both; animation-timeline: view(); animation-range: entry 0% entry 35%; }
    @keyframes bx-reveal { from { opacity: .45; transform: translateY(16px) scale(.99); } to { opacity: 1; transform: none; } }
  }
}
""".replace('NOISE', NOISE)
