"""Rebuild badminton-season-report.html from ../badminton-scores.xlsx.

Run from anywhere:  python -P build/run.py
Set BX_OUT=<path> to write somewhere other than ../badminton-season-report.html.
After adding a new week, re-read the narrative in build_page.py (verdicts, findings,
ranking reasons, strengths, outlook): it is hand-written against the latest numbers.
"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONPATH': here}
for step in ['parse.py', 'analysis.py', 'stats.py', 'build_data.py', 'build_page.py', 'build_web_2026.py']:
    print('==>', step, flush=True)
    r = subprocess.run([sys.executable, '-P', step], cwd=here, env=env, capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        print(r.stdout[-3000:], r.stderr[-3000:]); sys.exit(f'{step} failed')
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '')
# Keep the index.html copy (if one exists next to the report) in step with the fresh build.
if not os.environ.get('BX_OUT'):
    import shutil
    rep = os.path.join(here, '..', 'badminton-season-report.html'); idx = os.path.join(here, '..', 'index.html')
    if os.path.exists(idx):
        shutil.copyfile(rep, idx); print('==> also updated index.html')
