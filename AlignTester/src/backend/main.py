"""
AlignTester - Backend FastAPI
Application web pour les tests d'alignement Greaseweazle
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from api.routes import router as api_router
from api.websocket import websocket_manager

# Créer l'application FastAPI
app = FastAPI(
    title="AlignTester API",
    description="API pour les tests d'alignement Greaseweazle",
    version="0.1.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes API
app.include_router(api_router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Écho pour test - sera remplacé par la logique d'alignement
            await websocket_manager.send_personal_message(f"Message reçu: {data}", websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Route de santé
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "AlignTester API is running"}

# Servir le frontend en production (optionnel)
# app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

