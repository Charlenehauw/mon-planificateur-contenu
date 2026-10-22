#!/usr/bin/env python3
"""Installation de Montag'IA, une seule fois. Mac et Windows.

Usage : python moteur/installer.py      (ou python3 sur Mac)
Ce que ça fait :
  1. crée un environnement Python isolé (.venv) et y installe faster-whisper, imageio-ffmpeg et pillow ;
  2. met un ffmpeg dans montagia/bin si l'ordinateur n'en a pas ;
  3. vérifie Node.js (nécessaire pour HyperFrames) et explique comment l'installer s'il manque ;
  4. prépare HyperFrames (télécharge son navigateur de rendu) ;
  5. télécharge le modèle de transcription (environ 1,6 Go, une seule fois) ;
  6. qualité premium, tout en local et gratuit (environ 100 Mo) :
     voix IA (programme deep-filter), cadrage qui suit le visage (Vision d'Apple sur Mac, OpenCV ailleurs),
     téléchargement de reels modèles (yt-dlp). L'agrandissement IA (Real-ESRGAN, 50 Mo) se télécharge à la première demande.
     Un outil déjà présent sur l'ordinateur est réutilisé au lieu d'être téléchargé une deuxième fois.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
WIN = platform.system() == "Windows"
VENV = RACINE / ".venv"
PY = VENV / ("Scripts/python.exe" if WIN else "bin/python")


def etape(t):
    print(f"\n=== {t} ===", flush=True)


def ok(t):
    print(f"  OK  {t}", flush=True)


LISEZ_A_MONTER = ("Dépose ici les vidéos face caméra à monter, puis dis à Claude : « Monte ma vidéo ».\n"
                  "Tes plans de coupe filmés au téléphone (B-roll) vont dans le sous-dossier « Mes plans B-roll ».")
LISEZ_BROLLS = ("Dépose ici tes plans filmés au téléphone (ton bureau, tes mains, ta ville...) et tes photos.\n"
                "Claude choisit les plans qui collent à ce que tu dis et les place au bon moment.")


def preparer_dossiers():
    for nom, txt in (("Vidéos à monter", LISEZ_A_MONTER),
                     ("Vidéos à monter/Mes plans B-roll", LISEZ_BROLLS),
                     ("Mes vidéos montées", "Tes vidéos finies arrivent ici, prêtes à publier.")):
        d = RACINE.parent / nom
        d.mkdir(parents=True, exist_ok=True)
        (d / "LISEZ-MOI.txt").write_text(txt + "\n", encoding="utf-8")


def qualite_premium():
    """Voix IA, visage, reels modèles. Léger : environ 100 Mo. Rien de bloquant : si une pièce échoue, Montag'IA garde la méthode classique.
    Real-ESRGAN (agrandissement IA, 50 Mo) n'est téléchargé qu'à la première demande."""
    etape("4 ter. Qualité premium (voix IA, cadrage sur le visage)")
    if os.environ.get("MONTAGIA_SANS_PREMIUM"):
        print("  (reporté)"); return
    sys.path.insert(0, str(RACINE / "moteur"))
    import qualite
    # voix IA : programme autonome deep-filter (27 Mo), sans PyTorch
    exe = qualite.chemin_deepfilter()
    if not exe:
        print("  Voix IA (DeepFilterNet, 27 Mo)…", flush=True)
        try:
            exe = qualite.installer_deepfilter()
        except Exception as e:
            print(f"  voix IA : échec du téléchargement ({e})")
    voix = exe is not None or qualite.voix_ia_dispo()
    # yt-dlp autonome (37 Mo) : suit YouTube et Instagram sans dépendre du Python de l'ordinateur
    ytb = qualite.chemin_ytdlp()
    if not ytb:
        print("  Téléchargement de vidéos modèles (yt-dlp, 37 Mo)…", flush=True)
        try:
            ytb = qualite.installer_ytdlp()
        except Exception as e:
            print(f"  yt-dlp : échec du téléchargement ({e}), version pip utilisée")
    ok("voix IA prête" if voix else "voix IA indisponible sur cet ordinateur, voix studio classique utilisée")
    # visage : Vision d'Apple sur Mac (16 Mo), OpenCV YuNet ailleurs (150 Mo)
    mac = platform.system() == "Darwin"
    if mac:
        r = subprocess.run([str(PY), "-m", "pip", "install", "-q", "pyobjc-framework-Vision", "pyobjc-framework-Quartz", "yt-dlp"],
                           capture_output=True, text=True)
    else:
        r = subprocess.run([str(PY), "-m", "pip", "install", "-q", "opencv-python-headless>=4.8,<4.11", "yt-dlp"], capture_output=True, text=True)
        modeles = RACINE / ".outils" / "modeles"
        modeles.mkdir(parents=True, exist_ok=True)
        if not qualite.MODELE_VISAGE.exists():
            try:
                import urllib.request
                urllib.request.urlretrieve(qualite.URL_MODELE_VISAGE, qualite.MODELE_VISAGE)
            except Exception as e:
                print(f"  modèle de visage : échec ({e}), cadrage centré utilisé")
    if r.returncode != 0 and r.stderr.strip():
        print("  " + r.stderr.strip().splitlines()[-1][:200])
    test = ("import Vision, Quartz" if mac else
            f"import cv2, numpy; cv2.FaceDetectorYN.create(r'{qualite.MODELE_VISAGE}', '', (320, 320))")
    visage = subprocess.run([str(PY), "-c", test], capture_output=True).returncode == 0
    ydl = ytb is not None or subprocess.run([str(PY), "-c", "import yt_dlp"], capture_output=True).returncode == 0
    ok("cadrage qui suit le visage prêt" if visage else "détection du visage indisponible, cadrage centré utilisé")
    ok("téléchargement de reels modèles prêt" if ydl else "yt-dlp indisponible : donne le fichier du reel modèle à la main")
    deja = qualite.chemin_esrgan()
    ok(f"agrandissement IA déjà présent ({deja})" if deja else "agrandissement IA : téléchargé à la première demande (50 Mo)")
    machine = json.loads((RACINE / "config-machine.json").read_text(encoding="utf-8"))
    machine.update({"voix_ia": voix, "deep_filter": str(exe) if exe else None, "upscale_ia": str(deja) if deja else None, "visage": visage})
    (RACINE / "config-machine.json").write_text(json.dumps(machine, indent=1), encoding="utf-8")
    from outils import profil_machine, encodeur
    e = encodeur()               # encodeur vidéo matériel (Mac : VideoToolbox) ou x264 logiciel, gardé dans config-machine.json
    ok("encodeur vidéo matériel : " + e if e != "libx264" else "encodeur vidéo logiciel x264 (pas d'accélération matérielle trouvée)")
    prof = profil_machine()      # mesure et enregistre cœurs, mémoire, puce, puissance
    ok(f"ordinateur {prof['puissance']} : {prof['coeurs']} cœurs, {prof['ram_go']} Go, puce {prof['puce']}"
       + (" (vidéos en 1080p par défaut, 4K sur demande)" if prof["puissance"] == "faible" else " (4K par défaut)"))
    if prof["puissance"] == "faible":
        print("  ATTENTION  ordinateur modeste pour la vidéo" + (" (Mac à puce Intel)" if prof["puce"] != "apple" and sys.platform == "darwin" else "")
              + " : les montages prendront 2 à 4 fois plus de temps que sur un Mac récent à puce Apple.\n"
              "             Ferme les autres applications pendant un montage, et laisse-le tourner pendant que tu fais autre chose.")


def main():
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9 ou plus récent est nécessaire. Installe-le depuis https://www.python.org/downloads puis relance.")
    etape("1. Node.js")
    node = shutil.which("node")
    if not node:
        print("  Node.js manque. Installe la version LTS :")
        print("   - Windows : winget install OpenJS.NodeJS.LTS   (ou https://nodejs.org)")
        print("   - Mac     : brew install node                  (ou https://nodejs.org)")
        print("  Puis ferme et rouvre Claude, et relance cette installation.")
        sys.exit(1)
    v = subprocess.run([node, "-v"], capture_output=True, text=True).stdout.strip()
    if int(v.lstrip("v").split(".")[0]) < 18:
        sys.exit(f"Node.js {v} est trop ancien. Installe la version LTS depuis https://nodejs.org")
    ok(f"Node.js {v}")

    etape("2. Environnement Python")
    if not PY.exists():
        venv.EnvBuilder(with_pip=True).create(VENV)
    subprocess.run([str(PY), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
    subprocess.run([str(PY), "-m", "pip", "install", "-q", "faster-whisper>=1.1", "imageio-ffmpeg", "numpy", "pillow"], check=True)
    ok("faster-whisper, imageio-ffmpeg et pillow installés")

    etape("3. FFmpeg")
    exe = "ffmpeg.exe" if WIN else "ffmpeg"
    systeme = shutil.which("ffmpeg")
    bin_dir = RACINE / "bin"
    if systeme:
        ffm = systeme
        ok(f"ffmpeg déjà présent : {systeme}")
    else:
        src = subprocess.run([str(PY), "-c", "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"], capture_output=True, text=True).stdout.strip()
        bin_dir.mkdir(exist_ok=True)
        ffm = str(bin_dir / exe)
        shutil.copy(src, ffm)
        if not WIN:
            os.chmod(ffm, 0o755)
        ok(f"ffmpeg installé dans {ffm}")
    # ffprobe (indispensable au rendu HyperFrames) : système, sinon récupéré via npm, rangé à côté de ffmpeg
    if not shutil.which("ffprobe") and not (Path(ffm).parent / ("ffprobe.exe" if WIN else "ffprobe")).exists():
        npm = shutil.which("npm") or shutil.which("npm.cmd")
        if npm:
            outils_dir = RACINE / ".outils"; outils_dir.mkdir(exist_ok=True)
            subprocess.run([npm, "install", "--silent", "--no-audit", "--no-fund", "--prefix", str(outils_dir), "@ffprobe-installer/ffprobe"], capture_output=True)
            chemin = subprocess.run(["node", "-e", "console.log(require('@ffprobe-installer/ffprobe').path)"], cwd=str(outils_dir), capture_output=True, text=True).stdout.strip()
            if chemin and Path(chemin).exists():
                cible = Path(ffm).parent / ("ffprobe.exe" if WIN else "ffprobe")
                if Path(ffm).parent != bin_dir:   # ffmpeg système : on range ffprobe dans montagia/bin
                    bin_dir.mkdir(exist_ok=True); cible = bin_dir / cible.name
                shutil.copy(chemin, cible)
                if not WIN:
                    os.chmod(cible, 0o755)
                ok(f"ffprobe installé dans {cible}")
        else:
            print("  ffprobe manque et npm est introuvable : installe Node.js (étape 3) puis relance l'installation.")
    filtres = subprocess.run([ffm, "-hide_banner", "-filters"], capture_output=True, text=True, errors="replace").stdout
    cfg = RACINE / "config-machine.json"
    machine = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}   # on garde les réglages déjà présents
    machine.update({"ffmpeg": ffm, "arnndn": "arnndn" in filtres})
    cfg.write_text(json.dumps(machine, indent=1), encoding="utf-8")
    ok("débruitage IA de la voix disponible" if machine["arnndn"] else "débruitage IA indisponible avec ce ffmpeg, débruitage classique utilisé")

    etape("4. HyperFrames (moteur de rendu)")
    sys.path.insert(0, str(RACINE / "moteur"))
    from outils import npx, env_node, HYPERFRAMES
    r = subprocess.run([npx(), "-y", HYPERFRAMES, "doctor"], env=env_node(), capture_output=True, text=True, errors="replace")
    utiles = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip() and "docker" not in l.lower() and "Some checks failed" not in l]
    print("  " + "\n  ".join(utiles[-6:]))
    ok("HyperFrames prêt")

    etape("4 bis. Savoir-faire HyperFrames pour Claude (skills d'animation)")
    claude = None if os.environ.get("MONTAGIA_SANS_PLUGIN") else (shutil.which("claude") or shutil.which("claude.cmd"))
    if claude:
        subprocess.run([claude, "plugin", "marketplace", "add", "heygen-com/hyperframes"], capture_output=True)
        r2 = subprocess.run([claude, "plugin", "install", "hyperframes@hyperframes"], capture_output=True, text=True, errors="replace")
        ok("skills HyperFrames installées" if r2.returncode == 0 else "skills HyperFrames : à ajouter depuis Claude avec /plugin (heygen-com/hyperframes)")
    else:
        print("  Pour donner à Claude tout le savoir-faire d'animation HyperFrames : dans Claude Code, tape /plugin,")
        print("  ajoute la place de marché heygen-com/hyperframes et installe hyperframes@hyperframes. (Facultatif, l'outil marche sans.)")

    qualite_premium()

    etape("5. Modèle de transcription (une seule fois, environ 1,6 Go)")
    if os.environ.get("MONTAGIA_SANS_MODELE"):
        print("  (téléchargement du modèle reporté au premier montage)")
        preparer_dossiers()
        print("\nInstallation terminée.")
        return
    subprocess.run([str(PY), "-c", "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='auto', compute_type='auto'); print('  OK  modèle prêt')"], check=True)

    preparer_dossiers()
    print("\nInstallation terminée. Claude te pose maintenant quelques questions sur ton style (couleurs, police, ambiance),"
          "\npuis tu déposes ta vidéo dans « Vidéos à monter » et tu lui dis : « Monte ma vidéo ».")


if __name__ == "__main__":
    main()
