"""Générateur de mandalas uniques (vectoriels, zones fermées prêtes à colorier)."""
import math
import random

from lib.core import TRIM_W, TRIM_H, INCH, ink, fill_white_stroke, petal_path, star_path, frame, scatter

LW = 1.5


def _circle(ctx, cx, cy, r, lw=LW):
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    fill_white_stroke(ctx, lw)


def ring_petals(ctx, cx, cy, r0, r1, n, rot, rng, pointed=None, inner=True):
    pointed = rng.random() < 0.5 if pointed is None else pointed
    hw = min((r0 + r1) / 2 * math.pi / n * 0.95, (r1 - r0) * 0.6)
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        petal_path(ctx, cx, cy, r0, r1, a, hw, pointed)
        fill_white_stroke(ctx, LW)
        if inner and r1 - r0 > 22:
            petal_path(ctx, cx, cy, r0 + (r1 - r0) * 0.12, r0 + (r1 - r0) * 0.7, a, hw * 0.45, True)
            fill_white_stroke(ctx, LW * 0.8)


def ring_beads(ctx, cx, cy, r0, r1, n, rot, rng):
    rm = (r0 + r1) / 2
    rb = min((r1 - r0) / 2 * 0.85, rm * math.pi / n * 0.85)
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        x, y = cx + rm * math.cos(a), cy + rm * math.sin(a)
        _circle(ctx, x, y, rb)
        if rb > 7:
            _circle(ctx, x, y, rb * 0.45, LW * 0.8)


def ring_scallops(ctx, cx, cy, r0, r1, n, rot, rng):
    ink(ctx, LW)
    ctx.new_path()
    ctx.arc(cx, cy, r0, 0, 2 * math.pi)
    ctx.stroke()
    for k in range(2 if r1 - r0 > 24 else 1):
        rr = r1 - k * (r1 - r0) * 0.45
        ctx.new_path()
        for i in range(n):
            a0 = rot + (i + 0.5 * k) * 2 * math.pi / n
            a1 = a0 + 2 * math.pi / n
            am = (a0 + a1) / 2
            p0 = (cx + r0 * math.cos(a0), cy + r0 * math.sin(a0))
            pm = (cx + rr * 1.08 * math.cos(am), cy + rr * 1.08 * math.sin(am))
            p1 = (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1))
            ctx.move_to(*p0)
            ctx.curve_to(cx + rr * math.cos(a0 + 0.1 / n), cy + rr * math.sin(a0 + 0.1 / n),
                         pm[0], pm[1], pm[0], pm[1])
            ctx.curve_to(pm[0], pm[1], cx + rr * math.cos(a1 - 0.1 / n), cy + rr * math.sin(a1 - 0.1 / n), *p1)
        ink(ctx, LW)
        ctx.stroke()


def ring_zigzag(ctx, cx, cy, r0, r1, n, rot, rng):
    ink(ctx, LW)
    for r in (r0, r1):
        ctx.new_path(); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.stroke()
    ctx.new_path()
    for i in range(2 * n + 1):
        a = rot + i * math.pi / n
        r = r0 if i % 2 == 0 else r1
        (ctx.move_to if i == 0 else ctx.line_to)(cx + r * math.cos(a), cy + r * math.sin(a))
    ctx.stroke()
    if rng.random() < 0.6 and r1 - r0 > 16:
        for i in range(n):
            a = rot + (i + 0.5) * 2 * math.pi / n * 1.0
            a = rot + (2 * i + 1) * math.pi / n
            rr = r0 + (r1 - r0) * 0.38
            _circle(ctx, cx + rr * math.cos(a - math.pi / n), cy + rr * math.sin(a - math.pi / n),
                    min((r1 - r0) * 0.14, 6), LW * 0.8)


def ring_lattice(ctx, cx, cy, r0, r1, n, rot, rng):
    ink(ctx, LW)
    for r in (r0, r1):
        ctx.new_path(); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.stroke()
    for sgn in (1, -1):
        for i in range(n):
            a0 = rot + i * 2 * math.pi / n
            a1 = a0 + sgn * 2 * math.pi / n
            ctx.new_path()
            steps = 16
            for s in range(steps + 1):
                t = s / steps
                a = a0 + (a1 - a0) * t
                r = r0 + (r1 - r0) * t
                (ctx.move_to if s == 0 else ctx.line_to)(cx + r * math.cos(a), cy + r * math.sin(a))
            ctx.stroke()


def ring_rays(ctx, cx, cy, r0, r1, n, rot, rng):
    ink(ctx, LW)
    for r in (r0, r1):
        ctx.new_path(); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.stroke()
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        ctx.move_to(cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        ctx.line_to(cx + r1 * math.cos(a), cy + r1 * math.sin(a))
    ctx.stroke()
    rm = (r0 + r1) / 2
    for i in range(n):
        a = rot + (i + 0.5) * 2 * math.pi / n
        rr = min((r1 - r0) * 0.28, rm * math.pi / n * 0.5)
        if rr > 3:
            if rng.random() < 0.5:
                _circle(ctx, cx + rm * math.cos(a), cy + rm * math.sin(a), rr, LW * 0.8)
            else:
                star_path(ctx, cx + rm * math.cos(a), cy + rm * math.sin(a), rr * 1.3, 4, 0.45, a)
                fill_white_stroke(ctx, LW * 0.8)


def ring_arches(ctx, cx, cy, r0, r1, n, rot, rng):
    """Arches gothiques (ogives) imbriquées."""
    for k, scale in enumerate((1.0, 0.62)):
        top = r0 + (r1 - r0) * scale
        for i in range(n):
            a0 = rot + i * 2 * math.pi / n
            a1 = a0 + 2 * math.pi / n
            am = (a0 + a1) / 2
            ctx.new_path()
            ctx.move_to(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0))
            c1 = r0 + (top - r0) * 0.9
            ctx.curve_to(cx + c1 * math.cos(a0), cy + c1 * math.sin(a0),
                         cx + top * math.cos(am - 0.15 / n), cy + top * math.sin(am - 0.15 / n),
                         cx + top * math.cos(am), cy + top * math.sin(am))
            ctx.curve_to(cx + top * math.cos(am + 0.15 / n), cy + top * math.sin(am + 0.15 / n),
                         cx + c1 * math.cos(a1), cy + c1 * math.sin(a1),
                         cx + r0 * math.cos(a1), cy + r0 * math.sin(a1))
            ctx.close_path()
            fill_white_stroke(ctx, LW if k == 0 else LW * 0.8)


def ring_leaves(ctx, cx, cy, r0, r1, n, rot, rng):
    ink(ctx, LW)
    ctx.new_path(); ctx.arc(cx, cy, r0, 0, 2 * math.pi); ctx.stroke()
    hw = min((r0 + r1) / 2 * math.pi / n * 0.6, (r1 - r0) * 0.35)
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        for side in (-1, 1):
            aa = a + side * math.pi / n * 0.45
            petal_path(ctx, cx, cy, r0, r1 * 0.97, aa, hw * 0.8, True)
            fill_white_stroke(ctx, LW)
            ink(ctx, LW * 0.6)
            ctx.move_to(cx + r0 * math.cos(aa), cy + r0 * math.sin(aa))
            ctx.line_to(cx + (r1 * 0.85) * math.cos(aa), cy + (r1 * 0.85) * math.sin(aa))
            ctx.stroke()


RINGS = [ring_petals, ring_beads, ring_scallops, ring_zigzag, ring_lattice, ring_rays, ring_arches, ring_leaves]


def mandala(ctx, cx, cy, R, rng, lw=1.5, kids=False):
    global LW
    LW = lw
    base = rng.choice([6, 8, 8, 10, 12, 12, 16])
    # découpage en anneaux (de l'extérieur vers l'intérieur pour superposition correcte)
    radii = [R]
    r = R
    while r > R * 0.18:
        step = rng.uniform(0.08, 0.14) * R * (1.5 if kids else 1)
        r -= step
        radii.append(max(r, R * 0.12))
    radii[-1] = R * rng.uniform(0.1, 0.16)
    rings = list(zip(radii[1:], radii[:-1]))           # (r0, r1) de l'extérieur vers le centre
    last = None
    for idx, (r0, r1) in enumerate(rings):
        choices = [f for f in RINGS if f is not last]
        if idx == 0:
            choices = [ring_petals, ring_arches, ring_scallops, ring_leaves]
        f = rng.choice(choices)
        last = f
        mult = rng.choice([1, 1, 2]) if r1 > R * 0.5 else rng.choice([1, 1, 0.5])
        n = max(4, int(base * mult))
        if kids:
            n = max(4, min(n, 12))
        rot = rng.choice([0, math.pi / n])
        # disque de fond fermé de l'anneau
        ctx.new_path(); ctx.arc(cx, cy, r1, 0, 2 * math.pi); fill_white_stroke(ctx, LW)
        f(ctx, cx, cy, r0, r1, n, rot, rng)
    # cœur
    rc = radii[-1]
    _circle(ctx, cx, cy, rc)
    if rng.random() < 0.5:
        star_path(ctx, cx, cy, rc * 0.85, base // 2 if base // 2 >= 4 else base, 0.5)
        fill_white_stroke(ctx, LW)
    else:
        ring_petals(ctx, cx, cy, rc * 0.2, rc * 0.9, max(5, base // 2), 0, rng, inner=False)
    _circle(ctx, cx, cy, rc * 0.18)


def page(seed, kids=False, decor=True):
    def draw(ctx):
        rng = random.Random(seed)
        cx, cy = TRIM_W / 2, TRIM_H / 2
        R = (TRIM_W - 2 * 0.75 * INCH) / 2
        style = rng.random()
        if decor and style < 0.35:
            # mandala + motifs dans les coins
            frame(ctx, rng.choice(['simple', 'double']), 0.6 * INCH, 0.6 * INCH,
                  TRIM_W - 1.2 * INCH, TRIM_H - 1.2 * INCH, rng)
            mandala(ctx, cx, cy, R * 0.92, rng, lw=1.4)
            for (x, y) in [(0.6 * INCH, 0.6 * INCH), (TRIM_W - 0.6 * INCH, 0.6 * INCH),
                           (0.6 * INCH, TRIM_H - 0.6 * INCH), (TRIM_W - 0.6 * INCH, TRIM_H - 0.6 * INCH)]:
                pass
            for yy in (1.6 * INCH, TRIM_H - 1.6 * INCH):
                for xx in (1.6 * INCH, TRIM_W - 1.6 * INCH):
                    mandala(ctx, xx, yy, 0.75 * INCH, random.Random(seed * 7 + 1), lw=1.1, kids=True)
        elif decor and style < 0.55:
            # mandala principal + petit mandala haut et bas
            mandala(ctx, cx, cy, R, rng, lw=1.5 if not kids else 3)
            sub = random.Random(seed + 999)
            for yy in (1.35 * INCH, TRIM_H - 1.35 * INCH):
                mandala(ctx, cx, yy, 0.65 * INCH, sub, lw=1.1, kids=True)
        else:
            mandala(ctx, cx, cy, R * (1.0 if style < 0.85 else 0.95), rng, lw=1.5 if not kids else 3, kids=kids)
    return draw


def pages(book):
    return [page(book['seed'] * 1000 + i, kids=book.get('kids', False)) for i in range(50)]


def hero_draw(seed, size):
    def draw(ctx):
        rng = random.Random(seed)
        mandala(ctx, size / 2, size / 2, size / 2 - 4, rng, lw=1.6)
    return draw
