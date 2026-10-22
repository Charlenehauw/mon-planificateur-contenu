"""Qualité premium de Montag'IA : cadrage qui suit le visage, voix IA, agrandissement IA (4K).

Tout tourne sur l'ordinateur, gratuitement, sans compte en ligne, et le plus léger possible :
  - visage   : sur Mac, le détecteur Vision d'Apple (déjà dans le système, via pyobjc, 16 Mo) ;
               sur Windows et Linux, YuNet d'OpenCV (modèle dans systeme/.outils/modeles/)
  - voix IA  : DeepFilterNet, programme autonome deep-filter (27 Mo, sans PyTorch), bien plus propre que les
               filtres classiques sur un son de téléphone ou de WhatsApp déjà compressé
  - image IA : Real-ESRGAN (realesrgan-ncnn-vulkan), téléchargé seulement la première fois qu'on en a besoin,
               agrandit x4 une vidéo trop petite (WhatsApp 480 px) en recréant les détails au lieu de l'étirer.
Si un outil manque, Montag'IA retombe sur la méthode classique et le dit.
Un outil déjà présent sur l'ordinateur (PATH, ~/.clipping-tools, Homebrew) est utilisé tel quel.
"""
import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from outils import RACINE, WINDOWS, ffmpeg, lire_json, run, args_encodeur

MAC = platform.system() == "Darwin"
OUTILS = RACINE / ".outils"
MODELE_VISAGE = OUTILS / "modeles" / "face_detection_yunet_2023mar.onnx"
URL_MODELE_VISAGE = ("https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/"
                     "face_detection_yunet/face_detection_yunet_2023mar.onnx")
ESRGAN_EXE = "realesrgan-ncnn-vulkan" + (".exe" if WINDOWS else "")
URL_ESRGAN = {
    "mac": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-macos.zip",
    "windows": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip",
    "linux": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip",
}
DEEPFILTER_EXE = OUTILS / "deep-filter" / ("deep-filter.exe" if WINDOWS else "deep-filter")
_DF = "https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/deep-filter-0.5.6-"
URL_DEEPFILTER = {
    ("Darwin", "arm64"): _DF + "aarch64-apple-darwin",
    ("Darwin", "x86_64"): _DF + "x86_64-apple-darwin",
    ("Windows", "AMD64"): _DF + "x86_64-pc-windows-msvc.exe",
    ("Linux", "x86_64"): _DF + "x86_64-unknown-linux-musl",
    ("Linux", "aarch64"): _DF + "aarch64-unknown-linux-gnu",
}

# Après le débruitage IA, une finition légère : on ne « sculpte » plus la voix (c'est ce qui la faisait grésiller).
FINITION_VOIX_IA = ("highpass=f=70,deesser=i=0.25,"
                    "acompressor=threshold=-20dB:ratio=2:attack=15:release=150:makeup=2,"
                    "loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89")


def machine():
    f = RACINE / "config-machine.json"
    return lire_json(f) if f.exists() else {}


def noter_machine(**cles):
    cfg = RACINE / "config-machine.json"
    if cfg.exists():
        d = lire_json(cfg); d.update(cles)
        cfg.write_text(json.dumps(d, indent=1), encoding="utf-8")


def sans_quarantaine(exe):
    if not WINDOWS:
        os.chmod(exe, 0o755)
        subprocess.run(["xattr", "-d", "com.apple.quarantine", str(exe)], capture_output=True)


# ---------------------------------------------------------------- outils disponibles
def chemin_esrgan():
    """Real-ESRGAN : config, dossier Montag'IA, PATH, ~/.clipping-tools. None s'il n'existe nulle part."""
    cands = []
    m = machine().get("upscale_ia")
    if m:
        cands.append(Path(m))
    cands += [OUTILS / "realesrgan" / ESRGAN_EXE, Path.home() / ".clipping-tools" / "realesrgan" / ESRGAN_EXE]
    w = shutil.which("realesrgan-ncnn-vulkan")
    if w:
        cands.append(Path(w))
    for c in cands:
        if c.exists() and (c.parent / "models").exists():
            return c
    return None


def installer_esrgan():
    """Télécharge Real-ESRGAN (50 Mo, version officielle GitHub) dans systeme/.outils/realesrgan/. Appelé à la première
    demande d'agrandissement IA, pas à l'installation : la plupart des vidéos n'en ont pas besoin."""
    import urllib.request
    import zipfile
    dossier = OUTILS / "realesrgan"
    dossier.mkdir(parents=True, exist_ok=True)
    z = dossier / "realesrgan.zip"
    print("Téléchargement de Real-ESRGAN (50 Mo, une seule fois)…", flush=True)
    urllib.request.urlretrieve(URL_ESRGAN["mac" if MAC else ("windows" if WINDOWS else "linux")], z)
    with zipfile.ZipFile(z) as f:
        f.extractall(dossier)
    z.unlink()
    for inutile in ("input.jpg", "input2.jpg", "onepiece_demo.mp4"):
        (dossier / inutile).unlink(missing_ok=True)
    exe = dossier / ESRGAN_EXE
    sans_quarantaine(exe)
    noter_machine(upscale_ia=str(exe))
    return exe


def chemin_deepfilter():
    cands = []
    m = machine().get("deep_filter")
    if m:
        cands.append(Path(m))
    cands.append(DEEPFILTER_EXE)
    w = shutil.which("deep-filter")
    if w:
        cands.append(Path(w))
    for c in cands:
        if c.exists():
            return c
    return None


def installer_deepfilter():
    """Télécharge le programme deep-filter (27 Mo, version officielle GitHub) pour cet ordinateur. None si pas de version."""
    import urllib.request
    url = URL_DEEPFILTER.get((platform.system(), platform.machine()))
    if not url:
        return None
    DEEPFILTER_EXE.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, DEEPFILTER_EXE)
    sans_quarantaine(DEEPFILTER_EXE)
    test = subprocess.run([str(DEEPFILTER_EXE), "--help"], capture_output=True, text=True, errors="replace")
    if "deep filtering" not in (test.stdout + test.stderr).lower():
        DEEPFILTER_EXE.unlink(missing_ok=True)
        return None
    noter_machine(deep_filter=str(DEEPFILTER_EXE))
    return DEEPFILTER_EXE


YTDLP_EXE = OUTILS / "yt-dlp" / ("yt-dlp.exe" if WINDOWS else "yt-dlp")
URL_YTDLP = {"Darwin": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos",
             "Windows": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
             "Linux": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"}


def chemin_ytdlp():
    """Programme yt-dlp autonome (37 Mo, Python récent embarqué) : il suit YouTube et Instagram bien mieux que le paquet pip
    figé par le Python 3.9 d'Apple. Sinon None (on retombe sur le paquet pip)."""
    for c in [YTDLP_EXE] + ([Path(w)] if (w := shutil.which("yt-dlp")) else []):
        if c.exists():
            return c
    return None


def installer_ytdlp():
    import urllib.request
    url = URL_YTDLP.get(platform.system())
    if not url:
        return None
    YTDLP_EXE.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, YTDLP_EXE)
    sans_quarantaine(YTDLP_EXE)
    test = subprocess.run([str(YTDLP_EXE), "--version"], capture_output=True, text=True, errors="replace")
    if test.returncode != 0:
        YTDLP_EXE.unlink(missing_ok=True)
        return None
    noter_machine(yt_dlp=str(YTDLP_EXE))
    return YTDLP_EXE


def voix_ia_dispo():
    if chemin_deepfilter():
        return True
    try:
        import df  # noqa: F401  (ancienne installation avec PyTorch, toujours acceptée)
        return True
    except Exception:
        return False


def vision_dispo():
    if not MAC:
        return False
    try:
        import Quartz  # noqa: F401
        import Vision  # noqa: F401  (pyobjc)
        return True
    except Exception:
        return False


def visage_dispo():
    if vision_dispo():
        return True
    try:
        import cv2
        return MODELE_VISAGE.exists() and hasattr(cv2, "FaceDetectorYN")
    except Exception:
        return False


# ---------------------------------------------------------------- visage
def _points_vision(video, pas):
    """Mac : images extraites par ffmpeg puis détecteur Vision d'Apple (environ 10 ms par image)."""
    import Quartz
    import Vision
    from Foundation import NSURL
    pts = []
    with tempfile.TemporaryDirectory() as tmp:
        run([ffmpeg(), "-v", "error", "-i", video, "-vf", f"fps=1/{pas},scale=min(640\\,iw):-2", str(Path(tmp) / "%05d.jpg")])
        req = Vision.VNDetectFaceRectanglesRequest.alloc().init()
        for i, f in enumerate(sorted(Path(tmp).glob("*.jpg"))):
            src = Quartz.CGImageSourceCreateWithURL(NSURL.fileURLWithPath_(str(f)), None)
            img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None) if src else None
            faces = []
            if img is not None:
                h = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
                h.performRequests_error_([req], None)
                faces = list(req.results() or [])
            if faces:
                b = max(faces, key=lambda r: r.boundingBox().size.width).boundingBox()
                # Vision compte y depuis le bas de l'image
                pts.append((i * pas, b.origin.x + b.size.width / 2, 1 - (b.origin.y + b.size.height / 2), b.size.width))
            else:
                pts.append((i * pas, None, None, None))
    return pts


def _points_opencv(video, pas):
    import cv2
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    echelle = min(1.0, 640 / max(W, H))
    w2, h2 = int(W * echelle), int(H * echelle)
    det = cv2.FaceDetectorYN.create(str(MODELE_VISAGE), "", (w2, h2), 0.7, 0.3, 50)
    saut = max(1, int(round(fps * pas)))
    points, i = [], 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if i % saut == 0:
            ok, img = cap.retrieve()
            if ok:
                if echelle < 1:
                    img = cv2.resize(img, (w2, h2))
                _, faces = det.detect(img)
                if faces is not None and len(faces):
                    f = max(faces, key=lambda r: r[2] * r[3])
                    points.append((i / fps, (f[0] + f[2] / 2) / w2, (f[1] + f[3] / 2) / h2, f[2] / w2))
                else:
                    points.append((i / fps, None, None, None))
        i += 1
    cap.release()
    return points


def suivre_visage(video, pas=0.2, lissage=1.5):
    """Centre du visage au fil du temps, en fraction de la largeur/hauteur de l'image.
    Retourne [(t, cx, cy, largeur_visage)] lissé sur ±lissage s, ou [] si aucun visage."""
    points = _points_vision(video, pas) if vision_dispo() else _points_opencv(video, pas)
    vus = [p for p in points if p[1] is not None]
    if len(vus) < max(3, len(points) * 0.2):
        return []
    # trous : on reprend la dernière position connue
    plein, der = [], vus[0]
    for p in points:
        der = p if p[1] is not None else (p[0], der[1], der[2], der[3])
        plein.append(der)
    n = max(1, int(lissage / pas))
    lisse = []
    for k, (t, _, _, _) in enumerate(plein):
        fen = plein[max(0, k - n):k + n + 1]
        lisse.append((t, sum(p[1] for p in fen) / len(fen), sum(p[2] for p in fen) / len(fen), sum(p[3] for p in fen) / len(fen)))
    return lisse


def commandes_recadrage(piste, largeur_mise_a_l_echelle, largeur_sortie, fichier):
    """Écrit le fichier sendcmd qui fait glisser le recadrage 9:16 pour garder le visage au centre."""
    marge = largeur_mise_a_l_echelle - largeur_sortie
    with open(fichier, "w", encoding="utf-8") as f:
        for t, cx, _, _ in piste:
            x = min(marge, max(0, cx * largeur_mise_a_l_echelle - largeur_sortie / 2))
            f.write(f"{t:.2f} crop x {int(round(x))};\n")
    return sum(min(marge, max(0, p[1] * largeur_mise_a_l_echelle - largeur_sortie / 2)) for p in piste) / len(piste)


# ---------------------------------------------------------------- voix IA
def voix_ia(entree_wav, sortie_wav, attenuation=35):
    """Débruitage IA DeepFilterNet. attenuation = dB maximum retirés au bruit (35 = net mais naturel,
    20 = léger, 100 = silence total entre les phrases). Puis finition douce et niveau Instagram."""
    exe = chemin_deepfilter()
    tmp = Path(sortie_wav).with_name("voix-ia-brute.wav")
    if exe:
        with tempfile.TemporaryDirectory() as d:
            # deep-filter veut du 48 kHz mono et écrit un fichier du même nom dans le dossier de sortie
            ent = Path(d) / "entree" / "voix.wav"
            ent.parent.mkdir()
            run([ffmpeg(), "-y", "-v", "error", "-i", entree_wav, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", ent])
            run([str(exe), "-a", str(attenuation), "--pf", "-o", d, str(ent)])
            shutil.copy(Path(d) / "voix.wav", tmp)
    else:
        from df.enhance import enhance, init_df, load_audio, save_audio
        err = os.dup(2); nul = os.open(os.devnull, os.O_WRONLY); os.dup2(nul, 2)
        try:
            modele, etat, _ = init_df(log_level="ERROR")
        finally:
            os.dup2(err, 2); os.close(nul); os.close(err)
        audio, _ = load_audio(str(entree_wav), sr=etat.sr())
        save_audio(str(tmp), enhance(modele, etat, audio, atten_lim_db=attenuation), etat.sr())
    run([ffmpeg(), "-y", "-v", "error", "-i", tmp, "-af", FINITION_VOIX_IA + ",aformat=channel_layouts=stereo",
         "-ar", "48000", sortie_wav])
    tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------- image IA
def agrandir_ia(video, sortie, dossier_travail, fps=30, crop=None):
    """Agrandit chaque image x4 avec Real-ESRGAN (modèle realesrgan-x4plus, le plus fidèle sur un visage).
    crop = (x, y, w, h) en pixels source pour ne traiter que la zone utile. Long : environ 2 s par image
    de 300x500 px sur un Mac M récent, donc près d'une heure par minute de vidéo. Toujours lancer en arrière-plan."""
    exe = chemin_esrgan() or installer_esrgan()
    ent, sor = Path(dossier_travail) / "ia-entree", Path(dossier_travail) / "ia-sortie"
    for d in (ent, sor):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    vf = (f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else "") + f"fps={fps}"
    run([ffmpeg(), "-y", "-v", "error", "-i", video, "-vf", vf, str(ent / "%06d.png")])
    n = len(list(ent.glob("*.png")))
    print(f"Agrandissement IA de {n} images (Real-ESRGAN x4)…", flush=True)
    t0 = time.time()
    p = subprocess.Popen([str(exe), "-i", str(ent), "-o", str(sor), "-n", "realesrgan-x4plus", "-m", str(exe.parent / "models"),
                          "-s", "4", "-f", "png"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    annonce = False
    while p.poll() is None:
        time.sleep(10)
        faits = len(list(sor.glob("*.png")))
        if faits >= 10 and not annonce:
            reste = (time.time() - t0) / faits * (n - faits)
            print(f"  environ {int(reste // 60)} min restantes", flush=True)
            annonce = True
    if p.returncode != 0 or len(list(sor.glob("*.png"))) < n:
        raise RuntimeError("Real-ESRGAN s'est arrêté avant la fin.")
    run([ffmpeg(), "-y", "-v", "error", "-framerate", str(fps), "-i", str(sor / "%06d.png"),
         "-pix_fmt", "yuv420p", *args_encodeur(10), sortie])
    shutil.rmtree(ent, ignore_errors=True)
    shutil.rmtree(sor, ignore_errors=True)
    print(f"  agrandissement IA terminé en {int((time.time() - t0) // 60)} min", flush=True)
