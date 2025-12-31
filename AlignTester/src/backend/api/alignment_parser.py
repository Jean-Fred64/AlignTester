"""
Parser pour les résultats de la commande align de Greaseweazle
Extrait les valeurs de pourcentage d'alignement depuis la sortie
"""

import re
import math
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from .format_validator import validate_track_for_format, analyze_track_format_status

@dataclass
class AlignmentValue:
    """Représente une valeur d'alignement"""
    track: str  # Format "XX.Y" (numéro de piste et face)
    percentage: float  # Pourcentage d'alignement
    base: Optional[float] = None  # Valeur de base en us (format dtc)
    bands: Optional[List[float]] = None  # Bandes en us (format dtc)
    sectors_detected: Optional[int] = None  # Secteurs détectés (format gw align)
    sectors_expected: Optional[int] = None  # Secteurs attendus (format gw align)
    flux_transitions: Optional[int] = None  # Nombre de transitions de flux
    time_per_rev: Optional[float] = None  # Temps par révolution en ms
    format_type: Optional[str] = None  # Type de format (ibm.1440, etc.)
    # Nouvelles métriques
    consistency: Optional[float] = None  # Cohérence entre lectures (0-100)
    stability: Optional[float] = None  # Stabilité des timings (0-100)
    positioning_status: Optional[str] = None  # "correct", "unstable", "poor"
    # Analyse d'azimut (Section 9.7 du manuel Panasonic)
    azimuth_score: Optional[float] = None  # Score d'azimut (0-100)
    azimuth_status: Optional[str] = None  # "excellent", "good", "acceptable", "poor"
    azimuth_cv: Optional[float] = None  # Coefficient de variation (CV) pour l'azimut
    # Analyse d'asymétrie (Section 9.10 du manuel Panasonic)
    asymmetry_score: Optional[float] = None  # Score d'asymétrie (0-100)
    asymmetry_status: Optional[str] = None  # "excellent", "good", "acceptable", "poor"
    asymmetry_percent: Optional[float] = None  # Pourcentage d'asymétrie
    # Détails du calcul multi-critères (pour affichage détaillé)
    calculation_details: Optional[Dict] = None  # Détails du calcul (scores bruts, pénalités, poids, etc.)
    # Validation de format (informatif, non bloquant)
    is_in_format_range: Optional[bool] = None  # True si piste dans les limites du format
    format_warning: Optional[str] = None  # Message d'avertissement si hors limites
    # Détection de formatage
    is_formatted: Optional[bool] = None  # True si la piste semble formatée
    format_confidence: Optional[float] = None  # Niveau de confiance du formatage (0-100)
    format_status_message: Optional[str] = None  # Message descriptif du statut de formatage
    line_number: Optional[int] = None
    raw_line: Optional[str] = None
    timestamp: Optional[datetime] = None

class AlignmentParser:
    """Parse les résultats de la commande align"""
    
    # Pattern pour extraire les pourcentages : [XX.XXX%] (format dtc/KryoFlux)
    PERCENTAGE_PATTERN = re.compile(r'\[(\d+(?:\.\d+)?)\s*%\]')
    
    # Pattern pour extraire le numéro de piste au début : XX.Y ou TXX.Y
    TRACK_PATTERN = re.compile(r'^T?(\d+\.\d+)\s*:')
    
    # Pattern pour extraire base: X.XXX us (format dtc)
    BASE_PATTERN = re.compile(r'base:\s*([\d.]+)\s*us')
    
    # Pattern pour extraire les bandes : band: X.XXX us, Y.YYY us, ... (format dtc)
    BANDS_PATTERN = re.compile(r'band:\s*((?:[\d.]+\s*us,?\s*)+)')
    
    # Pattern pour extraire les secteurs : (X/Y sectors) (format gw align)
    SECTORS_PATTERN = re.compile(r'\((\d+)/(\d+)\s+sectors?\)')
    
    # Pattern pour extraire les flux transitions : (XXXXX flux in XXX.XXms) (format gw align)
    FLUX_PATTERN = re.compile(r'\((\d+)\s+flux\s+in\s+([\d.]+)ms\)')
    
    # Pattern pour extraire le format : Format XXXXX ou IBM MFM, etc.
    FORMAT_PATTERN = re.compile(r'(?:Format\s+)?([A-Za-z0-9.]+)')
    
    @staticmethod
    def _calculate_optimized_multi_criteria(
        avg_percentage: float,
        consistency: Optional[float],
        stability: Optional[float],
        azimuth_score: Optional[float],
        azimuth_cv: Optional[float],
        asymmetry_score: Optional[float],
        asymmetry_percent: Optional[float],
        num_readings: int
    ) -> tuple[float, dict[str, float]]:
        """
        Calcule le pourcentage d'alignement avec pondération adaptative et gestion des cas limites.
        
        Optimisations implémentées :
        - Pondération adaptative selon la disponibilité des métriques
        - Seuils de confiance basés sur le nombre de lectures
        - Pénalités non-linéaires pour les scores très faibles
        - Normalisation des scores dans [0, 100]
        
        Args:
            avg_percentage: Pourcentage moyen basé sur les secteurs détectés
            consistency: Score de cohérence (0-100) ou None
            stability: Score de stabilité (0-100) ou None
            azimuth_score: Score d'azimut (0-100) ou None
            azimuth_cv: Coefficient de variation d'azimut (pour confiance) ou None
            asymmetry_score: Score d'asymétrie (0-100) ou None
            asymmetry_percent: Pourcentage d'asymétrie (pour confiance) ou None
            num_readings: Nombre de lectures disponibles pour cette piste
        
        Returns:
            Tuple (adjusted_percentage, weights_used) où weights_used est un dict des poids utilisés
        """
        # 1. Normaliser les scores (0 si non disponible au lieu de 100)
        sector_score = max(0.0, min(100.0, avg_percentage))
        
        # Score de cohérence/stabilité (moyenne des deux si disponibles)
        quality_score = 0.0
        if consistency is not None and stability is not None:
            quality_score = max(0.0, min(100.0, (consistency + stability) / 2))
        elif consistency is not None:
            quality_score = max(0.0, min(100.0, consistency))
        elif stability is not None:
            quality_score = max(0.0, min(100.0, stability))
        
        azimuth_final = max(0.0, min(100.0, azimuth_score)) if azimuth_score is not None else 0.0
        asymmetry_final = max(0.0, min(100.0, asymmetry_score)) if asymmetry_score is not None else 0.0
        
        # 2. Calculer les poids adaptatifs selon la disponibilité
        has_quality = quality_score > 0
        has_azimuth = azimuth_final > 0
        has_asymmetry = asymmetry_final > 0
        
        # Poids de base (idéal)
        base_weights = {
            'sector': 0.40,
            'quality': 0.30 if has_quality else 0.0,
            'azimuth': 0.15 if has_azimuth else 0.0,
            'asymmetry': 0.15 if has_asymmetry else 0.0
        }
        
        # 3. Facteurs de confiance basés sur le nombre de lectures
        # Les métriques nécessitent au moins 3 lectures pour être fiables
        confidence_factors = {
            'sector': 1.0,  # Toujours fiable si on a des lectures
            'quality': min(1.0, num_readings / 3.0) if has_quality else 0.0,
            'azimuth': min(1.0, num_readings / 3.0) if has_azimuth else 0.0,
            'asymmetry': min(1.0, num_readings / 3.0) if has_asymmetry else 0.0
        }
        
        # 4. Ajuster les poids avec les facteurs de confiance
        adjusted_weights = {
            k: base_weights[k] * confidence_factors[k]
            for k in base_weights
        }
        
        # 5. Normaliser pour que la somme = 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}
        else:
            # Fallback : utiliser seulement le score de secteurs
            adjusted_weights = {'sector': 1.0, 'quality': 0.0, 'azimuth': 0.0, 'asymmetry': 0.0}
        
        # 6. Appliquer des pénalités non-linéaires pour les scores très faibles
        # Si un score est en dessous d'un seuil, appliquer une pénalité quadratique
        def apply_penalty(score: float, threshold: float = 50.0) -> float:
            """Applique une pénalité non-linéaire si le score est < threshold"""
            if score >= threshold:
                return score
            # Pénalité quadratique pour les scores < threshold
            # Exemple : score 30% avec threshold 50% → 30 * (30/50)^2 = 10.8%
            penalty_factor = (score / threshold) ** 2
            return score * penalty_factor
        
        sector_penalized = apply_penalty(sector_score, threshold=90.0)
        quality_penalized = apply_penalty(quality_score, threshold=70.0) if has_quality else 0.0
        azimuth_penalized = apply_penalty(azimuth_final, threshold=75.0) if has_azimuth else 0.0
        asymmetry_penalized = apply_penalty(asymmetry_final, threshold=75.0) if has_asymmetry else 0.0
        
        # 7. Calcul final avec poids adaptatifs
        adjusted_percentage = (
            sector_penalized * adjusted_weights['sector'] +
            quality_penalized * adjusted_weights['quality'] +
            azimuth_penalized * adjusted_weights['azimuth'] +
            asymmetry_penalized * adjusted_weights['asymmetry']
        )
        
        # 8. Clamper le résultat final dans [0, 100]
        adjusted_percentage = max(0.0, min(100.0, adjusted_percentage))
        
        # 9. Préparer les détails du calcul pour l'affichage
        calculation_details = {
            'scores_raw': {
                'sector': round(sector_score, 2),
                'quality': round(quality_score, 2),
                'azimuth': round(azimuth_final, 2),
                'asymmetry': round(asymmetry_final, 2)
            },
            'scores_penalized': {
                'sector': round(sector_penalized, 2),
                'quality': round(quality_penalized, 2),
                'azimuth': round(azimuth_penalized, 2),
                'asymmetry': round(asymmetry_penalized, 2)
            },
            'weights': {
                'sector': round(adjusted_weights['sector'], 3),
                'quality': round(adjusted_weights['quality'], 3),
                'azimuth': round(adjusted_weights['azimuth'], 3),
                'asymmetry': round(adjusted_weights['asymmetry'], 3)
            },
            'confidence_factors': {
                'sector': round(confidence_factors['sector'], 3),
                'quality': round(confidence_factors['quality'], 3),
                'azimuth': round(confidence_factors['azimuth'], 3),
                'asymmetry': round(confidence_factors['asymmetry'], 3)
            },
            'num_readings': num_readings,
            'has_quality': has_quality,
            'has_azimuth': has_azimuth,
            'has_asymmetry': has_asymmetry
        }
        
        return adjusted_percentage, adjusted_weights, calculation_details
    
    @staticmethod
    def parse_line(line: str, line_number: int = None) -> Optional[AlignmentValue]:
        """
        Parse une ligne de sortie et extrait les informations d'alignement
        
        Formats supportés:
        - Format dtc/KryoFlux: 00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
        - Format gw align: T0.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)
        - Format gw align raw: T0.0: Raw Flux (232869 flux in 612.34ms)
        - Format gw align avec format: T0.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)
        """
        if not line or not line.strip():
            return None
        
        # Ignorer les lignes d'en-tête et d'information
        line_stripped = line.strip()
        if (line_stripped.startswith('Aligning') or 
            line_stripped.startswith('Format ') or
            line_stripped.startswith('Reading') or
            'reading' in line_stripped.lower() and 'times' in line_stripped.lower()):
            return None
        
        # Ignorer les lignes d'avertissement qui ne contiennent pas de données
        if 'WARNING' in line and 'Out of range' in line:
            # Mais on peut quand même essayer de parser si elle contient des données
            pass
        
        percentage = None
        track = None
        base = None
        bands = None
        sectors_detected = None
        sectors_expected = None
        flux_transitions = None
        time_per_rev = None
        format_type = None
        
        # Chercher le numéro de piste (format T0.0 ou 00.0)
        track_match = AlignmentParser.TRACK_PATTERN.search(line)
        if track_match:
            track = track_match.group(1)
        
        # Format 1: dtc/KryoFlux avec pourcentage [XX.XXX%]
        percentage_match = AlignmentParser.PERCENTAGE_PATTERN.search(line)
        if percentage_match:
            try:
                percentage = float(percentage_match.group(1))
            except ValueError:
                pass
            
            # Chercher la valeur de base (format dtc)
            base_match = AlignmentParser.BASE_PATTERN.search(line)
            if base_match:
                try:
                    base = float(base_match.group(1))
                except ValueError:
                    pass
            
            # Chercher les bandes (format dtc)
            bands_match = AlignmentParser.BANDS_PATTERN.search(line)
            if bands_match:
                bands_str = bands_match.group(1)
                band_values = re.findall(r'([\d.]+)\s*us', bands_str)
                try:
                    bands = [float(b) for b in band_values]
                except ValueError:
                    pass
        
        # Format 2: gw align avec secteurs (X/Y sectors)
        sectors_match = AlignmentParser.SECTORS_PATTERN.search(line)
        if sectors_match:
            try:
                sectors_detected = int(sectors_match.group(1))
                sectors_expected = int(sectors_match.group(2))
                # Calculer le pourcentage basé sur les secteurs
                if sectors_expected > 0:
                    percentage = (sectors_detected / sectors_expected) * 100.0
            except (ValueError, IndexError):
                pass
        
        # Extraire les informations de flux (format gw align)
        flux_match = AlignmentParser.FLUX_PATTERN.search(line)
        if flux_match:
            try:
                flux_transitions = int(flux_match.group(1))
                time_per_rev = float(flux_match.group(2))
            except (ValueError, IndexError):
                pass
        
        # Extraire le format (format gw align)
        if 'IBM MFM' in line:
            format_type = 'ibm.1440'  # Format standard pour 1.44MB
        elif 'Format' in line:
            format_match2 = re.search(r'Format\s+([A-Za-z0-9.]+)', line)
            if format_match2:
                format_type = format_match2.group(1)
        elif 'from Raw Flux' in line:
            # Format déjà décodé, essayer d'extraire depuis le début de la ligne
            # Ex: "T0.0: IBM MFM (18/18 sectors) from Raw Flux..."
            format_match3 = re.search(r':\s*([A-Za-z0-9\s]+?)\s*\(', line)
            if format_match3:
                format_name = format_match3.group(1).strip()
                if 'IBM MFM' in format_name:
                    format_type = 'ibm.1440'
                else:
                    format_type = format_name.lower().replace(' ', '.')
        
        # Si on n'a pas de pourcentage mais qu'on a des secteurs, utiliser le calcul de secteurs
        if percentage is None and sectors_detected is not None and sectors_expected is not None:
            if sectors_expected > 0:
                percentage = (sectors_detected / sectors_expected) * 100.0
        
        # Si on n'a toujours pas de pourcentage, ne pas créer de valeur
        if percentage is None:
            return None
        
        # Valider si la piste est dans les limites du format (informatif, non bloquant)
        track_validation = validate_track_for_format(track or "", format_type)
        is_in_range = track_validation.get('is_in_range', True)
        format_warning = track_validation.get('warning')
        
        # Analyser le statut de formatage de la piste
        format_status = analyze_track_format_status(
            flux_transitions=flux_transitions,
            time_per_rev=time_per_rev,
            sectors_detected=sectors_detected,
            sectors_expected=sectors_expected,
            format_type=format_type
        )
        
        return AlignmentValue(
            track=track or "",
            percentage=percentage,
            base=base,
            bands=bands,
            sectors_detected=sectors_detected,
            sectors_expected=sectors_expected,
            flux_transitions=flux_transitions,
            time_per_rev=time_per_rev,
            format_type=format_type,
            is_in_format_range=is_in_range,
            format_warning=format_warning,
            is_formatted=format_status.get('is_formatted'),
            format_confidence=format_status.get('confidence'),
            format_status_message=format_status.get('status_message'),
            line_number=line_number,
            raw_line=line.strip(),
            timestamp=datetime.now()
        )
    
    @staticmethod
    def parse_output(output: str) -> List[AlignmentValue]:
        """
        Parse toute la sortie et retourne une liste de valeurs d'alignement
        """
        values = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines, 1):
            value = AlignmentParser.parse_line(line, line_number=i)
            if value:
                values.append(value)
        
        return values
    
    @staticmethod
    def calculate_statistics(values: List[AlignmentValue], limit: int = 160) -> Dict:
        """
        Calcule les statistiques d'alignement
        Groupe les lectures multiples par piste pour calculer des moyennes plus précises
        """
        if not values:
            return {
                "total_values": 0,
                "used_values": 0,
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
                "track_max": None,
                "track_normal": 0.0
            }
        
        # Grouper les valeurs par piste
        tracks_dict: Dict[str, List[AlignmentValue]] = {}
        for value in values:
            track_key = value.track if value.track else "unknown"
            if track_key not in tracks_dict:
                tracks_dict[track_key] = []
            tracks_dict[track_key].append(value)
        
        # Calculer les métriques avancées pour chaque piste
        track_averages: List[AlignmentValue] = []
        track_averages_all: List[AlignmentValue] = []  # Toutes les pistes (y compris hors limites)
        
        for track_key, track_values in tracks_dict.items():
            if not track_values:
                continue
            
            # Moyenne des pourcentages pour cette piste
            percentages = [v.percentage for v in track_values]
            avg_percentage = sum(percentages) / len(percentages) if percentages else 0.0
            
            # Prendre les valeurs de la première lecture comme référence
            first_value = track_values[0]
            
            # Moyenne des secteurs si disponibles
            sectors_detected = None
            sectors_expected = None
            if all(v.sectors_detected is not None for v in track_values):
                sectors_detected = int(sum(v.sectors_detected or 0 for v in track_values) / len(track_values))
                sectors_expected = first_value.sectors_expected
            
            # Moyenne des flux transitions si disponibles
            flux_transitions = None
            if all(v.flux_transitions is not None for v in track_values):
                flux_transitions = int(sum(v.flux_transitions or 0 for v in track_values) / len(track_values))
            
            # Moyenne du temps par révolution si disponible
            time_per_rev = None
            if all(v.time_per_rev is not None for v in track_values):
                time_per_rev = sum(v.time_per_rev or 0 for v in track_values) / len(track_values)
            
            # ===== ANALYSE DE COHÉRENCE =====
            consistency = None
            if len(percentages) > 1:
                # Calculer l'écart-type des pourcentages
                mean = avg_percentage
                variance = sum((p - mean) ** 2 for p in percentages) / len(percentages)
                std_dev = math.sqrt(variance)
                
                # Convertir en score de cohérence (0-100)
                # Écart-type de 0% = cohérence parfaite (100)
                # Écart-type de 5% = cohérence moyenne (50)
                # Écart-type de 10%+ = cohérence faible (0)
                consistency = max(0, 100 - (std_dev * 20))
                consistency = min(100, consistency)
            
            # ===== ANALYSE D'AZIMUT (Section 9.7 du manuel Panasonic) =====
            azimuth_score = None
            azimuth_status = None
            azimuth_cv = None
            if len(track_values) >= 3:
                # Analyser la variation des flux transitions
                flux_variations = [v.flux_transitions for v in track_values if v.flux_transitions is not None]
                
                if flux_variations and len(flux_variations) >= 3:
                    # Calculer l'écart-type des flux transitions
                    mean_flux = sum(flux_variations) / len(flux_variations)
                    variance_flux = sum((x - mean_flux) ** 2 for x in flux_variations) / len(flux_variations)
                    std_dev_flux = math.sqrt(variance_flux)
                    
                    # Coefficient de variation (CV) pour l'azimut
                    # CV < 0.5% = Excellent, < 1% = Bon, < 2% = Acceptable, >= 2% = Médiocre
                    cv_flux = (std_dev_flux / mean_flux) * 100 if mean_flux > 0 else 0
                    
                    # Analyser aussi la variation du time_per_rev
                    time_variations = [v.time_per_rev for v in track_values if v.time_per_rev is not None]
                    cv_time = 0
                    if time_variations and len(time_variations) >= 3:
                        mean_time = sum(time_variations) / len(time_variations)
                        time_variance = sum((x - mean_time) ** 2 for x in time_variations) / len(time_variations)
                        time_std_dev = math.sqrt(time_variance)
                        cv_time = (time_std_dev / mean_time) * 100 if mean_time > 0 else 0
                    
                    # Score combiné (moyenne pondérée: 70% flux, 30% time)
                    combined_cv = (cv_flux * 0.7) + (cv_time * 0.3)
                    azimuth_cv = combined_cv
                    
                    # Interprétation basée sur le manuel Panasonic
                    if combined_cv < 0.5:
                        azimuth_status = 'excellent'
                        azimuth_score = 100.0
                    elif combined_cv < 1.0:
                        azimuth_status = 'good'
                        azimuth_score = 90.0 - (combined_cv - 0.5) * 20
                    elif combined_cv < 2.0:
                        azimuth_status = 'acceptable'
                        azimuth_score = 80.0 - (combined_cv - 1.0) * 10
                    else:
                        azimuth_status = 'poor'
                        azimuth_score = max(0.0, 70.0 - (combined_cv - 2.0) * 5)
                    
                    azimuth_score = round(azimuth_score, 1)
            
            # ===== ANALYSE D'ASYSTRIE (Section 9.10 du manuel Panasonic) =====
            asymmetry_score = None
            asymmetry_status = None
            asymmetry_percent = None
            if len(track_values) >= 3:
                # Analyser les variations de time_per_rev
                time_variations = [v.time_per_rev for v in track_values if v.time_per_rev is not None]
                
                if time_variations and len(time_variations) >= 3:
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
                        time_asymmetry = ((deviation_above - deviation_below) / mean_time) * 100
                    else:
                        time_asymmetry = 0
                    
                    # Analyser aussi les flux transitions pour plus de précision
                    flux_variations = [v.flux_transitions for v in track_values if v.flux_transitions is not None]
                    flux_asymmetry = 0
                    if flux_variations and len(flux_variations) >= 3:
                        mean_flux = sum(flux_variations) / len(flux_variations)
                        min_flux = min(flux_variations)
                        max_flux = max(flux_variations)
                        if mean_flux > 0:
                            flux_dev_above = max_flux - mean_flux
                            flux_dev_below = mean_flux - min_flux
                            flux_asymmetry = ((flux_dev_above - flux_dev_below) / mean_flux) * 100
                    
                    # Asymétrie combinée (60% time, 40% flux)
                    combined_asymmetry = (abs(time_asymmetry) * 0.6) + (abs(flux_asymmetry) * 0.4)
                    asymmetry_percent = combined_asymmetry
                    
                    # Interprétation basée sur le manuel Panasonic
                    if combined_asymmetry < 0.1:
                        asymmetry_status = 'excellent'
                        asymmetry_score = 100.0
                    elif combined_asymmetry < 0.5:
                        asymmetry_status = 'good'
                        asymmetry_score = 95.0 - (combined_asymmetry - 0.1) * 10
                    elif combined_asymmetry < 1.0:
                        asymmetry_status = 'acceptable'
                        asymmetry_score = 90.0 - (combined_asymmetry - 0.5) * 20
                    else:
                        asymmetry_status = 'poor'
                        asymmetry_score = max(0.0, 80.0 - (combined_asymmetry - 1.0) * 10)
                    
                    asymmetry_score = round(asymmetry_score, 1)
            
            # ===== ANALYSE DE STABILITÉ =====
            stability = None
            if len(track_values) > 1:
                stability_scores = []
                
                # Stabilité des timings (time_per_rev)
                if all(v.time_per_rev is not None for v in track_values):
                    times = [v.time_per_rev for v in track_values]
                    mean_time = sum(times) / len(times)
                    time_variance = max(times) - min(times)
                    # Variance relative en pourcentage
                    if mean_time > 0:
                        time_stability = max(0, 100 - (time_variance / mean_time * 1000))
                        stability_scores.append(time_stability)
                
                # Stabilité des flux transitions
                if all(v.flux_transitions is not None for v in track_values):
                    fluxes = [v.flux_transitions for v in track_values]
                    mean_flux = sum(fluxes) / len(fluxes)
                    flux_variance = max(fluxes) - min(fluxes)
                    # Variance relative en pourcentage
                    if mean_flux > 0:
                        flux_stability = max(0, 100 - (flux_variance / mean_flux * 100))
                        stability_scores.append(flux_stability)
                
                # Stabilité des secteurs détectés
                if all(v.sectors_detected is not None for v in track_values):
                    sectors = [v.sectors_detected for v in track_values]
                    mean_sectors = sum(sectors) / len(sectors)
                    sector_variance = max(sectors) - min(sectors)
                    # Si variance = 0, stabilité parfaite
                    if sector_variance == 0:
                        sector_stability = 100
                    else:
                        # Pénalité basée sur la variance
                        sector_stability = max(0, 100 - (sector_variance * 10))
                    stability_scores.append(sector_stability)
                
                # Moyenne des scores de stabilité
                if stability_scores:
                    stability = sum(stability_scores) / len(stability_scores)
            
            # ===== DÉTECTION DE POSITIONNEMENT =====
            positioning_status = "correct"
            if len(percentages) > 1:
                # Si les pourcentages varient beaucoup, la tête peut être mal positionnée
                std_dev = math.sqrt(sum((p - avg_percentage) ** 2 for p in percentages) / len(percentages))
                
                # Si l'écart-type est élevé, le positionnement est instable
                if std_dev > 2.0:
                    positioning_status = "unstable"
                elif std_dev > 5.0:
                    positioning_status = "poor"
                
                # Si le pourcentage moyen est faible, le positionnement est probablement mauvais
                if avg_percentage < 95.0:
                    positioning_status = "poor"
                elif avg_percentage < 97.0:
                    positioning_status = "unstable"
            
            # Ajuster le pourcentage final en fonction de la cohérence, stabilité, azimut et asymétrie
            # Calcul multi-critères optimisé (Proposition 7 avec optimisations)
            # Pondération adaptative selon la disponibilité des métriques
            adjusted_percentage, weights_used, calculation_details = AlignmentParser._calculate_optimized_multi_criteria(
                avg_percentage=avg_percentage,
                consistency=consistency,
                stability=stability,
                azimuth_score=azimuth_score,
                azimuth_cv=azimuth_cv,
                asymmetry_score=asymmetry_score,
                asymmetry_percent=asymmetry_percent,
                num_readings=len(track_values)
            )
            
            # Déterminer si cette piste est dans les limites du format
            # Utiliser la validation de la première valeur (toutes les lectures d'une même piste ont le même statut)
            is_in_range = first_value.is_in_format_range if first_value.is_in_format_range is not None else True
            format_warning = first_value.format_warning
            
            # Analyser le statut de formatage (moyenne des lectures)
            format_status = analyze_track_format_status(
                flux_transitions=flux_transitions,
                time_per_rev=time_per_rev,
                sectors_detected=sectors_detected,
                sectors_expected=sectors_expected,
                format_type=first_value.format_type
            )
            
            # Créer une valeur moyenne pour cette piste avec les nouvelles métriques
            avg_value = AlignmentValue(
                track=first_value.track,
                percentage=round(adjusted_percentage, 3),
                base=first_value.base,
                bands=first_value.bands,
                sectors_detected=sectors_detected,
                sectors_expected=sectors_expected,
                flux_transitions=flux_transitions,
                time_per_rev=time_per_rev,
                format_type=first_value.format_type,
                consistency=round(consistency, 2) if consistency is not None else None,
                stability=round(stability, 2) if stability is not None else None,
                positioning_status=positioning_status,
                azimuth_score=azimuth_score,
                azimuth_status=azimuth_status,
                azimuth_cv=round(azimuth_cv, 3) if azimuth_cv is not None else None,
                asymmetry_score=asymmetry_score,
                asymmetry_status=asymmetry_status,
                asymmetry_percent=round(asymmetry_percent, 3) if asymmetry_percent is not None else None,
                calculation_details=calculation_details,
                is_in_format_range=is_in_range,
                format_warning=format_warning,
                is_formatted=format_status.get('is_formatted'),
                format_confidence=format_status.get('confidence'),
                format_status_message=format_status.get('status_message'),
                line_number=first_value.line_number,
                raw_line=f"Average of {len(track_values)} readings",
                timestamp=datetime.now()
            )
            
            # Ajouter à la liste complète (toutes les pistes)
            track_averages_all.append(avg_value)
            
            # Ajouter à la liste pour calcul final seulement si dans les limites
            if is_in_range:
                track_averages.append(avg_value)
        
        # Trier par numéro de piste (toutes les pistes)
        try:
            track_averages_all.sort(key=lambda v: float(v.track) if v.track and v.track.replace('.', '').isdigit() else 999)
            track_averages.sort(key=lambda v: float(v.track) if v.track and v.track.replace('.', '').isdigit() else 999)
        except (ValueError, AttributeError):
            pass
        
        # Limiter aux N premières pistes (pour calcul final, seulement celles dans les limites)
        limited_values = track_averages[:limit] if limit > 0 else track_averages
        
        # Toutes les valeurs (y compris hors limites) pour affichage
        all_values = track_averages_all[:limit * 2] if limit > 0 else track_averages_all  # Limite plus large pour inclure les pistes hors limites
        
        percentages = [v.percentage for v in limited_values]
        
        # Trouver la piste maximale
        track_max = None
        if limited_values:
            try:
                numeric_tracks = [float(v.track) for v in limited_values if v.track and v.track.replace('.', '').isdigit()]
                if numeric_tracks:
                    max_track_num = max(numeric_tracks)
                    track_max = f"{int(max_track_num)}.{int((max_track_num - int(max_track_num)) * 10)}"
            except (ValueError, AttributeError):
                if limited_values:
                    track_max = limited_values[-1].track
        
        # Calculer la moyenne, min, max
        average = sum(percentages) / len(percentages) if percentages else 0.0
        min_percent = min(percentages) if percentages else 0.0
        max_percent = max(percentages) if percentages else 0.0
        
        # Nombre de pistes utilisées
        track_normal = len(limited_values)
        
        return {
            "total_values": len(values),
            "used_values": len(limited_values),
            "total_tracks_tested": len(track_averages_all),  # Nombre total de pistes testées
            "tracks_in_range": len(track_averages),  # Nombre de pistes dans les limites
            "tracks_out_of_range": len(track_averages_all) - len(track_averages),  # Nombre de pistes hors limites
            "average": round(average, 3),
            "min": round(min_percent, 3),
            "max": round(max_percent, 3),
            "track_max": track_max,
            "track_normal": round(track_normal, 1),
            "values": [
                {
                    "track": v.track,
                    "percentage": v.percentage,
                    "base": v.base,
                    "bands": v.bands,
                    "sectors_detected": v.sectors_detected,
                    "sectors_expected": v.sectors_expected,
                    "flux_transitions": v.flux_transitions,
                    "time_per_rev": v.time_per_rev,
                    "format_type": v.format_type,
                    "consistency": v.consistency,
                    "stability": v.stability,
                    "positioning_status": v.positioning_status,
                    "azimuth_score": v.azimuth_score,
                    "azimuth_status": v.azimuth_status,
                    "azimuth_cv": v.azimuth_cv,
                    "asymmetry_score": v.asymmetry_score,
                    "asymmetry_status": v.asymmetry_status,
                    "asymmetry_percent": v.asymmetry_percent,
                    "calculation_details": v.calculation_details,
                    "is_in_format_range": v.is_in_format_range,
                    "format_warning": v.format_warning,
                    "is_formatted": v.is_formatted,
                    "format_confidence": v.format_confidence,
                    "format_status_message": v.format_status_message,
                    "line_number": v.line_number
                }
                for v in all_values  # Inclure toutes les pistes pour affichage
            ]
        }
    
    @staticmethod
    def get_alignment_quality(average: float) -> str:
        """
        Détermine la qualité de l'alignement basée sur la moyenne
        """
        if average >= 99.0:
            return "Perfect"
        elif average >= 97.0:
            return "Good"
        elif average >= 96.0:
            return "Average"
        else:
            return "Poor"

