# Voix sans visage, en noir et or (« sans ma tête »)

On garde la voix de Charlène, nettoyée et coupée (les « euh » et les blancs sont retirés), et on remplace entièrement l'image par des visuels :
- des titres plein écran, avec le mot fort en Playfair doré et des étoiles ;
- un téléphone dont l'écran change à chaque phrase, avec une pastille de titre au-dessus ;
- une carte d'offre ;
- les avis de ses clientes ;
- des extraits en plein écran ;
- des émojis ;
- des sous-titres en Montserrat, avec les mots forts en or.

Pour le refaire :
1. Préparer un projet face caméra comme d'habitude : `nouveau`, coupes des « euh », `mots.json` recalé, puis `replique` pour obtenir la voix finale. Copier le son dans `assets/voix.wav`.
2. Remplir les listes de `generer.py` avec les mots de la vidéo : TITRES, ECRANS, PLEINS, AVIS, EMOJIS et FORTS. Les temps s'écrivent « @mot », « @mot#2 », « @mot> » ou « @mot-0.2 ».
3. Lancer `python3 generer.py <dossier video> <mots.json> <durée>`, puis `npx hyperframes@0.8.96 render`, et enfin `loudnorm=I=-14:TP=-1.5` sur le son.
