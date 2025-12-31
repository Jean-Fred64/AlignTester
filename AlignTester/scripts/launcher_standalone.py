"""
Launcher Standalone pour AlignTester
Démarre le serveur FastAPI et ouvre automatiquement le navigateur
"""

import sys
import os
from pathlib import Path
import uvicorn
import webbrowser
import threading
import time
import signal

# Déterminer le chemin de base selon le mode d'exécution
if getattr(sys, 'frozen', False):
    # Mode standalone (PyInstaller)
    BASE_DIR = Path(sys.executable).parent
else:
    # Mode développement
    BASE_DIR = Path(__file__).parent.parent

# Chemins des ressources
# En mode standalone, le frontend est dans frontend/dist
# En mode développement, il est dans src/frontend/dist
if getattr(sys, 'frozen', False):
    FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
    BACKEND_DIR = BASE_DIR / "backend"
else:
    # Mode développement
    FRONTEND_DIR = BASE_DIR.parent / "src" / "frontend" / "dist"
    BACKEND_DIR = BASE_DIR.parent / "src" / "backend"

# Ajouter le backend au path Python
if BACKEND_DIR.exists():
    sys.path.insert(0, str(BACKEND_DIR))

# Variables globales pour le serveur
server_thread = None
server_process = None
shutdown_event = threading.Event()

def signal_handler(signum, frame):
    """Gestionnaire de signaux pour arrêt propre"""
    print("\n🛑 Arrêt de l'application...")
    shutdown_event.set()
    sys.exit(0)

# Enregistrer les gestionnaires de signaux
if sys.platform != 'win32':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def check_port(port=8000):
    """Vérifie si le port est disponible"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def find_free_port(start_port=8000):
    """Trouve un port libre"""
    import socket
    for port in range(start_port, start_port + 100):
        if check_port(port):
            return port
    return None

def start_server(port=8000):
    """Démarre le serveur FastAPI"""
    try:
        # Importer l'application FastAPI
        from main import app
        
        # Servir le frontend si disponible
        if FRONTEND_DIR.exists() and any(FRONTEND_DIR.iterdir()):
            from fastapi.staticfiles import StaticFiles
            # Servir les fichiers statiques
            app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
            print(f"📁 Frontend trouvé dans: {FRONTEND_DIR}")
        else:
            print(f"⚠️  Frontend non trouvé dans: {FRONTEND_DIR}")
            print("   L'application fonctionnera en mode API uniquement")
            print("   Vous pouvez accéder à l'API sur http://127.0.0.1:{port}/api")
        
        # Démarrer le serveur
        print(f"🚀 Démarrage du serveur sur http://127.0.0.1:{port}")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def open_browser(port=8000, delay=2):
    """Ouvre le navigateur après un court délai"""
    time.sleep(delay)
    if not shutdown_event.is_set():
        url = f"http://127.0.0.1:{port}"
        print(f"🌐 Ouverture du navigateur: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️  Impossible d'ouvrir le navigateur automatiquement: {e}")
            print(f"   Veuillez ouvrir manuellement: {url}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🎯 AlignTester - Version Standalone")
    print("=" * 60)
    print(f"📂 Répertoire de base: {BASE_DIR}")
    print(f"📁 Frontend: {FRONTEND_DIR} ({'✓' if FRONTEND_DIR.exists() else '✗'})")
    print(f"📁 Backend: {BACKEND_DIR} ({'✓' if BACKEND_DIR.exists() else '✗'})")
    print("=" * 60)
    
    # Trouver un port libre
    port = find_free_port(8000)
    if port is None:
        print("❌ Aucun port libre trouvé (8000-8099)")
        sys.exit(1)
    
    if port != 8000:
        print(f"⚠️  Le port 8000 est occupé, utilisation du port {port}")
    
    # Ouvrir le navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()
    
    # Démarrer le serveur (bloquant)
    try:
        start_server(port)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
