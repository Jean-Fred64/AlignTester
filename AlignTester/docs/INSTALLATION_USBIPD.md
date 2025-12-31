# Installation de usbipd pour Windows

## 📋 Prérequis

- Windows 10/11 avec winget (inclut depuis Windows 10 1809)
- PowerShell en tant qu'administrateur

---

## 🚀 Installation

### Méthode 1 : Via winget (Recommandé)

1. **Ouvrez PowerShell en tant qu'administrateur** :
   - Clic droit sur PowerShell → "Exécuter en tant qu'administrateur"

2. **Installez usbipd** :
   ```powershell
   winget install usbipd
   ```

3. **Vérifiez l'installation** :
   ```powershell
   usbipd --version
   ```

### Méthode 2 : Via le script PowerShell

1. **Exécutez le script** :
   ```powershell
   cd "S:\Divers SSD M2\Test D7\Aligntester\AlignTester"
   powershell -ExecutionPolicy Bypass -File "scripts\install_usbipd.ps1"
   ```

---

## ✅ Vérification

Après l'installation, testez :

```powershell
# Lister les devices USB
usbipd list
```

Vous devriez voir une liste des devices USB connectés, dont votre Greaseweazle (COM10).

---

## 🔍 Trouver le BUSID du Greaseweazle

1. **Listez les devices** :
   ```powershell
   usbipd list
   ```

2. **Cherchez votre device** :
   - Recherchez "Greaseweazle" ou "COM10" dans la liste
   - Notez le BUSID (format: `1-5`, `2-3`, etc.)

3. **Exemple de sortie** :
   ```
   BUSID  VID:PID    DEVICE                                                        STATE
   1-5    1209:4D69  Périphérique série USB (COM10)                              Not shared
   ```
   Dans cet exemple, le BUSID est `1-5`.

---

## 📝 Attacher le device à WSL

Une fois le BUSID identifié :

```powershell
# Attacher le device à WSL
usbipd attach --wsl --busid 1-5
```

Remplacez `1-5` par votre BUSID.

---

## ⚠️ Notes

- **Redémarrer PowerShell** : Après l'installation, vous devrez peut-être redémarrer PowerShell pour que `usbipd` soit dans le PATH
- **Permissions administrateur** : `usbipd` nécessite des droits administrateur pour fonctionner
- **Alternative** : Si vous avez des difficultés avec usbipd, vous pouvez utiliser directement `gw.exe` Windows qui fonctionne avec COM10

---

## 🔄 Détacher le device

Pour détacher le device de WSL :

```powershell
usbipd detach --busid 1-5
```

---

## 📚 Références

- Documentation usbipd : https://github.com/dorssel/usbipd-win
- Installation : https://github.com/dorssel/usbipd-win/wiki/WSL-support

