#!/usr/bin/env python3
"""Étape 6. Rend la vidéo finale : images (HyperFrames) + voix studio + musique et sons éventuels.

Usage : python moteur/rendre.py <dossier_projet> [--brouillon]
Sort : final.mp4

Format YouTube : seuls les passages avec effets passent par HyperFrames (page fenetres.html),
le reste de la vidéo est repris tel quel, les sous-titres sont posés par ffmpeg. Une vidéo de
30 minutes se rend ainsi en quelques dizaines de minutes au lieu de plusieurs heures.
"""
import hashlib
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import RACINE, MONTEES, ffmpeg, run, lire_json, npx, env_node, HYPERFRAMES, format_projet, sortie_4k, args_encodeur, encodeur


def pistes_audio(projet, cmd, n, voix):
    """Voix studio + musique et bruitages éventuels. Renvoie (filtres, sortie audio ou None)."""
    S = lire_json(projet / "sons.json")
    filtres, entrees = [], [voix]
    if S.get("musique"):
        mus = Path(S["musique"]) if Path(S["musique"]).is_absolute() else projet / S["musique"]
        cmd += ["-stream_loop", "-1", "-i", mus]
        filtres.append(f"[{n}:a]volume={S.get('musique_volume', 0.08)},afade=t=in:d=1[mus];[mus]{voix}sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[musd]")
        entrees.append("[musd]"); n += 1
    for s in S.get("sons", []):
        cmd += ["-i", RACINE / "assets" / "sons" / f"{s['son']}.wav"]
        ms = int(s["t"] * 1000)
        filtres.append(f"[{n}:a]adelay={ms}|{ms},volume={s['volume']}[s{n}]")
        entrees.append(f"[s{n}]"); n += 1
    if len(entrees) == 1:
        return filtres, None
    filtres.append("".join(entrees) + f"amix=inputs={len(entrees)}:normalize=0:duration=first,alimiter=limit=0.89[a]")
    return filtres, "[a]"


def rendre_hf(args):
    """Rendu HyperFrames avec l'encodeur matériel (--gpu) si l'ordinateur en a un, sinon (ou en cas d'échec) en logiciel."""
    gpu = encodeur() != "libx264"
    for essai in ([*args, "--gpu"], args) if gpu else (args,):
        r = subprocess.run([npx(), "-y", HYPERFRAMES, "render", *essai], env=env_node(), capture_output=True, text=True, errors="replace")
        if r.returncode == 0:
            return r
    return r


def cle_fenetres(projet, q):
    """Empreinte de tout ce qui change l'image des passages animés (pas les sous-titres ni le son)."""
    h = hashlib.sha256(q.encode())
    m = projet / "montage"
    for f in sorted(m.rglob("*")):
        if not f.is_file() or f.name in ("index.html", "donnees.js") or "snapshots" in f.parts or "sous-titres" in f.parts:
            continue
        h.update(str(f.relative_to(m)).encode())
        if f.stat().st_size > 20_000_000:   # grosses vidéos : taille + début du fichier
            h.update(str(f.stat().st_size).encode())
            with open(f, "rb") as x:
                h.update(x.read(4_000_000))
        else:
            h.update(f.read_bytes())
    return h.hexdigest()


def rendre_youtube(projet, q):
    t0 = time.time()
    fps = 30
    K = 2 if sortie_4k(projet) else 1               # 4K : la page est rendue en 3840x2160, les sous-titres doublés
    F = lire_json(projet / "fenetres.json")
    fen = F["fenetres"]
    rendu = projet / "rendu-fenetres.mp4"           # gardé hors de montage/ : réutilisé si rien n'a bougé
    cle = cle_fenetres(projet, q) if fen else ""
    t_images = 0.0
    if fen and rendu.exists() and (projet / "rendu-fenetres.cle").exists() and (projet / "rendu-fenetres.cle").read_text() == cle:
        print("Passages animés inchangés : rendu précédent réutilisé.")
    elif fen:
        rendu.unlink(missing_ok=True)
        print(f"Rendu des passages avec effets : {F['a_rendre']:.0f} s sur {F['duree']:.0f} s de vidéo…", flush=True)
        r = rendre_hf([str(projet / "montage"), "-c", "fenetres.html", "-o", str(rendu), "-q", q,
                       "--video-frame-format", "jpg", "--crf", "23" if q == "draft" else "14", "--quiet",
                       *(["--resolution", "landscape-4k"] if K > 1 else [])])
        if r.returncode != 0 or not rendu.exists():
            sys.exit("Le rendu a échoué :\n" + (r.stdout + r.stderr)[-3000:])
        (projet / "rendu-fenetres.cle").write_text(cle)
        t_images = time.time() - t0
        print(f"  passages rendus en {t_images / 60:.1f} min", flush=True)

    from sous_titres import fabriquer
    st = fabriquer(projet, projet / "montage" / "sous-titres")

    cmd = [ffmpeg(), "-y", "-i", projet / "base.mp4"]
    # la base peut finir un peu avant la voix (fin tenue) : on prolonge la dernière image
    filtres, n, cur = ["[0:v]tpad=stop_mode=clone:stop_duration=3[base]"], 1, "[base]"
    if fen:
        cmd += ["-i", rendu]
        # chaque image de la page des fenêtres retrouve sa place dans la vraie chronologie
        d0 = fen[0]["debut"] - fen[0]["page"]
        expr = f"T+{d0:.4f}" + "".join(
            f"+{(f['debut'] - f['page']) - (p['debut'] - p['page']):.4f}*gte(T,{f['page'] - 0.5 / fps:.4f})" for p, f in zip(fen, fen[1:]))
        actif = "+".join(f"between(t,{f['debut'] - 0.25 / fps:.4f},{f['fin'] - 0.75 / fps:.4f})" for f in fen)
        filtres.append(f"[{n}:v]setpts='({expr}-{0.3 / fps:.5f})/TB'[fx]")
        filtres.append(f"{cur}[fx]overlay=eof_action=pass:repeatlast=0:enable='{actif}'[v{n}]")
        cur, n = f"[v{n}]", n + 1
    if st:
        liste, y = st
        cmd += ["-f", "concat", "-safe", "0", "-i", liste]
        filtres.append(f"[{n}:v]format=rgba{f',scale=iw*{K}:ih*{K}:flags=lanczos' if K > 1 else ''}[st];{cur}[st]overlay=0:{y * K}:eof_action=pass[v{n}]")
        cur, n = f"[v{n}]", n + 1
    filtres.append(f"{cur}format=yuv420p[v]")
    fa, sortie_audio = pistes_audio(projet, cmd, n, "[0:a]")
    filtres += fa
    cmd += ["-filter_complex", ";".join(filtres), "-map", "[v]", "-map", sortie_audio or "0:a",
            "-t", f"{F['duree']:.3f}",
            *args_encodeur(24 if q == "draft" else 16),
            "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", projet / "final.mp4"]
    print("Assemblage de la vidéo complète (voix, sous-titres, passages animés)…", flush=True)
    t1 = time.time()
    run(cmd)
    total = time.time() - t0
    lire = lambda x: f"{int(x // 60)} min {int(x % 60):02d} s"
    print(f"Temps de rendu : {lire(total)} pour {lire(F['duree'])} de vidéo "
          f"(passages animés {lire(t_images)}, assemblage {lire(time.time() - t1)}).")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    projet = Path(args[0]).resolve()
    brouillon = "--brouillon" in sys.argv
    q = "draft" if brouillon else "looks"      # « looks » capture plus vite que « delivery », la qualité d'encodage est fixée par --crf
    if format_projet(projet) == "youtube":
        rendre_youtube(projet, q)
        livrer(projet)
        return
    images = projet / "montage" / "rendu-images.mp4"
    k4 = sortie_4k(projet)
    print("Rendu des images… " + ("(4K : 2 à 4 minutes pour 45 s de vidéo sur un Mac récent)" if k4 else "(1 à 2 minutes pour 45 s de vidéo sur un Mac récent)"), flush=True)
    r = rendre_hf([str(projet / "montage"), "-o", str(images), "-q", q, "--video-frame-format", "jpg", "--crf", "23" if q == "draft" else "14", "--quiet",
                   *(["--resolution", "portrait-4k"] if k4 else [])])
    if r.returncode != 0 or not images.exists():
        sys.exit("Le rendu a échoué :\n" + (r.stdout + r.stderr)[-3000:])

    S = lire_json(projet / "sons.json")
    cmd = [ffmpeg(), "-y", "-i", images, "-i", projet / "base.mp4"]
    filtres, entrees = [], ["[1:a]"]
    n = 2
    if S.get("musique"):
        mus = Path(S["musique"]) if Path(S["musique"]).is_absolute() else projet / S["musique"]
        cmd += ["-stream_loop", "-1", "-i", mus]
        filtres.append(f"[{n}:a]volume={S.get('musique_volume', 0.08)},afade=t=in:d=1[mus];[mus][1:a]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[musd]")
        entrees.append("[musd]"); n += 1
    for s in S.get("sons", []):
        cmd += ["-i", RACINE / "assets" / "sons" / f"{s['son']}.wav"]
        ms = int(s["t"] * 1000)
        filtres.append(f"[{n}:a]adelay={ms}|{ms},volume={s['volume']}[s{n}]")
        entrees.append(f"[s{n}]"); n += 1
    if len(entrees) == 1:
        cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest"]
    else:
        filtres.append("".join(entrees) + f"amix=inputs={len(entrees)}:normalize=0:duration=first,alimiter=limit=0.89[a]")
        cmd += ["-filter_complex", ";".join(filtres), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k"]
    cmd += ["-movflags", "+faststart", projet / "final.mp4"]
    run(cmd)
    livrer(projet)


def livrer(projet):
    import shutil
    MONTEES.mkdir(exist_ok=True)
    copie = MONTEES / f"{projet.name}.mp4"
    shutil.copy(projet / "final.mp4", copie)
    print(f"OK : {projet / 'final.mp4'}")
    print(f"Copie prête à publier : {copie}")
    if (projet / "sous-titres.srt").exists():
        shutil.copy(projet / "sous-titres.srt", MONTEES / f"{projet.name}.srt")
        print(f"Sous-titres pour YouTube (à importer dans YouTube Studio) : {MONTEES / (projet.name + '.srt')}")


if __name__ == "__main__":
    main()
