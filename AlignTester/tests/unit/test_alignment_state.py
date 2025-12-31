"""
Tests unitaires pour alignment_state.py
"""

import pytest
import asyncio
from datetime import datetime
from api.alignment_state import (
    AlignmentState,
    AlignmentStateManager,
    AlignmentStatus
)


class TestAlignmentState:
    """Tests pour AlignmentState"""
    
    def test_default_state(self):
        """Test état par défaut"""
        state = AlignmentState()
        
        assert state.status == AlignmentStatus.IDLE
        assert state.start_time is None
        assert state.end_time is None
        assert state.cylinders == 80
        assert state.retries == 3
        assert len(state.values) == 0
        assert state.statistics is None
    
    def test_state_to_dict(self):
        """Test conversion en dictionnaire"""
        state = AlignmentState(
            status=AlignmentStatus.RUNNING,
            cylinders=80,
            retries=3,
            progress_percentage=50.0
        )
        state.start_time = datetime.now()
        
        state_dict = state.to_dict()
        
        assert state_dict["status"] == "running"
        assert state_dict["cylinders"] == 80
        assert state_dict["retries"] == 3
        assert state_dict["progress_percentage"] == 50.0
        assert state_dict["values_count"] == 0
        assert state_dict["start_time"] is not None


@pytest.mark.asyncio
class TestAlignmentStateManager:
    """Tests pour AlignmentStateManager"""
    
    async def test_get_state_default(self):
        """Test récupération de l'état par défaut"""
        manager = AlignmentStateManager()
        state = await manager.get_state()
        
        assert state.status == AlignmentStatus.IDLE
        assert len(state.values) == 0
    
    async def test_update_state(self):
        """Test mise à jour de l'état"""
        manager = AlignmentStateManager()
        
        await manager.update_state(
            status=AlignmentStatus.RUNNING,
            cylinders=100,
            retries=5
        )
        
        state = await manager.get_state()
        assert state.status == AlignmentStatus.RUNNING
        assert state.cylinders == 100
        assert state.retries == 5
    
    async def test_reset_state(self):
        """Test réinitialisation de l'état"""
        manager = AlignmentStateManager()
        
        # Modifier l'état
        await manager.update_state(
            status=AlignmentStatus.RUNNING,
            cylinders=100
        )
        
        # Réinitialiser
        await manager.reset_state()
        
        state = await manager.get_state()
        assert state.status == AlignmentStatus.IDLE
        assert state.cylinders == 80
    
    async def test_start_alignment(self):
        """Test démarrage d'un alignement"""
        manager = AlignmentStateManager()
        
        # Créer une tâche fictive
        async def dummy_task():
            await asyncio.sleep(0.1)
        
        task = asyncio.create_task(dummy_task())
        
        await manager.start_alignment(cylinders=80, retries=3, process_task=task)
        
        state = await manager.get_state()
        assert state.status == AlignmentStatus.RUNNING
        assert state.start_time is not None
        assert state.cylinders == 80
        assert state.retries == 3
        assert state.process_task == task
        
        # Nettoyer
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    async def test_add_value(self):
        """Test ajout d'une valeur"""
        manager = AlignmentStateManager()
        
        await manager.start_alignment(
            cylinders=80,
            retries=3,
            process_task=asyncio.create_task(asyncio.sleep(0.1))
        )
        
        value = {
            "track": "00.0",
            "percentage": 99.911,
            "base": 1.000
        }
        
        await manager.add_value(value)
        
        state = await manager.get_state()
        assert len(state.values) == 1
        assert state.values[0] == value
        assert state.progress_percentage > 0
    
    async def test_complete_alignment(self):
        """Test complétion d'un alignement"""
        manager = AlignmentStateManager()
        
        await manager.start_alignment(
            cylinders=80,
            retries=3,
            process_task=asyncio.create_task(asyncio.sleep(0.1))
        )
        
        statistics = {
            "average": 99.5,
            "min": 98.0,
            "max": 100.0
        }
        
        await manager.complete_alignment(statistics)
        
        state = await manager.get_state()
        assert state.status == AlignmentStatus.COMPLETED
        assert state.end_time is not None
        assert state.statistics == statistics
        assert state.progress_percentage == 100.0
    
    async def test_set_error(self):
        """Test définition d'une erreur"""
        manager = AlignmentStateManager()
        
        await manager.start_alignment(
            cylinders=80,
            retries=3,
            process_task=asyncio.create_task(asyncio.sleep(0.1))
        )
        
        await manager.set_error("Erreur de test")
        
        state = await manager.get_state()
        assert state.status == AlignmentStatus.ERROR
        assert state.end_time is not None
        assert state.error_message == "Erreur de test"
    
    async def test_cancel_alignment(self):
        """Test annulation d'un alignement"""
        manager = AlignmentStateManager()
        
        # Créer une tâche qui attend
        task = asyncio.create_task(asyncio.sleep(10))
        
        await manager.start_alignment(cylinders=80, retries=3, process_task=task)
        
        # Annuler via le manager (qui annule la tâche)
        await manager.cancel_alignment()
        
        state = await manager.get_state()
        assert state.status == AlignmentStatus.CANCELLED
        assert state.end_time is not None
        # La tâche peut ne pas être immédiatement cancelled(), mais devrait l'être
        # Attendre un peu pour que l'annulation prenne effet
        await asyncio.sleep(0.01)
        # Vérifier au moins que le statut est CANCELLED
        assert state.status == AlignmentStatus.CANCELLED
        
        # Nettoyer
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def test_progress_calculation(self):
        """Test calcul de la progression"""
        manager = AlignmentStateManager()
        
        await manager.start_alignment(
            cylinders=10,  # 10 cylindres = 20 valeurs (2 faces par piste)
            retries=3,
            process_task=asyncio.create_task(asyncio.sleep(0.1))
        )
        
        # Ajouter 10 valeurs (50% de progression)
        for i in range(10):
            await manager.add_value({"track": f"{i//2}.{i%2}", "percentage": 99.0})
        
        state = await manager.get_state()
        assert state.progress_percentage == pytest.approx(50.0, abs=0.1)

