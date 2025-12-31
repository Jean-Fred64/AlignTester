# Comparaison des Dossiers Greaseweazle

## 📁 Deux Dossiers Présents

Il existe deux dossiers contenant les sources Greaseweazle dans le projet :

1. **`AlignTester/src/greaseweazle-1.23/`**
2. **`AlignTester/src/greaseweazle-1.23 sources/greaseweazle-1.23/`**

---

## 🔍 Différences Structurelles

### Structure du premier dossier

```
AlignTester/src/greaseweazle-1.23/
├── COPYING
├── INSTALL
├── PKG-INFO
├── pyproject.toml
├── README
├── RELEASE_NOTES
├── scripts/
├── setup.cfg
├── setup.py
└── src/
    └── greaseweazle/
```

**Caractéristiques** :
- Structure **plate** : fichiers directement dans le dossier
- Contient `setup.py` : prêt pour installation Python
- Contient `PKG-INFO` : package Python déjà préparé

### Structure du second dossier

```
AlignTester/src/greaseweazle-1.23 sources/
└── greaseweazle-1.23/
    ├── COPYING
    ├── INSTALL
    ├── Makefile
    ├── MANIFEST.in
    ├── pyproject.toml
    ├── README
    ├── README.md
    ├── RELEASE_NOTES
    ├── Rules.mk
    ├── scripts/
    └── src/
        └── greaseweazle/
```

**Caractéristiques** :
- Structure **imbriquée** : dossier supplémentaire `greaseweazle-1.23 sources/`
- **Pas de `setup.py`** : mais contient `Makefile` et `Rules.mk`
- Contient `README.md` en plus de `README`
- Contient `MANIFEST.in` : fichier de manifeste Python
- Contient `Rules.mk` : règles de build Makefile

---

## 📊 Comparaison Détaillée

| Fichier | greaseweazle-1.23 | greaseweazle-1.23 sources |
|---------|-------------------|---------------------------|
| `setup.py` | ✅ Présent | ✅ Présent |
| `PKG-INFO` | ✅ Présent | ❌ Absent |
| `setup.cfg` | ✅ Présent | ❌ Absent |
| `Makefile` | ❌ Absent | ✅ Présent |
| `Rules.mk` | ❌ Absent | ✅ Présent |
| `MANIFEST.in` | ❌ Absent | ✅ Présent |
| `README.md` | ❌ Absent | ✅ Présent |
| `README` | ✅ Présent | ✅ Présent |
| `.gitignore` | ❌ Absent | ✅ Présent |
| `.github/` | ❌ Absent | ✅ Présent |
| `COPYING` | ✅ Présent | ✅ Présent |
| `INSTALL` | ✅ Présent | ✅ Présent |
| `RELEASE_NOTES` | ✅ Présent | ✅ Présent |
| `pyproject.toml` | ✅ Présent | ✅ Présent |
| `scripts/` | ✅ Présent | ✅ Présent (avec `win/` en plus) |
| `src/` | ✅ Présent | ✅ Présent |
| `src/greaseweazle/__init__.py` | ✅ Présent | ❌ Absent |
| `src/greaseweazle.egg-info/` | ✅ Présent | ❌ Absent |

---

## 💡 Interprétation

### `greaseweazle-1.23/` (Premier dossier)

C'est une **distribution Python package préparée** :
- `setup.py` + `PKG-INFO` : Package Python déjà préparé/installé
- `setup.cfg` : Configuration pour setuptools
- `src/greaseweazle.egg-info/` : Métadonnées du package installé
- `src/greaseweazle/__init__.py` : Package Python généré
- **Prêt pour** : Utilisation directe (déjà "installé") ou `pip install .`

### `greaseweazle-1.23 sources/` (Second dossier)

C'est le **repository source original complet** :
- `Makefile` + `Rules.mk` : Système de build Make
- `MANIFEST.in` : Manifeste pour la distribution Python
- `README.md` : Documentation markdown complète (avec badges, liens)
- `.gitignore` : Fichiers Git à ignorer
- `.github/` : Configuration GitHub (CI/CD, workflows)
- `scripts/win/` : Scripts Windows supplémentaires
- **Prêt pour** : Build depuis les sources avec Make, développement, ou `pip install .`

---

## 🎯 Recommandation

### Pour AlignTester

**Utiliser `greaseweazle-1.23/`** car :
- ✅ Contient `setup.py` : plus facile à installer
- ✅ Structure plus simple : fichiers directement accessibles
- ✅ `PKG-INFO` : package déjà préparé
- ✅ Prêt pour installation Python standard

### Pour le développement Greaseweazle

**Utiliser `greaseweazle-1.23 sources/`** si vous voulez :
- Modifier les sources de Greaseweazle
- Utiliser le système de build Make
- Accéder à la documentation markdown complète (`README.md`)

---

## 📝 Action Recommandée

### Option 1 : Conserver les deux (recommandé pour référence)

Les deux dossiers peuvent coexister :
- `greaseweazle-1.23/` : Pour l'installation et l'utilisation
- `greaseweazle-1.23 sources/` : Pour référence et documentation

### Option 2 : Nettoyer (si redondant)

Si les sources sont identiques, vous pourriez :
- Conserver uniquement `greaseweazle-1.23/` (plus pratique)
- Supprimer `greaseweazle-1.23 sources/` (évite la duplication)

### Option 3 : Déplacer selon la structure du projet

Selon les règles du projet (`RULES.md`), tout devrait être dans `AlignTester/`. Les deux dossiers sont déjà bien placés dans `AlignTester/src/`.

---

## 🔄 Vérification de Similarité

Pour vérifier si le code source est identique :

```bash
cd AlignTester/src
diff -r "greaseweazle-1.23/src" "greaseweazle-1.23 sources/greaseweazle-1.23/src"
```

Si aucun diff n'apparaît → Les sources sont identiques, seule la structure diffère.

---

**Conclusion** : Les deux dossiers contiennent probablement les mêmes sources, mais dans des formats de distribution différents (package Python vs repository source). Pour AlignTester, privilégier `greaseweazle-1.23/` qui est plus pratique à utiliser.

---

**Dernière mise à jour** : Comparaison des deux dossiers Greaseweazle

