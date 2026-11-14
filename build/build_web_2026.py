import json, glob, os, re
from modern import modernize, MODERN
from glass import GLASS
from picker import restyle_picker, PICKER
from photo_ui import apply_photos, photo_js, PHOTO_CSS
from arena import arena_page, arena_js
from arena_css import ARENA_CSS
from fx import FX_CSS, FX_JS
from recap import RECAP_CSS

D = 'dash'
page = open(f'{D}/index.html', encoding='utf-8').read()
page = page.replace('<meta name="dash-one-writer">\n', '').replace('<link rel="stylesheet" href="style.css">\n', '').replace('\n<script src="app.js"></script>', '')
page = restyle_picker(modernize(page))
page, PHOTOS = apply_photos(page)
page, ARENA_CFG = arena_page(page, PHOTOS)
TOGGLE = ('<button type="button" class="bx-theme" aria-label="Switch between light and dark">'
          '<svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
          '<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
          '</button>')
page = page.replace('<header class="bx-head bx-hero">', '<header class="bx-head bx-hero">' + TOGGLE, 1)
_pj = json.load(open('parsed.json', encoding='utf-8')); _ex = _pj.get('extra_days', []); _nd = len(_pj['days'])
foot = ('<footer class="bx-foot"><p>Built from badminton-scores.xlsx (All matches, Season and the day tabs)'
        + (f' plus {", ".join(_ex)} from extra-days.json' if _ex else '') + f': {_nd} session days. '
        'Measured figures are counts from the match records; estimates come from the models described on the Models tab.</p></footer>\n')
i = page.rstrip().rfind('</div>')
page = page[:i] + foot + page[i:]
app = open(f'{D}/app.js', encoding='utf-8').read()
css = open(f'{D}/style.css', encoding='utf-8').read()
data = {os.path.basename(f)[:-5]: json.load(open(f, encoding='utf-8')) for f in glob.glob(f'{D}/data/*.json')}
data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

LIGHT = """
  --m-bg: #f4f5f9; --m-panel: #ffffff; --m-fg: #0b1220; --m-muted: #5a6376; --m-line: rgba(11, 18, 32, .08);
  --m-soft: rgba(11, 18, 32, .04); --m-ok: #0c8f57; --m-bad: #d92d50;
  --m-shadow: 0 1px 2px rgba(11, 18, 32, .04), 0 18px 40px -26px rgba(11, 18, 32, .28);
  --m-shadow-sm: 0 1px 2px rgba(11, 18, 32, .05);
  --m-shadow-hover: 0 2px 4px rgba(11, 18, 32, .05), 0 26px 50px -26px rgba(11, 18, 32, .36);
  --g-fill: rgba(255, 255, 255, .62); --g-edge: rgba(11, 18, 32, .07); --g-hi: rgba(255, 255, 255, .95);
  --c-coral: #ff5a36; --c-violet: #7c5cff; --c-blue: #2f80ff; --c-amber: #f0a020; --c-green: #17b26a;
  --c-pink: #ee46bc; --c-cyan: #06b6d4; --c-lime: #7cc010; --c-indigo: #4f46e5; --c-slate: #64748b; --gold: #f2b400;
  --series-1: #ff5a36; --series-2: #7c5cff; --series-3: #2f80ff; --series-4: #f0a020;
  --series-5: #17b26a; --series-6: #ee46bc; --series-7: #06b6d4; --series-8: #7cc010;
  --color-border-line: #e5e8ef; --color-warn: #b77400;
  --cds-chart-grid: rgba(11, 18, 32, .07); --cds-chart-axis: #c2c9d6; --cds-chart-reference: #8e97a8; --cds-chart-muted: #c9cfda;
  --cds-surface-popover: rgba(255, 255, 255, .92); --cds-border: #e2e6ee; --cds-shadow-popover: 0 14px 34px rgba(11, 18, 32, .18);
  --cds-text-secondary: #5a6376;
  color-scheme: light;"""
DARK = """
  --m-bg: #07090f; --m-panel: #121726; --m-fg: #eef1f8; --m-muted: #98a2b8; --m-line: rgba(255, 255, 255, .08);
  --m-soft: rgba(255, 255, 255, .05); --m-ok: #3ddc97; --m-bad: #ff6b8b;
  --m-shadow: 0 1px 2px rgba(0, 0, 0, .35), 0 18px 42px -26px rgba(0, 0, 0, .85);
  --m-shadow-sm: 0 1px 2px rgba(0, 0, 0, .4);
  --m-shadow-hover: 0 2px 4px rgba(0, 0, 0, .4), 0 26px 52px -26px rgba(0, 0, 0, .9);
  --g-fill: rgba(22, 28, 46, .58); --g-edge: rgba(255, 255, 255, .08); --g-hi: rgba(255, 255, 255, .08);
  --c-coral: #ff7a5c; --c-violet: #9d85ff; --c-blue: #5c9dff; --c-amber: #ffbe46; --c-green: #3fd68e;
  --c-pink: #ff72cf; --c-cyan: #33d1e6; --c-lime: #a6e03a; --c-indigo: #8a84ff; --c-slate: #9aa8bf;
  --series-1: #ff7a5c; --series-2: #9d85ff; --series-3: #5c9dff; --series-4: #ffbe46;
  --series-5: #3fd68e; --series-6: #ff72cf; --series-7: #33d1e6; --series-8: #a6e03a;
  --color-border-line: #232a3d; --color-warn: #ffc046;
  --cds-chart-grid: rgba(255, 255, 255, .07); --cds-chart-axis: #3a4560; --cds-chart-reference: #6c7894; --cds-chart-muted: #3a4560;
  --cds-surface-popover: rgba(24, 30, 48, .94); --cds-border: #2c3650; --cds-shadow-popover: 0 14px 34px rgba(0, 0, 0, .6);
  --cds-text-secondary: #98a2b8;
  color-scheme: dark;"""

TOKENS = f"""
/* Glass-on-colour-field palette: neutral ground, vivid accents per player and section, Geist type. */
:root {{{LIGHT}
  --m-display: "Geist", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  --m-body: "Geist", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  --m-mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --color-bg: var(--m-bg); --color-panel: var(--m-panel); --color-fg: var(--m-fg); --color-fg-muted: var(--m-muted);
  --color-ok: var(--m-ok); --color-bad: var(--m-bad);
  --font-anthropic-sans: var(--m-body); --font-anthropic-serif: var(--m-display);
  --cds-font-size-caption: 12.5px; --cds-font-size-body: 15px; --cds-font-size-heading: 17px; --cds-font-size-title: 30px;
  --cds-font-weight-medium: 600;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 16px; --cds-gap-lg: 24px; --cds-gap-xl: 36px;
  --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 20px; --cds-pad-xl: 28px;
  --cds-radius: 12px; --cds-dur-slow: 300ms; --cds-ease-out: cubic-bezier(.2, .7, .2, 1);
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{{DARK}
}} }}
:root[data-theme="dark"] {{{DARK}
}}
*, *::before, *::after {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; background: var(--m-bg); }}
body {{
  margin: 0; color: var(--m-fg); background: transparent; font-family: var(--m-body); font-size: 15px; line-height: 1.55;
  -webkit-font-smoothing: antialiased; font-feature-settings: "ss01", "cv11";
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 20px 56px;
}}
body::before {{
  content: ""; position: fixed; inset: -15%; z-index: -1; pointer-events: none;
  background:
    radial-gradient(28% 32% at 12% 10%, color-mix(in srgb, var(--c-violet) 26%, transparent), transparent 70%),
    radial-gradient(26% 30% at 88% 8%, color-mix(in srgb, var(--c-coral) 20%, transparent), transparent 70%),
    radial-gradient(30% 34% at 78% 78%, color-mix(in srgb, var(--c-cyan) 20%, transparent), transparent 70%),
    radial-gradient(26% 30% at 18% 86%, color-mix(in srgb, var(--c-green) 16%, transparent), transparent 70%);
  filter: blur(30px);
}}
.dash-skeleton {{ background: var(--m-soft); border-radius: 16px; }}
"""

WEB = """
/* web-only: colour field lives on the page, theme toggle, floating dock on phones */
.bx-web .bx::before { display: none; }
.bx { max-width: 1320px; margin-inline: auto; }
.bx-theme {
  position: absolute; top: 18px; right: 18px; z-index: 2; width: 42px; height: 42px; border-radius: 14px; cursor: pointer;
  display: grid; place-items: center; color: #ffffff; background: rgba(255, 255, 255, .09);
  border: 1px solid rgba(255, 255, 255, .18); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .18); transition: background .15s ease, transform .15s ease;
}
.bx-theme:hover { background: rgba(255, 255, 255, .18); transform: rotate(-12deg); }
.bx-theme svg { width: 19px; height: 19px; }
.bx-theme .i-sun { display: none; }
:root[data-theme="dark"] .bx-theme .i-sun { display: block; }
:root[data-theme="dark"] .bx-theme .i-moon { display: none; }
.bx-hero .bx-eyebrow { margin-right: 56px; }
@media (prefers-reduced-motion: no-preference) {
  body::before { animation: bx-field 28s ease-in-out infinite alternate; }
  @keyframes bx-field { from { transform: translate3d(0, 0, 0) scale(1); } to { transform: translate3d(-3%, 2%, 0) scale(1.06); } }
}
@media (max-width: 979px) {
  body.bx-web { padding-bottom: 104px; }
  .bx-web .bx > .bx-tabs {
    position: fixed; z-index: 30; top: auto;
    left: max(12px, env(safe-area-inset-left, 0px)); right: max(12px, env(safe-area-inset-right, 0px));
    bottom: calc(12px + env(safe-area-inset-bottom, 0px));
    padding: 7px; border-radius: 22px;
    background: color-mix(in srgb, var(--m-panel) 72%, transparent);
    box-shadow: inset 0 1px 0 var(--g-hi), 0 18px 40px -12px rgba(0, 0, 0, .35);
  }
}
"""

HEAD_THEME = """(() => { try { const t = localStorage.getItem('bx-theme'); document.documentElement.dataset.theme = t || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); } catch (e) { document.documentElement.dataset.theme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; } })();"""

AFTER = """
(() => {
  const root = document.documentElement;
  document.querySelectorAll('.bx-theme').forEach((b) => b.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('bx-theme', next); } catch (e) { /* private mode */ }
    window.dispatchEvent(new Event('resize'));
  }));
  // keep the open section's button in view inside the phone dock
  document.addEventListener('click', (ev) => {
    const tab = ev.target.closest('.bx-tab');
    if (tab) tab.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
  });
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.bx-kpi-v b[data-draw]').forEach((el) => {
    const final = el.textContent;
    const m = final.match(/^([0-9][0-9,]*\\.?[0-9]*)(.*)$/);
    if (!m) return;
    const target = parseFloat(m[1].replace(/,/g, ''));
    const dec = (m[1].split('.')[1] || '').length;
    const t0 = performance.now(); const dur = 1100;
    const step = (t) => {
      const p = Math.min(1, (t - t0) / dur); const e = 1 - Math.pow(1 - p, 3);
      el.textContent = p < 1 ? (target * e).toFixed(dec) + m[2] : final;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });
})();
"""

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>Badminton Arena</title>
<meta name="description" content="Player-by-player analysis of {len(json.load(open('tables.json', encoding='utf-8'))['matches'])} doubles matches over {_nd} session days: results, form, partnerships, opponents, pressure and adjusted strength models.">
<script>{HEAD_THEME}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400..800&family=Geist+Mono:wght@400..600&family=Inter:wght@400..800&family=Orbitron:wght@500..900&display=swap">
<style>{TOKENS}
{css}
{MODERN}
{GLASS}
{PICKER}
{WEB}
{PHOTO_CSS}
{ARENA_CSS}
{RECAP_CSS}
{FX_CSS}</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
</head>
<body class="bx-web">
<script type="application/json" id="bx-data">{data_json}</script>
<script>{open('web_shim.js', encoding='utf-8').read()}</script>
{page}
<script>{app}</script>
<script>dash.start();</script>
<script>{AFTER}</script>
<script>{photo_js(PHOTOS)}</script>
<script>{arena_js(ARENA_CFG)}</script>
<script>{FX_JS}</script>
</body>
</html>
"""
out = os.environ.get('BX_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'badminton-season-report.html')
open(out, 'w', encoding='utf-8').write(html)
print(out, len(html.encode('utf-8')))
