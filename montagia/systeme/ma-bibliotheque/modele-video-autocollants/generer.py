"""Génère la vidéo « explainer autocollants » de Biz' en poche (sans voix) : scènes HyperFrames + index."""
import json, sys
from pathlib import Path

OUT = Path(sys.argv[1])
MOT = 0.30          # écart entre deux mots
TENUE = 0.75        # tenue d'un groupe après son dernier mot
ROTS = [-3, 2, -1.5, 3, -2, 1.5]

MASCOTTE = """
      <svg id="{p}-masc" class="masc" viewBox="0 0 210 300">
        <ellipse cx="105" cy="292" rx="70" ry="8" fill="rgba(60,40,20,0.18)" />
        <g id="{p}-corps">
          <rect x="10" y="6" width="190" height="276" rx="40" fill="#141210" />
          <rect id="{p}-ecran" x="22" y="18" width="166" height="252" rx="30" fill="#E8BD3C" />
          <rect x="80" y="28" width="50" height="12" rx="6" fill="#141210" />
          <g id="{p}-yeux">
            <ellipse cx="75" cy="120" rx="22" ry="26" fill="#FFFFFF" /><circle cx="80" cy="124" r="11" fill="#141210" /><circle cx="84" cy="119" r="4" fill="#FFFFFF" />
            <ellipse cx="135" cy="120" rx="22" ry="26" fill="#FFFFFF" /><circle cx="140" cy="124" r="11" fill="#141210" /><circle cx="144" cy="119" r="4" fill="#FFFFFF" />
          </g>
          <circle cx="52" cy="168" r="11" fill="#F29C9C" opacity="0.7" /><circle cx="158" cy="168" r="11" fill="#F29C9C" opacity="0.7" />
          <path d="M80 172 Q105 198 130 172" fill="none" stroke="#141210" stroke-width="8" stroke-linecap="round" />
        </g>
      </svg>"""

CSS = """    @font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf"); }
    #root { position: absolute; inset: 0; }
    .tag { position: absolute; left: 0; right: 0; top: 190px; text-align: center; }
    .tag span { display: inline-block; background: #FBF6EA; padding: 18px 40px; font-family: "Lato"; font-weight: 900; font-size: 42px;
      letter-spacing: 0.06em; color: #141210; box-shadow: 0 6px 14px rgba(60, 40, 20, 0.18);
      clip-path: polygon(0 0, 100% 0, 98% 12%, 100% 25%, 98% 38%, 100% 50%, 98% 62%, 100% 75%, 98% 88%, 100% 100%, 0 100%, 2% 88%, 0 75%, 2% 62%, 0 50%, 2% 38%, 0 25%, 2% 12%); }
    .masc { position: absolute; left: 435px; top: 920px; width: 210px; height: 300px; }
    .grp { position: absolute; left: 60px; right: 60px; top: 1230px; text-align: center; }
    .mot { display: inline-block; margin: 6px 6px; padding: 4px 18px 8px; background: #141210; color: #FBF6EA; font-family: "Anton"; font-size: 66px;
      line-height: 1.1; box-shadow: 0 4px 10px rgba(20, 14, 6, 0.25); }
    .mot.or { background: #E8BD3C; color: #141210; }
    .st { position: absolute; }
    .carte { position: absolute; border: 14px solid #FFFFFF; border-radius: 28px; box-shadow: 0 18px 36px rgba(60, 40, 20, 0.25); background: #FFFFFF; }
    .carte img { display: block; width: 100%; border-radius: 14px; }
"""

def groupes_html(p, groupes, t0):
    """Sous-titres « lettres découpées » : chaque mot sur son étiquette, un groupe remplace le précédent."""
    html, tw, t = "", "", t0
    debuts = []
    for g in groupes:
        debuts.append(t)
        t += len(g) * MOT + TENUE
    for gi, g in enumerate(groupes):
        html += f'\n      <div id="{p}-g{gi}" class="grp">'
        for wi, w in enumerate(g):
            fort = w.startswith("*")
            txt = w.strip("*")
            html += f'<span id="{p}-g{gi}w{wi}" class="mot{" or" if fort else ""}">{txt}</span>'
            r = ROTS[(gi * 3 + wi) % len(ROTS)]
            tw += f'    tl.fromTo("#{p}-g{gi}w{wi}", {{ opacity: 0, scale: 0.6, rotation: {r * 3} }}, {{ opacity: 1, scale: 1, rotation: {r}, duration: 0.28, ease: "back.out(2)" }}, {debuts[gi] + wi * MOT:.2f});\n'
        html += "</div>"
        if gi + 1 < len(groupes):
            tw += f'    tl.to("#{p}-g{gi}", {{ opacity: 0, y: -16, duration: 0.14, ease: "power2.in" }}, {debuts[gi + 1] - 0.14:.2f});\n'
    return html, tw, debuts, t

def scene(cid, p, tag, groupes, visuels, extra_js="", fin_tenue=0.3):
    html_g, tw_g, debuts, t_fin = groupes_html(p, groupes, 0.55)
    dur = round(t_fin + fin_tenue, 2)
    vis_html, vis_js = "", ""
    for i, v in enumerate(visuels):
        vid = f"{p}-v{i}"
        g = v.get("g", 0)
        t = debuts[g] + v.get("dt", 0.0)
        r = v.get("rot", 0)
        if v["kind"] == "st":
            vis_html += f'\n      <img id="{vid}" class="st" src="assets/img/st-{v["src"]}.png" alt="" style="left: {v["x"] - v.get("w", 190) // 2}px; top: {v["y"]}px; width: {v.get("w", 190)}px;" />'
        elif v["kind"] == "carte":
            vis_html += f'\n      <div id="{vid}" class="carte" style="left: {540 - v.get("w", 600) // 2 + v.get("dx", 0)}px; top: {v["y"]}px; width: {v.get("w", 600)}px;"><img src="assets/img/ecran-{v["src"]}.png" alt="" /></div>'
        else:
            vis_html += "\n      " + v["html"].format(id=vid)
        if v.get("vol"):   # s'envole depuis la mascotte
            vis_js += f'    tl.fromTo("#{vid}", {{ x: {540 - v["x"]}, y: {1000 - v["y"]}, scale: 0.2, rotation: {r - 40}, opacity: 0 }}, {{ x: 0, y: 0, scale: 1, rotation: {r}, opacity: 1, duration: 0.6, ease: "back.out(1.4)" }}, {t:.2f});\n'
        else:
            vis_js += f'    tl.fromTo("#{vid}", {{ scale: 0.4, rotation: {r - 18}, opacity: 0 }}, {{ scale: 1, rotation: {r}, opacity: 1, duration: 0.45, ease: "back.out(1.7)" }}, {t:.2f});\n'
        if "sort_g" in v:  # part quand le visuel suivant arrive
            ts = debuts[v["sort_g"]] + v.get("sort_dt", 0.0)
            vis_js += f'    tl.to("#{vid}", {{ x: -1150, rotation: {r - 25}, duration: 0.4, ease: "power3.in" }}, {ts - 0.1:.2f});\n'
    masc = MASCOTTE.format(p=p)
    js = f"""    const tl = gsap.timeline({{ paused: true }});
    // ruban du chapitre
    tl.fromTo("#{p}-tag span", {{ opacity: 0, scaleX: 0.3, rotation: -8 }}, {{ opacity: 1, scaleX: 1, rotation: -2, duration: 0.4, ease: "back.out(1.6)" }}, 0.1);
    // la mascotte sautille à l'arrivée puis cligne des yeux
    tl.fromTo("#{p}-corps", {{ y: 0 }}, {{ y: -34, duration: 0.18, ease: "power2.out", yoyo: true, repeat: 1 }}, 0.2);
    tl.fromTo("#{p}-yeux", {{ scaleY: 1 }}, {{ scaleY: 0.1, transformOrigin: "50% 50%", duration: 0.08, yoyo: true, repeat: 1 }}, {min(1.6, dur - 0.4):.2f});
{vis_js}{tw_g}{extra_js}    window.__timelines["{cid}"] = tl;
"""
    doc = f"""<template>
  <style>
{CSS}  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{p}-scene" class="clip" data-start="0" data-duration="{dur}" data-layout-allow-overlap data-layout-allow-occlusion>
      <div id="{p}-tag" class="tag"><span>{tag}</span></div>{vis_html}{masc}{html_g}
    </div>
  </div>
  <script>
{js}  </script>
</template>
"""
    (OUT / "compositions" / f"{cid}.html").write_text(doc, encoding="utf-8")
    return dur, debuts, visuels

SCENES = []
def ajoute(*a, **k):
    SCENES.append((a[0],) + scene(*a, **k))

L, R = 190, 890
ajoute("accroche", "acc", "BIZ’ EN POCHE",
       [["Ton", "*business*"], ["tient", "enfin"], ["dans", "ta", "*poche.*"]],
       [dict(kind="carte", src="priorite", y=400, w=620, rot=-3, g=0),
        dict(kind="st", src="etincelles", x=R, y=330, w=170, rot=10, g=1),
        dict(kind="st", src="tel", x=L, y=700, w=170, rot=-10, g=2)])
ajoute("coach", "coa", "TON COACH DE POCHE",
       [["Une", "*app*"], ["qui", "organise"], ["tout", "ton", "business"], ["à", "ta", "*place.*"]],
       [dict(kind="carte", src="prospects", y=360, w=560, rot=3, g=0),
        dict(kind="st", src="idee", x=L, y=330, w=170, rot=-12, g=1),
        dict(kind="st", src="fusee", x=R, y=680, w=170, rot=10, g=3)])
ajoute("endroit", "end", "TOUT AU MÊME ENDROIT",
       [["*Prospects,*"], ["*ventes,*"], ["*réseaux,*"], ["*motivation…*"], ["tout", "est", "*là.*"]],
       [dict(kind="st", src="cible", x=260, y=360, w=200, rot=-10, g=0, vol=True),
        dict(kind="st", src="sac", x=820, y=360, w=200, rot=8, g=1, vol=True),
        dict(kind="st", src="hausse", x=260, y=640, w=200, rot=6, g=2, vol=True),
        dict(kind="st", src="coeur", x=820, y=640, w=200, rot=-8, g=3, vol=True),
        dict(kind="st", src="etincelles", x=540, y=470, w=180, rot=0, g=4)])
roles = [("priorite", "cible", ["Un", "qui", "te", "donne"], ["ta", "*priorité*", "du", "jour."]),
         ("prospects", "telephone", ["Un", "qui", "suit"], ["tes", "*prospects.*"]),
         ("ventes", "billets", ["Un", "qui", "compte"], ["tes", "*ventes.*"]),
         ("reseaux", "hausse", ["Un", "qui", "suit"], ["tes", "*abonnés.*"]),
         ("motivation", "coeur", ["Et", "un", "qui", "te", "rappelle"], ["*pourquoi*", "tu", "fais", "tout", "ça."])]
grp, vis = [], []
for i, (ecr, st, a, b) in enumerate(roles):
    gi = len(grp)
    grp += [a, b]
    rot = -3 if i % 2 == 0 else 3
    c = dict(kind="carte", src=ecr, y=330, w=560 if ecr != "priorite" else 640, rot=rot, g=gi)
    s = dict(kind="st", src=st, x=R if i % 2 == 0 else L, y=730, w=170, rot=-rot * 3, g=gi + 1)
    if i + 1 < len(roles):
        c["sort_g"] = gi + 2; s["sort_g"] = gi + 2
    vis += [c, s]
ajoute("roles", "rol", "UN ESPACE, UN RÔLE", grp, vis)
ajoute("quoi", "quo", "QUOI · QUAND · COMBIEN",
       [["Tu", "sais", "*quoi*", "faire,"], ["*quand*", "le", "faire,"], ["et", "*combien*", "tu", "gagnes."]],
       [dict(kind="st", src="coche", x=220, y=480, w=230, rot=-8, g=0, dt=0.6),
        dict(kind="st", src="horloge", x=540, y=430, w=230, rot=4, g=1, dt=0.3),
        dict(kind="st", src="sac", x=860, y=480, w=230, rot=10, g=2, dt=0.6)])
couleurs = "".join(f'''    tl.to("#fou-ecran", {{ attr: {{ fill: "{c}" }}, duration: 0.25, ease: "power2.inOut" }}, {t});\n''' for c, t in
                   (("#F2509A", 1.95), ("#3B82F6", 2.65), ("#9B5DE5", 3.35)))
ajoute("fou", "fou", "LE PLUS FOU",
       [["Elle", "prend"], ["*tes*", "*couleurs.*"], ["En", "un", "*clic.*"]],
       [dict(kind="carte", src="c-jaune", y=380, w=520, rot=-4, g=0),
        dict(kind="carte", src="c-rose", y=380, w=520, rot=3, dx=20, g=1, dt=0.25),
        dict(kind="carte", src="c-bleu", y=380, w=520, rot=-2, dx=-10, g=1, dt=0.95),
        dict(kind="carte", src="c-violet", y=380, w=520, rot=4, dx=15, g=2, dt=0.4),
        dict(kind="st", src="palette", x=R, y=300, w=180, rot=12, g=1)],
       extra_js="    // l'écran de la mascotte change de couleur comme l'appli\n" + couleurs)
MARQUE = '''<div id="{id}" class="marque" style="position: absolute; left: 190px; top: 340px; width: 700px; padding: 40px 30px 36px; background: #FFFFFF; border-radius: 34px; box-shadow: 0 18px 36px rgba(60,40,20,0.25); text-align: center;"><div style="font-family: Anton; font-size: 120px; line-height: 1; color: #141210;">BIZ’ EN</div><div style="font-family: Anton; font-size: 170px; line-height: 1; color: #E8BD3C;">POCHE</div><div style="margin-top: 10px; font-family: Lato; font-style: italic; font-size: 48px; color: #4a433c;">by Charlène</div></div>'''
SUIVRE = '''<div id="{id}" style="position: absolute; left: 140px; top: 780px; width: 800px; height: 110px; background: #FFFFFF; border-radius: 26px; box-shadow: 0 12px 28px rgba(60,40,20,0.2);"><div style="position: absolute; left: 34px; top: 32px; font-family: Lato; font-weight: 900; font-size: 38px; color: #141210;">@hwl.assistantevirtuelle</div><div id="bout-noir" style="position: absolute; right: 22px; top: 22px; width: 220px; height: 66px; border-radius: 16px; background: #141210; color: #FFFFFF; font-family: Lato; font-weight: 900; font-size: 30px; line-height: 66px; text-align: center;">S’abonner</div><div id="bout-or" style="position: absolute; right: 22px; top: 22px; width: 220px; height: 66px; border-radius: 16px; background: #E8BD3C; color: #141210; font-family: Lato; font-weight: 900; font-size: 30px; line-height: 66px; text-align: center; opacity: 0;">Abonnée ✓</div></div>'''
ajoute("cta", "cta", "LIEN EN BIO",
       [["*Biz’*", "*en*", "*poche*"], ["by", "Charlène"], ["le", "lien", "est"], ["dans", "ma", "*bio*", "♥"]],
       [dict(kind="html", html=MARQUE, rot=-2, g=0),
        dict(kind="html", html=SUIVRE, rot=1, g=2, dt=0.2)],
       extra_js='    // le bouton passe de « S’abonner » à « Abonnée »\n    tl.to("#bout-or", { opacity: 1, duration: 0.15 }, CLIC);\n    tl.fromTo("#bout-or", { scale: 0.85 }, { scale: 1, duration: 0.3, ease: "back.out(2)" }, CLIC);\n',
       fin_tenue=1.6)
# l'instant du clic dépend des débuts calculés
cta = OUT / "compositions" / "cta.html"
d, debuts = SCENES[-1][1], SCENES[-1][2]
clic = round(debuts[3] + 0.3, 2)
cta.write_text(cta.read_text(encoding="utf-8").replace("CLIC", str(clic)), encoding="utf-8")

# ---------- index : fond papier, scènes, feuilles de papier aux transitions, bruitages
debut, hosts, feuilles, sons = 0.0, "", "", []
for k, (cid, dur, debs, vis) in enumerate(SCENES):
    hosts += f'''
      <div id="{cid}" class="scene" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{debut:g}" data-duration="{dur:g}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'''
    for v in vis:
        if v["kind"] in ("st", "carte", "html"):
            sons.append(("pop", debut + debs[v.get("g", 0)] + v.get("dt", 0) + 0.05, 0.3))
    if cid == "cta":
        sons.append(("clic", debut + clic, 0.7)); sons.append(("impact", debut + debs[0] + 0.05, 0.4))
    if k > 0:
        feuilles += f'''
      <div id="feuille-{k}" class="clip" data-start="{debut - 0.3:.2f}" data-duration="0.6" data-track-index="2" style="position: absolute; inset: 0; z-index: 5;" data-layout-allow-overlap data-layout-allow-occlusion><div id="feuille-{k}-papier" class="feuille"></div></div>'''
        sons.append(("whoosh", debut - 0.32, 0.4))
    debut = round(debut + dur, 2)
total = debut
anims = "".join(f'''      tl.fromTo("#feuille-{k}-papier", {{ x: 1250, rotation: -4 }}, {{ x: -1450, rotation: 3, duration: 0.6, ease: "power2.inOut" }}, {float(SCENES[k][0] and 0) + sum(s[1] for s in SCENES[:k]) - 0.3:.2f});\n''' for k in range(1, len(SCENES)))
audios = "".join(f'\n      <audio id="sfx-{i + 1}" class="clip" src="assets/sons/{f}.wav" data-start="{t:.2f}" data-track-index="{10 + i}" data-volume="{v}"></audio>' for i, (f, t, v) in enumerate(sorted(sons, key=lambda s: s[1])))
index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #efe9e0; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #fond {{ position: absolute; inset: 0; z-index: 0; }}
      #fond img {{ width: 100%; height: 100%; display: block; }}
      .scene {{ z-index: 2; }}
      .feuille {{ position: absolute; left: -110px; top: -200px; width: 1300px; height: 2320px; background: #f6f1e8;
        box-shadow: -30px 0 60px rgba(60, 40, 20, 0.25), 30px 0 60px rgba(60, 40, 20, 0.25); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
      <div id="fond" class="clip" data-start="0" data-duration="{total}" data-track-index="0"><img src="assets/img/papier.jpg" alt="" /></div>
{hosts}
{feuilles}

      <!-- bruitages (Montag'IA), chacun sur une action visible -->{audios}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // une feuille de papier balaie l'écran à chaque changement de chapitre
{anims}      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(OUT / "index.html").write_text(index, encoding="utf-8")
print("durée", total, [(s[0], s[1]) for s in SCENES])
