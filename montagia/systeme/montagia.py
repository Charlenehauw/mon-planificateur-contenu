#!/usr/bin/env python3
"""Montag'IA, la commande unique.

  python montagia.py installer
  python montagia.py charte [--voir | --palette ... --police ... ...]
  python montagia.py mettre-a-jour                 nouvelle version, sans toucher à la charte, au style ni aux vidéos
  python montagia.py recuperer <ancien dossier>    reprend la charte et le style d'un ancien dossier Montag'IA
  python montagia.py nouveau <nom_du_projet> [video]     transcription + coupes + préparation (voix IA, visage centré)
                                                         sans vidéo : la plus récente du dossier « Vidéos à monter »
  python montagia.py nouveau <nom_du_projet> [video] --youtube   vidéo YouTube horizontale 1920x1080 (longue durée)
  python montagia.py nouveau <nom_du_projet> [video] --4k        vidéo finale en 4K (2160x3840, ou 3840x2160 en YouTube)
  python montagia.py preparer <projet> --agrandissement-ia       vidéo trop petite (WhatsApp...) : agrandissement IA Real-ESRGAN
  python montagia.py reference <projet> <lien ou fichier> [--extrait 612-648]   mode réplique : analyse un reel modèle (ou un passage d'une vidéo longue)
  python montagia.py animation <projet> <debut>-<fin>            une animation du modèle image par image (bande, mouvement, relevé)
  python montagia.py replique <projet> [--apercu 3,8.5]          mode réplique : monte au style relevé dans replique.json
  python montagia.py polices <projet> "texte" [--image img --zone x0,y0,x1,y1]   compare des polices à la référence
  python montagia.py couleurs <image> x0 y0 x1 y1                couleurs exactes d'une zone d'image
  python montagia.py couper <projet> [--retirer 3,7] [--garder 5]   puis relancer : preparer
  python montagia.py preparer <projet>
  python montagia.py detourer <projet>                   (texte derrière la personne, documentaire)
  python montagia.py brolls <projet>                     (inventaire de mes-brolls/)
  python montagia.py broll-auto <projet> "<recherche>" [nom]
  python montagia.py composer <projet>                   (lit fiche.json, vérifie les règles)
  python montagia.py apercu <projet> 3.5,10,22           (images de contrôle rapides, sans rendu)
  python montagia.py rendre <projet> [--brouillon]
  python montagia.py controle <projet>                   (planche finale à regarder)
  python montagia.py verifier <projet>                   (contrôle technique HyperFrames, utile après un effet sur mesure)
  python montagia.py garder <projet> <nom-effet>         (range un effet sur mesure réussi dans ma-bibliotheque/)
Les projets vivent dans montagia/systeme/projets/<nom>. Les vidéos finies sont copiées dans « Mes vidéos montées ».
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
M = RACINE / "moteur"
VENV_PY = RACINE / ".venv" / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable


def projet(nom):
    p = Path(nom).expanduser()
    return p if p.is_absolute() or p.exists() else RACINE / "projets" / nom


def lancer(script, *args):
    r = subprocess.run([PY, str(M / script), *map(str, args)])
    if r.returncode != 0:
        sys.exit(r.returncode)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    c, a = sys.argv[1], sys.argv[2:]
    if c == "installer":
        subprocess.run([sys.executable, str(M / "installer.py")]); return
    if c == "charte":
        lancer("charte.py", *a); return
    if c in ("mettre-a-jour", "mise-a-jour"):
        lancer("mettre_a_jour.py", *a); return
    if c == "recuperer":
        lancer("mettre_a_jour.py", "--recuperer", *a); return
    if c == "nouveau":
        youtube = "--youtube" in a
        k4, k1080 = "--4k" in a, "--1080" in a
        a = [x for x in a if x not in ("--youtube", "--4k", "--1080")]
        sys.path.insert(0, str(M))
        from outils import regler_projet, profil_machine
        if not k4 and not k1080:                       # sans précision : 4K si l'ordinateur le permet
            prof = profil_machine()
            k4 = prof["puissance"] != "faible"
            if not k4:
                print(f"Ordinateur modeste ({prof['coeurs']} cœurs, {prof['ram_go']} Go) : vidéo finale en 1080p, la définition qu'Instagram affiche au maximum."
                      " Ajoute --4k pour forcer la 4K (2 à 3 fois plus long).")
        opts, pos, i = [], [], 0
        while i < len(a):                      # options « --cle valeur » gardées dans l'ordre
            if a[i].startswith("--"):
                opts.append(a[i])
                if i + 1 < len(a) and not a[i + 1].startswith("--"):
                    opts.append(a[i + 1]); i += 1
            else:
                pos.append(a[i])
            i += 1
        if len(pos) == 2 and Path(pos[0]).expanduser().is_file():   # ancien ordre : <video> <nom>
            pos = [pos[1], pos[0]]
        nom = pos[0]
        if len(pos) > 1:
            video = Path(pos[1]).expanduser()
        else:
            dossier = RACINE.parent / "Vidéos à monter"
            vids = sorted([f for f in dossier.glob("*") if f.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm", ".mkv")], key=lambda f: f.stat().st_mtime)
            if not vids:
                sys.exit("Aucune vidéo dans « Vidéos à monter ». Dépose ta vidéo dans ce dossier puis relance.")
            video = vids[-1]
            print(f"Vidéo choisie : {video.name}")
        p = projet(nom); p.mkdir(parents=True, exist_ok=True)
        regler_projet(p, format="youtube" if youtube else None, sortie="4k" if k4 else None)
        if youtube:
            print("Format YouTube : vidéo horizontale" + (" 3840x2160 (4K)" if k4 else " 1920x1080") + ", sans recadrage.")
        elif k4:
            print("Sortie 4K : 2160x3840.")
        lancer("transcrire.py", video, p, *opts)
        lancer("couper.py", p)
        lancer("preparer.py", p)
        print(f"\nProjet prêt : {p}\nÀ relire : rapport-coupes.md et texte-final.txt"); return
    simples = {"couper": "couper.py", "preparer": "preparer.py", "detourer": "detourer.py", "brolls": "inventaire.py",
               "broll-auto": "broll_auto.py", "composer": "composer.py", "rendre": "rendre.py", "controle": "controle.py",
               "reference": "reference.py", "replique": "replique.py"}
    if c == "animation":
        lancer("reference.py", "animation", projet(a[0]), *a[1:]); return
    if c == "polices":
        lancer("reference.py", "polices", projet(a[0]), *a[1:]); return
    if c == "couleurs":
        lancer("reference.py", "couleurs", *a); return
    if c in simples:
        lancer(simples[c], projet(a[0]), *a[1:]); return
    if c == "garder":
        import shutil
        p, nom = projet(a[0]), a[1]
        dest = RACINE / "ma-bibliotheque"; dest.mkdir(exist_ok=True)
        n = 0
        for f in (p / "sur-mesure").glob(nom + "*"):
            (shutil.copytree if f.is_dir() else shutil.copy)(f, dest / f.name); n += 1
        print(f"OK : {n} fichier(s) rangé(s) dans {dest}. Réutilisable dans toutes les vidéos avec \"nom\": \"{nom}\"."); return
    if c == "verifier":
        p = projet(a[0])
        sys.path.insert(0, str(M))
        from outils import npx, env_node, HYPERFRAMES
        r = subprocess.run([npx(), "-y", HYPERFRAMES, "check", str(p / "montage")], env=env_node(), capture_output=True, text=True, errors="replace")
        lignes = [l for l in (r.stdout + r.stderr).splitlines() if "✗" in l or "error" in l.lower() or "⚠" in l]
        print("\n".join(lignes[:40]) or "Aucun problème détecté."); return
    if c == "apercu":
        p = projet(a[0])
        sys.path.insert(0, str(M))
        from outils import npx, env_node, HYPERFRAMES
        import shutil
        shutil.rmtree(p / "montage" / "snapshots", ignore_errors=True)
        subprocess.run([npx(), "-y", HYPERFRAMES, "snapshot", str(p / "montage"), "--at", a[1], "--no-end", "--describe", "false"], env=env_node(), capture_output=True)
        print(f"Images : {p / 'montage' / 'snapshots'}"); return
    print(__doc__)


if __name__ == "__main__":
    main()
