# Scripts de Build Standalone

Ce dossier contient les scripts pour créer des versions standalone (autonomes) d'AlignTester.

## 📁 Fichiers

- **`build_standalone.py`** : Script principal pour créer les exécutables standalone
- **`launcher_standalone.py`** : Launcher qui démarre le serveur et ouvre le navigateur

## 🚀 Utilisation rapide

### Build pour votre plateforme actuelle

```bash
# Depuis la racine du projet
python AlignTester/scripts/build_standalone.py
```

Le script va :
1. Vérifier les dépendances (PyInstaller, Node.js)
2. Builder le frontend React
3. Créer l'exécutable avec PyInstaller
4. Générer le package dans `build_standalone/dist/[plateforme]/aligntester/`

### Résultat

Après le build, vous trouverez :
- **Windows** : `build_standalone/dist/windows/aligntester/aligntester.exe`
- **Linux** : `build_standalone/dist/linux/aligntester/aligntester`
- **macOS** : `build_standalone/dist/macos/aligntester/aligntester`

## 📦 Distribution

Pour distribuer la version standalone :

1. **Compressez le dossier** `aligntester` :
   ```bash
   # Windows (PowerShell)
   Compress-Archive -Path build_standalone/dist/windows/aligntester -DestinationPath aligntester-standalone-windows-x64.zip
   
   # Linux/macOS
   cd build_standalone/dist
   zip -r aligntester-standalone-linux-x64.zip linux/aligntester
   zip -r aligntester-standalone-macos-x64.zip macos/aligntester
   ```

2. **Nommez les fichiers** selon la plateforme et l'architecture

## 📚 Documentation complète

- **Guide de build** : `AlignTester/docs/BUILD_STANDALONE.md`
- **Guide utilisateur** : `AlignTester/docs/GUIDE_STANDALONE_UTILISATEUR.md`

## ⚙️ Prérequis

- Python 3.11+
- PyInstaller (`pip install pyinstaller`)
- Node.js et npm (pour le build frontend)
- Toutes les dépendances Python (`pip install -r AlignTester/requirements.txt`)

## 🔧 Dépannage

Voir `AlignTester/docs/BUILD_STANDALONE.md` pour le dépannage détaillé.
