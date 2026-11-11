"""Générateurs de pages d'activités (enfants & adultes)."""
import math
import random

from lib.core import (TRIM_W, TRIM_H, INCH, ink, fill_white_stroke, rounded_rect, draw_text, hollow_text,
                      fit_size, paragraph, wrap, set_font, text_width, star_path, heart_path, doodle, scatter,
                      frame, flower)
from data import sprites as SP
from data import journals as J
from generators import quotes as QG
from generators import mandala as MG

M = 0.7 * INCH
GREY = (0.55, 0.55, 0.55)
LIGHT = (0.8, 0.8, 0.8)

KID_TITLE = 'Lilita One'
KID_TEXT = 'Sniglet'


# =================================================================== utilitaires
def sprite_grid(name, bank):
    rows = bank[name].strip('\n').split('\n')
    return rows


def draw_sprite(ctx, rows, x, y, cell, mode='fill', numbers=None, grid=True, lw=1.0):
    """mode: fill (gris), outline (cases à colorier), numbers (coloriage magique), empty (grille vide)."""
    h, w = len(rows), len(rows[0])
    shade = {'X': 0.35, 'o': 0.75, 'k': 0.0}
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            cx, cy = x + i * cell, y + j * cell
            if mode == 'fill' and c in shade:
                ctx.rectangle(cx, cy, cell, cell)
                g = shade[c]
                ctx.set_source_rgb(g, g, g)
                ctx.fill()
            if mode == 'numbers':
                num = {'X': '1', 'o': '2', 'k': '3', '.': '4'}[c]
                draw_text(ctx, num, cx + cell / 2, cy + cell * 0.68, KID_TEXT, cell * 0.5, color=(0.35, 0.35, 0.35))
            if mode == 'silhouette' and c != '.':
                ctx.rectangle(cx, cy, cell, cell)
                ctx.set_source_rgb(0, 0, 0)
                ctx.fill()
    if grid:
        ink(ctx, lw)
        ctx.set_source_rgb(0.25, 0.25, 0.25)
        for i in range(w + 1):
            ctx.move_to(x + i * cell, y); ctx.line_to(x + i * cell, y + h * cell)
        for j in range(h + 1):
            ctx.move_to(x, y + j * cell); ctx.line_to(x + w * cell, y + j * cell)
        ctx.stroke()
    if mode == 'outline':
        # contour épais autour des cases colorées pour guider
        ink(ctx, 2.6)
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c == '.':
                    continue
                cx, cy = x + i * cell, y + j * cell
                nb = lambda ii, jj: rows[jj][ii] if 0 <= jj < h and 0 <= ii < w else '.'
                if nb(i, j - 1) == '.': ctx.move_to(cx, cy); ctx.line_to(cx + cell, cy)
                if nb(i, j + 1) == '.': ctx.move_to(cx, cy + cell); ctx.line_to(cx + cell, cy + cell)
                if nb(i - 1, j) == '.': ctx.move_to(cx, cy); ctx.line_to(cx, cy + cell)
                if nb(i + 1, j) == '.': ctx.move_to(cx + cell, cy); ctx.line_to(cx + cell, cy + cell)
        ctx.stroke()
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c == 'k':
                    ctx.rectangle(x + i * cell, y + j * cell, cell, cell)
                    ctx.set_source_rgb(0, 0, 0); ctx.fill()


def mirror(rows):
    return [r[::-1] for r in rows]


def header(ctx, n, title, instruction, kids=True):
    fam = KID_TITLE if kids else 'Playfair Display'
    if kids:
        rounded_rect(ctx, M, M - 10, TRIM_W - 2 * M, 0.95 * INCH, 22)
        fill_white_stroke(ctx, 2.4)
        ctx.arc(M + 34, M + 0.95 * INCH / 2 - 10, 24, 0, 2 * math.pi)
        fill_white_stroke(ctx, 2.2)
        draw_text(ctx, str(n), M + 34, M + 0.95 * INCH / 2 - 1, KID_TITLE, 24)
        size = fit_size(ctx, title, fam, TRIM_W - 2 * M - 110, 34)
        draw_text(ctx, title, TRIM_W / 2 + 25, M + 0.95 * INCH / 2 + 2, fam, size)
        y = M + 0.95 * INCH + 26
        for line in wrap(ctx, instruction, KID_TEXT, 17, TRIM_W - 2 * M):
            draw_text(ctx, line, TRIM_W / 2, y, KID_TEXT, 17)
            y += 22
        return y + 6
    else:
        draw_text(ctx, title, TRIM_W / 2, M + 30, 'Playfair Display', fit_size(ctx, title, 'Playfair Display', TRIM_W - 2 * M, 30))
        ink(ctx, 1)
        ctx.move_to(TRIM_W / 2 - 60, M + 46); ctx.line_to(TRIM_W / 2 + 60, M + 46); ctx.stroke()
        ctx.arc(TRIM_W / 2, M + 46, 3, 0, 2 * math.pi); fill_white_stroke(ctx, 1)
        y = M + 76
        for line in wrap(ctx, instruction, 'Kalam', 15, TRIM_W - 2 * M - 40):
            draw_text(ctx, line, TRIM_W / 2, y, 'Kalam', 15, color=(0.2, 0.2, 0.2))
            y += 21
        return y + 10


def lines(ctx, x, y, w, y_end, gap=30, dotted=False):
    ink(ctx, 0.7)
    ctx.set_source_rgb(*GREY)
    if dotted:
        ctx.set_dash([2, 4])
    while y + gap <= y_end:
        y += gap
        ctx.move_to(x, y); ctx.line_to(x + w, y)
    ctx.stroke()
    ctx.set_dash([])


# =================================================================== activités enfants
def maze(ctx, rng, x, y, w, h, cols, rows, lw=3.0):
    cell = min(w / cols, h / rows)
    ox, oy = x + (w - cell * cols) / 2, y + (h - cell * rows) / 2
    walls_h = [[True] * cols for _ in range(rows + 1)]
    walls_v = [[True] * (cols + 1) for _ in range(rows)]
    seen = [[False] * cols for _ in range(rows)]
    stack = [(0, 0)]
    seen[0][0] = True
    while stack:
        cx, cy = stack[-1]
        nb = [(cx + dx, cy + dy, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < cols and 0 <= cy + dy < rows and not seen[cy + dy][cx + dx]]
        if not nb:
            stack.pop(); continue
        nx, ny, dx, dy = rng.choice(nb)
        if dx == 1: walls_v[cy][cx + 1] = False
        if dx == -1: walls_v[cy][cx] = False
        if dy == 1: walls_h[cy + 1][cx] = False
        if dy == -1: walls_h[cy][cx] = False
        seen[ny][nx] = True
        stack.append((nx, ny))
    walls_v[0][0] = False
    walls_v[rows - 1][cols] = False
    ink(ctx, lw)
    for j in range(rows + 1):
        for i in range(cols):
            if walls_h[j][i]:
                ctx.move_to(ox + i * cell, oy + j * cell); ctx.line_to(ox + (i + 1) * cell, oy + j * cell)
    for j in range(rows):
        for i in range(cols + 1):
            if walls_v[j][i]:
                ctx.move_to(ox + i * cell, oy + j * cell); ctx.line_to(ox + i * cell, oy + (j + 1) * cell)
    ctx.stroke()
    return ox, oy, cell


def act_maze(ctx, rng, n, theme, level, bank):
    names = list(bank)
    a, b = rng.sample(names, 2)
    y0 = header(ctx, n, "Le labyrinthe", f"Aide {article(a)} à rejoindre {article(b, 'le')} en traçant le chemin !")
    cols = {1: 6, 2: 8, 3: 11, 4: 14, 5: 18}[level]
    rows = int(cols * 1.25)
    top = y0 + 50
    ox, oy, cell = maze(ctx, rng, M + 40, top, TRIM_W - 2 * M - 80, TRIM_H - top - M - 70, cols, rows, lw=3.2 if level < 3 else 2.4)
    for nm, (px, py) in ((a, (ox - 4, oy - 4)), (b, (ox + cols * cell + 4, oy + rows * cell + 4))):
        r = sprite_grid(nm, bank)
        c = 3.2
        sx = px - len(r[0]) * c / 2
        sy = py - len(r) * c - 4 if py < TRIM_H / 2 else py + 6
        draw_sprite(ctx, r, sx, sy, c, 'fill', grid=False)
    draw_text(ctx, "DÉPART", ox + 20, oy - 52, KID_TITLE, 16, 'left')
    draw_text(ctx, "ARRIVÉE", ox + cols * cell - 20, oy + rows * cell + 64, KID_TITLE, 16, 'right')


def article(name, kind='le'):
    voy = name[0].lower() in 'aeiouyéèœ'
    if voy:
        return "l'" + name
    return ('le ' if kind == 'le' else 'le ') + name


def act_color_number(ctx, rng, n, theme, level, bank, palette_names):
    name = rng.choice(list(bank))
    rows = sprite_grid(name, bank)
    y0 = header(ctx, n, "Coloriage magique", f"Colorie chaque case avec la bonne couleur pour découvrir {article(name)} !")
    # légende
    lx = M + 30
    for i, col in enumerate(palette_names):
        bx = lx + i * (TRIM_W - 2 * M - 60) / 4
        rounded_rect(ctx, bx, y0 + 8, 34, 34, 8); fill_white_stroke(ctx, 2)
        draw_text(ctx, str(i + 1), bx + 17, y0 + 33, KID_TITLE, 20)
        draw_text(ctx, col, bx + 42, y0 + 32, KID_TEXT, 16, 'left')
    w, h = len(rows[0]), len(rows)
    avail_w, avail_h = TRIM_W - 2 * M - 20, TRIM_H - y0 - 70 - M
    cell = min(avail_w / w, avail_h / h, 48)
    x = (TRIM_W - cell * w) / 2
    y = y0 + 70 + (avail_h - cell * h) / 2
    draw_sprite(ctx, rows, x, y, cell, 'numbers', lw=1.2)


def act_pixel_copy(ctx, rng, n, theme, level, bank):
    name = rng.choice(list(bank))
    rows = sprite_grid(name, bank)
    y0 = header(ctx, n, "Recopie le dessin", f"Recopie {article(name)} case par case dans la grande grille.")
    w, h = len(rows[0]), len(rows)
    small = min((TRIM_W - 2 * M) * 0.45 / w, 16)
    draw_sprite(ctx, rows, (TRIM_W - small * w) / 2, y0 + 10, small, 'fill', lw=0.6)
    top = y0 + 30 + small * h
    cell = min((TRIM_W - 2 * M) / w, (TRIM_H - top - M - 10) / h)
    draw_sprite(ctx, ['.' * w] * h, (TRIM_W - cell * w) / 2, top, cell, 'empty', lw=1.2)


def act_pixel_color(ctx, rng, n, theme, level, bank):
    name = rng.choice(list(bank))
    rows = sprite_grid(name, bank)
    y0 = header(ctx, n, f"Colorie {article(name)}", "Choisis tes couleurs préférées et colorie toutes les cases du dessin.")
    w, h = len(rows[0]), len(rows)
    cell = min((TRIM_W - 2 * M) / w, (TRIM_H - y0 - M - 20) / h, 46)
    draw_sprite(ctx, rows, (TRIM_W - cell * w) / 2, y0 + 20 + (TRIM_H - y0 - M - 20 - cell * h) / 2,
                cell, 'outline', grid=True, lw=0.5)


def act_symmetry(ctx, rng, n, theme, level, bank):
    symmetric = [k for k in bank if sprite_grid(k, bank) == mirror(sprite_grid(k, bank))]
    name = rng.choice(symmetric or list(bank))
    rows = sprite_grid(name, bank)
    w, h = len(rows[0]), len(rows)
    half = w // 2
    y0 = header(ctx, n, "La symétrie", "Termine le dessin en recopiant la moitié de gauche comme dans un miroir.")
    cell = min((TRIM_W - 2 * M) / w, (TRIM_H - y0 - M - 20) / h, 44)
    x, y = (TRIM_W - cell * w) / 2, y0 + 20
    # miroir : fabrique une forme symétrique à partir de la moitié gauche
    sym = [r[:half] + r[:half][::-1] + (r[half] if w % 2 else '') for r in rows]
    sym = [s[:w] for s in sym]
    show = [s[:half] + '.' * (w - half) for s in sym]
    draw_sprite(ctx, show, x, y, cell, 'fill', lw=1.0)
    ink(ctx, 3); ctx.set_dash([10, 6])
    ctx.move_to(x + half * cell, y - 10); ctx.line_to(x + half * cell, y + h * cell + 10); ctx.stroke()
    ctx.set_dash([])


def act_shadow(ctx, rng, n, theme, level, bank):
    names = rng.sample(list(bank), 4)
    y0 = header(ctx, n, "Les ombres", "Relie chaque dessin à son ombre avec un trait.")
    shuffled = names[:]
    while shuffled == names:
        rng.shuffle(shuffled)
    slot_h = (TRIM_H - y0 - M) / 4
    for i, (a, b) in enumerate(zip(names, shuffled)):
        for nm, cxp, mode in ((a, TRIM_W * 0.28, 'fill'), (b, TRIM_W * 0.72, 'silhouette')):
            r = sprite_grid(nm, bank)
            c = min(slot_h * 0.75 / len(r), 150 / len(r[0]))
            draw_sprite(ctx, r, cxp - c * len(r[0]) / 2, y0 + i * slot_h + (slot_h - c * len(r)) / 2, c, mode, grid=False)
        for xx in (TRIM_W * 0.42, TRIM_W * 0.58):
            ctx.arc(xx, y0 + i * slot_h + slot_h / 2, 6, 0, 2 * math.pi); fill_white_stroke(ctx, 2)


def act_odd(ctx, rng, n, theme, level, bank):
    y0 = header(ctx, n, "L'intrus", "Sur chaque ligne, entoure le dessin qui est tourné dans l'autre sens !")
    names = rng.sample(list(bank), 4)
    slot_h = (TRIM_H - y0 - M) / 4
    for i, nm in enumerate(names):
        r = sprite_grid(nm, bank)
        k = rng.randrange(4)
        c = min(slot_h * 0.6 / len(r), (TRIM_W - 2 * M) / 4 * 0.8 / len(r[0]))
        for j in range(4):
            rr = mirror(r) if j == k else r
            cx = M + (j + 0.5) * (TRIM_W - 2 * M) / 4
            draw_sprite(ctx, rr, cx - c * len(r[0]) / 2, y0 + i * slot_h + (slot_h - c * len(r)) / 2, c, 'fill', grid=False)
        ink(ctx, 0.8); ctx.set_source_rgb(*LIGHT)
        ctx.move_to(M, y0 + (i + 1) * slot_h); ctx.line_to(TRIM_W - M, y0 + (i + 1) * slot_h); ctx.stroke()


def act_count(ctx, rng, n, theme, level, bank):
    kinds = rng.sample(['star', 'heart', 'circle', 'flower', 'drop', 'cloud'], 3)
    labels = {'star': 'étoiles', 'heart': 'cœurs', 'circle': 'ronds', 'flower': 'fleurs', 'drop': 'gouttes', 'cloud': 'nuages'}
    y0 = header(ctx, n, "Compte et colorie", "Compte chaque forme et écris le nombre dans la case. Puis colorie-les !")
    area = (M + 20, y0 + 10, TRIM_W - 2 * M - 40, TRIM_H - y0 - M - 140)
    counts = {k: rng.randint(2, 4 + level * 2) for k in kinds}
    placed = []
    pool = [k for k in kinds for _ in range(counts[k])]
    rng.shuffle(pool)
    x0, yy, w, h = area
    for k in pool:
        for _ in range(500):
            r = rng.uniform(22, 34)
            cx, cy = rng.uniform(x0 + r, x0 + w - r), rng.uniform(yy + r, yy + h - r)
            if all((cx - px) ** 2 + (cy - py) ** 2 > (r + pr + 8) ** 2 for px, py, pr in placed):
                placed.append((cx, cy, r))
                doodle(ctx, k, cx, cy, r, rng, 2.4)
                break
    by = TRIM_H - M - 110
    for i, k in enumerate(kinds):
        bx = M + 20 + i * (TRIM_W - 2 * M - 40) / 3
        doodle(ctx, k, bx + 30, by + 40, 26, random.Random(1), 2.4)
        rounded_rect(ctx, bx + 70, by + 10, 70, 62, 12); fill_white_stroke(ctx, 2.4)
        draw_text(ctx, labels[k], bx + 105, by + 100, KID_TEXT, 14)


def trace_path(ctx, kind, x0, x1, y, amp):
    steps = 120
    ctx.new_path()
    for s in range(steps + 1):
        t = s / steps
        x = x0 + (x1 - x0) * t
        if kind == 'wave':
            yy = y + amp * math.sin(t * 4 * math.pi)
        elif kind == 'zigzag':
            ph = (t * 6) % 1
            yy = y + amp * (4 * abs(ph - 0.5) - 1)
        elif kind == 'loop':
            a = t * 5 * 2 * math.pi
            x = x0 + (x1 - x0) * t + amp * 0.6 * math.sin(a)
            yy = y - amp * 0.8 * math.cos(a)
        elif kind == 'arc':
            ph = (t * 4) % 1
            yy = y - amp * math.sin(ph * math.pi)
        elif kind == 'square':
            ph = (t * 5) % 1
            yy = y - amp if ph < 0.5 else y + amp
        else:
            yy = y
        (ctx.move_to if s == 0 else ctx.line_to)(x, yy)


def act_trace(ctx, rng, n, theme, level, bank):
    y0 = header(ctx, n, "Je trace les lignes", "Suis les pointillés avec ton crayon sans lever la main !")
    kinds = rng.sample(['line', 'wave', 'zigzag', 'arc', 'loop', 'square'], 5)
    names = list(bank)
    slot = (TRIM_H - y0 - M) / 5
    for i, k in enumerate(kinds):
        y = y0 + slot * (i + 0.5)
        a, b = rng.sample(names, 2)
        for nm, xx in ((a, M + 30), (b, TRIM_W - M - 30)):
            r = sprite_grid(nm, bank)
            c = min(slot * 0.55 / len(r), 56 / len(r[0]))
            draw_sprite(ctx, r, xx - c * len(r[0]) / 2, y - c * len(r) / 2, c, 'fill', grid=False)
        trace_path(ctx, k, M + 75, TRIM_W - M - 75, y, slot * 0.22)
        ink(ctx, 3); ctx.set_source_rgb(0.45, 0.45, 0.45); ctx.set_dash([2, 9])
        ctx.stroke(); ctx.set_dash([])


def act_word_trace(ctx, rng, n, theme, level, bank, words):
    word = words[(n * 7) % len(words)]
    y0 = header(ctx, n, f"J'écris : {word}", "Repasse sur les lettres en pointillés, puis écris le mot tout seul.")
    r = sprite_grid(rng.choice(list(bank)), bank)
    c = min(150 / len(r), 200 / len(r[0]))
    draw_sprite(ctx, r, (TRIM_W - c * len(r[0])) / 2, y0 + 10, c, 'outline', grid=False)
    y = y0 + 30 + c * len(r)
    size = fit_size(ctx, word, 'Sniglet', TRIM_W - 2 * M - 40, 90)
    rows = int((TRIM_H - M - y) // (size * 1.25))
    for i in range(rows):
        base = y + (i + 1) * size * 1.2
        ink(ctx, 0.8); ctx.set_source_rgb(*LIGHT)
        for yy in (base, base - size * 0.5, base - size * 0.72):
            ctx.move_to(M, yy); ctx.line_to(TRIM_W - M, yy)
        ctx.stroke()
        if i < rows - 1:
            set_font(ctx, 'Sniglet', size)
            ctx.move_to(TRIM_W / 2 - text_width(ctx, word) / 2, base)
            ctx.text_path(word)
            ink(ctx, 1.8); ctx.set_source_rgb(0.4, 0.4, 0.4); ctx.set_dash([3, 5]); ctx.stroke(); ctx.set_dash([])


DOT_SHAPES = {
    'étoile': [(math.cos(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.42),
                math.sin(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.42)) for i in range(10)],
    'cœur': [(16 * math.sin(t) ** 3 / 17, -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17)
             for t in [i * 2 * math.pi / 20 for i in range(20)]],
    'maison': [(-0.7, 1), (-0.7, 0), (-0.9, 0), (0, -0.9), (0.9, 0), (0.7, 0), (0.7, 1), (0.2, 1), (0.2, 0.45), (-0.2, 0.45), (-0.2, 1)],
    'sapin': [(0, -1), (0.45, -0.45), (0.25, -0.45), (0.7, 0.1), (0.4, 0.1), (0.9, 0.65), (0.15, 0.65), (0.15, 1), (-0.15, 1), (-0.15, 0.65), (-0.9, 0.65), (-0.4, 0.1), (-0.7, 0.1), (-0.25, -0.45), (-0.45, -0.45)],
    'œuf': [(0.75 * math.sin(t), -math.cos(t) * (1.0 if math.cos(t) > 0 else 0.8)) for t in [i * 2 * math.pi / 18 for i in range(18)]],
    'volcan': [(-1, 0.8), (-0.7, 0.35), (-0.45, -0.15), (-0.3, -0.5), (-0.15, -0.62), (0, -0.5), (0.15, -0.62), (0.3, -0.5), (0.45, -0.15), (0.7, 0.35), (1, 0.8), (0, 0.8)],
    'poisson': [(-0.9, 0), (-0.5, -0.45), (0, -0.55), (0.45, -0.3), (0.95, -0.6), (0.8, 0), (0.95, 0.6), (0.45, 0.3), (0, 0.55), (-0.5, 0.45)],
    'fusée': [(0, -1), (0.3, -0.6), (0.3, 0.4), (0.6, 0.8), (0.3, 0.75), (0.2, 1), (-0.2, 1), (-0.3, 0.75), (-0.6, 0.8), (-0.3, 0.4), (-0.3, -0.6)],
    'feuille': [(0, -1), (0.45, -0.6), (0.6, -0.1), (0.45, 0.4), (0.1, 0.8), (0, 1), (-0.1, 0.8), (-0.45, 0.4), (-0.6, -0.1), (-0.45, -0.6)],
    'soleil': [(math.cos(i * math.pi / 8) * (1 if i % 2 == 0 else 0.62), math.sin(i * math.pi / 8) * (1 if i % 2 == 0 else 0.62)) for i in range(16)],
}


def act_dots(ctx, rng, n, theme, level, shape_names):
    name = shape_names[n % len(shape_names)]
    pts = DOT_SHAPES[name]
    y0 = header(ctx, n, "Relie les points", f"Relie les points de 1 à {len(pts)} pour découvrir le dessin, puis colorie-le !")
    cx, cy = TRIM_W / 2, (y0 + TRIM_H - M) / 2
    R = min(TRIM_W - 2 * M, TRIM_H - M - y0) * 0.42
    for i, (px, py) in enumerate(pts):
        x, y = cx + px * R, cy + py * R
        ctx.arc(x, y, 4.5, 0, 2 * math.pi); ctx.set_source_rgb(0, 0, 0); ctx.fill()
        dx, dy = px, py
        d = math.hypot(dx, dy) or 1
        draw_text(ctx, str(i + 1), x + dx / d * 18, y + dy / d * 18 + 6, KID_TEXT, 17)
    ctx.new_path(); ctx.arc(cx + pts[0][0] * R, cy + pts[0][1] * R, 9, 0, 2 * math.pi); ink(ctx, 1.5); ctx.stroke()
    scatter(ctx, rng, (M, y0, TRIM_W - 2 * M, TRIM_H - M - y0), ['star', 'sparkle', 'dot', 'cloud'],
            avoid=[(cx - R - 30, cy - R - 30, 2 * R + 60, 2 * R + 60)], count=8, rmin=14, rmax=26, lw=2)


def act_draw(ctx, rng, n, theme, level, bank, prompt):
    y0 = header(ctx, n, "À toi de dessiner !", prompt)
    frame(ctx, rng.choice(['dots', 'scallop', 'double']), M + 10, y0 + 10, TRIM_W - 2 * M - 20, TRIM_H - M - y0 - 20, rng, 2.4)


def act_sudoku(ctx, rng, n, theme, level, size=4):
    """Sudoku 4x4 avec formes (enfants) ou 6x6 chiffres."""
    base = [[(i * (2 if size == 4 else 3) + i // (2 if size == 4 else 2) + j) % size for j in range(size)] for i in range(size)]
    perm = list(range(size)); rng.shuffle(perm)
    grid = [[perm[v] for v in row] for row in base]
    holes = {4: 5 + level, 6: 12 + level * 2}[size]
    cells = [(i, j) for i in range(size) for j in range(size)]
    hidden = set(rng.sample(cells, holes))
    y0 = header(ctx, n, "Sudoku" + (" des formes" if size == 4 else ""),
                "Chaque ligne, chaque colonne et chaque bloc doit contenir une seule fois chaque " + ("forme." if size == 4 else "chiffre de 1 à 6."))
    S = min(TRIM_W - 2 * M - 60, TRIM_H - y0 - M - 120)
    cell = S / size
    x, y = (TRIM_W - S) / 2, y0 + 30
    shapes = ['circle', 'star', 'heart', 'drop']
    for i in range(size):
        for j in range(size):
            if (i, j) in hidden:
                continue
            cx, cy = x + (j + 0.5) * cell, y + (i + 0.5) * cell
            if size == 4:
                doodle(ctx, shapes[grid[i][j]], cx, cy, cell * 0.3, random.Random(0), 2.4)
            else:
                draw_text(ctx, str(grid[i][j] + 1), cx, cy + cell * 0.2, KID_TITLE, cell * 0.55)
    ink(ctx, 1.2)
    for k in range(size + 1):
        ctx.move_to(x + k * cell, y); ctx.line_to(x + k * cell, y + S)
        ctx.move_to(x, y + k * cell); ctx.line_to(x + S, y + k * cell)
    ctx.stroke()
    ink(ctx, 3.6)
    bw, bh = (2, 2) if size == 4 else (3, 2)
    for k in range(0, size + 1, bw):
        ctx.move_to(x + k * cell, y); ctx.line_to(x + k * cell, y + S)
    for k in range(0, size + 1, bh):
        ctx.move_to(x, y + k * cell); ctx.line_to(x + S, y + k * cell)
    ctx.stroke()
    if size == 4:
        for k, s in enumerate(shapes):
            doodle(ctx, s, M + 60 + k * (TRIM_W - 2 * M - 120) / 3, TRIM_H - M - 40, 22, random.Random(0), 2.2)


WS_DIRS = [(1, 0), (0, 1), (1, 1)]


def act_wordsearch(ctx, rng, n, theme, level, words):
    size = 10 if level < 3 else 12
    pool = [w for w in words if len(w) <= size]
    chosen = rng.sample(pool, min(len(pool), 8 if size == 10 else 10))
    grid = [[None] * size for _ in range(size)]
    placed = []
    for w in sorted(chosen, key=len, reverse=True):
        for _ in range(300):
            dx, dy = rng.choice(WS_DIRS)
            x = rng.randrange(size - (len(w) - 1) * dx)
            y = rng.randrange(size - (len(w) - 1) * dy)
            if all(grid[y + k * dy][x + k * dx] in (None, ch) for k, ch in enumerate(w)):
                for k, ch in enumerate(w):
                    grid[y + k * dy][x + k * dx] = ch
                placed.append(w)
                break
    alpha = 'ABCDEFGHIJKLMNOPRSTUVE'
    y0 = header(ctx, n, "Mots mêlés", "Retrouve tous les mots cachés dans la grille (horizontal, vertical, diagonal).")
    S = TRIM_W - 2 * M - 40
    cell = S / size
    x, y = (TRIM_W - S) / 2, y0 + 10
    rounded_rect(ctx, x - 8, y - 8, S + 16, S + 16, 16); ink(ctx, 2.4); ctx.stroke()
    for j in range(size):
        for i in range(size):
            ch = grid[j][i] or rng.choice(alpha)
            draw_text(ctx, ch, x + (i + 0.5) * cell, y + (j + 0.5) * cell + cell * 0.22, KID_TITLE, cell * 0.55)
    ly = y + S + 40
    for k, w in enumerate(sorted(placed)):
        cx = M + 30 + (k % 3) * (TRIM_W - 2 * M - 40) / 3
        cy = ly + (k // 3) * 30
        rounded_rect(ctx, cx, cy - 15, 18, 18, 4); ink(ctx, 1.5); ctx.stroke()
        draw_text(ctx, w, cx + 26, cy, KID_TEXT, 16, 'left')


def act_code(ctx, rng, n, theme, level, message):
    symbols = ['star', 'heart', 'circle', 'drop', 'flower', 'cloud', 'sparkle', 'dot', 'bolt', 'leaf']
    letters = sorted(set(message.replace(' ', '')))
    mapping = {ch: symbols[i % len(symbols)] + ('' if i < len(symbols) else '2') for i, ch in enumerate(letters)}
    y0 = header(ctx, n, "Le code secret", "Utilise le code pour déchiffrer le message mystère !")
    per = 5
    for i, ch in enumerate(letters):
        col, row = i % per, i // per
        cx = M + 40 + col * (TRIM_W - 2 * M - 80) / (per - 1)
        cy = y0 + 30 + row * 80
        sym = mapping[ch]
        doodle(ctx, sym.rstrip('2'), cx, cy, 20, random.Random(0), 2.2)
        if sym.endswith('2'):
            ctx.arc(cx, cy, 26, 0, 2 * math.pi); ink(ctx, 1.4); ctx.stroke()
        draw_text(ctx, '= ' + ch, cx, cy + 50, KID_TITLE, 20)
    y = y0 + 60 + (len(letters) // per + 1) * 80
    words = message.split()
    box = 46
    for w in words:
        total = len(w) * box
        if total > TRIM_W - 2 * M:
            box = (TRIM_W - 2 * M) / len(w)
    for w in words:
        total = len(w) * box
        x = (TRIM_W - total) / 2
        for k, ch in enumerate(w):
            sym = mapping[ch]
            doodle(ctx, sym.rstrip('2'), x + k * box + box / 2, y, box * 0.33, random.Random(0), 2)
            if sym.endswith('2'):
                ctx.arc(x + k * box + box / 2, y, box * 0.42, 0, 2 * math.pi); ink(ctx, 1.2); ctx.stroke()
            ink(ctx, 2)
            ctx.move_to(x + k * box + 6, y + box * 1.2); ctx.line_to(x + k * box + box - 6, y + box * 1.2); ctx.stroke()
        y += box * 1.9


def act_math(ctx, rng, n, theme, level):
    y0 = header(ctx, n, "Les calculs", "Calcule chaque opération et écris le résultat. Colorie les étoiles quand c'est juste !")
    rows = 10
    slot = (TRIM_H - y0 - M) / rows
    for i in range(rows):
        if level <= 2:
            a, b = rng.randint(1, 9), rng.randint(1, 9)
            op = '+'
        else:
            op = rng.choice(['+', '-'])
            a, b = rng.randint(5, 20), rng.randint(1, 10)
            if op == '-' and b > a:
                a, b = b, a
        y = y0 + slot * (i + 0.65)
        draw_text(ctx, f"{a}  {op}  {b}  =", TRIM_W / 2 - 40, y, KID_TITLE, 28, 'right')
        rounded_rect(ctx, TRIM_W / 2 - 20, y - 30, 80, 40, 10); fill_white_stroke(ctx, 2)
        star_path(ctx, TRIM_W / 2 + 120, y - 10, 18); fill_white_stroke(ctx, 2)


def act_spot_grid(ctx, rng, n, theme, level, bank):
    """Retrouve les dessins identiques au modèle."""
    name = rng.choice(list(bank))
    rows = sprite_grid(name, bank)
    y0 = header(ctx, n, "Les jumeaux", f"Entoure tous les dessins identiques au modèle. Combien en trouves-tu ?")
    c = min(100 / len(rows[0]), 70 / len(rows))
    draw_sprite(ctx, rows, (TRIM_W - c * len(rows[0])) / 2, y0, c, 'fill', grid=False)
    ink(ctx, 2); rounded_rect(ctx, (TRIM_W - c * len(rows[0])) / 2 - 10, y0 - 10, c * len(rows[0]) + 20, c * len(rows) + 20, 10); ctx.stroke()
    others = [k for k in bank if k != name]
    top = y0 + c * len(rows) + 30
    cols, rws = 4, 4
    cw, ch = (TRIM_W - 2 * M) / cols, (TRIM_H - M - top - 50) / rws
    for j in range(rws):
        for i in range(cols):
            r = rng.random()
            if r < 0.35:
                rr = rows
            elif r < 0.65:
                rr = mirror(rows)
            else:
                rr = sprite_grid(rng.choice(others), bank)
            cc = min(cw * 0.7 / len(rr[0]), ch * 0.7 / len(rr))
            draw_sprite(ctx, rr, M + i * cw + (cw - cc * len(rr[0])) / 2, top + j * ch + (ch - cc * len(rr)) / 2, cc, 'fill', grid=False)
    draw_text(ctx, "J'en ai trouvé :", TRIM_W / 2 - 20, TRIM_H - M - 10, KID_TEXT, 18, 'right')
    rounded_rect(ctx, TRIM_W / 2, TRIM_H - M - 38, 60, 40, 10); ink(ctx, 2); ctx.stroke()


# =================================================================== livres enfants : plans
def kids_book_pages(book):
    theme = book['theme']
    bank = {'dino': SP.DINOS, 'reptile': SP.REPTILES, 'mixte': {**SP.MIXTE, **{k: v for k, v in SP.DINOS.items() if k in ('T-Rex', 'Œuf')}}}[theme]
    words = book['words']
    pal = book['color_names']
    shapes = book['dot_shapes']
    draws = book['draw_prompts']
    plan = book['plan']
    out = []
    for i, kind in enumerate(plan):
        n = i + 1
        level = 1 + i * 5 // len(plan)

        def make(kind=kind, n=n, level=level):
            def draw(ctx):
                rng = random.Random(book['seed'] * 1000 + n)
                if kind == 'maze': act_maze(ctx, rng, n, theme, level, bank)
                elif kind == 'color': act_color_number(ctx, rng, n, theme, level, bank, pal)
                elif kind == 'copy': act_pixel_copy(ctx, rng, n, theme, level, bank)
                elif kind == 'pixel': act_pixel_color(ctx, rng, n, theme, level, bank)
                elif kind == 'sym': act_symmetry(ctx, rng, n, theme, level, bank)
                elif kind == 'shadow': act_shadow(ctx, rng, n, theme, level, bank)
                elif kind == 'odd': act_odd(ctx, rng, n, theme, level, bank)
                elif kind == 'count': act_count(ctx, rng, n, theme, level, bank)
                elif kind == 'trace': act_trace(ctx, rng, n, theme, level, bank)
                elif kind == 'word': act_word_trace(ctx, rng, n, theme, level, bank, words)
                elif kind == 'dots': act_dots(ctx, rng, n, theme, level, shapes)
                elif kind == 'draw': act_draw(ctx, rng, n, theme, level, bank, draws[n % len(draws)])
                elif kind == 'sudoku4': act_sudoku(ctx, rng, n, theme, level, 4)
                elif kind == 'sudoku6': act_sudoku(ctx, rng, n, theme, level, 6)
                elif kind == 'search': act_wordsearch(ctx, rng, n, theme, level, book['search_words'])
                elif kind == 'code': act_code(ctx, rng, n, theme, level, book['messages'][n % len(book['messages'])])
                elif kind == 'math': act_math(ctx, rng, n, theme, level)
                elif kind == 'twins': act_spot_grid(ctx, rng, n, theme, level, bank)
            return draw
        out.append(make())
    return out


# =================================================================== livres adultes : journal
def corner_doodles(ctx, rng, kinds=('flower', 'leaf', 'heart', 'sparkle')):
    for (x, y) in [(M - 10, TRIM_H - M + 10), (TRIM_W - M + 10, TRIM_H - M + 10)]:
        for k in range(3):
            doodle(ctx, rng.choice(kinds), x + rng.uniform(-14, 14), y + rng.uniform(-20, 4) - k * 4, rng.uniform(10, 16), rng, 1.3)


def j_prompt(ctx, rng, y0, act):
    lines(ctx, M, y0, TRIM_W - 2 * M, TRIM_H - M - 30, 30)


def j_list(ctx, rng, y0, act, n):
    gap = min(62, (TRIM_H - M - 30 - y0) / n)
    for i in range(n):
        y = y0 + gap * (i + 1)
        ctx.arc(M + 14, y - 8, 12, 0, 2 * math.pi); fill_white_stroke(ctx, 1.3)
        draw_text(ctx, str(i + 1), M + 14, y - 3.5, 'Playfair Display', 12)
        ink(ctx, 0.7); ctx.set_source_rgb(*GREY)
        ctx.move_to(M + 36, y); ctx.line_to(TRIM_W - M, y); ctx.stroke()


def j_checklist(ctx, rng, y0, act, items):
    gap = min(62, (TRIM_H - M - 30 - y0) / len(items))
    for i, it in enumerate(items):
        y = y0 + gap * (i + 1)
        rounded_rect(ctx, M + 4, y - 18, 20, 20, 4); fill_white_stroke(ctx, 1.4)
        if it:
            draw_text(ctx, it, M + 38, y - 3, 'Kalam', 15, 'left')
        ink(ctx, 0.6); ctx.set_source_rgb(*LIGHT)
        ctx.move_to(M + 38, y + 4); ctx.line_to(TRIM_W - M, y + 4); ctx.stroke()


def j_tracker(ctx, rng, y0, act, legend):
    cols = 7
    cell = (TRIM_W - 2 * M) / cols
    rows = 5
    ch = min(cell, (TRIM_H - M - y0 - 120) / rows)
    for d in range(31):
        i, j = d % cols, d // cols
        x, y = M + i * cell, y0 + j * ch
        rounded_rect(ctx, x + 4, y + 4, cell - 8, ch - 8, 10); fill_white_stroke(ctx, 1.4)
        draw_text(ctx, str(d + 1), x + 16, y + 22, 'Playfair Display', 11, 'left', GREY)
    ly = y0 + rows * ch + 30
    for k, lab in enumerate(legend):
        x = M + k * (TRIM_W - 2 * M) / len(legend)
        ctx.arc(x + 14, ly + 10, 12, 0, 2 * math.pi); fill_white_stroke(ctx, 1.4)
        draw_text(ctx, lab, x + 32, ly + 15, 'Kalam', 13, 'left')


def j_gratitude(ctx, rng, y0, act):
    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    slot = (TRIM_H - M - y0 - 10) / 7
    for i, d in enumerate(days):
        y = y0 + i * slot
        draw_text(ctx, d, M, y + 20, 'Great Vibes', 24, 'left')
        for k in range(3):
            yy = y + 22 + (k + 1) * (slot - 26) / 3
            heart_path(ctx, M + 120, yy - 6, 6); fill_white_stroke(ctx, 1)
            ink(ctx, 0.6); ctx.set_source_rgb(*GREY); ctx.move_to(M + 135, yy); ctx.line_to(TRIM_W - M, yy); ctx.stroke()


def j_boxes(ctx, rng, y0, act, n, labels=None):
    cols = 2
    rows = (n + 1) // 2
    w = (TRIM_W - 2 * M - 20) / cols
    h = (TRIM_H - M - y0 - 10 * rows) / rows
    for k in range(n):
        x, y = M + (k % cols) * (w + 20), y0 + (k // cols) * (h + 10)
        rounded_rect(ctx, x, y, w, h - 10, 16); fill_white_stroke(ctx, 1.6)
        if labels:
            draw_text(ctx, labels[k], x + w / 2, y + 30, 'Great Vibes', 26)


def j_letter(ctx, rng, y0, act):
    draw_text(ctx, "Cher(e) ...", M, y0 + 20, 'Great Vibes', 30, 'left')
    lines(ctx, M, y0 + 30, TRIM_W - 2 * M, TRIM_H - M - 80, 30)
    draw_text(ctx, "Avec tout mon amour,", TRIM_W - M, TRIM_H - M - 30, 'Great Vibes', 24, 'right')


def j_scale(ctx, rng, y0, act, items):
    gap = min(100, (TRIM_H - M - y0) / len(items))
    for i, it in enumerate(items):
        y = y0 + gap * i + 30
        draw_text(ctx, it, M, y, 'Playfair Display', 16, 'left')
        for k in range(10):
            x = M + 10 + k * (TRIM_W - 2 * M - 20) / 9.5
            ctx.arc(x + 10, y + 26, 13, 0, 2 * math.pi); fill_white_stroke(ctx, 1.3)
            draw_text(ctx, str(k + 1), x + 10, y + 31, 'Kalam', 12, color=GREY)


def j_two_col(ctx, rng, y0, act, cols, rows=None):
    w = (TRIM_W - 2 * M - 20) / 2
    for k, c in enumerate(cols):
        x = M + k * (w + 20)
        rounded_rect(ctx, x, y0, w, TRIM_H - M - y0, 18); fill_white_stroke(ctx, 1.6)
        draw_text(ctx, c, x + w / 2, y0 + 38, 'Great Vibes', 30)
        if rows:
            gap = (TRIM_H - M - y0 - 70) / len(rows)
            for i, r in enumerate(rows):
                yy = y0 + 70 + gap * (i + 0.6)
                draw_text(ctx, r, x + 18, yy, 'Kalam', 14, 'left')
                ctx.arc(x + w - 30, yy - 5, 11, 0, 2 * math.pi); fill_white_stroke(ctx, 1.3)
        else:
            lines(ctx, x + 16, y0 + 55, w - 32, TRIM_H - M - 15, 30)


def j_bingo(ctx, rng, y0, act, items):
    S = min(TRIM_W - 2 * M, TRIM_H - M - y0)
    cell = S / 5
    x = (TRIM_W - S) / 2
    for k, it in enumerate(items[:25]):
        i, j = k % 5, k // 5
        cx, cy = x + i * cell, y0 + j * cell
        rounded_rect(ctx, cx + 3, cy + 3, cell - 6, cell - 6, 10); fill_white_stroke(ctx, 1.4)
        if it == 'JOKER':
            star_path(ctx, cx + cell / 2, cy + cell / 2, cell * 0.33); fill_white_stroke(ctx, 1.4)
        else:
            ls = wrap(ctx, it, 'Kalam', 12, cell - 16)
            yy = cy + cell / 2 - (len(ls) - 1) * 7 + 4
            for l in ls:
                draw_text(ctx, l, cx + cell / 2, yy, 'Kalam', 12); yy += 14


def j_draw(ctx, rng, y0, act, circle=False, split=False):
    if circle:
        R = min(TRIM_W - 2 * M, TRIM_H - M - y0) / 2 - 10
        ctx.arc(TRIM_W / 2, (y0 + TRIM_H - M) / 2, R, 0, 2 * math.pi); fill_white_stroke(ctx, 1.6)
        ctx.arc(TRIM_W / 2, (y0 + TRIM_H - M) / 2, R - 8, 0, 2 * math.pi); ink(ctx, 0.8); ctx.stroke()
    elif split:
        h = (TRIM_H - M - y0 - 20) / 2
        for k, lab in enumerate(["Toi, par moi", "Moi, par toi"]):
            rounded_rect(ctx, M, y0 + k * (h + 20), TRIM_W - 2 * M, h, 18); fill_white_stroke(ctx, 1.6)
            draw_text(ctx, lab, M + 20, y0 + k * (h + 20) + 34, 'Great Vibes', 26, 'left')
    else:
        frame(ctx, 'double', M, y0, TRIM_W - 2 * M, TRIM_H - M - y0, rng, 1.6)


def j_fields(ctx, rng, y0, act, fields):
    gap = min(92, (TRIM_H - M - y0) / len(fields))
    for i, f in enumerate(fields):
        y = y0 + gap * (i + 0.6)
        draw_text(ctx, f + ' :', M, y, 'Playfair Display', 15, 'left')
        ink(ctx, 0.7); ctx.set_source_rgb(*GREY)
        ctx.move_to(M, y + 28); ctx.line_to(TRIM_W - M, y + 28); ctx.stroke()


def j_couple_form(ctx, rng, y0, act, fields):
    w = (TRIM_W - 2 * M) / 2
    gap = min(92, (TRIM_H - M - y0 - 40) / len(fields))
    draw_text(ctx, "Lui / Elle", M + w * 1.25, y0 + 12, 'Great Vibes', 24)
    draw_text(ctx, "Elle / Lui", M + w * 1.75, y0 + 12, 'Great Vibes', 24)
    for i, f in enumerate(fields):
        y = y0 + 40 + gap * (i + 0.6)
        draw_text(ctx, f, M, y, 'Kalam', 14, 'left')
        ink(ctx, 0.7); ctx.set_source_rgb(*GREY)
        for k in range(2):
            ctx.move_to(M + w + k * w / 2 + 6, y + 6); ctx.line_to(M + w + (k + 1) * w / 2 - 6, y + 6)
        ctx.stroke()


def j_questions(ctx, rng, y0, act, items):
    gap = (TRIM_H - M - y0) / len(items)
    for i, q in enumerate(items):
        y = y0 + gap * i + 20
        heart_path(ctx, M + 8, y - 5, 7); fill_white_stroke(ctx, 1.2)
        draw_text(ctx, q, M + 24, y, 'Playfair Display', 14, 'left')
        ink(ctx, 0.6); ctx.set_source_rgb(*LIGHT)
        for k in (1, 2):
            yy = y + k * min(26, (gap - 20) / 2.2)
            ctx.move_to(M + 24, yy); ctx.line_to(TRIM_W - M, yy)
        ctx.stroke()


def j_ttt(ctx, rng, y0, act):
    S = (TRIM_W - 2 * M - 60) / 3
    rows = int((TRIM_H - M - y0) // (S + 20))
    for j in range(rows):
        for i in range(3):
            x, y = M + i * (S + 30), y0 + j * (S + 20)
            c = S / 3
            ink(ctx, 2)
            for k in (1, 2):
                ctx.move_to(x + k * c, y + 8); ctx.line_to(x + k * c, y + S - 8)
                ctx.move_to(x + 8, y + k * c); ctx.line_to(x + S - 8, y + k * c)
            ctx.stroke()


def j_dots(ctx, rng, y0, act):
    n = 9
    S = min(TRIM_W - 2 * M - 40, TRIM_H - M - y0 - 90)
    gap = S / (n - 1)
    x = (TRIM_W - S) / 2
    for j in range(n):
        for i in range(n):
            ctx.arc(x + i * gap, y0 + 20 + j * gap, 4, 0, 2 * math.pi); ctx.set_source_rgb(0, 0, 0); ctx.fill()
    by = y0 + 20 + S + 40
    for k, lab in enumerate(["Score de toi :", "Score de moi :"]):
        draw_text(ctx, lab, M + 20 + k * (TRIM_W - 2 * M) / 2, by, 'Playfair Display', 16, 'left')
        rounded_rect(ctx, M + 150 + k * (TRIM_W - 2 * M) / 2, by - 24, 70, 34, 8); ink(ctx, 1.4); ctx.stroke()


def j_hangman(ctx, rng, y0, act):
    h = (TRIM_H - M - y0) / 2
    for k in range(2):
        y = y0 + k * h
        ink(ctx, 2.2)
        bx = M + 30
        ctx.move_to(bx, y + h - 30); ctx.line_to(bx + 120, y + h - 30)
        ctx.move_to(bx + 30, y + h - 30); ctx.line_to(bx + 30, y + 20); ctx.line_to(bx + 120, y + 20); ctx.line_to(bx + 120, y + 50)
        ctx.stroke()
        for i in range(8):
            ctx.move_to(M + 210 + i * 34, y + 110); ctx.line_to(M + 236 + i * 34, y + 110)
        ctx.stroke()
        draw_text(ctx, "Lettres essayées :", M + 220, y + 160, 'Kalam', 14, 'left')
        lines(ctx, M + 220, y + 160, TRIM_W - 2 * M - 220, y + h - 40, 26)


def j_battleship(ctx, rng, y0, act):
    n = 10
    S = min((TRIM_H - M - y0 - 80) / 2, TRIM_W - 2 * M - 60)
    c = S / n
    letters = 'ABCDEFGHIJ'
    for k, lab in enumerate(["Ma flotte", "La flotte adverse"]):
        x = (TRIM_W - S) / 2 + 10
        y = y0 + 20 + k * (S + 50)
        draw_text(ctx, lab, TRIM_W / 2, y - 4, 'Great Vibes', 24)
        ink(ctx, 1)
        for i in range(n + 1):
            ctx.move_to(x + i * c, y + 10); ctx.line_to(x + i * c, y + 10 + S)
            ctx.move_to(x, y + 10 + i * c); ctx.line_to(x + S, y + 10 + i * c)
        ctx.stroke()
        for i in range(n):
            draw_text(ctx, letters[i], x - 12, y + 10 + (i + 0.7) * c, 'Kalam', 11)
            draw_text(ctx, str(i + 1), x + (i + 0.5) * c, y + 6, 'Kalam', 11)


def j_acrostic(ctx, rng, y0, act, word):
    gap = (TRIM_H - M - y0) / len(word)
    for i, ch in enumerate(word):
        y = y0 + gap * (i + 0.7)
        hollow_text(ctx, ch, M + 30, y, 'Lobster', min(56, gap * 0.8), 1.8)
        ink(ctx, 0.7); ctx.set_source_rgb(*GREY)
        ctx.move_to(M + 70, y); ctx.line_to(TRIM_W - M, y); ctx.stroke()


def j_haiku(ctx, rng, y0, act, themes):
    h = (TRIM_H - M - y0) / len(themes)
    for i, t in enumerate(themes):
        y = y0 + i * h
        rounded_rect(ctx, M, y + 6, TRIM_W - 2 * M, h - 12, 14); fill_white_stroke(ctx, 1.4)
        draw_text(ctx, t, M + 20, y + 38, 'Great Vibes', 26, 'left')
        for k, syl in enumerate(['5', '7', '5']):
            yy = y + 50 + (k + 1) * (h - 70) / 3.3
            draw_text(ctx, syl, TRIM_W - M - 20, yy, 'Kalam', 11, 'right', GREY)
            ink(ctx, 0.6); ctx.set_source_rgb(*GREY); ctx.move_to(M + 20, yy); ctx.line_to(TRIM_W - M - 40, yy); ctx.stroke()


def j_words(ctx, rng, y0, act, words):
    x = M
    for w in words:
        set_font(ctx, 'Kalam', 16)
        tw = text_width(ctx, w) + 30
        rounded_rect(ctx, x, y0, tw, 34, 17); fill_white_stroke(ctx, 1.4)
        draw_text(ctx, w, x + tw / 2, y0 + 23, 'Kalam', 16)
        x += tw + 10
    lines(ctx, M, y0 + 40, TRIM_W - 2 * M, TRIM_H - M - 20, 30)


def j_log(ctx, rng, y0, act, cols):
    n = len(cols)
    w = (TRIM_W - 2 * M) / n
    rows = 18
    rh = (TRIM_H - M - y0 - 30) / rows
    rounded_rect(ctx, M, y0, TRIM_W - 2 * M, 30 + rows * rh, 10); ink(ctx, 1.4); ctx.stroke()
    for k, c in enumerate(cols):
        draw_text(ctx, c, M + (k + 0.5) * w, y0 + 20, 'Playfair Display', 12)
    ink(ctx, 0.7)
    for r in range(rows + 1):
        ctx.move_to(M, y0 + 30 + r * rh); ctx.line_to(TRIM_W - M, y0 + 30 + r * rh)
    for k in range(1, n):
        ctx.move_to(M + k * w, y0); ctx.line_to(M + k * w, y0 + 30 + rows * rh)
    ctx.stroke()


def format_quote(text):
    """Retrouve la mise en forme d'une citation du catalogue, sinon découpe automatiquement."""
    from data import quotes as Q
    key = text.replace(',', '').lower().split()
    for lst in (Q.BONHEUR, Q.FUN, Q.ANTI_COLERE, Q.COUPLE):
        for q in lst:
            if q.replace('*', '').replace('|', ' ').replace(',', '').lower().split() == key:
                return q
    words = text.split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if len(' '.join(cur)) >= 9:
            lines.append(' '.join(cur)); cur = []
    if cur:
        lines.append(' '.join(cur))
    return ' | '.join('*' + l + '*' if max(len(x) for x in l.split()) >= 5 else l for l in lines)


def journal_page(book, act, idx):
    def draw(ctx):
        rng = random.Random(book['seed'] * 1000 + idx)
        kind, title, text = act[0], act[1], act[2]
        opt = act[3] if len(act) > 3 else {}
        if kind == 'quote':
            text = format_quote(text)
            QG.draw_quote(ctx, text, TRIM_W / 2, TRIM_H / 2, TRIM_W - 2.2 * INCH, TRIM_H * 0.5, rng)
            frame(ctx, rng.choice(['flowers', 'double', 'dots', 'hearts']), M, M, TRIM_W - 2 * M, TRIM_H - 2 * M, rng, 1.8)
            scatter(ctx, rng, (M + 20, M + 20, TRIM_W - 2 * M - 40, TRIM_H - 2 * M - 40),
                    ['flower', 'heart', 'leaf', 'sparkle', 'star', 'dot'],
                    avoid=[(1.1 * INCH, TRIM_H * 0.25, TRIM_W - 2.2 * INCH, TRIM_H * 0.5)], count=40, rmin=14, rmax=36)
            return
        y0 = header(ctx, idx + 1, title, text, kids=False)
        k = kind
        if k == 'prompt': j_prompt(ctx, rng, y0, act)
        elif k == 'list': j_list(ctx, rng, y0, act, opt['n'])
        elif k == 'checklist': j_checklist(ctx, rng, y0, act, opt['items'])
        elif k == 'tracker': j_tracker(ctx, rng, y0, act, opt['legend'])
        elif k == 'gratitude': j_gratitude(ctx, rng, y0, act)
        elif k == 'boxes': j_boxes(ctx, rng, y0, act, opt['n'], opt.get('labels'))
        elif k == 'letter': j_letter(ctx, rng, y0, act)
        elif k == 'scale': j_scale(ctx, rng, y0, act, opt['items'])
        elif k == 'two_col': j_two_col(ctx, rng, y0, act, opt['cols'], opt.get('rows'))
        elif k == 'bingo': j_bingo(ctx, rng, y0, act, opt['items'])
        elif k == 'draw': j_draw(ctx, rng, y0, act, opt.get('circle'), opt.get('split'))
        elif k in ('baby',): j_fields(ctx, rng, y0, act, opt['fields'])
        elif k == 'couple_form': j_couple_form(ctx, rng, y0, act, opt['fields'])
        elif k == 'questions': j_questions(ctx, rng, y0, act, opt['items'])
        elif k == 'ttt': j_ttt(ctx, rng, y0, act)
        elif k == 'dots': j_dots(ctx, rng, y0, act)
        elif k == 'hangman': j_hangman(ctx, rng, y0, act)
        elif k == 'battleship': j_battleship(ctx, rng, y0, act)
        elif k == 'acrostic': j_acrostic(ctx, rng, y0, act, opt['word'])
        elif k == 'haiku': j_haiku(ctx, rng, y0, act, opt['themes'])
        elif k == 'words': j_words(ctx, rng, y0, act, opt['words'])
        elif k == 'log': j_log(ctx, rng, y0, act, opt['cols'])
        else:
            raise ValueError(k)
    return draw


def journal_pages(book):
    acts = {'bonheur': J.BONHEUR, 'postpartum': J.POSTPARTUM, 'ecriture': J.ECRITURE, 'couple': J.COUPLE}[book['theme']]
    assert len(acts) == 50, (book['slug'], len(acts))
    return [journal_page(book, a, i) for i, a in enumerate(acts)]
