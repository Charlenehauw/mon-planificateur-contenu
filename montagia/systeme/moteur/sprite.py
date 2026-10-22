#!/usr/bin/env python3
"""Fabrique un mini-personnage en pixel art à partir d'une image de la vidéo (détourage IA local).
Usage : python moteur/sprite.py <dossier_projet> <temps_en_secondes> [sortie.png]
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import ffmpeg, run, npx, env_node, HYPERFRAMES


def fabriquer(projet, t, sortie):
    projet = Path(projet).resolve()
    img = projet / "sprite-source.png"
    run([ffmpeg(), "-y", "-ss", str(t), "-i", projet / "base.mp4", "-frames:v", "1", img])
    cut = projet / "sprite-detoure.png"
    r = subprocess.run([npx(), "-y", HYPERFRAMES, "remove-background", str(img), "-o", str(cut)], env=env_node(), capture_output=True, text=True, errors="replace")
    if r.returncode != 0 or not cut.exists():
        raise RuntimeError("Détourage de l'image impossible :\n" + (r.stdout + r.stderr)[-1500:])
    from PIL import Image
    im = Image.open(cut).convert("RGBA")
    im = im.crop(im.getbbox())
    h = 34
    w = max(8, round(im.width * h / im.height))
    petit = im.resize((w, h), Image.BILINEAR)
    a = petit.split()[3].point(lambda v: 255 if v > 110 else 0)
    rgb = petit.convert("RGB").quantize(colors=20, method=Image.Quantize.MEDIANCUT).convert("RGB")
    petit = Image.merge("RGBA", (*rgb.split(), a))
    petit.resize((w * 13, h * 13), Image.NEAREST).save(sortie)
    return sortie


if __name__ == "__main__":
    p = Path(sys.argv[1])
    print("OK :", fabriquer(p, float(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else p / "pixel-moi.png"))
