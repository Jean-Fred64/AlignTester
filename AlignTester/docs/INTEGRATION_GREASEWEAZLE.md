# Intégration Greaseweazle - Documentation

## 📋 Vue d'ensemble

Ce document décrit l'intégration de Greaseweazle dans le projet AlignTester, y compris les ressources disponibles et leur utilisation.

---

## 📦 Ressources Greaseweazle Disponibles

### 1. Binaire Windows (Version 1.23)

**Emplacement** : `/home/jean-fred/Aligntester/greaseweazle-1.23/`

**Contenu** :
- `gw.exe` : Exécutable principal (16KB)
- DLLs nécessaires (Visual C++ Runtime) :
  - `msvcp140.dll`, `msvcp140_1.dll`, `msvcp140_2.dll`
  - `vcruntime140.dll`, `vcruntime140_1.dll`
  - `python311.dll`
  - Et autres DLLs de support
- `CAPSImg.dll` : Support CAPS Image
- Documentation :
  - `README` : Informations de base
  - `RELEASE_NOTES` : Notes de version
  - `COPYING` : Licence
  - `VERSION` : Version (1.23)

**Utilisation** :
- Pour Windows : Utiliser directement `gw.exe` depuis ce dossier
- Le chemin complet peut être référencé dans la configuration
- Toutes les DLLs doivent être dans le même dossier que `gw.exe`

### 2. Sources Python (Version 1.23)

**Emplacement** : `/home/jean-fred/Aligntester/AlignTester/src/greaseweazle-1.23/`

**Structure** :
```
greaseweazle-1.23/
├── src/
│   └── greaseweazle/    # Code source Python
├── scripts/             # Scripts de build
├── setup.py            # Configuration d'installation
├── pyproject.toml      # Configuration moderne
├── README              # Documentation
├── RELEASE_NOTES       # Notes de version
├── INSTALL             # Instructions d'installation
└── COPYING             # Licence
```

**Dépendances** (d'après `setup.py`) :
- Python >= 3.8
- `crcmod`
- `bitarray>=3`
- `pyserial`
- `requests`

**Installation** :
```bash
cd AlignTester/src/greaseweazle-1.23
pip install .
```

Cela installe le package Python et crée la commande `gw` dans le PATH.

---

## 🔧 Intégration dans AlignTester

### Détection du chemin gw.exe

Le code actuel dans `api/greaseweazle.py` détecte automatiquement :
- Sur Windows : Cherche `gw.exe` dans le dossier courant ou PATH
- Sur Linux/macOS : Cherche `gw` dans PATH

**Pour utiliser le binaire Windows fourni** :

1. **Option 1** : Ajouter le dossier au PATH Windows
2. **Option 2** : Spécifier le chemin complet dans la configuration
3. **Option 3** : Copier `gw.exe` et les DLLs dans un dossier accessible

### Configuration recommandée

Pour le développement et la version standalone, considérer :

```python
# Dans api/greaseweazle.py
def _detect_gw_path(self) -> str:
    """Détecte le chemin vers gw.exe ou gw"""
    if self.platform == "Windows":
        # 1. Chercher dans le dossier greaseweazle-1.23 à la racine
        gw_exe_root = Path(__file__).parent.parent.parent.parent.parent / "greaseweazle-1.23" / "gw.exe"
        if gw_exe_root.exists():
            return str(gw_exe_root.absolute())
        
        # 2. Chercher dans le dossier courant
        gw_exe = Path("gw.exe")
        if gw_exe.exists():
            return str(gw_exe.absolute())
        
        # 3. Chercher dans PATH
        return "gw.exe"
    else:
        return "gw"
```

### Pour la version standalone

**Note importante** : Greaseweazle n'est **pas inclus** dans le package standalone.

L'utilisateur doit installer Greaseweazle séparément :
- **Windows** : Installer `gw.exe` et le rendre accessible via PATH ou spécifier le chemin dans les paramètres
- **Linux/macOS** : Installer via `pip install greaseweazle` ou via le gestionnaire de paquets du système

---

## 📖 Documentation Greaseweazle

### Sources officielles

- **GitHub** : https://github.com/keirf/greaseweazle
- **Wiki** : https://github.com/keirf/greaseweazle/wiki/
- **Auteur** : Keir Fraser <keir.xen@gmail.com>

### Commandes principales

#### `gw --version`
Affiche les informations sur :
- Version des host tools
- Informations du device connecté (si présent) :
  - Port (COM10, /dev/ttyACM0, etc.)
  - Modèle
  - MCU
  - Firmware
  - Numéro de série
  - Informations USB

#### `gw align --help`
Affiche l'aide pour la commande align (disponible depuis PR #592)

#### `gw align --cylinders=N --retries=M`
Lance un test d'alignement avec :
- `--cylinders` : Nombre de cylindres à tester (défaut: 80)
- `--retries` : Nombre de tentatives par piste (défaut: variable)

**Format de sortie attendu** :
```
00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
00.1    : base: 1.004 us [99.742%], band: 2.005 us, 3.003 us
...
```

---

## 🔍 Analyse du Code Source

### Structure du package Python

D'après `setup.py`, le package contient :
- Module principal : `greaseweazle`
- Extension C optimisée : `greaseweazle.optimised.optimised`
- Points d'entrée : `gw=greaseweazle.cli:main`

### Points d'intérêt pour l'intégration

1. **Interface CLI** : `greaseweazle.cli:main`
   - C'est le point d'entrée de la commande `gw`
   - Parse les arguments de ligne de commande

2. **Gestion du device** : Probablement dans `greaseweazle.usb` ou similaire
   - Détection du port série
   - Communication avec le device

3. **Commande align** : ⚠️ **Non présente dans les sources fournies**
   - Pas de `tools/align.py` trouvé
   - Pas dans la liste des actions de `cli.py`
   - Mentionnée dans PR #592 mais peut-être dans une version/branche différente
   - **Action requise** : Tester si `gw align --help` fonctionne avec le binaire fourni

---

## 🚀 Utilisation dans AlignTester

### Endpoint `/api/info`

Cet endpoint utilise `gw --version` pour récupérer :
- Version des host tools
- Informations du device (port, modèle, firmware, etc.)
- Statut de connexion

### Exécution d'alignement

La commande `gw align` est exécutée via :
```python
executor = GreaseweazleExecutor()
result = await executor.run_align(cylinders=80, retries=3, on_output=callback)
```

La sortie est parsée en temps réel pour extraire les valeurs de pourcentage.

---

## 📝 Notes Importantes

### Licence

Greaseweazle est librement redistribuable. Voir le fichier `COPYING` pour les détails.

### Version

Version actuelle disponible : **1.23**

### Compatibilité

- **Windows** : Binaire fourni (`gw.exe` + DLLs)
- **Linux/macOS** : Installation depuis les sources Python ou via pip

### Commande align

**⚠️ Note importante** : D'après l'analyse du code source (`cli.py`), la commande `align` **n'est pas présente** dans la liste des actions disponibles dans la version 1.23 des sources fournies.

Les actions disponibles dans `cli.py` sont :
- `info`, `read`, `write`, `convert`, `erase`, `clean`, `seek`, `delays`, `update`, `pin`, `reset`, `bandwidth`, `rpm`

**La commande `align` est mentionnée dans la PR #592**, mais elle pourrait :
- Être dans une version ultérieure non encore publiée
- Être dans une branche de développement spécifique
- Nécessiter une compilation depuis une source différente

**Vérification** : Testez manuellement si `gw align --help` fonctionne avec votre binaire `gw.exe`. Si oui, la fonctionnalité est présente même si elle n'est pas visible dans les sources fournies.

---

## 🔄 Prochaines Étapes

1. **Analyser les sources** pour comprendre :
   - Comment fonctionne la commande `align`
   - Format exact de la sortie
   - Codes d'erreur possibles

2. **Intégrer dans la version standalone** :
   - Inclure `gw.exe` + DLLs dans le package
   - Configurer le chemin correctement

3. **Tests avec hardware réel** :
   - Tester avec le device connecté
   - Valider le parsing de la sortie réelle
   - Gérer les erreurs hardware

---

## 📚 Références

- **Dossier binaire** : `/home/jean-fred/Aligntester/greaseweazle-1.23/`
- **Dossier sources** : `/home/jean-fred/Aligntester/AlignTester/src/greaseweazle-1.23/`
- **GitHub officiel** : https://github.com/keirf/greaseweazle
- **Documentation** : https://github.com/keirf/greaseweazle/wiki/

---

**Dernière mise à jour** : Analyse des ressources Greaseweazle 1.23

