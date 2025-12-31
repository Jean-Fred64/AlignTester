#!/usr/bin/env python3
"""
Script de test pour le Mode Direct
Teste les fonctionnalités du backend pour le mode d'alignement Direct
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from api.manual_alignment import ManualAlignmentMode, AlignmentMode, MODE_CONFIG
from api.greaseweazle import GreaseweazleExecutor


async def test_mode_config():
    """Teste la configuration des modes"""
    print("=" * 60)
    print("Test 1: Configuration des modes")
    print("=" * 60)
    
    for mode in AlignmentMode:
        config = MODE_CONFIG[mode]
        print(f"\nMode: {mode.value}")
        print(f"  - Lectures: {config['reads']}")
        print(f"  - Délai: {config['delay_ms']}ms")
        print(f"  - Timeout: {config['timeout']}s")
        print(f"  - Cohérence: {config['calculate_consistency']}")
        print(f"  - Stabilité: {config['calculate_stability']}")
        print(f"  - Décimales: {config['decimal_places']}")
    
    print("\n✅ Configuration des modes: OK")


async def test_mode_creation():
    """Teste la création d'une instance avec le mode Direct"""
    print("\n" + "=" * 60)
    print("Test 2: Création d'instance avec Mode Direct")
    print("=" * 60)
    
    manual_mode = ManualAlignmentMode()
    
    # Vérifier que le mode par défaut est DIRECT
    assert manual_mode.state.alignment_mode == AlignmentMode.DIRECT, \
        f"Mode par défaut devrait être DIRECT, mais est {manual_mode.state.alignment_mode}"
    
    print(f"✅ Mode par défaut: {manual_mode.state.alignment_mode.value}")
    
    # Tester le changement de mode
    manual_mode.set_alignment_mode(AlignmentMode.FINE_TUNE)
    assert manual_mode.state.alignment_mode == AlignmentMode.FINE_TUNE, \
        "Le mode devrait être FINE_TUNE"
    print(f"✅ Changement de mode vers FINE_TUNE: OK")
    
    manual_mode.set_alignment_mode(AlignmentMode.DIRECT)
    assert manual_mode.state.alignment_mode == AlignmentMode.DIRECT, \
        "Le mode devrait être DIRECT"
    print(f"✅ Changement de mode vers DIRECT: OK")


async def test_calculate_direct_percentage():
    """Teste le calcul de pourcentage en mode Direct"""
    print("\n" + "=" * 60)
    print("Test 3: Calcul de pourcentage Direct")
    print("=" * 60)
    
    manual_mode = ManualAlignmentMode()
    
    # Test avec 18/18 secteurs (100%)
    percentage = manual_mode._calculate_direct_percentage(18, 18)
    assert percentage == 100.0, f"18/18 devrait donner 100%, mais donne {percentage}%"
    print(f"✅ 18/18 secteurs = {percentage}%")
    
    # Test avec 17/18 secteurs (~94.4%)
    percentage = manual_mode._calculate_direct_percentage(17, 18)
    expected = round((17 / 18) * 100.0, 1)
    assert percentage == expected, f"17/18 devrait donner {expected}%, mais donne {percentage}%"
    print(f"✅ 17/18 secteurs = {percentage}%")
    
    # Test avec 0/18 secteurs (0%)
    percentage = manual_mode._calculate_direct_percentage(0, 18)
    assert percentage == 0.0, f"0/18 devrait donner 0%, mais donne {percentage}%"
    print(f"✅ 0/18 secteurs = {percentage}%")
    
    # Test avec 9/9 secteurs (100%)
    percentage = manual_mode._calculate_direct_percentage(9, 9)
    assert percentage == 100.0, f"9/9 devrait donner 100%, mais donne {percentage}%"
    print(f"✅ 9/9 secteurs = {percentage}%")


async def test_get_direct_indicator():
    """Teste la génération d'indicateur Direct"""
    print("\n" + "=" * 60)
    print("Test 4: Génération d'indicateur Direct")
    print("=" * 60)
    
    from api.manual_alignment import TrackReading, AlignmentQuality
    
    manual_mode = ManualAlignmentMode()
    
    # Test avec lecture parfaite (100%)
    reading = TrackReading(
        track=40,
        head=0,
        percentage=100.0,
        sectors_detected=18,
        sectors_expected=18,
        quality=AlignmentQuality.PERFECT
    )
    
    indicator = manual_mode._get_direct_indicator(reading)
    assert indicator["percentage"] == 100.0
    assert indicator["status"] == "excellent"
    assert indicator["symbol"] == "✓"
    assert indicator["sectors_ratio"] == "18/18"
    print(f"✅ Lecture parfaite: {indicator['symbol']} {indicator['status']} - {indicator['bars']}")
    
    # Test avec lecture bonne (95%)
    reading = TrackReading(
        track=40,
        head=0,
        percentage=95.0,
        sectors_detected=17,
        sectors_expected=18,
        quality=AlignmentQuality.GOOD
    )
    
    indicator = manual_mode._get_direct_indicator(reading)
    assert indicator["status"] == "good"
    assert indicator["symbol"] == "○"
    print(f"✅ Lecture bonne: {indicator['symbol']} {indicator['status']} - {indicator['bars']}")
    
    # Test avec lecture moyenne (90%)
    reading = TrackReading(
        track=40,
        head=0,
        percentage=90.0,
        sectors_detected=16,
        sectors_expected=18,
        quality=AlignmentQuality.AVERAGE
    )
    
    indicator = manual_mode._get_direct_indicator(reading)
    assert indicator["status"] == "caution"
    assert indicator["symbol"] == "△"
    print(f"✅ Lecture moyenne: {indicator['symbol']} {indicator['status']} - {indicator['bars']}")
    
    # Test avec lecture faible (80%)
    reading = TrackReading(
        track=40,
        head=0,
        percentage=80.0,
        sectors_detected=14,
        sectors_expected=18,
        quality=AlignmentQuality.POOR
    )
    
    indicator = manual_mode._get_direct_indicator(reading)
    assert indicator["status"] == "warning"
    assert indicator["symbol"] == "✗"
    print(f"✅ Lecture faible: {indicator['symbol']} {indicator['status']} - {indicator['bars']}")


async def test_state_dict():
    """Teste la génération du dictionnaire d'état"""
    print("\n" + "=" * 60)
    print("Test 5: Génération du dictionnaire d'état")
    print("=" * 60)
    
    manual_mode = ManualAlignmentMode()
    state_dict = manual_mode._get_state_dict()
    
    # Vérifier les champs essentiels
    assert "alignment_mode" in state_dict, "Le dictionnaire devrait contenir 'alignment_mode'"
    assert "alignment_mode_config" in state_dict, "Le dictionnaire devrait contenir 'alignment_mode_config'"
    
    print(f"✅ Mode actuel: {state_dict['alignment_mode']}")
    print(f"✅ Configuration du mode:")
    config = state_dict["alignment_mode_config"]
    print(f"   - Lectures: {config['reads']}")
    print(f"   - Délai: {config['delay_ms']}ms")
    print(f"   - Latence estimée: {config['estimated_latency_ms']}ms")


async def test_greaseweazle_connection():
    """Teste la connexion à Greaseweazle (si disponible)"""
    print("\n" + "=" * 60)
    print("Test 6: Connexion à Greaseweazle")
    print("=" * 60)
    
    executor = GreaseweazleExecutor()
    
    try:
        connection_status = executor.check_connection()
        
        if connection_status.get("connected", False):
            print(f"✅ Greaseweazle connecté: {connection_status.get('device', 'N/A')}")
            print(f"   - Port: {connection_status.get('port', 'N/A')}")
            print(f"   - Modèle: {connection_status.get('model', 'N/A')}")
        else:
            error_msg = connection_status.get('error', 'Raison inconnue')
            print(f"⚠️  Greaseweazle non connecté: {error_msg}")
            print("   (Ce n'est pas une erreur si le matériel n'est pas connecté)")
            print("   Pour tester avec le matériel:")
            print("   1. Vérifiez que Greaseweazle est branché")
            print("   2. Vérifiez le port série (COM10 dans votre cas)")
            print("   3. Testez manuellement: gw info")
    except Exception as e:
        print(f"⚠️  Erreur lors de la vérification de connexion: {e}")
        print("   (Ce n'est pas une erreur si le matériel n'est pas connecté)")
        import traceback
        traceback.print_exc()


async def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "=" * 60)
    print("TESTS DU MODE DIRECT - Backend")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    tests_warnings = 0
    
    try:
        await test_mode_config()
        tests_passed += 1
    except AssertionError as e:
        print(f"\n❌ ERREUR dans test_mode_config: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE dans test_mode_config: {e}")
        tests_failed += 1
    
    try:
        await test_mode_creation()
        tests_passed += 1
    except AssertionError as e:
        print(f"\n❌ ERREUR dans test_mode_creation: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE dans test_mode_creation: {e}")
        tests_failed += 1
    
    try:
        await test_calculate_direct_percentage()
        tests_passed += 1
    except AssertionError as e:
        print(f"\n❌ ERREUR dans test_calculate_direct_percentage: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE dans test_calculate_direct_percentage: {e}")
        tests_failed += 1
    
    try:
        await test_get_direct_indicator()
        tests_passed += 1
    except AssertionError as e:
        print(f"\n❌ ERREUR dans test_get_direct_indicator: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE dans test_get_direct_indicator: {e}")
        tests_failed += 1
    
    try:
        await test_state_dict()
        tests_passed += 1
    except AssertionError as e:
        print(f"\n❌ ERREUR dans test_state_dict: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE dans test_state_dict: {e}")
        tests_failed += 1
    
    # Test de connexion Greaseweazle (non bloquant)
    try:
        await test_greaseweazle_connection()
        tests_passed += 1
    except Exception as e:
        print(f"\n⚠️  AVERTISSEMENT dans test_greaseweazle_connection: {e}")
        print("   (Ce test n'est pas bloquant - Greaseweazle peut ne pas être connecté)")
        tests_warnings += 1
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ Tests réussis: {tests_passed}")
    if tests_failed > 0:
        print(f"❌ Tests échoués: {tests_failed}")
    if tests_warnings > 0:
        print(f"⚠️  Avertissements: {tests_warnings}")
    
    if tests_failed == 0:
        print("\n✅ TOUS LES TESTS CRITIQUES SONT PASSÉS")
        if tests_warnings > 0:
            print("⚠️  Certains tests ont des avertissements (non bloquants)")
        return 0
    else:
        print(f"\n❌ {tests_failed} TEST(S) ONT ÉCHOUÉ")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)

