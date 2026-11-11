"""Coloriages à faire en couple : chaque page est partagée en deux zones « Toi » / « Moi »."""
import math
import random

from lib.core import TRIM_W, TRIM_H, INCH, ink, fill_white_stroke, heart_path, draw_text, frame, scatter
from generators import mandala as MG
from generators import quotes as QG


def split_line(ctx, x0, y0, x1, y1):
    ink(ctx, 2.2)
    ctx.set_dash([10, 7])
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
    ctx.set_dash([])


def labels(ctx, a, b):
    for (x, y), t in zip((a, b), ("Toi", "Moi")):
        draw_text(ctx, t, x, y, 'Great Vibes', 34)


def page(idx, seed):
    def draw(ctx):
        rng = random.Random(seed)
        style = idx % 4
        cx, cy = TRIM_W / 2, TRIM_H / 2
        if style == 0:      # grand cœur rempli de mandala, coupé en deux
            s = 3.9 * INCH
            ctx.save()
            heart_path(ctx, cx, cy - 0.2 * INCH, s)
            ctx.clip()
            MG.mandala(ctx, cx, cy - 0.35 * INCH, s * 1.1, rng, lw=1.4)
            ctx.restore()
            heart_path(ctx, cx, cy - 0.2 * INCH, s); ink(ctx, 3); ctx.stroke()
            split_line(ctx, cx, 0.9 * INCH, cx, TRIM_H - 0.9 * INCH)
            scatter(ctx, rng, (0.6 * INCH, 0.6 * INCH, TRIM_W - 1.2 * INCH, TRIM_H - 1.2 * INCH), ['heart', 'sparkle', 'dot'],
                    avoid=[(cx - s * 1.35, cy - s * 1.25, s * 2.7, s * 2.4), (cx - 8, 0, 16, TRIM_H)], count=26, rmin=10, rmax=22)
            labels(ctx, (1.3 * INCH, TRIM_H - 0.8 * INCH), (TRIM_W - 1.3 * INCH, TRIM_H - 0.8 * INCH))
        elif style == 1:    # deux mandalas jumeaux haut / bas
            R = 2.15 * INCH
            sub = rng.randint(0, 10 ** 6)
            for yy in (cy - 2.45 * INCH, cy + 2.45 * INCH):
                MG.mandala(ctx, cx, yy, R, random.Random(sub), lw=1.4)
            split_line(ctx, 0.8 * INCH, cy, TRIM_W - 0.8 * INCH, cy)
            heart_path(ctx, cx, cy, 22); fill_white_stroke(ctx, 2)
            labels(ctx, (1.1 * INCH, cy - 0.3 * INCH), (1.1 * INCH, cy + 0.6 * INCH))
        elif style == 2:    # un mandala partagé verticalement
            MG.mandala(ctx, cx, cy, (TRIM_W - 1.5 * INCH) / 2, rng, lw=1.5)
            split_line(ctx, cx, 0.8 * INCH, cx, TRIM_H - 0.8 * INCH)
            labels(ctx, (1.3 * INCH, 1.3 * INCH), (TRIM_W - 1.3 * INCH, 1.3 * INCH))
            scatter(ctx, rng, (0.6 * INCH, 0.6 * INCH, TRIM_W - 1.2 * INCH, TRIM_H - 1.2 * INCH), ['heart', 'flower', 'leaf'],
                    avoid=[(0.7 * INCH, cy - 3.9 * INCH, TRIM_W - 1.4 * INCH, 7.8 * INCH), (0, 0, TRIM_W, 1.7 * INCH)], count=20, rmin=14, rmax=30)
        else:               # citation d'amour au centre, motifs à se partager
            q = QG.THEMES['couple']['quotes'][(idx * 3) % 50]
            frame(ctx, 'hearts', 0.6 * INCH, 0.6 * INCH, TRIM_W - 1.2 * INCH, TRIM_H - 1.2 * INCH, rng)
            boxes, _ = QG.draw_quote(ctx, q, cx, cy, TRIM_W - 2.2 * INCH, TRIM_H * 0.4, rng)
            scatter(ctx, rng, (0.75 * INCH, 0.75 * INCH, TRIM_W - 1.5 * INCH, TRIM_H - 1.5 * INCH),
                    ['heart', 'heart', 'flower', 'star', 'leaf', 'sparkle'], avoid=boxes + [(cx - 10, 0, 20, TRIM_H)],
                    count=50, rmin=16, rmax=40)
            split_line(ctx, cx, 0.7 * INCH, cx, TRIM_H * 0.28)
            split_line(ctx, cx, TRIM_H * 0.72, cx, TRIM_H - 0.7 * INCH)
            labels(ctx, (1.5 * INCH, 1.95 * INCH), (TRIM_W - 1.5 * INCH, 1.95 * INCH))
    return draw


def pages(book):
    return [page(i, book['seed'] * 1000 + i) for i in range(50)]
