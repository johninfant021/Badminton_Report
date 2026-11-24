"""Champions pop-up: a 3D card reveal for the latest final.

winner_html() is built from tables.json (the last Final and that day's rows), so it always shows the most recent
champions. The champion cards fly in face-down and flip over one after the other; score, runners-up and buttons follow.

Performance rules (phones lagged and blinked with earlier versions):
- only transform and opacity are ever animated;
- every element's resting style is its final state, so closing, skipping and reduced motion need no special cases;
- no filter, backdrop-filter or shadow on anything that moves; clip-path only on leaf layers, never on a
  preserve-3d element (it would flatten the card);
- flashes stay inside the card, never across the screen.
"""
from html import escape
import photos

TROPHY = ('<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><defs><linearGradient id="wp-g" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#FFF3B0"/><stop offset=".55" stop-color="#FFD23F"/><stop offset="1" stop-color="#E09A00"/></linearGradient></defs>'
          '<path d="M20 8h24v14a12 12 0 0 1-24 0z" fill="url(#wp-g)"/>'
          '<path d="M20 12h-8v4a9 9 0 0 0 9 9M44 12h8v4a9 9 0 0 1-9 9" stroke="#FFD23F" stroke-width="3" stroke-linecap="round"/>'
          '<path d="M29 34h6v9h-6z" fill="#E0A800"/><path d="M22 44h20l2 8H20z" fill="url(#wp-g)"/><path d="M18 52h28v4H18z" fill="#B87F00"/></svg>')
EMBLEM = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<path d="M12 21a3 3 0 0 0 3-3H9a3 3 0 0 0 3 3z"/><path d="M9 18 5 4l7 3 7-3-4 14"/><path d="M12 7v11"/></svg>')
CROWN = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 18h18l-1.6-9.5-4.6 4.1L12 5l-2.8 7.6-4.6-4.1z"/></svg>'


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
    mvp = max(champs, key=lambda q: D[q]['adj'] if q in D else -99)
    def pic(q):
        # a crop made for the card (faces line up across the pair); the shared portrait if there is no photo file
        try:
            return f'src="{photos.data_uri(photos.card(q), 80)}"'
        except FileNotFoundError:
            return f'data-ph-portrait="{escape(q)}"'

    today = lambda q: f'{D[q]["W"]}–{D[q]["L"]}' if q in D else '–'

    def card(q, i):
        badge = (f'<span class="vc-badge" title="Best adjusted score of the two champions on the day: {D[q]["adj"]:+.2f} per match">MVP</span>'
                 if q == mvp and q in D else '')
        return (f'<div class="vc" style="--pc:{col(q)};--i:{i}"><div class="vc-fly"><div class="vc-tilt"><div class="vc-flip">'
                f'<div class="vc-thick" aria-hidden="true"></div>'
                f'<div class="vc-back" aria-hidden="true"><span class="vc-edge"></span><span class="vc-plate"><span class="vc-weave"></span><i class="vc-emb">{EMBLEM}</i><b>CHAMPION</b></span></div>'
                f'<div class="vc-front"><span class="vc-edge"></span>'
                f'<span class="vc-plate"><img {pic(q)} alt="" decoding="async"><span class="vc-shade"></span><span class="vc-line"></span><span class="vc-foil"></span></span>'
                f'{badge}<span class="vc-crown" aria-hidden="true">{CROWN}</span>'
                f'<span class="vc-name"><b>{escape(q)}</b><span class="vc-stats"><span><em>{today(q)}</em>today</span><span><em>{titles.get(q, 0)}</em>titles</span></span></span></div>'
                f'</div></div><span class="vc-burst" aria-hidden="true"></span></div><span class="vc-floor" aria-hidden="true"></span></div>')

    def mini(q):
        return (f'<span class="vr" style="--pc:{col(q)}"><span class="vr-ph"><img data-ph-avatar="{escape(q)}" alt=""></span>'
                f'<span class="vr-tx"><b>{escape(q)}</b><small>{today(q)} today</small></span></span>')

    try:
        w, d = day.split(); label = f'Week {int(w[1:])} · Day {int(d[1:])}'
    except Exception:
        label = day
    word = 'CHAMPIONS'
    letters = ''.join(f'<span class="wp-l" data-c="{c}" style="--n:{i}">{c}</span>' for i, c in enumerate(word))
    return (f'<div class="wp" id="wp" role="dialog" aria-modal="true" aria-labelledby="wp-t" aria-describedby="wp-d" data-day="{escape(day)}" hidden>'
            f'<div class="wp-bg" data-wp-close></div><div class="wp-beams" aria-hidden="true"><i></i><i></i><i></i></div>'
            f'<div class="wp-box"><span class="wp-frame" aria-hidden="true"></span>'
            f'<button type="button" class="wp-x" data-wp-close aria-label="Close">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg></button>'
            f'<div class="wp-scroll"><div class="wp-grid">'
            f'<div class="wp-head"><p class="wp-k"><span>{label}</span><span>Final result</span></p>'
            f'<h2 class="wp-t" id="wp-t"><span class="wp-sr">Champions</span><span class="wp-ls" aria-hidden="true">{letters}</span></h2></div>'
            f'<div class="wp-stage"><span class="wp-ring" aria-hidden="true"></span>{"".join(card(q, i) for i, q in enumerate(champs))}</div>'
            f'<div class="wp-info">'
            f'<div class="wp-score" role="img" aria-label="Final score {ws} to {ls}"><b class="w">{ws}</b><i></i><b>{ls}</b></div>'
            f'<div class="wp-run"><small class="wp-rl">Runners-up</small><div class="wp-rs">{"".join(mini(q) for q in runners)}</div></div>'
            f'<p class="wp-sub" id="wp-d"><b>{escape(" + ".join(champs))}</b> beat {escape(" + ".join(runners))} {ws}–{ls} to win {escape(day).replace(" ", "&nbsp;")}.</p>'
            f'<div class="wp-ctas"><a class="ar-cta" href="#latest" data-wp-go>Match report</a>'
            f'<button type="button" class="ar-cta ghost" data-wp-close>Continue</button></div>'
            f'<div class="wp-timer" aria-hidden="true"><i></i></div></div>'
            f'</div></div></div><canvas class="wp-confetti" aria-hidden="true"></canvas></div>'
            f'<button type="button" class="wp-fab" aria-controls="wp" aria-label="Show the latest champions">{TROPHY}'
            f'<span><small>{escape(day)} champions</small><b>{escape(" + ".join(champs))}</b></span></button>')


VICTORY_CSS = r"""
/* =====================================================================
   Champions pop-up — 3D card reveal
   ===================================================================== */
.wp { --cut: 22px; --cw: 220px; position: fixed; inset: 0; z-index: 2000; display: grid; place-items: center; padding: 18px; color: #F5F7FA; }
.wp[hidden] { display: none; }
.wp-sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.wp-bg { position: absolute; inset: 0; opacity: 0; transition: opacity .4s ease;
  background: radial-gradient(60% 60% at 36% 48%, rgba(74, 54, 4, .62), transparent 70%), radial-gradient(50% 55% at 78% 60%, rgba(0, 70, 96, .5), transparent 70%), rgba(3, 5, 10, .94); }
.wp.open .wp-bg { opacity: 1; }
.wp.closing .wp-bg { opacity: 0; }
/* stage lights: three still beams that only fade and slide in */
.wp-beams { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.wp-beams i { position: absolute; top: -15%; left: 12%; width: 22vw; height: 130%; opacity: .5; transform: skewX(-16deg); background: linear-gradient(90deg, transparent, rgba(255, 210, 63, .13) 50%, transparent); }
.wp-beams i:nth-child(2) { left: 40%; width: 14vw; transform: skewX(10deg); background: linear-gradient(90deg, transparent, rgba(0, 217, 255, .12) 50%, transparent); }
.wp-beams i:nth-child(3) { left: 68%; transform: skewX(18deg); }
.wp.closing .wp-beams { opacity: 0; }

/* ---------------- panel ---------------- */
.wp-box { position: relative; width: min(1220px, 100%); }
.wp.closing .wp-box { animation: wp-out .32s ease-in forwards; }
.wp-frame, .wp-frame::before { position: absolute; inset: 0; clip-path: polygon(34px 0, 100% 0, 100% calc(100% - 34px), calc(100% - 34px) 100%, 0 100%, 0 34px); }
.wp-frame { background: linear-gradient(120deg, #FFE680, rgba(255, 210, 63, .18) 24%, rgba(255, 255, 255, .08) 50%, rgba(0, 217, 255, .25) 76%, #00D9FF); }
.wp-frame::before { content: ""; inset: 1.5px; background: radial-gradient(80% 90% at 28% 30%, rgba(255, 210, 63, .12), transparent 60%), linear-gradient(160deg, #131824, #080B12 70%); }
.wp-scroll { position: relative; max-height: calc(100vh - 36px); max-height: calc(100svh - 36px); overflow: hidden auto; scrollbar-width: none; }
.wp-scroll::-webkit-scrollbar { display: none; }
.wp-grid { display: grid; grid-template-columns: auto minmax(300px, 1fr); grid-template-areas: "stage head" "stage info"; grid-template-rows: auto 1fr; column-gap: clamp(24px, 4vw, 60px); padding: 34px 44px 30px 40px; align-items: center; overflow: hidden; overflow: clip; }
.wp-x { position: absolute; right: 14px; top: 14px; z-index: 3; width: 40px; height: 40px; display: grid; place-items: center; border-radius: 12px; border: 1px solid rgba(255, 255, 255, .18); background: rgba(8, 11, 18, .85); color: #F5F7FA; cursor: pointer; transition: transform .2s ease, border-color .2s ease; }
.wp-x svg { width: 18px; height: 18px; }
.wp-x:hover { transform: scale(1.08); border-color: var(--ar-gold); }

/* ---------------- heading ---------------- */
.wp-head { grid-area: head; align-self: end; min-width: 0; }
.wp-k { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 48px 12px 0; }
.wp-k span { padding: 6px 12px 5px; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .18em; text-transform: uppercase; color: #0A0E14; background: var(--ar-gold); clip-path: polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%); }
.wp-k span + span { color: #BFEFFF; background: rgba(0, 217, 255, .16); }
.wp-t { margin: 0; perspective: 600px; font: 900 clamp(34px, 4.6vw, 60px)/1.05 var(--ar-h, var(--m-display)); letter-spacing: .03em; white-space: nowrap; }
/* each letter: dark copy underneath for depth, gold copy on top */
.wp-l { position: relative; display: inline-block; color: #7A5200; transform-origin: 50% 100%; }
.wp-l::after { content: attr(data-c); position: absolute; left: 0; top: -.055em; background: linear-gradient(180deg, #FFFBE0 8%, #FFD23F 55%, #E39A00 92%); -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-fill-color: transparent; }

/* ---------------- champion cards ---------------- */
.wp-stage { grid-area: stage; position: relative; display: flex; justify-content: center; gap: clamp(14px, 1.8vw, 26px); padding: 10px 4px 30px; }
.wp-ring { position: absolute; left: 50%; top: 46%; width: 420px; height: 420px; margin: -210px 0 0 -210px; border-radius: 50%; pointer-events: none;
  background: radial-gradient(circle, rgba(255, 210, 63, .20), transparent 62%); }
.wp-ring::before { content: ""; position: absolute; inset: 26px; border-radius: 50%; border: 1.5px dashed rgba(255, 210, 63, .28); }
.vc { position: relative; width: var(--cw); aspect-ratio: 5 / 7.2; flex: none; }
.vc-fly { position: absolute; inset: 0; perspective: 1500px; }
.vc-tilt, .vc-flip, .vc-front, .vc-back { position: absolute; inset: 0; transform-style: preserve-3d; -webkit-transform-style: preserve-3d; }
.vc-tilt { transition: transform .25s ease-out; }
/* front at 0, the thickness behind it, the back behind that: from either side the face you see is nearest */
.vc-back { transform: rotateY(180deg) translateZ(14px); }
.vc-front > *, .vc-back > * { -webkit-backface-visibility: hidden; backface-visibility: hidden; }
/* the notched metal frame: edge (metal) with the plate inset inside it, both cut to the same shape */
.vc-edge, .vc-plate, .vc-thick { position: absolute; display: block;
  clip-path: polygon(0 var(--cut), var(--cut) 0, 58% 0, calc(58% + 9px) 9px, calc(100% - 15px) 9px, 100% 24px, 100% calc(100% - var(--cut)), calc(100% - var(--cut)) 100%, 42% 100%, calc(42% - 9px) calc(100% - 9px), 15px calc(100% - 9px), 0 calc(100% - 24px)); }
.vc-edge { inset: 0; background: linear-gradient(135deg, #FFF6CF 0, #FFD23F 16%, #9A6A00 34%, #FFE680 50%, #B87F00 66%, #FFF0A8 82%, #8A5C00 100%); }
.vc-plate { inset: 4px; overflow: hidden; background: #0B0F17; }
.vc-thick { inset: 0; background: linear-gradient(180deg, #6B4800, #2E1F00); transform: translateZ(-7px); }
.vc-plate img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
.vc-shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(6, 9, 15, .25), transparent 22%, transparent 62%, rgba(6, 9, 15, .5) 100%), linear-gradient(0deg, color-mix(in srgb, var(--pc) 30%, transparent), transparent 26%); }
.vc-line { position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: linear-gradient(180deg, transparent, var(--pc) 30%, var(--pc) 70%, transparent); }
/* foil: a wide light band that slides across once the card has landed */
.vc-foil { position: absolute; top: -20%; bottom: -20%; left: 0; width: 60%; opacity: 0; transform: translateX(-130%) skewX(-20deg);
  background: linear-gradient(90deg, transparent, rgba(0, 217, 255, .22) 30%, rgba(255, 255, 255, .5) 50%, rgba(255, 210, 63, .3) 70%, transparent); }
.vc-name { position: absolute; left: 18px; right: 18px; bottom: 24px; display: grid; gap: 7px; padding: 10px 12px 9px 15px; text-align: left; transform: translateZ(20px);
  background: linear-gradient(90deg, rgba(5, 8, 14, .92) 55%, rgba(5, 8, 14, .62)); clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px)); }
.vc-name::before { content: ""; position: absolute; left: 0; top: 0; bottom: 12px; width: 4px; background: var(--pc); }
.vc-name::after { content: ""; position: absolute; left: 0; right: 12px; top: 0; height: 1.5px; background: linear-gradient(90deg, var(--ar-gold), transparent); }
.vc-name b { font: 900 clamp(17px, 1.75vw, 25px)/1 var(--ar-h, var(--m-display)); letter-spacing: .03em; color: #fff; white-space: nowrap; }
.vc-stats { display: flex; gap: 18px; }
.vc-stats > span { font: 600 10px/1.2 var(--m-body); letter-spacing: .04em; color: #C9D1DD; }
.vc-stats em { display: block; font: 800 15px/1.1 var(--ar-h, var(--m-display)); color: var(--ar-gold); font-style: normal; font-variant-numeric: tabular-nums; }
.vc-crown { position: absolute; left: 13px; top: 15px; width: 24px; height: 24px; color: var(--ar-gold); transform: translateZ(22px); }
.vc-crown svg { width: 100%; height: 100%; display: block; }
.vc-badge { position: absolute; right: -8px; top: 20px; padding: 8px 14px 7px; font: 900 13px/1 var(--ar-h, var(--m-display)); letter-spacing: .14em; color: #241A00; transform: translateZ(42px);
  background: linear-gradient(180deg, #FFF6CF, #FFC21A); clip-path: polygon(10px 0, 100% 0, calc(100% - 6px) 50%, 100% 100%, 10px 100%, 0 50%); }
.vc-back .vc-plate { display: grid; place-content: center; justify-items: center; gap: 12px; background: radial-gradient(70% 60% at 50% 44%, #2A2206, #0A0D14 78%); }
.vc-weave { position: absolute; inset: 0; opacity: .5; background: repeating-linear-gradient(45deg, rgba(255, 210, 63, .10) 0 2px, transparent 2px 16px), repeating-linear-gradient(-45deg, rgba(255, 210, 63, .10) 0 2px, transparent 2px 16px); }
.vc-emb { position: relative; width: 42%; min-width: 64px; aspect-ratio: 1; display: grid; place-items: center; color: var(--ar-gold); border-radius: 50%; border: 2px solid rgba(255, 210, 63, .55); background: #0B0F17; }
.vc-emb svg { width: 58%; height: 58%; }
.vc-back b { position: relative; font: 800 11px/1 var(--ar-h, var(--m-display)); letter-spacing: .26em; color: var(--ar-gold); }
.vc-burst { position: absolute; inset: -18%; border-radius: 50%; opacity: 0; pointer-events: none; background: radial-gradient(circle, rgba(255, 244, 200, .85), rgba(255, 210, 63, .35) 34%, transparent 66%); }
.vc-floor { position: absolute; left: 6%; right: 6%; bottom: -24px; height: 22px; border-radius: 50%; background: radial-gradient(closest-side, color-mix(in srgb, var(--pc) 55%, transparent), transparent); }

/* ---------------- score, runners-up, buttons ---------------- */
.wp-info { grid-area: info; align-self: start; display: grid; gap: 16px; margin-top: 18px; min-width: 0; }
.wp-score { position: relative; display: inline-flex; align-items: center; justify-self: start; gap: 16px; padding: 10px 26px 8px 22px; font: 900 clamp(44px, 5vw, 64px)/1 var(--ar-h, var(--m-display)); font-variant-numeric: tabular-nums;
  background: linear-gradient(100deg, rgba(255, 210, 63, .22), rgba(255, 255, 255, .04) 70%); clip-path: polygon(0 0, 100% 0, calc(100% - 18px) 100%, 0 100%); }
.wp-score::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--ar-gold); }
.wp-score b { color: #8E98AB; } .wp-score b.w { color: var(--ar-gold); }
.wp-score i { width: 4px; height: .72em; background: rgba(255, 255, 255, .28); transform: skewX(-16deg); }
.wp-rl { display: block; margin-bottom: 8px; font: 700 10.5px/1 var(--ar-h, var(--m-display)); letter-spacing: .2em; text-transform: uppercase; color: #9AA6B8; }
.wp-rs { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; max-width: 440px; }
/* runners-up: steel plates, same cut language as the champion frames */
.vr { display: flex; align-items: center; gap: 10px; min-width: 0; padding: 7px 10px 7px 7px; background: linear-gradient(110deg, rgba(160, 172, 194, .22), rgba(160, 172, 194, .05)); clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px)); }
.vr-ph { flex: none; width: 46px; height: 46px; padding: 2px; background: linear-gradient(135deg, #E6ECF5, #6C788C 50%, #C3CCDA); clip-path: polygon(0 0, calc(100% - 9px) 0, 100% 9px, 100% 100%, 9px 100%, 0 calc(100% - 9px)); }
.vr-ph img { width: 100%; height: 100%; object-fit: cover; display: block; clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px)); }
.vr-tx { display: grid; gap: 2px; min-width: 0; text-align: left; }
.vr-tx b { font: 700 14px/1.2 var(--ar-h, var(--m-display)); color: #E6EBF3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.vr-tx small { font-size: 11px; color: #9AA6B8; }
.wp-sub { margin: 0; max-width: 48ch; color: #C3CBD8; font-size: 14px; line-height: 1.5; text-align: left; }
.wp-sub b { color: #fff; }
.wp-ctas { display: flex; flex-wrap: wrap; gap: 12px; }
.wp-ctas .ar-cta { margin: 0; }
.wp-timer { height: 3px; width: min(320px, 100%); background: rgba(255, 255, 255, .1); overflow: hidden; }
.wp-timer i { display: block; height: 100%; width: 100%; transform-origin: 0 50%; background: linear-gradient(90deg, var(--ar-gold), var(--ar-cyan)); }
.wp-confetti { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 4; pointer-events: none; }

/* ---------------- the reveal (transform and opacity only) ---------------- */
.wp.open .wp-box { animation: wp-in .55s cubic-bezier(.2, .9, .25, 1) both; }
.wp.open .wp-beams i { animation: wp-beam .9s ease-out .1s backwards; }
.wp.open .wp-k { animation: wp-up .45s ease-out .3s backwards; }
.wp.open .wp-l { animation: wp-letter .55s cubic-bezier(.2, 1.2, .35, 1) calc(.4s + var(--n) * .045s) backwards; }
.wp.open .wp-ring { animation: wp-ring .9s cubic-bezier(.2, .9, .25, 1) .35s backwards; }
.wp.open .vc-fly { animation: vc-fly .75s cubic-bezier(.18, .95, .3, 1) calc(.45s + var(--i) * .14s) backwards; }
.wp.open .vc-flip { animation: vc-flip .95s cubic-bezier(.35, .1, .2, 1) calc(1.4s + var(--i) * .5s) backwards; }
.wp.open .vc-burst { animation: vc-burst .75s ease-out calc(1.72s + var(--i) * .5s) both; }
.wp.open .vc-foil { animation: vc-foil .9s ease-in-out calc(2.4s + var(--i) * .5s) 1 both; }
.wp.open .vc-badge { animation: vc-badge .45s cubic-bezier(.2, 1.5, .4, 1) 2.75s backwards; }
.wp.open .vc-floor { animation: wp-fade .6s ease-out 1s backwards; }
.wp.open .wp-score { animation: wp-score .5s cubic-bezier(.2, 1.25, .35, 1) 2.5s backwards; }
.wp.open .wp-run { animation: wp-up .45s ease-out 2.75s backwards; }
.wp.open .wp-sub { animation: wp-up .45s ease-out 2.9s backwards; }
.wp.open .wp-ctas { animation: wp-up .4s ease-out 1.2s backwards; }
.wp.open .wp-timer { animation: wp-fade .4s ease-out 3.1s backwards; }
.wp.open .wp-timer i { animation: wp-timer 11s linear 3.4s forwards; }
@media (hover: hover) { .wp-box:hover .wp-timer i { animation-play-state: paused; } }   /* not on touch, where hover sticks after a tap */
@keyframes wp-in { from { opacity: 0; transform: translateY(40px) scale(.94); } }
@keyframes wp-out { to { opacity: 0; transform: translateY(24px) scale(.95); } }
@keyframes wp-beam { from { opacity: 0; } }
@keyframes wp-fade { from { opacity: 0; } }
@keyframes wp-up { from { opacity: 0; transform: translateY(14px); } }
@keyframes wp-letter { from { opacity: 0; transform: translateY(.3em) rotateX(-85deg); } }
@keyframes wp-ring { from { opacity: 0; transform: scale(.4); } }
@keyframes wp-score { from { opacity: 0; transform: translateX(-40px) scale(1.25); } }
@keyframes wp-timer { to { transform: scaleX(0); } }
@keyframes vc-fly { 0% { opacity: 0; transform: translateY(120px) scale(.6); } 60% { opacity: 1; } }
@keyframes vc-flip { 0% { transform: translateZ(0) rotateY(180deg); } 12% { transform: translateZ(0) rotateY(190deg); } 55% { transform: translateZ(50px) rotateY(60deg); } 80% { transform: translateZ(20px) rotateY(-12deg); } 100% { transform: translateZ(0) rotateY(0deg); } }
@keyframes vc-burst { 0% { opacity: 0; transform: scale(.3); } 25% { opacity: .75; } 100% { opacity: 0; transform: scale(1.25); } }
@keyframes vc-foil { 0% { opacity: 1; transform: translateX(-130%) skewX(-20deg); } 100% { opacity: 1; transform: translateX(270%) skewX(-20deg); } }
@keyframes vc-badge { from { opacity: 0; transform: translateZ(120px) scale(2); } }

/* ---------------- trophy button ---------------- */
.wp-fab { position: fixed; right: 18px; bottom: 18px; z-index: 60; display: flex; align-items: center; gap: 0; padding: 7px; border-radius: 999px; cursor: pointer; text-align: left; color: var(--ar-fg); font-family: inherit;
  background: linear-gradient(180deg, rgba(30, 28, 12, .92), rgba(10, 13, 20, .95)); border: 1px solid rgba(255, 210, 63, .5); box-shadow: 0 0 24px rgba(255, 210, 63, .25), 0 14px 30px -12px #000;
  transition: transform .25s var(--ar-ease), opacity .3s ease; }
.wp-fab svg { width: 34px; height: 34px; flex: none; }
.wp-fab span { display: grid; line-height: 1.15; max-width: 0; opacity: 0; overflow: hidden; white-space: nowrap; transition: max-width .35s var(--ar-ease), opacity .25s ease, margin .35s var(--ar-ease); }
.wp-fab:hover span, .wp-fab:focus-visible span { max-width: 220px; opacity: 1; margin: 0 10px 0 10px; }
.wp-fab small { font: 700 9.5px/1.2 var(--ar-h, var(--m-display)); letter-spacing: .16em; text-transform: uppercase; color: var(--ar-gold); }
.wp-fab b { font-size: 13px; }
.wp-fab:hover { transform: translateY(-3px); }
html.hud-modal-open .wp-fab { opacity: 0; pointer-events: none; }

/* ---------------- sizes ---------------- */
@media (min-width: 981px) { .wp { --cw: min(296px, 20.5vw, 39vh); } }
@media (min-width: 981px) and (max-height: 620px) { .wp-grid { padding: 22px 40px 20px 34px; } .wp-info { gap: 11px; margin-top: 12px; } .wp-sub { display: none; } }
@media (max-width: 980px) {
  .wp { --cw: min(200px, 36vw); padding: 12px; }
  .wp-box { width: min(560px, 100%); }
  .wp-scroll { max-height: calc(100vh - 24px); max-height: calc(100svh - 24px); }
  .wp-grid { grid-template-columns: minmax(0, 1fr); grid-template-areas: "head" "stage" "info"; grid-template-rows: auto; padding: 22px 18px 18px; justify-items: center; }
  .wp-head { text-align: center; width: 100%; }
  .wp-k { justify-content: center; flex-wrap: nowrap; gap: 6px; margin: 4px 44px 14px; }
  .wp-k span { font-size: 9px; letter-spacing: .06em; padding: 6px 10px 5px; white-space: nowrap; }
  .wp-t { font-size: min(11vw, 56px); letter-spacing: 0; }
  .wp-stage { padding: 18px 0 28px; }
  .wp-ring { width: 300px; height: 300px; margin: -150px 0 0 -150px; }
  .wp-info { width: 100%; justify-items: center; gap: 13px; margin-top: 8px; }
  .wp-score { justify-self: center; font-size: 42px; padding: 8px 28px 6px 24px; clip-path: polygon(14px 0, 100% 0, calc(100% - 14px) 100%, 0 100%); }
  .wp-score::before { display: none; }
  .wp-run { width: 100%; max-width: 420px; }
  .wp-rl { text-align: center; }
  .wp-sub { text-align: center; font-size: 13px; }
  .wp-ctas { width: 100%; flex-wrap: nowrap; } .wp-ctas .ar-cta { flex: 1 1 0; min-width: 0; padding: 13px 6px; font-size: 11.5px; letter-spacing: .06em; white-space: nowrap; justify-content: center; }
}
@media (max-width: 480px) {
  .wp { --cut: 17px; --cw: min(156px, 39vw); }
  .vc-name { left: 12px; right: 12px; bottom: 17px; gap: 5px; padding: 8px 8px 7px 11px; } .vc-name b { font-size: 15px; } .vc-stats { gap: 10px; } .vc-stats em { font-size: 13px; } .vc-stats > span { font-size: 9px; }
  .vc-badge { font-size: 11px; padding: 6px 11px 5px; right: -5px; top: 17px; } .vc-crown { width: 19px; height: 19px; left: 11px; top: 13px; }
  .vc-back b { font-size: 9px; letter-spacing: .18em; }
  .vr { gap: 8px; } .vr-ph { width: 38px; height: 38px; } .vr-tx b { font-size: 12.5px; }
  .wp-fab { right: 12px; bottom: 12px; } .wp-fab svg { width: 28px; height: 28px; }
}
@media (max-width: 980px) and (max-height: 700px) { .wp-sub { display: none; } .wp-grid { padding-top: 14px; padding-bottom: 14px; } .wp-stage { padding: 12px 0 22px; } .wp { --cw: min(140px, 34vw, 23vh); } }
@media (prefers-reduced-motion: reduce) { .wp *, .wp *::before, .wp *::after { animation: none !important; transition: none !important; } }
"""

VICTORY_JS = r"""
(() => {
const root = document.documentElement;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const wp = $('#wp'); const fab = $('.wp-fab');
if (!wp) return;
const key = 'bx-wp-seen';
const lite = matchMedia('(max-width: 760px), (pointer: coarse)').matches;
const cv = $('.wp-confetti', wp); const ctx = cv.getContext('2d');
let parts = [], craf = 0, lastFocus = null, timers = [];
const later = (f, ms) => timers.push(setTimeout(f, ms));
const COLS = ['#FFD23F', '#FFF3B0', '#00D9FF', '#C6FF00', '#FFFFFF', '#FFB020'];
function burst(x0, w, y, k) {
  for (let i = 0; i < k; i++) {
    const a = -Math.PI / 2 + (Math.random() - .5) * Math.PI * .9, v = 8 + Math.random() * 12;
    parts.push({ x: x0 + Math.random() * w, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, w: 4 + Math.random() * 6, h: 3 + Math.random() * 4, r: Math.random() * 6.3, vr: (Math.random() - .5) * .4, c: COLS[(Math.random() * COLS.length) | 0], life: 1 });
  }
}
function confetti() {
  const d = Math.min(devicePixelRatio || 1, lite ? 1 : 1.5);
  cv.width = Math.round(innerWidth * d); cv.height = Math.round(innerHeight * d);
  const k = lite ? .4 : 1; parts = [];
  // one burst behind each champion card, as that card lands
  $$('.vc', wp).forEach((c, i) => { const r = c.getBoundingClientRect(); later(() => { burst(r.left, r.width, r.bottom - 10, Math.round(95 * k)); kick(); }, i * 500); });
  let last = 0;
  const step = (t) => {
    const f = last ? Math.min(3, (t - last) / 16.67) : 1; last = t;   // frames' worth of time, so 60, 90 and 120 Hz screens move alike
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height);
    for (const p of parts) {
      p.vy += .3 * f; const drag = Math.pow(.982, f); p.vx *= drag; p.vy *= drag;
      p.x += (p.vx + Math.sin(p.r * 2) * .6) * f; p.y += p.vy * f; p.r += p.vr * f;
      if (p.vy > 0) p.life -= .007 * f;
      const c = Math.cos(p.r) * d, sn = Math.sin(p.r) * d;
      ctx.setTransform(c, sn, -sn, c, p.x * d, p.y * d);
      ctx.globalAlpha = Math.max(0, Math.min(1, p.life)); ctx.fillStyle = p.c;
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.abs(Math.cos(p.r * 1.7)) + 1);
    }
    parts = parts.filter((p) => p.life > 0 && p.y < innerHeight + 40);
    if (parts.length) craf = requestAnimationFrame(step); else { craf = 0; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height); }
  };
  const kick = () => { if (!craf) { last = 0; craf = requestAnimationFrame(step); } };
}
function stop() { timers.forEach(clearTimeout); timers = []; cancelAnimationFrame(craf); craf = 0; parts = []; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height); }
function open() {
  if (!wp.hidden) return;
  stop(); lastFocus = document.activeElement;
  wp.hidden = false; root.classList.add('hud-modal-open'); wp.classList.remove('closing');
  $('.wp-scroll', wp).scrollTop = 0;
  $$('svg').forEach((g) => g.pauseAnimations && g.pauseAnimations());   // SVG path animations behind the pop-up
  // have the photos decoded before anything moves, so no card waits for its picture in the middle of a flip
  const imgs = $$('img', wp).filter((i) => i.src).map((i) => (i.decode ? i.decode().catch(() => {}) : 0));
  Promise.race([Promise.all(imgs), new Promise((r) => setTimeout(r, 500))]).then(() => {
    if (wp.hidden || wp.classList.contains('closing')) return;
    void wp.offsetWidth; wp.classList.add('open');
    if (!reduce) later(confetti, 1900);
  });
  setTimeout(() => $('.wp-x', wp).focus({ preventScroll: true }), 60);
  try { sessionStorage.setItem(key, wp.dataset.day); } catch (e) { /* private mode */ }
}
function close() {
  if (wp.hidden || wp.classList.contains('closing')) return;
  stop(); wp.classList.add('closing'); wp.classList.remove('open');
  $$('svg').forEach((g) => g.unpauseAnimations && g.unpauseAnimations());
  setTimeout(() => { wp.hidden = true; wp.classList.remove('closing'); root.classList.remove('hud-modal-open'); }, reduce ? 0 : 320);
  if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
}
$('.wp-timer i', wp).addEventListener('animationend', close);
// a tap on the cards skips to the end of the reveal
$('.wp-stage', wp).addEventListener('click', () => {
  if (!wp.getAnimations) return;
  wp.getAnimations({ subtree: true }).forEach((a) => { const el = a.effect && a.effect.target; if (el && !el.closest('.wp-timer') && a.animationName) a.finish(); });
});
// desktop: the cards turn towards the pointer
if (!reduce && matchMedia('(hover: hover) and (pointer: fine)').matches) {
  $$('.vc', wp).forEach((c) => {
    const t = $('.vc-tilt', c); let raf = 0;
    c.addEventListener('pointermove', (e) => {
      if (raf) return;
      raf = requestAnimationFrame(() => { raf = 0; const r = c.getBoundingClientRect(); const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5; t.style.transform = `rotateX(${(-y * 16).toFixed(1)}deg) rotateY(${(x * 20).toFixed(1)}deg)`; });
    });
    c.addEventListener('pointerleave', () => { cancelAnimationFrame(raf); raf = 0; t.style.transform = ''; });
  });
}
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
