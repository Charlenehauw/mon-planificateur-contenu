#!/usr/bin/env python3
"""Étape 1. Transcription mot par mot (faster-whisper, local, gratuit).

Usage : python moteur/transcrire.py <video> <dossier_projet> [--modele large-v3-turbo] [--langue fr]
Sort : transcript.json (chaque mot avec son début et sa fin) et transcript.txt (lisible).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import ffmpeg, run, ecrire_json


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    modele, langue = opt("--modele", "large-v3-turbo"), opt("--langue", "fr")
    src, projet = Path(args[0]).expanduser(), Path(args[1]).expanduser()
    if not src.exists():
        sys.exit(f"Vidéo introuvable : {src}")
    projet.mkdir(parents=True, exist_ok=True)
    wav = projet / "audio-16k.wav"
    run([ffmpeg(), "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", wav])

    print(f"Transcription ({modele})… la première fois, le modèle se télécharge.")
    from faster_whisper import WhisperModel
    import os
    m = WhisperModel(modele, device="auto", compute_type="auto", cpu_threads=os.cpu_count() or 4)
    vocab = opt("--vocabulaire", "")
    charte = Path(__file__).resolve().parent.parent / "ma-charte.json"
    if charte.exists():
        import json
        vocab = (vocab + " " + " ".join(json.loads(charte.read_text(encoding="utf-8")).get("vocabulaire", []))).strip()
    segs, info = m.transcribe(str(wav), language=langue, word_timestamps=True, vad_filter=True,
                              initial_prompt=(vocab or None))
    out = {"source": str(src.resolve()), "langue": info.language, "segments": []}
    for s in segs:
        out["segments"].append({
            "id": len(out["segments"]), "start": round(s.start, 3), "end": round(s.end, 3),
            "text": s.text.strip(),
            "words": [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for w in (s.words or [])],
        })
    ecrire_json(projet / "transcript.json", out)
    (projet / "transcript.txt").write_text(
        "\n".join(f"[{s['id']:02d}] {s['start']:7.2f} - {s['end']:7.2f}  {s['text']}" for s in out["segments"]) + "\n",
        encoding="utf-8")
    wav.unlink(missing_ok=True)
    print(f"OK : {len(out['segments'])} phrases -> {projet / 'transcript.txt'}")


if __name__ == "__main__":
    main()
