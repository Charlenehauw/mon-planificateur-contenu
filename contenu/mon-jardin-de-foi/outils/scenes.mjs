// Scènes des reels « Mon Jardin de Foi » (style premium : trait fin qui se dessine, typographie élégante).
// Chaque scène : { duree, fond: 'clair'|'sombre'|'aube'|'nuit', particules, html, sons: [{t, type}] , ambiance }
// Animations : data-a="rise|fade|pop|draw|bloom|strike|tick" data-t0=début data-t1=sortie (optionnel) data-d=durée

const FL = (r = 40, cls = 'tr') => {
  let p = '';
  for (let i = 0; i < 5; i++) p += `<path class="${cls}" pathLength="1" d="M0 0 C ${r * 0.5} ${-r * 0.35} ${r * 0.45} ${-r} 0 ${-r * 1.05} C ${-r * 0.45} ${-r} ${-r * 0.5} ${-r * 0.35} 0 0Z" transform="rotate(${i * 72})"/>`;
  return p + `<circle class="coeur" r="${r * 0.14}"/>`;
};
// Tige + feuilles + fleur (dessin au trait)
const PLANTE = (h = 220, r = 40) => `
  <path class="tr" pathLength="1" d="M0 0 C 6 ${-h * 0.35} -8 ${-h * 0.65} 0 ${-h}"/>
  <path class="tr" pathLength="1" d="M0 ${-h * 0.3} C ${h * 0.12} ${-h * 0.38} ${h * 0.28} ${-h * 0.36} ${h * 0.33} ${-h * 0.46} C ${h * 0.2} ${-h * 0.5} ${h * 0.08} ${-h * 0.45} 0 ${-h * 0.3}Z"/>
  <path class="tr" pathLength="1" d="M0 ${-h * 0.52} C ${-h * 0.12} ${-h * 0.6} ${-h * 0.28} ${-h * 0.58} ${-h * 0.32} ${-h * 0.68} C ${-h * 0.2} ${-h * 0.72} ${-h * 0.08} ${-h * 0.66} 0 ${-h * 0.52}Z"/>
  <g transform="translate(0 ${-h - r * 0.9})">${FL(r)}</g>`;
const POUSSE = (h = 120) => `
  <path class="tr" pathLength="1" d="M0 0 C 2 ${-h * 0.4} -3 ${-h * 0.7} 0 ${-h}"/>
  <path class="tr" pathLength="1" d="M0 ${-h} C ${h * 0.15} ${-h * 1.15} ${h * 0.45} ${-h * 1.15} ${h * 0.55} ${-h * 1.02} C ${h * 0.35} ${-h * 0.88} ${h * 0.12} ${-h * 0.9} 0 ${-h}Z"/>
  <path class="tr" pathLength="1" d="M0 ${-h * 0.85} C ${-h * 0.15} ${-h * 1.0} ${-h * 0.42} ${-h * 0.98} ${-h * 0.5} ${-h * 0.86} C ${-h * 0.32} ${-h * 0.74} ${-h * 0.12} ${-h * 0.76} 0 ${-h * 0.85}Z"/>
  <path class="tr" pathLength="1" d="M${-h * 0.5} 0 L ${h * 0.5} 0"/>`;

const titre = (t0, t1, txt, cls = '') => `<div class="bloc ${cls}" data-a="rise" data-t0="${t0}" data-t1="${t1}"><h1>${txt}</h1></div>`;
const sep = (t0, t1) => `<div class="sep" data-a="fade" data-t0="${t0}" data-t1="${t1}"><span></span><svg viewBox="-26 -26 52 52"><g>${FL(18, 'trf')}</g></svg><span></span></div>`;
const marque = (t0) => `
  <div class="final" data-a="rise" data-t0="${t0}">
    <svg class="logo" viewBox="-60 -70 120 120" data-a="draw" data-t0="${t0}" data-d="1.6"><g>${FL(42)}</g></svg>
    <div class="nom">Mon Jardin de Foi</div>
    <div class="cta" data-a="fade" data-t0="${t0 + 0.8}">Lien en bio</div>
  </div>`;

export const SCENES = {
  // R1 — chaque prière fait pousser une fleur
  jardin: {
    duree: 16, fond: 'clair', particules: 'petales', ambiance: 'jardin',
    sons: [3.6, 5.0, 6.4, 7.8, 9.2].map((t) => ({ t: t + 0.9, type: 'carillon' })).concat([{ t: 12.6, type: 'carillon2' }]),
    html: `
      <div class="haut">
        <div class="kicker" data-a="fade" data-t0="0.2" data-t1="11.6"><span></span>Mon Jardin de Foi<span></span></div>
        ${titre(0.4, 11.6, 'Et si chaque prière<br>faisait pousser<br>une fleur&nbsp;?')}
      </div>
      <div class="jardin">
        ${['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'].map((p, i) => `
          <div class="pl" data-a="fade" data-t0="${3.4 + i * 1.4}" data-t1="11.6">
            <svg viewBox="-80 -330 160 340" data-a="draw" data-t0="${3.4 + i * 1.4}" data-d="1.3"><g>${PLANTE(200 + (i % 2) * 40, 40)}</g></svg>
            <svg class="bl" viewBox="-80 -330 160 340" data-a="bloom" data-t0="${4.3 + i * 1.4}" data-d=".7"><g transform="translate(0 ${-(200 + (i % 2) * 40) - 36})">${FL(40, 'pf')}</g></svg>
            <div class="lbl">${p}</div>
          </div>`).join('')}
      </div>
      <div class="sous" data-a="rise" data-t0="10.2" data-t1="11.6">Ton jardin grandit avec toi, prière après prière.</div>
      ${marque(12.2)}`,
  },

  // R2 — pluie : la régularité
  pluie: {
    duree: 16, fond: 'sombre', particules: 'pluie', ambiance: 'pluie',
    sons: [{ t: 4.0, type: 'carillon2' }, { t: 12.4, type: 'carillon' }],
    html: `
      <div class="centre">
        ${titre(0.4, 3.6, 'Un peu,<br>mais régulièrement')}
        <div class="bloc" data-a="rise" data-t0="4" data-t1="8.4">
          <div class="ar arabe">أَحَبُّ الأَعْمَالِ إِلَى اللَّهِ<br>أَدْوَمُهَا وَإِنْ قَلَّ</div>
          ${sep(4.6, 8.4)}
          <p class="trad" data-a="fade" data-t0="5.4" data-t1="8.4">« Les œuvres les plus aimées d'Allah sont les plus régulières, même si elles sont peu nombreuses. »</p>
          <p class="ref" data-a="fade" data-t0="6.4" data-t1="8.4">Al-Bukhari &amp; Muslim</p>
        </div>
        <div class="bloc" data-a="rise" data-t0="8.8" data-t1="11.8" style="justify-content:flex-start;padding-top:330px"><p class="petit">Comme la pluie, goutte après goutte,<br>qui fait pousser tout un jardin.</p></div>
      </div>
      <svg class="pousse" viewBox="-120 -260 240 270" data-a="draw" data-t0="8.8" data-d="2.4" data-t1="11.8"><g>${PLANTE(170, 30)}</g></svg>
      ${marque(12.2)}`,
  },

  // R3 — 3 petites graines
  graines: {
    duree: 17, fond: 'clair', particules: 'lumiere', ambiance: 'jardin',
    sons: [{ t: 3.9, type: 'pop' }, { t: 6.4, type: 'pop' }, { t: 8.9, type: 'pop' }, { t: 13.2, type: 'carillon2' }],
    html: `
      <div class="centre">
        ${titre(0.3, 2.9, 'Débordée&nbsp;?')}
        <div class="bloc" data-a="rise" data-t0="3.1" data-t1="12.6">
          <div class="kicker2">Commence par</div>
          <h2>3 petites graines</h2>
          ${sep(3.4, 12.6)}
          <div class="graines">
            ${['1 verset par jour', '1 invocation après chaque prière', '1 bonne action discrète'].map((g, i) => `
              <div class="gr" data-a="rise" data-t0="${3.8 + i * 2.5}" data-t1="12.6">
                <svg viewBox="-70 -150 140 160" data-a="draw" data-t0="${3.8 + i * 2.5}" data-d="1.4"><g>${POUSSE(100)}</g></svg>
                <span>${g}</span>
              </div>`).join('')}
          </div>
          <p class="petit" data-a="fade" data-t0="10.6" data-t1="12.6">Plante. Arrose.<br>Et laisse Allah faire pousser.</p>
        </div>
      </div>
      ${marque(13.0)}`,
  },

  // R4 — aube : avec la difficulté, la facilité
  aube: {
    duree: 16, fond: 'aube', particules: 'lumiere', ambiance: 'aube',
    sons: [{ t: 4.2, type: 'carillon2' }, { t: 9.4, type: 'carillon' }],
    html: `
      <div class="centre">
        ${titre(0.5, 3.8, 'Ce que tu traverses<br>n\'est pas la fin<br>de ton histoire')}
        <div class="bloc" data-a="rise" data-t0="4.2" data-t1="12">
          <div class="ar arabe">فَإِنَّ مَعَ ٱلْعُسْرِ يُسْرًا<br>إِنَّ مَعَ ٱلْعُسْرِ يُسْرًا</div>
          ${sep(4.8, 12)}
          <p class="trad" data-a="fade" data-t0="5.6" data-t1="12">« À côté de la difficulté est, certes, une facilité. À côté de la difficulté, certes, une facilité. »</p>
          <p class="ref" data-a="fade" data-t0="6.6" data-t1="12">Sourate Ash-Sharh, 94:5-6</p>
          <p class="petit" data-a="fade" data-t0="9.2" data-t1="12">Allah l'a dit deux fois.<br>Pour que ton cœur l'entende bien.</p>
        </div>
      </div>
      ${marque(12.4)}`,
  },

  // R5 — checklist du vendredi
  jumua: {
    duree: 16, fond: 'sombre', particules: 'lumiere', ambiance: 'brise',
    sons: [4.4, 5.9, 7.4, 8.9].map((t) => ({ t: t + 0.35, type: 'tick' })).concat([{ t: 0.6, type: 'carillon2' }, { t: 12.4, type: 'carillon' }]),
    html: `
      <svg class="arche" viewBox="0 0 600 900" data-a="draw" data-t0="0.2" data-d="2.6" data-t1="11.8"><g>
        <path class="tr" pathLength="1" d="M60 900 L60 380 C60 200 200 90 300 40 C400 90 540 200 540 380 L540 900"/>
        <path class="tr" pathLength="1" d="M90 900 L90 390 C90 225 215 125 300 78 C385 125 510 225 510 390 L510 900"/>
      </g></svg>
      <div class="centre">
        <div class="bloc" data-a="rise" data-t0="0.6" data-t1="11.8">
          <div class="kicker2">Jumu'a Mubarak</div>
          <h2>Ta checklist<br>du vendredi</h2>
          ${sep(1.4, 11.8)}
          <div class="liste">
            ${['Ghusl', 'Sourate Al-Kahf', 'Salawat sur le Prophète ﷺ', 'Invocations, l\'heure exaucée'].map((x, i) => `
              <div class="li" data-a="rise" data-t0="${2.2 + i * 0.5}" data-t1="11.8">
                <svg viewBox="-24 -24 48 48"><circle r="20" class="rond"/><path class="tr ck" pathLength="1" d="M-9 1 L-2 8 L11 -8" data-a="draw" data-t0="${4.4 + i * 1.5}" data-d=".5"/></svg>
                <span>${x}</span>
              </div>`).join('')}
          </div>
          <p class="petit" data-a="fade" data-t0="10.4" data-t1="11.8">Qu'Allah accepte tes invocations.</p>
        </div>
      </div>
      ${marque(12.2)}`,
  },

  // R6 — nuit : apaiser son cœur
  nuit: {
    duree: 16, fond: 'nuit', particules: 'etoiles', ambiance: 'nuit',
    sons: [{ t: 4.2, type: 'carillon2' }, { t: 12.4, type: 'carillon' }],
    html: `
      <svg class="lune" viewBox="-100 -100 200 200" data-a="draw" data-t0="0.2" data-d="2.4"><g>
        <path class="tr" pathLength="1" d="M30 -70 A 75 75 0 1 0 30 70 A 58 58 0 1 1 30 -70Z"/>
      </g></svg>
      <div class="centre">
        ${titre(0.8, 3.8, 'Avant de dormir,<br>pose ton cœur')}
        <div class="bloc" data-a="rise" data-t0="4.2" data-t1="11.8">
          <div class="ar arabe">أَلَا بِذِكْرِ ٱللَّهِ<br>تَطْمَئِنُّ ٱلْقُلُوبُ</div>
          ${sep(4.8, 11.8)}
          <p class="trad" data-a="fade" data-t0="5.6" data-t1="11.8">« N'est-ce point par l'évocation d'Allah que se tranquillisent les cœurs&nbsp;? »</p>
          <p class="ref" data-a="fade" data-t0="6.6" data-t1="11.8">Sourate Ar-Ra'd, 13:28</p>
          <p class="petit" data-a="fade" data-t0="8.6" data-t1="11.8">Dis Alhamdulillah pour une chose.<br>Et confie le reste à Allah.</p>
        </div>
      </div>
      ${marque(12.2)}`,
  },

  // R7 — l'offre
  offre: {
    duree: 17, fond: 'sombre', particules: 'petales', ambiance: 'jardin',
    sons: [{ t: 0.5, type: 'carillon2' }, { t: 9.6, type: 'carillon' }, { t: 10.6, type: 'carillon2' }],
    html: `
      <div class="centre">
        ${titre(0.3, 3.4, 'Tout ton jardin de foi,<br>dans ta poche')}
        <div class="bloc tel" data-a="rise" data-t0="3.6" data-t1="9.2">
          <svg class="cadre" viewBox="0 0 400 700" data-a="draw" data-t0="3.6" data-d="1.4"><g><rect class="tr" pathLength="1" x="10" y="10" width="380" height="680" rx="56"/><path class="tr" pathLength="1" d="M160 40 L240 40"/></g></svg>
          <div class="ecran">
            ${['Ma journée par prière', 'Jeûne', 'Carnet du soir', 'Glow up & habitudes', 'Défis & aumône', 'Thèmes de couleur'].map((x, i) => `
              <div class="it" data-a="rise" data-t0="${4.4 + i * 0.6}" data-d=".6"><svg viewBox="-26 -26 52 52"><g>${FL(18, 'trf')}</g></svg>${x}</div>`).join('')}
          </div>
        </div>
        <div class="bloc prix" data-a="pop" data-t0="9.4" data-t1="15.4">
          <div class="kicker2">Jusqu'au 30 novembre</div>
          <div class="ancien" data-a="strike" data-t0="9.9" data-d=".5"><span>7,90 €</span><i></i></div>
          <div class="nouveau" data-a="pop" data-t0="10.5">2,99 €</div>
          <p class="petit">Paiement unique · accès à vie<br>Coran &amp; Apprentissage : gratuits</p>
          <div class="cta">Lien en bio</div>
        </div>
      </div>`,
  },
};

// ——— Variantes : mêmes animations, nouveaux textes (semaines suivantes) ———
const varier = (base, remplacements, extra = {}) => {
  let html = SCENES[base].html;
  for (const [a, b] of remplacements) {
    if (!html.includes(a)) throw new Error(`Variante de ${base} : texte introuvable « ${a.slice(0, 40)} »`);
    html = html.split(a).join(b);
  }
  return { ...SCENES[base], ...extra, html };
};

export const VARIANTES = {
  istighfar: varier('pluie', [
    ['Un peu,<br>mais régulièrement', 'Et si tu disais<br>Astaghfirullah&nbsp;?'],
    ['أَحَبُّ الأَعْمَالِ إِلَى اللَّهِ<br>أَدْوَمُهَا وَإِنْ قَلَّ', 'ٱسْتَغْفِرُوا۟ رَبَّكُمْ<br>إِنَّهُۥ كَانَ غَفَّارًا'],
    ["« Les œuvres les plus aimées d'Allah sont les plus régulières, même si elles sont peu nombreuses. »", "« Implorez le pardon de votre Seigneur, car Il est grand Pardonneur, pour qu'Il vous envoie du ciel des pluies abondantes. »"],
    ['Al-Bukhari &amp; Muslim', 'Sourate Nuh, 71:10-11'],
    ['Comme la pluie, goutte après goutte,<br>qui fait pousser tout un jardin.', "L'istighfar, c'est la pluie<br>qui fait refleurir ton cœur."],
  ]),
  matin: varier('graines', [
    ['Débordée&nbsp;?', 'Ton matin,<br>en douceur'],
    ['3 petites graines', '3 sunan du matin'],
    ['1 verset par jour', 'Tes adhkar du matin'],
    ['1 invocation après chaque prière', '2 rak\'at de Duha'],
    ['1 bonne action discrète', 'Un sourire, c\'est une aumône'],
    ['Plante. Arrose.<br>Et laisse Allah faire pousser.', 'Une graine chaque matin,<br>un jardin chaque année.'],
  ]),
  tawakkul: varier('aube', [
    ['Ce que tu traverses<br>n\'est pas la fin<br>de ton histoire', 'Tu n\'as pas<br>à tout porter<br>seule'],
    ['فَإِنَّ مَعَ ٱلْعُسْرِ يُسْرًا<br>إِنَّ مَعَ ٱلْعُسْرِ يُسْرًا', 'وَمَن يَتَوَكَّلْ عَلَى ٱللَّهِ<br>فَهُوَ حَسْبُهُۥٓ'],
    ['« À côté de la difficulté est, certes, une facilité. À côté de la difficulté, certes, une facilité. »', '« Et quiconque place sa confiance en Allah, Il lui suffit. »'],
    ['Sourate Ash-Sharh, 94:5-6', 'Sourate At-Talaq, 65:3'],
    ['Allah l\'a dit deux fois.<br>Pour que ton cœur l\'entende bien.', 'Fais ta part,<br>puis confie le reste à Allah.'],
  ]),
  semaine: varier('jardin', [
    ['Et si chaque prière<br>faisait pousser<br>une fleur&nbsp;?', 'Chaque jour où tu<br>reviens à Allah<br>fait pousser une fleur'],
    ...[['Fajr', 'Lun'], ['Dhuhr', 'Mar'], ['Asr', 'Mer'], ['Maghrib', 'Jeu'], ['Isha', 'Ven']].map(([a, b]) => [`<div class="lbl">${a}</div>`, `<div class="lbl">${b}</div>`]),
    ['Ton jardin grandit avec toi, prière après prière.', 'Pas une semaine parfaite. Juste revenir, encore.'],
  ]),
  invocations: varier('jumua', [
    ['Ta checklist<br>du vendredi', 'Tes invocations<br>du vendredi'],
    ...[['Ghusl', 'Pour toi'], ['Sourate Al-Kahf', 'Pour ta famille'], ['Salawat sur le Prophète ﷺ', 'Pour la oumma'], ["Invocations, l'heure exaucée", 'Salawat sur le Prophète ﷺ']].map(([a, b]) => [`<span>${a}</span>`, `<span>${b}</span>`]),
    ['Qu\'Allah accepte tes invocations.', 'Il y a une heure où Allah exauce.'],
  ]),
  kursi: varier('nuit', [
    ['Avant de dormir,<br>pose ton cœur', 'Avant de dormir,<br>récite Ayat al-Kursi'],
    ['أَلَا بِذِكْرِ ٱللَّهِ<br>تَطْمَئِنُّ ٱلْقُلُوبُ', 'ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ<br>ٱلْحَىُّ ٱلْقَيُّومُ'],
    ["« N'est-ce point par l'évocation d'Allah que se tranquillisent les cœurs&nbsp;? »", '« Allah ! Point de divinité à part Lui, le Vivant, Celui qui subsiste par Lui-même. »'],
    ["Sourate Ar-Ra'd, 13:28", 'Sourate Al-Baqara, 2:255'],
    ['Dis Alhamdulillah pour une chose.<br>Et confie le reste à Allah.', "Un gardien d'Allah veille sur toi<br>jusqu'au matin (Al-Bukhari)."],
  ]),
  vendredi: varier('aube', [
    ['Ce que tu traverses<br>n\'est pas la fin<br>de ton histoire', 'Jumu\'a Mubarak<br>le meilleur<br>des jours'],
    ['فَإِنَّ مَعَ ٱلْعُسْرِ يُسْرًا<br>إِنَّ مَعَ ٱلْعُسْرِ يُسْرًا', 'خير يوم طلعت عليه الشمس<br>يوم الجمعة'],
    ['« À côté de la difficulté est, certes, une facilité. À côté de la difficulté, certes, une facilité. »', '« Le meilleur jour durant lequel le soleil se lève est le vendredi. C\'est en ce jour qu\'Âdam fut créé, qu\'il fut introduit au Paradis et qu\'il en fut exclu. »'],
    ['Sourate Ash-Sharh, 94:5-6', 'Rapporté par Muslim (854)'],
    ['Allah l\'a dit deux fois.<br>Pour que ton cœur l\'entende bien.', 'Multiplie les prières<br>sur le Prophète ﷺ aujourd\'hui.'],
  ]),
  offre2: varier('offre', [
    ['Tout ton jardin de foi,<br>dans ta poche', 'Plus que quelques jours<br>pour l\'offre de lancement'],
  ]),
};
