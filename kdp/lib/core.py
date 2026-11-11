"""Primitives de dessin partagées (cairo, unités = points, 72 pt = 1 pouce)."""
import math
import random

import cairo
import numpy as np

INCH = 72.0
TRIM_W, TRIM_H = 8.5 * INCH, 11 * INCH          # format KDP 8,5 x 11 po (21,59 x 27,94 cm)
MARGIN = 0.6 * INCH                              # marge de sécurité (> exigences KDP sans fond perdu)
SPINE_PER_PAGE_IN = 0.002252                     # papier blanc KDP
BLEED_IN = 0.125

BLACK = (0, 0, 0)
WHITE = (1, 1, 1)


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ---------------------------------------------------------------- styles
def ink(ctx, width=2.0):
    ctx.set_source_rgb(*BLACK)
    ctx.set_line_width(width)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)


def fill_white_stroke(ctx, width=2.0):
    ctx.set_source_rgb(*WHITE)
    ctx.fill_preserve()
    ink(ctx, width)
    ctx.stroke()


# ---------------------------------------------------------------- texte
def set_font(ctx, family, size, bold=False, italic=False):
    ctx.select_font_face(family,
                         cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def text_width(ctx, s):
    xb, yb, w, h, xa, ya = ctx.text_extents(s)
    return xa


def draw_text(ctx, s, x, y, family, size, align='center', color=BLACK, bold=False, italic=False):
    set_font(ctx, family, size, bold, italic)
    w = text_width(ctx, s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    ctx.move_to(x, y)
    ctx.set_source_rgb(*color)
    ctx.show_text(s)
    ctx.new_path()
    return w


def hollow_text(ctx, s, x, y, family, size, stroke=2.2, align='center', fill=WHITE):
    """Texte « bulle » à colorier : intérieur blanc, contour noir."""
    set_font(ctx, family, size)
    w = text_width(ctx, s)
    if align == 'center':
        x -= w / 2
    ctx.move_to(x, y)
    ctx.text_path(s)
    ctx.set_source_rgb(*fill)
    ctx.fill_preserve()
    ink(ctx, stroke)
    ctx.stroke()
    return w


def fit_size(ctx, s, family, max_w, max_size, min_size=8):
    size = max_size
    while size > min_size:
        set_font(ctx, family, size)
        if text_width(ctx, s) <= max_w:
            return size
        size -= 1
    return min_size


def wrap(ctx, text, family, size, max_w):
    set_font(ctx, family, size)
    lines, cur = [], ''
    for word in text.split():
        t = (cur + ' ' + word).strip()
        if text_width(ctx, t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(ctx, text, x, y, w, family, size, leading=1.35, align='left', color=BLACK):
    yy = y
    for para in text.split('\n'):
        for line in wrap(ctx, para, family, size, w) or ['']:
            if align == 'center':
                draw_text(ctx, line, x + w / 2, yy, family, size, 'center', color)
            else:
                draw_text(ctx, line, x, yy, family, size, 'left', color)
            yy += size * leading
    return yy


# ---------------------------------------------------------------- formes
def heart_path(ctx, cx, cy, s):
    ctx.move_to(cx, cy + s * 0.9)
    ctx.curve_to(cx - s * 1.3, cy + s * 0.1, cx - s * 0.9, cy - s * 0.95, cx, cy - s * 0.35)
    ctx.curve_to(cx + s * 0.9, cy - s * 0.95, cx + s * 1.3, cy + s * 0.1, cx, cy + s * 0.9)
    ctx.close_path()


def star_path(ctx, cx, cy, r, n=5, inner=0.45, rot=-math.pi / 2):
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * inner
        a = rot + i * math.pi / n
        (ctx.move_to if i == 0 else ctx.line_to)(cx + rr * math.cos(a), cy + rr * math.sin(a))
    ctx.close_path()


def rounded_rect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def petal_path(ctx, cx, cy, r0, r1, a, half_width, pointed=True):
    """Pétale entre les rayons r0 et r1, centré sur l'angle a."""
    ca, sa = math.cos(a), math.sin(a)
    px, py = -sa, ca
    bx, by = cx + r0 * ca, cy + r0 * sa
    tx, ty = cx + r1 * ca, cy + r1 * sa
    mid = r0 + (r1 - r0) * 0.55
    mx, my = cx + mid * ca, cy + mid * sa
    hw = half_width
    ctx.move_to(bx, by)
    if pointed:
        ctx.curve_to(mx + px * hw, my + py * hw, tx - ca * (r1 - r0) * 0.15 + px * hw * 0.4,
                     ty - sa * (r1 - r0) * 0.15 + py * hw * 0.4, tx, ty)
        ctx.curve_to(tx - ca * (r1 - r0) * 0.15 - px * hw * 0.4, ty - sa * (r1 - r0) * 0.15 - py * hw * 0.4,
                     mx - px * hw, my - py * hw, bx, by)
    else:
        ctx.curve_to(mx + px * hw * 1.2, my + py * hw * 1.2, tx + px * hw * 1.1, ty + py * hw * 1.1, tx, ty)
        ctx.curve_to(tx - px * hw * 1.1, ty - py * hw * 1.1, mx - px * hw * 1.2, my - py * hw * 1.2, bx, by)
    ctx.close_path()


def flower(ctx, cx, cy, r, n=None, rng=random, lw=1.8, style=None):
    n = n or rng.choice([5, 6, 7, 8])
    style = style or rng.choice(['round', 'pointed', 'double'])
    rot = rng.random() * math.pi
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        petal_path(ctx, cx, cy, r * 0.25, r, a, r * (1.6 / n) * 1.3, pointed=(style == 'pointed'))
        fill_white_stroke(ctx, lw)
        if style == 'double':
            petal_path(ctx, cx, cy, r * 0.3, r * 0.7, a, r * (1.6 / n) * 0.6, pointed=True)
            fill_white_stroke(ctx, lw * 0.8)
    ctx.arc(cx, cy, r * 0.3, 0, 2 * math.pi)
    fill_white_stroke(ctx, lw)
    if r > 18:
        ctx.arc(cx, cy, r * 0.14, 0, 2 * math.pi)
        fill_white_stroke(ctx, lw * 0.8)


def leaf(ctx, cx, cy, r, a, lw=1.6):
    petal_path(ctx, cx, cy, 0, r, a, r * 0.32, pointed=True)
    fill_white_stroke(ctx, lw)
    ink(ctx, lw * 0.7)
    ctx.move_to(cx, cy)
    ctx.line_to(cx + r * 0.85 * math.cos(a), cy + r * 0.85 * math.sin(a))
    ctx.stroke()


def swirl(ctx, cx, cy, r, turns=1.6, lw=1.6, rot=0.0):
    ink(ctx, lw)
    steps = 60
    for i in range(steps + 1):
        t = i / steps
        a = rot + t * turns * 2 * math.pi
        rr = r * (1 - t * 0.85)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    ctx.stroke()


def sparkle(ctx, cx, cy, r, lw=1.4):
    ctx.move_to(cx, cy - r)
    for (dx, dy) in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        pass
    k = 0.22
    pts = [(0, -r), (k * r, -k * r), (r, 0), (k * r, k * r), (0, r), (-k * r, k * r), (-r, 0), (-k * r, -k * r)]
    for i, (x, y) in enumerate(pts):
        (ctx.move_to if i == 0 else ctx.line_to)(cx + x, cy + y)
    ctx.close_path()
    fill_white_stroke(ctx, lw)


def cloud(ctx, cx, cy, w, lw=1.8):
    h = w * 0.45
    ctx.new_path()
    ctx.arc(cx - w * 0.25, cy, h * 0.45, math.pi * 0.5, math.pi * 1.5)
    ctx.arc(cx - w * 0.05, cy - h * 0.35, h * 0.5, math.pi, math.pi * 1.95)
    ctx.arc(cx + w * 0.22, cy - h * 0.15, h * 0.42, math.pi * 1.25, math.pi * 0.3 + 2 * math.pi)
    ctx.line_to(cx - w * 0.25, cy + h * 0.45)
    ctx.close_path()
    fill_white_stroke(ctx, lw)


def doodle(ctx, kind, cx, cy, r, rng, lw=1.7):
    if kind == 'heart':
        heart_path(ctx, cx, cy, r * 0.8)
        fill_white_stroke(ctx, lw)
        if r > 16 and rng.random() < 0.5:
            heart_path(ctx, cx, cy + r * 0.05, r * 0.45)
            fill_white_stroke(ctx, lw * 0.8)
    elif kind == 'star':
        star_path(ctx, cx, cy, r, rot=-math.pi / 2 + rng.uniform(-0.3, 0.3))
        fill_white_stroke(ctx, lw)
    elif kind == 'flower':
        flower(ctx, cx, cy, r, rng=rng, lw=lw)
    elif kind == 'leaf':
        leaf(ctx, cx - r * 0.5, cy + r * 0.5, r * 1.3, rng.uniform(0, 2 * math.pi), lw)
    elif kind == 'dot':
        ctx.arc(cx, cy, r * 0.35, 0, 2 * math.pi)
        fill_white_stroke(ctx, lw)
    elif kind == 'circle':
        ctx.arc(cx, cy, r * 0.8, 0, 2 * math.pi)
        fill_white_stroke(ctx, lw)
        ctx.arc(cx, cy, r * 0.45, 0, 2 * math.pi)
        fill_white_stroke(ctx, lw)
    elif kind == 'sparkle':
        sparkle(ctx, cx, cy, r, lw)
    elif kind == 'swirl':
        swirl(ctx, cx, cy, r * 0.8, lw=lw, rot=rng.uniform(0, 6.3))
    elif kind == 'cloud':
        cloud(ctx, cx, cy, r * 2, lw)
    elif kind == 'bolt':
        s = r / 10
        pts = [(-2, -10), (5, -10), (1, -2), (6, -2), (-4, 10), (-1, 1), (-6, 1)]
        for i, (x, y) in enumerate(pts):
            (ctx.move_to if i == 0 else ctx.line_to)(cx + x * s, cy + y * s)
        ctx.close_path()
        fill_white_stroke(ctx, lw)
    elif kind == 'bubble':
        ctx.new_path()
        ctx.save(); ctx.translate(cx, cy); ctx.scale(1, 0.7)
        ctx.arc(0, 0, r, 0.35, 2 * math.pi + 0.05)
        ctx.restore()
        ctx.line_to(cx + r * 0.2, cy + r * 1.0)
        ctx.close_path()
        fill_white_stroke(ctx, lw)
    elif kind == 'drop':
        ctx.move_to(cx, cy - r)
        ctx.curve_to(cx + r * 0.9, cy, cx + r * 0.6, cy + r * 0.8, cx, cy + r * 0.8)
        ctx.curve_to(cx - r * 0.6, cy + r * 0.8, cx - r * 0.9, cy, cx, cy - r)
        fill_white_stroke(ctx, lw)


def scatter(ctx, rng, box, kinds, avoid=(), count=60, rmin=10, rmax=28, lw=1.7, tries=4000):
    """Disperse des motifs sans chevauchement dans box=(x,y,w,h), en évitant les rectangles 'avoid'."""
    x0, y0, w, h = box
    placed = []
    for _ in range(tries):
        if len(placed) >= count:
            break
        r = rng.uniform(rmin, rmax)
        cx, cy = rng.uniform(x0 + r, x0 + w - r), rng.uniform(y0 + r, y0 + h - r)
        bad = False
        for (ax, ay, aw, ah) in avoid:
            if ax - r < cx < ax + aw + r and ay - r < cy < ay + ah + r:
                bad = True
                break
        if bad:
            continue
        if any((cx - px) ** 2 + (cy - py) ** 2 < (r + pr + 4) ** 2 for px, py, pr in placed):
            continue
        placed.append((cx, cy, r))
    for cx, cy, r in placed:
        doodle(ctx, rng.choice(kinds), cx, cy, r, rng, lw)
    return placed


# ---------------------------------------------------------------- cadres
def frame(ctx, style, x, y, w, h, rng, lw=2.0):
    if style == 'simple':
        rounded_rect(ctx, x, y, w, h, 18)
        ink(ctx, lw)
        ctx.stroke()
    elif style == 'double':
        rounded_rect(ctx, x, y, w, h, 22)
        ink(ctx, lw)
        ctx.stroke()
        rounded_rect(ctx, x + 8, y + 8, w - 16, h - 16, 16)
        ink(ctx, lw * 0.7)
        ctx.stroke()
    elif style == 'dots':
        rounded_rect(ctx, x, y, w, h, 18)
        ink(ctx, lw)
        ctx.stroke()
        step = 26
        for i in range(int(w // step)):
            for yy in (y, y + h):
                ctx.arc(x + 13 + i * step + (w % step) / 2, yy, 5, 0, 2 * math.pi)
                fill_white_stroke(ctx, lw * 0.7)
        for i in range(1, int(h // step)):
            for xx in (x, x + w):
                ctx.arc(xx, y + i * step + (h % step) / 2, 5, 0, 2 * math.pi)
                fill_white_stroke(ctx, lw * 0.7)
    elif style == 'scallop':
        r = 12
        nx, ny = int(w // (2 * r)), int(h // (2 * r))
        rx, ry = w / nx / 2, h / ny / 2
        ink(ctx, lw)
        for i in range(nx):
            ctx.new_sub_path(); ctx.arc(x + rx + 2 * rx * i, y, rx, math.pi, 0)
            ctx.new_sub_path(); ctx.arc(x + rx + 2 * rx * i, y + h, rx, 0, math.pi)
        for j in range(ny):
            ctx.new_sub_path(); ctx.arc(x, y + ry + 2 * ry * j, ry, math.pi / 2, 3 * math.pi / 2)
            ctx.new_sub_path(); ctx.arc(x + w, y + ry + 2 * ry * j, ry, -math.pi / 2, math.pi / 2)
        ctx.stroke()
        ctx.rectangle(x, y, w, h)
        ctx.stroke()
    elif style == 'hearts':
        rounded_rect(ctx, x, y, w, h, 18)
        ink(ctx, lw)
        ctx.stroke()
        for (cx, cy) in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
            heart_path(ctx, cx, cy, 20)
            fill_white_stroke(ctx, lw)
    elif style == 'flowers':
        rounded_rect(ctx, x, y, w, h, 18)
        ink(ctx, lw)
        ctx.stroke()
        for (cx, cy) in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
            flower(ctx, cx, cy, 26, rng=rng, lw=lw)


def page_number(ctx, n, w=TRIM_W, h=TRIM_H):
    draw_text(ctx, str(n), w / 2, h - 0.35 * INCH, 'Josefin Sans', 9, color=(0.4, 0.4, 0.4))


# ---------------------------------------------------------------- rendu raster / mise en couleur
def render_png(draw_fn, w_pt, h_pt, dpi=150):
    """Rend une fonction de dessin dans une image numpy RGB (fond blanc)."""
    scale = dpi / INCH
    W, H = int(w_pt * scale), int(h_pt * scale)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    ctx.scale(scale, scale)
    draw_fn(ctx)
    surf.flush()
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data()).copy()
    return buf[:, :, [2, 1, 0]]  # BGRA -> RGB


def colorize(img, palette, rng, mode='radial', center=None, keep_bg=True, bg_color=None):
    """Remplit les zones blanches fermées d'un dessin au trait avec une palette."""
    from scipy import ndimage
    gray = img.mean(axis=2)
    white = gray > 200
    labels, n = ndimage.label(white)
    out = img.copy()
    H, W = gray.shape
    border = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    cy, cx = center if center else (H / 2, W / 2)
    idx = np.arange(1, n + 1)
    sizes = ndimage.sum(np.ones_like(labels), labels, idx)
    ys, xs = np.array(ndimage.center_of_mass(white, labels, idx)).T if n else ([], [])
    pal = [np.array(hexrgb(c)) * 255 for c in palette]
    lut = np.zeros((n + 1, 3), np.uint8)
    lut[0] = (0, 0, 0)
    ring_colors = {}
    for i in range(n):
        lab = i + 1
        if lab in border and keep_bg:
            lut[lab] = (np.array(hexrgb(bg_color)) * 255) if bg_color else (255, 255, 255)
            continue
        if sizes[i] < 6:
            lut[lab] = (40, 40, 40)
            continue
        if mode == 'radial':
            d = math.hypot(xs[i] - cx, ys[i] - cy)
            key = (int(d / 6), int(sizes[i] / 400))
            if key not in ring_colors:
                ring_colors[key] = pal[rng.randrange(len(pal))]
            lut[lab] = ring_colors[key]
        else:
            lut[lab] = pal[rng.randrange(len(pal))]
    colored = lut[labels]
    lines = ~white
    # conserver le trait (antialiasing) : mélange par l'intensité de gris
    alpha = np.clip((gray - 60) / 160.0, 0, 1)[..., None]
    res = colored * alpha + img * (1 - alpha)
    res[lines & (gray < 60)] = img[lines & (gray < 60)]
    return res.astype(np.uint8)


_KEEP = []


def np_to_surface(arr):
    H, W, _ = arr.shape
    bgra = np.zeros((H, W, 4), np.uint8)
    bgra[:, :, 0] = arr[:, :, 2]
    bgra[:, :, 1] = arr[:, :, 1]
    bgra[:, :, 2] = arr[:, :, 0]
    bgra[:, :, 3] = 255
    surf = cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_RGB24, W, H, W * 4)
    _KEEP.append(bgra)   # garder le tampon en vie jusqu'à la fin du PDF
    return surf


def place_image(ctx, arr, x, y, w, h=None, radius=0):
    surf = np_to_surface(arr)
    H, W, _ = arr.shape
    if h is None:
        h = w * H / W
    ctx.save()
    if radius:
        rounded_rect(ctx, x, y, w, h, radius)
        ctx.clip()
    ctx.translate(x, y)
    ctx.scale(w / W, h / H)
    ctx.set_source_surface(surf, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BEST)
    ctx.paint()
    ctx.restore()
    return h
