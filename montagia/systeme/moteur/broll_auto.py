#!/usr/bin/env python3
"""B-roll automatique : cherche et télécharge des vidéos libres de droits sur Pexels.
Il faut une clé gratuite (pexels.com/api) : variable PEXELS_API_KEY ou "pexels" dans ma-charte.json.

Usage : python moteur/broll_auto.py <dossier_projet> "<recherche en anglais>" [nom] [--horizontal]
Sort : brolls/<nom>.mp4 (vertical par défaut, 1080p max) + brolls/<nom>.jpg (aperçu à regarder)
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import RACINE, ffmpeg, run, lire_json


def cle():
    k = os.environ.get("PEXELS_API_KEY")
    ch = RACINE / "ma-charte.json"
    if not k and ch.exists():
        k = lire_json(ch).get("pexels")
    if not k:
        sys.exit("Pas de clé Pexels. Crée-la gratuitement sur https://www.pexels.com/api puis :\n"
                 "python moteur/charte.py --pexels TA_CLE   (ou variable PEXELS_API_KEY)")
    return k


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    projet, recherche = Path(args[0]), args[1]
    nom = args[2] if len(args) > 2 else recherche.replace(" ", "-")[:30]
    orient = "landscape" if "--horizontal" in sys.argv else "portrait"
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({"query": recherche, "orientation": orient, "per_page": 8, "size": "medium"})
    req = urllib.request.Request(url, headers={"Authorization": cle(), "User-Agent": "Montagia/1.0"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if not data.get("videos"):
        sys.exit(f"Aucun résultat pour « {recherche} ». Essaie d'autres mots (en anglais).")
    v = data["videos"][0]
    fichiers = sorted([f for f in v["video_files"] if f.get("height") and f["height"] <= 1920 and f.get("file_type") == "video/mp4"],
                      key=lambda f: f["height"], reverse=True)
    dossier = projet / "brolls"
    dossier.mkdir(exist_ok=True)
    out = dossier / f"{nom}.mp4"
    urllib.request.urlretrieve(fichiers[0]["link"], out)
    run([ffmpeg(), "-y", "-ss", "1", "-i", out, "-frames:v", "1", "-vf", "scale=360:-2", dossier / f"{nom}.jpg"])
    (dossier / f"{nom}.credit.txt").write_text(f"Vidéo de {v['user']['name']} sur Pexels : {v['url']}\n", encoding="utf-8")
    print(f"OK : {out} ({v['duration']} s). Aperçu : {dossier / (nom + '.jpg')}")


if __name__ == "__main__":
    main()
