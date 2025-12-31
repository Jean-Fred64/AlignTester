# Compilation Windows depuis Linux

## 📋 Vue d'ensemble

Ce guide explique comment compiler la version Windows de Greaseweazle depuis un environnement Linux. Plusieurs méthodes sont disponibles, chacune avec ses avantages et inconvénients.

---

## 🎯 Méthodes disponibles

### 1. Wine + Python Windows + cx_Freeze (Recommandé)

**Avantages** :
- ✅ Utilise la même méthode que la compilation native Windows
- ✅ Résultat identique à une compilation sur Windows
- ✅ Support complet de cx_Freeze

**Inconvénients** :
- ⚠️ Nécessite Wine installé
- ⚠️ Nécessite Python Windows dans Wine
- ⚠️ Plus lent que la compilation native

**Prérequis** :
```bash
# Installer Wine
sudo apt install wine wine64  # Ubuntu/Debian
sudo dnf install wine         # Fedora

# Installer Python Windows dans Wine
# Option 1: Télécharger et installer manuellement
wget https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
wine python-3.11.0-amd64.exe

# Option 2: Utiliser winetricks
winetricks python311
```

**Utilisation** :
```bash
./scripts/build_windows_from_linux.sh --method wine
```

---

### 2. Nuitka (Cross-compilation native)

**Avantages** :
- ✅ Compilation native rapide
- ✅ Pas besoin de Wine
- ✅ Supporte la cross-compilation Windows

**Inconvénients** :
- ⚠️ Nécessite MinGW-w64
- ⚠️ Peut nécessiter des ajustements pour certaines dépendances
- ⚠️ Résultat peut différer légèrement de cx_Freeze

**Prérequis** :
```bash
# Installer MinGW-w64
sudo apt install mingw-w64  # Ubuntu/Debian
sudo dnf install mingw64-gcc  # Fedora

# Installer Nuitka
pip3 install nuitka
```

**Utilisation** :
```bash
./scripts/build_windows_from_linux.sh --method nuitka
```

---

### 3. PyInstaller avec Wine

**Avantages** :
- ✅ PyInstaller est bien documenté
- ✅ Peut créer des exécutables standalone

**Inconvénients** :
- ⚠️ Nécessite Wine
- ⚠️ Nécessite des ajustements pour Windows
- ⚠️ Peut ne pas inclure toutes les dépendances

**Prérequis** :
```bash
pip3 install pyinstaller
# + Wine et Python Windows (voir méthode 1)
```

**Utilisation** :
```bash
./scripts/build_windows_from_linux.sh --method pyinstaller
```

---

### 4. Docker (Image Windows)

**Avantages** :
- ✅ Environnement Windows isolé
- ✅ Pas besoin de Wine sur le système hôte
- ✅ Résultat garanti identique à Windows

**Inconvénients** :
- ⚠️ Nécessite Docker
- ⚠️ Nécessite une image Windows (grosse taille)
- ⚠️ Plus complexe à configurer

**Prérequis** :
```bash
# Installer Docker
# Voir: https://docs.docker.com/get-docker/
```

**Utilisation** :
```bash
./scripts/build_windows_from_linux.sh --method docker
```

---

## 🚀 Utilisation rapide

### Méthode recommandée (Wine)

1. **Installer Wine** :
   ```bash
   sudo apt install wine wine64
   ```

2. **Installer Python Windows dans Wine** :
   ```bash
   # Télécharger Python 3.11
   wget https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
   
   # Installer dans Wine
   wine python-3.11.9-amd64.exe
   # Cochez "Add Python to PATH" lors de l'installation
   ```

3. **Exécuter le script** :
   ```bash
   cd /home/jean-fred/Aligntester/AlignTester
   ./scripts/build_windows_from_linux.sh --method wine
   ```

4. **Résultat** :
   Les fichiers compilés seront dans :
   ```
   build/greaseweazle-1.23b-windows/greaseweazle-1.23b/
   ```

---

## 📁 Structure des fichiers générés

Après compilation, vous obtiendrez :

```
build/greaseweazle-1.23b-windows/greaseweazle-1.23b/
├── gw.exe                    # Exécutable principal
├── python*.dll              # DLLs Python
├── lib/                     # Modules Python
│   ├── greaseweazle/       # Module complet
│   └── greaseweazle.data/  # Fichiers de configuration
└── [autres DLLs nécessaires]
```

---

## 🔧 Dépannage

### Wine ne trouve pas Python

Vérifiez où Python est installé :
```bash
find ~/.wine/drive_c -name "python.exe" -type f
```

Si Python n'est pas trouvé, réinstallez-le dans Wine.

### Erreurs de compilation avec MinGW

Assurez-vous que MinGW-w64 est correctement installé :
```bash
x86_64-w64-mingw32-gcc --version
```

### Problèmes de chemins dans Wine

Les chemins Linux peuvent causer des problèmes. Le script copie automatiquement les sources vers `C:\temp\` dans Wine pour éviter ces problèmes.

### Erreurs de dépendances

Si certaines dépendances ne sont pas trouvées :
```bash
# Dans Wine, installer les dépendances manuellement
wine python.exe -m pip install crcmod bitarray pyserial requests
```

---

## ⚡ Alternative : Utiliser WSL avec accès Windows

Si vous êtes sur WSL, vous pouvez aussi :

1. **Compiler directement sur Windows** depuis WSL :
   ```bash
   # Depuis WSL, accéder au système Windows
   cd /mnt/c/path/to/project
   powershell.exe -File build_windows.ps1
   ```

2. **Utiliser le script qui copie vers Windows natif** :
   ```bash
   # Le script build_windows_native.ps1 copie automatiquement
   # les sources vers C:\temp\ pour éviter les problèmes de chemins
   ```

---

## 📝 Notes importantes

1. **Routines optimisées** : Les routines optimisées (extensions C) seront compilées pour Windows si vous utilisez Wine avec Visual Studio Build Tools ou MinGW dans Wine.

2. **Tests** : Testez toujours l'exécutable généré sur une vraie machine Windows avant de le distribuer.

3. **Dépendances** : Certaines dépendances peuvent nécessiter des DLLs Windows spécifiques. Vérifiez que toutes les DLLs nécessaires sont incluses.

4. **Performance** : La compilation avec Wine est plus lente que la compilation native, mais le résultat est identique.

---

## 🔗 Ressources

- [Documentation Wine](https://www.winehq.org/documentation)
- [Nuitka Documentation](https://nuitka.net/doc/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [MinGW-w64](https://www.mingw-w64.org/)

---

## ✅ Vérification

Après compilation, testez l'exécutable :

1. **Copiez les fichiers sur Windows**
2. **Exécutez** :
   ```cmd
   gw.exe --version
   gw.exe align --help
   ```

Si tout fonctionne, la compilation est réussie ! ✅

