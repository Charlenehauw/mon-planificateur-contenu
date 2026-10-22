#!/usr/bin/env python3
"""Étape 7. Contrôle qualité : une planche d'images prise au milieu de chaque effet.
Claude DOIT regarder cette planche avant de livrer.

Usage : python moteur/controle.py <dossier_projet>
Sort : controle.jpg
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import ffmpeg, run, lire_json, format_projet


def main():
    projet = Path(sys.argv[1]).resolve()
    eff = lire_json(projet / "fiche-resolue.json")["effets"]
    duree = lire_json(projet / "mots.json")["duree"]
    youtube = format_projet(projet) == "youtube"
    if youtube:   # vidéo longue : chaque effet (hors recadrages) + des points réguliers, 30 images maximum
        effets = sorted(round(min(duree - 0.1, (e["debut"] + e["fin"]) / 2), 2) for e in eff if e["type"] != "recadrage")
        if len(effets) > 24:
            effets = [effets[round(i * (len(effets) - 1) / 23)] for i in range(24)]
        reguliers = {round(duree * k / 7, 2) for k in range(1, 7)}
        temps = sorted(set(effets) | reguliers | {0.3, round(duree - 0.5, 2)})[:30]
        for x in (projet / "controle").glob("*.jpg") if (projet / "controle").exists() else []:
            x.unlink()
    else:
        temps = sorted({round(min(duree - 0.1, (e["debut"] + e["fin"]) / 2), 2) for e in eff} | {0.3, round(duree / 2, 2), round(duree - 0.5, 2)})[:24]
    tmp = projet / "controle"
    tmp.mkdir(exist_ok=True)
    taille = "480:270" if youtube else "270:480"
    for i, t in enumerate(temps):
        etiquette = f"{int(t // 60)}m{t % 60:04.1f}s" if youtube else f"{t:.1f}s"
        run([ffmpeg(), "-y", "-ss", str(t), "-i", projet / "final.mp4", "-frames:v", "1", "-vf",
             f"scale={taille},drawtext=text='{etiquette}':x=8:y=8:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6", tmp / f"{i:02d}.jpg"])
    cols = 5 if youtube else 6
    run([ffmpeg(), "-y", "-framerate", "1", "-i", tmp / "%02d.jpg", "-vf", f"tile={cols}x{(len(temps) + cols - 1) // cols}", "-frames:v", "1", projet / "controle.jpg"])
    print(f"OK : {projet / 'controle.jpg'} ({len(temps)} images). Regarde-la avant de livrer.")


if __name__ == "__main__":
    main()
