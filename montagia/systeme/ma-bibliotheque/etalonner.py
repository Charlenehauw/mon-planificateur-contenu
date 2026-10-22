#!/usr/bin/env python3
"""Étalonnage de Charlène : enlève la dominante jaune / verte de l'image (balance des blancs automatique), à lancer
APRÈS « preparer » et AVANT « replique » (les couleurs des titres restent ainsi exactes).

Usage : python systeme/ma-bibliotheque/etalonner.py <projet> [--force 0.8] [--chaleur -3] [--apercu]
  --force    0 à 1 : part de la correction appliquée (1 par défaut, 1 = blancs parfaitement neutres)
  --chaleur  -10 à +10 : petit réglage au goût après correction (négatif = plus froid, positif = plus chaud ; -3 par défaut, le réglage choisi par Charlène)
  --lisser   0 à 3 : lissage doux de la peau et du bruit (compression WhatsApp…) + netteté des contours (0 par défaut ;
             1 léger, 2 conseillé pour une vidéo WhatsApp, 3 fort)
  --apercu   écrit seulement <projet>/etalonnage-avant-apres.jpg, sans toucher à la vidéo
Lit / écrit : <projet>/base.mp4 (l'original est gardé une fois dans base-origine.mp4 ; relancer repart toujours de l'original).
Après un nouveau « preparer », supprime base-origine.mp4 puis relance l'étalonnage.
Outils : ffmpeg et numpy, déjà sur l'ordinateur.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent.parent


def ffmpeg():
    cfg = RACINE / "config-machine.json"
    if cfg.exists():
        f = json.loads(cfg.read_text(encoding="utf-8")).get("ffmpeg")
        if f:
            return f
    return "ffmpeg"


def option(nom, defaut):
    return float(sys.argv[sys.argv.index(nom) + 1]) if nom in sys.argv else defaut


def image(video, t, w, h):
    raw = subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float32)


def duree(video):
    sortie = subprocess.run([str(Path(ffmpeg()).with_name("ffprobe")) if Path(ffmpeg()).is_absolute() else "ffprobe", "-v", "error",
                             "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    return float(sortie.strip())


def gains(video):
    """Moyenne des zones claires et peu colorées (murs, plafond, tissus blancs) sur 8 images : elles devraient être grises."""
    d = duree(video)
    pix = []
    for k in range(8):
        a = image(video, d * (k + .5) / 8, 270, 480).reshape(-1, 3)
        lum, ecart = a.mean(1), a.max(1) - a.min(1)
        pix.append(a[(lum > 140) & (lum < 245) & (ecart < 45)])
    pix = np.concatenate(pix)
    if len(pix) < 500:
        sys.exit("Pas assez de zones claires et neutres pour mesurer la dominante : étalonnage non appliqué.")
    m = pix.mean(0)
    return m.mean() / m, m


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    p = Path(sys.argv[1])
    if not p.exists():
        p = RACINE / "projets" / sys.argv[1]
    base, origine = p / "base.mp4", p / "base-origine.mp4"
    source = origine if origine.exists() else base
    g, m = gains(source)
    force, chaleur = option("--force", 1.0), option("--chaleur", -3) / 100
    g = 1 + (g - 1) * force
    g = np.clip(g * np.array([1 + chaleur, 1, 1 - chaleur]), 0.85, 1.15)
    print(f"Blancs mesurés R {m[0]:.0f} V {m[1]:.0f} B {m[2]:.0f} -> correction R x{g[0]:.3f} V x{g[1]:.3f} B x{g[2]:.3f}")
    filtre = f"colorchannelmixer=rr={g[0]:.4f}:gg={g[1]:.4f}:bb={g[2]:.4f},eq=contrast=1.03:saturation=1.04"
    lisser = int(option("--lisser", 0))
    if lisser > 0:
        # bruit et blocs de compression (hqdn3d), peau lissée sans toucher aux contours (bilateral), puis netteté (cas)
        filtre += [None, ",hqdn3d=2:1.5:3:3,bilateral=sigmaS=2:sigmaR=0.04,cas=0.45",
                   ",hqdn3d=3:2:5:5,bilateral=sigmaS=3:sigmaR=0.06,cas=0.6",
                   ",hqdn3d=4:3:6:6,bilateral=sigmaS=4:sigmaR=0.08,cas=0.7"][min(lisser, 3)]
        print(f"Lissage niveau {min(lisser, 3)}")
    if "--apercu" in sys.argv:
        t = duree(source) / 2
        sortie = p / "etalonnage-avant-apres.jpg"
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(source), "-frames:v", "1", "-filter_complex",
                        f"[0]scale=540:-1,split[a][b];[b]{filtre}[c];[a][c]hstack", str(sortie)], check=True)
        print(f"Avant / après : {sortie}")
        return
    if not origine.exists():
        base.rename(origine)
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(origine), "-vf", filtre, "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(base)], check=True)
    print(f"OK : {base} étalonné (original gardé dans {origine.name}). Relance maintenant replique puis finitions.")


if __name__ == "__main__":
    main()
