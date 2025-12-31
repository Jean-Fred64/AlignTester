"""
Module pour le mode d'alignement manuel interactif
Inspiré d'ImageDisk et AmigaTestKit
"""

import asyncio
import subprocess
import time
from typing import Optional, Dict, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
from .greaseweazle import GreaseweazleExecutor
from .alignment_parser import AlignmentParser, AlignmentValue


class AlignmentQuality(Enum):
    """Qualité d'alignement basée sur les pourcentages"""
    PERFECT = "Perfect"  # 99.0% - 100%
    GOOD = "Good"       # 97.0% - 98.9%
    AVERAGE = "Average"  # 96.0% - 96.9%
    POOR = "Poor"        # < 96.0%


class AlignmentMode(Enum):
    """Mode d'alignement avec différents compromis latence/précision"""
    DIRECT = "direct"  # Faible latence (~150-200ms), précision basique
    FINE_TUNE = "fine_tune"  # Latence modérée (~500-700ms), précision modérée
    HIGH_PRECISION = "high_precision"  # Latence élevée (~2-3s), précision maximale


# Configuration pour chaque mode
MODE_CONFIG = {
    AlignmentMode.DIRECT: {
        "reads": 1,
        "delay_ms": 50,  # Attente réduite pour latence minimale
        "timeout": 3,  # Timeout optimisé (3s au lieu de 5s) - une lecture rapide devrait être < 300ms
        "calculate_consistency": False,
        "calculate_stability": False,
        "decimal_places": 1,  # 1 décimale suffit
        "max_readings_history": 20,  # Garder seulement 20 dernières lectures
    },
    AlignmentMode.FINE_TUNE: {
        "reads": 3,
        "delay_ms": 100,
        "timeout": 10,
        "calculate_consistency": True,
        "calculate_stability": False,
        "decimal_places": 2,
        "max_readings_history": 50,
    },
    AlignmentMode.HIGH_PRECISION: {
        "reads": 15,
        "delay_ms": 100,
        "timeout": 30,
        "calculate_consistency": True,
        "calculate_stability": True,
        "decimal_places": 3,
        "max_readings_history": 100,
    }
}


@dataclass
class TrackReading:
    """Résultat d'une lecture de piste"""
    track: int
    head: int
    percentage: float
    sectors_detected: int
    sectors_expected: int
    flux_transitions: Optional[int] = None
    time_per_rev: Optional[float] = None
    consistency: Optional[float] = None
    stability: Optional[float] = None
    quality: AlignmentQuality = AlignmentQuality.POOR
    # Détails du calcul multi-critères (pour affichage détaillé)
    calculation_details: Optional[Dict] = None
    # Détection de formatage
    is_formatted: Optional[bool] = None
    format_confidence: Optional[float] = None
    format_status_message: Optional[str] = None
    is_in_format_range: Optional[bool] = None
    format_warning: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    raw_output: str = ""


@dataclass
class ManualAlignmentState:
    """État du mode d'alignement manuel"""
    is_running: bool = False
    current_track: int = 0
    current_head: int = 0
    readings: List[TrackReading] = field(default_factory=list)
    last_reading: Optional[TrackReading] = None
    auto_analyze: bool = True  # Analyse automatique après chaque déplacement
    num_reads: int = 3  # Nombre de lectures pour l'analyse
    format_type: str = "ibm.1440"  # Format de disquette
    diskdefs_path: Optional[str] = None  # Chemin vers diskdefs.cfg
    alignment_mode: AlignmentMode = AlignmentMode.DIRECT  # Mode d'alignement actif


class ManualAlignmentMode:
    """
    Mode d'alignement manuel interactif
    Permet de naviguer manuellement entre les pistes et d'analyser l'alignement
    """
    
    def __init__(self, executor: Optional[GreaseweazleExecutor] = None):
        self.executor = executor or GreaseweazleExecutor()
        self.state = ManualAlignmentState()
        self._running_task: Optional[asyncio.Task] = None
        self._update_task: Optional[asyncio.Task] = None
        self._on_update: Optional[Callable[[Dict], None]] = None
        self._operation_lock = asyncio.Lock()  # Verrou pour empêcher les opérations concurrentes
        self._reading_paused = False  # Flag pour mettre en pause la boucle de lecture
    
    def set_update_callback(self, callback: Callable[[Dict], None]):
        """Définit un callback pour les mises à jour en temps réel"""
        self._on_update = callback
    
    def _notify_update(self, data: Dict):
        """Notifie les mises à jour via le callback"""
        if self._on_update:
            try:
                self._on_update(data)
            except Exception as e:
                print(f"Erreur dans callback de mise à jour: {e}")
    
    async def start(self, initial_track: int = 0, initial_head: int = 0):
        """Démarre le mode manuel avec flux continu de lectures"""
        if self.state.is_running:
            return {"error": "Le mode manuel est déjà en cours d'exécution"}
        
        self.state.is_running = True
        self.state.current_track = initial_track
        self.state.current_head = initial_head
        self.state.readings = []
        self.state.last_reading = None
        
        # Effectuer un recal initial (seek vers track 0)
        await self.recalibrate()
        
        # Se positionner sur la piste initiale
        await self.seek(initial_track, initial_head, skip_analysis=True)
        
        # Démarrer la boucle continue de lecture
        self._running_task = asyncio.create_task(self._continuous_reading_loop())
        
        self._notify_update({
            "type": "started",
            "track": self.state.current_track,
            "head": self.state.current_head,
            "state": self._get_state_dict()
        })
        
        return {"success": True, "state": self._get_state_dict()}
    
    async def _continuous_reading_loop(self):
        """
        Boucle continue de lecture de la piste actuelle
        Similaire au comportement d'ImageDisk qui lit en continu
        Adaptée selon le mode d'alignement actif
        """
        while self.state.is_running:
            try:
                # Vérifier si la lecture est en pause (pendant un seek/recal)
                if self._reading_paused:
                    # Attente adaptée au mode
                    config = MODE_CONFIG[self.state.alignment_mode]
                    await asyncio.sleep(config["delay_ms"] / 1000.0)
                    continue
                
                # Utiliser le verrou pour éviter les conflits avec seek/recal
                async with self._operation_lock:
                    # Vérifier à nouveau si on est toujours en cours d'exécution
                    if not self.state.is_running:
                        break
                    
                    # Lire la piste selon le mode actif
                    try:
                        if self.state.alignment_mode == AlignmentMode.DIRECT:
                            await self._read_track_direct()
                        else:
                            await self._read_track_once()
                    except Exception as e:
                        # Erreur lors de la lecture - log mais continue la boucle
                        mode_name = self.state.alignment_mode.value
                        print(f"[ManualAlignment] Erreur dans lecture (mode {mode_name}): {e}")
                        # Notifier l'erreur mais continuer
                        self._notify_update({
                            "type": "reading_error",
                            "error": f"Erreur lecture (mode {mode_name}): {str(e)}",
                            "state": self._get_state_dict()
                        })
                
                # Attendre un délai adapté au mode
                config = MODE_CONFIG[self.state.alignment_mode]
                await asyncio.sleep(config["delay_ms"] / 1000.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # En cas d'erreur, notifier et continuer
                self._notify_update({
                    "type": "reading_error",
                    "error": str(e),
                    "state": self._get_state_dict()
                })
                # Attendre un peu plus longtemps en cas d'erreur
                await asyncio.sleep(0.5)
    
    async def _read_track_direct(self):
        """
        Lit la piste en mode Direct (faible latence)
        Inspiré d'ImageDisk : lecture simple, affichage immédiat
        Optimisé pour le réglage en temps réel
        """
        track = self.state.current_track
        head = self.state.current_head
        config = MODE_CONFIG[AlignmentMode.DIRECT]
        
        try:
            # Commande optimisée pour le mode Direct
            tracks_spec = f"c={track}:h={head}"
            args = [
                "align",
                f"--tracks={tracks_spec}",
                f"--reads={config['reads']}",  # 1 lecture
                f"--format={self.state.format_type}"
            ]
            
            # Ajouter --diskdefs si spécifié et accessible
            # Vérifier les permissions avant d'ajouter --diskdefs
            if self.state.diskdefs_path:
                try:
                    from pathlib import Path
                    diskdefs_file = Path(self.state.diskdefs_path)
                    if diskdefs_file.exists() and diskdefs_file.is_file():
                        # Vérifier qu'on peut lire le fichier
                        try:
                            with open(diskdefs_file, 'r') as f:
                                f.read(1)  # Lire un octet pour vérifier les permissions
                            args.append(f"--diskdefs={self.state.diskdefs_path}")
                        except PermissionError:
                            # Permission refusée, ne pas ajouter --diskdefs
                            pass
                        except Exception:
                            pass
                except Exception:
                    pass  # Ignorer les erreurs
            
            readings_data = []
            
            def on_output(line: str):
                """
                Callback pour collecter les lignes (SANS notification)
                ⚠️ IMPORTANT : Ne pas envoyer de notification ici pour éviter la saturation du frontend
                Inspiré d'ImageDisk et Amiga Test Kit : affichage APRÈS la lecture complète
                """
                readings_data.append(line)
                # ❌ NE PAS notifier ici - juste collecter les données
                # Les notifications seront envoyées APRÈS la lecture complète
            
            # Exécution avec timeout réduit
            command_start_time = time.time()
            result = await self.executor.run_command(args, on_output=on_output, timeout=config["timeout"])
            command_duration = (time.time() - command_start_time) * 1000  # en ms
            
            # Vérifier si la commande a échoué à cause de permissions sur diskdefs
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or 'Unknown error'
                raw_error = str(error_msg)
                
                # Si l'erreur est liée à diskdefs (permission refusée), réessayer sans --diskdefs
                if 'Permission denied' in raw_error and 'diskdefs' in raw_error.lower():
                    print(f"[ManualAlignment] Erreur permission diskdefs en mode Direct, réessayer sans --diskdefs")
                    # Réessayer sans --diskdefs (gw peut trouver le fichier automatiquement)
                    args_without_diskdefs = [arg for arg in args if not arg.startswith('--diskdefs')]
                    try:
                        readings_data_retry = []
                        def on_output_retry(line: str):
                            """Callback pour collecter les lignes lors du retry (sans notification)"""
                            readings_data_retry.append(line)
                            # ❌ NE PAS notifier ici non plus
                        
                        result_retry = await self.executor.run_command(args_without_diskdefs, on_output=on_output_retry, timeout=config["timeout"])
                        readings_data = readings_data_retry
                        result = result_retry
                    except Exception as e:
                        print(f"[ManualAlignment] Erreur lors de la retry sans diskdefs: {e}")
            
            # Parser les résultats même si la commande a échoué partiellement
            all_readings = AlignmentParser.parse_output("\n".join(readings_data))
            
            if all_readings:
                last_parsed = all_readings[-1]
                
                # Calcul basique (comme ImageDisk)
                expected_sectors = last_parsed.sectors_expected or 18
                sectors_detected = last_parsed.sectors_detected or 0
                percentage = self._calculate_direct_percentage(sectors_detected, expected_sectors)
                
                # Calculer la latence totale (temps de commande + délai)
                total_latency = command_duration + config["delay_ms"]
                
                # Créer un TrackReading simplifié (pas de calculs complexes)
                reading = TrackReading(
                    track=track,
                    head=head,
                    percentage=percentage,
                    sectors_detected=sectors_detected,
                    sectors_expected=expected_sectors,
                    quality=self._get_quality_from_percentage(percentage),
                    flux_transitions=last_parsed.flux_transitions,
                    time_per_rev=last_parsed.time_per_rev,
                    raw_output="\n".join(readings_data)
                )
                
                # Ajouter à l'historique (garder seulement les N dernières pour le mode Direct)
                self.state.readings.append(reading)
                max_history = config["max_readings_history"]
                if len(self.state.readings) > max_history:
                    self.state.readings = self.state.readings[-max_history:]
                
                self.state.last_reading = reading
                
                # ✅ UN SEUL message WebSocket avec le résultat final (comme ImageDisk et Amiga Test Kit)
                # Cela évite la saturation du frontend (20-40 messages/seconde → 2-3 messages/seconde)
                self._notify_update({
                    "type": "direct_reading_complete",
                    "reading": self._reading_to_dict(reading),
                    "indicator": self._get_direct_indicator(reading),
                    "timing": {
                        "command_duration_ms": round(command_duration, 1),
                        "total_latency_ms": round(total_latency, 1),
                        "delay_ms": config["delay_ms"],
                        "timestamp": datetime.now().isoformat(),
                        "flux_transitions": last_parsed.flux_transitions,
                        "time_per_rev_ms": last_parsed.time_per_rev
                    },
                    "state": self._get_state_dict()
                })
                
        except asyncio.TimeoutError:
            # ✅ Timeout spécifique
            print(f"[ManualAlignment] Timeout en mode Direct sur T{track}.{head}")
            self._notify_update({
                "type": "reading_error",
                "error": "Timeout lors de la lecture",
                "track": track,
                "head": head,
                "state": self._get_state_dict()
            })
            # Ne pas interrompre la boucle - continuer après le délai
        except subprocess.SubprocessError as e:
            # ✅ Erreur de sous-processus
            print(f"[ManualAlignment] Erreur sous-processus en mode Direct: {e}")
            self._notify_update({
                "type": "reading_error",
                "error": f"Erreur sous-processus: {str(e)}",
                "track": track,
                "head": head,
                "state": self._get_state_dict()
            })
        except Exception as e:
            # ✅ Erreur générale avec logging détaillé
            print(f"[ManualAlignment] Erreur mode Direct: {e}")
            import traceback
            traceback.print_exc()  # Log détaillé pour debug
            self._notify_update({
                "type": "reading_error",
                "error": str(e),
                "track": track,
                "head": head,
                "state": self._get_state_dict()
            })
            # ✅ Toujours continuer - ne jamais interrompre la boucle sauf arrêt explicite
    
    async def _read_track_once(self):
        """
        Lit la piste actuelle une seule fois (pour la boucle continue)
        """
        track = self.state.current_track
        head = self.state.current_head
        config = MODE_CONFIG.get(self.state.alignment_mode, MODE_CONFIG[AlignmentMode.FINE_TUNE])
        
        try:
            # Utiliser gw align avec le nombre de lectures selon le mode
            tracks_spec = f"c={track}:h={head}"
            args = [
                "align",
                f"--tracks={tracks_spec}",
                f"--reads={config['reads']}",  # Nombre de lectures selon le mode
                f"--format={self.state.format_type}"
            ]
            print(f"[ManualAlignment] Lecture piste {track}:h={head} avec format {self.state.format_type} (mode: {self.state.alignment_mode.value}, reads: {config['reads']})")
            
            # Ajouter --diskdefs si spécifié et accessible
            # Note: gw align peut aussi trouver diskdefs.cfg automatiquement
            # mais on peut le spécifier explicitement si nécessaire
            # Ne pas ajouter --diskdefs si on a eu des erreurs de permission précédemment
            if self.state.diskdefs_path:
                # Vérifier si le fichier est accessible (éviter les erreurs de permission)
                try:
                    from pathlib import Path
                    diskdefs_file = Path(self.state.diskdefs_path)
                    if diskdefs_file.exists() and diskdefs_file.is_file():
                        args.append(f"--diskdefs={self.state.diskdefs_path}")
                    else:
                        print(f"[ManualAlignment] diskdefs.cfg non accessible: {self.state.diskdefs_path}, gw utilisera le fichier par défaut")
                except Exception as e:
                    print(f"[ManualAlignment] Erreur vérification diskdefs: {e}, gw utilisera le fichier par défaut")
            
            readings_data = []
            reading_start_time = time.time()  # Temps de début de la lecture
            
            def on_output(line: str):
                """Callback pour traiter la sortie en temps réel"""
                readings_data.append(line)
                # Parser la ligne pour extraire les informations
                parsed = AlignmentParser.parse_line(line)
                if parsed:
                    # Forcer le format_type à celui spécifié dans la commande
                    # (le parser peut détecter un format différent dans la sortie)
                    parsed.format_type = self.state.format_type
                    
                    # Calculer le temps écoulé depuis le début de la lecture
                    elapsed_time = (time.time() - reading_start_time) * 1000  # en ms
                    
                    self._notify_update({
                        "type": "reading",
                        "line": line,
                        "parsed": {
                            "track": parsed.track,
                            "percentage": parsed.percentage,
                            "sectors_detected": parsed.sectors_detected,
                            "sectors_expected": parsed.sectors_expected,
                            "flux_transitions": parsed.flux_transitions,
                            "time_per_rev": parsed.time_per_rev
                        },
                        "timing": {
                            "elapsed_ms": round(elapsed_time, 1),
                            "timestamp": datetime.now().isoformat(),
                            "flux_transitions": parsed.flux_transitions,
                            "time_per_rev_ms": parsed.time_per_rev
                        }
                    })
            
            command_start_time = time.time()
            result = await self.executor.run_command(args, on_output=on_output, timeout=config.get("timeout", 10))
            command_duration = (time.time() - command_start_time) * 1000  # en ms
            
            # Parser toutes les lectures même si la commande a échoué
            # (parfois gw retourne un code d'erreur mais produit quand même des données)
            all_readings = AlignmentParser.parse_output("\n".join(readings_data))
            
            # Vérifier si la commande a échoué ET qu'on n'a pas de lectures valides
            if result.returncode != 0 and not all_readings:
                error_msg = result.stderr or result.stdout or 'Unknown error'
                # Filtrer les erreurs non critiques (permissions, warnings)
                if 'Permission denied' in error_msg or 'Permission denied' in str(result.stdout):
                    # Erreur de permission sur diskdefs - essayer sans --diskdefs
                    print(f"[ManualAlignment] Erreur permission diskdefs, réessayer sans --diskdefs")
                    # Réessayer sans --diskdefs (gw peut trouver le fichier automatiquement)
                    args_without_diskdefs = [arg for arg in args if not arg.startswith('--diskdefs')]
                    try:
                        readings_data_retry = []
                        def on_output_retry(line: str):
                            readings_data_retry.append(line)
                            parsed = AlignmentParser.parse_line(line)
                            if parsed:
                                parsed.format_type = self.state.format_type
                                self._notify_update({
                                    "type": "reading",
                                    "line": line,
                                    "parsed": {
                                        "track": parsed.track,
                                        "percentage": parsed.percentage,
                                        "sectors_detected": parsed.sectors_detected,
                                        "sectors_expected": parsed.sectors_expected,
                                        "flux_transitions": parsed.flux_transitions,
                                        "time_per_rev": parsed.time_per_rev
                                    }
                                })
                        result_retry = await self.executor.run_command(args_without_diskdefs, on_output=on_output_retry, timeout=10)
                        all_readings = AlignmentParser.parse_output("\n".join(readings_data_retry))
                        if result_retry.returncode == 0 or all_readings:
                            # Succès avec la retry, continuer normalement
                            pass
                        else:
                            # Toujours en erreur
                            print(f"[ManualAlignment] Erreur lors de la lecture (format: {self.state.format_type}, returncode: {result_retry.returncode})")
                            self._notify_update({
                                "type": "reading_error",
                                "error": f"Erreur lecture (format: {self.state.format_type}): {error_msg[:100]}",
                                "state": self._get_state_dict()
                            })
                            return
                    except Exception as e:
                        print(f"[ManualAlignment] Erreur lors de la retry: {e}")
                        self._notify_update({
                            "type": "reading_error",
                            "error": f"Erreur lecture (format: {self.state.format_type}): {error_msg[:100]}",
                            "state": self._get_state_dict()
                        })
                        return
                else:
                    # Autre erreur
                    print(f"[ManualAlignment] Erreur lors de la lecture (format: {self.state.format_type}, returncode: {result.returncode}): {error_msg}")
                    self._notify_update({
                        "type": "reading_error",
                        "error": f"Erreur lecture (format: {self.state.format_type}): {error_msg[:100]}",
                        "state": self._get_state_dict()
                    })
                    return
            
            # Si on a des lectures même avec un returncode != 0, continuer
            if not all_readings:
                # Pas de lectures valides, sortir
                return
            
            # Forcer le format_type pour toutes les lectures parsées
            # (le parser peut détecter un format différent dans la sortie)
            for reading in all_readings:
                reading.format_type = self.state.format_type
            
            if all_readings:
                # Prendre la dernière lecture
                last_parsed = all_readings[-1]
                
                # Déterminer le nombre de secteurs attendus selon le format
                # ibm.720 = 9 secteurs, ibm.1440 = 18 secteurs, etc.
                expected_sectors = last_parsed.sectors_expected
                if not expected_sectors or expected_sectors == 0:
                    # Essayer de déterminer depuis le format
                    if '720' in self.state.format_type:
                        expected_sectors = 9
                    elif '360' in self.state.format_type:
                        expected_sectors = 9
                    elif '1440' in self.state.format_type or '1200' in self.state.format_type:
                        expected_sectors = 15
                    else:
                        expected_sectors = 18  # Par défaut
                elif expected_sectors == 0 and last_parsed.sectors_detected == 0:
                    # Si on a 0 secteurs détectés et attendus, utiliser le format pour déterminer
                    if '720' in self.state.format_type:
                        expected_sectors = 9
                    elif '360' in self.state.format_type:
                        expected_sectors = 9
                    elif '1440' in self.state.format_type or '1200' in self.state.format_type:
                        expected_sectors = 15
                    else:
                        expected_sectors = 18  # Par défaut
                
                # Calculer les statistiques pour obtenir les métriques avancées (cohérence, stabilité, etc.)
                # et les détails du calcul multi-critères
                stats = AlignmentParser.calculate_statistics(all_readings, limit=1)
                calculation_details = None
                consistency = None
                stability = None
                if stats.get("values") and len(stats["values"]) > 0:
                    value = stats["values"][0]
                    calculation_details = value.get("calculation_details")
                    consistency = value.get("consistency")
                    stability = value.get("stability")
                    # Utiliser le pourcentage ajusté du calcul multi-critères si disponible
                    adjusted_percentage = value.get("percentage", last_parsed.percentage)
                else:
                    adjusted_percentage = last_parsed.percentage
                
                # Créer un TrackReading avec les informations de formatage
                reading = TrackReading(
                    track=track,
                    head=head,
                    percentage=adjusted_percentage,
                    sectors_detected=last_parsed.sectors_detected or 0,
                    sectors_expected=expected_sectors,
                    flux_transitions=last_parsed.flux_transitions,
                    time_per_rev=last_parsed.time_per_rev,
                    consistency=consistency,
                    stability=stability,
                    quality=self._get_quality_from_percentage(adjusted_percentage),
                    calculation_details=calculation_details,
                    is_formatted=last_parsed.is_formatted,
                    format_confidence=last_parsed.format_confidence,
                    format_status_message=last_parsed.format_status_message,
                    is_in_format_range=last_parsed.is_in_format_range,
                    format_warning=last_parsed.format_warning,
                    raw_output="\n".join(readings_data)
                )
                
                # Ajouter à l'historique
                self.state.readings.append(reading)
                self.state.last_reading = reading
                
                # Garder seulement les 100 dernières lectures
                if len(self.state.readings) > 100:
                    self.state.readings = self.state.readings[-100:]
                
                # Calculer la latence totale (temps de commande + délai)
                total_latency = command_duration + config.get("delay_ms", 100)
                
                # Notifier la mise à jour avec timings
                self._notify_update({
                    "type": "reading_complete",
                    "reading": self._reading_to_dict(reading),
                    "timing": {
                        "command_duration_ms": round(command_duration, 1),
                        "total_latency_ms": round(total_latency, 1),
                        "delay_ms": config.get("delay_ms", 100),
                        "timestamp": datetime.now().isoformat(),
                        "flux_transitions": last_parsed.flux_transitions,
                        "time_per_rev_ms": last_parsed.time_per_rev
                    },
                    "state": self._get_state_dict()
                })
        except Exception as e:
            # Erreur silencieuse pour ne pas interrompre la boucle
            # Log l'erreur pour debug mais continue la boucle
            print(f"[ManualAlignment] Erreur lors de la lecture (format: {self.state.format_type}): {e}")
            self._notify_update({
                "type": "reading_error",
                "error": str(e),
                "state": self._get_state_dict()
            })
            # Ne pas lever l'exception pour que la boucle continue
    
    async def stop(self):
        """Arrête le mode manuel"""
        if not self.state.is_running:
            return {"error": "Le mode manuel n'est pas en cours d'exécution"}
        
        self.state.is_running = False
        
        if self._running_task:
            self._running_task.cancel()
            try:
                await self._running_task
            except asyncio.CancelledError:
                pass
            self._running_task = None
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None
        
        self._notify_update({
            "type": "stopped",
            "state": self._get_state_dict()
        })
        
        return {"success": True}
    
    async def seek(self, track: int, head: Optional[int] = None, skip_analysis: bool = False):
        """
        Déplace la tête vers une piste spécifique
        Utilise la commande gw seek
        La boucle continue de lecture reprendra automatiquement sur la nouvelle piste
        Peut être utilisé même si le mode n'est pas démarré (pour l'analyse)
        """
        # Permettre le seek même si le mode n'est pas démarré (pour l'analyse)
        
        # Valider les limites
        if track < 0:
            track = 0
        if track > 83:
            track = 83
        
        # Utiliser la tête actuelle si non spécifiée
        if head is None:
            head = self.state.current_head if self.state.is_running else 0
        
        # Valider la tête
        if head < 0:
            head = 0
        if head > 1:
            head = 1
        
        # Mettre en pause la boucle de lecture pendant le seek (si elle tourne)
        if self.state.is_running:
            self._reading_paused = True
        
        try:
            # Utiliser le verrou pour empêcher les opérations concurrentes (si mode démarré)
            lock = self._operation_lock if self.state.is_running else asyncio.Lock()
            async with lock:
                # Utiliser gw seek pour déplacer la tête
                args = ["seek", str(track)]
                result = await self.executor.run_command(args, timeout=15)
                
                if result.returncode == 0:
                    self.state.current_track = track
                    self.state.current_head = head
                    
                    # La boucle continue de lecture reprendra automatiquement
                    # Pas besoin d'analyser manuellement, le flux continu le fera
                    
                    self._notify_update({
                        "type": "seek",
                        "track": track,
                        "head": head,
                        "state": self._get_state_dict()
                    })
                    
                    return {
                        "success": True,
                        "track": track,
                        "head": head,
                        "state": self._get_state_dict()
                    }
                else:
                    error_msg = result.stderr or result.stdout or 'Unknown error'
                    return {
                        "error": f"Erreur lors du seek: {error_msg}",
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
        except asyncio.TimeoutError:
            return {"error": "Timeout lors du seek - le lecteur ne répond pas"}
        except Exception as e:
            return {"error": f"Exception lors du seek: {str(e)}", "exception_type": type(e).__name__}
        finally:
            # Reprendre la boucle de lecture après le seek (si elle tournait)
            if self.state.is_running:
                self._reading_paused = False
            # Attendre un peu pour laisser le lecteur se stabiliser
            await asyncio.sleep(0.2)
    
    async def move_track(self, delta: int):
        """
        Déplace la tête de delta pistes
        +1 pour avancer, -1 pour reculer
        """
        new_track = self.state.current_track + delta
        return await self.seek(new_track)
    
    async def jump_track(self, track_number: int):
        """
        Saute vers une piste spécifique (10, 20, 30, etc.)
        Utilisé avec les touches 1-8
        """
        target_track = track_number * 10
        return await self.seek(target_track)
    
    async def set_head(self, head: int):
        """
        Change la tête active (0 ou 1)
        Utilise la commande gw seek avec la tête spécifiée
        """
        if not self.state.is_running:
            return {"error": "Le mode manuel n'est pas démarré"}
        
        if head < 0 or head > 1:
            return {"error": "La tête doit être 0 ou 1"}
        
        # Seek vers la piste actuelle avec la nouvelle tête
        return await self.seek(self.state.current_track, head)
    
    async def recalibrate(self):
        """
        Recalibre la tête (seek vers track 0)
        Similaire à la fonction Recal d'ImageDisk
        """
        if not self.state.is_running:
            return {"error": "Le mode manuel n'est pas démarré"}
        
        # Mettre en pause la boucle de lecture pendant le recal
        self._reading_paused = True
        
        try:
            # Utiliser le verrou pour empêcher les opérations concurrentes
            async with self._operation_lock:
                # Seek vers track 0, head 0
                args = ["seek", "0"]
                result = await self.executor.run_command(args, timeout=15)
                
                if result.returncode == 0:
                    self.state.current_track = 0
                    self.state.current_head = 0
                    
                    self._notify_update({
                        "type": "recalibrated",
                        "state": self._get_state_dict()
                    })
                    
                    return {"success": True, "state": self._get_state_dict()}
                else:
                    error_msg = result.stderr or result.stdout or 'Unknown error'
                    return {
                        "error": f"Erreur lors du recal: {error_msg}",
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
        except asyncio.TimeoutError:
            return {"error": "Timeout lors du recal - le lecteur ne répond pas"}
        except Exception as e:
            return {"error": f"Exception lors du recal: {str(e)}", "exception_type": type(e).__name__}
        finally:
            # Reprendre la boucle de lecture après le recal
            self._reading_paused = False
            # Attendre un peu pour laisser le lecteur se stabiliser
            await asyncio.sleep(0.2)
    
    async def analyze_current_track(self, track: Optional[int] = None, head: Optional[int] = None) -> Dict:
        """
        Analyse la piste actuelle (ou spécifiée) avec le format sélectionné
        Permet de tester si le format choisi correspond à la disquette
        
        Logique de sélection de la piste (par ordre de priorité) :
        1. Paramètres track/head fournis explicitement
        2. Si le mode est démarré : current_track/current_head
        3. Si une analyse précédente existe : last_reading.track/head
        4. Sinon : piste 0.0 par défaut
        
        Args:
            track: Numéro de piste (optionnel)
            head: Numéro de tête (optionnel)
        """
        # Utiliser les paramètres fournis ou déterminer la piste à analyser
        if track is None:
            if self.state.is_running:
                # Mode démarré : utiliser la piste actuelle
                track = self.state.current_track
            elif self.state.last_reading:
                # Pas de mode démarré mais analyse précédente : utiliser la dernière piste analysée
                track = self.state.last_reading.track
            else:
                # Aucune analyse précédente : démarrer à la piste 0
                track = 0
        
        if head is None:
            if self.state.is_running:
                # Mode démarré : utiliser la tête actuelle
                head = self.state.current_head
            elif self.state.last_reading:
                # Pas de mode démarré mais analyse précédente : utiliser la dernière tête analysée
                head = self.state.last_reading.head
            else:
                # Aucune analyse précédente : démarrer à la tête 0
                head = 0
        
        # Si le mode n'est pas démarré, on peut quand même analyser
        # mais il faut se positionner sur la piste d'abord
        was_running = self.state.is_running
        needs_seek = not was_running
        
        if needs_seek:
            # Se positionner sur la piste avant d'analyser
            try:
                seek_result = await self.seek(track, head, skip_analysis=True)
                if "error" in seek_result:
                    return {"error": f"Impossible de se positionner sur la piste {track}.{head}: {seek_result['error']}"}
            except Exception as e:
                return {"error": f"Erreur lors du positionnement: {str(e)}"}
        
        # Mettre en pause la boucle de lecture pendant l'analyse (si elle tourne)
        if was_running:
            self._reading_paused = True
        
        try:
            # Utiliser le verrou pour empêcher les opérations concurrentes (si mode démarré)
            lock = self._operation_lock if was_running else asyncio.Lock()
            async with lock:
                # Utiliser gw align pour analyser la piste avec plusieurs lectures
                tracks_spec = f"c={track}:h={head}"
                args = [
                    "align",
                    f"--tracks={tracks_spec}",
                    f"--reads={self.state.num_reads}",
                    f"--format={self.state.format_type}"
                ]
                
                # Ajouter --diskdefs si spécifié et accessible
                # Note: gw align peut aussi trouver diskdefs.cfg automatiquement
                # Vérifier les permissions avant d'ajouter --diskdefs
                if self.state.diskdefs_path:
                    try:
                        diskdefs_file = Path(self.state.diskdefs_path)
                        if diskdefs_file.exists() and diskdefs_file.is_file():
                            # Vérifier qu'on peut lire le fichier
                            try:
                                with open(diskdefs_file, 'r') as f:
                                    f.read(1)  # Lire un octet pour vérifier les permissions
                                args.append(f"--diskdefs={self.state.diskdefs_path}")
                            except PermissionError:
                                print(f"[ManualAlignment] Permission refusée pour diskdefs.cfg: {self.state.diskdefs_path}, gw utilisera le fichier par défaut")
                            except Exception as e:
                                print(f"[ManualAlignment] Erreur vérification diskdefs: {e}, gw utilisera le fichier par défaut")
                        else:
                            print(f"[ManualAlignment] diskdefs.cfg non trouvé: {self.state.diskdefs_path}, gw utilisera le fichier par défaut")
                    except Exception as e:
                        print(f"[ManualAlignment] Erreur vérification diskdefs: {e}, gw utilisera le fichier par défaut")
                
                readings_data = []
                
                def on_output(line: str):
                    """Callback pour traiter la sortie en temps réel"""
                    readings_data.append(line)
                    parsed = AlignmentParser.parse_line(line)
                    if parsed:
                        self._notify_update({
                            "type": "analysis_reading",
                            "line": line,
                            "parsed": {
                                "track": parsed.track,
                                "percentage": parsed.percentage,
                                "sectors_detected": parsed.sectors_detected,
                                "sectors_expected": parsed.sectors_expected
                            }
                        })
                
                result = await self.executor.run_command(args, on_output=on_output, timeout=30)
                
                # Log pour déboguer
                raw_output = "\n".join(readings_data)
                print(f"[DEBUG] Commande exécutée: {' '.join(args)}")
                print(f"[DEBUG] Code de retour: {result.returncode}")
                print(f"[DEBUG] Sortie brute ({len(readings_data)} lignes):")
                for i, line in enumerate(readings_data):
                    print(f"  [{i}] {repr(line)}")
                
                # Vérifier si la commande a échoué
                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout or "Erreur inconnue"
                    raw_error = str(error_msg)
                    
                    # Si l'erreur est liée à diskdefs (permission refusée), réessayer sans --diskdefs
                    if 'Permission denied' in raw_error and 'diskdefs' in raw_error.lower():
                        print(f"[ManualAlignment] Erreur permission diskdefs, réessayer sans --diskdefs")
                        # Réessayer sans --diskdefs (gw peut trouver le fichier automatiquement)
                        args_without_diskdefs = [arg for arg in args if not arg.startswith('--diskdefs')]
                        try:
                            readings_data_retry = []
                            def on_output_retry(line: str):
                                readings_data_retry.append(line)
                                parsed = AlignmentParser.parse_line(line)
                                if parsed:
                                    self._notify_update({
                                        "type": "analysis_reading",
                                        "line": line,
                                        "parsed": {
                                            "track": parsed.track,
                                            "percentage": parsed.percentage,
                                            "sectors_detected": parsed.sectors_detected,
                                            "sectors_expected": parsed.sectors_expected
                                        }
                                    })
                            
                            print(f"[DEBUG] Réessai sans --diskdefs: {' '.join(args_without_diskdefs)}")
                            result_retry = await self.executor.run_command(args_without_diskdefs, on_output=on_output_retry, timeout=30)
                            raw_output_retry = "\n".join(readings_data_retry)
                            
                            if result_retry.returncode == 0:
                                # Succès, parser les résultats
                                all_readings = AlignmentParser.parse_output(raw_output_retry)
                                if all_readings:
                                    readings_data = readings_data_retry
                                    raw_output = raw_output_retry
                                    result = result_retry
                                    print(f"[DEBUG] Réessai réussi, {len(all_readings)} lectures parsées")
                                else:
                                    return {
                                        "error": "Aucune donnée d'alignement trouvée après réessai. Vérifiez le format sélectionné.",
                                        "raw_output": raw_output_retry,
                                        "command": " ".join(args_without_diskdefs),
                                        "hint": "La sortie de gw align n'a pas pu être parsée. Vérifiez que le format est correct et que la disquette est insérée."
                                    }
                            else:
                                # Le réessai a aussi échoué
                                return {
                                    "error": f"La commande gw align a échoué même sans --diskdefs (code {result_retry.returncode}): {result_retry.stderr or result_retry.stdout or 'Erreur inconnue'}",
                                    "raw_output": raw_output_retry,
                                    "command": " ".join(args_without_diskdefs)
                                }
                        except Exception as retry_err:
                            return {
                                "error": f"Erreur lors du réessai sans --diskdefs: {str(retry_err)}",
                                "raw_output": raw_output,
                                "command": " ".join(args)
                            }
                    else:
                        # Autre erreur, retourner l'erreur originale
                        return {
                            "error": f"La commande gw align a échoué (code {result.returncode}): {error_msg}",
                            "raw_output": raw_output,
                            "command": " ".join(args)
                        }
                
                # Parser toutes les lectures
                all_readings = AlignmentParser.parse_output(raw_output)
                
                print(f"[DEBUG] Lectures parsées: {len(all_readings)}")
                for i, reading in enumerate(all_readings):
                    print(f"  Lecture {i}: track={reading.track}, percentage={reading.percentage}, sectors={reading.sectors_detected}/{reading.sectors_expected}")
                
                if not all_readings:
                    return {
                        "error": "Aucune donnée d'alignement trouvée. Vérifiez le format sélectionné.",
                        "raw_output": raw_output,
                        "command": " ".join(args),
                        "hint": "La sortie de gw align n'a pas pu être parsée. Vérifiez que le format est correct et que la disquette est insérée."
                    }
                
                # Calculer les statistiques
                stats = AlignmentParser.calculate_statistics(all_readings, limit=1)
                
                # Créer un TrackReading
                if stats.get("values") and len(stats["values"]) > 0:
                    value = stats["values"][0]
                    reading = TrackReading(
                        track=track,
                        head=head,
                        percentage=value.get("percentage", 0.0),
                        sectors_detected=value.get("sectors_detected", 0),
                        sectors_expected=value.get("sectors_expected", 18),
                        flux_transitions=value.get("flux_transitions"),
                        time_per_rev=value.get("time_per_rev"),
                        consistency=value.get("consistency"),
                        stability=value.get("stability"),
                        quality=self._get_quality_from_percentage(value.get("percentage", 0.0)),
                        calculation_details=value.get("calculation_details"),
                        is_formatted=value.get("is_formatted"),
                        format_confidence=value.get("format_confidence"),
                        format_status_message=value.get("format_status_message"),
                        is_in_format_range=value.get("is_in_format_range"),
                        format_warning=value.get("format_warning"),
                        raw_output="\n".join(readings_data)
                    )
                else:
                    first_reading = all_readings[0]
                    reading = TrackReading(
                        track=track,
                        head=head,
                        percentage=first_reading.percentage,
                        sectors_detected=first_reading.sectors_detected or 0,
                        sectors_expected=first_reading.sectors_expected or 18,
                        flux_transitions=first_reading.flux_transitions,
                        time_per_rev=first_reading.time_per_rev,
                        consistency=first_reading.consistency,
                        stability=first_reading.stability,
                        quality=self._get_quality_from_percentage(first_reading.percentage),
                        is_formatted=first_reading.is_formatted,
                        format_confidence=first_reading.format_confidence,
                        format_status_message=first_reading.format_status_message,
                        is_in_format_range=first_reading.is_in_format_range,
                        format_warning=first_reading.format_warning,
                        raw_output="\n".join(readings_data)
                    )
                
                # Ajouter à l'historique
                self.state.readings.append(reading)
                self.state.last_reading = reading
                
                # Garder seulement les 100 dernières lectures
                if len(self.state.readings) > 100:
                    self.state.readings = self.state.readings[-100:]
                
                # Notifier la mise à jour
                self._notify_update({
                    "type": "analysis_complete",
                    "reading": self._reading_to_dict(reading),
                    "statistics": stats,
                    "state": self._get_state_dict()
                })
                
                return {
                    "success": True,
                    "reading": self._reading_to_dict(reading),
                    "statistics": stats,
                    "state": self._get_state_dict()
                }
            
        except Exception as e:
            return {"error": f"Exception lors de l'analyse: {str(e)}", "exception_type": type(e).__name__}
        finally:
            # Reprendre la boucle de lecture après l'analyse (si elle tournait)
            if was_running:
                self._reading_paused = False
    
    def _get_quality_from_percentage(self, percentage: float) -> AlignmentQuality:
        """Détermine la qualité d'alignement basée sur le pourcentage"""
        if percentage >= 99.0:
            return AlignmentQuality.PERFECT
        elif percentage >= 97.0:
            return AlignmentQuality.GOOD
        elif percentage >= 96.0:
            return AlignmentQuality.AVERAGE
        else:
            return AlignmentQuality.POOR
    
    def _calculate_direct_percentage(self, sectors_detected: int, sectors_expected: int) -> float:
        """
        Calcul basique du pourcentage (Mode Direct)
        Inspiré d'ImageDisk : simple ratio secteurs détectés / attendus
        Pas de calculs complexes (médiane, cohérence, etc.)
        """
        if sectors_expected == 0:
            return 0.0
        
        percentage = (sectors_detected / sectors_expected) * 100.0
        
        # Arrondir selon la configuration du mode Direct
        config = MODE_CONFIG[AlignmentMode.DIRECT]
        decimal_places = config["decimal_places"]
        return round(percentage, decimal_places)
    
    def _get_direct_indicator(self, reading: TrackReading) -> Dict:
        """
        Génère un indicateur visuel simple (Mode Direct)
        Inspiré du Testkit : affichage visuel clair et immédiat
        """
        percentage = reading.percentage
        sectors_ratio = f"{reading.sectors_detected}/{reading.sectors_expected}"
        
        # Barre simple (comme Testkit)
        bar_count = int((percentage / 100.0) * 12)
        bars = "█" * bar_count + "░" * (12 - bar_count)
        
        # Statut simple avec symboles
        if percentage >= 99.0:
            status = "excellent"
            symbol = "✓"
            color = "green"
        elif percentage >= 95.0:
            status = "good"
            symbol = "○"
            color = "blue"
        elif percentage >= 90.0:
            status = "caution"
            symbol = "△"
            color = "yellow"
        else:
            status = "warning"
            symbol = "✗"
            color = "red"
        
        # Message simple
        message = f"{sectors_ratio} secteurs ({percentage}%)"
        
        return {
            "percentage": percentage,
            "sectors_ratio": sectors_ratio,
            "bars": bars,
            "status": status,
            "symbol": symbol,
            "color": color,
            "message": message
        }
    
    def _reading_to_dict(self, reading: TrackReading) -> Dict:
        """Convertit un TrackReading en dictionnaire"""
        return {
            "track": reading.track,
            "head": reading.head,
            "percentage": reading.percentage,
            "sectors_detected": reading.sectors_detected,
            "sectors_expected": reading.sectors_expected,
            "flux_transitions": reading.flux_transitions,
            "time_per_rev": reading.time_per_rev,
            "consistency": reading.consistency,
            "stability": reading.stability,
            "quality": reading.quality.value,
            "calculation_details": reading.calculation_details,
            "is_formatted": reading.is_formatted,
            "format_confidence": reading.format_confidence,
            "format_status_message": reading.format_status_message,
            "is_in_format_range": reading.is_in_format_range,
            "format_warning": reading.format_warning,
            "timestamp": reading.timestamp.isoformat(),
            "indicator": self._get_alignment_indicator(reading)
        }
    
    def _get_alignment_indicator(self, reading: TrackReading) -> Dict:
        """
        Génère des indicateurs visuels comme AmigaTestKit
        Indique si on s'éloigne de l'alignement idéal
        """
        percentage = reading.percentage
        quality = reading.quality
        
        # Calculer la distance par rapport à l'idéal (100%)
        distance_from_ideal = 100.0 - percentage
        
        # Indicateur de direction (si on s'éloigne ou se rapproche)
        # Basé sur la comparaison avec la lecture précédente
        direction = "stable"
        if len(self.state.readings) > 1:
            prev_reading = self.state.readings[-2]
            if percentage > prev_reading.percentage:
                direction = "improving"
            elif percentage < prev_reading.percentage:
                direction = "degrading"
        
        # Indicateur visuel (barre de qualité)
        # Perfect: ████████████ (12 barres)
        # Good:    ██████████░░ (10 barres)
        # Average:  ████████░░░░ (8 barres)
        # Poor:    ██████░░░░░░ (6 barres)
        bar_count = 12
        if quality == AlignmentQuality.GOOD:
            bar_count = 10
        elif quality == AlignmentQuality.AVERAGE:
            bar_count = 8
        elif quality == AlignmentQuality.POOR:
            bar_count = 6
        
        bars = "█" * bar_count + "░" * (12 - bar_count)
        
        # Couleur/statut
        status = "ok"
        if quality == AlignmentQuality.POOR:
            status = "warning"
        elif quality == AlignmentQuality.AVERAGE:
            status = "caution"
        elif quality == AlignmentQuality.PERFECT:
            status = "excellent"
        
        return {
            "percentage": percentage,
            "quality": quality.value,
            "distance_from_ideal": round(distance_from_ideal, 3),
            "direction": direction,
            "bars": bars,
            "status": status,
            "sectors_ratio": f"{reading.sectors_detected}/{reading.sectors_expected}",
            "recommendation": self._get_recommendation(reading)
        }
    
    def _get_recommendation(self, reading: TrackReading) -> str:
        """Génère une recommandation basée sur la lecture"""
        if reading.quality == AlignmentQuality.PERFECT:
            return "Alignement parfait, aucune action nécessaire"
        elif reading.quality == AlignmentQuality.GOOD:
            return "Alignement bon, ajustement mineur possible"
        elif reading.quality == AlignmentQuality.AVERAGE:
            return "Alignement moyen, ajustement recommandé"
        else:
            return "Alignement faible, ajustement nécessaire"
    
    def _get_state_dict(self) -> Dict:
        """Retourne l'état actuel sous forme de dictionnaire"""
        config = MODE_CONFIG[self.state.alignment_mode]
        return {
            "is_running": self.state.is_running,
            "current_track": self.state.current_track,
            "current_head": self.state.current_head,
            "auto_analyze": self.state.auto_analyze,
            "num_reads": self.state.num_reads,
            "format_type": self.state.format_type,
            "diskdefs_path": self.state.diskdefs_path,
            "alignment_mode": self.state.alignment_mode.value,
            "alignment_mode_config": {
                "reads": config["reads"],
                "delay_ms": config["delay_ms"],
                "timeout": config["timeout"],
                "estimated_latency_ms": config["delay_ms"] + (600 if config["reads"] == 1 else config["reads"] * 600)
            },
            "last_reading": self._reading_to_dict(self.state.last_reading) if self.state.last_reading else None,
            "total_readings": len(self.state.readings)
        }
    
    def get_state(self) -> Dict:
        """Retourne l'état actuel"""
        return self._get_state_dict()
    
    def set_auto_analyze(self, enabled: bool):
        """Active/désactive l'analyse automatique"""
        self.state.auto_analyze = enabled
    
    def set_num_reads(self, num_reads: int):
        """Définit le nombre de lectures pour l'analyse"""
        if num_reads < 1:
            num_reads = 1
        if num_reads > 20:
            num_reads = 20
        self.state.num_reads = num_reads
    
    def set_alignment_mode(self, mode: AlignmentMode):
        """Définit le mode d'alignement (Direct, Fine Tune, High Precision)"""
        if not isinstance(mode, AlignmentMode):
            # Si c'est une string, convertir
            try:
                mode = AlignmentMode(mode)
            except ValueError:
                raise ValueError(f"Mode invalide: {mode}. Modes valides: {[m.value for m in AlignmentMode]}")
        
        old_mode = self.state.alignment_mode
        self.state.alignment_mode = mode
        
        print(f"[ManualAlignment] Changement de mode: {old_mode.value} -> {mode.value}")
        
        # Notifier le changement de mode
        config = MODE_CONFIG[mode]
        self._notify_update({
            "type": "mode_changed",
            "old_mode": old_mode.value,
            "new_mode": mode.value,
            "mode_config": {
                "reads": config["reads"],
                "delay_ms": config["delay_ms"],
                "timeout": config["timeout"],
                "estimated_latency_ms": config["delay_ms"] + (600 if config["reads"] == 1 else config["reads"] * 600)
            },
            "state": self._get_state_dict()
        })
    
    def set_format(self, format_type: str, diskdefs_path: Optional[str] = None):
        """Définit le format de disquette et le chemin vers diskdefs.cfg"""
        print(f"[ManualAlignment] Changement de format: {self.state.format_type} -> {format_type}")
        self.state.format_type = format_type
        # Si diskdefs_path n'est pas fourni, essayer de le détecter automatiquement
        if diskdefs_path is None:
            from .diskdefs_parser import get_diskdefs_parser
            parser = get_diskdefs_parser()
            detected_path = parser.get_diskdefs_path()
            self.state.diskdefs_path = detected_path
        else:
            self.state.diskdefs_path = diskdefs_path
        print(f"[ManualAlignment] Format mis à jour: {self.state.format_type}, diskdefs: {self.state.diskdefs_path}")
        # Notifier le changement de format
        self._notify_update({
            "type": "format_changed",
            "format_type": format_type,
            "state": self._get_state_dict()
        })
    
    async def reset_data(self):
        """
        Réinitialise les données d'alignement (lectures, statistiques)
        sans affecter le format, la position actuelle, ou l'état de fonctionnement
        """
        # Réinitialiser uniquement les lectures, pas l'état complet
        self.state.readings = []
        self.state.last_reading = None
        
        # Notifier la réinitialisation
        self._notify_update({
            "type": "data_reset",
            "state": self._get_state_dict()
        })


# Instance globale du mode manuel
_manual_alignment_instance: Optional[ManualAlignmentMode] = None


def get_manual_alignment() -> ManualAlignmentMode:
    """Retourne l'instance globale du mode d'alignement manuel"""
    global _manual_alignment_instance
    if _manual_alignment_instance is None:
        _manual_alignment_instance = ManualAlignmentMode()
    return _manual_alignment_instance

