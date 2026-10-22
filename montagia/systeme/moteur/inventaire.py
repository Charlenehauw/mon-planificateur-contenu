#!/usr/bin/env python3
"""Inventaire des B-roll personnels (vidéos et photos du téléphone).
La personne les dépose dans « Vidéos à monter/Mes plans B-roll » : ils sont copiés dans <projet>/mes-brolls/.
Fabrique une planche avec une image de chaque fichier pour que Claude choisisse où les placer.

Usage : python moteur/inventaire.py <dossier_projet>
Sort : mes-brolls/inventaire.jpg et mes-brolls/inventaire.txt
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import ffmpeg, run, duree, BROLLS_PERSO

VID, IMG = {".mp4", ".mov", ".m4v", ".webm"}, {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def main():
    d = Path(sys.argv[1]) / "mes-brolls"
    d.mkdir(exist_ok=True)
    if BROLLS_PERSO.exists():                  # copie les plans déposés par la personne
        for f in BROLLS_PERSO.iterdir():
            if f.suffix.lower() in VID | IMG and not (d / f.name).exists():
                shutil.copy2(f, d / f.name)
    fichiers = sorted(f for f in d.iterdir() if f.suffix.lower() in VID | IMG)
    if not fichiers:
        sys.exit("Aucun plan trouvé. Dépose tes vidéos et photos du téléphone dans « Vidéos à monter/Mes plans B-roll » puis relance.")
    tmp = d / ".apercus"; tmp.mkdir(exist_ok=True)
    lignes = []
    for i, f in enumerate(fichiers):
        if f.suffix.lower() in VID:
            dur = duree(f)
            run([ffmpeg(), "-y", "-ss", str(min(1.0, dur / 2)), "-i", f, "-frames:v", "1", "-vf",
                 f"scale=320:568:force_original_aspect_ratio=decrease,pad=320:568:(ow-iw)/2:(oh-ih)/2,drawtext=text='{i + 1}':x=10:y=10:fontsize=40:fontcolor=white:box=1:boxcolor=black@0.6", tmp / f"{i:02d}.jpg"])
            lignes.append(f"{i + 1}. {f.name}  vidéo {dur:.1f} s")
        else:
            run([ffmpeg(), "-y", "-i", f, "-frames:v", "1", "-vf",
                 f"scale=320:568:force_original_aspect_ratio=decrease,pad=320:568:(ow-iw)/2:(oh-ih)/2,drawtext=text='{i + 1}':x=10:y=10:fontsize=40:fontcolor=white:box=1:boxcolor=black@0.6", tmp / f"{i:02d}.jpg"])
            lignes.append(f"{i + 1}. {f.name}  photo")
    cols = min(6, len(fichiers))
    run([ffmpeg(), "-y", "-framerate", "1", "-i", tmp / "%02d.jpg", "-vf", f"tile={cols}x{(len(fichiers) + cols - 1) // cols}", "-frames:v", "1", d / "inventaire.jpg"])
    (d / "inventaire.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes)); print(f"Planche : {d / 'inventaire.jpg'}")


if __name__ == "__main__":
    main()
