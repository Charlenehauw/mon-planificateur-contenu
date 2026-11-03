"""Vidéo « sans ma tête » : la voix de Charlène sur des visuels noir & or uniquement (téléphone, cartes, titres, sous-titres).
Usage : python3 gen_voix_noir.py <dossier video> <mots.json> <durée>"""
import json, re, sys
from pathlib import Path
OUT, MOTS, DUREE = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))["mots"], float(sys.argv[3])
norm = lambda m: re.sub(r"[^\w']", "", m.lower())
def T(v):
    if isinstance(v, (int, float)): return float(v)
    r = re.fullmatch(r"@([^#>+]+?)(?:#(\d+))?(>)?([+-][\d.]+)?", v)
    c, n = norm(r.group(1)), int(r.group(2) or 1)
    m = [w for w in MOTS if norm(w["w"]) == c][n - 1]
    return round((m["e"] if r.group(3) else m["s"]) + float(r.group(4) or 0), 2)
OR = "linear-gradient(115deg, #A9843F 0%, #E9D396 38%, #F6E7B8 50%, #C9A45C 68%, #9C773A 100%)"

# ---- le déroulé : titres plein écran, téléphone, cartes, extraits plein écran
TITRES = [  # (début, fin, [(texte, style, mot d'apparition)])
    (0.0, "@parler>+0.25", [("le prix de mon appli", "p", "@Je"), ("augmente", "c", "@vidéo"), ("SAMEDI", "m", "@maquillée")]),
    ("@l'idée-0.2", "@jours>+0.3", [("au départ, un", "p", "@l'idée"), ("plan d'action", "c", "@plan"), ("SUR 30 JOURS", "m", "@30")]),
    ("@mon-0.3", "@place>+0.3", [("mon", "p", "@mon"), ("cerveau", "c", "@cerveau"), ("D'ASSISTANTE", "m", "@d'assistante")]),
    ("@l'application#2-0.1", "@ça#5>+0.3", [("l'appli vaut", "p", "@l'application#2"), ("clairement", "c", "@clairement"), ("PLUS QUE ÇA", "m", "@plus")]),
    ("@toutes-0.2", "@incluses>+0.5", [("toutes les", "p", "@toutes"), ("mises à jour", "c", "@mises"), ("INCLUSES", "m", "@incluses")]),
    ("@profite-0.15", "@plus#3>+0.25", [("profite de l'offre", "p", "@profite"), ("avant samedi", "c", "@l'offre#2")]),
    ("@c'était#3-0.2", DUREE, [("BIZ’ EN", "m", "@c'était#3"), ("poche", "c", "@petit#4"), ("lien en bio ♥", "p", "@merci")]),
]
# écrans du téléphone : (début, fin, type, source, media_start, pastille)
ECRANS = [
    ("@parler>+0.25", "@samedi-0.1", "img", "accueil.jpg", 0, "BIZ’ EN <i>poche</i>"),
    ("@samedi-0.1", "@donc#2-0.1", "offre", "", 0, "OFFRE À <i>9 €</i>"),
    ("@donc#2-0.1", "@captures-0.1", "img", "mini-plan.jpg", 0, "TA <i>semaine</i>"),
    ("@captures-0.1", "@avis-0.1", "video", "tour-noir.mp4", 9.6, "TES <i>messages</i>"),
    ("@jours>+0.3", "@j'ai", "img", "objectif.jpg", 0, "TON <i>objectif</i>"),
    ("@j'ai", "@mon-0.3", "video", "tour-noir.mp4", 21.3, "TON <i>calendrier</i>"),
    ("@objectifs-0.15", "@le#3-0.1", "img", "objectif.jpg", 0, "TES <i>objectifs</i>"),
    ("@le#3-0.1", "@le#4-0.1", "img", "prospects.jpg", 0, "TES <i>prospects</i>"),
    ("@le#4-0.1", "@le#5-0.1", "video", "tour-noir.mp4", 15.8, "TES <i>clientes</i>"),
    ("@le#5-0.1", "@ton#3-0.05", "video", "tour-noir.mp4", 19.8, "TES <i>abonnés</i>"),
    ("@ton#3-0.05", "@tu-0.1", "video", "tour-noir.mp4", 21.3, "TON <i>contenu</i>"),
    ("@tu-0.1", "@tu#2-0.1", "video", "tour-noir.mp4", 6.0, "TES <i>messages</i>"),
    ("@tu#2-0.1", "@tu#3-0.1", "video", "tour-noir.mp4", 18.4, "TON <i>tarif juste</i>"),
    ("@tu#3-0.1", "@bref-0.1", "video", "tour-noir.mp4", 24.0, "TES <i>idées</i>"),
    ("@longue>+0.1", "@bénéficier-0.2", "video", "tour-noir.mp4", 0.0, "TON <i>tableau de bord</i>"),
    ("@bénéficier-0.2", "@l'application#2-0.1", "offre", "", 0, "OFFRE À <i>9 €</i>"),
    ("@incluses>+0.5", "@comme-0.1", "video", "tour-noir.mp4", 37.0, "TOUT EST <i>inclus</i>"),
    ("@comme-0.1", "@comme#2-0.1", "video", "tour-noir.mp4", 18.7, "TES <i>commissions</i>"),
    ("@comme#2-0.1", "@comme#3-0.1", "video", "tour-noir.mp4", 24.0, "IDÉES DE <i>contenu</i>"),
    ("@comme#3-0.1", "@profite-0.15", "video", "tour-noir.mp4", 33.0, "TES <i>couleurs</i>"),
]
PLEINS = [  # extraits plein écran : (début, fin, source, media_start)
    ("@une#3-0.2", "@objectifs-0.15", "promo.mp4", 0.0),
    ("@bref-0.1", "@longue>+0.1", "promo30.mp4", 4.9),
]
AVIS = [("@avis-0.1", "@l'idée-0.2", "avis-merci.jpg", -2), ("@les-0.1", "@toutes-0.2", "avis-prix.jpg", 2)]
EMOJIS = [("@augmenter", "graph"), ("@freebie", "cadeau"), ("@cerveau", "cerveau"), ("@rapide", "eclair"), ("@longue", "singe"),
          ("@t'activer", "reveil"), ("@clairement", "diamant"), ("@incluses", "coche"), ("@l'offre#2", "feu"), ("@merci", "coeur")]
FORTS = {norm(x) for x in ["l'application", "augmenter", "samedi", "produit", "avis", "plan", "30", "freebie", "guide", "cerveau", "complète",
         "business", "objectifs", "prospects", "clients", "abonnés", "contenu", "messages", "tarifs", "d'idées", "rapide", "10", "9€",
         "jamais", "clairement", "unanimes", "incluses", "commission", "couleurs", "profite", "plus"]}

css = f"""    @font-face {{ font-family: "MontB"; src: url("assets/fonts/Montserrat-Black.ttf"); }}
    @font-face {{ font-family: "MontX"; src: url("assets/fonts/Montserrat-ExtraBold.ttf"); }}
    @font-face {{ font-family: "Play"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf"); }}
    #root {{ position: absolute; inset: 0; }}
    i {{ font-family: "Play"; font-style: normal; text-transform: none; background: {OR}; -webkit-background-clip: text; background-clip: text; color: transparent; padding: 0 0.06em; }}
    .titre {{ position: absolute; left: 0; right: 0; top: 0; height: 1920px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding-bottom: 260px; text-align: center; }}
    .titre .p {{ font-family: "MontX"; font-size: 64px; color: #F3EDE4; }}
    .titre .c {{ font-family: "Play"; font-size: 190px; line-height: 1.15; background: {OR}; -webkit-background-clip: text; background-clip: text; color: transparent; padding: 0 0.08em; }}
    .titre .m {{ font-family: "MontB"; font-size: 120px; line-height: 1.05; color: #F3EDE4; }}
    .etoile {{ position: absolute; width: 70px; height: 70px; }}
    .etoile path {{ fill: #E2C275; }}
    .tel {{ visibility: hidden; position: absolute; left: 250px; top: 400px; width: 580px; height: 940px; border-radius: 72px; background: linear-gradient(160deg, #3A3128, #0E0C0A 40%, #2A231C); padding: 19px; box-shadow: 0 0 0 2px #5A4A36, 0 46px 90px rgba(0, 0, 0, 0.7), 0 0 80px rgba(201, 164, 92, 0.2); }}
    .ecran {{ position: relative; width: 542px; height: 902px; border-radius: 54px; overflow: hidden; background: #070605; }}
    .vue {{ visibility: hidden; position: absolute; left: 0; top: 0; width: 542px; height: 902px; padding-top: 52px; background: #070605; }}
    .vue video {{ width: 542px; height: 850px; object-fit: cover; object-position: top; display: block; }}
    .vue.photo {{ display: flex; align-items: center; justify-content: center; overflow: hidden; }}
    .vue.photo img {{ width: 542px; flex: none; display: block; }}
    .ilot {{ position: absolute; left: 196px; top: 15px; width: 150px; height: 38px; border-radius: 19px; background: #000; z-index: 5; }}
    .pastille {{ position: absolute; left: 0; right: 0; top: 230px; text-align: center; }}
    .pastille span {{ display: inline-block; padding: 14px 36px 12px; border-radius: 26px; background: #0A0908; border: 2px solid #5A4A36; font-family: "MontB"; font-size: 60px; line-height: 1.05; color: #F3EDE4; box-shadow: 0 14px 34px rgba(0, 0, 0, 0.5); }}
    .pastille i {{ font-size: 1.15em; }}
    .offre {{ text-align: center; padding: 130px 34px 0; }}
    .offre .k {{ font-family: "MontB"; font-size: 26px; letter-spacing: 0.18em; color: #BDB3A6; }}
    .offre .prix {{ margin-top: 30px; font-family: "Play"; font-size: 230px; line-height: 1; background: {OR}; -webkit-background-clip: text; background-clip: text; color: transparent; }}
    .offre .barre {{ margin-top: 6px; font-family: "MontB"; font-size: 58px; color: #6E6458; text-decoration: line-through; text-decoration-thickness: 5px; }}
    .offre .jusque {{ margin-top: 40px; font-family: "MontX"; font-size: 36px; color: #F3EDE4; }}
    .offre .jusque i {{ font-size: 1.25em; }}
    .offre .bouton {{ margin: 60px auto 0; width: 440px; padding: 26px 0; border-radius: 22px; background: {OR}; font-family: "MontB"; font-size: 28px; color: #0A0908; }}
    .plein {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    .avis {{ position: absolute; left: 70px; top: 560px; width: 940px; padding: 26px; border-radius: 40px; background: #141210; border: 2px solid #5A4A36; box-shadow: 0 40px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(201, 164, 92, 0.15); }}
    .avis img {{ width: 884px; display: block; border-radius: 24px; }}
    .avis .ttl {{ font-family: "MontB"; font-size: 46px; color: #F3EDE4; margin: 0 0 18px 8px; }}
    .avis .ttl i {{ font-size: 1.15em; }}
    .emo {{ position: absolute; left: 850px; top: 470px; width: 190px; }}
    .st {{ position: absolute; left: 60px; right: 60px; top: 1420px; text-align: center; font-family: "MontX"; font-size: 62px; line-height: 1.15; color: #FFFFFF; text-shadow: 0 4px 18px rgba(0, 0, 0, 0.9); }}
    .st b {{ font-weight: 400; color: #E2C275; }}
"""
h, js, sons = [], [], []
def apparait(sel, t, kind="pop"):
    js.append(f'    tl.fromTo("{sel}", {{ scale: 0.6, opacity: 0, y: 30 }}, {{ scale: 1, opacity: 1, y: 0, duration: 0.35, ease: "back.out(2)" }}, {t:.2f});')

zones = []   # moments sans sous-titres (titres plein écran)
for k, (a, b, lignes) in enumerate(TITRES):
    a, b = T(a), T(b); zones.append((a, b))
    spans = "".join(f'<div id="ti{k}-{j}" class="{st}">{tx}</div>' for j, (tx, st, _) in enumerate(lignes))
    etoiles = "".join(f'<svg id="et{k}-{j}" class="etoile" viewBox="-50 -50 100 100" style="left: {x}px; top: {y}px; width: {s}px; height: {s}px;"><path d="M0 -50 L9 -9 L50 0 L9 9 L0 50 L-9 9 L-50 0 L-9 -9 Z" /></svg>'
                      for j, (x, y, s) in enumerate([(130, 640, 70), (900, 560, 52), (880, 1060, 44)]))
    h.append(f'<div id="ti{k}" class="titre clip" data-start="{a}" data-duration="{round(b - a, 2)}">{spans}</div>{etoiles}')
    for j, (tx, st, t) in enumerate(lignes):
        tt = max(T(t), a + 0.05)
        if st == "c":
            js.append(f'    tl.fromTo("#ti{k}-{j}", {{ scale: 1.3, opacity: 0, filter: "blur(12px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, {tt:.2f});')
            sons.append(("impact", tt, 0.3))
            for e in range(3):
                js.append(f'    tl.fromTo("#et{k}-{e}", {{ scale: 0, rotation: -45, opacity: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, rotation: 0, opacity: 1, duration: 0.4, ease: "expo.out" }}, {tt + 0.1 + e * 0.12:.2f});')
                js.append(f'    tl.to("#et{k}-{e}", {{ opacity: 0, scale: 0.4, duration: 0.25 }}, {b - 0.3:.2f});')
        else:
            js.append(f'    tl.fromTo("#ti{k}-{j}", {{ opacity: 0, y: 24, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, {tt:.2f});')
    sons.append(("whoosh", a, 0.3))

# téléphone : visible quand au moins un écran est actif
EC = [(T(a), T(b), *r) for a, b, *r in ECRANS]
blocs = []
for a, b, *_ in sorted(EC):
    if blocs and a - blocs[-1][1] < 0.05: blocs[-1][1] = b
    else: blocs.append([a, b])
vues = []
for e, (a, b, kind, src, ms, pill) in enumerate(EC):
    d = round(b - a, 2)
    if kind == "video":
        inner = f'<video id="e{e}-m" class="clip" src="assets/video/{src}" data-start="{a}" data-duration="{d}" data-media-start="{ms}" muted playsinline></video>'
    elif kind == "offre":
        inner = ('<div class="offre"><div class="k">🔥 OFFRE DE LANCEMENT</div><div class="prix">9 €</div><div class="barre">15 €</div>'
                 '<div class="jusque">jusqu’à <i>samedi</i> minuit</div><div class="bouton">Je veux mon tableau de bord →</div></div>')
    else:
        inner = f'<img src="assets/img/{src}" alt="" />'
    vues.append(f'<div id="e{e}" class="vue{" photo" if kind == "img" else ""}">{inner}</div>')
    js.append(f'    tl.set("#e{e}", {{ autoAlpha: 1 }}, {a}); tl.set("#e{e}", {{ autoAlpha: 0 }}, {b});')
    js.append(f'    tl.fromTo("#e{e}", {{ y: 902 }}, {{ y: 0, duration: 0.3, ease: "power3.out" }}, {a});')
    h.append(f'<div id="pe{e}" class="pastille clip" data-start="{a}" data-duration="{d}"><span>{pill}</span></div>')
    js.append(f'    tl.fromTo("#pe{e} span", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }}, {a + 0.05:.2f});')
    sons.append(("clic", a, 0.45))
    if kind == "offre": sons.append(("ding", a + 0.2, 0.3))
h.append('<div id="tel" class="tel"><div class="ecran">' + "".join(vues) + '<div class="ilot"></div></div></div>')
for a, b in blocs:
    js.append(f'    tl.set("#tel", {{ autoAlpha: 1 }}, {a}); tl.set("#tel", {{ autoAlpha: 0 }}, {b});')
    js.append(f'    tl.fromTo("#tel", {{ y: 1200, rotation: 6 }}, {{ y: 0, rotation: 0, duration: 0.5, ease: "expo.out" }}, {a});')
    sons.append(("whoosh", a, 0.4))
for k, (a, b, src, ms) in enumerate(PLEINS):
    a, b = T(a), T(b)
    h.append(f'<video id="pl{k}" class="plein clip" src="assets/video/{src}" data-start="{a}" data-duration="{round(b - a, 2)}" data-media-start="{ms}" muted playsinline></video>')
    js.append(f'    tl.fromTo("#pl{k}", {{ clipPath: "circle(0% at 50% 50%)" }}, {{ clipPath: "circle(75% at 50% 50%)", duration: 0.45, ease: "power3.out" }}, {a});')
    sons.append(("whoosh", a, 0.45))
for k, (a, b, src, rot) in enumerate(AVIS):
    a, b = T(a), T(b)
    h.append(f'<div id="av{k}" class="avis clip" data-start="{a}" data-duration="{round(b - a, 2)}"><div class="ttl">CE QU\'ELLES <i>en disent</i> 💛</div><img src="assets/img/{src}" alt="" /></div>')
    js.append(f'    tl.fromTo("#av{k}", {{ scale: 0.4, opacity: 0, rotation: {rot * 4} }}, {{ scale: 1, opacity: 1, rotation: {rot}, duration: 0.45, ease: "back.out(1.7)" }}, {a});')
    sons.append(("pop", a, 0.5))
for k, (t, n) in enumerate(EMOJIS):
    t = T(t)
    h.append(f'<img id="em{k}" class="emo clip" src="assets/img/emo-{n}.png" alt="" data-start="{t}" data-duration="1.4" />')
    js.append(f'    tl.fromTo("#em{k}", {{ scale: 0, rotation: -25 }}, {{ scale: 1, rotation: 8, duration: 0.4, ease: "back.out(2.2)" }}, {t:.2f});')
    js.append(f'    tl.to("#em{k}", {{ rotation: -6, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {t + 0.4:.2f});')
    js.append(f'    tl.to("#em{k}", {{ scale: 0, opacity: 0, duration: 0.2 }}, {t + 1.2:.2f});')
    sons.append(("pop", t, 0.45))

# sous-titres : 3 mots max, coupés aux pauses et à la ponctuation, jamais pendant un titre plein écran
libres = [m for m in MOTS if not any(a - 0.01 <= m["s"] < b for a, b in zones)]
caps, g = [], []
for i, m in enumerate(libres):
    g.append(m); nx = libres[i + 1] if i + 1 < len(libres) else None
    if len(g) >= 3 or nx is None or nx["s"] - m["e"] > 0.35 or m["w"][-1:] in ".,!?" or len(" ".join(x["w"] for x in g + [nx])) > 18:
        caps.append([g[0]["s"], g[-1]["e"] + 0.25, g]); g = []
for i, c in enumerate(caps):
    if i + 1 < len(caps): c[1] = min(c[1], caps[i + 1][0])
    for a, b in zones:
        if c[0] < a < c[1]: c[1] = a
for i, (a, b, g) in enumerate(caps):
    txt = " ".join(f"<b>{w['w'].strip(',.')}</b>" if norm(w["w"]) in FORTS else w["w"].strip(",.") for w in g)
    h.append(f'<div id="st{i}" class="st clip" data-start="{a:.2f}" data-duration="{max(b - a, 0.1):.2f}">{txt}</div>')
    js.append(f'    tl.fromTo("#st{i}", {{ scale: 0.85, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.12, ease: "back.out(2)" }}, {a:.2f});')

scene = f"""<template>
  <style>
{css}  </style>
  <div id="root" data-composition-id="voix" data-width="1080" data-height="1920">
    <div id="voix-scene" class="clip" data-start="0" data-duration="{DUREE}" data-layout-allow-overlap data-layout-allow-occlusion data-layout-allow-caption-zone>
{chr(10).join('      ' + x for x in h)}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["voix"] = tl;
  </script>
</template>
"""
(OUT / "compositions" / "voix.html").write_text(scene, encoding="utf-8")
audios = "".join(f'\n      <audio id="sfx-{i + 1}" class="clip" src="assets/sons/{f}.wav" data-start="{t:.2f}" data-track-index="{10 + i}" data-volume="{v}"></audio>' for i, (f, t, v) in enumerate(sorted(sons, key=lambda s: s[1])))
index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #070605; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #fond {{ position: absolute; inset: 0; z-index: 0;
        background: radial-gradient(ellipse 65% 40% at 50% 44%, rgba(201, 164, 92, 0.16) 0%, rgba(201, 164, 92, 0) 70%), linear-gradient(180deg, #0D0B09 0%, #070605 55%, #0B0907 100%); }}
      .scene {{ z-index: 2; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUREE}" data-width="1080" data-height="1920">
      <div id="fond" class="clip" data-start="0" data-duration="{DUREE}" data-track-index="0"></div>
      <audio id="voix-audio" class="clip" src="assets/voix.wav" data-start="0" data-duration="{DUREE}" data-track-index="1" data-volume="1"></audio>
      <div id="voix" class="scene" data-composition-id="voix" data-composition-src="compositions/voix.html"
        data-start="0" data-duration="{DUREE}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>{audios}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
(OUT / "index.html").write_text(index, encoding="utf-8")
print("ok", len(caps), "sous-titres")
