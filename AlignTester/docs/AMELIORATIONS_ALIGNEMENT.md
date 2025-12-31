# Améliorations de l'Alignement - Implémentation

Ce document décrit les améliorations apportées au système d'alignement d'AlignTester, inspirées des meilleures pratiques des outils de référence.

---

## ✅ Améliorations Implémentées

### 1. 🔍 Détection de Positionnement

**Fonctionnalité** : Détecte si la tête de lecture est correctement positionnée sur la piste.

**Implémentation** :
- Analyse de la variation des pourcentages entre les lectures multiples
- Classification du statut :
  - `correct` : Écart-type < 2.0% et pourcentage moyen ≥ 97%
  - `unstable` : Écart-type entre 2.0% et 5.0% ou pourcentage moyen entre 95% et 97%
  - `poor` : Écart-type > 5.0% ou pourcentage moyen < 95%

**Code** : `alignment_parser.py`, fonction `calculate_statistics()`

```python
# Détection de positionnement
positioning_status = "correct"
if len(percentages) > 1:
    std_dev = math.sqrt(sum((p - avg_percentage) ** 2 for p in percentages) / len(percentages))
    
    if std_dev > 2.0:
        positioning_status = "unstable"
    elif std_dev > 5.0:
        positioning_status = "poor"
    
    if avg_percentage < 95.0:
        positioning_status = "poor"
    elif avg_percentage < 97.0:
        positioning_status = "unstable"
```

---

### 2. 📊 Analyse de Cohérence

**Fonctionnalité** : Calcule la cohérence entre les lectures multiples d'une même piste.

**Implémentation** :
- Calcul de l'écart-type des pourcentages entre les lectures
- Conversion en score de cohérence (0-100) :
  - Écart-type de 0% = cohérence parfaite (100)
  - Écart-type de 5% = cohérence moyenne (50)
  - Écart-type de 10%+ = cohérence faible (0)

**Code** : `alignment_parser.py`, fonction `calculate_statistics()`

```python
# Analyse de cohérence
consistency = None
if len(percentages) > 1:
    mean = avg_percentage
    variance = sum((p - mean) ** 2 for p in percentages) / len(percentages)
    std_dev = math.sqrt(variance)
    
    # Convertir en score de cohérence (0-100)
    consistency = max(0, 100 - (std_dev * 20))
    consistency = min(100, consistency)
```

**Utilisation** :
- Le pourcentage final est ajusté si la cohérence est faible (< 80%)
- Aide à identifier les pistes avec des lectures incohérentes

---

### 3. ⚖️ Analyse de Stabilité

**Fonctionnalité** : Analyse la stabilité des timings et des flux transitions entre les lectures.

**Implémentation** :
- Analyse de la stabilité de `time_per_rev` (temps par révolution)
- Analyse de la stabilité de `flux_transitions` (transitions de flux)
- Analyse de la stabilité de `sectors_detected` (secteurs détectés)
- Calcul d'un score de stabilité global (0-100)

**Code** : `alignment_parser.py`, fonction `calculate_statistics()`

```python
# Analyse de stabilité
stability = None
if len(track_values) > 1:
    stability_scores = []
    
    # Stabilité des timings
    if all(v.time_per_rev is not None for v in track_values):
        times = [v.time_per_rev for v in track_values]
        mean_time = sum(times) / len(times)
        time_variance = max(times) - min(times)
        if mean_time > 0:
            time_stability = max(0, 100 - (time_variance / mean_time * 1000))
            stability_scores.append(time_stability)
    
    # Stabilité des flux transitions
    if all(v.flux_transitions is not None for v in track_values):
        fluxes = [v.flux_transitions for v in track_values]
        mean_flux = sum(fluxes) / len(fluxes)
        flux_variance = max(fluxes) - min(fluxes)
        if mean_flux > 0:
            flux_stability = max(0, 100 - (flux_variance / mean_flux * 100))
            stability_scores.append(flux_stability)
    
    # Stabilité des secteurs
    if all(v.sectors_detected is not None for v in track_values):
        sectors = [v.sectors_detected for v in track_values]
        sector_variance = max(sectors) - min(sectors)
        sector_stability = 100 if sector_variance == 0 else max(0, 100 - (sector_variance * 10))
        stability_scores.append(sector_stability)
    
    if stability_scores:
        stability = sum(stability_scores) / len(stability_scores)
```

**Utilisation** :
- Le pourcentage final est ajusté si la stabilité est faible (< 80%)
- Aide à identifier les pistes avec des timings instables

---

### 4. 🎨 Feedback Visuel

**Fonctionnalité** : Affichage visuel des résultats avec indicateurs de couleur et icônes.

**Implémentation Frontend** : `AlignmentResults.tsx`

#### Indicateurs de Pourcentage

- **Vert (✓)** : ≥ 99% - Alignement parfait
- **Bleu (○)** : 97-98.9% - Bon alignement
- **Jaune (⚠)** : 96-96.9% - Alignement moyen
- **Rouge (✗)** : < 96% - Mauvais alignement

#### Indicateurs de Cohérence

- **Vert** : ≥ 90% - Cohérence excellente
- **Jaune** : 70-89% - Cohérence moyenne
- **Rouge** : < 70% - Cohérence faible

#### Indicateurs de Stabilité

- **Vert** : ≥ 90% - Stabilité excellente
- **Jaune** : 70-89% - Stabilité moyenne
- **Rouge** : < 70% - Stabilité faible

#### Indicateurs de Positionnement

- **✓ (Vert)** : `correct` - Positionnement correct
- **↕ (Jaune)** : `unstable` - Positionnement instable
- **✗ (Rouge)** : `poor` - Mauvais positionnement

#### Tableau Détaillé

Le tableau affiche pour chaque piste :
- **Piste** : Numéro de piste (format XX.Y)
- **Pourcentage** : Avec icône et couleur
- **Secteurs** : Format X/Y
- **Cohérence** : Score en pourcentage avec couleur
- **Stabilité** : Score en pourcentage avec couleur
- **Position** : Icône et statut textuel
- **Statut** : Indicateur visuel (cercle coloré + flèches)

---

## 📊 Structure des Données

### AlignmentValue (Backend)

```python
@dataclass
class AlignmentValue:
    track: str
    percentage: float
    sectors_detected: Optional[int]
    sectors_expected: Optional[int]
    flux_transitions: Optional[int]
    time_per_rev: Optional[float]
    format_type: Optional[str]
    # Nouvelles métriques
    consistency: Optional[float]  # 0-100
    stability: Optional[float]     # 0-100
    positioning_status: Optional[str]  # "correct", "unstable", "poor"
```

### AlignmentValue (Frontend)

```typescript
interface AlignmentValue {
  track: string;
  percentage: number;
  sectors_detected?: number;
  sectors_expected?: number;
  flux_transitions?: number;
  time_per_rev?: number;
  format_type?: string;
  consistency?: number;
  stability?: number;
  positioning_status?: string;
}
```

---

## 🔄 Flux de Données

1. **Backend** : `gw align` → Parser → Calcul des métriques → WebSocket
2. **Frontend** : WebSocket → Mise à jour en temps réel → Affichage visuel

### Exemple de Données Envoyées

```json
{
  "track": "0.0",
  "percentage": 99.07,
  "sectors_detected": 18,
  "sectors_expected": 18,
  "flux_transitions": 227901,
  "time_per_rev": 599.10,
  "format_type": "ibm.1440",
  "consistency": 95.5,
  "stability": 98.2,
  "positioning_status": "correct"
}
```

---

## 🎯 Avantages des Améliorations

1. **Détection Précoce** : Identifie les problèmes de positionnement avant qu'ils ne deviennent critiques
2. **Analyse Approfondie** : Fournit des métriques détaillées pour chaque piste
3. **Feedback Immédiat** : Affichage visuel clair et intuitif
4. **Ajustement Automatique** : Le pourcentage est ajusté en fonction de la cohérence et stabilité

---

## 📝 Notes Techniques

### Ajustement du Pourcentage

Le pourcentage final est ajusté en fonction de la cohérence et de la stabilité :

```python
adjusted_percentage = avg_percentage
if consistency is not None and consistency < 80:
    adjusted_percentage *= (consistency / 100)
if stability is not None and stability < 80:
    adjusted_percentage = (adjusted_percentage + avg_percentage * (stability / 100)) / 2
```

### Seuils Utilisés

- **Cohérence faible** : < 80%
- **Stabilité faible** : < 80%
- **Positionnement instable** : Écart-type > 2.0%
- **Positionnement mauvais** : Écart-type > 5.0% ou pourcentage < 95%

---

## 🔮 Améliorations Futures Possibles

1. **Détection de Positionnement Plus Précise** : Analyser les IDs de secteurs si disponibles dans la sortie de `gw align`
2. **Historique des Tests** : Sauvegarder les résultats pour comparaison
3. **Recommandations** : Suggérer des ajustements basés sur les métriques
4. **Export des Données** : Permettre l'export CSV/JSON des résultats

---

## 📚 Références

- **Amiga Test Kit** : Inspiration pour la détection de positionnement
- **dtc (KryoFlux)** : Inspiration pour l'analyse de cohérence
- **ImageDisk** : Inspiration pour l'analyse de stabilité

---

## ✅ Tests

Pour tester les améliorations :

1. Démarrer un test d'alignement avec plusieurs lectures (`retries > 1`)
2. Observer le tableau détaillé avec les nouvelles métriques
3. Vérifier les indicateurs visuels (couleurs, icônes)
4. Analyser les scores de cohérence et stabilité

Les métriques sont calculées automatiquement lorsque plusieurs lectures sont effectuées pour une même piste.

