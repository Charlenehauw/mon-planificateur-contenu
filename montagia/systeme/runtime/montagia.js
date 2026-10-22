/* Montag'IA, moteur d'effets.
 * Ce fichier ne se modifie jamais pendant un montage. Claude remplit seulement la fiche
 * (fiche.json) ; le compositeur la transforme en données (window.MONTAGIA) que ce moteur
 * anime toujours de la même façon. Même fiche, même vidéo.
 * Repère : 1080 x 1920. Zones : accroche 180-460, visage 460-1100, info 1100-1300,
 * sous-titres autour de style.position, zone interdite au texte sous 1536 et à droite de 960.
 * Format YouTube (D.format = "youtube") : repère 1920 x 1080, accroche en haut, cartes sur les côtés,
 * sous-titres en bas (posés par ffmpeg au rendu), panneau = la personne se range à droite.
 * Chaque position s'écrit V(valeur verticale, valeur paysage) : le vertical ne change jamais.
 */
function montagiaDemarrer() {
  var D = window.MONTAGIA;
  var S = D.style, C = S.couleurs, P = S.polices;
  var CLAIR = S.mode === "clair";
  var PAYSAGE = D.format === "youtube";
  function V(vertical, paysage) { return PAYSAGE ? paysage : vertical; }
  var W = V(1080, 1920), H = V(1920, 1080);
  var ST_Y = Math.round(S.sous_titres.position * H);   // les infos se placent au-dessus des sous-titres
  var FOND_PLEIN = CLAIR ? C.clair : C.sombre, TEXTE_PLEIN = CLAIR ? C.sombre : "#FFFFFF";
  (function () {
    var r = document.documentElement.style, T = S.sous_titres;
    r.setProperty("--accent", C.accent); r.setProperty("--clair", C.clair);
    r.setProperty("--sombre", C.sombre); r.setProperty("--mot-cle", T.couleur_mot_cle);
    var css = document.createElement("style");
    css.textContent = ".m-st{font-family:'" + T.police + "';font-weight:" + T.graisse + ";font-size:" + T.taille + "px;color:" + T.couleur + ";text-shadow:" + T.ombre + ";}";
    document.head.appendChild(css);
  })();
  var root = document.getElementById("root");
  var cam = document.getElementById("cam");
  var derriere = document.getElementById("derriere");
  var dessus = document.getElementById("dessus");
  var plein = document.getElementById("plein");
  var tl = gsap.timeline({ paused: true });
  var piste = 20;

  function el(tag, cls, parent, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    (parent || dessus).appendChild(e);
    return e;
  }
  function media(e, parent) {
    /* les vidéos sont déclarées dans la page par le compositeur (HyperFrames ne voit que celles-là) ;
       on les range simplement à leur place */
    var v = document.getElementById(e._v.shift());
    parent.appendChild(v);
    return v;
  }
  function montrer(e, debut, fin, entree, sortie) {
    tl.set(e, { autoAlpha: 0 }, 0);
    if (entree) tl.fromTo(e, entree[0], Object.assign({ autoAlpha: 1 }, entree[1]), debut);
    else tl.set(e, { autoAlpha: 1 }, debut);
    if (sortie) tl.to(e, Object.assign({ autoAlpha: 0 }, sortie), fin - (sortie.duration || 0));
    else tl.set(e, { autoAlpha: 0 }, fin);
  }
  function accent(t) { return String(t).replace(/ ([?!:;»])/g, "\u00a0$1").replace(/« /g, "«\u00a0").replace(/\*([^*]+)\*/g, '<em>$1</em>'); }
  function casse(t, mode) { return mode === "majuscules" ? String(t).toUpperCase() : t; }
  function ajuster(e, max) {
    var w = e.scrollWidth, fs = parseFloat(getComputedStyle(e).fontSize);
    if (w > max) e.style.fontSize = (fs * max / w).toFixed(1) + "px";
  }
  var ICONES = {
    ok: '<svg viewBox="0 0 34 34"><path d="M7 18 L14 25 L27 10" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    non: '<svg viewBox="0 0 34 34"><path d="M10 10 L24 24 M24 10 L10 24" stroke="#fff" stroke-width="5" stroke-linecap="round"/></svg>',
    etoile: '<svg viewBox="0 0 34 34"><path d="M17 4 L21 13 L30 14 L23 20 L25 29 L17 24 L9 29 L11 20 L4 14 L13 13 Z" fill="#fff"/></svg>',
    marque: '<svg viewBox="0 0 34 34"><path d="M9 5 h16 v24 l-8 -6 l-8 6 Z" fill="#fff"/></svg>',
    fleche: '<svg viewBox="0 0 34 34"><path d="M6 17 H26 M18 9 L26 17 L18 25" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  };

  /* ───────── caméra : cadrage de base ───────── */
  var base = D.cadrage || { x: 0, y: 0, echelle: 1 };
  tl.set(cam, { x: base.x, y: base.y, scale: base.echelle, transformOrigin: "0 0" }, 0);

  var E = {};

  /* 1. accroche : bloc fixe dès la première image, sans animation d'entrée */
  E.accroche = function (e) {
    var A = S.accroche;
    var b = el("div", "m-accroche", dessus, casse(accent(e.texte), S.sous_titres.casse));
    b.style.cssText += ";background:" + A.fond + ";color:" + A.couleur + ";font-family:'" + A.police + "';font-size:" + A.taille + "px;border-radius:" + A.rayon + "px;";
    tl.set(b, { autoAlpha: 1 }, 0);
    tl.to(b, { autoAlpha: 0, y: -20, duration: 0.25, ease: "power2.in" }, e.fin - 0.25);
  };

  /* 2. sous-titres (blocs calculés par le compositeur depuis les mots Whisper) */
  E.sous_titres = function (blocs) {
    var T = S.sous_titres;
    var hote = el("div", "m-st-hote", root);
    blocs.forEach(function (b, i) {
      var html = b.html;
      if (T.karaoke && b.mots) html = b.mots.map(function (m, j) { return '<span class="k' + (m.cle ? ' cle' : '') + '">' + m.w + '</span>'; }).join(" ");
      var d = el("div", "m-st", hote, casse(html, T.casse));
      if (T.karaoke && b.mots) d.querySelectorAll(".k").forEach(function (sp, j) {
        tl.set(sp, { color: T.couleur }, 0);
        tl.to(sp, { color: T.couleur_karaoke || C.accent, scale: 1.08, duration: 0.08 }, b.mots[j].s);
        tl.to(sp, { scale: 1, duration: 0.12 }, b.mots[j].s + 0.1);
      });
      d.style.top = Math.round(T.position * H) + "px";
      var anim = T.animation === "rebond"
        ? [{ autoAlpha: 0, scale: 0.6, y: 20 }, { scale: 1, y: 0, duration: 0.16, ease: "back.out(3)" }]
        : [{ autoAlpha: 0, scale: 0.92 }, { scale: 1, duration: 0.09, ease: "power2.out" }];
      montrer(d, b.s, b.e, anim, null);
    });
  };

  /* 3. carte mot : plein écran sombre, un mot géant qui se révèle dans un léger flou */
  E.carte_mot = function (e) {
    var c = el("div", "m-plein", plein);
    c.style.background = FOND_PLEIN;
    var m = el("div", "m-carte-mot", c, casse(accent(e.mot), S.sous_titres.casse) + '<em>.</em>');
    m.style.fontFamily = "'" + P.titre + "'"; m.style.color = TEXTE_PLEIN;
    montrer(c, e.debut, e.fin, [{ autoAlpha: 0 }, { duration: 0.08 }], { duration: 0.15 });
    tl.fromTo(m, { opacity: 0, scale: 1.18, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "power3.out" }, e.debut + 0.04);
    document.fonts.ready.then(function () { ajuster(m, V(960, 1760)); });
  };

  /* 4. carte titre cinéma (texte chromé, reflet qui traverse) */
  E.carte_titre = function (e) {
    var c = el("div", "m-plein m-tc", plein);
    if (e.fond === "video") c.style.background = "rgba(0,0,0,0.55)"; else c.style.background = "#050506";
    var p = e.petit ? el("div", "m-tc-petit", c, e.petit) : null;
    var g = el("div", "m-chrome", c, e.grand);
    g.style.fontSize = (e.taille || 120) + "px";
    var f = el("div", "m-flare", c);
    montrer(c, e.debut, e.fin, null, null);
    if (p) tl.fromTo(p, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: 0.35, ease: "power2.out" }, e.debut);
    tl.fromTo(g, { opacity: 0, scale: 1.2 }, { opacity: 1, scale: 1, duration: 0.35, ease: "power4.out" }, e.debut + (p ? 0.18 : 0));
    tl.fromTo(f, { x: V(40, 300), y: V(960, 540), opacity: 0 }, { x: V(900, 1560), opacity: 1, duration: Math.min(0.8, e.fin - e.debut), ease: "power1.inOut" }, e.debut + 0.1);
    document.fonts.ready.then(function () { ajuster(g, V(960, 1760)); });
  };

  /* 5. zoom : avancée caméra sur un point, maintien, retour */
  E.zoom = function (e) {
    var k = e.echelle || 1.25, fx = e.x != null ? e.x : V(540, 960), fy = e.y != null ? e.y : V(760, 420);
    var b = base.echelle;
    var cible = { scale: b * k, x: base.x + fx * b * (1 - k), y: base.y + fy * b * (1 - k) };
    var dur = Math.min(0.35, (e.fin - e.debut) / 3);
    tl.to(cam, Object.assign({ duration: e.doux ? 0.6 : dur, ease: e.doux ? "power1.inOut" : "power3.out" }, cible), e.debut);
    tl.to(cam, { scale: b, x: base.x, y: base.y, duration: dur, ease: "power2.inOut" }, e.fin - dur);
  };

  /* 6. B-roll : plein cadre (léger travelling) ou fenêtre arrondie en haut */
  E.broll = function (e) {
    var dur = e.fin - e.debut;
    if ((e.mode || "plein") === "plein") {
      var h = el("div", "m-plein m-broll", plein);
      var v = media(e, h);
      montrer(h, e.debut, e.fin, null, null);
      tl.fromTo(v, { scale: 1.0 }, { scale: 1.08, duration: dur, ease: "none" }, e.debut);
    } else {
      var f = el("div", "m-fenetre", dessus);
      media(e, f);
      montrer(f, e.debut, e.fin, [{ autoAlpha: 0, y: -60, scale: 0.92 }, { y: 0, scale: 1, duration: 0.35, ease: "back.out(1.4)" }], { y: -40, duration: 0.2 });
    }
  };

  /* 7. étiquettes : petites pastilles qui apparaissent une à une */
  E.etiquettes = function (e) {
    var hote = el("div", "m-etiq-hote", dessus);
    hote.style.top = (e.y || ST_Y - 130) + "px";
    var n = e.items.length;
    e.items.forEach(function (it, i) {
      var d = el("div", "m-etiq", hote, '<span class="ic" style="background:' + (it.icone === "non" ? "#D93A3A" : it.icone === "marque" ? C.accent : C.succes) + '">' + (ICONES[it.icone || "ok"] || ICONES.ok) + '</span><span>' + accent(it.texte) + '</span>');
      d.style.fontFamily = "'" + P.texte + "'";
      var t0 = it.debut != null ? it.debut : e.debut + i * Math.min(0.5, (e.fin - e.debut) / (n + 1));
      tl.fromTo(d, { autoAlpha: 0, y: 26, scale: 0.85 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(1.7)" }, t0);
    });
    tl.set(hote, { autoAlpha: 1 }, 0);
    tl.to(hote, { autoAlpha: 0, duration: 0.2 }, e.fin - 0.2);
  };

  /* 8. compteur : un chiffre qui défile jusqu'à sa valeur */
  E.compteur = function (e) {
    var c = el("div", "m-compteur", dessus);
    c.style.top = (e.y || V(ST_Y - 250, 330)) + "px";
    if (PAYSAGE) c.style.left = ((e.cote || "gauche") === "gauche" ? 70 : W - 70 - 620) + "px";
    var n = el("div", "m-cpt-n", c);
    n.style.fontFamily = "'" + P.fort + "'"; n.style.color = C.clair;
    var l = e.libelle ? el("div", "m-cpt-l", c, accent(e.libelle)) : null;
    var o = { v: e.de || 0 }, dec = e.decimales || 0;
    function maj() { n.innerHTML = (e.prefixe || "") + Number(o.v).toLocaleString("fr-FR", { minimumFractionDigits: dec, maximumFractionDigits: dec }) + '<em>' + (e.suffixe || "") + '</em>'; }
    maj();
    montrer(c, e.debut, e.fin, [{ autoAlpha: 0, y: 30 }, { y: 0, duration: 0.3, ease: "power3.out" }], { duration: 0.2 });
    tl.to(o, { v: e.a, duration: Math.min(1.4, (e.fin - e.debut) * 0.6), ease: "power2.out", onUpdate: maj }, e.debut + 0.1);
  };

  /* panneau : la personne se range dans un cadre en bas, le contenu se construit en haut */
  function panneau(e) {
    var dur = 0.55, b = base.echelle;
    tl.to(cam, { scale: b * 0.5, x: V(270, 900), y: V(900, 270), duration: dur, ease: "power3.inOut" }, e.debut);
    var cadre = el("div", "m-cadre" + (CLAIR ? " clair" : ""), root);
    montrer(cadre, e.debut + 0.3, e.fin, [{ autoAlpha: 0 }, { duration: 0.25 }], { duration: 0.2 });
    var fond = el("div", "m-plein m-expl-fond", document.getElementById("fond"));
    fond.style.background = CLAIR ? "radial-gradient(ellipse at 50% 25%, #FFFFFF 0%, " + C.clair + " 55%, #E9ECF2 100%)" : "radial-gradient(ellipse at 50% 20%, " + C.sombre + "EE 0%, #000000 80%)";
    montrer(fond, e.debut, e.fin, [{ autoAlpha: 0 }, { duration: 0.4 }], { duration: 0.3 });
    var p = el("div", "m-expl", root);
    p.style.fontFamily = "'" + P.texte + "'"; p.style.color = TEXTE_PLEIN;
    if (CLAIR) p.classList.add("clair");
    if (e.sur_titre) { var k1 = el("div", "m-expl-kick", p, e.sur_titre); k1.style.color = C.accent; }
    if (e.titre) { var t = el("div", "m-expl-titre", p, accent(e.titre)); t.style.fontFamily = "'" + P.titre + "'"; }
    montrer(p, e.debut + 0.2, e.fin, [{ autoAlpha: 0, y: 30 }, { y: 0, duration: 0.4, ease: "power3.out" }], { duration: 0.2 });
    tl.to(cam, { scale: b, x: base.x, y: base.y, duration: 0.5, ease: "power3.inOut" }, e.fin - 0.5);
    return p;
  }
  function svgEl(tag, attrs, parent) {
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }

  /* 9. cadre explicatif : étapes qui se cochent */
  E.cadre_explication = function (e) {
    var p = panneau(e);
    (e.items || []).forEach(function (it, i) {
      var s = el("div", "m-expl-item", p, '<span class="ck"><span class="fill" style="background:' + C.accent + '">' + ICONES.ok + '</span></span><span><small>' + String(i + 1).padStart(2, "0") + '</small><b>' + accent(it.texte) + '</b></span>');
      var t0 = it.debut != null ? it.debut : e.debut + 0.6 + i * 0.5;
      tl.fromTo(s, { autoAlpha: 0, x: 30 }, { autoAlpha: 1, x: 0, duration: 0.3 }, t0);
      tl.fromTo(s.querySelector(".fill"), { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }, t0 + 0.25);
    });
  };

  /* 22. diagramme de Venn : deux cercles qui se dessinent, le point commun apparaît au centre */
  E.venn = function (e) {
    var p = panneau(e);
    var svg = svgEl("svg", { viewBox: "0 0 900 560", class: "m-venn" }, p);
    var cx = [300, 600], noms = e.cercles || [{ texte: "A" }, { texte: "B" }];
    var cols = [C.accent, CLAIR ? C.sombre : "#FFFFFF"];
    noms.slice(0, 2).forEach(function (c, i) {
      var cir = svgEl("circle", { cx: cx[i], cy: 280, r: 230, fill: cols[i], "fill-opacity": 0, stroke: cols[i], "stroke-width": 6, pathLength: 1 }, svg);
      var t0 = c.debut != null ? c.debut : e.debut + 0.4 + i * 0.5;
      tl.fromTo(cir, { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut" }, t0);
      tl.to(cir, { attr: { "fill-opacity": 0.12 }, duration: 0.4 }, t0 + 0.5);
      var lab = svgEl("text", { x: i ? 720 : 180, y: 292, "text-anchor": "middle", class: "m-venn-txt" }, svg);
      lab.textContent = c.texte; lab.style.fill = TEXTE_PLEIN;
      tl.fromTo(lab, { opacity: 0 }, { opacity: 1, duration: 0.3 }, t0 + 0.4);
    });
    var com = svgEl("text", { x: 450, y: 292, "text-anchor": "middle", class: "m-venn-commun" }, svg);
    com.textContent = e.commun || ""; com.style.fill = C.accent;
    var tc = e.au != null ? e.au : e.debut + 1.6;
    tl.fromTo(com, { opacity: 0, scale: 0.4, transformOrigin: "450px 280px" }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2.2)" }, tc);
  };

  /* 23. feuille de route : le chemin se dessine et un repère avance d'étape en étape */
  E.feuille_route = function (e) {
    var p = panneau(e);
    var et = e.etapes || [];
    var n = Math.max(2, et.length);
    var svg = svgEl("svg", { viewBox: "0 0 900 600", class: "m-route" }, p);
    var pts = [];
    for (var i = 0; i < n; i++) pts.push([110 + (680 * i) / (n - 1), i % 2 ? 420 : 170]);
    var d = "M" + pts[0][0] + " " + pts[0][1];
    for (i = 1; i < n; i++) { var mx = (pts[i - 1][0] + pts[i][0]) / 2; d += " C" + mx + " " + pts[i - 1][1] + " " + mx + " " + pts[i][1] + " " + pts[i][0] + " " + pts[i][1]; }
    svgEl("path", { d: d, fill: "none", stroke: CLAIR ? "rgba(0,0,0,0.12)" : "rgba(255,255,255,0.18)", "stroke-width": 14, "stroke-linecap": "round" }, svg);
    var chemin = svgEl("path", { d: d, fill: "none", stroke: C.accent, "stroke-width": 14, "stroke-linecap": "round", pathLength: 1 }, svg);
    tl.set(chemin, { strokeDasharray: 1, strokeDashoffset: 1 }, 0);
    var mark = svgEl("circle", { cx: pts[0][0], cy: pts[0][1], r: 26, fill: C.accent, stroke: "#fff", "stroke-width": 7 }, svg);
    tl.set(mark, { opacity: 0 }, 0);
    tl.to(mark, { opacity: 1, duration: 0.2 }, e.debut + 0.4);
    et.forEach(function (s, i) {
      var t0 = s.debut != null ? s.debut : e.debut + 0.5 + i * ((e.fin - e.debut - 1) / n);
      var dot = svgEl("circle", { cx: pts[i][0], cy: pts[i][1], r: 18, fill: CLAIR ? "#FFFFFF" : C.sombre, stroke: C.accent, "stroke-width": 6 }, svg);
      var lab = svgEl("text", { x: pts[i][0], y: pts[i][1] + (i % 2 ? 78 : -48), "text-anchor": "middle", class: "m-route-txt" }, svg);
      lab.textContent = s.texte; lab.style.fill = TEXTE_PLEIN;
      tl.fromTo([dot, lab], { opacity: 0 }, { opacity: 1, duration: 0.3 }, e.debut + 0.3 + i * 0.12);
      tl.to(chemin, { strokeDashoffset: 1 - i / (n - 1), duration: 0.55, ease: "power2.inOut" }, t0);
      tl.to(mark, { attr: { cx: pts[i][0], cy: pts[i][1] }, duration: 0.55, ease: "power2.inOut" }, t0);
      tl.to(lab, { fill: C.accent, duration: 0.2 }, t0 + 0.4);
    });
  };

  /* 10. objet 3D : une image (logo, icône) en relief qui tourne, posée à un endroit, puis lancée vers la caméra */
  E.objet_3d = function (e) {
    var w = el("div", "m-o3d", dessus);
    var o = el("div", "m-o3d-in", w);
    var N = 14;
    for (var i = N - 1; i >= 0; i--) {
      var im = el("img", "", o);
      im.src = e.image;
      im.style.transform = "translateZ(" + (-i * 2.4) + "px)";
      im.style.filter = i === 0 ? "none" : "brightness(" + (0.82 - i * 0.012).toFixed(2) + ")";
    }
    var x = e.x != null ? e.x : V(540, 1500), y = e.y != null ? e.y : V(1150, 640), taille = e.taille || 260;
    w.style.width = w.style.height = taille + "px";
    tl.set(w, { x: x - taille / 2, y: y - taille / 2, autoAlpha: 0, scale: 0.2 }, 0);
    tl.to(w, { autoAlpha: 1, scale: 1, duration: 0.45, ease: "back.out(2)" }, e.debut);
    var fin_tour = e.lancer ? e.lancer : e.fin;
    tl.fromTo(o, { rotationY: -40, rotationX: 12 }, { rotationY: 520, rotationX: 12, duration: fin_tour - e.debut, ease: "none" }, e.debut);
    tl.to(w, { y: "-=18", duration: 0.9, yoyo: true, repeat: Math.max(0, Math.floor((fin_tour - e.debut) / 0.9) - 1), ease: "sine.inOut" }, e.debut + 0.45);
    if (e.lancer) {
      tl.to(o, { rotationY: 1080, rotationX: -8, duration: 0.9, ease: "power2.in" }, e.lancer);
      tl.to(w, { x: V(540, 960) - taille / 2, y: V(820, 420) - taille / 2, scale: 12, duration: 0.9, ease: "power3.in" }, e.lancer);
      tl.set(w, { autoAlpha: 0 }, e.lancer + 0.9);
    } else {
      tl.to(w, { autoAlpha: 0, scale: 0.6, duration: 0.25 }, e.fin - 0.25);
    }
  };

  /* 11. vitre brisée sur tout l'écran (motif déterministe) */
  E.vitre = function (e) {
    var cx = e.x != null ? e.x : V(540, 960), cy = e.y != null ? e.y : V(820, 420);
    var seed = 7; function r() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
    var NR = 16, ang = [], pts = [], radii = [46, 120, 250, 430, 700, 1100, 1500];
    for (var a = 0; a < NR; a++) ang.push((a / NR) * Math.PI * 2 + (r() - 0.5) * 0.28);
    for (a = 0; a < NR; a++) { var row = []; for (var k = 0; k < radii.length; k++) { var aa = ang[a] + (r() - 0.5) * 0.12, rr = radii[k] * (0.85 + r() * 0.3); row.push([cx + Math.cos(aa) * rr, cy + Math.sin(aa) * rr]); } pts.push(row); }
    var s = '<defs><filter id="m-glow"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><g class="lignes" filter="url(#m-glow)" stroke="#fff" stroke-linecap="round" fill="none">';
    for (a = 0; a < NR; a++) { var d = "M" + cx + " " + cy; pts[a].forEach(function (p) { d += " L" + p[0].toFixed(1) + " " + p[1].toFixed(1); }); s += '<path d="' + d + '" stroke-width="' + (2.6 - (a % 3) * 0.5) + '"/>'; }
    [0, 1, 2, 3].forEach(function (k) { for (var a = 0; a < NR; a++) { if ((a + k) % 3 === 2 && k > 0) continue; var p1 = pts[a][k], p2 = pts[(a + 1) % NR][k]; s += '<path d="M' + p1[0].toFixed(1) + ' ' + p1[1].toFixed(1) + ' Q' + ((p1[0] + p2[0]) / 2 + (r() - 0.5) * 18).toFixed(1) + ' ' + ((p1[1] + p2[1]) / 2 + (r() - 0.5) * 18).toFixed(1) + ' ' + p2[0].toFixed(1) + ' ' + p2[1].toFixed(1) + '" stroke-width="1.6" opacity="0.85"/>'; } });
    s += '</g><circle cx="' + cx + '" cy="' + cy + '" r="16" fill="rgba(255,255,255,0.85)" filter="url(#m-glow)"/><g>';
    for (a = 0; a < NR; a++) { var a1 = pts[a][1], a2 = pts[a][2], b1 = pts[(a + 1) % NR][1], b2 = pts[(a + 1) % NR][2]; s += '<path class="eclat" d="M' + a1.join(" ") + ' L' + a2.join(" ") + ' L' + b2.join(" ") + ' L' + b1.join(" ") + ' Z" fill="rgba(255,255,255,0.07)" stroke="#fff" stroke-width="1.6" style="transform-box:fill-box;transform-origin:50% 50%"/>'; }
    s += '</g>';
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("class", "m-vitre"); svg.innerHTML = s;
    root.appendChild(svg);
    var fl = el("div", "m-flash", root);
    var t = e.debut, f = e.fin || t + 2.4;
    tl.set(svg, { autoAlpha: 0 }, 0); tl.set(svg, { autoAlpha: 1 }, t);
    tl.fromTo(svg.querySelectorAll(".lignes path"), { strokeDasharray: 1600, strokeDashoffset: 1600 }, { strokeDashoffset: 0, duration: 0.22, ease: "power3.out", stagger: 0.004 }, t);
    tl.fromTo(fl, { opacity: 0.85 }, { opacity: 0, duration: 0.25, ease: "power2.out", immediateRender: false }, t);
    tl.set(fl, { opacity: 0 }, 0);
    tl.fromTo(cam, { x: base.x - 14 }, { x: base.x, duration: 0.35, ease: "elastic.out(1, 0.3)", immediateRender: false }, t);
    var chute = Math.min(1.1, (f - t) * 0.6);
    tl.to(svg.querySelector(".lignes"), { opacity: 0, duration: chute * 0.5 }, f - chute);
    svg.querySelectorAll(".eclat").forEach(function (sh, i) { tl.to(sh, { y: 900 + (i % 4) * 160, rotation: (i % 2 ? 1 : -1) * (40 + i * 7), opacity: 0, duration: chute, ease: "power2.in" }, f - chute - 0.1 + (i % 5) * 0.02); });
    tl.set(svg, { autoAlpha: 0 }, f);
  };

  /* 12. téléphones qui flottent en 3D (derrière la personne si le détourage existe) */
  E.telephones = function (e) {
    var hote = el("div", "m-phones", D.detourage ? derriere : dessus);
    var POS = V([{ x: -40, y: 300, ry: 26, rz: -7, z: -60 }, { x: 790, y: 300, ry: -26, rz: 7, z: -60 }, { x: 10, y: 820, ry: 18, rz: 4, z: -140 }, { x: 740, y: 820, ry: -18, rz: -4, z: -140 }, { x: 410, y: 160, ry: 6, rz: -3, z: -260 }],
      [{ x: 60, y: 120, ry: 26, rz: -7, z: -60 }, { x: 1610, y: 120, ry: -26, rz: 7, z: -60 }, { x: 330, y: 520, ry: 18, rz: 4, z: -140 }, { x: 1340, y: 520, ry: -18, rz: -4, z: -140 }, { x: 835, y: 40, ry: 6, rz: -3, z: -260 }]);
    (e.videos || []).slice(0, 5).forEach(function (src, i) {
      var p = POS[i], d = el("div", "m-ph", hote);
      d.style.left = p.x + "px"; d.style.top = p.y + "px";
      if (/\.(png|jpe?g|webp)$/i.test(src)) { var im = el("img", "", d); im.src = src; }
      else media(e, d);
      var t0 = e.debut + i * 0.12;
      tl.set(d, { autoAlpha: 0 }, 0);
      tl.fromTo(d, { autoAlpha: 0, x: p.x < W / 2 - 40 ? -120 : 120, y: 60, z: -500, rotationY: p.ry * 2, rotation: p.rz, scale: 0.6 }, { autoAlpha: 1, x: 0, y: 0, z: p.z, rotationY: p.ry, rotation: p.rz, scale: 1, duration: 0.7, ease: "power3.out" }, t0);
      tl.to(d, { y: i % 2 ? 16 : -16, duration: 1.0, ease: "sine.inOut", yoyo: true, repeat: Math.max(0, Math.floor((e.fin - t0 - 1.2) / 1.0)) }, t0 + 0.7);
      tl.to(d, { autoAlpha: 0, z: -600, duration: 0.35, ease: "power2.in" }, e.fin - 0.35);
    });
  };

  /* 13. texte derrière la personne (demande le détourage) */
  E.texte_derriere = function (e) {
    var b = el("div", "m-derriere", D.detourage ? derriere : dessus);
    b.style.top = (e.y || V(560, 180)) + "px";
    var p = e.petit ? el("div", "m-tc-petit", b, e.petit) : null;
    var g = el("div", "m-chrome", b, e.grand); g.style.fontSize = (e.taille || 150) + "px";
    if (CLAIR) { g.classList.add("plein-couleur"); g.style.color = C.sombre; if (p) p.style.color = C.accent; }
    montrer(b, e.debut, e.fin, [{ autoAlpha: 0, y: 40 }, { y: 0, duration: 0.5, ease: "power3.out" }], { duration: 0.25 });
    document.fonts.ready.then(function () { ajuster(g, W - 80); });
  };

  /* 14. carte documentaire : fond papier, cercle de couleur, portrait détouré noir et blanc, phrases chocs */
  E.documentaire = function (e) {
    var c = el("div", "m-plein m-doc", plein);
    var sun = el("div", "m-doc-sun", c); sun.style.background = e.couleur || "#F5D400";
    if (D.detourage) {
      var cut = el("div", "m-doc-cut", c);
      var w = el("div", "m-doc-monde", cut);
      media(e, w);
      w.style.transform = "translate(" + (base.x + V(0, 77)) + "px," + (base.y + V(120, 80)) + "px) scale(" + base.echelle * 0.92 + ")";
    }
    var nom = el("div", "m-doc-nom", c, e.nom);
    var tag = e.etiquette ? el("div", "m-doc-tag", c, e.etiquette) : null;
    if (tag) tag.style.background = e.couleur || "#F5D400";
    montrer(c, e.debut, e.fin, null, { duration: 0.2 });
    tl.fromTo(sun, { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.6)" }, e.debut);
    tl.fromTo(nom, { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }, e.debut + 0.25);
    var ph = e.phrases || [];
    ph.forEach(function (t, i) {
      var s = el("div", "m-doc-stk", c, t);
      s.style.top = (V(300, 170) + i * 120) + "px"; s.style.left = (V(560, 1260) - (i % 2) * 40) + "px";
      var t0 = ph.length && e.fin - e.debut > 2 ? e.debut + 0.9 + i * 0.42 : e.debut + 0.5 + i * 0.3;
      tl.fromTo(s, { opacity: 0, scale: 1.4, rotation: i % 2 ? 5 : -6 }, { opacity: 1, scale: 1, rotation: i % 2 ? 1.5 : -2, duration: 0.22, ease: "power4.out" }, t0);
    });
    if (tag) tl.fromTo(tag, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.25 }, e.debut + 0.9 + ph.length * 0.42);
  };

  /* 15. CTA commentaire : pastille façon Instagram, le mot-clé se tape lettre par lettre */
  E.cta_commentaire = function (e) {
    var c = el("div", "m-cta", dessus);
    c.style.top = (e.y || V(1240, 690)) + "px";
    var k = el("div", "m-cta-kick", c, e.kicker || "COMMENTE");
    k.style.fontFamily = "'" + P.texte + "'";
    var pill = el("div", "m-cta-pill", c);
    el("div", "m-cta-av", pill, "toi").style.background = C.sombre;
    var tx = el("div", "m-cta-txt", pill, String(e.mot).split("").map(function (ch) { return '<span class="ch">' + ch + '</span>'; }).join(""));
    tx.style.color = C.sombre; tx.style.fontFamily = "'" + P.texte + "'";
    var cur = el("div", "m-cta-cur", pill); cur.style.background = C.accent;
    var send = el("div", "m-cta-send", pill, '<svg width="70" height="70" viewBox="0 0 70 70"><circle cx="35" cy="35" r="35" fill="' + C.accent + '"/><path d="M20 35 L50 21 L41 49 L34 38 Z" fill="#fff"/></svg>');
    montrer(c, e.debut, e.fin, null, { duration: 0.2 });
    tl.fromTo(k, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, e.debut);
    tl.fromTo(pill, { opacity: 0, y: 90 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, e.debut + 0.12);
    tl.fromTo(tx.querySelectorAll(".ch"), { opacity: 0 }, { opacity: 1, duration: 0.01, stagger: 0.09 }, e.debut + 0.45);
    tl.to(cur, { opacity: 0, duration: 0.18, repeat: 5, yoyo: true }, e.debut + 0.45);
    tl.fromTo(send, { scale: 1 }, { scale: 1.18, duration: 0.14, yoyo: true, repeat: 3, ease: "power2.inOut" }, e.debut + 0.5 + String(e.mot).length * 0.09);
  };

  /* 16. image : visuel qui apparaît (couverture de guide, capture, produit) avec un zoom lent */
  E.image = function (e) {
    var c = el("div", "m-image", dessus);
    var lg = e.largeur || V(520, 600);
    c.style.width = lg + "px";
    c.style.left = (PAYSAGE ? ((e.cote || "droite") === "gauche" ? 70 : W - 70 - lg) : 540 - lg / 2) + "px";
    c.style.top = (e.y || V(1080, 120)) + "px";
    var im = el("img", "", c); im.src = e.fichier;
    montrer(c, e.debut, e.fin, [{ autoAlpha: 0, y: 60, rotation: -4, scale: 0.9 }, { y: 0, rotation: 0, scale: 1, duration: 0.45, ease: "back.out(1.5)" }], { y: 40, duration: 0.2 });
    tl.to(c, { scale: 1.05, duration: Math.max(0.5, e.fin - e.debut - 0.8), ease: "sine.inOut" }, e.debut + 0.45);
  };

  /* 17. flash : transition blanche franche */
  E.flash = function (e) {
    var f = el("div", "m-flash", root);
    tl.set(f, { opacity: 0 }, 0);
    tl.fromTo(f, { opacity: 0.9 }, { opacity: 0, duration: e.duree || 0.3, ease: "power2.out", immediateRender: false }, e.debut);
  };


  /* 18. icônes : 1 à 3 logos d'applis qui apparaissent au-dessus de la tête, avec leur nom */
  E.icones = function (e) {
    var hote = el("div", "m-icones", dessus);
    hote.style.top = (e.y || V(230, 60)) + "px";
    (e.items || []).forEach(function (it, i) {
      var d = el("div", "m-icone", hote, '<img src="' + it.image + '"/>' + (it.nom ? '<span>' + it.nom + '</span>' : ''));
      d.style.fontFamily = "'" + P.texte + "'";
      if (it.barre) el("div", "m-icone-barre", d);
      var t0 = it.debut != null ? it.debut : e.debut + i * 0.25;
      tl.fromTo(d, { autoAlpha: 0, scale: 0.3, y: 30 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(2.2)" }, t0);
      if (it.barre) tl.fromTo(d.querySelector(".m-icone-barre"), { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: "power2.out" }, it.barre === true ? t0 + 0.6 : it.barre);
    });
    tl.set(hote, { autoAlpha: 1 }, 0);
    tl.to(hote, { autoAlpha: 0, y: -20, duration: 0.25 }, e.fin - 0.25);
  };

  /* 19. fenêtre d'application : une carte façon ordinateur (titre + capture) qui s'ouvre au-dessus de la tête */
  E.fenetre_app = function (e) {
    var w = el("div", "m-app", dessus);
    w.style.top = (e.y || V(210, 110)) + "px";
    if (PAYSAGE && e.cote === "gauche") w.style.left = "70px";
    var barre = el("div", "m-app-barre", w, '<i style="background:#FF5F57"></i><i style="background:#FEBC2E"></i><i style="background:#28C840"></i><span>' + (e.titre || "") + '</span>');
    barre.style.fontFamily = "'" + P.texte + "'";
    var corps = el("div", "m-app-corps", w);
    if (e.image) { var im = el("img", "", corps); im.src = e.image; }
    if (e.texte) { var t = el("div", "m-app-texte", corps, accent(e.texte)); t.style.fontFamily = "'" + P.titre + "'"; }
    montrer(w, e.debut, e.fin, [{ autoAlpha: 0, scaleY: 0.05, scaleX: 0.6, transformOrigin: "50% 0%" }, { scaleY: 1, scaleX: 1, duration: 0.42, ease: "expo.out" }], { scaleY: 0.05, duration: 0.2 });
  };


  /* 20. illustration : carte animée sur le côté (icône qui se dessine, chiffre qui compte, ou transformation) */
  function carteIllus(parent, contenu) {
    var c = el("div", "m-illus-carte", parent);
    if (contenu.chiffre != null) {
      var n = el("div", "m-illus-chiffre", c); n.style.fontFamily = "'" + P.fort + "'"; n.style.color = C.accent;
      c._chiffre = n;
    } else if (contenu.icone) {
      var ic = el("div", "m-illus-ic", c, contenu.icone);
      ic.querySelectorAll("path,line,circle,rect,polyline,polygon,ellipse").forEach(function (p) { p.setAttribute("pathLength", "1"); });
      ic.style.color = C.accent;
    }
    if (contenu.texte) { var t = el("div", "m-illus-txt", c, accent(contenu.texte)); t.style.fontFamily = "'" + P.texte + "'"; }
    if (contenu.sous_texte) el("div", "m-illus-sous", c, contenu.sous_texte);
    return c;
  }
  E.illustration = function (e) {
    var gauche = (e.cote || "gauche") === "gauche";
    var hote = el("div", "m-illus " + (gauche ? "g" : "d"), dessus);
    hote.style.top = (e.y || V(640, 250)) + "px";
    var c = carteIllus(hote, e);
    var sens = gauche ? -1 : 1;
    tl.set(hote, { autoAlpha: 0 }, 0);
    tl.fromTo(hote, { autoAlpha: 0, x: sens * 360, rotationY: sens * -38, scale: 0.82 },
      { autoAlpha: 1, x: 0, rotationY: sens * -8, scale: 1, duration: 0.6, ease: "back.out(1.5)" }, e.debut);
    var traits = c.querySelectorAll(".m-illus-ic [pathLength]");
    if (traits.length) tl.fromTo(traits, { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut", stagger: 0.06 }, e.debut + 0.15);
    if (c._chiffre) {
      var o = { v: e.de || 0 }, dec = e.decimales || 0;
      var maj = function () { c._chiffre.textContent = (e.prefixe || "") + Number(o.v).toLocaleString("fr-FR", { minimumFractionDigits: dec, maximumFractionDigits: dec }) + (e.suffixe || ""); };
      maj();
      tl.to(o, { v: e.chiffre, duration: Math.min(1.2, (e.fin - e.debut) * 0.5), ease: "power2.out", onUpdate: maj }, e.debut + 0.2);
    }
    var tx = c.querySelector(".m-illus-txt");
    if (tx) tl.fromTo(tx, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, e.debut + 0.35);
    var dur = e.fin - e.debut;
    tl.fromTo(hote, { y: 0 }, { y: -14, duration: Math.max(0.6, dur / 2 - 0.4), ease: "sine.inOut", yoyo: true, repeat: 1, immediateRender: false }, e.debut + 0.6);
    if (e.vers) {
      var c2 = carteIllus(hote, e.vers);
      c2.classList.add("dos");
      var t = e.au || (e.debut + dur / 2);
      tl.set(c2, { autoAlpha: 0, rotationY: -90 }, 0);
      tl.to(c, { rotationY: 90, duration: 0.25, ease: "power2.in" }, t);
      tl.set(c, { autoAlpha: 0 }, t + 0.25);
      tl.set(c2, { autoAlpha: 1 }, t + 0.25);
      tl.to(c2, { rotationY: 0, duration: 0.35, ease: "back.out(1.6)" }, t + 0.25);
      var tr2 = c2.querySelectorAll(".m-illus-ic [pathLength]");
      if (tr2.length) tl.fromTo(tr2, { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.6, ease: "power2.inOut", stagger: 0.05 }, t + 0.3);
    }
    tl.to(hote, { autoAlpha: 0, x: sens * 300, rotationY: sens * -30, scale: 0.9, duration: 0.35, ease: "power2.in" }, e.fin - 0.35);
  };

  /* 21. rythme : léger recadrage franc à chaque nouvelle phrase (calculé par le compositeur) */
  E.recadrage = function (e) {
    var k = e.echelle || 1, b = base.echelle, fx = e.x != null ? e.x : V(540, 960), fy = e.y != null ? e.y : V(760, 420);
    tl.set(cam, { scale: b * k, x: base.x + fx * b * (1 - k), y: base.y + fy * b * (1 - k) }, e.debut);
  };


  /* 24. comparaison : deux cartes de part et d'autre, un VS au-dessus */
  E.comparaison = function (e) {
    E.illustration(Object.assign({}, e.gauche, { type: "illustration", cote: "gauche", debut: e.debut, fin: e.fin, y: e.y || V(620, 260) }));
    E.illustration(Object.assign({}, e.droite, { type: "illustration", cote: "droite", debut: e.debut + 0.25, fin: e.fin, y: e.y || V(620, 260) }));
    var vs = el("div", "m-vs", dessus, e.vs || "VS");
    vs.style.top = (e.y_vs || V(330, 70)) + "px"; vs.style.background = C.accent; vs.style.fontFamily = "'" + P.fort + "'";
    montrer(vs, e.debut + 0.45, e.fin, [{ autoAlpha: 0, scale: 0.2, rotation: -25 }, { scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2.6)" }], { scale: 0.4, duration: 0.2 });
  };

  /* 25. mini-moi en pixel art qui traverse l'écran */
  E.pixel_art = function (e) {
    var sp = el("img", "m-pixel", dessus); sp.src = e.image;
    var dur = e.fin - e.debut, y = e.y || V(1000, 620);
    tl.set(sp, { autoAlpha: 0, x: -320, y: y }, 0);
    tl.set(sp, { autoAlpha: 1 }, e.debut);
    tl.to(sp, { x: W + 20, duration: dur, ease: "none" }, e.debut);
    var pas = Math.max(2, Math.floor(dur / 0.32));
    tl.to(sp, { y: y - 34, duration: 0.16, ease: "steps(2)", yoyo: true, repeat: pas * 2 - 1 }, e.debut);
    tl.set(sp, { autoAlpha: 0 }, e.fin);
  };


  /* 27. chapitre : titre de partie. « plein » = carte aux couleurs de la charte qui balaie l'écran,
     « bandeau » = cartouche en haut à gauche, la personne reste visible. */
  E.chapitre = function (e) {
    var num = e.numero != null ? (typeof e.numero === "number" ? "Partie " + e.numero : e.numero) : "";
    if (e.mode === "bandeau") {
      var b = el("div", "m-chap-bandeau", dessus);
      b.style.background = C.clair; b.style.color = C.sombre; b.style.fontFamily = "'" + P.texte + "'";
      if (num) { var n0 = el("div", "m-chap-num", b, num); n0.style.color = C.accent; }
      var t0 = el("div", "m-chap-titre", b, accent(e.titre || "")); t0.style.fontFamily = "'" + P.titre + "'";
      montrer(b, e.debut, e.fin, [{ autoAlpha: 0, x: -80 }, { x: 0, duration: 0.55, ease: "power3.out" }], { x: -40, duration: 0.3 });
      return;
    }
    /* pas de clip-path : le rendu image par image ne le capture pas. Le fond balaie en scaleX. */
    var c = el("div", "m-plein m-chap", plein);
    var fond = el("div", "m-chap-fond", c); fond.style.background = FOND_PLEIN;
    var ct = el("div", "m-chap-contenu", c); ct.style.color = TEXTE_PLEIN; ct.style.fontFamily = "'" + P.texte + "'";
    var n = num ? el("div", "m-chap-num", ct, num) : null;
    if (n) n.style.color = C.accent;
    var t = el("div", "m-chap-titre", ct, accent(e.titre || "")); t.style.fontFamily = "'" + P.titre + "'";
    var tr = el("div", "m-chap-trait", ct); tr.style.background = C.accent;
    tl.set(c, { autoAlpha: 0 }, 0);
    tl.set(c, { autoAlpha: 1 }, e.debut);
    tl.set(fond, { transformOrigin: "0% 50%", scaleX: 0 }, 0);
    tl.to(fond, { scaleX: 1, duration: 0.45, ease: "power3.inOut" }, e.debut);
    if (n) tl.fromTo(n, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, e.debut + 0.25);
    tl.fromTo(t, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, e.debut + 0.32);
    tl.fromTo(tr, { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.inOut" }, e.debut + 0.5);
    tl.to(ct, { autoAlpha: 0, duration: 0.2 }, e.fin - 0.45);
    tl.set(fond, { transformOrigin: "100% 50%" }, e.fin - 0.4);
    tl.to(fond, { scaleX: 0, duration: 0.4, ease: "power3.inOut" }, e.fin - 0.4);
    tl.set(c, { autoAlpha: 0 }, e.fin);
  };

  /* 26. sur mesure : effet créé par Claude pour cette vidéo, dans la charte (couleurs, polices, mouvements maison, zones) */
  var ZONES = V({
    gauche: { left: 22, top: 560, width: 288, height: 620 }, droite: { left: 770, top: 560, width: 288, height: 620 },
    haut: { left: 60, top: 170, width: 960, height: 380 }, centre_bas: { left: 90, top: 1060, width: 900, height: 300 },
    plein: { left: 0, top: 0, width: 1080, height: 1920 }
  }, {
    gauche: { left: 70, top: 160, width: 380, height: 660 }, droite: { left: 1470, top: 160, width: 380, height: 660 },
    haut: { left: 360, top: 50, width: 1200, height: 280 }, centre_bas: { left: 360, top: 600, width: 1200, height: 260 },
    plein: { left: 0, top: 0, width: 1920, height: 1080 }
  });
  E.sur_mesure = function (e) {
    var fab = (window.MONTAGIA_SUR_MESURE || {})[e.nom];
    if (!fab) { console.warn("effet sur mesure introuvable", e.nom); return; }
    var zone;
    if (e.zone === "panneau") {
      zone = panneau(e);
    } else {
      var z = ZONES[e.zone || "haut"];
      zone = el("div", "m-sm m-sm-" + (e.zone || "haut"), e.zone === "plein" ? plein : dessus);
      zone.style.cssText += ";left:" + z.left + "px;top:" + z.top + "px;width:" + z.width + "px;height:" + z.height + "px;";
      if (e.zone === "plein") zone.style.background = FOND_PLEIN;
      montrer(zone, e.debut, e.fin, null, null);
    }
    var ctx = {
      tl: tl, zone: zone, debut: e.debut, fin: e.fin, reperes: e.reperes || {}, donnees: e.donnees || {},
      couleurs: { accent: C.accent, clair: C.clair, sombre: C.sombre, texte: TEXTE_PLEIN, fond: FOND_PLEIN }, polices: P, clair: CLAIR,
      largeur: W, hauteur: H, paysage: PAYSAGE,
      el: function (tag, cls, parent, html) { return el(tag, cls, parent || zone, html); },
      svg: function (tag, attrs, parent) { return svgEl(tag, attrs, parent); },
      accent: accent, icones: e.icones || {},
      carte: function (parent) { return el("div", "m-illus-carte", parent || zone); },
      entree: function (cible, t) { tl.fromTo(cible, { autoAlpha: 0, y: 40, scale: 0.9 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(1.5)" }, t != null ? t : e.debut); },
      sortie: function (cible, t) { tl.to(cible, { autoAlpha: 0, y: 30, scale: 0.92, duration: 0.35, ease: "power2.in" }, t != null ? t : e.fin - 0.35); },
      dessiner: function (cible, t, d) {
        var tr = (cible.querySelectorAll ? cible.querySelectorAll("path,line,circle,rect,polyline,polygon,ellipse") : [cible]);
        tr.forEach(function (p) { p.setAttribute("pathLength", "1"); });
        tl.fromTo(tr, { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: d || 0.7, ease: "power2.inOut", stagger: 0.05 }, t != null ? t : e.debut);
      }
    };
    fab(ctx);
  };

  /* ───────── assemblage ───────── */
  if (D.sous_titres && D.sous_titres.length) E.sous_titres(D.sous_titres);
  (D.effets || []).forEach(function (e) {
    if (!E[e.type]) { console.warn("effet inconnu", e.type); return; }
    E[e.type](e);
  });
  window.__timelines = window.__timelines || {};
  window.__timelines["montagia"] = tl;
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", montagiaDemarrer);
else montagiaDemarrer();
