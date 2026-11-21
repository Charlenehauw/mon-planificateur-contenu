# 🌷 Mon Jardin de Foi — production de contenu hebdomadaire

Chaque lundi, avant 8h : **7 carrousels + 7 reels** (1 de chaque par jour), programmés directement dans Metricool
(marque « Mon jardin », Instagram @mon.jardin.de.foi), et **3 séquences de stories** (rappel, créer du lien, offre ; 5 à 8 slides)
déposées dans le Drive « Mon jardin de foi » > « Story semaine N ».

## Identité de marque
- **Fondatrice** : Oum Imran (Cha'), maman de deux garçons, convertie depuis environ 5 ans.
- **Mission** : aider chaque sœur à faire grandir sa foi au quotidien, avec douceur et organisation.
- **Valeurs** : douceur 🤍 · régularité plutôt que perfection 🌱 · accessibilité 🫶 · sincérité · bienveillance entre sœurs.
- **Métaphore** : le jardin. Chaque journée complète fait pousser une fleur 🌱🌷🌸🌺🌹.
- **Vocabulaire** : jamais « wird » (connotation soufie) → « adhkar », « lecture du Coran », « invocations ».
- **Ton** : tutoiement, chaleureux, simple, encourageant, jamais culpabilisant, emojis floraux (dans les légendes).
- **Couleurs** : rose poudré `#fdf1f4` · rose `#e8a3b9` · framboise `#a34d6b` · mauve `#86385a`.
- **Polices** : Dancing Script (titres) · Quicksand (texte) · Amiri (arabe).
- **Style visuel premium** : fond texturé, cadre fin, alternance slides claires et mauves, pas d'emojis dans les visuels,
  une petite fleur minimaliste au trait différente par post (dans un coin, jamais sous le texte).

## Cible : « Sœur Yasmine »
Femme musulmane francophone, 20-40 ans, jeune maman ou étudiante, parfois convertie. Veut lire plus de Coran et être
régulière, mais elle est débordée, fatiguée et dispersée. Secondaires : nouvelles converties, mamans en post-partum.

## Offres
| Offre | Contenu | Prix |
|---|---|---|
| Gratuite | 📖 Coran (plan de lecture, sourates, mémorisation) + 📚 Apprentissage (leçons, 99 Noms, hadiths, quiz) | Gratuit |
| Complète | Ma journée par prière, jeûne, carnet du soir, glow up, habitudes, défis, aumône, thèmes | 2,99 € au lieu de 7,90 € jusqu'au 30/11, paiement unique, accès à vie |
| Bientôt 👀 | Nouveautés | À annoncer |

## Piliers (rotation sur la semaine)
Rappel islamique · Motivation · Bien-être de la femme · Mon offre.
Reels : alternance motion (dessins au trait animés) / ambiance B-roll. **Pas de musique** : bruitages et sons de nature
uniquement (vent, pluie, oiseaux, grillons, carillons).

## Générer une semaine
```bash
cd contenu/mon-jardin-de-foi
mkdir -p node_modules && ln -sfn "$(npm root -g)/playwright" node_modules/playwright
node outils/carrousels.mjs semaines/AAAA-MM-JJ
node outils/reels.mjs semaines/AAAA-MM-JJ
FORMAT=story node outils/carrousels.mjs semaines/AAAA-MM-JJ   # stories 1080x1920
node outils/reels_mrr.mjs semaines/AAAA-MM-JJ <dossier des clips MRR>   # reels « femme voilée »
```
- Son des reels : normalisé à -16 LUFS (loudnorm), ambiances dans les médiums pour rester audibles sur téléphone.
- `semaines/<date>/contenu.json` : textes des slides, légendes, dates de publication, scènes des reels.
- `outils/scenes.mjs` : scènes animées des reels · `outils/sons.py` : ambiances et bruitages synthétisés.

## Médias MRR
Dossier Drive « MRR » (partagé par lien) : femmes voilées en images et vidéos. Les reels « femme voilée » enchaînent 2 clips
+ textes + bruitages ; si un fichier `semaines/<date>/anasheed/<id>.mp3` existe, l'anasheed est mixé automatiquement.
Rendu des reels motion : lancer `node outils/reels.mjs <semaine> <id>` reel par reel (plusieurs d'un coup donne des vidéos vides).
Règle visuels MRR : sur 5 carrousels et 5 reels, **2 avec une femme** (uniquement yeux fermés ou de dos, tenue pudique)
et **3 sans personne, uniquement sur fond aux couleurs de la marque (pas de décor)**.

## Format hebdo validé (depuis le 9 novembre 2026)
- 7 reels motion (identité) ~18h · 5 carrousels ~10h · 5 reels MRR ~12h30 · 3 séquences de stories (envoyées à Cha').
- Vocabulaire : pluriel de sunnah = « sunan ».
- Médias Metricool : URLs raw.githubusercontent.com figées sur le SHA du commit. Vérifier le planning pour éviter les heures déjà prises.

## ⚠️ Nouvelles règles de Cha' (21 novembre 2026), prioritaires sur ce qui précède
- **Moins de promo** : sur 4 contenus, **1 seul parle de l'appli**. Les 3 autres n'en parlent pas du tout (pas de « lien en bio »,
  pas de prix) : uniquement des rappels, des versets, des hadiths, de l'audio, de la récitation du Coran.
- **Vidéos plus dynamiques, de 10 à 30 s, avec une vraie histoire et un fil conducteur** (début → tension → verset/rappel → fin) :
  effets, animations, bruitages, cartes, SMS, notifications, illustrations. Outil : `node outils/histoires.mjs <semaine> <id>`
  (section `histoires` du contenu.json ; plans `notif`, `sms`, `carte`, `verset`, `texte`, `liste`, `fin`). Un reel par exécution.
- **Coran** : plan `verset` = récitation Mishary Alafasy (everyayah.com, verset par verset), **sans bruitage ni ambiance par-dessus**
  (l'ambiance s'efface automatiquement). Citer la récitation dans la légende.
- **Plus de « Jumu'a Mubarak »**.
- Les anciens reels motion courts (`reels.mjs`, 16 s) ne sont plus utilisés seuls ; les reels MRR restent possibles s'ils racontent une histoire.
- Personnages des histoires : scénarios « POV » / « ma sœur » présentés comme des mises en situation, jamais comme des témoignages réels.
- **Thèmes** : bien-être, glow up, post-partum, patience… toujours **autour de l'islam, selon la sunnah** (hadiths et versets sourcés).
- **Styles de référence envoyés par Cha'** (à varier dans la semaine) :
  1. « X façons de… » : intro avec gros chiffre + puces, puis 1 point par plan (numéro, titre, source, icône animée, points de progression) → plan `points`.
  2. Checklist qui se coche (cartes empilées + icônes + barre « 3/6 » + sous-titres karaoké surlignés) → plan `checklist`.
  3. Compte à rebours / compteur à chiffres qui basculent + texte qui s'écrit avec mots surlignés (fond grille rose) → plan `compte`.
  + histoire SMS/notification/carte (`notif`, `sms`, `carte`) et récitation (`verset`). Fonds : `nuit`, `sombre`, `rose`, `grille`, `mauve`.
  Icônes disponibles (`ic`) : dents, cheveux, khol, lune, assiette, tasse, lit, dattes, coeur, mains, livre, tasbih, sablier, bebe, soleil, eau, marche.
