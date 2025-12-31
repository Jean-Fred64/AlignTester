"""
Parser pour extraire les formats disponibles depuis diskdefs.cfg
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Optional
from .greaseweazle import GreaseweazleExecutor


class DiskDefsParser:
    """Parse les fichiers diskdefs.cfg pour extraire les formats disponibles"""
    
    def __init__(self, executor: Optional[GreaseweazleExecutor] = None):
        self.executor = executor or GreaseweazleExecutor()
        self._formats_cache: Optional[List[Dict[str, str]]] = None
    
    def _find_diskdefs_path(self) -> Optional[Path]:
        """
        Trouve le chemin vers diskdefs.cfg
        Cherche dans le dossier data/ à côté de gw.exe
        Le chemin typique est: <gw_path>/../lib/greaseweazle/data/diskdefs.cfg
        """
        gw_path = Path(self.executor.gw_path)
        
        # Si gw_path est un chemin absolu
        if gw_path.is_absolute():
            # Chercher dans le dossier parent puis data/
            # Pour un exe Windows compilé, la structure est souvent:
            # gw.exe -> lib/greaseweazle/data/diskdefs.cfg
            possible_paths = [
                gw_path.parent / "lib" / "greaseweazle" / "data" / "diskdefs.cfg",
                gw_path.parent / "greaseweazle" / "data" / "diskdefs.cfg",
                gw_path.parent / "data" / "diskdefs.cfg",
                gw_path.parent.parent / "lib" / "greaseweazle" / "data" / "diskdefs.cfg",
            ]
            
            for path in possible_paths:
                if path.exists():
                    return path
        
        # Si c'est juste "gw" ou "gw.exe", chercher dans les chemins standards
        # Pour WSL, le chemin peut être dans /mnt/s/...
        if self.executor._is_wsl():
            possible_paths = [
                Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23b/lib/greaseweazle/data/diskdefs.cfg"),
                Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23/lib/greaseweazle/data/diskdefs.cfg"),
                Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23b/greaseweazle/data/diskdefs.cfg"),
                Path("/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23/greaseweazle/data/diskdefs.cfg"),
                Path("/mnt/c/Program Files/Greaseweazle/lib/greaseweazle/data/diskdefs.cfg"),
            ]
            
            for path in possible_paths:
                if path.exists():
                    return path
        
        # Chercher dans le projet local
        project_paths = [
            Path(__file__).parent.parent.parent / "greaseweazle-1.23b" / "src" / "greaseweazle" / "data" / "diskdefs.cfg",
            Path(__file__).parent.parent.parent / "greaseweazle-1.23" / "src" / "greaseweazle" / "data" / "diskdefs.cfg",
        ]
        
        for path in project_paths:
            if path.exists():
                return path
        
        return None
    
    def get_diskdefs_path(self) -> Optional[str]:
        """Retourne le chemin vers diskdefs.cfg sous forme de string"""
        path = self._find_diskdefs_path()
        return str(path) if path else None
    
    def _parse_diskdefs_file(self, file_path: Path, prefix: str = "") -> List[Dict[str, str]]:
        """
        Parse un fichier diskdefs.cfg et extrait les définitions de formats
        """
        formats = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Chercher "disk <nom>"
                disk_match = re.match(r'disk\s+([a-zA-Z0-9._]+)', line, re.IGNORECASE)
                if disk_match:
                    format_name = disk_match.group(1)
                    
                    # Ajouter le préfixe si nécessaire
                    if prefix:
                        full_name = f"{prefix}.{format_name}"
                    else:
                        full_name = format_name
                    
                    # Lire jusqu'au prochain "end" pour extraire les infos
                    cyls = None
                    heads = None
                    secs = None
                    bps = None
                    gap3 = None
                    rate = None
                    rpm = None
                    track_format = None
                    
                    j = i + 1
                    in_tracks_section = False
                    while j < len(lines):
                        section_line = lines[j].strip()
                        
                        # Chercher cyls
                        cyls_match = re.match(r'cyls\s*=\s*(\d+)', section_line, re.IGNORECASE)
                        if cyls_match:
                            cyls = cyls_match.group(1)
                        
                        # Chercher heads
                        heads_match = re.match(r'heads\s*=\s*(\d+)', section_line, re.IGNORECASE)
                        if heads_match:
                            heads = heads_match.group(1)
                        
                        # Détecter la section tracks (format: "tracks * format" ou "tracks 0-16 format")
                        # Exemples: 
                        #   - "tracks * ibm.mfm" (format avec point)
                        #   - "tracks * apple2.gcr" (format avec point)
                        #   - "tracks 0-16 c64.gcr" (format avec point et plage)
                        #   - "tracks * micropolis" (format sans point)
                        #   - "tracks * northstar" (format sans point)
                        # Pattern flexible pour capturer tous les formats (avec ou sans point)
                        tracks_match = re.search(r'tracks\s+[^\s]+\s+([a-z0-9]+(?:\.[a-z0-9]+)*)', section_line, re.IGNORECASE)
                        if tracks_match:
                            track_format = tracks_match.group(1).lower()
                            in_tracks_section = True
                        
                        # Dans la section tracks, chercher les paramètres
                        if in_tracks_section:
                            # Chercher secs
                            secs_match = re.match(r'secs\s*=\s*(\d+)', section_line, re.IGNORECASE)
                            if secs_match:
                                secs = secs_match.group(1)
                            
                            # Chercher bps
                            bps_match = re.match(r'bps\s*=\s*(\d+)', section_line, re.IGNORECASE)
                            if bps_match:
                                bps = bps_match.group(1)
                            
                            # Chercher gap3
                            gap3_match = re.match(r'gap3\s*=\s*(\d+)', section_line, re.IGNORECASE)
                            if gap3_match:
                                gap3 = gap3_match.group(1)
                            
                            # Chercher rate
                            rate_match = re.match(r'rate\s*=\s*(\d+)', section_line, re.IGNORECASE)
                            if rate_match:
                                rate = rate_match.group(1)
                            
                            # Chercher rpm
                            rpm_match = re.match(r'rpm\s*=\s*(\d+)', section_line, re.IGNORECASE)
                            if rpm_match:
                                rpm = rpm_match.group(1)
                        
                        # Arrêter au prochain "end" ou "disk"
                        if section_line.lower() == 'end':
                            if in_tracks_section:
                                in_tracks_section = False
                            else:
                                break
                        elif section_line.lower().startswith('disk '):
                            break
                        
                        j += 1
                    
                    # Calculer la capacité approximative
                    capacity_kb = None
                    if cyls and heads and secs and bps:
                        try:
                            total_sectors = int(cyls) * int(heads) * int(secs)
                            capacity_bytes = total_sectors * int(bps)
                            capacity_kb = capacity_bytes / 1024
                        except:
                            pass
                    
                    format_info = {
                        "name": full_name,
                        "display_name": full_name.replace('.', ' ').replace('_', ' ').title(),
                        "cyls": cyls,
                        "heads": heads,
                        "secs": secs,
                        "bps": bps,
                        "gap3": gap3,
                        "rate": rate,
                        "rpm": rpm,
                        "track_format": track_format,
                        "capacity_kb": round(capacity_kb) if capacity_kb else None,
                    }
                    
                    formats.append(format_info)
                
                i += 1
        
        except Exception as e:
            print(f"Erreur lors du parsing de {file_path}: {e}")
        
        return formats
    
    def _parse_all_diskdefs(self, main_file: Path) -> List[Dict[str, str]]:
        """
        Parse le fichier principal diskdefs.cfg et tous les fichiers importés
        """
        all_formats = []
        data_dir = main_file.parent
        
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parser le fichier principal (sans préfixe)
            all_formats.extend(self._parse_diskdefs_file(main_file))
            
            # Trouver les imports
            # Format: import <prefix>. "<file>"
            import_pattern = re.compile(r'import\s+([a-zA-Z0-9._]+)\.\s*"([^"]+)"', re.IGNORECASE)
            
            for match in import_pattern.finditer(content):
                prefix = match.group(1)
                imported_file = match.group(2)
                imported_path = data_dir / imported_file
                
                if imported_path.exists():
                    # Parser le fichier importé avec le préfixe
                    imported_formats = self._parse_diskdefs_file(imported_path, prefix=prefix)
                    all_formats.extend(imported_formats)
        
        except Exception as e:
            print(f"Erreur lors du parsing des diskdefs: {e}")
        
        return all_formats
    
    def get_available_formats(self, force_refresh: bool = False) -> List[Dict[str, str]]:
        """
        Retourne la liste des formats disponibles
        Utilise un cache pour éviter de re-parser à chaque fois
        """
        if self._formats_cache is not None and not force_refresh:
            return self._formats_cache
        
        diskdefs_path = self._find_diskdefs_path()
        
        if not diskdefs_path:
            # Formats par défaut si diskdefs.cfg n'est pas trouvé
            self._formats_cache = [
                {"name": "ibm.1440", "display_name": "IBM 1.44MB", "cyls": "80", "heads": "2"},
                {"name": "ibm.1200", "display_name": "IBM 1.2MB", "cyls": "80", "heads": "2"},
                {"name": "ibm.720", "display_name": "IBM 720KB", "cyls": "80", "heads": "2"},
                {"name": "ibm.360", "display_name": "IBM 360KB", "cyls": "40", "heads": "2"},
            ]
            return self._formats_cache
        
        # Parser tous les fichiers
        all_formats = self._parse_all_diskdefs(diskdefs_path)
        
        # Trier avec un ordre personnalisé
        all_formats = self._sort_formats(all_formats)
        
        # Mettre en cache
        self._formats_cache = all_formats
        
        return all_formats
    
    def _sort_formats(self, formats: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Trie les formats avec un ordre personnalisé :
        1. IBM (le plus commun) - 12 formats
        2. Amiga - 2 formats
        3. Apple (apple2, mac) - 5 formats
        4. Commodore - 6 formats
        5. Atari - 2 formats
        6. Atari ST (atarist) - 6 formats
        7. Autres marques par ordre alphabétique (incluant Amstrad CPC/PCW)
        """
        # Ordre de priorité des préfixes (plus le nombre est petit, plus c'est prioritaire)
        prefix_order = {
            'ibm': 1,           # IBM - le plus commun
            'amiga': 2,         # Amiga
            'apple2': 3,        # Apple II
            'mac': 3,           # Apple Macintosh
            'commodore': 4,     # Commodore
            'atari': 5,         # Atari (8-bit)
            'atarist': 6,       # Atari ST (16-bit)
            # Tous les autres en ordre alphabétique (priorité 1000+)
        }
        
        def get_sort_key(format_info: Dict[str, str]) -> tuple:
            """Retourne une clé de tri pour un format"""
            name = format_info["name"]
            
            # Extraire le préfixe (partie avant le premier point)
            if '.' in name:
                prefix = name.split('.')[0].lower()
            else:
                prefix = name.lower()
            
            # Obtenir l'ordre du préfixe (1000+ pour les non-prioritaires = ordre alphabétique)
            prefix_priority = prefix_order.get(prefix, 1000)
            
            # Si le préfixe n'est pas dans la liste prioritaire, utiliser l'ordre alphabétique
            if prefix_priority >= 1000:
                # Pour les non-prioritaires, trier par préfixe puis par nom
                return (prefix_priority, prefix, name)
            else:
                # Pour les prioritaires, trier par priorité puis par nom
                return (prefix_priority, name)
        
        # Trier les formats
        sorted_formats = sorted(formats, key=get_sort_key)
        
        return sorted_formats
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, str]]:
        """Retourne les informations sur un format spécifique"""
        formats = self.get_available_formats()
        for fmt in formats:
            if fmt["name"] == format_name:
                return fmt
        return None


# Instance globale
_diskdefs_parser_instance: Optional[DiskDefsParser] = None


def get_diskdefs_parser() -> DiskDefsParser:
    """Retourne l'instance globale du parser diskdefs"""
    global _diskdefs_parser_instance
    if _diskdefs_parser_instance is None:
        _diskdefs_parser_instance = DiskDefsParser()
    return _diskdefs_parser_instance

