# Reels motion design (sans visage)

## Scènes disponibles (le « moteur »)
- **ACCROCHE** : grosse phrase, mots qui apparaissent un par un (1 à 3 mots en italique couleur accent).
- **PHRASE** : émoji + phrase + sous-texte.
- **POINT** : numéro + émoji + phrase courte + sous-texte.
- **LISTE** : titre + 2 à 4 éléments qui arrivent l'un après l'autre, avec icônes.
- **AVANT / APRÈS** : un mot barré, remplacé par un autre (ex. 1 JOUR → 1 HEURE).
- **COMPTEUR / COMPTE À REBOURS** : chiffre qui défile (chiffres vrais uniquement).
- **MAQUETTE DE TÉLÉPHONE** : une app ou un message qui défile.
- **APPEL À L'ACTION** : mot-clé dans un gros bouton, prix si connu.

## Règles de fabrication
- 9:16, 1080×1920, 30 à 35 s, 5 à 8 scènes, 2,8 à 6 s par scène selon la quantité de texte.
- Charte du brief : fond, couleur de texte, accent en dégradé pour les mots en italique, police titres très grasse en capitales.
- Petit « zoom punch » à chaque nouvelle scène, barre de progression en haut, nom de la marque discret.
- **Bruitages uniquement** dans la vidéo (whoosh aux transitions, pop sur les apparitions, tic sur les compteurs, ding sur le CTA). La musique s'ajoute à la programmation (module `programmation-metricool`).
- Aucune ligne de texte ne doit sortir de l'écran ni être coupée : vérifie chaque scène.

## Production
1. Pars du planning validé (module `planning-semaine`) ou d'une idée.
2. Écris chaque reel sous forme de liste de scènes (type, texte, durée) et fais valider.
3. Si l'exécution de code est disponible : génère les images (HTML + navigateur sans tête, ou Python/Pillow), assemble en MP4 avec ffmpeg, mixe les bruitages synthétisés. Fais d'abord une **planche contact** (une image par reel) avant le rendu final.
4. Nomme les fichiers `R01_AAAA-MM-JJ_HHhMM_titre.mp4` et livre un zip + un fichier de légendes (module `legendes`).
5. Sinon, livre le storyboard scène par scène pour qu'elle le monte dans son application.

## Corrections
« Le reel 3 : le texte dépasse / c'est trop rapide / autre accroche » → corrige uniquement ce reel et renvoie-le.
