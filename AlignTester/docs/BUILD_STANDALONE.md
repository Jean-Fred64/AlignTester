# Guide de Build Standalone - AlignTester

Ce guide explique comment créer des versions standalone (autonomes) d'AlignTester pour Windows, Linux et macOS.

## 📋 Prérequis

### Pour toutes les plateformes

1. **Python 3.11+** installé
2. **Node.js et npm** installés (pour le build du frontend)
3. **Toutes les dépendances Python** installées :
   ```bash
   pip install -r AlignTester/requirements.txt
   ```

### Spécifique à chaque plateforme

- **Windows** : Aucun prérequis supplémentaire
- **Linux** : Peut nécessiter des bibliothèques système (voir ci-dessous)
- **macOS** : Peut nécessiter Xcode Command Line Tools

## 🚀 Build pour votre plateforme actuelle

### Étape 1 : Préparer l'environnement

```bash
# Aller dans le répertoire du projet
cd /chemin/vers/Aligntester

# Installer les dépendances Python
pip install -r AlignTester/requirements.txt

# Installer les dépendances frontend (si pas déjà fait)
cd AlignTester/src/frontend
npm install
cd ../../..
```

### Étape 2 : Lancer le build

```bash
# Windows
python AlignTester/scripts/build_standalone.py

# Linux
python3 AlignTester/scripts/build_standalone.py

# macOS
python3 AlignTester/scripts/build_standalone.py
```

Le script va :
1. ✅ Vérifier les dépendances
2. 📦 Builder le frontend React
3. 🔨 Créer l'exécutable avec PyInstaller
4. 📁 Générer le package dans `build_standalone/dist/[plateforme]/aligntester/`

### Étape 3 : Tester l'exécutable

```bash
# Windows
build_standalone/dist/windows/aligntester/aligntester.exe

# Linux
./build_standalone/dist/linux/aligntester/aligntester

# macOS
./build_standalone/dist/macos/aligntester/aligntester
```

## 🔄 Build pour d'autres plateformes

### Build Windows depuis Linux (WSL ou Linux natif)

Pour créer un exécutable Windows depuis Linux, vous avez plusieurs options :

#### Option 1 : Utiliser Wine (recommandé pour tests simples)

```bash
# Installer Wine
sudo apt-get install wine

# Installer Python pour Windows dans Wine
wine python-3.11.9-amd64.exe

# Installer PyInstaller dans Wine
wine pip install pyinstaller

# Modifier le script build_standalone.py pour utiliser wine python
```

#### Option 2 : Utiliser une machine Windows

Le plus simple est de faire le build directement sur une machine Windows.

### Build Linux depuis Windows

Utiliser WSL2 ou une machine Linux virtuelle.

### Build macOS depuis Linux/Windows

Utiliser une machine macOS (physique ou virtuelle) ou un service CI/CD comme GitHub Actions.

## 📦 Structure du package standalone

Après le build, vous obtiendrez une structure comme ceci :

```
aligntester/
├── aligntester.exe          # (Windows) ou aligntester (Linux/macOS)
├── _internal/               # Bibliothèques Python compilées
│   ├── python311.dll       # (Windows uniquement)
│   ├── lib/                # Bibliothèques Python
│   └── ...
├── frontend/                # Frontend React buildé
│   └── dist/
│       ├── index.html
│       ├── assets/
│       └── ...
├── backend/                 # Code backend Python
│   ├── main.py
│   ├── api/
│   └── ...
└── README_STANDALONE.txt    # Guide d'utilisation
```

## 🎯 Distribution

### Créer un package distributable

1. **Compresser le dossier** :
   ```bash
   # Windows (PowerShell)
   Compress-Archive -Path build_standalone/dist/windows/aligntester -DestinationPath aligntester-standalone-windows.zip
   
   # Linux/macOS
   cd build_standalone/dist
   zip -r aligntester-standalone-linux.zip linux/aligntester
   zip -r aligntester-standalone-macos.zip macos/aligntester
   ```

2. **Nommer les fichiers** :
   - `aligntester-standalone-windows-x64.zip`
   - `aligntester-standalone-linux-x64.zip`
   - `aligntester-standalone-macos-x64.zip`

### Taille attendue

- **Windows** : ~80-120 MB
- **Linux** : ~70-100 MB
- **macOS** : ~80-120 MB

## 🔧 Dépannage

### Erreur : PyInstaller non trouvé

```bash
pip install pyinstaller
```

### Erreur : npm non trouvé

Installez Node.js depuis https://nodejs.org/

### Erreur : Frontend non buildé

```bash
cd AlignTester/src/frontend
npm install
npm run build
```

### Erreur : Bibliothèques manquantes (Linux)

Sur certaines distributions Linux, vous pourriez avoir besoin de :

```bash
# Ubuntu/Debian
sudo apt-get install libc6-dev

# Fedora
sudo dnf install glibc-devel
```

### Erreur : UPX non trouvé (optionnel)

UPX compresse les exécutables mais n'est pas obligatoire. Si vous voyez un avertissement, vous pouvez l'ignorer ou installer UPX :

```bash
# Ubuntu/Debian
sudo apt-get install upx-ucl

# macOS
brew install upx
```

### L'exécutable ne démarre pas

1. Vérifiez les logs dans la console
2. Vérifiez que tous les fichiers sont présents dans le dossier
3. Sur Linux/macOS, vérifiez les permissions :
   ```bash
   chmod +x aligntester
   ```

### L'antivirus bloque l'exécutable (Windows)

Les exécutables PyInstaller sont parfois détectés comme suspects par les antivirus. C'est un faux positif connu. Solutions :

1. Ajouter une exception dans l'antivirus
2. Signer l'exécutable avec un certificat de code (nécessite un certificat payant)
3. Informer les utilisateurs que c'est un faux positif

## 📝 Notes importantes

1. **Greaseweazle** : L'exécutable standalone nécessite que Greaseweazle soit installé séparément sur le système cible. Il n'est pas inclus dans le package.

2. **Permissions USB** : Sur Linux, les utilisateurs peuvent avoir besoin d'ajouter leur utilisateur au groupe `dialout` ou `tty` :
   ```bash
   sudo usermod -a -G dialout $USER
   ```

3. **Port** : Si le port 8000 est occupé, l'application utilisera automatiquement un autre port (8001, 8002, etc.).

4. **Mises à jour** : Pour mettre à jour l'application, les utilisateurs doivent télécharger la nouvelle version et remplacer les fichiers.

## 🎯 Prochaines améliorations possibles

- [ ] Auto-update intégré
- [ ] Signature de code pour Windows
- [ ] Notarisation pour macOS
- [ ] Inclusion optionnelle de Greaseweazle (si licence le permet)
- [ ] Mode portable (sans installation)

## 📚 Ressources

- [Documentation PyInstaller](https://pyinstaller.org/)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Vite](https://vitejs.dev/)

---

**Dernière mise à jour** : 2024
**Version** : 0.1.0
