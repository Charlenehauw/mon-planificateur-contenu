# Cosy Colors · Post-partum — 25 dessins au trait générés en SVG (816 x 1056 = 8,5 x 11 po à 96 ppp)
# Usage : python3 dessins.py  -> svg/01.svg ... svg/25.svg
import math, random, os

W, H = 816, 1056
SW = 4.2  # épaisseur du trait principal
ici = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ici, 'svg'), exist_ok=True)

def g(svg, x=0, y=0, s=1, r=0):
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({r:.1f}) scale({s:.3f})">{svg}</g>'

def P(d, fill='#fff', sw=None):
    return f'<path d="{d}" fill="{fill}" stroke="#000" stroke-width="{sw or SW}" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>'

def C(cx, cy, r, fill='#fff', sw=None):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="#000" stroke-width="{sw or SW}" vector-effect="non-scaling-stroke"/>'

def L(d, sw=None):
    return P(d, 'none', sw)

# ——— Motifs de base (centrés sur 0,0, taille ~100) ———
def fleur(n=6, r=50, cr=None, forme=0):
    s = ''
    for i in range(n):
        a = 360 / n * i
        if forme == 0:
            d = f'M0 0 C {r*.55} {-r*.35} {r*.5} {-r} 0 {-r*1.0} C {-r*.5} {-r} {-r*.55} {-r*.35} 0 0Z'
        elif forme == 1:
            d = f'M0 0 C {r*.7} {-r*.2} {r*.7} {-r*.95} 0 {-r} C {-r*.7} {-r*.95} {-r*.7} {-r*.2} 0 0Z'
        else:
            d = f'M0 0 L {r*.3} {-r*.6} Q 0 {-r*1.15} {-r*.3} {-r*.6}Z'
        s += f'<g transform="rotate({a:.1f})">{P(d)}</g>'
        if forme == 1:
            s += f'<g transform="rotate({a:.1f})">{L(f"M0 {-r*.25} L0 {-r*.75}", 1.6)}</g>'
    cr = cr or r * .28
    return s + C(0, 0, cr) + C(0, 0, cr * .45, sw=1.8)

def marguerite(r=50):
    return fleur(12, r, r * .3, 2)

def feuille(l=60, nerv=True):
    d = f'M0 0 C {l*.35} {-l*.2} {l*.4} {-l*.75} 0 {-l} C {-l*.4} {-l*.75} {-l*.35} {-l*.2} 0 0Z'
    s = P(d)
    if nerv:
        s += L(f'M0 {-l*.05} L0 {-l*.85}', 1.6)
        for k in (.3, .5, .7):
            s += L(f'M0 {-l*k} L{l*.16} {-l*(k+.12)} M0 {-l*k} L{-l*.16} {-l*(k+.12)}', 1.4)
    return s

def tulipe(h=120):
    s = L(f'M0 0 C 4 {-h*.4} -4 {-h*.7} 0 {-h}')
    s += g(feuille(h * .5, False), 0, -h * .15, 1, 35) + g(feuille(h * .45, False), 0, -h * .3, 1, -40)
    t = -h
    s += P(f'M-22 {t} C -26 {t-30} -16 {t-48} -10 {t-52} L -4 {t-34} L 0 {t-56} L 4 {t-34} L 10 {t-52} C 16 {t-48} 26 {t-30} 22 {t} C 14 {t+10} -14 {t+10} -22 {t}Z')
    return s

def coeur(r=40):
    return P(f'M0 {r*.9} C {-r*1.4} {-r*.1} {-r*.7} {-r*1.1} 0 {-r*.4} C {r*.7} {-r*1.1} {r*1.4} {-r*.1} 0 {r*.9}Z')

def etoile(r=20, n=5):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * .45
        a = math.pi / n * i - math.pi / 2
        pts.append(f'{rr*math.cos(a):.1f},{rr*math.sin(a):.1f}')
    return P('M' + ' L'.join(pts) + 'Z', sw=2.4)

def nuage(l=120):
    h = l * .45
    return P(f'M{-l/2} 0 C {-l/2-10} {-h*.6} {-l*.25} {-h*.9} {-l*.15} {-h*.6} C {-l*.1} {-h*1.3} {l*.2} {-h*1.3} {l*.2} {-h*.7} C {l*.35} {-h*.95} {l/2+8} {-h*.6} {l/2} 0Z')

def lune(r=60):
    return P(f'M0 {-r} A {r} {r} 0 0 0 0 {r} A {r*.55} {r} 0 0 1 0 {-r}Z')

def tasse(s=1, deco='coeur'):
    o = P('M-60 -50 L 60 -50 L 50 50 C 45 65 -45 65 -50 50Z')
    o += P('M58 -30 C 95 -30 95 30 52 30 L 54 18 C 78 18 78 -18 57 -18Z')
    o += P('M-90 62 C -60 82 60 82 90 62 C 60 54 -60 54 -90 62Z')
    o += L('M-55 -38 L 55 -38', 1.8)
    if deco == 'coeur':
        o += g(coeur(14), 0, 8)
    elif deco == 'fleur':
        o += g(fleur(5, 16), 0, 6)
    for dx in (-25, 0, 25):
        o += L(f'M{dx} -62 C {dx-12} -78 {dx+12} -90 {dx} -108', 2.4)
    return g(o, 0, 0, s)

def pot(s=1):
    o = ''
    for a, l in ((-35, 110), (-10, 140), (15, 125), (40, 100), (-60, 80), (62, 85)):
        o += g(feuille(l), 0, -40, 1, a)
    o += P('M-60 -45 L 60 -45 L 45 60 L -45 60Z') + P('M-68 -60 L 68 -60 L 68 -40 L -68 -40Z')
    o += L('M-50 5 C -25 20 25 -10 50 5', 1.8)
    return g(o, 0, 0, s)

def biberon(s=1):
    o = P('M-30 -40 L 30 -40 L 30 90 C 30 105 -30 105 -30 90Z')
    o += P('M-36 -60 L 36 -60 L 36 -40 L -36 -40Z') + P('M-16 -60 C -16 -95 16 -95 16 -60Z')
    for y in (0, 25, 50, 75):
        o += L(f'M-30 {y} L -14 {y}', 1.8)
    o += g(coeur(10), 8, 40)
    return g(o, 0, 0, s)

def body(s=1):
    o = P('M-45 -70 C -20 -55 20 -55 45 -70 L 80 -45 L 62 -15 L 48 -25 L 48 50 C 48 70 25 80 15 85 L -15 85 C -25 80 -48 70 -48 50 L -48 -25 L -62 -15 L -80 -45Z')
    o += L('M-20 -60 C -10 -45 10 -45 20 -60', 2)
    o += g(coeur(12), 0, 5) + C(-8, 78, 3, sw=2) + C(8, 78, 3, sw=2)
    return g(o, 0, 0, s)

def chaussette(s=1):
    o = P('M-18 -50 L 18 -50 L 18 20 C 18 32 40 30 42 46 C 44 60 26 62 -4 60 C -22 59 -20 40 -18 20Z')
    o += P('M-20 -60 L 20 -60 L 20 -45 L -20 -45Z') + L('M-12 -58 L-12 -47 M-4 -58 L-4 -47 M4 -58 L4 -47 M12 -58 L12 -47', 1.4)
    return g(o, 0, 0, s)

def hochet(s=1):
    o = P('M-6 10 L 6 10 L 6 80 L -6 80Z') + C(0, 88, 12) + C(0, -30, 42)
    o += g(etoile(18), 0, -30)
    return g(o, 0, 0, s)

def tetine(s=1):
    o = P('M-40 0 C -40 -22 40 -22 40 0 C 40 22 -40 22 -40 0Z') + P('M-14 -16 C -14 -50 14 -50 14 -16Z')
    o += C(0, 26, 16, 'none') + C(0, 0, 6, sw=2)
    return g(o, 0, 0, s)

def theiere(s=1):
    o = P('M-70 -10 C -80 -70 80 -70 70 -10 C 75 50 50 70 0 70 C -50 70 -75 50 -70 -10Z')
    o += P('M68 -20 C 110 -40 120 -60 135 -70 L 140 -60 C 125 -40 110 0 72 20Z')
    o += P('M-72 -20 C -120 -30 -120 40 -65 35 L -66 22 C -100 22 -100 -12 -71 -6Z')
    o += P('M-45 -52 C -30 -75 30 -75 45 -52Z') + C(0, -78, 10)
    o += g(fleur(6, 22), 0, 5) + L('M-60 40 C -20 52 20 52 60 40', 1.8)
    return g(o, 0, 0, s)

def livre(s=1):
    o = P('M-90 0 C -60 -12 -20 -12 0 0 C 20 -12 60 -12 90 0 L 90 50 C 60 38 20 38 0 50 C -20 38 -60 38 -90 50Z')
    o += P('M-90 50 L -90 62 C -60 50 -20 50 0 62 C 20 50 60 50 90 62 L 90 50')
    o += L('M0 0 L0 50', 2)
    for y in (12, 22, 32):
        o += L(f'M-75 {y} C -55 {y-6} -30 {y-6} -12 {y}', 1.4) + L(f'M12 {y} C 30 {y-6} 55 {y-6} 75 {y}', 1.4)
    return g(o, 0, 0, s)

def bougie(s=1):
    o = P('M-28 -40 L 28 -40 L 28 60 L -28 60Z') + P('M0 -45 C -14 -60 -6 -80 0 -95 C 6 -80 14 -60 0 -45Z') + L('M0 -40 L0 -50', 2)
    o += P('M-45 60 L 45 60 L 40 72 L -40 72Z') + L('M-28 -30 C -14 -24 14 -24 28 -30', 1.6)
    return g(o, 0, 0, s)

def bocal(s=1):
    o = P('M-55 -60 L 55 -60 C 70 -40 70 80 55 95 L -55 95 C -70 80 -70 -40 -55 -60Z')
    o += P('M-50 -78 L 50 -78 L 50 -60 L -50 -60Z')
    o += P('M-30 -78 C -30 -95 30 -95 30 -78', 'none')
    for x, y, r in ((-25, 20, 18), (20, 50, 15), (15, -10, 13), (-20, 65, 12)):
        o += g(fleur(5, r), x, y)
    o += L('M-55 -40 L 55 -40', 1.6)
    return g(o, 0, 0, s)

def mandala(R=300, couches=5, seed=1):
    rnd = random.Random(seed)
    o = ''
    r = R
    k = 0
    while r > 40 and k < couches:
        n = rnd.choice([8, 10, 12, 16])
        f = rnd.choice([0, 1, 2])
        pr = r * .35
        o += C(0, 0, r, sw=2.6)
        for i in range(n):
            a = 360 / n * i
            if f == 0:
                d = f'M0 {-r+pr} C {pr*.6} {-r+pr*.6} {pr*.4} {-r} 0 {-r-pr*.15} C {-pr*.4} {-r} {-pr*.6} {-r+pr*.6} 0 {-r+pr}Z'
            elif f == 1:
                d = f'M{-pr*.5} {-r+pr} Q 0 {-r-pr*.6} {pr*.5} {-r+pr}Z'
            else:
                d = f'M0 {-r+pr*.95} C {pr*.9} {-r+pr*.5} {pr*.3} {-r-pr*.1} 0 {-r+pr*.25} C {-pr*.3} {-r-pr*.1} {-pr*.9} {-r+pr*.5} 0 {-r+pr*.95}Z'
            o = f'<g transform="rotate({a:.1f})">{P(d, sw=2.4)}</g>' + o if False else o + f'<g transform="rotate({a:.1f})">{P(d, sw=2.4)}{C(0, -r+pr*1.25, pr*.12, sw=1.8)}</g>'
        r -= pr * 1.45
        k += 1
    o += g(fleur(8, max(r, 30)), 0, 0)
    return o

def montgolfiere(s=1):
    o = P('M0 -100 C 70 -100 85 -30 30 40 L -30 40 C -85 -30 -70 -100 0 -100Z')
    o += L('M0 -100 C 30 -60 25 0 10 40 M0 -100 C -30 -60 -25 0 -10 40', 2)
    o += L('M-55 -40 C -20 -30 20 -30 55 -40', 2)
    o += L('M-28 40 L -18 70 M28 40 L 18 70', 2) + P('M-22 70 L 22 70 L 18 95 L -18 95Z')
    return g(o, 0, 0, s)

def nid(s=1):
    o = ''
    for x, r in ((-35, 0), (0, -6), (35, 0)):
        o += P(f'M{x} {-30+r} C {x+26} {-30+r} {x+30} {20} {x} {20} C {x-30} 20 {x-26} {-30+r} {x} {-30+r}Z')
    o += P('M-110 0 C -100 60 100 60 110 0 C 70 25 -70 25 -110 0Z')
    for i in range(9):
        y = 8 + i * 4
        o += L(f'M{-100+i*6} {y} C -40 {y+14} 40 {y+14} {100-i*6} {y}', 1.4)
    return g(o, 0, 0, s)

def soleil(r=80):
    o = ''
    for i in range(12):
        o += f'<g transform="rotate({i*30})">{P(f"M-12 {-r-8} L 0 {-r-50} L 12 {-r-8}Z", sw=2.4)}</g>'
    return o + C(0, 0, r) + C(0, 0, r * .7, sw=1.8)

def arc_en_ciel(R=260, n=5, ep=36):
    o = ''
    for i in range(n):
        r = R - i * ep
        o += P(f'M{-r} 0 A {r} {r} 0 0 1 {r} 0 L {r-ep} 0 A {r-ep} {r-ep} 0 0 0 {-r+ep} 0Z', sw=2.8)
    return o

# ——— Remplissage : petits motifs semés sans chevauchement ———
SEMIS = []
TXT = []
def semer(occupes, motifs, n, zone, rmin=20, rmax=38, seed=0):
    SEMIS.append((occupes, motifs, n, zone, rmin, rmax, seed))
    return f'§S{len(SEMIS)-1}§'

def _semer(occupes, motifs, n, zone, rmin=20, rmax=38, seed=0):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = zone
    o = ''
    essais = 0
    while n and essais < 4000:
        essais += 1
        r = rnd.uniform(rmin, rmax)
        x, y = rnd.uniform(x0 + r, x1 - r), rnd.uniform(y0 + r, y1 - r)
        if any((x - a) ** 2 + (y - b) ** 2 < (r + c + 6) ** 2 for a, b, c in occupes):
            continue
        if any(x + r > a and x - r < c and y + r > b and y - r < d for a, b, c, d in TXT):
            continue
        occupes.append((x, y, r))
        m = rnd.choice(motifs)
        o += g(m(r), x, y, 1, rnd.uniform(-30, 30))
        n -= 1
    return o

PETITS = [lambda r: fleur(5, r * .9), lambda r: etoile(r * .9), lambda r: coeur(r * .7), lambda r: g(feuille(r * 1.6), 0, r * .7),
          lambda r: C(0, 0, r * .35, sw=2) + C(0, 0, r * .12, sw=1.5), lambda r: fleur(8, r * .85, None, 2)]

def texte(t, y, taille=58, police='Quicksand', poids=700, sw=5):
    w = len(t) * taille * .46 + 30
    TXT.append((W/2 - w/2, y - taille * .9, W/2 + w/2, y + taille * .3))
    return (f'<text x="{W/2}" y="{y}" text-anchor="middle" font-family="{police}" font-weight="{poids}" font-size="{taille}" '
            f'fill="#fff" stroke="#000" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke">{t}</text>')

def cadre():
    return f'<rect x="40" y="40" width="{W-80}" height="{H-80}" rx="24" fill="none" stroke="#000" stroke-width="2.4"/>'

def page(contenu, cadre_on=True):
    import re
    contenu = re.sub(r'§S(\d+)§', lambda m: _semer(*SEMIS[int(m.group(1))]), contenu)
    TXT.clear(); SEMIS.clear()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/>{cadre() if cadre_on else ""}{contenu}</svg>')

PAGES = []
def P_(f):
    PAGES.append(f)
    return f

Z = (60, 60, W - 60, H - 60)

@P_
def p01():  # Mug fleuri
    occ = [(W/2, 600, 290), (W/2, 180, 150)]
    o = semer(occ, PETITS, 34, Z, seed=1)
    o += g(tasse(2.8, 'fleur'), W/2, 640)
    for x, y, r in ((250, 420, 34), (560, 430, 30), (180, 820, 28), (640, 830, 32)):
        pass
    o += texte('Un jour', 150, 76, 'Dancing Script', 700) + texte('à la fois', 225, 76, 'Dancing Script', 700)
    return page(o)

@P_
def p02():  # Mandala fleur
    return page(g(mandala(330, 6, 7), W/2, H/2))

@P_
def p03():  # Plante
    occ = [(W/2, 560, 280), (W/2, 160, 150)]
    o = semer(occ, PETITS, 30, Z, seed=3)
    o += g(pot(2.2), W/2, 720)
    o += texte('Je pousse', 130, 72, 'Dancing Script') + texte('à mon rythme', 205, 72, 'Dancing Script')
    return page(o)

@P_
def p04():  # Pause thé
    occ = [(W/2, 560, 300), (W/2, 160, 110)]
    o = semer(occ, PETITS, 28, Z, seed=4)
    o += g(theiere(2), 330, 560) + g(tasse(1.25, 'coeur'), 600, 690) + g(tasse(1.0, 'fleur'), 180, 790)
    o += texte('Pause thé', 190, 90, 'Dancing Script')
    return page(o)

@P_
def p05():  # Corde à linge
    o = L('M60 300 C 250 380 560 380 756 300', 2.6)
    for x, f, s in ((170, body, 1.2), (330, chaussette, 1.1), (470, body, 1.3), (640, chaussette, 1.1)):
        y = 300 + 80 * math.sin(math.pi * (x - 60) / 696)
        o += g(f(s), x, y + 95 * s)
        o += P(f'M{x-6} {y-14} L {x+6} {y-14} L {x+6} {y+14} L {x-6} {y+14}Z', sw=2)
    occ = [(W/2, 400, 330), (W/2, 140, 100), (W/2, 840, 140)]
    o = semer(occ, PETITS, 30, Z, seed=5) + o
    o += texte('Petits vêtements,', 800, 62, 'Dancing Script') + texte('grand amour', 880, 62, 'Dancing Script')
    return page(o)

@P_
def p06():  # Lune et nuages
    occ = [(W/2, 470, 240), (W/2, 840, 130)]
    o = ''
    rnd = random.Random(6)
    for _ in range(40):
        x, y = rnd.uniform(80, W - 80), rnd.uniform(80, 700)
        if (x - W/2) ** 2 + (y - 470) ** 2 > 260 ** 2:
            o += g(etoile(rnd.uniform(8, 18)), x, y, 1, rnd.uniform(0, 70))
    o += g(lune(190), W/2 + 30, 450) + g(nuage(300), W/2 - 80, 640) + g(nuage(220), W/2 + 170, 600)
    o += texte('Les nuits sont longues,', 840, 52, 'Dancing Script') + texte('mais je ne suis pas seule', 910, 52, 'Dancing Script')
    return page(o)

@P_
def p07():  # Arc-en-ciel
    o = g(arc_en_ciel(300, 6, 40), W/2, 640) + g(nuage(260), W/2 - 270, 655) + g(nuage(260), W/2 + 270, 655)
    occ = [(W/2, 520, 330), (W/2, 160, 100), (W/2, 840, 120)]
    o = semer(occ, PETITS, 26, Z, seed=7) + o
    o += texte('Après la pluie,', 820, 66, 'Dancing Script') + texte('le soleil revient', 895, 66, 'Dancing Script')
    return page(o)

@P_
def p08():  # Grand bouquet
    o = ''
    tiges = [(-120, 420), (-60, 470), (0, 500), (60, 470), (120, 420), (-90, 340), (90, 340), (0, 380)]
    for dx, h in tiges:
        o += L(f'M{W/2} 930 C {W/2+dx*.2} {930-h*.5} {W/2+dx} {930-h*.8} {W/2+dx*1.3} {930-h}')
    for dx, h in tiges:
        o += g(feuille(70), W/2 + dx * .7, 930 - h * .55, 1, dx * .4)
    rnd = random.Random(8)
    for i, (dx, h) in enumerate(tiges):
        o += g(fleur(rnd.choice([5, 6, 8]), rnd.uniform(55, 75), None, i % 3), W/2 + dx * 1.3, 930 - h)
    o += P(f'M{W/2-90} 820 L {W/2+90} 820 L {W/2+50} 960 L {W/2-50} 960Z') + g(coeur(22), W/2, 885)
    return page(o)

@P_
def p09():  # Motif bébé
    rnd = random.Random(9)
    o = ''
    items = [biberon, hochet, tetine, chaussette, body]
    for j, y in enumerate(range(150, 1000, 200)):
        for i, x in enumerate(range(130 + (j % 2) * 90, W - 60, 190)):
            f = items[(i + j) % len(items)]
            o += g(f(.75), x, y, 1, rnd.uniform(-15, 15))
    return page(o)

@P_
def p10():  # Mandala coeur
    o = g(coeur(300), W/2, 470)
    o += g(mandala(170, 4, 10), W/2, 470)
    occ = [(W/2, 470, 330)]
    o = semer(occ, PETITS, 26, Z, seed=10) + o
    return page(o)

@P_
def p11():  # Fenêtre cocon
    o = P('M190 120 L 626 120 L 626 760 L 190 760Z') + P('M210 140 L 596 140 L 596 740 L 210 740Z', sw=2)
    o += L('M408 140 L 408 740 M210 440 L 596 440', 2.6)
    rnd = random.Random(11)
    for _ in range(60):
        x, y = rnd.uniform(225, 585), rnd.uniform(155, 720)
        o += L(f'M{x:.0f} {y:.0f} l -6 18', 1.6)
    o += P('M150 760 L 666 760 L 680 800 L 136 800Z')
    o += g(pot(.9), 260, 700) + g(tasse(.8, 'coeur'), 420, 728) + g(pot(.75), 560, 712)
    o += g(nuage(130), 330, 250) + g(nuage(110), 500, 330)
    o += texte('Mon cocon', 900, 90, 'Dancing Script')
    return page(o)

@P_
def p12():  # Livre bougie tasse
    occ = [(W/2, 600, 300), (W/2, 180, 140)]
    o = semer(occ, PETITS, 30, Z, seed=12)
    o += g(bougie(2), 230, 500) + g(tasse(1.5, 'fleur'), 590, 540) + g(livre(3), W/2, 720)
    o += texte('Douceur', 190, 100, 'Dancing Script')
    return page(o)

@P_
def p13():  # Plaid patchwork
    o = ''
    rnd = random.Random(13)
    for i in range(5):
        for j in range(6):
            x, y = 108 + i * 120, 130 + j * 135
            o += P(f'M{x} {y} L {x+120} {y} L {x+120} {y+135} L {x} {y+135}Z', sw=2.6)
            cx, cy = x + 60, y + 67
            k = (i + j) % 4
            if k == 0: o += g(fleur(6, 38), cx, cy)
            elif k == 1: o += g(coeur(28), cx, cy)
            elif k == 2: o += g(etoile(34), cx, cy)
            else:
                for d in range(-40, 50, 20):
                    o += L(f'M{x+8} {cy+d} C {cx-20} {cy+d-10} {cx+20} {cy+d+10} {x+112} {cy+d}', 1.6)
    return page(o)

@P_
def p14():  # Mobile
    o = P(f'M{W/2-260} 200 C {W/2-100} 160 {W/2+100} 160 {W/2+260} 200', 'none') + L(f'M{W/2} 90 L {W/2} 175', 2.4)
    elems = [(-240, 380, lambda: lune(55)), (-120, 520, lambda: nuage(140)), (0, 430, lambda: etoile(60)),
             (120, 560, lambda: coeur(55)), (240, 380, lambda: nuage(130))]
    for dx, y, f in elems:
        x0 = W/2 + dx
        yb = 200 - 40 * math.cos(math.pi * dx / 520) + 40
        o += L(f'M{x0} {yb-30} L {x0} {y-50}', 1.8) + g(f(), x0, y)
    o += C(W/2, 90, 14)
    occ = [(W/2, 400, 340), (W/2, 860, 130)]
    o = semer(occ, PETITS, 22, Z, seed=14) + o
    o += texte('Dors, mon trésor', 860, 76, 'Dancing Script')
    return page(o)

@P_
def p15():  # Mandala étoile
    o = ''
    for i in range(8):
        o += f'<g transform="translate({W/2} {H/2}) rotate({i*45})">{P("M0 -340 L 60 -150 L 0 -120 L -60 -150Z")}{g(fleur(5, 26), 0, -230)}</g>'
    o += g(mandala(200, 5, 15), W/2, H/2)
    return page(o)

@P_
def p16():  # Couronne « Respire »
    o = ''
    rnd = random.Random(16)
    n = 22
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = W/2 + 280 * math.cos(a), 520 + 280 * math.sin(a)
        o += g(feuille(80), x, y, 1, math.degrees(a) + 90 + rnd.uniform(-30, 30))
    for i in range(8):
        a = 2 * math.pi * i / 8 + .2
        o += g(fleur(rnd.choice([5, 6]), 44, None, i % 3), W/2 + 280 * math.cos(a), 520 + 280 * math.sin(a))
    o += texte('Respire', 545, 120, 'Dancing Script')
    return page(o)

@P_
def p17():  # Jardin de tulipes
    o = ''
    rnd = random.Random(17)
    for k, y in enumerate((520, 760, 1000)):
        for x in range(120 + (k % 2) * 60, W - 60, 120):
            o += g(tulipe(rnd.uniform(140, 190)), x, y - 40, .95)
    o += g(soleil(60), 640, 180) + g(nuage(180), 220, 200)
    return page(o)

@P_
def p18():  # Coeur fleuri « Maman en construction »
    o = g(coeur(320), W/2, 440)
    occ = [(W/2, 860, 140)]
    rnd = random.Random(18)
    inner = ''
    pts = []
    for _ in range(3000):
        x, y = rnd.uniform(160, 656), rnd.uniform(200, 720)
        u, v = (x - W/2) / 320, -(y - 470) / 320
        if (u * u + v * v - .9) ** 3 - u * u * v ** 3 < -.02:  # intérieur du coeur
            r = rnd.uniform(26, 44)
            if all((x - a) ** 2 + (y - b) ** 2 > (r + c + 4) ** 2 for a, b, c in pts):
                pts.append((x, y, r))
                inner += g(fleur(rnd.choice([5, 6, 8]), r, None, rnd.choice([0, 1, 2])) if rnd.random() < .7 else feuille(r * 1.6), x, y, 1, rnd.uniform(0, 360))
    o += inner
    o += texte('Maman', 840, 74, 'Dancing Script') + texte('en construction', 915, 74, 'Dancing Script')
    return page(o)

@P_
def p19():  # Bocal tisane
    occ = [(W/2, 560, 280), (W/2, 150, 110)]
    o = semer(occ, PETITS, 30, Z, seed=19)
    o += g(bocal(2.5), W/2, 560)
    o += texte('Prendre soin', 130, 72, 'Dancing Script') + texte('de moi', 205, 72, 'Dancing Script')
    return page(o)

@P_
def p20():  # Panier à linge
    o = P('M230 520 L 586 520 L 550 860 L 266 860Z')
    for y in range(560, 860, 40):
        o += L(f'M{240+(y-520)*.1:.0f} {y} L {576-(y-520)*.1:.0f} {y}', 1.6)
    o += P('M210 500 L 606 500 L 606 530 L 210 530Z')
    o += g(body(1.1), 330, 450, 1, -20) + g(chaussette(1.1), 470, 450, 1, 25) + g(body(.9), 540, 470, 1, 15)
    occ = [(W/2, 650, 260), (W/2, 160, 110), (W/2, 930, 70)]
    o = semer(occ, PETITS, 26, Z, seed=20) + o
    o += texte('Le linge', 150, 80, 'Dancing Script') + texte('peut attendre', 230, 80, 'Dancing Script')
    return page(o)

@P_
def p21():  # Montgolfières
    o = ''
    for x, y, s in ((250, 360, 1.9), (560, 280, 1.4), (580, 650, 1.6), (220, 760, 1.1)):
        o += g(montgolfiere(s), x, y)
    for x, y, l in ((420, 160, 180), (130, 530, 150), (420, 500, 170), (680, 900, 150), (400, 900, 190)):
        o += g(nuage(l), x, y)
    return page(o)

@P_
def p22():  # Mandala feuilles
    o = ''
    for i in range(16):
        o += f'<g transform="translate({W/2} {H/2}) rotate({i*22.5})">{g(feuille(140), 0, -200)}</g>'
    o += g(mandala(180, 4, 22), W/2, H/2)
    for i in range(16):
        o += f'<g transform="translate({W/2} {H/2}) rotate({i*22.5+11})">{g(fleur(5, 22), 0, -360)}</g>'
    return page(o)

@P_
def p23():  # « Tu fais de ton mieux »
    o = ''
    rnd = random.Random(23)
    for x, y, r in ((170, 200, 60), (640, 210, 55), (130, 880, 58), (680, 860, 62), (400, 140, 40), (420, 930, 45)):
        o += g(fleur(rnd.choice([6, 8]), r, None, rnd.choice([0, 1])), x, y)
    for x, y, a in ((250, 250, 40), (560, 260, -40), (230, 820, 140), (590, 820, -140)):
        o += g(feuille(90), x, y, 1, a)
    o += texte('Tu fais', 450, 110, 'Dancing Script') + texte('de ton mieux,', 570, 110, 'Dancing Script') + texte('et c\'est assez', 690, 110, 'Dancing Script')
    return page(o)

@P_
def p24():  # Lever de soleil
    o = g(soleil(110), W/2, 470)
    o += P(f'M60 560 C 200 470 330 520 420 580 C 520 500 650 470 756 540 L 756 996 L 60 996Z')
    o += P(f'M60 700 C 220 620 420 690 756 640 L 756 996 L 60 996Z')
    o += P(f'M60 840 C 260 780 520 860 756 800 L 756 996 L 60 996Z')
    rnd = random.Random(24)
    for _ in range(14):
        o += g(fleur(5, 14), rnd.uniform(100, 700), rnd.uniform(890, 960))
    o += g(nuage(160), 180, 300) + g(nuage(140), 640, 330)
    o += texte('Chaque matin', 150, 70, 'Dancing Script') + texte('est un nouveau départ', 225, 70, 'Dancing Script')
    return page(o)

@P_
def p25():  # Nid douillet
    o = L('M60 640 C 260 600 560 620 756 560', 6) + g(feuille(90), 160, 625, 1, 60) + g(feuille(80), 680, 585, 1, -70)
    o += g(nid(3.2), W/2, 560)
    occ = [(W/2, 520, 300), (W/2, 840, 130)]
    o = semer(occ, PETITS, 26, Z, seed=25) + o
    o += texte('Un nid', 820, 76, 'Dancing Script') + texte('rempli d\'amour', 900, 76, 'Dancing Script')
    return page(o)

for i, f in enumerate(PAGES, 1):
    open(os.path.join(ici, 'svg', f'{i:02d}.svg'), 'w').write(f())
print(len(PAGES), 'dessins')
