"""
Routes API pour AlignTester
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict
import platform
import subprocess
from pathlib import Path
import asyncio

from .greaseweazle import GreaseweazleExecutor
from .alignment_parser import AlignmentParser
from .alignment_state import alignment_state_manager, AlignmentStatus
from .websocket import websocket_manager
from .settings import settings_manager
from .manual_alignment import get_manual_alignment
from .diskdefs_parser import get_diskdefs_parser

router = APIRouter()

# Modèles Pydantic
class AlignmentRequest(BaseModel):
    """Paramètres pour un test d'alignement"""
    cylinders: int = 80
    retries: int = 3
    timeout: Optional[int] = None
    format_type: Optional[str] = "ibm.1440"  # Format de disquette
    diskdefs_path: Optional[str] = None  # Chemin vers diskdefs.cfg

class GreaseweazleInfo(BaseModel):
    """Informations sur Greaseweazle"""
    platform: str
    gw_path: str
    version: Optional[str] = None
    align_available: bool = False
    device: Optional[Dict] = None  # Informations du device (port, model, firmware, etc.)

class DriveRequest(BaseModel):
    """Paramètres pour définir le lecteur"""
    drive: str  # A, B, 0, 1, 2, 3

class GwPathRequest(BaseModel):
    """Paramètres pour définir le chemin vers gw.exe"""
    gw_path: str

class Track0VerifyRequest(BaseModel):
    """Paramètres pour la vérification Track 0"""
    format_type: Optional[str] = "ibm.1440"  # Format de disquette à utiliser

# Instance globale de l'exécuteur Greaseweazle
executor = GreaseweazleExecutor()

# Détection de la plateforme et du chemin gw
def detect_gw_path() -> str:
    """Détecte le chemin vers gw.exe ou gw selon la plateforme"""
    return executor.gw_path

def check_gw_version(gw_path: str) -> Optional[str]:
    """Vérifie la version de Greaseweazle"""
    return executor.check_version()

def check_align_available(gw_path: str) -> bool:
    """Vérifie si la commande align est disponible (PR #592)"""
    return executor.check_align_available()

async def run_alignment_task(cylinders: int, retries: int, format_type: Optional[str] = None, diskdefs_path: Optional[str] = None):
    """
    Exécute l'alignement en arrière-plan et envoie les mises à jour via WebSocket
    """
    try:
        # Parser pour traiter les résultats
        parser = AlignmentParser()
        all_values = []
        value_queue = asyncio.Queue()
        
        def on_output_line(line: str):
            """Callback appelé pour chaque ligne de sortie (synchrone)"""
            # Parser la ligne
            value = parser.parse_line(line)
            if value:
                all_values.append(value)
                # Ajouter à la queue pour traitement asynchrone
                try:
                    value_data = {
                        "track": value.track,
                        "percentage": value.percentage,
                        "base": value.base,
                        "bands": value.bands,
                        "sectors_detected": value.sectors_detected,
                        "sectors_expected": value.sectors_expected,
                        "flux_transitions": value.flux_transitions,
                        "time_per_rev": value.time_per_rev,
                        "format_type": value.format_type,
                        "consistency": value.consistency,
                        "stability": value.stability,
                        "positioning_status": value.positioning_status,
                        "line_number": value.line_number
                    }
                    value_queue.put_nowait(value_data)
                except Exception:
                    pass  # Queue pleine, ignorer
        
        # Tâche pour envoyer les mises à jour via WebSocket
        async def send_updates():
            """Envoie les mises à jour depuis la queue"""
            updates_active = True
            while updates_active:
                try:
                    # Attendre une valeur avec timeout pour vérifier si terminé
                    try:
                        value_data = await asyncio.wait_for(value_queue.get(), timeout=0.2)
                        await websocket_manager.send_alignment_update({
                            "type": "value",
                            "value": value_data
                        })
                        await alignment_state_manager.add_value(value_data)
                    except asyncio.TimeoutError:
                        # Vérifier si le processus est terminé
                        current_state = await alignment_state_manager.get_state()
                        if current_state.status != AlignmentStatus.RUNNING:
                            updates_active = False
                            break
                except Exception as e:
                    print(f"Erreur lors de l'envoi de mise à jour: {e}")
                    updates_active = False
                    break
        
        # Démarrer la tâche d'envoi des mises à jour
        update_task = asyncio.create_task(send_updates())
        
        try:
            # Exécuter la commande align
            result = await executor.run_align(
                cylinders=cylinders,
                retries=retries,
                format_type=format_type or "ibm.1440",
                diskdefs_path=diskdefs_path,
                on_output=on_output_line
            )
            
            # Attendre que toutes les mises à jour soient envoyées
            await asyncio.sleep(0.5)  # Donner du temps pour les dernières mises à jour
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass
            
            # Calculer les statistiques
            statistics = parser.calculate_statistics(all_values, limit=cylinders * 2)
            statistics["quality"] = parser.get_alignment_quality(statistics["average"])
            
            # Mettre à jour l'état
            await alignment_state_manager.complete_alignment(statistics)
            
            # Envoyer les résultats finaux via WebSocket
            await websocket_manager.send_alignment_complete({
                "success": result["success"],
                "statistics": statistics,
                "returncode": result["returncode"]
            })
        except asyncio.CancelledError:
            update_task.cancel()
            raise
        
    except asyncio.CancelledError:
        await alignment_state_manager.cancel_alignment()
        await websocket_manager.broadcast({
            "type": "alignment_cancelled",
            "message": "Alignement annulé par l'utilisateur"
        })
    except Exception as e:
        error_msg = str(e)
        await alignment_state_manager.set_error(error_msg)
        await websocket_manager.broadcast({
            "type": "alignment_error",
            "error": error_msg
        })

@router.get("/info")
async def get_info():
    """Récupère les informations sur Greaseweazle et la plateforme"""
    gw_path = detect_gw_path()
    
    # Sauvegarder automatiquement le chemin si aucun n'est sauvegardé et que c'est un chemin absolu valide
    if not settings_manager.get_gw_path() and gw_path:
        from pathlib import Path
        path = Path(gw_path)
        if path.is_absolute() and path.exists():
            settings_manager.set_gw_path(gw_path)
    
    version = check_gw_version(gw_path)
    align_available = check_align_available(gw_path)
    
    # Récupérer les informations détaillées du device
    device_info = executor.get_device_info()
    
    return GreaseweazleInfo(
        platform=platform.system(),
        gw_path=gw_path,
        version=version,
        align_available=align_available,
        device=device_info
    )

@router.post("/align")
async def start_alignment(request: AlignmentRequest):
    """Démarre un test d'alignement"""
    # Vérifier l'état actuel
    current_state = await alignment_state_manager.get_state()
    if current_state.status == AlignmentStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Un alignement est déjà en cours. Veuillez attendre ou annuler."
        )
    
    # Vérifier si align est disponible
    if not executor.check_align_available():
        raise HTTPException(
            status_code=400,
            detail="La commande 'align' n'est pas disponible. Veuillez utiliser gw.exe compilé depuis PR #592."
        )
    
    # Vérifier que Greaseweazle est connecté
    connection_status = executor.check_connection()
    if not connection_status["connected"]:
        error_msg = connection_status.get("error", "Greaseweazle non détecté")
        raise HTTPException(
            status_code=400,
            detail=f"Greaseweazle non connecté ou non détecté. {error_msg}"
        )
    
    # Lancer l'alignement en arrière-plan
    task = asyncio.create_task(
        run_alignment_task(
            request.cylinders, 
            request.retries,
            request.format_type,
            request.diskdefs_path
        )
    )
    
    # Mettre à jour l'état
    await alignment_state_manager.start_alignment(
        cylinders=request.cylinders,
        retries=request.retries,
        process_task=task
    )
    
    # Envoyer notification de démarrage
    await websocket_manager.broadcast({
        "type": "alignment_started",
        "cylinders": request.cylinders,
        "retries": request.retries
    })
    
    return {
        "status": "started",
        "message": f"Test d'alignement démarré avec {request.cylinders} cylindres",
        "cylinders": request.cylinders,
        "retries": request.retries
    }

@router.post("/align/reset")
async def reset_alignment_data():
    """Réinitialise les données d'alignement (statistiques, valeurs) sans affecter le format"""
    await alignment_state_manager.reset_state()
    
    # Réinitialiser aussi les données du mode manuel
    manual_mode = get_manual_alignment()
    await manual_mode.reset_data()
    
    # Envoyer notification via WebSocket
    await websocket_manager.broadcast({
        "type": "alignment_reset",
        "message": "Données d'alignement réinitialisées"
    })
    return {
        "status": "reset",
        "message": "Données d'alignement réinitialisées"
    }

@router.post("/align/hard-reset")
async def hard_reset_greaseweazle():
    """Envoie la commande 'gw reset' pour réinitialiser le hardware Greaseweazle"""
    try:
        # Exécuter la commande gw reset
        result = await executor.run_command(["reset"], timeout=5)
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Greaseweazle réinitialisé avec succès",
                "output": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": f"Erreur lors de la réinitialisation (code {result.returncode})",
                "error": result.stderr or result.stdout
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la réinitialisation: {str(e)}"
        )

@router.post("/align/cancel")
async def cancel_alignment():
    """Annule l'alignement en cours"""
    current_state = await alignment_state_manager.get_state()
    if current_state.status != AlignmentStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Aucun alignement en cours"
        )
    
    # Annuler la tâche en cours
    if current_state.process_task and not current_state.process_task.done():
        current_state.process_task.cancel()
        try:
            await current_state.process_task
        except asyncio.CancelledError:
            pass
    
    await alignment_state_manager.cancel_alignment()
    
    # Envoyer notification d'annulation
    await websocket_manager.broadcast({
        "type": "alignment_cancelled",
        "message": "Alignement annulé par l'utilisateur"
    })
    
    return {
        "status": "cancelled",
        "message": "Alignement annulé"
    }

@router.get("/status")
async def get_status():
    """Récupère le statut actuel de l'application"""
    state = await alignment_state_manager.get_state()
    return state.to_dict()

@router.get("/detect")
async def detect_greaseweazle():
    """
    Détecte automatiquement Greaseweazle et vérifie la connexion
    Retourne les informations de détection et de connexion
    
    OPTIMISATION: Limite le nombre de ports retournés pour éviter de surcharger
    """
    # Détecter les ports série disponibles (mais limiter l'affichage)
    all_ports = executor.detect_serial_ports()
    
    # Filtrer pour ne garder que les ports potentiellement intéressants
    # (Greaseweazle ou ports USB série)
    interesting_ports = []
    greaseweazle_ports = []
    usb_ports = []
    
    for port in all_ports:
        if port.get("is_greaseweazle", False):
            greaseweazle_ports.append(port)
        elif port.get("vid") or port.get("product") or "USB" in str(port.get("description", "")):
            usb_ports.append(port)
    
    # Prioriser les ports Greaseweazle
    interesting_ports.extend(greaseweazle_ports)
    
    # Ajouter les ports USB (limiter à 10 max au total)
    remaining_slots = 10 - len(interesting_ports)
    if remaining_slots > 0:
        interesting_ports.extend(usb_ports[:remaining_slots])
    
    # Si toujours aucun port, afficher au moins les 5 premiers (pour debug)
    if len(interesting_ports) == 0 and len(all_ports) > 0:
        interesting_ports = all_ports[:5]
    
    # Vérifier la connexion (rapide, utilise directement gw info)
    connection_status = executor.check_connection()
    
    return {
        "ports_detected": len(all_ports),
        "ports_shown": len(interesting_ports),
        "ports": interesting_ports,  # Seulement les ports intéressants
        "greaseweazle_found": connection_status["connected"],
        "connection": connection_status,
        "gw_path": executor.gw_path,
        "gw_available": executor.check_align_available(),  # Si align est disponible, gw est disponible
        "align_available": executor.check_align_available()
    }

@router.get("/detect/ports")
async def detect_ports():
    """
    Liste tous les ports série disponibles
    Utile pour le débogage
    """
    ports = executor.detect_serial_ports()
    return {
        "ports": ports,
        "count": len(ports)
    }

@router.get("/settings")
async def get_settings():
    """Récupère les paramètres utilisateur"""
    return {
        "last_port": settings_manager.get_last_port(),
        "last_port_date": settings_manager.get("last_port_date"),
        "all_settings": settings_manager.get_all_settings()
    }

class LastPortRequest(BaseModel):
    """Modèle pour la requête de sauvegarde du port"""
    port: str

@router.post("/settings/last_port")
async def set_last_port(request: LastPortRequest):
    """Définit le dernier port utilisé (appelé depuis le frontend)"""
    settings_manager.set_last_port(request.port)
    return {
        "status": "saved",
        "last_port": request.port
    }

# ===== Routes pour le mode d'alignement manuel =====

class ManualAlignmentStartRequest(BaseModel):
    """Paramètres pour démarrer le mode manuel"""
    initial_track: int = 0
    initial_head: int = 0

class ManualAlignmentSeekRequest(BaseModel):
    """Paramètres pour seek vers une piste"""
    track: int
    head: Optional[int] = None

class ManualAlignmentMoveRequest(BaseModel):
    """Paramètres pour déplacer la tête"""
    delta: int  # +1 pour avancer, -1 pour reculer

class ManualAlignmentJumpRequest(BaseModel):
    """Paramètres pour sauter vers une piste"""
    track_number: int  # 1-8 pour tracks 10, 20, 30, etc.

class ManualAlignmentHeadRequest(BaseModel):
    """Paramètres pour changer de tête"""
    head: int  # 0 ou 1

class ManualAlignmentSettingsRequest(BaseModel):
    """Paramètres pour configurer le mode manuel"""
    auto_analyze: Optional[bool] = None
    num_reads: Optional[int] = None
    format_type: Optional[str] = None
    diskdefs_path: Optional[str] = None
    alignment_mode: Optional[str] = None  # "direct", "fine_tune", "high_precision"

class ManualAlignmentAnalyzeRequest(BaseModel):
    """Paramètres optionnels pour l'analyse"""
    track: Optional[int] = None
    head: Optional[int] = None

@router.post("/manual/start")
async def start_manual_alignment(request: ManualAlignmentStartRequest):
    """Démarre le mode d'alignement manuel"""
    manual_mode = get_manual_alignment()
    
    # Configurer le callback pour envoyer les mises à jour via WebSocket
    # Note: Le callback est synchrone, donc on utilise une queue pour les mises à jour async
    update_queue = asyncio.Queue()
    
    def on_update(data: dict):
        """Callback pour les mises à jour en temps réel (synchrone)"""
        try:
            update_queue.put_nowait(data)
        except Exception:
            pass  # Queue pleine, ignorer
    
    manual_mode.set_update_callback(on_update)
    
    # Tâche pour envoyer les mises à jour depuis la queue
    async def send_updates():
        """Envoie les mises à jour depuis la queue"""
        while manual_mode.state.is_running:
            try:
                data = await asyncio.wait_for(update_queue.get(), timeout=0.1)
                await websocket_manager.broadcast({
                    "type": "manual_alignment_update",
                    "data": data
                })
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Erreur lors de l'envoi de mise à jour manuelle: {e}")
                break
    
    # Démarrer la tâche d'envoi des mises à jour
    update_task = asyncio.create_task(send_updates())
    
    result = await manual_mode.start(
        initial_track=request.initial_track,
        initial_head=request.initial_head
    )
    
    if "error" in result:
        update_task.cancel()
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Stocker la tâche pour la nettoyer lors de l'arrêt
    manual_mode._update_task = update_task
    
    return result

@router.post("/manual/stop")
async def stop_manual_alignment():
    """Arrête le mode d'alignement manuel"""
    manual_mode = get_manual_alignment()
    result = await manual_mode.stop()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/manual/seek")
async def manual_seek(request: ManualAlignmentSeekRequest):
    """Déplace la tête vers une piste spécifique"""
    manual_mode = get_manual_alignment()
    result = await manual_mode.seek(request.track, request.head)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/manual/move")
async def manual_move(request: ManualAlignmentMoveRequest):
    """Déplace la tête de delta pistes (+1 ou -1)"""
    manual_mode = get_manual_alignment()
    result = await manual_mode.move_track(request.delta)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/manual/jump")
async def manual_jump(request: ManualAlignmentJumpRequest):
    """Saute vers une piste (1-8 pour tracks 10, 20, 30, etc.)"""
    if request.track_number < 1 or request.track_number > 8:
        raise HTTPException(status_code=400, detail="track_number doit être entre 1 et 8")
    
    manual_mode = get_manual_alignment()
    result = await manual_mode.jump_track(request.track_number)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/manual/head")
async def manual_set_head(request: ManualAlignmentHeadRequest):
    """Change la tête active (0 ou 1)"""
    if request.head not in [0, 1]:
        raise HTTPException(status_code=400, detail="head doit être 0 ou 1")
    
    manual_mode = get_manual_alignment()
    result = await manual_mode.set_head(request.head)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/manual/recal")
async def manual_recalibrate():
    """Recalibre la tête (seek vers track 0)"""
    manual_mode = get_manual_alignment()
    result = await manual_mode.recalibrate()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/manual/analyze")
async def manual_analyze(request: ManualAlignmentAnalyzeRequest = Body(default=ManualAlignmentAnalyzeRequest())):
    """Analyse la piste actuelle ou spécifiée
    
    Peut être appelé avec ou sans body. Si aucun body n'est fourni,
    utilise la piste actuelle du mode manuel (ou piste 0.0 par défaut).
    """
    manual_mode = get_manual_alignment()
    
    # Si une piste est spécifiée dans la requête, l'utiliser
    # Sinon, utiliser la piste actuelle du mode manuel
    track = request.track if request.track is not None else None
    head = request.head if request.head is not None else None
    
    result = await manual_mode.analyze_current_track(track=track, head=head)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/manual/state")
async def get_manual_state():
    """Récupère l'état actuel du mode manuel"""
    manual_mode = get_manual_alignment()
    return manual_mode.get_state()

@router.post("/manual/settings")
async def set_manual_settings(request: ManualAlignmentSettingsRequest):
    """Configure les paramètres du mode manuel"""
    manual_mode = get_manual_alignment()
    
    if request.auto_analyze is not None:
        manual_mode.set_auto_analyze(request.auto_analyze)
    
    if request.num_reads is not None:
        manual_mode.set_num_reads(request.num_reads)
    
    if request.format_type is not None:
        manual_mode.set_format(request.format_type, request.diskdefs_path)
    
    if request.alignment_mode is not None:
        from .manual_alignment import AlignmentMode
        try:
            mode = AlignmentMode(request.alignment_mode)
            manual_mode.set_alignment_mode(mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Mode invalide: {request.alignment_mode}. Modes valides: {[m.value for m in AlignmentMode]}"
            )
    
    return {
        "success": True,
        "state": manual_mode.get_state()
    }

@router.get("/manual/formats")
async def get_available_formats(refresh: bool = False):
    """Récupère la liste des formats disponibles depuis diskdefs.cfg"""
    parser = get_diskdefs_parser()
    formats = parser.get_available_formats(force_refresh=refresh)
    diskdefs_path = parser.get_diskdefs_path()
    
    # Extraire la liste des marques/préfixes uniques pour information
    prefixes = set()
    for fmt in formats:
        if '.' in fmt["name"]:
            prefix = fmt["name"].split('.')[0]
            prefixes.add(prefix)
        else:
            prefixes.add(fmt["name"])
    
    return {
        "success": True,
        "formats": formats,
        "count": len(formats),
        "diskdefs_path": diskdefs_path,
        "available_brands": sorted(list(prefixes))  # Liste des marques disponibles
    }

@router.get("/settings/drive")
async def get_drive():
    """Récupère le lecteur actuellement sélectionné"""
    from .settings import settings_manager
    drive = settings_manager.get_drive()
    return {
        "success": True,
        "drive": drive
    }

@router.post("/settings/drive")
async def set_drive(request: DriveRequest):
    """Définit le lecteur à utiliser"""
    from .settings import settings_manager
    try:
        settings_manager.set_drive(request.drive)
        return {
            "success": True,
            "drive": request.drive,
            "message": f"Lecteur défini sur {request.drive}"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/drive/test")
async def test_drive():
    """Teste le lecteur en envoyant une séquence de commandes seek pour un retour audible clair
    Séquence: 0 → 20 → 0 → 10 → 0 → 20 → 0"""
    from .settings import settings_manager
    from .greaseweazle import GreaseweazleExecutor
    
    # Vérifier que Greaseweazle est connecté
    executor = GreaseweazleExecutor()
    connection_status = executor.check_connection()
    if not connection_status["connected"]:
        raise HTTPException(
            status_code=400,
            detail="Greaseweazle non connecté ou non détecté. Veuillez d'abord détecter Greaseweazle."
        )
    
    try:
        # Séquence de pistes pour un retour audible clair
        # 0 → 20 → 0 → 10 → 0 → 20 → 0
        tracks_sequence = [0, 20, 0, 10, 0, 20, 0]
        results = []
        errors = []
        
        print(f"[test_drive] Début de la séquence de test: {tracks_sequence}")
        
        for i, track in enumerate(tracks_sequence):
            try:
                # Envoyer la commande seek avec --motor-on pour activer le moteur
                # Syntaxe: gw seek [--device DEVICE] [--drive DRIVE] [--motor-on] [--force] CYLINDER
                args = ["seek", "--motor-on", "--force", str(track)]
                result = await executor.run_command(args, timeout=10)
                
                print(f"[test_drive] Seek vers piste {track} ({i+1}/{len(tracks_sequence)}): returncode={result.returncode}")
                
                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout or 'Unknown error'
                    errors.append(f"Piste {track}: {error_msg}")
                    print(f"[test_drive] Erreur sur piste {track}: {error_msg}")
                
                results.append({
                    "track": track,
                    "success": result.returncode == 0,
                    "step": i + 1
                })
                
                # Petite pause entre les mouvements pour un retour audible plus clair
                if i < len(tracks_sequence) - 1:  # Pas de pause après le dernier
                    await asyncio.sleep(0.1)  # 100ms de pause entre les mouvements (réduit de 300ms pour accélérer)
                    
            except asyncio.TimeoutError:
                errors.append(f"Piste {track}: Timeout")
                results.append({
                    "track": track,
                    "success": False,
                    "error": "Timeout",
                    "step": i + 1
                })
                break  # Arrêter la séquence en cas de timeout
            except Exception as e:
                errors.append(f"Piste {track}: {str(e)}")
                results.append({
                    "track": track,
                    "success": False,
                    "error": str(e),
                    "step": i + 1
                })
                break  # Arrêter la séquence en cas d'erreur
        
        # Vérifier si toutes les commandes ont réussi
        all_success = all(r["success"] for r in results)
        
        if all_success:
            return {
                "success": True,
                "message": f"Séquence de test terminée avec succès. Vous devriez avoir entendu le lecteur se déplacer {len(tracks_sequence)} fois.",
                "sequence": tracks_sequence,
                "results": results,
                "total_steps": len(tracks_sequence)
            }
        else:
            return {
                "success": False,
                "error": f"Erreurs lors de la séquence: {'; '.join(errors)}",
                "sequence": tracks_sequence,
                "results": results,
                "total_steps": len(tracks_sequence),
                "completed_steps": len([r for r in results if r["success"]])
            }
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[test_drive] Exception: {str(e)}")
        print(f"[test_drive] Traceback: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du test du lecteur: {str(e)}"
        )

@router.get("/settings/gw-path")
async def get_gw_path():
    """Récupère le chemin vers gw.exe sauvegardé"""
    from .settings import settings_manager
    gw_path = settings_manager.get_gw_path()
    return {
        "success": True,
        "gw_path": gw_path
    }

@router.post("/settings/gw-path")
async def set_gw_path(request: GwPathRequest):
    """Définit le chemin vers gw.exe/gw"""
    from .settings import settings_manager
    from .greaseweazle import normalize_gw_path
    try:
        # Utiliser la fonction de normalisation unique
        normalized_path = normalize_gw_path(request.gw_path, validate=True)
        
        # Sauvegarder le chemin normalisé
        settings_manager.set_gw_path(normalized_path)
        
        # Mettre à jour l'executor global avec le nouveau chemin
        executor.gw_path = normalized_path
        
        return {
            "success": True,
            "gw_path": normalized_path,
            "message": f"Chemin gw.exe défini sur {normalized_path}"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la définition du chemin: {str(e)}"
        )

@router.post("/settings/gw-path/detect")
async def detect_gw_path_auto():
    """
    Détecte automatiquement le chemin vers gw.exe dans tous les emplacements possibles
    et le sauvegarde automatiquement si trouvé
    """
    from .settings import settings_manager
    
    # Utiliser la méthode de détection automatique
    detection_result = executor.detect_gw_path_auto()
    
    if detection_result.get("found") and detection_result.get("path"):
        detected_path = detection_result["path"]
        
        # Sauvegarder automatiquement le chemin trouvé
        settings_manager.set_gw_path(detected_path)
        
        # Mettre à jour l'executor global
        executor.gw_path = detected_path
        
        return {
            "success": True,
            "found": True,
            "gw_path": detected_path,
            "source": detection_result.get("source", "auto_detection"),
            "message": f"gw.exe détecté et sauvegardé: {detected_path}",
            "all_paths_found": detection_result.get("all_paths_found", [])
        }
    else:
        return {
            "success": False,
            "found": False,
            "gw_path": None,
            "error": detection_result.get("error", "Aucun exécutable gw.exe/gw trouvé"),
            "message": "Aucun exécutable gw.exe/gw trouvé. Veuillez spécifier le chemin manuellement."
        }

@router.post("/track0/verify")
async def verify_track0_sensor(request: Track0VerifyRequest = Track0VerifyRequest()):
    """
    Vérifie le capteur Track 0 (Section 9.9 du manuel Panasonic JU-253)
    Teste si le seek vers la piste 0 fonctionne correctement depuis différentes positions
    et effectue plusieurs lectures de la piste 0 pour vérifier la cohérence
    
    Cette vérification est recommandée avant de commencer un alignement pour s'assurer
    que le capteur Track 0 fonctionne correctement.
    
    Args:
        request: Paramètres de vérification, incluant le format_type de disquette
    """
    from .track0_verifier import Track0Verifier
    
    # Vérifier que Greaseweazle est connecté
    connection_status = executor.check_connection()
    if not connection_status["connected"]:
        raise HTTPException(
            status_code=400,
            detail="Greaseweazle non connecté ou non détecté. Veuillez d'abord détecter Greaseweazle."
        )
    
    try:
        verifier = Track0Verifier(executor)
        results = await verifier.verify_track0_sensor(
            test_positions=[10, 20, 40, 79],  # Positions de test
            reads_per_test=5,  # 5 lectures pour vérifier la cohérence
            format_type=request.format_type  # Format de disquette sélectionné
        )
        
        return {
            "status": "completed",
            "sensor_ok": results["sensor_ok"],
            "seek_tests": results["seek_tests"],
            "read_tests": results["read_tests"],
            "warnings": results["warnings"],
            "suggestions": results["suggestions"],
            "message": "Vérification Track 0 terminée"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la vérification Track 0: {str(e)}"
        )

