"""Home page: Final streaks. Who keeps reaching the final, and who keeps winning it.

Streaks run over the days a player played: a day missed does not break a run, a day played
without reaching the final does. "Finals won in a row" runs over the finals a player reached.
"""
from html import escape


def _runs(seq):
    """seq: [(day, flag)] in order. Returns ((best, start, end), current)."""
    best, cur, st = (0, None, None), 0, None
    for day, v in seq:
        if v:
            if cur == 0:
                st = day
            cur += 1
            if cur > best[0]:
                best = (cur, st, day)
        else:
            cur = 0
    return best, cur


def _rng(b):
    n, a, z = b
    if not n:
        return '—'
    return escape(a) if a == z else f'{escape(a)} – {escape(z)}'


def streak_stats(T, P):
    D = sorted(T['daily'], key=lambda r: r['day_index'])
    days = sorted({(r['day_index'], r['day']) for r in D})
    S = {}
    for p in P:
        rows = [r for r in D if r['player'] == p and r['played']]
        fins = [r for r in rows if r['final']]
        fb, fc = _runs([(r['day'], r['final']) for r in rows])
        wb, wc = _runs([(r['day'], r['title']) for r in fins])
        fc_start = rows[-fc]['day'] if fc else None
        by = {r['day_index']: r for r in D if r['player'] == p}
        strip = []
        for i, d in days[-10:]:
            r = by.get(i)
            strip.append((d, 'na' if not r or not r['played'] else ('t' if r['title'] else ('f' if r['final'] else 'o'))))
        S[p] = dict(days=len(rows), fin=len(fins), w=sum(r['title'] for r in fins), l=sum(not r['title'] for r in fins),
                    fbest=fb, fnow=fc, fnow_start=fc_start, wbest=wb, wnow=wc, strip=strip,
                    last=(fins[-1]['day'], fins[-1]['title']) if fins else None)
    return S


def streaks_html(T, P, slug, col, icon):
    S = streak_stats(T, P)
    av = lambda p, cls='rc-av': f'<img class="{cls}" data-ph-avatar="{escape(p)}" alt="" style="--pc:{col(p)}">'

    def card(cls, ic, label, p, big, unit, sub):
        return (f'<button type="button" class="st-hl ar-reveal {cls}" data-goto-player="{slug[p]}" style="--pc:{col(p)}">'
                f'<span class="st-hl-k">{icon(ic)}{label}</span>'
                f'<span class="st-hl-p">{av(p)}<b>{escape(p)}</b></span>'
                f'<span class="st-hl-v"><b>{big}</b> {unit}</span><span class="st-hl-s">{sub}</span></button>')

    # highlight cards
    live = max(P, key=lambda p: (S[p]['fnow'], S[p]['fbest'][0]))
    ever = max(P, key=lambda p: (S[p]['fbest'][0], S[p]['fnow']))
    cards = []
    if S[live]['fnow'] >= 2:
        lv = S[live]
        cards.append(card('hot', 'fire', 'Live final run', live, lv['fnow'], 'finals in a row',
                          f'Every day {escape(live)} has played since {escape(lv["fnow_start"])}' + (' — the longest run of the season' if lv['fnow'] == S[ever]['fbest'][0] else '')))
    # next-longest run by a different player (or the all-time run if it is not the live one)
    others = [p for p in P if p != live] if S[live]['fnow'] >= 2 and S[live]['fnow'] == S[live]['fbest'][0] else P
    nx = max(others, key=lambda p: S[p]['fbest'][0])
    cards.append(card('', 'trend', 'Longest final run' if nx == ever else 'Next longest run', nx, S[nx]['fbest'][0], 'finals in a row', _rng(S[nx]['fbest'])))
    wk = max(P, key=lambda p: (S[p]['wbest'][0], S[p]['w']))
    cards.append(card('gold', 'crown', 'Finals won in a row', wk, S[wk]['wbest'][0], 'titles in a row', _rng(S[wk]['wbest'])))
    elig = [p for p in P if S[p]['fin'] >= 5]
    br = max(elig, key=lambda p: (S[p]['w'] / S[p]['fin'], S[p]['w'])) if elig else None
    if br:
        cards.append(card('cyan', 'bolt', 'Best final record', br, f'{S[br]["w"]}–{S[br]["l"]}', 'in finals',
                          f'{round(100 * S[br]["w"] / S[br]["fin"])}% won · 5 or more finals'))

    # table rows: live run first, then longest run
    order = sorted(P, key=lambda p: (-S[p]['fnow'], -S[p]['fbest'][0], -S[p]['w']))
    top_now = max(S[p]['fnow'] for p in P)
    rows = []
    for p in order:
        s = S[p]
        pct = round(100 * s['fin'] / s['days']) if s['days'] else 0
        now = (f'<span class="st-now{" on" if s["fnow"] >= 3 else ""}{" lead" if s["fnow"] == top_now and top_now >= 2 else ""}">'
               f'{icon("fire") if s["fnow"] >= 3 else ""}<b>{s["fnow"]}</b></span>')
        wnow = f'<span class="st-now{" gold" if s["wnow"] >= 2 else ""}"><b>{s["wnow"]}</b></span>'
        dots = ''.join(f'<i class="st-d {k}" title="{escape(d)}: {dict(t="won the title", f="lost the final", o="out before the final", na="did not play")[k]}"></i>'
                       for d, k in s['strip'])
        last = (f'{escape(s["last"][0])} · {"won" if s["last"][1] else "lost"}') if s['last'] else '—'
        rows.append(f'<tr style="--pc:{col(p)}">'
                    f'<td class="st-pl" data-l="Player"><button type="button" data-goto-player="{slug[p]}">{av(p)}<span>{escape(p)}</span></button></td>'
                    f'<td data-l="Finals reached"><b>{s["fin"]}</b><small> of {s["days"]} · {pct}%</small></td>'
                    f'<td data-l="Final run now">{now}</td>'
                    f'<td data-l="Longest final run"><b>{s["fbest"][0]}</b><small>{_rng(s["fbest"])}</small></td>'
                    f'<td data-l="Finals W–L"><b>{s["w"]}–{s["l"]}</b><small>last: {last}</small></td>'
                    f'<td data-l="Wins in a row now">{wnow}</td>'
                    f'<td data-l="Most finals won in a row"><b>{s["wbest"][0]}</b><small>{_rng(s["wbest"])}</small></td>'
                    f'<td class="st-strip" data-l="Last 10 sessions"><span>{dots}</span></td></tr>')

    legend = ('<span class="st-lg"><i class="st-d t"></i>Won the title</span><span class="st-lg"><i class="st-d f"></i>Lost the final</span>'
              '<span class="st-lg"><i class="st-d o"></i>Out before the final</span><span class="st-lg"><i class="st-d na"></i>Did not play</span>')
    return (f'<section class="ar-block st" id="streaks"><div class="ar-head"><p class="ar-eyebrow">Who keeps reaching the final</p>'
            f'<h2 class="ar-h">Final streaks</h2></div>'
            f'<div class="st-hls">{"".join(cards)}</div>'
            f'<div class="st-card ar-reveal"><div class="st-card-hd"><h3>Final runs and finals won in a row</h3>'
            f'<p>A run counts the days a player played: a missed day does not break it, a day out before the final does. '
            f'“Won in a row” counts the finals a player reached.</p></div>'
            f'<div class="bx-tw st-tw"><table class="st-table"><thead><tr><th>Player</th><th>Finals reached</th><th>Final run now</th><th>Longest final run</th>'
            f'<th>Finals W–L</th><th>Wins in a row now</th><th>Most finals won in a row</th><th>Last 10 sessions</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div><div class="st-legend">{legend}</div></div></section>')


STREAKS_CSS = r"""
/* ---------------- final streaks (home) ---------------- */
.st-hls { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.st-hl { position: relative; overflow: hidden; display: grid; gap: 10px; align-content: start; text-align: left; padding: 18px 18px 16px; border-radius: 20px; cursor: pointer; color: var(--ar-fg); font: inherit;
  background: linear-gradient(150deg, color-mix(in srgb, var(--acc, var(--pc)) 16%, transparent), rgba(17, 23, 34, .88) 62%); border: 1px solid color-mix(in srgb, var(--acc, var(--pc)) 38%, transparent);
  box-shadow: var(--ar-shadow); transition: transform .25s var(--ar-ease), border-color .25s ease; }
.st-hl:hover { transform: translateY(-4px); border-color: color-mix(in srgb, var(--acc, var(--pc)) 70%, transparent); }
.st-hl.hot { --acc: #FF7A1A; } .st-hl.gold { --acc: var(--ar-gold); } .st-hl.cyan { --acc: var(--ar-cyan); }
.st-hl-k { display: inline-flex; align-items: center; gap: 7px; font: 700 11px/1 var(--ar-h, var(--m-display)); letter-spacing: .18em; text-transform: uppercase; color: var(--acc, var(--pc)); }
.st-hl-k .ar-ic { width: 16px; height: 16px; }
.st-hl-p { display: flex; align-items: center; gap: 10px; }
.st-hl-p b { font: 800 18px/1.1 var(--ar-h, var(--m-display)); letter-spacing: .03em; }
.st-hl-v { color: var(--ar-mut); font-size: 13px; }
.st-hl-v b { font: 800 clamp(34px, 3.4vw, 44px)/1 var(--ar-h, var(--m-display)); color: var(--acc, var(--pc)); margin-right: 4px; text-shadow: 0 0 22px color-mix(in srgb, var(--acc, var(--pc)) 45%, transparent); font-variant-numeric: tabular-nums; }
.st-hl-s { color: var(--ar-mut); font-size: 12.5px; line-height: 1.45; }
.st-hl.hot::after { content: ""; position: absolute; right: -30px; top: -30px; width: 120px; height: 120px; border-radius: 50%; pointer-events: none;
  background: radial-gradient(circle, rgba(255, 122, 26, .35), transparent 65%); }

.st-card { border-radius: 22px; padding: 18px 18px 14px; background: var(--ar-glass); border: 1px solid var(--ar-line); box-shadow: var(--ar-shadow); min-width: 0; }
.st-card-hd { display: grid; gap: 4px; margin-bottom: 12px; }
.st-card-hd h3 { margin: 0; font: 700 17px/1.2 var(--ar-h, var(--m-display)); letter-spacing: .03em; }
.st-card-hd p { margin: 0; font-size: 12.5px; color: var(--ar-mut); }
.st-table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.st-table th { padding: 10px 10px; text-align: left; white-space: normal; line-height: 1.35 !important; vertical-align: bottom; max-width: 9em; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .14em; text-transform: uppercase; color: var(--ar-mut); border-bottom: 1px solid rgba(0, 217, 255, .25); }
.st-table td { padding: 11px 10px; vertical-align: middle; border-bottom: 1px solid var(--ar-line); white-space: nowrap; }
.st-table tbody tr:last-child td { border-bottom: 0; }
.st-table tbody tr { transition: background-color .2s ease; }
.st-table tbody tr:hover { background: color-mix(in srgb, var(--pc) 8%, transparent); }
.st-table td b { font: 800 16px/1.1 var(--ar-h, var(--m-display)); }
.st-table td small { display: block; margin-top: 3px; font-size: 11.5px; color: var(--ar-mut); }
.st-table td > b + small { display: block; }
.st-pl button { display: inline-flex; align-items: center; gap: 9px; padding: 0; border: 0; background: none; color: var(--ar-fg); font: 600 14px var(--m-body); cursor: pointer; }
.st-pl button:hover span { color: var(--pc); }
.st-now { display: inline-flex; align-items: center; gap: 5px; min-width: 40px; justify-content: center; padding: 5px 10px; border-radius: 999px; background: rgba(255, 255, 255, .04); border: 1px solid var(--ar-line); }
.st-now b { font-size: 15px !important; }
.st-now .ar-ic { width: 14px; height: 14px; }
.st-now.on { color: #FFB066; border-color: rgba(255, 122, 26, .5); background: rgba(255, 122, 26, .12); }
.st-now.lead { color: #FFD9B0; background: linear-gradient(180deg, rgba(255, 122, 26, .4), rgba(255, 122, 26, .16)); box-shadow: 0 0 18px rgba(255, 122, 26, .35); }
.st-now.gold { color: var(--ar-gold); border-color: rgba(255, 210, 63, .5); background: rgba(255, 210, 63, .1); }
.st-strip span { display: inline-flex; gap: 4px; align-items: center; }
.st-d { display: inline-block; width: 11px; height: 11px; border-radius: 50%; flex: none; }
.st-d.t { background: var(--ar-gold); box-shadow: 0 0 8px rgba(255, 210, 63, .7); }
.st-d.f { border: 2px solid var(--ar-cyan); }
.st-d.o { background: rgba(137, 147, 164, .35); width: 8px; height: 8px; margin: 0 2px; }
.st-d.na { border: 1.5px dashed rgba(137, 147, 164, .4); }
.st-legend { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 12px; font-size: 12px; color: var(--ar-mut); }
.st-lg { display: inline-flex; align-items: center; gap: 7px; }
@media (max-width: 1100px) { .st-hls { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .st-hls { gap: 10px; }
  .st-hl { padding: 14px; gap: 8px; }
  .st-hl-p b { font-size: 15px; }
  .st-hl-v { display: grid; gap: 4px; }
  .st-hl-v b { font-size: 32px; margin: 0; }
  .st-card { padding: 14px 12px 12px; }
}
@media (max-width: 980px) {
  /* each player becomes a card: name and strip on top, the numbers in a 3-column grid */
  .st-tw { overflow: visible; -webkit-mask-image: none !important; mask-image: none !important; border: 0; background: none; }
  .st-table, .st-table tbody { display: block; }
  .st-table thead { display: none; }
  .st-table tr { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 8px; padding: 14px 4px; border-bottom: 1px solid var(--ar-line); }
  .st-table tbody tr:last-child { border-bottom: 0; }
  .st-table td { display: block; padding: 0; border: 0; white-space: normal; min-width: 0; }
  .st-table td::before { content: attr(data-l); display: block; margin-bottom: 4px; font: 700 9.5px/1.2 var(--ar-h, var(--m-display)); letter-spacing: .12em; text-transform: uppercase; color: var(--ar-mut); }
  .st-table td.st-pl { grid-column: 1 / 3; align-self: center; }
  .st-table td.st-pl::before, .st-table td.st-strip::before { display: none; }
  .st-table td.st-strip { grid-column: 3; grid-row: 1; align-self: center; justify-self: end; }
  .st-strip span { gap: 3px; flex-wrap: nowrap; justify-content: flex-end; }
  .st-d { width: 8px; height: 8px; }
  .st-d.o { width: 5px; height: 5px; margin: 0 1.5px; }
  .st-d.f { border-width: 1.5px; }
  .st-table td b { font-size: 15px; }
}
"""
