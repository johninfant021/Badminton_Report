"""Versus page: head-to-head compare for any two players, and a match predictor / team balancer.

Everything is computed here from the build tables and shipped as one JSON blob; the page script only
looks things up and draws. The predictor uses the season model directly: a team's expected margin is
the sum of its two players' values minus the other pair's, and the model's leftover spread (sigma)
turns that margin into a win chance.
"""
import json
from html import escape


def _team(s):
    return [x.strip() for x in s.split(' + ')]


def versus_data(T, P, slug, col, sigma):
    PL = {r['player']: r for r in T['players']}
    E = {r['player']: r for r in T['estimates']}
    PR = {r['player']: r for r in T['pressure']}
    OPP = {(r['player'], r['opponent']): r for r in T['opponents']}
    PAIR = {}
    for r in T['pairs']:
        PAIR[(r['a'], r['b'])] = PAIR[(r['b'], r['a'])] = r
    rank = {p: i + 1 for i, p in enumerate(sorted(P, key=lambda q: -E[q]['adj']))}
    players = {}
    for p in P:
        pl, e = PL[p], E[p]
        players[p] = dict(slug=slug[p], col=col(p), rank=rank[p], rec=pl['record'], win=pl['win_pct'], dpm=pl['dpm'], adj=e['adj'],
                          radj=e['recent_adj'], elo=e['elo'], titles=pl['titles'], fw=pl['fin_W'], fl=pl['fin_L'],
                          r20=pl.get('recent_record', ''), r20d=pl.get('recent_dpm', 0), clutch=PR[p]['clutch'] if p in PR else 0, days=pl['days'])
    # every meeting between two players on opposite sides, and every match they played together
    h2h = {}
    for m in T['matches']:
        A, B = _team(m['team_a']), _team(m['team_b'])
        for side, other, sf, so in ((A, B, m['score_a'], m['score_b']), (B, A, m['score_b'], m['score_a'])):
            for x in side:
                for y in other:
                    h2h.setdefault(f'{x}|{y}', []).append([m['day'], m['stage'], ' + '.join(side), ' + '.join(other), sf, so])
    vs = {}
    for x in P:
        for y in P:
            if x == y:
                continue
            o = OPP.get((x, y)); pr = PAIR.get((x, y))
            vs[f'{x}|{y}'] = dict(P=o['P'] if o else 0, W=o['W'] if o else 0, L=o['L'] if o else 0, dpm=o['dpm'] if o else 0,
                                 expW=o['exp_W'] if o else 0, last=h2h.get(f'{x}|{y}', [])[-6:],
                                 tP=pr['P'] if pr else 0, tW=pr['W'] if pr else 0, tL=pr['L'] if pr else 0, tdpm=pr['dpm'] if pr else 0,
                                 tvs=pr['vs_exp'] if pr else 0)
    fin = next((m for m in reversed(T['matches']) if m['stage'] == 'Final'), None)
    start = dict(a=_team(fin['team_a']), b=_team(fin['team_b']), day=fin['day']) if fin else None
    return dict(players=players, order=sorted(P, key=lambda q: rank[q]), vs=vs, sigma=round(sigma, 3), start=start,
                n=len(T['matches']))


def versus_html(T, P, slug, col, sigma):
    data = versus_data(T, P, slug, col, sigma)
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    order = data['order']
    av = lambda p: f'<img class="vs-av" data-ph-avatar="{escape(p)}" alt="" style="--pc:{col(p)}">'
    chips = lambda side: ''.join(f'<button type="button" class="vs-chip" data-side="{side}" data-p="{escape(p)}" style="--pc:{col(p)}" aria-pressed="false">{av(p)}<span>{escape(p)}</span></button>' for p in order)
    ports = lambda side: ''.join(f'<img class="vs-ph" data-ph-portrait="{escape(p)}" data-p="{escape(p)}" alt="" style="--pc:{col(p)}">' for p in order)
    pool = ''.join(f'<button type="button" class="pr-chip" data-p="{escape(p)}" style="--pc:{col(p)}">{av(p)}<span>{escape(p)}</span><i class="pr-tag"></i></button>' for p in order)
    slot = lambda k, lab: f'<button type="button" class="pr-slot" data-slot="{k}"><span class="pr-slot-e">{lab}</span></button>'
    return (
        '<section class="bx-sec vs" id="versus" data-panel="versus" hidden>\n'
        '<h2>Head to head</h2>\n'
        '<p class="bx-prose vs-brief">Pick any two players to see how they do against each other, how they do as partners and how their season numbers compare. '
        'Below, put any four players into two teams and the season model predicts the game; it can also find the fairest way to split them.</p>\n'
        # ---------------- compare
        '<div class="vs-card">'
        '<div class="vs-picks"><div class="vs-pick a"><small>Player 1</small><div class="vs-chips">' + chips('a') + '</div></div>'
        '<div class="vs-pick b"><small>Player 2</small><div class="vs-chips">' + chips('b') + '</div></div></div>'
        '<div class="vs-stage">'
        '<div class="vs-side a"><div class="vs-frame">' + ports('a') + '</div><div class="vs-who"><b data-k="a-name"></b><small data-k="a-sub"></small></div></div>'
        '<div class="vs-mid"><span class="vs-vs">VS</span><div class="vs-score"><b data-k="a-w">0</b><i>–</i><b data-k="b-w">0</b></div><small data-k="h2h-sub"></small>'
        '<button type="button" class="vs-swap" aria-label="Swap the two players"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 4 3 8l4 4"/><path d="M3 8h14"/><path d="m17 20 4-4-4-4"/><path d="M21 16H7"/></svg>Swap</button></div>'
        '<div class="vs-side b"><div class="vs-frame">' + ports('b') + '</div><div class="vs-who"><b data-k="b-name"></b><small data-k="b-sub"></small></div></div>'
        '</div>'
        '<div class="vs-boxes">'
        '<div class="vs-box"><h3>Against each other</h3><div data-k="against"></div></div>'
        '<div class="vs-box"><h3>As partners</h3><div data-k="together"></div></div>'
        '</div>'
        '<div class="vs-bars" data-k="bars"></div>'
        '</div>\n'
        # ---------------- predictor
        '<div class="pr-card">'
        '<div class="pr-hd"><div><h3>Match predictor</h3><p>Tap four players to fill the two teams; tap a slot to empty it.</p></div>'
        '<div class="pr-mode" role="group" aria-label="Strength used"><button type="button" data-mode="adj" aria-pressed="true">Season</button><button type="button" data-mode="radj" aria-pressed="false">Current form</button></div></div>'
        '<div class="pr-pool">' + pool + '</div>'
        '<div class="pr-court">'
        '<div class="pr-team a"><small>Team A</small><div class="pr-slots">' + slot('a0', 'Player') + slot('a1', 'Player') + '</div></div>'
        '<div class="pr-res" data-k="res"><span class="pr-hint">Pick four players</span></div>'
        '<div class="pr-team b"><small>Team B</small><div class="pr-slots">' + slot('b0', 'Player') + slot('b1', 'Player') + '</div></div>'
        '</div>'
        '<div class="pr-actions"><button type="button" class="ar-cta" data-act="balance">Balance teams</button>'
        '<button type="button" class="ar-cta ghost" data-act="random">Random four</button><button type="button" class="ar-cta ghost" data-act="clear">Clear</button></div>'
        '<div class="pr-splits" data-k="splits"></div>'
        f'<p class="pr-note">Season model built from all {data["n"]} matches: a team’s expected margin is the sum of its two players’ values minus the other pair’s; '
        f'margins still vary by about {data["sigma"]:.1f} points a game around that, which sets the win chance. “Current form” uses the recency-weighted values.</p>'
        '</div>\n'
        f'<script type="application/json" id="vs-data">{blob}</script>\n'
        '</section>\n')


VERSUS_CSS = r"""
/* ================= versus page ================= */
.vs-brief { max-width: 80ch; }
.vs-card, .pr-card { position: relative; display: grid; gap: 18px; padding: 20px; border-radius: 24px; background: var(--ar-glass); border: 1px solid var(--ar-line); box-shadow: var(--ar-shadow); min-width: 0; }
.pr-card { margin-top: 22px; }
.vs-card, .pr-card { grid-template-columns: minmax(0, 1fr); }
.vs-pick, .vs-box, .pr-team, .pr-res, .pr-pool, .vs-chips { min-width: 0; }
.vs-picks { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.vs-pick small, .pr-team small { display: block; margin-bottom: 8px; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .18em; text-transform: uppercase; color: var(--ar-mut); }
.vs-pick.a small { color: var(--ar-lime); } .vs-pick.b small { color: var(--ar-cyan); }
.vs-chips, .pr-pool { display: flex; flex-wrap: wrap; gap: 6px; }
.vs-chip, .pr-chip { position: relative; display: inline-flex; align-items: center; gap: 7px; padding: 4px 11px 4px 4px; border-radius: 999px; cursor: pointer; font: 600 13px var(--m-body); color: var(--ar-fg);
  background: rgba(255, 255, 255, .03); border: 1px solid var(--ar-line); transition: border-color .2s ease, background-color .2s ease, transform .2s ease; }
.vs-chip:hover, .pr-chip:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--pc) 60%, transparent); }
.vs-chip[aria-pressed="true"] { border-color: var(--pc); background: color-mix(in srgb, var(--pc) 18%, transparent); box-shadow: 0 0 16px color-mix(in srgb, var(--pc) 35%, transparent); }
.vs-chip:disabled { opacity: .35; cursor: not-allowed; transform: none; }
.vs-av { width: 26px; height: 26px; border-radius: 50%; object-fit: cover; border: 2px solid var(--pc); background: #0D121B; flex: none; }

.vs-stage { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 18px; padding: 8px 0; }
.vs-side { display: flex; align-items: center; gap: 16px; min-width: 0; }
.vs-side.b { flex-direction: row-reverse; text-align: right; }
.vs-frame { position: relative; flex: none; width: clamp(96px, 12vw, 150px); aspect-ratio: 3 / 4; border-radius: 16px; overflow: hidden; background: #0D121B;
  border: 2px solid var(--cur, var(--ar-line2)); box-shadow: 0 0 26px color-mix(in srgb, var(--cur, transparent) 45%, transparent); transition: border-color .3s ease, box-shadow .3s ease; }
.vs-ph { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transform: scale(1.06); transition: opacity .35s ease, transform .5s var(--ar-ease); }
.vs-ph.on { opacity: 1; transform: none; }
.vs-who { display: grid; gap: 4px; min-width: 0; }
.vs-who b { font: 800 clamp(20px, 2.6vw, 30px)/1.05 var(--ar-h, var(--m-display)); letter-spacing: .03em; color: var(--cur, var(--ar-fg)); overflow-wrap: anywhere; }
.vs-who small { color: var(--ar-mut); font-size: 12.5px; line-height: 1.45; }
.vs-mid { display: grid; justify-items: center; gap: 6px; text-align: center; }
.vs-vs { font: 900 clamp(26px, 3vw, 38px)/1 var(--ar-h, var(--m-display)); font-style: italic; letter-spacing: .06em;
  background: linear-gradient(180deg, #FFF6C8, var(--ar-gold) 60%, #C98A00); -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 0 14px rgba(255, 210, 63, .35)); }
.vs-score { display: flex; align-items: baseline; gap: 8px; font: 800 clamp(30px, 3.6vw, 44px)/1 var(--ar-h, var(--m-display)); font-variant-numeric: tabular-nums; }
.vs-score b:first-child { color: var(--ar-lime); } .vs-score b:last-child { color: var(--ar-cyan); }
.vs-score i { font-style: normal; color: rgba(255, 255, 255, .25); }
.vs-mid small { color: var(--ar-mut); font-size: 12px; max-width: 22ch; }
.vs-swap { display: inline-flex; align-items: center; gap: 6px; margin-top: 4px; padding: 7px 12px; border-radius: 10px; cursor: pointer; font: 700 11px/1 var(--ar-h, var(--m-display)); letter-spacing: .14em; text-transform: uppercase;
  color: var(--ar-fg); background: rgba(255, 255, 255, .03); border: 1px solid var(--ar-line); transition: border-color .2s ease, color .2s ease; }
.vs-swap svg { width: 15px; height: 15px; }
.vs-swap:hover { color: var(--ar-gold); border-color: rgba(255, 210, 63, .5); }

.vs-boxes { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.vs-box { padding: 16px; border-radius: 18px; background: rgba(5, 8, 13, .45); border: 1px solid rgba(255, 255, 255, .06); min-width: 0; }
.vs-box h3 { margin: 0 0 10px; font: 700 11px/1 var(--ar-h, var(--m-display)); letter-spacing: .18em; text-transform: uppercase; color: var(--ar-gold); }
.vs-big { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.vs-big b { font: 800 30px/1 var(--ar-h, var(--m-display)); font-variant-numeric: tabular-nums; }
.vs-big span { color: var(--ar-mut); font-size: 13px; }
.vs-line { margin: 8px 0 0; color: var(--ar-mut); font-size: 13px; line-height: 1.5; }
.vs-line b { color: var(--ar-fg); }
.vs-meets { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; }
.vs-m { display: grid; justify-items: center; gap: 3px; padding: 6px 8px; min-width: 56px; border-radius: 10px; font-size: 11px; color: var(--ar-mut); background: rgba(255, 255, 255, .03); border: 1px solid var(--ar-line); }
.vs-m b { font: 700 13px/1 var(--ar-h, var(--m-display)); }
.vs-m.w { border-color: rgba(198, 255, 0, .45); } .vs-m.w b { color: var(--ar-lime); }
.vs-m.l { border-color: rgba(0, 217, 255, .4); } .vs-m.l b { color: var(--ar-cyan); }

.vs-bars { display: grid; gap: 10px; width: 100%; max-width: 900px; margin: 0 auto; }
.vs-row { display: grid; grid-template-columns: minmax(70px, 1fr) minmax(0, 2.4fr) minmax(70px, 1fr); align-items: center; gap: 12px; }
.vs-row > b { font: 800 16px/1 var(--ar-h, var(--m-display)); font-variant-numeric: tabular-nums; color: var(--ar-mut); }
.vs-row > b:last-child { text-align: right; }
.vs-row > b.win:first-child { color: var(--ar-lime); } .vs-row > b.win:last-child { color: var(--ar-cyan); }
.vs-rm { display: grid; gap: 6px; }
.vs-rm small { text-align: center; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--ar-mut); font-weight: 700; }
.vs-tug { position: relative; display: flex; height: 8px; border-radius: 6px; overflow: hidden; background: rgba(255, 255, 255, .05); }
.vs-tug i { display: block; height: 100%; transition: width .6s var(--ar-ease); }
.vs-tug i.a { background: linear-gradient(90deg, rgba(198, 255, 0, .35), var(--ar-lime)); }
.vs-tug i.b { background: linear-gradient(90deg, var(--ar-cyan), rgba(0, 217, 255, .35)); }
.vs-tug::after { content: ""; position: absolute; left: 50%; top: -2px; bottom: -2px; width: 2px; margin-left: -1px; background: rgba(8, 11, 18, .9); }

/* ---------------- predictor ---------------- */
.pr-hd { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.pr-hd h3 { margin: 0; font: 800 20px/1.1 var(--ar-h, var(--m-display)); letter-spacing: .04em; }
.pr-hd p { margin: 4px 0 0; color: var(--ar-mut); font-size: 13px; }
.pr-mode { display: inline-flex; padding: 4px; border-radius: 12px; background: rgba(5, 8, 13, .55); border: 1px solid var(--ar-line); }
.pr-mode button { padding: 8px 14px; border: 0; border-radius: 9px; cursor: pointer; font: 700 12px/1 var(--m-body); color: var(--ar-mut); background: none; }
.pr-mode button[aria-pressed="true"] { color: #0A0E14; background: var(--ar-cyan); box-shadow: 0 0 16px rgba(0, 217, 255, .4); }
.pr-chip.in { opacity: .45; }
.pr-chip .pr-tag { position: absolute; top: -6px; right: -4px; padding: 2px 5px; border-radius: 6px; font: 800 9px/1 var(--ar-h, var(--m-display)); font-style: normal; color: #0A0E14; display: none; }
.pr-chip.in-a .pr-tag { display: block; background: var(--ar-lime); } .pr-chip.in-a .pr-tag::before { content: "A"; }
.pr-chip.in-b .pr-tag { display: block; background: var(--ar-cyan); } .pr-chip.in-b .pr-tag::before { content: "B"; }
.pr-court { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr) minmax(0, 1fr); gap: 16px; align-items: stretch; }
.pr-team { padding: 14px; border-radius: 18px; background: rgba(5, 8, 13, .45); border: 1px solid rgba(198, 255, 0, .25); }
.pr-team.b { border-color: rgba(0, 217, 255, .25); }
.pr-team.a small { color: var(--ar-lime); } .pr-team.b small { color: var(--ar-cyan); }
.pr-slots { display: grid; gap: 8px; }
.pr-slot { display: flex; align-items: center; gap: 10px; min-height: 52px; padding: 8px 10px; border-radius: 14px; cursor: pointer; text-align: left; color: var(--ar-fg); font: 700 15px var(--m-body);
  background: rgba(255, 255, 255, .02); border: 1.5px dashed rgba(137, 147, 164, .35); transition: border-color .2s ease, background-color .2s ease; }
.pr-slot { min-width: 0; }
.pr-slot > span:not(.pr-slot-e) { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pr-slot .pr-slot-e { color: var(--ar-mut); font-weight: 500; font-size: 13px; }
.pr-slot.full { border-style: solid; border-color: color-mix(in srgb, var(--pc) 70%, transparent); background: color-mix(in srgb, var(--pc) 12%, transparent); }
.pr-slot .vs-av { width: 34px; height: 34px; }
.pr-slot small { margin-left: auto; color: var(--ar-mut); font-size: 12px; font-weight: 600; }
.pr-res { display: grid; align-content: center; justify-items: center; gap: 10px; padding: 14px; border-radius: 18px; text-align: center;
  background: radial-gradient(90% 90% at 50% 0%, rgba(255, 210, 63, .1), transparent 70%), rgba(5, 8, 13, .45); border: 1px solid rgba(255, 210, 63, .22); }
.pr-hint { color: var(--ar-mut); font-size: 13px; }
.pr-sc { font: 900 clamp(32px, 4vw, 48px)/1 var(--ar-h, var(--m-display)); font-variant-numeric: tabular-nums; }
.pr-sc .a { color: var(--ar-lime); } .pr-sc .b { color: var(--ar-cyan); } .pr-sc i { font-style: normal; color: rgba(255, 255, 255, .25); margin: 0 6px; }
.pr-verdict { font: 700 11.5px/1.2 var(--ar-h, var(--m-display)); letter-spacing: .16em; text-transform: uppercase; color: var(--ar-gold); }
.pr-prob { width: 100%; display: grid; gap: 6px; }
.pr-prob .vs-tug { height: 12px; border-radius: 8px; }
.pr-prob div:last-child { display: flex; justify-content: space-between; font: 700 13px/1 var(--ar-h, var(--m-display)); }
.pr-prob .pa { color: var(--ar-lime); } .pr-prob .pb { color: var(--ar-cyan); }
.pr-res small { color: var(--ar-mut); font-size: 12px; }
.pr-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.pr-actions .ar-cta { margin: 0; }
.pr-splits { display: grid; gap: 8px; }
.pr-splits:empty { display: none; }
.pr-splits > small { font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .18em; text-transform: uppercase; color: var(--ar-mut); }
.pr-split { display: grid; grid-template-columns: minmax(0, 1fr) auto auto; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 14px; cursor: pointer; text-align: left;
  color: var(--ar-fg); font: 600 13.5px var(--m-body); background: rgba(255, 255, 255, .02); border: 1px solid var(--ar-line); transition: border-color .2s ease; }
.pr-split:hover { border-color: rgba(255, 210, 63, .45); }
.pr-split.cur { border-color: rgba(0, 217, 255, .55); background: rgba(0, 217, 255, .06); }
.pr-split em { font-style: normal; color: var(--ar-mut); font-size: 12.5px; white-space: nowrap; }
.pr-split .tag { padding: 3px 8px; border-radius: 999px; font: 800 10px/1 var(--ar-h, var(--m-display)); letter-spacing: .1em; text-transform: uppercase; color: #241A00; background: var(--ar-gold); white-space: nowrap; }
.pr-split .tag.no { visibility: hidden; }
.pr-note { margin: 0; color: var(--ar-mut); font-size: 12px; line-height: 1.55; }

@media (max-width: 860px) {
  .vs-picks, .vs-boxes { grid-template-columns: minmax(0, 1fr); }
  .vs-chips, .pr-pool { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 4px; scrollbar-width: none; }
  .vs-chips::-webkit-scrollbar, .pr-pool::-webkit-scrollbar { display: none; }
  .vs-chip, .pr-chip { flex: none; }
  .vs-stage { grid-template-columns: 1fr auto 1fr; gap: 8px; }
  .vs-side, .vs-side.b { flex-direction: column; text-align: center; gap: 8px; }
  .vs-frame { width: 92px; }
  .vs-who b { font-size: 17px; }
  .vs-who small { font-size: 11px; }
  .vs-row { grid-template-columns: 58px minmax(0, 1fr) 58px; gap: 8px; }
  .vs-row > b { font-size: 14px; }
  .pr-court { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10px; }
  .pr-team { padding: 10px; }
  .pr-slot { gap: 7px; min-height: 46px; padding: 6px 8px; font-size: 13.5px; }
  .pr-slot .vs-av { width: 28px; height: 28px; }
  .pr-slot small { display: none; }
  .pr-actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
  .pr-actions .ar-cta { width: auto; min-width: 0; padding: 12px 4px; font-size: 10px; letter-spacing: .04em; white-space: nowrap; }
  .pr-res { grid-column: 1 / -1; grid-row: 2; }
  .pr-split { grid-template-columns: minmax(0, 1fr) auto; }
  .pr-split .tag { grid-column: 1 / -1; justify-self: start; }
  .pr-split .tag.no { display: none; }
  .vs-card, .pr-card { padding: 14px; }
}
"""

VERSUS_JS = r"""
(() => {
const root = document.getElementById('versus'); const raw = document.getElementById('vs-data');
if (!root || !raw) return;
const D = JSON.parse(raw.textContent); const PLR = D.players;
const $ = (s, el = root) => el.querySelector(s); const $$ = (s, el = root) => [...el.querySelectorAll(s)];
const K = (k) => $(`[data-k="${k}"]`);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const sg = (v, d = 2) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(d);
const pct = (v) => Math.round(v * 100) + '%';
const avSrc = (p) => document.querySelector(`img[data-ph-avatar="${CSS.escape(p)}"][src]`)?.src || '';
const av = (p) => `<img class="vs-av" src="${avSrc(p)}" alt="" style="--pc:${PLR[p].col}">`;

/* ---------------- compare ---------------- */
let A = D.order[0], B = D.order[1];
const ROWS = [
  ['Win rate', (p) => p.win, (v) => pct(v), .3],
  ['Points per match', (p) => p.dpm, (v) => sg(v), 6],
  ['Adjusted strength', (p) => p.adj, (v) => sg(v), 6],
  ['Current form', (p) => p.radj, (v) => sg(v), 6],
  ['Last 20, per match', (p) => p.r20d, (v) => sg(v), 6],
  ['Elo', (p) => p.elo, (v) => String(v), 700],
  ['Titles', (p) => p.titles, (v) => String(v), 12],
  ['Finals won', (p) => (p.fw + p.fl ? p.fw / (p.fw + p.fl) : 0), (v) => pct(v), .6],
  ['Under pressure', (p) => p.clutch, (v) => sg(v, 1), 10],
];
function draw() {
  const a = PLR[A], b = PLR[B];
  $$('.vs-chip').forEach((c) => {
    const mine = c.dataset.side === 'a' ? A : B, other = c.dataset.side === 'a' ? B : A;
    c.setAttribute('aria-pressed', String(c.dataset.p === mine)); c.disabled = c.dataset.p === other;
  });
  $$('.vs-side.a .vs-ph').forEach((i) => i.classList.toggle('on', i.dataset.p === A));
  $$('.vs-side.b .vs-ph').forEach((i) => i.classList.toggle('on', i.dataset.p === B));
  $('.vs-side.a').style.setProperty('--cur', a.col); $('.vs-side.b').style.setProperty('--cur', b.col);
  K('a-name').textContent = A; K('b-name').textContent = B;
  K('a-sub').textContent = `#${a.rank} · ${a.rec} · ${a.titles} titles`; K('b-sub').textContent = `#${b.rank} · ${b.rec} · ${b.titles} titles`;
  const v = D.vs[`${A}|${B}`];
  K('a-w').textContent = v.W; K('b-w').textContent = v.L;
  K('h2h-sub').textContent = v.P ? `${v.P} meetings on opposite sides` : 'Never on opposite sides';
  // against each other
  if (v.P) {
    const exp = v.expW, d = v.W - exp;
    const meets = v.last.slice().reverse().map((m) => `<span class="vs-m ${m[4] > m[5] ? 'w' : 'l'}" title="${esc(m[2])} ${m[4]}–${m[5]} ${esc(m[3])} · ${esc(m[1])}"><b>${m[4]}–${m[5]}</b>${esc(m[0])}</span>`).join('');
    K('against').innerHTML = `<div class="vs-big"><b>${v.W}–${v.L}</b><span>${esc(A)}’s record against ${esc(B)} · ${pct(v.W / v.P)}</span></div>`
      + `<p class="vs-line">${esc(A)} averages <b>${sg(v.dpm)}</b> points a match in these meetings. Team strength predicted <b>${exp.toFixed(1)}</b> wins for ${esc(A)}; `
      + (Math.abs(d) < 1.5 ? 'the record is about what strength predicts.' : `that is <b>${sg(d, 1)}</b> ${d > 0 ? 'above' : 'below'} what strength predicts.`) + '</p>'
      + `<div class="vs-meets" aria-label="Last meetings, newest first">${meets}</div>`;
  } else K('against').innerHTML = '<p class="vs-line">These two have never played on opposite sides.</p>';
  // as partners
  if (v.tP) {
    K('together').innerHTML = `<div class="vs-big"><b>${v.tW}–${v.tL}</b><span>together · ${v.tP} matches · ${pct(v.tW / v.tP)}</span></div>`
      + `<p class="vs-line">As a pair they average <b>${sg(v.tdpm)}</b> points a match, <b>${sg(v.tvs)}</b> against what their separate levels predict`
      + (Math.abs(v.tvs) < 1 ? ' — no special chemistry either way.' : (v.tvs > 0 ? ' — they do better together than expected.' : ' — they do worse together than expected.')) + '</p>';
  } else K('together').innerHTML = '<p class="vs-line">The draw has never put these two on the same side.</p>';
  // stat bars
  K('bars').innerHTML = ROWS.map(([lab, f, fmt, sc]) => {
    const x = f(a), y = f(b); const share = Math.max(6, Math.min(94, 50 + (x - y) / sc * 50));
    return `<div class="vs-row"><b class="${x > y ? 'win' : ''}">${fmt(x)}</b><div class="vs-rm"><small>${lab}</small><div class="vs-tug"><i class="a" style="width:${share}%"></i><i class="b" style="width:${100 - share}%"></i></div></div><b class="${y > x ? 'win' : ''}">${fmt(y)}</b></div>`;
  }).join('');
}
root.addEventListener('click', (e) => {
  const c = e.target.closest('.vs-chip');
  if (c && !c.disabled) { if (c.dataset.side === 'a') A = c.dataset.p; else B = c.dataset.p; draw(); return; }
  if (e.target.closest('.vs-swap')) { [A, B] = [B, A]; draw(); }
});

/* ---------------- predictor ---------------- */
let mode = 'adj';
let S = { a0: null, a1: null, b0: null, b1: null };
if (D.start) { S = { a0: D.start.a[0], a1: D.start.a[1], b0: D.start.b[0], b1: D.start.b[1] }; }
const erf = (x) => { const t = 1 / (1 + .3275911 * Math.abs(x)); const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - .284496736) * t + .254829592) * t * Math.exp(-x * x); return x >= 0 ? y : -y; };
const phi = (z) => .5 * (1 + erf(z / Math.SQRT2));
const val = (p) => PLR[p][mode];
const margin = (ta, tb) => val(ta[0]) + val(ta[1]) - val(tb[0]) - val(tb[1]);
const score = (m) => { const l = Math.max(0, Math.round(21 - Math.abs(m))); return Math.abs(m) < .5 ? [21, 20] : (m > 0 ? [21, Math.min(l, 19)] : [Math.min(l, 19), 21]); };
const verdict = (pa) => { const x = Math.max(pa, 1 - pa); return x < .58 ? 'Coin flip' : x < .7 ? 'Slight favourite' : x < .85 ? 'Clear favourite' : 'Heavy favourite'; };
function teams() { return [[S.a0, S.a1], [S.b0, S.b1]]; }
function full() { return Object.values(S).every(Boolean); }
function splits(four) {
  const [p, q, r, s] = four;
  return [[[p, q], [r, s]], [[p, r], [q, s]], [[p, s], [q, r]]].map(([x, y]) => ({ x, y, m: margin(x, y) }));
}
function drawPr() {
  const used = Object.entries(S).filter(([, p]) => p);
  $$('.pr-chip').forEach((c) => {
    const at = used.find(([, p]) => p === c.dataset.p);
    c.classList.toggle('in', !!at); c.classList.toggle('in-a', !!at && at[0][0] === 'a'); c.classList.toggle('in-b', !!at && at[0][0] === 'b');
  });
  $$('.pr-slot').forEach((s) => {
    const p = S[s.dataset.slot];
    s.classList.toggle('full', !!p);
    if (p) { s.style.setProperty('--pc', PLR[p].col); s.innerHTML = `${av(p)}<span>${esc(p)}</span><small>${sg(val(p))}</small>`; }
    else { s.style.removeProperty('--pc'); s.innerHTML = '<span class="pr-slot-e">Player</span>'; }
  });
  const res = K('res'), sp = K('splits');
  if (!full()) { res.innerHTML = `<span class="pr-hint">Pick ${4 - used.length} more player${4 - used.length === 1 ? '' : 's'}</span>`; sp.innerHTML = ''; return; }
  const [ta, tb] = teams(); const m = margin(ta, tb); const pa = phi(m / D.sigma); const [sa, sb] = score(m);
  res.innerHTML = `<span class="pr-verdict">${verdict(pa)}</span><div class="pr-sc"><span class="a">${sa}</span><i>–</i><span class="b">${sb}</span></div>`
    + `<div class="pr-prob"><div class="vs-tug"><i class="a" style="width:${(pa * 100).toFixed(1)}%"></i><i class="b" style="width:${((1 - pa) * 100).toFixed(1)}%"></i></div>`
    + `<div><span class="pa">A ${pct(pa)}</span><span class="pb">${pct(1 - pa)} B</span></div></div>`
    + `<small>Expected margin ${sg(m, 1)} for Team A</small>`;
  const all = splits([S.a0, S.a1, S.b0, S.b1]); const best = Math.min(...all.map((o) => Math.abs(o.m))) + .05;   // ties within 0.05 a game count as equally balanced
  const key = (t) => t.slice().sort().join('+');
  const cur = key(ta);
  sp.innerHTML = '<small>All three ways to split these four</small>' + all.map((o) => {
    const isCur = key(o.x) === cur || key(o.y) === cur; const p1 = phi(o.m / D.sigma);
    return `<button type="button" class="pr-split${isCur ? ' cur' : ''}" data-x="${esc(o.x.join('|'))}" data-y="${esc(o.y.join('|'))}"><span>${esc(o.x.join(' + '))} <em>vs</em> ${esc(o.y.join(' + '))}</span>`
      + `<em>${sg(o.m, 1)} · ${pct(Math.max(p1, 1 - p1))} for ${o.m >= 0 ? 'the first pair' : 'the second pair'}</em><span class="tag${Math.abs(o.m) <= best ? '' : ' no'}">Most balanced</span></button>`;
  }).join('');
}
root.addEventListener('click', (e) => {
  const c = e.target.closest('.pr-chip');
  if (c) {
    const p = c.dataset.p; const at = Object.keys(S).find((k) => S[k] === p);
    if (at) S[at] = null; else { const k = ['a0', 'a1', 'b0', 'b1'].find((k) => !S[k]); if (k) S[k] = p; }
    drawPr(); return;
  }
  const s = e.target.closest('.pr-slot'); if (s) { S[s.dataset.slot] = null; drawPr(); return; }
  const md = e.target.closest('.pr-mode button');
  if (md) { mode = md.dataset.mode; $$('.pr-mode button').forEach((b) => b.setAttribute('aria-pressed', String(b === md))); drawPr(); return; }
  const sp = e.target.closest('.pr-split');
  if (sp) { const x = sp.dataset.x.split('|'), y = sp.dataset.y.split('|'); S = { a0: x[0], a1: x[1], b0: y[0], b1: y[1] }; drawPr(); return; }
  const act = e.target.closest('[data-act]'); if (!act) return;
  if (act.dataset.act === 'clear') S = { a0: null, a1: null, b0: null, b1: null };
  if (act.dataset.act === 'random') { const pool = D.order.slice().sort(() => Math.random() - .5).slice(0, 4); S = { a0: pool[0], a1: pool[1], b0: pool[2], b1: pool[3] }; }
  if (act.dataset.act === 'balance') {
    const four = Object.values(S).filter(Boolean);
    if (four.length < 4) { for (const p of D.order) { if (four.length >= 4) break; if (!four.includes(p)) four.push(p); } }
    const b = splits(four).sort((u, v) => Math.abs(u.m) - Math.abs(v.m))[0];
    S = { a0: b.x[0], a1: b.x[1], b0: b.y[0], b1: b.y[1] };
  }
  drawPr();
});

const go = () => { draw(); drawPr(); };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
// avatars are filled by the photo script; redraw once they have sources
setTimeout(() => drawPr(), 400);
})();
"""
