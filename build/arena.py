"""Arena layer: esports-style presentation on top of the existing report.

Adds a sticky top navigation, a full-screen hero, a season dashboard, an esports leaderboard,
season awards and richer player profiles. Every number comes from the same tables the report is
built from (tables.json and dash/data/*.json); nothing here changes the analysis.
"""
import json, math, os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
P = ['Anto', 'Jothi Sai', 'John', 'Pawan', 'Dinesh', 'Pratap', 'Bhanu']
SLUG = {'Anto': 'anto', 'Jothi Sai': 'jothi', 'John': 'john', 'Pawan': 'pawan', 'Dinesh': 'dinesh', 'Pratap': 'pratap', 'Bhanu': 'bhanu'}
MINUS = '−'
NAV = [('overview', 'Overview'), ('leaderboard', 'Leaderboard'), ('players', 'Players'), ('analytics', 'Analytics'),
       ('partnerships', 'Partnerships'), ('opponents', 'Opponents'), ('rankings', 'Rankings'), ('predictions', 'Predictions')]
VIEWS = {'overview': ['summary'], 'leaderboard': ['summary'], 'players': ['players'], 'analytics': ['weekly', 'pressure', 'model'],
         'partnerships': ['partners'], 'opponents': ['opponents'], 'rankings': ['rankings', 'strengths'], 'predictions': ['outlook', 'data']}


def sg(x, d=2):
    return f'{x:+.{d}f}'.replace('-', MINUS)


def num(x):
    return f'{x:,}'


def _load():
    T = json.load(open(os.path.join(HERE, 'tables.json'), encoding='utf-8'))
    dd = lambda n: json.load(open(os.path.join(HERE, 'dash', 'data', f'{n}.json'), encoding='utf-8'))
    return T, {r['key']: r['text'] for r in dd('facts')}, dd('rankings'), dd('comparison')


def _last(T, p, n):
    out = []
    for m in reversed(T['matches']):
        a, b = m['team_a'].split(' + '), m['team_b'].split(' + ')
        if p in a or p in b:
            out.append(m['winner'] == (m['team_a'] if p in a else m['team_b']))
            if len(out) == n:
                break
    return list(reversed(out))


def _badges(T, R, CMP):
    E = {e['player']: e for e in T['estimates']}; PL = {x['player']: x for x in T['players']}
    champ = min(P, key=lambda p: E[p]['adj_rank'])
    improved = [r['player'] for r in sorted([r for r in R if r['category'] == 'improved'], key=lambda r: r['rank'])]
    most_imp = improved[0]
    rising = max([p for p in P if p not in (champ, most_imp)], key=lambda p: PL[p]['recent_dpm'] - PL[p]['dpm'])
    streak = max(P, key=lambda p: PL[p]['best_win_streak'])
    slump = min(P, key=lambda p: E[p]['recent_adj'] - E[p]['adj'])
    pair = max([x for x in T['pairs'] if x['P'] >= 10], key=lambda x: x['dpm'])
    B = {
        'champion': dict(player=champ, icon='crown', label='Champion', stat=sg(E[champ]['adj']), unit='adjusted',
                         why=f'Ranked first on adjusted strength; first in {E[champ]["p_first"] * 100:.0f}% of resamples.'),
        'rising': dict(player=rising, icon='bolt', label='Rising Player', stat=sg(PL[rising]['recent_dpm']), unit='last 20, per match',
                       why=f'Biggest jump in points difference per match over the last 20 matches ({sg(PL[rising]["recent_dpm"])}) against the season ({sg(PL[rising]["dpm"])}).'),
        'improved': dict(player=most_imp, icon='trend', label='Most Improved', stat=sg(E[most_imp]['change']), unit='between halves',
                         why=f'First on the Most improved ranking: {sg(E[most_imp]["change"])} between halves, trend {sg(E[most_imp]["trend21"], 1)}.'),
        'streak': dict(player=streak, icon='fire', label='Winning Streak', stat=str(PL[streak]['best_win_streak']), unit='wins in a row',
                       why='Longest run of consecutive wins this season.'),
        'slump': dict(player=slump, icon='down', label='Recent Slump', stat=sg(E[slump]['recent_adj'] - E[slump]['adj']), unit='recent vs season',
                      why=f'Largest drop from season estimate ({sg(E[slump]["adj"])}) to recency-weighted estimate ({sg(E[slump]["recent_adj"])}).'),
        'pair': dict(player=pair['a'], player2=pair['b'], icon='link', label='Best Partnership', stat=pair['record'], unit=f'{sg(pair["dpm"])} per match',
                     why=f'Best points difference per match of any pair with 10 or more matches together ({pair["P"]} played).'),
    }
    return B


ICONS = {
    'crown': '<path d="M3 18h18l-1.5-9-4.5 4-3-7-3 7-4.5-4z"/><path d="M4 21h16"/>',
    'bolt': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    'trend': '<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
    'fire': '<path d="M12 22c4 0 7-3 7-7 0-5-5-7-5-12-3 2-4 5-4 7-1-1-2-2-2-4-2 2-3 5-3 9 0 4 3 7 7 7z"/>',
    'down': '<path d="m3 7 6 6 4-4 8 8"/><path d="M14 17h7v-7"/>',
    'link': '<path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/>',
    'shuttle': '<path d="M12 21a3 3 0 0 0 3-3H9a3 3 0 0 0 3 3z"/><path d="M9 18 5 4l7 3 7-3-4 14"/><path d="M12 7v11"/>',
    'arrow': '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
}


def icon(name, cls='ar-ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def court_svg():
    """Badminton court in perspective (true dimensions, 13.4 m x 6.1 m) for the hero background."""
    f, hcam, hor, cx = 980.0, 6.0, 170.0, 800.0
    z0 = 7.4
    def pt(X, zc):  # zc: distance from near baseline along the court
        z = z0 + zc
        return cx + f * X / z, hor + f * hcam / z
    L = 13.4; W = 3.05; S = 2.59
    lines = []
    def seg(x1, z1, x2, z2, cls='ln'):
        a = pt(x1, z1); b = pt(x2, z2)
        lines.append(f'<line class="{cls}" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" pathLength="1"/>')
    for X in (-W, W, -S, S):
        seg(X, 0, X, L)
    for zc in (0, 0.76, L / 2 - 1.98, L / 2 + 1.98, L - 0.76, L):
        seg(-W, zc, W, zc)
    seg(0, 0, 0, L / 2 - 1.98); seg(0, L / 2 + 1.98, 0, L)
    # net
    nl, nr = pt(-W - .3, L / 2), pt(W + .3, L / 2)
    top = 1.55 * f / (z0 + L / 2)
    net = (f'<path class="net" d="M{nl[0]:.1f},{nl[1]:.1f} L{nl[0]:.1f},{nl[1] - top:.1f} L{nr[0]:.1f},{nr[1] - top:.1f} L{nr[0]:.1f},{nr[1]:.1f} Z"/>'
           f'<line class="net-top" x1="{nl[0]:.1f}" y1="{nl[1] - top:.1f}" x2="{nr[0]:.1f}" y2="{nr[1] - top:.1f}"/>')
    a, b, c, d = pt(-W, 0), pt(W, 0), pt(W, L), pt(-W, L)
    floor = f'<polygon class="floor" points="{a[0]:.0f},{a[1]:.0f} {b[0]:.0f},{b[1]:.0f} {c[0]:.0f},{c[1]:.0f} {d[0]:.0f},{d[1]:.0f}"/>'
    s0, s1 = pt(-1.2, 3.0), pt(1.4, L - 3.2)
    arc = f'M{s0[0]:.0f},{s0[1] - 60:.0f} Q{cx:.0f},{hor - 120:.0f} {s1[0]:.0f},{s1[1] - 40:.0f}'
    shuttle = (f'<path id="ar-arc" class="arc" d="{arc}"/>'
               '<g class="shuttle"><circle r="7"/><path d="M-5,-4 L-26,-16 M-5,0 L-29,-2 M-5,4 L-26,12" />'
               '<animateMotion dur="4.2s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1">'
               '<mpath href="#ar-arc"/></animateMotion></g>')
    return (f'<svg class="ar-court" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'
            f'<defs><linearGradient id="ar-fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00D9FF" stop-opacity=".02"/>'
            f'<stop offset="1" stop-color="#C6FF00" stop-opacity=".10"/></linearGradient></defs>'
            f'{floor}<g class="lines">{"".join(lines)}</g>{net}{shuttle}</svg>')


def _stat_tile(key, label, value, sub, extra='', count=None, fmt='int', accent='lime'):
    c = f' data-count="{count}" data-fmt="{fmt}"' if count is not None else ''
    return (f'<div class="ar-stat ar-reveal ar-{accent}" data-k="{key}"><p class="ar-stat-l">{label}</p>'
            f'<p class="ar-stat-v"{c}>{value}</p><p class="ar-stat-s">{sub}</p>{extra}</div>')


def arena_page(page, photos):
    T, F, R, CMP = _load()
    E = {e['player']: e for e in T['estimates']}; PL = {x['player']: x for x in T['players']}
    CM = {x['player']: x for x in CMP}
    M = T['matches']; N = len(M)
    days = []
    for m in M:
        if m['day'] not in days:
            days.append(m['day'])
    weeks = len({m['week'] for m in M})
    st = {s: sum(1 for m in M if m['stage'] == s) for s in ('Qualifier', 'Eliminator', 'Final')}
    wins = sum(PL[p]['W'] for p in P); titles = st['Final']
    best = max(P, key=lambda p: PL[p]['win_pct'])
    order = sorted(P, key=lambda p: E[p]['adj_rank'])
    top = order[0]
    B = _badges(T, R, CMP)
    pbadge = {p: [k for k, b in B.items() if b['player'] == p or b.get('player2') == p] for p in P}
    pts = sum(m['score_a'] + m['score_b'] for m in M)
    col = lambda p: f'var(--series-{P.index(p) + 1})'

    # ---------------------------------------------------------------- nav + hero (outside .bx)
    links = ''.join(f'<a class="ar-link" href="#{v}" data-view="{v}">{l}</a>' for v, l in NAV)
    nav = (f'<header class="ar-nav" id="ar-nav"><div class="ar-nav-in">'
           f'<a class="ar-logo" href="#overview" data-view="overview">{icon("shuttle", "ar-logo-ic")}<span>BADMINTON<b>ARENA</b></span></a>'
           f'<nav class="ar-links" aria-label="Sections">{links}<span class="ar-ind" aria-hidden="true"></span></nav>'
           f'<span class="ar-live"><i></i>Through {escape(days[-1])}</span>'
           f'<button type="button" class="ar-burger" aria-expanded="false" aria-controls="ar-menu" aria-label="Open menu"><span></span><span></span><span></span></button>'
           f'</div><nav class="ar-menu" id="ar-menu" aria-label="Sections" hidden>{links}</nav></header>')
    e0 = E[top]; p0 = PL[top]
    hero = (f'<section class="ar-hero" id="overview" aria-label="Badminton Arena">'
            f'<div class="ar-hero-bg" aria-hidden="true"><div class="ar-glow g1"></div><div class="ar-glow g2"></div><div class="ar-grid"></div>{court_svg()}'
            f'<div class="ar-sparks">{"".join(f"<i style=--i:{i}></i>" for i in range(14))}</div></div>'
            f'<div class="ar-hero-in">'
            f'<p class="ar-kicker"><span class="ar-dot"></span>Doubles league · {weeks} weeks · {len(days)} session days</p>'
            f'<h1 class="ar-title"><span class="t1">BADMINTON</span><span class="t2">ARENA</span></h1>'
            f'<p class="ar-sub">COMPETE. <b>DOMINATE.</b> RISE.</p>'
            f'<div class="ar-hero-row">'
            f'<div class="ar-hero-stats">'
            f'<div><b data-count="{N}">{N}</b><span>Matches</span></div>'
            f'<div><b data-count="{len(P)}">{len(P)}</b><span>Players</span></div>'
            f'<div><b data-count="{len(days)}">{len(days)}</b><span>Session days</span></div>'
            f'<div><b data-count="{pts}">{num(pts)}</b><span>Points played</span></div></div>'
            f'<button type="button" class="ar-topcard" data-goto-player="{SLUG[top]}" style="--pc:{col(top)}">'
            f'<span class="ar-topcard-ph"><img data-ph-portrait="{escape(top)}" alt=""></span>'
            f'<span class="ar-topcard-tx"><span class="ar-tag">{icon("crown")}Current #1</span>'
            f'<span class="ar-topcard-n">{escape(top)}</span>'
            f'<span class="ar-topcard-s">{p0["record"]} · {p0["win_pct"] * 100:.1f}% · {p0["titles"]} titles</span>'
            f'<span class="ar-topcard-r"><b>{sg(e0["adj"])}</b> adjusted · Elo {num(e0["elo"])}</span></span></button></div>'
            f'<div class="ar-ctas"><a class="ar-cta" href="#dashboard" data-scroll="dashboard">Explore dashboard {icon("arrow")}</a>'
            f'<a class="ar-cta ghost" href="#leaderboard" data-view="leaderboard">View leaderboard</a></div></div>'
            f'<a class="ar-scroll" href="#dashboard" data-scroll="dashboard" aria-label="Scroll to dashboard"><span class="ar-mouse"><i></i></span><span>Scroll</span></a>'
            f'</section>')

    # ---------------------------------------------------------------- dashboard
    lede = page[page.find('<p class="bx-lede">'):]
    lede = lede[:lede.find('</p>') + 4].replace('class="bx-lede"', 'class="ar-story"')
    share = ''.join(f'<i style="--w:{PL[p]["W"] / wins * 100:.2f}%;--pc:{col(p)}" title="{escape(p)} {PL[p]["W"]} wins"></i>' for p in order)
    stack = ''.join(f'<img class="ar-stack-i" data-ph-avatar="{escape(p)}" alt="{escape(p)}" title="{escape(p)}" style="--pc:{col(p)}">' for p in order)
    stg = ''.join(f'<i style="--w:{st[s] / N * 100:.2f}%" class="s{i}" title="{s}: {st[s]}"></i>' for i, s in enumerate(('Qualifier', 'Eliminator', 'Final')))
    ring = lambda v: f'<svg class="ar-ring" viewBox="0 0 44 44" aria-hidden="true"><circle cx="22" cy="22" r="18"/><circle class="on" cx="22" cy="22" r="18" pathLength="100" style="--v:{v:.1f}"/></svg>'
    le3p = float(F['g.le3p'].rstrip('%')); acc = float(F['m.acc'].rstrip('%'))
    tiles = [
        _stat_tile('matches', 'Total matches', N, f'{st["Qualifier"]} qualifier · {st["Eliminator"]} eliminator · {st["Final"]} final', f'<div class="ar-seg">{stg}</div>', N),
        _stat_tile('players', 'Total players', len(P), f'{len(days)} session days over {weeks} weeks', f'<div class="ar-stack">{stack}</div>', len(P), accent='cyan'),
        _stat_tile('wins', 'Total wins', num(wins), 'Player wins: two winners in every doubles match', f'<div class="ar-share">{share}</div>', wins),
        _stat_tile('titles', 'Total titles', titles, f'{titles} finals decided · {sum(PL[p]["titles"] for p in P)} player titles', '', titles, accent='cyan'),
        _stat_tile('best', 'Best win rate', f'{PL[best]["win_pct"] * 100:.1f}%', f'{escape(best)} · {PL[best]["record"]}', ring(PL[best]['win_pct'] * 100), round(PL[best]['win_pct'] * 100, 1), 'pct1'),
        (f'<button type="button" class="ar-stat ar-reveal ar-perf" data-goto-player="{SLUG[top]}" style="--pc:{col(top)}"><p class="ar-stat-l">Top performer</p>'
         f'<span class="ar-perf-ph"><img data-ph-avatar="{escape(top)}" alt=""></span><p class="ar-stat-v">{escape(top)}</p>'
         f'<p class="ar-stat-s">{sg(e0["adj"])} points per match above average · first in {e0["p_first"] * 100:.0f}% of resamples</p></button>'),
        _stat_tile('close', 'Decided by 3 or fewer', f'{le3p:.0f}%', f'{F["g.le3"]} of {N} matches', ring(le3p), le3p, 'pct0', 'cyan'),
        _stat_tile('acc', 'Winner predicted', f'{acc:.0f}%', f'out of sample · margin error {F["m.cvmae"]} points', ring(acc), acc, 'pct0'),
    ]
    dash_html = (f'<section class="ar-block" id="dashboard"><div class="ar-head"><p class="ar-eyebrow">Season control room</p>'
                 f'<h2 class="ar-h">Dashboard</h2></div>{lede}<div class="ar-stats">{"".join(tiles)}</div></section>')

    # ---------------------------------------------------------------- leaderboard
    cards = []
    for p in order:
        e, x = E[p], PL[p]
        form = ''.join(f'<i class="{"w" if w else "l"}"></i>' for w in _last(T, p, 5))
        bd = ''.join(f'<span class="ar-bdg b-{k}" title="{escape(B[k]["why"])}">{icon(B[k]["icon"])}{B[k]["label"]}</span>' for k in pbadge[p])
        champ = p == top
        RING = '<span class="ar-ring-b" aria-hidden="true"></span>'
        cards.append(
            f'<button type="button" class="ar-card ar-reveal{" is-champ" if champ else ""}" data-goto-player="{SLUG[p]}" style="--pc:{col(p)}" '
            f'data-s-rank="{e["adj_rank"]}" data-s-win="{x["win_pct"]}" data-s-titles="{x["titles"]}" data-s-form="{e["recent_adj"]}" data-s-elo="{e["elo"]}" '
            f'aria-label="{escape(p)}, rank {e["adj_rank"]}: open profile">'
            f'{RING if champ else ""}<span class="ar-card-ph"><img data-ph-portrait="{escape(p)}" alt=""></span>'
            f'<span class="ar-card-top"><span class="ar-rank">{"" if not champ else icon("crown")}<b>#{e["adj_rank"]}</b></span>'
            f'<span class="ar-ovr"><b>{num(e["elo"])}</b><small>Elo</small></span></span>'
            f'<span class="ar-card-body">'
            f'<span class="ar-card-n">{escape(p)}</span>'
            f'<span class="ar-bdgs">{bd}</span>'
            f'<span class="ar-card-g">'
            f'<span><b>{x["win_pct"] * 100:.1f}%</b><small>Win rate</small></span>'
            f'<span><b>{x["record"]}</b><small>W–L</small></span>'
            f'<span><b>{x["titles"]}</b><small>Titles</small></span>'
            f'<span><b>{sg(e["adj"])}</b><small>Adjusted</small></span></span>'
            f'<span class="ar-bar" title="Win rate {x["win_pct"] * 100:.1f}%"><i style="--v:{x["win_pct"] * 100:.1f}%"></i></span>'
            f'<span class="ar-card-f"><span class="ar-form" aria-label="Last five results">{form}</span>'
            f'<span class="ar-trend t-{CM[p]["trend"].split()[0].lower().strip(",")}">{escape(CM[p]["trend"])}</span></span>'
            f'</span></button>')
    sorts = [('rank', 'Rank'), ('win', 'Win %'), ('titles', 'Titles'), ('form', 'Form'), ('elo', 'Elo')]
    lb_html = (f'<section class="ar-block" id="board"><div class="ar-head ar-head-row"><div><p class="ar-eyebrow">Ranked by adjusted strength</p>'
               f'<h2 class="ar-h">Leaderboard</h2></div>'
               f'<div class="ar-seg-ctl" role="group" aria-label="Sort leaderboard">'
               + ''.join(f'<button type="button" data-sort="{k}" aria-pressed="{"true" if k == "rank" else "false"}">{l}</button>' for k, l in sorts)
               + f'</div></div><div class="ar-lb">{"".join(cards)}</div>'
               f'<p class="ar-note">Rank, adjusted value and form come from the season model; Elo is the margin-weighted rating; the bar is win rate; the strip is the last five results. Tap a card for the full profile.</p></section>')

    # ---------------------------------------------------------------- awards
    aw = []
    for k, b in B.items():
        ph = f'<img class="ar-aw-i" data-ph-avatar="{escape(b["player"])}" alt="">'
        if b.get('player2'):
            ph = f'<span class="ar-aw-pair">{ph}<img class="ar-aw-i" data-ph-avatar="{escape(b["player2"])}" alt=""></span>'
        who = escape(b['player']) + (f' + {escape(b["player2"])}' if b.get('player2') else '')
        aw.append(f'<button type="button" class="ar-aw ar-reveal a-{k}" data-goto-player="{SLUG[b["player"]]}" style="--pc:{col(b["player"])}">'
                  f'<span class="ar-aw-ic">{icon(b["icon"])}</span><span class="ar-aw-l">{b["label"]}</span>{ph}'
                  f'<span class="ar-aw-n">{who}</span><span class="ar-aw-v"><b>{b["stat"]}</b> {b["unit"]}</span>'
                  f'<span class="ar-aw-why">{escape(b["why"])}</span></button>')
    aw_html = (f'<section class="ar-block" id="awards"><div class="ar-head"><p class="ar-eyebrow">Achievements unlocked</p>'
               f'<h2 class="ar-h">Season awards</h2></div><div class="ar-awards">{"".join(aw)}</div></section>')

    old = '<section class="bx-sec" id="summary" data-panel="summary">\n'
    assert page.count(old) == 1
    page = page.replace(old, old + dash_html + lb_html + aw_html, 1)

    # ---------------------------------------------------------------- player profiles
    for p in P:
        s = SLUG[p]
        a0 = page.find(f'<article class="bx-pr" id="p-{s}"'); a1 = page.find('</article>', a0)
        art = page[a0:a1]
        # identity stats in the header
        fx = lambda k: f'<b data-draw="f" data-source="facts" data-field="text" data-where="key={s}.{k}">—</b>'
        bd = ''.join(f'<span class="ar-bdg b-{k}" title="{escape(B[k]["why"])}">{icon(B[k]["icon"])}{B[k]["label"]}</span>' for k in pbadge[p])
        idstats = (f'<div class="ar-bdgs">{bd}</div><div class="ar-id">'
                   f'<span><small>Rank</small><b>#</b>{fx("rank")}</span><span><small>Win rate</small>{fx("pct")}</span>'
                   f'<span><small>Matches</small>{fx("P")}</span><span><small>Won–lost</small>{fx("rec")}</span>'
                   f'<span><small>Titles</small>{fx("titles")}</span><span><small>Elo rating</small>{fx("elo")}</span>'
                   f'<span><small>Adjusted</small>{fx("adj")}</span></div>'
                   f'<div class="ar-id-form"><small>Recent form · last 10</small><span class="ar-form10" data-ar-form="{escape(p)}"></span></div>')
        i = art.find('<p class="bx-pr-sub">'); j = art.find('</p>', i) + 4
        art = art[:j] + idstats + art[j:]
        # recent form, match history and weekly progression after the verdict
        v1 = art.find('</p>', art.find('<p class="bx-pr-verdict">')) + 4
        extra = (f'<div class="bx-grid ar-prof">'
                 f'<div class="bx-card ar-reveal"><div class="bx-card-head"><h3>Weekly progression</h3><span class="bx-tag bx-tag-e">Estimate</span></div>'
                 f'<p class="bx-note">Adjusted margin per match each week, partners and opponents taken out. Record above each bar.</p>'
                 f'<div class="ar-wk" data-ar-weekly="{escape(p)}"></div></div>'
                 f'<div class="bx-card ar-reveal"><div class="bx-card-head"><h3>Match history</h3><span class="bx-tag bx-tag-m">Measured</span></div>'
                 f'<p class="bx-note">Every match {escape(p)} played, newest first. Score is {escape(p)}’s side first.</p>'
                 f'<div class="ar-mh" data-ar-history="{escape(p)}"></div></div></div>')
        art = art[:v1] + extra + art[v1:]
        # strengths, weaknesses and training, copied from the Strengths and targets section
        k0 = page.find(f'<div class="bx-card" id="sw-{s}">')
        depth, k = 0, k0
        while True:
            o = page.find('<div', k); c = page.find('</div>', k)
            if o != -1 and o < c:
                depth += 1; k = o + 4
            else:
                depth -= 1; k = c + 6
                if depth == 0:
                    break
        sw = page[k0:k].replace(f'id="sw-{s}"', f'id="swp-{s}"', 1).replace(f'<h3>{p}</h3>', '<h3>Strengths, weaknesses and training</h3>', 1)
        sw = sw.replace('class="bx-card"', 'class="bx-card ar-sw ar-reveal"', 1)
        pn = art.find('<div class="bx-pn"')
        art = art[:pn] + sw + art[pn:]
        page = page[:a0] + art + page[a1:]

    cfg = dict(views=VIEWS, nav=[v for v, _ in NAV], slug=SLUG, players=P)
    return nav + hero + page, cfg


def arena_js(cfg):
    return '(() => {\nconst CFG = ' + json.dumps(cfg) + ';\n' + ARENA_JS + '\n})();'


ARENA_JS = r"""
const root = document.documentElement;
root.classList.add('ar-js');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const rows = (n) => { try { return (dash.data(n).data) || []; } catch (e) { return []; } };
const hero = $('#overview');
const NAVH = () => ($('#ar-nav')?.offsetHeight || 64) + 10;
const nf = new Intl.NumberFormat('en-US');

/* ---------------- views ---------------- */
const viewOfPanel = (pid) => {
  for (const v of CFG.nav) if (v !== 'overview' && v !== 'leaderboard' && CFG.views[v].includes(pid)) return v;
  return 'overview';
};
let current = null;
const ind = $('.ar-ind');
const setActive = (v) => {
  $$('.ar-link').forEach((a) => { const on = a.dataset.view === v; a.classList.toggle('is-on', on); if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
  const a = $(`.ar-links .ar-link[data-view="${v}"]`);
  if (a && ind) { ind.style.setProperty('--x', a.offsetLeft + 'px'); ind.style.setProperty('--w', a.offsetWidth + 'px'); ind.classList.add('on'); }
};
let settleT = [];
const scrollToEl = (el, smooth = true) => {
  if (!el) return;
  const go = (sm) => {
    const y = el === hero ? 0 : el.getBoundingClientRect().top + scrollY - NAVH();
    scrollTo({ top: Math.max(0, y), behavior: sm && !reduce ? 'smooth' : 'auto' });
  };
  go(smooth);
  // tables and charts draw just after a view opens and can push the target down: correct once they settle
  settleT.forEach(clearTimeout);
  settleT = [450, 1000, 1800].map((ms) => setTimeout(() => {
    if (el === hero) return;
    if (Math.abs(el.getBoundingClientRect().top - NAVH()) > 48) go(false);
  }, ms));
};
addEventListener('wheel', () => settleT.forEach(clearTimeout), { passive: true });
addEventListener('touchstart', () => settleT.forEach(clearTimeout), { passive: true });
const show = (v, opts = {}) => {
  if (!CFG.views[v]) v = 'overview';
  const panels = CFG.views[v];
  const changed = current === null || CFG.views[current].join() !== panels.join();
  $$('[data-panel]').forEach((s) => { s.hidden = !panels.includes(s.dataset.panel); });
  if (hero) hero.hidden = !(v === 'overview' || v === 'leaderboard');
  current = v; setActive(v); closeMenu();
  if (changed && !reduce) { const main = $('.bx'); main.classList.remove('ar-swap'); void main.offsetWidth; main.classList.add('ar-swap'); }
  if (opts.scroll !== false) {
    const target = v === 'overview' ? hero : (v === 'leaderboard' ? $('#board') : $(`[data-panel="${panels[0]}"]`));
    // a new set of panels animates in, so jump straight there; scroll smoothly only within the same view
    scrollToEl(opts.el || target, opts.smooth !== false && !changed);
  }
  try { history.replaceState(null, '', '#' + (opts.hash || v)); } catch (e) { /* file:// */ }
  setTimeout(observeAll, 0);
};
window.arenaShow = (v, scroll) => show(v, { scroll });
document.addEventListener('click', (ev) => {
  const a = ev.target.closest('[data-view]');
  if (a) { ev.preventDefault(); show(a.dataset.view); return; }
  const s = ev.target.closest('[data-scroll]');
  if (s) { ev.preventDefault(); scrollToEl(document.getElementById(s.dataset.scroll)); return; }
}, true);
// links inside the report (e.g. to a player's strengths card) keep the grouped view
window.addEventListener('click', (ev) => {
  const j = ev.target.closest('.bx-jump');
  if (!j) return;
  ev.preventDefault(); ev.stopPropagation();
  const el = document.getElementById(j.getAttribute('href').slice(1));
  const pid = el?.closest('[data-panel]')?.dataset.panel;
  if (el && pid) show(viewOfPanel(pid), { el, hash: el.id });
}, true);
// player cards anywhere open the profile
window.addEventListener('click', (ev) => {
  const c = ev.target.closest('[data-goto-player]');
  if (!c) return;
  ev.preventDefault(); ev.stopPropagation();
  const slug = c.dataset.gotoPlayer;
  show('players', { scroll: false, hash: 'p-' + slug });
  $(`.bx-pick-b[data-player="${slug}"]`)?.click();
  scrollToEl(document.getElementById('p-' + slug), false);
}, true);

/* scroll spy between Overview and Leaderboard, nav shadow */
const onScroll = () => {
  $('#ar-nav')?.classList.toggle('is-stuck', scrollY > 10);
  if (current === 'overview' || current === 'leaderboard') {
    const lb = $('#board'); if (!lb) return;
    const v = lb.getBoundingClientRect().top < innerHeight * 0.45 && $('#awards').getBoundingClientRect().bottom > NAVH() ? 'leaderboard' : 'overview';
    if (v !== current) { current = v; setActive(v); }
  }
};
addEventListener('scroll', onScroll, { passive: true });
addEventListener('resize', () => setActive(current), { passive: true });

/* mobile menu */
const burger = $('.ar-burger'); const menu = $('#ar-menu');
function closeMenu() { if (!menu || menu.hidden) return; menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); setTimeout(() => { if (!menu.classList.contains('open')) menu.hidden = true; }, 260); }
burger?.addEventListener('click', () => {
  if (menu.hidden) { menu.hidden = false; setTimeout(() => menu.classList.add('open'), 16); burger.setAttribute('aria-expanded', 'true'); }
  else closeMenu();
});
addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

/* ---------------- reveal, counters, chart wipe ---------------- */
const fmtCount = (v, f) => f === 'pct1' ? v.toFixed(1) + '%' : (f === 'pct0' ? Math.round(v) + '%' : nf.format(Math.round(v)));
const count = (el) => {
  const target = parseFloat(el.dataset.count); const f = el.dataset.fmt || 'int';
  if (reduce || !isFinite(target)) { el.textContent = fmtCount(target, f); return; }
  const t0 = performance.now(); const dur = 1300;
  const step = (t) => { const p = Math.min(1, (t - t0) / dur); const e = 1 - Math.pow(1 - p, 4); el.textContent = fmtCount(target * e, f); if (p < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
};
const pending = new Set();
const reveal = (el) => {
  if (!pending.has(el)) return;
  pending.delete(el); io?.unobserve(el); el.classList.add('is-in');
  if (el.classList.contains('bx-chart')) setTimeout(() => el.classList.add('ar-wiped'), 1500 + (parseInt(el.style.getPropertyValue('--d')) || 0));
  $$('[data-count]', el).forEach(count); if (el.dataset.count) count(el);
};
const io = 'IntersectionObserver' in window ? new IntersectionObserver((es) => {
  es.forEach((e) => { if (e.isIntersecting) reveal(e.target); });
}, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }) : null;
// fallback that needs no rendering callbacks: reveal whatever is on screen after scrolling or a view change
let chkT = null;
const checkPending = () => {
  clearTimeout(chkT);
  chkT = setTimeout(() => {
    pending.forEach((el) => {
      if (el.closest('[hidden]')) return;
      const r = el.getBoundingClientRect();
      if (r.top < innerHeight * 0.96 && r.bottom > 0) reveal(el);
    });
  }, 120);
};
addEventListener('scroll', checkPending, { passive: true });
// some browsers pause scroll events and observers in background tabs: a slow timer keeps reveals honest
setInterval(() => { if (pending.size) checkPending(); }, 700);
// player reports and sections shown later (player picker, prev/next, links) get registered too
let moT = null;
new MutationObserver(() => { clearTimeout(moT); moT = setTimeout(observeAll, 40); })
  .observe(document.body, { subtree: true, attributes: true, attributeFilter: ['hidden'] });
const seen = new WeakSet();
function observeAll() {
  const els = $$('.ar-reveal, .bx-card, .bx-chart, .bx-findings li, .ar-hero-stats, .bx-kpi');
  let k = 0;
  els.forEach((el) => {
    if (seen.has(el) || el.closest('[hidden]')) return;
    seen.add(el);
    if (reduce) { el.classList.add('is-in'); $$('[data-count]', el).forEach(count); return; }
    el.style.setProperty('--d', Math.min(k++ % 8, 7) * 60 + 'ms');
    pending.add(el); io?.observe(el);
  });
  checkPending();
}

/* ---------------- leaderboard sorting (FLIP) ---------------- */
const lb = $('.ar-lb');
$$('.ar-seg-ctl button').forEach((b) => b.addEventListener('click', () => {
  $$('.ar-seg-ctl button').forEach((x) => x.setAttribute('aria-pressed', x === b ? 'true' : 'false'));
  const k = b.dataset.sort; const cards = $$('.ar-card', lb);
  const first = new Map(cards.map((c) => [c, c.getBoundingClientRect()]));
  const champ = cards.find((c) => c.classList.contains('is-champ'));
  const rest = cards.filter((c) => c !== champ).sort((a, c) => {
    const va = parseFloat(a.dataset['s' + k[0].toUpperCase() + k.slice(1)]); const vc = parseFloat(c.dataset['s' + k[0].toUpperCase() + k.slice(1)]);
    return k === 'rank' ? va - vc : vc - va;
  });
  [champ, ...rest].forEach((c) => lb.appendChild(c));
  if (reduce) return;
  cards.forEach((c) => {
    const a = first.get(c); const z = c.getBoundingClientRect();
    const dx = a.left - z.left; const dy = a.top - z.top;
    if (dx || dy) c.animate([{ transform: `translate(${dx}px, ${dy}px)` }, { transform: 'none' }], { duration: 520, easing: 'cubic-bezier(.2,.8,.2,1)' });
  });
}));

/* ---------------- player profile widgets (from the embedded match data) ---------------- */
const MATCHES = rows('matches'); const WEEKLY = rows('weekly');
const sideOf = (m, p) => (m.team_a.split(' + ').includes(p) ? 'a' : (m.team_b.split(' + ').includes(p) ? 'b' : null));
const mine = (p) => MATCHES.filter((m) => sideOf(m, p));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
$$('[data-ar-form]').forEach((el) => {
  const p = el.dataset.arForm; const ms = mine(p).slice(-10);
  el.innerHTML = ms.map((m) => { const s = sideOf(m, p); const w = m.winner === (s === 'a' ? m.team_a : m.team_b);
    const sc = s === 'a' ? `${m.score_a}–${m.score_b}` : `${m.score_b}–${m.score_a}`;
    return `<i class="${w ? 'w' : 'l'}" title="${esc(m.day)} ${esc(m.label)}: ${w ? 'won' : 'lost'} ${sc}">${w ? 'W' : 'L'}</i>`; }).join('');
});
$$('[data-ar-history]').forEach((el) => {
  const p = el.dataset.arHistory; const ms = mine(p).reverse();
  const row = (m) => {
    const s = sideOf(m, p); const mate = (s === 'a' ? m.team_a : m.team_b).split(' + ').find((x) => x !== p);
    const opp = s === 'a' ? m.team_b : m.team_a; const w = m.winner === (s === 'a' ? m.team_a : m.team_b);
    const sc = s === 'a' ? `${m.score_a}–${m.score_b}` : `${m.score_b}–${m.score_a}`;
    return `<tr><td>${esc(m.day)}</td><td><span class="ar-stage st-${m.stage[0]}">${esc(m.stage === 'Qualifier' ? m.label : m.stage)}</span></td>`
      + `<td>${esc(mate)}</td><td>${esc(opp)}</td><td class="num">${sc}</td><td><span class="ar-res ${w ? 'w' : 'l'}">${w ? 'WIN' : 'LOSS'}</span></td></tr>`;
  };
  const head = '<thead><tr><th>Day</th><th>Match</th><th>Partner</th><th>Opponents</th><th class="num">Score</th><th>Result</th></tr></thead>';
  el.innerHTML = `<div class="bx-tw ar-mh-tw"><table class="bx-table ar-mh-t">${head}<tbody>${ms.slice(0, 10).map(row).join('')}</tbody><tbody class="ar-more" hidden>${ms.slice(10).map(row).join('')}</tbody></table></div>`
    + (ms.length > 10 ? `<button type="button" class="ar-btn ar-mh-more" aria-expanded="false">Show all ${ms.length} matches</button>` : '');
  el.querySelector('.ar-mh-more')?.addEventListener('click', (e) => {
    const more = el.querySelector('.ar-more'); const open = more.hidden; more.hidden = !open;
    e.currentTarget.setAttribute('aria-expanded', String(open)); e.currentTarget.textContent = open ? 'Show the latest 10' : `Show all ${ms.length} matches`;
  });
});
$$('[data-ar-weekly]').forEach((el) => {
  const p = el.dataset.arWeekly; const ws = WEEKLY.filter((w) => w.player === p).sort((a, b) => a.week - b.week);
  if (!ws.length) return;
  const max = Math.max(1, ...ws.map((w) => Math.abs(w.adj)));
  const W = 560; const H = 250; const top = 40; const bot = 46; const mid = top + (H - top - bot) / 2; const half = (H - top - bot) / 2;
  const bw = W / ws.length;
  const bars = ws.map((w, i) => {
    const h = Math.max(2, Math.abs(w.adj) / max * half); const x = i * bw + bw * 0.2; const y = w.adj >= 0 ? mid - h : mid;
    const lab = (w.adj >= 0 ? '+' : '−') + Math.abs(w.adj).toFixed(2);
    return `<g class="${w.adj >= 0 ? 'up' : 'dn'}" style="--i:${i}"><title>Week ${w.week}: ${w.record}, adjusted ${lab} per match</title>`
      + `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(bw * 0.6).toFixed(1)}" height="${h.toFixed(1)}" rx="6"/>`
      + `<text class="v" x="${(x + bw * 0.3).toFixed(1)}" y="${(w.adj >= 0 ? y - 7 : y + h + 15).toFixed(1)}">${lab}</text>`
      + `<text class="rec" x="${(x + bw * 0.3).toFixed(1)}" y="16">${w.record}</text>`
      + `<text class="wk" x="${(x + bw * 0.3).toFixed(1)}" y="${H - 6}">W${w.week}</text></g>`;
  }).join('');
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" class="ar-wk-svg" role="img" aria-label="Weekly adjusted performance for ${esc(p)}"><line x1="0" x2="${W}" y1="${mid}" y2="${mid}" class="zero"/>${bars}</svg>`;
});

/* ---------------- start ---------------- */
const h = location.hash.slice(1);
const start = () => {
  if (CFG.views[h]) { show(h, { scroll: h !== 'overview', smooth: false }); return; }
  const el = h ? document.getElementById(h) : null;
  const pid = el?.closest('[data-panel]')?.dataset.panel;
  if (el && pid) {
    const art = el.closest('.bx-pr');
    show(viewOfPanel(pid), { el, hash: h, smooth: false });
    if (art) $(`.bx-pick-b[data-player="${art.dataset.player}"]`)?.click();
    return;
  }
  show('overview', { scroll: false });
};
start();
observeAll();
setTimeout(() => root.classList.add('ar-ready'), 30);
"""
