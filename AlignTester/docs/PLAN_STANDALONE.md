# Plan de Développement - Version Standalone pour Débutants

## 🎯 Objectif

Créer une version standalone (autonome) d'AlignTester destinée aux utilisateurs débutants qui :
- Ne nécessite pas d'installation de Python, Node.js ou autres dépendances
- Fonctionne avec un simple double-clic
- Inclut une interface simplifiée avec guide pas à pas
- Cache les options avancées par défaut

---

## 📦 Architecture Proposée

### Option 1 : PyInstaller (Recommandé)

**Structure de l'application standalone :**

```
aligntester_standalone/
├── aligntester.exe           # Exécutable principal (Windows)
│   ou aligntester            # Exécutable principal (Linux/macOS)
├── backend/                  # Backend Python intégré (binaire)
│   ├── fastapi (compilé)
│   └── uvicorn (compilé)
├── frontend/                 # Frontend React buildé
│   ├── index.html
│   ├── assets/
│   └── ...
├── gw.exe                    # Greaseweazle (optionnel, si licence le permet)
└── README_STANDALONE.txt     # Guide d'utilisation simple
```

**Avantages :**
- ✅ Single executable ou package simple
- ✅ Fonctionne offline
- ✅ Pas de dépendances externes
- ✅ Distribution facile (fichier unique ou dossier)

**Inconvénients :**
- ⚠️ Taille importante (~50-100 MB avec dépendances)
- ⚠️ Nécessite PyInstaller et configuration

### Option 2 : Electron (Alternative)

**Structure :**
- Application Electron qui inclut Node.js
- Backend Python comme processus enfant
- Frontend React intégré

**Avantages :**
- ✅ Interface native
- ✅ Très répandu (VS Code, Discord, etc.)

**Inconvénients :**
- ❌ Taille très importante (~150-200 MB)
- ❌ Plus complexe à développer

### Option 3 : Serveur Intégré + Browser (Simple)

**Structure :**
- Exécutable Python avec serveur intégré
- Ouvre automatiquement le navigateur
- Frontend servi par le serveur intégré

**Avantages :**
- ✅ Simple à implémenter
- ✅ Taille raisonnable

**Inconvénients :**
- ⚠️ Nécessite un navigateur installé
- ⚠️ Moins "natif"

---

## 🛠️ Implémentation Recommandée : PyInstaller

### Étapes de Développement

#### 1. Script de Build Standalone

Créer `AlignTester/scripts/build_standalone.py` :

```python
"""
Script pour créer la version standalone d'AlignTester
Utilise PyInstaller pour créer un exécutable
"""

import os
import shutil
import subprocess
from pathlib import Path
import sys

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent.parent
ALIGNTESTER_DIR = PROJECT_ROOT / "AlignTester"
BUILD_DIR = PROJECT_ROOT / "build_standalone"
DIST_DIR = BUILD_DIR / "dist"

def build_frontend():
    """Build le frontend React en fichiers statiques"""
    frontend_dir = ALIGNTESTER_DIR / "src" / "frontend"
    os.chdir(frontend_dir)
    
    print("📦 Build du frontend...")
    subprocess.run(["npm", "run", "build"], check=True)
    
    dist_frontend = frontend_dir / "dist"
    return dist_frontend

def create_launcher_script():
    """Crée le script launcher qui démarre le serveur"""
    launcher_code = '''
import sys
import os
from pathlib import Path
import uvicorn
import webbrowser
import threading
import time

# Chemins
if getattr(sys, 'frozen', False):
    # Mode standalone (PyInstaller)
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"

def start_server():
    """Démarre le serveur FastAPI"""
    sys.path.insert(0, str(BACKEND_DIR))
    from main import app
    
    # Servir le frontend
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
    
    # Démarrer le serveur
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def open_browser():
    """Ouvre le navigateur après un court délai"""
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Ouvrir le navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Démarrer le serveur
    start_server()
'''
    
    launcher_path = ALIGNTESTER_DIR / "launcher_standalone.py"
    launcher_path.write_text(launcher_code)
    return launcher_path

def build_with_pyinstaller(launcher_path, frontend_dist):
    """Utilise PyInstaller pour créer l'exécutable"""
    print("🔨 Build avec PyInstaller...")
    
    # Créer le spec file pour PyInstaller
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{launcher_path}'],
    pathex=[],
    binaries=[],
    datas=[
        ('{frontend_dist}', 'frontend'),
        ('{ALIGNTESTER_DIR / "src" / "backend"}', 'backend'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'websockets',
    ],
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
    name='aligntester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Mettre à False pour masquer la console
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
    
    spec_path = BUILD_DIR / "aligntester.spec"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec_content)
    
    # Exécuter PyInstaller
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--clean",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR / "work"),
    ], check=True)

def main():
    """Fonction principale"""
    print("🚀 Build de la version standalone d'AlignTester...")
    
    # 1. Build frontend
    frontend_dist = build_frontend()
    
    # 2. Créer le launcher
    launcher_path = create_launcher_script()
    
    # 3. Build avec PyInstaller
    build_with_pyinstaller(launcher_path, frontend_dist)
    
    print("\n✅ Build terminé!")
    print(f"📁 Exécutable disponible dans: {DIST_DIR / 'aligntester'}")

if __name__ == "__main__":
    main()
```

#### 2. Mode Simple dans l'Interface

**Dans le frontend**, ajouter un toggle "Mode Simple" :

```typescript
// src/components/ModeToggle.tsx
const [simpleMode, setSimpleMode] = useState(true);

// Masquer les options avancées si simpleMode est true
{simpleMode && (
  <div className="simple-mode-guide">
    <h2>Guide pas à pas</h2>
    <StepsGuide />
  </div>
)}

{!simpleMode && (
  <AdvancedOptions />
)}
```

#### 3. Guide Utilisateur Standalone

Créer `release/docs/GUIDE_STANDALONE.md` :

```markdown
# Guide d'Utilisation - AlignTester Standalone

## Installation

1. Téléchargez `aligntester.exe` (Windows) ou `aligntester` (Linux/macOS)
2. Double-cliquez sur le fichier
3. Le navigateur s'ouvre automatiquement

## Première Utilisation

1. Connectez votre Greaseweazle
2. Cliquez sur "Démarrer le test"
3. Suivez les instructions à l'écran

## Mode Simple vs Avancé

- **Mode Simple** : Recommandé pour les débutants, guide pas à pas
- **Mode Avancé** : Pour les utilisateurs expérimentés, toutes les options

## Besoin d'aide ?

Consultez la FAQ dans l'application ou sur GitHub.
```

---

## 📋 Checklist de Développement

### Phase 1 : Préparation
- [ ] Installer PyInstaller : `pip install pyinstaller`
- [ ] Tester le build du frontend : `npm run build`
- [ ] Vérifier que le backend démarre correctement

### Phase 2 : Développement du Script de Build
- [ ] Créer `build_standalone.py`
- [ ] Implémenter `build_frontend()`
- [ ] Implémenter `create_launcher_script()`
- [ ] Implémenter `build_with_pyinstaller()`
- [ ] Tester le build sur Windows
- [ ] Tester le build sur Linux
- [ ] Tester le build sur macOS

### Phase 3 : Mode Simple dans l'Interface
- [ ] Ajouter le toggle "Mode Simple"
- [ ] Créer le composant `StepsGuide`
- [ ] Masquer les options avancées en mode simple
- [ ] Ajouter des messages d'aide contextuels
- [ ] Tester l'interface

### Phase 4 : Documentation
- [ ] Créer `GUIDE_STANDALONE.md`
- [ ] Créer `README_STANDALONE.txt` (dans le package)
- [ ] Ajouter des screenshots
- [ ] Créer une FAQ

### Phase 5 : Tests et Optimisation
- [ ] Tester sur différentes versions Windows
- [ ] Tester sur différentes versions Linux
- [ ] Tester sur macOS
- [ ] Optimiser la taille de l'exécutable
- [ ] Tester le lancement automatique du navigateur
- [ ] Tester le fonctionnement offline

### Phase 6 : Release
- [ ] Intégrer dans `prepare_release.py`
- [ ] Créer les packages de distribution
- [ ] Tester l'installation complète
- [ ] Publier sur GitHub Releases

---

## 🔄 Intégration avec le Workflow Actuel

### Modification de `prepare_release.py`

Ajouter une option pour créer aussi la version standalone :

```python
def prepare_release(include_standalone=False):
    # ... code existant ...
    
    if include_standalone:
        print("\n📦 Création de la version standalone...")
        subprocess.run([
            sys.executable,
            str(ALIGNTESTER_DIR / "scripts" / "build_standalone.py")
        ], check=True)
        
        # Copier la version standalone dans release/
        standalone_dir = BUILD_DIR / "dist" / "aligntester"
        release_standalone = RELEASE_DIR / "standalone"
        shutil.copytree(standalone_dir, release_standalone, dirs_exist_ok=True)
```

---

## 📝 Notes Importantes

1. **Licence Greaseweazle** : Vérifier si on peut inclure `gw.exe` dans le package
2. **Taille du package** : PyInstaller crée des packages volumineux, prévoir ~50-100 MB
3. **Antivirus** : Les exécutables PyInstaller sont parfois flaggés par les antivirus
4. **Signatures** : Pour Windows, considérer la signature de code pour éviter les warnings
5. **Mises à jour** : Prévoir un mécanisme de mise à jour (optionnel)

---

## 🎯 Timeline Suggérée

- **Après les tests** : Développer la version standalone
- **Estimation** : 1-2 semaines de développement
- **Priorité** : Moyenne (après la version web fonctionnelle et testée)

---

**Dernière mise à jour** : Date de création  
**Statut** : Planification

