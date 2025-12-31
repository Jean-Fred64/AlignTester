"""
Module de gestion des paramètres utilisateur
Stocke les préférences dans un fichier JSON
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
import os

class SettingsManager:
    """Gestionnaire des paramètres utilisateur"""
    
    def __init__(self, settings_file: Optional[str] = None):
        """
        Initialise le gestionnaire de paramètres
        
        Args:
            settings_file: Chemin vers le fichier de paramètres (optionnel)
        """
        if settings_file:
            self.settings_path = Path(settings_file)
        else:
            # Par défaut, créer dans un dossier data/ à côté du backend
            backend_dir = Path(__file__).parent
            data_dir = backend_dir.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            self.settings_path = data_dir / "settings.json"
        
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Charge les paramètres depuis le fichier"""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement des paramètres: {e}")
                return {}
        return {}
    
    def _save_settings(self):
        """Sauvegarde les paramètres dans le fichier"""
        try:
            # Créer le dossier parent si nécessaire
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de paramètre"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Définit une valeur de paramètre"""
        self._settings[key] = value
        self._save_settings()
    
    def get_last_port(self) -> Optional[str]:
        """Récupère le dernier port COM utilisé avec succès"""
        return self.get("last_port")
    
    def set_last_port(self, port: str):
        """Enregistre le dernier port COM utilisé avec succès"""
        self.set("last_port", port)
        # Enregistrer aussi la date de dernière utilisation
        from datetime import datetime
        self.set("last_port_date", datetime.now().isoformat())
    
    def get_drive(self) -> str:
        """Récupère le lecteur sélectionné (A, B, 0, 1, 2, 3)"""
        return self.get("drive", "A")  # Par défaut: Drive A (PC)
    
    def set_drive(self, drive: str):
        """Enregistre le lecteur sélectionné"""
        # Valider que c'est une valeur valide
        valid_drives = ["A", "B", "0", "1", "2", "3"]
        if drive in valid_drives:
            self.set("drive", drive)
        else:
            raise ValueError(f"Lecteur invalide: {drive}. Valeurs valides: {valid_drives}")
    
    def get_gw_path(self) -> Optional[str]:
        """Récupère le chemin vers gw.exe sauvegardé"""
        return self.get("gw_path")
    
    def set_gw_path(self, gw_path: str):
        """Enregistre le chemin vers gw.exe"""
        # Valider que le fichier existe (si c'est un chemin absolu)
        from pathlib import Path
        path = Path(gw_path)
        if path.is_absolute() and not path.exists():
            raise ValueError(f"Le chemin spécifié n'existe pas: {gw_path}")
        self.set("gw_path", gw_path)
        # Enregistrer aussi la date de dernière modification
        from datetime import datetime
        self.set("gw_path_date", datetime.now().isoformat())
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Récupère tous les paramètres"""
        return self._settings.copy()
    
    def clear(self):
        """Efface tous les paramètres"""
        self._settings = {}
        self._save_settings()

# Instance globale
settings_manager = SettingsManager()

