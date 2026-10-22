#!/usr/bin/env python3
"""Plusieurs identités (un compte, un client = une identité) : charte, framework de style et modèles de montage rangés à part.

Usage : python systeme/ma-bibliotheque/identite.py liste
        python systeme/ma-bibliotheque/identite.py active
        python systeme/ma-bibliotheque/identite.py creer <nom> [--depuis <autre identité>]
        python systeme/ma-bibliotheque/identite.py activer <nom>
        python systeme/ma-bibliotheque/identite.py sauver

Une identité = un dossier systeme/identites/<nom>/ avec ses fichiers :
  ma-charte.json, mon-framework.md, modele-replique.json, modele-finitions.json (et son logo si elle en a un).
Montag'IA travaille toujours avec les fichiers « actifs » (systeme/ma-charte.json, systeme/mon-framework.md,
systeme/ma-bibliotheque/modele-*.json). « activer » range d'abord l'identité en cours dans son dossier, puis met l'autre en place.
« creer » part d'une copie de l'identité en cours (ou de --depuis) : on change ensuite couleurs, polices, pseudo, style.
"""
import shutil
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "identites"
ACTIVE = DOSSIER / "active.txt"
FICHIERS = {                                   # nom dans le dossier de l'identité -> fichier actif
    "ma-charte.json": RACINE / "ma-charte.json",
    "mon-framework.md": RACINE / "mon-framework.md",
    "modele-replique.json": RACINE / "ma-bibliotheque" / "modele-replique.json",
    "modele-finitions.json": RACINE / "ma-bibliotheque" / "modele-finitions.json",
}


def nom_propre(nom):
    n = "".join(c if c.isalnum() or c in "-_" else "-" for c in nom.strip().lower()).strip("-")
    if not n:
        sys.exit("Donne un nom d'identité (lettres, chiffres, tirets).")
    return n


def active():
    return ACTIVE.read_text(encoding="utf-8").strip() if ACTIVE.exists() else None


def copier(de, vers):
    """de = None : fichiers actifs -> dossier « vers ». Sinon : dossier « de » -> fichiers actifs."""
    if de is None:
        vers.mkdir(parents=True, exist_ok=True)
    for nom, actif in FICHIERS.items():
        src = de / nom if de else actif
        dst = vers / nom if de is None else actif
        if src.exists():
            shutil.copy(src, dst)
        elif de is not None and dst.exists():
            dst.unlink()                       # l'identité n'a pas ce fichier : on ne garde pas celui de l'autre


def sauver():
    a = active()
    if not a:
        sys.exit("Aucune identité active. Crée d'abord la première : identite.py creer <nom>")
    copier(None, DOSSIER / a)
    print(f"OK : identité « {a} » sauvegardée.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    c, a = sys.argv[1], sys.argv[2:]
    DOSSIER.mkdir(exist_ok=True)
    if c == "liste":
        noms = sorted(d.name for d in DOSSIER.iterdir() if d.is_dir())
        for n in noms:
            print(("* " if n == active() else "  ") + n)
        if not noms:
            print("Aucune identité pour l'instant.")
    elif c == "active":
        print(active() or "aucune")
    elif c == "sauver":
        sauver()
    elif c == "creer":
        if not a:
            sys.exit("Usage : identite.py creer <nom> [--depuis <autre>]")
        n = nom_propre(a[0])
        if (DOSSIER / n).exists():
            sys.exit(f"L'identité « {n} » existe déjà.")
        if active():
            sauver()
        if "--depuis" in a:
            src = DOSSIER / nom_propre(a[a.index("--depuis") + 1])
            if not src.exists():
                sys.exit(f"Identité « {src.name} » introuvable.")
            shutil.copytree(src, DOSSIER / n)
            copier(DOSSIER / n, None)
        else:
            copier(None, DOSSIER / n)
        ACTIVE.write_text(n, encoding="utf-8")
        print(f"OK : identité « {n} » créée et active. Règle maintenant sa charte (charte ...) et son style (mon-framework.md), puis : identite.py sauver")
    elif c == "activer":
        if not a:
            sys.exit("Usage : identite.py activer <nom>")
        n = nom_propre(a[0])
        if not (DOSSIER / n).exists():
            sys.exit(f"Identité « {n} » introuvable. Identités : " + ", ".join(sorted(d.name for d in DOSSIER.iterdir() if d.is_dir())))
        if active() and active() != n:
            sauver()
        copier(DOSSIER / n, None)
        ACTIVE.write_text(n, encoding="utf-8")
        print(f"OK : identité « {n} » active.")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
