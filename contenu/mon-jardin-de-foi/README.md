# 🌷 Mon Jardin de Foi — production de contenu hebdomadaire

Chaque lundi : **7 carrousels + 7 reels** (1 de chaque par jour), programmés dans Metricool
(marque « Mon jardin », Instagram @mon.jardin.de.foi).

## Identité de marque
- **Fondatrice** : Oum Imran (Cha'), maman de deux garçons, convertie depuis ~6 ans.
- **Mission** : aider chaque sœur à faire grandir sa foi au quotidien, avec douceur et organisation.
- **Valeurs** : douceur 🤍 · régularité plutôt que perfection 🌱 · accessibilité 🫶 · sincérité · bienveillance entre sœurs.
- **Métaphore** : le jardin. Chaque journée complète fait pousser une fleur 🌱🌷🌸🌺🌹.
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
```
- `semaines/<date>/contenu.json` : textes des slides, légendes, dates de publication, scènes des reels.
- `outils/scenes.mjs` : scènes animées des reels · `outils/sons.py` : ambiances et bruitages synthétisés.
