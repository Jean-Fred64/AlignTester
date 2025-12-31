#!/usr/bin/env python3
"""
Script de test en direct du Mode Direct
Teste le Mode Direct avec une vraie disquette
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from api.manual_alignment import ManualAlignmentMode, AlignmentMode
from api.greaseweazle import GreaseweazleExecutor


class LiveTestCallback:
    """Callback pour afficher les résultats en temps réel"""
    
    def __init__(self):
        self.reading_count = 0
        self.start_time = None
        self.last_reading_time = None
        self.readings = []
    
    def __call__(self, data: dict):
        """Callback appelé pour chaque mise à jour"""
        update_type = data.get("type")
        
        if update_type == "started":
            self.start_time = time.time()
            print(f"\n✅ Mode Direct démarré sur T{data.get('track', 0)}.{data.get('head', 0)}")
            print("   Lecture en continu...\n")
        
        elif update_type == "direct_reading":
            # Lecture en cours (notification immédiate)
            track = data.get("track", 0)
            head = data.get("head", 0)
            sectors_detected = data.get("sectors_detected", 0)
            sectors_expected = data.get("sectors_expected", 18)
            percentage = data.get("percentage", 0.0)
            
            current_time = time.time()
            if self.last_reading_time:
                latency = (current_time - self.last_reading_time) * 1000  # en ms
            else:
                latency = 0
            
            self.last_reading_time = current_time
            self.reading_count += 1
            
            # Afficher de manière compacte
            print(f"\r[{self.reading_count:3d}] T{track}.{head} | "
                  f"{sectors_detected}/{sectors_expected} secteurs | "
                  f"{percentage:5.1f}% | "
                  f"Latence: {latency:5.1f}ms", end="", flush=True)
        
        elif update_type == "direct_reading_complete":
            # Lecture terminée (résultat final)
            reading = data.get("reading", {})
            indicator = data.get("indicator", {})
            
            track = reading.get("track", 0)
            head = reading.get("head", 0)
            percentage = reading.get("percentage", 0.0)
            sectors_ratio = indicator.get("sectors_ratio", "0/0")
            bars = indicator.get("bars", "")
            symbol = indicator.get("symbol", "")
            status = indicator.get("status", "")
            
            current_time = time.time()
            if self.last_reading_time:
                latency = (current_time - self.last_reading_time) * 1000
            else:
                latency = 0
            
            # Afficher le résultat complet
            print(f"\r[{self.reading_count:3d}] T{track}.{head} | "
                  f"{sectors_ratio} secteurs | "
                  f"{percentage:5.1f}% | "
                  f"{symbol} {status:10s} | "
                  f"{bars} | "
                  f"Latence: {latency:5.1f}ms")
            
            # Stocker pour statistiques
            self.readings.append({
                "time": current_time,
                "percentage": percentage,
                "latency": latency
            })
        
        elif update_type == "reading_error":
            error = data.get("error", "Erreur inconnue")
            print(f"\n❌ Erreur: {error}")
        
        elif update_type == "mode_changed":
            new_mode = data.get("new_mode", "unknown")
            config = data.get("mode_config", {})
            latency_est = config.get("estimated_latency_ms", 0)
            print(f"\n🔄 Mode changé vers: {new_mode} (latence estimée: {latency_est}ms)")


async def test_mode_direct_live(track: int = 40, head: int = 0, format_type: str = "ibm.1440"):
    """
    Teste le Mode Direct en temps réel avec une vraie disquette
    
    Args:
        track: Numéro de piste à tester (défaut: 40, piste centrale)
        head: Numéro de tête (0 ou 1, défaut: 0)
        format_type: Format de disquette (défaut: ibm.1440)
    """
    print("=" * 70)
    print("TEST MODE DIRECT - LECTURE EN TEMPS RÉEL")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  - Piste: T{track}.{head}")
    print(f"  - Format: {format_type}")
    print(f"  - Mode: Direct (1 lecture, 50ms délai)")
    print(f"  - Latence estimée: ~150-200ms par lecture")
    
    # Vérifier la connexion Greaseweazle
    print("\n" + "=" * 70)
    print("Vérification de la connexion Greaseweazle...")
    print("=" * 70)
    
    executor = GreaseweazleExecutor()
    connection_status = executor.check_connection()
    
    if not connection_status.get("connected", False):
        print("\n❌ ERREUR: Greaseweazle non connecté")
        print(f"   Erreur: {connection_status.get('error', 'Raison inconnue')}")
        print("\nVérifiez:")
        print("  1. Que Greaseweazle est branché en USB")
        print("  2. Que le port série est accessible")
        print("  3. Exécutez: python3 tests/diagnose_greaseweazle.py")
        return 1
    
    print(f"✅ Greaseweazle connecté")
    print(f"   - Port: {connection_status.get('port', 'N/A')}")
    device_info = connection_status.get('device_info', {})
    if device_info:
        print(f"   - Modèle: {device_info.get('model', 'N/A')}")
        print(f"   - Firmware: {device_info.get('firmware', 'N/A')}")
    
    # Vérifier que la commande align est disponible
    if not executor.check_align_available():
        print("\n❌ ERREUR: La commande 'align' n'est pas disponible")
        print("   Vous devez utiliser une version de Greaseweazle compilée depuis la PR #592")
        return 1
    
    print("✅ Commande 'align' disponible")
    
    # Créer l'instance du mode manuel
    print("\n" + "=" * 70)
    print("Initialisation du Mode Direct...")
    print("=" * 70)
    
    manual_mode = ManualAlignmentMode(executor=executor)
    
    # S'assurer que le mode est Direct
    manual_mode.set_alignment_mode(AlignmentMode.DIRECT)
    
    # Configurer le format
    manual_mode.set_format(format_type)
    
    # Configurer le callback
    callback = LiveTestCallback()
    manual_mode.set_update_callback(callback)
    
    print("✅ Mode Direct initialisé")
    print("\n" + "=" * 70)
    print("DÉMARRAGE DU TEST")
    print("=" * 70)
    print("\n⚠️  Assurez-vous qu'une disquette est insérée dans le lecteur")
    print("   Le test va commencer dans 2 secondes...")
    print("   Appuyez sur Ctrl+C pour arrêter\n")
    
    await asyncio.sleep(2)
    
    try:
        # Démarrer le mode manuel
        result = await manual_mode.start(initial_track=track, initial_head=head)
        
        if "error" in result:
            print(f"\n❌ Erreur lors du démarrage: {result['error']}")
            return 1
        
        # Laisser tourner pendant un certain temps (ou jusqu'à interruption)
        print("\n📊 Lecture en cours... (Appuyez sur Ctrl+C pour arrêter)\n")
        
        try:
            # Lire pendant 30 secondes ou jusqu'à interruption
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            print("\n\n⚠️  Arrêt demandé par l'utilisateur")
        
        # Arrêter le mode
        print("\n" + "=" * 70)
        print("ARRÊT DU MODE DIRECT...")
        print("=" * 70)
        
        await manual_mode.stop()
        
        # Afficher les statistiques
        print("\n" + "=" * 70)
        print("STATISTIQUES")
        print("=" * 70)
        
        if callback.readings:
            percentages = [r["percentage"] for r in callback.readings]
            latencies = [r["latency"] for r in callback.readings if r["latency"] > 0]
            
            print(f"\nNombre de lectures: {len(callback.readings)}")
            
            if percentages:
                avg_percentage = sum(percentages) / len(percentages)
                min_percentage = min(percentages)
                max_percentage = max(percentages)
                print(f"\nPourcentage d'alignement:")
                print(f"  - Moyenne: {avg_percentage:.1f}%")
                print(f"  - Minimum: {min_percentage:.1f}%")
                print(f"  - Maximum: {max_percentage:.1f}%")
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                min_latency = min(latencies)
                max_latency = max(latencies)
                print(f"\nLatence:")
                print(f"  - Moyenne: {avg_latency:.1f}ms")
                print(f"  - Minimum: {min_latency:.1f}ms")
                print(f"  - Maximum: {max_latency:.1f}ms")
                
                # Vérifier si la latence est dans les objectifs
                if avg_latency < 300:
                    print(f"  ✅ Latence excellente (< 300ms)")
                elif avg_latency < 500:
                    print(f"  ✅ Latence bonne (< 500ms)")
                else:
                    print(f"  ⚠️  Latence élevée (> 500ms)")
        
        print("\n✅ Test terminé")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        await manual_mode.stop()
        return 0
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        await manual_mode.stop()
        return 1


async def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test du Mode Direct avec une vraie disquette")
    parser.add_argument("--track", type=int, default=40, help="Numéro de piste (défaut: 40)")
    parser.add_argument("--head", type=int, default=0, choices=[0, 1], help="Numéro de tête (0 ou 1, défaut: 0)")
    parser.add_argument("--format", type=str, default="ibm.1440", help="Format de disquette (défaut: ibm.1440)")
    
    args = parser.parse_args()
    
    exit_code = await test_mode_direct_live(
        track=args.track,
        head=args.head,
        format_type=args.format
    )
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

