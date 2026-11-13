XLSX = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'badminton-scores.xlsx')
import json, os, math
import numpy as np
from html import escape

T = json.load(open('tables.json'))
md = json.load(open('model.json'))
rd = json.load(open('report_data.json'))
M, days = md['M'], md['days']
P = ['Anto', 'Jothi Sai', 'John', 'Pawan', 'Dinesh', 'Pratap', 'Bhanu']
SLUG = {'Anto': 'anto', 'Jothi Sai': 'jothi', 'John': 'john', 'Pawan': 'pawan', 'Dinesh': 'dinesh', 'Pratap': 'pratap', 'Bhanu': 'bhanu'}
PL = {x['player']: x for x in T['players']}
E = {x['player']: x for x in T['estimates']}
PR = {x['player']: x for x in T['pressure']}
WK = {}
for w in T['weekly']:
    WK.setdefault(w['player'], []).append(w)
PART = {}
for x in T['partners']:
    PART.setdefault(x['player'], []).append(x)
OPP = {}
for x in T['opponents']:
    OPP.setdefault(x['player'], []).append(x)
BAND = {x['key']: x for x in T['bands']}
PAIRS = {x['key']: x for x in T['pairs']}
OUT = 'dash/data'

MINUS = '−'


def pct(x, d=1):
    return f'{x * 100:.{d}f}%'


def sg(x, d=2):
    return f'{x:+.{d}f}'.replace('-', MINUS)


def num(x, d=0):
    return (f'{x:,.{d}f}' if d else f'{int(round(x)):,}').replace('-', MINUS)


facts = {}


def F(key, text, kind, basis):
    text = str(text)
    if key in facts and facts[key]['text'] != text:
        raise ValueError(f'fact {key} redefined: {facts[key]["text"]} vs {text}')
    facts[key] = dict(key=key, text=text, kind=kind, basis=basis)
    return f'<b data-draw="f" data-source="facts" data-field="text" data-where="key={key}">—</b>'


def fm(key, text, basis):
    return F(key, text, 'measured', basis)


def fe(key, text, basis):
    return F(key, text, 'estimate', basis)


def K(name):
    return f'<b data-draw="k" data-k="{name}">—</b>'


def V(src, field, where, fmt):
    return f'<span class="n" data-draw="v" data-source="{src}" data-field="{field}" data-where="{escape(where)}" data-fmt="{fmt}">—</span>'


def tag(kind):
    return f'<span class="bx-tag bx-tag-{kind}">{"Measured" if kind == "m" else "Estimate"}</span>'


# ---------------------------------------------------------------- global facts
N = len(M)
nd = len(days)
NWK = len({m['wk'] for m in M})
H1N = nd // 2
SH = lambda d: ('W1 ' + d.replace('Day ', 'D')) if not d.startswith('W') else d.replace('Day ', 'D')
import openpyxl as _ox
_am = _ox.load_workbook(XLSX, data_only=True)['All matches']
AM_DAYS = {r[0] for r in _am.iter_rows(min_row=4, values_only=True) if isinstance(r[0], str) and 'Day' in r[0] and isinstance(r[5], (int, float))}
N_AM = sum(1 for r in _am.iter_rows(min_row=4, values_only=True) if isinstance(r[0], str) and 'Day' in r[0] and isinstance(r[5], (int, float)))
NOT_IN_AM = [d for d in days if d not in AM_DAYS]
EXTRA = json.load(open('parsed.json', encoding='utf-8')).get('extra_days', [])
IN_WB_NOT_AM = [d for d in NOT_IN_AM if d not in EXTRA]
def final_streak(p):
    n = 0
    for m in reversed([m for m in M if m['stage'] == 'Final' and (p in m['A'] or p in m['B'])]):
        if (m['sa'] > m['sb']) == (p in m['A']): n += 1
        else: break
    return n
def day_rec(p, day):
    w = l = 0
    for m in M:
        if m['day'] != day: continue
        if p in m['A']: w += m['sa'] > m['sb']; l += m['sa'] < m['sb']
        elif p in m['B']: w += m['sb'] > m['sa']; l += m['sb'] < m['sa']
    return f'{w}\u2013{l}'
LAST = days[-1]
def last_champs():
    m = [m for m in M if m['day'] == LAST and m['stage'] == 'Final']
    if not m: return None
    m = m[0]; return m['A'] if m['sa'] > m['sb'] else m['B']
allm = [abs(m['sa'] - m['sb']) for m in M]
le3 = sum(x <= 3 for x in allm); le5 = sum(x <= 5 for x in allm)
deuce = sum(max(m['sa'], m['sb']) > 21 for m in M)
stage_mean = {st: np.mean([abs(m['sa'] - m['sb']) for m in M if m['stage'] == st]) for st in ('Qualifier', 'Eliminator', 'Final')}
stage_n = {st: sum(1 for m in M if m['stage'] == st) for st in ('Qualifier', 'Eliminator', 'Final')}
g = dict(
    n=fm('g.n', num(N), f'Matches with both scores entered: the day tabs plus {len(EXTRA)} day(s) from extra-days.json. The All matches tab lists {N_AM} of them.'),
    days=fm('g.days', num(nd), 'Session days with scores: five in week 1, five in week 2, two in week 3, three in week 4, two in week 5, five in week 6, three in week 7, one in week 8 so far.'),
    weeks=fm('g.weeks', num(NWK), 'Week labels in the day names (Day 1–5 is week 1, W2–W8 follow).'),
    players=fm('g.players', num(7), 'Distinct names across all matches.'),
    pm=fm('g.pm', num(N * 4), 'Player-matches: four players in every match.'),
    pts=fm('g.pts', num(sum(m['sa'] + m['sb'] for m in M)), 'Total points scored in all matches.'),
    q=fm('g.q', num(stage_n['Qualifier']), 'Matches labelled Round 1–7.'),
    el=fm('g.el', num(stage_n['Eliminator']), 'Matches labelled Eliminator.'),
    fi=fm('g.fi', num(stage_n['Final']), 'Matches labelled Final; the Day 1 final is game 1 only.'),
    mm=fm('g.mm', f'{np.mean(allm):.1f}', 'Mean winning margin over all matches, in points.'),
    mq=fm('g.mq', f'{stage_mean["Qualifier"]:.1f}', 'Mean winning margin in qualifier rounds.'),
    me=fm('g.me', f'{stage_mean["Eliminator"]:.1f}', 'Mean winning margin in eliminators.'),
    mf=fm('g.mf', f'{stage_mean["Final"]:.1f}', 'Mean winning margin in finals.'),
    le3=fm('g.le3', num(le3), 'Matches won by three points or fewer.'),
    le3p=fm('g.le3p', pct(le3 / N, 0), 'Share of matches won by three points or fewer.'),
    le5=fm('g.le5', num(le5), 'Matches won by five points or fewer.'),
    le5p=fm('g.le5p', pct(le5 / N, 0), 'Share of matches won by five points or fewer.'),
    deuce=fm('g.deuce', num(deuce), 'Matches where the winner scored more than 21.'),
    wkrange=fm('g.wkrange', '1–5', 'Fewest and most session days in any one week (week 8 has one so far; weeks 3 and 5 have two; weeks 4 and 7 three; weeks 1, 2 and 6 five).'),
    half=fm('g.half', num(H1N), 'Session days in the first half of the season for the half-season comparison (W1 D1–' + SH(days[H1N - 1]) + ').'),
    half2=fm('g.half2', num(nd - H1N), 'Session days in the second half of the season (' + SH(days[H1N]) + '–' + SH(days[-1]) + ').'),
    other=fm('g.other', num(nd - 1), 'Days used to predict each held-out day.'),
    odd=fm('g.odd', '23–20', 'Score recorded in three matches that went past 21 with a three-point margin.'),
    oddn=fm('g.oddn', num(sum(1 for m in M if max(m['sa'], m['sb']) > 21 and abs(m['sa'] - m['sb']) != 2)), 'Matches past 21 that did not end on a two-point lead.'),
    d1=fm('g.d1', '21–19', 'Score of the only recorded game of the W1 D1 final.'),
    wbjs=fm('g.wbjs', '+2.96', 'Jothi Sai’s fitted value quoted in the Season tab note (row 19).'),
    wban=fm('g.wban', '+3.33', 'Anto’s fitted value quoted in the Season tab note (row 19).'),
    dnnow=fm('g.dnnow', num(md['season_sheet']['Dinesh']['now']), 'Season tab “Rating now” for Dinesh.'),
    dnnote=fm('g.dnnote', '3', 'Dinesh’s rating as listed in the Season tab note (row 18).'),
    jsnow=fm('g.jsnow', num(md['season_sheet']['Jothi Sai']['now']), 'Season tab “Rating now” for Jothi Sai.'),
    jsnote=fm('g.jsnote', '5', 'Jothi Sai’s rating after the latest refit, per the Season tab note (row 18).'),
    wbscale=fm('g.wbscale', '1–5', 'Lowest and highest workbook rating used on court.'),
    ciw=fe('g.ciw', f"±{min((E[p]['adj_hi'] - E[p]['adj_lo']) / 2 for p in P):.1f}–{max((E[p]['adj_hi'] - E[p]['adj_lo']) / 2 for p in P):.1f}", 'Smallest and largest half-width of the players’ 90% intervals.'),
)
meta = rd['meta']
cvl = md['cvres'][str(md['best_lam'])]
gm = dict(
    sigma=fe('m.sigma', f'{md["sigma"]:.1f}', 'Standard deviation of the match margin left unexplained by the season model.'),
    cvmae=fe('m.cvmae', f'{cvl[0]:.1f}', f'Mean absolute error of predicted margins when each day is predicted from the other {nd - 1} days.'),
    cvrmse=fe('m.cvrmse', f'{cvl[1]:.1f}', 'Root-mean-square error of the same out-of-sample predictions.'),
    base=fe('m.base', f'{md["base_mae"]:.1f}', 'Mean absolute error of predicting every match as level (the average winning margin).'),
    acc=fe('m.acc', pct(cvl[2], 0), 'Share of matches where the out-of-sample predicted winner won.'),
    r2=fe('m.r2', pct(1 - (cvl[1] / md['base_rmse']) ** 2, 0), 'Share of match-margin variance explained out of sample: 1 − (model RMSE ÷ no-model RMSE)².'),
    insmae=fe('m.insmae', f'{md["insample_mae"]:.1f}', 'Mean absolute error when the model is scored on the matches it was fitted to.'),
    lam=fe('m.lam', num(md['best_lam']), 'Ridge penalty chosen by leave-one-day-out cross-validation.'),
    elo_acc=fe('m.eloacc', pct(md['elo_check'][1], 0), 'Share of matches from W1 D4 on where the Elo favourite won, using ratings from before the match.'),
    elo_brier=fe('m.elobrier', f'{md["elo_check"][0]:.3f}', 'Brier score of Elo pre-match win probabilities from W1 D4 on (0.25 is a coin flip).'),
)


def sname(p):
    return p.split()[0] if p != 'Jothi Sai' else 'Jothi Sai'


# ---------------------------------------------------------------- per-player facts
def pf(p, k, text, basis, kind='measured'):
    return F(f'{SLUG[p]}.{k}', text, kind, basis)


def best_worst_week(p):
    ws = [w for w in WK[p] if w['P'] >= 8]
    b = max(ws, key=lambda w: w['adj']); wst = min(ws, key=lambda w: w['adj'])
    return b, wst


def partner_rows(p, minn=10):
    return [x for x in PART[p] if x['P'] >= minn]


def opp_rows(p, minn=15):
    return [x for x in OPP[p] if x['P'] >= minn]


def wb_path(p):
    h = md['wbrating'][p]
    vals = [x for x in h if x is not None]
    return vals[0], vals[-1], min(vals), max(vals)


def finals_in_week(p, wk):
    w = l = 0
    for m in M:
        if m['stage'] == 'Final' and m['wk'] == wk:
            if p in m['A']:
                w += m['sa'] > m['sb']; l += m['sa'] < m['sb']
            elif p in m['B']:
                w += m['sb'] > m['sa']; l += m['sb'] < m['sa']
    return w, l


def streak_span(p, want):
    seq = []
    for m in M:
        if p in m['A']:
            seq.append((m['day'], m['sa'] > m['sb']))
        elif p in m['B']:
            seq.append((m['day'], m['sb'] > m['sa']))
    best = (0, None, None); cur = 0; start = None; prev = None
    for day, w in seq:
        if w == prev:
            cur += 1
        else:
            cur = 1; start = day
        prev = w
        if w == want and cur > best[0]:
            best = (cur, start, day)
    sh = lambda d: ('W1 ' + d.replace('Day ', 'D')) if not d.startswith('W') else d.replace('Day ', 'D')
    return best[0], sh(best[1]), sh(best[2])


def base_facts(p):
    x = PL[p]; e = E[p]; r = PR[p]
    d = {}
    d['days'] = pf(p, 'days', num(x['days']), 'Day tabs on which the player appears in at least one match.')
    d['P'] = pf(p, 'P', num(x['P']), 'Matches played, qualifier and knockout.')
    d['rec'] = pf(p, 'rec', x['record'], 'Wins–losses in all matches.')
    d['pct'] = pf(p, 'pct', pct(x['win_pct']), 'Wins ÷ matches.')
    d['ci'] = pf(p, 'ci', f'{pct(x["win_lo"], 0)}–{pct(x["win_hi"], 0)}', 'Wilson 90% interval for the win rate, from the record alone.', 'estimate')
    d['diff'] = pf(p, 'diff', sg(x['diff'], 0), 'Points scored minus points conceded, all matches.')
    d['dpm'] = pf(p, 'dpm', sg(x['dpm']), 'Points difference ÷ matches played.')
    d['PF'] = pf(p, 'PF', num(x['PF']), 'Points scored, all matches.')
    d['PA'] = pf(p, 'PA', num(x['PA']), 'Points conceded, all matches.')
    d['aw'] = pf(p, 'aw', f'{x["avg_win_margin"]:.1f}', 'Average margin in matches won.')
    d['al'] = pf(p, 'al', f'{x["avg_loss_margin"]:.1f}', 'Average margin in matches lost.')
    d['q'] = pf(p, 'q', x['q_record'], 'Qualifier-round wins–losses.')
    d['qp'] = pf(p, 'qp', pct(x['q_pct']), 'Qualifier win rate.')
    d['qd'] = pf(p, 'qd', sg(x['q_dpm']), 'Qualifier points difference per match.')
    d['ko'] = pf(p, 'ko', x['ko_record'], 'Eliminator and final wins–losses.')
    d['kop'] = pf(p, 'kop', pct(x['ko_pct']), 'Knockout win rate.')
    d['kod'] = pf(p, 'kod', sg(x['ko_dpm']), 'Knockout points difference per match.')
    d['el'] = pf(p, 'el', x['el_record'], 'Eliminator wins–losses.')
    d['fin'] = pf(p, 'fin', x['fin_record'], 'Final wins–losses, including the Day 1 game-1 result.')
    d['finP'] = pf(p, 'finP', num(x['fin_P']), 'Finals played.')
    d['titles'] = pf(p, 'titles', num(x['titles']), 'Finals won, as the Season tab counts them (Day 1 game 1 counted as the title).')
    d['tconf'] = pf(p, 'tconf', num(x['titles_confirmed']), 'Finals won excluding the Day 1 final, whose deciding game was not recorded.')
    d['telim'] = pf(p, 'telim', num(x['titles_via_elim']), 'Titles won on days the player had to come through an eliminator.')
    d['top'] = pf(p, 'top', num(x['top_seeds']), 'Days finishing first in the qualifier table (diff, then points scored).')
    d['posd'] = pf(p, 'posd', num(x['pos_days']), 'Days with a positive points difference.')
    d['rrec'] = pf(p, 'rrec', x['recent_record'], 'Wins–losses in the player’s last 20 matches.')
    d['rdpm'] = pf(p, 'rdpm', sg(x['recent_dpm']), 'Points difference per match over the last 20 matches.')
    d['heavy'] = pf(p, 'heavy', num(x['heavy_losses']), 'Matches lost by eight points or more.')
    d['heavyp'] = pf(p, 'heavyp', pct(x['heavy_rate']), 'Matches lost by eight or more ÷ matches played.')
    d['big'] = pf(p, 'big', num(x['big_wins']), 'Matches won by eight points or more.')
    d['sw'] = pf(p, 'sw', num(x['best_win_streak']), 'Longest run of consecutive wins, in match order.')
    d['sl'] = pf(p, 'sl', num(x['worst_loss_streak']), 'Longest run of consecutive losses, in match order.')
    d['adj'] = pf(p, 'adj', sg(e['adj']), 'Season ridge estimate: points per match this player adds to a team’s margin versus an average player, after partners and opponents.', 'estimate')
    d['adjci'] = pf(p, 'adjci', f'{sg(e["adj_lo"])} to {sg(e["adj_hi"])}', '90% interval from resampling whole days 2,000 times.', 'estimate')
    d['radj'] = pf(p, 'radj', sg(e['recent_adj']), 'Same model with matches weighted by recency (half-life five session days).', 'estimate')
    d['h1'] = pf(p, 'h1', sg(e['h1']), f'Model fitted to W1 D1–{SH(days[H1N - 1])} only (first {H1N} days).', 'estimate')
    d['h2'] = pf(p, 'h2', sg(e['h2']), f'Model fitted to {SH(days[H1N])}–{SH(days[-1])} only (last {nd - H1N} days).', 'estimate')
    d['chg'] = pf(p, 'chg', sg(e['change']), 'Second-half estimate minus first-half estimate.', 'estimate')
    d['chgci'] = pf(p, 'chgci', f'{sg(e["change_lo"])} to {sg(e["change_hi"])}', '90% bootstrap interval for the half-season change.', 'estimate')
    d['elo'] = pf(p, 'elo', num(e['elo']), 'Final Elo (start 1500, team = mean of its two players, K 32 scaled by margin).', 'estimate')
    d['pfirst'] = pf(p, 'pfirst', pct(e['p_first'], 0), 'Share of bootstrap resamples in which this player has the highest season estimate.', 'estimate')
    d['ctx'] = pf(p, 'ctx', sg(e['draw_context']), 'Average of (partner estimate − both opponents’ estimates) over the player’s matches: what the draw alone was worth per match.', 'estimate')
    d['mate'] = pf(p, 'mate', sg(e['avg_partner']), 'Average season estimate of the player’s partners, match-weighted.', 'estimate')
    d['oppav'] = pf(p, 'oppav', sg(e['avg_opp']), 'Average combined season estimate of the opposing pair.', 'estimate')
    d['c3'] = pf(p, 'c3', r['c3_record'], 'Wins–losses in matches decided by three points or fewer.')
    d['c3e'] = pf(p, 'c3e', f'{r["c3_exp"]:.1f}', 'Expected close-game wins: for each close match, the chance of being on the winning side given it finished within three, from out-of-sample predicted margins.', 'estimate')
    d['c3v'] = pf(p, 'c3v', sg(r['c3_vs'], 1), 'Close-game wins minus expected close-game wins.', 'estimate')
    d['c3sd'] = pf(p, 'c3sd', f'{r["c3_sd"]:.1f}', 'One standard deviation of chance variation in close-game wins.', 'estimate')
    d['c5'] = pf(p, 'c5', r['c5_record'], 'Wins–losses in matches decided by five points or fewer.')
    d['deuce'] = pf(p, 'deuce', r['deuce_record'], 'Wins–losses in matches that went past 21.')
    d['koe'] = pf(p, 'koe', f'{r["ko_exp"]:.1f}', 'Expected knockout wins from out-of-sample predicted margins.', 'estimate')
    d['kov'] = pf(p, 'kov', sg(r['ko_vs'], 1), 'Knockout wins minus expected knockout wins.', 'estimate')
    d['fine'] = pf(p, 'fine', f'{r["fin_exp"]:.1f}', 'Expected final wins from out-of-sample predicted margins.', 'estimate')
    d['finv'] = pf(p, 'finv', sg(r['fin_vs'], 1), 'Final wins minus expected final wins.', 'estimate')
    d['clutch'] = pf(p, 'clutch', sg(r['clutch'], 1), 'Close-game wins above expectation plus knockout wins above expectation.', 'estimate')
    d['dsd'] = pf(p, 'dsd', f'{e["daily_sd"]:.1f}', 'Standard deviation of the player’s daily adjusted performance.', 'estimate')
    d['noise'] = pf(p, 'noise', f'{e["noise_sd"]:.1f}', 'Day-to-day standard deviation expected from match noise alone, given matches per day.', 'estimate')
    d['tr'] = pf(p, 'tr', sg(e['trend21'], 1), f'Fitted change in daily adjusted performance across the {nd - 1}-day span (least-squares slope × {nd - 1}).', 'estimate')
    d['trt'] = pf(p, 'trt', f'{e["trend_t"]:.1f}'.replace('-', MINUS), 'Slope ÷ its standard error; beyond ±2 is unlikely to be chance.', 'estimate')
    d['nw'] = pf(p, 'nw', pct(e['neutral_win_recent'], 0), 'Expected win rate with a random partner against random opponents, using the recency-weighted estimates.', 'estimate')
    d['upl'] = pf(p, 'upl', sg(e['uplift']), 'Average over the six partners of: partner’s points difference per match with this player minus without.', 'measured')
    d['early'] = pf(p, 'early', sg(e['early_adj']), 'Adjusted performance in qualifier rounds 1–3.', 'estimate')
    d['late'] = pf(p, 'late', sg(e['late_adj']), 'Adjusted performance in qualifier rounds 4–7.', 'estimate')
    s0, s1, lo, hi = wb_path(p)
    d['wb0'] = pf(p, 'wb0', num(s0), 'First rating the workbook shows for this player (Season tab, rating history).')
    d['wb1'] = pf(p, 'wb1', num(PL[p]['wb_now']), 'Season tab “Rating now”: the rating on the last day the player played.')
    d['wblo'] = pf(p, 'wblo', num(lo), 'Lowest workbook rating used on court.')
    d['wbhi'] = pf(p, 'wbhi', num(hi), 'Highest workbook rating used on court.')
    b, w = best_worst_week(p)
    d['bw'] = b; d['ww'] = w
    d['bwrec'] = pf(p, 'bwrec', b['record'], f'Week {b["week"]} wins–losses.')
    d['bwd'] = pf(p, 'bwd', sg(b['diff'], 0), f'Week {b["week"]} points difference.')
    d['bwa'] = pf(p, 'bwa', sg(b['adj']), f'Week {b["week"]} adjusted performance per match.', 'estimate')
    d['wwrec'] = pf(p, 'wwrec', w['record'], f'Week {w["week"]} wins–losses.')
    d['wwd'] = pf(p, 'wwd', sg(w['diff'], 0), f'Week {w["week"]} points difference.')
    d['wwa'] = pf(p, 'wwa', sg(w['adj']), f'Week {w["week"]} adjusted performance per match.', 'estimate')
    n, a, z = streak_span(p, True)
    d['swspan'] = pf(p, 'swspan', f'{a}–{z}' if a != z else a, 'Days the longest winning run started and ended.')
    n, a, z = streak_span(p, False)
    d['slspan'] = pf(p, 'slspan', f'{a}–{z}' if a != z else a, 'Days the longest losing run started and ended.')
    return d


PF_ = {p: base_facts(p) for p in P}


def partner_fact(p, q, field='rec'):
    x = next(r for r in PART[p] if r['partner'] == q)
    k = f'{SLUG[p]}.w.{SLUG[q]}'
    if field == 'rec':
        return F(k + '.rec', x['record'], 'measured', f'Wins–losses with {q} as partner.')
    if field == 'dpm':
        return F(k + '.dpm', sg(x['dpm']), 'measured', f'Points difference per match with {q} as partner.')
    if field == 'n':
        return F(k + '.n', num(x['P']), 'measured', f'Matches with {q} as partner.')
    if field == 'exp':
        return F(k + '.exp', sg(x['exp_dpm']), 'estimate', f'Expected points difference per match for this pair from the two players’ season estimates and the opponents faced.')
    if field == 'vs':
        return F(k + '.vs', sg(x['vs_exp']), 'estimate', f'Actual minus expected points difference per match with {q}.')


def opp_fact(p, q, field='rec'):
    x = next(r for r in OPP[p] if r['opponent'] == q)
    k = f'{SLUG[p]}.v.{SLUG[q]}'
    if field == 'rec':
        return F(k + '.rec', x['record'], 'measured', f'Wins–losses in matches with {q} on the other side.')
    if field == 'pct':
        return F(k + '.pct', pct(x['win_pct'], 0), 'measured', f'Win rate in matches with {q} on the other side.')
    if field == 'n':
        return F(k + '.n', num(x['P']), 'measured', f'Matches with {q} on the other side.')


def band_fact(p, b, field='rec'):
    x = BAND[f'{p}|{b}']
    k = f'{SLUG[p]}.b.{b}'
    if field == 'rec':
        return F(k + '.rec', x['record'], 'measured', f'Wins–losses against {b} opposing pairs (combined season estimate above +1.5 is strong, below −1.5 weak).')
    if field == 'exp':
        return F(k + '.exp', f'{x["exp_W"]:.1f}', 'estimate', f'Expected wins against {b} opposing pairs.')
    if field == 'dpm':
        return F(k + '.dpm', sg(x['dpm']), 'measured', f'Points difference per match against {b} opposing pairs.')


def week_fact(p, wk, field):
    x = next(w for w in WK[p] if w['week'] == wk)
    k = f'{SLUG[p]}.wk{wk}.{field}'
    if field == 'rec':
        return F(k, x['record'], 'measured', f'Week {wk} wins–losses.')
    if field == 'diff':
        return F(k, sg(x['diff'], 0), 'measured', f'Week {wk} points difference.')
    if field == 'dpm':
        return F(k, sg(x['dpm']), 'measured', f'Week {wk} points difference per match.')
    if field == 'adj':
        return F(k, sg(x['adj']), 'estimate', f'Week {wk} adjusted performance per match.')


# ---------------------------------------------------------------- HTML helpers
def table(src, key, cols, cls='', where=None, sort=None, maxh=False, caption=None, rowkey_col=None):
    """cols: list of (field, label, fmt, numeric)"""
    attrs = f'data-source="{src}" data-row-key="{key}"'
    if where:
        attrs += f' data-filter="{escape(where)}"'
    if sort:
        attrs += f' data-order="{sort}"'
    ths = ''.join(
        f'<th data-field="{f}" data-fmt="{fmt}" class="{"num" if numc else ""}" aria-sort="none"><button type="button" class="bx-sort">{escape(lbl)}</button></th>'
        for f, lbl, fmt, numc in cols)
    cap = f'<caption>{caption}</caption>' if caption else ''
    return (f'<div class="bx-tw{" bx-tw-tall" if maxh else ""}"><table class="bx-table {cls}" {attrs}>{cap}<thead><tr>{ths}</tr></thead>'
            f'<tbody data-draw="t"></tbody></table></div>')


def card(title, body, kind=None, note=None, cid=None, wide=False):
    t = tag(kind) if kind else ''
    n = f'<p class="bx-note">{note}</p>' if note else ''
    i = f' id="{cid}"' if cid else ''
    return f'<div class="bx-card{" bx-wide" if wide else ""}"{i}><div class="bx-card-head"><h3>{title}</h3>{t}</div>{n}{body}</div>'


def chart(name, src, h=None, extra=''):
    style = f' style="min-height:{h}px"' if h else ''
    return f'<div class="bx-chart dash-skeleton" data-draw="{name}" data-source="{src}"{extra}{style}></div>'


html = []
A = html.append

A('<meta name="dash-one-writer">')
A('<link rel="stylesheet" href="style.css">')
A('<div class="bx">')

# ---------------------------------------------------------------- header + tabs
TABS = [('summary', 'Summary'), ('players', 'Players'), ('weekly', 'Weekly'), ('partners', 'Partnerships'),
        ('opponents', 'Opponents'), ('pressure', 'Pressure and consistency'), ('model', 'Models'),
        ('rankings', 'Rankings'), ('strengths', 'Strengths and targets'), ('outlook', 'Outlook'), ('data', 'Data checks')]
A('<header class="bx-head">')
A('<p class="bx-eyebrow">Doubles season · badminton-scores.xlsx</p>')
A('<h1 class="bx-title">Badminton season analytics</h1>')
A(f'<p class="bx-lede">{g["n"]} doubles matches over {g["days"]} session days and {g["weeks"]} weeks, all re-derived from the match records. '
  f'Anto is the strongest player by every measure, Jothi Sai is a clear second once the hardest draws in the group are accounted for, '
  f'John and Dinesh have improved the most, and Pawan has had the sharpest recent drop.</p>')
A('<nav class="bx-tabs" aria-label="Report sections">')
for i, (tid, lbl) in enumerate(TABS):
    A(f'<button type="button" class="bx-tab" data-tab="{tid}" aria-controls="{tid}" aria-selected="{"true" if i == 0 else "false"}">{lbl}</button>')
A('</nav></header>')

# ================================================================ SUMMARY
A('<section class="bx-sec" id="summary" data-panel="summary">')
A('<h2>Executive summary</h2>')
A('<div class="bx-kpis">')
kp = [('Matches analysed', g['n'], f'{g["q"]} qualifier · {g["el"]} eliminator · {g["fi"]} final'),
      ('Session days', g['days'], f'over {g["weeks"]} weeks'),
      ('Decided by ' + K('close3') + ' or fewer', g['le3p'], f'{g["le3"]} of {g["n"]} matches'),
      ('Out-of-sample winner picked', gm['acc'], f'margin error {gm["cvmae"]} points')]
for lbl, big, sub in kp:
    A(f'<div class="bx-kpi"><p class="bx-kpi-l">{lbl}</p><p class="bx-kpi-v">{big}</p><p class="bx-kpi-s">{sub}</p></div>')
A('</div>')
a, j, jo, pw, di, pt, bh = (PF_[p] for p in P)
A('<div class="bx-prose">')
A('<ol class="bx-findings">')
A(f'<li><b>Anto is the best player in the group, and it is not close.</b> {a["rec"]} ({a["pct"]}), {a["dpm"]} points per match and {a["titles"]} titles from {a["days"]} days. '
  f'Separated from partners and opponents, Anto adds an estimated {a["adj"]} points per match ({a["adjci"]}) and ranks first in {a["pfirst"]} of resamples. '
  f'The workbook now rates Jothi Sai level with Anto at 5, but its own fitted values ({g["wban"]} against {g["wbjs"]}) and every model in this report still put Anto ahead.</li>')
A(f'<li><b>Jothi Sai is the clear second, and the raw record undersells that.</b> {j["rec"]} ({j["pct"]}) and {j["dpm"]} per match look ordinary, but Jothi Sai’s draws were the hardest in the group: '
  f'partners and opponents were worth {j["ctx"]} points per match against Jothi Sai, who faced Anto {opp_fact("Jothi Sai", "Anto", "n")} times. Adjusted, Jothi Sai is {j["adj"]}.</li>')
A(f'<li><b>John improved the most and handles tight matches best.</b> John’s second-half estimate rose {jo["chg"]} points per match, Week 6 was John’s best week ({week_fact("John", 6, "rec")}, {week_fact("John", 6, "diff")}), John went {fm("john.lastday", day_rec("John", LAST), "John’s wins–losses on the latest session day.")} on {SH(LAST)}, '
  f'and John won {jo["c3"]} of matches decided by {K("close3")} or fewer, {jo["c3v"]} wins above what the margins predict.</li>')
A(f'<li><b>Pawan is fourth on the season but in the worst form of it.</b> Week 7 ({week_fact("Pawan", 7, "rec")}, {week_fact("Pawan", 7, "diff")}) was Pawan’s worst week, the recency-weighted estimate has fallen to {pw["radj"]}, '
  f'and the workbook has cut the rating to {pw["wb1"]}. Finals remain a weak spot overall ({pw["fin"]}, {pw["finv"]} against expectation), although Pawan has won the last {fe("pawan.fstreak", num(final_streak("Pawan")), "Finals won in a row, counting back from the latest final Pawan played.")} finals Pawan has played.</li>')
A(f'<li><b>Dinesh and Pratap are level on the season but moving in opposite directions.</b> Their estimates ({di["adj"]} and {pt["adj"]}) cannot be separated statistically. '
  f'Dinesh has the best knockout record in the group ({di["ko"]}), rose {di["chg"]} between halves and had the best adjusted week of the season in Week 7; Pratap fell {pt["chg"]} and lost {pt["sl"]} straight in Week 6, '
  f'but steadied in Week 7 ({week_fact("Pratap", 7, "rec")}), so Pratap’s downward trend no longer clears chance (t = {pt["trt"]}). '
  f'Dinesh went {fm("dinesh.lastday", day_rec("Dinesh", LAST), "Dinesh’s wins–losses on the latest session day.")} on {SH(LAST)}, a step back from Week 7.</li>')
A(f'<li><b>Bhanu’s results are the weakest by a wide margin, and close matches hurt most.</b> {bh["rec"]}, {bh["dpm"]} per match, adjusted {bh["adj"]}. '
  f'Bhanu won {bh["c3"]} of matches decided by {K("close3")} or fewer, {bh["c3v"]} wins against expectation — the largest pressure gap in the data. The last {K("recentN")} matches ({bh["rrec"]}, {bh["rdpm"]} per match) are below even the season average.</li>')
A('</ol>')
A(f'<p class="bx-callout"><b>How to read this report.</b> Every figure is marked <span class="bx-tag bx-tag-m">Measured</span> (counted straight from the match records) or '
  f'<span class="bx-tag bx-tag-e">Estimate</span> (from a statistical model, with its uncertainty). Pairings in this league are deliberately balanced, strong with weak, so raw win rates '
  f'are pulled toward even and partner records reflect the draw. The adjusted estimates correct for that. A single match is noisy: after accounting for who is on court, '
  f'margins still vary by about {gm["sigma"]} points, so only the larger differences here are reliable.</p>')
A('</div>')

A('<h2 id="leaderboard">Overall leaderboard</h2>')
A('<div class="bx-grid">')
A(card('Season results', table('players', 'player', [
    ('player', 'Player', 'text', False), ('days', 'Days', 'int', True), ('P', 'P', 'int', True), ('W', 'W', 'int', True), ('L', 'L', 'int', True),
    ('win_pct', 'Win %', 'pct', True), ('PF', 'For', 'int', True), ('PA', 'Against', 'int', True), ('diff', 'Diff', 's0', True),
    ('dpm', 'Diff / match', 's2', True), ('q_record', 'Qualifier', 'text', True), ('ko_record', 'Knockout', 'text', True),
    ('fin_record', 'Finals', 'text', True), ('titles', 'Titles', 'int', True), ('wb_start', 'Rating start', 'int', True), ('wb_now', 'Rating now', 'int', True)],
    sort='-win_pct'), 'm', 'Counted from the match log. Ratings are the workbook’s own 1–5 pairing ratings.', cid='lb-measured', wide=True))
A(card('Adjusted strength and form', table('estimates', 'player', [
    ('player', 'Player', 'text', False), ('adj', 'Season', 's2', True), ('adj_lo', 'Low', 's2', True), ('adj_hi', 'High', 's2', True),
    ('recent_adj', 'Recent', 's2', True), ('change', 'Half-season change', 's2', True), ('elo', 'Elo', 'int', True),
    ('p_first', 'Chance ranked first', 'pct0', True), ('draw_context', 'Draw worth', 's2', True), ('neutral_win_recent', 'Neutral-draw win %', 'pct0', True)],
    sort='-adj'), 'e', 'Points per match each player adds to a team’s margin versus an average player. Low and high bound the 90% interval. Draw worth is what partners and opponents were worth per match.', cid='lb-model', wide=True))
A('</div>')
A('<div class="bx-grid">')
A(card('Win rate with 90% interval', chart('c-win', 'players', 300), 'm', 'Bars are the season win rate; whiskers show the range the true rate plausibly sits in given the number of matches.', cid='ch-win'))
A(card('Points difference per match: raw and adjusted', chart('c-dpm', 'players estimates', 300), 'e', 'Raw is the measured average; adjusted removes the effect of partners and opponents. Gaps show who the draw helped or hurt.', cid='ch-dpm'))
A('</div>')
A(card('Points difference through the season', chart('c-cum', 'daily', 340), 'm', 'Running total of points scored minus conceded after each session day. Flat stretches are days missed.', cid='ch-cum', wide=True))
A('</section>')

# ================================================================ PLAYERS
A('<section class="bx-sec" id="players" data-panel="players" hidden>')
A('<h2>Player reports</h2>')
A('<div class="bx-pick" role="group" aria-label="Choose a player">')
for i, p in enumerate(P):
    A(f'<button type="button" class="bx-pick-b" data-player="{SLUG[p]}" aria-pressed="{"true" if i == 0 else "false"}">{p}</button>')
A('</div>')

VERDICT = {}
x = PF_['Anto']
VERDICT['Anto'] = (
    f'The benchmark of the group. Anto played every one of the {g["days"]} days, won {x["rec"]} and finished first in the qualifier table on {x["top"]} days. '
    f'The record is strong despite the draw working against Anto: the pairing system gave Anto the weakest partners of anyone (average partner {x["mate"]}), '
    f'yet the adjusted estimate of {x["adj"]} leads the group by more than a point a match. Anto loses rarely and narrowly — average defeat {x["al"]} points, '
    f'and only {x["heavyp"]} of Anto’s matches were lost by {K("heavy")} or more, the lowest rate in the group.')
x = PF_['Jothi Sai']
VERDICT['Jothi Sai'] = (
    f'The second-best player, hidden by a hard schedule. Jothi Sai’s {x["rec"]} and {x["dpm"]} per match are only the second-best raw numbers by a small margin, '
    f'but no one had a tougher draw: opponents averaged {x["oppav"]} combined and the draw cost {x["ctx"]} per match. The adjusted estimate is {x["adj"]} ({x["adjci"]}). '
    f'Jothi Sai played {x["days"]} of {g["days"]} days, missing all of Week 4.')
x = PF_['John']
VERDICT['John'] = (
    f'The improver. John’s season numbers ({x["rec"]}, {x["dpm"]} per match) are close to Jothi Sai’s raw line, but they combine a flat first five weeks with a strong Week 6; John played one day of Week 7 and went {fm("john.lastday", day_rec("John", LAST), "John’s wins–losses on the latest session day.")} on {SH(LAST)}. '
    f'John’s adjusted estimate moved from {x["h1"]} in the first half to {x["h2"]} in the second, and the workbook raised the rating from {x["wb0"]} to {x["wb1"]}. '
    f'John is the best close-match player in the group and has won {x["telim"]} of {x["titles"]} titles after coming through an eliminator.')
x = PF_['Pawan']
VERDICT['Pawan'] = (
    f'A reliable mid-table player whose knockout results lag the qualifier form. Pawan is {x["q"]} in qualifiers ({x["qd"]} per match) but {x["ko"]} in knockouts and {x["fin"]} in finals. '
    f'Pawan’s adjusted estimate ({x["adj"]}, interval {x["adjci"]}) is clearly above Dinesh and Pratap but cannot be told apart from zero with full confidence. '
    f'Weeks 6 and 7 were the two weakest weeks of the season — Week 7 ({week_fact("Pawan", 7, "rec")}, {week_fact("Pawan", 7, "diff")}) the worst — and the workbook has cut the rating to {x["wb1"]}.')
x = PF_['Dinesh']
VERDICT['Dinesh'] = (
    f'A below-average qualifier who becomes dangerous in knockouts. Dinesh’s {x["rec"]} and {x["dpm"]} per match flatter Dinesh slightly: the draw was the most favourable in the group — '
    f'strong partners (average {x["mate"]}) against weaker opponents, worth {x["ctx"]} per match — so the adjusted estimate is {x["adj"]}. Against that, Dinesh is {x["ko"]} in knockouts and '
    f'{x["fin"]} in finals, the level rose between the two halves of the season, and Week 7 was Dinesh’s best adjusted week.')
x = PF_['Pratap']
VERDICT['Pratap'] = (
    f'The season’s biggest slide, now steadying. Pratap was level with the middle of the group early on — topping the qualifier on {x["top"]} days and winning the W4 D3 title — '
    f'but the adjusted estimate fell from {x["h1"]} to {x["h2"]}, and Week 6 ({week_fact("Pratap", 6, "rec")}, {week_fact("Pratap", 6, "diff")}) was the worst week any player other than Bhanu had all season. '
    f'Week 7 ({week_fact("Pratap", 7, "rec")}, {week_fact("Pratap", 7, "diff")}) was back to level, and the workbook rating is back to {x["wb1"]} after a spell at {x["wblo"]} alongside Bhanu.')
x = PF_['Bhanu']
VERDICT['Bhanu'] = (
    f'The weakest results in the group by a distance. Bhanu is {x["rec"]} with {x["dpm"]} per match and has held the bottom workbook rating all season. '
    f'The adjusted estimate ({x["adj"]}) is what a team with Bhanu gives up per match against an average pairing. '
    f'Bright spots are few: one title (W6 D3 with John) and Week 6, the best adjusted week of the season ({week_fact("Bhanu", 6, "adj")}). Week 7 ({week_fact("Bhanu", 7, "rec")}) slipped back, and the last {K("recentN")} matches ({x["rrec"]}, {x["rdpm"]} per match) are below the season average.')

for i, p in enumerate(P):
    x = PF_[p]; e = E[p]; sl = SLUG[p]
    A(f'<article class="bx-pr" id="p-{sl}" data-player="{sl}"{"" if i == 0 else " hidden"}>')
    A(f'<div class="bx-pr-head"><h3 class="bx-pr-name">{p}</h3>'
      f'<p class="bx-pr-sub">Adjusted rank {pf(p, "rank", num(e["adj_rank"]), "Rank of the season adjusted estimate.", "estimate")} of {g["players"]} · '
      f'workbook rating {x["wb0"]} → {x["wb1"]} · {x["days"]} of {g["days"]} days played</p></div>')
    A(f'<p class="bx-pr-verdict">{VERDICT[p]}</p>')
    # stat grid
    stats = [('Matches', x['P']), ('Won–lost', x['rec']), ('Win rate', x['pct']), ('90% range', x['ci']),
             ('Points for', x['PF']), ('Points against', x['PA']), ('Points difference', x['diff']), ('Per match', x['dpm']),
             ('Average winning margin', x['aw']), ('Average losing margin', x['al']), ('Qualifier', x['q']), ('Knockout', x['ko']),
             ('Eliminators', x['el']), ('Finals', x['fin']), ('Titles', x['titles']), ('Titles, Day 1 excluded', x['tconf']),
             ('Rating at start', x['wb0']), ('Rating now', x['wb1']), ('Rating range', f'{x["wblo"]}–{x["wbhi"]}'), ('Elo at season end', x['elo'])]
    A(f'<div class="bx-card"><div class="bx-card-head"><h3>Season line</h3>{tag("m")}</div><dl class="bx-stats">')
    for lbl, val in stats:
        A(f'<div><dt>{lbl}</dt><dd>{val}</dd></div>')
    A('</dl><p class="bx-note">Win-rate range and Elo are estimates; the rest are counts from the match log.</p></div>')
    # charts
    A('<div class="bx-grid">')
    A(card('Day by day', chart('p-daily', 'daily', 240, f' data-player="{p}"'), 'm', 'Points difference each session day. Filled dots mark titles, open dots finals lost.'))
    A(card('Week by week', table('weekly', 'key', [('label', 'Week', 'text', False), ('days', 'Days', 'int', True), ('record', 'W–L', 'text', True),
                                                   ('win_pct', 'Win %', 'pct', True), ('diff', 'Diff', 's0', True), ('dpm', 'Per match', 's2', True), ('adj', 'Adjusted', 's2', True)],
                                   where=f'player={p}', sort='week'), 'm', 'Adjusted is an estimate: the week’s margins with partners’ and opponents’ season estimates taken out.'))
    A('</div><div class="bx-grid">')
    A(card('With each partner', chart('p-partners', 'partners', 250, f' data-player="{p}"'), 'm', f'Points difference per match with each partner; label shows record and matches. Fewer than {K("regular")} matches is too few to judge.'))
    A(card('Against each opponent', chart('p-opps', 'opponents', 250, f' data-player="{p}"'), 'm', 'Win rate in matches where that player was on the other side. Each match counts against both opponents.'))
    A('</div>')
    # narrative blocks
    pr = partner_rows(p); best_p = max(pr, key=lambda r: r['dpm']); worst_p = min(pr, key=lambda r: r['dpm'])
    orr = opp_rows(p); fav = max(orr, key=lambda r: r['win_pct']); tough = min(orr, key=lambda r: r['win_pct'])
    A('<div class="bx-grid">')
    body = (f'<ul class="bx-list">'
            f'<li><b>Rating path.</b> Workbook rating {x["wb0"]} → {x["wb1"]} (range {x["wblo"]}–{x["wbhi"]}); Elo ends at {x["elo"]}. '
            f'Adjusted estimate {x["h1"]} in the first half, {x["h2"]} in the second ({x["chg"]}, interval {x["chgci"]}).</li>'
            f'<li><b>Best week.</b> Week {x["bw"]["week"]}: {x["bwrec"]}, {x["bwd"]} (adjusted {x["bwa"]} per match).</li>'
            f'<li><b>Worst week.</b> Week {x["ww"]["week"]}: {x["wwrec"]}, {x["wwd"]} (adjusted {x["wwa"]} per match).</li>'
            f'<li><b>Recent form.</b> Last {K("recentN")} matches {x["rrec"]} at {x["rdpm"]} per match, against {x["dpm"]} for the season; recency-weighted estimate {x["radj"]}.</li>'
            f'<li><b>Streaks.</b> Longest winning run {x["sw"]} ({x["swspan"]}); longest losing run {x["sl"]} ({x["slspan"]}).</li></ul>')
    A(card('Form and progression', body, 'e'))
    body = (f'<ul class="bx-list">'
            f'<li><b>Best regular partner.</b> {best_p["partner"]}: {partner_fact(p, best_p["partner"])} ({partner_fact(p, best_p["partner"], "dpm")} per match over {partner_fact(p, best_p["partner"], "n")}).</li>'
            f'<li><b>Weakest regular partner.</b> {worst_p["partner"]}: {partner_fact(p, worst_p["partner"])} ({partner_fact(p, worst_p["partner"], "dpm")} per match over {partner_fact(p, worst_p["partner"], "n")}).</li>'
            f'<li><b>Most favourable opponent.</b> {fav["opponent"]}: {opp_fact(p, fav["opponent"])} ({opp_fact(p, fav["opponent"], "pct")}).</li>'
            f'<li><b>Hardest opponent.</b> {tough["opponent"]}: {opp_fact(p, tough["opponent"])} ({opp_fact(p, tough["opponent"], "pct")}).</li>'
            f'<li><b>Against strong pairs.</b> {band_fact(p, "strong")} against opposing pairs rated above {K("band")} combined, with {band_fact(p, "strong", "exp")} wins expected.</li>'
            f'<li><b>Under pressure.</b> Close matches {x["c3"]} ({x["c3v"]} versus expectation); knockouts {x["ko"]} ({x["kov"]}); finals {x["fin"]} ({x["finv"]}).</li></ul>'
            f'<p class="bx-note">Regular partner means {K("regular")} or more matches together; opponents need {K("oppmin")} or more meetings.</p>')
    A(card('Partners, opponents and pressure', body, 'm'))
    A('</div>')
    A(f'<p class="bx-pr-foot">Strengths, weaknesses, training priorities and next-month targets for {p} are on the <a href="#sw-{sl}" class="bx-jump">Strengths and targets</a> tab.</p>')
    A('</article>')
A('</section>')

# ================================================================ WEEKLY
A('<section class="bx-sec" id="weekly" data-panel="weekly" hidden>')
A('<h2>Weekly performance</h2>')
A(f'<p class="bx-prose">Weeks are unequal — {g["wkrange"]} session days — and players missed different weeks (John Week 3, Jothi Sai Week 4, Pratap Week 5; Week 8 has one day so far and Bhanu sat it out), so compare rates per match, not totals. '
  f'“Adjusted” removes partners’ and opponents’ season strength from each margin; it is the fairest single number for comparing a player’s weeks.</p>')
A(card('Adjusted performance by week', chart('c-weekheat', 'weekly', 330), 'e', 'Each cell is the player’s average adjusted margin per match that week, with the week’s record. Blank cells are weeks not played.', cid='ch-weekheat', wide=True))
A(card('Every player, every week', table('weekly', 'key', [('player', 'Player', 'text', False), ('label', 'Week', 'text', False), ('days', 'Days', 'int', True),
                                                           ('P', 'P', 'int', True), ('record', 'W–L', 'text', True), ('win_pct', 'Win %', 'pct', True),
                                                           ('diff', 'Diff', 's0', True), ('dpm', 'Per match', 's2', True), ('adj', 'Adjusted', 's2', True)],
                                      sort='player,week', maxh=True), 'm', 'Sort any column. Adjusted is an estimate.', wide=True))
A('<div class="bx-grid">')
body = '<ul class="bx-list">'
for p in P:
    x = PF_[p]
    body += (f'<li><b>{p}.</b> Best Week {x["bw"]["week"]} ({x["bwrec"]}, adjusted {x["bwa"]}); worst Week {x["ww"]["week"]} ({x["wwrec"]}, adjusted {x["wwa"]}).</li>')
body += f'</ul><p class="bx-note">Weeks with fewer than {K("weekmin")} matches are not eligible.</p>'
A(card('Best and worst week', body, 'm'))
body = '<ul class="bx-list">'
for p in P:
    x = PF_[p]
    body += f'<li><b>{p}.</b> Last {K("recentN")}: {x["rrec"]}, {x["rdpm"]} per match · season {x["dpm"]} · recency-weighted estimate {x["radj"]} vs season {x["adj"]}.</li>'
body += '</ul>'
A(card('Recent form against the season', body, 'm', f'Last {K("recentN")} matches is the same sample size for everyone.'))
A('</div>')
x = PF_
A(card('Who is improving, declining or holding steady', (
    f'<ul class="bx-list">'
    f'<li><b>Improving — John and Dinesh.</b> John rose {x["John"]["chg"]} between halves with a daily trend of {x["John"]["tr"]}; Week 6 was John’s best full week and {SH(LAST)} went {fm("john.lastday", day_rec("John", LAST), "John’s wins–losses on the latest session day.")}. '
    f'Dinesh rose {x["Dinesh"]["chg"]} with a trend of {x["Dinesh"]["tr"]}, and Week 7 was Dinesh’s best adjusted week, though {SH(LAST)} ({fm("dinesh.lastday", day_rec("Dinesh", LAST), "Dinesh’s wins–losses on the latest session day.")}) was a step back. Both are suggestive rather than proven: neither interval excludes zero.</li>'
    f'<li><b>Declining — Pawan (recent, sharp), Pratap (season, now steadying).</b> Pawan fell {x["Pawan"]["chg"]} between halves, Weeks 6 and 7 were the two weakest weeks, and the workbook cut the rating to {x["Pawan"]["wb1"]}. '
    f'Pratap’s trend of {x["Pratap"]["tr"]} (t = {x["Pratap"]["trt"]}) was the one clear decline after Week 6, but a level Week 7 ({week_fact("Pratap", 7, "rec")}) has pulled it back inside chance.</li>'
    f'<li><b>Holding steady — Anto, Jothi Sai, Bhanu.</b> Anto ({x["Anto"]["tr"]}) and Jothi Sai ({x["Jothi Sai"]["tr"]}) have no meaningful trend. Bhanu dipped in Weeks 4–5, recovered in Week 6 and slipped back in Week 7, '
    f'leaving no net trend ({x["Bhanu"]["tr"]}).</li></ul>'
    f'<p class="bx-note">Trend is the fitted change in daily adjusted performance across the season; half-season change compares separate fits of the first {g["half"]} and last {g["half2"]} days.</p>'), 'e', wide=True))
A('</section>')

# ================================================================ PARTNERSHIPS
A('<section class="bx-sec" id="partners" data-panel="partners" hidden>')
A('<h2>Partnership analysis</h2>')
ajp = PAIRS['Anto + Jothi Sai']; jdp = PAIRS['John + Dinesh']; dbp = PAIRS['Dinesh + Bhanu']; ppp = max(T['pairs'], key=lambda q: q['P'])
nz = sum(1 for x in T['pairs'] if abs(x['z']) > 1.645)
A(f'<p class="bx-prose">Partnerships here are assigned, not chosen: the workbook builds balanced teams from its ratings, so strong players are usually paired with weak ones. '
  f'That makes a raw partnership record mostly a measure of the two players’ combined strength. To find genuine chemistry, each pair’s results are compared with what the two '
  f'players’ separate estimates predict against the opponents they actually met. Out of {fm("pr.n", num(len(T["pairs"])), "Distinct partnerships that played at least once.")} partnerships, '
  f'{fe("pr.nz", num(nz) if nz else "none", "Pairs whose result versus expectation is more than 1.645 standard errors from zero.")} {"differs" if nz <= 1 else "differ"} from expectation by more than chance would usually allow '
  f'— no more than chance alone would produce across that many pairs. In short, there is no reliable evidence of special chemistry or clashes; partnership results are explained by individual strength.</p>')
A('<div class="bx-grid">')
A(card('Partnership matrix', chart('c-pairmatrix', 'pairs', 380), 'm', f'Points difference per match for each pair, with record. Faded cells have fewer than {K("regular")} matches.', cid='ch-pairmatrix'))
A(card('Results versus expectation', chart('c-pairvs', 'pairs', 520), 'e', 'Actual minus expected points per match for each pair, with one standard error either side. Bars crossing zero are consistent with no chemistry effect.', cid='ch-pairvs'))
A('</div>')
A(card('Key partnership findings', (
    f'<ul class="bx-list">'
    f'<li><b>Best record: Anto + Jothi Sai, {fm("pr.aj.rec", ajp["record"], "Wins–losses as partners.")}</b> at {fm("pr.aj.dpm", sg(ajp["dpm"]), "Points difference per match as partners.")} per match. '
    f'That is almost exactly what two of the strongest players should produce ({fe("pr.aj.exp", sg(ajp["exp_dpm"]), "Expected points difference per match for the pair.")} expected), so it is strength, not chemistry. '
    f'It is also a small sample, because the balancing draw rarely puts them together.</li>'
    f'<li><b>Strongest chemistry signal: John + Dinesh, {fm("pr.jd.rec", jdp["record"], "Wins–losses as partners.")}</b> but {fm("pr.jd.dpm", sg(jdp["dpm"]), "Points difference per match as partners.")} per match against '
    f'{fe("pr.jd.exp", sg(jdp["exp_dpm"]), "Expected points difference per match for the pair.")} expected ({fe("pr.jd.vs", sg(jdp["vs_exp"]), "Actual minus expected per match.")}). '
    f'Suggestive over {fm("pr.jd.n", num(jdp["P"]), "Matches together.")} matches, not proven.</li>'
    f'<li><b>Most frequent pair: {ppp["key"]}</b>, {fm("pr.pp.n", num(ppp["P"]), "Matches together.")} matches, {fm("pr.pp.rec", ppp["record"], "Wins–losses as partners.")} — slightly {"better" if ppp["vs_exp"] > 0 else "worse"} than expected ({fe("pr.pp.vs", sg(ppp["vs_exp"]), "Actual minus expected per match.")}).</li>'
    f'<li><b>Worst record: Dinesh + Bhanu, {fm("pr.db.rec", dbp["record"], "Wins–losses as partners.")}</b>, {fm("pr.db.dpm", sg(dbp["dpm"]), "Points difference per match as partners.")} per match over only '
    f'{fm("pr.db.n", num(dbp["P"]), "Matches together.")} matches. The workbook kept them apart from W6 D2 until W7 D3, when the five-player rotation paired them in a qualifier and the eliminator; both were lost.</li>'
    f'<li><b>Partnering Bhanu</b> costs every partner except Anto heavily. Anto + Bhanu went {partner_fact("Anto", "Bhanu")} — better than expected ({partner_fact("Anto", "Bhanu", "vs")}) — '
    f'while Pawan + Bhanu went {partner_fact("Pawan", "Bhanu")} and Pratap + Bhanu {partner_fact("Pratap", "Bhanu")}.</li></ul>'), 'm', wide=True))
body = '<ul class="bx-list">'
for p in P:
    pr = partner_rows(p); b = max(pr, key=lambda r: r['dpm']); w = min(pr, key=lambda r: r['dpm'])
    body += (f'<li><b>{p}.</b> Best {b["partner"]} ({partner_fact(p, b["partner"])}, {partner_fact(p, b["partner"], "dpm")}); '
             f'worst {w["partner"]} ({partner_fact(p, w["partner"])}, {partner_fact(p, w["partner"], "dpm")}). Partners do {PF_[p]["upl"]} points per match better with {sname(p)} than without, on average.</li>')
body += f'</ul><p class="bx-note">Only partners with {K("regular")} or more matches together are named.</p>'
A(card('Best and worst partner for each player', body, 'm', wide=True))
A(card('All partnerships', table('pairs', 'key', [('key', 'Pair', 'text', False), ('P', 'P', 'int', True), ('record', 'W–L', 'text', True), ('win_pct', 'Win %', 'pct', True),
                                                 ('ci_lo', 'Low', 'pct0', True), ('ci_hi', 'High', 'pct0', True), ('dpm', 'Per match', 's2', True),
                                                 ('exp_dpm', 'Expected', 's2', True), ('vs_exp', 'Versus expected', 's2', True), ('vs_exp_se', '± error', 'f1', True), ('sample', 'Sample', 'text', False)],
                                sort='-P', maxh=True), 'm', 'Low and high are the 90% range for the win rate. Expected and versus expected are estimates.', wide=True))
A('</section>')

# ================================================================ OPPONENTS
A('<section class="bx-sec" id="opponents" data-panel="opponents" hidden>')
A('<h2>Opponent analysis</h2>')
maxadj = max(abs(x['adj']) for x in T['opponents'] if x['P'] >= 15)
SHORT_STRONG = min(P, key=lambda p: BAND[f'{p}|strong']['vs_exp'])
A(f'<p class="bx-prose">In doubles each match puts a player against two opponents at once, and every opponent also had a partner, so a head-to-head record is shared credit. '
  f'Records against the strongest players are poor for everyone simply because those players are strong. The useful question is whether anyone does unusually well or badly '
  f'against a particular opponent once strength is accounted for. The answer is no: across all pairings with {K("oppmin")} or more meetings, the largest such deviation is '
  f'{fe("op.maxadj", f"{maxadj:.1f}", "Largest absolute difference between a player’s adjusted performance against one opponent and their overall adjusted performance (15+ meetings).")} points per match, '
  f'within normal match-to-match noise. There are no hidden “bogey” matchups in this data.</p>')
A('<div class="bx-grid">')
A(card('Head-to-head matrix', chart('c-oppmatrix', 'opponents', 380), 'm', 'Row player’s win rate in matches where the column player was on the other side, with record.', cid='ch-oppmatrix'))
A(card('Against strong, middle and weak pairs', table('bands', 'key', [('player', 'Player', 'text', False), ('band', 'Opposition', 'text', False), ('P', 'P', 'int', True),
                                                                      ('record', 'W–L', 'text', True), ('win_pct', 'Win %', 'pct', True), ('dpm', 'Per match', 's2', True),
                                                                      ('exp_W', 'Expected wins', 'f1', True), ('vs_exp', 'Versus expected', 's1', True)],
                                     sort='player,band', maxh=True), 'm', f'Opposing pairs grouped by combined season estimate: strong above {K("band")}, weak below {K("bandneg")}. Expected wins are model estimates.'))
A('</div>')
body = '<ul class="bx-list">'
for p in P:
    orr = opp_rows(p); fav = max(orr, key=lambda r: r['win_pct']); tough = min(orr, key=lambda r: r['win_pct'])
    body += (f'<li><b>{p}.</b> Most favourable {fav["opponent"]} ({opp_fact(p, fav["opponent"])}); hardest {tough["opponent"]} ({opp_fact(p, tough["opponent"])}); '
             f'against strong pairs {band_fact(p, "strong")} ({band_fact(p, "strong", "dpm")} per match, {band_fact(p, "strong", "exp")} wins expected).</li>')
body += '</ul>'
A(card('Each player’s matchups', body, 'm', f'Opponents with {K("oppmin")} or more meetings.', wide=True))
A(card('What stands out', (
    f'<ul class="bx-list"><li><b>Anto is the only player who breaks even against strong pairs</b> ({band_fact("Anto", "strong")}, {band_fact("Anto", "strong", "dpm")} per match).</li>'
    f'<li><b>{SHORT_STRONG} falls furthest short against strong pairs</b>: {band_fact(SHORT_STRONG, "strong")} with {band_fact(SHORT_STRONG, "strong", "exp")} expected.</li>'
    f'<li><b>John’s hardest opponent is Jothi Sai</b> ({opp_fact("John", "Jothi Sai")}), not Anto ({opp_fact("John", "Anto")}).</li>'
    f'<li><b>Jothi Sai met Anto {opp_fact("Jothi Sai", "Anto", "n")} times</b>, the most frequent opposing pair in the league, and won {opp_fact("Jothi Sai", "Anto", "pct")}. '
    f'The draw puts the top two on opposite sides, which is the main reason Jothi Sai’s raw record sits below the adjusted level.</li></ul>'), 'm', wide=True))
A('</section>')

# ================================================================ PRESSURE
A('<section class="bx-sec" id="pressure" data-panel="pressure" hidden>')
A('<h2>Pressure and consistency</h2>')
A(f'<p class="bx-prose">{g["le3"]} of {g["n"]} matches ({g["le3p"]}) were decided by {K("close3")} points or fewer and {g["le5"]} ({g["le5p"]}) by {K("close5")} or fewer; {g["deuce"]} went past {K("game")}. '
  f'Finals were the tightest stage (average margin {g["mf"]} against {g["mq"]} in qualifiers). Win rates in close matches mostly reflect team strength, so each player’s close-match '
  f'and knockout wins are compared with what their predicted margins imply. With these sample sizes, a gap needs to be roughly twice its standard deviation before it means much.</p>')
A('<div class="bx-grid">')
A(card('Wins above expectation under pressure', chart('c-clutch', 'pressure', 320), 'e', f'Close matches ({K("close3")} points or fewer) and knockout matches, actual wins minus expected. Whiskers are one standard deviation of chance either side.', cid='ch-clutch'))
A(card('Day-to-day consistency', chart('c-consist', 'daily estimates', 320), 'e', 'Each dot is one session day’s adjusted performance. The shaded band is the spread match noise alone would produce around the player’s average.', cid='ch-consist'))
A('</div>')
A(card('Pressure record', table('pressure', 'player', [('player', 'Player', 'text', False), ('c3_record', 'Within 3', 'text', True), ('c3_exp', 'Expected', 'f1', True),
                                                      ('c3_vs', 'Above expected', 's1', True), ('c5_record', 'Within 5', 'text', True), ('deuce_record', 'Past 21', 'text', True),
                                                      ('ko_record', 'Knockout', 'text', True), ('ko_vs', 'KO above expected', 's1', True), ('fin_record', 'Finals', 'text', True),
                                                      ('fin_vs', 'Finals above expected', 's1', True), ('best_win_streak', 'Best run', 'int', True), ('worst_loss_streak', 'Worst run', 'int', True)],
                       sort='-clutch'), 'm', 'Records are measured; expected and above-expected columns are estimates.', wide=True))
x = PF_
A('<div class="bx-grid">')
A(card('Findings', (
    f'<ul class="bx-list">'
    f'<li><b>John is the best performer under pressure</b>: close matches {x["John"]["c3"]} ({x["John"]["c3v"]}, chance spread ±{x["John"]["c3sd"]}), knockouts {x["John"]["ko"]} ({x["John"]["kov"]}), finals {x["John"]["fin"]}.</li>'
    f'<li><b>Dinesh lifts in knockouts</b>: {x["Dinesh"]["ko"]} ({x["Dinesh"]["kov"]}) and {x["Dinesh"]["fin"]} in finals, despite a losing qualifier record ({x["Dinesh"]["q"]}).</li>'
    f'<li><b>Anto under-converts finals</b>: {x["Anto"]["fin"]} with {x["Anto"]["fine"]} expected. In Week 6 Anto reached every final and won {fm("anto.w6f", str(finals_in_week("Anto", 6)[0]) + " of " + str(sum(finals_in_week("Anto", 6))), "Week 6 finals won of finals played.")}.</li>'
    f'<li><b>Pawan’s finals remain a weak spot</b>: {x["Pawan"]["fin"]}, {x["Pawan"]["finv"]} wins against expectation, though Pawan has won the last {fe("pawan.fstreak", num(final_streak("Pawan")), "Finals won in a row, counting back from the latest final Pawan played.")} finals Pawan has played.</li>'
    f'<li><b>Bhanu loses close matches far more than expected</b>: {x["Bhanu"]["c3"]} against {x["Bhanu"]["c3e"]} expected ({x["Bhanu"]["c3v"]}, {"about twice" if PR["Bhanu"]["c3_vs"] / PR["Bhanu"]["c3_sd"] <= -1.85 else "nearly twice"} the chance spread of ±{x["Bhanu"]["c3sd"]}). '
    f'This is the single strongest pressure signal in the data.</li>'
    f'<li><b>Comebacks cannot be identified</b> because only final scores were recorded. The nearest measurable thing is winning a title after coming through an eliminator: '
    + ', '.join(f'{p} {x[p]["telim"]}' for p in sorted([p for p in P if PL[p]['titles_via_elim']], key=lambda p: -PL[p]['titles_via_elim'])) + '.</li></ul>'), 'e'))
A(card('Consistency', (
    f'<ul class="bx-list">'
    f'<li><b>For Anto, Jothi Sai, John and Pawan, day-to-day swings are no larger than chance.</b> Their daily adjusted performance varies by {x["Anto"]["dsd"]}, {x["Jothi Sai"]["dsd"]}, {x["John"]["dsd"]} and {x["Pawan"]["dsd"]} points, '
    f'while a day’s handful of noisy matches would produce about {x["Anto"]["noise"]} on their own. Good and bad days for these four are mostly luck of the draw and the bounce.</li>'
    f'<li><b>Dinesh and Pratap vary a little more than chance</b> ({x["Dinesh"]["dsd"]} and {x["Pratap"]["dsd"]} against about {x["Dinesh"]["noise"]}).</li>'
    f'<li><b>Bhanu is the least consistent</b> ({x["Bhanu"]["dsd"]} against {x["Bhanu"]["noise"]}): good and bad days differ by more than the matches alone explain.</li>'
    f'<li><b>Most consistent results:</b> Anto had a positive points difference on {x["Anto"]["posd"]} of {x["Anto"]["days"]} days and lost by {K("heavy")} or more only {x["Anto"]["heavy"]} times.</li>'
    f'<li><b>Streaks:</b> Anto’s {x["Anto"]["sw"]}-match winning run ({x["Anto"]["swspan"]}) is the season’s longest; Bhanu’s {x["Bhanu"]["sl"]}-match losing run ({x["Bhanu"]["slspan"]}) and Pratap’s {x["Pratap"]["sl"]} ({x["Pratap"]["slspan"]}) the longest losing runs.</li></ul>'), 'e'))
A('</div>')
A('</section>')

# ================================================================ MODELS
A('<section class="bx-sec" id="model" data-panel="model" hidden>')
A('<h2>Advanced statistical analysis</h2>')
A('<div class="bx-grid">')
A(card('Adjusted strength with 90% intervals', chart('c-forest', 'estimates', 330), 'e', 'Points per match each player adds to a team’s margin versus an average player. Solid: whole season. Hollow: recency-weighted.', cid='ch-forest'))
A(card('Chance of each final rank', table('estimates', 'player', [('player', 'Player', 'text', False), ('adj_rank', 'Rank', 'int', True), ('p_first', 'Ranked first', 'pct0', True),
                                                                   ('p_top3', 'Top three', 'pct0', True), ('elo', 'Elo', 'int', True), ('elo_wl', 'Elo, wins only', 'int', True),
                                                                   ('exp_wins', 'Expected wins', 'f1', True), ('wins_vs_exp', 'Wins above expected', 's1', True)], sort='adj_rank'),
           'e', f'From {K("boot")} resamples of whole session days. Expected wins use out-of-sample predictions for every match.'))
A('</div>')
A(card('Elo rating through the season', chart('c-elo', 'daily', 360), 'e', f'Margin-weighted Elo after each session day. Everyone starts at {K("elostart")}.', cid='ch-elo', wide=True))
A('<div class="bx-grid">')
A(card('Workbook rating by day', chart('c-wbr', 'daily', 300), 'm', f'The {g["wbscale"]} rating the workbook used to make the draw each day. Blank: did not play.', cid='ch-wbr'))
A(card('Season ranking progression', chart('c-bump', 'daily', 300), 'm', 'Rank on cumulative points difference after each day.', cid='ch-bump'))
A('</div>')
A('<div class="bx-grid">')
A(card('Method', (
    f'<ol class="bx-list bx-ol">'
    f'<li><b>Adjusted plus-minus (ridge regression).</b> Each match is one equation: team A’s margin = the two A players’ values − the two B players’ values + noise. '
    f'Solving all {g["n"]} equations together separates each player from partners and opponents. A small ridge penalty (λ = {gm["lam"]}, chosen by leaving out one day at a time) '
    f'keeps estimates stable; values sum to zero, so an estimate of one point means a player adds one point per match more than the average of these {g["players"]} players.</li>'
    f'<li><b>Uncertainty.</b> Whole session days were resampled with replacement {K("boot")} times and the model refitted each time; the middle {K("ci")} of refits gives each interval '
    f'and the rank probabilities.</li>'
    f'<li><b>Form and change.</b> A recency-weighted fit (weights halve every {K("halflife")} session days) estimates current level. Separate fits of the first {g["half"]} and last {g["half2"]} days estimate change. '
    f'Daily adjusted performance — each day’s margins minus what partners and opponents predict — feeds the trend and consistency figures.</li>'
    f'<li><b>Elo.</b> Each player starts at {K("elostart")}. A team’s rating is the average of its two players; after each match both winners gain and both losers lose '
    f'{K("eloK")} × (result − expected), scaled up for wider margins. Elo depends on match order and needs time to settle, so it is a progression view, not the main estimate.</li>'
    f'<li><b>Expectations.</b> A predicted margin and the model’s leftover spread ({gm["sigma"]} points) give each team’s chance of winning. Predictions used for expected wins come from fits '
    f'that leave out the day being predicted.</li></ol>'), 'e'))
A(card('How well it works, and its limits', (
    f'<ul class="bx-list">'
    f'<li><b>Validation.</b> Predicting each day from the other {g["other"]}, the model’s average margin error is {gm["cvmae"]} points against {gm["base"]} for a no-information guess, '
    f'and it names the winner {gm["acc"]} of the time. It explains about {gm["r2"]} of the variation in margins; the rest is ordinary match-to-match variation. Elo picked {gm["elo_acc"]} of winners from W1 D4 on.</li>'
    f'<li><b>The workbook’s own rating</b> uses the same kind of fit and reports a similar error, and its fitted values agree with this model that Anto ({g["wban"]}) is ahead of Jothi Sai ({g["wbjs"]}); '
    f'this model has Anto first in {PF_["Anto"]["pfirst"]} of resamples. Two differences on the whole-number scale: it puts Anto and Jothi Sai level at 5, '
    f'although the season estimates are {fe("m.ajgap", sg(E["Anto"]["adj"] - E["Jothi Sai"]["adj"]), "Anto season estimate minus Jothi Sai season estimate.")} points per match apart; and it rates Dinesh above Pawan, '
    + ('which matches the recency-weighted fit' if E['Dinesh']['recent_adj'] > E['Pawan']['recent_adj'] else 'which neither the season fit nor the recency-weighted fit supports')
    + f' (recent: Dinesh {PF_["Dinesh"]["radj"]}, Pawan {PF_["Pawan"]["radj"]}).</li>'
    f'<li><b>Additive assumption.</b> The model treats a pair as the sum of two players. The partnership tab checks for chemistry directly and finds none beyond chance.</li>'
    f'<li><b>Constant ability.</b> The season estimate assumes a player’s level is fixed; the recency and half-season fits relax that.</li>'
    f'<li><b>No rally data.</b> Only final scores exist, so nothing here says anything about technique, fitness or tactics.</li>'
    f'<li><b>Small samples.</b> Players have {fm("m.minP", num(min(PL[p]["P"] for p in P)), "Fewest matches played by any player.")}–{fm("m.maxP", num(max(PL[p]["P"] for p in P)), "Most matches played by any player.")} matches. '
    f'Season estimates are good to about {g["ciw"]} points; pair and head-to-head figures are much less certain.</li></ul>'), 'e'))
A('</div>')
A('</section>')

# ================================================================ RANKINGS
A('<section class="bx-sec" id="rankings" data-panel="rankings" hidden>')
A('<h2>Player rankings</h2>')
A('<p class="bx-prose">Eight separate rankings, each on a stated basis. Where neighbours cannot be separated statistically the reason column says so. Click a heading to re-sort.</p>')
RANKCATS = [('overall', 'Overall season performance'), ('form', 'Current form'), ('contribution', 'Individual contribution'), ('consistency', 'Consistency'),
            ('knockout', 'Knockout performance'), ('partnership', 'Partnership performance'), ('improved', 'Most improved'), ('clutch', 'Best clutch performer')]
A('<div class="bx-grid bx-grid-rank">')
for cid, lbl in RANKCATS:
    A(card(lbl, table('rankings', 'key', [('rank', '#', 'int', True), ('player', 'Player', 'text', False), ('metric', 'Measure', 'text', True), ('basis', 'Why', 'text', False)],
                      where=f'category={cid}', sort='rank'), None, None, cid=f'rk-{cid}'))
A('</div>')
A(card('Final comparison', table('comparison', 'player', [
    ('player', 'Player', 'text', False), ('record', 'Season W–L', 'text', True), ('win_pct', 'Win %', 'pct', True), ('dpm', 'Diff / match', 's2', True),
    ('recent_record', 'Last 20', 'text', True), ('recent_dpm', 'Last 20 / match', 's2', True), ('adj', 'Adjusted', 's2', True), ('recent_adj', 'Recent adjusted', 's2', True),
    ('elo', 'Elo', 'int', True), ('wb_now', 'Rating', 'int', True), ('ko_record', 'Knockout', 'text', True), ('titles', 'Titles', 'int', True),
    ('consistency', 'Consistency', 'text', False), ('trend', 'Trend', 'text', False)], sort='-adj'), 'm',
    'Adjusted, recent adjusted, Elo, consistency and trend are estimates; the rest are counts.', cid='cmp', wide=True))
x = PF_
A(card('Verdicts', (
    f'<dl class="bx-awards">'
    f'<div><dt>Best overall player</dt><dd><b>Anto</b> — best record, points difference, titles and adjusted estimate; first in {x["Anto"]["pfirst"]} of resamples.</dd></div>'
    f'<div><dt>Best current form</dt><dd><b>Anto</b> — recency-weighted {x["Anto"]["radj"]}, last 20 {x["Anto"]["rrec"]}. John is hottest relative to John’s own season (last 20 {x["John"]["rdpm"]} per match against {x["John"]["dpm"]}).</dd></div>'
    f'<div><dt>Most improved</dt><dd><b>John</b> — {x["John"]["chg"]} between halves, trend {x["John"]["tr"]}, rating {x["John"]["wb0"]} → {x["John"]["wb1"]}, and the {SH(LAST)} title. Dinesh is next ({x["Dinesh"]["chg"]}, best adjusted week in Week 7).</dd></div>'
    f'<div><dt>Most consistent</dt><dd><b>Jothi Sai</b> — the steadiest week-to-week level, though Anto, John and Pawan are within chance of Jothi Sai. Anto has the most consistent results.</dd></div>'
    f'<div><dt>Strongest partnership player</dt><dd><b>Anto</b> — every one of Anto’s partners does better with Anto than without (average {x["Anto"]["upl"]} per match).</dd></div>'
    f'<div><dt>Greatest improvement potential</dt><dd><b>Dinesh</b> — already rising, with the best knockout record and a measurable gap between rounds 1–3 ({x["Dinesh"]["early"]}) and later rounds ({x["Dinesh"]["late"]}). '
    f'Closing that gap alone would move Dinesh clear of Pratap.</dd></div></dl>'), None, wide=True))
A('</section>')

# ================================================================ STRENGTHS
A('<section class="bx-sec" id="strengths" data-panel="strengths" hidden>')
A('<h2>Strengths, weaknesses and targets</h2>')
A('<p class="bx-prose">Everything here comes from scores. Training priorities name the match situations the numbers point to; they do not diagnose technique, footwork or fitness, which scores cannot show. '
  'Each target is set from the player’s own season and recent figures shown beside it.</p>')
SW = {}
x = PF_
ANTO_LOW = min(partner_rows('Anto'), key=lambda q: q['vs_exp'])['partner']
SW['Anto'] = dict(
    s=f'Dominant qualifier level: {x["Anto"]["q"]}, {x["Anto"]["qd"]} per match, top of the table on {x["Anto"]["top"]} days — and the only player who breaks even against strong pairs ({band_fact("Anto", "strong")}).',
    w=f'Finals conversion: {x["Anto"]["fin"]} against {x["Anto"]["fine"]} expected ({x["Anto"]["finv"]}). ' + ('That is the most finals lost by anyone in the group.' if all(PL[q]['fin_L'] < PL['Anto']['fin_L'] for q in P if q != 'Anto') else 'No one has lost more finals.'),
    imp=f'Results with {ANTO_LOW} ({partner_fact("Anto", ANTO_LOW)}) are below what the pair should produce ({partner_fact("Anto", ANTO_LOW, "vs")} per match), though that is within chance.',
    tr=f'Flat at a high level: trend {x["Anto"]["tr"]}, recency-weighted {x["Anto"]["radj"]} against {x["Anto"]["adj"]} for the season.',
    pri=['Match-play under final conditions: games started from level late scores, against the strongest available pairs.',
         'Keep partner-neutral habits: Anto’s results hold up with weak partners, so priority is maintaining that rather than changing anything.'])
SW['Jothi Sai'] = dict(
    s=f'Knockouts: eliminators {x["Jothi Sai"]["el"]} and knockouts {x["Jothi Sai"]["ko"]} ({x["Jothi Sai"]["kov"]} above expectation). Jothi Sai also faced the hardest schedule in the group.',
    w=f'Heavy defeats: {x["Jothi Sai"]["heavy"]} losses by eight or more ({x["Jothi Sai"]["heavyp"]}), more than twice Anto’s rate. Close matches {x["Jothi Sai"]["c3"]}.',
    imp=f'With Dinesh the pair underperforms ({partner_fact("Jothi Sai", "Dinesh")}, {partner_fact("Jothi Sai", "Dinesh", "vs")} per match versus expectation).',
    tr=f'Steady, slightly up recently: last 20 {x["Jothi Sai"]["rrec"]} ({x["Jothi Sai"]["rdpm"]} per match) against {x["Jothi Sai"]["dpm"]} for the season; Week 6 the best week.',
    pri=['Limiting runs of lost points once a game turns: practise games started from a deficit.',
         'Close-game finishing: games started level late in the game.'])
SW['John'] = dict(
    s=f'Pressure: close matches {x["John"]["c3"]} ({x["John"]["c3v"]}), matches past 21 {x["John"]["deuce"]}, finals {x["John"]["fin"]}.',
    w=f'Volatility: {x["John"]["heavy"]} heavy defeats ({x["John"]["heavyp"]}) and a poor record against Jothi Sai ({opp_fact("John", "Jothi Sai")}).',
    imp=f'Results with Bhanu ({partner_fact("John", "Bhanu")}) are the worst of John’s regular partnerships.',
    tr=f'Rising: {x["John"]["h1"]} → {x["John"]["h2"]} between halves, Week 6 {week_fact("John", 6, "rec")} at {week_fact("John", 6, "dpm")} per match.',
    pri=['Consolidate the Week 6 level across a full month before treating it as the new baseline; Weeks 7 and 8 so far were single days, both above it.',
         'Reducing heavy defeats: games started from a deficit.'])
SW['Pawan'] = dict(
    s=f'Partnering the strong players: with Anto {partner_fact("Pawan", "Anto")} and with John {partner_fact("Pawan", "John")}, both better than the pairs should produce, and a winning qualifier record over the season ({x["Pawan"]["q"]}).',
    w=f'Current form: Week 7 {week_fact("Pawan", 7, "rec")}, {week_fact("Pawan", 7, "diff")} (adjusted {week_fact("Pawan", 7, "adj")} per match), the worst week of Pawan’s season; the recency-weighted estimate is down to {x["Pawan"]["radj"]}.',
    imp=f'Finals: {x["Pawan"]["fin"]} ({x["Pawan"]["finv"]} versus expectation); knockouts overall {x["Pawan"]["ko"]}.',
    tr=f'Falling: {x["Pawan"]["h1"]} → {x["Pawan"]["h2"]} between halves; last 20 {x["Pawan"]["rrec"]} at {x["Pawan"]["rdpm"]} per match; Weeks 6 and 7 the two weakest weeks.',
    pri=['Final-condition match play: single games to 21 against strong pairs with a result recorded.',
         'Close-game finishing: the close-match record is {0}.'.format(x["Pawan"]["c3"])])
SW['Dinesh'] = dict(
    s=f'Knockouts: {x["Dinesh"]["ko"]} ({x["Dinesh"]["kov"]} above expectation) and finals {x["Dinesh"]["fin"]}.',
    w=f'Early rounds: adjusted {x["Dinesh"]["early"]} in rounds 1–3 against {x["Dinesh"]["late"]} later, and a losing qualifier record ({x["Dinesh"]["q"]}).',
    imp=f'Against strong pairs: {band_fact("Dinesh", "strong")} ({band_fact("Dinesh", "strong", "dpm")} per match).',
    tr=f'Rising but noisy: {x["Dinesh"]["h1"]} → {x["Dinesh"]["h2"]} between halves; trend {x["Dinesh"]["tr"]}; Week 7 the best adjusted week ({week_fact("Dinesh", 7, "adj")}).',
    pri=['Start-of-session readiness: the early-round gap is measured, its cause is not; a structured warm-up game before round 1 is a low-cost test.',
         'Match play against the strongest pairs.'])
SW['Pratap'] = dict(
    s=f'Close matches: {x["Pratap"]["c3"]} ({x["Pratap"]["c3v"]} versus expectation) — Pratap competes in tight games.',
    w=f'Knockouts {x["Pratap"]["ko"]} and eliminators {x["Pratap"]["el"]}; against strong pairs {band_fact("Pratap", "strong")} with {band_fact("Pratap", "strong", "exp")} expected.',
    imp=f'With Dinesh ({partner_fact("Pratap", "Dinesh")}) and Bhanu ({partner_fact("Pratap", "Bhanu")}) the results are heavy losses.',
    tr=f'Declining, now steadying: {x["Pratap"]["h1"]} → {x["Pratap"]["h2"]}; Week 6 {week_fact("Pratap", 6, "rec")}, {week_fact("Pratap", 6, "diff")}, including {x["Pratap"]["sl"]} straight losses; Week 7 back to {week_fact("Pratap", 7, "rec")}.',
    pri=['Find what changed after Week 4, the best week of Pratap’s season; the scores show when, not why.',
         'Match play against strong pairs, where Pratap’s results fall short of expectation.'])
SW['Bhanu'] = dict(
    s=f'Holding up beside the strongest players: with Anto ({partner_fact("Anto", "Bhanu", "vs")} per match) and Jothi Sai ({partner_fact("Jothi Sai", "Bhanu", "vs")}) the pair beats expectation.',
    w=f'Close matches: {x["Bhanu"]["c3"]} against {x["Bhanu"]["c3e"]} expected ({x["Bhanu"]["c3v"]}).',
    imp=f'Heavy defeats: {x["Bhanu"]["heavy"]} losses by eight or more ({x["Bhanu"]["heavyp"]}).',
    tr=f'Low and variable: Weeks 4–5 were the worst, Week 6 the best adjusted week ({week_fact("Bhanu", 6, "adj")}), Week 7 back down ({week_fact("Bhanu", 7, "adj")}); last 20 {x["Bhanu"]["rrec"]}.',
    pri=['Close-game finishing: games started level late in the game.',
         'Limiting heavy defeats: games started from a deficit.'])
TARGETS = []
def tgt(p, metric, season, recent, target):
    TARGETS.append(dict(key=f'{p}|{len([t for t in TARGETS if t["player"] == p]) + 1}', player=p, metric=metric, season=season, recent=recent, target=target))

def rr(p, n=20):
    vs = [m for m in M if p in m['A'] or p in m['B']][-n:]
    return vs
for p in P:
    xx = PL[p]; rp = PR[p]
for p, rows in {
    'Anto': [('Finals won', xx_ := PL['Anto']['fin_record'], '—', 'Two of every three'),
             ('Qualifier points difference per match', sg(PL['Anto']['q_dpm']), '—', 'At least +3.00'),
             ('Share of matches lost by 8+', pct(PL['Anto']['heavy_rate']), '—', '8% or less')],
    'Jothi Sai': [('Qualifier win rate', pct(PL['Jothi Sai']['q_pct']), '—', '58% or more'),
                  ('Share of matches lost by 8+', pct(PL['Jothi Sai']['heavy_rate']), '—', '12% or less'),
                  ('Close matches won (3 or fewer)', PR['Jothi Sai']['c3_record'], '—', 'Half or more')],
    'John': [('Points difference per match', sg(PL['John']['dpm']), sg(PL['John']['recent_dpm']), 'At least +1.50'),
             ('Win rate', pct(PL['John']['win_pct']), pct(PL['John']['recent_W'] / 20), '60% or more'),
             ('Share of matches lost by 8+', pct(PL['John']['heavy_rate']), '—', '10% or less')],
    'Pawan': [('Finals won', PL['Pawan']['fin_record'], '—', 'Half or more'),
              ('Points difference per match', sg(PL['Pawan']['dpm']), sg(PL['Pawan']['recent_dpm']), 'At least +0.50'),
              ('Share of matches lost by 8+', pct(PL['Pawan']['heavy_rate']), '—', '12% or less')],
    'Dinesh': [('Qualifier win rate', pct(PL['Dinesh']['q_pct']), '—', '45% or more'),
               ('Adjusted gap, rounds 1–3 vs later', sg(E['Dinesh']['early_adj'] - E['Dinesh']['late_adj']), '—', 'Halve it'),
               ('Win rate against strong pairs', pct(BAND['Dinesh|strong']['win_pct']), '—', '30% or more')],
    'Pratap': [('Points difference per match', sg(PL['Pratap']['dpm']), sg(PL['Pratap']['recent_dpm']), 'At least −1.00'),
               ('Longest losing run', num(PL['Pratap']['worst_loss_streak']), '—', 'Three or fewer'),
               ('Win rate against strong pairs', pct(BAND['Pratap|strong']['win_pct']), '—', '25% or more')],
    'Bhanu': [('Close matches won (3 or fewer)', pct(PR['Bhanu']['c3_pct']), '—', '35% or more'),
              ('Share of matches lost by 8+', pct(PL['Bhanu']['heavy_rate']), '—', '25% or less'),
              ('Points difference per match', sg(PL['Bhanu']['dpm']), sg(PL['Bhanu']['recent_dpm']), 'At least −3.00')],
}.items():
    for metric, season, recent, target in rows:
        tgt(p, metric, season, recent, target)

A('<div class="bx-grid">')
for p in P:
    d = SW[p]
    pri = ''.join(f'<li>{t}</li>' for t in d['pri'])
    body = (f'<dl class="bx-sw"><div><dt>Biggest strength</dt><dd>{d["s"]}</dd></div><div><dt>Biggest weakness</dt><dd>{d["w"]}</dd></div>'
            f'<div><dt>Also worth work</dt><dd>{d["imp"]}</dd></div><div><dt>Trend</dt><dd>{d["tr"]}</dd></div>'
            f'<div><dt>Training priorities</dt><dd><ul class="bx-list">{pri}</ul></dd></div></dl>'
            + table('targets', 'key', [('metric', 'Next-month target', 'text', False), ('season', 'Season', 'text', True), ('recent', 'Last 20', 'text', True), ('target', 'Target', 'text', True)],
                    where=f'player={p}', sort='key'))
    A(card(p, body, None, cid=f'sw-{SLUG[p]}'))
A('</div>')
A('</section>')

# ================================================================ OUTLOOK
A('<section class="bx-sec" id="outlook" data-panel="outlook" hidden>')
A('<h2>Recommendations and next-season outlook</h2>')
A('<div class="bx-grid">')
A(card('Projected order next season', table('estimates', 'player', [('player', 'Player', 'text', False), ('recent_adj', 'Current level', 's2', True),
                                                                     ('recent_lo', 'Low', 's2', True), ('recent_hi', 'High', 's2', True),
                                                                     ('neutral_win_recent', 'Neutral-draw win %', 'pct0', True), ('p_top3', 'Chance of top three', 'pct0', True)], sort='-recent_adj'),
       'e', 'Current level is the recency-weighted estimate. Neutral-draw win % assumes random partners and opponents; under the workbook’s balanced draw everyone’s raw win rate will sit closer to even.'))
A(card('Predictions', (
    f'<ul class="bx-list">'
    f'<li><b>Anto stays first.</b> Every model has Anto ahead, and Anto’s current level ({x["Anto"]["radj"]}) is the highest. Expect Anto to keep topping qualifier tables; finals are where there is most still to gain.</li>'
    f'<li><b>Jothi Sai second, John closing.</b> Jothi Sai ({x["Jothi Sai"]["radj"]}) is still ahead of John ({x["John"]["radj"]}) on current level, but the intervals overlap and John’s {SH(LAST)} title narrowed the gap.</li>'
    f'<li><b>Fourth place is open.</b> Pawan ({x["Pawan"]["radj"]}) and Dinesh ({x["Dinesh"]["radj"]}) are almost level on current form, and their intervals overlap heavily; season estimates have Pawan fourth.</li>'
    f'<li><b>Dinesh stays ahead of Pratap.</b> Season estimates are level, but current levels ({x["Dinesh"]["radj"]} against {x["Pratap"]["radj"]}) and trends favour Dinesh.</li>'
    f'<li><b>Bhanu remains seventh</b> ({x["Bhanu"]["radj"]}); the gap to sixth is about three points a match, and the last {K("recentN")} matches have not narrowed it.</li>'
    f'<li><b>Uncertainty.</b> These are projections from {g["n"]} matches. A month of new results will move them, and any player whose interval overlaps a neighbour’s could swap places.</li></ul>'), 'e'))
A('</div>')
A(card('Recommendations for the group and the workbook', (
    f'<ul class="bx-list">'
    f'<li><b>Record every game of a final.</b> The Day 1 decider is missing, so that title is credited on game 1 alone.</li>'
    f'<li><b>Check the {g["oddn"]} scores of {g["odd"]}</b> (W3 D2 round 6, W6 D1 round 5, W6 D1 final). Past deuce a game ends the moment one side leads by two, so it cannot finish three points apart above {K("game")}.</li>'
    f'<li><b>Use a finer rating scale.</b> Anto and Jothi Sai both sit at 5 although their estimates differ by {fe("m.ajgap", sg(E["Anto"]["adj"] - E["Jothi Sai"]["adj"]), "Anto season estimate minus Jothi Sai season estimate.")} points per match, '
    f'and Pawan and Pratap share 2 although they differ by {fe("m.pwpt", sg(E["Pawan"]["adj"] - E["Pratap"]["adj"]), "Pawan season estimate minus Pratap season estimate.")}; whole-number steps also cap movement at one a day.</li>'
    f'<li><b>Keep balancing, but rotate the top two.</b> Jothi Sai faced Anto {opp_fact("Jothi Sai", "Anto", "n")} times and partnered Anto only {partner_fact("Jothi Sai", "Anto", "n")}. More Anto + Jothi Sai pairings would give information on that partnership and spread the hardest draws.</li>'
    f'<li><b>Record point-by-point scores for knockout matches</b> if anyone is willing: it is the only way to measure comebacks and late-game finishing directly.</li>'
    f'<li><b>Decide whether to keep the Bhanu–Dinesh exclusion.</b> It kept that pairing off court from W6 D2 until W7 D3, when the five-player rotation needed it; the pair lost both matches and is now {fm("pr.db.rec", dbp["record"], "Wins–losses as partners.")}. Either keep it on six- and seven-player days or drop it so the pairing can be measured.</li></ul>'), 'm', wide=True))
A('</section>')

# ================================================================ DATA CHECKS
A('<section class="bx-sec" id="data" data-panel="data" hidden>')
A('<h2>Data checks and issues</h2>')
A(f'<p class="bx-prose">All {g["n"]} matches were read from the {g["days"]} day tabs and compared row by row with the All matches tab. That tab lists {fm("g.nam", num(N_AM), "Matches listed in the All matches tab.")} of them — it stops at {SH(sorted(AM_DAYS, key=days.index)[-1])}, so {", ".join(SH(d) for d in NOT_IN_AM)} {"is" if len(NOT_IN_AM) == 1 else "are"} not yet in the workbook’s season totals — and for those every team, score and stage agrees. '
  f'Every Season-tab total was then recomputed from the same matches; all agree exactly. This report adds {", ".join(SH(d) for d in NOT_IN_AM)} on top. Note claims checked against the data (for example Anto’s unbeaten qualifier days and title count) also agree. '
  f'The issues below do not change any total but affect how some figures should be read.</p>')
A(card('Season tab against recomputed totals', table('checks', 'player', [('player', 'Player', 'text', False), ('matches', 'Matches', 'text', True), ('wins', 'Wins', 'text', True),
                                                                         ('points_for', 'For', 'text', True), ('points_against', 'Against', 'text', True), ('qual_wins', 'Qualifier wins', 'text', True),
                                                                         ('ko', 'Knockout W of P', 'text', True), ('finals', 'Finals', 'text', True), ('titles', 'Titles', 'text', True), ('result', 'Result', 'text', False)]),
       'm', f'Each cell reads workbook = recomputed, over the days the Season tab covers (W1 D1–{SH(sorted(AM_DAYS, key=days.index)[-1])}).', wide=True))
A(card('Issues found', (
    f'<ol class="bx-list bx-ol">'
    f'<li><b>Day 1 final incomplete.</b> Only the first game (Pratap + Jothi Sai {g["d1"]}) was recorded; the decider was not. The Season tab counts that game as the title and as a final. '
    f'Jothi Sai’s titles are {PF_["Jothi Sai"]["titles"]} counted, {PF_["Jothi Sai"]["tconf"]} confirmed; Pratap’s {PF_["Pratap"]["titles"]} counted, {PF_["Pratap"]["tconf"]} confirmed.</li>'
    f'<li><b>Impossible scores.</b> {g["odd"]} appears {g["oddn"]} times: W3 D2 round 6, W6 D1 round 5 and the W6 D1 final. The W3 D2 note calls it “a two-point lead”, which it is not. Each is used as recorded; the effect is at most one point per match.</li>'
    f'<li><b>Days not in the workbook’s totals.</b> The All matches tab stops at {SH(sorted(AM_DAYS, key=days.index)[-1])}. '
    + (f'{", ".join(SH(d) for d in IN_WB_NOT_AM)} {"has its" if len(IN_WB_NOT_AM) == 1 else "have their"} own tab with every score but {"is" if len(IN_WB_NOT_AM) == 1 else "are"} not counted by the Season tab. ' if IN_WB_NOT_AM else '')
    + (f'{", ".join(SH(d) for d in EXTRA)} {"is" if len(EXTRA) == 1 else "are"} not in the workbook at all: the scores were entered from the scoring app into extra-days.json. ' if EXTRA else '')
    + f'This report counts all of them, so its totals run {N - N_AM} matches ahead of the Season tab until the workbook catches up.</li>'
    f'<li><b>No starting rating for Dinesh.</b> Dinesh missed W1 D1 and W1 D2; the first rating ({PF_["Dinesh"]["wb0"]}) is from W1 D3.</li>'
    f'<li><b>Unequal attendance and weeks.</b> Matches per player range from {fm("m.minP", num(min(PL[p]["P"] for p in P)), "Fewest matches played by any player.")} to '
    f'{fm("m.maxP", num(max(PL[p]["P"] for p in P)), "Most matches played by any player.")}, and weeks run {g["wkrange"]} days. All comparisons use per-match rates.</li>'
    f'<li><b>Knockout formats changed</b> several times (one eliminator, three eliminators, recount qualification, and on W7 D3 a five-player format with seed 1 going straight to the final). Eliminator wins do not always equal qualification for the final.</li>'
    f'<li><b>Non-random pairings.</b> The draw is built from ratings to balance teams. Raw partner and opponent records are therefore confounded by the draw, which is why the adjusted model is used.</li>'
    f'<li><b>Unsigned projections.</b> The workbook’s “Projected margin” column (from W2 D3, qualifier rounds only) gives size but not direction, so it cannot be checked against results.</li>'
    f'<li><b>Leftover template text.</b> Several played tabs still say “Fill in the YELLOW score cells only”, and W1 D5 carries a planning note about projected rounds. Cosmetic only.</li></ol>'
    f'<p class="bx-note">Day labels: W1 D1–W1 D5 are the workbook tabs “Day 1”–“Day 5”; later tabs keep their own names.</p>'), 'm', wide=True))
A(card('Match log', table('matches', 'n', [('n', '#', 'int', True), ('day', 'Day', 'text', False), ('stage', 'Stage', 'text', False), ('label', 'Match', 'text', False),
                                          ('team_a', 'Team A', 'text', False), ('score', 'Score', 'text', True), ('team_b', 'Team B', 'text', False),
                                          ('margin', 'Margin', 'int', True), ('pred_margin', 'Predicted', 's1', True)], sort='n', maxh=True),
       'm', 'Every match as recorded. Predicted is the out-of-sample model margin for team A (an estimate).', wide=True))
A('</section>')

A('</div>')
A('<script src="app.js"></script>')
page = '\n'.join(html)

# ---------------------------------------------------------------- rankings dataset
def rk(cat, order, metric_fn, basis_fn):
    rows = []
    for i, p in enumerate(order):
        rows.append(dict(key=f'{cat}|{i + 1}', category=cat, rank=i + 1, player=p, metric=metric_fn(p), basis=basis_fn(p, i)))
    return rows

rankings = []
o_overall = sorted(P, key=lambda p: (-PL[p]['win_pct']))
rankings += rk('overall', o_overall, lambda p: f'{PL[p]["record"]} · {pct(PL[p]["win_pct"])} · {sg(PL[p]["dpm"])}/match · {PL[p]["titles"]} titles',
               lambda p, i: {
                   'Anto': 'Leads every season measure: wins, points difference and titles.',
                   'Jothi Sai': 'Second on win rate and points difference, most titles per day after Anto, despite the hardest draw.',
                   'John': 'Level with Jothi Sai on win rate with one more title; slightly lower points difference per match.',
                   'Pawan': 'Still positive on every measure, but lowest of the four winning-record players after a poor Week 7.',
                   'Dinesh': f'Just under break-even; {PL["Dinesh"]["titles"]} titles help, but the qualifier record is losing.',
                   'Pratap': 'Clearly negative points difference; strong start undone by Week 6.',
                   'Bhanu': 'Lowest on every measure.'}[p])
o_form = sorted(P, key=lambda p: -E[p]['recent_adj'])
rankings += rk('form', o_form, lambda p: f'{sg(E[p]["recent_adj"])} recent · last 20 {PL[p]["recent_record"]}',
               lambda p, i: {
                   'Anto': 'Highest recency-weighted estimate and best last-20 record.',
                   'Jothi Sai': 'Second on current level; last 20 better than the season.',
                   'John': 'Interval overlaps Jothi Sai; best last-20 points difference after Anto.',
                   'Pawan': 'Fourth on current level, just ahead of Dinesh; Week 7 was the low point and the latest day brought a title.',
                   'Dinesh': 'Fifth on current level: a poor latest day undid part of Week 7’s gain.',
                   'Pratap': 'Steadier lately after the Week 6 slump, but still sixth on current level.',
                   'Bhanu': 'Seventh on level, and the last 20 are below the season average.'}[p])
o_con = sorted(P, key=lambda p: -E[p]['adj'])
rankings += rk('contribution', o_con, lambda p: f'{sg(E[p]["adj"])} ({sg(E[p]["adj_lo"])} to {sg(E[p]["adj_hi"])})',
               lambda p, i: {
                   'Anto': f'First in {pct(E[p]["p_first"], 0)} of resamples.',
                   'Jothi Sai': f'Second in {pct(md["rankprob"]["Jothi Sai"][1], 0)} of resamples.',
                   'John': 'Third; interval overlaps Pawan’s.',
                   'Pawan': 'Fourth; interval spans zero.',
                   'Dinesh': 'Statistically tied with Pratap.',
                   'Pratap': 'Statistically tied with Dinesh.',
                   'Bhanu': 'Clearly last; about three points below the next player.'}[p])
dr = {p: r_ for r_, p in enumerate(sorted(P, key=lambda p: E[p]['daily_sd']))}
wr = {p: r_ for r_, p in enumerate(sorted(P, key=lambda p: E[p]['weekly_sd']))}
o_cons = sorted(P, key=lambda p: (dr[p] + wr[p], -PL[p]['pos_days'] / PL[p]['days'], E[p]['excess_sd']))
rankings += rk('consistency', o_cons, lambda p: f'daily spread {E[p]["daily_sd"]:.2f} · weekly {E[p]["weekly_sd"]:.2f}',
               lambda p, i: {
                   'Jothi Sai': 'Steadiest from week to week; daily swings within chance.',
                   'John': 'Daily swings within chance; one big upward week (Week 6).',
                   'Pawan': 'Daily swings within chance, but the Week 6–7 slide widens the weekly spread.',
                   'Anto': 'Within chance on both; also the most consistent results (positive on most days).',
                   'Dinesh': 'Slightly more variable than chance alone.',
                   'Pratap': 'Slightly more variable than chance; widest week-to-week spread.',
                   'Bhanu': 'Clearly more variable day to day than chance explains.'}[p])
o_ko = sorted(P, key=lambda p: -PL[p]['ko_pct'])
rankings += rk('knockout', o_ko, lambda p: f'{PL[p]["ko_record"]} · finals {PL[p]["fin_record"]} · {sg(PR[p]["ko_vs"], 1)} vs expected',
               lambda p, i: {
                   'Dinesh': 'Best knockout win rate and furthest above expectation.',
                   'Jothi Sai': f'Eliminators {PL["Jothi Sai"]["el_record"]}; finals just below even.',
                   'Anto': 'Most knockout wins in the group, but below expectation in finals.',
                   'John': 'About as expected; winning finals record.',
                   'Pawan': 'Losing knockout record, finals the weakest part.',
                   'Pratap': 'Eliminators a clear weakness.',
                   'Bhanu': 'Lowest win rate, roughly what team strength predicts.'}[p])
o_part = sorted(P, key=lambda p: -E[p]['uplift'])
rankings += rk('partnership', o_part, lambda p: f'{sg(E[p]["uplift"])} partner uplift · {sum(1 for r_ in PART[p] if r_["P"] >= 10 and r_["dpm"] > 0)} of {sum(1 for r_ in PART[p] if r_["P"] >= 10)} regular pairs positive',
               lambda p, i: {
                   'Anto': 'Every partner does better with Anto than without.',
                   'Jothi Sai': 'Lifts five of six partners; Dinesh the exception.',
                   'John': 'Lifts five of six; Bhanu the exception.',
                   'Pawan': 'Lifts four of six partners.',
                   'Dinesh': 'Only John does better with Dinesh than without; the others do worse.',
                   'Pratap': 'Partners average worse with Pratap than without.',
                   'Bhanu': 'Partners do much worse with Bhanu; the pairing system offsets this with stronger partners.'}[p])
def imp_key(p):
    a1 = sorted(P, key=lambda q: -E[q]['change']).index(p); a2 = sorted(P, key=lambda q: -E[q]['trend21']).index(p)
    return (a1 + a2, -(PL[p]['wb_now'] - (md['wbrating'][p][next(i for i, v in enumerate(md['wbrating'][p]) if v is not None)])))
o_imp = sorted(P, key=imp_key)
rankings += rk('improved', o_imp, lambda p: f'{sg(E[p]["change"])} halves · {sg(E[p]["trend21"], 1)} trend',
               lambda p, i: {
                   'John': 'Up on both measures and up two workbook steps.',
                   'Dinesh': 'Up on both measures after a strong Week 7, though the latest day dipped; within chance.',
                   'Jothi Sai': 'Small rise, mostly late.',
                   'Anto': 'Flat at the top.',
                   'Pawan': 'Down on both measures after Weeks 6–7; the sharpest recent fall.',
                   'Bhanu': 'Mid-season dip; the Week 6 recovery did not hold in Week 7.',
                   'Pratap': 'Down over the season, though Week 7 was level.'}[p])
o_cl = sorted(P, key=lambda p: -PR[p]['clutch'])
rankings += rk('clutch', o_cl, lambda p: f'{sg(PR[p]["clutch"], 1)} wins (close {sg(PR[p]["c3_vs"], 1)}, KO {sg(PR[p]["ko_vs"], 1)})',
               lambda p, i: {
                   'John': 'Well above expectation in close matches; knockouts as expected.',
                   'Dinesh': 'Knockout wins well above expectation.',
                   'Jothi Sai': 'Knockouts above expectation; close matches as expected.',
                   'Pratap': 'Good in close matches; knockouts a little below expectation.',
                   'Anto': 'Close matches above, knockouts below; nets slightly negative.',
                   'Pawan': 'Below in both, mainly finals.',
                   'Bhanu': 'Close-match losses far beyond expectation.'}[p])

# ---------------------------------------------------------------- comparison
def cons_tier(p):
    ex = E[p]['excess_sd']
    return 'Within chance' if ex < 0.5 else ('Slightly variable' if ex < 1.5 else 'Variable')
def trend_lbl(p):
    return {'John': 'Improving', 'Dinesh': 'Improving', 'Pratap': 'Declining, steadying', 'Pawan': 'Recent slump',
            'Anto': 'Steady', 'Jothi Sai': 'Steady', 'Bhanu': 'Steady, low'}[p]
comparison = [dict(player=p, record=PL[p]['record'], win_pct=PL[p]['win_pct'], dpm=PL[p]['dpm'], recent_record=PL[p]['recent_record'],
                   recent_dpm=PL[p]['recent_dpm'], adj=E[p]['adj'], recent_adj=E[p]['recent_adj'], elo=E[p]['elo'], wb_now=PL[p]['wb_now'],
                   ko_record=PL[p]['ko_record'], titles=PL[p]['titles'], consistency=cons_tier(p), trend=trend_lbl(p)) for p in P]

# ---------------------------------------------------------------- checks
ss = md['season_sheet']
checks = []
def _tot(p):
    t = dict(P=0, W=0, PF=0, PA=0, q_W=0, ko_W=0, ko_P=0, fin_P=0, titles=0)
    for m in M:
        if m['day'] not in AM_DAYS:
            continue
        if p in m['A']:
            pf_, pa_ = m['sa'], m['sb']
        elif p in m['B']:
            pf_, pa_ = m['sb'], m['sa']
        else:
            continue
        won = pf_ > pa_
        t['P'] += 1; t['W'] += won; t['PF'] += pf_; t['PA'] += pa_
        if m['stage'] == 'Qualifier':
            t['q_W'] += won
        else:
            t['ko_P'] += 1; t['ko_W'] += won
        if m['stage'] == 'Final':
            t['fin_P'] += 1; t['titles'] += won
    return t
for p in P:
    x = _tot(p); w = ss[p]
    def c(a, b):
        return f'{a} = {b}' if a == b else f'{a} ≠ {b}'
    row = dict(player=p, matches=c(w['P'], x['P']), wins=c(w['W'], x['W']), points_for=c(w['F'], x['PF']), points_against=c(w['A'], x['PA']),
               qual_wins=c(w['QW'], x['q_W']), ko=c(f'{w["KOW"]} of {w["KOP"]}', f'{x["ko_W"]} of {x["ko_P"]}'), finals=c(w['Fin'], x['fin_P']), titles=c(w['T'], x['titles']))
    row['result'] = 'All agree' if all('≠' not in v for k, v in row.items() if k != 'player') else 'Mismatch'
    checks.append(row)

# ---------------------------------------------------------------- write
for name, rows in dict(facts=list(facts.values()), rankings=rankings, comparison=comparison, checks=checks, targets=TARGETS).items():
    json.dump(rows, open(f'{OUT}/{name}.json', 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
open('dash/index.html', 'w', encoding='utf-8').write(page)
print('index.html bytes', len(page.encode('utf-8')), 'facts', len(facts))
print([ (r['category'], r['rank'], r['player']) for r in rankings if r['category'] in ('consistency', 'improved')])
print(checks[0])
