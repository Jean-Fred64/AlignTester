#!/usr/bin/env python3
"""
Script de diagnostic pour Greaseweazle
Vérifie la connexion et la disponibilité de Greaseweazle
"""

import sys
import subprocess
import platform
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from api.greaseweazle import GreaseweazleExecutor


def test_gw_path():
    """Teste si gw.exe/gw est trouvé"""
    print("=" * 60)
    print("Test 1: Détection du chemin gw")
    print("=" * 60)
    
    executor = GreaseweazleExecutor()
    gw_path = executor.gw_path
    
    print(f"Chemin détecté: {gw_path}")
    
    # Vérifier si le fichier existe
    if Path(gw_path).exists():
        print(f"✅ Fichier trouvé: {Path(gw_path).absolute()}")
    else:
        print(f"⚠️  Fichier non trouvé (peut être dans PATH)")
    
    return executor


def test_gw_version(executor):
    """Teste la version de Greaseweazle"""
    print("\n" + "=" * 60)
    print("Test 2: Version de Greaseweazle")
    print("=" * 60)
    
    try:
        version = executor.check_version()
        if version:
            print(f"✅ Version: {version}")
            return True
        else:
            print("❌ Impossible de récupérer la version")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_gw_align_available(executor):
    """Teste si la commande align est disponible"""
    print("\n" + "=" * 60)
    print("Test 3: Disponibilité de la commande 'align'")
    print("=" * 60)
    
    try:
        available = executor.check_align_available()
        if available:
            print("✅ Commande 'align' disponible")
        else:
            print("❌ Commande 'align' non disponible")
            print("   Vous devez utiliser une version de Greaseweazle compilée depuis la PR #592")
        return available
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_gw_info_direct(executor):
    """Teste directement la commande gw info"""
    print("\n" + "=" * 60)
    print("Test 4: Commande 'gw info' (directe)")
    print("=" * 60)
    
    try:
        print(f"Exécution: {executor.gw_path} info")
        print("(Cela peut prendre quelques secondes...)")
        
        result = subprocess.run(
            [executor.gw_path, "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"\nCode de retour: {result.returncode}")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        if result.returncode == 0:
            print("\n✅ Commande 'gw info' réussie")
            return True
        else:
            print(f"\n⚠️  Commande 'gw info' retourne le code {result.returncode}")
            print("   (Cela peut être normal si Greaseweazle n'est pas connecté)")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n❌ Timeout: La commande 'gw info' prend trop de temps")
        print("   Possible causes:")
        print("   - Greaseweazle non connecté")
        print("   - Port série non accessible")
        print("   - Problème de communication USB")
        return False
    except FileNotFoundError:
        print(f"\n❌ Fichier non trouvé: {executor.gw_path}")
        print("   Vérifiez que Greaseweazle est installé et dans le PATH")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_connection(executor):
    """Teste la connexion via l'API"""
    print("\n" + "=" * 60)
    print("Test 5: Connexion via l'API")
    print("=" * 60)
    
    try:
        connection_status = executor.check_connection()
        
        print(f"Connecté: {connection_status.get('connected', False)}")
        print(f"Port: {connection_status.get('port', 'N/A')}")
        print(f"Dernier port utilisé: {connection_status.get('last_port', 'N/A')}")
        
        if connection_status.get('error'):
            print(f"Erreur: {connection_status.get('error')}")
        
        if connection_status.get('device_info'):
            device = connection_status['device_info']
            print(f"\nInformations du device:")
            print(f"  - Modèle: {device.get('model', 'N/A')}")
            print(f"  - MCU: {device.get('mcu', 'N/A')}")
            print(f"  - Firmware: {device.get('firmware', 'N/A')}")
            print(f"  - Série: {device.get('serial', 'N/A')}")
        
        if connection_status.get('connected'):
            print("\n✅ Greaseweazle connecté et accessible")
            return True
        else:
            print("\n⚠️  Greaseweazle non connecté ou non accessible")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la vérification de connexion: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_device_info(executor):
    """Teste get_device_info()"""
    print("\n" + "=" * 60)
    print("Test 6: get_device_info()")
    print("=" * 60)
    
    try:
        device_info = executor.get_device_info()
        
        if device_info:
            print(f"Connecté: {device_info.get('connected', False)}")
            print(f"Port: {device_info.get('port', 'N/A')}")
            
            if device_info.get('error'):
                print(f"Erreur: {device_info.get('error')}")
            
            if device_info.get('connected'):
                print("\n✅ Device info récupéré avec succès")
                return True
            else:
                print("\n⚠️  Device non connecté")
                return False
        else:
            print("\n❌ get_device_info() retourne None")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("DIAGNOSTIC GREASEWEAZLE")
    print("=" * 60)
    print(f"\nPlateforme: {platform.system()}")
    print(f"Architecture: {platform.machine()}")
    
    results = {}
    
    # Test 1: Chemin gw
    executor = test_gw_path()
    results['gw_path'] = True
    
    # Test 2: Version (non bloquant)
    try:
        results['version'] = test_gw_version(executor)
    except Exception:
        results['version'] = False
        print("⚠️  Test de version échoué (non bloquant)")
    
    # Test 3: Commande align
    results['align_available'] = test_gw_align_available(executor)
    
    # Test 4: gw info direct
    results['gw_info'] = test_gw_info_direct(executor)
    
    # Test 5: Connexion API
    results['connection'] = test_connection(executor)
    
    # Test 6: Device info
    results['device_info'] = test_device_info(executor)
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {'OK' if result else 'ÉCHEC'}")
    
    all_passed = all(results.values())
    
    # Les tests critiques sont: gw_path, align_available, gw_info, connection, device_info
    critical_tests = ['gw_path', 'align_available', 'gw_info', 'connection', 'device_info']
    critical_passed = all(results.get(test, False) for test in critical_tests)
    
    if critical_passed:
        print("\n✅ TOUS LES TESTS CRITIQUES SONT PASSÉS")
        if not results.get('version', True):
            print("⚠️  Le test de version a échoué (non bloquant)")
        return 0
    else:
        print("\n❌ CERTAINS TESTS CRITIQUES ONT ÉCHOUÉ")
        print("\nConseils de dépannage:")
        print("1. Vérifiez que Greaseweazle est branché en USB")
        print("2. Vérifiez que le port série est accessible")
        print("3. Testez manuellement: gw info")
        print("4. Si vous êtes dans WSL, vérifiez que le device est attaché:")
        print("   - Windows: usbipd attach --wsl --busid <BUSID>")
        print("   - WSL: ls -la /dev/ttyACM*")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

