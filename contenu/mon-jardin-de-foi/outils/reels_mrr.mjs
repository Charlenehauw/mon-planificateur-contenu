// Monte les reels « femme voilée » à partir des clips MRR : 2 clips enchaînés (fondu), textes en surimpression,
// ambiance/bruitages, et anasheed si un fichier semaines/<date>/anasheed/<id>.(mp3|wav|m4a) existe.
// Usage : node outils/reels_mrr.mjs semaines/2026-11-09 <dossier des clips> [id]
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ici = path.dirname(fileURLToPath(import.meta.url));
const dossier = path.resolve(process.argv[2]);
const clips = path.resolve(process.argv[3]);
const seule = process.argv[4];
const data = JSON.parse(fs.readFileSync(path.join(dossier, 'contenu.json'), 'utf8'));
const css = fs.readFileSync(path.join(ici, 'brand.css'), 'utf8');
const sortie = path.join(dossier, 'reels');
fs.mkdirSync(sortie, { recursive: true });
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || '/tmp', 'mrr-'));
const AMB = { pages: 'brise', mer: 'mer', brise: 'brise', aube: 'aube', jardin: 'jardin', nuit: 'nuit', pluie: 'pluie' };
const run = (cmd, args) => { const r = spawnSync(cmd, args, { stdio: ['ignore', 'inherit', 'inherit'] }); if (r.status) throw new Error(cmd + ' ' + args.join(' ')); };
const duree = (f) => parseFloat(spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).stdout.toString());

function calque([brut, , , style]) {
  const texte = brut.replace(/ ([?!:;»])/g, '\u00a0$1').replace(/« /g, '«\u00a0');
  const ref = style === 'ref';
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}
  html,body{background:transparent;width:540px;height:960px;margin:0}
  .z{position:absolute;left:40px;right:40px;${ref ? 'top:640px' : 'top:470px'};display:flex;justify-content:center;text-align:center}
  .t{font-family:var(--titre);font-weight:600;color:#fff;font-size:${texte.length > 60 ? 30 : 40}px;line-height:1.2;
     text-shadow:0 2px 18px rgba(63,26,44,.85),0 0 4px rgba(63,26,44,.6);padding:18px 22px;border-radius:22px;
     background:rgba(63,26,44,.28);backdrop-filter:blur(2px)}
  .r{font-family:var(--texte);font-size:12px;letter-spacing:.3em;text-transform:uppercase;font-weight:700;color:#fbe7ee;text-shadow:0 1px 8px rgba(0,0,0,.6)}
  </style></head><body><div class="z">${ref ? `<div class="r">${texte}</div>` : `<div class="t">${texte}</div>`}</div></body></html>`;
}
const signature = `<!doctype html><html><head><meta charset="utf-8"><style>${css}html,body{background:transparent;width:540px;height:960px;margin:0}
  .s{position:absolute;bottom:150px;left:0;right:0;text-align:center;font-family:var(--titre);font-size:26px;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.6)}
  .c{position:absolute;bottom:128px;left:0;right:0;text-align:center;font-size:10px;letter-spacing:.25em;color:#fbe7ee;font-weight:700;text-shadow:0 1px 6px rgba(0,0,0,.6)}</style></head>
  <body><div class="s">Mon Jardin de Foi</div><div class="c">@MON.JARDIN.DE.FOI</div></body></html>`;

const browser = await chromium.launch();
const pg = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
const png = async (html, f) => { await pg.setContent(html); await pg.evaluate(() => document.fonts.ready); await pg.screenshot({ path: f, omitBackground: true }); };

for (const r of data.reels_mrr) {
  if (seule && r.id !== seule) continue;
  const [a, b] = r.clips.map((c) => path.join(clips, c + '.mp4'));
  const da = Math.min(duree(a), 6), db = Math.min(duree(b), 6), X = 0.7, D = +(da + db - X).toFixed(2);
  // 1) fond vidéo : 2 clips recadrés 1080x1920, fondu enchaîné, léger zoom, ton chaud
  const fond = path.join(tmp, r.id + '-fond.mp4');
  const prep = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1';
  run('ffmpeg', ['-nostdin', '-loglevel', 'error', '-y', '-i', a, '-i', b, '-filter_complex',
    `[0:v]trim=0:${da},setpts=PTS-STARTPTS,${prep}[x];[1:v]trim=0:${db},setpts=PTS-STARTPTS,${prep}[y];[x][y]xfade=transition=fade:duration=${X}:offset=${(da - X).toFixed(2)},` +
    `zoompan=z='min(1+0.0006*on,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,eq=saturation=1.05,format=yuv420p[v]`,
    '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', fond]);
  // 2) calques texte
  const calques = [];
  for (const [k, t] of r.textes.entries()) { const f = path.join(tmp, `${r.id}-t${k}.png`); await png(calque(t), f); calques.push([f, t[1], Math.min(t[2], D - 0.3)]); }
  const sig = path.join(tmp, r.id + '-sig.png'); await png(signature, sig);
  // 3) audio : ambiance + anasheed éventuel
  const evts = path.join(tmp, r.id + '.json'); fs.writeFileSync(evts, JSON.stringify([{ t: 0.4, type: 'carillon2' }, { t: r.textes[1][1], type: 'carillon' }]));
  const amb = path.join(tmp, r.id + '.wav');
  run('python3', [path.join(ici, 'sons.py'), AMB[r.ambiance] || 'brise', String(D), evts, amb]);
  const nasheed = ['mp3', 'wav', 'm4a'].map((e) => path.join(dossier, 'anasheed', `${r.id}.${e}`)).find((f) => fs.existsSync(f));
  // 4) assemblage
  const ins = ['-i', fond, ...calques.flatMap(([f, , t1]) => ['-loop', '1', '-t', String(t1 + 0.5), '-i', f]), '-loop', '1', '-t', String(D), '-i', sig, '-i', amb];
  if (nasheed) ins.push('-i', nasheed);
  let fc = '', cur = '0:v';
  calques.forEach(([, t0, t1], k) => {
    fc += `[${k + 1}:v]format=rgba,scale=1080:1920,fade=in:st=${t0}:d=0.6:alpha=1,fade=out:st=${(t1 - 0.5).toFixed(2)}:d=0.5:alpha=1[c${k}];`;
    fc += `[${cur}][c${k}]overlay=0:0:enable='between(t,${t0},${t1})'[o${k}];`; cur = `o${k}`;
  });
  const si = calques.length + 1, ai = si + 1;
  fc += `[${si}:v]format=rgba,scale=1080:1920,fade=in:st=${(D - 2.2).toFixed(2)}:d=0.6:alpha=1[sg];[${cur}][sg]overlay=0:0:enable='gte(t,${(D - 2.2).toFixed(2)})'[vf];`;
  fc += nasheed
    ? `[${ai}:a]volume=0.45[am];[${ai + 1}:a]atrim=0:${D},afade=t=out:st=${(D - 1.2).toFixed(2)}:d=1.2[an];[an][am]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[af]`
    : `[${ai}:a]loudnorm=I=-16:TP=-1.5:LRA=11[af]`;
  const out = path.join(sortie, `${r.id}.mp4`);
  run('ffmpeg', ['-nostdin', '-loglevel', 'error', '-y', ...ins, '-filter_complex', fc, '-map', '[vf]', '-map', '[af]', '-t', String(D),
    '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-ar', '44100', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out]);
  run('ffmpeg', ['-nostdin', '-loglevel', 'error', '-y', '-ss', '2.5', '-i', out, '-frames:v', '1', '-q:v', '3', path.join(sortie, `${r.id}-cover.jpg`)]);
  console.log('✔', r.id, D + 's', nasheed ? 'avec anasheed' : 'bruitages seuls');
}
await browser.close();
