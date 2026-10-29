# Passages B-roll au-dessus d'un face caméra (reel-4)

À utiliser après `replique` et avant `finitions` :
1. Copier `final.mp4` dans `<projet>/broll/assets/video/base.mp4`, puis extraire le son dans `assets/voix.wav`.
2. Remplir les listes de `generer.py` :
   - `TELS` : un téléphone qui monte, des écrans qui défilent, une pastille Anton noire avec le mot fort en or ;
   - `AVIS` : captures de messages dans une carte blanche « Ce qu'elles en disent 💛 » ;
   - `PROMO` : un extrait plein écran ;
   - `VOILES` : le fond flouté derrière.
3. Lancer `python3 generer.py <projet>/broll <durée>`, puis `npx hyperframes@0.8.96 render`.
4. Garder l'ancien `final.mp4` sous le nom `final-titres.mp4`, mettre le rendu B-roll à la place de `final.mp4`, puis lancer `finitions.py`. Les sous-titres passent sous le téléphone (y 1260) : le bas du téléphone est à 1210.
5. Contrôler le son : crête sous -1 dB (`loudnorm=I=-14:TP=-1.5`).
