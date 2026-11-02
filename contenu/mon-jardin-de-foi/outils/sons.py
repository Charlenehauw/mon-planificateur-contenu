"""Bruitages et ambiances nature synthétisés (aucune musique) pour les reels Mon Jardin de Foi.
Usage : python3 sons.py <ambiance> <duree> <evenements.json> <sortie.wav>
ambiance : jardin | pluie | aube | brise | nuit
"""
import json, sys, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    b = 1 - a
    for i in range(len(x)):
        acc = b * x[i] + a * acc
        y[i] = acc
    return y


def lp(x, fc, n=2):
    for _ in range(n):
        x = onepole_lp(x, fc)
    return x


def hp(x, fc):
    return x - lp(x, fc, 1)


def norm(x):
    m = np.max(np.abs(x)) or 1
    return x / m


def vent(n, force=1.0):
    w = rng.standard_normal(n)
    b = norm(lp(w, 380, 2))
    t = np.arange(n) / SR
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.09 * t + 1.3) * np.sin(2 * np.pi * 0.033 * t + 0.4)
    return b * lfo * 0.22 * force


def pluie(n):
    w = rng.standard_normal(n)
    fond = norm(lp(hp(w, 900), 5200, 1)) * 0.10
    out = fond.copy()
    nb = int(n / SR * 26)
    for _ in range(nb):
        p = rng.integers(0, n - 4000)
        L = rng.integers(300, 1600)
        env = np.exp(-np.arange(L) / (L / 5))
        burst = rng.standard_normal(L) * env * rng.uniform(0.02, 0.07)
        out[p:p + L] += hp(burst, 1500)
    return out


def oiseau(dur_tot, densite=1.0):
    n = int(dur_tot * SR)
    out = np.zeros(n)
    t = rng.uniform(0.3, 1.2)
    while t < dur_tot - 1:
        base = rng.uniform(2800, 4600)
        nb = rng.integers(2, 6)
        for k in range(nb):
            L = int(rng.uniform(0.05, 0.13) * SR)
            tt = np.arange(L) / SR
            sens = rng.choice([-1, 1])
            f = base + sens * rng.uniform(400, 1400) * (tt / tt[-1]) + 120 * np.sin(2 * np.pi * 38 * tt)
            ph = 2 * np.pi * np.cumsum(f) / SR
            env = np.sin(np.pi * tt / tt[-1]) ** 2
            s = np.sin(ph) * env * rng.uniform(0.04, 0.09)
            p = int((t + k * rng.uniform(0.12, 0.2)) * SR)
            if p + L < n:
                out[p:p + L] += s
        t += rng.uniform(1.4, 3.2) / densite
    return out


def grillons(n):
    out = np.zeros(n)
    for f0, decal, vol in [(4300, 0.0, 0.035), (4720, 0.31, 0.025)]:
        t = decal
        while t < n / SR - 0.5:
            for k in range(3):
                L = int(0.028 * SR)
                tt = np.arange(L) / SR
                s = np.sin(2 * np.pi * f0 * tt) * np.sin(np.pi * tt / tt[-1]) * vol
                p = int((t + k * 0.045) * SR)
                out[p:p + L] += s
            t += rng.uniform(0.55, 0.75)
    return out


def cloche(f, L=2.4, vol=0.16):
    tt = np.arange(int(L * SR)) / SR
    s = np.zeros_like(tt)
    for mult, amp, dec in [(1, 1, 1.6), (2.76, 0.35, 0.9), (5.4, 0.15, 0.5), (2.0, 0.25, 1.2)]:
        s += amp * np.sin(2 * np.pi * f * mult * tt) * np.exp(-tt / dec)
    att = np.minimum(1, tt / 0.004)
    return s * att * vol


def effet(type_):
    if type_ == 'carillon':
        L = int(2.8 * SR)
        s = np.zeros(L)
        for k, f in enumerate([1318.5, 1568.0, 2093.0]):
            c = cloche(f, 2.4, 0.11)
            p = int(k * 0.09 * SR)
            s[p:p + len(c)] += c[: L - p]
        return s
    if type_ == 'carillon2':
        a = cloche(784.0, 2.6, 0.13); b = cloche(1174.7, 2.0, 0.05); a[:len(b)] += b; return a
    if type_ == 'pop':
        L = int(0.09 * SR)
        tt = np.arange(L) / SR
        f = 520 + 600 * tt / tt[-1]
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.025) * 0.22
    if type_ == 'tick':
        L = int(0.035 * SR)
        tt = np.arange(L) / SR
        return (hp(rng.standard_normal(L), 2500) * 0.12 + np.sin(2 * np.pi * 2300 * tt) * 0.08) * np.exp(-tt / 0.008)
    raise ValueError(type_)


def main():
    amb, duree, evts, sortie = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
    n = int(duree * SR)
    if amb == 'jardin':
        x = vent(n, 0.9) + oiseau(duree, 1.0)
    elif amb == 'pluie':
        x = pluie(n) + vent(n, 0.5)
    elif amb == 'aube':
        x = vent(n, 0.7) + oiseau(duree, 1.6)
    elif amb == 'brise':
        x = vent(n, 1.0) + oiseau(duree, 0.5) * 0.6
    elif amb == 'nuit':
        x = grillons(n) + vent(n, 0.55)
    else:
        raise ValueError(amb)
    for e in json.load(open(evts)):
        s = effet(e['type'])
        p = int(e['t'] * SR)
        if p < n:
            x[p:p + len(s)] += s[: n - p]
    t = np.arange(n) / SR
    x *= np.minimum(1, t / 0.6) * np.minimum(1, (duree - t) / 1.2)
    x = x / max(np.max(np.abs(x)), 1e-6) * 0.7
    # léger élargissement stéréo
    d = int(0.011 * SR)
    g = np.concatenate([np.zeros(d), x[:-d]])
    st = np.stack([x * 0.9 + g * 0.1, x * 0.75 + g * 0.25], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
    with wave.open(sortie, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main()
