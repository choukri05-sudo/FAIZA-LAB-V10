# FAIZA LAB V10 — Calibration inverse, résultats mesurés

**23 novembre 2026 — expérience informatique contrôlée, sur motifs synthétiques, avec inspection complémentaire de 5 photos réelles.**

## Méthode : partir du résultat final

Objectif contrôlé : reconstruire exactement la grille de perles de référence, cellule par cellule. Une différence signifie qu'au moins une perle ne correspond plus. C'est un objectif de mesure **strict**, et non une validation esthétique ni une garantie de tissage.

1. Trois grilles sources de géométries différentes, avec couleurs et positions connues : un coquelicot issu du labo V08, un bracelet floral vert construit pour l'essai et un motif géométrique construit pour l'essai. Les deux derniers sont des modèles de test et non des photos réelles.
2. Rendu synthétique de perles, puis dégradations par flou gaussien, réduction, JPEG, bruit numérique et exposition : 23 conditions par motif.
3. Deux traitements (classification brute et lissage bilatéral + filtre médian) : **3 × 23 × 2 = 138 résultats** de grilles comparés à la vérité connue.
4. Vectorisation sans IA (OpenCV : segmentation en régions puis contours SVG), relecture du SVG et contrôle final sur 21 tests complets. Deuxième solution : récupération des perles puis SVG exact par regroupement horizontal (structure-aware).
5. Cinq photos réelles du projet (coquelicot flou, bracelet vert, deux géométriques, pastel) : étude VISUELLE et SVG, sans grille de référence connue. Recadrage manuel des régions étudiées pour ne pas confondre segmentation et vectorisation.

## Mesures : reconstruction des perles AVANT le tracé SVG

La fidélité est le pourcentage exact de perles de premier plan dont le code couleur retrouve celui de la grille source.

| Dégradation | Coquelicot | Floral vert | Géométrique |
|---|---:|---:|---:|
| Flou σ = 1,8 pixels | 100.0 % | 100.0 % | 100.0 % |
| Flou σ = 2,5 pixels | 62.3 % | 99.9 % | 100.0 % |
| Flou σ = 3,5 pixels | 12.4 % | 82.0 % | 48.8 % |
| 3 pixels conservés / perle | 100.0 % | 100.0 % | 100.0 % |
| 2 pixels conservés / perle | 9.9 % | 74.8 % | 19.6 % |
| Bruit σ = 20/255, sans lissage | 93.3 % | 86.1 % | 97.3 % |
| Bruit σ = 20/255, avec lissage | 99.8 % | 96.5 % | 99.9 % |
| JPEG qualité 18 | 91.3 % | 88.5 % | 97.6 % |
| Exposition relative 0,60 | 94.1 % | 40.3 % | 100.0 % |

**Constat expérimental** : à 10 pixels de pas dans le rendu initial, les **trois** modèles sont reconstitués sans aucune erreur après un flou de σ = 1,8 pixels par reconnaissance directe; à 2,5 pixels, le coquelicot perd près de 38 % des cellules de couleur. À 3 pixels effectifs par perle après réduction, les trois références restent exactes; à 2 pixels, elles échouent. Ces intervalles sont observés **dans ce jeu de test** avec palette connue et perles parfaitement alignées; ils ne sont pas un seuil universel pour les photographies.

## Vérification du résultat après SVG (chaîne complète)

| Cas | Avant SVG : perles correctes | Après vectorisation directe : perles correctes |
|---|---:|---:|
| Coquelicot, flou 1,2 | 100.0 % | 62.7 % |
| Coquelicot, flou 1,8 | 100.0 % | 36.9 % |
| Floral vert, flou 1,8 | 100.0 % | 98.7 % |
| Géométrique, flou 1,8 | 100.0 % | 93.0 % |
| Coquelicot, 3 pixels/perle | 100.0 % | 13.0 % |
| Géométrique, 3 pixels/perle | 100.0 % | 53.0 % |

**Cause vérifiée** : le tracé SVG par contours bruts introduit de nouvelles erreurs à la place des formes des perles, même lorsque la palette par cellule est correcte. Il est donc faux de refuser la photo en raison de ce défaut de programme. La branche spéciale *photo de perles → structure discrète → SVG par lignes* passe le contrôle d'aller-retour SVG sans créer d'erreur supplémentaire; elle conserve le résultat de reconnaissance, mais ne produit pas encore un dessin artistique général.

## Cinq vraies photographies, sans vérité de fabrication

| Photo utilisée | Variance du Laplacien sur le recadrage limité à 550 px maximum | Régions SVG extraites |
|---|---:|---:|
| coquelicot_ancien | 4.2 | 145 |
| bracelet_vert | 221.8 | 297 |
| geometrie_franche | 816.7 | 1718 |
| bracelet_geometrique | 1026.0 | 715 |
| pastel_geom | 121.5 | 587 |

Ces valeurs ne sont **PAS** des seuils de rejet. Elles dépendent notamment du recadrage, de la texture des perles et de la résolution. Le coquelicot original est déjà très flou et sa vectorisation 8 couleurs n'établit pas une vraie grille correcte. Des images contenant du bruit peuvent avoir un Laplacien artificiellement très élevé tout en produisant des erreurs.

## Paramètres conclus par raisonnement inverse

**Mesurés sur nos 3 contrôles et non encore généralisables :**

- Le détail critique doit être défini en *nombre de cellules de perles*, et non en taille de fichier ou en résolution absolue.
- Pour les rendus synthétiques de cet essai, la perte par réduction commence entre **3 et 2 pixels utiles par pas de perle**; l'objectif provisoire d'acquisition est donc **au moins 3 pixels utiles/par perle**, puis à confirmer sur photos réelles et autres techniques.
- La reconstruction directe reste exacte jusqu'à **σ flou = 1,8 pixel** (soit **0,18 pas de perle**) dans ces modèles. Ce rapport n'est pas directement mesurable sur une photo inconnue : un estimateur de largeur des détails doit d'abord être développé.
- Le filtre bilatéral + médian peut améliorer le bruit (test bruit 20/255), mais **détruit** certains détails en présence de flou : le choix du filtre doit être conditionné par la nature de la dégradation, jamais systématique.
- JPEG, éclairage et bruit n'admettent **pas de valeur unique** déduite de ces données. La palette et la structure du motif changent fortement la tolérance.
- Il faut une **branche de vectorisation de régions** pour les motifs illustrés et une **branche de reconstruction de la trame** pour les photographies de perlage existant. Les traiter identiquement est une erreur de conception.

## Règle d'admission à mettre en œuvre, mais à ne pas encore figer

L'image est d'abord traitée par plusieurs chaînes de reconstruction. **L'acceptation dépend des pertes mesurées dans le dessin et la grille finaux** (rupture de contours, perte des détails indispensables, ambiguïtés de couleurs, contraintes de tissage), avec possibilité de proposer un autre cadrage ou une autre taille de perles. Il ne faut pas rejeter une image simplement parce que la première méthode SVG est mauvaise. Sans image de référence et sans mesure sémantique fiable, un seuil de rejet numérique automatique serait encore prématuré.

## Limites qui empêchent de déclarer un seuil définitif

- Échantillon de calibration : trois grilles de test, colorimétrie/pas exacts connus. Les vraies photos ne disposent pas de grilles de référence validées.
- Recadrage manuel des cinq photos réelles; segmentation automatique de l'objet encore non validée.
- Tracé testé effectivement : **notre méthode OpenCV et SVG**. Les moteurs GitHub **VTracer** et **ImageTracerJS n'ont pas été exécutés** dans cette session : composants indisponibles hors ligne. Aucun résultat ne leur est attribué.
- Les critères esthétiques (réalisme, beauté du motif, disponibilité des perles, symétrie conditionnelle) et la fabrication loom/peyote/brick stitch sont encore à valider humainement et techniquement.

## Fichiers de preuve

- `01_comparaison_photos_reelles.png` : planche de cinq photos étudiées, **exclue de cette diffusion publique faute de droits de redistribution vérifiés**.
- `02_effet_du_flou.png`, `03_effet_resolution.png` : courbes tirées des 138 mesures.
- `04_erreur_de_vectorisation.png` : démonstration du problème du SVG brut.
- `mesures_completes.csv` : 138 mesures par motif, dégradation et traitement.
- `test_chaine_complete.csv` : 21 essais re-vectorisés et re-lus.
- `test_vectorisation_structurelle.csv` : 84 essais de sortie technique structurelle (3 × 14 × 2); les contrôles SVG des exemples sélectionnés sont strictement sans perte additionnelle.
- `masters` : grilles de référence et rendus contrôlés.
- `cas_reels` : statistiques anonymes des photos étudiées uniquement ; images et tracés issus de ces photos **non fournis**. `svg` : exemples synthétiques reproductibles.
- Scripts Python : reproduction complète des expériences **synthétiques**. La partie photographies réelles exige les sources autorisées et n’est pas reproductible à partir de ce paquet public.

**Conclusion** : ce test permet de quantifier quelques limites sur des images où l'on connaît la bonne grille. Il montre surtout qu'il faut d'abord améliorer la reconstruction des formes et la vectorisation, sous peine de fixer de mauvais seuils de rejet. **Ne pas encore intégrer ces paramètres comme règles de production dans Faiza.**
