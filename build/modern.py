import re

INIT = {'anto': 'AN', 'jothi': 'JS', 'john': 'JO', 'pawan': 'PA', 'dinesh': 'DI', 'pratap': 'PR', 'bhanu': 'BH'}
INITP = {'Anto': 'AN', 'Jothi Sai': 'JS', 'John': 'JO', 'Pawan': 'PA', 'Dinesh': 'DI', 'Pratap': 'PR', 'Bhanu': 'BH'}


def modernize(page):
    nav = re.search(r'<nav class="bx-tabs".*?</nav>', page, re.S).group(0)
    assert page.count(nav + '</header>') == 1
    page = page.replace(nav + '</header>', '<div class="bx-chips" data-draw="hero-chips" data-source="players estimates"></div></header>\n' + nav, 1)
    page = page.replace('<header class="bx-head">', '<header class="bx-head bx-hero">', 1)
    old = '<nav class="bx-tabs" aria-label="Report sections">'
    assert page.count(old) == 1
    page = page.replace(old, old + '<p class="bx-nav-label">Jump to a section</p>', 1)
    for slug, ini in INIT.items():
        old = f'class="bx-pick-b" data-player="{slug}"'
        assert page.count(old) == 1
        page = page.replace(old, f'{old} data-initials="{ini}"', 1)
    page, n = re.subn(r'<div class="bx-pr-head"><h3 class="bx-pr-name">(.*?)</h3>(<p class="bx-pr-sub">.*?</p>)</div>',
                      lambda m: f'<div class="bx-pr-head"><span class="bx-av" aria-hidden="true">{INITP[m.group(1)]}</span>'
                                f'<div class="bx-pr-id"><h3 class="bx-pr-name">{m.group(1)}</h3>{m.group(2)}</div></div>', page, flags=re.S)
    assert n == 7, n
    # mini visuals in the four headline tiles
    viz = ['<div class="bx-kpi-viz" data-draw="kpi-viz" data-kind="stages" data-source="facts"></div>',
           '<div class="bx-kpi-viz" data-draw="kpi-viz" data-kind="weeks" data-source="daily"></div>',
           '<div class="bx-kpi-viz" data-draw="kpi-viz" data-kind="ring" data-key="g.le3p" data-source="facts"></div>',
           '<div class="bx-kpi-viz" data-draw="kpi-viz" data-kind="ring" data-key="m.acc" data-source="facts"></div>']
    tiles = re.findall(r'<div class="bx-kpi">.*?</div>', page, re.S)
    assert len(tiles) == 4, len(tiles)
    for t, v in zip(tiles, viz):
        page = page.replace(t, t[:-len('</div>')] + v + '</div>', 1)
    return page


# Shared modern layer. Each target defines the --m-* surface tokens, the --c-* accent palette and the fonts.
MODERN = r"""
/* ---------- modern layer: hairline cards, dark glow header, sidebar navigation on wide screens ---------- */
.bx { display: grid; grid-template-columns: minmax(0, 1fr); gap: 26px; font-family: var(--m-body); color: var(--m-fg); }
.bx > * { min-width: 0; }
@media (min-width: 980px) {
  .bx { grid-template-columns: 216px minmax(0, 1fr); column-gap: 30px; align-items: start; }
  .bx > .bx-hero { grid-column: 1 / -1; }
  .bx > .bx-tabs {
    grid-column: 1; grid-row: 2 / span 2; position: sticky; top: 14px;
    flex-direction: column; flex-wrap: nowrap; align-items: stretch; overflow: visible; padding: 10px;
  }
  .bx > .bx-sec { grid-column: 2; grid-row: 2; }
  .bx > .bx-foot { grid-column: 2; }
  .bx-tab { width: 100%; justify-content: flex-start; }
}

/* section colours */
#summary, .bx-tab[data-tab=summary] { --sc: var(--c-coral); }
#players, .bx-tab[data-tab=players] { --sc: var(--c-violet); }
#weekly, .bx-tab[data-tab=weekly] { --sc: var(--c-blue); }
#partners, .bx-tab[data-tab=partners] { --sc: var(--c-green); }
#opponents, .bx-tab[data-tab=opponents] { --sc: var(--c-pink); }
#pressure, .bx-tab[data-tab=pressure] { --sc: var(--c-amber); }
#model, .bx-tab[data-tab=model] { --sc: var(--c-cyan); }
#rankings, .bx-tab[data-tab=rankings] { --sc: var(--gold); }
#strengths, .bx-tab[data-tab=strengths] { --sc: var(--c-lime); }
#outlook, .bx-tab[data-tab=outlook] { --sc: var(--c-indigo); }
#data, .bx-tab[data-tab=data] { --sc: var(--c-slate); }

/* header */
.bx-hero {
  position: relative; overflow: hidden; isolation: isolate;
  border-radius: 26px; padding: clamp(22px, 4vw, 46px); gap: 14px; color: #ffffff;
  background:
    radial-gradient(55% 85% at 0% 0%, rgba(124, 92, 255, .55), transparent 62%),
    radial-gradient(45% 75% at 100% 0%, rgba(255, 90, 54, .42), transparent 62%),
    radial-gradient(55% 80% at 85% 125%, rgba(6, 182, 212, .40), transparent 62%),
    radial-gradient(40% 70% at 8% 125%, rgba(23, 178, 106, .32), transparent 62%),
    #0b1020;
  box-shadow: 0 30px 60px -36px rgba(11, 16, 32, .75);
}
.bx-hero::before {
  content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none;
  background-image: linear-gradient(rgba(255, 255, 255, .055) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, .055) 1px, transparent 1px);
  background-size: 44px 44px;
  -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 25%, transparent 75%);
  mask-image: radial-gradient(ellipse at 50% 0%, #000 25%, transparent 75%);
}
.bx-hero .bx-eyebrow {
  align-self: flex-start; display: inline-flex; align-items: center; gap: 8px;
  padding: 5px 12px; border-radius: 999px; font-size: 12.5px; font-weight: 600;
  letter-spacing: 0; text-transform: none; color: rgba(255, 255, 255, .86);
  background: rgba(255, 255, 255, .08); border: 1px solid rgba(255, 255, 255, .14);
}
.bx-hero .bx-eyebrow::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: #c6f432; box-shadow: 0 0 0 4px rgba(198, 244, 50, .2); }
.bx-hero .bx-title {
  font-family: var(--m-display); font-weight: 800; font-size: clamp(34px, 5.6vw, 62px);
  letter-spacing: -.035em; line-height: 1.02; text-transform: none; color: #ffffff;
  background: linear-gradient(92deg, #ffffff 0%, #ffffff 48%, #d9ccff 70%, #ffc2ad 100%);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.bx-hero .bx-lede { color: rgba(255, 255, 255, .78); font-size: 16.5px; line-height: 1.6; max-width: 68ch; }
.bx-hero .bx-lede b[data-draw] { color: #ffffff; font-weight: 700; }
.bx-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.bx-chip {
  display: flex; align-items: center; gap: 10px; padding: 5px 14px 5px 5px; border-radius: 999px;
  background: rgba(255, 255, 255, .07); border: 1px solid rgba(255, 255, 255, .13);
  -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
}
.bx-chip-rank {
  width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center; flex: none;
  font-family: var(--m-display); font-weight: 800; font-size: 14px; color: #ffffff;
  background: var(--pc); box-shadow: 0 0 14px -2px var(--pc);
}
.bx-chip-txt { display: flex; align-items: baseline; gap: 8px; }
.bx-chip-name { font-weight: 700; color: #ffffff; }
.bx-chip-stat { font-size: 12.5px; color: rgba(255, 255, 255, .7); font-variant-numeric: tabular-nums; }

/* navigation */
.bx-tabs {
  position: sticky; top: 0; z-index: 5; display: flex; flex-wrap: nowrap; gap: 4px; padding: 6px;
  overflow-x: auto; scrollbar-width: none; border-radius: 18px;
  background: color-mix(in srgb, var(--m-panel) 84%, transparent);
  -webkit-backdrop-filter: blur(14px) saturate(1.3); backdrop-filter: blur(14px) saturate(1.3);
  border: 1px solid var(--m-line); box-shadow: var(--m-shadow);
}
.bx-tabs::-webkit-scrollbar { display: none; }
.bx-nav-label { display: none; }
.bx-tab {
  flex: none; display: inline-flex; align-items: center; gap: 10px; cursor: pointer; font-family: var(--m-body);
  font-size: 13.5px; font-weight: 700; color: var(--m-fg); text-align: left; line-height: 1.25;
  background: color-mix(in srgb, var(--sc) 7%, var(--m-panel));
  border: 1px solid color-mix(in srgb, var(--sc) 30%, var(--m-line));
  border-radius: 12px; padding: 7px 12px 7px 7px;
  transition: background .15s ease, border-color .15s ease, transform .15s ease, box-shadow .15s ease;
}
.bx-tab::before {
  content: ""; width: 22px; height: 22px; border-radius: 7px; flex: none;
  background: radial-gradient(circle, #ffffff 0 3px, transparent 3.5px), var(--sc);
}
.bx-tab::after { content: "\203A"; display: none; margin-left: auto; padding-left: 6px; font-size: 20px; line-height: 1; font-weight: 600; color: color-mix(in srgb, var(--sc) 75%, var(--m-muted)); transition: transform .15s ease; }
.bx-tab:hover { color: var(--m-fg); background: color-mix(in srgb, var(--sc) 16%, var(--m-panel)); border-color: var(--sc); box-shadow: 0 6px 16px -10px var(--sc); }
.bx-tab:focus-visible { outline: 2px solid var(--sc); outline-offset: 2px; }
.bx-tab[aria-selected=true] {
  color: #ffffff; border-color: transparent;
  background: linear-gradient(120deg, color-mix(in srgb, var(--sc) 62%, #000000), color-mix(in srgb, var(--sc) 46%, #000000));
  box-shadow: 0 10px 22px -12px var(--sc);
}
.bx-tab[aria-selected=true]::before { background: radial-gradient(circle, var(--sc) 0 3.5px, transparent 4px), #ffffff; }
.bx-tab[aria-selected=true]::after { color: #ffffff; }
@media (min-width: 980px) {
  .bx > .bx-tabs { gap: 6px; }
  .bx-nav-label { display: block; margin: 2px 4px 4px; font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--m-muted); }
  .bx-tab::after { display: block; }
  .bx-tab:hover { transform: translateX(3px); }
  .bx-tab:hover::after { transform: translateX(2px); }
}

/* headings, cards, tags */
.bx h2 {
  font-family: var(--m-display); font-weight: 800; font-size: clamp(25px, 3vw, 33px); letter-spacing: -.028em;
  line-height: 1.1; text-transform: none; margin: 2px 0 0; display: flex; align-items: center; gap: 14px; color: var(--m-fg);
}
.bx-sec > h2::before {
  content: ""; width: 10px; height: 10px; border-radius: 3px; flex: none;
  background: var(--sc); box-shadow: 0 0 0 5px color-mix(in srgb, var(--sc) 20%, transparent);
}
.bx-sec { gap: 18px; }
.bx-grid { gap: 16px; }
.bx-card {
  background: var(--m-panel); border: 1px solid var(--m-line); border-radius: 20px; padding: 20px;
  box-shadow: var(--m-shadow); transition: box-shadow .2s ease, border-color .2s ease;
}
.bx-card:hover { box-shadow: var(--m-shadow-hover); border-color: color-mix(in srgb, var(--sc) 28%, var(--m-line)); }
.bx-card-head h3 { font-family: var(--m-display); font-size: 17px; font-weight: 700; letter-spacing: -.012em; color: var(--m-fg); }
.bx-note { color: var(--m-muted); }
.bx-tag { border: 0 !important; font-style: normal !important; font-weight: 700; font-size: 11.5px; padding: 3px 10px; border-radius: 999px; }
.bx-tag-m { background: color-mix(in srgb, var(--c-green) 15%, transparent); color: color-mix(in srgb, var(--c-green) 72%, var(--m-fg)); }
.bx-tag-e { background: color-mix(in srgb, var(--c-amber) 18%, transparent); color: color-mix(in srgb, var(--c-amber) 62%, var(--m-fg)); }

/* headline numbers */
.bx-kpis { gap: 14px; }
.bx-kpi {
  position: relative; overflow: hidden; color: var(--m-fg); background: var(--m-panel);
  border: 1px solid var(--m-line); border-radius: 20px; padding: 18px 20px; box-shadow: var(--m-shadow);
}
.bx-kpi::before {
  content: ""; position: absolute; right: -50px; bottom: -70px; width: 180px; height: 180px; border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--kc) 30%, transparent), transparent 68%); pointer-events: none;
}
.bx-kpi:nth-child(1) { --kc: var(--c-coral); }
.bx-kpi:nth-child(2) { --kc: var(--c-violet); }
.bx-kpi:nth-child(3) { --kc: var(--c-blue); }
.bx-kpi:nth-child(4) { --kc: var(--c-green); }
.bx-kpi-l { display: flex; align-items: center; gap: 8px; color: var(--m-muted); font-weight: 600; font-size: 13px; }
.bx-kpi-l::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--kc); flex: none; }
.bx-kpi-v {
  font-family: var(--m-display); font-size: 46px; font-weight: 800; letter-spacing: -.035em; line-height: 1.05;
  background: linear-gradient(120deg, var(--kc), color-mix(in srgb, var(--kc) 50%, var(--c-violet)));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.bx-kpi-v b[data-draw] { font-weight: 800; }
.bx-kpi-s { color: var(--m-muted); }

/* summary text */
.bx-prose { max-width: 76ch; }
.bx-findings { list-style: none; padding-left: 0; counter-reset: f; gap: 12px; }
.bx-findings li {
  counter-increment: f; position: relative; padding: 14px 16px 14px 60px; line-height: 1.6;
  background: var(--m-panel); border: 1px solid var(--m-line); border-radius: 16px; box-shadow: var(--m-shadow-sm);
}
.bx-findings li::before {
  content: counter(f); position: absolute; left: 14px; top: 13px; width: 32px; height: 32px; border-radius: 10px;
  display: grid; place-items: center; font-family: var(--m-display); font-weight: 800; font-size: 15px;
  color: var(--fc); background: color-mix(in srgb, var(--fc) 15%, transparent);
}
.bx-findings li:nth-child(1) { --fc: var(--c-coral); }
.bx-findings li:nth-child(2) { --fc: var(--c-violet); }
.bx-findings li:nth-child(3) { --fc: var(--c-blue); }
.bx-findings li:nth-child(4) { --fc: var(--c-amber); }
.bx-findings li:nth-child(5) { --fc: var(--c-green); }
.bx-findings li:nth-child(6) { --fc: var(--c-cyan); }
.bx-callout {
  color: var(--m-fg); border: 1px solid color-mix(in srgb, var(--c-blue) 24%, transparent); border-left-width: 1px;
  background: color-mix(in srgb, var(--c-blue) 8%, var(--m-panel)); border-radius: 16px; padding: 16px 18px;
}

/* tables */
.bx-table { font-size: 13.5px; }
.bx-table th { background: var(--m-panel); border-bottom: 1px solid var(--m-line); }
.bx-sort { font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--m-muted); padding: 10px; }
.bx-sort:hover { color: var(--m-fg); }
.bx-table td { padding: 10px; border-bottom: 1px solid var(--m-line); }
.bx-table tbody tr:hover td { background: var(--m-soft); }
.bx-table td.pos { color: var(--m-ok); font-weight: 700; }
.bx-table td.neg { color: var(--m-bad); font-weight: 700; }
.bx-table td.pl { font-weight: 700; white-space: nowrap; }
.bx-table td.pl::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--pc); margin-right: 8px; vertical-align: 1px; box-shadow: 0 0 0 3px color-mix(in srgb, var(--pc) 20%, transparent); }
.rk { display: inline-grid; place-items: center; min-width: 26px; height: 26px; border-radius: 8px; font-weight: 800; color: var(--m-fg); background: var(--m-soft); }
.rk-1 { background: linear-gradient(135deg, #ffd34d, #f2a900); color: #3a2a00; }
.rk-2 { background: linear-gradient(135deg, #e3e8ee, #a9b4c2); color: #1f2733; }
.rk-3 { background: linear-gradient(135deg, #e6a36b, #b8692c); color: #ffffff; }
.bx-grid-rank .bx-table td { white-space: normal; }
.bx-grid-rank .bx-table td:nth-child(3) { min-width: 9em; }
.bx-grid-rank .bx-table td:last-child { min-width: 13em; }

/* player picker and report */
.bx-pick { gap: 8px; }
.bx-pick-b {
  display: inline-flex; align-items: center; gap: 8px; padding: 5px 14px 5px 5px; border-radius: 999px;
  font-family: var(--m-body); font-size: 14px; font-weight: 700; color: var(--m-fg);
  background: var(--m-panel); border: 1px solid var(--m-line); box-shadow: var(--m-shadow-sm);
}
.bx-pick-b::before {
  content: attr(data-initials); width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center;
  font-size: 11px; font-weight: 800; color: #ffffff; background: var(--pc);
}
.bx-pick-b:hover { border-color: color-mix(in srgb, var(--pc) 50%, var(--m-line)); background: var(--m-panel); color: var(--m-fg); }
.bx-pick-b[aria-pressed=true] {
  color: var(--m-fg); border-color: var(--pc); background: color-mix(in srgb, var(--pc) 12%, var(--m-panel));
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--pc) 22%, transparent);
}
.bx-pr { --sc: var(--pc); gap: 18px; }
.bx-pr-head {
  position: relative; overflow: hidden; flex-direction: row; align-items: center; gap: 18px;
  padding: 22px 24px; border-radius: 24px; color: #ffffff;
  background:
    radial-gradient(70% 150% at 100% 0%, color-mix(in srgb, var(--pc) 60%, transparent), transparent 62%),
    radial-gradient(50% 120% at 0% 100%, color-mix(in srgb, var(--pc) 30%, transparent), transparent 60%),
    #0b1020;
}
.bx-av {
  width: 64px; height: 64px; border-radius: 20px; flex: none; display: grid; place-items: center;
  font-family: var(--m-display); font-weight: 800; font-size: 23px; letter-spacing: -.02em; color: #ffffff;
  background: linear-gradient(135deg, var(--pc), color-mix(in srgb, var(--pc) 55%, #000000));
  box-shadow: 0 0 0 4px rgba(255, 255, 255, .12), 0 12px 24px -10px var(--pc);
}
.bx-pr-id { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.bx-pr-name { font-family: var(--m-display); color: #ffffff; font-size: clamp(28px, 4vw, 42px); font-weight: 800; letter-spacing: -.03em; line-height: 1.05; text-transform: none; }
.bx-pr-sub { color: rgba(255, 255, 255, .78); font-size: 14px; }
.bx-pr-sub b[data-draw] { color: #ffffff; }
.bx-pr-verdict {
  max-width: none; font-size: 16px; line-height: 1.65; padding: 16px 18px; border-radius: 16px;
  background: color-mix(in srgb, var(--pc) 7%, var(--m-panel)); border: 1px solid color-mix(in srgb, var(--pc) 22%, transparent);
}
.bx-stats { gap: 10px; }
.bx-stats > div { border-top: 0; padding: 10px 12px; border-radius: 12px; background: var(--m-soft); }
.bx-stats dt { color: var(--m-muted); }
.bx-stats dd { font-family: var(--m-display); font-size: 21px; font-weight: 800; letter-spacing: -.02em; line-height: 1.15; }
.bx-stats dd b[data-draw] { font-weight: 800; }
.bx-pr-foot { color: var(--m-muted); }
.bx-jump { color: color-mix(in srgb, var(--sc) 75%, var(--m-fg)); font-weight: 700; }

/* strengths cards */
#strengths .bx-card[id^=sw-] { --sc: var(--pc); background: linear-gradient(180deg, color-mix(in srgb, var(--pc) 9%, var(--m-panel)), var(--m-panel) 140px); }
#strengths .bx-card[id^=sw-] .bx-card-head h3 { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 800; letter-spacing: -.025em; }
#strengths .bx-card[id^=sw-] .bx-card-head h3::before { content: ""; width: 12px; height: 12px; border-radius: 4px; background: var(--pc); box-shadow: 0 0 0 4px color-mix(in srgb, var(--pc) 22%, transparent); }
.bx-sw dt { font-size: 11px; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; color: color-mix(in srgb, var(--sc) 70%, var(--m-fg)); }

/* verdict tiles */
.bx-awards { gap: 12px; }
.bx-awards > div { padding: 14px 16px; border-radius: 16px; background: color-mix(in srgb, var(--ac) 9%, var(--m-panel)); border: 1px solid color-mix(in srgb, var(--ac) 28%, transparent); }
.bx-awards > div:nth-child(1) { --ac: var(--gold); }
.bx-awards > div:nth-child(2) { --ac: var(--c-coral); }
.bx-awards > div:nth-child(3) { --ac: var(--c-blue); }
.bx-awards > div:nth-child(4) { --ac: var(--c-violet); }
.bx-awards > div:nth-child(5) { --ac: var(--c-green); }
.bx-awards > div:nth-child(6) { --ac: var(--c-pink); }
.bx-awards dt { font-size: 11px; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; color: color-mix(in srgb, var(--ac) 65%, var(--m-fg)); }

.bx-foot { font-size: 12.5px; color: var(--m-muted); border-top: 1px solid var(--m-line); padding-top: 14px; }
@media (max-width: 560px) {
  .bx-kpi-v { font-size: 38px; }
  .bx-pr-head { padding: 18px; gap: 14px; }
  .bx-av { width: 52px; height: 52px; border-radius: 16px; font-size: 19px; }
  .bx-findings li { padding-left: 54px; }
}
"""

# Dashboard: surfaces follow the dashboard's own theme; fonts stay the dashboard's.
DASH_ADAPTER = """
.bx {
  --m-panel: var(--color-panel); --m-fg: var(--color-fg); --m-muted: var(--color-fg-muted); --m-line: var(--color-border-line);
  --m-soft: color-mix(in srgb, var(--color-fg) 5%, transparent); --m-ok: var(--color-ok); --m-bad: var(--color-bad);
  --m-shadow: 0 1px 2px rgba(16, 24, 40, .05), 0 12px 30px -20px rgba(16, 24, 40, .28);
  --m-shadow-sm: 0 1px 2px rgba(16, 24, 40, .06);
  --m-shadow-hover: 0 2px 4px rgba(16, 24, 40, .06), 0 18px 40px -22px rgba(16, 24, 40, .38);
  --m-display: var(--font-anthropic-sans); --m-body: var(--font-anthropic-sans); --m-mono: var(--font-anthropic-sans);
  --g-fill: color-mix(in srgb, var(--color-panel) 74%, transparent);
  --g-edge: color-mix(in srgb, var(--color-fg) 9%, transparent);
  --g-hi: color-mix(in srgb, var(--color-panel) 72%, #ffffff);
  --c-coral: #f0603c; --c-violet: #7c5cff; --c-blue: #2f80ff; --c-amber: #e39a12; --c-green: #16a765;
  --c-pink: #e8479f; --c-cyan: #0aa9c2; --c-lime: #79b511; --c-indigo: #5146e5; --c-slate: #6b7a90; --gold: #f2b400;
  max-width: 1320px;
}
"""


# 2026 layer: liquid-glass surfaces, bento headline tiles, mono labels, motion on section change and scroll.
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
.bx-kpi-l { font-size: 11px; }
.bx-table td.num, .bx-stats dd b[data-draw] { font-family: var(--m-mono); letter-spacing: -.01em; }
.bx-stats dd b[data-draw] { font-weight: 600; }
.bx-stats dt { font-size: 10px; }

/* header: moving aurora and film grain */
.bx-hero { border-radius: 30px; background-size: 140% 140%; }
.bx-hero::after {
  content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; opacity: .22; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}
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
.bx-pr-head::after {
  content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; opacity: .2; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}
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
"""
