"""
Gestionnaire WebSocket pour l'affichage temps réel
"""

from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    """Gestionnaire des connexions WebSocket"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accepte une nouvelle connexion WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Déconnecte un WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envoie un message à un WebSocket spécifique"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Erreur envoi message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Diffuse un message à tous les WebSockets connectés"""
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"Erreur broadcast: {e}")
                disconnected.append(connection)
        
        # Nettoyer les connexions déconnectées
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_alignment_update(self, data: dict):
        """Envoie une mise à jour d'alignement"""
        await self.broadcast({
            "type": "alignment_update",
            "data": data
        })
    
    async def send_alignment_complete(self, results: dict):
        """Envoie les résultats finaux d'alignement"""
        await self.broadcast({
            "type": "alignment_complete",
            "results": results
        })

# Instance globale du gestionnaire
websocket_manager = ConnectionManager()

