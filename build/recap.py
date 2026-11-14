"""Latest-session recap for the Arena overview.

Built only from tables.json (matches and the per-player daily rows), so it rewrites itself
whenever a new day is added: champions, the day table with Elo and rating moves, the day's
highlights (biggest win, closest game, upset, MVP) and every match of the day.
"""
from html import escape

MINUS = '−'


def _sg(x, d=0):
    return f'{x:+.{d}f}'.replace('-', MINUS)


def _day_title(d):
    # 'W8 D2' -> 'Week 8, Day 2'
    try:
        w, k = d.split()
        return f'Week {int(w[1:])}, Day {int(k[1:])}'
    except Exception:
        return d


def _team(s):
    return s.split(' + ')


def recap_html(T, P, slug, col, icon):
    M = T['matches']
    last = M[-1]['day']
    DM = [m for m in M if m['day'] == last]
    D = [r for r in T['daily'] if r['day'] == last and r['played']]
    li = D[0]['day_index'] if D else 0
    prev = {r['player']: r for r in T['daily'] if r['day_index'] == li - 1}
    hist = {}
    for r in sorted(T['daily'], key=lambda r: r['day_index']):
        if r['day_index'] < li and r['wb_rating'] is not None and r['played']:
            hist[r['player']] = r['wb_rating']
    D.sort(key=lambda r: (r['seed'] or 99))

    fin = next((m for m in DM if m['stage'] == 'Final'), None)
    champs = _team(fin['winner']) if fin else []
    runners = (_team(fin['team_b']) if fin['winner'] == fin['team_a'] else _team(fin['team_a'])) if fin else []
    fscore = (f'{max(fin["score_a"], fin["score_b"])}–{min(fin["score_a"], fin["score_b"])}') if fin else ''
    seed1 = D[0]['player'] if D else None
    mvp = max(D, key=lambda r: (r['adj'], r['diff'], r['W'])) if D else None
    best = max(D, key=lambda r: (r['W'] - r['L'], r['diff'])) if D else None
    big = max(DM, key=lambda m: (m['margin'], -DM.index(m)))
    close = min(DM, key=lambda m: (m['margin'], -max(m['score_a'], m['score_b'])))
    ups = []
    for m in DM:
        if m.get('pred_margin') is None:
            continue
        u = -m['pred_margin'] if m['winner'] == m['team_a'] else m['pred_margin']
        ups.append((u, m))
    upset = max(ups, key=lambda x: x[0]) if ups else None
    pts = sum(m['score_a'] + m['score_b'] for m in DM)
    deuce = sum(max(m['score_a'], m['score_b']) > 21 for m in DM)
    avg = sum(m['margin'] for m in DM) / len(DM)
    nq = sum(m['stage'] == 'Qualifier' for m in DM); nk = len(DM) - nq

    def wscore(m):
        a, b = m['score_a'], m['score_b']
        return (f'{a}–{b}', m['team_a'], m['team_b']) if m['winner'] == m['team_a'] else (f'{b}–{a}', m['team_b'], m['team_a'])

    def av(p, cls='rc-av'):
        return f'<img class="{cls}" data-ph-avatar="{escape(p)}" alt="" style="--pc:{col(p)}">'

    # ---------------- story line
    story = []
    if fin:
        story.append(f'<b>{escape(" + ".join(champs))}</b> won {escape(last)}, beating {escape(" + ".join(runners))} {fscore} in the final.')
    if seed1:
        r0 = D[0]
        story.append(f'{escape(seed1)} topped the qualifier and went in as seed 1.')
    if mvp:
        story.append(f'Best adjusted day: <b>{escape(mvp["player"])}</b> ({_sg(mvp["adj"], 2)} per match once partners and opponents are taken out, {mvp["W"]}–{mvp["L"]})'
                     + (f'; best record: <b>{escape(best["player"])}</b> ({best["W"]}–{best["L"]}, {_sg(best["diff"])}).' if best and best['player'] != mvp['player'] else '.'))
    s, w, l = wscore(big)
    story.append(f'Biggest win: {escape(w)} {s} over {escape(l)}.')

    # ---------------- champions card
    champ_html = ''
    if fin:
        champ_html = (f'<div class="rc-champ ar-reveal" style="--pc:{col(champs[0])}">'
                      f'<span class="rc-champ-k">{icon("crown")}Champions · {escape(last)}</span>'
                      f'<span class="rc-champ-av">{"".join(av(p, "rc-av lg") for p in champs)}</span>'
                      f'<span class="rc-champ-n">{escape(" + ".join(champs))}</span>'
                      f'<span class="rc-champ-s"><b>{fscore}</b> in the final against {escape(" + ".join(runners))}</span>'
                      + (f'<span class="rc-mvp">{av(mvp["player"])}<span><small>Top adjusted</small><b>{escape(mvp["player"])}</b>'
                         f'<em>{_sg(mvp["adj"], 2)} adjusted · {mvp["W"]}–{mvp["L"]} · {_sg(mvp["diff"])}</em></span></span>' if mvp else '')
                      + (f'<span class="rc-mvp alt">{av(best["player"])}<span><small>Best record</small><b>{escape(best["player"])}</b>'
                         f'<em>{best["W"]}–{best["L"]} · {_sg(best["diff"])} · {_sg(best["adj"], 2)} adjusted</em></span></span>' if best and mvp and best['player'] != mvp['player'] else '')
                      + '</div>')

    # ---------------- day table
    rows = []
    for r in D:
        p = r['player']
        de = r['elo'] - prev[p]['elo'] if p in prev else 0
        r0 = hist.get(p); r1 = r['wb_rating']
        mv = '' if r0 is None or r1 is None or r0 == r1 else (f'<i class="up">▲{r1 - r0}</i>' if r1 > r0 else f'<i class="dn">▼{r0 - r1}</i>')
        res = ('<span class="rc-res t">Champion</span>' if r['title'] else
               ('<span class="rc-res f">Final</span>' if r['final'] else '<span class="rc-res o">Out</span>'))
        rows.append(f'<tr style="--pc:{col(p)}"><td class="rc-seed">{r["seed"] or "–"}</td>'
                    f'<td class="rc-pl"><button type="button" data-goto-player="{slug[p]}">{av(p)}<span>{escape(p)}</span></button></td>'
                    f'<td>{r["W"]}–{r["L"]}</td><td class="{"pos" if r["diff"] > 0 else ("neg" if r["diff"] < 0 else "")}">{_sg(r["diff"]) if r["diff"] else "0"}</td>'
                    f'<td class="rc-h1">{_sg(r["adj"], 2)}</td>'
                    f'<td class="{"pos" if de > 0 else ("neg" if de < 0 else "")}">{_sg(de) if round(de) else "0"}</td>'
                    f'<td class="rc-h2">{r1 if r1 is not None else "–"}{mv}</td><td>{res}</td></tr>')
    absent = [p for p in P if p not in {r['player'] for r in D}]
    table_html = (f'<div class="rc-table ar-reveal"><div class="rc-cap"><h3>Day table</h3><span>Seeded by qualifier · all {len(DM)} matches counted</span></div>'
                  f'<div class="rc-scroll"><table class="rc-t"><thead><tr><th>Seed</th><th>Player</th><th>W–L</th><th>Diff</th><th class="rc-h1">Adjusted</th>'
                  f'<th title="Change in margin-weighted Elo over the day">Elo ±</th><th class="rc-h2" title="1–5 rating used for the draw, with the change from the player’s previous day">Rating</th><th>Result</th></tr></thead>'
                  f'<tbody>{"".join(rows)}</tbody></table></div>'
                  + (f'<p class="rc-foot">Did not play: {escape(", ".join(absent))}.</p>' if absent else '')
                  + '</div>')

    # ---------------- highlight tiles
    def tile(k, lab, val, sub, accent='lime'):
        return (f'<div class="rc-hl-i ar-reveal rc-{accent}"><span class="rc-hl-ic">{icon(k)}</span><small>{lab}</small>'
                f'<b>{val}</b><span>{sub}</span></div>')
    s1, w1, l1 = wscore(big); s2, w2, l2 = wscore(close)
    tiles = [tile('fire', 'Biggest win', s1, f'{escape(w1)} over {escape(l1)} · {escape(big["label"])}'),
             tile('bolt', 'Closest game', s2, f'{escape(w2)} over {escape(l2)} · {escape(close["label"])}' + (' · past 21' if max(close['score_a'], close['score_b']) > 21 else ''), 'cyan')]
    if upset and upset[0] >= 1.5:
        s3, w3, l3 = wscore(upset[1])
        tiles.append(tile('trend', 'Upset of the day', s3, f'{escape(w3)} beat {escape(l3)}, predicted to lose by {upset[0]:.1f}'))
    else:
        tiles.append(tile('trend', 'Upsets', 'None', 'Every winner was the predicted side or within 1.5 points'))
    tiles.append(tile('shuttle', 'Day in numbers', f'{len(DM)} matches', f'{nq} qualifier · {nk} knockout · {pts:,} points · avg margin {avg:.1f}'
                      + (f' · {deuce} past 21' if deuce else ''), 'cyan'))

    # ---------------- every match of the day
    ml = []
    for m in DM:
        s, w, l = wscore(m)
        stage = 'q' if m['stage'] == 'Qualifier' else ('f' if m['stage'] == 'Final' else 'e')
        ml.append(f'<li class="rc-m s-{stage}"><span class="rc-m-l">{escape(m["label"])}</span>'
                  f'<span class="rc-m-w">{escape(w)}</span><span class="rc-m-s">{s}</span><span class="rc-m-x">{escape(l)}</span></li>')
    matches_html = (f'<div class="rc-matches ar-reveal"><div class="rc-cap"><h3>Every match</h3><span>Winners first</span></div>'
                    f'<ol class="rc-ml">{"".join(ml)}</ol></div>')

    return (f'<section class="ar-block rc" id="latest"><div class="ar-head"><p class="ar-eyebrow">Match day report · {_day_title(last)}</p>'
            f'<h2 class="ar-h">Latest session</h2></div>'
            f'<p class="ar-story rc-story">{" ".join(story)}</p>'
            f'<div class="rc-grid">{champ_html}{table_html}</div>'
            f'<div class="rc-hl">{"".join(tiles)}</div>{matches_html}</section>')


RECAP_CSS = r"""
/* ---------------- latest-session recap ---------------- */
.rc .ar-story { margin-bottom: 18px; }
.rc-grid { display: grid; grid-template-columns: minmax(0, 360px) minmax(0, 1fr); gap: 16px; align-items: stretch; }
.rc-champ, .rc-table, .rc-hl-i, .rc-matches { border-radius: 22px; background: var(--ar-glass); border: 1px solid var(--ar-line); box-shadow: var(--ar-shadow);
  -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px); color: var(--ar-fg); }
.rc-champ { position: relative; overflow: hidden; display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px; padding: 24px 20px 18px;
  background: radial-gradient(120% 70% at 50% 0%, rgba(255, 210, 63, .18), transparent 60%), var(--ar-glass); border-color: rgba(255, 210, 63, .35); }
.rc-champ::before { content: ""; position: absolute; inset: -40% -20% auto; height: 70%; background: conic-gradient(from 180deg, transparent, rgba(255, 210, 63, .18), transparent 30%); filter: blur(20px); pointer-events: none; }
.rc-champ-k { display: inline-flex; align-items: center; gap: 6px; font: 700 11px/1 var(--ar-h, var(--m-display)); letter-spacing: .2em; text-transform: uppercase; color: var(--ar-gold); }
.rc-champ-k .ar-ic { width: 16px; height: 16px; }
.rc-champ-av { display: flex; justify-content: center; margin: 4px 0 2px; }
.rc-av { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 2px solid var(--pc, var(--ar-line2)); background: #0D121B; flex: none; }
.rc-av.lg { width: 92px; height: 92px; border-width: 3px; box-shadow: 0 0 0 4px rgba(8, 11, 18, .9), 0 0 30px color-mix(in srgb, var(--pc) 60%, transparent); }
.rc-av.lg + .rc-av.lg { margin-left: -18px; }
.rc-champ-n { font: 800 clamp(20px, 2.4vw, 26px)/1.1 var(--ar-h, var(--m-display)); letter-spacing: .02em; }
.rc-champ-s { color: var(--ar-mut); font-size: 13.5px; }
.rc-champ-s b { color: var(--ar-gold); font-family: var(--ar-h, var(--m-display)); font-size: 18px; margin-right: 4px; text-shadow: 0 0 16px rgba(255, 210, 63, .5); }
.rc-mvp { margin-top: auto; width: 100%; display: flex; align-items: center; gap: 12px; text-align: left; padding: 12px 14px; border-radius: 16px; background: rgba(198, 255, 0, .07); border: 1px solid rgba(198, 255, 0, .22); }
.rc-mvp > span { display: grid; gap: 1px; }
.rc-mvp small { font-size: 10.5px; letter-spacing: .16em; text-transform: uppercase; color: var(--ar-lime); font-weight: 700; }
.rc-mvp b { font-size: 15px; }
.rc-mvp + .rc-mvp { margin-top: 0; }
.rc-mvp.alt { background: rgba(0, 217, 255, .06); border-color: rgba(0, 217, 255, .22); }
.rc-mvp.alt small { color: var(--ar-cyan); }
.rc-mvp em { font-style: normal; color: var(--ar-mut); font-size: 12.5px; }
.rc-table, .rc-matches { padding: 18px 18px 14px; min-width: 0; }
.rc-cap { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.rc-cap h3 { margin: 0; font: 700 16px var(--ar-h, var(--m-display)); letter-spacing: .04em; }
.rc-cap span { color: var(--ar-mut); font-size: 12px; }
.rc-scroll { overflow-x: auto; }
.rc-t { width: 100%; border-collapse: collapse; font-size: 13.5px; font-variant-numeric: tabular-nums; }
.rc-t th { text-align: left; font-size: 10.5px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--ar-mut); padding: 6px 8px; border-bottom: 1px solid var(--ar-line2); white-space: nowrap; }
.rc-t td { padding: 7px 8px; border-bottom: 1px solid var(--ar-line); white-space: nowrap; }
.rc-t tr:last-child td { border-bottom: 0; }
.rc-t tbody tr { transition: background .2s ease; }
.rc-t tbody tr:hover { background: color-mix(in srgb, var(--pc) 9%, transparent); }
.rc-t .pos { color: var(--ar-lime); } .rc-t .neg { color: var(--ar-red); }
.rc-seed { font: 800 15px var(--ar-h, var(--m-display)); color: var(--ar-mut); width: 1%; }
.rc-t tbody tr:first-child .rc-seed { color: var(--ar-lime); text-shadow: 0 0 12px rgba(198, 255, 0, .6); }
.rc-pl button { display: inline-flex; align-items: center; gap: 9px; padding: 0; border: 0; background: none; color: var(--ar-fg); font: 600 14px var(--m-body); cursor: pointer; }
.rc-pl button:hover span { color: var(--pc); }
.rc-t i { font-style: normal; font-size: 11px; margin-left: 5px; font-weight: 700; }
.rc-t i.up { color: var(--ar-lime); } .rc-t i.dn { color: var(--ar-red); }
.rc-res { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 10.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; border: 1px solid var(--ar-line2); color: var(--ar-mut); }
.rc-res.t { color: #0B0F17; background: var(--ar-gold); border-color: var(--ar-gold); box-shadow: 0 0 14px rgba(255, 210, 63, .5); }
.rc-res.f { color: var(--ar-cyan); border-color: rgba(0, 217, 255, .45); }
.rc-foot { margin: 10px 0 0; color: var(--ar-mut); font-size: 12px; }
.rc-hl { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
.rc-hl-i { position: relative; overflow: hidden; display: grid; gap: 4px; padding: 16px 18px; }
.rc-hl-i small { font-size: 10.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--ar-mut); }
.rc-hl-i b { font: 800 26px/1.1 var(--ar-h, var(--m-display)); color: var(--ar-lime); text-shadow: 0 0 18px rgba(198, 255, 0, .35); }
.rc-hl-i.rc-cyan b { color: var(--ar-cyan); text-shadow: 0 0 18px rgba(0, 217, 255, .35); }
.rc-hl-i > span:last-child { color: var(--ar-mut); font-size: 12.5px; line-height: 1.4; }
.rc-hl-ic { position: absolute; right: 14px; top: 14px; opacity: .35; }
.rc-hl-ic .ar-ic { width: 22px; height: 22px; }
.rc-matches { margin-top: 16px; }
.rc-ml { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 8px; }
.rc-m { display: grid; grid-template-columns: auto 1fr auto; grid-template-areas: "l l l" "w s s" "x x x"; gap: 2px 10px; padding: 10px 12px; border-radius: 14px; background: rgba(255, 255, 255, .025); border: 1px solid var(--ar-line); border-left: 3px solid var(--ar-line2); }
.rc-m.s-e { border-left-color: var(--ar-cyan); } .rc-m.s-f { border-left-color: var(--ar-gold); background: rgba(255, 210, 63, .05); }
.rc-m-l { grid-area: l; font-size: 10.5px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--ar-mut); }
.rc-m-w { grid-area: w; font-weight: 700; font-size: 13.5px; }
.rc-m-s { grid-area: s; justify-self: end; font: 800 15px var(--ar-h, var(--m-display)); color: var(--ar-lime); }
.rc-m.s-f .rc-m-s { color: var(--ar-gold); }
.rc-m-x { grid-area: x; color: var(--ar-mut); font-size: 12.5px; }
@media (max-width: 980px) { .rc-grid { grid-template-columns: 1fr; } .rc-hl { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .rc-h1, .rc-h2 { display: none; } .rc-hl { grid-template-columns: 1fr; } .rc-t { font-size: 12.5px; } .rc-t td, .rc-t th { padding: 6px 4px; }
  .rc-table { padding: 14px 10px 10px; } .rc-t th { font-size: 9.5px; letter-spacing: .06em; } .rc-pl button { gap: 6px; font-size: 13px; } .rc-pl .rc-av { width: 24px; height: 24px; }
  .rc-res { padding: 2px 6px; font-size: 9px; letter-spacing: .03em; } }
"""
