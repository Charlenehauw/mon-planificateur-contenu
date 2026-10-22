#!/usr/bin/env python3
"""Met à jour Montag'IA sans rien perdre.

Remplace uniquement le moteur (code, skills, polices, mode d'emploi). Garde tout ce qui appartient à la personne :
sa charte, son style (mon-framework.md), sa marque, sa bibliothèque d'effets, ses projets, ses vidéos à monter
et ses vidéos montées, et les outils déjà installés. Fait une sauvegarde avant de toucher à quoi que ce soit.

Usage (depuis le dossier Montag'IA, celui qui contient « COMMENCE ICI ») :
  python3 systeme/montagia.py mettre-a-jour
  ou, pour une ancienne version qui n'a pas cette commande :
  python3 mettre-a-jour.py                       (script téléchargé depuis la page d'accès)
  python3 mettre-a-jour.py --recuperer <ancien dossier>   (nouveau dossier déjà dézippé : reprend le style de l'ancien)
Fonctionne sur Mac et Windows, sans rien installer de plus.
"""
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

SITE = "https://systembia.com/telechargements/montagia-a34af0/"
DERNIERE = "Montagia-v1.4.zip"
# Ce qui est remplacé : le moteur, jamais les affaires de la personne
REMPLACER = ["CLAUDE.md", ".claude/skills/montage-ia", ".claude/skills/mon-style", "COMMENCE ICI - Mode d'emploi.pdf",
             "systeme/montagia.py", "systeme/moteur", "systeme/runtime", "systeme/styles", "systeme/assets", "systeme/exemples",
             "systeme/LISEZ-MOI.md", "systeme/CREDITS.md"]
# Ce qui appartient à la personne et se reprend d'un ancien dossier
A_ELLE = ["systeme/ma-charte.json", "systeme/mon-framework.md", "systeme/ma-marque", "systeme/ma-bibliotheque"]


def trouver_racine(depart):
    for d in (depart, depart / "montagia", depart.parent):
        if (d / "systeme" / "montagia.py").exists():
            return d.resolve()
    sys.exit("Je ne trouve pas le dossier Montag'IA ici. Lance-moi depuis le dossier qui contient « COMMENCE ICI ».")


def copier(src, dst):
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def supprimer(p):
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()


def version_en_ligne():
    try:
        with urllib.request.urlopen(SITE + "derniere-version.txt", timeout=20) as r:
            nom = r.read().decode().strip()
            return nom if nom.endswith(".zip") else DERNIERE
    except Exception:
        return DERNIERE


def bilan(racine):
    s = racine / "systeme"
    projets = [p for p in (s / "projets").iterdir() if p.is_dir()] if (s / "projets").exists() else []
    montees = [f for f in (racine / "Mes vidéos montées").glob("*.mp4")] if (racine / "Mes vidéos montées").exists() else []
    print("  Gardé, sans aucune modification :")
    print("   - ta charte (couleurs, police, sous-titres)" if (s / "ma-charte.json").exists() else "   - pas encore de charte (Claude te posera les questions)")
    if (s / "mon-framework.md").exists():
        print("   - ton style de montage (mon-framework.md)")
    if (s / "ma-bibliotheque").exists() and any(f.suffix == ".js" for f in (s / "ma-bibliotheque").iterdir()):
        print("   - tes effets sur mesure (ma-bibliotheque)")
    print(f"   - tes projets ({len(projets)}) et tes vidéos montées ({len(montees)})")
    print("   - tes vidéos à monter et les outils déjà installés")


def mettre_a_jour(racine):
    nom = version_en_ligne()
    print(f"Mise à jour de Montag'IA vers {nom.replace('Montagia-', '').replace('.zip', '')}…")
    tmp = Path(tempfile.mkdtemp(prefix="montagia-maj-"))
    try:
        zp = tmp / nom
        local = os.environ.get("MONTAGIA_ZIP_LOCAL")     # essais : un zip déjà sur l'ordinateur
        if local:
            shutil.copy(local, zp)
        else:
            urllib.request.urlretrieve(SITE + nom, zp)
        with zipfile.ZipFile(zp) as z:
            z.extractall(tmp / "neuf")
        neuf = tmp / "neuf" / "montagia"
        if not (neuf / "systeme" / "montagia.py").exists():
            sys.exit("Le fichier téléchargé n'est pas complet. Rien n'a été modifié. Réessaie dans un moment.")
        # 1. sauvegarde de ce qui va être remplacé + des affaires de la personne (quelques Mo)
        date = datetime.datetime.now().strftime("%Y-%m-%d %Hh%M")
        sauv = racine / "systeme" / "sauvegardes" / f"avant mise à jour {date}"
        for rel in REMPLACER + A_ELLE + ["systeme/config-machine.json"]:
            if (racine / rel).exists():
                copier(racine / rel, sauv / rel)
        # 2. remplacement du moteur uniquement
        for rel in REMPLACER:
            if (neuf / rel).exists():
                supprimer(racine / rel)
                copier(neuf / rel, racine / rel)
        # 3. dossiers et mode d'emploi manquants, sans toucher à leur contenu
        for d in ("Vidéos à monter", "Vidéos à monter/Mes plans B-roll", "Vidéos à monter/Modèle", "Mes vidéos montées",
                  "systeme/projets", "systeme/ma-bibliotheque"):
            (racine / d).mkdir(parents=True, exist_ok=True)
            lis = neuf / d / "LISEZ-MOI.txt"
            if lis.exists():
                shutil.copy2(lis, racine / d / "LISEZ-MOI.txt")
        (racine / "systeme" / "VERSION").write_text(nom.replace("Montagia-v", "").replace(".zip", "") + "\n", encoding="utf-8")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"  Sauvegarde faite dans systeme/sauvegardes/avant mise à jour {date}")
    bilan(racine)
    print("\nDernière étape : Claude relance l'installation, qui n'ajoute que ce qui manque (quelques minutes).")
    r = subprocess.run([sys.executable, str(racine / "systeme" / "montagia.py"), "installer"], cwd=racine)
    print("\nMise à jour terminée." if r.returncode == 0 else "\nLe moteur est à jour. L'installation a besoin d'un coup de main : demande à Claude « Installe Montag'IA ».")


def recuperer(racine, ancien):
    ancien = trouver_racine(Path(ancien).expanduser())
    if ancien == racine:
        sys.exit("C'est le même dossier, rien à reprendre.")
    print(f"Je reprends ton style depuis l'ancien dossier : {ancien}")
    for rel in A_ELLE:
        if (ancien / rel).exists():
            if (racine / rel).exists() and (racine / rel).is_file():
                copier(racine / rel, racine / "systeme" / "sauvegardes" / "avant reprise" / rel)
            copier(ancien / rel, racine / rel)
            print("  repris :", rel.replace("systeme/", ""))
    print("Ton ancien dossier n'a pas été modifié. Tes anciennes vidéos montées y sont toujours.")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)   # messages dans l'ordre, même avec l'installation lancée ensuite
    except Exception:
        pass
    racine = trouver_racine(Path.cwd())
    if "--recuperer" in sys.argv:
        recuperer(racine, sys.argv[sys.argv.index("--recuperer") + 1])
    else:
        mettre_a_jour(racine)
