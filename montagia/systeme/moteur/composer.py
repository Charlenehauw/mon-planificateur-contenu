#!/usr/bin/env python3
"""Étape 5. Transforme la fiche de montage en projet HyperFrames prêt à rendre.

La fiche (fiche.json) est le SEUL fichier que Claude écrit. Ce script :
  1. résout les temps (« @caméra » = début du mot caméra, « @caméra> » = sa fin, « @caméra#2 » = 2e occurrence) ;
  2. applique les règles de la maison (rythme, zones interdites, effets obligatoires) ;
  3. calcule les sous-titres depuis les mots ;
  4. écrit projet/montage/ (index.html + moteur d'effets + polices + médias).
Format YouTube (projet créé avec --youtube) : repère 1920x1080, sous-titres posés au rendu par ffmpeg
(sous-titres.json + sous-titres.srt pour YouTube), et une page fenetres.html qui ne contient que les
passages avec effets, mis bout à bout : seuls ces passages passent par le rendu image par image.

Usage : python moteur/composer.py <dossier_projet>
"""
import copy
import json
import math
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import RACINE, lire_json, ecrire_json, format_projet, dimensions_format

GROS = {"sur_mesure", "chapitre", "carte_mot", "carte_titre", "broll", "cadre_explication", "documentaire", "objet_3d", "telephones", "vitre", "texte_derriere", "venn", "feuille_route", "comparaison", "pixel_art"}
PLEIN_ECRAN = {"carte_mot", "carte_titre", "documentaire", "cadre_explication", "venn", "feuille_route"}
BESOIN_DETOURAGE = {"texte_derriere", "documentaire"}
SONS = {  # son, décalage, volume
    "carte_mot": [("impact", 0.0, 0.7)], "carte_titre": [("montee", -0.9, 0.5), ("impact", 0.0, 0.6)],
    "zoom": [("whoosh", -0.05, 0.25)], "broll": [("whoosh", -0.15, 0.45)], "etiquettes": [("pop", 0.0, 0.5)],
    "compteur": [("montee", 0.0, 0.35)], "cadre_explication": [("whoosh", 0.0, 0.5)],
    "objet_3d": [("pop", 0.0, 0.6)], "vitre": [("vitre", 0.0, 1.0), ("impact", 0.0, 0.7)],
    "telephones": [("whoosh", 0.0, 0.5)], "texte_derriere": [("whoosh", 0.0, 0.35)],
    "documentaire": [("impact", 0.0, 0.6)], "cta_commentaire": [("clavier", 0.45, 0.5), ("ding", 1.2, 0.4)],
    "image": [("pop", 0.0, 0.55)], "icones": [("pop", 0.0, 0.5)], "illustration": [("whoosh", -0.05, 0.35), ("pop", 0.3, 0.4)], "sur_mesure": [("whoosh", 0.0, 0.35)], "comparaison": [("whoosh", 0.0, 0.4), ("impact", 0.45, 0.4)],
    "venn": [("whoosh", 0.0, 0.45)], "feuille_route": [("whoosh", 0.0, 0.45)], "pixel_art": [("pop", 0.0, 0.4)], "fenetre_app": [("clic", 0.0, 0.5)], "flash": [("whoosh", -0.1, 0.4)],
}
ZONE_TEXTE_MAX_Y = 1536
ZONE_SOUS_TITRES_YOUTUBE = 880     # paysage : sous cette ligne, la bande des sous-titres
ICONES = RACINE / "assets" / "icones"


def icone_svg(nom):
    f = ICONES / f"{nom}.svg"
    if not f.exists():
        tags = json.loads((ICONES / "tags.json").read_text(encoding="utf-8"))
        proches = [k for k, v in tags.items() if nom in k or nom in v][:8]
        raise ValueError(f"icône « {nom} » inconnue. Proches : {', '.join(proches) or 'aucune'}")
    svg = f.read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    return re.sub(r'\s(width|height)="24"', "", svg).replace('class="lucide', 'class="ic lucide').strip()


def sans_accents(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def nettoyer(t):
    return re.sub(r"[^a-z0-9]", "", sans_accents(t))


class Temps:
    def __init__(self, mots):
        self.mots = mots

    def __call__(self, v, champ, effet):
        if isinstance(v, (int, float)):
            return float(v)
        m = re.fullmatch(r"@(.+?)(#(\d+))?(>)?([+-]\d+(\.\d+)?)?", str(v).strip())
        if not m:
            raise ValueError(f"{effet}: temps illisible pour « {champ} » : {v}")
        cible, n, fin, dec = nettoyer(m.group(1)), int(m.group(3) or 1), bool(m.group(4)), float(m.group(5) or 0)
        for mode in ("exact", "debut"):
            vus = 0
            for x in self.mots:
                n_x = nettoyer(x["w"])
                if n_x == cible or (mode == "debut" and n_x.startswith(cible) and len(cible) >= 5):
                    vus += 1
                    if vus == n:
                        return round((x["e"] if fin else x["s"]) + dec, 3)
        raise ValueError(f"{effet}: le mot « {m.group(1)} » (occurrence {n}) n'existe pas dans texte-final.txt")


def blocs_sous_titres(mots, style, mots_cles, masques, max_car=None):
    T = style["sous_titres"]
    cles = {nettoyer(k) for k in mots_cles}
    blocs, cur = [], []

    def fermer():
        if not cur:
            return
        html = " ".join((f"<em>{w['w']}</em>" if nettoyer(w["w"]) in cles else w["w"]) for w in cur)
        s, e = cur[0]["s"], cur[-1]["e"]
        blocs.append({"html": html, "s": round(s, 3), "e": round(e, 3),
                      "mots": [{"w": w["w"], "s": round(w["s"], 3), "cle": nettoyer(w["w"]) in cles} for w in cur]})
        cur.clear()

    for i, w in enumerate(mots):
        if cur and (w["s"] - cur[-1]["e"] > 0.5 or len(cur) >= T["mots_par_bloc"]
                    or (max_car and len(" ".join(x["w"] for x in cur)) + 1 + len(w["w"]) > max_car)
                    or (max_car and len(cur) >= 3 and w["w"][:1].isupper() and not w["w"].isupper())):
            fermer()   # YouTube : Whisper ne met pas toujours de ponctuation, une majuscule ouvre souvent une phrase
        cur.append(w)
        if re.search(r"[.!?,;:]$", w["w"]):
            fermer()
    fermer()
    for i in range(len(blocs) - 1):  # chaque bloc reste affiché jusqu'au suivant (sans trou visible)
        if blocs[i + 1]["s"] - blocs[i]["e"] < 0.35:
            blocs[i]["e"] = blocs[i + 1]["s"]
        else:
            blocs[i]["e"] = round(blocs[i]["e"] + 0.15, 3)
    garde = [b for b in blocs if not any(b["s"] < f - 0.05 and b["e"] > d + 0.05 for d, f in masques)]
    return garde


TEMPS_EFFET = ("debut", "fin", "lancer", "au")


def nombre(v):
    return type(v) in (int, float)


def decaler(e, d):
    """Copie d'un effet dont tous les temps sont décalés de d secondes (page des fenêtres YouTube)."""
    e = copy.deepcopy(e)
    for k in TEMPS_EFFET:
        if nombre(e.get(k)):
            e[k] = round(e[k] + d, 3)
    if isinstance(e.get("reperes"), dict):
        e["reperes"] = {k: (round(v + d, 3) if nombre(v) else v) for k, v in e["reperes"].items()}
    for cle in ("items", "etapes", "cercles"):
        for it in e.get(cle) or []:
            if isinstance(it, dict):
                for k in ("debut", "barre"):
                    if nombre(it.get(k)):
                        it[k] = round(it[k] + d, 3)
    return e


def fenetres_effets(effets, duree, fps=30):
    """Passages à rendre image par image : chaque effet avec une marge, regroupés s'ils sont proches,
    calés sur les images. Le reste de la vidéo est copié tel quel par ffmpeg."""
    spans = sorted((max(0.0, e["debut"] - 0.25), min(duree, e["fin"] + 0.35)) for e in effets if e["type"] != "recadrage")
    groupes = []
    for a, b in spans:
        if groupes and a - groupes[-1][1] < 1.5:
            groupes[-1][1] = max(groupes[-1][1], b)
        else:
            groupes.append([a, b])
    res, o = [], 0.0
    for a, b in groupes:
        a = math.floor(a * fps + 1e-6) / fps
        b = min(math.ceil(b * fps - 1e-6) / fps, duree)
        res.append({"debut": round(a, 4), "fin": round(b, 4), "page": round(o, 4)})
        o += b - a
    return res


def ecrire_srt(blocs, fichier):
    def tc(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    lignes = []
    for i, b in enumerate(blocs, 1):
        texte = re.sub(r"</?em>", "", b["html"])
        lignes += [str(i), f"{tc(b['s'])} --> {tc(b['e'])}", texte, ""]
    Path(fichier).write_text("\n".join(lignes), encoding="utf-8")


def main():
    projet = Path(sys.argv[1])
    fiche = lire_json(projet / "fiche.json")
    M = lire_json(projet / "mots.json")
    mots, duree = M["mots"], M["duree"]
    from charte import style_de_la_charte
    style = style_de_la_charte(fiche.get("style"))   # sans « style » dans la fiche : l'ambiance de la charte
    fmt = format_projet(projet)
    youtube = fmt == "youtube"
    LARG, HAUT = dimensions_format(fmt)
    if youtube:   # sous-titres YouTube : une ligne en bas de l'image, des phrases plus longues
        style["sous_titres"].update({"position": 0.87, "mots_par_bloc": 8, "karaoke": False})
    for k in ("karaoke", "couleur_karaoke", "position", "mots_par_bloc"):
        if k in fiche.get("sous_titres", {}):
            style["sous_titres"][k] = fiche["sous_titres"][k]
    t = Temps(mots)
    erreurs, alertes, effets = [], [], []

    for i, e in enumerate(fiche.get("effets", [])):
        nom = f"effet {i + 1} ({e.get('type')})"
        try:
            e = dict(e)
            if "debut" in e:
                e["debut"] = t(e["debut"], "debut", nom)
            if "fin" in e:
                e["fin"] = t(e["fin"], "fin", nom)
            elif "duree" in e:
                e["fin"] = round(e["debut"] + float(e["duree"]), 3)
            if "lancer" in e:
                e["lancer"] = t(e["lancer"], "lancer", nom)
            if "au" in e:
                e["au"] = t(e["au"], "au", nom)
            if isinstance(e.get("reperes"), dict):
                e["reperes"] = {k: t(v, "repère " + k, nom) for k, v in e["reperes"].items()}
            if e.get("type") == "sur_mesure":
                e["icones"] = {n: icone_svg(n) for n in e.get("icones", [])} if isinstance(e.get("icones"), list) else e.get("icones", {})
                if e.get("zone", "haut") not in ("gauche", "droite", "haut", "centre_bas", "plein", "panneau"):
                    raise ValueError(f"{nom}: zone inconnue « {e.get('zone')} » (gauche, droite, haut, centre_bas, plein, panneau)")
            if e.get("type") == "illustration":
                if e.get("icone"):
                    e["icone"] = icone_svg(e["icone"])
                if isinstance(e.get("vers"), dict) and e["vers"].get("icone"):
                    e["vers"] = dict(e["vers"]); e["vers"]["icone"] = icone_svg(e["vers"]["icone"])
            if e.get("type") == "comparaison":
                for c in ("gauche", "droite"):
                    e[c] = dict(e.get(c) or {})
                    if e[c].get("icone"):
                        e[c]["icone"] = icone_svg(e[c]["icone"])
            for cle_liste in ("items", "etapes", "cercles"):
                e[cle_liste] = [dict(x) if isinstance(x, dict) else x for x in (e.get(cle_liste) or [])] or e.get(cle_liste)
            for it in (e.get("items") or []) + (e.get("etapes") or []) + (e.get("cercles") or []):
                if isinstance(it, dict) and "debut" in it:
                    it["debut"] = t(it["debut"], "item", nom)
                if isinstance(it, dict) and isinstance(it.get("barre"), str):
                    it["barre"] = t(it["barre"], "barre", nom)
        except ValueError as x:
            erreurs.append(str(x)); continue
        if e["type"] == "accroche":
            e["debut"] = 0.0
            e.setdefault("fin", 2.5)
        if e["type"] == "objet_3d" and e.get("lancer") and "fin" not in e:
            e["fin"] = round(e["lancer"] + 0.95, 3)
        if e["type"] == "vitre":
            e.setdefault("fin", e["debut"] + 1.8)
        if "debut" not in e or "fin" not in e:
            erreurs.append(f"{nom}: il manque debut ou fin"); continue
        if e["fin"] <= e["debut"]:
            erreurs.append(f"{nom}: la fin ({e['fin']}) est avant le début ({e['debut']})")
        if e["fin"] > duree + 0.05:
            alertes.append(f"{nom}: finit après la vidéo, ramené à {duree:.2f} s"); e["fin"] = duree
        if youtube and e.get("y", 0) > ZONE_SOUS_TITRES_YOUTUBE:
            alertes.append(f"{nom}: y={e['y']} touche la bande des sous-titres (au-dessus de {ZONE_SOUS_TITRES_YOUTUBE} conseillé)")
        elif not youtube and e.get("y", 0) > ZONE_TEXTE_MAX_Y:
            erreurs.append(f"{nom}: y={e['y']} est dans la zone des boutons d'Instagram (max {ZONE_TEXTE_MAX_Y})")
        for champ in ("fichier", "image"):
            if champ in e:
                p = (projet / e[champ]) if not Path(e[champ]).is_absolute() else Path(e[champ])
                if not p.exists():
                    erreurs.append(f"{nom}: fichier introuvable {e[champ]}")
                e[champ] = p
        if "videos" in e:
            e["videos"] = [(projet / v) if not Path(v).is_absolute() else Path(v) for v in e["videos"]]
            for v in e["videos"]:
                if not v.exists():
                    erreurs.append(f"{nom}: fichier introuvable {v}")
        if e["type"] == "pixel_art" and not e.get("image"):
            sprite = projet / "pixel-moi.png"
            if not sprite.exists():
                from sprite import fabriquer
                print("Fabrication du mini-personnage en pixel art…")
                fabriquer(projet, float(e.get("image_au", 1.0)), sprite)
            e["image"] = sprite
        if e["type"] in BESOIN_DETOURAGE and not (projet / "detourage.webm").exists():
            erreurs.append(f"{nom}: cet effet demande le détourage. Lance : python moteur/detourer.py {projet}")
        effets.append(e)

    # illustrations : côtés alternés automatiquement, jamais deux en même temps du même côté
    illus = sorted([e for e in effets if e["type"] == "illustration"], key=lambda e: e["debut"])
    cote = "gauche"
    for e in illus:
        e.setdefault("cote", cote)
        cote = "droite" if e["cote"] == "gauche" else "gauche"
    for a, b in zip(illus, illus[1:]):
        if a["cote"] == b["cote"] and b["debut"] < a["fin"]:
            erreurs.append(f"Deux illustrations du même côté se chevauchent ({a['debut']:.1f} s et {b['debut']:.1f} s).")
        if b["debut"] - a["debut"] < 1.2:
            alertes.append(f"Illustrations trop rapprochées ({a['debut']:.1f} s et {b['debut']:.1f} s) : laisse au moins 1,5 s.")

    # rythme automatique : recadrage franc à chaque nouvelle phrase (toutes les 3,5 s minimum)
    vis = fiche.get("visage")
    rythme = fiche.get("rythme", not youtube)   # YouTube : pas de recadrage à chaque phrase (vidéo posée)
    if rythme and vis:
        bloque = [(e["debut"] - 0.2, e["fin"] + 0.2) for e in effets if e["type"] in ("zoom", "chapitre", "cadre_explication", "objet_3d", "documentaire", "carte_mot", "carte_titre", "broll", "venn", "feuille_route", "illustration", "comparaison", "sur_mesure", "pixel_art")]
        debuts, prec = [], None
        for i, w in enumerate(mots):
            if i == 0 or re.search(r"[.!?]$", mots[i - 1]["w"]) or (prec and w["s"] - mots[i - 1]["e"] > 0.45):
                debuts.append(w["s"])
            prec = w
        dernier, niveau = -10.0, 0
        niveaux = [1.0, fiche.get("rythme_zoom", 1.09)]
        for d in debuts:
            if d - dernier < 3.5 or d < 0.5 or any(a <= d <= b for a, b in bloque):
                continue
            niveau = 1 - niveau
            effets.append({"type": "recadrage", "debut": round(d - 0.02, 3), "fin": round(d + 0.1, 3), "echelle": niveaux[niveau], "x": vis["x"], "y": vis["y"]})
            dernier = d
        for a, b in bloque:   # retour au cadre normal après chaque gros effet
            effets.append({"type": "recadrage", "debut": round(b, 3), "fin": round(b + 0.1, 3), "echelle": 1.0, "x": vis["x"], "y": vis["y"]})
    elif rythme:
        alertes.append("Rythme automatique désactivé : ajoute \"visage\": {\"x\": ..., \"y\": ...} (centre du visage) dans la fiche.")

    # règles de la maison
    types = [e["type"] for e in effets]
    if "accroche" not in types:
        alertes.append("Pas d'accroche : chaque vidéo doit ouvrir sur une accroche écrite (effet accroche).")
    if "cta_commentaire" not in types and not youtube:
        alertes.append("Pas de CTA commentaire : ajoute cta_commentaire sur la phrase d'appel à l'action.")
    gros = sorted([e for e in effets if e["type"] in GROS], key=lambda e: e["debut"])
    for a, b in zip(gros, gros[1:]):
        if b["debut"] - a["debut"] < 2.5 and not (a["type"] == "objet_3d" and b["type"] == "vitre"):
            alertes.append(f"Rythme : {a['type']} ({a['debut']:.1f} s) et {b['type']} ({b['debut']:.1f} s) sont trop proches. Laisse respirer (2,5 s minimum).")
    plein = sorted([(e["debut"], e["fin"]) for e in effets if e["type"] in PLEIN_ECRAN or (e["type"] == "broll" and e.get("mode", "plein") == "plein")
                    or (e["type"] == "chapitre" and e.get("mode") != "bandeau")])
    for (d1, f1), (d2, f2) in zip(plein, plein[1:]):
        if d2 < f1 - 0.05:
            erreurs.append(f"Deux effets plein écran se chevauchent ({d1:.1f}-{f1:.1f} s et {d2:.1f}-{f2:.1f} s).")
    densite = len(gros) / max(duree, 1) * 10
    if densite > 2.2:
        alertes.append(f"Trop d'effets : {len(gros)} gros effets pour {duree:.0f} s. Vise 1 à 2 toutes les 10 secondes.")
    if youtube:
        reperes_t = sorted([0.0] + [e["debut"] for e in effets if e["type"] != "recadrage"] + [duree])
        for a, b in zip(reperes_t, reperes_t[1:]):
            if b - a > 60:
                alertes.append(f"Aucun effet entre {a:.0f} s et {b:.0f} s : vise un effet toutes les 20 à 40 s.")
        if fiche.get("cadrage"):
            alertes.append("« cadrage » est ignoré en format YouTube (l'image reste entière).")

    for x in alertes:
        print("ALERTE :", x)
    if erreurs:
        for x in erreurs:
            print("ERREUR :", x)
        sys.exit("La fiche contient des erreurs. Corrige fiche.json puis relance.")

    # sous-titres
    # vitre : s'efface avant le gros effet suivant
    for e in effets:
        if e["type"] == "vitre":
            suivants = [x["debut"] for x in effets if x is not e and x["type"] in GROS and x["debut"] > e["debut"]]
            if suivants and min(suivants) < e["fin"]:
                e["fin"] = round(max(e["debut"] + 0.9, min(suivants) - 0.05), 3)
    masques = [(e["debut"], e["fin"]) for e in effets if e["type"] in PLEIN_ECRAN | {"image", "cta_commentaire", "compteur"}
               or (e["type"] == "chapitre" and e.get("mode") != "bandeau")]
    st = fiche.get("sous_titres", {"actif": True})
    blocs = blocs_sous_titres(mots, style, st.get("mots_cles", []), masques, 42 if youtube else None) if st.get("actif", True) else []
    if youtube:
        # posés par ffmpeg au rendu (rapide sur 30 min) ; le .srt complet sert aux sous-titres YouTube
        ecrire_json(projet / "sous-titres.json", {"style": style["sous_titres"], "blocs": blocs, "largeur": LARG, "hauteur": HAUT})
        ecrire_srt(blocs_sous_titres(mots, style, [], [], 42), projet / "sous-titres.srt")
        blocs_page = []
    else:
        blocs_page = blocs

    # projet HyperFrames
    out = projet / "montage"
    if out.exists():
        shutil.rmtree(out)
    (out / "media").mkdir(parents=True)
    shutil.copytree(RACINE / "assets" / "fonts", out / "fonts")
    for f in ("gsap.min.js", "montagia.js"):
        shutil.copy(RACINE / "runtime" / f, out / f)
    if youtube:   # vidéo longue : lien vers le fichier plutôt qu'une copie de plusieurs Go
        try:
            os.link(projet / "base.mp4", out / "media" / "base.mp4")
        except OSError:
            shutil.copy(projet / "base.mp4", out / "media" / "base.mp4")
    else:
        shutil.copy(projet / "base.mp4", out / "media" / "base.mp4")
    det = None
    if (projet / "detourage.webm").exists():
        shutil.copy(projet / "detourage.webm", out / "media" / "detourage.webm"); det = "media/detourage.webm"
    copies = {}

    def media_local(p):
        p = Path(p)
        if str(p) not in copies:
            nom = f"m{len(copies):02d}{p.suffix.lower()}"
            shutil.copy(p, out / "media" / nom)
            copies[str(p)] = "media/" + nom
        return copies[str(p)]

    for e in effets:
        for champ in ("fichier", "image"):
            if champ in e:
                e[champ] = media_local(e[champ])
        if "videos" in e:
            e["videos"] = [media_local(v) for v in e["videos"]]
        for it in e.get("items", []) or []:
            if isinstance(it, dict) and "image" in it:
                p = Path(it["image"]) if Path(it["image"]).is_absolute() else projet / it["image"]
                it["image"] = media_local(p)

    # vidéos déclarées dans la page dès le départ
    pool, piste = [], 20

    def declarer(src, debut, fin, decalage=0.0):
        nonlocal piste
        vid = f"mv-{len(pool)}"
        attrs = f'id="{vid}" src="{src}" muted playsinline data-start="{debut:.3f}" data-duration="{max(0.1, fin - debut):.3f}" data-track-index="{piste}"'
        if decalage:
            attrs += f' data-media-start="{decalage:.3f}"'
        pool.append(f"<video {attrs}></video>")
        piste += 1
        return vid

    for e in effets:
        if e["type"] == "broll":
            e["_v"] = [declarer(e["fichier"], e["debut"], e["fin"], float(e.get("decalage", 0)))]
        elif e["type"] == "telephones":
            e["_v"] = [declarer(v, e["debut"], e["fin"]) for v in e["videos"] if not re.search(r"\.(png|jpe?g|webp)$", v, re.I)]
        elif e["type"] == "documentaire" and det:
            e["_v"] = [declarer(det, e["debut"], e["fin"], e["debut"])]

    import json
    data = {"style": style, "effets": effets, "sous_titres": blocs_page, "duree": duree,
            "detourage": det, "cadrage": fiche.get("cadrage")}
    if youtube:
        data.update({"format": "youtube", "cadrage": None})
    modele = (RACINE / "runtime" / "page.html").read_text(encoding="utf-8")
    modele = modele.replace("__LARGEUR__", str(LARG)).replace("__HAUTEUR__", str(HAUT)).replace("__FORMAT__", fmt)
    html = modele
    html = html.replace("__DUREE__", f"{duree:.3f}")
    (out / "donnees.js").write_text("window.MONTAGIA = " + json.dumps(data, ensure_ascii=False) + ";\nwindow.MONTAGIA_SUR_MESURE = window.MONTAGIA_SUR_MESURE || {};\n", encoding="utf-8")
    html = html.replace("__DETOURAGE__", f'<video id="v-detour" src="{det}" muted playsinline data-start="0" data-duration="{duree:.3f}" data-track-index="2"></video>' if det else "")
    scripts = []
    for e in effets:
        if e["type"] != "sur_mesure":
            continue
        src_dir = None
        for d in (projet / "sur-mesure", RACINE / "ma-bibliotheque"):
            if (d / f"{e['nom']}.js").exists():
                src_dir = d; break
        if not src_dir:
            sys.exit(f"ERREUR : sur-mesure/{e['nom']}.js introuvable (ni dans le projet, ni dans ma-bibliotheque/).")
        (out / "sur-mesure").mkdir(exist_ok=True)
        for ext in (".js", ".css"):
            f = src_dir / f"{e['nom']}{ext}"
            if f.exists():
                shutil.copy(f, out / "sur-mesure" / f.name)
                scripts.append(f'<link rel="stylesheet" href="sur-mesure/{f.name}">' if ext == ".css" else f'<script src="sur-mesure/{f.name}"></script>')
        for f in (src_dir / f"{e['nom']}-fichiers").glob("*") if (src_dir / f"{e['nom']}-fichiers").exists() else []:
            shutil.copy(f, out / "sur-mesure" / f.name)
    html = html.replace("__SUR_MESURE__", "\n".join(dict.fromkeys(scripts)))
    html = html.replace("__MEDIAS__", "\n    ".join(pool))
    (out / "index.html").write_text(html, encoding="utf-8")

    if youtube:
        # page des fenêtres : uniquement les passages avec effets, mis bout à bout (rendu rapide)
        fen = fenetres_effets(effets, duree)
        total = round(sum(f["fin"] - f["debut"] for f in fen), 4)
        ecrire_json(projet / "fenetres.json", {"duree": duree, "fenetres": fen, "a_rendre": total})
        pool, piste = [], 20
        effets_f = []
        for f in fen:
            d = f["page"] - f["debut"]
            for e in effets:
                if e["type"] == "recadrage" or not (f["debut"] - 1e-6 <= e["debut"] <= f["fin"]):
                    continue
                x = decaler({k: v for k, v in e.items() if k != "_v"}, d)
                if x["type"] == "broll":
                    x["_v"] = [declarer(x["fichier"], x["debut"], x["fin"], float(x.get("decalage", 0)))]
                elif x["type"] == "telephones":
                    x["_v"] = [declarer(v, x["debut"], x["fin"]) for v in x["videos"] if not re.search(r"\.(png|jpe?g|webp)$", v, re.I)]
                elif x["type"] == "documentaire" and det:
                    x["_v"] = [declarer(det, x["debut"], x["fin"], e["debut"])]
                effets_f.append(x)
        clips = lambda src, cls, piste_n: "\n    ".join(
            f'<video id="{cls}-{i}" class="{cls}" src="{src}" muted playsinline data-start="{f["page"]:.3f}" data-duration="{f["fin"] - f["debut"]:.3f}" data-media-start="{f["debut"]:.3f}" data-track-index="{piste_n}"></video>'
            for i, f in enumerate(fen))
        html_f = modele.replace('<video id="v-base" src="media/base.mp4" muted playsinline data-start="0" data-duration="__DUREE__" data-track-index="1"></video>',
                                clips("media/base.mp4", "v-base", 1))
        html_f = html_f.replace("__DUREE__", f"{total + 0.5:.3f}")   # marge : le rendu laisse tomber les toutes dernières images
        html_f = html_f.replace("__DETOURAGE__", clips(det, "v-detour", 2) if det else "")
        html_f = html_f.replace('<script src="donnees.js"></script>', '<script src="donnees-fenetres.js"></script>')
        html_f = html_f.replace("__SUR_MESURE__", "\n".join(dict.fromkeys(scripts)))
        html_f = html_f.replace("__MEDIAS__", "\n    ".join(pool))
        data_f = dict(data, effets=effets_f, duree=total)
        (out / "donnees-fenetres.js").write_text("window.MONTAGIA = " + json.dumps(data_f, ensure_ascii=False) + ";\nwindow.MONTAGIA_SUR_MESURE = window.MONTAGIA_SUR_MESURE || {};\n", encoding="utf-8")
        (out / "fenetres.html").write_text(html_f, encoding="utf-8")
        print(f"YouTube : {len(fen)} passages avec effets, {total:.0f} s à rendre image par image sur {duree:.0f} s.")

    # sons
    sons = []
    if fiche.get("sons", style.get("sons", False)):
        for e in effets:
            if e.get("son") is False:
                continue
            for son, dec, vol in SONS.get(e["type"], []):
                tt = e["debut"] + dec
                if e["type"] == "objet_3d" and e.get("lancer"):
                    sons.append({"son": "whoosh", "t": e["lancer"], "volume": 0.6})
                if e["type"] == "etiquettes":
                    n = len(e["items"])
                    for k, it in enumerate(e["items"]):
                        t0 = it.get("debut", e["debut"] + k * min(0.5, (e["fin"] - e["debut"]) / (n + 1)))
                        sons.append({"son": son, "t": round(t0, 3), "volume": vol})
                    continue
                sons.append({"son": son, "t": round(max(0, tt), 3), "volume": vol})
    ecrire_json(projet / "sons.json", {"sons": sons, "musique": fiche.get("musique") or style.get("charte", {}).get("musique"), "musique_volume": fiche.get("musique_volume", style.get("musique_volume", 0.08))})
    ecrire_json(projet / "fiche-resolue.json", {"effets": [{k: (str(v) if isinstance(v, Path) else v) for k, v in e.items()} for e in effets]})
    print(f"OK : {len(effets)} effets, {len(blocs)} sous-titres, {len(sons)} sons -> {out}")


if __name__ == "__main__":
    main()
