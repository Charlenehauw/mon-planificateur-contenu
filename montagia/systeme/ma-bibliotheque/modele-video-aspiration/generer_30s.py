"""Pub « 6 applis aspirées dans Biz' en poche » (inspirée de la pub Hour) : une seule scène HyperFrames + index."""
import sys
from pathlib import Path
OUT = Path(sys.argv[1])

APPS = [("agenda", "Agenda"), ("notes", "Notes"), ("rappels", "Rappels"), ("tableur", "Tableur"), ("calcul", "Calculette"), ("idees", "Idées posts")]
GRILLE = [(270, 470), (540, 470), (810, 470), (270, 720), (540, 720), (810, 720)]   # centre x, haut de l'icône
BIZ = (540, 1000)       # centre x, haut de l'icône Biz' en poche (230 px)
ORBITE = [(115, 560), (115, 880), (115, 1200), (965, 620), (965, 940), (965, 1250)]
T_ASP, PAS = 0.7, 0.45  # première aspiration, écart
T_MORPH = 3.9
T_F0, D_F = 4.9, 1.7    # première fonction, durée de chacune
FEATS = [  # (titre, nouveau ?, type, source)
    ("MA SEMAINE <b>ORGANISÉE</b>", True, "video", "semaine.mp4"),
    ("TON CALENDRIER <b>ÉDITORIAL</b>", True, "video", "calendrier.mp4"),
    ("TA PRIORITÉ <b>DU JOUR</b>", False, "video", "app-objectif.mp4"),
    ("TON PLAN <b>SUR MESURE</b>", False, "video", "plan30.mp4"),
    ("TES <b>PROSPECTS</b>", False, "video", "app-prospects.mp4"),
    ("TES <b>CLIENTES</b>", False, "video", "clientes.mp4"),
    ("TON TARIF <b>JUSTE</b>", True, "img", "image-5.jpg"),
    ("TES <b>COMMISSIONS</b>", False, "video", "app-commissions.mp4"),
    ("TES <b>RÉSEAUX</b>", False, "video", "app-reseaux.mp4"),
    ("TES MESSAGES <b>PRÊTS</b>", False, "video", "messages.mp4"),
    ("TA <b>MOTIVATION</b>", False, "video", "app-motivation.mp4"),
    ("TES <b>VICTOIRES</b>", False, "video", "app-victoires.mp4"),
    ("7 <b>AMBIANCES</b>", True, "video", "ambiances.mp4"),
]
T_FIN = round(T_F0 + D_F * len(FEATS), 2)
DUREE = round(T_FIN + 3.0, 2)

css = """    @font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf"); }
    #root { position: absolute; inset: 0; }
    .haut { position: absolute; left: 0; right: 0; top: 230px; text-align: center; font-family: "Anton"; font-size: 118px; line-height: 1; color: #141210; }
    .haut b { font-weight: 400; color: #E8BD3C; }
    .app { position: absolute; width: 170px; text-align: center; }
    .tuile { width: 170px; height: 170px; border-radius: 40px; background: #FFFFFF; box-shadow: 0 10px 24px rgba(60, 40, 20, 0.15); display: flex; align-items: center; justify-content: center; }
    .tuile img { width: 96px; }
    .nom { margin-top: 10px; font-family: "Lato"; font-weight: 700; font-size: 28px; color: #5a524a; }
    #biz { position: absolute; left: 425px; top: 1000px; width: 230px; text-align: center; }
    #biz-tuile { width: 230px; height: 230px; border-radius: 54px; background: #E8BD3C; box-shadow: 0 16px 34px rgba(60, 40, 20, 0.25); padding-top: 34px; }
    #biz-tuile .l1 { font-family: "Anton"; font-size: 96px; line-height: 1; color: #141210; }
    #biz-tuile .l2 { font-family: "Anton"; font-size: 40px; line-height: 1; color: #141210; letter-spacing: 0.04em; }
    #biz .nom { font-size: 30px; color: #141210; }
    #badge { position: absolute; left: 190px; top: -22px; width: 70px; height: 70px; border-radius: 35px; background: #FF3B30; color: #FFFFFF; font-family: "Lato"; font-weight: 900; font-size: 38px; line-height: 70px; text-align: center; }
    #badge span { position: absolute; left: 0; right: 0; top: 0; }
    .tel { position: absolute; left: 230px; top: 400px; width: 620px; height: 952px; border-radius: 74px; background: #141210; padding: 20px; box-shadow: 0 50px 90px rgba(40, 28, 12, 0.32); }
    .ecran { position: relative; width: 580px; height: 912px; border-radius: 56px; overflow: hidden; background: #EDE8E3; }
    .vue { position: absolute; left: 0; top: 0; width: 580px; height: 912px; padding-top: 56px; background: #EDE8E3; }
    .vue video, .vue img.plein { width: 580px; height: 856px; object-fit: cover; object-position: top; display: block; }
    .vue.photo { display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ECE7E1; }
    .vue.photo img { width: 580px; flex: none; display: block; }
    .vue.photo img.rogne { width: 604px; }
    .ilot { position: absolute; left: 215px; top: 16px; width: 150px; height: 40px; border-radius: 20px; background: #141210; z-index: 5; }
    .mini { position: absolute; width: 120px; height: 120px; border-radius: 30px; background: #FFFFFF; box-shadow: 0 8px 20px rgba(60, 40, 20, 0.15); display: flex; align-items: center; justify-content: center; }
    .mini img { width: 70px; }
    .fleche { position: absolute; width: 120px; height: 120px; }
    .fleche path { fill: none; stroke: #8a8178; stroke-width: 6; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 220; }
    .puce { position: absolute; left: 0; right: 0; top: 170px; text-align: center; }
    .puce .neuf { display: inline-block; padding: 8px 22px; border-radius: 30px; background: #E8BD3C; font-family: "Lato"; font-weight: 900; font-size: 30px; letter-spacing: 0.12em; color: #141210; }
    .puce .titre { margin-top: 14px; font-family: "Anton"; font-size: 92px; line-height: 1; color: #141210; }
    .puce .titre b { font-weight: 400; color: #E8BD3C; }
    #splash { position: absolute; inset: 0; background: #E8BD3C; text-align: center; padding-top: 290px; z-index: 4; }
    #splash .l1 { font-family: "Anton"; font-size: 150px; line-height: 1; color: #141210; }
    #splash .l2 { font-family: "Anton"; font-size: 150px; line-height: 1; color: #FFFFFF; }
    #splash .by { margin-top: 18px; font-family: "Lato"; font-style: italic; font-size: 48px; color: #141210; }
"""
h, js = [], []
h.append('<div id="h1" class="haut">6 APPLIS…</div><div id="h2" class="haut">…DANS <b>UNE SEULE.</b></div><div id="h3" class="haut" style="top: 200px; font-size: 96px;">TOUT TON BUSINESS,<br /><b>DANS TA POCHE.</b></div>')
for i, ((k, nom), (x, y)) in enumerate(zip(APPS, GRILLE)):
    h.append(f'<div id="app{i}" class="app" style="left: {x - 85}px; top: {y}px;"><div class="tuile"><img src="assets/img/ic-{k}.png" alt="" /></div><div class="nom">{nom}</div></div>')
badge = "".join(f'<span id="b{n}">{n}</span>' for n in range(1, 7))
h.append(f'<div id="biz"><div id="biz-tuile"><div class="l1">BIZ’</div><div class="l2">EN POCHE</div></div><div class="nom">Biz’ en poche</div><div id="badge">{badge}</div></div>')
# téléphone + écrans
vues = []
for f, (titre, neuf, kind, src) in enumerate(FEATS):
    t0 = round(T_F0 + D_F * f, 2)
    if kind == "video":
        inner = f'<video id="v{f}-media" class="clip" src="assets/video/{src}" data-start="{t0}" data-duration="{D_F}" muted playsinline></video>'
        vues.append(f'<div id="v{f}" class="vue">{inner}</div>')
    else:
        # capture photo : largeur entière de l'écran, centrée en hauteur (barres de défilement rognées)
        cls = ' class="rogne"' if src in ("image-5.jpg", "image-6.jpg") else ""
        fond = ' style="background: #EFE7E4;"' if src == "image-5.jpg" else ""   # même beige que la capture
        vues.append(f'<div id="v{f}" class="vue photo"{fond}><img{cls} src="assets/img/{src}" alt="" /></div>')
    js.append(f'    tl.fromTo("#v{f}", {{ y: 912, opacity: 1 }}, {{ y: 0, duration: 0.32, ease: "power3.out" }}, {t0 - 0.05:.2f});')
    if f + 1 < len(FEATS):
        js.append(f'    tl.to("#v{f}", {{ y: -200, opacity: 0, duration: 0.3, ease: "power2.in" }}, {t0 + D_F - 0.08:.2f});')
    h.append(f'<div id="p{f}" class="puce">' + ('<div class="neuf">NOUVEAU ✨</div>' if neuf else '<div class="neuf" style="visibility: hidden;">·</div>') + f'<div class="titre">{titre}</div></div>')
    js.append(f'    tl.fromTo("#p{f}", {{ opacity: 0, y: 30, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.25, ease: "power3.out" }}, {t0:.2f});')
    if neuf:
        js.append(f'    tl.fromTo("#p{f} .neuf", {{ scale: 0.5 }}, {{ scale: 1, duration: 0.35, ease: "back.out(2.2)" }}, {t0 + 0.05:.2f});')
    js.append(f'    tl.to("#p{f}", {{ opacity: 0, y: -20, filter: "blur(6px)", duration: 0.15, ease: "power2.in" }}, {t0 + D_F - 0.15:.2f});')
h.append('<div id="tel" class="tel"><div class="ecran">' + "".join(vues) +
         '<div id="splash"><div class="l1">BIZ’ EN</div><div class="l2">POCHE</div><div class="by">by Charlène</div></div><div class="ilot"></div></div></div>')
for i, ((k, _), (x, y)) in enumerate(zip(APPS, ORBITE)):
    h.append(f'<div id="m{i}" class="mini" style="left: {x - 60}px; top: {y - 60}px;"><img src="assets/img/ic-{k}.png" alt="" /></div>')
FLECHES = [(150, 380, "M20 100 Q60 20 110 40 M92 26 L110 40 L94 56", 1), (850, 450, "M100 100 Q60 20 10 40 M28 26 L10 40 L26 56", 1),
           (150, 1020, "M20 20 Q60 100 110 80 M92 64 L110 80 L94 96", 1), (850, 1080, "M100 20 Q60 100 10 80 M28 64 L10 80 L26 96", 1)]
for i, (x, y, d, _) in enumerate(FLECHES):
    h.append(f'<svg id="f{i}" class="fleche" viewBox="0 0 120 120" style="left: {x - 60}px; top: {y - 60}px;"><path d="{d}" /></svg>')

# --- intro : les applis sont aspirées dans l'icône Biz' en poche
js0 = []
js0.append('    tl.fromTo(".app", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(1.8)", stagger: 0.05 }, 0.0);')
js0.append('    tl.fromTo("#biz", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.8)" }, 0.15);')
js0.append('    tl.fromTo("#h1", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25 }, 0.2);')
js0.append('    tl.fromTo("#badge", { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2.5)" }, ' + f"{T_ASP + 0.4:.2f});")
for i, (x, y) in enumerate(GRILLE):
    t = T_ASP + PAS * i
    dx, dy = 540 - x, (BIZ[1] + 115) - (y + 85)
    js0.append(f'    tl.to("#app{i}", {{ x: {dx}, y: {dy}, scale: 0.15, opacity: 0, rotation: {(-1) ** i * 25}, duration: 0.42, ease: "power3.in" }}, {t:.2f});')
    js0.append(f'    tl.fromTo("#biz-tuile", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.09, ease: "power2.out", yoyo: true, repeat: 1 }}, {t + 0.38:.2f});')
    js0.append(f'    tl.fromTo("#b{i + 1}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {t + 0.4:.2f});')
    if i:
        js0.append(f'    tl.to("#b{i}", {{ opacity: 0, duration: 0.01 }}, {t + 0.4:.2f});')
js0.append(f'    tl.to("#h1", {{ opacity: 0, filter: "blur(8px)", duration: 0.15 }}, {T_ASP + PAS * 4 + 0.35:.2f});')
js0.append(f'    tl.fromTo("#h2", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.25 }}, {T_ASP + PAS * 4 + 0.5:.2f});')
# --- l'icône devient le téléphone
js0.append(f'    tl.to(["#h2", "#biz .nom", "#badge"], {{ opacity: 0, duration: 0.2 }}, {T_MORPH:.2f});')
js0.append(f'    tl.to("#biz-tuile", {{ scale: 2.6, y: -240, opacity: 0, duration: 0.5, ease: "power3.in" }}, {T_MORPH:.2f});')
js0.append(f'    tl.fromTo("#tel", {{ scale: 0.3, y: 240, opacity: 0 }}, {{ scale: 1, y: 0, opacity: 1, duration: 0.7, ease: "expo.out" }}, {T_MORPH + 0.25:.2f});')
js0.append(f'    tl.fromTo(".mini", {{ scale: 0, opacity: 0, rotation: -30 }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.4, ease: "back.out(1.8)", stagger: 0.07 }}, {T_MORPH + 0.6:.2f});')
js0.append(f'    tl.fromTo(".fleche path", {{ strokeDashoffset: 220 }}, {{ strokeDashoffset: 0, duration: 0.5, ease: "power2.out", stagger: 0.08 }}, {T_MORPH + 0.9:.2f});')
# --- fin : écran jaune avec la marque
js.append(f'    tl.fromTo("#splash", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.45, ease: "power3.inOut" }}, {T_FIN:.2f});')
js.append(f'    tl.fromTo("#splash .l1, #splash .l2", {{ scale: 1.3, opacity: 0, filter: "blur(10px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out", stagger: 0.1 }}, {T_FIN + 0.35:.2f});')
js.append(f'    tl.fromTo("#splash .by", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {T_FIN + 0.75:.2f});')
js.append(f'    tl.fromTo("#h3", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3 }}, {T_FIN + 0.2:.2f});')
js.append(f'    tl.fromTo(".mini", {{ y: 0 }}, {{ y: -16, duration: 0.15, ease: "power2.out", yoyo: true, repeat: 1, stagger: 0.05 }}, {T_FIN + 0.4:.2f});')

scene_html = f"""<template>
  <style>
{css}  </style>
  <div id="root" data-composition-id="pub" data-width="1080" data-height="1920">
    <div id="pub-scene" class="clip" data-start="0" data-duration="{DUREE}" data-layout-allow-overlap data-layout-allow-occlusion data-layout-allow-caption-zone>
      {chr(10).join('      ' + x for x in h).strip()}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // 1. les applis habituelles sont aspirées dans l'icône Biz' en poche, la pastille compte 1 à 6
{chr(10).join(js0)}
    // 2. le téléphone montre les nouveautés une par une
{chr(10).join(js)}
    window.__timelines["pub"] = tl;
  </script>
</template>
"""
(OUT / "compositions" / "pub.html").write_text(scene_html, encoding="utf-8")

sons = [("pop", T_ASP + PAS * i + 0.4, 0.45) for i in range(6)]
sons += [("whoosh", T_MORPH + 0.05, 0.5), ("pop", T_MORPH + 0.65, 0.3)]
sons += [("clic", T_F0 + D_F * f - 0.03, 0.6) for f in range(len(FEATS))]
sons += [("ding", T_F0 + D_F * f + 0.1, 0.22) for f, x in enumerate(FEATS) if x[1]]
sons += [("whoosh", T_FIN - 0.05, 0.4), ("impact", T_FIN + 0.4, 0.45)]
audios = "".join(f'\n      <audio id="sfx-{i + 1}" class="clip" src="assets/sons/{f}.wav" data-start="{t:.2f}" data-track-index="{10 + i}" data-volume="{v}"></audio>' for i, (f, t, v) in enumerate(sorted(sons, key=lambda s: s[1])))
index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #ede8e3; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #fond {{ position: absolute; inset: 0; z-index: 0;
        background: radial-gradient(ellipse 70% 45% at 50% 45%, rgba(255, 253, 249, 0.9) 0%, rgba(255, 253, 249, 0) 70%), linear-gradient(180deg, #f1ece6 0%, #ebe4dc 60%, #e2d8cd 100%); }}
      .scene {{ z-index: 2; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUREE}" data-width="1080" data-height="1920">
      <div id="fond" class="clip" data-start="0" data-duration="{DUREE}" data-track-index="0"></div>
      <div id="pub" class="scene" data-composition-id="pub" data-composition-src="compositions/pub.html"
        data-start="0" data-duration="{DUREE}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <!-- bruitages (Montag'IA), chacun sur une action visible -->{audios}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
(OUT / "index.html").write_text(index, encoding="utf-8")
print("durée", DUREE)

