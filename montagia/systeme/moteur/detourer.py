#!/usr/bin/env python3
"""Détourage de la personne (pour le texte derrière elle et la carte documentaire).
Modèle IA local, gratuit, Mac et Windows. Environ 1 minute pour 30 s de vidéo.

Usage : python moteur/detourer.py <dossier_projet>
Sort : detourage.webm (la personne seule, fond transparent)
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import npx, env_node, HYPERFRAMES


def main():
    projet = Path(sys.argv[1]).resolve()
    r = subprocess.run([npx(), "-y", HYPERFRAMES, "remove-background", str(projet / "base.mp4"), "-o", str(projet / "detourage.webm"), "--quality", "best"],
                       env=env_node(), capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        sys.exit("Détourage échoué :\n" + (r.stdout + r.stderr)[-2500:])
    print(f"OK : {projet / 'detourage.webm'}")


if __name__ == "__main__":
    main()
