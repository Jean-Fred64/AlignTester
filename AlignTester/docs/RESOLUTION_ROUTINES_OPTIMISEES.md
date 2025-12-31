# Résolution : Routines Optimisées Non Trouvées

## 🔴 Problème

Vous voyez le message d'avertissement :
```
*** WARNING: Optimised data routines not found: Run scripts/setup.sh
```

## ✅ Solution

### Sous Windows

#### Option 1 : Script PowerShell (Recommandé)

1. Ouvrez PowerShell dans le dossier source de Greaseweazle :
   ```powershell
   cd "C:\chemin\vers\AlignTester\src\greaseweazle-1.23b"
   ```

2. Exécutez le script :
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup.ps1
   ```

   Ou depuis le dossier `scripts` :
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
   ```

#### Option 2 : Script Batch

1. Ouvrez l'invite de commande dans le dossier source :
   ```cmd
   cd "C:\chemin\vers\AlignTester\src\greaseweazle-1.23b"
   ```

2. Exécutez le script :
   ```cmd
   .\scripts\setup.bat
   ```

#### Option 3 : Installation manuelle

1. Installez Visual Studio Build Tools (recommandé) :
   - Téléchargez depuis : https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
   - Installez le composant "C++ build tools"

2. Ouvrez PowerShell et exécutez :
   ```powershell
   cd "C:\chemin\vers\AlignTester\src\greaseweazle-1.23b"
   $env:SETUPTOOLS_SCM_PRETEND_VERSION = "1.23b"
   python -m pip install -e . --force-reinstall
   ```

### Sous Linux/WSL

1. Allez dans le dossier source :
   ```bash
   cd /home/jean-fred/Aligntester/AlignTester/src/greaseweazle-1.23b
   ```

2. Exécutez le script :
   ```bash
   ./setup.sh
   ```

   Ou depuis le dossier `scripts` :
   ```bash
   ./scripts/setup.sh
   ```

## 📋 Prérequis

### Windows

- **Python 3.8+** installé et dans le PATH
- **Compilateur C/C++** :
  - Visual Studio Build Tools (recommandé) avec les composants C++
  - Ou MinGW-w64

### Linux/WSL

- **Python 3.8+**
- **GCC** (compilateur C) : `sudo apt install gcc` (Ubuntu/Debian)

## ⚠️ Important

- Les routines optimisées améliorent les **performances** mais ne sont **pas obligatoires**
- Greaseweazle fonctionnera sans elles, mais sera plus lent
- Si vous n'avez pas de compilateur C/C++, vous pouvez ignorer l'avertissement

## 🔍 Vérification

Après avoir exécuté le script, vérifiez que les routines sont disponibles :

**Windows (PowerShell)** :
```powershell
python -c "from greaseweazle.optimised import optimised; print('OK')"
```

**Linux/WSL** :
```bash
python3 -c "from greaseweazle.optimised import optimised; print('OK')"
```

Si vous voyez `OK`, les routines optimisées sont compilées et disponibles ! ✅

## 🆘 Problèmes courants

### "Python non trouvé"
- Vérifiez que Python est installé et dans le PATH
- Sous Windows, essayez `py` au lieu de `python`

### "GCC/compilateur non trouvé"
- Installez Visual Studio Build Tools (Windows) ou GCC (Linux)
- Ou ignorez l'avertissement si vous n'avez pas besoin des performances optimales

### "Permission denied" (Linux)
- Utilisez `chmod +x setup.sh` pour rendre le script exécutable
- Ou exécutez avec `bash setup.sh`

