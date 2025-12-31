# Documentation - Aligntester

## Vue d'ensemble

**Aligntester** est un outil Python conçu pour analyser les données de sortie du programme **dtc** (DiskTool Console) utilisé avec le système **KryoFlux**. Cet outil permet de vérifier l'alignement d'un lecteur de disquettes en extrayant et en analysant les valeurs de pourcentage d'alignement présentes dans les fichiers de sortie de dtc.

## Contexte technique

### KryoFlux et dtc

KryoFlux est un système de préservation de médias développé par The Software Preservation Society. Le programme **dtc** (DiskTool Console) est l'outil en ligne de commande qui permet de lire et d'analyser les disquettes.

### Format des données

Les fichiers de sortie de dtc contiennent des informations détaillées sur chaque piste (track) et chaque face (side) de la disquette analysée. Chaque ligne contient notamment :

- Un numéro de piste (format `XX.Y` où XX est le numéro de piste et Y est la face : 0 ou 1)
- Des informations sur la fréquence (`frev`)
- Des informations sur les bandes (`band`)
- Une valeur de base avec un pourcentage d'alignement : `base: X.XXX us [YY.YYY%]`

Exemple de ligne typique :
```
00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
```

## Architecture du projet

Le projet contient plusieurs versions évolutives du code, montrant l'évolution de l'outil :

### Versions du code

1. **`aligntester.py`** - Version initiale simple
2. **`aligntester_final.py`** - Ajout d'une limite de 160 valeurs
3. **`aligntester_finalfin.py`** - Ajout de la précision à 3 décimales
4. **`aligntester_Kryoflux.py`** - Version avec tri et détails complets
5. **`aligntester_Kryoflux_FR.py`** - Version française complète (recommandée)
6. **`aligntester_Kryoflux_EN.py`** - Version anglaise
7. **`aligntester_bargraph.py`** - Version avec représentation graphique
8. **`aligntester_bargraph_data.py`** - Version avec données détaillées
9. **`extraction_pourcentage.py`** - Version simplifiée d'extraction

## Fonctionnalités principales

### 1. Extraction des valeurs de pourcentage

L'outil utilise des expressions régulières pour extraire les valeurs de pourcentage d'alignement présentes dans le format `[XX.XXX%]` :

```python
pattern = r'\[(\d+(?:\.\d+)?)\s*%\]'
```

Cette expression régulière capture :
- Les nombres entiers ou décimaux
- Entre crochets `[]`
- Suivis du symbole `%`

### 2. Tri et organisation des données

La version avancée (`aligntester_Kryoflux_FR.py`) extrait également :
- Le numéro de piste au début de chaque ligne (format `XX.Y`)
- Le numéro de ligne dans le fichier
- La ligne originale complète

Les données sont ensuite triées par numéro de piste pour garantir un traitement ordonné.

### 3. Calcul de la moyenne

L'outil calcule la moyenne des valeurs de pourcentage d'alignement, en se limitant par défaut aux **160 premières valeurs** (correspondant généralement à 80 pistes, chaque piste ayant deux faces).

### 4. Représentation graphique

La fonction `calculer_barre_graphique()` génère une barre de progression visuelle :
- Longueur totale : 50 caractères
- Utilise le caractère `█` pour représenter le pourcentage
- Affiche le pourcentage avec 3 décimales
- Ajoute un texte d'évaluation selon la moyenne :
  - **99.000% - 99.999%** : "Align Perfect"
  - **97.000% - 98.999%** : "Align Good"
  - **96.000% - 96.999%** : "Align Average"
  - **< 96.000%** : "Align Poor"

### 5. Statistiques détaillées

La version complète affiche :
- Le nombre total de valeurs trouvées
- Le nombre de valeurs utilisées pour le calcul
- Le numéro de la dernière piste lue (`track_max`)
- Le nombre de pistes utilisées pour la moyenne (`track_normal`)
- Les détails de chaque valeur utilisée (ligne, numéro, valeur, ligne originale)

## Utilisation

### Version simple (fichier codé en dur)

```python
nom_fichier = 'donnees.txt'
resultats = extraire_valeurs_pourcentage(nom_fichier)
```

### Version avec arguments en ligne de commande

```bash
python aligntester_Kryoflux_FR.py D359T5.txt
```

### Paramètres

- **`nom_fichier`** : Chemin vers le fichier de sortie de dtc
- **`limite`** : Nombre de valeurs à utiliser pour le calcul (défaut : 160)

## Structure du code

### Fonction principale : `extraire_valeurs_pourcentage()`

```python
def extraire_valeurs_pourcentage(nom_fichier, limite=160):
    """
    Extrait les valeurs numériques entre crochets [] se terminant par %
    et calcule leur moyenne, en limitant à 160 premières valeurs
    avec une précision de 3 chiffres après la virgule
    """
```

**Processus :**
1. Ouvre le fichier en mode lecture avec encodage UTF-8
2. Parcourt chaque ligne du fichier
3. Utilise une expression régulière pour trouver les valeurs `[XX.XXX%]`
4. Extrait le numéro de piste au début de la ligne
5. Stocke toutes les informations dans une liste de dictionnaires
6. Trie les valeurs par numéro de piste
7. Limite aux N premières valeurs (défaut : 160)
8. Calcule la moyenne
9. Affiche les statistiques et la représentation graphique

### Fonction de visualisation : `calculer_barre_graphique()`

```python
def calculer_barre_graphique(moyenne):
    """
    Génère une représentation graphique de la moyenne avec des conditions spécifiques
    """
```

**Processus :**
1. Définit la longueur totale de la barre (50 caractères)
2. Calcule le nombre de blocs à remplir proportionnellement à la moyenne
3. Détermine le texte d'évaluation selon les seuils
4. Construit la barre avec des caractères `█` et des espaces
5. Retourne la chaîne formatée

## Format de sortie

### Exemple de sortie typique

```
Nombre total de valeurs trouvées : 170
Nombre de valeurs utilisées pour la moyenne : 160
Nombre total de track lues : 85.1
Nombre total de track pour le calcul de la moyenne : 80.0

Détails des valeurs utilisées :
Ligne 8 - Numéro 0.0 : 00.0    : base: 1.000 us [99.911%], ...
Ligne 12 - Numéro 0.1 : 00.1    : base: 1.004 us [99.742%], ...
...

Représentation graphique :
[████████████████████████████████████████████████] 99.523% Align Perfect
```

## Interprétation des résultats

### Seuils d'alignement

- **Align Perfect (99.0% - 99.9%)** : Alignement excellent, le lecteur est parfaitement calibré
- **Align Good (97.0% - 98.9%)** : Bon alignement, acceptable pour la plupart des usages
- **Align Average (96.0% - 96.9%)** : Alignement moyen, peut nécessiter un réglage
- **Align Poor (< 96.0%)** : Mauvais alignement, réglage nécessaire

### Statistiques importantes

- **track_max** : Indique la dernière piste lue, permet de vérifier que toutes les pistes ont été analysées
- **track_normal** : Nombre de pistes utilisées pour le calcul (généralement la moitié du nombre de valeurs, car chaque piste a deux faces)

## Gestion des erreurs

Le code gère plusieurs types d'erreurs :

1. **FileNotFoundError** : Fichier introuvable
   ```python
   except FileNotFoundError:
       print(f"Erreur : Le fichier {nom_fichier} n'a pas été trouvé.")
   ```

2. **Exceptions générales** : Autres erreurs
   ```python
   except Exception as e:
       print(f"Une erreur est survenue : {e}")
   ```

3. **Vérification des arguments** : Pour les versions avec ligne de commande
   ```python
   if len(sys.argv) < 2:
       print("Utilisation : python script.py <nom_du_fichier>")
       sys.exit(1)
   ```

## Dépendances

Le projet utilise uniquement des bibliothèques standard Python :

- **`re`** : Pour les expressions régulières
- **`math`** : Pour les calculs mathématiques (floor)
- **`sys`** : Pour les arguments en ligne de commande

Aucune installation de packages externes n'est nécessaire.

## Fichiers de données

Le projet contient des exemples de fichiers de sortie dtc :

- **`D359T5.txt`** : Exemple de sortie pour un format MFM (IBM PC)
- **`donnees.txt`** : Exemple de sortie pour un format AmigaDOS

Ces fichiers montrent les différents formats que l'outil peut traiter.

## Évolution du projet

L'historique des fichiers montre une évolution progressive :

1. **Version initiale** : Extraction simple des pourcentages
2. **Ajout de limite** : Limitation à 160 valeurs pour standardiser les calculs
3. **Précision** : Passage à 3 décimales pour plus de précision
4. **Tri et organisation** : Tri par numéro de piste pour un traitement ordonné
5. **Visualisation** : Ajout de la barre graphique pour une lecture rapide
6. **Statistiques** : Ajout de statistiques détaillées (track_max, track_normal)
7. **Internationalisation** : Versions française et anglaise

## Recommandations d'utilisation

### Version recommandée

Pour une utilisation complète, utilisez **`aligntester_Kryoflux_FR.py`** qui combine :
- Extraction précise des données
- Tri et organisation
- Statistiques complètes
- Visualisation graphique
- Interface en français

### Workflow typique

1. Lancer dtc pour analyser une disquette :
   ```bash
   dtc -f<fichier_sortie> -i0
   ```

2. Rediriger la sortie vers un fichier :
   ```bash
   dtc -f<fichier_sortie> -i0 > resultat.txt
   ```

3. Analyser avec aligntester :
   ```bash
   python aligntester_Kryoflux_FR.py resultat.txt
   ```

4. Interpréter les résultats selon les seuils d'alignement

## Limitations et considérations

1. **Limite de 160 valeurs** : Cette limite est arbitraire et peut être ajustée selon les besoins. Elle correspond généralement à 80 pistes (160 faces).

2. **Format de fichier** : L'outil est conçu pour les fichiers de sortie de dtc. D'autres formats peuvent nécessiter des modifications.

3. **Tri par numéro de piste** : Le tri suppose que les numéros de pistes sont au format `XX.Y`. Des formats différents nécessiteront une adaptation.

4. **Encodage** : Le code suppose un encodage UTF-8. Pour d'autres encodages, modifier la ligne d'ouverture du fichier.

## Améliorations possibles

1. **Export des résultats** : Ajout d'une fonction pour exporter les résultats en CSV ou JSON
2. **Graphiques avancés** : Utilisation de matplotlib pour des graphiques plus détaillés
3. **Analyse par piste** : Affichage d'un graphique montrant l'alignement par piste
4. **Comparaison** : Fonction pour comparer plusieurs analyses
5. **Interface graphique** : Développement d'une interface utilisateur avec tkinter ou PyQt
6. **Support de formats multiples** : Extension pour supporter d'autres formats de sortie

## Conclusion

Aligntester est un outil spécialisé mais efficace pour analyser l'alignement des lecteurs de disquettes à partir des données de dtc. Son évolution montre une progression vers une solution complète et utilisable, avec des fonctionnalités d'extraction, d'analyse et de visualisation.

L'outil est particulièrement utile pour :
- Les techniciens de maintenance de lecteurs de disquettes
- Les archivistes numériques utilisant KryoFlux
- Les passionnés de rétro-informatique
- Les professionnels de la préservation de médias

