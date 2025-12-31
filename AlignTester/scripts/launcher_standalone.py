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

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    # Forcer UTF-8 pour stdout et stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Déterminer le chemin de base selon le mode d'exécution
if getattr(sys, 'frozen', False):
    # Mode standalone (PyInstaller)
    # PyInstaller place les fichiers dans _MEIPASS (temporaire) ou _internal (permanent)
    if hasattr(sys, '_MEIPASS'):
        # Mode onefile (fichier temporaire)
        BASE_DIR = Path(sys._MEIPASS)
    else:
        # Mode onedir (dossier permanent)
        BASE_DIR = Path(sys.executable).parent
        # Les fichiers datas peuvent être dans _internal ou à côté de l'exécutable
        _internal_dir = BASE_DIR / "_internal"
        if _internal_dir.exists():
            # Vérifier si les fichiers sont dans _internal
            if (_internal_dir / "frontend").exists() or (_internal_dir / "backend").exists():
                BASE_DIR = _internal_dir
else:
    # Mode développement
    BASE_DIR = Path(__file__).parent.parent

# Chemins des ressources
# En mode standalone, le frontend est dans frontend/dist
# En mode développement, il est dans src/frontend/dist
if getattr(sys, 'frozen', False):
    # Essayer plusieurs emplacements possibles
    # PyInstaller peut placer les fichiers dans différents endroits
    exe_dir = Path(sys.executable).parent
    possible_frontend_dirs = [
        BASE_DIR / "frontend" / "dist",
        BASE_DIR / "dist",  # Si frontend/dist est directement dans BASE_DIR
        exe_dir / "frontend" / "dist",
        exe_dir / "_internal" / "frontend" / "dist",
        BASE_DIR.parent / "frontend" / "dist",
        # Essayer aussi sans le sous-dossier dist
        BASE_DIR / "frontend",
        exe_dir / "frontend",
        exe_dir / "_internal" / "frontend",
    ]
    possible_backend_dirs = [
        BASE_DIR / "backend",
        exe_dir / "backend",
        exe_dir / "_internal" / "backend",
        BASE_DIR.parent / "backend",
    ]
    
    FRONTEND_DIR = None
    for dir_path in possible_frontend_dirs:
        if dir_path.exists():
            # Vérifier si c'est un dossier dist ou contient index.html
            if (dir_path / "index.html").exists() or any(dir_path.glob("*.html")):
                FRONTEND_DIR = dir_path
                break
            # Ou si c'est un dossier avec des sous-dossiers assets
            if (dir_path / "assets").exists():
                FRONTEND_DIR = dir_path
                break
    
    BACKEND_DIR = None
    for dir_path in possible_backend_dirs:
        if dir_path.exists() and (dir_path / "main.py").exists():
            BACKEND_DIR = dir_path
            break
else:
    # Mode développement
    FRONTEND_DIR = BASE_DIR.parent / "src" / "frontend" / "dist"
    BACKEND_DIR = BASE_DIR.parent / "src" / "backend"

# Ajouter le backend au path Python (sera fait dans start_server si nécessaire)

# Variables globales pour le serveur
server_thread = None
server_process = None
shutdown_event = threading.Event()

def signal_handler(signum, frame):
    """Gestionnaire de signaux pour arrêt propre"""
    print("\n[*] Arret de l'application...")
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
    global BACKEND_DIR, FRONTEND_DIR
    try:
        # Déterminer le chemin du backend à utiliser
        backend_to_use = BACKEND_DIR
        
        # Ajouter le backend au path Python si nécessaire
        if backend_to_use and backend_to_use.exists():
            backend_str = str(backend_to_use.resolve())
            if backend_str not in sys.path:
                sys.path.insert(0, backend_str)
            print(f"[*] Backend ajoute au path: {backend_str}")
        else:
            print(f"[ERROR] Backend non trouve: {backend_to_use}")
            print(f"[*] Path Python actuel: {sys.path}")
            print(f"[*] BASE_DIR: {BASE_DIR}")
            print(f"[*] Essai de recherche dans _internal...")
            # Essayer de trouver le backend dans _internal
            _internal = Path(sys.executable).parent / "_internal"
            if _internal.exists():
                print(f"[*] _internal trouve: {_internal}")
                for item in _internal.iterdir():
                    print(f"[*]   - {item}")
                backend_internal = _internal / "backend"
                if backend_internal.exists():
                    backend_str = str(backend_internal.resolve())
                    sys.path.insert(0, backend_str)
                    print(f"[OK] Backend trouve dans _internal: {backend_str}")
                    backend_to_use = backend_internal
                    BACKEND_DIR = backend_internal  # Mettre à jour la variable globale
                else:
                    raise ImportError(f"Backend directory not found in {_internal}")
            else:
                raise ImportError(f"Backend directory not found: {backend_to_use}")
        
        # Importer l'application FastAPI
        from main import app
        
        # Chercher le frontend si pas trouvé
        frontend_to_use = FRONTEND_DIR
        if not frontend_to_use or not frontend_to_use.exists():
            # Essayer de trouver le frontend dans plusieurs emplacements
            exe_dir = Path(sys.executable).parent
            _internal = exe_dir / "_internal"
            
            # D'abord, lister le contenu de _internal pour debug
            if _internal.exists():
                print(f"[*] Contenu de _internal:")
                try:
                    for item in sorted(_internal.iterdir()):
                        item_type = "DIR" if item.is_dir() else "FILE"
                        print(f"[*]   - {item.name} ({item_type})")
                except Exception as e:
                    print(f"[*]   Erreur lors de la lecture: {e}")
            
            # En mode onedir (COLLECT), PyInstaller place les datas dans le même dossier que l'exécutable
            # En mode onefile, les datas sont dans _internal
            search_paths = [
                exe_dir / "frontend" / "dist",  # Mode onedir - datas dans le même dossier que l'exe
                exe_dir / "frontend",
                _internal / "frontend" / "dist",  # Mode onefile - datas dans _internal
                _internal / "frontend",
                _internal / "dist",  # Peut-être que PyInstaller a mis dist directement
                BASE_DIR / "frontend" / "dist",
                BASE_DIR / "frontend",
            ]
            
            # Chercher récursivement dans exe_dir et _internal pour trouver index.html
            for search_root in [exe_dir, _internal]:
                if search_root.exists():
                    print(f"[*] Recherche recursive de index.html dans {search_root}...")
                    try:
                        for html_file in search_root.rglob("index.html"):
                            html_dir = html_file.parent
                            print(f"[*]   Trouve index.html dans: {html_dir}")
                            if (html_dir / "assets").exists() or any(html_dir.glob("*.js")) or any(html_dir.glob("*.css")):
                                frontend_to_use = html_dir
                                FRONTEND_DIR = html_dir
                                print(f"[OK] Frontend trouve recursivement: {html_dir}")
                                break
                        if frontend_to_use and frontend_to_use.exists():
                            break
                    except Exception as e:
                        print(f"[*]   Erreur lors de la recherche recursive: {e}")
            
            print(f"[*] Recherche du frontend dans {len(search_paths)} emplacements...")
            for search_path in search_paths:
                if search_path.exists():
                    # Vérifier si c'est un dossier dist valide
                    if (search_path / "index.html").exists() or any(search_path.glob("*.html")):
                        frontend_to_use = search_path
                        FRONTEND_DIR = search_path
                        print(f"[OK] Frontend trouve: {search_path}")
                        break
                    # Ou si c'est un dossier avec assets
                    if (search_path / "assets").exists():
                        frontend_to_use = search_path
                        FRONTEND_DIR = search_path
                        print(f"[OK] Frontend trouve (avec assets): {search_path}")
                        break
                    else:
                        print(f"[*]   - {search_path} existe mais ne contient pas index.html")
                        # Lister le contenu pour debug
                        try:
                            contents = list(search_path.iterdir())[:5]
                            print(f"[*]     Contenu: {[x.name for x in contents]}")
                        except:
                            pass
                else:
                    print(f"[*]   - {search_path} n'existe pas")
        
        # Servir le frontend si disponible
        if frontend_to_use and frontend_to_use.exists() and any(frontend_to_use.iterdir()):
            from fastapi.staticfiles import StaticFiles
            # Servir les fichiers statiques
            app.mount("/", StaticFiles(directory=str(frontend_to_use), html=True), name="static")
            print(f"[OK] Frontend servi depuis: {frontend_to_use}")
        else:
            frontend_msg = str(frontend_to_use) if frontend_to_use else "None"
            print(f"[WARN] Frontend non trouve dans: {frontend_msg}")
            print("   L'application fonctionnera en mode API uniquement")
            print(f"   Vous pouvez acceder a l'API sur http://127.0.0.1:{port}/api")
        
        # Démarrer le serveur
        print(f"[*] Demarrage du serveur sur http://127.0.0.1:{port}")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"[ERROR] Erreur lors du demarrage du serveur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def open_browser(port=8000, delay=2):
    """Ouvre le navigateur après un court délai"""
    time.sleep(delay)
    if not shutdown_event.is_set():
        url = f"http://127.0.0.1:{port}"
        print(f"[*] Ouverture du navigateur: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[WARN] Impossible d'ouvrir le navigateur automatiquement: {e}")
            print(f"   Veuillez ouvrir manuellement: {url}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("[*] AlignTester - Version Standalone")
    print("=" * 60)
    print(f"[*] Repertoire de base: {BASE_DIR}")
    frontend_status = "OK" if (FRONTEND_DIR and FRONTEND_DIR.exists()) else "MANQUANT"
    backend_status = "OK" if (BACKEND_DIR and BACKEND_DIR.exists()) else "MANQUANT"
    print(f"[*] Frontend: {FRONTEND_DIR} ({frontend_status})")
    print(f"[*] Backend: {BACKEND_DIR} ({backend_status})")
    print("=" * 60)
    
    # Trouver un port libre
    port = find_free_port(8000)
    if port is None:
        print("[ERROR] Aucun port libre trouve (8000-8099)")
        sys.exit(1)
    
    if port != 8000:
        print(f"[WARN] Le port 8000 est occupe, utilisation du port {port}")
    
    # Ouvrir le navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()
    
    # Démarrer le serveur (bloquant)
    try:
        start_server(port)
    except KeyboardInterrupt:
        print("\n[*] Arret demande par l'utilisateur")
    except Exception as e:
        print(f"\n[ERROR] Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
