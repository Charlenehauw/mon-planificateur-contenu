#!/usr/bin/env python3
"""Mode réplique, étape 1 : analyser un reel de référence (« monte exactement comme cette vidéo »).

Usage :
  python moteur/reference.py <projet> <lien Instagram/TikTok/YouTube ou fichier vidéo> [--extrait 612-648]
                                                                      (--extrait : seulement ce passage d'une vidéo longue, en secondes)
  python moteur/reference.py animation <projet> <debut>-<fin> [--video fichier]
                                                                      une animation image par image (bande + mouvement.json + relevé)
  python moteur/reference.py couleurs <image> <x0> <y0> <x1> <y1>      couleurs dominantes d'une zone
  python moteur/reference.py polices <projet> "<texte>" [--image img --zone x0,y0,x1,y1]
                                                                      planche de polices candidates
Sort dans <projet>/reference/ :
  reference.mp4, legende.txt, planche-01.jpg… (2 images par seconde), images/ (images en grand),
  mots-reference.json et texte-reference.txt (ce qui est dit, mot à mot), analyse.md (le relevé à lire).
Tout est local et gratuit : yt-dlp pour télécharger, ffmpeg, faster-whisper, OpenCV.
"""
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import RACINE, WINDOWS, ffmpeg, run, ecrire_json, dimensions, duree

POLICES_CACHE = RACINE / ".outils" / "polices"
GOOGLE = "https://github.com/google/fonts/raw/main/ofl/"
# polices gratuites (licence OFL) téléchargées à la demande
POLICES_GOOGLE = {
    "Inter": "inter/Inter%5Bopsz,wght%5D.ttf",
    "Montserrat": "montserrat/Montserrat%5Bwght%5D.ttf",
    "Poppins Bold": "poppins/Poppins-Bold.ttf",
    "DM Sans": "dmsans/DMSans%5Bopsz,wght%5D.ttf",
    "Sora": "sora/Sora%5Bwght%5D.ttf",
    "Archivo Black": "archivoblack/ArchivoBlack-Regular.ttf",
    "Anton": "anton/Anton-Regular.ttf",
    "Bebas Neue": "bebasneue/BebasNeue-Regular.ttf",
    "Playfair Display Italic": "playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf",
    "Bodoni Moda Italic": "bodonimoda/BodoniModa-Italic%5Bopsz,wght%5D.ttf",
    "DM Serif Display Italic": "dmserifdisplay/DMSerifDisplay-Italic.ttf",
    "Instrument Serif Italic": "instrumentserif/InstrumentSerif-Italic.ttf",
    "Cormorant Garamond Italic": "cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf",
    "Libre Bodoni Italic": "librebodoni/LibreBodoni-Italic%5Bwght%5D.ttf",
}
# polices déjà présentes sur l'ordinateur (fichier, style)
POLICES_SYSTEME_MAC = [("HelveticaNeue.ttc", "Bold"), ("HelveticaNeue.ttc", "Medium"), ("Helvetica.ttc", "Bold"),
                       ("Avenir Next.ttc", "Bold"), ("Futura.ttc", "Medium"), ("Arial Bold.ttf", None),
                       ("Didot.ttc", "Italic"), ("Bodoni 72.ttc", "Book Italic"), ("Georgia Bold Italic.ttf", None)]
POLICES_SYSTEME_WIN = [("arialbd.ttf", None), ("segoeuib.ttf", None), ("georgiaz.ttf", None), ("timesbi.ttf", None)]


def dossiers_polices():
    if WINDOWS:
        return [Path("C:/Windows/Fonts"), Path.home() / "AppData/Local/Microsoft/Windows/Fonts"]
    return [Path("/System/Library/Fonts"), Path("/System/Library/Fonts/Supplemental"), Path("/Library/Fonts"),
            Path.home() / "Library/Fonts"]


def trouver_police(fichier):
    for d in [POLICES_CACHE] + dossiers_polices():
        if (d / fichier).exists():
            return d / fichier
    return None


def police_google(nom):
    """Télécharge (une fois) une police Google Fonts dans systeme/.outils/polices/ et renvoie son chemin."""
    POLICES_CACHE.mkdir(parents=True, exist_ok=True)
    chemin = POLICES_GOOGLE[nom]
    f = POLICES_CACHE / urllib.parse.unquote(chemin.split("/")[-1])
    if not f.exists():
        urllib.request.urlretrieve(GOOGLE + chemin, f)
    return f


# ---------------------------------------------------------------- analyse d'un reel
def telecharger(source, dossier, extrait=None):
    """Télécharge (ou copie) la vidéo modèle. extrait = (debut, fin) en secondes pour ne prendre qu'un passage
    d'une vidéo longue (YouTube) : yt-dlp ne télécharge que ce morceau."""
    cible = dossier / "reference.mp4"
    if Path(source).expanduser().exists():
        if extrait:
            run([ffmpeg(), "-y", "-v", "error", "-ss", str(extrait[0]), "-to", str(extrait[1]), "-i", str(Path(source).expanduser()),
                 "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-c:a", "aac", cible])
        else:
            shutil.copy(Path(source).expanduser(), cible)
        return cible, ""
    from qualite import chemin_ytdlp
    exe = chemin_ytdlp()
    # le programme yt-dlp autonome (à jour) avec Node comme moteur JavaScript : YouTube jusqu'en 1080p.
    # Sans lui, le paquet pip (figé en 2025 par Python 3.9) ne sort YouTube qu'en 360p via le client android.
    base = ([str(exe), "--js-runtimes", "node", "--remote-components", "ejs:github"] if exe else [sys.executable, "-m", "yt_dlp"])
    base += ["-f", "bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4]/b", "--merge-output-format", "mp4",
             "--no-playlist", "--write-info-json", "--ffmpeg-location", str(Path(ffmpeg()).parent), "-o", str(dossier / "reference.%(ext)s")]
    if extrait:
        base += ["--download-sections", f"*{extrait[0]}-{extrait[1]}", "--force-keyframes-at-cuts"]
    # Instagram veut la session Chrome ; YouTube refuse parfois le client web (« The page needs to be reloaded »), le client android passe
    essais = [base + ["--cookies-from-browser", "chrome", source],
              base + ["--extractor-args", "youtube:player_client=android,web", source],
              base + [source]]
    for cmd in essais:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if cible.exists():
            break
    if not cible.exists():
        sys.exit("Téléchargement impossible. Instagram demande parfois d'être connecté dans Chrome. "
                 "Sinon, enregistre la vidéo et donne le fichier.\n" + (r.stdout + r.stderr)[-800:])
    legende = ""
    info = dossier / "reference.info.json"
    if info.exists():
        d = json.loads(info.read_text(encoding="utf-8"))
        legende = f"Compte : {d.get('uploader') or d.get('channel') or ''}\n\n{d.get('description') or ''}"
        info.unlink()
    return cible, legende


def coupes_franches(video):
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(video), "-vf", "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace")
    import re
    return [round(float(x), 2) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def cartons_pleins(video, d):
    """Passages plein écran d'une seule couleur (cartons de texte) : [(debut, fin, '#RRGGBB')]."""
    from PIL import Image
    tmp = d / "_cartons"
    shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
    run([ffmpeg(), "-v", "error", "-i", video, "-vf", "fps=8,scale=72:128", str(tmp / "%05d.png")])
    res, cur = [], None
    for i, f in enumerate(sorted(tmp.glob("*.png"))):
        im = Image.open(f).convert("RGB")
        pts = [im.getpixel((x, y)) for x in (3, 36, 68) for y in (4, 30, 64, 98, 124) if not (x == 36 and y in (30, 64, 98))]
        moy = tuple(sum(p[k] for p in pts) // len(pts) for k in range(3))
        uni = all(sum(abs(p[k] - moy[k]) for k in range(3)) < 24 for p in pts)
        t = i / 8
        if uni:
            hexa = "#%02X%02X%02X" % moy
            if cur and t - cur[1] <= 0.13 and sum(abs(a - b) for a, b in zip(cur[3], moy)) < 30:
                cur[1] = t + 0.125
            else:
                if cur:
                    res.append(cur)
                cur = [t, t + 0.125, hexa, moy]
        elif cur and t - cur[1] > 0.13:
            res.append(cur); cur = None
    if cur:
        res.append(cur)
    shutil.rmtree(tmp, ignore_errors=True)
    return [(round(a, 2), round(b, 2), c) for a, b, c, _ in res if b - a >= 0.25]


def taille_visage(video):
    """Largeur du visage (fraction de l'image) toutes les 0,5 s : repère les zooms et changements de plan."""
    try:
        from qualite import visage_dispo, suivre_visage
        if not visage_dispo():
            return []
        return [(round(t, 1), round(lv, 3)) for t, _, _, lv in suivre_visage(video, pas=0.5, lissage=0.25)]
    except Exception:
        return []


def transcrire(video, d):
    from faster_whisper import WhisperModel
    m = WhisperModel("large-v3-turbo", device="auto", compute_type="auto")
    segs, _ = m.transcribe(str(video), language="fr", word_timestamps=True, vad_filter=True)
    mots, lignes = [], []
    for s in segs:
        lignes.append(f"{s.start:6.2f}  {s.text.strip()}")
        mots += [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]
    ecrire_json(d / "mots-reference.json", mots)
    (d / "texte-reference.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return mots


def dits_entre(mots, a, b):
    return " ".join(m["w"] for m in mots if m["s"] < b and m["e"] > a)


def analyser(projet, source, extrait=None):
    d = Path(projet) / "reference"
    d.mkdir(parents=True, exist_ok=True)
    (d / "images").mkdir(exist_ok=True)
    video, legende = telecharger(source, d, extrait)
    if legende:
        (d / "legende.txt").write_text(legende, encoding="utf-8")
    w, h = dimensions(video)
    dur = duree(video)
    print(f"Référence : {w}x{h}, {dur:.1f} s. Planches, coupes, cartons, transcription…", flush=True)
    for f in d.glob("planche-*.jpg"):
        f.unlink()
    run([ffmpeg(), "-v", "error", "-i", video, "-vf", "fps=2,scale=180:-2,tile=10x6", str(d / "planche-%02d.jpg")])
    coupes = coupes_franches(video)
    cartons = cartons_pleins(video, d)
    visage = taille_visage(video)
    mots = transcrire(video, d)
    # images en grand : chaque carton (milieu et fin), puis un plan toutes les ~6 s pour étudier les sous-titres
    for i, (a, b, _) in enumerate(cartons):
        for nom, t in (("milieu", (a + b) / 2), ("fin", b - 0.1)):
            run([ffmpeg(), "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", str(d / "images" / f"carton-{i + 1:02d}-{nom}.png")])
    n_plans = max(6, int(dur // 6))
    for i in range(n_plans):
        t = dur * (i + 0.5) / n_plans
        run([ffmpeg(), "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", str(d / "images" / f"plan-{i + 1:02d}-{t:05.1f}s.png")])
    # zooms : sauts de taille du visage de plus de 8 %
    zooms = []
    for (t0, a), (t1, b) in zip(visage, visage[1:]):
        if a and b and abs(b - a) / a > 0.08:
            zooms.append((t1, round(b / a, 2)))
    L = [f"# Analyse du reel de référence", "",
         f"- Fichier : reference.mp4 ({w}x{h}, {dur:.1f} s)",
         f"- Planches à regarder (2 images par seconde, 30 s par planche) : " + ", ".join(sorted(p.name for p in d.glob("planche-*.jpg"))),
         f"- Images en grand : dossier images/ (cartons et plans réguliers)", "",
         "## Coupes franches (changement de plan net)", ""]
    L += [f"- {t:.2f} s : « {dits_entre(mots, t - 0.3, t + 0.6)} »" for t in coupes] or ["- aucune"]
    L += ["", "## Cartons plein écran d'une seule couleur", ""]
    L += [f"- {a:.2f} à {b:.2f} s ({b - a:.1f} s), fond {c} : pendant « {dits_entre(mots, a, b)} »" for a, b, c in cartons] or ["- aucun"]
    L += ["", "## Changements de taille du visage (zooms, autre prise)", ""]
    L += [f"- {t:.1f} s : x{r}" for t, r in zooms] or ["- aucun (cadre fixe)"]
    L += ["", "## Ce qui est dit (mot à mot dans mots-reference.json)", "", "```", (d / "texte-reference.txt").read_text(encoding="utf-8").strip(), "```", "",
          "## À relever toi-même en regardant les planches et les images en grand", "",
          "1. Sous-titres : combien de mots à la fois, position (y), police, graisse, couleur, ombre ou contour, animation d'entrée (coupe sèche, pop, fondu).",
          "2. Mots clés : police, couleur exacte (`reference.py couleurs`), taille, halo, comment ils s'empilent avec les petits mots.",
          "3. Cartons : couleur de fond (ci-dessus), police et couleur du texte, ombre, durée, mots qui s'ajoutent un par un ou non.",
          "4. Transitions : coupes sèches ou fondus, zooms, plans de coupe (B-roll).",
          "5. Ce qu'il n'y a PAS : pas de titre en haut ? pas de bouton d'appel à l'action ? Alors n'en mets pas.",
          "6. Polices : `python systeme/montagia.py polices <projet> \"mot\" --image <image> --zone x0,y0,x1,y1` pour comparer côte à côte."]
    (d / "analyse.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    ecrire_json(d / "analyse.json", {"largeur": w, "hauteur": h, "duree": dur, "coupes": coupes,
                                     "cartons": [{"debut": a, "fin": b, "couleur": c} for a, b, c in cartons], "zooms": zooms})
    print(f"OK : analyse dans {d / 'analyse.md'} ({len(coupes)} coupes, {len(cartons)} cartons, {len(mots)} mots)")


# ---------------------------------------------------------------- une animation, image par image
def animation(projet, debut, fin, video=None):
    """Décortique un passage court (0,3 à 6 s) de la vidéo modèle : chaque image à la cadence d'origine,
    une bande (strip) pour voir le mouvement d'un coup d'œil, et le relevé du mouvement des zones qui bougent
    (ce qui change entre deux images = le texte ou l'élément animé). Sort dans reference/animations/<debut>-<fin>/."""
    from PIL import Image, ImageChops, ImageDraw
    d = Path(projet) / "reference"
    video = Path(video) if video else d / "reference.mp4"
    if not video.exists():
        sys.exit(f"Vidéo modèle introuvable : {video}. Lance d'abord : montagia.py reference <projet> <lien>")
    fin = min(fin, debut + 6.0)
    out = d / "animations" / f"{debut:05.2f}-{fin:05.2f}"
    shutil.rmtree(out, ignore_errors=True)
    (out / "images").mkdir(parents=True)
    r = subprocess.run([ffmpeg(), "-i", str(video)], capture_output=True, text=True, errors="replace").stderr
    import re
    m = re.search(r"(\d+(?:\.\d+)?) fps", r)
    fps = float(m.group(1)) if m else 30.0
    run([ffmpeg(), "-y", "-v", "error", "-ss", f"{debut:.3f}", "-to", f"{fin:.3f}", "-i", video, "-vsync", "0", str(out / "images" / "%04d.png")])
    frames = sorted((out / "images").glob("*.png"))
    if len(frames) < 2:
        sys.exit("Passage trop court, élargis-le.")
    W, H = Image.open(frames[0]).size
    # mouvement : zone qui change par rapport à l'image précédente et par rapport à la première image
    import numpy as np

    def zone_dense(diff, seuil=80, part=0.03):
        """Boîte des pixels qui changent franchement (texte, forme), en ignorant le bruit et le léger mouvement de la caméra :
        on garde la zone où vivent 94 % des pixels changés, et seulement si assez de pixels changent."""
        a = np.asarray(diff) > seuil
        ys, xs = np.nonzero(a)
        if len(xs) < 80:
            return None
        return [int(np.percentile(xs, 3)), int(np.percentile(ys, 3)), int(np.percentile(xs, 97)), int(np.percentile(ys, 97))]
    prev = None
    base = Image.open(frames[0]).convert("L")
    rel = []
    for i, f in enumerate(frames):
        im = Image.open(f).convert("L")
        t = debut + i / fps
        bb_prev = zone_dense(ImageChops.difference(im, prev)) if prev is not None else None
        bb_base = zone_dense(ImageChops.difference(im, base))
        rel.append({"image": i + 1, "t": round(t, 3), "change_vs_precedente": bb_prev, "change_vs_premiere": bb_base})
        prev = im
    ecrire_json(out / "mouvement.json", {"fps": fps, "largeur": W, "hauteur": H, "images": rel})
    # bande : jusqu'à 24 images, redimensionnées, avec le temps écrit dessous
    n = len(frames)
    pas = max(1, n // 24)
    choisies = frames[::pas][:24]
    vignette_h = 480
    vignette_w = int(W * vignette_h / H)
    cols = min(8, len(choisies))
    rows = -(-len(choisies) // cols)
    bande = Image.new("RGB", (cols * vignette_w, rows * (vignette_h + 22)), (20, 20, 20))
    dr = ImageDraw.Draw(bande)
    for k, f in enumerate(choisies):
        im = Image.open(f).convert("RGB").resize((vignette_w, vignette_h))
        x, y = (k % cols) * vignette_w, (k // cols) * (vignette_h + 22)
        bande.paste(im, (x, y))
        idx = frames.index(f)
        dr.text((x + 4, y + vignette_h + 4), f"#{idx + 1}  t={debut + idx / fps:.2f}s", fill=(255, 220, 120))
    bande.save(out / "bande.jpg", quality=88)
    # résumé lisible : quand ça bouge, quand ça s'arrête, dans quelle zone
    actifs = [x for x in rel if x["change_vs_precedente"]]
    zone = None
    for x in rel:
        b = x["change_vs_premiere"]
        if b:
            zone = b if zone is None else (min(zone[0], b[0]), min(zone[1], b[1]), max(zone[2], b[2]), max(zone[3], b[3]))
    L = [f"# Animation de {debut:.2f} à {fin:.2f} s ({n} images à {fps:g} i/s, {W}x{H})", "",
         f"- Bande à regarder : {out / 'bande.jpg'} ; chaque image dans images/ (#numéro = colonne « image » de mouvement.json).",
         f"- Zone qui bouge (x0, y0, x1, y1) : {zone}" if zone else "- Rien ne bouge par rapport à la première image.",
         f"- Images où quelque chose change : {len(actifs)} sur {n}"
         + (f" (de #{actifs[0]['image']} à #{actifs[-1]['image']}, soit {actifs[0]['t']:.2f} à {actifs[-1]['t']:.2f} s)" if actifs else ""), "",
         "## À relever en regardant la bande", "",
         "1. Quoi : texte, forme, image, zoom de la vidéo elle-même ? Combien d'éléments ?",
         "2. Entrée : d'où ça vient (bas, gauche, du centre en grossissant, fondu), en combien d'images, et la courbe (démarre vite puis freine = ease-out ; rebond = overshoot).",
         "3. Tenue : combien de temps l'élément reste fixe, est-ce qu'il bouge un peu pendant (dérive, pulsation).",
         "4. Sortie : fondu, glissement, coupe sèche, ou remplacé par le suivant.",
         "5. Style : police, taille, couleur, ombre, halo, fond (mesure avec `couleurs` et `polices`).",
         "6. Son : y a-t-il un bruitage calé dessus (écoute le passage).",
         "Écris ces réponses noir sur blanc avant de reproduire : c'est ta fiche de l'animation (section 3 quinquies de la skill)."]
    (out / "releve.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"OK : {out / 'bande.jpg'} ({n} images), relevé dans {out / 'releve.md'}")


# ---------------------------------------------------------------- outils de relevé
def couleurs(image, x0, y0, x1, y1, n=8):
    from PIL import Image
    im = Image.open(image).convert("RGB").crop((x0, y0, x1, y1))
    c = Counter((r // 6 * 6, g // 6 * 6, b // 6 * 6) for r, g, b in im.getdata())
    tot = sum(c.values())
    for (r, g, b), v in c.most_common(n):
        print(f"#{r:02X}{g:02X}{b:02X}  {100 * v / tot:5.1f} %")


def planche_polices(projet, texte, image=None, zone=None):
    from PIL import Image, ImageDraw, ImageFont
    cands = []
    for f, st in (POLICES_SYSTEME_WIN if WINDOWS else POLICES_SYSTEME_MAC):
        p = trouver_police(f)
        if p:
            cands.append((f"{f}{' ' + st if st else ''}", p, st))
    for nom in POLICES_GOOGLE:
        try:
            cands.append((nom + " (Google)", police_google(nom), None))
        except Exception:
            pass
    haut = 110
    ref = None
    if image:
        ref = Image.open(image).convert("RGB")
        if zone:
            ref = ref.crop(zone)
        ref.thumbnail((700, 400))
    im = Image.new("RGB", (1500, haut * len(cands) + 20), (245, 245, 245))
    d = ImageDraw.Draw(im)
    pet = ImageFont.load_default()
    for i, (nom, p, st) in enumerate(cands):
        variable = "[" in p.name                   # police variable : montrée en gras (700), comme dans la plupart des reels
        f = charger(p, 72, st or ("Bold" if variable else None))
        d.text((10, i * haut + 10), texte, font=f, fill=(20, 20, 20))
        d.text((10, i * haut + 88), nom + (" (graisse 700)" if variable else ""), font=pet, fill=(120, 0, 0))
    if ref:
        im.paste(ref, (1500 - ref.width - 10, 10))
    sortie = Path(projet) / "reference" / "planche-polices.png"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    print(f"OK : {sortie} (le nom de chaque police est écrit sous l'exemple)")


def charger(chemin, taille, style=None, axes=None):
    """Police Pillow : style = sous-famille dans un .ttc (« Bold »), axes = {"Weight": 700} pour une police variable."""
    from PIL import ImageFont
    chemin = str(chemin)
    if chemin.lower().endswith(".ttc") and style:
        for i in range(20):
            try:
                f = ImageFont.truetype(chemin, taille, index=i)
            except Exception:
                break
            if f.getname()[1].lower() == style.lower():
                return f
    f = ImageFont.truetype(chemin, taille)
    try:
        ax = f.get_variation_axes()
        noms = [a["name"].decode() if isinstance(a["name"], bytes) else a["name"] for a in ax]
        voulu = dict(axes or {})
        if style and not axes and "Weight" in noms:
            voulu["Weight"] = {"bold": 700, "black": 900, "medium": 500, "semibold": 600}.get(style.lower(), 400)
        if voulu:
            f.set_variation_by_axes([voulu.get(n, a["default"]) for n, a in zip(noms, ax)])
    except Exception:
        pass
    return f


def main():
    if len(sys.argv) < 3:
        print(__doc__); return
    if sys.argv[1] == "animation":
        video = sys.argv[sys.argv.index("--video") + 1] if "--video" in sys.argv else None
        a, b = sys.argv[3].split("-") if "-" in sys.argv[3] else (sys.argv[3], sys.argv[4])
        animation(sys.argv[2], float(a), float(b), video); return
    if sys.argv[1] == "couleurs":
        couleurs(sys.argv[2], *map(int, sys.argv[3:7])); return
    if sys.argv[1] == "polices":
        img = sys.argv[sys.argv.index("--image") + 1] if "--image" in sys.argv else None
        zone = tuple(map(int, sys.argv[sys.argv.index("--zone") + 1].split(","))) if "--zone" in sys.argv else None
        planche_polices(sys.argv[2], sys.argv[3], img, zone); return
    extrait = None
    if "--extrait" in sys.argv:
        a, b = sys.argv[sys.argv.index("--extrait") + 1].split("-")
        extrait = (float(a), float(b))
    analyser(sys.argv[1], sys.argv[2], extrait)


if __name__ == "__main__":
    main()
