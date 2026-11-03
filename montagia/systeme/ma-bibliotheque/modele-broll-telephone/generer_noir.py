"""reel-4 : passages B-roll (téléphone, avis, pub) posés au-dessus de final.mp4 (titres déjà incrustés)."""
import sys
from pathlib import Path
OUT = Path(sys.argv[1])
DUREE = float(sys.argv[2])

# téléphones : (début, fin, [écrans]) ; écran = (début, type, source, media_start, titre de la pastille)
TELS = [
    (11.55, 16.45, [(11.55, "img", "accueil.jpg", 0, "TA <i>journée</i>"),
                    (14.6, "img", "mini-plan.jpg", 0, "TA <i>semaine</i>")]),
    (39.9, 52.9, [(39.9, "img", "objectif.jpg", 0, "TES <i>objectifs</i>"),
                  (41.65, "img", "prospects.jpg", 0, "TES <i>prospects</i>"),
                  (43.25, "video", "tour-noir.mp4", 15.8, "TES <i>clientes</i>"),
                  (44.45, "video", "tour-noir.mp4", 19.8, "TES <i>abonnés</i>"),
                  (46.25, "video", "tour-noir.mp4", 21.3, "TON <i>contenu</i>"),
                  (47.15, "video", "tour-noir.mp4", 6.0, "TES <i>messages</i>"),
                  (49.6, "video", "tour-noir.mp4", 18.4, "TON <i>tarif juste</i>"),
                  (51.3, "video", "tour-noir.mp4", 24.0, "TES <i>idées</i>")]),
    (64.25, 67.7, [(64.25, "offre", "", 0, "OFFRE À <i>9 €</i>")]),
    (82.55, 89.95, [(82.55, "video", "tour-noir.mp4", 18.7, "TES <i>commissions</i>"),
                    (84.35, "video", "tour-noir.mp4", 24.0, "IDÉES DE <i>contenu</i>"),
                    (86.7, "video", "tour-noir.mp4", 33.0, "TES <i>couleurs</i>")]),
]
OUTILS = []
AVIS = [(16.45, 18.05, "avis-merci.jpg", -2), (70.25, 74.0, "avis-prix.jpg", 2)]
PROMO = (33.55, 39.75)
VOILES = [(11.4, 18.15), (39.75, 53.05), (64.1, 67.85), (70.1, 74.15), (82.4, 90.1)]
OR = "linear-gradient(115deg, #A9843F 0%, #E9D396 38%, #F6E7B8 50%, #C9A45C 68%, #9C773A 100%)"

css = f"""    @font-face {{ font-family: "MontB"; src: url("assets/fonts/Montserrat-Black.ttf"); }}
    @font-face {{ font-family: "MontX"; src: url("assets/fonts/Montserrat-ExtraBold.ttf"); }}
    @font-face {{ font-family: "Play"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf"); }}
    #root {{ position: absolute; inset: 0; }}
    i {{ font-family: "Play"; font-style: normal; text-transform: none; background: {OR}; -webkit-background-clip: text; background-clip: text; color: transparent; padding: 0 0.06em; }}
    .voile {{ position: absolute; inset: 0; opacity: 0; backdrop-filter: blur(26px); -webkit-backdrop-filter: blur(26px); background: radial-gradient(ellipse 70% 45% at 50% 42%, rgba(201, 164, 92, 0.16), rgba(7, 6, 5, 0) 70%), rgba(7, 6, 5, 0.72); }}
    .tel {{ visibility: hidden; position: absolute; left: 270px; top: 330px; width: 540px; height: 880px; border-radius: 68px; background: linear-gradient(160deg, #3A3128, #0E0C0A 40%, #2A231C); padding: 18px; box-shadow: 0 0 0 2px #5A4A36, 0 46px 90px rgba(0, 0, 0, 0.7), 0 0 70px rgba(201, 164, 92, 0.2); }}
    .ecran {{ position: relative; width: 504px; height: 844px; border-radius: 52px; overflow: hidden; background: #070605; }}
    .vue {{ visibility: hidden; position: absolute; left: 0; top: 0; width: 504px; height: 844px; padding-top: 50px; background: #070605; }}
    .vue video {{ width: 504px; height: 794px; object-fit: cover; object-position: top; display: block; }}
    .vue.photo {{ display: flex; align-items: center; justify-content: center; overflow: hidden; }}
    .vue.photo img {{ width: 504px; flex: none; display: block; }}
    .ilot {{ position: absolute; left: 182px; top: 14px; width: 140px; height: 36px; border-radius: 18px; background: #000; z-index: 5; }}
    .cadre {{ position: absolute; border: 6px solid #D9B866; border-radius: 20px; z-index: 4; }}
    .pastille {{ position: absolute; left: 0; right: 0; top: 196px; text-align: center; }}
    .pastille span {{ display: inline-block; padding: 14px 36px 12px; border-radius: 26px; background: #0A0908; border: 2px solid #5A4A36; font-family: "MontB"; font-size: 58px; line-height: 1.05; color: #F3EDE4; box-shadow: 0 14px 34px rgba(0, 0, 0, 0.5); }}
    .pastille i {{ font-size: 1.15em; }}
    .offre {{ text-align: center; padding: 120px 34px 0; }}
    .offre .k {{ font-family: "MontB"; font-size: 24px; letter-spacing: 0.18em; color: #BDB3A6; }}
    .offre .prix {{ margin-top: 30px; font-family: "Play"; font-size: 210px; line-height: 1; background: {OR}; -webkit-background-clip: text; background-clip: text; color: transparent; }}
    .offre .barre {{ margin-top: 6px; font-family: "MontB"; font-size: 54px; color: #6E6458; text-decoration: line-through; text-decoration-thickness: 5px; }}
    .offre .jusque {{ margin-top: 40px; font-family: "MontX"; font-size: 34px; color: #F3EDE4; }}
    .offre .jusque i {{ font-size: 1.25em; }}
    .offre .bouton {{ margin: 60px auto 0; width: 420px; padding: 26px 0; border-radius: 22px; background: {OR}; font-family: "MontB"; font-size: 28px; color: #0A0908; }}
    .avis {{ position: absolute; left: 70px; top: 520px; width: 940px; padding: 26px; border-radius: 40px; background: #141210; border: 2px solid #5A4A36; box-shadow: 0 40px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(201, 164, 92, 0.15); }}
    .avis img {{ width: 884px; display: block; border-radius: 24px; }}
    .avis .ttl {{ font-family: "MontB"; font-size: 46px; color: #F3EDE4; margin: 0 0 18px 8px; }}
    .avis .ttl i {{ font-size: 1.15em; }}
    #promo {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
"""
h, js, sons = [], [], []
for i, (a, b) in enumerate(VOILES):
    h.append(f'<div id="voile{i}" class="voile"></div>')
    js.append(f'    tl.fromTo("#voile{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {a});')
    js.append(f'    tl.to("#voile{i}", {{ opacity: 0, duration: 0.15 }}, {round(b - 0.15, 2)});')

def frac(x0, y0, x1, y1):   # case de l'image 720 de large -> écran 504 de large (+ 50 px d'encoche)
    k = 504 / 720
    return f"left: {x0 * k:.0f}px; top: {50 + y0 * k:.0f}px; width: {(x1 - x0) * k:.0f}px; height: {(y1 - y0) * k:.0f}px;"

for t, (a, b, ecrans) in enumerate(TELS):
    vues = []
    for e, (s, kind, src, ms, titre) in enumerate(ecrans):
        fin = ecrans[e + 1][0] if e + 1 < len(ecrans) else b
        d = round(fin - s, 2)
        vid = f"t{t}e{e}"
        if kind == "video":
            inner = f'<video id="{vid}-m" class="clip" src="assets/video/{src}" data-start="{s}" data-duration="{d}" data-media-start="{ms}" muted playsinline></video>'
        elif kind == "offre":
            inner = ('<div class="offre"><div class="k">🔥 OFFRE DE LANCEMENT</div><div class="prix">9 €</div><div class="barre">15 €</div>'
                     '<div class="jusque">jusqu’à <i>samedi</i> minuit</div><div class="bouton">Je veux mon tableau de bord →</div></div>')
        else:
            inner = f'<img src="assets/img/{src}" alt="" />'
        extra = ""
        if kind == "outils":
            x = CADRE_MSG
            extra += f'<div id="cadre-msg" class="cadre clip" data-start="{x[0]}" data-duration="{round(OUTILS[0][0] - x[0], 2)}" style="{frac(*x[1])}"></div>'
            for k, (s2, _, box) in enumerate(OUTILS):
                f2 = OUTILS[k + 1][0] if k + 1 < len(OUTILS) else b
                extra += f'<div id="cadre{k}" class="cadre clip" data-start="{s2 + 0.25}" data-duration="{round(f2 - s2 - 0.25, 2)}" style="{frac(*box)}"></div>'
        cl = "vue photo" if kind == "img" else "vue"
        vues.append(f'<div id="{vid}" class="{cl}">{inner}{extra}</div>')
        js.append(f'    tl.set("#{vid}", {{ autoAlpha: 1 }}, {s});')
        js.append(f'    tl.set("#{vid}", {{ autoAlpha: 0 }}, {fin});')
        if e:
            js.append(f'    tl.fromTo("#{vid}", {{ y: 844 }}, {{ y: 0, duration: 0.3, ease: "power3.out" }}, {s});')
            sons.append(("clic", s, 0.5))
        h.append(f'<div id="p{vid}" class="pastille clip" data-start="{s}" data-duration="{d if kind != "outils" else round(OUTILS[0][0] - s, 2)}"><span>{titre}</span></div>')
        js.append(f'    tl.fromTo("#p{vid} span", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }}, {s + 0.05:.2f});')
    js.append(f'    tl.set("#tel{t}", {{ autoAlpha: 1 }}, {a});')
    js.append(f'    tl.set("#tel{t}", {{ autoAlpha: 0 }}, {b});')
    h.append(f'<div id="tel{t}" class="tel"><div class="ecran">' + "".join(vues) + '<div class="ilot"></div></div></div>')
    js.append(f'    tl.fromTo("#tel{t}", {{ y: 1300, rotation: 6 }}, {{ y: 0, rotation: 0, duration: 0.5, ease: "expo.out" }}, {a});')
    js.append(f'    tl.to("#tel{t}", {{ y: 1300, rotation: -6, duration: 0.3, ease: "power3.in" }}, {round(b - 0.3, 2)});')
    sons.append(("whoosh", a, 0.45))
for k, (s2, titre, _) in enumerate(OUTILS):
    f2 = OUTILS[k + 1][0] if k + 1 < len(OUTILS) else TELS[1][1]
    h.append(f'<div id="po{k}" class="pastille clip" data-start="{s2}" data-duration="{round(f2 - s2, 2)}"><span>{titre}</span></div>')
    js.append(f'    tl.fromTo("#po{k} span", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }}, {s2 + 0.05:.2f});')
    sons.append(("clic", s2, 0.4))
js.append('    tl.fromTo(".cadre", { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: 0.25, ease: "expo.out", stagger: 0 }, 0);')
for i, (a, b, src, rot) in enumerate(AVIS):
    h.append(f'<div id="avis{i}" class="avis clip" data-start="{a}" data-duration="{round(b - a, 2)}"><div class="ttl">CE QU\'ELLES <i>en disent</i> 💛</div><img src="assets/img/{src}" alt="" /></div>')
    js.append(f'    tl.fromTo("#avis{i}", {{ scale: 0.4, opacity: 0, rotation: {rot * 4} }}, {{ scale: 1, opacity: 1, rotation: {rot}, duration: 0.45, ease: "back.out(1.7)" }}, {a});')
    js.append(f'    tl.to("#avis{i}", {{ scale: 0.6, opacity: 0, duration: 0.2, ease: "power2.in" }}, {round(b - 0.2, 2)});')
    sons.append(("pop", a, 0.5))
a, b = PROMO
h.append(f'<video id="promo" class="clip" src="assets/video/promo.mp4" data-start="{a}" data-duration="{round(b - a, 2)}" muted playsinline></video>')
js.append(f'    tl.fromTo("#promo", {{ clipPath: "circle(0% at 50% 55%)" }}, {{ clipPath: "circle(75% at 50% 55%)", duration: 0.45, ease: "power3.out" }}, {a});')
js.append(f'    tl.to("#promo", {{ clipPath: "circle(0% at 50% 55%)", duration: 0.3, ease: "power3.in" }}, {round(b - 0.3, 2)});')
sons += [("whoosh", a, 0.5), ("pop", a + 1.1, 0.3), ("pop", a + 1.55, 0.3), ("pop", a + 2.0, 0.3), ("ding", 64.4, 0.3)]
# fix : les cadres de « Mes outils » apparaissent quand leur clip commence (la ligne stagger ci-dessus remet seulement leur état)
js = [x for x in js if '".cadre"' not in x]
js.append('    tl.set(".cadre", { opacity: 1 }, 0);')

scene = f"""<template>
  <style>
{css}  </style>
  <div id="root" data-composition-id="broll" data-width="1080" data-height="1920">
    <div id="broll-scene" class="clip" data-start="0" data-duration="{DUREE}" data-layout-allow-overlap data-layout-allow-occlusion data-layout-allow-caption-zone>
{chr(10).join('      ' + x for x in h)}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["broll"] = tl;
  </script>
</template>
"""
(OUT / "compositions" / "broll.html").write_text(scene, encoding="utf-8")
audios = "".join(f'\n      <audio id="sfx-{i + 1}" class="clip" src="assets/sons/{f}.wav" data-start="{t:.2f}" data-track-index="{10 + i}" data-volume="{v}"></audio>' for i, (f, t, v) in enumerate(sorted(sons, key=lambda s: s[1])))
index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #base {{ position: absolute; inset: 0; width: 1080px; height: 1920px; z-index: 0; }}
      .scene {{ z-index: 2; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUREE}" data-width="1080" data-height="1920">
      <video id="base" class="clip" src="assets/video/base.mp4" data-start="0" data-duration="{DUREE}" data-track-index="0" muted playsinline></video>
      <audio id="voix" class="clip" src="assets/voix.wav" data-start="0" data-duration="{DUREE}" data-track-index="1" data-volume="1"></audio>
      <div id="broll" class="scene" data-composition-id="broll" data-composition-src="compositions/broll.html"
        data-start="0" data-duration="{DUREE}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <!-- bruitages des passages B-roll -->{audios}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
(OUT / "index.html").write_text(index, encoding="utf-8")
print("ok", DUREE)
