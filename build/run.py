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
