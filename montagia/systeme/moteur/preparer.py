#!/usr/bin/env python3
"""Étape 3. Prépare la base du montage.

Applique les coupes, met la vidéo au format vertical 1080x1920 (sans déformer),
ou au format YouTube 1920x1080 pour un projet créé avec --youtube (sans recadrage),
nettoie la voix (souffle, respirations, niveau -14 LUFS) et recale chaque mot
sur la nouvelle chronologie. C'est sur ces temps-là que la fiche s'appuie.

Usage : python moteur/preparer.py <dossier_projet> [--sans-coupes] [--youtube | --vertical] [--4k | --1080]
        [--agrandissement-ia] [--centre] [--voix-legere] [--voix-classique] [--sans-etalonnage]
  --4k                 vidéo finale en 4K (2160x3840 en vertical)
  --agrandissement-ia  vidéo trop petite (WhatsApp, 480 px) : Real-ESRGAN recrée les détails (long, voir qualite.py)
  --centre             recadrage centré au lieu de suivre le visage
  --voix-classique     filtres classiques au lieu de la voix IA DeepFilterNet
Sort : base.mp4 (voix comprise), voix.wav, mots.json, texte-final.txt, visage.json
"""
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import RACINE, ffmpeg, run, lire_json, ecrire_json, dimensions, format_projet, regler_projet, dimensions_sortie, args_encodeur
from qualite import (voix_ia, voix_ia_dispo, visage_dispo, suivre_visage, commandes_recadrage,
                     chemin_esrgan, agrandir_ia)


TENUE_FIN = 1.2

# Voix studio : débruitage IA (RNNoise), égalisation podcast, anti-sifflantes,
# compression douce, respirations atténuées, niveau Instagram (-14 LUFS).
CHAINE_VOIX_STUDIO = (
    "aresample=48000,highpass=f=75,arnndn=m=voix.rnnn:mix=0.9,afftdn=nf=-30,"
    "equalizer=f=110:t=q:w=1.1:g=2.5,equalizer=f=280:t=q:w=1.2:g=-2.5,"
    "equalizer=f=3400:t=q:w=1.4:g=3,equalizer=f=9500:t=q:w=1.0:g=1.5,"
    "deesser=i=0.35,acompressor=threshold=-21dB:ratio=3:attack=10:release=140:makeup=3,"
    "agate=threshold=0.018:ratio=2.5:range=0.3:attack=6:release=200,"
    "loudnorm=I=-14:TP=-1.5:LRA=7,alimiter=limit=0.89"
)


def plage_couleur(src):
    r = subprocess.run([ffmpeg(), "-i", str(src)], capture_output=True, text=True, errors="replace").stderr
    return "full" if re.search(r"yuvj4|\(pc[,)]|pc, ", r) else "tv"


def vers_chronologie(piste, plages):
    """Passe une piste de visage (temps de la vidéo source) sur la chronologie après coupes."""
    out, decal = [], 0.0
    for p in plages:
        for pt in piste:
            if p["debut"] <= pt[0] < p["fin"]:
                out.append((pt[0] - p["debut"] + decal, *pt[1:]))
        decal += p["fin"] - p["debut"]
    return out


def main():
    t_debut = time.time()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    projet = Path(args[0])
    tr = lire_json(projet / "transcript.json")
    src = tr["source"]
    if "--sans-coupes" in sys.argv or not (projet / "coupes.json").exists():
        fin = max(w["e"] for s in tr["segments"] for w in s["words"]) + 0.3
        plages = [{"debut": 0.0, "fin": round(fin, 3)}]
    else:
        plages = lire_json(projet / "coupes.json")["plages"]

    for drapeau in ("--youtube", "--vertical"):          # changer le format d'un projet existant
        if drapeau in sys.argv:
            regler_projet(projet, format=drapeau[2:] if drapeau == "--youtube" else None)
    if "--4k" in sys.argv:
        regler_projet(projet, sortie="4k")
    if "--1080" in sys.argv:
        regler_projet(projet, sortie=None)
    youtube = format_projet(projet) == "youtube"
    L, H = dimensions_sortie(projet)                    # 1080x1920, 2160x3840 (4K), 1920x1080 ou 3840x2160
    K = H // (1080 if youtube else 1920)
    w, h = dimensions(src)
    plage = plage_couleur(src)     # « full » sur beaucoup d'iPhone : sinon image délavée
    conv = f":in_range={plage}:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709"
    rapport = []

    # ---------- 1. le son : coupes, puis voix IA (DeepFilterNet) ou voix studio classique
    parts, labels = [], ""
    for i, p in enumerate(plages):
        parts.append(f"[0:a]atrim={p['debut']}:{p['fin']},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0, p['fin'] - p['debut'] - 0.015):.3f}:d=0.015[a{i}]")
        labels += f"[a{i}]"
    parts.append(f"{labels}concat=n={len(plages)}:v=0:a=1,apad=pad_dur={TENUE_FIN},aresample=48000[a]")
    brute, voix = (projet / "voix-brute.wav").resolve(), (projet / "voix.wav").resolve()
    run([ffmpeg(), "-y", "-i", str(Path(src).resolve()), "-filter_complex", ";".join(parts), "-map", "[a]", "-ac", "1", "-c:a", "pcm_s16le", brute])
    voix_faite = False
    t_voix = time.time()
    if "--voix-classique" not in sys.argv and voix_ia_dispo():
        try:
            voix_ia(brute, voix, attenuation=20 if "--voix-legere" in sys.argv else 35)
            voix_faite = True
            rapport.append("voix IA (DeepFilterNet)")
        except Exception as e:
            print(f"Voix IA indisponible ({str(e)[:120]}), voix studio classique utilisée.")
    if not voix_faite:
        chaine = CHAINE_VOIX_STUDIO
        machine = RACINE / "config-machine.json"
        if machine.exists() and not lire_json(machine).get("arnndn", True):
            chaine = chaine.replace("arnndn=m=voix.rnnn:mix=0.9,", "")
        if "--voix-legere" in sys.argv:
            chaine = chaine.replace("mix=0.9", "mix=0.55").replace("afftdn=nf=-30,", "").replace("ratio=3:", "ratio=2:")
        run([ffmpeg(), "-y", "-i", brute, "-af", chaine + ",aformat=channel_layouts=stereo", "-ar", "48000", voix], cwd=str(RACINE / "assets" / "voix"))
        rapport.append("voix studio classique")
    rapport[-1] += f" {int(time.time() - t_voix)} s"

    # ---------- 2. l'image : recadrage qui suit le visage, agrandissement IA si la vidéo est trop petite
    recadre = (not youtube) and w / h > 9 / 16 + 0.01
    piste = []
    t_visage = time.time()
    if recadre and "--centre" not in sys.argv:
        if visage_dispo():
            piste = vers_chronologie(suivre_visage(src), plages)
            rapport.append(("cadrage qui suit le visage" if piste else "aucun visage détecté, cadrage centré") + f" {int(time.time() - t_visage)} s")
        else:
            rapport.append("cadrage centré (détecteur de visage absent, relance l'installation)")
    petite = h < 720
    ia = "--agrandissement-ia" in sys.argv
    if petite and not ia:
        print(f"ATTENTION : vidéo de petite taille ({w}x{h}). Pour une image nette, relance une fois les coupes validées : "
              f"python systeme/montagia.py preparer {projet.name} --agrandissement-ia   (agrandissement IA, environ "
              f"1 h par minute de vidéo sur un Mac récent, à lancer en arrière-plan).")
    entree, w_src, x_dec = src, w, 0          # x_dec : début de la zone traitée par l'IA, en pixels source
    if ia:
        if not chemin_esrgan():
            sys.exit("Agrandissement IA impossible : Real-ESRGAN n'est pas installé. Lance : python systeme/montagia.py installer")
        # zone utile : l'union de toutes les positions du cadre 9:16 (inutile d'agrandir ce qui sera coupé)
        lc = int(round(h * 9 / 16)) if recadre else w
        if recadre and piste:
            xs = [min(w - lc, max(0, cx * w - lc / 2)) for _, cx, _, _ in piste]
            x0, x1 = int(min(xs)), int(min(w, max(xs) + lc + 2))
        elif recadre:
            x0, x1 = (w - lc) // 2, (w - lc) // 2 + lc
        else:
            x0, x1 = 0, w
        x0 -= x0 % 2; x1 -= x1 % 2
        agrandi_ia = projet / "image-ia.mp4"
        import json as _json
        cle = _json.dumps({"plages": plages, "zone": [x0, x1], "source": str(Path(src).resolve()),
                           "taille": Path(src).stat().st_size})
        deja = agrandi_ia.exists() and (projet / "image-ia.cle").exists() and (projet / "image-ia.cle").read_text() == cle
        coupe = projet / "coupe-ia-entree.mp4"
        parts, labels = [], ""
        for i, p in enumerate(plages):
            parts.append(f"[0:v]trim={p['debut']}:{p['fin']},setpts=PTS-STARTPTS[v{i}]")
            labels += f"[v{i}]"
        parts.append(f"{labels}concat=n={len(plages)}:v=1:a=0,tpad=stop_mode=clone:stop_duration={TENUE_FIN},"
                     f"scale=iw:ih{conv},crop={x1 - x0}:{h}:{x0}:0,fps=30[v]")
        if deja:
            print("Agrandissement IA déjà fait pour ces coupes : réutilisé (image-ia.mp4).")
        else:
            run([ffmpeg(), "-y", "-i", str(Path(src).resolve()), "-filter_complex", ";".join(parts), "-map", "[v]",
                 "-c:v", "libx264", "-crf", "8", "-preset", "veryfast", "-pix_fmt", "yuv420p", coupe])
            agrandir_ia(coupe, agrandi_ia, projet)
            coupe.unlink(missing_ok=True)
            (projet / "image-ia.cle").write_text(cle)
        entree, w_src, x_dec = agrandi_ia, x1 - x0, x0
        plages_v = None                                  # déjà coupée
        conv_v = ""
        rapport.append("agrandissement IA Real-ESRGAN")
    else:
        plages_v = plages
        conv_v = conv
    if youtube:
        # paysage, jamais de recadrage du sujet : une vidéo verticale ou carrée garde toute son image sur un fond flou d'elle-même
        if abs(w / h - 16 / 9) < 0.02:
            cadre = f"scale={L}:{H}:flags=lanczos+accurate_rnd+full_chroma_int{conv_v}"
        elif 1.55 < w / h < 1.95:
            cadre = f"scale={L}:{H}:force_original_aspect_ratio=increase:flags=lanczos{conv_v},crop={L}:{H}"
        else:
            cadre = (f"scale={L}:{H}:force_original_aspect_ratio=decrease:flags=lanczos{conv_v},split[fg][bg0];"
                     f"[bg0]scale={L}:{H}:force_original_aspect_ratio=increase,crop={L}:{H},boxblur={40 * K}:2,eq=brightness=-0.06[bg];"
                     f"[bg][fg]overlay=(W-w)/2:(H-h)/2")
    elif recadre:
        ls = int(round(w_src * H / h / 2)) * 2           # largeur une fois mise à la hauteur de sortie
        x_centre = (ls - L) // 2
        if piste:
            cmd = projet / "recadrage.txt"
            # la piste est en fraction de la largeur source : on la ramène dans la zone traitée
            pist2 = [(t, (cx * w - x_dec) / w_src, cy, lv) for t, cx, cy, lv in piste]
            x_moy = commandes_recadrage(pist2, ls, L, cmd)
            # nom de fichier seul (ffmpeg tourne dans le dossier du projet) : aucun souci d'espace ou d'apostrophe
            cadre = f"scale={ls}:{H}:flags=lanczos+accurate_rnd+full_chroma_int{conv_v},sendcmd=f={cmd.name},crop={L}:{H}:{x_centre}:0"
            vx = sum(cx * w * H / h - x_dec * H / h for _, cx, _, _ in piste) / len(piste) - x_moy
            vy = sum(cy for _, _, cy, _ in piste) / len(piste) * H
            ecrire_json(projet / "visage.json", {"x": round(vx / K), "y": round(vy / K), "repere": "1080 x 1920"})
            print(f"Visage suivi : centre moyen x={round(vx / K)} y={round(vy / K)} (repère 1080 x 1920, voir visage.json)")
        else:
            cadre = f"scale={ls}:{H}:flags=lanczos+accurate_rnd+full_chroma_int{conv_v},crop={L}:{H}"
    else:
        cadre = f"scale={L}:-2:flags=lanczos+accurate_rnd+full_chroma_int{conv_v},crop={L}:{H}"   # déjà vertical
    if youtube:
        agrandi = min(L / w, H / h) > 1.05
    else:
        agrandi = H / (h * (4 if ia else 1)) > 1.05
    nettete = "unsharp=5:5:0.75:5:5:0.0" if agrandi and not ia else "unsharp=3:3:0.3"
    parts = []
    if plages_v:
        labels = ""
        for i, p in enumerate(plages_v):
            parts.append(f"[0:v]trim={p['debut']}:{p['fin']},setpts=PTS-STARTPTS[v{i}]")
            labels += f"[v{i}]"
        # fin tenue : la dernière image reste 1,2 s (le temps de lire le CTA)
        parts.append(f"{labels}concat=n={len(plages_v)}:v=1:a=0,tpad=stop_mode=clone:stop_duration={TENUE_FIN}[vc]")
    else:
        parts.append("[0:v]null[vc]")
    t_image = time.time()
    etalonnage = "" if "--sans-etalonnage" in sys.argv else "eq=contrast=1.06:saturation=1.12:gamma=0.98,"
    parts.append(f"[vc]{cadre},fps=30,{etalonnage}{nettete},format=yuv420p[v]")
    # encodage quasi sans perte (qualité 13) avec l'encodeur matériel de l'ordinateur s'il existe : la base est réencodée au rendu
    run([ffmpeg(), "-y", "-i", str(Path(entree).resolve()), "-i", voix, "-filter_complex", ";".join(parts), "-map", "[v]", "-map", "1:a",
         *args_encodeur(13), "-color_range", "tv",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "320k", "-shortest",
         "-movflags", "+faststart", Path(projet).resolve() / "base.mp4"], cwd=str(Path(projet).resolve()))
    brute.unlink(missing_ok=True)
    rapport.append(f"image {int(time.time() - t_image)} s")
    print(f"Image {L}x{H}{' (4K)' if K > 1 else ''} : " + ", ".join(rapport) + f" (total {int(time.time() - t_debut)} s)")

    # recalage des mots sur la chronologie finale
    mots, decal = [], 0.0
    tous = [x for s in tr["segments"] for x in s["words"]]
    for p in plages:
        for x in tous:
            if x["s"] >= p["debut"] - 0.01 and x["e"] <= p["fin"] + 0.01:
                mots.append({"w": x["w"], "s": round(x["s"] - p["debut"] + decal, 3), "e": round(x["e"] - p["debut"] + decal, 3)})
        decal += p["fin"] - p["debut"]
    # recollage : Whisper sépare « d » / « 'abord » et « lance » / « -le »
    colles = []
    for m in mots:
        if colles and (m["w"][:1] in "'’-" or colles[-1]["w"][-1:] in "'’" or re.match(r"^[.,]\d", m["w"])):
            colles[-1]["w"] += m["w"]; colles[-1]["e"] = m["e"]
        else:
            colles.append(dict(m))
    # corrections (fichier corrections.json du projet ou de la charte : {"menteurs": "monteurs"})
    corr = {}
    for f in (RACINE / "ma-charte.json", projet / "corrections.json"):
        if f.exists():
            d = lire_json(f)
            corr.update(d.get("corrections", d) if isinstance(d, dict) else {})
    cl = {k.lower(): v for k, v in corr.items()}
    for m in colles:
        g = re.match(r"^(\W*)(.+?)(\W*)$", m["w"])
        if g and g.group(2).lower() in cl:
            n = cl[g.group(2).lower()]
            if g.group(2)[:1].isupper():
                n = n[:1].upper() + n[1:]
            m["w"] = g.group(1) + n + g.group(3)
    mots = colles
    ecrire_json(projet / "mots.json", {"duree": round(decal + TENUE_FIN, 3), "mots": mots})
    lignes, ligne = [], []
    for i, m in enumerate(mots):
        ligne.append(f"{m['w']}")
        if re.search(r"[.!?]$", m["w"]) or i == len(mots) - 1:
            lignes.append(f"{mots[i - len(ligne) + 1]['s']:6.2f}  " + " ".join(ligne))
            ligne = []
    (projet / "texte-final.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"OK : base.mp4 ({decal:.1f} s{', format YouTube 1920x1080' if youtube else ''}), {len(mots)} mots recalés -> texte-final.txt")


if __name__ == "__main__":
    main()
