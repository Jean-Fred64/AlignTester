# Correction du problème Greaseweazle dans la version standalone

## 🔴 Problème identifié

Lors de l'exécution de `gw.exe` dans la version standalone Windows, l'erreur suivante se produit :

```
Fatal Python error: init_fs_encoding: failed to get the Python codec of the filesystem encoding
ModuleNotFoundError: No module named 'encodings'
```

## 🔍 Cause

Le binaire `gw.exe` est un exécutable Python créé avec **cx_Freeze** qui nécessite :
1. L'exécutable `gw.exe` lui-même
2. Les DLLs nécessaires (Visual C++ Runtime, Python DLL)
3. **Le dossier `lib/`** qui contient tous les modules Python de base, notamment :
   - `encodings/` (module essentiel pour l'encodage des fichiers)
   - `greaseweazle/` (le package Greaseweazle)
   - Tous les autres modules Python nécessaires

Le script `build_standalone.py` n'incluait que `gw.exe` et les DLLs, mais **pas le dossier `lib/`**, ce qui causait l'erreur.

## ✅ Solution

Le script `build_standalone.py` a été modifié pour inclure récursivement :
- ✅ `gw.exe` et toutes les DLLs (comme avant)
- ✅ **Tous les fichiers du dossier `lib/`** (nouveau)
- ✅ **Tous les fichiers du dossier `share/`** (licences, etc.)

### Modifications apportées

Dans `AlignTester/scripts/build_standalone.py`, la section "Greaseweazle" a été mise à jour pour :

1. **Inclure récursivement le dossier `lib/`** :
   ```python
   lib_dir = greaseweazle_dir / "lib"
   if lib_dir.exists() and lib_dir.is_dir():
       lib_files = []
       for item in lib_dir.rglob("*"):
           if item.is_file():
               rel_path = item.relative_to(lib_dir)
               target_lib_dir = f"{target_dir}/lib/{rel_path.parent}"
               lib_files.append((str(item.resolve()), target_lib_dir))
       greaseweazle_files.extend(lib_files)
   ```

2. **Inclure récursivement le dossier `share/`** (si présent)

3. **Préserver la structure des dossiers** pour que `gw.exe` puisse trouver les modules dans `lib/`

## 📦 Structure dans le build standalone

Après le build, la structure sera :

```
aligntester-standalone-windows-x64/
├── aligntester.exe
├── _internal/
│   ├── ...
│   └── greaseweazle/
│       ├── gw.exe
│       ├── *.dll
│       ├── lib/
│       │   ├── encodings/
│       │   ├── greaseweazle/
│       │   └── ... (tous les modules Python)
│       └── share/
│           └── ...
```

## 🔧 Vérification

Pour vérifier que le problème est résolu :

1. **Rebuild la version standalone** :
   ```bash
   python AlignTester/scripts/build_standalone.py
   ```

2. **Vérifier que le dossier `lib/` est inclus** :
   - Dans `build_standalone/dist/windows/aligntester/_internal/greaseweazle/`
   - Le dossier `lib/` doit contenir `encodings/` et `greaseweazle/`

3. **Tester `gw.exe`** :
   ```cmd
   cd _internal\greaseweazle
   gw.exe --version
   ```
   
   Cette commande devrait maintenant fonctionner sans erreur.

## 📝 Notes

- Le dossier `lib/` est essentiel car il contient tous les modules Python nécessaires à l'exécution de `gw.exe`
- La structure des dossiers doit être préservée car `gw.exe` cherche les modules dans `lib/` relatif à son emplacement
- Cette solution fonctionne car PyInstaller copie les fichiers dans `_internal/` en préservant la structure des dossiers

## 🔗 Références

- [cx_Freeze Documentation](https://cx-freeze.readthedocs.io/)
- [PyInstaller datas documentation](https://pyinstaller.org/en/stable/spec-files.html#adding-files-to-the-bundle)
