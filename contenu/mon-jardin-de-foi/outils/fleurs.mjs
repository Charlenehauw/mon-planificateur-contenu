// Petites illustrations SVG réutilisables (fleurs, pétales, feuilles) aux couleurs de la marque.
export const C = { poudre: '#fdf1f4', rose: '#e8a3b9', framboise: '#a34d6b', mauve: '#86385a', feuille: '#9bb59a', feuilleFonce: '#6f8f6e', or: '#e9c48a' };

export function fleur({ x = 0, y = 0, r = 40, petales = 5, couleur = C.rose, coeur = C.framboise, rot = 0, opacite = 1, echelle = 1 } = {}) {
  let p = '';
  for (let i = 0; i < petales; i++) {
    const a = (360 / petales) * i;
    p += `<ellipse cx="0" cy="${-r * 0.55}" rx="${r * 0.36}" ry="${r * 0.58}" fill="${couleur}" transform="rotate(${a})"/>`;
  }
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${echelle})" opacity="${opacite}">${p}<circle r="${r * 0.24}" fill="${coeur}"/></g>`;
}

export function tulipe({ x = 0, y = 0, h = 120, couleur = C.rose, fonce = C.framboise, echelle = 1, opacite = 1 } = {}) {
  return `<g transform="translate(${x} ${y}) scale(${echelle})" opacity="${opacite}">
    <path d="M0 0 C 2 ${-h * 0.4} -2 ${-h * 0.7} 0 ${-h}" stroke="${C.feuilleFonce}" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M0 ${-h * 0.35} C ${h * 0.25} ${-h * 0.45} ${h * 0.3} ${-h * 0.6} ${h * 0.28} ${-h * 0.72} C ${h * 0.12} ${-h * 0.6} ${h * 0.05} ${-h * 0.5} 0 ${-h * 0.42}Z" fill="${C.feuille}"/>
    <path d="M${-h * 0.18} ${-h} C ${-h * 0.2} ${-h * 1.2} ${-h * 0.1} ${-h * 1.3} 0 ${-h * 1.22} C ${h * 0.1} ${-h * 1.3} ${h * 0.2} ${-h * 1.2} ${h * 0.18} ${-h} C ${h * 0.12} ${-h * 0.9} ${-h * 0.12} ${-h * 0.9} ${-h * 0.18} ${-h}Z" fill="${couleur}"/>
    <path d="M0 ${-h * 1.22} C ${h * 0.08} ${-h * 1.1} ${h * 0.06} ${-h * 0.98} 0 ${-h * 0.93} C ${-h * 0.06} ${-h * 0.98} ${-h * 0.08} ${-h * 1.1} 0 ${-h * 1.22}Z" fill="${fonce}" opacity=".55"/>
  </g>`;
}

export function feuille({ x = 0, y = 0, l = 60, rot = 0, couleur = C.feuille, opacite = 1 } = {}) {
  return `<g transform="translate(${x} ${y}) rotate(${rot})" opacity="${opacite}"><path d="M0 0 C ${l * 0.3} ${-l * 0.35} ${l * 0.75} ${-l * 0.3} ${l} 0 C ${l * 0.75} ${l * 0.3} ${l * 0.3} ${l * 0.35} 0 0Z" fill="${couleur}"/><path d="M0 0 L ${l * 0.9} 0" stroke="${C.feuilleFonce}" stroke-width="1.5" opacity=".5"/></g>`;
}

export function petale({ x = 0, y = 0, s = 18, rot = 0, couleur = C.rose, opacite = 0.8 } = {}) {
  return `<g transform="translate(${x} ${y}) rotate(${rot})" opacity="${opacite}"><path d="M0 ${-s} C ${s * 0.8} ${-s * 0.6} ${s * 0.7} ${s * 0.6} 0 ${s} C ${-s * 0.7} ${s * 0.6} ${-s * 0.8} ${-s * 0.6} 0 ${-s}Z" fill="${couleur}"/></g>`;
}

// Bouquet décoratif d'angle
export function bouquet(x, y, e = 1, miroir = false) {
  const s = miroir ? -1 : 1;
  return `<g transform="translate(${x} ${y}) scale(${s * e} ${e})">
    ${feuille({ x: 0, y: 0, l: 120, rot: -35 })}
    ${feuille({ x: 0, y: 0, l: 95, rot: -80 })}
    ${feuille({ x: 0, y: 0, l: 80, rot: 10, couleur: '#b7cbb5' })}
    ${fleur({ x: 70, y: -70, r: 46, couleur: C.rose })}
    ${fleur({ x: 10, y: -125, r: 30, couleur: '#f3c6d4', coeur: C.mauve, rot: 20 })}
    ${fleur({ x: 125, y: -10, r: 26, couleur: C.framboise, coeur: '#f3c6d4', rot: 12 })}
  </g>`;
}

// ——— Style « premium » : botaniques en trait fin ———
export function brancheLigne({ x = 0, y = 0, e = 1, rot = 0, couleur = '#a34d6b', epaisseur = 2.2, opacite = 1 } = {}) {
  const st = `stroke="${couleur}" stroke-width="${epaisseur / e}" fill="none" stroke-linecap="round" stroke-linejoin="round"`;
  const f = (cx, cy, r, a) => {
    let p = '';
    for (let i = 0; i < 5; i++) p += `<path d="M0 0 C ${r * 0.5} ${-r * 0.35} ${r * 0.45} ${-r} 0 ${-r * 1.05} C ${-r * 0.45} ${-r} ${-r * 0.5} ${-r * 0.35} 0 0Z" transform="rotate(${i * 72})" ${st}/>`;
    return `<g transform="translate(${cx} ${cy}) rotate(${a})">${p}<circle r="${r * 0.13}" fill="${couleur}"/></g>`;
  };
  const l = (cx, cy, len, a) => `<g transform="translate(${cx} ${cy}) rotate(${a})"><path d="M0 0 C ${len * 0.3} ${-len * 0.3} ${len * 0.75} ${-len * 0.25} ${len} 0 C ${len * 0.75} ${len * 0.25} ${len * 0.3} ${len * 0.3} 0 0Z" ${st}/><path d="M0 0 L ${len * 0.85} 0" ${st} opacity=".6"/></g>`;
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${e})" opacity="${opacite}">
    <path d="M0 0 C 40 -90 30 -200 110 -300 C 150 -350 170 -390 175 -430" ${st}/>
    <path d="M62 -170 C 100 -190 130 -230 140 -270" ${st}/>
    ${l(20, -60, 70, -60)}${l(35, -110, 60, 200)}${l(70, -210, 60, -40)}${l(100, -260, 55, 150)}${l(150, -340, 45, -75)}
    ${f(175, -440, 34, 10)}${f(140, -278, 22, -20)}
    <circle cx="48" cy="-150" r="5" fill="${couleur}"/><circle cx="120" cy="-320" r="4" fill="${couleur}"/>
  </g>`;
}

export function fleurLigne({ x = 0, y = 0, r = 20, couleur = '#a34d6b', epaisseur = 2.5 } = {}) {
  let p = '';
  for (let i = 0; i < 5; i++) p += `<path d="M0 0 C ${r * 0.5} ${-r * 0.35} ${r * 0.45} ${-r} 0 ${-r * 1.05} C ${-r * 0.45} ${-r} ${-r * 0.5} ${-r * 0.35} 0 0Z" transform="rotate(${i * 72})" stroke="${couleur}" stroke-width="${epaisseur}" fill="none" stroke-linejoin="round"/>`;
  return `<g transform="translate(${x} ${y})">${p}<circle r="${r * 0.15}" fill="${couleur}"/></g>`;
}

// ——— Fleurs minimalistes (une par post) — dessinées au trait, centrées sur (0,0), ~120px ———
const S = (c, w = 2) => `stroke="${c}" stroke-width="${w}" fill="none" stroke-linecap="round" stroke-linejoin="round"`;
export const MOTIFS = [
  // 0 tulipe
  (c) => `<path d="M0 60 C 2 20 -2 0 0 -10" ${S(c)}/><path d="M0 35 C 18 25 26 10 24 -2 C 12 4 4 16 0 30" ${S(c)}/>
    <path d="M-22 -40 C -24 -18 -12 -8 0 -8 C 12 -8 24 -18 22 -40 C 14 -32 8 -34 0 -48 C -8 -34 -14 -32 -22 -40Z" ${S(c)}/>`,
  // 1 marguerite
  (c) => Array.from({ length: 12 }, (_, i) => `<ellipse cx="0" cy="-30" rx="7" ry="20" transform="rotate(${i * 30})" ${S(c, 1.8)}/>`).join('') + `<circle r="9" fill="${c}"/>`,
  // 2 rose (spirale)
  (c) => `<path d="M0 0 C 6 -6 12 2 6 8 C -2 16 -16 6 -12 -6 C -6 -22 18 -22 22 -4 C 26 16 4 30 -14 24 C -34 16 -34 -14 -18 -28 C 0 -42 32 -34 38 -12" ${S(c)}/>
    <path d="M-30 30 C -20 46 20 46 30 30" ${S(c)}/><path d="M0 44 L0 64" ${S(c)}/>`,
  // 3 brin de lavande
  (c) => `<path d="M0 62 C -2 20 2 -20 0 -60" ${S(c)}/>` + Array.from({ length: 7 }, (_, i) => `<ellipse cx="${i % 2 ? 6 : -6}" cy="${-56 + i * 11}" rx="5" ry="8" transform="rotate(${i % 2 ? 25 : -25} ${i % 2 ? 6 : -6} ${-56 + i * 11})" ${S(c, 1.8)}/>`).join(''),
  // 4 fleur cinq pétales
  (c) => Array.from({ length: 5 }, (_, i) => `<path d="M0 0 C 20 -14 18 -40 0 -42 C -18 -40 -20 -14 0 0Z" transform="rotate(${i * 72})" ${S(c)}/>`).join('') + `<circle r="5" fill="${c}"/>`,
  // 5 coquelicot
  (c) => `<path d="M0 0 C -30 -10 -36 -44 -8 -48 C 0 -50 4 -46 0 -40 C 4 -46 30 -50 34 -26 C 38 -6 16 0 0 0Z" ${S(c)}/>
    <path d="M0 0 C -24 4 -40 26 -22 40 C -8 48 0 40 0 34 C 0 40 14 48 26 38 C 40 24 22 4 0 0Z" ${S(c)}/>` + [0, 60, 120, 180, 240, 300].map((a) => `<circle cx="${Math.cos(a * Math.PI / 180) * 7}" cy="${Math.sin(a * Math.PI / 180) * 7}" r="2" fill="${c}"/>`).join(''),
  // 6 muguet
  (c) => `<path d="M-30 62 C -30 0 0 -50 40 -56" ${S(c)}/>` + [[-22, 10], [-12, -14], [4, -34], [24, -48]].map(([x, y]) => `<path d="M${x} ${y} l 0 8" ${S(c, 1.6)}/><path d="M${x - 8} ${y + 22} C ${x - 9} ${y + 10} ${x + 9} ${y + 10} ${x + 8} ${y + 22} L ${x + 4} ${y + 19} L ${x} ${y + 23} L ${x - 4} ${y + 19}Z" ${S(c, 1.6)}/>`).join(''),
];
