"""Esports HUD layer: the latest-champions "Victory" pop-up and a gaming restyle of the report sections.

winner_html() is built from tables.json (the last Final and the daily rows), so the pop-up always shows
the most recent champions. It opens once per browser session for each new day, and the trophy button
in the corner reopens it. HUD_CSS restyles the report (section banners, briefing boxes, HUD panels,
scoreboard tables, bullets, chips, page backdrop); HUD_JS numbers the section banners and runs the pop-up.
"""
from html import escape

MINUS = '−'
TROPHY = ('<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><defs><linearGradient id="wp-g" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#FFF3B0"/><stop offset=".55" stop-color="#FFD23F"/><stop offset="1" stop-color="#E09A00"/></linearGradient></defs>'
          '<path d="M20 8h24v14a12 12 0 0 1-24 0z" fill="url(#wp-g)"/>'
          '<path d="M20 12h-8v4a9 9 0 0 0 9 9M44 12h8v4a9 9 0 0 1-9 9" stroke="#FFD23F" stroke-width="3" stroke-linecap="round"/>'
          '<path d="M29 34h6v9h-6z" fill="#E0A800"/><path d="M22 44h20l2 8H20z" fill="url(#wp-g)"/><path d="M18 52h28v4H18z" fill="#B87F00"/>'
          '<path d="M27 15l2.2 4.4 4.8.7-3.5 3.4.8 4.8-4.3-2.3-4.3 2.3.8-4.8-3.5-3.4 4.8-.7z" fill="#fff" opacity=".85" transform="translate(5 -1)"/></svg>')


def winner_html(T, P, col):
    M = T['matches']
    fin = next((m for m in reversed(M) if m['stage'] == 'Final'), None)
    if not fin:
        return ''
    day = fin['day']
    won_a = fin['winner'] == fin['team_a']
    champs = fin['team_a' if won_a else 'team_b'].split(' + ')
    runners = fin['team_b' if won_a else 'team_a'].split(' + ')
    ws, ls = (fin['score_a'], fin['score_b']) if won_a else (fin['score_b'], fin['score_a'])
    D = {r['player']: r for r in T['daily'] if r['day'] == day and r['played']}
    titles = {}
    for m in M:
        if m['stage'] == 'Final':
            for q in m['winner'].split(' + '):
                titles[q] = titles.get(q, 0) + 1

    CROWN = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 18h18l-1.6-9.5-4.6 4.1L12 5l-2.8 7.6-4.6-4.1z"/></svg>'

    def team(ps, win):
        pics = ''.join(f'<span class="wp-ph" style="--pc:{col(q)}"><img data-ph-portrait="{escape(q)}" alt="">'
                       f'<span class="wp-cap"><b class="wp-nm">{escape(q)}</b><small>{(str(D[q]["W"]) + "–" + str(D[q]["L"]) + " today") if q in D else ""}'
                       f'{(" · " + str(titles.get(q, 0)) + " titles") if win else ""}</small></span></span>' for q in ps)
        tag = f'<span class="wp-tag">{CROWN}Champions</span>' if win else '<span class="wp-tag">Runners-up</span>'
        return f'<div class="wp-team {"win" if win else "lose"}">{tag}<div class="wp-pics">{pics}</div></div>'

    try:
        w, d = day.split(); label = f'Week {int(w[1:])} · Day {int(d[1:])}'
    except Exception:
        label = day
    return (f'<div class="wp" id="wp" role="dialog" aria-modal="true" aria-labelledby="wp-t" data-day="{escape(day)}" hidden>'
            f'<div class="wp-bg" data-wp-close></div><div class="wp-rays" aria-hidden="true"></div><canvas class="wp-confetti" aria-hidden="true"></canvas>'
            f'<div class="wp-box">'
            f'<button type="button" class="wp-x" data-wp-close aria-label="Close">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg></button>'
            f'<p class="wp-k">{label} · Final result</p>'
            f'<div class="wp-trophy">{TROPHY}</div>'
            f'<h2 class="wp-t" id="wp-t" data-text="VICTORY">VICTORY</h2>'
            f'<div class="wp-match">{team(champs, True)}'
            f'<div class="wp-mid"><span class="wp-ring" aria-hidden="true"></span><div class="wp-score"><b class="w" data-to="{ws}">{ws}</b><i>:</i><b data-to="{ls}">{ls}</b></div>'
            f'<small>Final</small></div>{team(runners, False)}</div>'
            f'<p class="wp-sub"><b>{escape(" + ".join(champs))}</b> beat {escape(" + ".join(runners))} {ws}–{ls} to win {escape(day)}.</p>'
            f'<div class="wp-ctas"><a class="ar-cta" href="#latest" data-wp-go>Match report</a>'
            f'<button type="button" class="ar-cta ghost" data-wp-close>Continue</button></div>'
            f'<div class="wp-timer" aria-hidden="true"><i></i></div></div></div>'
            f'<button type="button" class="wp-fab" aria-controls="wp" aria-label="Show the latest champions">{TROPHY}'
            f'<span><small>{escape(day)} champions</small><b>{escape(" + ".join(champs))}</b></span></button>')


HUD_CSS = r"""
/* =====================================================================
   HUD — esports restyle of the report sections + Victory pop-up
   ===================================================================== */
/* ---------------- page backdrop: perspective floor + slow scan ---------------- */
.hud-bg { position: fixed; inset: 0; z-index: -1; pointer-events: none; overflow: hidden; }
.hud-bg::before { content: ""; position: absolute; left: -50%; right: -50%; bottom: -8vh; height: 55vh; transform: perspective(420px) rotateX(70deg); transform-origin: 50% 100%; opacity: .13;
  background-image: linear-gradient(rgba(0, 217, 255, .9) 1px, transparent 1px), linear-gradient(90deg, rgba(198, 255, 0, .7) 1px, transparent 1px); background-size: 80px 80px;
  -webkit-mask-image: linear-gradient(to top, #000, transparent 85%); mask-image: linear-gradient(to top, #000, transparent 85%); }
.hud-bg::after { content: ""; position: absolute; left: 0; right: 0; top: -20vh; height: 20vh; opacity: .5;
  background: linear-gradient(180deg, transparent, rgba(0, 217, 255, .035) 60%, rgba(198, 255, 0, .05) 98%, transparent); animation: hud-scan 11s linear infinite; }
@keyframes hud-floor { to { background-position: 0 80px, 0 0; } }
@keyframes hud-scan { to { transform: translateY(140vh); } }

/* ---------------- section banners ---------------- */
.bx-sec > h2[data-idx] { position: relative; overflow: hidden; isolation: isolate; padding: 26px 0 16px; margin-top: 6px; gap: 16px;
  font-size: clamp(26px, 3.3vw, 42px); letter-spacing: .07em; border-bottom: 1px solid var(--ar-line); text-shadow: 0 0 30px rgba(0, 217, 255, .25); }
.bx-sec > h2[data-idx]::before { content: attr(data-idx) !important; width: auto !important; height: auto !important; border-radius: 0 !important; box-shadow: 0 0 18px rgba(198, 255, 0, .45) !important;
  background: var(--ar-lime) !important; color: #0A0E15; font: 800 12px/1 var(--ar-h, var(--m-display)); letter-spacing: .18em; padding: 8px 14px 7px 10px; text-shadow: none;
  clip-path: polygon(0 0, 100% 0, calc(100% - 9px) 100%, 0 100%); align-self: center; }
.bx-sec:not([hidden]) > h2[data-idx]::after { bottom: 0 !important; }
.hud-wm { position: absolute; right: -6px; bottom: -.18em; z-index: -1; pointer-events: none; white-space: nowrap; font: 900 clamp(60px, 9vw, 132px)/1 var(--ar-h, var(--m-display));
  letter-spacing: .02em; color: transparent; -webkit-text-stroke: 1px rgba(0, 217, 255, .13); text-shadow: none; opacity: .9; }
.ar-head { position: relative; isolation: isolate; }
.ar-head .hud-wm { bottom: -.05em; -webkit-text-stroke-color: rgba(198, 255, 0, .10); }
@media (max-width: 700px) { .hud-wm { font-size: 64px; } .bx-sec > h2[data-idx] { padding-top: 18px; } }

/* ---------------- section intro = mission briefing ---------------- */
.bx-sec > p.bx-prose { position: relative; max-width: none; margin: 0; padding: 34px 24px 18px 26px; border-radius: 4px 18px 18px 4px; color: #C3CBD8;
  background: linear-gradient(90deg, rgba(0, 217, 255, .08), rgba(17, 23, 34, .55) 30%, rgba(17, 23, 34, .35)); border: 1px solid var(--ar-line); border-left: 3px solid var(--ar-cyan);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .03); }
.bx-sec > p.bx-prose::before { content: "// BRIEFING"; position: absolute; left: 26px; top: 12px; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .22em; color: var(--ar-cyan); }
.bx-sec > p.bx-prose b { color: #fff; }

/* ---------------- HUD panels ---------------- */
.bx-card, .bx-findings li, .bx-callout, .bx-pr-verdict { border-radius: 14px !important; }
.bx-card { position: relative; }
.bx-card::after, .bx-findings li > .bx-ft::after { content: ""; position: absolute; inset: -1px; pointer-events: none; border-radius: inherit; z-index: 2; opacity: .8;
  background: linear-gradient(var(--ar-lime), var(--ar-lime)) left top / 18px 2px no-repeat, linear-gradient(var(--ar-lime), var(--ar-lime)) left top / 2px 18px no-repeat,
    linear-gradient(var(--ar-cyan), var(--ar-cyan)) right bottom / 18px 2px no-repeat, linear-gradient(var(--ar-cyan), var(--ar-cyan)) right bottom / 2px 18px no-repeat; transition: opacity .3s ease; }
.bx-findings li > .bx-ft::after { display: none; }
.bx-card:hover::after { opacity: 1; filter: drop-shadow(0 0 6px rgba(198, 255, 0, .7)); }
.bx-card-head { padding-bottom: 12px; margin-bottom: 4px; border-bottom: 1px dashed rgba(137, 147, 164, .2); }
.bx-card-head h3 { display: flex; align-items: center; gap: 10px; font-family: var(--ar-h, var(--m-display)) !important; font-size: 13.5px !important; font-weight: 700 !important;
  letter-spacing: .1em !important; text-transform: uppercase; }
.bx-card-head h3::before { content: ""; flex: none; width: 8px; height: 10px; background: var(--ar-lime); clip-path: polygon(0 0, 100% 50%, 0 100%); filter: drop-shadow(0 0 4px var(--ar-lime)); }
.bx-tag { border-radius: 4px !important; clip-path: polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%); padding-left: 12px !important; padding-right: 12px !important; }
.bx-note { font-size: 12.5px; }

/* ---------------- scoreboard tables ---------------- */
.bx-tw { border: 1px solid rgba(0, 217, 255, .12); background: rgba(5, 8, 13, .55); }
.bx-table thead th { font-family: var(--ar-h, var(--m-display)) !important; font-size: 9.5px !important; letter-spacing: .16em !important; border-bottom: 2px solid rgba(0, 217, 255, .35) !important; }
.bx-table thead th .bx-sort { font: inherit !important; letter-spacing: inherit; color: inherit; text-transform: uppercase; }
.bx-table thead th[aria-sort="ascending"], .bx-table thead th[aria-sort="descending"] { color: var(--ar-lime) !important; }
.bx-table tbody tr:nth-child(even) td { background: rgba(255, 255, 255, .018); }
.bx-table tbody tr td:first-child { box-shadow: inset 0 0 0 transparent; transition: box-shadow .2s ease; }
.bx-table tbody tr:hover td { background: rgba(198, 255, 0, .045) !important; }
.bx-table tbody tr:hover td:first-child { box-shadow: inset 3px 0 0 var(--ar-lime); }
.bx-table td.num { font-family: var(--m-body); font-variant-numeric: tabular-nums; }

/* ---------------- bullets, callouts, awards ---------------- */
.bx-list { list-style: none !important; padding-left: 0 !important; display: grid; gap: 10px; }
.bx-list > li { position: relative; padding: 2px 0 10px 24px !important; border-bottom: 1px solid rgba(137, 147, 164, .08); list-style: none !important; }
.bx-list > li:last-child { border-bottom: 0; padding-bottom: 2px !important; }
.bx-list > li::before { content: "" !important; position: absolute; left: 4px; top: .62em; width: 8px; height: 8px; transform: rotate(45deg); border-radius: 1px;
  background: var(--ar-lime); box-shadow: 0 0 8px rgba(198, 255, 0, .7); display: block !important; }
.bx-list > li:nth-child(even)::before { background: var(--ar-cyan); box-shadow: 0 0 8px rgba(0, 217, 255, .7); }
.bx-list > li > b:first-child { color: #fff; }
.bx-callout { position: relative; padding-top: 36px !important; }
.bx-callout::before { content: "// FIELD GUIDE"; position: absolute; left: 20px; top: 13px; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .22em; color: var(--ar-cyan); }
.bx-awards > div { position: relative; border-left: 2px solid rgba(198, 255, 0, .5); padding-left: 14px; }
.bx-awards dt { font-family: var(--ar-h, var(--m-display)); text-transform: uppercase; letter-spacing: .12em; font-size: 11px; color: var(--ar-lime); }
.bx-pr-verdict { border-left: 3px solid var(--ar-lime) !important; }
.bx-foot { border-top: 1px solid var(--ar-line); padding-top: 18px; font-size: 12px; color: var(--ar-mut); }

/* ---------------- Victory pop-up ---------------- */
html { scrollbar-gutter: stable; }   /* locking scroll for the pop-up then does not change the page width (no full re-layout) */
html.hud-modal-open { overflow: hidden; }
.wp { position: fixed; inset: 0; z-index: 2000; display: grid; place-items: center; padding: 18px; }
.wp[hidden] { display: none; }
.wp-bg { position: absolute; inset: 0; background: radial-gradient(60% 55% at 50% 42%, rgba(40, 34, 6, .62), rgba(3, 5, 9, .955) 70%); opacity: 0; transition: opacity .45s ease; }
.wp-rays { position: absolute; left: 50%; top: 42%; width: 105vmax; height: 105vmax; margin: -52.5vmax 0 0 -52.5vmax; will-change: transform; contain: strict; backface-visibility: hidden; pointer-events: none; opacity: 0; transition: opacity 1s ease .25s;
  background: repeating-conic-gradient(from 0deg, rgba(255, 210, 63, .12) 0 5deg, transparent 5deg 15deg); -webkit-mask-image: radial-gradient(circle, #000 0, transparent 42%); mask-image: radial-gradient(circle, #000 0, transparent 42%);
  animation: wp-spin 70s linear infinite; }
.wp-confetti { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.wp.open .wp-bg, .wp.open .wp-rays { opacity: 1; }
.wp-box { position: relative; width: min(1000px, 100%); max-height: calc(100svh - 36px); overflow: auto; padding: 30px 30px 24px; text-align: center; color: var(--ar-fg); border-radius: 22px;
  background: radial-gradient(90% 55% at 50% 0%, rgba(255, 210, 63, .16), transparent 70%) padding-box, linear-gradient(180deg, rgba(22, 27, 38, .97), rgba(9, 12, 19, .98)) padding-box,
    linear-gradient(135deg, #FFE680, rgba(255, 210, 63, .25) 30%, rgba(0, 217, 255, .45) 55%, rgba(255, 210, 63, .25) 75%, #FFD23F) border-box;
  border: 1.5px solid transparent; box-shadow: 0 0 0 1px rgba(255, 210, 63, .12), 0 0 48px rgba(255, 210, 63, .2), 0 30px 60px rgba(0, 0, 0, .8); opacity: 0; scrollbar-width: none; }
.wp.open .wp-box { animation: wp-in .9s cubic-bezier(.18, 1.2, .32, 1) .08s forwards; }
.wp.closing .wp-box { animation: wp-out .38s ease-in forwards; }
.wp.closing .wp-bg, .wp.closing .wp-rays { opacity: 0; }
.wp-box::before, .wp-box::after { content: ""; position: absolute; width: 26px; height: 26px; pointer-events: none; border: 2px solid var(--ar-gold); filter: drop-shadow(0 0 6px rgba(255, 210, 63, .8)); }
.wp-box::before { left: 10px; top: 10px; border-right: 0; border-bottom: 0; border-top-left-radius: 8px; }
.wp-box::after { right: 10px; bottom: 10px; border-left: 0; border-top: 0; border-bottom-right-radius: 8px; }
.wp-x { position: absolute; right: 14px; top: 14px; z-index: 3; width: 38px; height: 38px; display: grid; place-items: center; border-radius: 50%; border: 1px solid var(--ar-line2); background: rgba(8, 11, 18, .7); color: var(--ar-fg); cursor: pointer; transition: transform .2s ease, border-color .2s ease; }
.wp-x svg { width: 18px; height: 18px; }
.wp-x:hover { transform: rotate(90deg); border-color: var(--ar-gold); }
.wp-k { margin: 0; font: 700 11.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .26em; text-transform: uppercase; color: var(--ar-gold); }
.wp-trophy { width: 58px; height: 58px; margin: 10px auto 0; filter: drop-shadow(0 0 10px rgba(255, 210, 63, .6)); }
.wp-trophy svg { width: 100%; height: 100%; }
.wp.open .wp-trophy { animation: wp-drop .9s cubic-bezier(.3, 1.6, .5, 1) .35s both, wp-glow 2.4s ease-in-out 1.3s infinite; will-change: transform; }
.wp-t { position: relative; margin: 6px 0 14px; font: 900 clamp(44px, 8vw, 80px)/1 var(--ar-h, var(--m-display)); letter-spacing: .12em; text-transform: uppercase;
  background: linear-gradient(105deg, transparent 42%, rgba(255, 255, 255, .95) 50%, transparent 58%) 160% 0 / 260% 100% no-repeat, linear-gradient(180deg, #FFFBE0 10%, #FFD23F 55%, #E39A00 92%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  filter: drop-shadow(0 2px 0 #9A6A00) drop-shadow(0 4px 0 #6F4C00); }
.wp.open .wp-t { animation: wp-word .8s cubic-bezier(.2, 1.2, .3, 1) .25s both; will-change: transform, opacity; }
.wp-match { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 26px; margin-top: 16px; perspective: 1100px; }
.wp-team { position: relative; padding: 28px 14px 14px; border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 210, 63, .14), rgba(255, 255, 255, .02) 70%); border: 1px solid rgba(255, 210, 63, .5);
  box-shadow: inset 0 0 24px rgba(255, 210, 63, .1), 0 0 24px rgba(255, 210, 63, .14), 0 18px 34px -22px #000; }
.wp-team.win::after { content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none;
  background: linear-gradient(115deg, transparent 35%, rgba(255, 255, 255, .16) 50%, transparent 65%) -150% 0 / 250% 100% no-repeat; }
.wp.open .wp-team.win::after { animation: wp-sheen 1.4s ease-in-out 1.7s 1 both; }
.wp-team.lose { background: linear-gradient(180deg, rgba(150, 162, 184, .10), rgba(255, 255, 255, .015) 70%); border-color: rgba(150, 162, 184, .3);
  box-shadow: 0 24px 50px -26px #000; scale: .88; opacity: .82; }
.wp-tag { position: absolute; left: 50%; top: 0; translate: -50% -50%; z-index: 2; display: inline-flex; align-items: center; gap: 7px; padding: 7px 15px 6px; border-radius: 999px; white-space: nowrap;
  font: 800 11px/1 var(--ar-h, var(--m-display)); letter-spacing: .2em; text-transform: uppercase; color: #241A00;
  background: linear-gradient(180deg, #FFEB8A, #FFC21A); box-shadow: 0 0 22px rgba(255, 210, 63, .65), 0 4px 0 #A87400; }
.wp-tag svg { width: 14px; height: 14px; }
.wp-team.lose .wp-tag { color: #DCE2EC; background: linear-gradient(180deg, #3A4356, #262D3B); box-shadow: 0 4px 0 #161B25; border: 1px solid rgba(160, 172, 194, .35); }
.wp-pics { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 360px; margin: 0 auto; }
.wp-ph { position: relative; display: block; aspect-ratio: 3 / 4; border-radius: 12px; overflow: hidden; border: 2px solid var(--pc); background: #0D121B; text-align: left;
  box-shadow: 0 0 12px color-mix(in srgb, var(--pc) 38%, transparent), 0 10px 20px -12px #000; }
.wp-team.win .wp-ph:first-child { rotate: -2.5deg; }
.wp-team.win .wp-ph:last-child { rotate: 2.5deg; }
.wp-ph img { width: 100%; height: 100%; object-fit: cover; display: block; }
.wp-ph::after { content: ""; position: absolute; inset: 45% 0 0; background: linear-gradient(180deg, transparent, rgba(6, 9, 15, .92) 75%); pointer-events: none; }
.wp-cap { position: absolute; left: 10px; right: 8px; bottom: 9px; z-index: 1; display: grid; gap: 3px; }
.wp-nm { font: 800 16px/1.1 var(--ar-h, var(--m-display)); letter-spacing: .03em; color: #fff; text-shadow: 0 2px 8px #000; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.wp-cap small { font-size: 11px; line-height: 1.3; color: #C9D1DD; }
.wp.open .wp-team.win { animation: wp-team-l 1s cubic-bezier(.2, 1.1, .3, 1) .45s both; }
.wp.open .wp-team.lose { animation: wp-team-r 1s cubic-bezier(.2, 1.1, .3, 1) .6s both; }
.wp-mid { position: relative; display: grid; justify-items: center; gap: 6px; padding: 0 4px; }
.wp-score { position: relative; z-index: 1; display: flex; align-items: baseline; gap: 6px; font: 900 clamp(42px, 6vw, 68px)/1 var(--ar-h, var(--m-display)); font-variant-numeric: tabular-nums; }
.wp-score b { color: #8E98AB; }
.wp-score b.w { color: var(--ar-gold); text-shadow: 0 0 26px rgba(255, 210, 63, .7), 0 3px 0 #9A6A00; }
.wp-score i { font-style: normal; color: rgba(255, 255, 255, .25); }
.wp-mid small { font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .3em; text-transform: uppercase; color: var(--ar-gold); opacity: .8; }
.wp-ring { position: absolute; left: 50%; top: 42%; width: 90px; height: 90px; margin: -45px 0 0 -45px; border-radius: 50%; border: 2px solid var(--ar-gold); opacity: 0; pointer-events: none; }
.wp.open .wp-score { animation: wp-slam .55s cubic-bezier(.3, 1.5, .5, 1) 1.05s both; }
.wp.open .wp-ring { animation: wp-shock .9s cubic-bezier(.1, .7, .3, 1) 1.2s both; }
.wp-sub { margin: 18px auto 0; max-width: 46ch; color: #C3CBD8; font-size: 14.5px; }
.wp-sub b { color: #fff; }
.wp-ctas { display: flex; justify-content: center; flex-wrap: wrap; gap: 12px; margin-top: 18px; }
.wp-ctas .ar-cta { margin: 0; }
.wp-timer { margin: 20px auto 0; height: 3px; width: min(320px, 80%); border-radius: 3px; background: rgba(255, 255, 255, .08); overflow: hidden; }
.wp-timer i { display: block; height: 100%; width: 100%; transform-origin: 0 50%; background: linear-gradient(90deg, var(--ar-gold), var(--ar-lime)); }
.wp.open .wp-timer i { animation: wp-timer 11s linear 1s forwards; }
.wp-box:hover .wp-timer i { animation-play-state: paused; }
.wp-fab { position: fixed; right: 18px; bottom: 18px; z-index: 60; display: flex; align-items: center; gap: 0; padding: 7px; border-radius: 999px; cursor: pointer; text-align: left; color: var(--ar-fg); font-family: inherit;
  background: linear-gradient(180deg, rgba(30, 28, 12, .92), rgba(10, 13, 20, .95)); border: 1px solid rgba(255, 210, 63, .5); box-shadow: 0 0 24px rgba(255, 210, 63, .25), 0 14px 30px -12px #000;
  transition: transform .25s var(--ar-ease), opacity .3s ease; }
.wp-fab svg { width: 34px; height: 34px; flex: none; filter: drop-shadow(0 0 8px rgba(255, 210, 63, .7)); }
.wp-fab span { display: grid; line-height: 1.15; max-width: 0; opacity: 0; overflow: hidden; white-space: nowrap; transition: max-width .35s var(--ar-ease), opacity .25s ease, margin .35s var(--ar-ease); }
.wp-fab:hover span, .wp-fab:focus-visible span { max-width: 220px; opacity: 1; margin: 0 10px 0 10px; }
.wp-fab small { font: 700 9.5px/1.2 var(--ar-h, var(--m-display)); letter-spacing: .16em; text-transform: uppercase; color: var(--ar-gold); }
.wp-fab b { font-size: 13px; }
.wp-fab:hover { transform: translateY(-3px); }
html.hud-modal-open .wp-fab { opacity: 0; pointer-events: none; }
@keyframes wp-spin { to { transform: rotate(360deg); } }
@keyframes wp-in { 0% { opacity: 0; transform: translateY(46px) scale(.86); } 55% { opacity: 1; } 100% { opacity: 1; transform: none; } }
@keyframes wp-out { to { opacity: 0; transform: translateY(24px) scale(.94); } }
@keyframes wp-drop { 0% { opacity: 0; transform: translateY(-80px) scale(.4) rotate(-20deg); } 100% { opacity: 1; transform: none; } }
@keyframes wp-glow { 50% { transform: translateY(-4px); } }
@keyframes wp-word { 0% { opacity: 0; transform: translateY(18px) scale(1.25); } 100% { opacity: 1; transform: none; } }
@keyframes wp-team-l { 0% { opacity: 0; transform: translateX(-90px) scale(.92); } 100% { opacity: 1; transform: none; } }
@keyframes wp-team-r { 0% { opacity: 0; transform: translateX(90px) scale(.92); } 100% { opacity: 1; transform: none; } }
@keyframes wp-slam { 0% { opacity: 0; transform: scale(2.4); } 70% { opacity: 1; } 100% { opacity: 1; transform: none; } }
@keyframes wp-shock { 0% { opacity: .9; transform: scale(.4); } 100% { opacity: 0; transform: scale(3.2); } }
@keyframes wp-sheen { 0% { background-position: -150% 0; } 100% { background-position: 250% 0; } }
@keyframes wp-shine { 0% { background-position: 160% 0, 0 0; } 100% { background-position: -60% 0, 0 0; } }
@keyframes wp-pop { 0% { opacity: 0; transform: scale(.3); } 100% { opacity: 1; transform: none; } }
@keyframes wp-timer { to { transform: scaleX(0); } }
@keyframes wp-fab { 50% { opacity: 1; } }
.wp-fab::after { content: ""; position: absolute; inset: -1px; border-radius: inherit; pointer-events: none; box-shadow: 0 0 40px rgba(255, 210, 63, .5); opacity: 0; animation: wp-fab 2.8s ease-in-out infinite; }
/* phones and touch screens: no backdrop blur, still rays, lighter cards, smaller glows */
.wp-lite .wp-bg { -webkit-backdrop-filter: none; backdrop-filter: none; background: radial-gradient(70% 55% at 50% 40%, rgba(40, 34, 6, .7), rgba(3, 5, 9, .97) 75%); }
.wp-lite .wp-rays { animation: none; width: 110vmax; height: 110vmax; margin: -55vmax 0 0 -55vmax; will-change: auto; }
.wp-lite.open .wp-rays { opacity: .7; }
.wp-lite .wp-box { box-shadow: 0 0 0 1px rgba(255, 210, 63, .12), 0 0 40px rgba(255, 210, 63, .18), 0 30px 60px rgba(0, 0, 0, .8); }
.wp-lite .wp-t { filter: drop-shadow(0 3px 0 #7A5400); }
.wp-lite.open .wp-t { animation: wp-word .7s cubic-bezier(.2, 1.2, .3, 1) .2s both; }
.wp-lite.open .wp-team.win::after { animation: none; }
.wp-lite .wp-team.lose { filter: none; opacity: .85; }
.wp-lite .wp-trophy { filter: drop-shadow(0 0 12px rgba(255, 210, 63, .6)); }
.wp-lite.open .wp-trophy { animation: wp-drop .8s cubic-bezier(.3, 1.6, .5, 1) .3s both; }
.wp-lite .wp-ph { box-shadow: 0 0 12px color-mix(in srgb, var(--pc) 35%, transparent); }
.wp-lite.open .wp-team.win, .wp-lite.open .wp-team.lose { animation-name: wp-rise; animation-duration: .7s; }
@keyframes wp-rise { 0% { opacity: 0; transform: translateY(36px) scale(.96); } 100% { opacity: 1; transform: none; } }
html.wp-touch .wp-fab::after { animation: none; }
@media (max-width: 600px) {
  .wp-box { padding: 26px 16px 20px; }
  .wp-k { padding: 2px 44px 0; font-size: 10px; letter-spacing: .16em; line-height: 1.5; }
  .wp-match { grid-template-columns: 1fr; gap: 26px; margin-top: 18px; }
  .wp-team { padding: 24px 12px 12px; }
  .wp-team.win .wp-pics { max-width: 250px; margin: 0 auto; }
  .wp-team.lose { scale: 1; }
  .wp-team.lose .wp-pics { max-width: 190px; margin: 0 auto; }
  .wp-nm { font-size: 13px; } .wp-cap small { font-size: 9.5px; } .wp-cap { left: 8px; bottom: 7px; }
  .wp-score { font-size: 46px; }
  .wp-t { font-size: 44px; margin-bottom: 4px; }
  .wp-ctas { flex-wrap: nowrap; } .wp-ctas .ar-cta { flex: 1 1 0; min-width: 0; padding: 12px 6px; font-size: 11.5px; letter-spacing: .08em; white-space: nowrap; }
  .wp-trophy { width: 44px; height: 44px; margin-top: 8px; }
  .wp-fab { right: 12px; bottom: 12px; } .wp-fab svg { width: 28px; height: 28px; }
}
@media (prefers-reduced-motion: reduce) {
  .hud-bg::before, .hud-bg::after, .wp-rays, .wp-fab { animation: none !important; }
  .wp.open .wp-box, .wp.open .wp-t, .wp.open .wp-team, .wp.open .wp-score, .wp.open .wp-trophy, .wp.open .wp-ring, .wp.open .wp-team.win::after { animation: none !important; opacity: 1; transform: none; }
  .wp-ring { display: none; }
}
"""

HUD_JS = r"""
(() => {
const root = document.documentElement;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

/* page backdrop */
const bg = document.createElement('div'); bg.className = 'hud-bg'; bg.setAttribute('aria-hidden', 'true'); document.body.prepend(bg);

/* section banners: running number + outline watermark */
let n = 0;
$$('.bx-sec > h2').forEach((h) => {
  n += 1; h.dataset.idx = String(n).padStart(2, '0') + ' //';
  const wm = document.createElement('span'); wm.className = 'hud-wm'; wm.setAttribute('aria-hidden', 'true');
  wm.textContent = h.textContent.trim().split(/\s+/)[0]; h.appendChild(wm);
});
$$('.ar-head').forEach((hd) => {
  const h = $('.ar-h', hd); if (!h) return;
  const wm = document.createElement('span'); wm.className = 'hud-wm'; wm.setAttribute('aria-hidden', 'true');
  wm.textContent = h.textContent.trim().split(/\s+/).pop(); hd.appendChild(wm);
});

/* ---------------- Victory pop-up ---------------- */
const wp = $('#wp'); const fab = $('.wp-fab');
if (!wp) return;
const key = 'bx-wp-seen';
const lite = matchMedia('(max-width: 760px), (pointer: coarse)').matches;
if (lite) { wp.classList.add('wp-lite'); root.classList.add('wp-touch'); }
const cv = $('.wp-confetti', wp); const ctx = cv.getContext('2d');
let parts = [], craf = 0, lastFocus = null, autoT = 0, held = [];
const COLS = ['#C6FF00', '#00D9FF', '#FFD23F', '#FFFFFF', '#FF4FD8', '#FFB020'];
function burst(x, y, k) {
  for (let i = 0; i < k; i++) {
    const a = -Math.PI / 2 + (Math.random() - .5) * Math.PI * 1.25, v = 7 + Math.random() * 12;
    parts.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, w: 5 + Math.random() * 7, h: 3 + Math.random() * 5, r: Math.random() * 6.3, vr: (Math.random() - .5) * .4,
      c: COLS[(Math.random() * COLS.length) | 0], life: 1, shape: Math.random() < .25 ? 1 : 0 });
  }
}
function confetti() {
  const d = 1;
  cv.width = Math.round(innerWidth * d); cv.height = Math.round(innerHeight * d);
  const k = lite ? .4 : .7;
  parts = []; burst(innerWidth * .2, innerHeight * .75, Math.round(90 * k)); burst(innerWidth * .8, innerHeight * .75, Math.round(90 * k));
  setTimeout(() => burst(innerWidth * .5, innerHeight * .55, Math.round(80 * k)), 450);
  cancelAnimationFrame(craf);
  let last = 0;
  const step = (t) => {
    const f = last ? Math.min(3, (t - last) / 16.67) : 1; last = t;   // frames' worth of time, so 60, 90 and 120 Hz screens move alike
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height);
    for (const p of parts) {
      p.vy += .32 * f; const drag = Math.pow(.985, f); p.vx *= drag; p.vy *= drag;
      p.x += (p.vx + Math.sin(p.r * 2) * .6) * f; p.y += p.vy * f; p.r += p.vr * f;
      if (p.y > innerHeight * .55 && p.vy > 0) p.life -= .006 * f;
      const c = Math.cos(p.r) * d, sn = Math.sin(p.r) * d;
      ctx.setTransform(c, sn, -sn, c, p.x * d, p.y * d);
      ctx.globalAlpha = Math.max(0, Math.min(1, p.life)); ctx.fillStyle = p.c;
      if (p.shape) ctx.fillRect(-p.w / 3, -p.w / 3, p.w / 1.5, p.w / 1.5); else ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.abs(Math.cos(p.r * 1.7)) + 1);
    }
    parts = parts.filter((p) => p.life > 0 && p.y < innerHeight + 40);
    if (parts.length) craf = requestAnimationFrame(step); else { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height); }
  };
  craf = requestAnimationFrame(step);
}
function countUp() {
  $$('.wp-score b[data-to]', wp).forEach((b) => {
    const to = +b.dataset.to; if (reduce) { b.textContent = to; return; }
    const t0 = performance.now() + 850, dur = 900;
    const f = (t) => { const p = Math.max(0, Math.min(1, (t - t0) / dur)); b.textContent = Math.round(to * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(f); };
    b.textContent = '0'; requestAnimationFrame(f);
  });
}
const imgs = () => $$('img', wp).filter((i) => i.getAttribute('src'));
const predecode = () => Promise.all(imgs().map((i) => (i.decode ? i.decode().catch(() => {}) : null)));
(window.requestIdleCallback || ((cb) => setTimeout(cb, 1500)))(() => { predecode(); });
fab?.addEventListener('pointerenter', () => { predecode(); }, { passive: true });
function open() {
  if (!wp.hidden && !wp.classList.contains('closing')) return;
  let go = false; const start = () => { if (go) return; go = true; reallyOpen(); };
  predecode().then(start); setTimeout(start, 140);   // never wait long for a decode
}
function reallyOpen() {
  lastFocus = document.activeElement;
  wp.hidden = false; root.classList.add('hud-modal-open'); wp.classList.remove('closing');
  $$('svg.ar-court').forEach((g) => g.pauseAnimations && g.pauseAnimations());   // the hero shuttle (SMIL) behind the pop-up
  try {
    held = document.getAnimations().filter((a) => {
      const t = a.effect && a.effect.target; if (!t || wp.contains(t) || a.playState !== 'running') return false;
      return a.effect.getComputedTiming().iterations === Infinity;
    });
    held.forEach((a) => a.pause());
  } catch (e) { held = []; }
  void wp.offsetWidth; wp.classList.add('open');   // flush styles so the entrance transitions run
  countUp(); if (!reduce) setTimeout(confetti, 380);
  setTimeout(() => $('.wp-x', wp).focus({ preventScroll: true }), 60);
  try { sessionStorage.setItem(key, wp.dataset.day); } catch (e) { /* private mode */ }
  clearTimeout(autoT);
}
function close() {
  if (wp.hidden || wp.classList.contains('closing')) return;
  wp.classList.add('closing'); wp.classList.remove('open');
  $$('svg.ar-court').forEach((g) => g.unpauseAnimations && g.unpauseAnimations());
  held.forEach((a) => { try { a.play(); } catch (e) { /* element gone */ } }); held = [];
  setTimeout(() => { wp.hidden = true; wp.classList.remove('closing'); root.classList.remove('hud-modal-open'); cancelAnimationFrame(craf); ctx.clearRect(0, 0, cv.width, cv.height); }, reduce ? 0 : 380);
  if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
}
$('.wp-timer i', wp).addEventListener('animationend', close);
wp.addEventListener('click', (e) => {
  if (e.target.closest('[data-wp-close]')) { e.preventDefault(); close(); return; }
  if (e.target.closest('[data-wp-go]')) {
    e.preventDefault(); e.stopPropagation(); close();
    const go = () => { const el = $('#latest'); if (!el) return; scrollTo({ top: el.getBoundingClientRect().top + scrollY - (($('#ar-nav')?.offsetHeight || 64) + 10), behavior: reduce ? 'auto' : 'smooth' }); };
    if ($('#latest')?.closest('[hidden]') && window.arenaShow) { window.arenaShow('overview', false); setTimeout(go, 80); } else setTimeout(go, reduce ? 0 : 400);
  }
}, true);
addEventListener('keydown', (e) => {
  if (wp.hidden) return;
  if (e.key === 'Escape') { e.preventDefault(); close(); return; }
  if (e.key === 'Tab') {   // keep focus inside the dialog
    const f = $$('button, a[href]', wp).filter((x) => x.offsetParent); if (!f.length) return;
    const i = f.indexOf(document.activeElement);
    if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
  }
});
fab?.addEventListener('click', open);
let seen = null; try { seen = sessionStorage.getItem(key); } catch (e) { /* private mode */ }
if (seen !== wp.dataset.day) setTimeout(open, reduce ? 300 : 1100);
})();
"""
