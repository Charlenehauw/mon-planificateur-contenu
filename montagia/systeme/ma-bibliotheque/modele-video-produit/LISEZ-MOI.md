# Modèle « vidéo produit » (motion design, sans face caméra)
Fait pour « Coach Chachou, ton coach dans la poche » (appli en artefact Claude, 23/10/2026 ; pas de logo, pas de musique, Charlène n'apparaît pas), inspiré de `analyse-modele.md`. Outil : HyperFrames (hyperframes@0.8.96).
Pour un nouveau produit : `npx hyperframes@0.8.96 init video` dans le projet, copier `index.html` et `compositions/` ici,
mettre les visuels dans `video/assets/` (img/, video/ recadrées sans les barres du navigateur et accélérées, fonts/Anton-Regular.ttf,
gsap.min.js depuis systeme/runtime, sons/ depuis systeme/assets/sons), changer les textes, puis `check`, `snapshot`, `render`.
Tous les écrans sont dans un téléphone (cadre noir + îlot ; contenu décalé de 56 px sous l'îlot).
Scènes : intro (titre qui se construit) → tableau (téléphone qui bascule en 3D + 4 mots-clés) → objectif (plongée dans l'écran, visite de l'appli)
→ outils (4 outils qui s'allument en or, le téléphone reste en place) → messages et plan (téléphone + enregistrement d'écran) → semaine (cases cochées) → fin (REJOINS + LIEN EN BIO).
Émojis (PNG faits avec Pillow, assets/img/emoji-*.png) qui surgissent dans les espaces vides à gauche et à droite du téléphone, un « pop » chacun.
Pas de musique dans le fichier : Charlène ajoute un son tendance dans TikTok / Instagram. Bruitages Montag'IA sur chaque action.

Version du 23/10/2026 (« espace complet ») : 12 scènes, 48,6 s. Après messages et plan 30 jours, l'enregistrement complet de l'appli
(exemple « Léa », 384 x 848) est découpé en séquences : prospects (« TON BUSINESS STRUCTURÉ. »), clientes & ventes, réseaux,
motivation, victoires. Découpe : crop=384:724:0:124 (sans la barre du haut), agrandi en 720 de large (lanczos + netteté légère),
vitesse ajustée pour remplir chaque scène. La scène « semaine » a été retirée (le mini plan apparaît dans « une vision claire »).

Version du 24/10/2026 : produit renommé « Biz’ en poche by Charlène » (intro et écran final). Fichier : produit-biz-en-poche.mp4.

Version du 24/10/2026 (mise à jour appli) : 15 scènes, 60,4 s. Nouvelles scènes : guide (visite au démarrage, entrée par la plongée),
commissions (affiliation), perso (« TON APP, TES COULEURS », changement d'ambiance accéléré x2,6, dernière scène avant la fin).
Source : enregistrement 384 x 848 de 42 s, même découpe crop=384:724:0:124.
