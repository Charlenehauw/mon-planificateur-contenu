---
name: mon-style
description: Mon style à moi, dans Montag'IA. S'active quand la personne veut que ses vidéos soient montées dans SON style (son framework, sa façon de monter), dit « analyse ce style », « monte comme cette vidéo », « voici mon modèle », « refais ce montage », colle un lien de vidéo modèle, ou dépose une vidéo dans « Vidéos à monter/Modèle ». Analyse la vidéo modèle, écrit le style dans systeme/mon-framework.md, puis la skill montage-ia l'applique à chaque montage.
---

# Mon style à moi

**Avant tout** : si `systeme/ma-charte.json` n'existe pas ou n'a pas la clé `style`, fais d'abord l'accueil de la skill `montage-ia` (section 0 bis :
les deux premières vidéos servent à caler le style, puis le questionnaire couleurs, police, ambiance). Ensuite seulement, le modèle.

**D'abord, une question.** Si la personne veut LE MÊME montage que la vidéo modèle (« exactement pareil », « mêmes couleurs,
mêmes animations », « refais ce montage sur ma vidéo »), ce n'est pas cette skill : c'est la **réplique d'un reel de référence**,
section 3 quater de la skill `montage-ia` (relevé exact des couleurs, polices et animations, puis reproduction à l'identique).
Cette skill-ci sert quand elle veut un style personnel, inspiré d'un modèle, appliqué à toutes ses vidéos.
En cas de doute, demande avec l'outil de questions à choix : « Le même montage, à l'identique » ou « M'en inspirer pour mon style ».

La personne a déjà une façon de monter qu'elle aime (la sienne, ou une vidéo qui l'inspire).
Ton travail : comprendre ce style à partir d'une vidéo modèle, l'écrire noir sur blanc dans `systeme/mon-framework.md`,
le faire valider, puis l'appliquer à chaque montage avec la skill `montage-ia`.
Parle simplement, en français, sans jargon. Toutes les commandes se lancent depuis le dossier Montag'IA.

## 1. Récupérer la vidéo modèle

- Le plus simple : elle dépose le fichier dans « Vidéos à monter/Modèle » (ou le glisse dans la conversation).
- Si elle colle un lien Instagram, TikTok ou YouTube : `python systeme/montagia.py reference _modele-<nom> "<lien>"` le télécharge
  (yt-dlp, avec sa session Chrome si le site demande d'être connecté) et prépare déjà planches, cartons, couleurs et texte dans
  `systeme/projets/_modele-<nom>/reference/` (lis `analyse.md`, il remplace les étapes 1 à 4 ci-dessous). Si ça échoue :
  - si c'est sa propre vidéo, elle la reprend dans sa galerie ou la télécharge depuis l'application ;
  - si c'est la vidéo de quelqu'un d'autre, elle fait un enregistrement d'écran de son téléphone pendant la lecture, puis l'envoie sur son ordinateur.
- **Une seule vidéo modèle pour commencer**, celle qui lui ressemble le plus. Chaque modèle demande 10 à 20 minutes d'analyse :
  trois d'un coup, c'est long et le style se brouille. Si elle en donne plusieurs, choisis la plus représentative, dis-lui laquelle
  et pourquoi, et garde les autres pour ajuster ensuite. Le lien et le fichier donnent la même qualité ; le lien évite de télécharger.

## 2. Analyser la vidéo modèle

Le chemin de ffmpeg est dans `systeme/config-machine.json` (clé `ffmpeg`, ffprobe est dans le même dossier).
Le Python de Montag'IA : `systeme/.venv/bin/python` (Mac) ou `systeme\.venv\Scripts\python.exe` (Windows).
Range tout dans `systeme/projets/_modele-<nom>/`.

1. **Format et durée** : `ffprobe -v error -show_entries format=duration:stream=width,height -of json "<modele>"`.
2. **Planches d'images** (une image par seconde, 20 par planche) :
   `ffmpeg -i "<modele>" -vf "fps=1,scale=360:-1,tile=5x4" "systeme/projets/_modele-<nom>/planche-%02d.jpg"`.
   Regarde CHAQUE planche.
3. **Rythme des coupes** : `ffmpeg -i "<modele>" -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time` (sous Windows : `findstr pts_time` à la place de `grep pts_time`).
   Compte les changements de plan par minute.
4. **Le texte** : `<python> systeme/moteur/transcrire.py "<modele>" systeme/projets/_modele-<nom>/`, puis lis `transcript.txt`.
   Ça sert à comprendre la structure du discours (accroche, déroulé, appel à l'action), jamais à reprendre les phrases.
5. Si un moment précis t'intrigue, extrais une image en grand : `ffmpeg -ss <secondes> -i "<modele>" -frames:v 1 "systeme/projets/_modele-<nom>/zoom-<s>.jpg"`.

## 3. Écrire `systeme/mon-framework.md`

Décris le style avec des règles concrètes et mesurables, que tu pourras appliquer sans revoir la vidéo modèle.
Traduis chaque élément vers ce que Montag'IA sait faire (effets du catalogue de la skill `montage-ia`, charte, effets sur mesure).

```markdown
# Mon framework de montage
Modèle analysé : <fichier>, <durée>, le <date>

## Accroche
Forme (question, chiffre, contradiction…), longueur, position à l'écran, durée, animation d'entrée.
→ Montag'IA : effet `accroche`, mot coloré sur …

## Rythme
Un changement de plan toutes les X s, zooms (fréquence, force), respirations coupées serrées ou non.
→ Montag'IA : zoom toutes les … s, échelle …

## Sous-titres
Nombre de mots, position, taille, couleur, mots mis en valeur, karaoké ou non.
→ Montag'IA : charte sous-titres `un-mot` / `classique` / `dynamique`, karaoké oui/non, mots_cles = …

## Animations et visuels
Ce qui revient souvent (cartes, listes, chiffres, icônes, captures d'écran), à quel moment du discours.
→ Montag'IA : `illustration` sur…, `compteur` dès qu'un chiffre…, `etiquettes` pour…, effet sur mesure « … » si rien n'existe.

## B-roll
Fréquence, durée, type de plans (personnels, banque d'images), plein écran ou fenêtre.

## Structure du discours
Ordre des parties (accroche, problème, preuve, méthode, appel à l'action) et durée de chacune.

## Fin et appel à l'action
Forme de la fin, mot-clé, durée.

## Couleurs et police
Ce que la vidéo modèle utilise, et la charte Montag'IA la plus proche (palette, police, accent #hex).

## Ce qu'on ne reproduit pas
Le contenu, la musique, les logos et les visuels de la vidéo modèle appartiennent à leur auteur.
On s'inspire de la façon de monter, jamais du contenu.
```

Puis :
1. Présente le framework à la personne en quelques phrases simples (pas le fichier brut), et demande ce qu'elle veut ajuster.
2. Si les couleurs, la police ou les sous-titres du modèle diffèrent de sa charte, propose de mettre la charte à jour
   (`python systeme/montagia.py charte ...`, voir la skill `montage-ia`) et attends son accord.
3. Enregistre la version validée dans `systeme/mon-framework.md`.
4. Si elle veut plusieurs styles (un pour les conseils, un pour les témoignages…), enregistre chacun dans
   `systeme/mes-styles/<nom>.md` et copie celui qu'elle choisit dans `systeme/mon-framework.md` au moment du montage.

## 4. L'appliquer à chaque montage

La skill `montage-ia` reste la recette de base. Si `systeme/mon-framework.md` existe, lis-le AVANT d'écrire la fiche :
il remplace les réglages de la recette sur l'accroche, le rythme, le choix et la fréquence des effets, les sous-titres, les B-roll et la fin.
Les règles de la section 5 de `montage-ia` ne changent jamais (rien sur le visage, rien sous y=1536, moteur intouché,
2 ou 3 effets sur mesure au maximum, couleurs et polices de la charte uniquement, contrôle final regardé).
Quand tu livres, dis en une phrase ce qui vient de son framework (« accroche en question et zoom à chaque phrase, comme ton modèle »).

## 5. Ce qu'il faut dire franchement

- Le résultat reprend l'esprit et la structure du modèle, dans sa charte. Ce n'est pas une copie image par image.
- Si le modèle utilise un effet impossible ici (gros effets 3D, tournage à plusieurs caméras, montage de plusieurs vidéos), dis-le et propose l'équivalent le plus proche.
- Montag'IA monte des vidéos verticales (reels, TikTok, Shorts) et des vidéos YouTube horizontales (format YouTube, section 3 ter de `montage-ia`).
  Si le modèle est une vidéo YouTube, écris dans le framework que le format visé est YouTube : le montage se fera avec `--youtube`.
