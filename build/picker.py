import re

ORDER = [('anto', 'Anto', 'AN'), ('jothi', 'Jothi Sai', 'JS'), ('john', 'John', 'JO'), ('pawan', 'Pawan', 'PA'),
         ('dinesh', 'Dinesh', 'DI'), ('pratap', 'Pratap', 'PR'), ('bhanu', 'Bhanu', 'BH')]


def restyle_picker(page):
    """Player chooser as cards that read as buttons, plus previous/next buttons under each report."""
    old = '<div class="bx-pick" role="group" aria-label="Choose a player">'
    assert page.count(old) == 1
    page = page.replace(old, '<p class="bx-pick-hint">Choose a player to open their report</p>' + old, 1)
    for slug, name, ini in ORDER:
        m = re.search(rf'<button type="button" class="bx-pick-b" data-player="{slug}" data-initials="{ini}" aria-pressed="(true|false)">{re.escape(name)}</button>', page)
        assert m, slug
        new = (f'<button type="button" class="bx-pick-b" data-player="{slug}" data-initials="{ini}" aria-pressed="{m.group(1)}" aria-controls="p-{slug}">'
               f'<span class="bx-pk-av" aria-hidden="true">{ini}</span>'
               f'<span class="bx-pk-body"><span class="bx-pk-name">{name}</span>'
               f'<span class="bx-pk-stat"><b data-draw="v" data-source="players" data-field="record" data-where="player={name}" data-fmt="text">—</b>'
               f' · <b data-draw="v" data-source="estimates" data-field="adj" data-where="player={name}" data-fmt="s2">—</b></span>'
               f'<span class="bx-pk-cta"><span class="bx-pk-open">View report</span><span class="bx-pk-on">Viewing now</span></span></span></button>')
        page = page.replace(m.group(0), new, 1)
    for i, (slug, name, ini) in enumerate(ORDER):
        ps, pn, _ = ORDER[i - 1]
        ns, nn, _ = ORDER[(i + 1) % len(ORDER)]
        art = re.search(rf'<article class="bx-pr" id="p-{slug}".*?</article>', page, re.S).group(0)
        foot = '<p class="bx-pr-foot">'
        assert art.count(foot) == 1
        nav = (f'<div class="bx-pn" role="group" aria-label="More player reports">'
               f'<button type="button" class="bx-pn-b bx-pn-prev" data-goto="{ps}"><span class="bx-pn-k">Previous player</span><span class="bx-pn-n">{pn}</span></button>'
               f'<button type="button" class="bx-pn-b bx-pn-next" data-goto="{ns}"><span class="bx-pn-k">Next player</span><span class="bx-pn-n">{nn}</span></button></div>')
        page = page.replace(art, art.replace(foot, nav + foot, 1), 1)
    return page


PICKER = r"""
/* ---------- player chooser: cards that read as buttons ---------- */
.bx-pick-hint { display: flex; align-items: center; gap: 10px; margin: 0; font-family: var(--m-mono); font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--m-muted); }
.bx-pick-hint::after { content: "\2193"; font-size: 14px; color: var(--sc); }
.bx-pick { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 176px), 1fr)); gap: 12px; }
.bx-pick-b {
  position: relative; display: flex; align-items: center; gap: 12px; width: 100%; min-height: 0;
  padding: 12px 34px 12px 12px; border-radius: 18px; text-align: left; cursor: pointer; color: var(--m-fg);
  font-family: var(--m-body); font-size: 14px; font-weight: 600;
  background: var(--g-fill); -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  border: 1px solid color-mix(in srgb, var(--pc) 38%, var(--g-edge));
  box-shadow: inset 0 1px 0 var(--g-hi), var(--m-shadow-sm);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease, background .18s ease;
}
.bx-pick-b::before { display: none; }
.bx-pick-b::after { content: "\2192"; position: absolute; top: 50%; right: 14px; margin-top: -10px; font-size: 16px; line-height: 20px; font-weight: 700; color: var(--pc); transition: transform .18s ease; }
.bx-pick-b:hover { transform: translateY(-2px); color: var(--m-fg); border-color: var(--pc); background: color-mix(in srgb, var(--pc) 10%, var(--g-fill)); box-shadow: inset 0 1px 0 var(--g-hi), 0 16px 30px -18px var(--pc); }
.bx-pick-b:hover::after { transform: translateX(4px); }
.bx-pick-b:active { transform: translateY(0) scale(.985); }
.bx-pk-av {
  width: 44px; height: 44px; border-radius: 14px; flex: none; display: grid; place-items: center;
  font-family: var(--m-display); font-weight: 800; font-size: 15px; letter-spacing: -.01em; color: #ffffff;
  background: linear-gradient(135deg, var(--pc), color-mix(in srgb, var(--pc) 55%, #000000));
  box-shadow: 0 8px 18px -10px var(--pc);
}
.bx-pk-body { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.bx-pk-name { font-family: var(--m-display); font-weight: 700; font-size: 16px; letter-spacing: -.02em; line-height: 1.2; }
.bx-pk-stat { font-family: var(--m-mono); font-size: 11px; color: var(--m-muted); white-space: nowrap; }
.bx-pk-stat b[data-draw] { font-weight: 600; color: var(--m-fg); }
.bx-pk-cta { margin-top: 3px; font-size: 12px; font-weight: 700; color: color-mix(in srgb, var(--pc) 78%, var(--m-fg)); }
.bx-pk-on { display: none; }
.bx-pick-b[aria-pressed=true] {
  color: #ffffff; border-color: transparent; transform: none;
  background: linear-gradient(135deg, color-mix(in srgb, var(--pc) 72%, #000000), color-mix(in srgb, var(--pc) 42%, #0b1020));
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--pc) 32%, transparent), 0 16px 30px -18px var(--pc);
}
.bx-pick-b[aria-pressed=true]::after { content: "\2713"; color: #ffffff; transform: none; }
.bx-pick-b[aria-pressed=true] .bx-pk-av { background: #ffffff; color: color-mix(in srgb, var(--pc) 70%, #000000); box-shadow: none; }
.bx-pick-b[aria-pressed=true] .bx-pk-stat { color: rgba(255, 255, 255, .72); }
.bx-pick-b[aria-pressed=true] .bx-pk-stat b[data-draw] { color: #ffffff; }
.bx-pick-b[aria-pressed=true] .bx-pk-cta { color: #ffffff; }
.bx-pick-b[aria-pressed=true] .bx-pk-open { display: none; }
.bx-pick-b[aria-pressed=true] .bx-pk-on { display: inline; }
.bx-pick-b:focus-visible { outline: 2px solid var(--pc); outline-offset: 3px; }

/* previous / next player */
.bx-pn { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.bx-pn-b {
  display: flex; flex-direction: column; gap: 2px; padding: 14px 18px; border-radius: 18px; cursor: pointer;
  font-family: var(--m-body); color: var(--m-fg); text-align: left;
  background: var(--g-fill); -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  border: 1px solid var(--g-edge); box-shadow: inset 0 1px 0 var(--g-hi), var(--m-shadow-sm);
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.bx-pn-next { text-align: right; align-items: flex-end; }
.bx-pn-b:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--sc) 55%, var(--g-edge)); box-shadow: inset 0 1px 0 var(--g-hi), var(--m-shadow-hover); }
.bx-pn-k { font-family: var(--m-mono); font-size: 10.5px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--m-muted); }
.bx-pn-n { font-family: var(--m-display); font-size: 18px; font-weight: 700; letter-spacing: -.02em; }
.bx-pn-prev .bx-pn-n::before { content: "\2190  "; color: var(--sc); }
.bx-pn-next .bx-pn-n::after { content: "  \2192"; color: var(--sc); }
.bx-pn-b:focus-visible { outline: 2px solid var(--sc); outline-offset: 3px; }
@media (max-width: 560px) {
  .bx-pick { grid-template-columns: 1fr 1fr; gap: 10px; }
  .bx-pick-b { padding: 10px 26px 10px 10px; gap: 10px; border-radius: 16px; }
  .bx-pick-b::after { right: 10px; }
  .bx-pk-av { width: 36px; height: 36px; border-radius: 12px; font-size: 13px; }
  .bx-pk-name { font-size: 14.5px; }
  .bx-pk-stat { font-size: 10px; }
}
"""
