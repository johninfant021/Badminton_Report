"""Leaderboard section: best match scores, the biggest wins of the season by points margin.

The list never cuts through a tie: it runs to the end of the group the 10th match belongs to, and the rows shown
before "show" stop where a tie group starts.
"""
from html import escape


def best_scores(T, P, n=10):
    """(rows, shown): matches ranked by margin, newest first within a margin, tie groups kept whole."""
    team = lambda s: sorted((x.strip() for x in s.split(' + ')), key=P.index)
    rows = []
    for m in T['matches']:
        wa = m['winner'] == m['team_a']
        rows.append(dict(n=m['n'], margin=abs(m['score_a'] - m['score_b']), w=team(m['team_a'] if wa else m['team_b']), l=team(m['team_b'] if wa else m['team_a']),
                         hi=max(m['score_a'], m['score_b']), lo=min(m['score_a'], m['score_b']), day=m['day'],
                         stage=m['label'] if m['stage'] == 'Qualifier' else m['stage']))
    rows.sort(key=lambda r: (-r['margin'], -r['n']))
    cut = rows[min(n, len(rows)) - 1]['margin']
    rows = [r for r in rows if r['margin'] >= cut]
    above = sum(r['margin'] > cut for r in rows)
    shown = len(rows) if len(rows) <= n else (above if above >= 5 else n)
    return rows, shown


def scores_html(T, P, col, icon):
    rows, shown = best_scores(T, P)
    av = lambda p: f'<img class="rc-av" data-ph-avatar="{escape(p)}" alt="" style="--pc:{col(p)}">'
    nb = lambda s: escape(s).replace(' ', '&nbsp;')
    top = rows[0]['margin'] or 1

    def row(r):
        rk = 1 + sum(x['margin'] > r['margin'] for x in rows)
        return (f'<li class="sk-row bs-row{" lead" if rk == 1 else ""}" style="--pc:{col(r["w"][0])}">'
                f'<span class="sk-rk">{rk}</span>'
                f'<span class="sk-pl sk-pair"><span class="sk-avs">{av(r["w"][0])}{av(r["w"][1])}</span>'
                f'<span><b>{escape(" + ".join(r["w"]))}</b><small>beat {escape(" + ".join(r["l"]))}</small></span></span>'
                f'<span class="bs-when"><b>{nb(r["day"])}</b><small>{nb(r["stage"])}</small></span>'
                f'<span class="sk-bar" aria-hidden="true"><i style="width:{round(100 * r["margin"] / top)}%"></i></span>'
                f'<span class="sk-n bs-sc"><b>{r["hi"]}–{r["lo"]}</b></span>'
                f'<span class="sk-tot"><b>+{r["margin"]}</b><small>points</small></span></li>')

    out = [row(r) for r in rows]
    rest = len(rows) - shown
    more = (f'<details class="sk-more"><summary>Show {rest} more</summary><ol class="sk-list">{"".join(out[shown:])}</ol></details>' if rest else '')
    return (f'<div class="sk-card bs ar-reveal" id="best-scores"><div class="sk-card-hd"><span class="sk-ic">{icon("fire")}</span><div><h3>Best match scores</h3>'
            f'<p>The biggest wins of the season by points margin, out of all {len(T["matches"])} matches. Equal margins share a rank, newest first.</p></div></div>'
            f'<div class="sk-hd bs-hd" aria-hidden="true"><span>#</span><span>Winners</span><span>When</span><span></span><span>Score</span><span>Margin</span></div>'
            f'<ol class="sk-list">{"".join(out[:shown])}</ol>{more}</div>')


SCORES_CSS = r"""
/* ---------------- best match scores (leaderboard section) ---------------- */
.sk-card.bs { --acc: var(--ar-gold); margin-top: 4px; }
.bs .bs-hd, .bs .bs-row { grid-template-columns: 30px minmax(0, 1.6fr) 110px minmax(40px, 1fr) 92px 72px; }
.bs .bs-hd span:nth-child(5), .bs .bs-hd span:nth-child(6) { text-align: right; }
.bs .bs-hd span:nth-child(4) { text-align: left; }
.bs-when { display: grid; gap: 2px; font-variant-numeric: tabular-nums; }
.bs-when b { font: 700 13.5px/1.2 var(--m-body); }
.bs-when small { font-size: 11.5px; color: var(--ar-mut); }
.bs-sc b { white-space: nowrap; }
@media (max-width: 620px) {
  /* phone rows: rank | winners and losers | score; then day and stage beside the margin, with the bar underneath */
  .bs .bs-row { grid-template-columns: 28px minmax(0, 1fr) auto; grid-template-areas: "rk pl n" "rk when tot" "rk bar bar"; }
  .bs-when { grid-area: when; display: flex; align-items: baseline; gap: 6px; }
  .bs-when b { font-size: 12px; }
}
"""
