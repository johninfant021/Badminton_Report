import json, math, openpyxl
import numpy as np
from math import erf, sqrt

rng = np.random.default_rng(7)
P = ['Anto', 'Jothi Sai', 'John', 'Pawan', 'Dinesh', 'Pratap', 'Bhanu']
IDX = {p: i for i, p in enumerate(P)}
d = json.load(open('parsed.json'))
days = d['days']


def week(day):
    return 1 if not day.startswith('W') else int(day[1])


M = []
for k, m in enumerate(d['matches']):
    stage = 'Qualifier' if m['label'].startswith('Round') else ('Final' if m['label'].startswith('Final') else 'Eliminator')
    rnd = int(m['label'].split()[1]) if stage == 'Qualifier' else None
    M.append(dict(i=k, day=m['day'], di=days.index(m['day']), wk=week(m['day']), stage=stage, rnd=rnd, label=m['label'],
                  A=[m['a1'], m['a2']], B=[m['b1'], m['b2']], sa=m['sa'], sb=m['sb']))
N = len(M)

# ---------- workbook ratings from Season sheet ----------
wb = openpyxl.load_workbook(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'badminton-scores.xlsx'), data_only=True)
ws = wb['Season']
wbrating = {}
for r in range(26, 33):
    p = ws.cell(r, 1).value
    wbrating[p] = [ws.cell(r, c).value if isinstance(ws.cell(r, c).value, (int, float)) else None for c in range(2, 2 + len(days))]
    for k, dname in enumerate(days):
        if dname in d.get('extra_days', []):
            wbrating[p][k] = d['ratings'].get(dname, {}).get(p)
season_sheet = {ws.cell(r, 1).value: dict(now=ws.cell(r, 2).value, start=ws.cell(r, 3).value, P=ws.cell(r, 4).value,
                                          W=ws.cell(r, 5).value, F=ws.cell(r, 6).value, A=ws.cell(r, 7).value,
                                          QW=ws.cell(r, 10).value, KOP=ws.cell(r, 11).value, KOW=ws.cell(r, 12).value,
                                          Fin=ws.cell(r, 13).value, T=ws.cell(r, 14).value) for r in range(5, 12)}


# ---------- ridge (adjusted plus-minus on point margin) ----------
def design(ms):
    X = np.zeros((len(ms), 7))
    y = np.zeros(len(ms))
    for r, m in enumerate(ms):
        for p in m['A']:
            X[r, IDX[p]] += 1
        for p in m['B']:
            X[r, IDX[p]] -= 1
        y[r] = m['sa'] - m['sb']
    return X, y


def ridge(ms, lam=4.0, w=None):
    X, y = design(ms)
    W = np.ones(len(ms)) if w is None else np.asarray(w)
    A = X.T @ (W[:, None] * X) + lam * np.eye(7) + 1e3 * np.ones((7, 7))  # last term pins the mean to zero
    return np.linalg.solve(A, X.T @ (W * y))


def cv(lam):
    errs, sq, sign = [], [], []
    for day in days:
        tr = [m for m in M if m['day'] != day]
        te = [m for m in M if m['day'] == day]
        sv = ridge(tr, lam)
        X, y = design(te)
        pr = X @ sv
        errs += list(np.abs(pr - y)); sq += list((pr - y) ** 2); sign += list((np.sign(pr) == np.sign(y)).astype(float))
    return float(np.mean(errs)), float(math.sqrt(np.mean(sq))), float(np.mean(sign))


lams = [0.5, 1, 2, 4, 8, 16, 32, 64]
cvres = {lam: cv(lam) for lam in lams}
best_lam = min(lams, key=lambda l: cvres[l][1])
X, y = design(M)
base_mae = float(np.mean(np.abs(y)))
base_rmse = float(math.sqrt(np.mean(y ** 2)))
s = ridge(M, best_lam)
resid = y - X @ s
sigma = float(np.std(resid, ddof=7))
insample_mae = float(np.mean(np.abs(resid)))

B = 2000
boot = np.zeros((B, 7))
for b in range(B):
    pick = rng.choice(len(days), len(days), replace=True)  # resample whole days
    ms = [m for k in pick for m in M if m['day'] == days[k]]
    boot[b] = ridge(ms, best_lam)
lo, hi = np.percentile(boot, 5, axis=0), np.percentile(boot, 95, axis=0)
ranks = np.argsort(np.argsort(-boot, axis=1), axis=1) + 1
rankprob = {P[i]: [float(np.mean(ranks[:, i] == r)) for r in range(1, 8)] for i in range(7)}

# recency weighted fit: half-life of 5 session days
hl = 5.0
wrec = [0.5 ** ((len(days) - 1 - m['di']) / hl) for m in M]
s_rec = ridge(M, best_lam, wrec)
bootr = np.zeros((B, 7))
for b in range(B):
    pick = rng.choice(N, N, replace=True)
    bootr[b] = ridge([M[k] for k in pick], best_lam, [wrec[k] for k in pick])
lor, hir = np.percentile(bootr, 5, axis=0), np.percentile(bootr, 95, axis=0)

# first half vs second half of the season (split at the midpoint day)
HALF = len(days) // 2
half1 = [m for m in M if m['di'] < HALF]
half2 = [m for m in M if m['di'] >= HALF]
s_h1 = ridge(half1, best_lam)
s_h2 = ridge(half2, best_lam)
bd = np.zeros((B, 7))
for b in range(B):
    p1 = [half1[k] for k in rng.choice(len(half1), len(half1))]
    p2 = [half2[k] for k in rng.choice(len(half2), len(half2))]
    bd[b] = ridge(p2, best_lam) - ridge(p1, best_lam)
lod, hid = np.percentile(bd, 5, axis=0), np.percentile(bd, 95, axis=0)

cum = [list(ridge([m for m in M if m['di'] <= k], best_lam)) for k in range(len(days))]


def pred_margin(m, sv):
    return sum(sv[IDX[p]] for p in m['A']) - sum(sv[IDX[p]] for p in m['B'])


loo_pred = {}
for day in days:
    sv = ridge([m for m in M if m['day'] != day], best_lam)
    for m in M:
        if m['day'] == day:
            loo_pred[m['i']] = pred_margin(m, sv)


# ---------- Elo ----------
def run_elo(K=32, mov=True, score_from=3):
    R = {p: 1500.0 for p in P}
    hist, br, acc = [], [], []
    for k, day in enumerate(days):
        for m in [x for x in M if x['day'] == day]:
            ra = (R[m['A'][0]] + R[m['A'][1]]) / 2
            rb = (R[m['B'][0]] + R[m['B'][1]]) / 2
            ea = 1 / (1 + 10 ** (-(ra - rb) / 400))
            sa = 1.0 if m['sa'] > m['sb'] else 0.0
            if k >= score_from:
                br.append((ea - sa) ** 2); acc.append(float((ea > 0.5) == (sa == 1.0)))
            mult = math.log(abs(m['sa'] - m['sb']) + 1) / math.log(6) if mov else 1.0  # a 5-point margin = x1.0
            dlt = K * mult * (sa - ea)
            for p in m['A']:
                R[p] += dlt
            for p in m['B']:
                R[p] -= dlt
        hist.append({p: round(R[p], 1) for p in P})
    return R, hist, float(np.mean(br)), float(np.mean(acc))


elo, elo_hist, elo_brier, elo_acc = run_elo()
elo_plain, _, eb2, ea2 = run_elo(mov=False)

json.dump(dict(cvres={str(k): v for k, v in cvres.items()}, best_lam=best_lam, s=list(s), lo=list(lo), hi=list(hi),
               sigma=sigma, insample_mae=insample_mae, base_mae=base_mae, base_rmse=base_rmse, rankprob=rankprob,
               s_rec=list(s_rec), lor=list(lor), hir=list(hir), s_h1=list(s_h1), s_h2=list(s_h2), lod=list(lod),
               hid=list(hid), cum=cum, elo=elo, elo_plain=elo_plain, elo_hist=elo_hist,
               elo_check=[elo_brier, elo_acc, eb2, ea2], loo_pred={str(k): v for k, v in loo_pred.items()},
               wbrating=wbrating, season_sheet=season_sheet, M=M, days=days), open('model.json', 'w'), indent=1)

print('CV by lambda (MAE, RMSE, sign acc):')
for k, v in cvres.items():
    print(' ', k, [round(x, 3) for x in v])
print('best lam', best_lam, 'baseline MAE', round(base_mae, 2), 'RMSE', round(base_rmse, 2), 'insample MAE',
      round(insample_mae, 2), 'sigma', round(sigma, 2))
for i, p in enumerate(P):
    print(f'{p:10s} ridge {s[i]:+.2f} [{lo[i]:+.2f},{hi[i]:+.2f}]  recent {s_rec[i]:+.2f} [{lor[i]:+.2f},{hir[i]:+.2f}]  '
          f'H1 {s_h1[i]:+.2f} H2 {s_h2[i]:+.2f} d {s_h2[i]-s_h1[i]:+.2f} [{lod[i]:+.2f},{hid[i]:+.2f}]  '
          f'elo {elo[p]:.0f} eloWL {elo_plain[p]:.0f}  P(#1) {rankprob[p][0]:.2f}')
print('elo brier/acc MOV', elo_brier, elo_acc, ' plain', eb2, ea2)
