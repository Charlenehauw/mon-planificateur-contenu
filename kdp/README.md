# 📚 Gamme KDP – Atelier Petits Bonheurs

26 livres de coloriage et d'activités au format broché **8,5 x 11 po**, **108 pages**, chaque dessin au **recto seul**
(page blanche derrière). Chaque dossier de `livres/` contient tout ce qu'il faut pour publier.

## 📁 Contenu de chaque dossier livre

| Fichier | Rôle |
|---|---|
| `interieur.pdf` | Manuscrit intérieur à téléverser sur KDP (sans fond perdu) |
| `couverture.pdf` | Couverture complète : 4e de couverture + dos + 1re de couverture, fond perdu inclus |
| `apercu-couverture.png` | Aperçu rapide de la couverture |
| `aplus/` | 6 visuels du contenu A+ (bannière 970x600, aperçu 970x300, 3 tuiles 300x300, collection 970x300) |
| `fiche-produit.md` | Titre, sous-titre, description HTML, 7 mots-clés, catégories, paramètres d'impression, prix, textes A+ |
| `prompts.md` | (livres illustrés uniquement) les 50 prompts pour générer les dessins |

## ✅ État de la gamme

| Public | Livre | État |
|---|---|---|
| Enfants | Coloriage Dinosaures | ⏳ illustrations à générer |
| Enfants | Coloriage Reptiles | ⏳ illustrations à générer |
| Enfants | Coloriage de la Mer | ⏳ illustrations à générer |
| Enfants | Coloriage Camions de Chantier | ⏳ illustrations à générer |
| Enfants | Coloriage Mixte | ⏳ illustrations à générer |
| Enfants | Activités Dinosaures 4-6 ans | ✅ prêt |
| Enfants | Activités Reptiles 4-6 ans | ✅ prêt |
| Enfants | Activités Mixte 6-8 ans | ✅ prêt |
| Femmes | Coloriage Maternité | ⏳ illustrations à générer |
| Femmes | Coloriage Fleurs | ⏳ illustrations à générer |
| Femmes | Mandalas | ✅ prêt |
| Femmes | Citations Bonheur | ✅ prêt |
| Femmes | Citations Fun | ✅ prêt |
| Femmes | Anti-colère | ✅ prêt |
| Femmes | Coloriage Beauté | ⏳ illustrations à générer |
| Femmes | Coloriage Cuisine | ⏳ illustrations à générer |
| Femmes | Cosy Été / Automne / Hiver / Printemps | ⏳ illustrations à générer |
| Femmes | Activités Bonheur | ✅ prêt |
| Femmes | Activités Post-partum | ✅ prêt |
| Femmes | Activités Écriture | ✅ prêt |
| Couples | Citations d'amour à colorier | ✅ prêt |
| Couples | Coloriage à faire en couple | ✅ prêt |
| Couples | Activités en couple | ✅ prêt |

## 🎨 Terminer un livre illustré

1. Ouvre `livres/<livre>/prompts.md` et génère les 50 images (Higgsfield, Midjourney, Canva…), en portrait.
2. Enregistre-les dans `images/<livre>/` sous les noms `01.png` à `50.png`.
3. Lance `python3 build.py <livre>` : l'intérieur, la couverture (avec un dessin colorisé automatiquement) et les visuels A+ sont créés.
4. Sur KDP, déclare le contenu « généré par IA » (images).

## 🛠️ Commandes

```bash
pip install pycairo numpy scipy pillow pymupdf   # une seule fois
python3 build.py --list                          # liste des livres
python3 build.py femmes-03-mandalas              # reconstruire un livre
python3 build.py all                             # reconstruire toute la gamme
```

Le nom d'auteur et de marque se change dans `catalog.py` (`BRAND`). Toutes les métadonnées (titres, descriptions,
mots-clés, palettes, citations) se trouvent dans `catalog.py`, `data/quotes.py` et `data/journals.py`.

## 🚀 Checklist de publication KDP

1. **Détails** : copie le titre, le sous-titre, la série, l'auteur, la description (mode HTML), les 7 mots-clés et les 3 catégories depuis la fiche.
2. **Contenu** : ISBN KDP gratuit · Noir et blanc, papier blanc · 8,5 x 11 po · **Sans fond perdu** · Finition **mate** · téléverse `interieur.pdf` puis `couverture.pdf`.
3. Vérifie l'aperçu en ligne (marges et code-barres : la zone en bas à droite de la 4e de couverture est laissée libre).
4. **Prix** : prix conseillé dans la fiche, à vérifier avec le calculateur KDP.
5. Après publication : **Marketing > Contenu A+** → crée les 4 modules avec les images de `aplus/` et les textes de la fiche.

Les polices utilisées (Google Fonts, licence OFL / Apache) sont libres d'usage commercial.
