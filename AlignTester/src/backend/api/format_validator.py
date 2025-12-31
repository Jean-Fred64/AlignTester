"""
Module de validation des formats de disquette
Vérifie si les pistes sont dans les limites du format (informatif, non bloquant)
"""

from typing import Dict, Optional, Tuple, Any
import math

# Définitions des limites de formats IBM
# Format: 'nom_format': {'max_cyl': N, 'heads': N, 'sectors_per_track': N}
FORMAT_LIMITS: Dict[str, Dict[str, int]] = {
    'ibm.160': {'max_cyl': 39, 'heads': 1, 'sectors_per_track': 8},
    'ibm.180': {'max_cyl': 39, 'heads': 1, 'sectors_per_track': 9},
    'ibm.320': {'max_cyl': 39, 'heads': 2, 'sectors_per_track': 8},
    'ibm.360': {'max_cyl': 39, 'heads': 2, 'sectors_per_track': 9},
    'ibm.720': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 9},
    'ibm.800': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 10},
    'ibm.1200': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 15},
    'ibm.1440': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 18},
    'ibm.1680': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 21},
    'ibm.dmf': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 21},
    'ibm.2880': {'max_cyl': 79, 'heads': 2, 'sectors_per_track': 36},
}


def parse_track_number(track_str: str) -> Optional[Tuple[int, int]]:
    """
    Parse un numéro de piste au format "XX.Y" ou "TXX.Y"
    Retourne (cylinder, head) ou None si invalide
    """
    if not track_str:
        return None
    
    # Enlever le préfixe "T" si présent
    track_str = track_str.lstrip('T').strip()
    
    try:
        parts = track_str.split('.')
        if len(parts) != 2:
            return None
        
        cylinder = int(parts[0])
        head = int(parts[1])
        
        return (cylinder, head)
    except (ValueError, IndexError):
        return None


def is_track_in_format_range(track_num: int, format_type: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Vérifie si une piste est dans la plage valide du format
    
    Args:
        track_num: Numéro de cylindre (0-83 typiquement)
        format_type: Type de format (ex: 'ibm.1440', 'ibm.720')
    
    Returns:
        Tuple (is_in_range, warning_message)
        - is_in_range: True si la piste est dans les limites, False sinon
        - warning_message: Message d'avertissement si hors limites, None sinon
    """
    if not format_type:
        # Format inconnu, on accepte par défaut (pas de validation possible)
        return (True, None)
    
    # Normaliser le format (enlever préfixes, mettre en minuscules)
    format_key = format_type.lower().strip()
    
    # Chercher dans les limites définies
    if format_key not in FORMAT_LIMITS:
        # Format non reconnu, on accepte par défaut
        return (True, None)
    
    limits = FORMAT_LIMITS[format_key]
    max_cyl = limits['max_cyl']
    
    if track_num > max_cyl:
        warning = (
            f"Piste {track_num} hors limites du format {format_type} "
            f"(max: {max_cyl}). Cette piste n'est pas formatée selon les spécifications. "
            f"Les données sont affichées à titre informatif mais ne sont pas incluses "
            f"dans le calcul final de l'alignement."
        )
        return (False, warning)
    
    return (True, None)


def get_format_info(format_type: Optional[str]) -> Optional[Dict[str, int]]:
    """
    Retourne les informations sur un format (limites, secteurs, etc.)
    """
    if not format_type:
        return None
    
    format_key = format_type.lower().strip()
    return FORMAT_LIMITS.get(format_key)


def get_expected_sectors_for_format(format_type: Optional[str]) -> Optional[int]:
    """
    Retourne le nombre de secteurs attendus pour un format
    """
    info = get_format_info(format_type)
    if info:
        return info.get('sectors_per_track')
    return None


def validate_track_for_format(
    track_str: str,
    format_type: Optional[str]
) -> Dict[str, Any]:
    """
    Valide une piste pour un format donné
    
    Args:
        track_str: Numéro de piste au format "XX.Y" ou "TXX.Y"
        format_type: Type de format
    
    Returns:
        Dict avec:
        - is_in_range: bool
        - warning: Optional[str]
        - cylinder: Optional[int]
        - head: Optional[int]
        - format_info: Optional[Dict]
    """
    parsed = parse_track_number(track_str)
    
    if parsed is None:
        return {
            'is_in_range': True,  # Par défaut, on accepte si on ne peut pas parser
            'warning': None,
            'cylinder': None,
            'head': None,
            'format_info': None
        }
    
    cylinder, head = parsed
    is_in_range, warning = is_track_in_format_range(cylinder, format_type)
    format_info = get_format_info(format_type)
    
    return {
        'is_in_range': is_in_range,
        'warning': warning,
        'cylinder': cylinder,
        'head': head,
        'format_info': format_info
    }


def analyze_track_format_status(
    flux_transitions: Optional[int],
    time_per_rev: Optional[float],
    sectors_detected: Optional[int],
    sectors_expected: Optional[int],
    format_type: Optional[str]
) -> Dict[str, Any]:
    """
    Analyse si une piste est formatée ou contient seulement du flux résiduel
    
    Args:
        flux_transitions: Nombre de transitions de flux détectées
        time_per_rev: Temps par révolution en ms
        sectors_detected: Nombre de secteurs détectés
        sectors_expected: Nombre de secteurs attendus
        format_type: Type de format (ex: 'ibm.1440', 'ibm.720')
    
    Returns:
        Dict avec:
        - is_formatted: bool - True si la piste semble formatée
        - confidence: float - Niveau de confiance (0-100)
        - flux_density: float - Densité de flux (transitions/ms)
        - sector_ratio: float - Ratio secteurs détectés/attendus
        - status_message: str - Message descriptif
    """
    # Valeurs par défaut si données manquantes
    if flux_transitions is None or time_per_rev is None or time_per_rev == 0:
        return {
            'is_formatted': False,
            'confidence': 0.0,
            'flux_density': 0.0,
            'sector_ratio': 0.0,
            'status_message': 'Données de flux insuffisantes pour déterminer le formatage'
        }
    
    # Calculer la densité de flux
    flux_density = flux_transitions / time_per_rev if time_per_rev > 0 else 0.0
    
    # Calculer le ratio de secteurs
    sector_ratio = 0.0
    if sectors_expected and sectors_expected > 0:
        sector_ratio = (sectors_detected or 0) / sectors_expected
    elif sectors_detected and sectors_detected > 0:
        # Si on a des secteurs détectés mais pas de valeur attendue, utiliser le format
        expected = get_expected_sectors_for_format(format_type)
        if expected and expected > 0:
            sector_ratio = sectors_detected / expected
    
    # Seuils minimaux de flux pour une piste formatée (basés sur les formats IBM)
    min_flux_for_formatted = {
        'ibm.720': 30000,    # ~30k transitions pour 9 secteurs à 250kbps
        'ibm.1440': 60000,   # ~60k transitions pour 18 secteurs à 500kbps
        'ibm.360': 30000,    # ~30k transitions pour 9 secteurs à 250kbps
        'ibm.1200': 50000,   # ~50k transitions pour 15 secteurs à 500kbps
        'ibm.800': 35000,    # ~35k transitions pour 10 secteurs à 250kbps
    }
    
    # Seuil par défaut si format inconnu
    min_flux = min_flux_for_formatted.get(format_type or '', 30000)
    
    # Critères de formatage
    is_formatted = False
    confidence = 0.0
    status_message = ""
    
    # Critère 1: Nombre minimum de transitions de flux
    if flux_transitions < min_flux:
        status_message = f"Flux insuffisant ({flux_transitions} < {min_flux}) - piste probablement non formatée"
        return {
            'is_formatted': False,
            'confidence': 0.0,
            'flux_density': flux_density,
            'sector_ratio': sector_ratio,
            'status_message': status_message
        }
    
    # Critère 2: Ratio de secteurs
    if sectors_expected and sectors_expected > 0:
        if sector_ratio >= 0.9:
            # Au moins 90% des secteurs attendus détectés
            is_formatted = True
            confidence = min(100.0, sector_ratio * 100.0)
            status_message = f"Piste formatée détectée ({sectors_detected}/{sectors_expected} secteurs, {confidence:.1f}% confiance)"
        elif sector_ratio >= 0.5:
            # Entre 50% et 90% - formatage partiel ou problème d'alignement
            is_formatted = True
            confidence = sector_ratio * 80.0  # Confiance réduite
            status_message = f"Piste partiellement formatée ({sectors_detected}/{sectors_expected} secteurs, {confidence:.1f}% confiance)"
        else:
            # Moins de 50% - probablement non formatée ou très mal alignée
            is_formatted = False
            confidence = sector_ratio * 50.0
            status_message = f"Piste probablement non formatée ({sectors_detected}/{sectors_expected} secteurs seulement)"
    else:
        # Pas de secteurs attendus, utiliser uniquement la densité de flux
        if flux_density > 100:
            # Densité élevée suggère une piste formatée
            is_formatted = True
            confidence = min(100.0, flux_density / 2.0)  # Normaliser
            status_message = f"Flux détecté (densité: {flux_density:.1f} transitions/ms) - piste peut-être formatée"
        else:
            is_formatted = False
            confidence = 0.0
            status_message = f"Flux faible (densité: {flux_density:.1f} transitions/ms) - piste probablement non formatée"
    
    # Ajuster la confiance selon la densité de flux
    if is_formatted and flux_density > 0:
        # Si la densité est très élevée, augmenter la confiance
        if flux_density > 200:
            confidence = min(100.0, confidence * 1.1)
        # Si la densité est faible, réduire la confiance
        elif flux_density < 50:
            confidence = confidence * 0.8
    
    return {
        'is_formatted': is_formatted,
        'confidence': round(confidence, 2),
        'flux_density': round(flux_density, 2),
        'sector_ratio': round(sector_ratio, 3),
        'status_message': status_message
    }

