#!/usr/bin/env python3
"""
Script de test pour l'API du Mode Direct
Teste les endpoints API pour le mode d'alignement Direct
"""

import requests
import json
import time
import sys

API_BASE_URL = "http://localhost:8000/api"


def test_api_info():
    """Teste l'endpoint /info"""
    print("=" * 60)
    print("Test API: /info")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/info", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Greaseweazle disponible: {data.get('align_available', False)}")
        print(f"   - Version: {data.get('version', 'N/A')}")
        print(f"   - Chemin: {data.get('gw_path', 'N/A')}")
        
        return data.get('align_available', False)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def test_manual_state():
    """Teste l'endpoint /manual/state"""
    print("\n" + "=" * 60)
    print("Test API: /manual/state")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/manual/state", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ État récupéré")
        print(f"   - Mode: {data.get('alignment_mode', 'N/A')}")
        print(f"   - En cours: {data.get('is_running', False)}")
        print(f"   - Piste actuelle: T{data.get('current_track', 0)}.{data.get('current_head', 0)}")
        
        if 'alignment_mode_config' in data:
            config = data['alignment_mode_config']
            print(f"   - Configuration:")
            print(f"     * Lectures: {config.get('reads', 'N/A')}")
            print(f"     * Délai: {config.get('delay_ms', 'N/A')}ms")
            print(f"     * Latence estimée: {config.get('estimated_latency_ms', 'N/A')}ms")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return None


def test_change_mode(mode: str):
    """Teste le changement de mode via /manual/settings"""
    print("\n" + "=" * 60)
    print(f"Test API: Changement de mode vers '{mode}'")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/manual/settings",
            json={"alignment_mode": mode},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            state = data.get('state', {})
            print(f"✅ Mode changé vers: {state.get('alignment_mode', 'N/A')}")
            return True
        else:
            print(f"❌ Échec du changement de mode")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"   Détails: {error_data.get('detail', 'N/A')}")
            except:
                print(f"   Réponse: {e.response.text}")
        return False


def test_invalid_mode():
    """Teste avec un mode invalide"""
    print("\n" + "=" * 60)
    print("Test API: Mode invalide")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/manual/settings",
            json={"alignment_mode": "invalid_mode"},
            timeout=5
        )
        
        # On s'attend à une erreur 400
        if response.status_code == 400:
            print("✅ Erreur correctement retournée pour mode invalide")
            error_data = response.json()
            print(f"   Message: {error_data.get('detail', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur inattendue: code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return False


def test_all_modes():
    """Teste tous les modes disponibles"""
    print("\n" + "=" * 60)
    print("Test API: Tous les modes")
    print("=" * 60)
    
    modes = ["direct", "fine_tune", "high_precision"]
    results = {}
    
    for mode in modes:
        print(f"\n--- Test du mode '{mode}' ---")
        success = test_change_mode(mode)
        results[mode] = success
        
        if success:
            # Vérifier que le mode a bien été changé
            state = test_manual_state()
            if state and state.get('alignment_mode') == mode:
                print(f"✅ Mode '{mode}' correctement appliqué")
            else:
                print(f"⚠️  Mode '{mode}' peut ne pas être appliqué correctement")
        
        time.sleep(0.5)  # Petite pause entre les tests
    
    return results


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("TESTS DE L'API - MODE DIRECT")
    print("=" * 60)
    print("\n⚠️  Assurez-vous que le serveur backend est démarré (python main.py)")
    print("   URL: http://localhost:8000")
    print()
    
    # Test de connexion au serveur
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Serveur backend accessible")
        else:
            print(f"⚠️  Serveur répond avec le code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de se connecter au serveur: {e}")
        print("   Démarrez le serveur avec: cd AlignTester/src/backend && python main.py")
        return 1
    
    # Tests
    all_passed = True
    
    # Test 1: Info
    align_available = test_api_info()
    if not align_available:
        print("\n⚠️  La commande 'align' n'est pas disponible")
        print("   Les tests suivants peuvent échouer")
    
    # Test 2: État initial
    initial_state = test_manual_state()
    
    # Test 3: Mode invalide
    if not test_invalid_mode():
        all_passed = False
    
    # Test 4: Tous les modes
    mode_results = test_all_modes()
    if not all(mode_results.values()):
        all_passed = False
    
    # Test 5: Retour au mode Direct
    print("\n" + "=" * 60)
    print("Test API: Retour au mode Direct")
    print("=" * 60)
    if not test_change_mode("direct"):
        all_passed = False
    
    # Résumé
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TOUS LES TESTS API SONT PASSÉS")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

