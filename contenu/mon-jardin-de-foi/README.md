# 🌷 Mon Jardin de Foi — production de contenu hebdomadaire

Chaque lundi, avant 8h : **7 carrousels + 7 reels** (1 de chaque par jour), programmés directement dans Metricool
(marque « Mon jardin », Instagram @mon.jardin.de.foi), et **3 séquences de stories** (rappel, créer du lien, offre ; 5 à 8 slides)
déposées dans le Drive « Mon jardin de foi » > « Story semaine N ».

## Identité de marque
- **Fondatrice** : Oum Imran (Cha'), maman de deux garçons, convertie depuis ~6 ans.
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
et **3 décors sans personne**.
