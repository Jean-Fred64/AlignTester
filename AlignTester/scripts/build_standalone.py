"""
Script pour créer la version standalone d'AlignTester
Utilise PyInstaller pour créer des exécutables pour Windows, Linux et macOS
"""

import os
import shutil
import subprocess
import sys
import platform
from pathlib import Path

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    # Forcer UTF-8 pour stdout et stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Chemins
# __file__ est dans AlignTester/scripts/build_standalone.py
# Donc parent = scripts, parent.parent = AlignTester, parent.parent.parent = racine du projet
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.resolve()
ALIGNTESTER_DIR = SCRIPT_DIR.parent.resolve()  # AlignTester/
BUILD_DIR = PROJECT_ROOT / "build_standalone"
DIST_DIR = BUILD_DIR / "dist"

# Chemins des sources
SRC_DIR = ALIGNTESTER_DIR / "src"
BACKEND_DIR = SRC_DIR / "backend"
FRONTEND_DIR = SRC_DIR / "frontend"
LAUNCHER_PATH = SCRIPT_DIR / "launcher_standalone.py"

def print_step(message):
    """Affiche un message de progression"""
    print(f"\n{'='*60}")
    print(f"[*] {message}")
    print(f"{'='*60}")

def check_dependencies():
    """Vérifie que les dépendances nécessaires sont installées"""
    print_step("Vérification des dépendances")
    
    # Vérifier PyInstaller
    try:
        import PyInstaller
        print(f"[OK] PyInstaller installe (version {PyInstaller.__version__})")
    except ImportError:
        print("[ERROR] PyInstaller n'est pas installe")
        print("   Installez-le avec: pip install pyinstaller")
        return False
    
    # Vérifier Node.js pour le build frontend
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Node.js installe ({result.stdout.strip()})")
        else:
            print("[WARN] Node.js non trouve - le build frontend sera ignore")
    except FileNotFoundError:
        print("[WARN] Node.js non trouve - le build frontend sera ignore")
    
    return True

def build_frontend():
    """Build le frontend React en fichiers statiques"""
    print_step("Build du frontend")
    
    if not FRONTEND_DIR.exists():
        print("[WARN] Dossier frontend non trouve, skip du build frontend")
        return None
    
    # Vérifier si node_modules existe
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("[*] Installation des dependances npm...")
        os.chdir(FRONTEND_DIR)
        subprocess.run(["npm", "install"], check=False)
    
    # Build du frontend
    print("[*] Build du frontend avec Vite...")
    os.chdir(FRONTEND_DIR)
    
    try:
        result = subprocess.run(["npm", "run", "build"], check=True, capture_output=True, text=True)
        print("[OK] Build frontend reussi")
        
        dist_frontend = FRONTEND_DIR / "dist"
        if dist_frontend.exists():
            print(f"[OK] Frontend builde dans: {dist_frontend}")
            return dist_frontend
        else:
            print("[WARN] Dossier dist non trouve apres le build")
            return None
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erreur lors du build frontend:")
        print(e.stdout)
        print(e.stderr)
        return None
    except FileNotFoundError:
        print("[WARN] npm non trouve, skip du build frontend")
        return None

def create_spec_file(platform_name, frontend_dist=None):
    """Crée le fichier .spec pour PyInstaller"""
    print_step(f"Création du fichier .spec pour {platform_name}")
    
    # Déterminer les extensions selon la plateforme
    if platform_name == "windows":
        exe_name = "aligntester.exe"
        console = True  # True pour voir les logs, False pour masquer
    else:
        exe_name = "aligntester"
        console = True
    
    # Collecter les données à inclure
    datas = []
    
    # Frontend - inclure le dossier dist complet
    # PyInstaller peut copier un dossier entier avec la syntaxe (source_dir, dest_dir)
    # Cela copie récursivement tout le contenu du dossier source vers dest_dir
    if frontend_dist and frontend_dist.exists():
        # Utiliser la syntaxe (dossier_source, dossier_destination) pour copier récursivement
        # PyInstaller copiera tout le contenu de frontend_dist vers frontend/dist
        datas.append((str(frontend_dist.resolve()), "frontend/dist"))
        print(f"[OK] Frontend ajoute (dossier complet): {frontend_dist} -> frontend/dist")
    
    # Backend - inclure tous les fichiers Python
    if BACKEND_DIR.exists():
        # Inclure tous les fichiers Python du backend
        for py_file in BACKEND_DIR.rglob("*.py"):
            rel_path = py_file.relative_to(BACKEND_DIR)
            target_dir = f"backend/{rel_path.parent}" if rel_path.parent != Path('.') else "backend"
            datas.append((str(py_file), target_dir))
        print(f"[OK] Backend ajoute: {BACKEND_DIR}")
    
    # Créer le contenu du spec file
    # Convertir le chemin en string et utiliser des slashes normaux pour compatibilité
    launcher_path_resolved = LAUNCHER_PATH.resolve()
    launcher_path_str = str(launcher_path_resolved).replace('\\', '/')
    
    # Vérifier que le fichier existe
    if not launcher_path_resolved.exists():
        print(f"[ERROR] Fichier launcher non trouve: {launcher_path_resolved}")
        return None
    
    # Utiliser collect_all pour inclure automatiquement tous les modules
    # Convertir datas en format Python pour le spec file
    # Vérifier que les fichiers existent avant de les inclure
    valid_datas = []
    for src, dst in datas:
        src_path = Path(src)
        if src_path.exists():
            valid_datas.append((src, dst))
        else:
            print(f"[WARN] Fichier non trouve, ignore: {src}")
    
    print(f"[*] {len(valid_datas)} fichiers datas valides sur {len(datas)} total)")
    
    # Compter les fichiers frontend et backend
    frontend_count = sum(1 for _, dst in valid_datas if dst.startswith("frontend"))
    backend_count = sum(1 for _, dst in valid_datas if dst.startswith("backend"))
    print(f"[*]   - Frontend: {frontend_count} fichiers")
    print(f"[*]   - Backend: {backend_count} fichiers")
    
    if valid_datas:
        print(f"[*] Exemples de fichiers datas:")
        # Afficher au moins un exemple de frontend et de backend
        frontend_examples = [(src, dst) for src, dst in valid_datas if dst.startswith("frontend")][:2]
        backend_examples = [(src, dst) for src, dst in valid_datas if dst.startswith("backend")][:2]
        for src, dst in frontend_examples + backend_examples:
            print(f"[*]   - {Path(src).name} -> {dst}")
    
    # Construire la liste datas en format Python avec des raw strings pour Windows
    # IMPORTANT: PyInstaller nécessite des tuples (source, destination)
    # où source est un chemin absolu et destination est un chemin relatif
    datas_lines = []
    for src, dst in valid_datas:
        # Utiliser repr() pour échapper correctement les chemins
        # Sur Windows, les backslashes doivent être échappées
        src_str = str(Path(src).resolve())
        # Utiliser des raw strings pour Windows, mais repr() gère déjà l'échappement
        src_escaped = repr(src_str)
        dst_escaped = repr(dst)
        datas_lines.append(f"    ({src_escaped}, {dst_escaped}),")
    datas_str = "[\n" + "\n".join(datas_lines) + "\n]"
    
    # Log pour debug: afficher quelques exemples de datas frontend
    frontend_datas = [(src, dst) for src, dst in valid_datas if dst.startswith("frontend")]
    if frontend_datas:
        print(f"[*] Exemples de datas frontend dans spec file:")
        for src, dst in frontend_datas[:2]:
            print(f"[*]   - {Path(src).name} -> {dst}")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Fichier généré automatiquement pour {platform_name}

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Données à inclure (frontend, backend et autres)
datas = {datas_str}

# Collecter tous les modules de FastAPI, Starlette, Uvicorn, etc.
datas_fastapi, binaries_fastapi, hiddenimports_fastapi = collect_all('fastapi')
datas_starlette, binaries_starlette, hiddenimports_starlette = collect_all('starlette')
datas_uvicorn, binaries_uvicorn, hiddenimports_uvicorn = collect_all('uvicorn')
datas_pydantic, binaries_pydantic, hiddenimports_pydantic = collect_all('pydantic')
datas_websockets, binaries_websockets, hiddenimports_websockets = collect_all('websockets')

# Combiner toutes les données
all_datas = datas + datas_fastapi + datas_starlette + datas_uvicorn + datas_pydantic + datas_websockets
all_binaries = binaries_fastapi + binaries_starlette + binaries_uvicorn + binaries_pydantic + binaries_websockets
all_hiddenimports = hiddenimports_fastapi + hiddenimports_starlette + hiddenimports_uvicorn + hiddenimports_pydantic + hiddenimports_websockets

# Ajouter d'autres imports nécessaires
all_hiddenimports.extend([
    'pydantic_settings',
    'pyserial',
    'pyserial.tools',
    'pyserial.tools.list_ports',
    'multipart',
    'python_multipart',
    'asyncio',
    'json',
    'platform',
    'subprocess',
])

a = Analysis(
    [r'{launcher_path_str}'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{exe_name.replace(".exe", "")}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console={str(console)},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='aligntester',
)
'''
    
    spec_path = BUILD_DIR / f"aligntester_{platform_name}.spec"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec_content)
    print(f"[OK] Fichier .spec cree: {spec_path}")
    
    return spec_path

def build_with_pyinstaller(spec_path, platform_name):
    """Utilise PyInstaller pour créer l'exécutable"""
    print_step(f"Build avec PyInstaller pour {platform_name}")
    
    dist_platform = DIST_DIR / platform_name
    work_platform = BUILD_DIR / "work" / platform_name
    
    # Nettoyer les anciens builds
    if dist_platform.exists():
        print(f"🧹 Nettoyage de l'ancien build: {dist_platform}")
        shutil.rmtree(dist_platform)
    if work_platform.exists():
        shutil.rmtree(work_platform)
    
    # Exécuter PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--clean",
        "--distpath", str(dist_platform),
        "--workpath", str(work_platform),
    ]
    
    print(f"[*] Execution: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[OK] Build PyInstaller reussi")
        
        # Vérifier que les fichiers frontend sont bien inclus
        exe_dir = dist_platform / "aligntester"
        _internal = exe_dir / "_internal"
        frontend_internal = _internal / "frontend" / "dist"
        frontend_exe_dir = exe_dir / "frontend" / "dist"
        
        print(f"[*] Verification inclusion frontend:")
        print(f"[*]   - {frontend_internal} existe: {frontend_internal.exists()}")
        print(f"[*]   - {frontend_exe_dir} existe: {frontend_exe_dir.exists()}")
        
        if frontend_internal.exists():
            files = list(frontend_internal.rglob("*"))
            files = [f for f in files if f.is_file()]
            print(f"[OK] Frontend trouve dans _internal: {len(files)} fichiers")
        elif frontend_exe_dir.exists():
            files = list(frontend_exe_dir.rglob("*"))
            files = [f for f in files if f.is_file()]
            print(f"[OK] Frontend trouve dans exe_dir: {len(files)} fichiers")
        else:
            print(f"[WARN] Frontend non trouve dans le build!")
            # Lister le contenu de _internal pour debug
            if _internal.exists():
                print(f"[*] Contenu de _internal:")
                for item in sorted(_internal.iterdir())[:10]:
                    item_type = "DIR" if item.is_dir() else "FILE"
                    print(f"[*]   - {item.name} ({item_type})")
        
        return exe_dir
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erreur lors du build PyInstaller:")
        print(e.stdout)
        print(e.stderr)
        return None

def create_readme_standalone(platform_name, dist_path):
    """Crée un README pour la version standalone"""
    # Déterminer l'extension de l'exécutable
    exe_ext = ".exe" if platform_name == "windows" else ""
    exe_name = f"aligntester{exe_ext}"
    
    readme_content = f"""# AlignTester - Version Standalone ({platform_name.title()})

## Installation

1. Extrayez tous les fichiers de ce dossier dans un répertoire de votre choix
2. Double-cliquez sur `{exe_name}` pour lancer l'application
3. Le navigateur s'ouvrira automatiquement sur http://127.0.0.1:8000

## Utilisation

- L'application démarre automatiquement un serveur web local
- Le navigateur s'ouvre automatiquement (si ce n'est pas le cas, ouvrez http://127.0.0.1:8000)
- Connectez votre Greaseweazle et suivez les instructions à l'écran

## Arrêt de l'application

- Fermez la fenêtre de terminal/console pour arrêter l'application
- Ou utilisez Ctrl+C dans le terminal

## Dépannage

### Le port 8000 est déjà utilisé
L'application utilisera automatiquement un autre port (8001, 8002, etc.)
Regardez le message dans la console pour connaître le port utilisé.

### Le navigateur ne s'ouvre pas automatiquement
Ouvrez manuellement votre navigateur et allez sur http://127.0.0.1:8000
(ou le port indiqué dans la console)

### Problèmes avec Greaseweazle
- Vérifiez que votre Greaseweazle est bien connecté
- Vérifiez les permissions USB (Linux/macOS peuvent nécessiter des droits sudo)
- Consultez la documentation Greaseweazle pour votre système

## Support

Pour plus d'informations, consultez:
- GitHub: https://github.com/votre-repo/aligntester
- Documentation: Voir les fichiers dans le dossier docs/

Version: 0.1.0
Plateforme: {platform_name.title()}
"""
    
    readme_path = dist_path / "README_STANDALONE.txt"
    readme_path.write_text(readme_content)
    print(f"[OK] README cree: {readme_path}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("[*] Build de la version standalone d'AlignTester")
    print("=" * 60)
    print(f"[*] Repertoire du projet: {PROJECT_ROOT}")
    print(f"[*] Plateforme actuelle: {platform.system()} ({platform.machine()})")
    print("=" * 60)
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Créer les dossiers de build
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build frontend
    frontend_dist = build_frontend()
    
    # Déterminer la plateforme
    current_platform = platform.system().lower()
    if current_platform == "windows":
        platform_name = "windows"
    elif current_platform == "linux":
        platform_name = "linux"
    elif current_platform == "darwin":
        platform_name = "macos"
    else:
        print(f"[WARN] Plateforme non reconnue: {current_platform}")
        print("   Utilisation de 'linux' par defaut")
        platform_name = "linux"
    
    # Créer le fichier .spec
    spec_path = create_spec_file(platform_name, frontend_dist)
    
    # Build avec PyInstaller
    dist_path = build_with_pyinstaller(spec_path, platform_name)
    
    if dist_path and dist_path.exists():
        # Créer le README
        create_readme_standalone(platform_name, dist_path)
        
        print("\n" + "=" * 60)
        print("[OK] Build termine avec succes!")
        print("=" * 60)
        print(f"[*] Executable disponible dans: {dist_path}")
        print(f"\n[*] Pour distribuer:")
        print(f"   1. Compressez le dossier: {dist_path}")
        print(f"   2. Nommez-le: aligntester-standalone-{platform_name}.zip")
        print(f"   3. Distribuez-le aux utilisateurs")
        print("=" * 60)
    else:
        print("\n[ERROR] Le build a echoue")
        sys.exit(1)

if __name__ == "__main__":
    main()
