import json, math, os, itertools
import numpy as np
from math import erf, sqrt

P = ['Anto', 'Jothi Sai', 'John', 'Pawan', 'Dinesh', 'Pratap', 'Bhanu']
IDX = {p: i for i, p in enumerate(P)}
md = json.load(open('model.json'))
rd = json.load(open('report_data.json'))
M, days = md['M'], md['days']
s = np.array(md['s']); sig = md['sigma']
loo = {int(k): v for k, v in md['loo_pred'].items()}
OUT = 'dash/data'
os.makedirs(OUT, exist_ok=True)


def Phi(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def ce(mu, k=3):
    a = Phi((k - mu) / sig) - Phi(-mu / sig)
    b = Phi(-mu / sig) - Phi((-k - mu) / sig)
    return a / (a + b)


def short(day):
    return ('W1 ' + day.replace('Day ', 'D')) if not day.startswith('W') else day.replace('Day ', 'D')


def r(x, n=2):
    return None if x is None else round(float(x), n)


def rec(w, l):
    return f'{w}–{l}'


def views(p):
    out = []
    for m in M:
        if p in m['A']:
            sg, mate, opp, pf, pa = 1, [x for x in m['A'] if x != p][0], m['B'], m['sa'], m['sb']
        elif p in m['B']:
            sg, mate, opp, pf, pa = -1, [x for x in m['B'] if x != p][0], m['A'], m['sb'], m['sa']
        else:
            continue
        out.append(dict(m=m, mate=mate, opp=opp, pf=pf, pa=pa, d=pf - pa, win=pf > pa, mu=sg * loo[m['i']],
                        imp=(pf - pa) - (s[IDX[mate]] - s[IDX[opp[0]]] - s[IDX[opp[1]]])))
    return out


V = {p: views(p) for p in P}

# ---------------- matches ----------------
matches = []
for k, m in enumerate(M):
    matches.append(dict(n=k + 1, day=short(m['day']), week=m['wk'], stage=m['stage'], label=m['label'],
                        team_a=' + '.join(m['A']), team_b=' + '.join(m['B']), score=f"{m['sa']}–{m['sb']}",
                        score_a=m['sa'], score_b=m['sb'],
                        winner=' + '.join(m['A'] if m['sa'] > m['sb'] else m['B']), margin=abs(m['sa'] - m['sb']),
                        pred_margin=r(loo[m['i']], 1)))

# ---------------- players (measured) ----------------
players, estimates, pressure, comparison = [], [], [], []
for p in P:
    o = rd['players'][p]; R = o['overall']; vs = V[p]; i = IDX[p]
    wb = o['wb']['sheet']; hist = o['wb']['hist']
    start = next((x for x in hist if x is not None), None)
    titles_conf = sum(1 for t in o['titles'] if not t['day1_uncertain'])
    rw = o['recent']
    players.append(dict(
        player=p, days=o['days_played'], P=R['n'], W=R['w'], L=R['l'], record=rec(R['w'], R['l']),
        win_pct=r(R['pct'], 3), win_lo=r(o['ci_pct'][0], 3), win_hi=r(o['ci_pct'][1], 3),
        PF=R['pf'], PA=R['pa'], diff=R['diff'], dpm=r(R['dpm']),
        avg_win_margin=r(R['avgW']), avg_loss_margin=r(R['avgL']),
        q_P=o['qual']['n'], q_W=o['qual']['w'], q_L=o['qual']['l'], q_record=rec(o['qual']['w'], o['qual']['l']),
        q_pct=r(o['qual']['pct'], 3), q_diff=o['qual']['diff'], q_dpm=r(o['qual']['dpm']),
        ko_P=o['ko']['n'], ko_W=o['ko']['w'], ko_L=o['ko']['l'], ko_record=rec(o['ko']['w'], o['ko']['l']),
        ko_pct=r(o['ko']['pct'], 3), ko_diff=o['ko']['diff'], ko_dpm=r(o['ko']['dpm']),
        el_record=rec(o['elim']['w'], o['elim']['l']), el_W=o['elim']['w'], el_L=o['elim']['l'],
        fin_P=o['final']['n'], fin_W=o['final']['w'], fin_L=o['final']['l'], fin_record=rec(o['final']['w'], o['final']['l']),
        fin_pct=r(o['final']['pct'], 3), titles=len(o['titles']), titles_confirmed=titles_conf,
        titles_via_elim=sum(1 for t in o['titles'] if t['via_elim']), top_seeds=o['top_seed'],
        # latest rating on court (includes extra-days.json ratings, which are newer than the Season tab)
        pos_days=o['pos_days'], wb_start=start, wb_now=next((x for x in reversed(hist) if x is not None), wb['now']),
        recent_record=rec(rw['w'], rw['l']), recent_W=rw['w'], recent_L=rw['l'], recent_dpm=r(rw['dpm']),
        heavy_losses=o['heavy_losses'], heavy_rate=r(o['heavy_losses'] / R['n'], 3), big_wins=o['big_wins'],
        best_win_streak=o['streaks']['best_w'], worst_loss_streak=o['streaks']['best_l'],
        current_streak=f"{o['streaks']['current'][0]}{o['streaks']['current'][1]}", sd_margin=r(o['sd_margin'])))

    # pressure (measured + expected)
    c = [v for v in vs if abs(v['d']) <= 3]; pc = [ce(v['mu']) for v in c]
    c5 = [v for v in vs if abs(v['d']) <= 5]
    ko = [v for v in vs if v['m']['stage'] != 'Qualifier']; pk = [Phi(v['mu'] / sig) for v in ko]
    fi = [v for v in vs if v['m']['stage'] == 'Final']; pf = [Phi(v['mu'] / sig) for v in fi]
    de = [v for v in vs if max(v['pf'], v['pa']) > 21]
    cw = sum(v['win'] for v in c); kw = sum(v['win'] for v in ko); fw = sum(v['win'] for v in fi)
    c3_vs = cw - sum(pc); ko_vs = kw - sum(pk)
    pressure.append(dict(
        player=p, c3_W=cw, c3_L=len(c) - cw, c3_record=rec(cw, len(c) - cw), c3_pct=r(cw / len(c), 3),
        c3_exp=r(sum(pc), 1), c3_vs=r(c3_vs, 1), c3_sd=r(sqrt(sum(x * (1 - x) for x in pc)), 1),
        c5_record=rec(sum(v['win'] for v in c5), len(c5) - sum(v['win'] for v in c5)),
        c5_pct=r(sum(v['win'] for v in c5) / len(c5), 3),
        deuce_record=rec(sum(v['win'] for v in de), len(de) - sum(v['win'] for v in de)),
        ko_record=rec(kw, len(ko) - kw), ko_exp=r(sum(pk), 1), ko_vs=r(ko_vs, 1),
        ko_sd=r(sqrt(sum(x * (1 - x) for x in pk)), 1),
        fin_record=rec(fw, len(fi) - fw), fin_exp=r(sum(pf), 1), fin_vs=r(fw - sum(pf), 1),
        clutch=r(c3_vs + ko_vs, 1), clutch_sd=r(sqrt(sum(x * (1 - x) for x in pc) + sum(x * (1 - x) for x in pk)), 1),
        best_win_streak=o['streaks']['best_w'], worst_loss_streak=o['streaks']['best_l']))

    # estimates
    daily = o['daily']; nd = np.array([x['n'] for x in daily]); imp = np.array([x['implied'] for x in daily])
    noise = sqrt(np.mean(sig ** 2 / nd)); obs = float(np.std(imp, ddof=1))
    wk = [w['implied'] for w in o['weekly'] if w['n']]
    early = [v['imp'] for v in vs if v['m']['stage'] == 'Qualifier' and v['m']['rnd'] <= 3]
    late = [v['imp'] for v in vs if v['m']['stage'] == 'Qualifier' and v['m']['rnd'] >= 4]
    ups = [o['partners'][q]['uplift'] for q in P if q != p]
    mo = o['model']
    estimates.append(dict(
        player=p, adj=r(mo['s']), adj_lo=r(mo['lo']), adj_hi=r(mo['hi']),
        recent_adj=r(mo['rec']), recent_lo=r(mo['rlo']), recent_hi=r(mo['rhi']),
        h1=r(mo['h1']), h2=r(mo['h2']), change=r(mo['h2'] - mo['h1']), change_lo=r(mo['dlo']), change_hi=r(mo['dhi']),
        trend21=r(o['trend']['per21']), trend_t=r(o['trend']['t']),
        elo=round(mo['elo']), elo_wl=round(mo['elo_plain']),
        p_first=r(mo['rankprob'][0], 3), p_top3=r(sum(mo['rankprob'][:3]), 3),
        neutral_win=r(rd['neutral'][p], 3), neutral_win_recent=r(rd['neutral_rec'][p], 3),
        exp_wins=r(R['expW'], 1), wins_vs_exp=r(R['w'] - R['expW'], 1),
        avg_partner=r(o['avg_mate']), avg_opp=r(o['avg_opp']), draw_context=r(o['ctx_dpm']),
        implied_mean=r(o['mean_implied']), daily_sd=r(obs), noise_sd=r(noise), excess_sd=r(sqrt(max(0, obs ** 2 - noise ** 2))),
        weekly_sd=r(np.std(wk, ddof=1)), uplift=r(np.mean(ups)),
        early_adj=r(np.mean(early)), late_adj=r(np.mean(late)), early_n=len(early), late_n=len(late)))

E = {e['player']: e for e in estimates}
PL = {x['player']: x for x in players}
PR = {x['player']: x for x in pressure}
for k, rnk in enumerate(np.argsort(-np.array([E[p]['adj'] for p in P]))):
    E[P[rnk]]['adj_rank'] = k + 1
for k, rnk in enumerate(np.argsort(-np.array([E[p]['elo'] for p in P]))):
    E[P[rnk]]['elo_rank'] = k + 1

# ---------------- weekly / daily ----------------
weekly = []
for p in P:
    for w in rd['players'][p]['weekly']:
        if not w['n']:
            continue
        weekly.append(dict(key=f'{p}|{w["wk"]}', player=p, week=w['wk'], label=f'Week {w["wk"]}', days=w['days'],
                           P=w['n'], W=w['w'], L=w['l'], record=rec(w['w'], w['l']), win_pct=r(w['pct'], 3),
                           diff=w['diff'], dpm=r(w['dpm']), adj=r(w['implied'])))
daily = []
for p in P:
    dmap = {x['di']: x for x in rd['players'][p]['daily']}
    for di in range(len(days)):
        x = dmap.get(di)
        daily.append(dict(key=f'{p}|{di}', player=p, day_index=di, day=rd['days'][di], week=1 if not days[di].startswith('W') else int(days[di][1]),
                          played=x is not None, P=x['n'] if x else 0, W=x['w'] if x else 0, L=(x['n'] - x['w']) if x else 0,
                          diff=x['diff'] if x else None, adj=r(x['implied']) if x else None,
                          seed=x['seed'] if x else None, field=x['field'] if x else None,
                          final=x['final'] if x else False, title=x['title'] if x else False,
                          wb_rating=md['wbrating'][p][di], elo=round(rd['elo_hist'][p][di]),
                          cum_diff=rd['cumdiff'][p][di], cum_adj=r(rd['cum_adj'][p][di]), cum_adj_rank=rd['cumrank_adj'][p][di]))
# cumulative points-diff rank
for di in range(len(days)):
    rows = [d for d in daily if d['day_index'] == di]
    for k, d in enumerate(sorted(rows, key=lambda d: -d['cum_diff'])):
        d['cum_rank'] = k + 1

# ---------------- partners / pairs ----------------
partners, pairs = [], []
for p in P:
    for q, v in rd['players'][p]['partners'].items():
        partners.append(dict(key=f'{p}|{q}', player=p, partner=q, P=v['n'], W=v['w'], L=v['l'], record=rec(v['w'], v['l']),
                             win_pct=r(v['pct'], 3), dpm=r(v['dpm']), exp_dpm=r(v['expdpm']), vs_exp=r(v['synergy']),
                             partner_without_dpm=r(v['partner_wo_dpm']), uplift=r(v['uplift'])))
for a, b in itertools.combinations(P, 2):
    v = rd['players'][a]['partners'][b]
    pairs.append(dict(key=f'{a} + {b}', a=a, b=b, P=v['n'], W=v['w'], L=v['l'], record=rec(v['w'], v['l']),
                      win_pct=r(v['pct'], 3), ci_lo=r(v['ci'][0], 3), ci_hi=r(v['ci'][1], 3), diff=v['diff'], dpm=r(v['dpm']),
                      exp_dpm=r(v['expdpm']), vs_exp=r(v['synergy']), vs_exp_se=r(v['syn_se']),
                      z=r(v['synergy'] / v['syn_se']), sample=('small' if v['n'] < 10 else 'usable')))

# ---------------- opponents / bands ----------------
opponents, bands = [], []
for p in P:
    for q, v in rd['players'][p]['opps'].items():
        opponents.append(dict(key=f'{p}|{q}', player=p, opponent=q, P=v['n'], W=v['w'], L=v['l'], record=rec(v['w'], v['l']),
                              win_pct=r(v['pct'], 3), dpm=r(v['dpm']), exp_W=r(v['expW'], 1), vs_exp=r(v['w'] - v['expW'], 1),
                              adj=r(v['adj'])))
    for b in ('strong', 'middle', 'weak'):
        v = rd['players'][p]['bands'][b]
        bands.append(dict(key=f'{p}|{b}', player=p, band=b, P=v['n'], W=v['w'], L=v['n'] - v['w'], record=rec(v['w'], v['n'] - v['w']),
                          win_pct=r(v['pct'], 3), dpm=r(v['dpm']), exp_W=r(v['expW'], 1), vs_exp=r(v['w'] - v['expW'], 1)))

json.dump(dict(players=players, estimates=estimates, pressure=pressure, weekly=weekly, daily=daily, partners=partners,
               pairs=pairs, opponents=opponents, bands=bands, matches=matches), open('tables.json', 'w'), indent=1)
for name, rows in dict(players=players, estimates=estimates, pressure=pressure, weekly=weekly, daily=daily,
                       partners=partners, pairs=pairs, opponents=opponents, bands=bands, matches=matches).items():
    json.dump(rows, open(f'{OUT}/{name}.json', 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
for e in estimates:
    print(e['player'], e['adj_rank'], e['elo_rank'], e['weekly_sd'], e['uplift'], e['early_adj'], e['late_adj'], e['p_first'], e['p_top3'])
print({p: PR[p]['clutch'] for p in P})
print('sizes', {f: os.path.getsize(f'{OUT}/{f}') for f in os.listdir(OUT)})
print([ (x['key'], x['vs_exp'], x['z']) for x in sorted(pairs, key=lambda x: -abs(x['z']))[:6]])
print(md['rankprob'])
