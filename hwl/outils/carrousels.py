"""Génère les carrousels HWL (1080x1350) dans l'identité de la marque."""
import json, sys, pathlib, html
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
FONTS = ROOT / "node_modules/@fontsource"

def font_face(fam, path, weight, style="normal"):
    return f"@font-face{{font-family:'{fam}';src:url('file://{FONTS / path}') format('woff2');font-weight:{weight};font-style:{style};}}"

CSS = "".join([
    font_face("Oswald", "oswald/files/oswald-latin-600-normal.woff2", 600),
    font_face("Oswald", "oswald/files/oswald-latin-500-normal.woff2", 500),
    font_face("Playfair", "playfair-display/files/playfair-display-latin-400-italic.woff2", 400, "italic"),
    font_face("Playfair", "playfair-display/files/playfair-display-latin-600-italic.woff2", 600, "italic"),
    font_face("Inter", "inter/files/inter-latin-400-normal.woff2", 400),
    font_face("Inter", "inter/files/inter-latin-600-normal.woff2", 600),
    font_face("Inter", "inter/files/inter-latin-700-normal.woff2", 700),
]) + """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#F0EFEE;font-family:Inter;color:#2F3437;position:relative;overflow:hidden}
.halo{position:absolute;border-radius:50%;filter:blur(60px);opacity:.7}
.top{position:absolute;top:58px;left:0;right:0;text-align:center;font:600 22px Inter;letter-spacing:6px;color:#4E6F94}
.top:before,.top:after{content:"";display:inline-block;width:60px;height:2px;background:#C9B98A;vertical-align:middle;margin:0 22px}
.wrap{position:absolute;left:80px;right:80px;top:170px}
.kicker{font:600 26px Inter;letter-spacing:4px;color:#E6B93A;text-transform:uppercase;margin-bottom:22px}
h1{font:600 104px/1.1 Oswald;color:#6F8FB3;text-transform:uppercase;letter-spacing:.5px}
h2{font:600 84px/1.1 Oswald;color:#6F8FB3;text-transform:uppercase}
h1 em,h2 em{font-style:normal;color:#E6B93A}
p.body{font:400 38px/1.5 Inter;margin-top:34px;color:#2F3437}
p.body b{font-weight:700}
.big{font:600 260px/1 Oswald;color:#E6B93A;margin-top:30px}
.src{position:absolute;left:80px;right:80px;bottom:150px;font:400 24px/1.4 Inter;color:#8A8F94}
.cards{margin-top:46px;display:flex;flex-direction:column;gap:22px}
.card{background:#fff;border-radius:60px;padding:28px 40px;font:600 34px Inter;box-shadow:0 6px 18px rgba(78,111,148,.10);display:flex;align-items:center;gap:22px}
.card .s{color:#E6B93A;font-size:34px}
.card.x .s{color:#8A8F94}
.card.x{color:#8A8F94}
.num{font:600 40px Oswald;color:#fff;background:#6F8FB3;border-radius:50%;width:62px;height:62px;display:flex;align-items:center;justify-content:center;flex:none}
.bottom{position:absolute;bottom:62px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center}
.glisse{font:italic 400 34px Playfair;color:#4E6F94}
.glisse span{color:#E6B93A;font-style:normal;font-family:Inter;font-weight:700}
.pg{font:600 26px Inter;letter-spacing:2px;color:#8A8F94}
.ill{position:absolute;left:0;right:0;bottom:200px;display:flex;justify-content:center}
.center{text-align:center;left:80px;right:80px}
.btn{display:inline-flex;align-items:center;gap:22px;background:#E6B93A;color:#fff;font:600 58px Oswald;padding:34px 64px;border-radius:26px;box-shadow:0 10px 26px rgba(230,185,58,.35);margin-top:70px;text-transform:uppercase}
.script{font:italic 400 44px Playfair;color:#4E6F94;margin-top:36px}
.handle{position:absolute;bottom:150px;left:0;right:0;text-align:center;font:400 26px Inter;color:#8A8F94}
.hl{background:linear-gradient(transparent 58%,#F3DC8E 58%);padding:0 4px}
.strike{text-decoration:line-through;text-decoration-color:#E6B93A;text-decoration-thickness:6px}
"""

STAR = """<svg width="{s}" height="{s}" viewBox="0 0 100 100"><path d="M50 0 C55 35 65 45 100 50 C65 55 55 65 50 100 C45 65 35 55 0 50 C35 45 45 35 50 0Z" fill="#E6B93A"/><circle cx="42" cy="48" r="3.2" fill="#2F3437"/><circle cx="58" cy="48" r="3.2" fill="#2F3437"/><path d="M43 56 Q50 62 57 56" stroke="#2F3437" stroke-width="2.6" fill="none" stroke-linecap="round"/></svg>"""
SPARK = """<svg width="{s}" height="{s}" viewBox="0 0 100 100"><path d="M50 0 C55 35 65 45 100 50 C65 55 55 65 50 100 C45 65 35 55 0 50 C35 45 45 35 50 0Z" fill="#E6B93A"/></svg>"""

ILL = {
"facture": """<svg width="420" height="420" viewBox="0 0 200 200"><rect x="45" y="20" width="110" height="150" rx="10" fill="#fff" stroke="#6F8FB3" stroke-width="6"/><rect x="62" y="44" width="56" height="10" rx="4" fill="#DCE5EF"/><rect x="62" y="66" width="76" height="8" rx="4" fill="#DCE5EF"/><rect x="62" y="82" width="76" height="8" rx="4" fill="#DCE5EF"/><rect x="62" y="98" width="50" height="8" rx="4" fill="#DCE5EF"/><rect x="62" y="128" width="76" height="20" rx="6" fill="#F3DC8E"/><circle cx="150" cy="150" r="30" fill="#E6B93A"/><path d="M137 150 l9 9 l18 -19" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
"inbox": """<svg width="420" height="360" viewBox="0 0 200 170"><path d="M30 70 L60 25 H140 L170 70 V140 a10 10 0 0 1 -10 10 H40 a10 10 0 0 1 -10 -10Z" fill="#fff" stroke="#6F8FB3" stroke-width="6" stroke-linejoin="round"/><path d="M30 70 H70 a30 22 0 0 0 60 0 H170" fill="none" stroke="#6F8FB3" stroke-width="6"/><rect x="80" y="8" width="40" height="52" rx="5" fill="#F3DC8E" stroke="#E6B93A" stroke-width="4"/><path d="M100 30 v28 m-12 -12 l12 12 l12 -12" stroke="#4E6F94" stroke-width="5" fill="none" stroke-linecap="round"/></svg>""",
"calendrier": """<svg width="400" height="380" viewBox="0 0 200 190"><rect x="25" y="35" width="150" height="140" rx="14" fill="#fff" stroke="#6F8FB3" stroke-width="6"/><rect x="25" y="35" width="150" height="38" rx="14" fill="#6F8FB3"/><rect x="25" y="58" width="150" height="15" fill="#6F8FB3"/><rect x="58" y="20" width="10" height="30" rx="5" fill="#4E6F94"/><rect x="132" y="20" width="10" height="30" rx="5" fill="#4E6F94"/><text x="100" y="140" text-anchor="middle" font-family="Oswald" font-weight="600" font-size="62" fill="#E6B93A">1/09</text><text x="100" y="62" text-anchor="middle" font-family="Oswald" font-weight="600" font-size="20" fill="#fff" letter-spacing="3">2027</text></svg>""",
"pdf": """<svg width="380" height="380" viewBox="0 0 200 200"><rect x="50" y="25" width="100" height="135" rx="10" fill="#fff" stroke="#8A8F94" stroke-width="6"/><text x="100" y="105" text-anchor="middle" font-family="Oswald" font-weight="600" font-size="40" fill="#8A8F94">PDF</text><path d="M35 175 L165 30" stroke="#E6B93A" stroke-width="12" stroke-linecap="round"/></svg>""",
"horloge": """<svg width="400" height="400" viewBox="0 0 200 200"><circle cx="100" cy="105" r="72" fill="#fff" stroke="#6F8FB3" stroke-width="7"/><path d="M100 105 V62 M100 105 L132 122" stroke="#4E6F94" stroke-width="8" stroke-linecap="round"/><circle cx="100" cy="105" r="7" fill="#E6B93A"/><rect x="88" y="18" width="24" height="14" rx="5" fill="#6F8FB3"/><path d="M28 60 l18 12 M172 60 l-18 12" stroke="#E6B93A" stroke-width="7" stroke-linecap="round"/></svg>""",
"calcul": """<svg width="360" height="400" viewBox="0 0 180 200"><rect x="30" y="15" width="120" height="170" rx="16" fill="#fff" stroke="#6F8FB3" stroke-width="6"/><rect x="46" y="32" width="88" height="38" rx="6" fill="#DCE5EF"/><text x="126" y="60" text-anchor="end" font-family="Oswald" font-weight="600" font-size="24" fill="#4E6F94">1 200 €</text><g fill="#F0EFEE" stroke="#6F8FB3" stroke-width="3"><rect x="46" y="84" width="24" height="20" rx="5"/><rect x="78" y="84" width="24" height="20" rx="5"/><rect x="46" y="112" width="24" height="20" rx="5"/><rect x="78" y="112" width="24" height="20" rx="5"/><rect x="46" y="140" width="24" height="20" rx="5"/><rect x="78" y="140" width="24" height="20" rx="5"/></g><rect x="110" y="84" width="24" height="76" rx="5" fill="#E6B93A"/></svg>""",
"robot": """<svg width="400" height="380" viewBox="0 0 200 190"><line x1="100" y1="20" x2="100" y2="45" stroke="#6F8FB3" stroke-width="6"/><circle cx="100" cy="16" r="9" fill="#E6B93A"/><rect x="40" y="45" width="120" height="95" rx="24" fill="#fff" stroke="#6F8FB3" stroke-width="6"/><circle cx="75" cy="88" r="12" fill="#6F8FB3"/><circle cx="125" cy="88" r="12" fill="#6F8FB3"/><path d="M78 115 Q100 128 122 115" stroke="#4E6F94" stroke-width="6" fill="none" stroke-linecap="round"/><rect x="60" y="148" width="80" height="26" rx="10" fill="#DCE5EF"/></svg>""",
"coeur": """<svg width="380" height="360" viewBox="0 0 200 190"><path d="M100 170 C40 125 20 95 20 65 C20 40 40 22 63 22 C80 22 93 32 100 45 C107 32 120 22 137 22 C160 22 180 40 180 65 C180 95 160 125 100 170Z" fill="#fff" stroke="#6F8FB3" stroke-width="7"/><path d="M70 85 l20 20 l40 -40" stroke="#E6B93A" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
}

def page(slide, i, n):
    halos = ('<div class="halo" style="width:520px;height:520px;background:#DCE5EF;right:-160px;top:-120px"></div>'
             '<div class="halo" style="width:460px;height:460px;background:#F5E7C2;left:-180px;bottom:-140px"></div>')
    t = slide["type"]
    inner = ""
    if t == "cover":
        inner = f'<div class="wrap"><div class="kicker">{slide["kicker"]}</div><h1>{slide["title"]}</h1>' + (f'<p class="body">{slide["body"]}</p>' if slide.get("body") else "") + '</div>'
    elif t == "text":
        inner = f'<div class="wrap"><div class="kicker">{slide["kicker"]}</div><h2>{slide["title"]}</h2><p class="body">{slide["body"]}</p>'
        if slide.get("cards"):
            inner += '<div class="cards">' + "".join(
                f'<div class="card{" x" if slide.get("x") else ""}"><span class="s">{"✕" if slide.get("x") else "✦"}</span>{c}</div>' for c in slide["cards"]) + '</div>'
        if slide.get("steps"):
            inner += '<div class="cards">' + "".join(f'<div class="card"><span class="num">{k+1}</span>{c}</div>' for k, c in enumerate(slide["steps"])) + '</div>'
        inner += '</div>'
    elif t == "stat":
        inner = f'<div class="wrap"><div class="kicker">{slide["kicker"]}</div><div class="big">{slide["big"]}</div><p class="body">{slide["body"]}</p></div><div class="src">Source : {slide["src"]}</div>'
    elif t == "cta":
        inner = (f'<div class="wrap center" style="top:250px;position:absolute"><h2>{slide["title"]}</h2>'
                 f'<div class="btn">{slide["btn"]}</div><div class="script">{slide["script"]}</div>'
                 f'<div style="margin-top:60px">{STAR.format(s=170)}</div></div>'
                 f'<div class="handle">{slide.get("note","@hwl.assistantevirtuelle")}</div>')
    ill = ""
    if slide.get("ill"):
        ill = f'<div class="ill">{ILL[slide["ill"]]}</div>'
    deco = ""
    if slide.get("spark"):
        deco = f'<div style="position:absolute;right:110px;bottom:520px">{SPARK.format(s=70)}</div>'
    if slide.get("star"):
        deco += f'<div style="position:absolute;right:120px;bottom:210px">{STAR.format(s=150)}</div>'
    glisse = '<div class="glisse">Glisse <span>→</span></div>' if i < n else '<div></div>'
    bottom = f'<div class="bottom">{glisse}<div class="pg">{i:02d}/{n:02d}</div></div>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{halos}<div class="top">HWL · ASSISTANTE VIRTUELLE</div>{inner}{ill}{deco}{bottom}</body></html>'

def render(spec_path, out_dir):
    raw = pathlib.Path(spec_path).read_text()
    for a, b2 in [(" :", "\u00a0:"), (" ?", "\u00a0?"), (" %", "\u00a0%"), (" ×", "\u00a0×"), ("× ", "×\u00a0"), ("es-tu", "es\u2011tu"), (" €", "\u00a0€")]:
        raw = raw.replace(a, b2)
    spec = json.loads(raw)
    out = pathlib.Path(out_dir).resolve(); out.mkdir(parents=True, exist_ok=True)
    n = len(spec["slides"])
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(spec["slides"], 1):
            f = out / f"slide-{i:02d}.html"
            f.write_text(page(s, i, n))
            pg.goto(f"file://{f}")
            pg.wait_for_timeout(250)
            pg.screenshot(path=str(out / f"slide-{i:02d}.png"))
            f.unlink()
        b.close()

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
