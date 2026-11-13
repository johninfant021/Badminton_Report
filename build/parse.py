import openpyxl, re, json
p = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'badminton-scores.xlsx')
wb = openpyxl.load_workbook(p, data_only=True)
P = ['Anto','Jothi Sai','John','Pawan','Dinesh','Pratap','Bhanu']
days = [n for n in wb.sheetnames if 'Day' in n]
matches=[]; notes={}; ratings={}
for d in days:
    ws = wb[d]
    notes[d] = []
    for r in range(1, ws.max_row+1):
        a = ws.cell(r,1).value
        row = [ws.cell(r,c).value for c in range(1, ws.max_column+1)]
        # text notes
        for v in row:
            if isinstance(v,str) and len(v)>45: notes[d].append(f'r{r}: {v}')
        if isinstance(a,str) and (a.startswith('Round') or a.startswith('Eliminator') or a.startswith('Final') or a.startswith('Semi')):
            b,c,s1,s2,f,g = row[1:7]
            if b in P and c in P and f in P and g in P:
                matches.append(dict(day=d,row=r,label=a,a1=b,a2=c,sa=s1,sb=s2,b1=f,b2=g, proj=row[8] if len(row)>8 and isinstance(row[8],(int,float)) else None))
            elif any(x not in (None,'') for x in (b,c,s1,s2,f,g)):
                print('ODD ROW', d, r, row[:9])
        # ratings in standings: B=player, C=rating numeric, D = P
        if row[1] in P and isinstance(row[2],(int,float)) and len(row)>3 and isinstance(row[3],(int,float)) and not isinstance(a,str):
            ratings.setdefault(d,{})[row[1]] = row[2]
# days not in the workbook yet (see ../extra-days.json); a workbook tab with the same name wins
extra_path = __import__('os').path.join(__import__('os').path.dirname(p), 'extra-days.json')
extra_days = []
if __import__('os').path.exists(extra_path):
    for x in json.load(open(extra_path, encoding='utf-8')).get('days', []):
        d = x['day']
        if d in days:
            print('extra-days.json:', d, 'is now in the workbook; using the workbook tab'); continue
        for k, m in enumerate(x['matches']):
            (a1, a2), (b1, b2), (s1, s2) = m['a'], m['b'], m['score']
            assert all(q in P for q in (a1, a2, b1, b2)), (d, m)
            matches.append(dict(day=d, row=None, label=m['label'], a1=a1, a2=a2, sa=s1, sb=s2, b1=b1, b2=b2, proj=None))
        ratings[d] = dict(x.get('ratings', {}))
        notes[d] = [x.get('source', 'extra-days.json')]
        days.append(d); extra_days.append(d)
json.dump(dict(matches=matches,notes=notes,ratings=ratings,days=days,extra_days=extra_days), open('parsed.json','w'), indent=1, default=str)
print(len(matches), 'matches from day sheets')
for d in days: print(d, sum(1 for m in matches if m['day']==d), ratings.get(d))
