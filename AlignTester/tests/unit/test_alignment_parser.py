"""
Tests unitaires pour alignment_parser.py
"""

import pytest
from api.alignment_parser import AlignmentParser, AlignmentValue


class TestAlignmentParser:
    """Tests pour AlignmentParser"""
    
    def test_parse_line_complete_format(self):
        """Test parsing d'une ligne complète"""
        line = "00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us"
        result = AlignmentParser.parse_line(line, line_number=1)
        
        assert result is not None
        assert result.track == "00.0"
        assert result.percentage == 99.911
        assert result.base == 1.000
        assert result.bands == [2.002, 3.001, 4.006]
        assert result.line_number == 1
        assert result.raw_line == line.strip()
    
    def test_parse_line_without_base(self):
        """Test parsing d'une ligne sans valeur de base"""
        line = "01.0    : [98.5%], band: 2.002 us"
        result = AlignmentParser.parse_line(line)
        
        assert result is not None
        assert result.track == "01.0"
        assert result.percentage == 98.5
        assert result.base is None
    
    def test_parse_line_without_track(self):
        """Test parsing d'une ligne sans numéro de piste"""
        line = "base: 1.000 us [99.911%]"
        result = AlignmentParser.parse_line(line)
        
        assert result is not None
        assert result.track == ""
        assert result.percentage == 99.911
    
    def test_parse_line_percentage_only(self):
        """Test parsing avec seulement un pourcentage"""
        line = "[95.5%]"
        result = AlignmentParser.parse_line(line)
        
        assert result is not None
        assert result.percentage == 95.5
        assert result.track == ""
        assert result.base is None
        assert result.bands is None
    
    def test_parse_line_empty(self):
        """Test parsing d'une ligne vide"""
        result = AlignmentParser.parse_line("")
        assert result is None
        
        result = AlignmentParser.parse_line("   ")
        assert result is None
    
    def test_parse_line_no_percentage(self):
        """Test parsing d'une ligne sans pourcentage"""
        line = "00.0    : base: 1.000 us"
        result = AlignmentParser.parse_line(line)
        assert result is None
    
    def test_parse_line_invalid_percentage(self):
        """Test parsing avec pourcentage invalide"""
        line = "[invalid%]"
        result = AlignmentParser.parse_line(line)
        assert result is None
    
    def test_parse_output_multiple_lines(self, sample_alignment_output):
        """Test parsing de plusieurs lignes"""
        results = AlignmentParser.parse_output(sample_alignment_output)
        
        assert len(results) == 5
        assert all(isinstance(r, AlignmentValue) for r in results)
        assert results[0].track == "00.0"
        assert results[0].percentage == 99.911
        assert results[1].track == "00.1"
        assert results[1].percentage == 99.742
    
    def test_parse_output_empty(self):
        """Test parsing d'une sortie vide"""
        results = AlignmentParser.parse_output("")
        assert len(results) == 0
    
    def test_parse_output_with_empty_lines(self):
        """Test parsing avec des lignes vides"""
        output = "00.0    : base: 1.000 us [99.911%]\n\n01.0    : base: 1.001 us [99.856%]\n   \n"
        results = AlignmentParser.parse_output(output)
        
        assert len(results) == 2
        assert results[0].track == "00.0"
        assert results[1].track == "01.0"
    
    def test_calculate_statistics(self, sample_alignment_output):
        """Test calcul des statistiques"""
        values = AlignmentParser.parse_output(sample_alignment_output)
        stats = AlignmentParser.calculate_statistics(values, limit=10)
        
        assert stats["total_values"] == 5
        # Les valeurs sont groupées par piste, donc used_values = nombre de pistes uniques
        assert stats["used_values"] == 5  # 5 pistes différentes (00.0, 00.1, 01.0, 01.1, 02.0)
        assert stats["average"] == pytest.approx(99.844, abs=0.001)
        assert stats["min"] == pytest.approx(99.742, abs=0.001)
        assert stats["max"] == pytest.approx(99.923, abs=0.001)
        # track_max peut être "2.0" ou "02.0" selon le formatage
        assert stats["track_max"] in ["2.0", "02.0"]
        # track_normal est maintenant le nombre de pistes (après groupement)
        assert stats["track_normal"] == 5.0
        assert len(stats["values"]) == 5
    
    def test_calculate_statistics_with_limit(self, sample_alignment_output):
        """Test calcul des statistiques avec limite"""
        # Créer 200 valeurs avec des pistes différentes pour éviter le groupement
        values_list = []
        for i in range(200):
            track_num = i % 80  # Pistes 0-79 (dans limites)
            head = (i // 80) % 2
            value = AlignmentParser.parse_line(
                f"{track_num}.{head}    : base: 1.000 us [99.911%], band: 2.002 us"
            )
            if value:
                values_list.append(value)
        
        stats = AlignmentParser.calculate_statistics(values_list, limit=160)
        
        assert stats["total_values"] == len(values_list)
        # Les valeurs sont groupées par piste, donc used_values peut être différent
        assert stats["used_values"] <= 160
        assert stats["used_values"] > 0
    
    def test_calculate_statistics_empty(self):
        """Test calcul des statistiques avec liste vide"""
        stats = AlignmentParser.calculate_statistics([])
        
        assert stats["total_values"] == 0
        assert stats["used_values"] == 0
        assert stats["average"] == 0.0
        assert stats["min"] == 0.0
        assert stats["max"] == 0.0
    
    def test_get_alignment_quality_perfect(self):
        """Test classification de qualité - Perfect"""
        assert AlignmentParser.get_alignment_quality(99.5) == "Perfect"
        assert AlignmentParser.get_alignment_quality(99.0) == "Perfect"
        assert AlignmentParser.get_alignment_quality(99.999) == "Perfect"
    
    def test_get_alignment_quality_good(self):
        """Test classification de qualité - Good"""
        assert AlignmentParser.get_alignment_quality(97.5) == "Good"
        assert AlignmentParser.get_alignment_quality(98.9) == "Good"
        assert AlignmentParser.get_alignment_quality(97.0) == "Good"
    
    def test_get_alignment_quality_average(self):
        """Test classification de qualité - Average"""
        assert AlignmentParser.get_alignment_quality(96.5) == "Average"
        assert AlignmentParser.get_alignment_quality(96.9) == "Average"
        assert AlignmentParser.get_alignment_quality(96.0) == "Average"
    
    def test_get_alignment_quality_poor(self):
        """Test classification de qualité - Poor"""
        assert AlignmentParser.get_alignment_quality(95.5) == "Poor"
        assert AlignmentParser.get_alignment_quality(90.0) == "Poor"
        assert AlignmentParser.get_alignment_quality(85.0) == "Poor"
    
    def test_parse_line_with_bands(self):
        """Test parsing avec plusieurs bandes"""
        line = "00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us, 5.010 us"
        result = AlignmentParser.parse_line(line)
        
        assert result is not None
        assert len(result.bands) == 4
        assert result.bands == [2.002, 3.001, 4.006, 5.010]
    
    def test_parse_line_single_band(self):
        """Test parsing avec une seule bande"""
        line = "00.0    : base: 1.000 us [99.911%], band: 2.002 us"
        result = AlignmentParser.parse_line(line)
        
        assert result is not None
        assert result.bands == [2.002]
    
    def test_parse_line_with_format_validation_in_range(self):
        """Test parsing avec validation de format - piste dans les limites"""
        line = "T40.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)"
        result = AlignmentParser.parse_line(line, line_number=1)
        
        # Forcer le format pour le test
        result.format_type = "ibm.1440"
        # Re-parser avec le format pour déclencher la validation
        from api.format_validator import validate_track_for_format
        validation = validate_track_for_format(result.track, result.format_type)
        result.is_in_format_range = validation['is_in_range']
        result.format_warning = validation['warning']
        
        assert result is not None
        assert result.track == "40.0"
        assert result.is_in_format_range is True
        assert result.format_warning is None
    
    def test_parse_line_with_format_validation_out_of_range(self):
        """Test parsing avec validation de format - piste hors limites"""
        line = "T80.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)"
        result = AlignmentParser.parse_line(line, line_number=1)
        
        # Forcer le format pour le test
        result.format_type = "ibm.1440"
        # Re-parser avec le format pour déclencher la validation
        from api.format_validator import validate_track_for_format
        validation = validate_track_for_format(result.track, result.format_type)
        result.is_in_format_range = validation['is_in_range']
        result.format_warning = validation['warning']
        
        assert result is not None
        assert result.track == "80.0"
        assert result.is_in_format_range is False
        assert result.format_warning is not None
        assert "hors limites" in result.format_warning.lower()
    
    def test_calculate_statistics_excludes_out_of_range_tracks(self):
        """Test que les pistes hors limites sont exclues du calcul final"""
        # Créer des valeurs : 3 pistes dans limites, 2 hors limites
        values = []
        
        # Pistes dans limites (0-79 pour ibm.1440)
        for track_num in [40, 50, 60]:
            value = AlignmentValue(
                track=f"{track_num}.0",
                percentage=99.0,
                format_type="ibm.1440",
                sectors_detected=18,
                sectors_expected=18
            )
            # Valider
            from api.format_validator import validate_track_for_format
            validation = validate_track_for_format(value.track, value.format_type)
            value.is_in_format_range = validation['is_in_range']
            value.format_warning = validation['warning']
            values.append(value)
        
        # Pistes hors limites (80-81)
        for track_num in [80, 81]:
            value = AlignmentValue(
                track=f"{track_num}.0",
                percentage=100.0,  # Faux positif
                format_type="ibm.1440",
                sectors_detected=18,
                sectors_expected=18
            )
            # Valider
            from api.format_validator import validate_track_for_format
            validation = validate_track_for_format(value.track, value.format_type)
            value.is_in_format_range = validation['is_in_range']
            value.format_warning = validation['warning']
            values.append(value)
        
        stats = AlignmentParser.calculate_statistics(values, limit=10)
        
        # Vérifier que seules les pistes dans limites sont utilisées pour le calcul
        assert stats["total_values"] == 5
        assert stats["tracks_in_range"] == 3  # Seulement les pistes 40, 50, 60
        assert stats["tracks_out_of_range"] == 2  # Pistes 80, 81
        assert stats["average"] == 99.0  # Moyenne des 3 pistes dans limites (99.0, 99.0, 99.0)
        assert stats["used_values"] == 3  # Utilisées pour le calcul
        
        # Mais toutes les valeurs sont conservées pour affichage
        assert len(stats["values"]) == 5  # Toutes les pistes sont dans values
    
    def test_calculate_statistics_all_tracks_in_range(self):
        """Test avec toutes les pistes dans les limites"""
        values = []
        
        for track_num in [0, 40, 79]:  # Toutes dans limites pour ibm.1440
            value = AlignmentValue(
                track=f"{track_num}.0",
                percentage=99.0 + (track_num % 10) * 0.1,
                format_type="ibm.1440"
            )
            from api.format_validator import validate_track_for_format
            validation = validate_track_for_format(value.track, value.format_type)
            value.is_in_format_range = validation['is_in_range']
            value.format_warning = validation['warning']
            values.append(value)
        
        stats = AlignmentParser.calculate_statistics(values, limit=10)
        
        assert stats["tracks_in_range"] == 3
        assert stats["tracks_out_of_range"] == 0
        assert stats["used_values"] == 3
        assert len(stats["values"]) == 3
    
    def test_calculate_statistics_all_tracks_out_of_range(self):
        """Test avec toutes les pistes hors limites"""
        values = []
        
        for track_num in [80, 81, 82]:  # Toutes hors limites pour ibm.1440
            value = AlignmentValue(
                track=f"{track_num}.0",
                percentage=100.0,
                format_type="ibm.1440"
            )
            from api.format_validator import validate_track_for_format
            validation = validate_track_for_format(value.track, value.format_type)
            value.is_in_format_range = validation['is_in_range']
            value.format_warning = validation['warning']
            values.append(value)
        
        stats = AlignmentParser.calculate_statistics(values, limit=10)
        
        assert stats["tracks_in_range"] == 0
        assert stats["tracks_out_of_range"] == 3
        assert stats["used_values"] == 0  # Aucune piste utilisée pour le calcul
        assert stats["average"] == 0.0  # Pas de moyenne possible
        # Mais toutes les valeurs sont conservées pour affichage
        assert len(stats["values"]) == 3
    
    def test_calculate_statistics_format_warning_in_values(self):
        """Test que les avertissements de format sont inclus dans les valeurs"""
        value = AlignmentValue(
            track="80.0",
            percentage=100.0,
            format_type="ibm.1440"
        )
        from api.format_validator import validate_track_for_format
        validation = validate_track_for_format(value.track, value.format_type)
        value.is_in_format_range = validation['is_in_range']
        value.format_warning = validation['warning']
        
        stats = AlignmentParser.calculate_statistics([value], limit=10)
        
        assert len(stats["values"]) == 1
        result_value = stats["values"][0]
        assert result_value["is_in_format_range"] is False
        assert result_value["format_warning"] is not None
        assert "hors limites" in result_value["format_warning"].lower()

