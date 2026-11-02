// Génère les reels animés (1080x1920, 30 i/s, MP4 H.264 + AAC) avec bruitages nature.
// Usage : node outils/reels.mjs semaines/2026-11-02 [id]
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { SCENES } from './scenes.mjs';

const ici = path.dirname(fileURLToPath(import.meta.url));
const dossier = path.resolve(process.argv[2]);
const data = JSON.parse(fs.readFileSync(path.join(dossier, 'contenu.json'), 'utf8'));
const css = fs.readFileSync(path.join(ici, 'brand.css'), 'utf8');
const sortie = path.join(dossier, 'reels');
fs.mkdirSync(sortie, { recursive: true });
const FPS = 30;

const THEMES = {
  clair: { bg: 'radial-gradient(120% 80% at 30% 15%, #ffffff 0%, #fbeef2 45%, #f4d6e0 100%)', t: '#86385a', x: '#5c2740', a: '#a34d6b', p: '#e8a3b9' },
  sombre: { bg: 'radial-gradient(120% 80% at 30% 12%, #a34d6b 0%, #6e2b49 45%, #3f1a2c 100%)', t: '#fdf1f4', x: '#fbe7ee', a: '#e8a3b9', p: '#e8a3b9' },
  aube: { bg: 'linear-gradient(180deg, #fde9e0 0%, #f8d3d8 40%, #eeb0c2 75%, #c97994 100%)', t: '#86385a', x: '#5c2740', a: '#a34d6b', p: '#ffffff' },
  nuit: { bg: 'linear-gradient(180deg, #23101d 0%, #3a1830 50%, #5c2740 100%)', t: '#fdf1f4', x: '#fbe7ee', a: '#e8a3b9', p: '#ffffff' },
};

function page(sc) {
  const th = THEMES[sc.fond];
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}
  html,body { width:540px; height:960px; overflow:hidden; background:${th.bg}; }
  :root { --t:${th.t}; --x:${th.x}; --a:${th.a}; --p:${th.p}; }
  #fx { position:absolute; inset:0; width:540px; height:960px; }
  #grain { position:absolute; inset:0; opacity:${sc.fond === 'clair' || sc.fond === 'aube' ? 0.10 : 0.2}; }
  .cadre-ext { position:absolute; inset:18px; border:1px solid var(--a); opacity:.35; border-radius:3px; }
  .scene { position:absolute; inset:0; color:var(--x); text-align:center; }
  [data-a] { opacity:0; will-change:opacity, transform; }
  svg [data-a] { opacity:1; }
  .tr, .trf { fill:none; stroke:var(--a); stroke-width:1.6px; vector-effect:non-scaling-stroke; stroke-linecap:round; stroke-linejoin:round; }
  .coeur { fill:var(--a); }
  .pf { fill:var(--p); opacity:.85; }
  .centre > .bloc, .haut { position:absolute; left:46px; right:46px; }
  .centre > .bloc { top:0; bottom:0; display:flex; flex-direction:column; justify-content:center; align-items:center; }
  .haut { top:165px; }
  h1 { font-family:var(--titre); font-weight:600; color:var(--t); font-size:50px; line-height:1.08; }
  h2 { font-family:var(--titre); font-weight:600; color:var(--t); font-size:44px; line-height:1.1; }
  .kicker, .kicker2 { display:flex; align-items:center; justify-content:center; gap:12px; font-size:11px; font-weight:600; letter-spacing:.36em; text-transform:uppercase; color:var(--a); margin-bottom:18px; }
  .kicker span { width:34px; height:1px; background:var(--a); }
  .sep { display:flex; align-items:center; justify-content:center; gap:10px; margin:24px auto; }
  .sep span { width:56px; height:1px; background:var(--a); opacity:.7; }
  .sep svg { width:22px; height:22px; }
  .arabe { font-size:40px; line-height:1.85; color:var(--t); }
  .trad { font-size:21px; line-height:1.55; font-style:italic; font-weight:500; max-width:430px; }
  .ref { margin-top:16px; font-size:11px; letter-spacing:.28em; text-transform:uppercase; font-weight:600; color:var(--a); }
  .petit { margin-top:26px; font-size:19px; line-height:1.55; font-weight:500; }
  .jardin { position:absolute; top:410px; left:30px; right:30px; display:flex; justify-content:space-between; }
  .pl { position:relative; width:92px; height:290px; }
  .pl svg { position:absolute; left:0; top:0; width:92px; height:196px; }
  .pl .lbl { position:absolute; bottom:56px; left:0; right:0; font-size:11px; letter-spacing:.24em; text-transform:uppercase; font-weight:700; color:var(--a); }
  .sous { position:absolute; top:715px; left:46px; right:46px; font-size:19px; font-weight:500; }
  .pousse { position:absolute; left:170px; top:560px; width:200px; height:225px; }
  .graines { display:flex; flex-direction:column; gap:16px; align-items:flex-start; }
  .gr { display:flex; align-items:center; gap:16px; font-size:21px; font-weight:600; text-align:left; }
  .gr svg { width:52px; height:60px; flex:none; }
  .arche { position:absolute; left:50px; top:110px; width:440px; height:690px; opacity:.6; }
  .liste { display:flex; flex-direction:column; gap:16px; align-items:flex-start; }
  .li { display:flex; align-items:center; gap:16px; font-size:21px; font-weight:600; }
  .li svg { width:34px; height:34px; flex:none; }
  .rond { fill:none; stroke:var(--a); stroke-width:1.4px; vector-effect:non-scaling-stroke; }
  .ck { stroke-width:2.6px; }
  .lune { position:absolute; right:56px; top:96px; width:110px; height:110px; }
  .tel .cadre { width:236px; height:413px; }
  .tel .ecran { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:200px; display:flex; flex-direction:column; gap:14px; text-align:left; }
  .it { display:flex; align-items:center; gap:10px; font-size:15px; font-weight:600; padding-bottom:10px; border-bottom:1px solid rgba(232,163,185,.35); }
  .it svg { width:18px; height:18px; flex:none; }
  .prix .ancien { position:relative; display:inline-block; font-size:28px; color:var(--a); font-weight:500; letter-spacing:.06em; }
  .prix .ancien i { position:absolute; left:-4px; top:52%; height:1.5px; background:var(--a); width:0; }
  .prix .nouveau { font-family:var(--titre); font-size:120px; font-weight:600; color:var(--t); line-height:1.1; }
  .final { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
  .logo { width:96px; height:96px; }
  .nom { margin-top:8px; font-family:var(--titre); font-size:52px; color:var(--t); font-weight:600; }
  .cta { margin-top:26px; font-size:12px; letter-spacing:.34em; text-transform:uppercase; font-weight:600; color:var(--a); border:1px solid var(--a); border-radius:40px; padding:13px 30px; }
  .compte { position:absolute; bottom:44px; left:0; right:0; font-size:11px; letter-spacing:.22em; font-weight:600; color:var(--a); opacity:.85; }
  </style></head><body>
  <canvas id="fx" width="1080" height="1920"></canvas>
  <svg id="grain" width="540" height="960"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .35  0 0 0 0 .15  0 0 0 0 .25  0 0 0 .6 0"/></filter><rect width="540" height="960" filter="url(#g)"/></svg>
  <div class="cadre-ext"></div>
  <div class="scene">${sc.html}<div class="compte">@mon.jardin.de.foi</div></div>
  <script>
  const PART = ${JSON.stringify(sc.particules)}, COUL = ${JSON.stringify(th.p)};
  const cl = (v) => Math.max(0, Math.min(1, v));
  const ease = (p) => 1 - Math.pow(1 - p, 3);
  let s = 12345; const R = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const P = Array.from({ length: PART === 'pluie' ? 170 : PART === 'etoiles' ? 140 : PART === 'lumiere' ? 26 : 22 }, () => ({ x: R(), y: R(), v: R(), r: R(), k: R() }));
  const ctx = document.getElementById('fx').getContext('2d');
  function fx(t) {
    ctx.clearRect(0, 0, 1080, 1920);
    for (const p of P) {
      if (PART === 'pluie') {
        const y = ((p.y * 2100 + t * (900 + p.v * 700)) % 2100) - 100, x = p.x * 1080 - y * 0.06;
        ctx.strokeStyle = 'rgba(253,241,244,' + (0.10 + p.k * 0.18) + ')'; ctx.lineWidth = 1.2 + p.r * 1.2;
        ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 4, y + 34 + p.v * 30); ctx.stroke();
      } else if (PART === 'etoiles') {
        const a = 0.25 + 0.75 * Math.abs(Math.sin(t * (0.6 + p.v * 1.4) + p.k * 6.28));
        ctx.fillStyle = 'rgba(255,240,246,' + a * (0.35 + p.r * 0.5) + ')';
        ctx.beginPath(); ctx.arc(p.x * 1080, p.y * 1300, 1 + p.r * 2.4, 0, 6.29); ctx.fill();
      } else if (PART === 'lumiere') {
        const y = 1920 - ((p.y * 2200 + t * (18 + p.v * 30)) % 2200), x = p.x * 1080 + Math.sin(t * 0.4 + p.k * 6) * 30;
        const rad = 30 + p.r * 90, g = ctx.createRadialGradient(x, y, 0, x, y, rad);
        g.addColorStop(0, 'rgba(255,236,224,' + (0.10 + p.k * 0.14) + ')'); g.addColorStop(1, 'rgba(255,236,224,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, rad, 0, 6.29); ctx.fill();
      } else {
        const y = ((p.y * 2200 + t * (40 + p.v * 60)) % 2200) - 140, x = p.x * 1080 + Math.sin(t * (0.5 + p.v) + p.k * 6) * 60;
        const sz = 9 + p.r * 12;
        ctx.save(); ctx.translate(x, y); ctx.rotate(t * (0.3 + p.v * 0.6) + p.k * 6); ctx.globalAlpha = 0.22 + p.k * 0.3;
        ctx.fillStyle = COUL; ctx.beginPath(); ctx.moveTo(0, -sz);
        ctx.bezierCurveTo(sz * 0.8, -sz * 0.6, sz * 0.7, sz * 0.6, 0, sz); ctx.bezierCurveTo(-sz * 0.7, sz * 0.6, -sz * 0.8, -sz * 0.6, 0, -sz); ctx.fill(); ctx.restore();
      }
    }
  }
  const E = [...document.querySelectorAll('[data-a]')];
  for (const el of E) {
    if (el.dataset.a === 'draw') {
      el._p = el.tagName === 'path' ? [el] : [...el.querySelectorAll('.tr')];
      el._p.forEach((p) => { p.style.strokeDasharray = '1 1'; p.style.strokeDashoffset = 1; });
      el._c = [...el.querySelectorAll('.coeur')];
    }
  }
  window.setT = (t) => {
    fx(t);
    for (const el of E) {
      const t0 = +el.dataset.t0, d = +(el.dataset.d || (el.dataset.a === 'draw' ? 1.6 : 0.9));
      const t1 = el.dataset.t1 ? +el.dataset.t1 : 1e9;
      const p = ease(cl((t - t0) / d)), o = ease(cl((t - t1) / 0.55)), vis = p * (1 - o);
      const a = el.dataset.a;
      if (a === 'draw') {
        el._p.forEach((q) => (q.style.strokeDashoffset = 1 - p));
        el._c.forEach((c) => (c.style.opacity = cl((t - t0 - d * 0.8) / 0.3)));
        el.style.opacity = t < t0 ? 0 : 1 - o;
      } else if (a === 'rise') { el.style.opacity = vis; el.style.transform = 'translateY(' + ((1 - p) * 26 - o * 16) + 'px)'; }
      else if (a === 'fade') { el.style.opacity = vis; }
      else if (a === 'pop' || a === 'bloom') {
        el.style.opacity = vis; const sc = 0.6 + 0.4 * p + (a === 'bloom' ? 0.08 * Math.sin(p * 3.14) : 0);
        el.style.transform = 'scale(' + sc + ')'; el.style.transformOrigin = a === 'bloom' ? '50% 22%' : '50% 50%';
      } else if (a === 'strike') { el.style.opacity = 1; el.querySelector('i').style.width = 'calc(' + (p * 100) + '% + 8px)'; }
    }
  };
  </script></body></html>`;
}

const browser = await chromium.launch();
const pg = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
const seule = process.argv[3];
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || '/tmp', 'reels-'));
for (const r of data.reels) {
  if (seule && r.id !== seule) continue;
  const sc = SCENES[r.scene];
  await pg.setContent(page(sc), { waitUntil: 'load' });
  await pg.evaluate(() => document.fonts.ready);
  const evts = path.join(tmp, r.id + '.json'), wav = path.join(tmp, r.id + '.wav');
  fs.writeFileSync(evts, JSON.stringify(sc.sons));
  const a = spawnSync('python3', [path.join(ici, 'sons.py'), sc.ambiance, String(sc.duree), evts, wav], { stdio: 'inherit' });
  if (a.status) throw new Error('audio');
  const out = path.join(sortie, `${r.id}.mp4`);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', wav,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(FPS),
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const fini = new Promise((ok, ko) => ff.on('close', (c) => (c ? ko(new Error('ffmpeg ' + c)) : ok())));
  const N = Math.round(sc.duree * FPS);
  for (let f = 0; f < N; f++) {
    await pg.evaluate((t) => window.setT(t), f / FPS);
    const buf = await pg.screenshot({ type: 'jpeg', quality: 90 });
    if (!ff.stdin.write(buf)) await new Promise((ok) => ff.stdin.once('drain', ok));
  }
  ff.stdin.end();
  await fini;
  // Couverture (image de la fin du titre) pour la grille Instagram
  await pg.evaluate((t) => window.setT(t), 2.6);
  await pg.screenshot({ path: path.join(sortie, `${r.id}-cover.jpg`), type: 'jpeg', quality: 92 });
  console.log('✔', r.id, sc.duree + 's');
}
await browser.close();
