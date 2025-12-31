"""
Tests d'intégration pour l'API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
from pathlib import Path

# Ajouter le chemin du backend
BACKEND_DIR = Path(__file__).parent.parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from main import app


@pytest.fixture
def client():
    """Client de test pour l'API"""
    return TestClient(app)


class TestHealthCheck:
    """Tests pour le health check"""
    
    def test_health_check(self, client):
        """Test du health check"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data


class TestInfoEndpoint:
    """Tests pour l'endpoint /api/info"""
    
    @patch('api.routes.executor.check_version')
    @patch('api.routes.executor.check_align_available')
    @patch('platform.system')
    def test_get_info(self, mock_platform, mock_align, mock_version, client):
        """Test récupération des informations"""
        mock_platform.return_value = "Linux"
        mock_version.return_value = "Greaseweazle 1.0.0"
        mock_align.return_value = True
        
        response = client.get("/api/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "Linux"
        assert data["version"] == "Greaseweazle 1.0.0"
        assert data["align_available"] is True
    
    @patch('api.routes.executor.check_version')
    @patch('api.routes.executor.check_align_available')
    def test_get_info_no_version(self, mock_align, mock_version, client):
        """Test récupération des informations sans version"""
        mock_version.return_value = None
        mock_align.return_value = False
        
        response = client.get("/api/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] is None
        assert data["align_available"] is False


class TestAlignEndpoint:
    """Tests pour l'endpoint /api/align"""
    
    @patch('api.routes.run_alignment_task')
    @patch('api.routes.alignment_state_manager')
    @patch('api.routes.executor.check_align_available')
    def test_start_alignment_success(
        self, mock_align_available, mock_state_manager, mock_run_task, client
    ):
        """Test démarrage d'un alignement - succès"""
        from api.alignment_state import AlignmentStatus
        
        mock_align_available.return_value = True
        
        # Mock de l'état
        mock_state = AsyncMock()
        mock_state.status = AlignmentStatus.IDLE
        mock_state_manager.get_state = AsyncMock(return_value=mock_state)
        mock_state_manager.start_alignment = AsyncMock()
        
        # Mock de la tâche
        mock_task = AsyncMock()
        import asyncio
        with patch('asyncio.create_task', return_value=mock_task):
            response = client.post(
                "/api/align",
                json={"cylinders": 80, "retries": 3}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["cylinders"] == 80
        assert data["retries"] == 3
    
    @patch('api.routes.executor.check_align_available')
    def test_start_alignment_not_available(self, mock_align_available, client):
        """Test démarrage - align non disponible"""
        mock_align_available.return_value = False
        
        response = client.post(
            "/api/align",
            json={"cylinders": 80, "retries": 3}
        )
        
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "disponible" in detail or "non disponible" in detail
    
    @patch('api.routes.alignment_state_manager')
    def test_start_alignment_already_running(self, mock_state_manager, client):
        """Test démarrage - alignement déjà en cours"""
        from api.alignment_state import AlignmentStatus
        
        mock_state = AsyncMock()
        mock_state.status = AlignmentStatus.RUNNING
        mock_state_manager.get_state = AsyncMock(return_value=mock_state)
        
        response = client.post(
            "/api/align",
            json={"cylinders": 80, "retries": 3}
        )
        
        assert response.status_code == 400
        assert "déjà en cours" in response.json()["detail"].lower()
    
    @patch('api.routes.run_alignment_task')
    @patch('api.routes.alignment_state_manager')
    @patch('api.routes.executor.check_align_available')
    def test_start_alignment_default_params(
        self, mock_align_available, mock_state_manager, mock_run_task, client
    ):
        """Test démarrage avec paramètres par défaut"""
        from api.alignment_state import AlignmentStatus
        
        mock_align_available.return_value = True
        mock_state = AsyncMock()
        mock_state.status = AlignmentStatus.IDLE
        mock_state_manager.get_state = AsyncMock(return_value=mock_state)
        mock_state_manager.start_alignment = AsyncMock()
        
        import asyncio
        with patch('asyncio.create_task', return_value=AsyncMock()):
            response = client.post("/api/align", json={})
        
        # Devrait utiliser les valeurs par défaut (cylinders=80, retries=3)
        assert response.status_code == 200
        data = response.json()
        assert data["cylinders"] == 80
        assert data["retries"] == 3


class TestStatusEndpoint:
    """Tests pour l'endpoint /api/status"""
    
    @patch('api.routes.alignment_state_manager')
    def test_get_status_idle(self, mock_state_manager, client):
        """Test récupération du statut - idle"""
        from api.alignment_state import AlignmentState, AlignmentStatus
        
        mock_state = AlignmentState()
        mock_state.status = AlignmentStatus.IDLE
        mock_state_manager.get_state = AsyncMock(return_value=mock_state)
        
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "idle"
    
    @patch('api.routes.alignment_state_manager')
    def test_get_status_running(self, mock_state_manager, client):
        """Test récupération du statut - running"""
        from api.alignment_state import AlignmentState, AlignmentStatus
        from datetime import datetime
        
        mock_state = AlignmentState()
        mock_state.status = AlignmentStatus.RUNNING
        mock_state.start_time = datetime.now()
        mock_state.cylinders = 80
        mock_state.retries = 3
        mock_state.progress_percentage = 45.5
        mock_state.values = [{"track": "00.0", "percentage": 99.911}]
        
        mock_state_manager.get_state = AsyncMock(return_value=mock_state)
        
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["cylinders"] == 80
        assert data["progress_percentage"] == 45.5
        assert data["values_count"] == 1


class TestCancelEndpoint:
    """Tests pour l'endpoint /api/align/cancel"""
    
    @patch('api.routes.alignment_state_manager')
    def test_cancel_alignment_success(self, mock_state_manager, client):
        """Test annulation - succès"""
        from api.alignment_state import AlignmentState, AlignmentStatus
        
        mock_state = AlignmentState()
        mock_state.status = AlignmentStatus.RUNNING
        mock_state_manager.get_state = AsyncMock(return_value=mock_state)
        mock_state_manager.cancel_alignment = AsyncMock()
        
        response = client.post("/api/align/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
    
    @patch('api.routes.alignment_state_manager')
    def test_cancel_alignment_not_running(self, mock_state_manager, client):
        """Test annulation - pas d'alignement en cours"""
        from api.alignment_state import AlignmentState, AlignmentStatus
        
        mock_state = AlignmentState()
        mock_state.status = AlignmentStatus.IDLE
        mock_state_manager.get_state = AsyncMock(return_value=mock_state)
        
        response = client.post("/api/align/cancel")
        
        assert response.status_code == 400
        assert "aucun alignement" in response.json()["detail"].lower()

