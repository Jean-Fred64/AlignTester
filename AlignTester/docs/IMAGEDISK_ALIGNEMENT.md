# Comment ImageDisk Vérifie l'Alignement

Ce document explique comment ImageDisk fonctionne pour vérifier l'alignement des têtes de disquette et comment cela se compare à notre implémentation avec Greaseweazle.

---

## 🔍 Fonctionnement d'ImageDisk

### Principe de Base

ImageDisk est un outil DOS qui accède directement au contrôleur de disquette (FDC 765) pour tester l'alignement. Le processus fonctionne ainsi :

1. **Positionnement de la tête** : `seek(cylindre)` positionne la tête sur une piste spécifique
2. **Lecture répétée** : `readid()` ou `read_sector()` lit la même piste plusieurs fois
3. **Analyse des IDs** : Compare les IDs de secteurs détectés avec les IDs attendus
4. **Calcul du pourcentage** : Le pourcentage d'alignement est calculé en fonction de la cohérence des lectures

### Fonction `align()` d'ImageDisk

La fonction `align()` d'ImageDisk :

```c
// Pseudo-code du fonctionnement
void align(int cylinder, int head) {
    for (int i = 0; i < num_reads; i++) {
        seek(cylinder, head);
        sector_ids = readid();  // Lit les IDs de secteurs
        analyze(sector_ids);     // Analyse la cohérence
        display_results();       // Affiche les résultats
        delay(100ms);
    }
}
```

**Ce qu'ImageDisk fait réellement** :
- Lit la même piste plusieurs fois (typiquement 10-20 fois)
- Détecte les IDs de secteurs à chaque lecture
- Compare les IDs détectés avec les IDs attendus
- Calcule un pourcentage basé sur la cohérence :
  - Si tous les IDs sont corrects → 100%
  - Si certains IDs sont incorrects → pourcentage réduit
  - Si les IDs varient entre lectures → mauvais alignement

### Format de Sortie d'ImageDisk

ImageDisk n'affiche **PAS directement** des pourcentages dans le format `[99.911%]`. Il affiche plutôt :

```
Cylinder 40, Head 0:
  Read 1: 18 sectors, IDs: 40,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
  Read 2: 18 sectors, IDs: 40,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
  Read 3: 18 sectors, IDs: 40,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
  ...
```

Le pourcentage est **calculé** par l'utilisateur ou par un script d'analyse basé sur :
- La cohérence des IDs entre les lectures
- Le nombre de secteurs détectés correctement
- La stabilité des lectures

---

## 📊 Format de Sortie de dtc (KryoFlux)

### D'où viennent les pourcentages `[99.911%]` ?

Les pourcentages dans le format `[99.911%]` proviennent de **dtc (DiskTool Console)** de **KryoFlux**, pas directement d'ImageDisk.

**Format de sortie de dtc** :
```
00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
00.1    : base: 1.004 us [99.742%], band: 2.003 us, 3.002 us, 4.007 us
01.0    : base: 1.001 us [99.856%], band: 2.001 us, 3.000 us, 4.005 us
...
```

**Comment dtc calcule les pourcentages** :
1. Lit le flux brut de la piste
2. Analyse les transitions de flux
3. Détecte les index marks et les secteurs
4. Calcule la cohérence temporelle (timing)
5. Convertit en pourcentage d'alignement basé sur :
   - La stabilité des timings
   - La cohérence des index marks
   - La qualité du signal

**Le pourcentage représente** :
- **99.911%** = La piste est lue avec 99.911% de cohérence par rapport à une référence idéale
- Plus le pourcentage est élevé, plus l'alignement est bon
- Les valeurs typiques :
  - **99.0% - 99.9%** : Alignement parfait
  - **97.0% - 98.9%** : Bon alignement
  - **96.0% - 96.9%** : Alignement moyen
  - **< 96.0%** : Mauvais alignement

---

## 🔄 Comparaison : ImageDisk vs Greaseweazle `align`

### ImageDisk `align()`

**Processus** :
1. Positionne la tête sur la piste
2. Lit les IDs de secteurs plusieurs fois
3. Compare les IDs entre les lectures
4. L'utilisateur/script calcule le pourcentage manuellement

**Sortie** :
```
Cylinder 40, Head 0 - Reading 1: 18 sectors detected
Cylinder 40, Head 0 - Reading 2: 18 sectors detected
Cylinder 40, Head 0 - Reading 3: 18 sectors detected
...
```

**Calcul du pourcentage** (fait manuellement ou par script) :
- Si 18/18 secteurs corrects à chaque lecture → ~100%
- Si 17/18 secteurs corrects → ~94.4%
- Si les IDs varient entre lectures → pourcentage réduit

### Greaseweazle `gw align`

**Processus** :
1. Positionne automatiquement la tête
2. Lit le flux brut plusieurs fois
3. Décode le format (si spécifié) ou analyse le flux brut
4. Affiche un résumé pour chaque lecture

**Sortie actuelle** :
```
Aligning T0.0, reading 2 times, revs=3
Format ibm.1440
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227897 flux in 599.09ms)
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)
```

**Ce qui manque** :
- ❌ Pas de calcul automatique de pourcentage d'alignement
- ❌ Pas de format `[XX.XXX%]` dans la sortie
- ❌ Pas d'analyse de cohérence entre lectures

---

## 💡 Pourquoi Notre Parser Ne Fonctionne Pas

### Problème Identifié

Notre parser (`alignment_parser.py`) cherche des lignes avec le format :
```
00.0    : base: 1.000 us [99.911%], band: 2.002 us, ...
```

Mais `gw align` produit :
```
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227897 flux in 599.09ms)
```

**Les deux formats sont différents** :
- **dtc (KryoFlux)** : Produit des pourcentages calculés automatiquement
- **gw align** : Produit des informations brutes (secteurs, flux, timing)

### Solution : Adapter le Parser ou Calculer les Pourcentages

Nous avons deux options :

#### Option 1 : Adapter le Parser pour Analyser la Sortie de `gw align`

Analyser la sortie de `gw align` et calculer les pourcentages nous-mêmes :

```python
# Exemple de sortie gw align
# T0.0: IBM MFM (18/18 sectors) from Raw Flux (227897 flux in 599.09ms)
# T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)

# Calcul du pourcentage basé sur :
# - Nombre de secteurs détectés vs attendus
# - Cohérence entre les lectures
# - Stabilité des timings
```

#### Option 2 : Utiliser une Méthode Similaire à ImageDisk

Implémenter une logique similaire à ImageDisk :
1. Lire la piste plusieurs fois
2. Analyser les IDs de secteurs détectés
3. Comparer entre les lectures
4. Calculer le pourcentage de cohérence

---

## 🎯 Comment ImageDisk Calcule Réellement l'Alignement

### Méthode 1 : Analyse des IDs de Secteurs

**Principe** :
- ImageDisk lit la piste plusieurs fois
- À chaque lecture, il détecte les IDs de secteurs (C, H, R, N)
- Si l'alignement est bon, les IDs sont cohérents entre les lectures
- Si l'alignement est mauvais, les IDs varient ou sont incorrects

**Calcul du pourcentage** :
```
Pourcentage = (Lectures avec IDs corrects / Total de lectures) × 100
```

**Exemple** :
- 10 lectures, 9 avec tous les IDs corrects → 90%
- 10 lectures, 10 avec tous les IDs corrects → 100%

### Méthode 2 : Analyse de la Stabilité des Timings

**Principe** :
- ImageDisk mesure les timings entre les index marks
- Si l'alignement est bon, les timings sont stables
- Si l'alignement est mauvais, les timings varient

**Calcul du pourcentage** :
```
Pourcentage = (1 - (Variation des timings / Timing moyen)) × 100
```

### Méthode 3 : Analyse du Flux Brut (comme dtc)

**Principe** (utilisé par dtc/KryoFlux) :
- Analyse les transitions de flux brutes
- Mesure la cohérence des index marks
- Calcule un pourcentage basé sur la qualité du signal

**C'est cette méthode qui produit les pourcentages `[99.911%]`**

---

## 🔧 Adaptation pour Notre Application

### Ce qu'il Faut Faire

Pour que notre application fonctionne avec `gw align`, nous devons :

1. **Adapter le parser** pour analyser la sortie de `gw align`
2. **Calculer les pourcentages** nous-mêmes basés sur :
   - Le nombre de secteurs détectés
   - La cohérence entre les lectures
   - La stabilité des timings

### Exemple d'Adaptation

```python
def parse_gw_align_output(line: str):
    """
    Parse la sortie de gw align et calcule un pourcentage
    Format: T0.0: IBM MFM (18/18 sectors) from Raw Flux (...)
    """
    # Extraire le nombre de secteurs
    # Exemple: "18/18 sectors" → 18 détectés sur 18 attendus = 100%
    # Exemple: "17/18 sectors" → 17 détectés sur 18 attendus = 94.4%
    
    # Pour plusieurs lectures, calculer la moyenne
    # Analyser la cohérence entre les lectures
    # Calculer le pourcentage final
```

---

## 📝 Conclusion

### Points Clés

1. **ImageDisk** ne produit pas directement des pourcentages `[XX.XXX%]`
2. **dtc (KryoFlux)** produit ces pourcentages via analyse du flux brut
3. **gw align** produit des informations brutes, pas de pourcentages calculés
4. **Notre parser** est conçu pour le format dtc, pas pour gw align

### Prochaines Étapes

1. **Adapter le parser** pour analyser la sortie de `gw align`
2. **Calculer les pourcentages** basés sur :
   - Secteurs détectés vs attendus
   - Cohérence entre lectures multiples
   - Stabilité des timings
3. **Implémenter la logique** similaire à ImageDisk ou dtc

---

---

## 🎮 Amiga Test Kit : Méthode de Test d'Alignement

### Vue d'Ensemble

L'**Amiga Test Kit** (testkit) est un outil de diagnostic Amiga qui inclut un test de calibration/alignement des têtes de disquette. Il utilise une approche similaire à ImageDisk mais adaptée au matériel Amiga.

### Fonction `drive_cal_test()` du Testkit

Le testkit implémente un test d'alignement continu dans la fonction `drive_cal_test()` (fichier `floppy.c`).

**Processus de test** :

1. **Sélection du lecteur** : Sélectionne le lecteur de disquette (DF0-DF3)
2. **Positionnement** : Se positionne sur un cylindre spécifique (0-79)
3. **Sélection de la tête** : Sélectionne la tête inférieure (0) ou supérieure (1)
4. **Lecture de la piste** : Lit le flux MFM brut de la piste
5. **Décodage MFM** : Décode la piste avec `mfm_decode_track()` pour extraire les en-têtes de secteurs
6. **Analyse des en-têtes** : Vérifie chaque secteur détecté

### Structure des En-têtes de Secteurs

Le testkit utilise une structure `sec_header` pour chaque secteur :

```c
struct sec_header {
    uint8_t format;      // Format du secteur (0xff pour AmigaDOS)
    uint8_t trk;         // Numéro de piste dans l'en-tête
    uint8_t sec;         // Numéro de secteur
    uint8_t togo;        // Secteurs restants jusqu'au gap
    uint32_t data_csum;  // Checksum des données
};
```

### Méthode de Détection d'Alignement

Le testkit détecte l'alignement en analysant les **numéros de cylindre** dans les en-têtes de secteurs :

```c
// Pour chaque secteur détecté
if ((h->format == 0xff) && !h->data_csum && (h->sec < 11)) {
    if (h->trk > trk) {
        // Cylindre détecté > cylindre attendu → tête trop haute
        map[h->sec] = '+';
    } else if (h->trk < trk) {
        // Cylindre détecté < cylindre attendu → tête trop basse
        map[h->sec] = '-';
    } else {
        // Cylindre détecté = cylindre attendu → alignement correct
        map[h->sec] = '.';
    }
}
```

**Symboles d'affichage** :
- **`.`** : Secteur valide avec le bon numéro de cylindre (alignement correct)
- **`X`** : Secteur manquant ou invalide
- **`+`** : Secteur détecté avec un numéro de cylindre supérieur (tête trop haute)
- **`-`** : Secteur détecté avec un numéro de cylindre inférieur (tête trop basse)

### Format de Sortie du Testkit

**Affichage en temps réel** :
```
Cyl 40 Head 0 (Lower): ........... (11/11 okay)
Cyl 40 Head 1 (Upper): ........... (11/11 okay)
```

**Exemple avec mauvais alignement** :
```
Cyl 40 Head 0 (Lower): ..+..+..+.. (8/11 okay)
Cyl 40 Head 1 (Upper): --..--..--. (6/11 okay)
```

### Calcul du Score d'Alignement

Le testkit calcule le score basé sur le **nombre de secteurs valides** :

```c
good = 0;
for (i = 0; i < 11; i++) {
    if (map[i] == '.')
        good++;
}
// Affiche: (good/11 okay)
```

**Pour une disquette DD Amiga** :
- **11/11 secteurs** → Alignement parfait (100%)
- **10/11 secteurs** → Bon alignement (~91%)
- **9/11 secteurs** → Alignement moyen (~82%)
- **< 9/11 secteurs** → Mauvais alignement

### Fonctionnalités Avancées

1. **Re-seek automatique** : Peut re-positionner automatiquement la tête à intervalles réguliers (0, 1, 2, 3, 5, 10, 30 secondes)
2. **Sélection de tête** : Teste les deux têtes ou une seule à la fois
3. **Navigation manuelle** : Permet de changer de cylindre pendant le test
4. **Affichage continu** : Met à jour l'affichage en temps réel avec un indicateur de progression

### Décodage MFM

Le testkit utilise `mfm_decode_track()` pour décoder le flux MFM brut :

```asm
mfm_decode_track:
    // Recherche les marqueurs de synchronisation 0x4489
    // Décode chaque en-tête de secteur (format, track, sector, togo)
    // Décode les données de chaque secteur
    // Vérifie les checksums
    // Retourne le nombre de secteurs détectés
```

**Processus de décodage** :
1. Recherche les marqueurs de synchronisation `0x4489`
2. Décode l'en-tête MFM (4 mots longs)
3. Décode les données du secteur (512 bytes)
4. Vérifie le checksum des données
5. Extrait les informations (format, track, sector)

### Comparaison : Testkit vs ImageDisk

| Caractéristique | ImageDisk | Amiga Test Kit |
|----------------|-----------|----------------|
| **Plateforme** | DOS/PC | Amiga natif |
| **Méthode** | Lecture répétée des IDs | Analyse des en-têtes MFM |
| **Affichage** | Liste des IDs | Carte visuelle des secteurs |
| **Score** | Pourcentage calculé | Nombre de secteurs valides |
| **Format** | IDs bruts (C,H,R,N) | En-têtes décodés (format,trk,sec) |
| **Temps réel** | Non | Oui (affichage continu) |

### Avantages de la Méthode Testkit

1. **Visuel** : La carte des secteurs (`...........`) est facile à interpréter
2. **Directionnel** : Les symboles `+` et `-` indiquent la direction du problème
3. **Temps réel** : Permet d'ajuster le lecteur pendant le test
4. **Précis** : Analyse les en-têtes réels plutôt que des IDs bruts
5. **Spécifique Amiga** : Comprend le format AmigaDOS (11 secteurs DD)

### Application à Notre Projet

**Ce que nous pouvons apprendre du testkit** :

1. **Méthode d'analyse** : Analyser les en-têtes de secteurs décodés plutôt que des IDs bruts
2. **Calcul du score** : Utiliser le ratio secteurs valides / secteurs attendus
3. **Détection directionnelle** : Identifier si la tête est trop haute ou trop basse
4. **Affichage visuel** : Fournir un feedback visuel clair à l'utilisateur

**Adaptation pour Greaseweazle** :

```python
# Pseudo-code inspiré du testkit
def analyze_alignment(flux_data, expected_track):
    sectors = decode_mfm_track(flux_data)
    valid_count = 0
    alignment_map = []
    
    for sector in sectors:
        if sector.format == 0xff and sector.checksum_valid:
            if sector.track == expected_track:
                alignment_map.append('.')  # OK
                valid_count += 1
            elif sector.track > expected_track:
                alignment_map.append('+')  # Trop haut
            else:
                alignment_map.append('-')  # Trop bas
        else:
            alignment_map.append('X')  # Manquant
    
    score = (valid_count / expected_sectors) * 100
    return alignment_map, score
```

---

## 📝 Conclusion

### Points Clés

1. **ImageDisk** ne produit pas directement des pourcentages `[XX.XXX%]`
2. **dtc (KryoFlux)** produit ces pourcentages via analyse du flux brut
3. **gw align** produit des informations brutes, pas de pourcentages calculés
4. **Amiga Test Kit** utilise une méthode visuelle basée sur l'analyse des en-têtes MFM
5. **Notre parser** est conçu pour le format dtc, pas pour gw align

### Prochaines Étapes

1. **Adapter le parser** pour analyser la sortie de `gw align`
2. **Calculer les pourcentages** basés sur :
   - Secteurs détectés vs attendus
   - Cohérence entre lectures multiples
   - Stabilité des timings
3. **Implémenter la logique** similaire à ImageDisk, dtc, ou testkit
4. **Ajouter un affichage visuel** inspiré du testkit (carte des secteurs)

---

## 🔧 Alignement Sans Oscilloscope avec Disquette de Référence

### Vue d'Ensemble

L'alignement des têtes de lecture des lecteurs de disquettes peut être effectué **sans oscilloscope** en utilisant une **disquette formatée en usine** comme référence. Cette méthode est largement utilisée dans la communauté de préservation de données et est considérée comme fiable pour la plupart des applications.

### Principe de Base

Une **disquette formatée en usine** (factory-formatted reference disk) garantit que :
- Les pistes sont correctement positionnées selon les spécifications du fabricant
- Les secteurs sont formatés avec une précision maximale
- La géométrie de la disquette est optimale pour servir de référence

**L'idée** : Si votre lecteur peut lire parfaitement cette disquette de référence, alors il est correctement aligné. Si des erreurs apparaissent, il faut ajuster les vis de réglage jusqu'à ce que la lecture soit optimale.

### Méthodes d'Alignement Sans Oscilloscope

#### Méthode 1 : Utilisation de Logiciels Spécialisés

**Outils disponibles** :
- **ImageDisk** : Outil DOS classique qui lit les IDs de secteurs de manière répétée
- **Amiga Test Kit** : Outil Amiga natif avec affichage visuel en temps réel
- **TrackDiskSync** : Logiciel Amiga avec signaux audio et visuels pour l'ajustement
- **KryoFlux/dtc** : Analyse les transitions de flux avec une résolution très fine
- **Greaseweazle** : Outil moderne avec commande `align` pour tests d'alignement

**Procédure typique** :
1. Insérer la disquette de référence formatée en usine
2. Lancer le logiciel de test sur une piste spécifique (généralement piste 40, tête 0)
3. Observer les résultats en temps réel
4. Ajuster les vis de réglage du lecteur (très délicat, nécessite des outils fins)
5. Continuer jusqu'à obtenir des résultats optimaux

#### Méthode 2 : Analyse des Erreurs de Lecture

**Principe** :
- Le logiciel lit la piste plusieurs fois (10-20 fois)
- À chaque lecture, il détecte les secteurs et compare avec les secteurs attendus
- Si l'alignement est bon : tous les secteurs sont détectés de manière cohérente
- Si l'alignement est mauvais : certains secteurs manquent ou varient entre lectures

**Indicateurs de bon alignement** :
- **100% des secteurs détectés** à chaque lecture
- **Cohérence parfaite** : les mêmes secteurs sont détectés à chaque lecture
- **Stabilité des timings** : les temps de révolution sont constants

**Indicateurs de mauvais alignement** :
- **Secteurs manquants** : moins de secteurs détectés que prévu
- **Variation entre lectures** : différents secteurs détectés à chaque lecture
- **Instabilité des timings** : temps de révolution variables

#### Méthode 3 : Analyse du Flux Brut (KryoFlux)

**Principe** (utilisé par KryoFlux/dtc) :
- Lit les **transitions de flux brutes** avec une résolution très fine
- Analyse la **cohérence des index marks**
- Calcule un **pourcentage d'alignement** basé sur :
  - La stabilité des timings
  - La cohérence des index marks
  - La qualité du signal

**Avantages** :
- Très précis (résolution temporelle fine)
- Indépendant du format de disquette
- Produit des pourcentages directement utilisables

**Inconvénients** :
- Nécessite un matériel spécialisé (KryoFlux)
- Plus complexe à interpréter pour les débutants

### Procédure d'Alignement Recommandée

#### Étape 1 : Préparation

1. **Obtenir une disquette de référence** :
   - Disquette formatée en usine (factory-formatted)
   - Format standard (IBM 1.44MB pour 3.5", IBM 1.2MB pour 5.25")
   - En bon état (pas de dommages physiques)

2. **Préparer le lecteur** :
   - Nettoyer les têtes de lecture
   - Vérifier que le lecteur fonctionne correctement
   - S'assurer que les vis de réglage sont accessibles

3. **Préparer les outils** :
   - Tournevis fin (pour les vis de réglage)
   - Logiciel de test installé et configuré
   - Matériel de connexion (Greaseweazle, KryoFlux, etc.)

#### Étape 2 : Test Initial

1. Insérer la disquette de référence
2. Lancer un test sur une piste centrale (piste 40, tête 0)
3. Observer les résultats :
   - Si **100% des secteurs** sont détectés de manière cohérente → alignement probablement bon
   - Si des **secteurs manquent** ou **varient** → alignement à ajuster

#### Étape 3 : Ajustement (si nécessaire)

1. **Identifier la direction du problème** :
   - Si la tête lit des secteurs de la piste adjacente (trop haute ou trop basse)
   - Observer les numéros de secteurs détectés pour déterminer la direction

2. **Ajuster les vis de réglage** :
   - **Très délicat** : les ajustements sont de l'ordre du millimètre
   - Ajuster **légèrement** (1/8 de tour ou moins)
   - Attendre que le lecteur se stabilise (1-2 secondes)

3. **Tester immédiatement** :
   - Relancer le test sur la même piste
   - Observer si les résultats s'améliorent ou se dégradent
   - Ajuster dans la direction qui améliore les résultats

4. **Répéter** jusqu'à obtenir des résultats optimaux

#### Étape 4 : Validation

1. **Tester plusieurs pistes** :
   - Piste 0 (bord extérieur)
   - Piste 40 (centre)
   - Piste 79 (bord intérieur)

2. **Tester les deux têtes** :
   - Tête 0 (inférieure)
   - Tête 1 (supérieure)

3. **Vérifier la cohérence** :
   - Tous les secteurs doivent être détectés
   - Les résultats doivent être stables entre les lectures

### Avantages de la Méthode Sans Oscilloscope

1. **Accessibilité** : Pas besoin d'équipement coûteux (oscilloscope)
2. **Simplicité** : Utilise des logiciels disponibles gratuitement
3. **Efficacité** : Permet un alignement précis avec une disquette de référence
4. **Flexibilité** : Peut être utilisé avec différents outils (ImageDisk, TestKit, Greaseweazle)

### Limitations

1. **Dépendance de la disquette de référence** :
   - La qualité de l'alignement dépend de la qualité de la disquette de référence
   - Une disquette endommagée donnera de mauvais résultats

2. **Précision** :
   - Moins précis qu'un oscilloscope professionnel
   - Suffisant pour la plupart des applications de préservation

3. **Temps de réglage** :
   - Peut prendre du temps pour trouver le réglage optimal
   - Nécessite de la patience et de la précision

### Conseils Pratiques

1. **Utiliser une piste centrale** (piste 40) pour l'ajustement initial
2. **Faire des ajustements très petits** (1/8 de tour ou moins)
3. **Tester immédiatement** après chaque ajustement
4. **Noter les résultats** pour suivre l'évolution
5. **Ne pas forcer** les vis de réglage (risque de casser le mécanisme)
6. **Utiliser un mode temps réel** pour voir les effets immédiatement

---

## 🚀 Propositions d'Amélioration pour AlignTester

### Analyse des Problèmes Actuels

#### Problème 1 : Mode Analyse - Résultats Aléatoires

**Symptômes** :
- Les résultats varient entre les exécutions
- Pas de cohérence dans les pourcentages calculés

**Causes identifiées** :
1. **Calcul de pourcentage simpliste** : Basé uniquement sur `secteurs_detected / sectors_expected * 100`
2. **Pas de validation de cohérence** : Ne vérifie pas si les résultats sont stables entre lectures
3. **Variations naturelles** : Les lectures peuvent varier légèrement même avec un bon alignement

**Solution proposée** :
- Implémenter un calcul de pourcentage basé sur la **moyenne de plusieurs lectures**
- Ajouter une **analyse de cohérence** (écart-type entre lectures)
- Ajuster le pourcentage en fonction de la cohérence (réduire si instable)

#### Problème 2 : Mode Manuel - Latence Élevée

**Symptômes** :
- Latence de ~700ms par lecture (600ms pour la lecture + 100ms d'attente)
- Difficile de régler en direct car on ne voit pas immédiatement les effets

**Causes identifiées** :
1. **Lecture complète** : Chaque lecture fait un tour complet de la piste (~600ms)
2. **Attente fixe** : 100ms d'attente entre chaque lecture
3. **Pas d'optimisation** : Pas de mode "rapide" pour le réglage en direct

**Solution proposée** :
- Implémenter un **Mode Direct** avec latence minimale
- Utiliser `--reads=1` pour une seule lecture rapide
- Réduire l'attente entre lectures (50ms au lieu de 100ms)
- Afficher les résultats immédiatement sans calculs complexes

#### Problème 3 : Mode Automatique - Faux Positifs

**Symptômes** :
- Annonce "correct" mais des pistes sont en défaut à la fin
- Des pistes hors limites sont comptées comme valides

**Causes identifiées** :
1. **Calcul de moyenne** : Moyenne toutes les pistes sans vérifier les limites du format
2. **Pas de validation** : Ne vérifie pas si les pistes sont dans les limites du format
3. **Seuil trop permissif** : Accepte des résultats qui devraient être rejetés

**Solution proposée** :
- **Mode Grande Précision** pour la vérification finale
- Utiliser `--reads=10-20` pour une analyse approfondie
- Valider que les pistes sont dans les limites du format
- Calculer des statistiques robustes (médiane, écart-type, etc.)

### Architecture Proposée : Trois Modes d'Opération

#### Mode 1 : Direct (Faible Latence) - Pour Réglage en Temps Réel

**Objectif** : Permettre un réglage en direct avec feedback immédiat

**Caractéristiques** :
- **Latence** : ~150-200ms par lecture
- **Précision** : Basique (suffisante pour voir la direction)
- **Lectures** : 1 seule lecture par itération
- **Calculs** : Minimal (juste secteurs détectés)
- **Affichage** : Immédiat, mise à jour continue

**Implémentation** :
```python
# Mode Direct
args = [
    "align",
    f"--tracks={tracks_spec}",
    "--reads=1",  # Une seule lecture
    f"--format={format_type}"
]
# Attente réduite : 50ms au lieu de 100ms
await asyncio.sleep(0.05)
```

**Utilisation** :
- Pendant le réglage des vis
- Pour voir immédiatement les effets des ajustements
- Pour trouver la direction générale du problème

#### Mode 2 : Ajustage Fin (Précision Modérée) - Pour Ajustements Fins

**Objectif** : Permettre des ajustements fins avec une précision acceptable

**Caractéristiques** :
- **Latence** : ~500-700ms par itération
- **Précision** : Modérée (bonne pour les ajustements fins)
- **Lectures** : 3-5 lectures par itération
- **Calculs** : Analyse de cohérence basique
- **Affichage** : Mise à jour après chaque itération

**Implémentation** :
```python
# Mode Ajustage Fin
args = [
    "align",
    f"--tracks={tracks_spec}",
    "--reads=3",  # 3 lectures pour cohérence
    f"--format={format_type}"
]
# Attente normale : 100ms
await asyncio.sleep(0.1)
# Calculer la cohérence entre les 3 lectures
consistency = calculate_consistency(readings)
```

**Utilisation** :
- Après le réglage grossier (Mode Direct)
- Pour affiner l'alignement
- Quand on veut un compromis latence/précision

#### Mode 3 : Grande Précision (Vérification Finale) - Pour Validation

**Objectif** : Vérifier l'alignement avec une précision maximale

**Caractéristiques** :
- **Latence** : ~2-3 secondes par piste
- **Précision** : Maximale (analyse approfondie)
- **Lectures** : 10-20 lectures par piste
- **Calculs** : Analyse complète (cohérence, stabilité, médiane)
- **Affichage** : Résultats détaillés après analyse complète

**Implémentation** :
```python
# Mode Grande Précision
args = [
    "align",
    f"--tracks={tracks_spec}",
    "--reads=15",  # 15 lectures pour précision maximale
    f"--format={format_type}"
]
# Analyse complète avec toutes les métriques
statistics = calculate_detailed_statistics(all_readings)
```

**Utilisation** :
- En mode automatique (scan de toutes les pistes)
- Pour validation finale après réglage
- Pour générer un rapport détaillé

### Comparaison avec les Solutions Existantes

| Caractéristique | ImageDisk | Amiga Test Kit | AlignTester Actuel | AlignTester Proposé |
|----------------|-----------|----------------|---------------------|---------------------|
| **Latence** | ~100ms | ~50ms | ~700ms | 150ms (Direct) / 500ms (Fin) / 2000ms (Précision) |
| **Précision** | Moyenne | Bonne | Variable | Adaptative (3 modes) |
| **Feedback temps réel** | Oui | Oui | Oui (mais lent) | Oui (3 niveaux) |
| **Calcul de pourcentage** | Manuel | Visuel | Automatique (simpliste) | Automatique (robuste) |
| **Validation** | Non | Basique | Partielle | Complète (Mode Précision) |

### Implémentation Technique

#### 1. Ajout d'un Paramètre de Mode

```python
class AlignmentMode(Enum):
    DIRECT = "direct"  # Faible latence, précision basique
    FINE_TUNE = "fine_tune"  # Latence modérée, précision modérée
    HIGH_PRECISION = "high_precision"  # Latence élevée, précision maximale
```

#### 2. Configuration par Mode

```python
MODE_CONFIG = {
    AlignmentMode.DIRECT: {
        "reads": 1,
        "delay_ms": 50,
        "calculate_consistency": False,
        "calculate_stability": False,
    },
    AlignmentMode.FINE_TUNE: {
        "reads": 3,
        "delay_ms": 100,
        "calculate_consistency": True,
        "calculate_stability": False,
    },
    AlignmentMode.HIGH_PRECISION: {
        "reads": 15,
        "delay_ms": 100,
        "calculate_consistency": True,
        "calculate_stability": True,
    }
}
```

#### 3. Calcul de Pourcentage Amélioré

```python
def calculate_robust_percentage(readings: List[AlignmentValue]) -> float:
    """
    Calcule un pourcentage robuste basé sur plusieurs lectures
    """
    if not readings:
        return 0.0
    
    # Calculer la médiane (plus robuste que la moyenne)
    percentages = [r.percentage for r in readings]
    median = statistics.median(percentages)
    
    # Calculer l'écart-type
    std_dev = statistics.stdev(percentages) if len(percentages) > 1 else 0
    
    # Ajuster en fonction de la cohérence
    # Si l'écart-type est élevé, réduire le pourcentage
    if std_dev > 2.0:
        # Pénalité pour incohérence
        adjusted = median * (1 - (std_dev / 100))
    else:
        adjusted = median
    
    return round(adjusted, 3)
```

#### 4. Interface Utilisateur

**Mode Manuel** :
- **Bouton "Mode Direct"** : Active le mode faible latence
- **Bouton "Ajustage Fin"** : Active le mode précision modérée
- **Indicateur visuel** : Affiche le mode actif et la latence estimée

**Mode Automatique** :
- **Utilise automatiquement le Mode Grande Précision**
- Affiche les résultats avec validation complète
- Signale les pistes hors limites

### Avantages de cette Approche

1. **Flexibilité** : Trois modes adaptés à différents besoins
2. **Précision adaptative** : Plus de précision quand nécessaire, moins de latence quand on ajuste
3. **Robustesse** : Calculs améliorés pour éviter les faux positifs
4. **Compatibilité** : S'inspire des meilleures pratiques (ImageDisk, TestKit)

### Plan d'Implémentation

1. **Phase 1** : Implémenter le Mode Direct (faible latence)
2. **Phase 2** : Implémenter le Mode Ajustage Fin
3. **Phase 3** : Améliorer le Mode Grande Précision (automatique)
4. **Phase 4** : Améliorer les calculs de pourcentage (robustesse)
5. **Phase 5** : Ajouter l'interface utilisateur pour sélectionner le mode

---

**Références** :
- Documentation ImageDisk (manuels originaux)
- Documentation dtc/KryoFlux
- Code source de Greaseweazle `align.py`
- Code source Amiga Test Kit (`floppy.c`, `mfm.S`) - v1.21
- Documentation TrackDiskSync (Aminet)
- Guides d'alignement de la communauté de préservation de données

