# Contrôle du Bouton "Analyse"

## 📍 Emplacement

Le bouton **"Analyse"** est maintenant situé **juste après la sélection du format de disquette**, dans une section **toujours visible** et **toujours accessible**, indépendamment de l'état du mode manuel.

## 🎯 Ce que fait le bouton "Analyse"

### Fonctionnement détaillé

Quand vous cliquez sur le bouton "Analyse", voici ce qui se passe **étape par étape** :

#### 1. Préparation
- ✅ Vérifie que Greaseweazle est disponible (`alignAvailable`)
- ✅ Met à jour le format sélectionné dans les paramètres
- ✅ Détermine quelle piste analyser :
  - **Si le mode manuel est démarré** : Analyse la piste actuelle (`current_track`, `current_head`)
  - **Si le mode manuel n'est pas démarré** : Se positionne automatiquement sur la piste **T0.0** et l'analyse

#### 2. Positionnement (si nécessaire)
Si le mode manuel n'est pas démarré :
- Exécute `gw seek 0` pour se positionner sur la piste 0
- Sélectionne la tête 0 par défaut

#### 3. Exécution de la commande Greaseweazle
Exécute la commande suivante :
```bash
gw align --tracks=c=<track>:h=<head> --reads=3 --format=<format_selectionné>
```

**Paramètres** :
- `--tracks=c=<track>:h=<head>` : Piste et tête à analyser
- `--reads=3` : Nombre de lectures (par défaut 3, configurable)
- `--format=<format>` : Format de disquette sélectionné (ex: `ibm.1440`, `ibm.720`)

#### 4. Lecture multiple
La piste est lue **3 fois** (par défaut) pour :
- Évaluer la **cohérence** entre les lectures
- Détecter les **variations** dans les mesures
- Calculer des **statistiques fiables**

#### 5. Analyse des résultats
Pour chaque lecture, le système analyse :

**a) Informations de base**
- **Secteurs détectés** : Nombre de secteurs trouvés
- **Secteurs attendus** : Nombre selon le format
- **Pourcentage d'alignement** : `(secteurs_détectés / secteurs_attendus) × 100`

**b) Informations de flux**
- **Transitions de flux** : Nombre de transitions magnétiques
- **Temps par révolution** : Durée d'une rotation (ms)
- **Densité de flux** : `transitions / temps_par_révolution`

**c) Validation du format**
- **Dans les limites ?** : La piste est-elle dans la plage valide ?
  - Ex: IBM 1440 = pistes 0-79
  - Si piste > 79 → Avertissement mais données conservées
- **Formatage détecté ?** : La piste est-elle réellement formatée ?
  - Analyse du flux brut
  - Ratio secteurs détectés/attendus
  - Niveau de confiance (0-100%)

**d) Métriques avancées**
- **Cohérence** : Stabilité des pourcentages entre lectures (0-100)
- **Stabilité** : Stabilité des timings et flux (0-100)
- **Statut de positionnement** : "correct", "unstable", ou "poor"

#### 6. Calcul des statistiques
Les résultats de toutes les lectures sont agrégés :
- Moyenne des pourcentages
- Écart-type (cohérence)
- Variance des timings (stabilité)
- Détection de formatage

#### 7. Résultat retourné
Un objet `TrackReading` est créé avec toutes les informations et affiché dans l'interface.

---

## 🎮 Comment contrôler ce que fait le bouton

### Contrôle 1 : Format de disquette

**Avant de cliquer sur "Analyse"** :
1. Sélectionnez le format dans le menu déroulant (ex: `ibm.1440`, `ibm.720`)
2. Le bouton utilisera automatiquement ce format lors de l'analyse

**Exemple** :
- Format sélectionné : `ibm.1440` → Attend 18 secteurs par piste
- Format sélectionné : `ibm.720` → Attend 9 secteurs par piste

### Contrôle 2 : Piste à analyser

**Option A : Mode manuel démarré**
1. Démarrez le mode manuel (bouton "Démarrer le mode manuel")
2. Naviguez vers la piste souhaitée avec les boutons +/- ou les sauts rapides (1-8)
3. Cliquez sur "Analyse" → Analyse la piste actuelle

**Option B : Mode manuel non démarré**
1. Cliquez directement sur "Analyse"
2. La piste **T0.0** sera analysée par défaut
3. Pour analyser une autre piste, démarrez d'abord le mode manuel

### Contrôle 3 : Nombre de lectures

**Actuellement** : 3 lectures par défaut (configurable dans le backend via `num_reads`)

**Pour modifier** :
- Modifier `state.num_reads` dans le backend (valeur par défaut : 3)
- Plus de lectures = résultats plus fiables mais analyse plus longue

### Contrôle 4 : Tête (Head)

**Si le mode manuel est démarré** :
- Utilise la tête actuellement sélectionnée (`current_head`)
- Changez la tête avec le bouton "Tête 0/1 (H)" avant d'analyser

**Si le mode manuel n'est pas démarré** :
- Utilise la tête 0 par défaut

---

## 📊 Exemple d'utilisation

### Scénario 1 : Vérifier l'alignement d'une piste spécifique

1. **Démarrer le mode manuel**
2. **Naviguer vers la piste 40** (bouton "40" ou touches +/-)
3. **Sélectionner le format** : `ibm.1440`
4. **Cliquer sur "Analyse"**
5. **Résultat** : Analyse de la piste T40.0 avec le format IBM 1440

### Scénario 2 : Tester si un format correspond à la disquette

1. **Sélectionner un format** : `ibm.720`
2. **Cliquer sur "Analyse"** (même sans démarrer le mode manuel)
3. **Résultat** : Analyse de la piste T0.0 avec le format IBM 720
4. **Vérifier** :
   - `is_formatted` : La piste est-elle formatée ?
   - `format_confidence` : Niveau de confiance
   - `sectors_detected` : Nombre de secteurs trouvés (devrait être 9 pour IBM 720)

### Scénario 3 : Diagnostiquer un problème d'alignement

1. **Démarrer le mode manuel**
2. **Naviguer vers une piste problématique**
3. **Sélectionner le bon format**
4. **Cliquer sur "Analyse"**
5. **Examiner** :
   - `consistency` : Les lectures sont-elles cohérentes ?
   - `stability` : Les timings sont-ils stables ?
   - `positioning_status` : "unstable" ou "poor" indique un problème

---

## 🔧 Paramètres configurables

### Dans le backend (`manual_alignment.py`)

```python
self.state.num_reads = 3  # Nombre de lectures (défaut: 3)
self.state.format_type = "ibm.1440"  # Format par défaut
```

### Dans l'interface

- **Format** : Menu déroulant (toujours visible)
- **Piste** : Navigation avec boutons +/- ou sauts rapides (si mode démarré)
- **Tête** : Bouton "Tête 0/1 (H)" (si mode démarré)

---

## ⚠️ Limitations et comportements

### Si le mode manuel n'est pas démarré
- ✅ Le bouton fonctionne quand même
- ✅ Analyse automatiquement la piste **T0.0**
- ⚠️ Vous ne pouvez pas choisir une autre piste sans démarrer le mode manuel

### Si le mode manuel est démarré
- ✅ Analyse la piste actuellement sélectionnée
- ✅ Vous pouvez naviguer vers n'importe quelle piste avant d'analyser
- ✅ Vous pouvez changer de tête avant d'analyser

### Si `alignAvailable` est false
- ❌ Le bouton est désactivé
- ⚠️ Message d'erreur affiché : "La commande align n'est pas disponible"
- 💡 Vérifiez que Greaseweazle est installé et configuré

---

## 📝 Résultat de l'analyse

Après avoir cliqué sur "Analyse", vous obtiendrez :

### Dans l'interface
- **Pourcentage d'alignement** : Affiché en grand
- **Qualité** : Perfect / Good / Average / Poor
- **Secteurs** : X/Y secteurs détectés
- **Indicateurs visuels** : Barres de qualité, direction, recommandation

### Dans les données techniques (console/API)
```json
{
  "track": 40,
  "head": 0,
  "percentage": 99.5,
  "sectors_detected": 18,
  "sectors_expected": 18,
  "is_formatted": true,
  "format_confidence": 100.0,
  "format_status_message": "Piste formatée détectée (18/18 secteurs, 100.0% confiance)",
  "is_in_format_range": true,
  "format_warning": null,
  "consistency": 98.5,
  "stability": 97.2
}
```

---

## 🎹 Raccourci clavier

- **Touche A** : Lance l'analyse de la piste actuelle
  - Fonctionne même si le mode manuel n'est pas démarré
  - Utilise le format actuellement sélectionné

---

## 💡 Conseils d'utilisation

1. **Toujours sélectionner le format** avant d'analyser
   - Le format détermine le nombre de secteurs attendus
   - Un mauvais format donnera des résultats incorrects

2. **Pour tester plusieurs pistes** :
   - Démarrez le mode manuel
   - Naviguez vers chaque piste
   - Cliquez sur "Analyse" pour chaque piste

3. **Pour tester plusieurs formats** :
   - Changez le format dans le menu
   - Cliquez sur "Analyse" pour chaque format
   - Comparez les résultats

4. **Interpréter les résultats** :
   - `is_formatted: false` → La piste n'est probablement pas formatée
   - `is_in_format_range: false` → La piste est hors limites du format
   - `consistency < 80` → Les lectures varient beaucoup, problème d'alignement possible
   - `stability < 80` → Les timings sont instables, problème mécanique possible

