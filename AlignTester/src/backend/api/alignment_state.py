"""
Gestion de l'état de l'alignement
"""

from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

class AlignmentStatus(Enum):
    """Statut de l'alignement"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class AlignmentState:
    """État actuel de l'alignement"""
    status: AlignmentStatus = AlignmentStatus.IDLE
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    cylinders: int = 80
    retries: int = 3
    current_cylinder: Optional[int] = None
    progress_percentage: float = 0.0
    values: List[Dict] = field(default_factory=list)
    statistics: Optional[Dict] = None
    error_message: Optional[str] = None
    process_task: Optional[asyncio.Task] = None
    
    def to_dict(self) -> Dict:
        """Convertit l'état en dictionnaire pour la sérialisation"""
        return {
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "cylinders": self.cylinders,
            "retries": self.retries,
            "current_cylinder": self.current_cylinder,
            "progress_percentage": self.progress_percentage,
            "values_count": len(self.values),
            "statistics": self.statistics,
            "error_message": self.error_message
        }

class AlignmentStateManager:
    """Gestionnaire de l'état global de l'alignement"""
    
    def __init__(self):
        self._state = AlignmentState()
        self._lock = asyncio.Lock()
    
    async def get_state(self) -> AlignmentState:
        """Récupère l'état actuel"""
        async with self._lock:
            return self._state
    
    async def update_state(self, **kwargs):
        """Met à jour l'état"""
        async with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._state, key):
                    setattr(self._state, key, value)
    
    async def reset_state(self):
        """Réinitialise l'état"""
        async with self._lock:
            # Annuler le processus en cours si existe
            if self._state.process_task and not self._state.process_task.done():
                self._state.process_task.cancel()
            
            self._state = AlignmentState()
    
    async def start_alignment(self, cylinders: int, retries: int, process_task: asyncio.Task):
        """Démarre un nouvel alignement"""
        async with self._lock:
            self._state.status = AlignmentStatus.RUNNING
            self._state.start_time = datetime.now()
            self._state.cylinders = cylinders
            self._state.retries = retries
            self._state.process_task = process_task
            self._state.values = []
            self._state.statistics = None
            self._state.error_message = None
            self._state.progress_percentage = 0.0
    
    async def add_value(self, value: Dict):
        """Ajoute une valeur d'alignement"""
        async with self._lock:
            self._state.values.append(value)
            # Mettre à jour le pourcentage de progression
            if self._state.cylinders > 0:
                self._state.progress_percentage = min(
                    (len(self._state.values) / (self._state.cylinders * 2)) * 100,
                    100.0
                )
    
    async def complete_alignment(self, statistics: Dict):
        """Marque l'alignement comme terminé"""
        async with self._lock:
            self._state.status = AlignmentStatus.COMPLETED
            self._state.end_time = datetime.now()
            self._state.statistics = statistics
            self._state.progress_percentage = 100.0
    
    async def set_error(self, error_message: str):
        """Marque l'alignement comme erreur"""
        async with self._lock:
            self._state.status = AlignmentStatus.ERROR
            self._state.end_time = datetime.now()
            self._state.error_message = error_message
    
    async def cancel_alignment(self):
        """Annule l'alignement en cours"""
        async with self._lock:
            if self._state.process_task and not self._state.process_task.done():
                self._state.process_task.cancel()
            self._state.status = AlignmentStatus.CANCELLED
            self._state.end_time = datetime.now()

# Instance globale
alignment_state_manager = AlignmentStateManager()

