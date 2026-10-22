#!/usr/bin/env python3
"""Sous-titres du format YouTube : une image transparente par phrase (Pillow, polices de la charte),
enchaînées dans une liste que ffmpeg pose en bas de la vidéo pendant le rendu.
Rapide sur une vidéo de 30 minutes, contrairement au rendu image par image.

Usage (appelé par rendre.py) : fabriquer(projet, dossier_sortie) -> (liste_concat, y) ou None
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import RACINE, lire_json

POLICES = {"Sora": "Sora.ttf", "Archivo": "Archivo.ttf", "Archivo Black": "ArchivoBlack-Regular.ttf",
           "Playfair Display": "PlayfairDisplay.ttf", "Montserrat": "Montserrat.ttf", "Poppins": "Poppins-Bold.ttf",
           "Bebas Neue": "BebasNeue-Regular.ttf", "Caveat": "Caveat.ttf"}
HAUTEUR_BANDE = 260


def couleur(hexa, alpha=255):
    h = hexa.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def police(nom, graisse, taille):
    from PIL import ImageFont
    f = ImageFont.truetype(str(RACINE / "assets" / "fonts" / POLICES.get(nom, "Sora.ttf")), taille)
    try:   # polices variables : on règle la graisse de la charte
        vals = []
        for a in f.get_variation_axes():
            nm = a.get("name", b"")
            nm = (nm.decode(errors="ignore") if isinstance(nm, bytes) else str(nm)).lower()
            vals.append(max(a["minimum"], min(a["maximum"], graisse)) if "weight" in nm or "wght" in nm else a["default"])
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f


def lignes_du_bloc(mots, f, largeur_max):
    espace = f.getlength(" ")
    total = sum(f.getlength(m["w"]) for m in mots) + espace * (len(mots) - 1)
    if total <= largeur_max or len(mots) < 2:
        return [mots]
    # deux lignes équilibrées
    meilleur, coupe = None, 1
    for k in range(1, len(mots)):
        a = sum(f.getlength(m["w"]) for m in mots[:k]) + espace * (k - 1)
        b = sum(f.getlength(m["w"]) for m in mots[k:]) + espace * (len(mots) - k - 1)
        if meilleur is None or max(a, b) < meilleur:
            meilleur, coupe = max(a, b), k
    return [mots[:coupe], mots[coupe:]]


def image_bloc(bloc, T, f, largeur):
    from PIL import Image, ImageDraw, ImageFilter
    maj = T.get("casse") == "majuscules"
    mots = [{"w": (m["w"].upper() if maj else m["w"]), "cle": m.get("cle")} for m in bloc["mots"]]
    lignes = lignes_du_bloc(mots, f, largeur - 320)
    asc, desc = f.getmetrics()
    haut_ligne = int((asc + desc) * 1.08)
    y0 = HAUTEUR_BANDE // 2 - haut_ligne * len(lignes) // 2
    texte = Image.new("RGBA", (largeur, HAUTEUR_BANDE), (0, 0, 0, 0))
    ombre = Image.new("RGBA", (largeur, HAUTEUR_BANDE), (0, 0, 0, 0))
    dt, do = ImageDraw.Draw(texte), ImageDraw.Draw(ombre)
    espace = f.getlength(" ")
    blanc, cle = couleur(T.get("couleur", "#FFFFFF")), couleur(T.get("couleur_mot_cle", "#FFD60A"))
    for i, ligne in enumerate(lignes):
        lg = sum(f.getlength(m["w"]) for m in ligne) + espace * (len(ligne) - 1)
        x, y = (largeur - lg) / 2, y0 + i * haut_ligne
        for m in ligne:
            do.text((x, y + 4), m["w"], font=f, fill=(0, 0, 0, 215))
            dt.text((x, y), m["w"], font=f, fill=cle if m["cle"] else blanc, stroke_width=2, stroke_fill=(0, 0, 0, 90))
            x += f.getlength(m["w"]) + espace
    ombre = ombre.filter(ImageFilter.GaussianBlur(9))
    return Image.alpha_composite(ombre, texte)


def fabriquer(projet, dossier):
    projet, dossier = Path(projet), Path(dossier)
    f_st = projet / "sous-titres.json"
    if not f_st.exists():
        return None
    D = lire_json(f_st)
    blocs, T, L, H = D["blocs"], D["style"], D["largeur"], D["hauteur"]
    if not blocs:
        return None
    from PIL import Image
    dossier.mkdir(parents=True, exist_ok=True)
    for x in dossier.glob("*.png"):
        x.unlink()
    taille = max(46, min(64, round(T.get("taille", 60) * 0.85)))
    f = police(T.get("police", "Sora"), int(T.get("graisse", 700)), taille)
    Image.new("RGBA", (L, HAUTEUR_BANDE), (0, 0, 0, 0)).save(dossier / "vide.png")
    lignes, t = [], 0.0
    for i, b in enumerate(sorted(blocs, key=lambda b: b["s"])):
        s, e = max(b["s"], t), b["e"]
        if e - s < 0.05:
            continue
        if s - t > 0.001:
            lignes += ["file 'vide.png'", f"duration {s - t:.3f}"]
        nom = f"st{i:05d}.png"
        image_bloc(b, T, f, L).save(dossier / nom, optimize=False, compress_level=1)
        lignes += [f"file '{nom}'", f"duration {e - s:.3f}"]
        t = e
    lignes += ["file 'vide.png'", "duration 1.000", "file 'vide.png'"]
    (dossier / "liste.txt").write_text("ffconcat version 1.0\n" + "\n".join(lignes) + "\n", encoding="utf-8")
    y = min(H - HAUTEUR_BANDE, round(T.get("position", 0.87) * H) - HAUTEUR_BANDE // 2)
    return dossier / "liste.txt", y
