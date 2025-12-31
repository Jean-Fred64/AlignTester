# Propositions pour Fiabiliser la Méthode d'Alignement

## 📚 Références Techniques

Ce document intègre les procédures d'alignement du **Manuel de Service Panasonic JU-253** (MSD870909100) pour les lecteurs de disquette 3.5 pouces JU-253-T/P/PK. Les sections pertinentes du manuel incluent :

- **Section 9.6** : Radial Alignment Adjustment (pages 8-9) - Alignement radial des têtes
- **Section 9.7** : Azimuth Verification (pages 9-10) - Vérification de l'azimut
- **Section 9.8** : Index Burst Verification and Adjustment - Vérification du signal d'index
- **Section 9.9** : Track 00 Sensor Adjustment (pages 10-11) - Ajustement du capteur Track 0
- **Section 9.10** : Asymmetry Verification (page 12) - Vérification de l'asymétrie du signal
- **Section 11** : Panasonic Alignment Diskette - Disque d'alignement de référence

Ces procédures sont adaptées pour fonctionner **sans oscilloscope** en utilisant des métriques logicielles dérivées des lectures de flux brut via Greaseweazle.

---

## 🔍 Problème Identifié

### Symptôme
Au-delà de la piste 79 pour les formats IBM 1440 et IBM 720, on constate des mesures d'alignement à 100% alors que ces pistes ne devraient pas être formatées (zone non formatée de la disquette).

### Cause Racine
Le calcul actuel du pourcentage d'alignement est trop simpliste :
- Il se base uniquement sur le ratio `secteurs_detectés / secteurs_attendus * 100`
- Il ne vérifie **pas** si la piste est dans la plage valide du format
- Il ne vérifie **pas** la cohérence des IDs de secteurs (numéro de cylindre, tête, secteur)
- Il ne distingue **pas** entre une piste formatée et une piste non formatée avec du flux résiduel

### Conséquence
- **Faux positifs** : Des pistes non formatées sont considérées comme bien alignées
- **Fiabilité réduite** : Les mesures ne reflètent pas la réalité de l'alignement
- **Confusion** : L'utilisateur ne peut pas faire confiance aux résultats

---

## 📋 Propositions d'Amélioration

### Proposition 1 : Validation des Limites de Format (Informatif, Non Bloquant)

#### Principe
Vérifier si la piste testée est dans la plage valide du format et afficher un indicateur informatif. **Cette validation n'est PAS bloquante** - on peut toujours tester au-delà des limites pour voir ce que le lecteur lit, mais ces pistes ne sont **pas incluses dans le calcul final de l'alignement**.

#### Comportement
- ✅ **Permet de tester toutes les pistes** (y compris > 79 pour IBM 720/1440)
- ✅ **Affiche un indicateur visuel** pour les pistes hors limites
- ✅ **Exclut les pistes hors limites du calcul final** de l'alignement
- ✅ **Conserve toutes les données** pour affichage informatif

#### Implémentation

```python
# Module format_validator.py

FORMAT_LIMITS = {
    'ibm.720': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 9},
    'ibm.1440': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 18},
    'ibm.360': {'max_cyl': 39, 'heads': 2, 'sectors_per_track': 9},
    'ibm.1200': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 15},
    # ... autres formats
}

def is_track_in_format_range(track_num: int, format_type: str) -> Tuple[bool, Optional[str]]:
    """
    Vérifie si une piste est dans la plage valide du format
    Retourne (is_in_range, warning_message)
    """
    if format_type not in FORMAT_LIMITS:
        return (True, None)  # Format inconnu, on accepte par défaut
    
    limits = FORMAT_LIMITS[format_type]
    if track_num > limits['max_cyl']:
        warning = (
            f"Piste {track_num} hors limites du format {format_type} "
            f"(max: {limits['max_cyl']}). Données affichées à titre informatif "
            f"mais non incluses dans le calcul final."
        )
        return (False, warning)
    
    return (True, None)
```

#### Modifications dans `calculate_statistics()`

```python
# Filtrer les pistes hors limites pour le calcul final
track_averages_in_range = [v for v in track_averages if v.is_in_format_range]

# Calculer les statistiques seulement sur les pistes dans les limites
percentages = [v.percentage for v in track_averages_in_range]
average = sum(percentages) / len(percentages) if percentages else 0.0

# Mais retourner TOUTES les valeurs pour affichage
return {
    "average": average,  # Calculé seulement sur pistes dans limites
    "values": all_values,  # Toutes les pistes pour affichage
    "tracks_in_range": len(track_averages_in_range),
    "tracks_out_of_range": len(track_averages) - len(track_averages_in_range)
}
```

#### Avantages
- ✅ Permet d'explorer toutes les pistes sans restriction
- ✅ Indicateur clair pour les pistes hors limites
- ✅ Calcul final fiable (seulement pistes dans limites)
- ✅ Données informatives conservées pour diagnostic

#### Inconvénients
- ⚠️ Nécessite de maintenir une liste de formats
- ⚠️ Ne résout pas le problème si la piste est dans la plage mais non formatée

---

### Proposition 2 : Analyse de Cohérence des IDs de Secteurs (Méthode ImageDisk)

#### Principe
Comme ImageDisk, analyser les IDs de secteurs détectés pour vérifier leur cohérence avec la piste attendue.

#### Implémentation

```python
@dataclass
class SectorID:
    """ID d'un secteur IBM MFM"""
    cylinder: int
    head: int
    sector: int
    size: int  # Taille du secteur (N dans l'ID)

def parse_sector_ids_from_output(line: str) -> List[SectorID]:
    """
    Extrait les IDs de secteurs depuis la sortie de gw align
    Note: gw align ne fournit pas directement les IDs, il faudrait
    soit parser le flux brut, soit utiliser une option de gw align
    """
    # TODO: Implémenter l'extraction des IDs depuis le flux ou la sortie
    pass

def validate_sector_ids(
    sector_ids: List[SectorID],
    expected_cylinder: int,
    expected_head: int
) -> Dict[str, Any]:
    """
    Valide la cohérence des IDs de secteurs
    Retourne un score de validité (0-100)
    """
    if not sector_ids:
        return {
            'validity_score': 0.0,
            'valid_sectors': 0,
            'total_sectors': 0,
            'cylinder_mismatches': 0,
            'head_mismatches': 0
        }
    
    valid_count = 0
    cylinder_mismatches = 0
    head_mismatches = 0
    
    for sid in sector_ids:
        if sid.cylinder == expected_cylinder:
            if sid.head == expected_head:
                valid_count += 1
            else:
                head_mismatches += 1
        else:
            cylinder_mismatches += 1
    
    total = len(sector_ids)
    validity_score = (valid_count / total * 100.0) if total > 0 else 0.0
    
    return {
        'validity_score': validity_score,
        'valid_sectors': valid_count,
        'total_sectors': total,
        'cylinder_mismatches': cylinder_mismatches,
        'head_mismatches': head_mismatches
    }
```

#### Avantages
- ✅ Méthode éprouvée (utilisée par ImageDisk)
- ✅ Détecte les problèmes d'alignement même si des secteurs sont détectés
- ✅ Indique la direction du problème (tête trop haute/basse)

#### Inconvénients
- ⚠️ Nécessite d'extraire les IDs de secteurs depuis le flux brut
- ⚠️ Greaseweazle ne fournit pas directement les IDs dans la sortie standard
- ⚠️ Plus complexe à implémenter

---

### Proposition 3 : Détection de Pistes Non Formatées (Méthode AmigaTestKit)

#### Principe
Comme AmigaTestKit, analyser le flux brut pour détecter si une piste est réellement formatée ou si elle contient seulement du flux résiduel.

#### Implémentation

```python
def analyze_track_format_status(
    flux_transitions: int,
    time_per_rev: float,
    sectors_detected: int,
    sectors_expected: int,
    format_type: str
) -> Dict[str, Any]:
    """
    Analyse si une piste est formatée ou contient seulement du flux résiduel
    """
    # Calculer la densité de flux
    flux_density = flux_transitions / time_per_rev if time_per_rev > 0 else 0
    
    # Seuils pour détecter une piste formatée
    # Une piste formatée IBM MFM devrait avoir:
    # - Un nombre minimum de transitions de flux
    # - Une densité de flux cohérente
    # - Des secteurs avec des IDs valides
    
    is_formatted = False
    confidence = 0.0
    
    # Critère 1: Nombre de secteurs détectés
    if sectors_detected > 0:
        # Critère 2: Ratio secteurs détectés vs attendus
        if sectors_expected > 0:
            sector_ratio = sectors_detected / sectors_expected
            if sector_ratio >= 0.8:  # Au moins 80% des secteurs attendus
                is_formatted = True
                confidence = sector_ratio * 100.0
        else:
            # Pas de secteurs attendus, utiliser la densité de flux
            if flux_density > 1000:  # Seuil arbitraire à ajuster
                is_formatted = True
                confidence = min(100.0, flux_density / 10.0)
    
    # Critère 3: Densité de flux minimale pour une piste formatée
    # Une piste IBM MFM formatée devrait avoir au moins X transitions
    min_flux_for_formatted = {
        'ibm.720': 50000,   # ~50k transitions pour 9 secteurs
        'ibm.1440': 100000, # ~100k transitions pour 18 secteurs
        'ibm.360': 50000,
        'ibm.1200': 80000,
    }
    
    min_flux = min_flux_for_formatted.get(format_type, 50000)
    if flux_transitions < min_flux:
        # Pas assez de flux pour une piste formatée
        is_formatted = False
        confidence = 0.0
    
    return {
        'is_formatted': is_formatted,
        'confidence': confidence,
        'flux_density': flux_density,
        'sector_ratio': sectors_detected / sectors_expected if sectors_expected > 0 else 0.0
    }
```

#### Avantages
- ✅ Détecte les pistes non formatées même si elles contiennent du flux résiduel
- ✅ Utilise plusieurs critères pour plus de fiabilité
- ✅ Peut être combiné avec d'autres méthodes

#### Inconvénients
- ⚠️ Les seuils doivent être calibrés empiriquement
- ⚠️ Peut être sensible aux variations entre lecteurs

---

### Proposition 4 : Analyse d'Azimut (Basée sur Section 9.7 du Manuel Panasonic)

#### Principe
L'azimut vérifie que la tête de lecture/écriture est perpendiculaire à la piste. Un mauvais azimut cause des variations importantes du signal entre les lectures. Cette analyse est inspirée de la **Section 9.7 : Azimuth Verification** du manuel Panasonic.

#### Implémentation

```python
def analyze_azimuth(self, readings: List[AlignmentValue]) -> Dict:
    """
    Analyse l'azimut basée sur les variations de signal
    Inspiré de la section 9.7 du manuel Panasonic JU-253
    
    Principe : Un bon azimut produit des lectures stables avec peu de variation
    Un mauvais azimut cause des variations importantes entre les lectures
    """
    if not readings or len(readings) < 3:
        return {
            'status': 'insufficient_data',
            'confidence': 0,
            'message': 'Pas assez de lectures pour analyser l\'azimut'
        }
    
    # Analyser la variation des flux transitions
    flux_variations = [r.flux_transitions for r in readings if r.flux_transitions]
    
    if not flux_variations:
        return {'status': 'unknown', 'confidence': 0}
    
    # Calculer l'écart-type des flux transitions
    mean_flux = sum(flux_variations) / len(flux_variations)
    variance = sum((x - mean_flux) ** 2 for x in flux_variations) / len(flux_variations)
    std_dev = math.sqrt(variance)
    
    # Coefficient de variation (CV) pour l'azimut
    # CV < 0.5% = Excellent, < 1% = Bon, < 2% = Acceptable, >= 2% = Médiocre
    cv = (std_dev / mean_flux) * 100 if mean_flux > 0 else 0
    
    # Analyser aussi la variation du time_per_rev
    time_variations = [r.time_per_rev for r in readings if r.time_per_rev]
    if time_variations:
        mean_time = sum(time_variations) / len(time_variations)
        time_variance = sum((x - mean_time) ** 2 for x in time_variations) / len(time_variations)
        time_std_dev = math.sqrt(time_variance)
        time_cv = (time_std_dev / mean_time) * 100 if mean_time > 0 else 0
    else:
        time_cv = 0
    
    # Score combiné (moyenne pondérée)
    combined_cv = (cv * 0.7) + (time_cv * 0.3)
    
    # Interprétation basée sur le manuel Panasonic
    if combined_cv < 0.5:
        status = 'excellent'
        confidence = 100.0
    elif combined_cv < 1.0:
        status = 'good'
        confidence = 90.0 - (combined_cv - 0.5) * 20
    elif combined_cv < 2.0:
        status = 'acceptable'
        confidence = 80.0 - (combined_cv - 1.0) * 10
    else:
        status = 'poor'
        confidence = max(0.0, 70.0 - (combined_cv - 2.0) * 5)
    
    return {
        'status': status,
        'confidence': round(confidence, 1),
        'coefficient_of_variation': round(combined_cv, 3),
        'flux_cv': round(cv, 3),
        'time_cv': round(time_cv, 3),
        'mean_flux': round(mean_flux, 0),
        'flux_std_dev': round(std_dev, 0),
        'suggestion': self.get_azimuth_suggestion(status, combined_cv)
    }

def get_azimuth_suggestion(self, status: str, cv: float) -> str:
    """Génère une suggestion d'ajustement basée sur l'azimut"""
    if status == 'excellent':
        return "✅ Azimut excellent - Aucun ajustement nécessaire"
    elif status == 'good':
        return "✓ Azimut bon - Ajustement mineur possible si nécessaire"
    elif status == 'acceptable':
        return "⚠️ Azimut acceptable - Ajuster l'azimut (vis de réglage d'angle de la tête) pour améliorer"
    else:
        return "❌ Azimut médiocre - Ajuster l'azimut (vis de réglage d'angle de la tête) - La tête n'est pas perpendiculaire à la piste"
```

#### Avantages
- ✅ Détecte les problèmes d'azimut sans oscilloscope
- ✅ Utilise des métriques logicielles (variation des flux transitions)
- ✅ Basé sur les procédures du manuel Panasonic
- ✅ Fournit des suggestions d'ajustement claires

#### Inconvénients
- ⚠️ Nécessite plusieurs lectures (minimum 3) pour être fiable
- ⚠️ Les seuils doivent être calibrés selon le type de lecteur

---

### Proposition 5 : Vérification du Capteur Track 0 (Basée sur Section 9.9 du Manuel Panasonic)

#### Principe
Le capteur Track 0 est critique pour le positionnement correct de la tête. Cette vérification est inspirée de la **Section 9.9 : Track 00 Sensor Adjustment** du manuel Panasonic.

#### Implémentation

```python
def verify_track0_sensor(self, executor: GreaseweazleExecutor) -> Dict:
    """
    Vérifie le capteur Track 0 (Section 9.9 du manuel Panasonic)
    Teste si le seek vers la piste 0 fonctionne correctement
    """
    results = {
        'sensor_ok': False,
        'seek_tests': [],
        'read_tests': [],
        'warnings': [],
        'suggestions': []
    }
    
    # Test 1: Seek vers piste 0 depuis différentes positions
    test_positions = [10, 20, 40, 79]  # Positions de test
    for start_pos in test_positions:
        try:
            # Seek vers la position de départ
            seek_result_start = await executor.run_command(
                ['seek', str(start_pos), '--head', '0'],
                timeout=5
            )
            
            # Seek vers piste 0
            seek_result_0 = await executor.run_command(
                ['seek', '0', '--head', '0'],
                timeout=5
            )
            
            results['seek_tests'].append({
                'from_track': start_pos,
                'success': seek_result_0.returncode == 0,
                'message': seek_result_0.stdout if seek_result_0.returncode == 0 else seek_result_0.stderr
            })
        except Exception as e:
            results['seek_tests'].append({
                'from_track': start_pos,
                'success': False,
                'error': str(e)
            })
    
    # Test 2: Lecture de la piste 0 (plusieurs lectures pour cohérence)
    try:
        track0_readings = await self.multiple_readings(0, 0, reads=5)
        
        # Vérifier la cohérence des lectures
        all_readings_ok = all(
            r.sectors_detected == r.sectors_expected 
            for r in track0_readings 
            if r.sectors_expected and r.sectors_detected is not None
        )
        
        # Vérifier que toutes les lectures détectent la piste 0
        all_track0 = all(
            r.track == '0.0' or r.track.startswith('0.')
            for r in track0_readings
        )
        
        results['read_tests'] = {
            'readings_count': len(track0_readings),
            'all_readings_ok': all_readings_ok,
            'all_track0': all_track0,
            'readings': [
                {
                    'track': r.track,
                    'sectors_detected': r.sectors_detected,
                    'sectors_expected': r.sectors_expected,
                    'percentage': r.percentage
                }
                for r in track0_readings
            ]
        }
        
        if not all_readings_ok:
            results['warnings'].append(
                "Les lectures de la piste 0 sont incohérentes - "
                "Le capteur Track 0 peut nécessiter un ajustement"
            )
        
        if not all_track0:
            results['warnings'].append(
                "Certaines lectures ne détectent pas la piste 0 - "
                "Le capteur Track 0 peut être défectueux"
            )
            
    except Exception as e:
        results['warnings'].append(f"Erreur lors des lectures de piste 0: {str(e)}")
    
    # Évaluation finale
    all_seeks_ok = all(test['success'] for test in results['seek_tests'])
    reads_ok = results['read_tests'].get('all_readings_ok', False) and \
               results['read_tests'].get('all_track0', False)
    
    results['sensor_ok'] = all_seeks_ok and reads_ok
    
    if not results['sensor_ok']:
        results['suggestions'].append(
            "❌ Capteur Track 0 nécessite un ajustement. "
            "Consultez la Section 9.9 du manuel Panasonic JU-253 pour "
            "les procédures d'ajustement du capteur Track 0."
        )
    else:
        results['suggestions'].append(
            "✅ Capteur Track 0 fonctionne correctement"
        )
    
    return results
```

#### Avantages
- ✅ Détecte les problèmes de capteur Track 0 avant l'alignement
- ✅ Teste à la fois le seek et la lecture
- ✅ Basé sur les procédures du manuel Panasonic
- ✅ Fournit des suggestions d'ajustement

#### Inconvénients
- ⚠️ Nécessite plusieurs tests (seek + lecture)
- ⚠️ Peut être plus long à exécuter

---

### Proposition 6 : Analyse d'Asymétrie (Basée sur Section 9.10 du Manuel Panasonic)

#### Principe
L'asymétrie du signal indique un problème d'alignement. Un signal symétrique indique un bon alignement. Cette analyse est inspirée de la **Section 9.10 : Asymmetry Verification** du manuel Panasonic.

#### Implémentation

```python
def analyze_asymmetry(self, readings: List[AlignmentValue]) -> Dict:
    """
    Analyse l'asymétrie du signal (Section 9.10 du manuel Panasonic)
    Un signal symétrique indique un bon alignement
    """
    if not readings or len(readings) < 3:
        return {'status': 'insufficient_data'}
    
    # Analyser les variations de time_per_rev
    time_variations = [r.time_per_rev for r in readings if r.time_per_rev]
    
    if not time_variations or len(time_variations) < 3:
        return {'status': 'insufficient_data'}
    
    # Calculer la symétrie (écart entre min et max par rapport à la moyenne)
    mean_time = sum(time_variations) / len(time_variations)
    min_time = min(time_variations)
    max_time = max(time_variations)
    
    # Asymétrie relative (en pourcentage)
    # Un signal symétrique a min et max équidistants de la moyenne
    deviation_above = max_time - mean_time
    deviation_below = mean_time - min_time
    
    # Asymétrie = différence relative entre les deux déviations
    if mean_time > 0:
        asymmetry = ((deviation_above - deviation_below) / mean_time) * 100
    else:
        asymmetry = 0
    
    # Analyser aussi les flux transitions pour plus de précision
    flux_variations = [r.flux_transitions for r in readings if r.flux_transitions]
    flux_asymmetry = 0
    if flux_variations and len(flux_variations) >= 3:
        mean_flux = sum(flux_variations) / len(flux_variations)
        min_flux = min(flux_variations)
        max_flux = max(flux_variations)
        if mean_flux > 0:
            flux_dev_above = max_flux - mean_flux
            flux_dev_below = mean_flux - min_flux
            flux_asymmetry = ((flux_dev_above - flux_dev_below) / mean_flux) * 100
    
    # Asymétrie combinée
    combined_asymmetry = (abs(asymmetry) * 0.6) + (abs(flux_asymmetry) * 0.4)
    
    # Interprétation basée sur le manuel Panasonic
    if combined_asymmetry < 0.1:
        status = 'excellent'
        confidence = 100.0
    elif combined_asymmetry < 0.5:
        status = 'good'
        confidence = 95.0 - (combined_asymmetry - 0.1) * 10
    elif combined_asymmetry < 1.0:
        status = 'acceptable'
        confidence = 90.0 - (combined_asymmetry - 0.5) * 20
    else:
        status = 'poor'
        confidence = max(0.0, 80.0 - (combined_asymmetry - 1.0) * 10)
    
    return {
        'status': status,
        'confidence': round(confidence, 1),
        'asymmetry_percent': round(combined_asymmetry, 3),
        'time_asymmetry': round(asymmetry, 3),
        'flux_asymmetry': round(flux_asymmetry, 3),
        'mean_time': round(mean_time, 2),
        'time_range': round(max_time - min_time, 2),
        'suggestion': self.get_asymmetry_suggestion(status, combined_asymmetry)
    }

def get_asymmetry_suggestion(self, status: str, asymmetry: float) -> str:
    """Génère une suggestion d'ajustement basée sur l'asymétrie"""
    if status == 'excellent':
        return "✅ Signal symétrique - Alignement excellent"
    elif status == 'good':
        return "✓ Signal légèrement asymétrique - Alignement bon"
    elif status == 'acceptable':
        return "⚠️ Signal asymétrique - Ajuster les vis d'alignement radial pour équilibrer le signal"
    else:
        return "❌ Signal très asymétrique - Ajuster les vis d'alignement radial - Le signal n'est pas équilibré, indiquant un problème d'alignement"
```

#### Avantages
- ✅ Détecte les problèmes d'alignement via l'asymétrie du signal
- ✅ Utilise des métriques logicielles (variation des timings)
- ✅ Basé sur les procédures du manuel Panasonic
- ✅ Fournit des suggestions d'ajustement

#### Inconvénients
- ⚠️ Nécessite plusieurs lectures (minimum 3) pour être fiable
- ⚠️ Les seuils doivent être calibrés selon le type de lecteur

---

### Proposition 7 : Calcul de Pourcentage Amélioré avec Validation Multi-Critères

#### Principe
Combiner plusieurs critères pour calculer un pourcentage d'alignement fiable, en intégrant les analyses du manuel Panasonic :
1. Validation de la plage de format
2. Analyse de cohérence des IDs
3. Détection de formatage
4. Ratio secteurs détectés/attendus
5. **Analyse d'azimut** (Section 9.7)
6. **Analyse d'asymétrie** (Section 9.10)
7. **Vérification Track 0** (Section 9.9)

#### Implémentation

```python
def calculate_reliable_alignment_percentage(
    track_num: int,
    head_num: int,
    format_type: str,
    sectors_detected: int,
    sectors_expected: int,
    flux_transitions: Optional[int] = None,
    time_per_rev: Optional[float] = None,
    sector_ids: Optional[List[SectorID]] = None
) -> Dict[str, Any]:
    """
    Calcule un pourcentage d'alignement fiable en combinant plusieurs critères
    """
    result = {
        'percentage': 0.0,
        'is_valid': False,
        'reasons': [],
        'warnings': []
    }
    
    # Critère 1: Validation de la plage
    if not is_track_in_format_range(track_num, format_type):
        result['reasons'].append(f"Piste {track_num} hors limites du format {format_type}")
        result['warnings'].append("Piste non formatée - mesure non fiable")
        return result
    
    # Critère 2: Détection de formatage
    if flux_transitions is not None and time_per_rev is not None:
        format_status = analyze_track_format_status(
            flux_transitions, time_per_rev,
            sectors_detected, sectors_expected, format_type
        )
        
        if not format_status['is_formatted']:
            result['reasons'].append("Piste non formatée détectée")
            result['warnings'].append("Flux résiduel seulement - mesure non fiable")
            return result
    
    # Critère 3: Validation des IDs de secteurs
    id_validity_score = 100.0
    if sector_ids:
        id_validation = validate_sector_ids(sector_ids, track_num, head_num)
        id_validity_score = id_validation['validity_score']
        
        if id_validation['cylinder_mismatches'] > 0:
            result['warnings'].append(
                f"{id_validation['cylinder_mismatches']} secteurs avec numéro de cylindre incorrect"
            )
        if id_validation['head_mismatches'] > 0:
            result['warnings'].append(
                f"{id_validation['head_mismatches']} secteurs avec numéro de tête incorrect"
            )
    
    # Critère 4: Ratio secteurs
    if sectors_expected > 0:
        sector_ratio = sectors_detected / sectors_expected
        sector_score = sector_ratio * 100.0
    else:
        sector_score = 0.0
    
    # Critère 5: Analyse d'azimut (Section 9.7)
    azimuth_score = 100.0
    if len(readings) >= 3:
        azimuth_analysis = self.analyze_azimuth(readings)
        azimuth_score = azimuth_analysis.get('confidence', 100.0)
        if azimuth_analysis.get('status') == 'poor':
            result['warnings'].append(
                f"Azimut médiocre détecté (CV: {azimuth_analysis.get('coefficient_of_variation', 0):.2f}%) - "
                "La tête n'est pas perpendiculaire à la piste"
            )
    
    # Critère 6: Analyse d'asymétrie (Section 9.10)
    asymmetry_score = 100.0
    if len(readings) >= 3:
        asymmetry_analysis = self.analyze_asymmetry(readings)
        asymmetry_score = asymmetry_analysis.get('confidence', 100.0)
        if asymmetry_analysis.get('status') == 'poor':
            result['warnings'].append(
                f"Signal asymétrique détecté (asymétrie: {asymmetry_analysis.get('asymmetry_percent', 0):.2f}%) - "
                "Le signal n'est pas équilibré"
            )
    
    # Calcul du pourcentage final (moyenne pondérée)
    # Poids: 40% ratio secteurs, 30% validité IDs, 15% azimut, 15% asymétrie
    weights = {
        'sector': 0.40,
        'id_validity': 0.30,
        'azimuth': 0.15,
        'asymmetry': 0.15
    }
    
    if sector_ids:
        final_percentage = (
            sector_score * weights['sector'] +
            id_validity_score * weights['id_validity'] +
            azimuth_score * weights['azimuth'] +
            asymmetry_score * weights['asymmetry']
        )
    else:
        # Sans IDs, ajuster les poids
        final_percentage = (
            sector_score * 0.50 +
            azimuth_score * 0.25 +
            asymmetry_score * 0.25
        )
    
    # Ajustement si la piste est suspecte
    if format_status and format_status['confidence'] < 80.0:
        final_percentage *= (format_status['confidence'] / 100.0)
        result['warnings'].append("Confiance réduite - piste peut-être partiellement formatée")
    
    result['percentage'] = round(final_percentage, 3)
    result['is_valid'] = True
    result['sector_score'] = round(sector_score, 3)
    result['id_validity_score'] = round(id_validity_score, 3) if sector_ids else None
    result['azimuth_score'] = round(azimuth_score, 1) if len(readings) >= 3 else None
    result['asymmetry_score'] = round(asymmetry_score, 1) if len(readings) >= 3 else None
    result['format_confidence'] = format_status['confidence'] if format_status else None
    
    return result
```

#### Avantages
- ✅ Combine plusieurs méthodes pour plus de fiabilité
- ✅ Fournit des raisons et avertissements pour chaque mesure
- ✅ S'adapte selon les données disponibles

#### Inconvénients
- ⚠️ Plus complexe à implémenter
- ⚠️ Nécessite de calibrer les poids et seuils

---

### Proposition 8 : Mode d'Alignement Guidé (Basé sur Section 9.6 du Manuel Panasonic)

#### Principe
Implémenter un mode d'alignement guidé étape par étape basé sur la **Section 9.6 : Radial Alignment Adjustment** du manuel Panasonic, adapté pour fonctionner sans oscilloscope.

#### Implémentation

```python
class GuidedAlignmentProcedure:
    """
    Procédure guidée d'alignement basée sur le manuel Panasonic JU-253
    Guide l'utilisateur étape par étape sans oscilloscope
    """
    
    STEPS = [
        {
            'name': 'verify_track0',
            'description': 'Vérifier le capteur Track 0 (Section 9.9)',
            'action': 'verify_track0_sensor',
            'critical': True
        },
        {
            'name': 'reference_reading',
            'description': 'Effectuer une lecture de référence sur piste 40',
            'action': 'multiple_readings',
            'params': {'track': 40, 'head': 0, 'reads': 10},
            'critical': True
        },
        {
            'name': 'analyze_positioning',
            'description': 'Analyser le positionnement actuel',
            'action': 'analyze_positioning',
            'critical': True
        },
        {
            'name': 'analyze_azimuth',
            'description': 'Vérifier l\'azimut (Section 9.7)',
            'action': 'analyze_azimuth',
            'critical': False
        },
        {
            'name': 'analyze_asymmetry',
            'description': 'Vérifier l\'asymétrie (Section 9.10)',
            'action': 'analyze_asymmetry',
            'critical': False
        },
        {
            'name': 'suggest_adjustment',
            'description': 'Obtenir des suggestions d\'ajustement',
            'action': 'generate_suggestions',
            'critical': True
        }
    ]
    
    def run_guided_procedure(self, executor: GreaseweazleExecutor):
        """Exécute la procédure guidée complète"""
        results = {
            'steps': [],
            'overall_status': 'unknown',
            'suggestions': []
        }
        
        for step in self.STEPS:
            step_result = {
                'name': step['name'],
                'description': step['description'],
                'status': 'pending',
                'data': None,
                'warnings': [],
                'suggestions': []
            }
            
            try:
                print(f"Étape: {step['name']} - {step['description']}")
                
                if step['action'] == 'verify_track0_sensor':
                    result = self.verify_track0_sensor(executor)
                    step_result['data'] = result
                    step_result['status'] = 'success' if result.get('sensor_ok') else 'warning'
                    step_result['suggestions'] = result.get('suggestions', [])
                    
                elif step['action'] == 'multiple_readings':
                    params = step.get('params', {})
                    readings = await self.multiple_readings(
                        params['track'], params['head'], params['reads']
                    )
                    step_result['data'] = readings
                    step_result['status'] = 'success'
                    
                elif step['action'] == 'analyze_positioning':
                    # Utiliser les lectures de l'étape précédente
                    if results['steps'] and results['steps'][-1]['name'] == 'reference_reading':
                        readings = results['steps'][-1]['data']
                        result = self.analyze_positioning(readings)
                        step_result['data'] = result
                        step_result['status'] = result.get('status', 'unknown')
                        step_result['suggestions'] = result.get('suggestions', [])
                    
                elif step['action'] == 'analyze_azimuth':
                    if results['steps'] and results['steps'][-1]['name'] == 'reference_reading':
                        readings = results['steps'][-1]['data']
                        result = self.analyze_azimuth(readings)
                        step_result['data'] = result
                        step_result['status'] = result.get('status', 'unknown')
                        step_result['suggestions'] = [result.get('suggestion', '')]
                    
                elif step['action'] == 'analyze_asymmetry':
                    if results['steps'] and results['steps'][-1]['name'] == 'reference_reading':
                        readings = results['steps'][-1]['data']
                        result = self.analyze_asymmetry(readings)
                        step_result['data'] = result
                        step_result['status'] = result.get('status', 'unknown')
                        step_result['suggestions'] = [result.get('suggestion', '')]
                    
                elif step['action'] == 'generate_suggestions':
                    # Collecter toutes les analyses précédentes
                    all_metrics = {}
                    for prev_step in results['steps']:
                        if prev_step.get('data'):
                            all_metrics[prev_step['name']] = prev_step['data']
                    
                    suggestions = self.generate_alignment_suggestions(all_metrics)
                    step_result['data'] = suggestions
                    step_result['status'] = 'success'
                    step_result['suggestions'] = suggestions
                    results['suggestions'].extend(suggestions)
                
                # Afficher les suggestions
                if step_result['suggestions']:
                    for suggestion in step_result['suggestions']:
                        print(f"  → {suggestion}")
                
            except Exception as e:
                step_result['status'] = 'error'
                step_result['error'] = str(e)
                if step.get('critical', False):
                    print(f"  ❌ Erreur critique: {e}")
                    results['overall_status'] = 'failed'
                    break
            
            results['steps'].append(step_result)
        
        # Déterminer le statut global
        if results['overall_status'] != 'failed':
            critical_steps_ok = all(
                step['status'] in ['success', 'warning']
                for step in results['steps']
                if self.STEPS[results['steps'].index(step)].get('critical', False)
            )
            results['overall_status'] = 'success' if critical_steps_ok else 'warning'
        
        return results
```

#### Avantages
- ✅ Guide l'utilisateur étape par étape
- ✅ Intègre toutes les procédures du manuel Panasonic
- ✅ Fournit des suggestions contextuelles
- ✅ Fonctionne sans oscilloscope

#### Inconvénients
- ⚠️ Plus long à exécuter (plusieurs étapes)
- ⚠️ Nécessite une interface utilisateur dédiée

---

### Proposition 9 : Mode "Raw Flux" pour Pistes Hors Limites

#### Principe
Pour les pistes hors limites du format, utiliser le mode "raw flux" et analyser uniquement la présence/absence de flux, sans essayer de décoder des secteurs.

#### Implémentation

```python
async def read_track_raw_flux(
    executor: GreaseweazleExecutor,
    track: int,
    head: int
) -> Dict[str, Any]:
    """
    Lit une piste en mode raw flux (sans format)
    Utile pour les pistes hors limites ou non formatées
    """
    args = [
        "align",
        f"--tracks=c={track}:h={head}",
        "--reads=1",
        "--raw"  # Mode raw flux
    ]
    
    # Exécuter et parser la sortie
    # Analyser uniquement la présence de flux, pas de secteurs
    pass

def analyze_raw_flux_alignment(
    flux_transitions: int,
    time_per_rev: float,
    expected_empty: bool = False
) -> Dict[str, Any]:
    """
    Analyse l'alignement basé sur le flux brut uniquement
    Pour une piste non formatée, on s'attend à peu ou pas de flux
    """
    flux_density = flux_transitions / time_per_rev if time_per_rev > 0 else 0
    
    if expected_empty:
        # Pour une piste non formatée, on s'attend à peu de flux
        # Si on détecte beaucoup de flux, c'est suspect (peut-être de la piste adjacente)
        if flux_density > 500:  # Seuil à calibrer
            return {
                'alignment_score': 0.0,
                'status': 'unexpected_flux',
                'message': 'Flux détecté sur piste non formatée - possible problème d\'alignement'
            }
        else:
            return {
                'alignment_score': 100.0,
                'status': 'empty_as_expected',
                'message': 'Piste vide comme attendu'
            }
    else:
        # Pour une piste formatée, on s'attend à du flux
        # L'alignement est basé sur la stabilité du flux entre lectures
        return {
            'alignment_score': 100.0,  # À calculer basé sur la stabilité
            'status': 'has_flux',
            'message': 'Flux détecté'
        }
```

#### Avantages
- ✅ Permet d'analyser les pistes hors limites
- ✅ Détecte les problèmes d'alignement même sans format
- ✅ Utile pour le diagnostic

#### Inconvénients
- ⚠️ Moins précis que l'analyse avec format
- ⚠️ Nécessite des seuils calibrés

---

## 🎯 Recommandations d'Implémentation

### Phase 1 : Correctifs Immédiats (Priorité Haute)

1. **Validation des limites de format** (Proposition 1)
   - Implémentation rapide
   - Impact immédiat sur la fiabilité
   - Élimine les faux positifs sur pistes > 79

2. **Détection de formatage** (Proposition 3)
   - Améliore la détection des pistes non formatées
   - Peut être combiné avec la validation des limites

3. **Vérification du capteur Track 0** (Proposition 5)
   - Détecte les problèmes avant l'alignement
   - Basé sur Section 9.9 du manuel Panasonic
   - Critique pour la fiabilité

### Phase 2 : Améliorations Moyen Terme (Priorité Moyenne)

4. **Analyse d'azimut** (Proposition 4)
   - Détecte les problèmes d'azimut sans oscilloscope
   - Basé sur Section 9.7 du manuel Panasonic
   - Améliore la précision des mesures

5. **Analyse d'asymétrie** (Proposition 6)
   - Détecte les problèmes d'alignement via l'asymétrie
   - Basé sur Section 9.10 du manuel Panasonic
   - Complémentaire à l'analyse d'azimut

6. **Calcul amélioré multi-critères** (Proposition 7)
   - Combine toutes les validations précédentes
   - Intègre azimut et asymétrie dans le calcul
   - Fournit des métriques plus fiables

7. **Mode raw flux pour pistes hors limites** (Proposition 9)
   - Permet d'analyser toutes les pistes
   - Utile pour le diagnostic

### Phase 3 : Améliorations Avancées (Priorité Basse)

8. **Mode d'alignement guidé** (Proposition 8)
   - Guide l'utilisateur étape par étape
   - Intègre toutes les procédures du manuel Panasonic
   - Nécessite une interface utilisateur dédiée

9. **Analyse des IDs de secteurs** (Proposition 2)
   - Nécessite d'extraire les IDs depuis le flux
   - Plus complexe mais plus précis
   - Peut être ajouté si Greaseweazle fournit cette information

---

## 📊 Exemple d'Utilisation

### Avant (Problème Actuel)

```
Piste 80.0 (IBM 1440): 18/18 secteurs détectés → 100% ✅ (FAUX POSITIF)
Piste 81.0 (IBM 1440): 18/18 secteurs détectés → 100% ✅ (FAUX POSITIF)
```

### Après (Avec Validations)

```
Piste 80.0 (IBM 1440): 
  ⚠️ Piste hors limites du format (max: 79)
  ⚠️ Mesure non fiable - piste non formatée
  → Pourcentage: N/A (invalide)

Piste 40.0 (IBM 1440): 
  ✅ Piste dans limites
  ✅ Piste formatée détectée (confiance: 95%)
  ✅ 18/18 secteurs détectés
  ✅ IDs de secteurs cohérents (18/18 valides)
  → Pourcentage: 99.2% (fiable)
```

---

## 🔧 Modifications de Code Nécessaires

### 1. Nouveau Module : `format_validator.py`

```python
# AlignTester/src/backend/api/format_validator.py
# Contient les fonctions de validation de format
```

### 2. Modification : `alignment_parser.py`

```python
# Ajouter la validation des limites
# Ajouter la détection de formatage
# Modifier calculate_statistics() pour utiliser les nouvelles validations
```

### 3. Modification : `manual_alignment.py`

```python
# Utiliser les nouvelles validations lors des lectures
# Afficher des avertissements pour les pistes invalides
```

---

## 📝 Tests à Effectuer

1. **Test sur piste 79** (dernière piste valide) : Doit donner un pourcentage fiable
2. **Test sur piste 80** (hors limites) : Doit être marqué comme invalide
3. **Test sur piste 40** (piste centrale) : Doit donner un pourcentage fiable
4. **Test sur disquette partiellement formatée** : Doit détecter les zones non formatées
5. **Test avec différents formats** : IBM 720, IBM 1440, IBM 360, etc.

---

## 🎓 Références

### Documents Techniques
- **Manuel de Service Panasonic JU-253** (MSD870909100) : Procédures d'alignement pour lecteurs 3.5 pouces
  - Section 9.6 : Radial Alignment Adjustment (pages 8-9)
  - Section 9.7 : Azimuth Verification (pages 9-10)
  - Section 9.8 : Index Burst Verification and Adjustment
  - Section 9.9 : Track 00 Sensor Adjustment (pages 10-11)
  - Section 9.10 : Asymmetry Verification (page 12)
  - Section 11 : Panasonic Alignment Diskette

### Documents du Projet
- Document `IMAGEDISK_ALIGNEMENT.md` : Méthodes d'ImageDisk et AmigaTestKit
- Document `COMPARAISON_METHODES_ALIGNEMENT.md` : Comparaison des différentes méthodes
- Document `DOCUMENTATION_GREASEWEAZLE.md` : Documentation technique Greaseweazle
- Code source Greaseweazle `align.py` : Comprendre ce que gw align fait réellement
- `diskdefs_ibm.cfg` : Définitions des formats et leurs limites

### Concepts Techniques
- **Alignement radial** : Positionnement correct de la tête par rapport au centre de la piste
- **Azimut** : Angle perpendiculaire de la tête par rapport à la piste
- **Asymétrie** : Équilibre du signal de lecture (indicateur de qualité d'alignement)
- **Capteur Track 0** : Capteur optique/mécanique qui détecte la position zéro du lecteur

---

## ✅ Conclusion

### Priorités Immédiates

Les propositions **1, 3 et 5** sont les plus prioritaires car elles :
- Résolvent directement le problème identifié (pistes > 79)
- Sont relativement simples à implémenter
- Améliorent immédiatement la fiabilité des mesures
- Intègrent les procédures critiques du manuel Panasonic (Track 0)

### Améliorations Complémentaires

Les propositions **4, 6 et 7** (azimut, asymétrie, calcul multi-critères) peuvent être ajoutées progressivement pour :
- Améliorer encore la précision et la fiabilité
- Intégrer toutes les procédures du manuel Panasonic
- Fournir un diagnostic complet sans oscilloscope

### Vision Long Terme

La proposition **8** (mode guidé) représente l'intégration complète de toutes les procédures du manuel Panasonic dans une interface utilisateur guidée, permettant un alignement professionnel sans équipement de mesure spécialisé.

### Avantages de l'Approche Manuel Panasonic

En intégrant les procédures du manuel Panasonic JU-253 :
- ✅ **Méthodes éprouvées** : Basées sur des procédures de service officielles
- ✅ **Sans oscilloscope** : Adaptées pour fonctionner avec des métriques logicielles
- ✅ **Diagnostic complet** : Couvre tous les aspects de l'alignement (radial, azimut, asymétrie, Track 0)
- ✅ **Suggestions contextuelles** : Guide l'utilisateur dans les ajustements nécessaires
- ✅ **Fiabilité accrue** : Combine plusieurs critères pour des mesures plus fiables

