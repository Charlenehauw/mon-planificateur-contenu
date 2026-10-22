#!/usr/bin/env python3
"""Étape 2. Coupes automatiques : hésitations, phrases reprises, faux départs, blancs.

Règle d'or : on ne demande JAMAIS un temps de coupe à une IA. Les temps viennent des mots.
Claude ne décide qu'en numéros de phrases, avec --retirer et --garder.

Usage : python moteur/couper.py <dossier_projet> [--retirer 3,7] [--garder 5]
Sort : coupes.json (plages gardées) et rapport-coupes.md (à relire).
"""
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils import lire_json, ecrire_json

HESITATIONS = {"euh", "heu", "hum", "hmm", "bah", "ben", "euhm", "mmh", "um", "uh", "eh"}
SIMILARITE_REPRISE = 0.72
MARGE_AVANT, MARGE_APRES, PAUSE_MAX = 0.08, 0.12, 0.35


def norm(t):
    return re.sub(r"[^a-zà-ÿ0-9 ]", "", t.lower()).strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    projet = Path(args[0])
    lst = lambda k: {int(x) for x in sys.argv[sys.argv.index(k) + 1].split(",") if x} if k in sys.argv else set()
    retirer, garder = lst("--retirer"), lst("--garder")
    segs = lire_json(projet / "transcript.json")["segments"]
    retires = {}
    for s in segs:
        mots = norm(s["text"]).split()
        if mots and all(m in HESITATIONS for m in mots):
            retires[s["id"]] = "hésitation seule"
    for i, s in enumerate(segs):
        if s["id"] in retires:
            continue
        for j in range(i + 1, min(i + 3, len(segs))):
            n = segs[j]
            if n["id"] in retires:
                continue
            a, b = norm(s["text"]), norm(n["text"])
            if len(a.split()) >= 3 and difflib.SequenceMatcher(None, a, b).ratio() >= SIMILARITE_REPRISE:
                retires[s["id"]] = f"phrase reprise (la bonne prise est la {n['id']})"
                break
            if j == i + 1 and len(a.split()) <= 4 and b.startswith(a[: max(8, len(a) - 2)]) and len(b) > len(a):
                retires[s["id"]] = f"faux départ (repris en {n['id']})"
                break
    for k in garder:
        retires.pop(k, None)
    for k in retirer:
        retires[k] = "retiré à la relecture"

    gardes = [s for s in segs if s["id"] not in retires and s["words"]]
    plages = []
    for s in gardes:
        mots = [w for w in s["words"] if norm(w["w"]) not in HESITATIONS] or s["words"]
        d, f = max(0.0, mots[0]["s"] - MARGE_AVANT), mots[-1]["e"] + MARGE_APRES
        if plages and d - plages[-1]["fin"] <= PAUSE_MAX:
            plages[-1]["fin"] = round(f, 3)
            plages[-1]["phrases"].append(s["id"])
        else:
            plages.append({"debut": round(d, 3), "fin": round(f, 3), "phrases": [s["id"]]})
    ecrire_json(projet / "coupes.json", {"plages": plages})
    total = sum(p["fin"] - p["debut"] for p in plages)
    l = ["# Rapport de coupes", "", f"Durée gardée : {total:.1f} s, {len(plages)} plans.", "", "## Retiré"]
    l += [f"- [{k:02d}] « {next(s for s in segs if s['id'] == k)['text']} » ({v})" for k, v in sorted(retires.items())] or ["- rien"]
    l += ["", "## Gardé"] + [f"- [{s['id']:02d}] {s['text']}" for s in gardes]
    (projet / "rapport-coupes.md").write_text("\n".join(l) + "\n", encoding="utf-8")
    print(f"OK : {len(plages)} plans, {total:.1f} s gardées. Relire : {projet / 'rapport-coupes.md'}")


if __name__ == "__main__":
    main()
