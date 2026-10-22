# Mon framework de montage
Identité : hwl-assistantevirtuelle (@hwl.assistantevirtuelle). Plusieurs identités (comptes, clients) : voir « Identités » en bas.
Modèle analysé : Vidéos à monter/Modèle/modele-1.mp4 (reel Instagram, 1 min 03, 720 x 1280), le 22/10/2026
Analyse visuelle (planches image par image, détection des coupes). Transcription du modèle à faire dès que le modèle de transcription est disponible.
Statut : validé par Charlène après le premier reel (reel-1), avec ses demandes ajoutées le 22/10/2026.

## Accroche
Titre de 2 à 3 lignes empilées en haut de l'écran (y ≈ 280-480), au-dessus de la tête, pendant les 3 à 5 premières secondes.
Premier mot (le sujet, ex. un nom d'outil) en couleur claire crème/sable, suite en blanc, très serré (interligne faible, lignes qui se chevauchent légèrement).
Les mots arrivent un par un sur la voix, avec un léger flou qui se dissipe à l'entrée.
→ Montag'IA : effet `accroche`, mot clé entre *astérisques* en couleur claire (#DBCC9B / #F0EFEE), police Anton.

## Rythme
Peu de coupes franches (3 en 1 min) : c'est le contenu qui bouge, pas le plan. Une nouvelle carte ou capture toutes les 3 à 5 s pendant les passages explicatifs.
Pas de zooms marqués ; léger recadrage à chaque nouvelle phrase.
→ Montag'IA : rythme automatique (visage), zoom doux seulement sur la phrase clé, 1 effet toutes les 3 à 5 s.

## Sous-titres
2 à 4 mots, en minuscules, blancs, petits et gras, centrés sur la poitrine (y ≈ 1050-1150), sur 1 ou 2 lignes serrées, ombre douce.
Pas de karaoké. Différence voulue par Charlène : les mots forts passent en jaune doré.
→ Sous-titres faits par les finitions : 2 à 3 mots, Lato Black blanc, ombre douce, mots forts en jaune #E8BD3C (voir « Ses demandes »).

## Animations et visuels
- Captures d'écran / enregistrements d'écran dans une carte arrondie qui flotte au centre (cadre blanc ou sombre, coins arrondis, ombre), souvent avec un fond flouté derrière quand l'écran prend toute la place.
- Petites étoiles crème qui scintillent aux coins de la carte à son apparition.
- Titre de section en gros (Anton) au-dessus d'une capture quand on change de partie (ex. « Design Studio de CapCut »).
- Une vignette (miniature, résultat) dans un cadre blanc arrondi au-dessus de la tête pour montrer le résultat.
→ Montag'IA : `fenetre_app` / `image` pour les captures, `illustration` pour les idées, effet sur mesure « étoiles » (2 ou 3 maximum), `carte_titre` pour les titres de partie si demandé.

## B-roll
Ses propres enregistrements d'écran (plein centre, 3 à 8 s chacun), fond de la vidéo flouté derrière. Pas de banque d'images.
→ Charte : B-roll « miens » (dossier « Vidéos à monter/Mes plans B-roll »).

## Structure du discours
1. Accroche : la nouveauté / la promesse (0-5 s)
2. « On teste ensemble » : contexte perso (5-15 s)
3. Démonstration pas à pas avec captures (15-55 s)
4. Résultat montré + avis perso (55-63 s)

## Fin et appel à l'action
Fin sur le résultat (plusieurs propositions côte à côte) et un avis perso. Si appel à l'action : `cta_commentaire` avec le mot-clé de la charte.

## Couleurs et police
Modèle : crème/sable pour les titres, blanc pour le texte, fond naturel de la pièce.
Charlène : jaune doré #E8BD3C (accent), crème #F0EFEE (fonds), bleu #77A2BA (texte sur fond clair), sable #DBCC9B, bleus poudrés #B2CEDF et #CCDFEC.
Polices voulues : Anton (titres, accroche) et Lato (sous-titres, petits textes), via le moteur de réplique (polices Google gratuites).
Charte classique en attendant : Bebas Neue (la plus proche d'Anton).

## Ses demandes (À CHAQUE VIDÉO)
Charlène a demandé ces trois finitions sur toutes ses prochaines vidéos :
1. **Petites étoiles crème** (#F0EFEE, halo sable) qui scintillent autour du mot fort de l'accroche, 2 ou 3 étoiles décalées de 0,1 s, + un « ding » très léger (volume 0.25).
   Puis 1 ou 2 fois dans la vidéo sur un titre ou une carte importante.
2. **Mots forts en couleur** dans les sous-titres : jaune doré #E8BD3C, 1 à 2 par phrase (résultat, outil, émotion, chiffre).
3. **Gros émojis avec bruitage** sur les mots drôles ou chargés d'émotion (ex. « caca » → 💩 + « pop »). Taille 220 à 280, à côté du visage
   (jamais dessus), pop qui rebondit et léger balancement, 1,2 à 1,6 s. 1 émoji toutes les 4 s au maximum.
   Bruitages discrets (volume 0.3 à 0.6) : « pop » pour un émoji, « whoosh » à l'entrée de l'accroche, « impact » sur la chute, « ding » sur les étoiles.

## Comment on le fabrique (outils)
1. `nouveau` → relire coupes et transcription (corrections.json si un mot est faux).
1 bis. **Étalonnage** (Charlène trouvait l'image trop jaune) : `systeme/.venv/bin/python systeme/ma-bibliotheque/etalonner.py <projet> --apercu`,
   regarder `etalonnage-avant-apres.jpg`, puis sans `--apercu`. Balance des blancs automatique, réglage par défaut `--chaleur -3`.
   Filmé le soir sous une lampe jaune : `--blanc x0,y0,x1,y1` sur un bout de mur blanc (repère 1080 x 1920) et `--force 0.65`
   (garde un peu de chaleur, peau naturelle). Exemple reel-3 : `--blanc 940,620,1070,780 --force 0.65 --lisser 2`.
   Vidéo WhatsApp ou un peu bruitée : ajouter `--lisser 2` (peau lissée, bruit de compression enlevé, contours nets). Validé par Charlène sur reel-2.
1 ter. **Les « euh » et les blancs** (Charlène veut qu'on les coupe) : la transcription « avale » souvent les « euh » dans le mot d'avant
   (mot anormalement long, ex. « et » qui dure 0,8 s). Repérer les mots de plus de 0,45 s, regarder l'énergie du son dessus
   (silence = blanc, son faible et continu = « euh »), couper ces trous dans `coupes.json` (plages en temps de la vidéo source,
   garder 0,05 s autour des vrais mots), puis `preparer`. Vérifier ensuite que les petits mots n'ont pas disparu de `mots.json`
   (comparer avec transcript.json) et les remettre avec leurs temps recalés s'il le faut. Exemple : reel-2, 6 coupes, 2,65 s gagnées.
2. `replique.json` : blocs titres en Anton (police « titre », fichier Anton-Regular.ttf) et Lato (Lato-Black.ttf), à blocs_y ≈ 330 (au-dessus de la tête),
   avec `"sous_titres": {"actif": false}` (les sous-titres sont faits par les finitions, pour avoir les mots forts en couleur).
   Modèles à copier puis adapter aux mots de la vidéo : `systeme/ma-bibliotheque/modele-replique.json` et `modele-finitions.json` (issus de reel-1).
3. `python systeme/montagia.py replique <projet>`.
4. `finitions.json` (émojis, étoiles, bruitages, sous-titres avec mots_forts), puis
   `systeme/.venv/bin/python systeme/ma-bibliotheque/finitions.py <projet> --apercu t1,t2` (regarder les images), puis sans `--apercu` pour le rendu final.
   La vidéo finie remplace celle de « Mes vidéos montées ». Mode d'emploi complet en tête du fichier finitions.py.
Polices : Anton et Lato se téléchargent gratuitement (Google Fonts, licence OFL) dans `systeme/.outils/polices/` si elles manquent.
Émojis : Apple Color Emoji sur Mac, Segoe UI Emoji sur Windows (déjà sur l'ordinateur).

## Ce qu'on ne reproduit pas
Le contenu, la musique, les logos et les visuels de la vidéo modèle appartiennent à leur auteur.
On s'inspire de la façon de monter, jamais du contenu.

## Identités
Charlène travaille pour plusieurs comptes et clients : chacun a sa propre identité (charte, framework, modèles).
- Voir les identités : `python systeme/ma-bibliotheque/identite.py liste` (l'étoile = l'identité active)
- **Au début de chaque montage, demander pour quel compte ou client est la vidéo**, puis `identite.py activer <nom>`.
- Nouvelle identité : `identite.py creer <nom>` (part d'une copie de l'active), puis faire l'accueil de `montage-ia`
  (couleurs, police, ambiance, sous-titres, B-roll, pseudo, modèle éventuel) et réécrire le framework pour ce client, puis `identite.py sauver`.
- Après tout changement de charte ou de style : `identite.py sauver`.
