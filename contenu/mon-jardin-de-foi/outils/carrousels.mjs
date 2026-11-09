// Génère les slides des carrousels (1080x1350, JPG) — style premium éditorial
// Usage : node outils/carrousels.mjs semaines/2026-11-02 [id]
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { fleurLigne, MOTIFS } from './fleurs.mjs';

const ici = path.dirname(fileURLToPath(import.meta.url));
const dossier = path.resolve(process.argv[2]);
const data = JSON.parse(fs.readFileSync(path.join(dossier, 'contenu.json'), 'utf8'));
const css = fs.readFileSync(path.join(ici, 'brand.css'), 'utf8');
// FORMAT=story → stories 1080x1920 (clé « stories » du contenu.json)
const STORY = process.env.FORMAT === 'story';
const LISTE = STORY ? data.stories : data.carrousels;
const sortie = path.join(dossier, STORY ? 'stories' : 'carrousels');
fs.mkdirSync(sortie, { recursive: true });

const W = 1080, H = STORY ? 1920 : 1350;
const SOMBRES = new Set(['cover', 'arabic', 'offer']);

// Dans les visuels premium, pas d'emojis : on les retire (ils restent dans les légendes)
const sansEmoji = (t = '') => t.replace(/[\p{Extended_Pictographic}\u{1F1E6}-\u{1F1FF}\u{FE0F}\u{200D}]/gu, '').replace(/\s{2,}/g, ' ').replace(/^\s+|\s+$/g, '').replace(/^[\s·]+/, '')
  .replace(/ ([?!:;»])/g, '\u00a0$1').replace(/« /g, '«\u00a0').replace(/\s+\)/g, ')');
const puce = (c) => `<svg class="puce" viewBox="-26 -26 52 52">${fleurLigne({ r: 20, couleur: c, epaisseur: 3 })}</svg>`;

// Une fleur minimaliste différente par post, seulement sur certaines slides, toujours dans un coin (hors texte)
function fleurMini(i, k, c) {
  if ((i + k) % 3 !== 0) return '';
  const coin = (i + k) % 2 === 0 ? { x: W - 150, y: H - (STORY ? 330 : 205), r: -12 } : { x: 150, y: STORY ? 300 : 205, r: 14 };
  return `<g transform="translate(${coin.x} ${coin.y}) rotate(${coin.r}) scale(.9)" opacity=".75">${MOTIFS[k % MOTIFS.length](c)}</g>`;
}

function decor(i, sombre, k) {
  const trait = sombre ? '#e8a3b9' : '#a34d6b';
  const op = sombre ? 0.55 : 0.35;
  const cote = i % 2 === 0;
  return `<svg class="decor" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <defs>
      <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.15  0 0 0 0 0.25  0 0 0 .55 0"/></filter>
      <radialGradient id="lum" cx="${cote ? 22 : 78}%" cy="18%" r="75%">
        <stop offset="0" stop-color="${sombre ? '#a34d6b' : '#ffffff'}"/>
        <stop offset="1" stop-color="${sombre ? '#4e1f35' : '#f9e3ea'}"/>
      </radialGradient>
    </defs>
    <rect width="${W}" height="${H}" fill="url(#lum)"/>
    <rect width="${W}" height="${H}" filter="url(#grain)" opacity="${sombre ? 0.22 : 0.12}"/>
    <rect x="44" y="44" width="${W - 88}" height="${H - 88}" rx="6" fill="none" stroke="${trait}" stroke-width="1.6" opacity="${op + 0.15}"/>
    <rect x="56" y="56" width="${W - 112}" height="${H - 112}" rx="4" fill="none" stroke="${trait}" stroke-width=".8" opacity="${op}"/>
    ${fleurMini(i, k, trait)}
  </svg>`;
}

function contenu(s, sombre) {
  const c = sombre ? '#e8a3b9' : '#a34d6b';
  const kicker = s.kicker ? `<div class="kicker"><span></span>${sansEmoji(s.kicker)}<span></span></div>` : '';
  const sep = `<div class="sep"><span></span>${fleurLigne ? `<svg viewBox="-26 -26 52 52">${fleurLigne({ r: 18, couleur: c, epaisseur: 2.4 })}</svg>` : ''}<span></span></div>`;
  switch (s.type) {
    case 'cover':
      return `${kicker}<h1>${sansEmoji(s.title)}</h1>${sep}<p class="chapo">${sansEmoji(s.text)}</p>`;
    case 'arabic':
      return `<div class="arabe ar">${s.ar}</div>${sep}<p class="trad">${sansEmoji(s.text)}</p><p class="ref">${s.src}</p>`;
    case 'text':
      return `${kicker}<h2>${sansEmoji(s.title)}</h2>${sep}<p>${sansEmoji(s.text)}</p>`;
    case 'step':
      return `<div class="num">${s.num.padStart(2, '0')}</div><h2>${sansEmoji(s.title)}</h2>${sep}<p>${sansEmoji(s.text)}</p>`;
    case 'list':
      return `${kicker}<h2>${sansEmoji(s.title)}</h2>${sep}<ul>${s.items.map((t) => `<li>${puce(c)}<span>${sansEmoji(t)}</span></li>`).join('')}</ul>`;
    case 'check':
      return `<h2>${sansEmoji(s.title)}</h2>${sep}<ul class="check">${s.items.map((t) => `<li><span class="box"></span><span>${sansEmoji(t)}</span></li>`).join('')}</ul>`;
    case 'offer':
      return `<div class="kicker"><span></span>${sansEmoji(s.title)}<span></span></div><div class="ancien">${s.old}</div><div class="nouveau">${s.price}</div>${sep}<p class="chapo">${sansEmoji(s.text)}</p><div class="bouton">${sansEmoji(s.cta)}</div>`;
    case 'cta':
      return `<h2>${sansEmoji(s.title)}</h2>${sep}<p>${sansEmoji(s.text)}</p><div class="bouton">${sansEmoji(s.cta)}</div>`;
  }
  throw new Error('type inconnu ' + s.type);
}

function page(s, i, n, k) {
  const sombre = SOMBRES.has(s.type) || !!s.photo;
  const photo = s.photo ? `<img class="photo" src="data:image/jpeg;base64,${fs.readFileSync(path.join(dossier, s.photo)).toString('base64')}"><div class="voile"></div><div class="cadre-ph"></div>` : '';
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}
  body { width:${W}px; height:${H}px; overflow:hidden; position:relative; }
  .decor { position:absolute; inset:0; }
  .theme { position:absolute; inset:0; --t:${sombre ? '#fdf1f4' : '#86385a'}; --x:${sombre ? '#fbe7ee' : '#5c2740'}; --a:${sombre ? '#e8a3b9' : '#a34d6b'}; }
  .entete { position:absolute; top:${STORY ? 230 : 100}px; left:0; right:0; text-align:center; font-weight:600; letter-spacing:.42em; text-transform:uppercase; font-size:19px; color:var(--a); }
  .photo { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:50% 25%; }
  .cadre-ph { position:absolute; inset:44px; border:1.6px solid rgba(232,163,185,.7); border-radius:6px; }
  .cadre-ph::after { content:''; position:absolute; inset:10px; border:.8px solid rgba(232,163,185,.5); border-radius:4px; }
  .voile { position:absolute; inset:0; background:linear-gradient(180deg, rgba(63,26,44,.05) 0%, rgba(63,26,44,.15) 35%, rgba(63,26,44,.82) 62%, rgba(63,26,44,.94) 100%); }
  .zone { position:absolute; top:${s.photo ? Math.round(H * 0.5) : (STORY ? 330 : 235)}px; bottom:${STORY ? (s.sticker ? 860 : 420) : 275}px; left:130px; right:130px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; color:var(--x); }
  .kicker { display:flex; align-items:center; gap:22px; font-weight:600; font-size:22px; letter-spacing:.34em; text-transform:uppercase; color:var(--a); margin-bottom:46px; }
  .kicker span { width:60px; height:1.5px; background:var(--a); opacity:.7; }
  h1 { font-family:var(--titre); font-weight:600; color:var(--t); font-size:124px; line-height:1.04; letter-spacing:-.005em; }
  h2 { font-family:var(--titre); font-weight:600; color:var(--t); font-size:92px; line-height:1.08; }
  .sep { display:flex; align-items:center; gap:18px; margin:46px auto; }
  .sep span { width:110px; height:1.5px; background:var(--a); opacity:.6; }
  .sep svg { width:40px; height:40px; }
  p { font-size:42px; line-height:1.55; font-weight:400; }
  p b, li b { color:var(--a); font-weight:700; }
  .chapo { font-size:40px; letter-spacing:.01em; font-weight:500; opacity:.95; }
  .arabe { font-size:92px; line-height:1.75; color:var(--t); }
  .trad { font-size:46px; line-height:1.5; font-weight:500; font-style:italic; }
  .ref, .src { display:block; margin-top:30px; font-size:22px; letter-spacing:.24em; text-transform:uppercase; font-weight:600; color:var(--a); font-style:normal; }
  .num { font-family:var(--titre); font-size:120px; line-height:1; color:var(--a); opacity:.9; margin-bottom:18px; }
  ul { list-style:none; text-align:left; display:flex; flex-direction:column; gap:30px; }
  li { display:flex; align-items:center; gap:28px; font-size:42px; line-height:1.35; font-weight:500; }
  .puce { width:44px; height:44px; flex:none; }
  .check li { gap:30px; }
  .box { width:44px; height:44px; flex:none; border:2.5px solid var(--a); border-radius:50%; }
  .ancien { font-size:52px; color:var(--a); text-decoration:line-through; text-decoration-thickness:2px; font-weight:500; letter-spacing:.06em; }
  .nouveau { font-family:var(--titre); font-size:230px; font-weight:600; color:var(--t); line-height:1.05; }
  .bouton { margin-top:56px; color:var(--a); font-weight:600; font-size:26px; letter-spacing:.3em; text-transform:uppercase; padding:26px 54px; border:1.6px solid var(--a); border-radius:80px; }
  .pied { position:absolute; bottom:${STORY ? 250 : 100}px; left:130px; right:130px; display:flex; justify-content:space-between; align-items:center; font-size:19px; letter-spacing:.32em; text-transform:uppercase; font-weight:600; color:var(--a); }
  .pied .compte { font-family:var(--texte); letter-spacing:.2em; text-transform:none; }
  </style></head><body>
  ${decor(i, sombre, k)}
  ${photo}
  <div class="theme">
    <div class="entete">Mon Jardin de Foi</div>
    <div class="zone">${contenu(s, sombre)}</div>
    ${STORY ? '<div class="pied" style="justify-content:center"><span class="compte">@mon.jardin.de.foi</span></div>' : `<div class="pied"><span>${String(i + 1).padStart(2, '0')} / ${String(n).padStart(2, '0')}</span><span class="compte">@mon.jardin.de.foi</span><span>${i < n - 1 ? 'Glisse →' : 'Enregistre ♡'}</span></div>`}
  </div>
  </body></html>`;
}

const browser = await chromium.launch();
const pg = await browser.newPage({ viewport: { width: W, height: H } });
const seule = process.argv[3];
for (const c of LISTE) {
  if (seule && c.id !== seule) continue;
  const n = c.slides.length;
  for (let i = 0; i < n; i++) {
    await pg.setContent(page(c.slides[i], i, n, LISTE.indexOf(c) + (STORY ? 3 : 0)), { waitUntil: 'load' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.evaluate((k0) => {
      const z = document.querySelector('.zone');
      let k = k0;
      for (const el of z.children) el.style.zoom = k;
      while (z.scrollHeight > z.clientHeight + 2 && k > 0.6) { k -= 0.04; for (const el of z.children) el.style.zoom = k; }
    }, STORY ? 1.2 : 1);
    await pg.screenshot({ path: path.join(sortie, `${c.id}-${String(i + 1).padStart(2, '0')}.jpg`), type: 'jpeg', quality: 93 });
  }
  console.log('✔', c.id, n, 'slides');
}
await browser.close();
