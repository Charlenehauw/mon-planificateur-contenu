// Rendu PNG des aperçus + PDF intérieur KDP (8,5 x 11 po, une page blanche au dos de chaque dessin)
import { chromium } from 'playwright';
import fs from 'node:fs';
const svgs = fs.readdirSync('svg').filter(f => f.endsWith('.svg')).sort();
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
fs.mkdirSync('apercus', { recursive: true });
for (const f of svgs) { await p.setContent(`<style>body{margin:0}</style>${fs.readFileSync('svg/' + f, 'utf8')}`); await p.evaluate(() => document.fonts.ready); await p.screenshot({ path: 'apercus/' + f.replace('.svg', '.png') }); }
const titre = `<div class="pg" style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-family:Quicksand">
<div style="font-family:'Dancing Script';font-size:84px;font-weight:700">Cosy Colors</div>
<div style="font-size:30px;letter-spacing:.2em;text-transform:uppercase;margin-top:10px">Post-partum</div>
<div style="font-size:20px;margin-top:24px;max-width:5.5in;line-height:1.5">25 dessins tout doux à colorier,<br>pour poser ton cerveau et tes émotions</div>
<div style="margin-top:1.4in;font-size:22px">Ce livre appartient à</div>
<div style="width:4.5in;border-bottom:2px solid #000;height:50px"></div></div><div class="pg"></div>`;
const pages = titre + svgs.map(f => `<div class="pg">${fs.readFileSync('svg/' + f, 'utf8')}</div><div class="pg"></div>`).join('');
await p.setContent(`<style>@page{size:8.5in 11in;margin:0}body{margin:0}.pg{width:8.5in;height:11in;page-break-after:always;overflow:hidden}.pg svg{width:100%;height:100%}</style>${pages}`);
await p.evaluate(() => document.fonts.ready);
await p.pdf({ path: 'cosy-colors-post-partum-interieur.pdf', width: '8.5in', height: '11in', printBackground: true });
await b.close(); console.log('ok', svgs.length);
