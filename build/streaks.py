"""Home page: Final streaks, as two separate tables.

1. Most finals entered: total finals each player reached, with the share of days played.
2. Finals won in a row: each player's longest run of finals won, counted over the finals the
   player reached, so a lost final ends the run.
"""
from html import escape


def _best_run(seq):
    """seq: [(day, flag)] in order. Returns (length, first day, last day) of the longest run of True."""
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
    return best


def _all_best(seq):
    """seq: [(day, day_index, flag)]. Every run of True as long as the longest: [(n, first, last, first_index, last_index)]."""
    runs, cur = [], None
    for day, i, v in seq:
        if v:
            cur = [cur[0] + 1, cur[1], day, cur[3], i] if cur else [1, day, day, i, i]
        else:
            if cur:
                runs.append(tuple(cur))
            cur = None
    if cur:
        runs.append(tuple(cur))
    n = max((r[0] for r in runs), default=0)
    return [r for r in runs if r[0] == n] if n else []


def _rng(b):
    n, a, z = b
    if not n:
        return 'No final yet'
    return escape(a) if a == z else f'{escape(a)} – {escape(z)}'


def streak_stats(T, P):
    D = sorted(T['daily'], key=lambda r: r['day_index'])
    S = {}
    for p in P:
        rows = [r for r in D if r['player'] == p and r['played']]
        fins = [r for r in rows if r['final']]
        S[p] = dict(days=len(rows), fin=len(fins), w=sum(r['title'] for r in fins), l=sum(not r['title'] for r in fins),
                    fbest=_best_run([(r['day'], r['final']) for r in rows]),
                    wbest=_best_run([(r['day'], r['title']) for r in fins]),
                    fruns=_all_best([(r['day'], r['day_index'], r['final']) for r in rows]),
                    wruns=_all_best([(r['day'], r['day_index'], r['title']) for r in fins]))
    return S


def _ranks(order, key):
    """Standard competition ranks (1, 2, 2, 4) on the run length."""
    out, prev, rk = {}, None, 0
    for i, p in enumerate(order):
        k = key(p)
        if k != prev:
            rk, prev = i + 1, k
        out[p] = rk
    return out


def streaks_html(T, P, slug, col, icon):
    S = streak_stats(T, P)
    av = lambda p: f'<img class="rc-av" data-ph-avatar="{escape(p)}" alt="" style="--pc:{col(p)}">'

    def table(kind):
        if kind == 'f':
            # most finals entered: total finals reached, with the share of days played
            order = sorted(P, key=lambda p: (-S[p]['fin'], -S[p]['fin'] / max(1, S[p]['days']), p))
            n_of = lambda p: S[p]['fin']
            sub = lambda p: f'{S[p]["w"]} won · {S[p]["l"]} lost'
            unit, col_n, col_t = 'finals', 'Finals', 'Rate'
            tot = lambda p: (f'{round(100 * S[p]["fin"] / S[p]["days"]) if S[p]["days"] else 0}%', f'of {S[p]["days"]} days')
            notes = lambda p: ''
        else:
            # finals won in a row: longest run of titles, counted over the finals reached
            order = sorted(P, key=lambda p: (-S[p]['wbest'][0], -S[p]['w'], p))
            n_of = lambda p: S[p]['wbest'][0]
            sub = lambda p: _rng(S[p]['wbest'])
            unit, col_n, col_t = 'titles', 'In a row', 'Finals W–L'
            tot = lambda p: (f'{S[p]["w"]}–{S[p]["l"]}', 'in finals')

            def notes(p):
                return ''.join(f'<small class="sk-note">also {_rng(r[:3])}</small>' for r in S[p]['wruns'][1:] if r[0] >= 2)
        rk = _ranks(order, n_of)
        top = max(n_of(p) for p in P) or 1
        rows = []
        for p in order:
            n = n_of(p); t1, t2 = tot(p)
            rows.append(f'<li class="sk-row{" lead" if rk[p] == 1 and n else ""}" style="--pc:{col(p)}">'
                        f'<span class="sk-rk">{rk[p]}</span>'
                        f'<button type="button" class="sk-pl" data-goto-player="{slug[p]}">{av(p)}<span><b>{escape(p)}</b><small>{sub(p)}</small>{notes(p)}</span></button>'
                        f'<span class="sk-bar" aria-hidden="true"><i style="width:{max(3, round(100 * n / top))}%"></i></span>'
                        f'<span class="sk-n"><b>{n}</b><small>{unit if n != 1 else unit[:-1]}</small></span>'
                        f'<span class="sk-tot"><b>{t1}</b><small>{t2}</small></span></li>')
        head = (f'<div class="sk-hd" aria-hidden="true"><span>#</span><span>Player</span><span></span>'
                f'<span>{col_n}</span><span>{col_t}</span></div>')
        return head + f'<ol class="sk-list">{"".join(rows)}</ol>'

    f_lead = max(P, key=lambda p: (S[p]['fin'], S[p]['w']))
    w_lead = max(P, key=lambda p: (S[p]['wbest'][0], S[p]['w']))
    return (f'<section class="ar-block st" id="streaks"><div class="ar-head"><p class="ar-eyebrow">Who reaches the final most, and who keeps winning it</p>'
            f'<h2 class="ar-h">Final streaks</h2></div>'
            f'<div class="sk-grid">'
            f'<div class="sk-card ar-reveal f"><div class="sk-card-hd"><span class="sk-ic">{icon("trend")}</span><div><h3>Most finals entered</h3>'
            f'<p>Total finals each player has reached this season, with the share of the days they played.</p></div></div>'
            f'{table("f")}'
            f'<p class="sk-foot"><b>{escape(f_lead)}</b> has reached the most finals: {S[f_lead]["fin"]} of {S[f_lead]["days"]} days.</p></div>'
            f'<div class="sk-card ar-reveal w"><div class="sk-card-hd"><span class="sk-ic">{icon("crown")}</span><div><h3>Finals won in a row</h3>'
            f'<p>Each player’s longest run of finals won, counted over the finals they reached: a lost final ends the run.</p></div></div>'
            f'{table("w")}'
            f'<p class="sk-foot"><b>{escape(w_lead)}</b> holds the record: {S[w_lead]["wbest"][0]} titles in a row ({_rng(S[w_lead]["wbest"])}).</p></div>'
            f'</div></section>')


STREAKS_CSS = r"""
/* ---------------- final streaks (home): two tables ---------------- */
.sk-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; align-items: start; }
.sk-card { --acc: var(--ar-lime); position: relative; overflow: hidden; display: grid; gap: 12px; padding: 18px; border-radius: 22px; min-width: 0;
  background: radial-gradient(120% 80% at 0% 0%, color-mix(in srgb, var(--acc) 10%, transparent), transparent 60%), var(--ar-glass); border: 1px solid var(--ar-line); box-shadow: var(--ar-shadow); }
.sk-card.w { --acc: var(--ar-gold); }
.sk-card::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 2px; background: linear-gradient(90deg, var(--acc), transparent 70%); }
.sk-card-hd { display: flex; gap: 12px; align-items: flex-start; }
.sk-ic { flex: none; width: 40px; height: 40px; display: grid; place-items: center; border-radius: 12px; color: var(--acc);
  background: color-mix(in srgb, var(--acc) 12%, transparent); border: 1px solid color-mix(in srgb, var(--acc) 40%, transparent); }
.sk-ic .ar-ic { width: 20px; height: 20px; }
.sk-card-hd h3 { margin: 0; font: 800 18px/1.2 var(--ar-h, var(--m-display)); letter-spacing: .03em; }
.sk-card-hd p { margin: 4px 0 0; font-size: 12.5px; line-height: 1.5; color: var(--ar-mut); }

/* one grid for the header and every row, so the columns line up */
.sk-hd, .sk-row { display: grid; grid-template-columns: 30px minmax(0, 1.5fr) minmax(40px, 1fr) 64px 86px; align-items: center; column-gap: 12px; }
.sk-hd { padding: 0 12px 8px; border-bottom: 1px solid color-mix(in srgb, var(--acc) 30%, transparent);
  font: 700 10px/1.2 var(--ar-h, var(--m-display)); letter-spacing: .14em; text-transform: uppercase; color: var(--ar-mut); }
.sk-hd span:nth-child(4), .sk-hd span:nth-child(5) { text-align: right; }
.sk-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
.sk-row { position: relative; padding: 10px 12px; border-radius: 14px; background: rgba(5, 8, 13, .4); border: 1px solid rgba(255, 255, 255, .05); transition: border-color .2s ease, background-color .2s ease; }
.sk-row:hover { border-color: color-mix(in srgb, var(--pc) 55%, transparent); background: color-mix(in srgb, var(--pc) 7%, rgba(5, 8, 13, .4)); }
.sk-row.lead { border-color: color-mix(in srgb, var(--acc) 55%, transparent); background: linear-gradient(90deg, color-mix(in srgb, var(--acc) 14%, transparent), rgba(5, 8, 13, .4) 70%);
  box-shadow: 0 0 22px color-mix(in srgb, var(--acc) 16%, transparent); }
.sk-rk { width: 28px; height: 28px; display: grid; place-items: center; border-radius: 9px; font: 800 13px/1 var(--ar-h, var(--m-display)); color: var(--ar-mut); background: rgba(255, 255, 255, .04); }
.sk-row.lead .sk-rk { color: #0A0E14; background: var(--acc); box-shadow: 0 0 14px color-mix(in srgb, var(--acc) 60%, transparent); }
.sk-pl { display: flex; align-items: center; gap: 10px; min-width: 0; padding: 0; border: 0; background: none; color: var(--ar-fg); text-align: left; cursor: pointer; font: inherit; }
.sk-pl > span { display: grid; gap: 2px; min-width: 0; }
.sk-pl b { font: 700 14.5px/1.2 var(--m-body); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sk-pl small { font-size: 11.5px; color: var(--ar-mut); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-variant-numeric: tabular-nums; }
.sk-pl:hover b { color: var(--pc); }
.sk-pl small.sk-note { white-space: normal; font-size: 10.5px; color: color-mix(in srgb, var(--acc) 70%, var(--ar-mut)); }
.sk-bar { height: 8px; border-radius: 6px; background: rgba(255, 255, 255, .05); overflow: hidden; }
.sk-bar i { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, color-mix(in srgb, var(--acc) 35%, transparent), var(--acc)); transform-origin: left; }
.ar-js .sk-card.is-in .sk-bar i { animation: ar-grow 1s var(--ar-ease) .15s backwards; }
.sk-n, .sk-tot { display: grid; justify-items: end; gap: 2px; text-align: right; font-variant-numeric: tabular-nums; }
.sk-n b { font: 800 22px/1 var(--ar-h, var(--m-display)); color: var(--ar-fg); }
.sk-row.lead .sk-n b { color: var(--acc); text-shadow: 0 0 16px color-mix(in srgb, var(--acc) 50%, transparent); }
.sk-tot b { font: 700 15px/1 var(--ar-h, var(--m-display)); }
.sk-n small, .sk-tot small { font-size: 10.5px; color: var(--ar-mut); white-space: nowrap; }
.sk-foot { margin: 2px 0 0; font-size: 12.5px; color: var(--ar-mut); }
.sk-foot b { color: var(--acc); }

@media (max-width: 1180px) { .sk-grid { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 620px) {
  .sk-card { padding: 14px 12px; }
  .sk-card-hd h3 { font-size: 16px; }
  .sk-ic { width: 34px; height: 34px; border-radius: 10px; }
  /* phone rows: rank | player and dates | run; the bar and the total sit on a second line */
  .sk-hd { display: none; }
  .sk-row { grid-template-columns: 28px minmax(0, 1fr) auto; grid-template-areas: "rk pl n" "rk bar tot"; row-gap: 8px; column-gap: 10px; padding: 10px; }
  .sk-rk { grid-area: rk; align-self: start; margin-top: 4px; }
  .sk-pl { grid-area: pl; }
  .sk-n { grid-area: n; }
  .sk-bar { grid-area: bar; align-self: center; }
  .sk-tot { grid-area: tot; display: flex; align-items: baseline; gap: 4px; }
  .sk-tot b { font-size: 12.5px; }
  .sk-n b { font-size: 20px; }
}
"""
