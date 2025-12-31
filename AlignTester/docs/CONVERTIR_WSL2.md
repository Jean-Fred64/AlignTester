# Convertir Debian en WSL 2

## ⚠️ Problème

Votre distribution Debian est actuellement en **WSL 1**, mais `usbipd` nécessite **WSL 2** pour fonctionner.

## ✅ Solution : Convertir en WSL 2

### Étape 1 : Vérifier la version actuelle

Dans PowerShell Windows (pas en admin nécessaire) :

```powershell
wsl --list --verbose
```

Vous devriez voir :
```
  Debian    Running    1
```

### Étape 2 : Convertir en WSL 2

**Option A : Script automatisé (recommandé)**

Dans PowerShell Windows (en tant qu'administrateur) :

```powershell
cd "S:\Divers SSD M2\Test D7\Aligntester\AlignTester"
powershell -ExecutionPolicy Bypass -File "scripts\convert_to_wsl2.ps1"
```

**Option B : Commandes manuelles**

Dans PowerShell Windows (en tant qu'administrateur) :

```powershell
# Arrêter WSL si nécessaire
wsl --shutdown

# Convertir Debian en WSL 2
wsl --set-version Debian 2
```

**Note** : Cette conversion peut prendre quelques minutes. Ne fermez pas la fenêtre PowerShell.

### Étape 3 : Vérifier la conversion

```powershell
wsl --list --verbose
```

Vous devriez maintenant voir :
```
  Debian    Running    2
```

### Étape 4 : Redémarrer WSL

```powershell
# Redémarrer WSL
wsl --shutdown
wsl -d Debian
```

---

## 🔄 Alternative : Utiliser directement gw.exe Windows

Si vous préférez ne pas convertir en WSL 2, vous pouvez utiliser directement `gw.exe` Windows qui fonctionne avec COM10 :

```powershell
cd "S:\Divers SSD M2\Test D7\Greaseweazle\greaseweazle-1.23b"
.\gw.exe info
.\gw.exe align --device COM10 --tracks c=40:h=0 --reads 10
```

---

## 📝 Notes

- **WSL 2** est plus performant et supporte plus de fonctionnalités
- La conversion est **irréversible** (mais vous pouvez toujours créer une nouvelle distribution WSL 1 si besoin)
- Après la conversion, `usbipd attach` devrait fonctionner

---

## 🔗 Références

- [Documentation WSL](https://docs.microsoft.com/en-us/windows/wsl/)
- [Migrer vers WSL 2](https://docs.microsoft.com/en-us/windows/wsl/install-manual#step-6---set-your-distribution-version-to-wsl-1-or-wsl-2)

