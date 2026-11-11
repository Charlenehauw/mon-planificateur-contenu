"""Pages citations à colorier : lettres bulles + décor de motifs."""
import math
import random

from lib.core import (TRIM_W, TRIM_H, INCH, set_font, text_width, hollow_text, fit_size, frame, scatter,
                      ink, fill_white_stroke, rounded_rect, heart_path, doodle)
from data import quotes as Q

BOLD_FONTS = ['Luckiest Guy', 'Lilita One', 'Chewy', 'Bowlby One', 'Sniglet']
SCRIPT_FONTS = ['Pacifico', 'Lobster']

THEMES = {
    'bonheur': dict(quotes=Q.BONHEUR, kinds=['flower', 'heart', 'star', 'sparkle', 'leaf', 'swirl', 'cloud', 'dot']),
    'fun': dict(quotes=Q.FUN, kinds=['star', 'sparkle', 'heart', 'circle', 'swirl', 'bubble', 'dot', 'drop']),
    'anticolere': dict(quotes=Q.ANTI_COLERE, kinds=['bolt', 'star', 'sparkle', 'swirl', 'heart', 'bubble', 'dot', 'circle']),
    'couple': dict(quotes=Q.COUPLE, kinds=['heart', 'heart', 'heart', 'flower', 'sparkle', 'star', 'leaf', 'dot']),
}


def parse(q):
    lines = []
    for raw in q.split('|'):
        raw = raw.strip()
        emph = '*' in raw
        lines.append((raw.replace('*', '').strip(), emph))
    return lines


def layout(ctx, lines, bold, script, max_w, max_h):
    sizes = []
    for txt, emph in lines:
        fam = bold if emph else script
        mx = 110 if emph else 58
        if not emph and len(txt) <= 3:
            mx = 48
        sizes.append((fam, fit_size(ctx, txt, fam, max_w, mx, 14)))

    def heights(scale):
        return [s * scale * (0.98 if fam == bold else 1.25) for fam, s in sizes]
    scale = 1.0
    while sum(heights(scale)) > max_h and scale > 0.3:
        scale -= 0.03
    return [(fam, s * scale) for fam, s in sizes], heights(scale)


def draw_quote(ctx, q, cx, cy, max_w, max_h, rng, bold=None, script=None):
    bold = bold or rng.choice(BOLD_FONTS)
    script = script or rng.choice(SCRIPT_FONTS)
    lines = parse(q)
    sizes, hs = layout(ctx, lines, bold, script, max_w, max_h)
    total = sum(hs)
    y = cy - total / 2
    boxes = []
    for (txt, emph), (fam, size), h in zip(lines, sizes, hs):
        base = y + h * (0.88 if fam == bold else 0.8)
        w = hollow_text(ctx, txt, cx, base, fam, size, stroke=2.4 if emph else 2.0)
        boxes.append((cx - w / 2 - 6, y - 4, w + 12, h + 8))
        y += h
    return boxes, total


def wavy_background(ctx, x, y, w, h, rng):
    """Bandes ondulées façon zentangle derrière la citation."""
    n = rng.randint(10, 14)
    ys = sorted(rng.uniform(y + 20, y + h - 20) for _ in range(n))
    ink(ctx, 1.6)
    prev = None
    for yy in ys:
        amp, freq, ph = rng.uniform(6, 22), rng.uniform(1.0, 2.6), rng.uniform(0, 6.3)
        pts = [(x + w * t / 80, yy + amp * math.sin(ph + freq * 2 * math.pi * t / 80)) for t in range(81)]
        ctx.new_path()
        for i, (px, py) in enumerate(pts):
            (ctx.move_to if i == 0 else ctx.line_to)(px, py)
        ink(ctx, 1.6)
        ctx.stroke()
        if prev:
            motif = rng.choice(['dots', 'hearts', 'circles', 'none', 'scales'])
            for i in range(4, 78, rng.choice([5, 6, 7])):
                mx = pts[i][0]
                my = (pts[i][1] + prev[i][1]) / 2
                gap = abs(pts[i][1] - prev[i][1])
                r = min(gap * 0.36, 16)
                if r < 3:
                    continue
                if motif == 'dots':
                    ctx.arc(mx, my, r * 0.6, 0, 2 * math.pi); fill_white_stroke(ctx, 1.2)
                elif motif == 'hearts':
                    heart_path(ctx, mx, my, r * 0.8); fill_white_stroke(ctx, 1.2)
                elif motif == 'circles':
                    ctx.arc(mx, my, r, 0, 2 * math.pi); fill_white_stroke(ctx, 1.2)
                    ctx.arc(mx, my, r * 0.45, 0, 2 * math.pi); fill_white_stroke(ctx, 1.0)
                elif motif == 'scales':
                    ctx.new_path(); ctx.arc(mx, my + r * 0.5, r, math.pi, 0); ink(ctx, 1.2); ctx.stroke()
        prev = pts


def page(theme, idx, seed):
    def draw(ctx):
        rng = random.Random(seed)
        th = THEMES[theme]
        q = th['quotes'][idx % len(th['quotes'])]
        fx, fy, fw, fh = 0.6 * INCH, 0.6 * INCH, TRIM_W - 1.2 * INCH, TRIM_H - 1.2 * INCH
        style = ['scatter', 'stripes', 'scatter', 'card'][idx % 4]
        fstyle = rng.choice(['simple', 'double', 'dots', 'scallop'] + (['hearts'] * 3 if theme == 'couple' else ['flowers']))
        if style == 'stripes':
            ctx.save(); rounded_rect(ctx, fx, fy, fw, fh, 18); ctx.clip()
            wavy_background(ctx, fx, fy, fw, fh, rng)
            ctx.restore()
            frame(ctx, 'simple', fx, fy, fw, fh, rng)
            bw, bh = fw - 1.3 * INCH, fh * 0.55
            bx, by = fx + (fw - bw) / 2, fy + (fh - bh) / 2
            rounded_rect(ctx, bx, by, bw, bh, 30); fill_white_stroke(ctx, 2.4)
            rounded_rect(ctx, bx + 7, by + 7, bw - 14, bh - 14, 24); ink(ctx, 1.2); ctx.stroke()
            draw_quote(ctx, q, TRIM_W / 2, TRIM_H / 2, bw - 50, bh - 50, rng)
        elif style == 'card':
            frame(ctx, fstyle, fx, fy, fw, fh, rng)
            bw, bh = fw - 1.1 * INCH, fh * 0.62
            bx, by = fx + (fw - bw) / 2, fy + (fh - bh) / 2
            # carte festonnée
            r = 14
            nx, ny = int(bw // (2 * r)), int(bh // (2 * r))
            ink(ctx, 2)
            rounded_rect(ctx, bx, by, bw, bh, 24); fill_white_stroke(ctx, 2.2)
            boxes, _ = draw_quote(ctx, q, TRIM_W / 2, TRIM_H / 2, bw - 60, bh - 60, rng)
            scatter(ctx, rng, (fx + 10, fy + 10, fw - 20, fh - 20), th['kinds'],
                    avoid=[(bx - 4, by - 4, bw + 8, bh + 8)], count=40, rmin=16, rmax=40)
        else:
            frame(ctx, fstyle, fx, fy, fw, fh, rng)
            boxes, total = draw_quote(ctx, q, TRIM_W / 2, TRIM_H / 2, fw - 1.0 * INCH, fh * 0.6, rng)
            scatter(ctx, rng, (fx + 14, fy + 14, fw - 28, fh - 28), th['kinds'], avoid=boxes,
                    count=60, rmin=16, rmax=44)
    return draw


def pages(book):
    return [page(book['theme'], i, book['seed'] * 1000 + i) for i in range(50)]


def hero_draw(theme, seed, w, h, idx=0):
    def draw(ctx):
        rng = random.Random(seed)
        q = THEMES[theme]['quotes'][idx]
        boxes, _ = draw_quote(ctx, q, w / 2, h / 2, w * 0.82, h * 0.62, rng)
        scatter(ctx, rng, (6, 6, w - 12, h - 12), THEMES[theme]['kinds'], avoid=boxes, count=45,
                rmin=w * 0.025, rmax=w * 0.06)
    return draw
