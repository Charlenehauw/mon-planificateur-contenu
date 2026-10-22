#!/usr/bin/env python3
"""Finitions de Charlène, posées APRÈS le rendu (replique ou rendre) : gros émojis, étoiles qui scintillent, bruitages.

Usage : python systeme/ma-bibliotheque/finitions.py <projet> [--apercu 3.0,8.5]
Lit   : <projet>/final.mp4, <projet>/mots.json, <projet>/finitions.json
Sort  : <projet>/final-finitions.mp4, copié dans « Mes vidéos montées » (à la place de la version sans finitions),
        ou des images dans <projet>/apercu-finitions/ avec --apercu.

finitions.json (positions dans le repère 1080 x 1920, temps en secondes ou « @mot », « @mot#2 », « @mot> », « @mot+0.2 ») :
{
 "emojis":  [{"t": "@caca", "emoji": "💩", "x": 820, "y": 560, "taille": 260, "duree": 1.2, "son": "pop"}],
 "etoiles": [{"t": "@test", "x": 300, "y": 300, "taille": 60, "duree": 1.5}],
 "sons":    [{"t": "@go", "son": "whoosh", "volume": 0.5}],
 "sous_titres": {"mots_forts": ["tonnerre", "Claude"], "y": 1260, "taille": 68, "mots": 3}
}
« sous_titres » remplace les sous-titres du moteur (mettre "sous_titres": {"actif": false} dans replique.json) :
2 à 3 mots en Lato blanc sur la poitrine, les mots forts en jaune doré, rien pendant les blocs de replique.json.
Un émoji ou une étoile peut porter "son" (nom d'un fichier de systeme/assets/sons sans .wav, ou un chemin) et "volume" (0 à 1).
Règles : rien sur le visage, rien sous y = 1536, 1 émoji toutes les 4 s au maximum, bruitages discrets (volume 0.3 à 0.6).
"""
import json
import math
import platform
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RACINE = Path(__file__).resolve().parent.parent
SONS = RACINE / "assets" / "sons"
FPS = 30
CREME = (240, 239, 238)
JAUNE = (232, 189, 60)
OMBRE = (30, 42, 51)
SABLE = (219, 204, 155)

POLICES_EMOJI = [
    "/System/Library/Fonts/Apple Color Emoji.ttc",           # Mac
    "C:/Windows/Fonts/seguiemj.ttf",                          # Windows
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",      # Linux
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
]


def ffmpeg():
    cfg = RACINE / "config-machine.json"
    if cfg.exists():
        f = json.loads(cfg.read_text(encoding="utf-8")).get("ffmpeg")
        if f:
            return f
    return "ffmpeg"


def norm(m):
    return re.sub(r"[^\w']", "", m.lower())


def temps(v, mots, quoi):
    """Nombre, ou « @mot », « @mot#2 », « @mot> » (fin du mot), suivi d'un décalage « +0.2 » / « -0.1 »."""
    if isinstance(v, (int, float)):
        return float(v)
    r = re.fullmatch(r"@([^#>+\-]+(?:-[^#>+\-]+)*?)(?:#(\d+))?(>)?([+-][\d.]+)?", str(v).strip())
    if not r:
        sys.exit(f"{quoi} : temps illisible « {v} ».")
    cible, n, fin, dec = norm(r.group(1)), int(r.group(2) or 1), r.group(3), float(r.group(4) or 0)
    trouves = [m for m in mots if norm(m["w"]) == cible]
    if len(trouves) < n:
        sys.exit(f"{quoi} : le mot « {r.group(1)} » n'apparaît pas {n} fois dans la vidéo.")
    m = trouves[n - 1]
    return (m["e"] if fin else m["s"]) + dec


def image_emoji(car, taille):
    for p in POLICES_EMOJI:
        if not Path(p).exists():
            continue
        for t in (160, 137, 109, 96, 64):          # les polices émoji en couleur n'existent qu'à certaines tailles
            try:
                f = ImageFont.truetype(p, t)
                break
            except OSError:
                f = None
        if f is None:
            continue
        im = Image.new("RGBA", (t * 2, t * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((t // 2, t // 2), car, font=f, embedded_color=True)
        boite = im.getbbox()
        if not boite:
            continue
        im = im.crop(boite)
        k = taille / max(im.size)
        return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    sys.exit("Aucune police d'émojis en couleur trouvée sur cet ordinateur.")


def image_etoile(taille, couleur=CREME):
    """Étoile à 4 branches avec un halo doux, comme dans le reel modèle."""
    s = taille * 3
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r, f = s / 2, taille / 2, taille / 9
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else f
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    halo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(halo).polygon(pts, fill=SABLE + (200,))
    halo = halo.filter(ImageFilter.GaussianBlur(taille / 6))
    d.polygon(pts, fill=couleur + (255,))
    return Image.alpha_composite(halo, im)


def courbe_pop(u):
    """0 → 1.15 → 1 sur u de 0 à 1 (apparition qui rebondit)."""
    if u >= 1:
        return 1.0
    return 1.15 * math.sin(u * math.pi / 2) if u < 0.7 else 1.15 - 0.15 * (u - 0.7) / 0.3


class Finitions:
    def __init__(self, projet):
        self.p = Path(projet)
        self.F = json.loads((self.p / "finitions.json").read_text(encoding="utf-8"))
        self.mots = json.loads((self.p / "mots.json").read_text(encoding="utf-8"))["mots"]
        self.src = self.p / "final.mp4"
        sortie = subprocess.run([str(Path(ffmpeg()).with_name("ffprobe")) if Path(ffmpeg()).is_absolute() else "ffprobe",
                                 "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                                 "-of", "json", str(self.src)], capture_output=True, text=True).stdout
        info = json.loads(sortie)
        self.W, self.H = info["streams"][0]["width"], info["streams"][0]["height"]
        self.duree = float(info["format"]["duration"])
        self.K = self.W / 1080
        self.elements, self.sons = [], []
        for i, e in enumerate(self.F.get("emojis", [])):
            q = f"émoji {i + 1}"
            t0 = temps(e["t"], self.mots, q)
            self.verifier(e, q)
            self.elements.append(dict(img=image_emoji(e["emoji"], int(e.get("taille", 240) * self.K)), t0=t0,
                                      t1=t0 + e.get("duree", 1.2), x=e["x"] * self.K, y=e["y"] * self.K, sorte="emoji"))
            if e.get("son"):
                self.sons.append((t0, e["son"], e.get("volume", 0.5)))
        for i, e in enumerate(self.F.get("etoiles", [])):
            q = f"étoile {i + 1}"
            t0 = temps(e["t"], self.mots, q)
            self.verifier(e, q)
            self.elements.append(dict(img=image_etoile(int(e.get("taille", 60) * self.K)), t0=t0, t1=t0 + e.get("duree", 1.5),
                                      x=e["x"] * self.K, y=e["y"] * self.K, sorte="etoile", phase=i * 1.7))
            if e.get("son"):
                self.sons.append((t0, e["son"], e.get("volume", 0.4)))
        for i, s in enumerate(self.F.get("sons", [])):
            self.sons.append((temps(s["t"], self.mots, f"son {i + 1}"), s["son"], s.get("volume", 0.5)))
        self.caps = self.preparer_sous_titres(self.F.get("sous_titres"))

    def blocs_replique(self):
        f = self.p / "replique.json"
        if not f.exists():
            return []
        R = json.loads(f.read_text(encoding="utf-8"))
        zones = []
        for i, b in enumerate(R.get("blocs", [])):
            debut = b.get("debut") or min((m[2] for l in b["lignes"] for m in l["mots"]), key=lambda v: temps(v, self.mots, ""))
            zones.append((temps(debut, self.mots, f"bloc {i + 1}"), temps(b["fin"], self.mots, f"bloc {i + 1}")))
        return zones

    def preparer_sous_titres(self, S):
        if not S:
            return []
        police = next((d / "Lato-Black.ttf" for d in (RACINE / ".outils" / "polices", Path.home() / "Library/Fonts")
                       if (d / "Lato-Black.ttf").exists()), None)
        if police is None:
            sys.exit("Police Lato-Black.ttf introuvable (systeme/.outils/polices).")
        self.police_st = ImageFont.truetype(str(police), int(S.get("taille", 68) * self.K))
        self.y_st = S.get("y", 1260) * self.K
        forts = {norm(m) for m in S.get("mots_forts", [])}
        zones, maxi = self.blocs_replique(), S.get("mots", 3)
        libres = [m for m in self.mots if not any(a - .01 <= m["s"] < b for a, b in zones)]
        caps, groupe = [], []
        for k, m in enumerate(libres):
            groupe.append(m)
            suivant = libres[k + 1] if k + 1 < len(libres) else None
            coupe = (len(groupe) >= maxi or suivant is None or suivant["s"] - m["e"] > .35
                     or m["w"].rstrip()[-1:] in ".,!?" or len(" ".join(g["w"] for g in groupe)) > 16)
            if coupe:
                caps.append(dict(mots=[(g["w"].strip("«» "), norm(g["w"]) in forts) for g in groupe],
                                 t0=groupe[0]["s"], t1=groupe[-1]["e"] + .25))
                groupe = []
        for k, c in enumerate(caps):
            if k + 1 < len(caps):
                c["t1"] = min(c["t1"], caps[k + 1]["t0"])
            for a, b in zones:
                if c["t0"] < a < c["t1"]:
                    c["t1"] = a
        for c in caps:
            self.elements.append(dict(t0=c["t0"], t1=c["t1"], sorte="sous_titre", cap=c))
        return caps

    def dessiner_sous_titre(self, fond, c, t):
        f, esp = self.police_st, int(self.police_st.size * .28)
        tailles = [f.getbbox(w) for w, _ in c["mots"]]
        larg = sum(b[2] - b[0] for b in tailles) + esp * (len(tailles) - 1)
        calque = Image.new("RGBA", fond.size, (0, 0, 0, 0))
        ombre = Image.new("RGBA", fond.size, (0, 0, 0, 0))
        d, do = ImageDraw.Draw(calque), ImageDraw.Draw(ombre)
        x = fond.width / 2 - larg / 2
        for (w, fort), b in zip(c["mots"], tailles):
            y = self.y_st - (b[3] + b[1]) / 2
            d.text((x - b[0], y), w, font=f, fill=(JAUNE if fort else (255, 255, 255)) + (255,))
            do.text((x - b[0], y + 3 * self.K), w, font=f, fill=OMBRE + (205,))
            x += b[2] - b[0] + esp
        ombre = ombre.filter(ImageFilter.GaussianBlur(10 * self.K))
        fond.alpha_composite(ombre)
        fond.alpha_composite(calque)

    def verifier(self, e, quoi):
        if e["y"] > 1536:
            sys.exit(f"{quoi} : y = {e['y']} est sous la ligne 1536 (zone cachée par l'interface Instagram).")

    def dessiner(self, fond, t):
        for e in self.elements:
            if not (e["t0"] <= t < e["t1"]):
                continue
            if e["sorte"] == "sous_titre":
                self.dessiner_sous_titre(fond, e["cap"], t)
                continue
            u, reste = (t - e["t0"]) / 0.28, e["t1"] - t
            if e["sorte"] == "emoji":
                k = courbe_pop(u) * (1 + 0.03 * math.sin((t - e["t0"]) * 6))
                ang = 6 * math.sin((t - e["t0"]) * 5)
                alpha = min(1.0, reste / 0.15)
            else:
                k = courbe_pop(u) * (0.75 + 0.25 * math.sin((t - e["t0"]) * 9 + e["phase"]))
                ang = (t - e["t0"]) * 40
                alpha = min(1.0, reste / 0.25)
            im = e["img"]
            im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS).rotate(ang, expand=True, resample=Image.BICUBIC)
            if alpha < 1:
                im.putalpha(im.getchannel("A").point(lambda a: int(a * alpha)))
            fond.alpha_composite(im, (int(e["x"] - im.width / 2), int(e["y"] - im.height / 2)))

    def chemin_son(self, nom):
        p = Path(nom)
        return p if p.suffix and p.exists() else SONS / f"{nom}.wav"

    def apercu(self, instants):
        d = self.p / "apercu-finitions"
        d.mkdir(exist_ok=True)
        for t in instants:
            raw = subprocess.run([ffmpeg(), "-v", "error", "-ss", str(t), "-i", str(self.src), "-frames:v", "1",
                                  "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True).stdout
            im = Image.frombytes("RGBA", (self.W, self.H), raw)
            self.dessiner(im, t)
            im.convert("RGB").save(d / f"{t:06.2f}.jpg", quality=88)
        print(f"Aperçus : {d}")

    def rendre(self):
        sortie = self.p / "final-finitions.mp4"
        cmd = [ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{self.W}x{self.H}", "-r", str(FPS),
               "-i", "-", "-i", str(self.src)]
        filtres, entrees = [], ["[1:a]"]
        for k, (t, nom, vol) in enumerate(self.sons):
            cmd += ["-i", str(self.chemin_son(nom))]
            ms = max(0, int(t * 1000))
            filtres.append(f"[{k + 2}:a]volume={vol},adelay={ms}|{ms}[s{k}]")
            entrees.append(f"[s{k}]")
        if self.sons:
            filtres.append("".join(entrees) + f"amix=inputs={len(entrees)}:normalize=0:duration=first,alimiter=limit=0.89[a]")
            cmd += ["-filter_complex", ";".join(filtres), "-map", "0:v", "-map", "[a]"]
        else:
            cmd += ["-map", "0:v", "-map", "1:a"]
        cmd += ["-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", "-shortest", str(sortie)]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        dec = subprocess.Popen([ffmpeg(), "-v", "error", "-i", str(self.src), "-f", "rawvideo", "-pix_fmt", "rgba", "-r", str(FPS), "-"],
                               stdout=subprocess.PIPE)
        taille, n = self.W * self.H * 4, 0
        while True:
            raw = dec.stdout.read(taille)
            if len(raw) < taille:
                break
            t = n / FPS
            if any(e["t0"] <= t < e["t1"] for e in self.elements):
                im = Image.frombytes("RGBA", (self.W, self.H), raw)
                self.dessiner(im, t)
                raw = im.tobytes()
            enc.stdin.write(raw)
            n += 1
        enc.stdin.close()
        enc.wait()
        dec.wait()
        if enc.returncode != 0:
            sys.exit("Le rendu des finitions a échoué.")
        copie = RACINE.parent / "Mes vidéos montées" / f"{self.p.name}.mp4"
        copie.write_bytes(sortie.read_bytes())
        print(f"OK : {sortie} ({len(self.caps)} sous-titres, {len([e for e in self.elements if e['sorte'] == 'emoji'])} émojis, "
              f"{len([e for e in self.elements if e['sorte'] == 'etoile'])} étoiles, {len(self.sons)} bruitages)")
        print(f"Copie prête à publier : {copie}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    projet = Path(sys.argv[1])
    if not projet.exists():
        projet = RACINE / "projets" / sys.argv[1]
    f = Finitions(projet)
    if "--apercu" in sys.argv:
        f.apercu([float(x) for x in sys.argv[sys.argv.index("--apercu") + 1].split(",")])
    else:
        f.rendre()


if __name__ == "__main__":
    main()
