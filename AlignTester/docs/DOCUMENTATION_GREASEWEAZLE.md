# Documentation Technique - Greaseweazle

## Vue d'ensemble

Greaseweazle est un projet open-source permettant d'interfacer des lecteurs de disquettes anciens avec des machines modernes via une connexion USB. Il offre un accès au niveau du flux brut (raw flux) des disquettes, ce qui le rend particulièrement adapté pour des tâches avancées telles que l'alignement des têtes de lecture, la préservation de formats non-standard, et la récupération de données.

**Dépôt GitHub** : https://github.com/keirf/greaseweazle

## Architecture de communication USB

### Interface matérielle

La carte Greaseweazle se connecte à l'ordinateur hôte via USB et apparaît comme un **périphérique série virtuel** (USB CDC/ACM). La communication s'effectue via un protocole série bidirectionnel.

### Identification du périphérique

Selon le système d'exploitation :

- **Windows** : Apparaît comme un port COM (ex: `COM3`, `COM6`)
  - Pilote : `usbser.sys` (inclus dans Windows)
  - Peut nécessiter Zadig pour certains modèles

- **macOS** : Apparaît comme `/dev/cu.usbmodem*` ou `/dev/tty.usbmodem*`
  - Installation via `pipx` ou `pip`

- **Linux** : Apparaît comme `/dev/ttyACM*` ou `/dev/ttyUSB*`
  - Recommandation : Ajouter des règles udev pour accès sans privilèges root

### Protocole de communication

La communication s'effectue via un protocole série avec les caractéristiques suivantes :
- **Vitesse** : 115200 baud (par défaut, peut varier selon le firmware)
- **Bits de données** : 8
- **Parité** : None
- **Bits d'arrêt** : 1
- **Contrôle de flux** : Hardware (RTS/CTS) ou Software (XON/XOFF)

## Outil en ligne de commande : `gw` / `gw.exe`

### Installation

**Linux et macOS** :
```bash
# Installation via pipx (recommandé)
pipx install greaseweazle

# Ou via pip
pip install greaseweazle
```

**Windows** :
- Télécharger la dernière release depuis [GitHub Releases](https://github.com/keirf/greaseweazle/releases)
- Décompresser l'archive ZIP
- Exécuter `gw.exe` depuis le dossier décompressé
- **Avantage** : Pas besoin d'installer Python, tout est inclus dans l'exécutable

### `gw.exe` - Exécutable Windows

**Description** : `gw.exe` est l'exécutable Windows standalone de Greaseweazle. C'est l'équivalent binaire de la commande `gw` disponible sous Linux/macOS.

**Caractéristiques** :
- ✅ Exécutable standalone (pas besoin de Python installé)
- ✅ Toutes les dépendances incluses
- ✅ Utilisation directe depuis le dossier décompressé
- ✅ Même syntaxe que `gw` sous Linux/macOS

**Utilisation** :
```cmd
# Depuis le dossier décompressé
gw.exe --help
gw.exe info
gw.exe read --format ibm.1440 disk.img
gw.exe align --tracks c=40:h=0 --reads 10
```

**Où le trouver** :
- Télécharger depuis : https://github.com/keirf/greaseweazle/releases
- Dernière version : Greaseweazle Tools 1.23 (ou plus récent)
- Le fichier `gw.exe` se trouve dans le dossier décompressé

### Compilation de `gw.exe` avec la commande `align` (PR #592)

Si vous voulez créer votre propre `gw.exe` avec la commande `align` du PR #592 avant qu'elle soit mergée :

#### Méthode 1 : Utiliser PyInstaller (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/keirf/greaseweazle.git
cd greaseweazle

# Récupérer le PR #592
git fetch origin pull/592/head:pr-592-alignment
git checkout pr-592-alignment

# Installer PyInstaller
pip install pyinstaller

# Créer l'exécutable
pyinstaller --onefile --name gw --console src/greaseweazle/tools/gw.py

# L'exécutable sera dans dist/gw.exe
```

#### Méthode 2 : Utiliser Nuitka

```bash
# Installer Nuitka
pip install nuitka

# Compiler
python -m nuitka --onefile --output-filename=gw.exe src/greaseweazle/tools/gw.py
```

#### Méthode 3 : Utiliser cx_Freeze

```bash
# Installer cx_Freeze
pip install cx_Freeze

# Nécessite un fichier setup.py configuré
# (voir documentation cx_Freeze)
```

**Note** : La compilation nécessite Python installé sur Windows. L'exécutable généré sera standalone et pourra être distribué sans Python.

### Structure générale des commandes

**Linux/macOS** :
```bash
gw [OPTIONS_GLOBALES] <COMMANDE> [OPTIONS_COMMANDE] [ARGUMENTS]
```

**Windows** :
```cmd
gw.exe [OPTIONS_GLOBALES] <COMMANDE> [OPTIONS_COMMANDE] [ARGUMENTS]
```

Les deux utilisent exactement la même syntaxe, seule la commande de base change (`gw` vs `gw.exe`).

### Options globales

| Option | Description |
|--------|-------------|
| `--device DEVICE` | Spécifie le port série (ex: `COM3`, `/dev/ttyACM0`) |
| `--drive DRIVE` | Spécifie le lecteur à utiliser (A, B, 0, 1, 2, 3) - Voir section "Sélection de lecteur" ci-dessous |
| `--usb-pipe` | Utilise le pipe USB direct (mode avancé) |
| `--help` | Affiche l'aide générale |
| `--version` | Affiche la version |

## Sélection de lecteur (Drive Select)

Greaseweazle supporte les configurations multi-lecteurs Shugart et IBM/PC. Les commandes `read` et `write` acceptent l'option `--drive N` où **N** est l'un des identifiants suivants : **A**, **B**, **0**, **1**, ou **2** (non sensible à la casse : **a** et **b** sont également acceptés).

**Valeur par défaut** : **A** (IBM/PC Drive A), nécessitant un lecteur IBM/PC et un "câble avec twist" (voir explication ci-dessous).

**⚠️ Note importante** : Greaseweazle F1 ne supporte pas les lecteurs multiples et toute lettre de lecteur non par défaut spécifiée sera ignorée.

### Dépannage : Erreur "Track 0 not found"

Si votre lecteur échoue avec une erreur _Track 0 not found_, vous pouvez avoir :

* **Un lecteur Shugart, strapé pour DS0 (pin 10)** : Connecter avec un câble droit et utiliser `--drive 0`
* **Un lecteur PC utilisé avec un câble droit** : Utiliser `--drive B`

### A, B : IBM/PC

En mode IBM/PC, l'en-tête Greaseweazle agit de la même manière que sur une carte mère PC : Deux lecteurs peuvent être connectés, chacun avec une ligne motor-enable indépendante. Tous les lecteurs PC sont strapés pour drive-select DS1 (pin 12), et un twist de câble est utilisé pour différencier les lecteurs **A** et **B** :

* **A** : Lecteur connecté via un câble avec twist sur les pins 10-16
* **B** : Lecteur connecté via un câble droit (straight ribbon cable)

Un câble à deux lecteurs aura des connecteur(s) avant et après un twist, comme illustré dans la documentation.

**Caractéristiques** :
- Deux lecteurs maximum
- Lignes motor-enable indépendantes
- Tous les lecteurs strapés pour DS1 (pin 12)
- Différenciation via twist de câble

### 0, 1, 2 : Shugart

Jusqu'à trois lecteurs peuvent être connectés, avec des lignes de sélection de lecteur DS0-DS2 sur les pins 10, 12 et 14 respectivement. Tous les lecteurs partagent un signal motor-select commun sur le pin 16. Les lecteurs sont adressés par les identifiants de lecteur **0**, **1**, et **2**.

**Caractéristiques** :
- Jusqu'à trois lecteurs (0, 1, 2)
- Lignes de sélection DS0-DS2 sur pins 10, 12, 14
- Signal motor-select commun sur pin 16
- Adressage par identifiants numériques

**Note** : Certaines configurations peuvent supporter un quatrième lecteur (DS3 sur pin 16), mais cela dépend du matériel et du firmware.

### Résumé des pins

Le tableau ci-dessous résume l'utilisation des pins 10-16 sur les bus respectifs :

| Pin | IBM/PC | Shugart |
|-----|--------|---------|
| 10  | Drive Select (via twist) | DS0 (Drive 0) |
| 12  | DS1 (tous les lecteurs) | DS1 (Drive 1) |
| 14  | - | DS2 (Drive 2) |
| 16  | Motor Enable (indépendant) | Motor Select (commun) |

### Exemples d'utilisation

```bash
# Utiliser le lecteur A (IBM/PC, câble avec twist)
gw read --drive A --format ibm.1440 disk.img

# Utiliser le lecteur B (IBM/PC, câble droit)
gw read --drive B --format ibm.1440 disk.img

# Utiliser le lecteur Shugart 0
gw read --drive 0 --format ibm.1440 disk.img

# Utiliser le lecteur Shugart 1
gw read --drive 1 --format ibm.1440 disk.img

# Avec la commande align
gw align --drive A --tracks c=40:h=0 --reads 10
gw align --drive 0 --tracks c=40:h=0 --reads 10
```

### Documentation de référence

Pour plus de détails et des diagrammes visuels, consultez la [documentation officielle sur GitHub](https://github.com/keirf/greaseweazle/wiki/Drive-Select).

---

## Liste complète des commandes disponibles

### 1. `info` - Informations sur la carte

**Description** : Affiche des informations détaillées sur la carte Greaseweazle connectée.

**Syntaxe** :
```bash
gw info [--device DEVICE]
```

**Exemple** :
```bash
gw info
gw info --device COM3
```

**Sortie typique** :
```
Greaseweazle v1.0
Firmware: v1.2.3
Serial: 12345678
Model: F1
```

**Utilisation pour l'alignement** : Permet de vérifier la connexion et la version du firmware avant de commencer les tests.

---

### 2. `read` - Lecture de disquette

**Description** : Lit le contenu d'une disquette et enregistre les données dans un fichier image.

**Syntaxe** :
```bash
gw read [OPTIONS] OUTPUT_FILE
```

**Options principales** :

| Option | Description |
|--------|-------------|
| `--format FORMAT` | Format de la disquette (ex: `ibm.1440`, `ibm.720`, `amiga.amiga`) |
| `--tracks TRACKS` | Pistes spécifiques à lire (ex: `0-79`, `0,1,2`) |
| `--heads HEADS` | Têtes spécifiques (ex: `0`, `1`, `0-1`) |
| `--revs REVS` | Nombre de révolutions à lire (défaut: 2) |
| `--device DEVICE` | Port série de la carte |
| `--flux` | Lit en mode flux brut (raw flux) |
| `--retries N` | Nombre de tentatives en cas d'erreur |
| `--adjust-speed` | Ajuste automatiquement la vitesse de rotation |

**Exemples** :
```bash
# Lecture standard d'une disquette 1.44MB
gw read --format ibm.1440 disk.img

# Lecture d'une piste spécifique
gw read --tracks 0 --format ibm.1440 track0.img

# Lecture en mode flux brut (pour analyse d'alignement)
gw read --flux --tracks 0-79 disk.flux

# Lecture avec plusieurs révolutions
gw read --revs 5 --tracks 43 track43.img
```

**Utilisation pour l'alignement** : 
- Permet de lire des pistes spécifiques pour tester l'alignement
- Le mode `--flux` donne accès aux données brutes pour analyse précise
- Plusieurs révolutions (`--revs`) permettent de détecter les variations

---

### 3. `write` - Écriture sur disquette

**Description** : Écrit une image de disquette sur une disquette physique.

**Syntaxe** :
```bash
gw write [OPTIONS] INPUT_FILE
```

**Options principales** :

| Option | Description |
|--------|-------------|
| `--format FORMAT` | Format de la disquette |
| `--tracks TRACKS` | Pistes spécifiques à écrire |
| `--heads HEADS` | Têtes spécifiques |
| `--device DEVICE` | Port série de la carte |
| `--flux` | Écrit depuis un fichier flux brut |
| `--erase-first` | Efface la disquette avant écriture |
| `--verify` | Vérifie après écriture |

**Exemples** :
```bash
# Écriture standard
gw write --format ibm.1440 disk.img

# Écriture d'une piste spécifique
gw write --tracks 43 --format ibm.1440 track43.img

# Écriture depuis un fichier flux
gw write --flux disk.flux
```

**Utilisation pour l'alignement** : Permet d'écrire des pistes de test pour vérifier l'alignement.

---

### 4. `erase` - Effacement de disquette

**Description** : Efface le contenu d'une disquette.

**Syntaxe** :
```bash
gw erase [OPTIONS]
```

**Options principales** :

| Option | Description |
|--------|-------------|
| `--tracks TRACKS` | Pistes spécifiques à effacer |
| `--heads HEADS` | Têtes spécifiques |
| `--device DEVICE` | Port série de la carte |

**Exemples** :
```bash
# Effacement complet
gw erase

# Effacement d'une piste spécifique
gw erase --tracks 43
```

**Utilisation pour l'alignement** : Permet de préparer une disquette pour les tests.

---

### 5. `seek` - Positionnement de la tête

**Description** : Positionne la tête de lecture/écriture sur une piste spécifique.

**Syntaxe** :
```bash
gw seek [OPTIONS] TRACK
```

**Options principales** :

| Option | Description |
|--------|-------------|
| `--device DEVICE` | Port série de la carte |
| `--head HEAD` | Tête à utiliser (0 ou 1) |
| `--verify` | Vérifie la position après le seek |

**Exemples** :
```bash
# Se positionner sur la piste 0
gw seek 0

# Se positionner sur la piste 43, tête 1
gw seek --head 1 43

# Se positionner et vérifier
gw seek --verify 43
```

**Utilisation pour l'alignement** : **CRITIQUE** - Permet de positionner précisément la tête pour les tests d'alignement. C'est l'équivalent de la fonction `seek()` d'ImageDisk.

---

### 6. `align` - Test d'alignement des têtes ⭐

**Description** : Lit répétitivement la même piste pour faciliter l'alignement des têtes de lecture. Cette commande automatise le processus de test d'alignement similaire à la fonction `align()` d'ImageDisk.

**⚠️ Note** : Cette commande est disponible depuis la version 1.23b de Greaseweazle.

**Syntaxe générale** :
```bash
gw align [OPTIONS]
```

**⚠️ Avertissement** : Si vous voyez le message `*** WARNING: Optimised data routines not found: Run scripts/setup.sh`, cela signifie que les routines optimisées ne sont pas disponibles. Cela n'empêche pas l'utilisation de la commande, mais peut affecter les performances.

**🔧 Résolution du problème** :

- **Sous Linux/WSL** : Exécutez `./setup.sh` dans le dossier source de Greaseweazle
- **Sous Windows** : Exécutez `.\setup.ps1` ou `.\scripts\setup.ps1` dans PowerShell, ou `.\scripts\setup.bat` dans l'invite de commande

**Note** : Sous Windows, vous devez avoir installé Visual Studio Build Tools (avec les composants C++) ou MinGW-w64 pour compiler les routines optimisées.

**Paramètres requis** :

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `--tracks TSPEC` | Piste(s) à lire (requis) | `c=40:h=0` ou `c=40:h=0,1` |

**Options principales** :

| Option | Description | Défaut |
|--------|-------------|--------|
| `-h, --help` | Affiche l'aide de la commande | - |
| `--device DEVICE` | Nom du périphérique (port COM/série) | Auto-détection |
| `--drive DRIVE` | Lecteur à utiliser | A |
| `--diskdefs DISKDEFS` | Fichier de définitions de disques | - |
| `--format FORMAT` | Format de disquette pour décodage | - |
| `--revs N` | Nombre de révolutions par tentative | 3 |
| `--tracks TSPEC` | Piste(s) à lire (requis) | - |
| `--reads N` | Nombre de fois à lire la piste | 10 |
| `--raw` | Lecture en flux brut (pas de décodage) | False |
| `--fake-index SPEED` | Index factices à la vitesse SPEED | - |
| `--hard-sectors` | Lecture depuis un disque à secteurs durs | False |
| `--adjust-speed SPEED` | Ajuster les données de piste à la vitesse effective SPEED | - |
| `--pll PLLSPEC` | Surcharge manuelle des paramètres PLL | - |
| `--densel LEVEL, --dd LEVEL` | Sélection de densité sur pin 2 (H, L) | - |
| `--gen-tg43` | Générer signal TG43 pour lecteur 8 pouces sur pin 2 depuis piste 60. Active le filtre de postcompensation | False |
| `--reverse` | Inverser les données de piste (disque retourné) | False |

**Formats de spécification détaillés** :

#### DRIVE (Identifiant de lecteur)
Spécifie le lecteur et le bus :
- `0 | 1 | 2 | 3` : Unité sur bus Shugart
- `A | B` : Unité sur bus IBM/PC

#### SPEED (Vitesse de rotation)
Temps de rotation de la piste spécifié comme :
- `<N>rpm` : Tours par minute (ex: `300rpm`)
- `<N>ms` : Millisecondes (ex: `200ms`)
- `<N>us` : Microsecondes (ex: `200000us`)
- `<N>ns` : Nanosecondes
- `<N>scp` : Format SCP
- `<N>` : Nombre seul (interprété selon le contexte)

#### TSPEC (Spécification de pistes)
Liste séparée par deux-points (`:`) contenant :
- `c=SET` : Ensemble de cylindres à accéder
- `h=SET` : Ensemble de têtes (côtés) à accéder
- `step=[0-9]` : Nombre de pas physiques de tête entre cylindres
- `hswap` : Échanger les têtes physiques du lecteur
- `h[01].off=[+-][0-9]` : Décalages de cylindre physique par tête

**SET** est une liste séparée par virgules d'entiers et de plages d'entiers.

**Exemples de TSPEC** :
- `c=40:h=0` : Cylindre 40, tête 0 uniquement
- `c=0-7,9-12:h=0-1` : Cylindres 0-7 et 9-12, toutes les têtes
- `c=40:h=0,1` : Cylindre 40, têtes 0 et 1 (alternance)
- `c=40:h=0:step=2` : Cylindre 40, tête 0, avec double-step

**Note importante** : `TSPEC` peut spécifier une seule piste (ex: `c=40:h=0`) ou plusieurs têtes sur le même cylindre (ex: `c=40:h=0,1`) pour alterner entre les têtes.

#### PLLSPEC (Paramètres PLL)
Liste séparée par deux-points (`:`) contenant :
- `period=PCT` : Ajustement de période en pourcentage de l'erreur de phase
- `phase=PCT` : Ajustement de phase en pourcentage de l'erreur de phase
- `lowpass=USEC` : Filtrer les périodes de flux plus courtes que USEC

**Défauts** : `period=5:phase=60` (pas de filtre lowpass)

**Exemples de PLLSPEC** :
- `period=5:phase=60` : Paramètres par défaut
- `period=10:phase=70:lowpass=2.5` : Ajustements personnalisés avec filtre

**Exemples d'utilisation** :

```bash
# Alignement basique : lit la piste 40, tête 0, 10 fois
gw align --tracks c=40:h=0

# Plus de lectures pour meilleure statistique
gw align --tracks c=40:h=0 --reads 20 --revs 5

# Alternance entre têtes 0 et 1 sur le même cylindre
gw align --tracks c=40:h=0,1 --reads 10

# Avec format spécifique pour décodage
gw align --tracks c=0:h=0 --format ibm.1440 --reads 15

# Mode flux brut (analyse directe)
gw align --tracks c=40:h=0 --raw --reads 10

# Pour lecteur 8 pouces avec signal TG43
gw align --tracks c=40:h=0 --gen-tg43 --reads 10

# Avec ajustement de vitesse
gw align --tracks c=40:h=0 --adjust-speed 300rpm --reads 10

# Avec paramètres PLL personnalisés
gw align --tracks c=40:h=0 --pll period=10:phase=70:lowpass=2.5 --reads 10

# Pour disque à secteurs durs
gw align --tracks c=0:h=0 --hard-sectors --reads 10

# Avec sélection de densité
gw align --tracks c=40:h=0 --densel H --reads 10

# Spécifier le lecteur B
gw align --drive B --tracks c=40:h=0 --reads 10

# Spécifier le port COM
gw align --device COM10 --tracks c=40:h=0 --reads 10

# Plage de cylindres avec toutes les têtes
gw align --tracks c=0-7,9-12:h=0-1 --reads 5
```

**Formats de disquettes supportés** :

La commande `align` supporte tous les formats de disquettes reconnus par Greaseweazle. Voici la liste complète des formats disponibles (version 1.23b) :

**Acorn** :
- `acorn.adfs.160`, `acorn.adfs.1600`, `acorn.adfs.320`, `acorn.adfs.640`, `acorn.adfs.800`
- `acorn.dfs.ds`, `acorn.dfs.ds80`, `acorn.dfs.ss`, `acorn.dfs.ss80`

**Akai** :
- `akai.1600`, `akai.800`

**Amiga** :
- `amiga.amigados`, `amiga.amigados_hd`

**Apple II** :
- `apple2.appledos.140`, `apple2.nofs.140`, `apple2.prodos.140`

**Atari** :
- `atari.130`, `atari.90`

**Atari ST** :
- `atarist.360`, `atarist.400`, `atarist.440`, `atarist.720`, `atarist.800`, `atarist.880`

**CoCo (TRS-80 Color Computer)** :
- `coco.decb`, `coco.decb.40t`
- `coco.os9.40ds`, `coco.os9.40ss`, `coco.os9.80ds`, `coco.os9.80ss`

**Commodore** :
- `commodore.1541`, `commodore.1571`, `commodore.1581`
- `commodore.cmd.fd2000.dd`, `commodore.cmd.fd2000.hd`, `commodore.cmd.fd4000.ed`

**Data General** :
- `datageneral.2f`

**DEC** :
- `dec.rx01`, `dec.rx02`

**Dragon** :
- `dragon.40ds`, `dragon.40ss`, `dragon.80ds`, `dragon.80ss`

**Eagle** :
- `eagle.dsqd.800`, `eagle.ssqd.400`

**Ensoniq** :
- `ensoniq.1600`, `ensoniq.800`, `ensoniq.mirage`

**Epson QX-10** :
- `epson.qx10.320`, `epson.qx10.396`, `epson.qx10.399`, `epson.qx10.400`
- `epson.qx10.booter`, `epson.qx10.logo`

**GEM** :
- `gem.1600`

**HP** :
- `hp.mmfm.9885`, `hp.mmfm.9895`

**IBM/PC** :
- `ibm.1200`, `ibm.1440`, `ibm.160`, `ibm.1680`, `ibm.180`, `ibm.2880`
- `ibm.320`, `ibm.360`, `ibm.720`, `ibm.800`
- `ibm.dmf`, `ibm.scan`

**Kaypro** :
- `kaypro.dsdd.40`, `kaypro.dsdd.80`, `kaypro.ssdd.40`

**Luxor** :
- `luxor.1000.abcnet`, `luxor.1000.data`, `luxor.1000.program`
- `luxor.160`, `luxor.320`, `luxor.640`, `luxor.80`

**Macintosh** :
- `mac.400`, `mac.800`

**Micropolis** :
- `micropolis.100tpi.ds`, `micropolis.100tpi.ds.275`, `micropolis.100tpi.ss`, `micropolis.100tpi.ss.275`
- `micropolis.48tpi.ds`, `micropolis.48tpi.ds.275`, `micropolis.48tpi.ss`, `micropolis.48tpi.ss.275`

**MM1** :
- `mm1.os9.80dshd_32`, `mm1.os9.80dshd_33`, `mm1.os9.80dshd_36`, `mm1.os9.80dshd_37`

**MSX** :
- `msx.1d`, `msx.1dd`, `msx.2d`, `msx.2dd`

**Northstar** :
- `northstar.fm.ds`, `northstar.fm.ss`, `northstar.mfm.ds`, `northstar.mfm.ss`

**OCC1** :
- `occ1.dd`, `occ1.sd`

**Olivetti** :
- `olivetti.m20`

**PC-98** :
- `pc98.2d`, `pc98.2dd`, `pc98.2hd`, `pc98.2hs`, `pc98.n88basic.hd`

**Raw (Flux brut)** :
- `raw.125`, `raw.250`, `raw.500`

**SCI** :
- `sci.prophet`

**Sega** :
- `sega.sf7000`

**Thomson** :
- `thomson.1s160`, `thomson.1s320`, `thomson.1s80`
- `thomson.2s160`, `thomson.2s320`

**TSC FLEX** :
- `tsc.flex.dsdd`, `tsc.flex.ssdd`

**Xerox** :
- `xerox.860.dssd`, `xerox.860.ss`

**ZX Spectrum** :
- `zx.3dos.ds80`, `zx.3dos.ss40`
- `zx.d80.ds80`
- `zx.fdd3000.ds80`, `zx.fdd3000.ss40`
- `zx.kempston.ds80`, `zx.kempston.ss40`
- `zx.opus.ds80`, `zx.opus.ss40`
- `zx.plusd.ds80`
- `zx.quorum.ds80`
- `zx.rocky.ds80`, `zx.rocky.ss40`
- `zx.trdos.ds80`
- `zx.turbodrive.ds40`, `zx.turbodrive.ds80`
- `zx.watford.ds80`, `zx.watford.ss40`

**Note** : Pour utiliser un format, utilisez l'option `--format FORMAT`. Si vous n'utilisez pas `--format`, utilisez `--raw` pour lire en mode flux brut sans décodage.

**Sortie typique** :

**En mode brut (`--raw`)** :
```
Aligning T40.0, reading 10 times, revs=3
T40.0: 50000 flux transitions, 200.0ms per rev, 300.0 RPM
T40.0: 50010 flux transitions, 200.1ms per rev, 299.9 RPM
T40.0: 49995 flux transitions, 199.9ms per rev, 300.1 RPM
...
```

**Avec format décodé** :
```
Aligning T40.0, reading 10 times, revs=3
Format ibm.1440
T40.0: 18 sectors, 0 missing, 0 bad from 50000 flux transitions, 200.0ms per rev
T40.0: 18 sectors, 0 missing, 0 bad from 50010 flux transitions, 200.1ms per rev
T40.0: 18 sectors, 1 missing, 0 bad from 49995 flux transitions, 200.2ms per rev
...
```

**Fonctionnalités clés** :

1. **Lecture répétée automatique** : Lit la même piste plusieurs fois sans intervention manuelle
2. **Alternance de têtes** : Supporte l'alternance entre plusieurs têtes sur le même cylindre
3. **Statistiques** : Chaque lecture affiche un résumé permettant d'analyser les variations
4. **Décodage optionnel** : Peut décoder le format ou lire en flux brut
5. **Support multi-formats** : Compatible avec différents formats de disquettes

**Utilisation pour l'alignement** : 
- **CRITIQUE** - Cette commande est l'équivalent direct de la fonction `align()` d'ImageDisk
- Automatise le processus de lecture répétée pour détecter les problèmes d'alignement
- Les variations entre les lectures indiquent la qualité de l'alignement
- L'alternance entre têtes permet de tester les deux têtes simultanément

**Comparaison avec ImageDisk** :

| Fonctionnalité | ImageDisk | Greaseweazle `align` |
|----------------|-----------|----------------------|
| Lecture répétée | ✅ Boucle manuelle | ✅ Automatique (`--reads`) |
| Détection d'IDs | ✅ Via `readid()` | ✅ Via décodage format |
| Affichage temps réel | ✅ Continu | ✅ Par lecture |
| Alternance têtes | ✅ Manuel (H) | ✅ Automatique (`h=0,1`) |
| Positionnement | ✅ `seek()` | ✅ Automatique via `usb.seek()` |
| Mesure RPM | ✅ `rpm()` | ✅ Incluse dans sortie |
| Signal sonore | ✅ Beep | ❌ Non implémenté |

**Intégration dans une interface web** :

```python
import subprocess
import json
import re

def run_alignment(cylinder, head, reads=10, revs=3, format_type=None):
    """Exécute la commande d'alignement et parse les résultats"""
    cmd = ['gw', 'align', '--tracks', f'c={cylinder}:h={head}',
           '--reads', str(reads), '--revs', str(revs)]
    
    if format_type:
        cmd.extend(['--format', format_type])
    else:
        cmd.append('--raw')
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parser la sortie
    readings = []
    for line in result.stdout.split('\n'):
        if 'T' in line and ':' in line:
            # Format: T40.0: 18 sectors, 0 missing, 0 bad from ...
            # ou: T40.0: 50000 flux transitions, 200.0ms per rev, 300.0 RPM
            parts = line.split(':')
            if len(parts) >= 2:
                track_info = parts[0].strip()
                reading_info = parts[1].strip()
                readings.append({
                    'track': track_info,
                    'info': reading_info,
                    'raw_line': line
                })
    
    return {
        'success': result.returncode == 0,
        'readings': readings,
        'stdout': result.stdout,
        'stderr': result.stderr
    }
```

**État du développement** :
- **Version** : Disponible depuis Greaseweazle 1.23b
- **Statut** : ✅ Commande stable et fonctionnelle
- **Note** : Si vous voyez l'avertissement `Optimised data routines not found`, cela n'empêche pas l'utilisation mais peut affecter les performances. 
  - **Linux/WSL** : Exécutez `./setup.sh` ou `./scripts/setup.sh` dans le dossier source
  - **Windows** : Exécutez `.\setup.ps1` ou `.\scripts\setup.bat` (nécessite Visual Studio Build Tools ou MinGW)

**Cas d'utilisation typiques** :

1. **Test d'alignement standard** : Utiliser avec `--raw` pour analyse directe du flux
2. **Vérification de format** : Utiliser avec `--format` pour décoder et vérifier les secteurs
3. **Test multi-têtes** : Utiliser `h=0,1` pour alterner entre les têtes
4. **Analyse statistique** : Augmenter `--reads` et `--revs` pour plus de données
5. **Lecteurs spéciaux** : Utiliser `--gen-tg43` pour lecteurs 8 pouces, `--hard-sectors` pour disques à secteurs durs

---

### 7. `update` - Mise à jour du firmware

**Description** : Met à jour le firmware de la carte Greaseweazle.

**Syntaxe** :
```bash
gw update [OPTIONS] [FIRMWARE_FILE]
```

**Options principales** :

| Option | Description |
|--------|-------------|
| `--device DEVICE` | Port série de la carte |
| `--force` | Force la mise à jour même si la version est identique |

**Exemples** :
```bash
# Mise à jour automatique (télécharge la dernière version)
gw update

# Mise à jour depuis un fichier local
gw update firmware.bin
```

---

### 8. `flux` - Opérations sur flux brut

**Description** : Opérations avancées sur les flux bruts de données.

**Syntaxe** :
```bash
gw flux [SOUS-COMMANDE] [OPTIONS]
```

**Sous-commandes** :

- `read` : Lit un flux brut
- `write` : Écrit un flux brut
- `convert` : Convertit entre formats de flux

**Exemples** :
```bash
# Lecture d'un flux brut
gw flux read --tracks 0-79 disk.flux

# Conversion de format
gw flux convert input.flux output.scp
```

**Utilisation pour l'alignement** : Le mode flux brut est essentiel pour l'analyse précise nécessaire aux tests d'alignement.

---

### 9. `test` - Tests de diagnostic

**Description** : Effectue des tests de diagnostic sur la carte et le lecteur.

**Syntaxe** :
```bash
gw test [OPTIONS]
```

**Options principales** :

| Option | Description |
|--------|-------------|
| `--device DEVICE` | Port série de la carte |
| `--tracks TRACKS` | Pistes à tester |
| `--rpm` | Teste la vitesse de rotation |

**Exemples** :
```bash
# Test général
gw test

# Test de vitesse de rotation
gw test --rpm

# Test de pistes spécifiques
gw test --tracks 0-10
```

**Utilisation pour l'alignement** : Permet de vérifier le bon fonctionnement avant les tests d'alignement.

---

### 10. `rpm` - Mesure de vitesse de rotation

**Description** : Mesure la vitesse de rotation de la disquette (RPM).

**Syntaxe** :
```bash
gw rpm [OPTIONS]
```

**Options principales** :

| Option | Description |
|--------|-------------|
| `--device DEVICE` | Port série de la carte |
| `--tracks TRACKS` | Pistes à mesurer |
| `--revs N` | Nombre de révolutions à mesurer |

**Exemples** :
```bash
# Mesure standard
gw rpm

# Mesure sur plusieurs pistes
gw rpm --tracks 0,20,40,60,79
```

**Utilisation pour l'alignement** : La vitesse de rotation doit être stable pour des tests d'alignement précis. Équivalent de la fonction `rpm()` d'ImageDisk.

---

## API Python (greaseweazle.py)

Pour une intégration dans une interface web, il est possible d'utiliser directement l'API Python de Greaseweazle plutôt que d'appeler l'outil en ligne de commande.

### Installation du module Python

```bash
pip install greaseweazle
```

### Exemple d'utilisation basique

```python
from greaseweazle import usb as gw_usb
from greaseweazle import flux

# Connexion à la carte
usb = gw_usb.Device()

# Lecture d'une piste
with open('track0.flux', 'wb') as f:
    flux_data = usb.read_track(0, 0)  # Piste 0, tête 0
    f.write(flux_data)

# Positionnement de la tête
usb.seek(43, 0)  # Piste 43, tête 0

# Fermeture
usb.close()
```

### Classes principales

#### `greaseweazle.usb.Device`

Classe principale pour la communication avec la carte.

**Méthodes principales** :

```python
class Device:
    def __init__(self, device=None):
        """Initialise la connexion à la carte"""
        
    def seek(self, cyl, head):
        """Positionne la tête sur la piste cyl, tête head"""
        
    def read_track(self, cyl, head, revs=2):
        """Lit une piste (cyl, head) avec revs révolutions"""
        
    def write_track(self, cyl, head, flux_data):
        """Écrit une piste"""
        
    def get_info(self):
        """Retourne les informations de la carte"""
        
    def close(self):
        """Ferme la connexion"""
```

#### `greaseweazle.flux`

Classes pour manipuler les flux bruts.

```python
from greaseweazle.flux import Flux

# Lecture d'un fichier flux
flux = Flux.read('track.flux')

# Accès aux données
for rev in flux.revolutions:
    for index in rev.indexes:
        # Analyse des index marks
        pass
```

## Compatibilité avec les tests d'alignement ImageDisk

### ✅ Adaptabilité confirmée

La carte Greaseweazle est **parfaitement adaptée** pour reproduire les tests d'alignement d'ImageDisk via une interface web pour les raisons suivantes :

#### 1. Accès au niveau du flux brut
- Permet de lire les données brutes comme ImageDisk
- Accès aux index marks et aux transitions de flux
- Analyse précise des signaux

#### 2. Contrôle précis de la tête
- Commande `seek` pour positionner la tête
- Contrôle de la tête (0 ou 1)
- Support du double-step si nécessaire

#### 3. Lecture de pistes spécifiques
- Possibilité de lire une piste spécifique
- Plusieurs révolutions pour analyse statistique
- Détection des IDs de secteurs

#### 4. Interface programmable
- API Python disponible
- Peut être intégrée dans une application web
- Communication série standard (USB CDC)

### Correspondance avec ImageDisk

| Fonction ImageDisk | Équivalent Greaseweazle |
|-------------------|------------------------|
| `seek(cylindre)` | `gw seek CYLINDRE` ou `usb.seek(cyl, head)` |
| `readid()` | Lecture flux + analyse des IDs |
| `read_sector()` | `gw read --tracks CYL` ou `usb.read_track()` |
| `analyze_track()` | `gw read --flux --tracks CYL` + analyse |
| `align()` ⭐ | `gw align --tracks c=CYL:h=HEAD` (PR #592) |
| `rpm()` | `gw rpm` |
| `resync()` | `gw seek` avec repositionnement |

### Fonctionnalités supplémentaires

Greaseweazle offre des fonctionnalités supplémentaires utiles pour l'alignement :

1. **Lecture de plusieurs révolutions** : Permet d'analyser la stabilité
2. **Mode flux brut** : Accès direct aux transitions de flux
3. **Mesure RPM précise** : Vérification de la vitesse de rotation
4. **Support multi-formats** : Compatible avec différents formats de disquettes

## État actuel des fonctionnalités d'alignement

### Commandes disponibles

| Commande | Statut | Description |
|----------|--------|-------------|
| `gw seek` | ✅ Stable | Positionnement de la tête |
| `gw read --flux` | ✅ Stable | Lecture en flux brut |
| `gw rpm` | ✅ Stable | Mesure de vitesse |
| `gw align` | 🔄 PR #592 (ouvert) | Test d'alignement automatisé |

### Utilisation recommandée

**Version stable actuelle** :
- Utiliser `gw seek` + `gw read --flux` en boucle pour reproduire `align()` d'ImageDisk
- Implémenter la logique d'analyse dans votre interface web

**Avec PR #592 (quand mergé)** :
- Utiliser directement `gw align` pour automatiser le processus
- Simplifier l'implémentation dans votre interface web

## Architecture pour interface web

### Schéma d'intégration

```
┌─────────────────┐
│  Interface Web  │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Serveur Web    │
│  (Backend)      │
│  - Flask/FastAPI│
└────────┬────────┘
         │ API Python
         ▼
┌─────────────────┐
│  Greaseweazle   │
│  (Python API)   │
└────────┬────────┘
         │ USB Serial
         ▼
┌─────────────────┐
│  Carte GW       │
│  (Hardware)     │
└────────┬────────┘
         │ FDD Interface
         ▼
┌─────────────────┐
│  Lecteur FDD    │
└─────────────────┘
```

### Utilisation de `gw.exe` dans une interface web (Windows)

Si vous développez sur Windows, vous pouvez utiliser `gw.exe` directement via subprocess :

```python
import subprocess
import os

# Chemin vers gw.exe (ajuster selon votre installation)
GW_EXE = r"C:\chemin\vers\greaseweazle\gw.exe"

def run_gw_command(command, args):
    """Exécute une commande gw.exe"""
    cmd = [GW_EXE, command] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(GW_EXE)
    )
    return {
        'success': result.returncode == 0,
        'stdout': result.stdout,
        'stderr': result.stderr
    }

# Exemple d'utilisation
result = run_gw_command('align', [
    '--tracks', 'c=40:h=0',
    '--reads', '10',
    '--revs', '3'
])
```

### Exemple d'implémentation backend

```python
from flask import Flask, jsonify, request
from greaseweazle import usb as gw_usb
import threading
import subprocess
import os
import platform

app = Flask(__name__)
gw_device = None
lock = threading.Lock()

# Détecter la plateforme et utiliser la bonne commande
GW_CMD = 'gw.exe' if platform.system() == 'Windows' else 'gw'

@app.route('/api/connect', methods=['POST'])
def connect():
    global gw_device
    device = request.json.get('device', None)
    try:
        with lock:
            gw_device = gw_usb.Device(device)
            info = gw_device.get_info()
        return jsonify({'status': 'connected', 'info': info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/seek', methods=['POST'])
def seek():
    data = request.json
    cyl = data.get('cylinder', 0)
    head = data.get('head', 0)
    try:
        with lock:
            gw_device.seek(cyl, head)
        return jsonify({'status': 'ok', 'cylinder': cyl, 'head': head})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/read_track', methods=['POST'])
def read_track():
    data = request.json
    cyl = data.get('cylinder', 0)
    head = data.get('head', 0)
    revs = data.get('revolutions', 2)
    try:
        with lock:
            flux_data = gw_device.read_track(cyl, head, revs)
        # Analyse des IDs de secteurs
        # ... code d'analyse ...
        return jsonify({
            'status': 'ok',
            'cylinder': cyl,
            'head': head,
            'sectors': analyzed_sectors
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/align', methods=['POST'])
def align():
    """Nouvelle route pour utiliser la commande align (quand disponible)"""
    data = request.json
    cyl = data.get('cylinder', 0)
    head = data.get('head', 0)
    reads = data.get('reads', 10)
    revs = data.get('revolutions', 3)
    format_type = data.get('format', None)
    
    try:
        # Utiliser gw.exe sur Windows, gw sur Linux/macOS
        cmd = [GW_CMD, 'align', '--tracks', f'c={cyl}:h={head}',
               '--reads', str(reads), '--revs', str(revs)]
        if format_type:
            cmd.extend(['--format', format_type])
        else:
            cmd.append('--raw')
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parser les résultats
        readings = []
        for line in result.stdout.split('\n'):
            if 'T' in line and ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    readings.append({
                        'track': parts[0].strip(),
                        'info': parts[1].strip()
                    })
        
        return jsonify({
            'status': 'ok' if result.returncode == 0 else 'error',
            'readings': readings,
            'stdout': result.stdout
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/rpm', methods=['GET'])
def rpm():
    try:
        with lock:
            rpm_value = gw_device.measure_rpm()
        return jsonify({'status': 'ok', 'rpm': rpm_value})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Exemple d'implémentation frontend (JavaScript)

```javascript
// Connexion à la carte
async function connect() {
    const response = await fetch('/api/connect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({device: 'COM3'})
    });
    const data = await response.json();
    console.log('Connected:', data);
}

// Positionnement de la tête
async function seek(cylinder, head) {
    const response = await fetch('/api/seek', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cylinder: cylinder, head: head})
    });
    return await response.json();
}

// Utilisation de la commande align (quand disponible)
async function runAlignment(cylinder, head, reads=10, revs=3) {
    const response = await fetch('/api/align', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            cylinder: cylinder,
            head: head,
            reads: reads,
            revolutions: revs,
            format: 'ibm.1440'  // ou null pour mode raw
        })
    });
    return await response.json();
}

// Lecture d'une piste avec analyse d'alignement
async function readTrackForAlignment(cylinder, head) {
    const response = await fetch('/api/read_track', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            cylinder: cylinder,
            head: head,
            revolutions: 5  // Plusieurs révolutions pour statistiques
        })
    });
    const data = await response.json();
    
    // Analyse des résultats
    let correct = 0, incorrect = 0;
    data.sectors.forEach(sector => {
        if (sector.detected_cylinder === cylinder) {
            correct++;
        } else {
            incorrect++;
        }
    });
    
    return {correct, incorrect, total: data.sectors.length};
}

// Boucle de détection d'alignement (similaire à ImageDisk)
async function alignmentLoop(targetCylinder, head) {
    await seek(targetCylinder, head);
    
    const results = [];
    for (let i = 0; i < 10; i++) {
        const result = await readTrackForAlignment(targetCylinder, head);
        results.push(result);
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    // Calcul des statistiques
    const avgCorrect = results.reduce((sum, r) => sum + r.correct, 0) / results.length;
    const avgIncorrect = results.reduce((sum, r) => sum + r.incorrect, 0) / results.length;
    
    return {
        correct: Math.round(avgCorrect),
        incorrect: Math.round(avgIncorrect),
        quality: avgCorrect / (avgCorrect + avgIncorrect) * 100
    };
}
```

## Commandes avancées pour l'alignement

### Lecture avec analyse d'IDs

```bash
# Lecture d'une piste avec 5 révolutions pour statistiques
gw read --tracks 43 --revs 5 --format ibm.1440 track43.img

# Lecture en mode flux brut pour analyse précise
gw read --flux --tracks 43 --revs 5 track43.flux
```

### Test de positionnement

```bash
# Séquence de tests de positionnement
for i in 0 10 20 30 40 50 60 70 79; do
    gw seek $i
    gw read --tracks $i --revs 3 test_track${i}.img
done
```

### Utilisation de la commande align (quand disponible)

```bash
# Test d'alignement automatisé
gw align --tracks c=40:h=0 --reads 20 --revs 5

# Alternance entre têtes
gw align --tracks c=40:h=0,1 --reads 10

# Avec format pour décodage
gw align --tracks c=0:h=0 --format ibm.1440 --reads 15
```

### Mesure RPM avant alignement

```bash
# Vérifier la vitesse de rotation
gw rpm --tracks 0,20,40,60,79
```

## Limitations et considérations

### Limitations matérielles

1. **Vitesse de communication USB** : La communication série peut être un goulot d'étranglement pour les opérations en temps réel
2. **Latence USB** : Délai entre commande et exécution (typiquement 10-50ms)
3. **Buffer limité** : Les données de flux doivent être traitées par blocs

### Limitations logicielles

1. **Commande "align" en développement** : Disponible dans PR #592, pas encore mergé
2. **Pas de signal sonore** : Contrairement à ImageDisk, pas de beep pour feedback
3. **Pas de resynchronisation automatique** : Doit être implémentée dans le code applicatif
4. **Gestion d'erreurs** : Nécessite une gestion explicite des timeouts et erreurs

### Points d'attention pour l'alignement

1. **Timing** : Les délais entre commandes doivent être respectés
2. **Stabilité** : Plusieurs lectures sont nécessaires pour des statistiques fiables
3. **Calibration** : La vitesse de rotation doit être vérifiée régulièrement

## Comparaison avec ImageDisk

| Aspect | ImageDisk | Greaseweazle |
|--------|----------|--------------|
| **Interface** | DOS, accès direct FDC | USB, API Python |
| **Plateforme** | DOS uniquement | Multi-plateforme |
| **Accès matériel** | Direct (FDC 765) | Via USB série |
| **Latence** | Très faible (~1ms) | Modérée (~10-50ms) |
| **Précision** | Très élevée | Élevée |
| **Intégration web** | Impossible | Possible |
| **Coût** | Logiciel gratuit | Carte matérielle (~$50) |
| **Commande align** | ✅ Intégrée | 🔄 PR #592 (en développement) |

## Conclusion

La carte Greaseweazle est **parfaitement adaptée** pour reproduire les tests d'alignement d'ImageDisk via une interface web. Elle offre :

✅ Accès au niveau du flux brut  
✅ Contrôle précis de la tête  
✅ API Python pour intégration  
✅ Support multi-plateforme  
✅ Documentation complète  

**Mise à jour importante** : Le PR #592 ajoute une commande `align` dédiée qui automatise le processus de test d'alignement, rendant Greaseweazle encore plus proche d'ImageDisk en termes de fonctionnalités.

Les principales différences avec ImageDisk sont :
- Latence légèrement plus élevée (acceptable pour l'alignement)
- Commande `align` en développement (PR #592)
- Pas de signal sonore (peut être implémenté dans l'interface web)
- Avantage majeur : Accessible via interface web moderne

## Installation et compilation

### Installation standard

**Linux/macOS** :
```bash
pipx install greaseweazle
# ou
pip install greaseweazle
```

**Windows** :
- Télécharger depuis : https://github.com/keirf/greaseweazle/releases
- Décompresser et utiliser `gw.exe` directement

### Installation avec commande `align` (PR #592)

Pour utiliser la commande `align` avant qu'elle soit mergée :

**Méthode 1 : Installation depuis la branche du PR**

```bash
# Cloner le dépôt
git clone https://github.com/keirf/greaseweazle.git
cd greaseweazle

# Récupérer la branche du PR #592
git fetch origin pull/592/head:pr-592-alignment
git checkout pr-592-alignment

# Installer en mode développement
pip install -e .
```

**Méthode 2 : Compilation de `gw.exe` avec PyInstaller**

```bash
# Après avoir checkout la branche du PR
pip install pyinstaller

# Créer l'exécutable
pyinstaller --onefile --name gw --console src/greaseweazle/tools/gw.py

# L'exécutable sera dans dist/gw.exe
```

**Méthode 3 : Installation directe depuis GitHub**

```bash
# Installer directement depuis la branche du PR
pip install git+https://github.com/keirf/greaseweazle.git@pull/592/head
```

### Vérification de l'installation

```bash
# Vérifier que la commande est disponible
gw --help
# ou sur Windows
gw.exe --help

# Tester la commande align
gw align --help
# ou
gw.exe align --help
```

## Ressources supplémentaires

- **Dépôt GitHub** : https://github.com/keirf/greaseweazle
- **Releases Windows** : https://github.com/keirf/greaseweazle/releases
- **Wiki** : https://github.com/keirf/greaseweazle/wiki
- **PR #592** : https://github.com/keirf/greaseweazle/pull/592 (Commande align)
- **Manuel utilisateur** : Disponible dans le dépôt
- **Forum de discussion** : Discussions GitHub du projet

## Annexe : Format des fichiers flux

Les fichiers flux bruts contiennent les transitions de flux avec leurs timings. Format typique :
- **Header** : Métadonnées (format, pistes, etc.)
- **Flux data** : Séquence de timings entre transitions
- **Index marks** : Marqueurs de début de secteur

L'analyse de ces fichiers permet de :
- Détecter les IDs de secteurs
- Mesurer les timings précis
- Analyser la qualité du signal
- Détecter les problèmes d'alignement

