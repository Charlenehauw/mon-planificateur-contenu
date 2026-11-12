# Programmation Instagram et TikTok (Metricool)

## Prérequis (à vérifier une fois)
- Connecteurs **Metricool** et **Google Drive** ajoutés dans Claude ; si l'environnement limite le réseau, autoriser `drive.google.com` et `drive.usercontent.google.com`.
- Instagram en compte **professionnel relié à une page Facebook**, connecté à Metricool ; TikTok connecté à Metricool.
- Dossier Drive partagé « Tous les utilisateurs disposant du lien ».

## Fichiers
Metricool n'accepte pas les liens Drive classiques (« …/view »). Utilise le lien de téléchargement direct :
`https://drive.google.com/uc?export=download&id=[ID du fichier]`
Lis toi-même le contenu du sous-dossier de la semaine pour récupérer les ID.

## Réglages
- **Instagram** : publication automatique ; reels en type REEL ; carrousels en post à plusieurs images ; stories en STORY.
- **Son des reels** : un son du style défini dans le brief, **toujours plus long que la vidéo** (sinon la fin est muette) — vérifie la durée renvoyée par Metricool. Volume du son ~85, volume de la vidéo ~40 (0 pour les B-roll muets). Les morceaux d'artistes sous licence ne sont souvent pas disponibles via l'API : propose des reprises/créations d'utilisateurs du bon style.
- **Mention IA** : cochée pour tout contenu créé par Claude (Instagram et TikTok), pas pour les vidéos filmées par la personne.
- **TikTok** : titre obligatoire (≤ 90 caractères), publication automatique si elle ne veut aucune action (le son est alors celui de la vidéo), contenu commercial coché pour une promo.
- Fuseau horaire de la marque ; aucun créneau dans le passé.

## Après programmation
Récapitule (date, heure, plateforme, titre, son) et signale ce qui a bloqué. Quand tu modifies un post, Metricool lui donne un nouvel identifiant : c'est normal.

## Modifier
« Sur le post du [jour] à [heure] : remplace [la légende / le son / l'heure] » → modifie uniquement ce post, en renvoyant tout son contenu d'origine.
