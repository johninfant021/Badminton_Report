"""Photo layer: player pictures from ../Profile across the report, plus a ranked squad section.

apply_photos(page) adds the squad markup; PHOTO_CSS and photo_js() are added to the page by build_web_2026.py.
"""
import json, os
from html import escape
from photos import all_photos

HERE = os.path.dirname(os.path.abspath(__file__))
P = ['Anto', 'Jothi Sai', 'John', 'Pawan', 'Dinesh', 'Pratap', 'Bhanu']
SLUG = {'Anto': 'anto', 'Jothi Sai': 'jothi', 'John': 'john', 'Pawan': 'pawan', 'Dinesh': 'dinesh', 'Pratap': 'pratap', 'Bhanu': 'bhanu'}
MINUS = '−'


def _sg(x):
    return (f'{x:+.2f}').replace('-', MINUS)


def _squad(photos):
    T = json.load(open(os.path.join(HERE, 'tables.json'), encoding='utf-8'))
    E = {e['player']: e for e in T['estimates']}
    PL = {x['player']: x for x in T['players']}
    CMP = {x['player']: x for x in json.load(open(os.path.join(HERE, 'dash', 'data', 'comparison.json'), encoding='utf-8'))}
    order = sorted(P, key=lambda p: E[p]['adj_rank'])
    cards = []
    for p in order:
        e, x = E[p], PL[p]
        last = []
        for m in reversed(T['matches']):
            a, b = m['team_a'].split(' + '), m['team_b'].split(' + ')
            if p in a or p in b:
                last.append(m['winner'] == m['team_a'] if p in a else m['winner'] == m['team_b'])
            if len(last) == 5:
                break
        dots = ''.join(f'<i class="{"w" if w else "l"}" title="{"Won" if w else "Lost"}"></i>' for w in reversed(last))
        move = e['recent_adj'] - e['adj']
        arrow = ('up', '↗') if move > 0.25 else (('down', '↘') if move < -0.25 else ('flat', '→'))
        cards.append(
            f'<button type="button" class="bx-sq" data-goto-player="{SLUG[p]}" style="--pc: var(--series-{P.index(p) + 1})" aria-label="Open {escape(p)}’s report">'
            f'<span class="bx-sq-ph"><img data-ph-portrait="{escape(p)}" alt="" decoding="async"></span>'
            f'<span class="bx-sq-rank">{e["adj_rank"]}</span>'
            f'<span class="bx-sq-tt">{x["titles"]} title{"s" if x["titles"] != 1 else ""}</span>'
            f'<span class="bx-sq-body">'
            f'<span class="bx-sq-name">{escape(p)}</span>'
            f'<span class="bx-sq-rec">{x["record"]} <em>·</em> {x["win_pct"] * 100:.0f}%</span>'
            f'<span class="bx-sq-row"><span class="bx-sq-adj"><b>{_sg(e["adj"])}</b><small>adjusted</small></span>'
            f'<span class="bx-sq-mv bx-mv-{arrow[0]}" title="Recent level {_sg(e["recent_adj"])}">{arrow[1]} {escape(CMP[p]["trend"])}</span></span>'
            f'<span class="bx-sq-form" aria-label="Last five results">{dots}</span>'
            f'</span></button>')
    return ('<div class="bx-squad-wrap"><div class="bx-squad-head"><h2 id="squad">The squad</h2>'
            '<p>Ranked by adjusted strength · last five results · tap a player for the full report</p></div>'
            f'<div class="bx-squad">{"".join(cards)}</div></div>')


def apply_photos(page):
    photos = all_photos()
    old = '<section class="bx-sec" id="summary" data-panel="summary">\n<h2>Executive summary</h2>'
    assert page.count(old) == 1
    page = page.replace(old, old.replace('<h2>', _squad(photos) + '<h2>'), 1)
    return page, photos


def photo_js(photos):
    ph = {p: dict(a=v['avatar'], p=v['portrait']) for p, v in photos.items()}
    return ("(() => {\nconst PH = " + json.dumps(ph) + ";\nconst SLUG = " + json.dumps(SLUG) + ";\n" + r"""
const BY_SLUG = Object.fromEntries(Object.entries(SLUG).map(([n, s]) => [s, n]));
const NAMES = Object.keys(PH);
const img = (name, cls, kind = 'a') => { const i = document.createElement('img'); i.className = cls; i.src = PH[name][kind]; i.alt = ''; i.decoding = 'async'; return i; };
const once = (el) => { if (el.dataset.ph) return false; el.dataset.ph = '1'; return true; };
function enhance() {
  document.querySelectorAll('img[data-ph-portrait]:not([src])').forEach((i) => { const n = i.dataset.phPortrait; if (PH[n]) i.src = PH[n].p; });
  // hero chips
  document.querySelectorAll('.bx-chip').forEach((c) => {
    const n = c.querySelector('.bx-chip-name')?.textContent; if (!PH[n] || !once(c)) return;
    const wrap = document.createElement('span'); wrap.className = 'bx-chip-ph'; wrap.append(img(n, 'bx-ph-i'));
    const r = c.querySelector('.bx-chip-rank'); if (r) wrap.append(r);
    c.prepend(wrap); c.classList.add('has-ph');
  });
  // player chooser
  document.querySelectorAll('.bx-pick-b').forEach((b) => {
    const n = BY_SLUG[b.dataset.player]; const av = b.querySelector('.bx-pk-av'); if (!n || !av || !once(av)) return;
    av.replaceChildren(img(n, 'bx-ph-i')); av.classList.add('has-ph');
  });
  // report headers
  document.querySelectorAll('.bx-pr').forEach((a) => {
    const n = BY_SLUG[a.dataset.player]; const av = a.querySelector('.bx-av'); if (!n || !av || !once(av)) return;
    av.replaceChildren(img(n, 'bx-ph-i', 'p')); av.classList.add('has-ph');
  });
  // previous / next
  document.querySelectorAll('.bx-pn-b').forEach((b) => {
    const n = BY_SLUG[b.dataset.goto]; const t = b.querySelector('.bx-pn-n'); if (!n || !t || !once(b)) return;
    t.prepend(img(n, 'bx-ph-mini'));
  });
  // table cells naming a player, or a pair
  document.querySelectorAll('.bx-table tbody td').forEach((td) => {
    if (td.dataset.ph || td.children.length) return;
    const t = td.textContent.trim();
    if (PH[t]) { once(td); td.classList.add('has-ph'); td.prepend(img(t, 'bx-ph-mini')); return; }
    const pr = t.split(' + ');
    if (pr.length === 2 && PH[pr[0]] && PH[pr[1]]) {
      once(td); td.classList.add('has-ph');
      const s = document.createElement('span'); s.className = 'bx-ph-pair'; s.append(img(pr[0], 'bx-ph-mini'), img(pr[1], 'bx-ph-mini')); td.prepend(s);
    }
  });
  // list items that start with a player's name
  document.querySelectorAll('.bx-list > li > b:first-child').forEach((b) => {
    const n = b.textContent.trim().replace(/\.$/, ''); if (!PH[n] || !once(b)) return;
    b.classList.add('has-ph'); b.prepend(img(n, 'bx-ph-mini'));
  });
  // strengths cards
  document.querySelectorAll('#strengths .bx-card[id^="sw-"] .bx-card-head h3').forEach((h) => {
    const n = h.textContent.trim(); if (!PH[n] || !once(h)) return;
    h.classList.add('has-ph'); h.prepend(img(n, 'bx-ph-head'));
  });
}
let q = false;
const sched = () => { if (q) return; q = true; requestAnimationFrame(() => { q = false; enhance(); }); };
enhance();
new MutationObserver(sched).observe(document.body, { childList: true, subtree: true });
// squad cards open that player's report
document.addEventListener('click', (ev) => {
  const c = ev.target.closest('[data-goto-player]'); if (!c) return;
  document.querySelector('.bx-tab[data-tab="players"]')?.click();
  requestAnimationFrame(() => {
    document.querySelector(`.bx-pick-b[data-player="${c.dataset.gotoPlayer}"]`)?.click();
    document.getElementById('p-' + c.dataset.gotoPlayer)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});
})();
""")


PHOTO_CSS = r"""
/* ================= photo layer ================= */
.bx-ph-i { width: 100%; height: 100%; object-fit: cover; display: block; border-radius: inherit; }
.bx-ph-mini {
  width: 26px; height: 26px; border-radius: 50%; object-fit: cover; flex: none; vertical-align: middle; margin-right: 9px;
  box-shadow: 0 0 0 2px var(--m-panel), 0 0 0 3.5px var(--pc, var(--m-line));
}
.bx-ph-head { width: 40px; height: 40px; border-radius: 14px; object-fit: cover; margin-right: 12px; box-shadow: 0 0 0 2px color-mix(in srgb, var(--pc) 60%, transparent), 0 10px 22px -12px var(--pc); }

/* squad */
.bx-squad-wrap { display: grid; gap: 14px; margin-bottom: 8px; }
.bx-squad-head { display: flex; align-items: baseline; justify-content: space-between; gap: 6px 16px; flex-wrap: wrap; }
.bx-squad-head h2 { margin: 0; }
.bx-squad-head p { margin: 0; font-family: var(--m-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: var(--m-muted); }
.bx-squad { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 12px; }
.bx-sq {
  position: relative; display: block; aspect-ratio: 3 / 4.7; padding: 0; overflow: hidden; isolation: isolate; cursor: pointer;
  border-radius: 22px; border: 1px solid color-mix(in srgb, var(--pc) 35%, var(--g-edge)); background: #0b0f1a; color: #ffffff; text-align: left;
  font-family: var(--m-body); box-shadow: var(--m-shadow);
  transition: transform .25s cubic-bezier(.2, .7, .2, 1), box-shadow .25s ease, border-color .25s ease;
}
.bx-sq-ph { position: absolute; inset: 0; z-index: -2; }
.bx-sq-ph img { width: 100%; height: 100%; object-fit: cover; transform: scale(1.02); transition: transform .5s cubic-bezier(.2, .7, .2, 1), filter .3s ease; }
.bx-sq::before {
  content: ""; position: absolute; inset: 0; z-index: -1;
  background: linear-gradient(180deg, rgba(5, 8, 16, 0) 38%, rgba(5, 8, 16, .6) 62%, color-mix(in srgb, var(--pc) 30%, #05080f) 100%);
}
.bx-sq:hover { transform: translateY(-4px); border-color: var(--pc); box-shadow: 0 24px 44px -24px var(--pc), var(--m-shadow); }
.bx-sq:hover .bx-sq-ph img { transform: scale(1.08); }
.bx-sq:focus-visible { outline: 2px solid var(--pc); outline-offset: 3px; }
.bx-sq-rank {
  position: absolute; top: 10px; left: 10px; min-width: 30px; height: 30px; padding: 0 8px; border-radius: 10px; display: grid; place-items: center;
  font-family: var(--m-display); font-weight: 800; font-size: 15px; color: #ffffff;
  background: color-mix(in srgb, var(--pc) 80%, #000000); box-shadow: 0 6px 16px -6px var(--pc), inset 0 1px 0 rgba(255, 255, 255, .25);
}
.bx-sq:first-child .bx-sq-rank { background: linear-gradient(135deg, #ffd34d, #f2a900); color: #2a1b00; box-shadow: 0 6px 18px -6px #f2b400; }
.bx-sq-tt {
  position: absolute; top: 10px; right: 10px; padding: 4px 9px; border-radius: 999px;
  font-family: var(--m-mono); font-size: 10.5px; font-weight: 600; letter-spacing: .02em; color: #ffffff;
  background: rgba(10, 14, 24, .55); -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, .16);
}
.bx-sq-body { position: absolute; inset: auto 0 0 0; display: grid; gap: 4px; padding: 12px 12px 13px; }
.bx-sq-name { font-family: var(--m-display); font-weight: 800; font-size: 19px; letter-spacing: -.025em; line-height: 1.05; text-shadow: 0 2px 12px rgba(0, 0, 0, .5); }
.bx-sq-rec { font-family: var(--m-mono); font-size: 11.5px; color: rgba(255, 255, 255, .78); }
.bx-sq-rec em { font-style: normal; opacity: .5; }
.bx-sq-row { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; margin-top: 2px; }
.bx-sq-adj { display: grid; line-height: 1; }
.bx-sq-adj b { font-family: var(--m-display); font-size: 22px; font-weight: 800; letter-spacing: -.03em; }
.bx-sq-adj small { font-family: var(--m-mono); font-size: 9px; letter-spacing: .08em; text-transform: uppercase; color: rgba(255, 255, 255, .6); margin-top: 3px; }
.bx-sq-mv { max-width: 100%; overflow: hidden; text-overflow: ellipsis; font-size: 10.5px; font-weight: 700; padding: 3px 8px; border-radius: 999px; white-space: nowrap; color: rgba(255, 255, 255, .85); background: rgba(255, 255, 255, .14); }
.bx-mv-up { color: #6ff2b4; background: rgba(23, 178, 106, .22); }
.bx-mv-down { color: #ff9db1; background: rgba(217, 45, 80, .24); }
.bx-sq-form { display: flex; gap: 4px; margin-top: 4px; }
.bx-sq-form i { flex: 1; height: 4px; border-radius: 4px; background: rgba(255, 255, 255, .22); }
.bx-sq-form i.w { background: #3fd68e; box-shadow: 0 0 8px rgba(63, 214, 142, .6); }
.bx-sq-form i.l { background: rgba(255, 107, 139, .75); }
@media (max-width: 1280px) { .bx-squad { grid-template-columns: repeat(4, minmax(0, 1fr)); } .bx-sq:first-child { grid-column: span 1; } }
@media (max-width: 760px) {
  .bx-squad { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 10px; padding-bottom: 6px; margin-inline: -2px; scrollbar-width: none; }
  .bx-squad::-webkit-scrollbar { display: none; }
  .bx-sq { flex: 0 0 46%; scroll-snap-align: start; }
}

/* hero chips with faces */
.bx-chip.has-ph { padding-left: 6px; gap: 10px; }
.bx-chip-ph { position: relative; flex: none; width: 38px; height: 38px; border-radius: 50%; box-shadow: 0 0 0 2px var(--pc); }
.bx-chip-ph .bx-ph-i { border-radius: 50%; }
.bx-chip.has-ph .bx-chip-rank {
  position: absolute; right: -5px; bottom: -4px; width: 17px; height: 17px; min-width: 0; margin: 0; padding: 0; border-radius: 50%;
  display: grid; place-items: center; font-size: 9.5px; line-height: 1; box-shadow: 0 0 0 2px #0b1020;
}

/* chooser: face instead of initials */
.bx-pk-av.has-ph { padding: 0; overflow: hidden; border-radius: 50%; width: 52px; height: 52px; background: none; box-shadow: 0 0 0 2px var(--pc), 0 10px 22px -10px var(--pc); }
.bx-pick-b[aria-pressed=true] .bx-pk-av.has-ph { background: none; box-shadow: 0 0 0 2px #ffffff, 0 0 0 5px color-mix(in srgb, var(--pc) 60%, transparent); }
@media (max-width: 560px) { .bx-pk-av.has-ph { width: 40px; height: 40px; } }

/* report header: portrait */
.bx-pr-head:has(.bx-av.has-ph) { padding: 18px 26px 18px 18px; gap: 26px; min-height: 0; align-items: center; }
.bx-av.has-ph {
  width: 148px; height: 185px; padding: 0; border-radius: 22px; overflow: hidden; flex: none; background: #0b0f1a;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, .14), 0 0 0 5px color-mix(in srgb, var(--pc) 35%, transparent), 0 26px 48px -22px var(--pc);
}
.bx-pr-head:has(.bx-av.has-ph) .bx-pr-name { font-size: clamp(30px, 4vw, 46px); letter-spacing: -.035em; line-height: 1; }
@media (max-width: 560px) {
  .bx-pr-head:has(.bx-av.has-ph) { padding: 14px; gap: 16px; }
  .bx-av.has-ph { width: 96px; height: 120px; border-radius: 18px; }
}

/* tables, lists, prev/next */
.bx-table td.has-ph { white-space: nowrap; }
.bx-table td.pl.has-ph::before { display: none; }
.bx-ph-pair { display: inline-flex; margin-right: 9px; vertical-align: middle; }
.bx-ph-pair .bx-ph-mini { margin-right: 0; width: 24px; height: 24px; }
.bx-ph-pair .bx-ph-mini + .bx-ph-mini { margin-left: -8px; }
.bx-list > li > b.has-ph { display: inline-flex; align-items: center; }
.bx-list > li > b.has-ph .bx-ph-mini { width: 24px; height: 24px; margin-right: 8px; }
#strengths .bx-card[id^="sw-"] .bx-card-head h3.has-ph::before { display: none; }
#strengths .bx-card[id^="sw-"] .bx-card-head h3.has-ph { display: flex; align-items: center; font-size: 20px; }
.bx-pn-n { display: inline-flex; align-items: center; }
.bx-pn-n .bx-ph-mini { width: 28px; height: 28px; margin: 0 8px; }
.bx-pn-next .bx-pn-n { flex-direction: row; }
"""
