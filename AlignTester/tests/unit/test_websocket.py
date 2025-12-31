"""
Tests unitaires pour websocket.py
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from api.websocket import ConnectionManager, websocket_manager


@pytest.mark.asyncio
class TestConnectionManager:
    """Tests pour ConnectionManager"""
    
    async def test_connect(self):
        """Test connexion d'un WebSocket"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        
        assert websocket in manager.active_connections
        assert len(manager.active_connections) == 1
        websocket.accept.assert_called_once()
    
    async def test_disconnect(self):
        """Test déconnexion d'un WebSocket"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        assert len(manager.active_connections) == 1
        
        manager.disconnect(websocket)
        assert websocket not in manager.active_connections
        assert len(manager.active_connections) == 0
    
    async def test_disconnect_not_connected(self):
        """Test déconnexion d'un WebSocket non connecté"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        # Ne devrait pas lever d'erreur
        manager.disconnect(websocket)
        assert len(manager.active_connections) == 0
    
    async def test_send_personal_message(self):
        """Test envoi de message personnel"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        await manager.send_personal_message("Test message", websocket)
        
        websocket.send_text.assert_called_once_with("Test message")
    
    async def test_send_personal_message_error(self):
        """Test envoi de message avec erreur"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        websocket.send_text = AsyncMock(side_effect=Exception("Send error"))
        
        await manager.connect(websocket)
        await manager.send_personal_message("Test", websocket)
        
        # Le WebSocket devrait être déconnecté en cas d'erreur
        assert websocket not in manager.active_connections
    
    async def test_broadcast(self):
        """Test diffusion à tous les clients"""
        manager = ConnectionManager()
        
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        
        await manager.connect(websocket1)
        await manager.connect(websocket2)
        
        message = {"type": "test", "data": "value"}
        await manager.broadcast(message)
        
        # Vérifier que les deux WebSockets ont reçu le message
        assert websocket1.send_text.call_count == 1
        assert websocket2.send_text.call_count == 1
        
        # Vérifier le contenu du message (JSON stringifié)
        call_args1 = websocket1.send_text.call_args[0][0]
        assert json.loads(call_args1) == message
    
    async def test_broadcast_with_disconnected(self):
        """Test diffusion avec des clients déconnectés"""
        manager = ConnectionManager()
        
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        websocket2.send_text = AsyncMock(side_effect=Exception("Disconnected"))
        
        await manager.connect(websocket1)
        await manager.connect(websocket2)
        
        message = {"type": "test"}
        await manager.broadcast(message)
        
        # websocket1 devrait recevoir le message
        assert websocket1.send_text.call_count == 1
        
        # websocket2 devrait être retiré des connexions actives
        assert websocket2 not in manager.active_connections
    
    async def test_send_alignment_update(self):
        """Test envoi de mise à jour d'alignement"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        
        data = {"value": 99.911}
        await manager.send_alignment_update(data)
        
        websocket.send_text.assert_called_once()
        message = json.loads(websocket.send_text.call_args[0][0])
        assert message["type"] == "alignment_update"
        assert message["data"] == data
    
    async def test_send_alignment_complete(self):
        """Test envoi de résultats finaux"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        
        results = {"average": 99.5, "min": 98.0, "max": 100.0}
        await manager.send_alignment_complete(results)
        
        websocket.send_text.assert_called_once()
        message = json.loads(websocket.send_text.call_args[0][0])
        assert message["type"] == "alignment_complete"
        assert message["results"] == results
    
    async def test_multiple_connections(self):
        """Test avec plusieurs connexions"""
        manager = ConnectionManager()
        
        websockets = [AsyncMock() for _ in range(5)]
        
        for ws in websockets:
            await manager.connect(ws)
        
        assert len(manager.active_connections) == 5
        
        await manager.broadcast({"type": "test"})
        
        for ws in websockets:
            assert ws.send_text.call_count == 1

