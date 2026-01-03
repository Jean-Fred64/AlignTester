"""
Module d'intégration avec Greaseweazle
Gère l'exécution des commandes gw.exe / gw
"""

import subprocess
import platform
import asyncio
import sys
import shutil
from pathlib import Path
from typing import Optional, Callable, List, Dict
import json
import glob
import os
from .settings import settings_manager

# Pour la détection des ports série
try:
    from serial.tools import list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

def _is_wsl() -> bool:
    """Détecte si on est dans WSL (Windows Subsystem for Linux)"""
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            return 'microsoft' in version_info or 'wsl' in version_info
    except:
        return False

def normalize_gw_path(path: str, validate: bool = True) -> str:
    """
    Normalise et valide le chemin vers gw.exe/gw
    
    Gère :
    - Conversion Windows vers WSL (/mnt/c/...)
    - Détection automatique si c'est un dossier ou un fichier
    - Validation de l'existence du chemin
    - Retourne un chemin absolu normalisé
    
    Args:
        path: Chemin à normaliser (peut être un fichier ou un dossier)
        validate: Si True, valide que le chemin existe (défaut: True)
        
    Returns:
        Chemin absolu normalisé vers gw.exe/gw
        
    Raises:
        ValueError: Si le chemin n'existe pas et validate=True
    """
    # Nettoyer le chemin (enlever les espaces en début/fin)
    path = path.strip()
    
    # Si le chemin est vide ou juste un nom (ex: "gw.exe"), le retourner tel quel
    # (sera cherché dans PATH)
    if not path or (not os.path.isabs(path) and '/' not in path and '\\' not in path and ':' not in path):
        return path
    
    # Convertir chemin Windows vers WSL si nécessaire
    is_wsl_env = _is_wsl()
    if is_wsl_env and len(path) >= 3 and path[1] == ':' and path[2] in ['\\', '/']:
        # Chemin Windows (format X:\... ou X:/...)
        drive_letter = path[0].lower()
        remaining_path = path[3:].replace('\\', '/')
        path = f"/mnt/{drive_letter}/{remaining_path}"
    
    # Créer un objet Path
    path_obj = Path(path)
    
    # Si c'est un chemin absolu, le normaliser
    if path_obj.is_absolute() or path.startswith('/mnt/'):
        # Chemin absolu - vérifier s'il existe
        if validate and not path_obj.exists():
            raise ValueError(f"Le chemin spécifié n'existe pas: {path}")
        
        # Si c'est un dossier, chercher gw.exe/gw dedans
        if path_obj.is_dir():
            # Chercher gw.exe (Windows) ou gw (Linux) dans le dossier
            gw_exe = path_obj / "gw.exe"
            gw_bin = path_obj / "gw"
            
            if gw_exe.exists():
                return str(gw_exe.resolve())
            elif gw_bin.exists():
                return str(gw_bin.resolve())
            elif validate:
                raise ValueError(f"gw.exe ou gw non trouvé dans le dossier: {path}")
            else:
                # Si validate=False, retourner le chemin du dossier + /gw.exe ou /gw
                # (sera validé plus tard)
                # Dans WSL, on peut avoir gw.exe Windows, donc essayer d'abord gw.exe
                if is_wsl_env:
                    return str(path_obj / "gw.exe")  # WSL : préférer gw.exe Windows
                else:
                    return str(path_obj / "gw.exe") if platform.system() == "Windows" else str(path_obj / "gw")
        elif path_obj.is_file():
            # C'est déjà un fichier - vérifier que c'est bien gw.exe ou gw
            if path_obj.name.lower() not in ["gw.exe", "gw"]:
                if validate:
                    raise ValueError(f"Le fichier spécifié n'est pas gw.exe ou gw: {path}")
            return str(path_obj.resolve())
        else:
            # Le chemin n'existe pas
            if validate:
                raise ValueError(f"Le chemin spécifié n'existe pas: {path}")
            # Si validate=False, retourner le chemin tel quel
            return path
    else:
        # Chemin relatif - retourner tel quel (sera cherché dans PATH ou cwd)
        return path

class GreaseweazleExecutor:
    """Exécuteur de commandes Greaseweazle"""
    
    def __init__(self, gw_path: Optional[str] = None):
        self.platform = platform.system()
        self.gw_path = gw_path or self._detect_gw_path()
    
    def _is_wsl(self) -> bool:
        """Détecte si on est dans WSL (Windows Subsystem for Linux)"""
        return _is_wsl()
    
    def _detect_gw_path(self) -> str:
        """Détecte le chemin vers gw.exe ou gw"""
        # D'abord, vérifier si un chemin est sauvegardé dans les settings
        saved_path = settings_manager.get_gw_path()
        if saved_path:
            try:
                # Normaliser le chemin sauvegardé (sans validation pour ne pas bloquer si le fichier a été déplacé)
                normalized = normalize_gw_path(saved_path, validate=False)
                path_obj = Path(normalized)
                if path_obj.exists():
                    return str(path_obj.resolve())
            except (ValueError, OSError):
                # Si le chemin sauvegardé est invalide, continuer avec la détection automatique
                pass
        
        # Détection automatique - chercher dans les emplacements possibles
        search_paths = []
        
        if self.platform == "Windows":
            # 1. Répertoire de l'exécutable (standalone)
            if getattr(sys, 'frozen', False):
                exe_dir = Path(sys.executable).parent
                search_paths.extend([
                    exe_dir / "gw.exe",
                    exe_dir / "greaseweazle" / "gw.exe",
                    exe_dir / "greaseweazle-1.23" / "gw.exe",
                    exe_dir.parent / "gw.exe",
                    exe_dir.parent / "greaseweazle" / "gw.exe",
                    exe_dir.parent / "greaseweazle-1.23" / "gw.exe",
                ])
            
            # 2. Répertoire courant et répertoire de travail
            search_paths.extend([
                Path("gw.exe"),
                Path.cwd() / "gw.exe",
            ])
            
            # 3. Emplacements Windows communs
            search_paths.extend([
                Path("C:/Program Files/Greaseweazle/gw.exe"),
                Path("C:/Program Files (x86)/Greaseweazle/gw.exe"),
                Path.home() / "AppData/Local/Greaseweazle/gw.exe",
            ])
            
            # 4. Chercher dans PATH
            gw_in_path = shutil.which("gw.exe")
            if gw_in_path:
                search_paths.append(Path(gw_in_path))
        else:
            # Linux/WSL
            if self._is_wsl():
                # Chemins WSL vers gw.exe Windows
                search_paths.extend([
                    Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23b/gw.exe"),
                    Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23/gw.exe"),
                    Path("/mnt/c/Program Files/Greaseweazle/gw.exe"),
                    Path("/mnt/c/Program Files (x86)/Greaseweazle/gw.exe"),
                ])
            
            # Chercher gw dans PATH
            gw_in_path = shutil.which("gw")
            if gw_in_path:
                search_paths.append(Path(gw_in_path))
        
        # Tester tous les chemins
        for gw_path in search_paths:
            try:
                if gw_path.exists():
                    return str(gw_path.resolve())
            except (OSError, ValueError):
                continue
        
        # En dernier recours, retourner le nom de l'exécutable (sera cherché dans PATH)
        return "gw.exe" if self.platform == "Windows" else "gw"
    
    async def run_command(
        self,
        args: List[str],
        on_output: Optional[Callable[[str], None]] = None,
        timeout: Optional[int] = None
    ) -> subprocess.CompletedProcess:
        """Exécute une commande Greaseweazle de manière asynchrone"""
        # Vérifier si un port série doit être ajouté
        # Ne pas ajouter --device si déjà présent dans les args
        has_device = any(arg.startswith('--device') for arg in args)
        
        # Construire la commande : gw.exe [action] [--device port] [--drive X] [autres args]
        # IMPORTANT: --device doit être placé APRÈS l'action, pas avant
        cmd = [self.gw_path]
        
        if not has_device:
            # Récupérer le port depuis les settings
            # NE PAS appeler check_connection() ici car cela créerait une récursion infinie
            # (check_connection() appelle get_device_info() qui appelle run_command())
            last_port = settings_manager.get_last_port()
            drive = settings_manager.get_drive()
            
            # Ajouter l'action d'abord
            if args:
                cmd.append(args[0])  # L'action (info, align, seek, etc.)
                
                # Ajouter --device après l'action si un port est disponible
                if last_port:
                    cmd.extend(["--device", last_port])
                    print(f"[GreaseweazleExecutor] Ajout du port: --device {last_port}")
                else:
                    # Si aucun port n'est sauvegardé, gw.exe peut détecter automatiquement
                    # mais c'est plus lent. On log pour informer l'utilisateur.
                    print(f"[GreaseweazleExecutor] Aucun port sauvegardé, gw.exe va détecter automatiquement")
                
                # Ajouter --drive si ce n'est pas déjà dans les args
                has_drive = any(arg.startswith('--drive') for arg in args)
                if not has_drive:
                    cmd.extend(["--drive", drive])
                    print(f"[GreaseweazleExecutor] Ajout du lecteur: --drive {drive}")
                
                # Ajouter les autres arguments
                if len(args) > 1:
                    cmd.extend(args[1:])
            else:
                # Pas d'action, vérifier si --drive est nécessaire
                has_drive = any(arg.startswith('--drive') for arg in args)
                if not has_drive:
                    drive = settings_manager.get_drive()
                    cmd.extend(["--drive", drive])
                    print(f"[GreaseweazleExecutor] Ajout du lecteur: --drive {drive}")
                cmd.extend(args)
        else:
            # --device est déjà dans les args, vérifier si --drive est présent
            has_drive = any(arg.startswith('--drive') for arg in args)
            if not has_drive:
                drive = settings_manager.get_drive()
                # Insérer --drive après --device si présent, sinon au début
                device_idx = next((i for i, arg in enumerate(args) if arg.startswith('--device')), -1)
                if device_idx >= 0 and device_idx + 1 < len(args):
                    # Insérer après --device et sa valeur
                    args.insert(device_idx + 2, "--drive")
                    args.insert(device_idx + 3, drive)
                else:
                    # Ajouter au début
                    args.insert(0, "--drive")
                    args.insert(1, drive)
                print(f"[GreaseweazleExecutor] Ajout du lecteur: --drive {drive}")
            cmd.extend(args)
        
        # Log pour debug (peut être désactivé en production)
        print(f"[GreaseweazleExecutor] Exécution: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT  # Rediriger stderr vers stdout
        )
        
        stdout_lines = []
        stderr_lines = []
        
        # Lire la sortie en temps réel
        if process.stdout:
            while True:
                line_bytes = await process.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode('utf-8', errors='replace').strip()
                if line:  # Ignorer les lignes vides
                    stdout_lines.append(line)
                    if on_output:
                        # Le callback est synchrone mais peut être appelé depuis async
                        try:
                            on_output(line)
                        except Exception as e:
                            print(f"Erreur dans on_output callback: {e}")
        
        # Attendre la fin du processus
        return_code = await process.wait()
        
        # Lire stderr si disponible (normalement vide car redirigé vers stdout)
        if process.stderr:
            stderr_content_bytes = await process.stderr.read()
            if stderr_content_bytes:
                stderr_content = stderr_content_bytes.decode('utf-8', errors='replace')
                stderr_lines = stderr_content.strip().split('\n')
        
        # Log le résultat pour debug
        if return_code != 0:
            print(f"[GreaseweazleExecutor] Commande échouée (code {return_code})")
            if stdout_lines:
                print(f"[GreaseweazleExecutor] stdout: {stdout_lines[-5:]}")  # Dernières 5 lignes
            if stderr_lines:
                print(f"[GreaseweazleExecutor] stderr: {stderr_lines[-5:]}")
        
        return subprocess.CompletedProcess(
            cmd,
            return_code,
            "\n".join(stdout_lines),
            "\n".join(stderr_lines) if stderr_lines else ""
        )
    
    async def run_align(
        self,
        cylinders: int = 80,
        retries: int = 3,
        format_type: str = "ibm.1440",
        diskdefs_path: Optional[str] = None,
        on_output: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Exécute la commande align
        
        IMPORTANT: gw align exige que toutes les pistes soient sur le même cylindre.
        On teste donc un cylindre à la fois, en boucle.
        
        Args:
            cylinders: Nombre de cylindres à tester
            retries: Nombre de tentatives par piste
            format_type: Format de disquette (ex: "ibm.1440", "ibm.720")
            diskdefs_path: Chemin vers diskdefs.cfg (optionnel)
            on_output: Callback pour chaque ligne de sortie
        """
        all_stdout = []
        all_stderr = []
        return_code = 0
        
        # Tester chaque cylindre séparément (gw align ne peut tester qu'un seul cylindre à la fois)
        for cyl in range(cylinders):
            # Pour chaque cylindre, tester les deux têtes (0 et 1)
            tracks_spec = f"c={cyl}:h=0,1"
            
            # --reads correspond au nombre de tentatives (retries)
            # --format permet de décoder les secteurs (nécessaire pour calculer les pourcentages)
            args = [
                "align",
                f"--tracks={tracks_spec}",
                f"--reads={retries}",
                f"--format={format_type}"
            ]
            
            # Ajouter --diskdefs si spécifié et accessible
            if diskdefs_path:
                try:
                    diskdefs_file = Path(diskdefs_path)
                    if diskdefs_file.exists() and diskdefs_file.is_file():
                        # Vérifier qu'on peut lire le fichier
                        try:
                            with open(diskdefs_file, 'r') as f:
                                f.read(1)  # Lire un octet pour vérifier les permissions
                            args.append(f"--diskdefs={diskdefs_path}")
                        except PermissionError:
                            print(f"[GreaseweazleExecutor] Permission refusée pour diskdefs.cfg: {diskdefs_path}, gw utilisera le fichier par défaut")
                        except Exception as e:
                            print(f"[GreaseweazleExecutor] Erreur vérification diskdefs: {e}, gw utilisera le fichier par défaut")
                    else:
                        print(f"[GreaseweazleExecutor] diskdefs.cfg non trouvé: {diskdefs_path}, gw utilisera le fichier par défaut")
                except Exception as e:
                    print(f"[GreaseweazleExecutor] Erreur vérification diskdefs: {e}, gw utilisera le fichier par défaut")
            
            result = await self.run_command(args, on_output=on_output)
            
            # Accumuler les sorties
            if result.stdout:
                all_stdout.append(result.stdout)
            if result.stderr:
                all_stderr.append(result.stderr)
            
            # Si une commande échoue, on continue mais on note l'erreur
            if result.returncode != 0:
                return_code = result.returncode
                # Ne pas arrêter complètement, continuer avec les autres cylindres
        
        return {
            "returncode": return_code,
            "stdout": "\n".join(all_stdout),
            "stderr": "\n".join(all_stderr),
            "success": return_code == 0
        }
    
    def check_version(self) -> Optional[str]:
        """Vérifie la version de Greaseweazle (host tools)"""
        try:
            result = subprocess.run(
                [self.gw_path, "--version"],
                capture_output=True,
                text=True,
                timeout=2  # Timeout réduit pour éviter de bloquer
            )
            if result.returncode == 0:
                # Extraire la version des host tools (première ligne)
                # La sortie peut être dans stdout ou stderr
                output = result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
                lines = output.split('\n')
                for line in lines:
                    if line.startswith('Host Tools:'):
                        return line.split(':', 1)[1].strip()
                # Si pas de ligne "Host Tools:", retourner la première ligne
                if output:
                    return output.split('\n')[0].strip()
        except subprocess.TimeoutExpired:
            # Timeout = gw.exe ne répond pas (peut-être pas accessible depuis WSL)
            pass
        except Exception as e:
            # Erreur silencieuse pour ne pas polluer les logs
            pass
        return None
    
    def get_device_info(self) -> Optional[Dict]:
        """
        Récupère les informations détaillées du device Greaseweazle
        Retourne un dictionnaire avec port, model, firmware, etc.
        
        OPTIMISATION: Timeout adaptatif selon la plateforme (WSL plus lent)
        """
        try:
            # Utiliser la commande 'info' pour obtenir les infos du device
            # Note: gw.exe envoie la sortie dans stderr, pas stdout
            # Timeout plus long pour WSL qui doit exécuter un exécutable Windows
            timeout = 5 if self._is_wsl() else 2
            
            result = subprocess.run(
                [self.gw_path, "info"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            # Accepter returncode 0 ou 1 (1 peut être dû à des warnings non bloquants comme "GitHub API Rate Limit")
            if result.returncode in [0, 1]:
                # La sortie peut être dans stdout ou stderr selon la version
                output = result.stdout if result.stdout.strip() else result.stderr
                # Filtrer les messages d'erreur non bloquants (GitHub API Rate Limit, etc.)
                filtered_output = self._filter_non_critical_errors(output)
                return self._parse_device_info(filtered_output)
            else:
                # Si la commande échoue, le device n'est probablement pas connecté
                return {
                    "port": None,
                    "model": None,
                    "mcu": None,
                    "firmware": None,
                    "serial": None,
                    "usb": None,
                    "connected": False,
                    "error": result.stderr.strip() if result.stderr else "Device non connecté"
                }
        except subprocess.TimeoutExpired:
            # Timeout = Greaseweazle non connecté ou non accessible
            return {
                "port": None,
                "model": None,
                "mcu": None,
                "firmware": None,
                "serial": None,
                "usb": None,
                "connected": False,
                "error": "Timeout: Greaseweazle non accessible (vérifiez la connexion USB)"
            }
        except Exception as e:
            # Erreur silencieuse pour ne pas polluer les logs
            return {
                "port": None,
                "model": None,
                "mcu": None,
                "firmware": None,
                "serial": None,
                "usb": None,
                "connected": False,
                "error": f"Erreur: {str(e)}"
            }
    
    def _filter_non_critical_errors(self, output: str) -> str:
        """
        Filtre les messages d'erreur non bloquants de la sortie
        (ex: GitHub API Rate Limit exceeded)
        """
        lines = output.split('\n')
        filtered_lines = []
        skip_next = False
        
        for line in lines:
            # Ignorer les lignes contenant des erreurs non bloquantes
            if 'FATAL ERROR' in line and 'Rate Limit' in line:
                skip_next = True
                continue
            if skip_next and line.strip() == '':
                skip_next = False
                continue
            if not skip_next:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _parse_device_info(self, output: str) -> Dict:
        """Parse les informations du device depuis la sortie de gw info"""
        info = {
            "port": None,
            "model": None,
            "mcu": None,
            "firmware": None,
            "serial": None,
            "usb": None,
            "connected": False
        }
        
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ignorer les warnings et lignes non pertinentes
            if line.startswith('***') or line.startswith('Host Tools:'):
                continue
            
            # Format: "  Port:     COM10" ou "Port: COM10"
            # Gérer les deux formats
            if 'Port:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    info["port"] = parts[1].strip()
                    info["connected"] = True
            elif 'Model:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    info["model"] = parts[1].strip()
            elif 'MCU:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    info["mcu"] = parts[1].strip()
            elif 'Firmware:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    info["firmware"] = parts[1].strip()
            elif 'Serial:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    info["serial"] = parts[1].strip()
            elif 'USB:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    info["usb"] = parts[1].strip()
        
        return info
    
    def check_align_available(self) -> bool:
        """Vérifie si la commande align est disponible"""
        try:
            result = subprocess.run(
                [self.gw_path, "align", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def detect_gw_path_auto(self) -> Dict:
        """
        Détecte automatiquement gw.exe dans tous les emplacements possibles
        Retourne un dictionnaire avec les informations de détection
        """
        found_paths = []
        all_paths_checked = []
        
        # D'abord, vérifier si un chemin est sauvegardé dans les settings
        saved_path = settings_manager.get_gw_path()
        if saved_path:
            try:
                normalized = normalize_gw_path(saved_path, validate=False)
                path_obj = Path(normalized)
                if path_obj.exists():
                    return {
                        "found": True,
                        "path": str(path_obj.resolve()),
                        "source": "saved_settings",
                        "all_paths_checked": [str(path_obj.resolve())]
                    }
            except (ValueError, OSError):
                pass
        
        # Détection automatique - utiliser la même logique que _detect_gw_path()
        search_paths = []
        
        if self.platform == "Windows":
            # 1. Répertoire de l'exécutable (standalone)
            if getattr(sys, 'frozen', False):
                exe_dir = Path(sys.executable).parent
                search_paths.extend([
                    exe_dir / "gw.exe",
                    exe_dir / "greaseweazle" / "gw.exe",
                    exe_dir / "greaseweazle-1.23" / "gw.exe",
                    exe_dir.parent / "gw.exe",
                    exe_dir.parent / "greaseweazle" / "gw.exe",
                    exe_dir.parent / "greaseweazle-1.23" / "gw.exe",
                ])
            
            # 2. Répertoire courant
            search_paths.extend([
                Path("gw.exe"),
                Path.cwd() / "gw.exe",
            ])
            
            # 3. Emplacements Windows communs
            search_paths.extend([
                Path("C:/Program Files/Greaseweazle/gw.exe"),
                Path("C:/Program Files (x86)/Greaseweazle/gw.exe"),
                Path.home() / "AppData/Local/Greaseweazle/gw.exe",
            ])
            
            # 4. Chercher dans le PATH
            gw_in_path = shutil.which("gw.exe")
            if gw_in_path:
                search_paths.append(Path(gw_in_path))
        else:
            # Linux/WSL
            if self._is_wsl():
                search_paths.extend([
                    Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23b/gw.exe"),
                    Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23/gw.exe"),
                    Path("/mnt/c/Program Files/Greaseweazle/gw.exe"),
                    Path("/mnt/c/Program Files (x86)/Greaseweazle/gw.exe"),
                ])
            
            # Chercher gw dans PATH
            gw_in_path = shutil.which("gw")
            if gw_in_path:
                search_paths.append(Path(gw_in_path))
        
        # Vérifier tous les chemins
        for gw_path in search_paths:
            all_paths_checked.append(str(gw_path))
            try:
                if gw_path.exists():
                    abs_path = str(gw_path.resolve())
                    found_paths.append(abs_path)
            except (OSError, ValueError):
                pass
        
        if found_paths:
            return {
                "found": True,
                "path": found_paths[0],
                "source": "auto_detection",
                "all_paths_checked": all_paths_checked,
                "all_paths_found": found_paths
            }
        else:
            return {
                "found": False,
                "path": None,
                "source": "auto_detection",
                "error": "Aucun exécutable gw.exe/gw trouvé",
                "all_paths_checked": all_paths_checked
            }
    
    def detect_serial_ports(self) -> List[Dict]:
        """
        Détecte les ports série disponibles (Windows/Linux/WSL)
        Retourne une liste de dictionnaires avec les informations des ports
        """
        ports = []
        
        if SERIAL_AVAILABLE:
            # Utiliser pyserial pour une détection fiable
            try:
                for port in list_ports.comports():
                    port_info = {
                        "device": port.device,
                        "description": port.description,
                        "manufacturer": port.manufacturer,
                        "product": port.product,
                        "serial_number": port.serial_number,
                        "vid": hex(port.vid) if port.vid else None,
                        "pid": hex(port.pid) if port.pid else None,
                    }
                    
                    # Vérifier si c'est potentiellement un Greaseweazle
                    is_greaseweazle = (
                        (port.vid == 0x1209 and port.pid == 0x4d69) or  # PID officiel
                        (port.vid == 0x1209 and port.pid == 0x0001) or  # Ancien PID partagé
                        (port.manufacturer == "Keir Fraser" and port.product == "Greaseweazle") or
                        (port.product and "greaseweazle" in port.product.lower()) or
                        (port.serial_number and port.serial_number.upper().startswith("GW"))
                    )
                    port_info["is_greaseweazle"] = is_greaseweazle
                    ports.append(port_info)
            except Exception as e:
                print(f"Erreur lors de la détection avec pyserial: {e}")
        
        # Fallback : détection manuelle selon la plateforme
        if not ports:
            if self.platform == "Windows":
                # Sur Windows, chercher les ports COM
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
                    i = 0
                    while True:
                        try:
                            port_name, port_value, _ = winreg.EnumValue(key, i)
                            ports.append({
                                "device": port_value,
                                "description": port_name,
                                "manufacturer": None,
                                "product": None,
                                "serial_number": None,
                                "vid": None,
                                "pid": None,
                                "is_greaseweazle": False  # Impossible à déterminer sans pyserial
                            })
                            i += 1
                        except (WindowsError, OSError):
                            break
                    winreg.CloseKey(key)
                except ImportError:
                    # winreg non disponible (pas sur Windows)
                    pass
                except Exception as e:
                    print(f"Erreur lors de la détection Windows: {e}")
            else:
                # Linux/WSL : chercher dans /dev
                patterns = ["/dev/ttyACM*", "/dev/ttyUSB*", "/dev/tty.usbmodem*"]
                for pattern in patterns:
                    for device in glob.glob(pattern):
                        try:
                            # Vérifier que c'est un fichier de périphérique
                            if os.path.exists(device):
                                ports.append({
                                    "device": device,
                                    "description": f"USB Serial Device ({device})",
                                    "manufacturer": None,
                                    "product": None,
                                    "serial_number": None,
                                    "vid": None,
                                    "pid": None,
                                    "is_greaseweazle": False  # Impossible à déterminer sans pyserial
                                })
                        except Exception:
                            pass
        
        return ports
    
    def detect_greaseweazle_port(self) -> Optional[Dict]:
        """
        Détecte automatiquement le port série de Greaseweazle
        Retourne les informations du port si trouvé, None sinon
        
        OPTIMISATION: 
        - Teste d'abord le dernier port utilisé avec succès (rapide)
        - Puis utilise gw info directement (sans tester tous les ports)
        """
        # 1. Essayer d'abord le dernier port sauvegardé (très rapide)
        last_port = settings_manager.get_last_port()
        if last_port:
            # Vérifier si ce port existe toujours dans la liste
            ports = self.detect_serial_ports()
            for port in ports:
                if port.get("device") == last_port:
                    # Tester rapidement si c'est toujours un Greaseweazle
                    try:
                        result = subprocess.run(
                            [self.gw_path, "--device", last_port, "info"],
                            capture_output=True,
                            text=True,
                            timeout=1  # Timeout très court pour le port connu
                        )
                        if result.returncode == 0:
                            # C'est toujours le bon port !
                            port["is_greaseweazle"] = True
                            return port
                    except Exception:
                        # Le port sauvegardé ne fonctionne plus, continuer
                        pass
        
        # 2. Chercher un port qui correspond à Greaseweazle via pyserial
        ports = self.detect_serial_ports()
        for port in ports:
            if port.get("is_greaseweazle", False):
                # Sauvegarder ce port pour la prochaine fois
                if port.get("device"):
                    settings_manager.set_last_port(port.get("device"))
                return port
        
        # 3. Si pyserial n'a pas trouvé, utiliser gw info directement (sans tester chaque port)
        # gw.exe détecte automatiquement le bon port, pas besoin de tester tous les ports
        # C'est beaucoup plus rapide et ne bloque pas l'event loop
        try:
            timeout = 5 if self._is_wsl() else 2
            result = subprocess.run(
                [self.gw_path, "info"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                # Greaseweazle est connecté, récupérer le port depuis les infos
                output = result.stdout if result.stdout.strip() else result.stderr
                device_info = self._parse_device_info(output)
                if device_info.get("connected") and device_info.get("port"):
                    # Sauvegarder le port pour la prochaine fois
                    settings_manager.set_last_port(device_info.get("port"))
                    
                    # Retourner un port fictif avec les infos réelles
                    return {
                        "device": device_info.get("port"),
                        "description": f"Greaseweazle {device_info.get('model', 'Device')}",
                        "manufacturer": "Keir Fraser",
                        "product": "Greaseweazle",
                        "serial_number": device_info.get("serial"),
                        "vid": "0x1209",
                        "pid": "0x4d69",
                        "is_greaseweazle": True
                    }
        except subprocess.TimeoutExpired:
            # Timeout = Greaseweazle non connecté ou non accessible
            pass
        except Exception:
            # Erreur = Greaseweazle non connecté
            pass
        
        return None
    
    def check_connection(self) -> Dict:
        """
        Vérifie si Greaseweazle est connecté et accessible
        Retourne un dictionnaire avec le statut de connexion
        
        OPTIMISATION: 
        - Teste d'abord le dernier port utilisé (rapide)
        - Puis utilise gw info directement
        """
        result = {
            "connected": False,
            "port": None,
            "device_info": None,
            "error": None,
            "last_port": settings_manager.get_last_port()  # Inclure le port sauvegardé
        }
        
        # Utiliser directement gw info (beaucoup plus rapide que de tester 192 ports)
        # gw.exe détecte automatiquement le bon port
        device_info = self.get_device_info()
        if device_info:
            if device_info.get("connected", False):
                result["connected"] = True
                port = device_info.get("port")
                result["port"] = port
                result["device_info"] = device_info
                
                # Sauvegarder le port pour la prochaine fois
                if port:
                    settings_manager.set_last_port(port)
            else:
                result["error"] = device_info.get("error", "Greaseweazle non détecté")
        else:
            result["error"] = "Impossible de récupérer les informations du device"
        
        return result

