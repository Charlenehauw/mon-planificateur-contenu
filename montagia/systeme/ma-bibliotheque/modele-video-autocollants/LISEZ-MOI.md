# Modèle « explainer autocollants » (sans voix)
Fait pour Biz’ en poche by Charlène (26/10/2026), inspiré de `analyse-modele.md` (reel avec voix off et mascotte robot).
Choix de Charlène : pas de voix (les étiquettes de mots portent le texte), mascotte = un petit téléphone jaune avec des yeux,
couleurs de son identité (papier crème, noir, jaune doré #E8BD3C, Anton / Lato). Pas de musique.

Fabrication : un projet HyperFrames (hyperframes@0.8.96) avec dans `assets/` : gsap.min.js, fonts/Anton-Regular.ttf, sons/,
img/papier.jpg (fond papier généré avec numpy/Pillow), img/st-*.png (émojis autocollants : contour blanc + ombre, Pillow + NotoColorEmoji),
img/ecran-*.png (morceaux d'écrans de l'appli recadrés et agrandis x2,5). Puis :
  python3 generer.py <dossier du projet>   -> écrit compositions/*.html et index.html
Tout le texte, l'ordre des chapitres et les visuels sont dans la liste SCENES en bas de generer.py.
Bruitages (26/10) : « clic » sur chaque étiquette de mot, « pop » sur les mots forts et les autocollants, « choc » quand le ruban se colle, « whoosh » sur les envols, les feuilles et les changements de couleur, montée + impact sur l'accroche et « le plus fou », clic + ding sur « Abonnée ».
Version courte (< 20 s) : generer_court.py (5 chapitres, un mot toutes les 0,22 s), fichier biz-en-poche-autocollants-20s.mp4.
Rythme : un mot toutes les 0,30 s, un groupe reste 0,75 s après son dernier mot ; une feuille de papier balaie l'écran entre deux chapitres.
