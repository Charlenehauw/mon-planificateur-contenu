#!/usr/bin/env python3
"""La charte de la personne : ses couleurs, sa police, son style de sous-titres, ses B-roll.
Elle se règle une fois. Tous les montages la suivent ensuite.

Usage :
  python moteur/charte.py --voir                       (affiche les choix possibles et la charte actuelle)
  python moteur/charte.py --palette bleu-electrique --police moderne --sous-titres classique \\
        --brolls auto --pseudo "@moncompte" --mot-cle GUIDE [--accent "#123456"] [--logo chemin.png]
        [--vocabulaire "Claude,Notion"] [--sons non] [--musique chemin.mp3]
        [--clair "#F6EFE6" --sombre "#3B2A20"]                  (ses couleurs de fond et de texte, en plus de --accent)
        [--style signature|epure|impact] [--da "terracotta, chaleureux, épuré"]   (l'ambiance de ses vidéos)
Sort : ma-charte.json (à la racine de Montag'IA)
"""
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import RACINE, lire_json, ecrire_json

CH = RACINE / "ma-charte.json"
DEFAUTS = {"palette": "blanc-premium", "police": "moderne", "sous_titres": "classique", "brolls": "non", "sons": False}
STYLES = ("signature", "epure", "impact")


def hexa(v, k):
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", v or ""):
        sys.exit(f"{k} : il faut un code couleur du type #RRGGBB (reçu : {v})")
    return v.upper()


def opt(k, d=None):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d


def main():
    C = lire_json(RACINE / "styles" / "choix.json")
    actuelle = lire_json(CH) if CH.exists() else {}
    if "--voir" in sys.argv or len(sys.argv) == 1:
        for k in ("palettes", "polices", "sous_titres"):
            print(f"\n{k.upper()}")
            for cle, v in C[k].items():
                print(f"  {cle:18s} {v['nom']}" + (f"  accent {v['accent']}" if 'accent' in v else ""))
        print("\nCHARTE ACTUELLE :", actuelle or "aucune (à créer)")
        return
    ch = dict(actuelle)
    for cle, k, liste in (("palette", "--palette", "palettes"), ("police", "--police", "polices"), ("sous_titres", "--sous-titres", "sous_titres")):
        v = opt(k)
        if v:
            if v not in C[liste]:
                sys.exit(f"{k} inconnu : {v}. Choix : {', '.join(C[liste])}")
            ch[cle] = v
    for cle, k in (("pseudo", "--pseudo"), ("mot_cle", "--mot-cle"), ("brolls", "--brolls"), ("pexels", "--pexels"), ("mode", "--mode")):
        if opt(k):
            ch[cle] = opt(k)
    for cle, k in (("accent_perso", "--accent"), ("clair_perso", "--clair"), ("sombre_perso", "--sombre")):
        if opt(k):
            ch[cle] = hexa(opt(k), k)
    if opt("--style"):
        if opt("--style") not in STYLES:
            sys.exit(f"--style inconnu : {opt('--style')}. Choix : {', '.join(STYLES)}")
        ch["style"] = opt("--style")
    if opt("--da"):
        ch["da"] = opt("--da")
    if opt("--sons"):
        ch["sons"] = opt("--sons").lower() in ("oui", "yes", "true", "1")
    if opt("--vocabulaire"):
        ch["vocabulaire"] = [x.strip() for x in opt("--vocabulaire").split(",") if x.strip()]
    for cle, k in (("logo", "--logo"), ("musique", "--musique")):
        if opt(k):
            src = Path(opt(k)).expanduser()
            if not src.exists():
                sys.exit(f"Fichier introuvable : {src}")
            (RACINE / "ma-marque").mkdir(exist_ok=True)
            dst = RACINE / "ma-marque" / (cle + src.suffix.lower())
            shutil.copy(src, dst)
            ch[cle] = str(dst)
    for k, v in DEFAUTS.items():
        ch.setdefault(k, v)
    ecrire_json(CH, ch)
    print("OK : charte enregistrée ->", CH)
    print(ch)


def style_de_la_charte(base_nom=None):
    """Style final = style maison + charte de la personne. Utilisé par le compositeur.
    base_nom None : l'ambiance choisie dans la charte (clé « style »), sinon « signature »."""
    S = lire_json(RACINE / "styles" / f"{base_nom or 'signature'}.json")
    ch = lire_json(CH) if CH.exists() else {}
    C = lire_json(RACINE / "styles" / "choix.json")
    for k, v in DEFAUTS.items():
        ch.setdefault(k, v)
    if base_nom is None:
        base_nom = ch.get("style", "signature")
        S = lire_json(RACINE / "styles" / f"{base_nom}.json")
    p = C["palettes"][ch["palette"]]
    acc = ch.get("accent_perso") or p["accent"]
    clair, sombre = ch.get("clair_perso") or p["clair"], ch.get("sombre_perso") or p["sombre"]
    S["couleurs"].update({"accent": acc, "clair": clair, "sombre": sombre})
    f = C["polices"][ch["police"]]
    st = C["sous_titres"][ch["sous_titres"]]
    S["polices"]["titre"] = f["titre"]
    S["sous_titres"].update({"police": f["sous_titres"], "graisse": f["graisse"], "taille": f["taille"] + st["taille_bonus"],
                             "mots_par_bloc": st["mots_par_bloc"], "position": st["position"], "animation": st["animation"],
                             "karaoke": st.get("karaoke", False), "couleur_karaoke": ch.get("couleur_karaoke") or acc,
                             "couleur_mot_cle": acc if acc.upper() != "#FFFFFF" else "#FFD60A",
                             "casse": "majuscules" if ch.get("police") == "percutante" else "normale"})
    S["accroche"].update({"fond": clair, "couleur": sombre, "police": f["titre"]})
    S["mode"] = ch.get("mode") or p.get("mode", "sombre")
    S["sons"] = ch.get("sons", False)
    S["charte"] = ch
    return S


if __name__ == "__main__":
    main()
