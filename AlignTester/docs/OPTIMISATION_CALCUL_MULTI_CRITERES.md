# Optimisation du Calcul Multi-Critères

## 📋 Vue d'ensemble

Ce document propose des optimisations pour améliorer la précision et la fiabilité du calcul multi-critères utilisé dans `alignment_parser.py` pour évaluer l'alignement d'un lecteur de disquettes.

---

## 🔍 Analyse du Calcul Actuel

### Formule Actuelle

```python
adjusted_percentage = (
    sector_score * 0.40 +      # 40% - Score basé sur les secteurs détectés
    quality_score * 0.30 +      # 30% - Moyenne de cohérence et stabilité
    azimuth_final * 0.15 +      # 15% - Score d'azimut
    asymmetry_final * 0.15      # 15% - Score d'asymétrie
)
```

### Problèmes Identifiés

1. **Valeurs par défaut problématiques** :
   - Si `azimuth_score` ou `asymmetry_score` sont `None`, on utilise `100.0`
   - Cela peut fausser le résultat vers le haut si les métriques ne sont pas disponibles
   - Un score de 100% par défaut n'est pas réaliste

2. **Pondération fixe** :
   - Les poids sont fixes (40%, 30%, 15%, 15%)
   - Pas d'adaptation selon la disponibilité des données
   - Pas d'adaptation selon la qualité des métriques

3. **Pas de normalisation** :
   - Les scores peuvent avoir des échelles différentes
   - Pas de vérification de cohérence entre les métriques

4. **Pas de seuils de confiance** :
   - On ne tient pas compte de la fiabilité de chaque métrique
   - Une métrique calculée avec peu de données devrait avoir moins de poids

5. **Pas de gestion des cas limites** :
   - Si une métrique est très mauvaise (< 50%), elle devrait avoir plus d'impact négatif
   - Les métriques critiques (secteurs) devraient avoir un poids minimum garanti

---

## 💡 Propositions d'Optimisation

### Proposition 1 : Pondération Adaptative selon la Disponibilité des Données

**Principe** : Ajuster les poids selon quelles métriques sont disponibles.

**Avantages** :
- Évite de pénaliser si une métrique n'est pas disponible (pas assez de lectures)
- Répartit le poids des métriques manquantes sur les métriques disponibles
- Plus réaliste que d'utiliser 100% par défaut

**Implémentation** :

```python
def calculate_adaptive_weights(
    has_sector_score: bool,
    has_quality_score: bool,
    has_azimuth: bool,
    has_asymmetry: bool
) -> Dict[str, float]:
    """
    Calcule les poids adaptatifs selon la disponibilité des métriques
    """
    # Poids de base (idéal)
    base_weights = {
        'sector': 0.40,
        'quality': 0.30,
        'azimuth': 0.15,
        'asymmetry': 0.15
    }
    
    # Identifier les métriques disponibles
    available = {
        'sector': has_sector_score,
        'quality': has_quality_score,
        'azimuth': has_azimuth,
        'asymmetry': has_asymmetry
    }
    
    # Calculer le poids total disponible
    total_available_weight = sum(
        base_weights[k] for k, v in available.items() if v
    )
    
    if total_available_weight == 0:
        # Aucune métrique disponible, utiliser poids par défaut
        return base_weights
    
    # Redistribuer les poids proportionnellement
    weights = {}
    for key in base_weights:
        if available[key]:
            # Redistribuer proportionnellement
            weights[key] = base_weights[key] / total_available_weight
        else:
            weights[key] = 0.0
    
    return weights
```

### Proposition 2 : Seuils de Confiance et Pondération par Fiabilité

**Principe** : Réduire le poids des métriques peu fiables (calculées avec peu de données).

**Avantages** :
- Les métriques calculées avec beaucoup de lectures ont plus de poids
- Les métriques calculées avec peu de lectures ont moins de poids
- Plus réaliste et fiable

**Implémentation** :

```python
def calculate_confidence_weights(
    num_readings: int,
    consistency: Optional[float],
    stability: Optional[float],
    azimuth_cv: Optional[float],
    asymmetry_percent: Optional[float]
) -> Dict[str, float]:
    """
    Calcule les poids en fonction de la confiance de chaque métrique
    """
    base_weights = {
        'sector': 0.40,
        'quality': 0.30,
        'azimuth': 0.15,
        'asymmetry': 0.15
    }
    
    # Facteurs de confiance (0.0 à 1.0)
    confidence_factors = {
        'sector': 1.0,  # Toujours disponible si on a des lectures
        'quality': min(1.0, num_readings / 3.0),  # Nécessite au moins 3 lectures
        'azimuth': min(1.0, num_readings / 3.0),  # Nécessite au moins 3 lectures
        'asymmetry': min(1.0, num_readings / 3.0)  # Nécessite au moins 3 lectures
    }
    
    # Ajuster les facteurs selon la disponibilité
    if consistency is None and stability is None:
        confidence_factors['quality'] = 0.0
    if azimuth_cv is None:
        confidence_factors['azimuth'] = 0.0
    if asymmetry_percent is None:
        confidence_factors['asymmetry'] = 0.0
    
    # Calculer les poids ajustés
    adjusted_weights = {
        k: base_weights[k] * confidence_factors[k]
        for k in base_weights
    }
    
    # Normaliser pour que la somme = 1.0
    total = sum(adjusted_weights.values())
    if total > 0:
        adjusted_weights = {k: v / total for k, v in adjusted_weights.items()}
    else:
        # Fallback : utiliser seulement le score de secteurs
        adjusted_weights = {'sector': 1.0, 'quality': 0.0, 'azimuth': 0.0, 'asymmetry': 0.0}
    
    return adjusted_weights
```

### Proposition 3 : Gestion des Cas Limites avec Impact Non-Linéaire

**Principe** : Si une métrique est très mauvaise (< 50%), elle devrait avoir un impact négatif plus important.

**Avantages** :
- Détecte mieux les problèmes critiques
- Évite les faux positifs (bon score alors qu'il y a un problème)
- Plus réaliste pour le diagnostic

**Implémentation** :

```python
def apply_non_linear_penalty(score: float, threshold: float = 50.0) -> float:
    """
    Applique une pénalité non-linéaire si le score est en dessous du seuil
    """
    if score >= threshold:
        return score
    else:
        # Pénalité quadratique pour les scores faibles
        # Exemple : score 30% → pénalité → ~18%
        penalty_factor = (score / threshold) ** 2
        return score * penalty_factor

# Utilisation dans le calcul
sector_score_penalized = apply_non_linear_penalty(sector_score, threshold=90.0)
quality_score_penalized = apply_non_linear_penalty(quality_score, threshold=70.0)
azimuth_final_penalized = apply_non_linear_penalty(azimuth_final, threshold=75.0)
asymmetry_final_penalized = apply_non_linear_penalty(asymmetry_final, threshold=75.0)
```

### Proposition 4 : Normalisation et Validation des Scores

**Principe** : S'assurer que tous les scores sont dans une plage valide et cohérente.

**Avantages** :
- Évite les erreurs de calcul
- Assure la cohérence des résultats
- Facilite le débogage

**Implémentation** :

```python
def normalize_score(score: Optional[float], default: float = 0.0, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Normalise un score dans la plage [min_val, max_val]
    """
    if score is None:
        return default
    
    # Clamper dans la plage valide
    score = max(min_val, min(max_val, score))
    
    return score

# Utilisation
sector_score = normalize_score(avg_percentage, default=0.0)
quality_score = normalize_score(quality_score, default=0.0)
azimuth_final = normalize_score(azimuth_score, default=0.0)  # 0 au lieu de 100 si non disponible
asymmetry_final = normalize_score(asymmetry_score, default=0.0)  # 0 au lieu de 100 si non disponible
```

### Proposition 5 : Calcul Final Optimisé (Combinant toutes les optimisations)

**Implémentation complète** :

```python
# Calcul multi-critères optimisé
def calculate_optimized_percentage(
    avg_percentage: float,
    consistency: Optional[float],
    stability: Optional[float],
    azimuth_score: Optional[float],
    azimuth_cv: Optional[float],
    asymmetry_score: Optional[float],
    asymmetry_percent: Optional[float],
    num_readings: int
) -> float:
    """
    Calcule le pourcentage d'alignement avec pondération adaptative et gestion des cas limites
    """
    # 1. Normaliser les scores
    sector_score = normalize_score(avg_percentage, default=0.0)
    
    quality_score = 0.0
    if consistency is not None and stability is not None:
        quality_score = normalize_score((consistency + stability) / 2, default=0.0)
    elif consistency is not None:
        quality_score = normalize_score(consistency, default=0.0)
    elif stability is not None:
        quality_score = normalize_score(stability, default=0.0)
    
    azimuth_final = normalize_score(azimuth_score, default=0.0)  # 0 si non disponible
    asymmetry_final = normalize_score(asymmetry_score, default=0.0)  # 0 si non disponible
    
    # 2. Calculer les poids adaptatifs
    weights = calculate_confidence_weights(
        num_readings=num_readings,
        consistency=consistency,
        stability=stability,
        azimuth_cv=azimuth_cv,
        asymmetry_percent=asymmetry_percent
    )
    
    # 3. Appliquer les pénalités non-linéaires pour les scores faibles
    sector_score_penalized = apply_non_linear_penalty(sector_score, threshold=90.0)
    quality_score_penalized = apply_non_linear_penalty(quality_score, threshold=70.0)
    azimuth_final_penalized = apply_non_linear_penalty(azimuth_final, threshold=75.0)
    asymmetry_final_penalized = apply_non_linear_penalty(asymmetry_final, threshold=75.0)
    
    # 4. Calcul final avec poids adaptatifs
    adjusted_percentage = (
        sector_score_penalized * weights['sector'] +
        quality_score_penalized * weights['quality'] +
        azimuth_final_penalized * weights['azimuth'] +
        asymmetry_final_penalized * weights['asymmetry']
    )
    
    # 5. Clamper le résultat final dans [0, 100]
    adjusted_percentage = max(0.0, min(100.0, adjusted_percentage))
    
    return adjusted_percentage
```

---

## 📊 Comparaison : Avant vs Après

### Scénario 1 : Toutes les métriques disponibles

**Avant** :
- Sector: 95%, Quality: 90%, Azimuth: 85%, Asymmetry: 80%
- Calcul: `95*0.40 + 90*0.30 + 85*0.15 + 80*0.15 = 90.25%`

**Après** (avec optimisations) :
- Même calcul si toutes les métriques sont fiables
- Résultat similaire mais avec validation et normalisation

### Scénario 2 : Métriques manquantes (peu de lectures)

**Avant** :
- Sector: 95%, Quality: None, Azimuth: None, Asymmetry: None
- Calcul: `95*0.40 + 100*0.30 + 100*0.15 + 100*0.15 = 98%` ❌ (Faux positif)

**Après** (avec optimisations) :
- Sector: 95%, Quality: 0 (non disponible), Azimuth: 0, Asymmetry: 0
- Poids redistribués: Sector: 100%, Quality: 0%, Azimuth: 0%, Asymmetry: 0%
- Calcul: `95*1.0 = 95%` ✅ (Plus réaliste)

### Scénario 3 : Métrique critique très faible

**Avant** :
- Sector: 30%, Quality: 90%, Azimuth: 85%, Asymmetry: 80%
- Calcul: `30*0.40 + 90*0.30 + 85*0.15 + 80*0.15 = 63.75%` (Peut masquer le problème)

**Après** (avec optimisations) :
- Sector: 30% → pénalité → ~10%
- Calcul: `10*0.40 + 90*0.30 + 85*0.15 + 80*0.15 = 54.25%` ✅ (Détecte mieux le problème)

---

## 🎯 Recommandations d'Implémentation

### Phase 1 : Corrections Immédiates (Priorité Haute)

1. **Remplacer les valeurs par défaut 100.0 par 0.0** :
   - Si une métrique n'est pas disponible, utiliser 0.0 au lieu de 100.0
   - Cela évite les faux positifs

2. **Implémenter la pondération adaptative** :
   - Redistribuer les poids si des métriques sont manquantes
   - Plus réaliste que d'utiliser des valeurs par défaut

### Phase 2 : Améliorations Moyen Terme (Priorité Moyenne)

3. **Ajouter les seuils de confiance** :
   - Réduire le poids des métriques calculées avec peu de données
   - Augmenter le poids des métriques fiables

4. **Implémenter la normalisation** :
   - S'assurer que tous les scores sont dans [0, 100]
   - Valider les entrées

### Phase 3 : Optimisations Avancées (Priorité Basse)

5. **Ajouter les pénalités non-linéaires** :
   - Détecter mieux les problèmes critiques
   - Éviter les faux positifs

6. **Ajouter des métriques de confiance** :
   - Afficher la confiance de chaque métrique dans l'interface
   - Aider l'utilisateur à interpréter les résultats

---

## 📝 Code Proposé pour `alignment_parser.py`

```python
def calculate_optimized_multi_criteria(
    avg_percentage: float,
    consistency: Optional[float],
    stability: Optional[float],
    azimuth_score: Optional[float],
    azimuth_cv: Optional[float],
    asymmetry_score: Optional[float],
    asymmetry_percent: Optional[float],
    num_readings: int
) -> Tuple[float, Dict[str, float]]:
    """
    Calcule le pourcentage d'alignement avec pondération adaptative
    
    Returns:
        (adjusted_percentage, weights_used)
    """
    # Normaliser les scores (0 si non disponible au lieu de 100)
    sector_score = max(0.0, min(100.0, avg_percentage))
    
    quality_score = 0.0
    if consistency is not None and stability is not None:
        quality_score = max(0.0, min(100.0, (consistency + stability) / 2))
    elif consistency is not None:
        quality_score = max(0.0, min(100.0, consistency))
    elif stability is not None:
        quality_score = max(0.0, min(100.0, stability))
    
    azimuth_final = max(0.0, min(100.0, azimuth_score)) if azimuth_score is not None else 0.0
    asymmetry_final = max(0.0, min(100.0, asymmetry_score)) if asymmetry_score is not None else 0.0
    
    # Calculer les poids adaptatifs
    has_quality = quality_score > 0
    has_azimuth = azimuth_final > 0
    has_asymmetry = asymmetry_final > 0
    
    # Poids de base
    base_weights = {
        'sector': 0.40,
        'quality': 0.30 if has_quality else 0.0,
        'azimuth': 0.15 if has_azimuth else 0.0,
        'asymmetry': 0.15 if has_asymmetry else 0.0
    }
    
    # Facteurs de confiance basés sur le nombre de lectures
    confidence_factors = {
        'sector': 1.0,  # Toujours fiable
        'quality': min(1.0, num_readings / 3.0) if has_quality else 0.0,
        'azimuth': min(1.0, num_readings / 3.0) if has_azimuth else 0.0,
        'asymmetry': min(1.0, num_readings / 3.0) if has_asymmetry else 0.0
    }
    
    # Ajuster les poids avec les facteurs de confiance
    adjusted_weights = {
        k: base_weights[k] * confidence_factors[k]
        for k in base_weights
    }
    
    # Normaliser pour que la somme = 1.0
    total_weight = sum(adjusted_weights.values())
    if total_weight > 0:
        adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}
    else:
        # Fallback : utiliser seulement le score de secteurs
        adjusted_weights = {'sector': 1.0, 'quality': 0.0, 'azimuth': 0.0, 'asymmetry': 0.0}
    
    # Appliquer des pénalités non-linéaires pour les scores très faibles
    def apply_penalty(score: float, threshold: float = 50.0) -> float:
        if score >= threshold:
            return score
        # Pénalité quadratique pour les scores < threshold
        penalty_factor = (score / threshold) ** 2
        return score * penalty_factor
    
    sector_penalized = apply_penalty(sector_score, threshold=90.0)
    quality_penalized = apply_penalty(quality_score, threshold=70.0) if has_quality else 0.0
    azimuth_penalized = apply_penalty(azimuth_final, threshold=75.0) if has_azimuth else 0.0
    asymmetry_penalized = apply_penalty(asymmetry_final, threshold=75.0) if has_asymmetry else 0.0
    
    # Calcul final
    adjusted_percentage = (
        sector_penalized * adjusted_weights['sector'] +
        quality_penalized * adjusted_weights['quality'] +
        azimuth_penalized * adjusted_weights['azimuth'] +
        asymmetry_penalized * adjusted_weights['asymmetry']
    )
    
    # Clamper dans [0, 100]
    adjusted_percentage = max(0.0, min(100.0, adjusted_percentage))
    
    return adjusted_percentage, adjusted_weights
```

---

## ✅ Conclusion

Les optimisations proposées permettront :

1. **Éviter les faux positifs** : Utiliser 0.0 au lieu de 100.0 pour les métriques manquantes
2. **Pondération adaptative** : Ajuster les poids selon la disponibilité des données
3. **Seuils de confiance** : Réduire le poids des métriques peu fiables
4. **Gestion des cas limites** : Détecter mieux les problèmes critiques avec des pénalités non-linéaires
5. **Normalisation** : Assurer la cohérence des résultats

Ces améliorations rendront le calcul multi-critères plus fiable et plus réaliste, surtout dans les cas où certaines métriques ne sont pas disponibles ou sont peu fiables.

