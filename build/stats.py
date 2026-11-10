import json, math, itertools
import numpy as np
from math import erf, sqrt

P = ['Anto', 'Jothi Sai', 'John', 'Pawan', 'Dinesh', 'Pratap', 'Bhanu']
IDX = {p: i for i, p in enumerate(P)}
md = json.load(open('model.json'))
M, days = md['M'], md['days']
s = np.array(md['s']); s_rec = np.array(md['s_rec']); sigma = md['sigma']
loo = {int(k): v for k, v in md['loo_pred'].items()}


def Phi(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def short(day):
    return ('W1 ' + day.replace('Day ', 'D')) if not day.startswith('W') else day.replace('Day ', 'D')


SHORT = [short(x) for x in days]


def views(p):
    out = []
    for m in M:
        if p in m['A']:
            mate = [x for x in m['A'] if x != p][0]; opp = m['B']; pf, pa = m['sa'], m['sb']; sign = 1
        elif p in m['B']:
            mate = [x for x in m['B'] if x != p][0]; opp = m['A']; pf, pa = m['sb'], m['sa']; sign = -1
        else:
            continue
        mu = sign * loo[m['i']]  # out-of-sample predicted margin from this player's side
        exp_ctx = s[IDX[mate]] - s[IDX[opp[0]]] - s[IDX[opp[1]]]
        out.append(dict(m=m, mate=mate, opp=opp, pf=pf, pa=pa, diff=pf - pa, win=pf > pa, mu=mu,
                        implied=(pf - pa) - exp_ctx, ctx=exp_ctx))
    return out


V = {p: views(p) for p in P}


def rec(vs):
    n = len(vs); w = sum(v['win'] for v in vs); pf = sum(v['pf'] for v in vs); pa = sum(v['pa'] for v in vs)
    wm = [v['diff'] for v in vs if v['win']]; lm = [-v['diff'] for v in vs if not v['win']]
    return dict(n=n, w=w, l=n - w, pct=(w / n if n else None), pf=pf, pa=pa, diff=pf - pa,
                dpm=((pf - pa) / n if n else None), avgW=(sum(wm) / len(wm) if wm else None),
                avgL=(sum(lm) / len(lm) if lm else None),
                expW=sum(Phi(v['mu'] / sigma) for v in vs))


def wilson(w, n, z=1.645):
    if n == 0:
        return (None, None)
    ph = w / n; den = 1 + z * z / n; c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def close_exp(mu, k):
    # P(win | |margin| <= k) for margin ~ N(mu, sigma)
    a = Phi((k - mu) / sigma) - Phi((0 - mu) / sigma)
    b = Phi((0 - mu) / sigma) - Phi((-k - mu) / sigma)
    return a / (a + b) if a + b > 0 else 0.5


# ---------- qualifier seeds per day ----------
seeds = {}
for day in days:
    q = [m for m in M if m['day'] == day and m['stage'] == 'Qualifier']
    tab = {}
    for m in q:
        for side, pf, pa in (('A', m['sa'], m['sb']), ('B', m['sb'], m['sa'])):
            for p in m[side]:
                t = tab.setdefault(p, [0, 0, 0, 0])
                t[0] += 1; t[1] += pf > pa; t[2] += pf; t[3] += pa
    order = sorted(tab, key=lambda p: (-(tab[p][2] - tab[p][3]), -tab[p][2], -tab[p][1]))
    seeds[day] = {p: (i + 1, len(order), tab[p]) for i, p in enumerate(order)}

out = {'players': {}, 'days': SHORT, 'weeks': sorted({m['wk'] for m in M})}
for p in P:
    vs = V[p]; i = IDX[p]
    R = rec(vs)
    q = rec([v for v in vs if v['m']['stage'] == 'Qualifier'])
    ko = rec([v for v in vs if v['m']['stage'] != 'Qualifier'])
    el = rec([v for v in vs if v['m']['stage'] == 'Eliminator'])
    fi = rec([v for v in vs if v['m']['stage'] == 'Final'])
    played_days = sorted({v['m']['di'] for v in vs})
    # titles and their route
    titles = []
    for v in vs:
        if v['m']['stage'] == 'Final' and v['win']:
            day = v['m']['day']
            via_elim = any(x['m']['day'] == day and x['m']['stage'] == 'Eliminator' for x in vs)
            titles.append(dict(day=short(day), via_elim=via_elim, seed=seeds[day][p][0], partner=v['mate'],
                               score=f"{v['pf']}-{v['pa']}", day1_uncertain=(day == 'Day 1')))
    finals = [dict(day=short(v['m']['day']), win=v['win'], partner=v['mate'], opp=v['opp'], score=f"{v['pf']}-{v['pa']}")
              for v in vs if v['m']['stage'] == 'Final']
    # daily
    daily = []
    for di in played_days:
        dv = [v for v in vs if v['m']['di'] == di]
        r = rec(dv)
        sd = seeds[days[di]].get(p)
        daily.append(dict(di=di, day=SHORT[di], wk=dv[0]['m']['wk'], n=r['n'], w=r['w'], diff=r['diff'],
                          implied=float(np.mean([v['implied'] for v in dv])), seed=sd[0] if sd else None,
                          field=sd[1] if sd else None, final=any(v['m']['stage'] == 'Final' for v in dv),
                          title=any(v['m']['stage'] == 'Final' and v['win'] for v in dv)))
    # weekly
    weekly = []
    for wk in sorted({m['wk'] for m in M}):
        wv = [v for v in vs if v['m']['wk'] == wk]
        if not wv:
            weekly.append(dict(wk=wk, n=0)); continue
        r = rec(wv)
        weekly.append(dict(wk=wk, n=r['n'], w=r['w'], l=r['l'], pct=r['pct'], diff=r['diff'], dpm=r['dpm'],
                           implied=float(np.mean([v['implied'] for v in wv])),
                           days=len({v['m']['di'] for v in wv})))
    # recent form: last 20 matches
    last = vs[-20:]
    rl = rec(last)
    # trend in daily implied performance
    xs = np.array([dd['di'] for dd in daily], float); ys = np.array([dd['implied'] for dd in daily])
    A = np.vstack([np.ones_like(xs), xs]).T
    coef, res, *_ = np.linalg.lstsq(A, ys, rcond=None)
    yhat = A @ coef; s2 = np.sum((ys - yhat) ** 2) / (len(xs) - 2)
    se = math.sqrt(s2 / np.sum((xs - xs.mean()) ** 2))
    # streaks
    seq = [v['win'] for v in vs]
    best_w = best_l = cur = 0; prev = None; bw = bl = 0
    for x in seq:
        cur = cur + 1 if x == prev else 1; prev = x
        if x: bw = max(bw, cur)
        else: bl = max(bl, cur)
    cur_streak = (('W' if seq[-1] else 'L'), cur)
    # close games
    def clutch(k):
        cv = [v for v in vs if abs(v['diff']) <= k]
        w = sum(v['win'] for v in cv)
        e = sum(close_exp(v['mu'], k) for v in cv)
        return dict(n=len(cv), w=w, l=len(cv) - w, exp=e)
    deuce = [v for v in vs if max(v['pf'], v['pa']) > 21]
    # partners
    partners = {}
    for q2 in P:
        if q2 == p: continue
        pv = [v for v in vs if v['mate'] == q2]
        r = rec(pv)
        resid = [v['diff'] - (s[i] + s[IDX[q2]] - s[IDX[v['opp'][0]]] - s[IDX[v['opp'][1]]]) for v in pv]
        # partner's own results without p
        qv_wo = [v for v in V[q2] if v['mate'] != p]
        wo = rec(qv_wo)
        lo_, hi_ = wilson(r['w'], r['n'])
        partners[q2] = dict(n=r['n'], w=r['w'], l=r['l'], pct=r['pct'], diff=r['diff'], dpm=r['dpm'],
                            expdpm=(float(np.mean([v['diff'] - x for v, x in zip(pv, resid)])) if pv else None),
                            synergy=(float(np.mean(resid)) if pv else None),
                            syn_se=(sigma / math.sqrt(len(pv)) if pv else None),
                            ci=(lo_, hi_), partner_wo_dpm=wo['dpm'], uplift=((r['dpm'] - wo['dpm']) if pv else None))
    # opponents
    opps = {}
    for o in P:
        if o == p: continue
        ov = [v for v in vs if o in v['opp']]
        r = rec(ov)
        lo_, hi_ = wilson(r['w'], r['n'])
        opps[o] = dict(n=r['n'], w=r['w'], l=r['l'], pct=r['pct'], dpm=r['dpm'], expW=r['expW'],
                       adj=(float(np.mean([v['implied'] for v in ov]) - float(np.mean([v['implied'] for v in vs]))) if ov else None),
                       ci=(lo_, hi_))
    # by opposition strength band
    bands = {}
    for name, f in (('strong', lambda x: x > 1.5), ('middle', lambda x: -1.5 <= x <= 1.5), ('weak', lambda x: x < -1.5)):
        bv = [v for v in vs if f(s[IDX[v['opp'][0]]] + s[IDX[v['opp'][1]]])]
        r = rec(bv)
        bands[name] = dict(n=r['n'], w=r['w'], pct=r['pct'], dpm=r['dpm'], expW=r['expW'])
    # session position split
    early = [v for v in vs if v['m']['stage'] == 'Qualifier' and v['m']['rnd'] <= 3]
    late = [v for v in vs if v['m']['stage'] == 'Qualifier' and v['m']['rnd'] >= 4]
    out['players'][p] = dict(
        overall=R, qual=q, ko=ko, elim=el, final=fi, titles=titles, finals=finals, days_played=len(played_days),
        top_seed=sum(1 for dd in daily if dd['seed'] == 1),
        avg_seed_pct=float(np.mean([(dd['seed'] - 1) / (dd['field'] - 1) for dd in daily])),
        daily=daily, weekly=weekly, recent=rl, season_dpm=R['dpm'],
        trend=dict(slope=float(coef[1]), se=se, per21=float(coef[1] * (len(days) - 1)), t=float(coef[1] / se)),
        streaks=dict(best_w=bw, best_l=bl, current=cur_streak),
        close3=clutch(3), close5=clutch(5),
        deuce=dict(n=len(deuce), w=sum(v['win'] for v in deuce)),
        sd_margin=float(np.std([v['diff'] for v in vs], ddof=1)),
        sd_daily_implied=float(np.std([dd['implied'] for dd in daily], ddof=1)),
        pos_days=sum(1 for dd in daily if dd['diff'] > 0), zero_days=sum(1 for dd in daily if dd['diff'] == 0),
        heavy_losses=sum(1 for v in vs if v['diff'] <= -8), big_wins=sum(1 for v in vs if v['diff'] >= 8),
        partners=partners, opps=opps, bands=bands,
        avg_mate=float(np.mean([s[IDX[v['mate']]] for v in vs])),
        avg_opp=float(np.mean([s[IDX[v['opp'][0]]] + s[IDX[v['opp'][1]]] for v in vs])),
        ctx_dpm=float(np.mean([v['ctx'] for v in vs])),
        mean_implied=float(np.mean([v['implied'] for v in vs])),
        early=rec(early), late=rec(late),
        model=dict(s=md['s'][i], lo=md['lo'][i], hi=md['hi'][i], rec=md['s_rec'][i], rlo=md['lor'][i], rhi=md['hir'][i],
                   h1=md['s_h1'][i], h2=md['s_h2'][i], dlo=md['lod'][i], dhi=md['hid'][i], elo=md['elo'][p],
                   elo_plain=md['elo_plain'][p], rankprob=md['rankprob'][p]),
        wb=dict(hist=md['wbrating'][p], sheet=md['season_sheet'][p]),
        ci_pct=wilson(R['w'], R['n']),
    )


# neutral-draw expected win%: random partner, random opponents
def neutral(sv):
    res = {}
    for p in P:
        i = IDX[p]; probs = []
        for q2 in P:
            if q2 == p: continue
            rest = [x for x in P if x not in (p, q2)]
            for k, l in itertools.combinations(rest, 2):
                probs.append(Phi((sv[i] + sv[IDX[q2]] - sv[IDX[k]] - sv[IDX[l]]) / sigma))
        res[p] = float(np.mean(probs))
    return res


out['neutral'] = neutral(s); out['neutral_rec'] = neutral(s_rec)
# season progression: cumulative points-diff rank and cumulative adjusted rank after each day
cumdiff = {p: [] for p in P}; tot = {p: 0 for p in P}
for di in range(len(days)):
    for m in M:
        if m['di'] == di:
            for p in m['A']: tot[p] += m['sa'] - m['sb']
            for p in m['B']: tot[p] += m['sb'] - m['sa']
    for p in P: cumdiff[p].append(tot[p])
out['cumdiff'] = cumdiff
cumrank = {p: [] for p in P}
for di in range(len(days)):
    order = sorted(P, key=lambda p: -md['cum'][di][IDX[p]])
    for p in P: cumrank[p].append(order.index(p) + 1)
out['cumrank_adj'] = cumrank
out['cum_adj'] = {p: [md['cum'][di][IDX[p]] for di in range(len(days))] for p in P}
out['elo_hist'] = {p: [h[p] for h in md['elo_hist']] for p in P}
out['seeds'] = {short(day): {p: v[0] for p, v in seeds[day].items()} for day in days}
out['meta'] = dict(sigma=sigma, best_lam=md['best_lam'], cv=md['cvres'], base_mae=md['base_mae'], base_rmse=md['base_rmse'],
                   insample_mae=md['insample_mae'], elo_check=md['elo_check'], n=len(M))
# stage summary
for st in ('Qualifier', 'Eliminator', 'Final'):
    mm = [abs(m['sa'] - m['sb']) for m in M if m['stage'] == st]
    out['meta'][st] = dict(n=len(mm), mean=float(np.mean(mm)), le3=sum(x <= 3 for x in mm), le5=sum(x <= 5 for x in mm))
allm = [abs(m['sa'] - m['sb']) for m in M]
out['meta']['all'] = dict(mean=float(np.mean(allm)), le3=sum(x <= 3 for x in allm), le5=sum(x <= 5 for x in allm),
                          deuce=sum(max(m['sa'], m['sb']) > 21 for m in M))
# pair matrix
out['pairs'] = {}
for a, b in itertools.combinations(P, 2):
    pv = out['players'][a]['partners'][b]
    out['pairs'][f'{a}|{b}'] = pv
json.dump(out, open('report_data.json', 'w'), indent=1, default=float)

# ---------- print summary ----------
f = lambda x, n=2: ('—' if x is None else f'{x:+.{n}f}')
for p in P:
    o = out['players'][p]; R = o['overall']
    print(f"\n===== {p}  days {o['days_played']}  P{R['n']} W{R['w']} L{R['l']} {R['pct']:.3f} CI{tuple(round(x,2) for x in o['ci_pct'])} "
          f"PF{R['pf']} PA{R['pa']} D{R['diff']} dpm{R['dpm']:+.2f} avgW {R['avgW']:.2f} avgL {R['avgL']:.2f} expW {R['expW']:.1f}")
    for k in ('qual', 'ko', 'elim', 'final'):
        r = o[k]; print(f"  {k:6s} {r['w']}-{r['l']} ({(r['pct'] or 0):.3f}) diff {r['diff']} dpm {f(r['dpm'])} expW {r['expW']:.1f}")
    print('  titles', [(t['day'], t['partner'], t['score'], 'elim' if t['via_elim'] else 'direct', t['seed']) for t in o['titles']])
    print('  top seed days', o['top_seed'], 'avg seed pct', round(o['avg_seed_pct'], 2), 'pos days', o['pos_days'], 'zero', o['zero_days'])
    print('  weekly', [(w['wk'], w['n'], w.get('w'), w.get('diff'), round(w['implied'], 2) if w['n'] else None) for w in o['weekly']])
    print('  recent20', o['recent']['w'], '-', o['recent']['l'], 'dpm', f(o['recent']['dpm']), 'season dpm', f(o['season_dpm']))
    print('  trend per21', f(o['trend']['per21']), 't', round(o['trend']['t'], 2))
    print('  streaks', o['streaks'], 'close3', o['close3'], 'close5', {k: (round(v, 1) if isinstance(v, float) else v) for k, v in o['close5'].items()}, 'deuce', o['deuce'])
    print('  sd margin', round(o['sd_margin'], 2), 'sd daily implied', round(o['sd_daily_implied'], 2), 'heavy L', o['heavy_losses'], 'big W', o['big_wins'])
    print('  avg mate', f(o['avg_mate']), 'avg opp sum', f(o['avg_opp']), 'ctx dpm', f(o['ctx_dpm']), 'mean implied', f(o['mean_implied']))
    print('  early', o['early']['w'], '-', o['early']['l'], f(o['early']['dpm']), ' late', o['late']['w'], '-', o['late']['l'], f(o['late']['dpm']))
    print('  bands', {k: (v['n'], v['w'], f(v['dpm']), round(v['expW'], 1)) for k, v in o['bands'].items()})
    print('  partners:')
    for q2, v in sorted(o['partners'].items(), key=lambda kv: -(kv[1]['dpm'] or -99)):
        print(f"    {q2:10s} n{v['n']:3d} {v['w']}-{v['l']} {v['pct'] if v['pct'] is None else round(v['pct'],2)} dpm {f(v['dpm'])} exp {f(v['expdpm'])} syn {f(v['synergy'])}±{(v['syn_se'] or 0):.1f} uplift {f(v['uplift'])}")
    print('  opponents:')
    for o2, v in sorted(o['opps'].items(), key=lambda kv: -(kv[1]['pct'] or 0)):
        print(f"    {o2:10s} n{v['n']:3d} {v['w']}-{v['l']} {round(v['pct'],2)} dpm {f(v['dpm'])} expW {v['expW']:.1f} adj {f(v['adj'])}")
print('\nneutral', {k: round(v, 3) for k, v in out['neutral'].items()})
print('neutral_rec', {k: round(v, 3) for k, v in out['neutral_rec'].items()})
print('meta', {k: v for k, v in out['meta'].items() if k not in ('cv',)})
print('cumdiff final', {p: out['cumdiff'][p][-1] for p in P})
