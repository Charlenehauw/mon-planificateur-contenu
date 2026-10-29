"""reel-4 : passages B-roll (téléphone, avis, pub) posés au-dessus de final.mp4 (titres déjà incrustés)."""
import sys
from pathlib import Path
OUT = Path(sys.argv[1])
DUREE = float(sys.argv[2])

# téléphones : (début, fin, [écrans]) ; écran = (début, type, source, media_start, titre de la pastille)
TELS = [
    (11.55, 16.45, [(11.55, "video", "semaine.mp4", 0.0, "MA SEMAINE <b>ORGANISÉE</b>"),
                    (14.6, "img", "page.jpg", 0, "MA PAGE <b>DE VENTE</b>")]),
    (39.9, 52.9, [(39.9, "video", "app-objectif.mp4", 0.0, "TES <b>OBJECTIFS</b>"),
                  (41.65, "video", "app-prospects.mp4", 0.0, "TES <b>PROSPECTS</b>"),
                  (43.25, "video", "clientes.mp4", 0.0, "TES <b>CLIENTES</b>"),
                  (44.45, "video", "app-reseaux.mp4", 0.0, "TES <b>ABONNÉS</b>"),
                  (46.25, "video", "calendrier.mp4", 4.0, "TON <b>CONTENU</b>"),
                  (47.15, "outils", "outils.png", 0, "GÉNÉRATEUR DE <b>MESSAGES</b>")]),
    (64.25, 67.7, [(64.25, "img", "page.jpg", 0, "OFFRE À <b>9 €</b>")]),
    (82.55, 89.95, [(82.55, "video", "app-commissions.mp4", 0.0, "SYSTÈME DE <b>COMMISSION</b>"),
                    (84.35, "video", "calendrier.mp4", 8.5, "IDÉES DE <b>CONTENU</b>"),
                    (86.7, "video", "tour.mp4", 30.0, "TES <b>COULEURS</b>")]),
]
# pastilles en plus sur l'écran « Mes outils » + cadres dorés sur la bonne case (repère de l'image 720 de large)
OUTILS = [(49.6, "GÉNÉRATEUR DE <b>TARIFS</b>", (28, 612, 350, 810)), (51.3, "GÉNÉRATEUR <b>D'IDÉES</b>", (28, 358, 350, 592))]
CADRE_MSG = (47.6, (370, 358, 693, 592))
AVIS = [(16.45, 18.05, "avis-merci.jpg", -2), (70.25, 74.0, "avis-prix.jpg", 2)]
PROMO = (33.55, 39.75)
VOILES = [(11.4, 18.15), (39.75, 53.05), (64.1, 67.85), (70.1, 74.15), (82.4, 90.1)]

css = """    @font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf"); }
    #root { position: absolute; inset: 0; }
    .voile { position: absolute; inset: 0; opacity: 0; backdrop-filter: blur(26px) saturate(1.05); -webkit-backdrop-filter: blur(26px); background: rgba(237, 232, 227, 0.42); }
    .tel { visibility: hidden; position: absolute; left: 270px; top: 330px; width: 540px; height: 880px; border-radius: 68px; background: #141210; padding: 18px; box-shadow: 0 46px 80px rgba(40, 28, 12, 0.35); }
    .ecran { position: relative; width: 504px; height: 844px; border-radius: 52px; overflow: hidden; background: #EDE8E3; }
    .vue { visibility: hidden; position: absolute; left: 0; top: 0; width: 504px; height: 844px; padding-top: 50px; background: #EDE8E3; }
    .vue video, .vue img { width: 504px; height: 794px; object-fit: cover; object-position: top; display: block; }
    .ilot { position: absolute; left: 182px; top: 14px; width: 140px; height: 36px; border-radius: 18px; background: #141210; z-index: 5; }
    .cadre { position: absolute; border: 6px solid #E8BD3C; border-radius: 20px; box-shadow: 0 0 22px rgba(232, 189, 60, 0.6); z-index: 4; }
    .pastille { position: absolute; left: 0; right: 0; top: 196px; text-align: center; }
    .pastille span { display: inline-block; padding: 14px 34px 10px; border-radius: 22px; background: #141210; font-family: "Anton"; font-size: 64px; line-height: 1; color: #FFFFFF; box-shadow: 0 14px 30px rgba(20, 18, 16, 0.25); }
    .pastille b { font-weight: 400; color: #E8BD3C; }
    .avis { position: absolute; left: 70px; top: 520px; width: 940px; padding: 26px; border-radius: 40px; background: #FFFFFF; box-shadow: 0 40px 80px rgba(40, 28, 12, 0.3); }
    .avis img { width: 888px; display: block; border-radius: 24px; }
    .avis .ttl { font-family: "Anton"; font-size: 46px; color: #141210; margin: 0 0 16px 8px; }
    .avis .ttl b { font-weight: 400; color: #E8BD3C; }
    #promo { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }
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
        else:
            inner = f'<img src="assets/img/{src}" alt="" />'
        extra = ""
        if kind == "outils":
            x = CADRE_MSG
            extra += f'<div id="cadre-msg" class="cadre clip" data-start="{x[0]}" data-duration="{round(OUTILS[0][0] - x[0], 2)}" style="{frac(*x[1])}"></div>'
            for k, (s2, _, box) in enumerate(OUTILS):
                f2 = OUTILS[k + 1][0] if k + 1 < len(OUTILS) else b
                extra += f'<div id="cadre{k}" class="cadre clip" data-start="{s2 + 0.25}" data-duration="{round(f2 - s2 - 0.25, 2)}" style="{frac(*box)}"></div>'
        vues.append(f'<div id="{vid}" class="vue">{inner}{extra}</div>')
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
    h.append(f'<div id="avis{i}" class="avis clip" data-start="{a}" data-duration="{round(b - a, 2)}"><div class="ttl">CE QU\'ELLES <b>EN DISENT</b> 💛</div><img src="assets/img/{src}" alt="" /></div>')
    js.append(f'    tl.fromTo("#avis{i}", {{ scale: 0.4, opacity: 0, rotation: {rot * 4} }}, {{ scale: 1, opacity: 1, rotation: {rot}, duration: 0.45, ease: "back.out(1.7)" }}, {a});')
    js.append(f'    tl.to("#avis{i}", {{ scale: 0.6, opacity: 0, duration: 0.2, ease: "power2.in" }}, {round(b - 0.2, 2)});')
    sons.append(("pop", a, 0.5))
a, b = PROMO
h.append(f'<video id="promo" class="clip" src="assets/video/promo.mp4" data-start="{a}" data-duration="{round(b - a, 2)}" muted playsinline></video>')
js.append(f'    tl.fromTo("#promo", {{ clipPath: "circle(0% at 50% 55%)" }}, {{ clipPath: "circle(75% at 50% 55%)", duration: 0.45, ease: "power3.out" }}, {a});')
js.append(f'    tl.to("#promo", {{ clipPath: "circle(0% at 50% 55%)", duration: 0.3, ease: "power3.in" }}, {round(b - 0.3, 2)});')
sons += [("whoosh", a, 0.5), ("pop", a + 0.75, 0.3), ("pop", a + 1.2, 0.3), ("pop", a + 1.65, 0.3), ("ding", 64.4, 0.3)]
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
