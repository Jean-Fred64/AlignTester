# Utilisation de Greaseweazle depuis WSL

Ce guide explique comment utiliser le device Greaseweazle depuis un environnement WSL (Windows Subsystem for Linux).

---

## ⚠️ Prérequis Importants

### 1. WSL 2 est obligatoire pour usbipd

**⚠️ CRITIQUE** : `usbipd` nécessite **WSL 2**. Si votre distribution est en WSL 1, elle ne fonctionnera pas.

**Vérifier la version** :
```powershell
# Dans PowerShell Windows
wsl --list --verbose
```

Si vous voyez `Debian Running 1` (ou autre distribution avec version 1), vous devez convertir en WSL 2 :

```powershell
# Dans PowerShell Windows (en tant qu'administrateur)
wsl --shutdown
wsl --set-version Debian 2
```

**Note** : La conversion peut prendre quelques minutes. Vérifiez ensuite avec `wsl --list --verbose`.

Voir aussi : [docs/CONVERTIR_WSL2.md](CONVERTIR_WSL2.md)

### 2. WSL doit être en cours d'exécution

**WSL doit être en cours d'exécution** pour que `usbipd attach` fonctionne. Gardez au moins **un terminal WSL ouvert** pendant l'attachement et l'utilisation du device.

---

## 📋 Options Disponibles

Vous avez plusieurs options pour utiliser Greaseweazle depuis WSL :

1. **Via usbipd** : Connecter le device USB à WSL (nécessite usbipd)
2. **Utiliser gw.exe Windows directement** : Plus simple, fonctionne avec COM10
3. **Via /dev/ttyS* (port COM)** : Accéder directement au port COM depuis WSL (avancé)

---

## 🔌 Option 1 : Via usbipd (Recommandé pour utilisation native Linux)

Cette méthode permet de connecter le device USB directement à WSL, où il apparaîtra comme `/dev/ttyACM0`.

### Installation

1. **Installer usbipd sur Windows** (en tant qu'administrateur dans PowerShell) :
```powershell
# Dans PowerShell en tant qu'administrateur
winget install usbipd
```

2. **Installer le client usbipd dans WSL** :

**Pour Debian/Ubuntu** :
```bash
# Dans WSL
sudo apt update
sudo apt install usbip hwdata
```

**Note pour Ubuntu** : Si vous êtes sur Ubuntu et que `usbip` n'est pas disponible, utilisez :
```bash
sudo apt install linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*/usbip 20
```

**Vérification** :
```bash
which usbip
usbip version
```

### Utilisation

**⚠️ IMPORTANT : Gardez un terminal WSL ouvert pendant toute la procédure !**

1. **Sur Windows (PowerShell en admin)** :
```powershell
# Lister les devices USB
usbipd list

# Attacher le device Greaseweazle à WSL (2 étapes nécessaires)
# Étape 1: Lier (bind) le device (une seule fois)
usbipd bind --busid <BUSID>

# Étape 2: Attacher à WSL
usbipd attach --wsl --busid <BUSID>
```

**Note** : Le `bind` doit être fait une première fois. Ensuite, vous pouvez utiliser directement `attach` lors des prochaines utilisations.

2. **Dans WSL**, le device devrait apparaître comme `/dev/ttyACM0` ou similaire :
```bash
# Vérifier que le device est disponible
ls -la /dev/ttyACM*

# Utiliser avec gw
gw info
gw align --device /dev/ttyACM0 --tracks c=40:h=0 --reads 10
```

### Détacher le device

```powershell
# Sur Windows (PowerShell en admin)
usbipd detach --busid <BUSID>
```

---

## 💻 Option 2 : Utiliser directement `gw.exe` depuis WSL

Vous pouvez appeler directement l'exécutable Windows depuis WSL.

### Configuration

```bash
# Dans WSL, créer un alias ou wrapper
alias gw="cmd.exe /c gw.exe"

# Ou utiliser directement avec le chemin complet
/mnt/s/Divers\ SSD\ M2/Test\ D7/Greaseweazle/greaseweazle-1.23/gw.exe info
```

### Exemple d'utilisation

```bash
# Depuis WSL
cd /mnt/s/'Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23b'
./gw.exe info

# Pour align
./gw.exe align --device COM10 --tracks c=40:h=0 --reads 10
```

**Note** : Les chemins Windows sont accessibles depuis WSL via `/mnt/<lettre>/`. Le `S:` devient `/mnt/s/`.

---

## 🔧 Option 3 : Accéder directement au port COM depuis WSL (Avancé)

Les ports COM Windows peuvent être accessibles depuis WSL, mais cela nécessite une configuration spéciale.

### Via /dev/ttyS* (Ports série virtuels)

```bash
# Le port COM10 Windows peut correspondre à /dev/ttyS9 dans WSL
# (COM1 = /dev/ttyS0, COM2 = /dev/ttyS1, ..., COM10 = /dev/ttyS9)

# Vérifier les ports disponibles
ls -la /dev/ttyS*

# Tester la connexion (nécessite des permissions)
sudo chmod 666 /dev/ttyS9
```

**Limitations** :
- Pas tous les ports COM sont accessibles de cette manière
- Nécessite des permissions spéciales
- Peut ne pas fonctionner avec tous les devices USB

---

## 📊 Utilisation de la commande `align`

La commande `align` est l'une des fonctionnalités les plus importantes de Greaseweazle pour les tests d'alignement de têtes. Elle lit répétitivement la même piste pour faciliter l'alignement.

### Syntaxe de base

```bash
gw align --tracks TSPEC [OPTIONS]
```

### Exemples d'utilisation depuis WSL

#### Avec usbipd (device `/dev/ttyACM0`)

```bash
# Alignement basique : piste 40, tête 0, 10 lectures
gw align --device /dev/ttyACM0 --tracks c=40:h=0 --reads 10

# Plus de lectures pour meilleure statistique
gw align --device /dev/ttyACM0 --tracks c=40:h=0 --reads 20 --revs 5

# Alternance entre têtes 0 et 1 sur le même cylindre
gw align --device /dev/ttyACM0 --tracks c=40:h=0,1 --reads 10

# Avec format spécifique pour décodage
gw align --device /dev/ttyACM0 --tracks c=0:h=0 --format ibm.1440 --reads 15

# Mode flux brut (analyse directe)
gw align --device /dev/ttyACM0 --tracks c=40:h=0 --raw --reads 10
```

#### Avec gw.exe Windows (port COM)

```bash
# Depuis WSL, utiliser gw.exe Windows
cd /mnt/s/'Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23b'
./gw.exe align --device COM10 --tracks c=40:h=0 --reads 10

# Avec format
./gw.exe align --device COM10 --tracks c=0:h=0 --format ibm.1440 --reads 15

# Mode brut
./gw.exe align --device COM10 --tracks c=40:h=0 --raw --reads 10
```

### Spécification des pistes (TSPEC)

La syntaxe `TSPEC` permet de spécifier précisément les pistes à lire :

- **Piste unique** : `c=40:h=0` (cylindre 40, tête 0)
- **Plusieurs têtes** : `c=40:h=0,1` (cylindre 40, têtes 0 et 1 en alternance)
- **Plage de cylindres** : `c=0-7,9-12:h=0-1` (cylindres 0-7 et 9-12, toutes les têtes)
- **Avec double-step** : `c=40:h=0:step=2`

### Options principales

| Option | Description | Défaut |
|--------|-------------|--------|
| `--reads N` | Nombre de lectures à effectuer | 10 |
| `--revs N` | Nombre de révolutions par lecture | 3 |
| `--format FORMAT` | Format de disquette (ex: `ibm.1440`) | - |
| `--raw` | Mode flux brut (pas de décodage) | False |
| `--device DEVICE` | Port série (`/dev/ttyACM0` ou `COM10`) | Auto |
| `--drive DRIVE` | Lecteur (A, B, 0, 1, 2, 3) | A |

### Interprétation des résultats

**En mode brut (`--raw`)** :
```
T40.0: 50000 flux transitions, 200.0ms per rev, 300.0 RPM
T40.0: 50010 flux transitions, 200.1ms per rev, 299.9 RPM
T40.0: 49995 flux transitions, 199.9ms per rev, 300.1 RPM
```
- Les variations dans le nombre de transitions indiquent la stabilité
- Les variations de RPM indiquent la stabilité de la vitesse de rotation

**Avec format décodé** :
```
T40.0: 18 sectors, 0 missing, 0 bad from 50000 flux transitions, 200.0ms per rev
T40.0: 18 sectors, 0 missing, 0 bad from 50010 flux transitions, 200.1ms per rev
T40.0: 18 sectors, 1 missing, 0 bad from 49995 flux transitions, 200.2ms per rev
```
- Le nombre de secteurs détectés doit être constant
- Les secteurs manquants (`missing`) ou mauvais (`bad`) indiquent des problèmes d'alignement

### Conseils d'utilisation

1. **Commencer par le mode brut** : Utilisez `--raw` pour une analyse directe sans décodage
2. **Augmenter les lectures** : Utilisez `--reads 20` ou plus pour de meilleures statistiques
3. **Plusieurs révolutions** : Utilisez `--revs 5` pour plus de données par lecture
4. **Tester les deux têtes** : Utilisez `h=0,1` pour alterner entre les têtes
5. **Vérifier la connexion** : Utilisez `gw info` avant de commencer

### Formats de disquettes supportés

La commande supporte tous les formats Greaseweazle. Les plus courants :
- `ibm.1440` : Disquette 1.44 MB (3.5")
- `ibm.720` : Disquette 720 KB (3.5")
- `ibm.360` : Disquette 360 KB (5.25")
- `amiga.amigados` : Format Amiga
- `raw.250` : Flux brut 250 kbps

Voir la documentation complète dans `DOCUMENTATION_GREASEWEAZLE.md` pour la liste complète.

---

## 🛠️ Scripts Utilitaires

### Lister les devices USB et ports COM

```powershell
# Sur Windows (PowerShell)
cd "S:\Divers SSD M2\Test D7\Aligntester\AlignTester"
powershell -ExecutionPolicy Bypass -File "scripts\list_com_ports.ps1"
```

### Attacher automatiquement le Greaseweazle

```powershell
# Sur Windows (PowerShell admin)
cd "S:\Divers SSD M2\Test D7\Aligntester\AlignTester"
powershell -ExecutionPolicy Bypass -File "scripts\attach_greaseweazle.ps1"
```

### Vérifier la connexion dans WSL

```bash
# Dans WSL
cd ~/Aligntester/AlignTester
./scripts/connect_greaseweazle_wsl.sh
```

---

## 📝 Dépannage

### Erreur : "There is no WSL 2 distribution running"

**Causes possibles** :

1. **Votre distribution est en WSL 1** (la cause la plus probable) :
   ```powershell
   # Vérifier
   wsl --list --verbose
   
   # Si vous voyez "Debian Running 1", convertissez en WSL 2 :
   wsl --shutdown
   wsl --set-version Debian 2
   ```

2. **WSL n'est pas actif** : Gardez au moins un terminal WSL ouvert. WSL doit être actif pour que usbipd puisse attacher un device.

   ```bash
   # Dans WSL, gardez ce terminal ouvert
   # Puis dans PowerShell Windows (admin), réessayez :
   usbipd attach --wsl --busid 3-1
   ```

### Device non détecté dans WSL

1. Vérifiez que le device est bien attaché :
   ```powershell
   usbipd list
   # Le device devrait avoir "Attached - Debian" (ou votre distro WSL)
   ```

2. Vérifiez dans WSL :
   ```bash
   ls -la /dev/ttyACM*
   dmesg | tail -20  # Voir les messages du noyau
   ```

3. Redémarrez l'attachement :
   ```powershell
   usbipd detach --busid 3-1
   usbipd attach --wsl --busid 3-1
   ```

### Permissions insuffisantes

```bash
# Ajouter votre utilisateur au groupe dialout
sudo usermod -a -G dialout $USER

# Déconnectez-vous et reconnectez-vous pour que les changements prennent effet
# Ou utilisez newgrp dialout
newgrp dialout
```

---

## 🔗 Références

- [usbipd-win documentation](https://github.com/dorssel/usbipd-win)
- [WSL USB support](https://github.com/dorssel/usbipd-win/wiki/WSL-support)
- [Greaseweazle documentation](https://github.com/keirf/Greaseweazle)
