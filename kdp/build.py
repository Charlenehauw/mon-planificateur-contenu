"""Fabrique un livre KDP complet : intérieur PDF, couverture PDF, visuels A+ et fiche produit.

Usage :
    python3 build.py --list
    python3 build.py femmes-03-mandalas        # un livre
    python3 build.py all                       # toute la gamme
"""
import glob
import math
import os
import random
import sys

import cairo
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as C
from lib.core import (INCH, TRIM_W, TRIM_H, SPINE_PER_PAGE_IN, BLEED_IN, hexrgb, draw_text, hollow_text, fit_size,
                      wrap, set_font, text_width, rounded_rect, fill_white_stroke, ink, frame, scatter, render_png,
                      colorize, place_image, paragraph, heart_path, star_path, doodle)
from generators import mandala as MG, quotes as QG, activities as AG, duo as DG
from data import sprites as SP

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'livres')
IMAGES = os.path.join(ROOT, 'images')


# =================================================================== contenu
def content_pages(book):
    g = book['gen']
    if g == 'mandala':
        return MG.pages(book)
    if g == 'quotes':
        return QG.pages(book)
    if g == 'duo':
        return DG.pages(book)
    if g == 'kids':
        return AG.kids_book_pages(book)
    if g == 'journal':
        return AG.journal_pages(book)
    if g == 'figurative':
        return figurative_pages(book)
    raise ValueError(g)


def figurative_images(book):
    files = sorted(glob.glob(os.path.join(IMAGES, book['slug'], '*.png')) +
                   glob.glob(os.path.join(IMAGES, book['slug'], '*.jpg')))
    return files


def load_lineart(path):
    im = Image.open(path).convert('L')
    a = np.array(im)
    a = np.where(a > 170, 255, 0).astype(np.uint8)          # noir et blanc franc pour l'impression
    return np.stack([a] * 3, axis=2)


def figurative_pages(book):
    files = figurative_images(book)[:50]
    out = []
    for f in files:
        def draw(ctx, f=f):
            arr = load_lineart(f)
            H, W, _ = arr.shape
            mw, mh = TRIM_W - 1.2 * INCH, TRIM_H - 1.2 * INCH
            s = min(mw / W, mh / H)
            place_image(ctx, arr, (TRIM_W - W * s) / 2, (TRIM_H - H * s) / 2, W * s, H * s)
        out.append(draw)
    return out


def is_kids(book):
    return book['audience'] == 'Enfants'


# =================================================================== pages liminaires
def title_page(book):
    def draw(ctx):
        rng = random.Random(book['seed'])
        fam = book['title_font']
        lines = split_title(book['title'])
        y = 2.6 * INCH
        for l in lines:
            size = fit_size(ctx, l, fam, TRIM_W - 2 * INCH, 52)
            hollow_text(ctx, l, TRIM_W / 2, y, fam, size, 2)
            y += size * 1.25
        y += 10
        for l in wrap(ctx, book['subtitle'], 'Playfair Display', 14, TRIM_W - 2.4 * INCH)[:4]:
            draw_text(ctx, l, TRIM_W / 2, y, 'Playfair Display', 14, color=(0.25, 0.25, 0.25))
            y += 20
        MG.mandala(ctx, TRIM_W / 2, TRIM_H - 3.0 * INCH, 1.3 * INCH, rng, lw=1.2, kids=True)
        draw_text(ctx, C.BRAND, TRIM_W / 2, TRIM_H - 0.9 * INCH, 'Playfair Display', 13)
    return draw


def copyright_page(book):
    def draw(ctx):
        y = TRIM_H - 3.4 * INCH
        txt = (f"© {C.YEAR} {C.BRAND}. Tous droits réservés.\n\n"
               "Aucune partie de ce livre ne peut être reproduite, stockée ou transmise sous quelque forme que ce soit "
               "sans l'autorisation écrite préalable de l'éditeur, à l'exception de l'usage personnel des pages à colorier.\n\n"
               "Conseil : chaque dessin est imprimé au recto seul. Glisse tout de même une feuille cartonnée sous la page "
               "si tu utilises des feutres à alcool ou des feutres très encrés.\n\n"
               "Une question, une suggestion ? Ton avis sur Amazon nous aide énormément à faire vivre nos livres. Merci !")
        paragraph(ctx, txt, 1.2 * INCH, y, TRIM_W - 2.4 * INCH, 'Playfair Display', 10.5, 1.45, 'center', (0.3, 0.3, 0.3))
    return draw


def owner_page(book):
    def draw(ctx):
        rng = random.Random(book['seed'] + 5)
        kids = is_kids(book)
        frame(ctx, 'scallop' if kids else 'double', 0.9 * INCH, 2.4 * INCH, TRIM_W - 1.8 * INCH, 4.6 * INCH, rng, 2)
        t = "Ce livre appartient à" if book['audience'] != 'Couples' else "Ce livre appartient à"
        hollow_text(ctx, t, TRIM_W / 2, 3.6 * INCH, 'Luckiest Guy' if kids else 'Lobster', 44, 2)
        ink(ctx, 1.2)
        ctx.set_source_rgb(0.4, 0.4, 0.4)
        for k in range(2 if book['audience'] == 'Couples' else 1):
            yy = 5.0 * INCH + k * 0.9 * INCH
            ctx.move_to(1.6 * INCH, yy); ctx.line_to(TRIM_W - 1.6 * INCH, yy)
        ctx.stroke()
        if book['audience'] == 'Couples':
            heart_path(ctx, TRIM_W / 2, 5.45 * INCH, 14); fill_white_stroke(ctx, 1.5)
        scatter(ctx, rng, (0.7 * INCH, 7.3 * INCH, TRIM_W - 1.4 * INCH, 2.9 * INCH),
                ['heart', 'star', 'flower', 'sparkle'] if not kids else ['star', 'heart', 'circle', 'sparkle', 'cloud'],
                count=18, rmin=16, rmax=34)
    return draw


def test_page(book):
    def draw(ctx):
        kids = is_kids(book)
        fam = 'Luckiest Guy' if kids else 'Lobster'
        hollow_text(ctx, "Teste tes couleurs" if kids else "Mon nuancier", TRIM_W / 2, 1.5 * INCH, fam, 42, 2)
        draw_text(ctx, "Essaie ici tes crayons et feutres avant de commencer.", TRIM_W / 2, 1.95 * INCH,
                  'Playfair Display', 13, color=(0.3, 0.3, 0.3))
        cols, rows = 5, 7
        w = (TRIM_W - 1.6 * INCH) / cols
        h = (TRIM_H - 3.0 * INCH) / rows
        for j in range(rows):
            for i in range(cols):
                x, y = 0.8 * INCH + i * w, 2.3 * INCH + j * h
                if kids:
                    ctx.arc(x + w / 2, y + h / 2, min(w, h) * 0.38, 0, 2 * math.pi); fill_white_stroke(ctx, 1.6)
                else:
                    rounded_rect(ctx, x + 6, y + 6, w - 12, h - 12, 10); fill_white_stroke(ctx, 1.2)
    return draw


def thanks_page(book):
    def draw(ctx):
        rng = random.Random(book['seed'] + 9)
        kids = is_kids(book)
        hollow_text(ctx, "Bravo !" if kids else "Merci !", TRIM_W / 2, 3.2 * INCH, 'Luckiest Guy' if kids else 'Lobster', 80, 2.4)
        txt = ("Tu as terminé ton livre ! Nous espérons qu'il t'a apporté de jolis moments de calme et de créativité.\n\n"
               "Si ce livre t'a plu, laisser un avis sur Amazon nous aide énormément : c'est grâce à vous que nous pouvons "
               "créer de nouveaux livres. Merci du fond du cœur !")
        paragraph(ctx, txt, 1.3 * INCH, 4.1 * INCH, TRIM_W - 2.6 * INCH, 'Playfair Display', 14, 1.45, 'center')
        for i in range(5):
            star_path(ctx, TRIM_W / 2 + (i - 2) * 0.8 * INCH, 6.6 * INCH, 22); fill_white_stroke(ctx, 2)
        scatter(ctx, rng, (0.7 * INCH, 7.3 * INCH, TRIM_W - 1.4 * INCH, 3.0 * INCH), ['heart', 'star', 'flower', 'sparkle'],
                count=16, rmin=16, rmax=34)
    return draw


def split_title(t):
    if ' – ' in t:
        a, b = t.split(' – ', 1)
        return [a, b]
    words = t.split()
    if len(words) <= 3:
        return [t]
    best, lines = None, []
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        score = abs(len(a) - len(b))
        if best is None or score < best:
            best, lines = score, [a, b]
    return lines


# =================================================================== intérieur
def blank(ctx):
    pass


def build_interior(book, pages, path):
    seq = [title_page(book), copyright_page(book), owner_page(book), blank, test_page(book), blank]
    for p in pages:
        seq += [p, blank]                       # dessin au recto, page blanche au verso
    seq += [thanks_page(book), blank]
    surf = cairo.PDFSurface(path, TRIM_W, TRIM_H)
    surf.set_metadata(cairo.PDF_METADATA_TITLE, book['title'])
    surf.set_metadata(cairo.PDF_METADATA_AUTHOR, C.BRAND)
    ctx = cairo.Context(surf)
    for fn in seq:
        ctx.save()
        fn(ctx)
        ctx.restore()
        ctx.show_page()
    surf.finish()
    return len(seq)


# =================================================================== visuels colorés
def colored_sprite(rows, cell, colors):
    h, w = len(rows), len(rows[0])
    arr = np.full((h * cell, w * cell, 3), 255, np.uint8)
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c in colors:
                arr[j * cell:(j + 1) * cell, i * cell:(i + 1) * cell] = np.array(hexrgb(colors[c])) * 255
    return arr


def hero_image(book, size=2000):
    """Illustration colorée principale (pour couverture et A+)."""
    rng = random.Random(book['seed'])
    pal = book['palette']
    g = book['gen']
    if g == 'mandala':
        a = render_png(MG.hero_draw(book['seed'] * 1000 + 3, 500), 500, 500, dpi=size / 500 * 72)
        return colorize(a, pal, rng, 'radial')
    if g == 'quotes':
        a = render_png(QG.hero_draw(book['theme'], book['seed'], 500, 500, idx=0), 500, 500, dpi=size / 500 * 72)
        return colorize(a, pal, rng, 'random')
    if 'hero_quote' in book:
        def d(ctx):
            r = random.Random(book['seed'])
            boxes, _ = QG.draw_quote(ctx, book['hero_quote'], 250, 250, 410, 310, r)
            scatter(ctx, r, (6, 6, 488, 488), ['heart', 'star', 'flower', 'sparkle', 'leaf', 'dot'], avoid=boxes, count=45, rmin=12, rmax=30)
        a = render_png(d, 500, 500, dpi=size / 500 * 72)
        return colorize(a, pal, rng, 'random')
    if g == 'duo' or g == 'journal':
        theme = 'couple' if book['audience'] == 'Couples' else 'bonheur'
        a = render_png(QG.hero_draw(theme, book['seed'], 500, 500, idx=1 if g == 'duo' else 0), 500, 500, dpi=size / 500 * 72)
        return colorize(a, pal, rng, 'random')
    if g == 'kids':
        bank = {'dino': SP.DINOS, 'reptile': SP.REPTILES, 'mixte': SP.MIXTE}[book['theme']]
        names = list(bank)[:4]
        canvas = np.full((size, size, 3), 255, np.uint8)
        for k, nm in enumerate(names):
            rows = bank[nm].strip('\n').split('\n')
            cell = int(size * 0.42 / max(len(rows), len(rows[0])))
            spr = colored_sprite(rows, cell, {'X': pal[k % 3], 'o': pal[3], 'k': '#222222'})
            h, w, _ = spr.shape
            cx, cy = (k % 2) * size // 2 + size // 4, (k // 2) * size // 2 + size // 4
            canvas[cy - h // 2:cy - h // 2 + h, cx - w // 2:cx - w // 2 + w] = spr
        return canvas
    if g == 'figurative':
        files = figurative_images(book)
        if files:
            a = load_lineart(files[0])
            im = Image.fromarray(a).resize((size, int(size * a.shape[0] / a.shape[1])))
            return colorize(np.array(im), pal, rng, 'random')
        return None
    raise ValueError(g)


def thumbs(pages, idxs, dpi=40):
    return [render_png(pages[i], TRIM_W, TRIM_H, dpi=dpi) for i in idxs if i < len(pages)]


# =================================================================== couverture
def cover_bg(book):
    pal = book['palette']
    if book['audience'] == 'Enfants':
        return hexrgb(pal[3] if len(pal) > 3 else pal[0])
    c = lightest(pal)
    return tuple(0.55 * v + 0.45 * w for v, w in zip(c, hexrgb(pal[0])))


def build_cover(book, n_pages, pages, path):
    spine = n_pages * SPINE_PER_PAGE_IN * INCH
    bleed = BLEED_IN * INCH
    W = 2 * TRIM_W + spine + 2 * bleed
    H = TRIM_H + 2 * bleed
    pal = book['palette']
    bg = cover_bg(book)
    dark = darkest(pal)
    surf = cairo.PDFSurface(path, W, H)
    ctx = cairo.Context(surf)
    rng = random.Random(book['seed'])

    # fond
    ctx.set_source_rgb(*bg); ctx.paint()
    # motif léger
    ctx.save()
    ctx.push_group()
    scatter(ctx, rng, (0, 0, W, H), ['heart', 'star', 'flower', 'sparkle', 'dot', 'circle'], count=160, rmin=8, rmax=22, lw=1.2)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.12)
    ctx.restore()

    fx = bleed + TRIM_W + spine                  # début de la 1re de couverture
    draw_front(ctx, book, fx, bleed, dark, rng)
    draw_back(ctx, book, bleed, bleed, pages, dark)
    draw_spine(ctx, book, bleed + TRIM_W, spine, H, dark)
    surf.finish()
    return W / INCH, H / INCH, spine / INCH


def darkest(pal):
    c = min((hexrgb(c) for c in pal), key=lambda c: sum(c))
    lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    k = min(1.0, 0.28 / max(lum, 1e-3))          # assombrit jusqu'à un contraste lisible
    return tuple(v * k for v in c)


def lightest(pal):
    return max((hexrgb(c) for c in pal), key=lambda c: sum(c))


def outlined_title(ctx, text, x, y, fam, size, fill, outline=(1, 1, 1), ow=7):
    set_font(ctx, fam, size)
    w = text_width(ctx, text)
    ctx.move_to(x - w / 2, y)
    ctx.text_path(text)
    ctx.set_source_rgb(*outline); ctx.set_line_width(ow); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*fill); ctx.fill()


def draw_front(ctx, book, x0, y0, dark, rng):
    pal = book['palette']
    fam = book['title_font']
    cx = x0 + TRIM_W / 2
    # titre
    lines = split_title(book['title'])
    y = y0 + 1.35 * INCH
    for i, l in enumerate(lines):
        size = fit_size(ctx, l, fam, TRIM_W - 1.1 * INCH, 74 if i == 0 else 56)
        col = hexrgb(pal[i % (len(pal) - 1)]) if is_kids(book) else dark
        outlined_title(ctx, l, cx, y, fam, size, col, ow=9 if is_kids(book) else 6)
        y += size * 1.12
    # illustration
    hero = hero_image(book)
    card_w = TRIM_W - 1.5 * INCH
    card_h = TRIM_H - (y - y0) - 2.4 * INCH
    cy0 = y + 0.05 * INCH
    rounded_rect(ctx, cx - card_w / 2 - 6, cy0 - 6, card_w + 12, card_h + 12, 30)
    ctx.set_source_rgb(*dark); ctx.fill()
    rounded_rect(ctx, cx - card_w / 2, cy0, card_w, card_h, 26)
    ctx.set_source_rgb(1, 1, 1); ctx.fill()
    if hero is not None:
        hh, hw, _ = hero.shape
        s = min((card_w - 30) / hw, (card_h - 30) / hh)
        place_image(ctx, hero, cx - hw * s / 2, cy0 + (card_h - hh * s) / 2, hw * s, hh * s)
    else:
        draw_text(ctx, "Illustration de couverture", cx, cy0 + card_h / 2 - 10, 'Playfair Display', 22, color=(0.5, 0.5, 0.5))
        draw_text(ctx, "(générée automatiquement dès que les dessins sont ajoutés)", cx, cy0 + card_h / 2 + 18,
                  'Playfair Display', 13, color=(0.5, 0.5, 0.5))
    # badge
    bx, by = x0 + TRIM_W - 1.05 * INCH, cy0 + 0.1 * INCH
    star_path(ctx, bx, by, 0.85 * INCH, 12, 0.82)
    ctx.set_source_rgb(*hexrgb(pal[1])); ctx.fill_preserve()
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(4); ctx.stroke()
    draw_text(ctx, "50", bx, by + 6, 'Luckiest Guy', 36, color=dark)
    label = "COLORIAGES" if book['kind'] == 'Coloriage' else "ACTIVITÉS"
    draw_text(ctx, label, bx, by + 24, 'Lilita One', 12.5, color=dark)
    # bandeau bas
    sub = short_sub(book)
    by2 = y0 + TRIM_H - 1.55 * INCH
    size = fit_size(ctx, sub, 'Lilita One' if is_kids(book) else 'Playfair Display', TRIM_W - 1.4 * INCH, 30)
    rounded_rect(ctx, x0 + 0.6 * INCH, by2 - 0.05 * INCH, TRIM_W - 1.2 * INCH, 0.62 * INCH, 0.31 * INCH)
    ctx.set_source_rgb(*dark); ctx.fill()
    draw_text(ctx, sub, cx, by2 + 0.38 * INCH, 'Lilita One' if is_kids(book) else 'Playfair Display', size, color=(1, 1, 1))
    tag = f"{book['age']}  •  Grand format  •  Recto seul"
    draw_text(ctx, tag, cx, y0 + TRIM_H - 0.62 * INCH, 'Playfair Display', 15, color=dark)


def short_sub(book):
    m = {
        'Coloriage': "50 dessins uniques à colorier",
        'Activités': "50 activités ludiques et variées",
    }
    if book['gen'] == 'journal':
        return "50 activités pour prendre soin de toi" if book['audience'] == 'Femmes' else "50 activités à vivre à deux"
    if book['gen'] == 'quotes':
        return "50 citations à colorier"
    if book['gen'] == 'duo':
        return "50 coloriages à partager"
    return m[book['kind']]


def draw_back(ctx, book, x0, y0, pages, dark):
    cx = x0 + TRIM_W / 2
    ctx.push_group()
    fam = book['title_font']
    hook = book['hook']
    y = y0 + 1.25 * INCH
    for l in wrap(ctx, hook, fam, 28, TRIM_W - 1.6 * INCH):
        draw_text(ctx, l, cx, y, fam, fit_size(ctx, l, fam, TRIM_W - 1.6 * INCH, 28), color=dark)
        y += 36
    y += 6
    y = paragraph(ctx, book['pitch'], x0 + 0.95 * INCH, y, TRIM_W - 1.9 * INCH, 'Playfair Display', 13, 1.4, 'center', (0.15, 0.15, 0.15))
    # vignettes
    th = thumbs(pages, [1, 7, 13], dpi=28)
    if th:
        tw = (TRIM_W - 2.2 * INCH) / 3
        for i, t in enumerate(th):
            tx = x0 + 0.85 * INCH + i * (tw + 0.25 * INCH)
            h = tw * TRIM_H / TRIM_W
            rounded_rect(ctx, tx - 3, y + 14 - 3, tw + 6, h + 6, 8); ctx.set_source_rgb(*dark); ctx.fill()
            place_image(ctx, t, tx, y + 14, tw, h, radius=6)
        y += 14 + tw * TRIM_H / TRIM_W + 10
    feats = features(book)[:4]
    y += 14
    for f in feats:
        star_path(ctx, x0 + 1.0 * INCH, y - 5, 7); ctx.set_source_rgb(*hexrgb(book['palette'][1])); ctx.fill()
        draw_text(ctx, f, x0 + 1.18 * INCH, y, 'Playfair Display', 12, 'left', (0.15, 0.15, 0.15))
        y += 20
    content = ctx.pop_group()
    rounded_rect(ctx, x0 + 0.55 * INCH, y0 + 0.6 * INCH, TRIM_W - 1.1 * INCH, y - y0 - 0.25 * INCH, 28)
    ctx.set_source_rgba(1, 1, 1, 0.94); ctx.fill()
    ctx.set_source(content); ctx.paint()
    draw_text(ctx, C.BRAND, x0 + 0.8 * INCH, y0 + TRIM_H - 0.8 * INCH, 'Playfair Display', 14, 'left', dark)
    # zone code-barres (laissée libre, KDP l'ajoute) : 2 x 1,2 po en bas à droite


def draw_spine(ctx, book, x, w, H, dark):
    ctx.save()
    ctx.translate(x + w / 2, H / 2)
    ctx.rotate(math.pi / 2)
    size = min(w * 0.5, 11)
    txt = book['title']
    draw_text(ctx, txt, -0.6 * INCH, size * 0.35, 'Playfair Display', size, color=dark)
    draw_text(ctx, C.BRAND, H / 2 - 1.6 * INCH, size * 0.35, 'Playfair Display', size * 0.8, color=dark)
    ctx.restore()


# =================================================================== fiche & A+
def features(book):
    f = []
    if book['kind'] == 'Coloriage':
        f.append("50 dessins originaux, tous différents")
    else:
        f.append("50 activités variées et progressives")
    f.append("Imprimé au recto seul : pas de bavure sur le dessin suivant")
    f.append("Grand format 21,6 x 27,9 cm (8,5 x 11 po)")
    f.append("Couverture souple mate, papier blanc")
    if is_kids(book):
        f.append("Traits épais adaptés aux petites mains")
    elif book['gen'] in ('figurative',) and 'season' in book:
        f.append("Style « bold & easy » : gros traits, zones larges")
    return f


def description_html(book):
    kids = is_kids(book)
    feats = features(book)
    li = ''.join(f"<li>{x}</li>" for x in feats)
    if kids:
        public = ("Parfait pour les enfants de " + book['age'] + " : un cadeau idéal pour un anniversaire, Noël, les vacances "
                  "ou une activité calme sans écran à la maison, en voiture ou au restaurant.")
    elif book['audience'] == 'Couples':
        public = ("Un cadeau original pour la Saint-Valentin, un anniversaire de rencontre, un mariage ou simplement "
                  "pour s'offrir une soirée complice sans écran.")
    else:
        public = ("Un moment rien qu'à toi pour déconnecter, réduire le stress et laisser parler ta créativité. "
                  "Le cadeau idéal pour une amie, une sœur, une maman ou... pour toi !")
    return (f"<p><b>{book['hook']}</b></p>"
            f"<p>{book['pitch']}</p>"
            f"<p><b>Ce que tu vas adorer :</b></p><ul>{li}</ul>"
            f"<p>{public}</p>"
            f"<p><b>Clique sur « Ajouter au panier » et offre-toi (ou offre) de jolis moments créatifs !</b></p>")


def aplus_texts(book):
    kids = is_kids(book)
    return [
        ("Module 1 – En-tête image + texte (970 x 600)", "aplus-1-banniere-970x600.png",
         book['hook'], book['pitch']),
        ("Module 2 – Image avec texte en surimpression (970 x 300)", "aplus-2-apercu-970x300.png",
         "Un aperçu de l'intérieur", "Des pages pensées pour " + ("les petites mains : traits épais, grandes zones." if kids else "un vrai moment de détente, avec des niveaux de détails variés.")),
        ("Module 3 – Trois images et texte (300 x 300)", "aplus-3a/3b/3c-300x300.png",
         "Pourquoi tu vas l'adorer", "  |  ".join(features(book)[:3])),
        ("Module 4 – Image avec texte en surimpression (970 x 300)", "aplus-4-collection-970x300.png",
         "Découvre toute la collection", f"Retrouve tous les livres {C.BRAND} : coloriages et activités pour enfants, femmes et couples."),
    ]


def build_aplus(book, pages, folder):
    pal = book['palette']
    dark = darkest(pal)
    hero = hero_image(book, 700)

    def banner(ctx):
        ctx.set_source_rgb(*cover_bg(book)); ctx.paint()
        scatter(ctx, random.Random(2), (0, 0, 970, 600), ['heart', 'star', 'sparkle', 'dot'], count=40, rmin=6, rmax=14, lw=1)
        if hero is not None:
            rounded_rect(ctx, 520, 40, 410, 520, 26); ctx.set_source_rgb(1, 1, 1); ctx.fill()
            hh, hw, _ = hero.shape
            s = min(380 / hw, 490 / hh)
            place_image(ctx, hero, 725 - hw * s / 2, 300 - hh * s / 2, hw * s, hh * s)
        y = 120
        for l in split_title(book['title']):
            size = fit_size(ctx, l, book['title_font'], 440, 52)
            outlined_title(ctx, l, 270, y, book['title_font'], size, dark, ow=5)
            y += size * 1.15
        y += 10
        for f in features(book)[:4]:
            star_path(ctx, 70, y - 5, 8); ctx.set_source_rgb(*hexrgb(pal[1])); ctx.fill()
            for l in wrap(ctx, f, 'Playfair Display', 17, 400):
                draw_text(ctx, l, 90, y, 'Playfair Display', 17, 'left', (0.1, 0.1, 0.1)); y += 22
            y += 8

    def strip(ctx):
        ctx.set_source_rgb(*cover_bg(book)); ctx.paint()
        th = thumbs(pages, [0, 5, 10, 15, 20], dpi=24)
        tw = 150
        for i, t in enumerate(th):
            x = 40 + i * 182
            place_image(ctx, t, x, 50, tw, tw * TRIM_H / TRIM_W, radius=8)
        draw_text(ctx, "Aperçu de l'intérieur", 485, 30, 'Playfair Display', 20, color=dark)

    def tile(text, idx):
        def d(ctx):
            ctx.set_source_rgb(*hexrgb(pal[idx % len(pal)])); ctx.paint()
            rounded_rect(ctx, 20, 20, 260, 260, 24); ctx.set_source_rgb(1, 1, 1); ctx.fill()
            icon = ['star', 'heart', 'flower'][idx]
            doodle(ctx, icon, 150, 95, 45, random.Random(1), 3)
            ls = wrap(ctx, text, 'Playfair Display', 19, 220)
            y = 180
            for l in ls:
                draw_text(ctx, l, 150, y, 'Playfair Display', 19, color=dark); y += 24
        return d

    def collection(ctx):
        ctx.set_source_rgb(*dark); ctx.paint()
        draw_text(ctx, f"La collection {C.BRAND}", 485, 60, 'Playfair Display', 30, color=(1, 1, 1))
        others = [b for b in C.BOOKS if b['audience'] == book['audience'] and b['slug'] != book['slug']][:6]
        for i, b in enumerate(others):
            x = 40 + (i % 3) * 300
            y = 110 + (i // 3) * 85
            rounded_rect(ctx, x, y, 285, 70, 14); ctx.set_source_rgb(*hexrgb(b['palette'][0])); ctx.fill()
            ls = wrap(ctx, b['title'], 'Playfair Display', 15, 260)[:2]
            yy = y + 30 if len(ls) > 1 else y + 41
            for l in ls:
                draw_text(ctx, l, x + 142, yy, 'Playfair Display', 15, color=(1, 1, 1)); yy += 19

    out = {}
    for name, fn, (w, h) in [('aplus-1-banniere-970x600.png', banner, (970, 600)),
                             ('aplus-2-apercu-970x300.png', strip, (970, 300)),
                             ('aplus-3a-300x300.png', tile(features(book)[0], 0), (300, 300)),
                             ('aplus-3b-300x300.png', tile(features(book)[1], 1), (300, 300)),
                             ('aplus-3c-300x300.png', tile(features(book)[2], 2), (300, 300)),
                             ('aplus-4-collection-970x300.png', collection, (970, 300))]:
        arr = render_png(fn, w, h, dpi=72 * 2)               # rendu x2 pour la netteté
        Image.fromarray(arr).save(os.path.join(folder, name), optimize=True)
        out[name] = (w * 2, h * 2)
    return out


def price(book, n_pages):
    print_cost_eur = 1.0 + 0.012 * n_pages     # estimation impression N&B grand format (amazon.fr)
    p = 7.99 if is_kids(book) else 8.99
    roy = p / 1.055 * 0.6 - print_cost_eur      # TVA livres 5,5 % ; redevance 60 %
    return p, print_cost_eur, roy


def write_fiche(book, n_pages, cover_dims, folder, ready):
    p, cost, roy = price(book, n_pages)
    W, H, spine = cover_dims if cover_dims else (None, None, n_pages * SPINE_PER_PAGE_IN)
    kw = '\n'.join(f"{i + 1}. {k}" for i, k in enumerate(book['keywords']))
    cats = '\n'.join(f"- {c}" for c in book['categories'])
    feats = '\n'.join(f"- {f}" for f in features(book))
    aplus = '\n\n'.join(f"**{m}**  \nImage : `{img}`  \nTitre : {t}  \nTexte : {d}" for m, img, t, d in aplus_texts(book))
    ai = ("Oui – contenu généré par IA (images). À déclarer dans la section « Contenu généré par l'IA » de KDP."
          if book['gen'] == 'figurative' else "Non – contenu créé par programme (dessins vectoriels originaux).")
    status = "✅ Prêt à publier" if ready else "⏳ En attente des 50 illustrations (voir prompts.md)"
    md = f"""# {book['title']}

**Statut : {status}**

## Informations KDP – Détails du livre broché

| Champ | À saisir |
|---|---|
| Langue | Français |
| Titre | {book['title']} |
| Sous-titre | {book['subtitle']} |
| Série | Collection {C.BRAND} – {book['audience']} |
| Auteur | {C.BRAND} |
| Public | {book['age']} |
| Contenu explicite | Non |
| Livre à faible contenu (low-content) | Non – laisse décoché pour obtenir l'ISBN gratuit et l'aperçu « Feuilleter » |
| Contenu généré par IA | {ai} |

### Description (à coller dans l'éditeur KDP, en mode HTML)

```html
{description_html(book)}
```

### 7 mots-clés
{kw}

### Catégories (choisir les 3 plus proches dans le sélecteur KDP)
{cats}

## Caractéristiques
{feats}

## Contenu du livre broché (paramètres d'impression)

| Paramètre | Valeur |
|---|---|
| ISBN | ISBN gratuit KDP |
| Encre et papier | Noir et blanc, papier blanc |
| Format | 8,5 x 11 po (21,59 x 27,94 cm) |
| Fond perdu | Sans fond perdu (intérieur) |
| Finition de couverture | Mate |
| Nombre de pages | {n_pages} |
| Épaisseur du dos | {spine:.3f} po |
| Fichier intérieur | `interieur.pdf` |
| Fichier couverture | `couverture.pdf` {f'({W:.3f} x {H:.3f} po, fond perdu inclus)' if W else ''} |

## Prix conseillé
- Prix : **{p:.2f} €** (amazon.fr) – adapte les autres marketplaces avec le convertisseur KDP
- Coût d'impression estimé : ~{cost:.2f} € → redevance estimée : ~{roy:.2f} € par vente (à vérifier dans le calculateur KDP)

## Contenu A+ (KDP > Marketing > Contenu A+)

{aplus}
"""
    with open(os.path.join(folder, 'fiche-produit.md'), 'w') as f:
        f.write(md)


def write_prompts(book, folder):
    tpl = C.KIDS_PROMPT if is_kids(book) else (C.COSY_PROMPT if 'season' in book else C.ADULT_PROMPT)
    lines = [f"# Prompts – {book['title']}\n",
             f"Génère chaque image en **portrait 3:4 ou 8.5:11**, puis enregistre-la dans `kdp/images/{book['slug']}/` "
             "en la nommant `01.png`, `02.png`... `50.png`. Relance ensuite `python3 build.py " + book['slug'] + "`.\n"]
    for i, s in enumerate(book['subjects'], 1):
        lines.append(f"{i:02d}. {tpl.format(s=s)}")
    with open(os.path.join(folder, 'prompts.md'), 'w') as f:
        f.write('\n\n'.join(lines) + '\n')
    os.makedirs(os.path.join(IMAGES, book['slug']), exist_ok=True)


# =================================================================== orchestration
def build(slug):
    book = C.get(slug)
    folder = os.path.join(OUT, slug)
    os.makedirs(folder, exist_ok=True)
    os.makedirs(os.path.join(folder, 'aplus'), exist_ok=True)
    pages = content_pages(book)
    ready = len(pages) >= 50
    if book['gen'] == 'figurative':
        write_prompts(book, folder)
    n_pages = 6 + 2 * 50 + 2
    dims = None
    if ready:
        n_pages = build_interior(book, pages[:50], os.path.join(folder, 'interieur.pdf'))
        dims = build_cover(book, n_pages, pages, os.path.join(folder, 'couverture.pdf'))
        build_aplus(book, pages, os.path.join(folder, 'aplus'))
        preview(folder)
    write_fiche(book, n_pages, dims, folder, ready)
    print(f"{slug}: {'OK' if ready else 'en attente d illustrations'} ({n_pages} pages)")


def preview(folder):
    """Aperçu PNG de la couverture pour contrôle rapide."""
    try:
        import pymupdf
        doc = pymupdf.open(os.path.join(folder, 'couverture.pdf'))
        doc[0].get_pixmap(dpi=40).save(os.path.join(folder, 'apercu-couverture.png'))
    except Exception as e:  # aperçu facultatif
        print('aperçu ignoré :', e)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] == '--list':
        for b in C.BOOKS:
            print(b['slug'], '-', b['title'])
    elif args[0] == 'all':
        for b in C.BOOKS:
            build(b['slug'])
    else:
        for s in args:
            build(s)
