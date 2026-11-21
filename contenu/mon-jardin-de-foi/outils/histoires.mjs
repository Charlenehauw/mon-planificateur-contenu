// Reels « histoire » (10 à 30 s) : une vraie petite histoire en plans enchaînés — écran verrouillé + notification,
// conversation SMS qui s'écrit, carte qui se retourne, verset récité (Coran, sans bruitage par-dessus), textes animés, fin.
// Usage : node outils/histoires.mjs semaines/<date> <id>      (UN reel par exécution)
// Récitations : everyayah.com (Mishary Alafasy, verset par verset), mises en cache dans semaines/<date>/coran/
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ici = path.dirname(fileURLToPath(import.meta.url));
const dossier = path.resolve(process.argv[2]);
const seule = process.argv[3];
const data = JSON.parse(fs.readFileSync(path.join(dossier, 'contenu.json'), 'utf8'));
const css = fs.readFileSync(path.join(ici, 'brand.css'), 'utf8');
const sortie = path.join(dossier, 'reels');
fs.mkdirSync(sortie, { recursive: true });
const FPS = 30, TR = 0.4;
const RECITATEUR = 'Alafasy_128kbps';
const duree = (f) => parseFloat(spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).stdout.toString());
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/ ([?!:;»])/g, ' $1').replace(/« /g, '« ');

function recitation(sourate, aya) {
  const nom = String(sourate).padStart(3, '0') + String(aya).padStart(3, '0');
  const dir = path.join(dossier, 'coran'); fs.mkdirSync(dir, { recursive: true });
  const f = path.join(dir, nom + '.mp3');
  if (!fs.existsSync(f)) {
    const r = spawnSync('curl', ['-sf', '-o', f, `https://everyayah.com/data/${RECITATEUR}/${nom}.mp3`]);
    if (r.status) throw new Error('Récitation introuvable ' + nom);
  }
  return f;
}

// ——— Compilation : chaque plan devient du HTML + des événements (bruitages, récitations) aux temps absolus ———
function compiler(h) {
  let T = 0; const plans = [], sons = [], coran = [];
  const A = (t0, a, d, t1) => `data-a="${a}" data-t0="${t0.toFixed(2)}"${d ? ` data-d="${d}"` : ''}${t1 ? ` data-t1="${t1.toFixed(2)}"` : ''}`;
  h.plans.forEach((p, i) => {
    let d = p.d || 3, html = '';
    const t = (x) => T + x;
    if (p.type === 'notif') {
      d = p.d || 3;
      html = `${p.pov ? `<div class="pov" ${A(t(0.1), 'rise')}>${esc(p.pov)}</div>` : ''}
        <div class="lock"><div class="heure" ${A(t(0), 'fade', 0.6)}>${p.heure}</div><div class="jour" ${A(t(0.1), 'fade', 0.6)}>${esc(p.jour || '')}</div>
        <div class="notif" ${A(t(0.7), 'drop', 0.5)}><div class="ic"><svg viewBox="-26 -26 52 52"><g>${fl(16)}</g></svg></div>
        <div><div class="de">${esc(p.de)} <span>maintenant</span></div><div class="msg">${esc(p.texte)}</div></div></div></div>`;
      sons.push({ t: t(0.7), type: 'vibre' }, { t: t(0.75), type: 'ding' });
    } else if (p.type === 'sms') {
      let x = 0.5, bulles = '';
      const saisie = [];
      for (const [qui, txt] of p.msgs) {
        if (qui === 'moi') {
          const dt = Math.min(1.1, 0.25 + txt.length * 0.022);
          saisie.push(`<div class="saisie" ${A(t(x), 'type', dt, t(x + dt + 0.05))} data-txt="${esc(txt)}"></div>`);
          for (let k = 0; k < dt - 0.1; k += 0.085) sons.push({ t: t(x + k), type: 'touche' });
          x += dt + 0.1;
          bulles += `<div class="b moi" ${A(t(x), 'bulle', 0.35)}>${esc(txt)}</div>`;
          sons.push({ t: t(x), type: 'envoi' });
          x += 0.55 + txt.length * 0.012;
        } else {
          bulles += `<div class="dots" ${A(t(x), 'fade', 0.2, t(x + 0.85))}><i></i><i></i><i></i></div>`;
          x += 0.9;
          bulles += `<div class="b elle" ${A(t(x), 'bulle', 0.35)}>${esc(txt)}</div>`;
          sons.push({ t: t(x), type: 'ding' });
          x += 0.55 + txt.length * 0.015;
        }
      }
      d = p.d || x + 0.9;
      html = `<div class="tel"><div class="haut"><div class="av"><svg viewBox="-26 -26 52 52"><g>${fl(15)}</g></svg></div>
        <div><div class="nom">${esc(p.contact)}</div><div class="etat">en ligne</div></div></div>
        <div class="fil"><div class="chip">Aujourd'hui ${esc(p.heure || '')}</div>${bulles}</div>
        <div class="bas"><div class="champ">${saisie.join('')}<span class="ph">Message</span></div><div class="env">➤</div></div></div>`;
    } else if (p.type === 'carte') {
      d = p.d || 2.4;
      html = `${p.dessus ? `<div class="pov" ${A(t(0.05), 'rise')}>${esc(p.dessus)}</div>` : ''}
        <div class="carte" ${A(t(0.35), 'flip', 0.8)}><div class="face dos"><svg viewBox="-26 -26 52 52"><g>${fl(18)}</g></svg></div>
        <div class="face avant"><div class="k">${esc(p.kicker)}</div><svg class="fl" viewBox="-26 -26 52 52"><g>${fl(16)}</g></svg>
        <div class="ti">${esc(p.titre)}</div><div class="st">${esc(p.sous || '')}</div></div></div>`;
      sons.push({ t: t(0.35), type: 'flip' }, { t: t(0.9), type: 'carillon2' });
    } else if (p.type === 'verset') {
      let x = 0.7, blocs = '';
      const debut = t(0.2);
      p.ayat.forEach((a, k) => {
        const f = recitation(p.sourate, a.n), dd = duree(f);
        coran.push({ t: t(x), f });
        const fin = k < p.ayat.length - 1 ? t(x + dd + 0.15) : null;
        const mots = a.ar.split(' ');
        blocs += `<div class="aya" ${A(t(x), 'fade', 0.4, fin)}><div class="ar">${mots.map((m, j) => `<span ${A(t(x + (dd * 0.8) * j / mots.length), 'mot', 0.45)}>${m}</span>`).join(' ')}</div>
          <div class="fr" ${A(t(x + 0.6), 'rise')}>${esc(a.fr)}</div></div>`;
        x += dd + 0.25;
      });
      d = x + (p.fin || 0.8);
      sons.push({ t: debut, type: 'silence', d: d - 0.2 });
      html = `<div class="verset"><div class="k" ${A(t(0.1), 'fade')}>${esc(p.kicker || 'Écoute')}</div><div class="onde" ${A(t(0.3), 'fade')} data-onde="${t(0.7).toFixed(2)},${t(x).toFixed(2)}">${'<i></i>'.repeat(23)}</div>${blocs}
        <div class="ref" ${A(t(0.5), 'fade')}>${esc(p.ref)}</div>
        ${p.note ? `<div class="note" ${A(t(d - 3.2), 'rise')}>${esc(p.note)}</div>` : ''}
        <div class="rec" ${A(t(0.4), 'fade')}>Récitation : Mishary Alafasy</div></div>`;
    } else if (p.type === 'texte') {
      let x = 0.3, l = '';
      for (const ligne of p.lignes) { l += `<div class="ln" ${A(t(x), 'pop', 0.5)}>${esc(ligne).replace(/\*(.+?)\*/g, '<b>$1</b>')}</div>`; sons.push({ t: t(x), type: 'pop' }); x += p.pas || 0.9; }
      d = p.d || x + 1.4;
      html = `<div class="textes">${l}</div>`;
    } else if (p.type === 'liste') {
      let x = 0.6, l = '';
      for (const it of p.items) {
        l += `<div class="li" ${A(t(x), 'rise')}><svg viewBox="-24 -24 48 48"><circle r="20" class="rond"/><path class="ck" pathLength="1" d="M-9 1 L-2 8 L11 -8" ${A(t(x + 0.45), 'trait', 0.4)}/></svg><span>${esc(it)}</span></div>`;
        sons.push({ t: t(x + 0.5), type: 'tick' }); x += 0.9;
      }
      d = p.d || x + 1.2;
      html = `<div class="liste"><div class="ti" ${A(t(0.1), 'rise')}>${esc(p.titre)}</div>${l}</div>`;
    } else if (p.type === 'fin') {
      d = p.d || 3;
      html = `<div class="fin"><svg class="logo" viewBox="-60 -70 120 120" ${A(t(0.1), 'dessin', 1.2)}><g>${fl(42, 'tr')}</g></svg>
        <div class="ti" ${A(t(0.4), 'rise')}>${esc(p.titre)}</div>
        ${p.cta ? `<div class="cta" ${A(t(1.0), 'pop')}>${esc(p.cta)}</div>` : ''}
        <div class="sig" ${A(t(1.2), 'fade')}>@mon.jardin.de.foi</div></div>`;
      sons.push({ t: t(0.3), type: 'carillon' });
    } else throw new Error('Plan inconnu ' + p.type);
    if (i > 0) sons.push({ t: T, type: 'whoosh' });
    plans.push(`<section class="plan p-${p.type}" data-p0="${T.toFixed(2)}" data-p1="${(T + d).toFixed(2)}" data-tr="${p.transition || (i % 2 ? 'glisse' : 'monte')}">${html}</section>`);
    T += d - TR;
  });
  const D = +(T + TR).toFixed(2);
  return { html: plans.join(''), sons: sons.filter((s) => s.t < D - 0.3), coran, D };
}

function fl(r, cls = 'trf') {
  let s = '';
  for (let i = 0; i < 5; i++) s += `<path class="${cls}" pathLength="1" d="M0 0 C ${r * .5} ${-r * .35} ${r * .45} ${-r} 0 ${-r * 1.05} C ${-r * .45} ${-r} ${-r * .5} ${-r * .35} 0 0Z" transform="rotate(${i * 72})"/>`;
  return s + `<circle class="coeur" r="${r * .14}"/>`;
}

const FONDS = {
  nuit: 'linear-gradient(180deg,#1f0e1a 0%,#3a1830 55%,#5c2740 100%)',
  rose: 'radial-gradient(120% 80% at 30% 15%,#ffffff 0%,#fbeef2 45%,#f4d6e0 100%)',
  mauve: 'radial-gradient(120% 80% at 30% 12%,#a34d6b 0%,#6e2b49 45%,#3f1a2c 100%)',
};

function page(h, c) {
  const clair = h.fond === 'rose';
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}
  html,body{width:540px;height:960px;overflow:hidden;background:${FONDS[h.fond] || FONDS.nuit};margin:0}
  :root{--t:${clair ? '#86385a' : '#fdf1f4'};--x:${clair ? '#5c2740' : '#fbe7ee'};--a:${clair ? '#a34d6b' : '#e8a3b9'}}
  #fx{position:absolute;inset:0;width:540px;height:960px}
  .plan{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--x);text-align:center;opacity:0}
  [data-a]{opacity:0}
  .trf,.tr{fill:none;stroke:var(--a);stroke-width:1.6px;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}.coeur{fill:var(--a)}
  .pov{position:absolute;top:96px;left:40px;right:40px;font-weight:700;font-size:20px;color:#fff;background:rgba(63,26,44,.55);border-radius:16px;padding:12px 16px;letter-spacing:.01em}
  .lock{display:flex;flex-direction:column;align-items:center;width:100%}
  .heure{font-family:var(--texte);font-weight:300;font-size:104px;color:#fff;letter-spacing:.02em;margin-top:30px}
  .jour{font-size:17px;color:#fbe7ee;font-weight:600;margin-top:-4px}
  .notif{margin-top:70px;width:440px;display:flex;gap:14px;align-items:center;text-align:left;background:rgba(253,241,244,.93);color:#5c2740;border-radius:24px;padding:16px 18px;box-shadow:0 12px 40px rgba(0,0,0,.35)}
  .notif .ic,.av{width:46px;height:46px;flex:none;border-radius:13px;background:#86385a;display:flex;align-items:center;justify-content:center}
  .notif .ic svg,.av svg{width:34px;height:34px}.notif .ic .trf,.av .trf{stroke:#fdf1f4}.notif .ic .coeur,.av .coeur{fill:#fdf1f4}
  .notif .de{font-weight:700;font-size:15px}.notif .de span{font-weight:500;font-size:12px;opacity:.6;margin-left:6px}.notif .msg{font-size:15px;line-height:1.35;margin-top:3px}
  .tel{width:430px;height:800px;border-radius:46px;background:#fdf1f4;border:7px solid #2a1220;box-shadow:0 20px 60px rgba(0,0,0,.45);display:flex;flex-direction:column;overflow:hidden;color:#5c2740}
  .tel .haut{display:flex;align-items:center;gap:12px;padding:44px 20px 14px;background:#fff;border-bottom:1px solid #f1d3dd;text-align:left}
  .av{border-radius:50%}.nom{font-weight:700;font-size:17px}.etat{font-size:12px;color:#a34d6b}
  .fil{flex:1;display:flex;flex-direction:column;justify-content:flex-start;gap:12px;padding:22px 16px;overflow:hidden}
  .chip{align-self:center;font-size:12px;font-weight:700;color:#a34d6b;background:#f6dbe4;border-radius:20px;padding:5px 12px;margin-bottom:8px}
  .b{max-width:82%;padding:14px 18px;border-radius:24px;font-size:21px;line-height:1.35;text-align:left;font-weight:500}
  .b.moi{align-self:flex-end;background:#a34d6b;color:#fff;border-bottom-right-radius:6px}
  .b.elle{align-self:flex-start;background:#fff;color:#5c2740;border-bottom-left-radius:6px;box-shadow:0 2px 8px rgba(134,56,90,.12)}
  .dots{align-self:flex-start;background:#fff;border-radius:22px;padding:14px 18px;display:flex;gap:6px}
  .dots i{width:8px;height:8px;border-radius:50%;background:#e8a3b9;display:block}
  .bas{display:flex;align-items:center;gap:10px;padding:12px 14px 30px;background:#fff;border-top:1px solid #f1d3dd}
  .champ{flex:1;position:relative;background:#fdf1f4;border-radius:22px;padding:11px 16px;font-size:16px;text-align:left;min-height:20px}
  .champ .ph{color:#c98aa1}.saisie{position:absolute;left:16px;right:12px;top:11px;background:#fdf1f4;color:#5c2740}
  .env{width:42px;height:42px;border-radius:50%;background:#a34d6b;color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px}
  .carte{width:360px;height:500px;position:relative;transform-style:preserve-3d;perspective:1400px}
  .face{position:absolute;inset:0;border-radius:28px;backface-visibility:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 18px 50px rgba(0,0,0,.4)}
  .dos{background:#86385a;transform:rotateY(180deg)}.dos svg{width:120px;height:120px}.dos .trf{stroke:#e8a3b9}
  .avant{background:linear-gradient(160deg,#fdf1f4,#f4d6e0);color:#86385a;border:2px solid #e8a3b9;padding:30px}
  .avant .k{font-size:12px;letter-spacing:.32em;text-transform:uppercase;font-weight:700;color:#a34d6b}
  .avant .fl{width:56px;height:56px;margin:22px 0}.avant .trf{stroke:#a34d6b}.avant .coeur{fill:#a34d6b}
  .avant .ti{font-family:var(--titre);font-size:44px;line-height:1.1;font-weight:600}.avant .st{margin-top:16px;font-size:17px;color:#5c2740;font-weight:500}
  .verset{width:100%;height:100%;position:relative}
  .verset .k{position:absolute;top:120px;left:0;right:0;font-size:12px;letter-spacing:.36em;text-transform:uppercase;font-weight:700;color:var(--a)}
  .aya{position:absolute;left:36px;right:36px;top:250px;display:flex;flex-direction:column;align-items:center}
  .aya .ar{font-family:var(--arabe);font-size:50px;line-height:1.9;color:var(--t);direction:rtl}
  .aya .ar span{display:inline-block}
  .aya .fr{margin-top:26px;font-size:22px;line-height:1.5;font-style:italic;font-weight:500;max-width:440px}
  .verset .ref{position:absolute;top:620px;left:0;right:0;font-size:12px;letter-spacing:.28em;text-transform:uppercase;font-weight:700;color:var(--a)}
  .verset .note{position:absolute;top:680px;left:50px;right:50px;font-size:17px;line-height:1.5;font-weight:500}
  .onde{position:absolute;top:160px;left:0;right:0;height:46px;display:flex;justify-content:center;align-items:center;gap:5px}
  .onde i{width:4px;border-radius:3px;background:var(--a);height:6px;display:block}
  .verset .rec{position:absolute;bottom:70px;left:0;right:0;font-size:11px;letter-spacing:.2em;opacity:.7}
  .textes{display:flex;flex-direction:column;gap:22px;padding:0 44px}
  .textes .ln{font-family:var(--titre);font-size:46px;line-height:1.15;color:var(--t);font-weight:600}
  .textes .ln b{color:var(--a);font-weight:700}
  .liste .ti{font-family:var(--titre);font-size:44px;color:var(--t);margin-bottom:26px;font-weight:600}
  .liste .li{display:flex;align-items:center;gap:16px;font-size:21px;font-weight:600;margin:12px 0;text-align:left}
  .liste svg{width:36px;height:36px;flex:none}.rond{fill:none;stroke:var(--a);stroke-width:1.4px;vector-effect:non-scaling-stroke}
  .ck{fill:none;stroke:var(--a);stroke-width:3px;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}
  .fin{display:flex;flex-direction:column;align-items:center;padding:0 50px}.fin .logo{width:100px;height:100px}
  .fin .ti{margin-top:20px;font-family:var(--titre);font-size:42px;line-height:1.15;color:var(--t);font-weight:600}
  .fin .cta{margin-top:28px;font-size:13px;letter-spacing:.24em;text-transform:uppercase;font-weight:700;color:var(--a);border:1px solid var(--a);border-radius:40px;padding:13px 26px}
  .fin .sig{margin-top:40px;font-size:12px;letter-spacing:.22em;font-weight:700;color:var(--a)}
  </style></head><body><canvas id="fx" width="1080" height="1920"></canvas>${c.html}
  <script>
  const cl=(v)=>Math.max(0,Math.min(1,v)), ease=(p)=>1-Math.pow(1-p,3), back=(p)=>{const c=1.6;return 1+(c+1)*Math.pow(p-1,3)+c*Math.pow(p-1,2)};
  let s=7; const R=()=>(s=(s*16807)%2147483647)/2147483647;
  const P=Array.from({length:90},()=>({x:R(),y:R(),v:R(),r:R(),k:R()}));
  const ctx=document.getElementById('fx').getContext('2d');
  const CLAIR=${clair};
  function fx(t){ctx.clearRect(0,0,1080,1920);for(const p of P){const a=.2+.8*Math.abs(Math.sin(t*(.5+p.v)+p.k*6.28));
    const y=(p.y*1920-t*(8+p.v*16)+1920)%1920;ctx.fillStyle=CLAIR?'rgba(232,163,185,'+a*.35+')':'rgba(255,240,246,'+a*(.25+p.r*.45)+')';
    ctx.beginPath();ctx.arc(p.x*1080,y,1+p.r*2.6,0,6.29);ctx.fill();}}
  const PL=[...document.querySelectorAll('.plan')], E=[...document.querySelectorAll('[data-a]')];
  for(const el of E){if(el.dataset.a==='dessin'){el._p=[...el.querySelectorAll('.tr')];el._p.forEach(q=>{q.style.strokeDasharray='1 1'});}
    if(el.dataset.a==='trait'){el.style.strokeDasharray='1 1';}}
  window.setT=(t)=>{fx(t);
    for(const p of PL){const p0=+p.dataset.p0,p1=+p.dataset.p1;if(t<p0-.01||t>p1+.01){p.style.opacity=0;continue}
      const e=ease(cl((t-p0)/${TR})), x=ease(cl((t-(p1-${TR}))/${TR})), k=cl((t-p0)/(p1-p0));
      const z=1+.035*k; let tf='';
      if(p.dataset.tr==='glisse') tf='translateX('+((1-e)*540-x*540)+'px)';
      else tf='translateY('+((1-e)*120)+'px)';
      p.style.transform=tf+' scale('+(z*(1-.06*x)*(1.06-.06*e))+')';
      p.style.opacity=Math.min(e,1-x); p.style.filter='blur('+((1-e)*8+x*6)+'px)';}
    for(const el of E){const t0=+el.dataset.t0,d=+(el.dataset.d||.6),t1=el.dataset.t1?+el.dataset.t1:1e9,a=el.dataset.a;
      const q=cl((t-t0)/d),p=ease(q),o=ease(cl((t-t1)/.3)),vis=p*(1-o);
      if(a==='rise'){el.style.opacity=vis;el.style.transform='translateY('+((1-p)*24)+'px)'}
      else if(a==='fade'){el.style.opacity=vis}
      else if(a==='pop'){el.style.opacity=vis;el.style.transform='scale('+(q<=0?.5:.5+.5*back(q))+')'}
      else if(a==='drop'){el.style.opacity=vis;el.style.transform='translateY('+((1-p)*-140)+'px) scale('+(.9+.1*p)+')'}
      else if(a==='bulle'){el.style.opacity=t<t0?0:1;el.style.display=t<t0?'none':'';el.style.transform='scale('+(q<=0?.4:.4+.6*back(q))+')';el.style.transformOrigin=el.classList.contains('moi')?'100% 100%':'0% 100%'}
      else if(a==='mot'){el.style.opacity=p;el.style.transform='translateY('+((1-p)*10)+'px)';el.style.filter='blur('+((1-p)*4)+'px)'}
      else if(a==='type'){el.style.opacity=t>=t0&&t<t1?1:0;const n=Math.floor(el.dataset.txt.length*cl((t-t0)/d));el.textContent=el.dataset.txt.slice(0,n)+((t*2|0)%2?'|':'')}
      else if(a==='flip'){el.style.opacity=t<t0-.2?0:1;el.style.transform='rotateY('+(180*(1-p))+'deg) scale('+(.85+.15*p)+')'}
      else if(a==='dessin'){el.style.opacity=t<t0?0:1;el._p.forEach(q2=>q2.style.strokeDashoffset=1-p)}
      else if(a==='trait'){el.style.opacity=t<t0?0:1;el.style.strokeDashoffset=1-p}
      if(el.dataset.onde){const [o0,o1]=el.dataset.onde.split(',').map(Number),on=t>o0&&t<o1;el.querySelectorAll('i').forEach((i,j)=>i.style.height=(6+(on?34*Math.abs(Math.sin(t*(5+j%5)+j*1.7))*Math.abs(Math.sin(t*2.3+j)):0))+'px')}
      if(el.classList.contains('dots')){el.style.display=t<t0||t>t1?'none':'flex';el.querySelectorAll('i').forEach((i,j)=>i.style.transform='translateY('+(-5*Math.max(0,Math.sin(t*9-j*.9)))+'px)')}
    }};
  </script></body></html>`;
}

const browser = await chromium.launch();
const pg = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || '/tmp', 'hist-'));
for (const h of data.histoires || []) {
  if (seule && h.id !== seule) continue;
  const c = compiler(h);
  await pg.setContent(page(h, c), { waitUntil: 'load' });
  await pg.evaluate(() => document.fonts.ready);
  const evts = path.join(tmp, h.id + '.json'), amb = path.join(tmp, h.id + '.wav');
  fs.writeFileSync(evts, JSON.stringify(c.sons));
  if (spawnSync('python3', [path.join(ici, 'sons.py'), h.ambiance || 'chambre', String(c.D), evts, amb], { stdio: 'inherit' }).status) throw new Error('audio');
  // Mixage : ambiance + bruitages, puis récitations placées à leur temps (le Coran reste seul : ambiance effacée)
  const ins = ['-i', amb], f = [];
  c.coran.forEach((q, k) => { ins.push('-i', q.f); f.push(`[${k + 1}:a]aresample=44100,aformat=channel_layouts=stereo,adelay=${Math.round(q.t * 1000)}|${Math.round(q.t * 1000)},volume=1.6[q${k}]`); });
  const mix = path.join(tmp, h.id + '-mix.wav');
  const fc = f.join(';') + (f.length ? ';' : '') + `[0:a]volume=0.55[am];[am]${c.coran.map((_, k) => `[q${k}]`).join('')}amix=inputs=${c.coran.length + 1}:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[o]`;
  if (spawnSync('ffmpeg', ['-nostdin', '-loglevel', 'error', '-y', ...ins, '-filter_complex', fc, '-map', '[o]', '-ar', '44100', mix], { stdio: 'inherit' }).status) throw new Error('mix');
  const out = path.join(sortie, `${h.id}.mp4`);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', mix,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const fini = new Promise((ok, ko) => ff.on('close', (x) => (x ? ko(new Error('ffmpeg ' + x)) : ok())));
  const N = Math.round(c.D * FPS);
  for (let k = 0; k < N; k++) {
    await pg.evaluate((t) => window.setT(t), k / FPS);
    const buf = await pg.screenshot({ type: 'jpeg', quality: 90 });
    if (!ff.stdin.write(buf)) await new Promise((ok) => ff.stdin.once('drain', ok));
  }
  ff.stdin.end(); await fini;
  await pg.evaluate((t) => window.setT(t), h.couverture ?? 2.2);
  await pg.screenshot({ path: path.join(sortie, `${h.id}-cover.jpg`), type: 'jpeg', quality: 92 });
  console.log('✔', h.id, c.D + 's', c.coran.length ? `· ${c.coran.length} verset(s) récité(s)` : '');
}
await browser.close();
