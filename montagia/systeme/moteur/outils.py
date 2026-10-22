"""Outils communs de Montag'IA, identiques sur Mac et Windows."""
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent          # montagia/systeme
ACCUEIL = RACINE.parent                                  # montagia/ (ce que voit l'acheteur)
A_MONTER = ACCUEIL / "Vidéos à monter"
BROLLS_PERSO = A_MONTER / "Mes plans B-roll"                # plans du téléphone, visibles
MONTEES = ACCUEIL / "Mes vidéos montées"
WINDOWS = platform.system() == "Windows"


def lire_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ecrire_json(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def trouver(outil):
    """ffmpeg / ffprobe : variable MONTAGIA_FFMPEG_DIR, dossier local, PATH, puis imageio-ffmpeg."""
    exe = outil + (".exe" if WINDOWS else "")
    candidats = []
    if os.environ.get("MONTAGIA_FFMPEG_DIR"):
        candidats.append(Path(os.environ["MONTAGIA_FFMPEG_DIR"]) / exe)
    machine = RACINE / "config-machine.json"
    if machine.exists() and outil == "ffmpeg":
        candidats.append(Path(json.loads(machine.read_text(encoding="utf-8"))["ffmpeg"]))
    candidats.append(RACINE / "bin" / exe)
    candidats.append(Path.home() / ".clipping-tools" / "bin" / exe)
    for c in candidats:
        if c.exists():
            return str(c)
    w = shutil.which(outil)
    if w:
        return w
    if outil == "ffmpeg":
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return None


def ffmpeg():
    f = trouver("ffmpeg")
    if not f:
        sys.exit("ffmpeg introuvable. Lance l'installation : python moteur/installer.py")
    return f


def run(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        raise RuntimeError("Commande échouée : " + " ".join(map(str, cmd))[:400] + "\n" + r.stderr[-2500:])
    return r


def duree(fichier):
    """Durée d'un média en secondes, sans ffprobe obligatoire."""
    fp = trouver("ffprobe")
    if fp:
        r = run([fp, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fichier])
        return float(r.stdout.strip())
    r = subprocess.run([ffmpeg(), "-i", str(fichier)], capture_output=True, text=True, errors="replace")
    import re
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def dimensions(fichier):
    import re
    r = subprocess.run([ffmpeg(), "-i", str(fichier)], capture_output=True, text=True, errors="replace")
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", r.stderr)
    w, h = int(m.group(1)), int(m.group(2))
    rot = re.search(r"rotate\s*:\s*(-?\d+)", r.stderr) or re.search(r"rotation of (-?\d+)", r.stderr)
    if rot and abs(int(float(rot.group(1)))) in (90, 270):
        w, h = h, w
    return w, h


def format_projet(projet):
    """« youtube » (paysage 1920x1080) ou « vertical » (1080x1920, le format d'origine)."""
    f = Path(projet) / "projet.json"
    return lire_json(f).get("format", "vertical") if f.exists() else "vertical"


def dimensions_format(fmt):
    """Repère de travail de la fiche (positions en pixels). Ne change pas en 4K : le rendu 4K double tout."""
    return (1920, 1080) if fmt == "youtube" else (1080, 1920)


def reglages_projet(projet):
    f = Path(projet) / "projet.json"
    return lire_json(f) if f.exists() else {}


def regler_projet(projet, **cles):
    """Ajoute des réglages à projet.json sans effacer les autres (format, sortie 4K...)."""
    d = reglages_projet(projet)
    d.update({k: v for k, v in cles.items() if v is not None})
    for k in [k for k, v in cles.items() if v is None]:
        d.pop(k, None)
    if d:
        ecrire_json(Path(projet) / "projet.json", d)
    elif (Path(projet) / "projet.json").exists():
        (Path(projet) / "projet.json").unlink()


def profil_machine():
    """Cœurs, mémoire (Go), puce et puissance (« forte », « moyenne », « faible »), mesurés une fois et gardés dans config-machine.json."""
    cfg = RACINE / "config-machine.json"
    d = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
    if "puissance" in d and d.get("profil_v") == 2:   # v1 comptait les cœurs logiques : un Mac Intel passait pour « moyenne »
        return d
    coeurs = os.cpu_count() or 4
    go = 8
    try:
        if platform.system() == "Darwin":
            go = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip()) // 1024 ** 3
            coeurs = int(subprocess.run(["sysctl", "-n", "hw.physicalcpu"], capture_output=True, text=True).stdout.strip() or coeurs)
        elif WINDOWS:
            import ctypes
            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in
                            ("ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile", "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual")]
            m = MS(); m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            go = int(m.ullTotalPhys) // 1024 ** 3
        else:
            go = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") // 1024 ** 3
    except Exception:
        pass
    apple = platform.system() == "Darwin" and platform.machine() == "arm64"
    puce = "apple" if apple else platform.machine()
    if (apple and go >= 16) or (coeurs >= 8 and go >= 16 and platform.system() != "Darwin"):
        puissance = "forte"
    elif go <= 8 or coeurs <= 4 or (platform.system() == "Darwin" and not apple):   # tout Mac Intel est modeste pour la vidéo
        puissance = "faible"
    else:
        puissance = "moyenne"
    d.update({"coeurs": coeurs, "ram_go": go, "puce": puce, "puissance": puissance, "profil_v": 2})
    if cfg.exists():
        cfg.write_text(json.dumps(d, indent=1), encoding="utf-8")
    return d


ENCODEURS_MATERIELS = ["h264_videotoolbox", "h264_nvenc", "h264_qsv", "h264_amf"]   # Mac, NVIDIA, Intel, AMD


def detecter_encodeur():
    """Premier encodeur matériel qui marche vraiment (test d'un clip de 0,3 s), sinon x264 logiciel."""
    for e in ENCODEURS_MATERIELS:
        r = subprocess.run([ffmpeg(), "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=320x240:d=0.3", "-pix_fmt", "yuv420p",
                            "-c:v", e, "-f", "null", "-"], capture_output=True)
        if r.returncode == 0:
            return e
    return "libx264"


def encodeur():
    cfg = RACINE / "config-machine.json"
    d = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
    if "encodeur" not in d:
        d["encodeur"] = detecter_encodeur()
        if cfg.exists():
            cfg.write_text(json.dumps(d, indent=1), encoding="utf-8")
    return d["encodeur"]


def args_encodeur(crf=16):
    """Options ffmpeg du codec vidéo H.264 : encodeur matériel de l'ordinateur (4 à 5 fois plus rapide en 4K)
    ou x264 logiciel. crf = qualité voulue en échelle x264 (13 quasi sans perte, 16 livraison, 23 brouillon)."""
    e = encodeur()
    if e == "h264_videotoolbox":
        q = 78 if crf <= 14 else (70 if crf <= 18 else 58)
        return ["-c:v", e, "-q:v", str(q), "-profile:v", "high", "-allow_sw", "1"]
    if e == "h264_nvenc":
        return ["-c:v", e, "-preset", "p5", "-rc", "vbr", "-cq", str(crf + 2), "-b:v", "0", "-profile:v", "high"]
    if e == "h264_qsv":
        return ["-c:v", e, "-global_quality", str(crf + 4), "-preset", "medium"]
    if e == "h264_amf":
        return ["-c:v", e, "-quality", "quality", "-rc", "cqp", "-qp_i", str(crf), "-qp_p", str(crf + 2)]
    return ["-c:v", "libx264", "-preset", "veryfast" if crf <= 14 else "faster", "-crf", str(crf)]


def coeurs_rendu(k4=False):
    """Morceaux rendus en même temps (réplique). Mesuré le 15 oct 2026 : l'encodeur vidéo travaille déjà sur tous les cœurs,
    un deuxième processus n'apporte rien (4K : 58 s à 1, 65 s à 2). On garde donc un seul passage ; --coeurs N pour essayer autre chose."""
    return 1


def sortie_4k(projet):
    """True si la vidéo finale doit sortir en 4K (2160x3840 en vertical, 3840x2160 en YouTube)."""
    return reglages_projet(projet).get("sortie") == "4k"


def dimensions_sortie(projet):
    l, h = dimensions_format(format_projet(projet))
    return (l * 2, h * 2) if sortie_4k(projet) else (l, h)


def npx():
    n = shutil.which("npx") or shutil.which("npx.cmd")
    if not n:
        sys.exit("Node.js introuvable. Lance l'installation : python moteur/installer.py")
    return n


HYPERFRAMES = "hyperframes@0.8.96"


def env_node():
    e = dict(os.environ)
    chemins = [str(RACINE / "bin")]
    f = trouver("ffmpeg")
    if f:
        chemins.append(str(Path(f).parent))
    e["PATH"] = os.pathsep.join(chemins) + os.pathsep + e.get("PATH", "")
    cache = Path.home() / ".montagia" / "npm-cache"
    cache.mkdir(parents=True, exist_ok=True)
    e["npm_config_cache"] = str(cache)
    return e
