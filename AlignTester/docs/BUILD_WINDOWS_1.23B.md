# Compilation de Greaseweazle 1.23b pour Windows

## 📋 Vue d'ensemble

Ce guide explique comment compiler la version **1.23b** de Greaseweazle pour Windows, incluant la commande `align`.

---

## ✅ Prérequis

1. **Windows** (7, 8, 10, 11)
2. **Python 3.8 ou supérieur** installé
3. **Accès au dossier source** : `AlignTester/src/greaseweazle-1.23b/`

---

## 🚀 Méthode 1 : Script PowerShell avec chemin Windows natif (Recommandé)

> **⚠️ Important** : Si vous compilez depuis WSL, utilisez ce script qui copie automatiquement les sources vers un dossier Windows natif (`C:\temp\`) pour éviter les problèmes avec les chemins WSL.

### Étape 1 : Vérifier Python 3.11/3.12

Assurez-vous d'avoir Python 3.11 ou 3.12 installé. Pour vérifier :

```powershell
py -3.11 --version
# ou
py -3.12 --version
```

Si vous n'avez pas Python 3.11/3.12 :
1. Téléchargez depuis : https://www.python.org/downloads/
   - Python 3.11 : https://www.python.org/downloads/release/python-3119/
   - Python 3.12 : https://www.python.org/downloads/release/python-31212/ (dernière version 3.12.12)
2. Installez Python 3.11 ou 3.12
3. Cochez "Add Python to PATH" lors de l'installation

### Étape 2 : Ouvrir PowerShell

Ouvrez PowerShell (pas forcément en administrateur, mais recommandé) et naviguez vers le projet :

```powershell
cd "S:\Divers SSD M2\Test D7\Aligntester\AlignTester"
```

### Étape 3 : Exécuter le script

```powershell
powershell -ExecutionPolicy Bypass -File "build\greaseweazle-1.23b-windows\build_windows_native.ps1"
```

Ce script va :
- ✅ Détecter automatiquement Python 3.11 ou 3.12
- ✅ **Copier les sources vers `C:\temp\greaseweazle-1.23b-build`** (si vous êtes dans WSL)
- ✅ Installer les dépendances nécessaires
- ✅ Configurer la version 1.23b
- ✅ Compiler `gw.exe` avec cx_Freeze depuis un chemin Windows natif
- ✅ Tester que tout fonctionne
- ✅ Copier les résultats vers `build/greaseweazle-1.23b-windows/greaseweazle-1.23b/`
- ✅ Nettoyer le dossier temporaire

### Étape 4 : Résultat

Les fichiers compilés seront dans :
```
AlignTester/build/greaseweazle-1.23b-windows/greaseweazle-1.23b/
```

Contenu :
- `gw.exe` : Exécutable principal (avec la commande `align`)
- `*.dll` : DLLs nécessaires (Python, Visual C++ Runtime)
- `lib/` : Modules Python et données
- Documentation (COPYING, README, RELEASE_NOTES, VERSION)

---

## 🚀 Méthode 2 : Script PowerShell avec Python 3.11/3.12 (Alternative)

> **Important** : Ce script détecte automatiquement Python 3.11 ou 3.12, qui sont compatibles avec cx_Freeze. Python 3.13 pose des problèmes de compatibilité.

### Étape 1 : Vérifier Python 3.11/3.12

Assurez-vous d'avoir Python 3.11 ou 3.12 installé. Pour vérifier :

```powershell
py -3.11 --version
# ou
py -3.12 --version
```

Si vous n'avez pas Python 3.11/3.12 :
1. Téléchargez depuis : https://www.python.org/downloads/
   - Python 3.11 : https://www.python.org/downloads/release/python-3119/
   - Python 3.12 : https://www.python.org/downloads/release/python-31212/ (dernière version 3.12.12)
2. Installez Python 3.11 ou 3.12
3. Cochez "Add Python to PATH" lors de l'installation

### Étape 2 : Ouvrir PowerShell

Ouvrez PowerShell (pas forcément en administrateur, mais recommandé) et naviguez vers le projet :

```powershell
cd "S:\Divers SSD M2\Test D7\Aligntester\AlignTester"
```

### Étape 3 : Exécuter le script

```powershell
powershell -ExecutionPolicy Bypass -File "build\greaseweazle-1.23b-windows\build_windows_py311.ps1"
```

Ce script va :
- ✅ Détecter automatiquement Python 3.11 ou 3.12
- ✅ Installer les dépendances nécessaires
- ✅ Configurer la version 1.23b
- ✅ Compiler `gw.exe` avec cx_Freeze
- ✅ Tester que tout fonctionne
- ✅ Créer le dossier de distribution complet

Le script va :
- ✅ Vérifier Python
- ✅ Installer les dépendances (cx_Freeze, setuptools-scm)
- ✅ Configurer la version 1.23b
- ✅ Compiler `gw.exe` avec cx_Freeze
- ✅ Créer le dossier de distribution
- ✅ Tester que `gw.exe` fonctionne

### Étape 3 : Résultat

Les fichiers compilés seront dans :
```
AlignTester/build/greaseweazle-1.23b-windows/greaseweazle-1.23b/
```

Contenu :
- `gw.exe` : Exécutable principal
- `*.dll` : DLLs nécessaires (Python, Visual C++ Runtime)
- `greaseweazle.data/` : Données de configuration
- `COPYING`, `README`, `RELEASE_NOTES`, `VERSION`

---

## 🔧 Méthode 2 : Script PowerShell Original (Alternative)

Si vous préférez utiliser le script original (qui peut avoir des problèmes avec Python 3.13) :

```powershell
powershell -ExecutionPolicy Bypass -File "build\greaseweazle-1.23b-windows\build_windows.ps1"
```

> **Note** : Ce script peut échouer avec Python 3.13. Utilisez plutôt `build_windows_py311.ps1`.

## 🔧 Méthode 3 : Compilation Manuelle

### Étape 1 : Installer les dépendances

```powershell
python -m pip install -U pip setuptools wheel
python -m pip install cx_Freeze setuptools-scm
```

### Étape 2 : Configurer la version

```powershell
cd "AlignTester\src\greaseweazle-1.23b"
$env:SETUPTOOLS_SCM_PRETEND_VERSION = "1.23b"
```

### Étape 3 : Créer __init__.py

```powershell
"__version__ = '1.23b'" | Out-File -FilePath "src\greaseweazle\__init__.py" -Encoding utf8 -NoNewline
```

### Étape 4 : Installer le package

```powershell
python -m pip install -e .
```

### Étape 5 : Compiler avec cx_Freeze

```powershell
cd scripts\win
python setup.py build
```

### Étape 6 : Récupérer les fichiers

Les fichiers compilés seront dans :
```
scripts\win\build\exe.win-amd64\
```

Copiez-les dans un dossier de distribution :
```powershell
# Créer le dossier de distribution
mkdir ..\..\..\..\build\greaseweazle-1.23b-windows\greaseweazle-1.23b

# Copier les fichiers
Copy-Item -Path "build\exe.win-amd64\*" -Destination "..\..\..\..\build\greaseweazle-1.23b-windows\greaseweazle-1.23b" -Recurse
```

---

## 🧪 Méthode 4 : Utiliser le Makefile (si Make est disponible)

Si vous avez Make installé (via WSL, Git Bash, ou autre) :

```bash
cd AlignTester/src/greaseweazle-1.23b
export SETUPTOOLS_SCM_PRETEND_VERSION="1.23b"
make windist
```

Cela créera un dossier `greaseweazle-1.23b/` avec tous les fichiers.

---

## ✅ Vérification

### Tester gw.exe

```powershell
cd "build\greaseweazle-1.23b-windows\greaseweazle-1.23b"
.\gw.exe --version
.\gw.exe info
.\gw.exe align --help
```

### Vérifier la version

La sortie de `gw.exe --version` devrait afficher :
```
Host Tools: 1.23b
```

### Vérifier la commande align

La sortie de `gw.exe --help` devrait inclure :
```
align       Repeatedly read the same track for floppy drive alignment.
```

---

## 📦 Structure du Package Final

```
greaseweazle-1.23b/
├── gw.exe                    # Exécutable principal
├── python311.dll            # DLL Python
├── vcruntime140.dll         # Visual C++ Runtime
├── msvcp140.dll             # Visual C++ Runtime
├── (autres DLLs)            # Autres dépendances
├── greaseweazle.data/       # Données de configuration
│   └── *.cfg
├── COPYING                   # Licence
├── README                    # Documentation
├── RELEASE_NOTES             # Notes de version
└── VERSION                   # Version (1.23b)
```

---

## 🔍 Dépannage

### Erreur : "Python non trouvé"

- Vérifiez que Python est installé : `python --version`
- Ajoutez Python au PATH si nécessaire

### Erreur : "cx_Freeze non trouvé"

- Installez : `python -m pip install cx_Freeze`

### Erreur : "setuptools-scm was unable to detect version"

- Définissez la variable d'environnement :
  ```powershell
  $env:SETUPTOOLS_SCM_PRETEND_VERSION = "1.23b"
  ```

### Erreur lors de la compilation

- Vérifiez que `align.py` est présent dans `src/greaseweazle/tools/`
- Vérifiez que `'align'` est dans la liste des actions de `cli.py`
- Vérifiez que `__init__.py` contient `__version__ = '1.23b'`

### gw.exe ne fonctionne pas

- Vérifiez que toutes les DLLs sont présentes
- Testez depuis le dossier de distribution (pas depuis un autre dossier)
- Vérifiez les permissions d'exécution

---

## 📝 Notes Importantes

1. **Version** : La version 1.23b est configurée dans `src/greaseweazle/__init__.py`
2. **Commande align** : Doit être présente dans `cli.py` et `tools/align.py` doit exister
3. **DLLs** : Toutes les DLLs nécessaires sont incluses automatiquement par cx_Freeze
4. **CAPSImg.dll** : Optionnel, pour le support IPF (peut être ajouté manuellement)

---

## 🔗 Références

- **Dossier source** : `AlignTester/src/greaseweazle-1.23b/`
- **Script PowerShell** : `build/greaseweazle-1.23b-windows/build_windows.ps1`
- **Documentation cx_Freeze** : https://cx-freeze.readthedocs.io/

---

**Dernière mise à jour** : Guide de compilation Windows pour version 1.23b

