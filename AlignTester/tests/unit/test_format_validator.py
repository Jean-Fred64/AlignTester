"""
Tests unitaires pour format_validator.py
"""

import pytest
from api.format_validator import (
    parse_track_number,
    is_track_in_format_range,
    get_format_info,
    get_expected_sectors_for_format,
    validate_track_for_format,
    FORMAT_LIMITS
)


class TestFormatValidator:
    """Tests pour format_validator"""
    
    def test_parse_track_number_valid(self):
        """Test parsing de numéro de piste valide"""
        assert parse_track_number("40.0") == (40, 0)
        assert parse_track_number("79.1") == (79, 1)
        assert parse_track_number("0.0") == (0, 0)
        assert parse_track_number("T40.0") == (40, 0)
        assert parse_track_number("T79.1") == (79, 1)
    
    def test_parse_track_number_invalid(self):
        """Test parsing de numéro de piste invalide"""
        assert parse_track_number("") is None
        assert parse_track_number("40") is None
        assert parse_track_number("40.") is None
        assert parse_track_number(".0") is None
        assert parse_track_number("invalid") is None
        assert parse_track_number("40.0.1") is None
    
    def test_is_track_in_format_range_ibm_720(self):
        """Test validation pour IBM 720 (max cyl: 79)"""
        # Dans les limites
        is_in, warning = is_track_in_format_range(0, "ibm.720")
        assert is_in is True
        assert warning is None
        
        is_in, warning = is_track_in_format_range(79, "ibm.720")
        assert is_in is True
        assert warning is None
        
        # Hors limites
        is_in, warning = is_track_in_format_range(80, "ibm.720")
        assert is_in is False
        assert warning is not None
        assert "hors limites" in warning.lower()
        assert "80" in warning
        assert "79" in warning
        
        is_in, warning = is_track_in_format_range(81, "ibm.720")
        assert is_in is False
        assert warning is not None
    
    def test_is_track_in_format_range_ibm_1440(self):
        """Test validation pour IBM 1440 (max cyl: 79)"""
        # Dans les limites
        is_in, warning = is_track_in_format_range(40, "ibm.1440")
        assert is_in is True
        assert warning is None
        
        is_in, warning = is_track_in_format_range(79, "ibm.1440")
        assert is_in is True
        assert warning is None
        
        # Hors limites
        is_in, warning = is_track_in_format_range(80, "ibm.1440")
        assert is_in is False
        assert warning is not None
    
    def test_is_track_in_format_range_ibm_360(self):
        """Test validation pour IBM 360 (max cyl: 39)"""
        # Dans les limites
        is_in, warning = is_track_in_format_range(0, "ibm.360")
        assert is_in is True
        assert warning is None
        
        is_in, warning = is_track_in_format_range(39, "ibm.360")
        assert is_in is True
        assert warning is None
        
        # Hors limites
        is_in, warning = is_track_in_format_range(40, "ibm.360")
        assert is_in is False
        assert warning is not None
    
    def test_is_track_in_format_range_unknown_format(self):
        """Test avec format inconnu"""
        is_in, warning = is_track_in_format_range(100, "unknown.format")
        assert is_in is True  # Par défaut, on accepte
        assert warning is None
    
    def test_is_track_in_format_range_none_format(self):
        """Test avec format None"""
        is_in, warning = is_track_in_format_range(100, None)
        assert is_in is True
        assert warning is None
    
    def test_get_format_info(self):
        """Test récupération d'infos de format"""
        info = get_format_info("ibm.720")
        assert info is not None
        assert info['max_cyl'] == 79
        assert info['heads'] == 2
        assert info['sectors_per_track'] == 9
        
        info = get_format_info("ibm.1440")
        assert info is not None
        assert info['max_cyl'] == 79
        assert info['sectors_per_track'] == 18
        
        info = get_format_info("unknown")
        assert info is None
        
        info = get_format_info(None)
        assert info is None
    
    def test_get_expected_sectors_for_format(self):
        """Test récupération du nombre de secteurs attendus"""
        assert get_expected_sectors_for_format("ibm.720") == 9
        assert get_expected_sectors_for_format("ibm.1440") == 18
        assert get_expected_sectors_for_format("ibm.360") == 9
        assert get_expected_sectors_for_format("ibm.1200") == 15
        assert get_expected_sectors_for_format("unknown") is None
        assert get_expected_sectors_for_format(None) is None
    
    def test_validate_track_for_format_valid(self):
        """Test validation complète d'une piste valide"""
        result = validate_track_for_format("40.0", "ibm.1440")
        
        assert result['is_in_range'] is True
        assert result['warning'] is None
        assert result['cylinder'] == 40
        assert result['head'] == 0
        assert result['format_info'] is not None
        assert result['format_info']['max_cyl'] == 79
    
    def test_validate_track_for_format_out_of_range(self):
        """Test validation d'une piste hors limites"""
        result = validate_track_for_format("80.0", "ibm.1440")
        
        assert result['is_in_range'] is False
        assert result['warning'] is not None
        assert result['cylinder'] == 80
        assert result['head'] == 0
        assert "hors limites" in result['warning'].lower()
    
    def test_validate_track_for_format_with_t_prefix(self):
        """Test validation avec préfixe T"""
        result = validate_track_for_format("T40.0", "ibm.1440")
        
        assert result['is_in_range'] is True
        assert result['cylinder'] == 40
        assert result['head'] == 0
    
    def test_validate_track_for_format_invalid_track(self):
        """Test validation avec piste invalide"""
        result = validate_track_for_format("invalid", "ibm.1440")
        
        assert result['is_in_range'] is True  # Par défaut accepté si invalide
        assert result['warning'] is None
        assert result['cylinder'] is None
        assert result['head'] is None
    
    def test_validate_track_for_format_unknown_format(self):
        """Test validation avec format inconnu"""
        result = validate_track_for_format("80.0", "unknown.format")
        
        assert result['is_in_range'] is True  # Format inconnu = accepté par défaut
        assert result['warning'] is None
        assert result['cylinder'] == 80
        assert result['head'] == 0
    
    def test_all_formats_in_limits(self):
        """Test que tous les formats définis ont des limites valides"""
        for format_name, limits in FORMAT_LIMITS.items():
            assert 'max_cyl' in limits
            assert 'heads' in limits
            assert 'sectors_per_track' in limits
            assert limits['max_cyl'] >= 0
            assert limits['heads'] > 0
            assert limits['sectors_per_track'] > 0
    
    def test_analyze_track_format_status_formatted(self):
        """Test détection de formatage - piste formatée"""
        from api.format_validator import analyze_track_format_status
        
        # Piste formatée IBM 1440 avec 18 secteurs
        result = analyze_track_format_status(
            flux_transitions=100000,
            time_per_rev=200.0,
            sectors_detected=18,
            sectors_expected=18,
            format_type="ibm.1440"
        )
        
        assert result['is_formatted'] is True
        assert result['confidence'] > 80.0
        assert result['flux_density'] > 0
        assert result['sector_ratio'] == 1.0
        assert "formatée" in result['status_message'].lower()
    
    def test_analyze_track_format_status_not_formatted(self):
        """Test détection de formatage - piste non formatée"""
        from api.format_validator import analyze_track_format_status
        
        # Piste non formatée avec peu de flux
        result = analyze_track_format_status(
            flux_transitions=5000,
            time_per_rev=200.0,
            sectors_detected=0,
            sectors_expected=18,
            format_type="ibm.1440"
        )
        
        assert result['is_formatted'] is False
        assert result['confidence'] < 50.0
        assert "non formatée" in result['status_message'].lower() or "insuffisant" in result['status_message'].lower()
    
    def test_analyze_track_format_status_partial(self):
        """Test détection de formatage - piste partiellement formatée"""
        from api.format_validator import analyze_track_format_status
        
        # Piste avec seulement 50% des secteurs
        result = analyze_track_format_status(
            flux_transitions=80000,
            time_per_rev=200.0,
            sectors_detected=9,
            sectors_expected=18,
            format_type="ibm.1440"
        )
        
        assert result['is_formatted'] is True  # Toujours considérée formatée mais avec confiance réduite
        assert result['confidence'] < 100.0
        assert result['sector_ratio'] == 0.5
    
    def test_analyze_track_format_status_insufficient_flux(self):
        """Test détection avec flux insuffisant"""
        from api.format_validator import analyze_track_format_status
        
        # Flux en dessous du minimum
        result = analyze_track_format_status(
            flux_transitions=10000,  # < 60000 pour ibm.1440
            time_per_rev=200.0,
            sectors_detected=18,
            sectors_expected=18,
            format_type="ibm.1440"
        )
        
        assert result['is_formatted'] is False
        assert result['confidence'] == 0.0
        assert "insuffisant" in result['status_message'].lower()
    
    def test_analyze_track_format_status_missing_data(self):
        """Test détection avec données manquantes"""
        from api.format_validator import analyze_track_format_status
        
        # Données manquantes
        result = analyze_track_format_status(
            flux_transitions=None,
            time_per_rev=None,
            sectors_detected=None,
            sectors_expected=None,
            format_type="ibm.1440"
        )
        
        assert result['is_formatted'] is False
        assert result['confidence'] == 0.0
        assert "insuffisantes" in result['status_message'].lower()

