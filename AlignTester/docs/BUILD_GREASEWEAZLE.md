# Build et Test de Greaseweazle avec Commande Align

## 📋 Résumé

Le script de build `scripts/build_greaseweazle.sh` permet de compiler et installer Greaseweazle depuis les sources, mais **la commande `align` n'est pas disponible dans la version 1.23 actuelle**.

---

## 🛠️ Script de Build

### Utilisation

```bash
cd AlignTester
./scripts/build_greaseweazle.sh [options]
```

### Options disponibles

- `--install-mode MODE` : Mode d'installation (local, system, venv)
  - `local` : Installation dans un dossier local (défaut)
  - `system` : Installation dans le système Python
  - `venv` : Installation dans l'environnement virtuel
- `--clean` : Nettoyer avant le build
- `--test-align` : Tester la commande align après le build
- `--help` : Afficher l'aide

### Exemples

```bash
# Build dans l'environnement virtuel avec test de align
./scripts/build_greaseweazle.sh --install-mode venv --test-align

# Build avec nettoyage préalable
./scripts/build_greaseweazle.sh --clean --test-align

# Build dans le système (peut nécessiter sudo)
./scripts/build_greaseweazle.sh --install-mode system
```

---

## ✅ Résultats du Build

### Commandes Disponibles (Version 1.23)

D'après les tests, les commandes disponibles sont :

- `info` : Afficher les informations sur la configuration Greaseweazle
- `read` : Lire un disque vers un fichier d'image
- `write` : Écrire un disque depuis un fichier d'image
- `convert` : Convertir entre formats d'image
- `erase` : Effacer un disque
- `clean` : Nettoyer un lecteur avec un disque de nettoyage
- `seek` : Aller à la piste spécifiée
- `delays` : Afficher/modifier les paramètres de délai du lecteur
- `update` : Mettre à jour le firmware Greaseweazle
- `pin` : Changer l'état d'une broche d'interface
- `reset` : Réinitialiser le device Greaseweazle
- `bandwidth` : Rapporter la bande passante USB disponible
- `rpm` : Mesurer le RPM du lecteur

**❌ `align` n'est PAS dans cette liste.**

---

## 🔍 Recherche de la Commande Align

### Statut Actuel

La commande `align` est mentionnée dans :
- **PR #592** : Pull Request qui propose cette fonctionnalité
- **Issue #495** : Discussion sur l'alignement des têtes de lecture

**Mais elle n'est pas encore intégrée dans la version officielle.**

### Options pour Obtenir Align

#### Option 1 : Attendre l'intégration officielle

La commande pourrait être intégrée dans une version future de Greaseweazle.

#### Option 2 : Utiliser une branche/PR spécifique

Si la PR #592 contient la commande, on peut installer depuis cette branche :

```bash
pip install git+https://github.com/keirf/greaseweazle@pull/592/head
# ou depuis la branche de la PR
pip install git+https://github.com/keirf/greaseweazle@nom-de-la-branche
```

#### Option 3 : Implémenter la commande align localement

Créer `src/greaseweazle/tools/align.py` et l'ajouter à la liste des actions dans `cli.py`.

---

## 🔨 Implémentation de la Commande Align

### Structure d'une Commande

Chaque commande dans `tools/` suit cette structure :

```python
# tools/align.py
description = "Align drive heads using alignment test"

def main(argv) -> None:
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--cylinders", type=int, default=80, help="Number of cylinders")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries")
    args = parser.parse_args(argv[2:])
    
    # Implémentation de la logique d'alignement
    # ...
```

### Ajout à cli.py

Il faudrait ajouter `'align'` à la liste des actions :

```python
actions = [ 'info',
            'read',
            'write',
            # ...
            'align',  # <-- Ajouter ici
            'rpm' ]
```

### Besoins pour l'Implémentation

1. **Accès au device USB** : Via `greaseweazle.usb.USB`
2. **Lecture des pistes** : Pour mesurer l'alignement
3. **Calcul des pourcentages** : Basé sur les mesures
4. **Format de sortie** : Compatible avec le parser existant dans AlignTester

---

## 📝 Format de Sortie Attendu

D'après le parser dans `api/alignment_parser.py`, le format attendu est :

```
00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
00.1    : base: 1.004 us [99.742%], band: 2.005 us, 3.003 us
01.0    : base: 1.002 us [99.855%], band: 2.003 us, 3.002 us
...
```

Où :
- `XX.Y` : Numéro de piste (cylindre.secteur)
- `base: X.XXX us` : Valeur de base en microsecondes
- `[XX.XXX%]` : Pourcentage d'alignement (à extraire)
- `band: ...` : Valeurs de bande

---

## 🚀 Prochaines Étapes Recommandées

### 1. Vérifier la PR #592

```bash
# Voir si la PR contient la commande align
git clone https://github.com/keirf/greaseweazle.git
cd greaseweazle
git fetch origin pull/592/head:pr-592
git checkout pr-592
# Vérifier si tools/align.py existe
ls src/greaseweazle/tools/align.py
```

### 2. Tester avec le Binaire Windows

Si vous avez le binaire `gw.exe`, tester directement :

```bash
cd /home/jean-fred/Aligntester/greaseweazle-1.23
./gw.exe align --help
```

Si cela fonctionne, le binaire contient une version avec `align`.

### 3. Implémenter une Version Basique

Créer une version basique de `align` qui :
- Se connecte au device
- Lit quelques pistes
- Calcule et affiche les pourcentages
- Utilise le format attendu par le parser

---

## 🔗 Références

- **Repository GitHub** : https://github.com/keirf/greaseweazle
- **PR #592** : https://github.com/keirf/greaseweazle/pull/592
- **Issue #495** : https://github.com/keirf/greaseweazle/issues/495
- **Documentation Wiki** : https://github.com/keirf/greaseweazle/wiki

---

## ✅ Checklist

- [x] Script de build créé et fonctionnel
- [x] Build testé avec version GitHub latest
- [x] Vérification que `align` n'est pas disponible
- [ ] Vérifier la PR #592 pour l'existence de `align`
- [ ] Tester avec le binaire Windows fourni
- [ ] Implémenter `align` si nécessaire
- [ ] Intégrer `align` dans AlignTester

---

**Dernière mise à jour** : Build testé, `align` non disponible dans v1.23

