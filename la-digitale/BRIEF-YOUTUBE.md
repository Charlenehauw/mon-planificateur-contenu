# Brief YouTube — La digitale 🎧

> Statut : **actif** — production automatique chaque mercredi (voir « Routine hebdomadaire »).

## Rythme
- 3 vidéos longues par semaine, **1h**, publiées **vendredi, dimanche et mardi à 19h** (Europe/Paris)
- 7 Shorts par semaine (30 s, 9:16), **1 par jour à 12h30**, du jeudi au mercredi suivant
- Sons d'ambiance **sans musique** : pluie, vagues, feu de bois, forêt…

## Style visuel (à partir des prochaines vidéos)
- **Girly, mignon, kawaii** : couleurs pastel, personnages et décors doux, ambiance cosy
- Visuel animé en boucle (lumières, particules, pluie, flammes…)
- Bouton / rappel **« S'abonner »** animé sur les vidéos
- **Miniature** personnalisée pour chaque vidéo longue

## Codes YouTube à respecter
- Miniature 1280×720 (16:9), texte court et lisible, contraste fort, < 2 Mo
- Titre : mot-clé en premier (ex. « Pluie douce… »), durée, usage (dormir / se concentrer)
- Description : 2 premières lignes accrocheuses, usages, appel à l'abonnement, crédits son, hashtags
- Rappel « S'abonner » discret (coin bas), jamais sur toute la durée, pas sur les zones d'interface des Shorts
- Shorts : rien d'important dans le tiers bas ni sur le bord droit (zone des boutons)
- Déclaration « contenu IA » si visuel réaliste généré par IA
- Audience : « non destinée aux enfants » (sauf indication contraire)

## Publication
- Metricool, marque « La digitale » (blogId 7813796), chaîne YouTube reliée
- Vidéos hébergées sur un lien public (ici, `la-digitale/videos/`) pour que Metricool les récupère

## Déjà publié
- 03/11/2026 9h30 — Ambiance forêt dorée 15 min
- 03/11/2026 12h30 — Short « 30 secondes pour respirer en forêt »

## Routine hebdomadaire

### Mercredi — création (tâche planifiée)
1. Lire ce brief. Récupérer les sons dans le dossier Google Drive **« youtube »** (connecteur Google Drive).
   Si le dossier n'existe pas ou est vide : prévenir Charlène et s'arrêter, ne rien inventer.
2. Choisir 3 ambiances différentes (ne pas répéter celles de la semaine précédente, voir « Historique »).
3. Pour chaque ambiance : scène **kawaii animée** en boucle (outils dans `la-digitale/outils/` :
   `scene.html` = exemple de scène forêt à adapter, `render.js` = rendu des images, `loop.py` = boucle audio
   sans coupure), avec rappel « S'abonner » animé.
   - Vidéo 1h 1920×1080 + miniature 1280×720 avec texte court
   - Shorts 1080×1920, 30 s (7 au total, tirés des 3 ambiances)
4. **Shorts** : les pousser dans `la-digitale/videos/AAAA-MM-JJ/` (dépôt public), puis les programmer dans Metricool
   via le lien raw GitHub, 1 par jour à 12h30, du jeudi au mercredi suivant.
5. **Vidéos longues** (trop lourdes pour GitHub) : les envoyer à Charlène (fichiers + miniatures) avec les
   noms de fichiers attendus : `AAAA-MM-JJ_vendredi_<ambiance>.mp4`, `..._dimanche_...`, `..._mardi_...`.
   Elle les dépose dans **Drive > youtube > a-publier**.
6. Ajouter à `la-digitale/PLANNING-YOUTUBE.md` les titres, descriptions et tags SEO des 3 vidéos longues,
   puis mettre à jour l'historique ci-dessous.

### Jeudi soir — programmation des vidéos longues (tâche planifiée)
1. Chercher les vidéos de la semaine dans Drive > youtube > a-publier.
2. Les partager en lecture (« toute personne disposant du lien »), puis les programmer dans Metricool : vendredi, dimanche
   et mardi à 19h, avec titres, descriptions et tags tirés de `PLANNING-YOUTUBE.md` (+ miniature si
   la chaîne est vérifiée).
3. Si des fichiers manquent : rappel à Charlène, ne rien programmer de partiel sans le signaler.

## Historique des ambiances
- Semaine du 03/11/2026 : forêt dorée (test)
