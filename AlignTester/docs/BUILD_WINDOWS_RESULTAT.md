# Résultat de la compilation Windows 1.23b

## ✅ Vérifications préalables

Toutes les vérifications de conformité avec le projet original ont été effectuées :

1. **✅ scripts/win identiques** : Les fichiers `setup.py` et `gw.py` sont identiques à ceux du projet original
2. **✅ setup.py conforme** : La seule différence est la gestion de la version (normal pour 1.23b)
3. **✅ Fichiers 1.23b présents** :
   - `align.py` présent dans `src/greaseweazle/tools/`
   - `'align'` ajouté dans `cli.py`
   - `__init__.py` avec version `1.23b`

**Conclusion** : La préparation est conforme au projet Greaseweazle original avec les modifications nécessaires pour la version 1.23b.

---

## ⚠️ Résultat de la compilation avec Python 3.13

### Statut : Partiellement réussi

La compilation avec cx_Freeze a été lancée et a créé les fichiers, **mais** il y a un problème d'exécution avec Python 3.13.

### Problème identifié

```
ModuleNotFoundError: No module named '__startup__'
```

Ce problème est connu avec **cx_Freeze et Python 3.13**. L'exécutable `gw.exe` a été créé mais ne peut pas s'exécuter correctement.

---

## 🔧 Solution : Script pour Python 3.11/3.12

Un nouveau script a été créé : **`build_windows_py311.ps1`**

Ce script :
- ✅ Détecte automatiquement Python 3.11 ou 3.12
- ✅ Utilise la bonne version pour la compilation
- ✅ Vérifie que tout fonctionne après compilation
- ✅ Crée un dossier de distribution complet

### Utilisation

```powershell
powershell -ExecutionPolicy Bypass -File "build\greaseweazle-1.23b-windows\build_windows_py311.ps1"
```

---

## 🔧 Autres Solutions recommandées

### Option 1 : Utiliser Python 3.11 ou 3.12 (Recommandé)

La compilation devrait fonctionner avec Python 3.11 ou 3.12, qui sont les versions testées par Greaseweazle.

**Installation** :
1. Téléchargez Python 3.11 ou 3.12 depuis :
   - Python 3.11 : https://www.python.org/downloads/release/python-3119/
   - Python 3.12 : https://www.python.org/downloads/release/python-31212/ (dernière version 3.12.12)
2. Installez en cochant "Add Python to PATH"
3. Utilisez le script `build_windows_py311.ps1` qui détectera automatiquement la bonne version

### Option 2 : Utiliser le binaire Windows existant

En attendant, vous pouvez utiliser le `gw.exe` Windows existant (version 1.23) que vous avez déjà, qui fonctionne avec votre device sur COM10.

Pour tester la commande `align`, vous devrez :
- Soit compiler avec Python 3.11/3.12 (recommandé)
- Soit attendre une mise à jour de cx_Freeze compatible avec Python 3.13
- Soit utiliser la version Linux 1.23b compilée dans WSL

### Option 3 : Compiler avec Visual Studio Build Tools

Si vous installez **Visual Studio Build Tools** (pour compiler l'extension C), vous pouvez installer le package complet et utiliser la méthode officielle :

```powershell
cd "src\greaseweazle-1.23b"
$env:SETUPTOOLS_SCM_PRETEND_VERSION = "1.23b"
py -3.11 -m pip install -e .  # Utiliser Python 3.11
cd scripts\win
py -3.11 setup.py build
```

---

## 📁 Fichiers générés

Les fichiers de compilation sont dans :
```
AlignTester/src/greaseweazle-1.23b/scripts/win/build/exe.win-amd64-3.13/
```

Avec Python 3.11/3.12, les fichiers seront dans :
```
AlignTester/src/greaseweazle-1.23b/scripts/win/build/exe.win-amd64-3.11/
# ou
AlignTester/src/greaseweazle-1.23b/scripts/win/build/exe.win-amd64-3.12/
```

Contenu :
- `gw.exe` - Exécutable principal
- `python*.dll` - DLL Python
- `lib/` - Modules Python et données
  - `greaseweazle/` - Module complet avec `align.py`
  - `greaseweazle.data/` - Fichiers de configuration

Le script `build_windows_py311.ps1` copie automatiquement tous les fichiers dans :
```
AlignTester/build/greaseweazle-1.23b-windows/greaseweazle-1.23b/
```

---

## 📝 Prochaines étapes

1. **Utiliser le script `build_windows_py311.ps1`** avec Python 3.11/3.12 (meilleure option)
2. **Vérifier que gw.exe fonctionne** avec la commande `align`
3. **Tester avec votre device** Greaseweazle sur COM10

---

**Date** : 2024-12-21  
**Script créé** : `build_windows_py311.ps1` pour Python 3.11/3.12  
**Statut** : Script prêt à utiliser avec Python 3.11/3.12
