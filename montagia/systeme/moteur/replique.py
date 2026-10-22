#!/usr/bin/env python3
"""Mode réplique, étape 2 : monter la vidéo exactement dans le style d'un reel de référence.

Usage : python moteur/replique.py <projet> [--apercu 3.0,8.5,12.9]
Lit   : base.mp4 et mots.json (sortis de « preparer »), replique.json (écrit par Claude après l'analyse)
Sort  : final.mp4 (copié dans « Mes vidéos montées »), ou des images d'aperçu dans apercu-replique/

Ce moteur pose, image par image, ce que l'on voit dans la plupart des reels « éditoriaux » :
  - des sous-titres mot à mot (coupe sèche, comme dans la référence),
  - des blocs de phrase où les mots s'empilent (petits mots + mot clé dans une autre police, halo, ombre),
  - des cartons plein écran d'une couleur avec des mots qui s'ajoutent au fil de la voix,
  - des zooms secs (punch-in).
Toutes les positions sont dans le repère 1080 x 1920, même en 4K (le moteur double tout).

replique.json (exemple complet dans systeme/exemples/replique-exemple.json) :
{
 "polices": {"sans": {"fichier": "HelveticaNeue.ttc", "style": "Bold"},
             "serif": {"google": "Bodoni Moda Italic", "axes": {"Weight": 700, "Optical size": 28}}},
 "styles": {"sous_titre": {"police": "sans", "taille": 74, "couleur": "#FFFFFF", "ombre": ["#000000", 0.55, 7, 3]},
            "cle": {"police": "serif", "taille": 170, "couleur": "#E074F8", "ombre": ["#28003C", 0.5, 8, 4], "halo": ["#AA3CDC", 0.55, 14]}},
 "sous_titres": {"style": "sous_titre", "y": 1250, "tenue_max": 0.6, "max_caracteres": 11},
 "carton": {"couleur": "#EDC8FC", "y": 900},
 "blocs_y": 1250,
 "animation": {"rebond": 0.06, "avance": 0.035},
 "blocs": [
   {"type": "video", "fin": "@Comment", "lignes": [
       {"dx": -190, "mots": [["de la", "petit", "@de#2"]]},
       {"dx": 0, "chevauche": 0.16, "mots": [["répartie", "cle", "@répartie"]]}]},
   {"type": "carton", "debut": 29.52, "fin": "@Et#3", "lignes": [...]}],
 "zooms": [{"debut": "@Et#6", "echelle": 1.1, "y": 760}]
}
« dx » = décalage horizontal de la ligne depuis le centre, « chevauche » = part de la hauteur qui recouvre la ligne du dessus.
Ombre = [couleur, opacité, flou, décalage vers le bas]. Halo = [couleur, opacité, flou].
"""
import math
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import ffmpeg, lire_json, dimensions, duree, coeurs_rendu, args_encodeur
from composer import Temps
from reference import charger, trouver_police, police_google

FPS = 30


def hexa(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


class Replique:
    def __init__(self, projet):
        self.projet = Path(projet)
        self.R = lire_json(self.projet / "replique.json")
        self.mots = lire_json(self.projet / "mots.json")["mots"]
        self.duree = lire_json(self.projet / "mots.json")["duree"]
        self.W, self.H = dimensions(self.projet / "base.mp4")
        self.K = self.W / 1080
        self.t = Temps(self.mots)
        self._polices, self._cache = {}, {}
        self.preparer()

    # ---------- polices et styles
    def police(self, nom, taille):
        cle = (nom, taille)
        if cle not in self._polices:
            spec = self.R["polices"][nom]
            if spec.get("google"):
                chemin = police_google(spec["google"])
            else:
                chemin = Path(spec["fichier"])
                if not chemin.is_absolute():
                    chemin = (self.projet / spec["fichier"]) if (self.projet / spec["fichier"]).exists() else trouver_police(spec["fichier"])
                if not chemin:
                    sys.exit(f"Police introuvable : {spec['fichier']}")
            self._polices[cle] = charger(chemin, taille, spec.get("style"), spec.get("axes"))
        return self._polices[cle]

    def style(self, nom, echelle=1.0):
        s = self.R["styles"][nom]
        return s, self.police(s["police"], max(8, int(s["taille"] * self.K * echelle)))

    def encre(self, texte, nom, echelle=1.0):
        _, f = self.style(nom, echelle)
        l, t, r, b = f.getbbox(texte)
        return r - l, b - t

    def dessiner(self, calque, texte, nom, x, y, echelle=1.0):
        """x, y = coin haut-gauche de la boîte d'encre, en pixels de sortie."""
        s, f = self.style(nom, echelle)
        l, t, _, _ = f.getbbox(texte)
        W, H, K = self.W, self.H, self.K

        def masque(dy=0):
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).text((x - l, y - t + dy), texte, font=f, fill=255)
            return m

        def peindre(couleur, alpha):
            calque.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (W, H), c) for c in hexa(couleur)], alpha)))
        base = masque()
        if s.get("halo"):
            c, a, flou = s["halo"]
            peindre(c, base.filter(ImageFilter.GaussianBlur(flou * K)).point(lambda v: int(min(255, v * a * 1.6))))
        if s.get("ombre"):
            c, a, flou, dy = s["ombre"]
            peindre(c, masque(dy * K).filter(ImageFilter.GaussianBlur(flou * K)).point(lambda v: int(v * a)))
        if s.get("contour"):
            c, ep = s["contour"]
            peindre(c, base.filter(ImageFilter.MaxFilter(int(ep * K) * 2 + 1)))
        peindre(s["couleur"], base)

    # ---------- chronologie
    def temps(self, v, champ, quoi):
        if v == "fin":
            return self.duree
        return self.t(v, champ, quoi)

    def preparer(self):
        R, K = self.R, self.K
        self.blocs = []
        for i, b in enumerate(R.get("blocs", [])):
            quoi = f"bloc {i + 1}"
            els, y, prev_h = [], 0, None
            for ligne in b["lignes"]:
                items = [(tx, st, self.temps(tm, "mots", quoi)) for tx, st, tm in ligne["mots"]]
                tailles = [self.encre(tx, st) for tx, st, _ in items]
                esp = int(R["styles"][items[0][1]]["taille"] * K * .28)
                lw = sum(s[0] for s in tailles) + esp * (len(items) - 1)
                lh = max(s[1] for s in tailles)
                if prev_h is not None:
                    y -= int(min(prev_h, lh) * ligne.get("chevauche", 0.1))
                x = ligne.get("dx", 0) * K - lw / 2
                for (tx, st, tm), (w_, h_) in zip(items, tailles):
                    els.append(dict(texte=tx, style=st, t=tm, x=x, y=y + (lh - h_), w=w_, h=h_))
                    x += w_ + esp
                y += lh
                prev_h = lh
            minx = min(e["x"] for e in els); maxx = max(e["x"] + e["w"] for e in els)
            maxy = max(e["y"] + e["h"] for e in els)
            ech = min(1.0, self.W * R.get("largeur_max", .76) / (maxx - minx))
            carton = b["type"] == "carton"
            cy = (R.get("carton", {}).get("y", 900) if carton else R.get("blocs_y", 1250)) * K
            cx0 = (minx + maxx) / 2
            for e in els:
                e["x"] = self.W / 2 + (e["x"] - cx0) * ech
                e["y"] = cy + (e["y"] - maxy / 2) * ech
                e["echelle"] = ech
            t0 = self.temps(b["debut"], "debut", quoi) if "debut" in b else min(e["t"] for e in els)
            t1 = self.temps(b["fin"], "fin", quoi)
            if t1 <= t0:
                sys.exit(f"{quoi} : la fin ({t1:.2f} s) arrive avant le début ({t0:.2f} s).")
            self.blocs.append(dict(i=i, carton=carton, t0=t0, t1=t1, els=els, cy=cy,
                                   fond=hexa(b.get("couleur") or R.get("carton", {}).get("couleur", "#EDC8FC"))))
        # sous-titres mot à mot hors blocs
        S = R.get("sous_titres", {})
        self.caps = []
        if S.get("actif", True):
            maxc = S.get("max_caracteres", 11)
            i = 0
            mots = self.mots
            while i < len(mots):
                w = mots[i]; txt, fin = w["w"], w["e"]
                if (len(txt) <= 3 and i + 1 < len(mots) and len(txt + mots[i + 1]["w"]) <= maxc
                        and mots[i + 1]["s"] - w["e"] < .25):
                    txt += " " + mots[i + 1]["w"]; fin = mots[i + 1]["e"]; i += 1
                i += 1
                if not any(b["t0"] - .01 <= w["s"] < b["t1"] for b in self.blocs):
                    self.caps.append(dict(texte=txt.strip("«» "), t0=w["s"], fin=fin))
            for k, c in enumerate(self.caps):
                nxt = self.caps[k + 1]["t0"] if k + 1 < len(self.caps) else self.duree
                c["t1"] = min(nxt, c["fin"] + S.get("tenue_max", 0.6))
                for b in self.blocs:
                    if c["t0"] < b["t0"] < c["t1"]:
                        c["t1"] = b["t0"]
        self.zooms = [dict(t0=self.temps(z["debut"], "debut", "zoom"), t1=self.temps(z.get("fin", "fin"), "fin", "zoom"),
                           s=z.get("echelle", 1.1), y=z.get("y", 760) * K) for z in R.get("zooms", [])]

    # ---------- rendu d'une image
    def tuile(self, cle, fn):
        if cle not in self._cache:
            lay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            fn(lay)
            bb = lay.getbbox()
            self._cache[cle] = None if bb is None else (np.asarray(lay.crop(bb)).astype(np.float32), bb)
        return self._cache[cle]

    def coller(self, img, tuile, bb, s=1.0, centre=None):
        arr = tuile
        x0, y0, x1, y1 = bb
        if abs(s - 1) > 1e-3:
            cx, cy = centre
            im = Image.fromarray(tuile.astype(np.uint8), "RGBA")
            nw, nh = max(1, int(im.width * s)), max(1, int(im.height * s))
            arr = np.asarray(im.resize((nw, nh), Image.LANCZOS)).astype(np.float32)
            x0 = int(round(cx + (x0 - cx) * s)); y0 = int(round(cy + (y0 - cy) * s))
            x1, y1 = x0 + nw, y0 + nh
        fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(self.W, x1), min(self.H, y1)
        if fx1 <= fx0 or fy1 <= fy0:
            return
        a = arr[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
        al = a[..., 3:4] / 255.0
        reg = img[fy0:fy1, fx0:fx1].astype(np.float32)
        img[fy0:fy1, fx0:fx1] = (reg * (1 - al) + a[..., :3] * al).astype(np.uint8)

    def image(self, img, t):
        for z in self.zooms:
            if z["t0"] <= t < z["t1"]:
                s, cx, cy = z["s"], self.W / 2, z["y"]
                box = (cx - cx / s, cy - cy / s, cx + (self.W - cx) / s, cy + (self.H - cy) / s)
                img = np.asarray(Image.fromarray(img).resize((self.W, self.H), Image.BICUBIC, box=box)).copy()
                break
        A = self.R.get("animation", {})
        for b in self.blocs:
            if b["t0"] <= t < b["t1"]:
                if b["carton"]:
                    img = np.empty_like(img); img[:] = b["fond"]
                vis = [e for e in b["els"] if e["t"] <= t + 1e-6] or b["els"][:1]

                def fn(lay, vis=vis):
                    for e in vis:
                        self.dessiner(lay, e["texte"], e["style"], e["x"], e["y"], e["echelle"])
                res = self.tuile(("bloc", b["i"], len(vis)), fn)
                t_der = max(max(e["t"] for e in vis), b["t0"])
                rebond = A.get("rebond", 0.06) * math.exp(-(t - t_der) / 0.07) if t >= t_der else 0
                s = 1 + A.get("avance", 0.035) * (t - b["t0"]) / max(.5, b["t1"] - b["t0"]) + rebond
                if res:
                    self.coller(img, *res, s, (self.W / 2, b["cy"]))
                return img
        S = self.R.get("sous_titres", {})
        for c in self.caps:
            if c["t0"] <= t < c["t1"]:
                def fn(lay, c=c):
                    nom = S.get("style", "sous_titre")
                    w_, h_ = self.encre(c["texte"], nom)
                    ech = min(1.0, self.W * .76 / w_)
                    w_, h_ = self.encre(c["texte"], nom, ech)
                    self.dessiner(lay, c["texte"], nom, self.W / 2 - w_ / 2, S.get("y", 1250) * self.K - h_ / 2, ech)
                res = self.tuile(("cap", c["texte"], c["t0"]), fn)
                if res:
                    self.coller(img, *res)
                break
        return img


_REP = None


def _init_worker(projet):
    global _REP
    _REP = Replique(Path(projet))


def _rendre_segment(args):
    """Un morceau de la vidéo (images f0 à f1), rendu et encodé par un cœur, sans son."""
    projet, i, f0, f1, preset, crf = args
    rep = _REP
    W, H = rep.W, rep.H
    sortie = Path(projet) / "segments-replique" / f"seg-{i:03d}.mp4"
    n = f1 - f0
    # on cherche une demi-image avant f0 pour tomber exactement sur l'image f0
    dec = subprocess.Popen([ffmpeg(), "-v", "error", "-ss", f"{max(0.0, (f0 - 0.5) / FPS):.4f}", "-i", str(Path(projet) / "base.mp4"),
                            "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    enc = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-pix_fmt", "yuv420p", *args_encodeur(crf), "-color_range", "tv",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-an", str(sortie)],
                           stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    taille, k = W * H * 3, 0
    while k < n:
        buf = dec.stdout.read(taille)
        if len(buf) < taille:
            break
        img = rep.image(np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(), (f0 + k) / FPS)
        enc.stdin.write(img.tobytes())
        k += 1
    dec.stdout.close(); dec.wait()
    enc.stdin.close(); enc.wait()
    if enc.returncode != 0 or k == 0:
        raise RuntimeError(f"segment {i} : {k}/{n} images rendues")
    return i, k


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    projet = Path(args[0]).resolve()
    rep = Replique(projet)
    W, H = rep.W, rep.H
    apercu = []
    if "--apercu" in sys.argv:
        apercu = [float(x) for x in sys.argv[sys.argv.index("--apercu") + 1].split(",")]
        (projet / "apercu-replique").mkdir(exist_ok=True)
    print(f"Réplique : {len(rep.blocs)} blocs et cartons, {len(rep.caps)} sous-titres, rendu {W}x{H}…", flush=True)

    if apercu:   # quelques images seulement, en un seul passage
        dec = subprocess.Popen([ffmpeg(), "-v", "error", "-i", str(projet / "base.mp4"), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        voulu = {int(round(p * FPS)) for p in apercu}
        n, taille = 0, W * H * 3
        while n <= max(voulu):
            buf = dec.stdout.read(taille)
            if len(buf) < taille:
                break
            if n in voulu:
                img = rep.image(np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(), n / FPS)
                Image.fromarray(img).resize((540, 960), Image.LANCZOS).save(projet / "apercu-replique" / f"{n / FPS:06.2f}.jpg", quality=88)
            n += 1
        dec.stdout.close(); dec.terminate()
        print(f"Aperçus : {projet / 'apercu-replique'}")
        return

    # rendu complet : la vidéo est découpée en morceaux rendus en parallèle (un par cœur), puis recollés
    t0 = time.time()
    k4 = W > 1080
    total = int(round(duree(projet / "base.mp4") * FPS))
    coeurs = int(sys.argv[sys.argv.index("--coeurs") + 1]) if "--coeurs" in sys.argv else coeurs_rendu(k4)
    seg = projet / "segments-replique"
    import shutil
    shutil.rmtree(seg, ignore_errors=True); seg.mkdir()
    taille_seg = max(60, -(-total // (coeurs * 3)))
    taches = [(str(projet), i, f0, min(total, f0 + taille_seg), "faster", 17 if k4 else 16)
              for i, f0 in enumerate(range(0, total, taille_seg))]
    print(f"  {len(taches)} morceaux sur {coeurs} cœur(s)…", flush=True)
    faits, rendus = 0, 0
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(coeurs, initializer=_init_worker, initargs=(str(projet),)) as pool:
        for i, k in pool.imap_unordered(_rendre_segment, taches):
            faits += 1; rendus += k
            if faits % max(1, len(taches) // 5) == 0 or faits == len(taches):
                print(f"  {100 * faits // len(taches)} % ({int(time.time() - t0)} s)", flush=True)
    liste = seg / "liste.txt"
    liste.write_text("".join(f"file '{seg / f'seg-{i:03d}.mp4'}'\n" for i in range(len(taches))), encoding="utf-8")
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-i", str(projet / "base.mp4"),
                    "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", "-movflags", "+faststart", str(projet / "final.mp4")], check=True)
    shutil.rmtree(seg, ignore_errors=True)
    if rendus < total - 2:
        print(f"ATTENTION : {rendus} images rendues sur {total} attendues.")
    from rendre import livrer
    livrer(projet)
    print(f"OK : final.mp4 ({rendus / FPS:.1f} s, {W}x{H}) rendu en {int(time.time() - t0)} s")


if __name__ == "__main__":
    main()
