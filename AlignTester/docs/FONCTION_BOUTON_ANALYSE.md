# Fonctionnement du Bouton "Analyse"

## 📋 Vue d'Ensemble

Le bouton **"Analyse"** (raccourci clavier : **A**) permet d'effectuer une analyse approfondie de la piste actuelle avec le format de disquette sélectionné.

## 🔍 Ce que fait le bouton "Analyse"

### 1. Préparation

1. **Vérification du mode manuel** : Le mode manuel doit être démarré (actuellement requis)
2. **Mise à jour du format** : Le format sélectionné dans l'interface est appliqué
3. **Positionnement** : Utilise la piste et la tête actuellement sélectionnées (`current_track`, `current_head`)

### 2. Exécution de la commande Greaseweazle

Le bouton exécute la commande suivante :

```bash
gw align --tracks=c=<track>:h=<head> --reads=<num_reads> --format=<format_type>
```

**Paramètres** :
- `--tracks=c=<track>:h=<head>` : Piste et tête à analyser
- `--reads=<num_reads>` : Nombre de lectures (par défaut : 3)
- `--format=<format_type>` : Format de disquette (ex: `ibm.1440`, `ibm.720`)

### 3. Lecture multiple de la piste

La piste est lue **plusieurs fois** (par défaut 3 fois) pour :
- **Évaluer la cohérence** : Les résultats sont-ils stables entre les lectures ?
- **Détecter les variations** : Y a-t-il des fluctuations dans les mesures ?
- **Calculer des statistiques** : Moyenne, écart-type, stabilité

### 4. Analyse des résultats

Pour chaque lecture, le système analyse :

#### a) Informations de base
- **Secteurs détectés** : Nombre de secteurs trouvés sur la piste
- **Secteurs attendus** : Nombre de secteurs selon le format
- **Pourcentage d'alignement** : `(secteurs_détectés / secteurs_attendus) × 100`

#### b) Informations de flux
- **Transitions de flux** : Nombre de transitions magnétiques détectées
- **Temps par révolution** : Durée d'une rotation complète en ms
- **Densité de flux** : `transitions / temps_par_révolution`

#### c) Validation du format
- **Dans les limites** : La piste est-elle dans la plage valide du format ?
  - Ex: IBM 1440 = pistes 0-79
  - Si piste > 79 → Avertissement mais données conservées
- **Formatage détecté** : La piste est-elle réellement formatée ?
  - Analyse du flux brut
  - Ratio secteurs détectés/attendus
  - Niveau de confiance (0-100%)

#### d) Métriques avancées
- **Cohérence** : Stabilité des pourcentages entre les lectures
  - Écart-type des mesures
  - Score de cohérence (0-100)
- **Stabilité** : Stabilité des timings et flux
  - Variance des temps par révolution
  - Variance des transitions de flux
  - Score de stabilité (0-100)
- **Statut de positionnement** : "correct", "unstable", ou "poor"

### 5. Calcul des statistiques

Les résultats de toutes les lectures sont agrégés :

```python
# Moyenne des pourcentages
average_percentage = mean([reading1.percentage, reading2.percentage, ...])

# Cohérence (écart-type)
consistency = 100 - (std_dev * 20)

# Stabilité (variance des timings/flux)
stability = calculate_stability_scores(...)

# Détection de formatage
format_status = analyze_track_format_status(
    flux_transitions, time_per_rev,
    sectors_detected, sectors_expected, format_type
)
```

### 6. Résultat retourné

Le bouton retourne un objet `TrackReading` avec :

```json
{
  "track": 40,
  "head": 0,
  "percentage": 99.5,
  "sectors_detected": 18,
  "sectors_expected": 18,
  "flux_transitions": 100000,
  "time_per_rev": 200.0,
  "consistency": 98.5,
  "stability": 97.2,
  "quality": "Perfect",
  "is_formatted": true,
  "format_confidence": 100.0,
  "format_status_message": "Piste formatée détectée (18/18 secteurs, 100.0% confiance)",
  "is_in_format_range": true,
  "format_warning": null,
  "timestamp": "2024-01-15T10:30:00",
  "raw_output": "..."
}
```

## 🎯 Cas d'usage

### Cas 1 : Vérifier l'alignement d'une piste spécifique
1. Naviguer vers la piste (ex: piste 40)
2. Sélectionner le format (ex: IBM 1440)
3. Cliquer sur "Analyse"
4. Examiner les résultats :
   - Pourcentage d'alignement
   - Cohérence et stabilité
   - Statut de formatage

### Cas 2 : Tester si un format correspond à la disquette
1. Sélectionner un format (ex: IBM 720)
2. Naviguer vers une piste connue (ex: piste 0)
3. Cliquer sur "Analyse"
4. Vérifier :
   - `is_formatted` : La piste est-elle formatée ?
   - `format_confidence` : Niveau de confiance
   - `sectors_detected` : Nombre de secteurs trouvés

### Cas 3 : Diagnostiquer un problème d'alignement
1. Naviguer vers une piste problématique
2. Cliquer sur "Analyse"
3. Examiner :
   - `consistency` : Les lectures sont-elles cohérentes ?
   - `stability` : Les timings sont-ils stables ?
   - `positioning_status` : "unstable" ou "poor" indique un problème

## ⚠️ Limitations actuelles

1. **Mode manuel requis** : Le bouton nécessite que le mode manuel soit démarré
2. **Positionnement préalable** : Il faut d'abord se positionner sur la piste avec les contrôles de navigation

## 🔄 Différence avec les lectures continues

| Aspect | Lectures continues | Bouton "Analyse" |
|--------|-------------------|------------------|
| **Fréquence** | ~10 fois/seconde | 1 fois (sur demande) |
| **Nombre de lectures** | 1 par itération | 3 (configurable) |
| **Format** | Utilise le format actuel | Met à jour le format avant |
| **Statistiques** | Basiques | Complètes (cohérence, stabilité) |
| **Détection formatage** | Oui | Oui (plus détaillée) |
| **Utilisation** | Automatique | Manuelle (bouton) |

## 📊 Exemple de sortie

```
Analyse de la piste 40.0 (IBM 1440) :
- Lecture 1 : 18/18 secteurs détectés, 99.5%
- Lecture 2 : 18/18 secteurs détectés, 99.6%
- Lecture 3 : 18/18 secteurs détectés, 99.4%

Résultats :
- Pourcentage moyen : 99.5%
- Cohérence : 98.5% (écart-type faible)
- Stabilité : 97.2% (timings stables)
- Formatage : Oui (100% confiance)
- Dans limites : Oui (piste 40 ≤ 79)
- Qualité : Perfect
```

## 🎹 Raccourci clavier

- **Touche A** : Lance l'analyse de la piste actuelle

## 🔧 Configuration

Le nombre de lectures peut être configuré via `num_reads` (par défaut : 3).

Plus de lectures = résultats plus fiables mais analyse plus longue.

