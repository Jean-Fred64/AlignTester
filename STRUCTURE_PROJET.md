# Structure du Projet AlignTester

## Organisation des dossiers

Ce projet est organisé pour séparer clairement le **développement** et la **version finale** à publier.

```
Aligntester/
├── AlignTester/          # 🛠️  DÉVELOPPEMENT
│   ├── src/              # Code source (backend + frontend)
│   ├── tests/            # Scripts de tests
│   ├── docs/             # Documentation de développement
│   └── scripts/          # Scripts utilitaires
│       └── prepare_release.py  # Script pour préparer la release
│
├── release/              # 📦 VERSION FINALE (GitHub)
│   └── (fichiers finaux uniquement)
│
├── imd120sc/             # (dossier existant)
├── *.py                  # (fichiers Python existants)
├── *.md                  # (documentation existante)
└── .gitignore            # Exclusion des fichiers temporaires
```

## 🛠️ Dossier AlignTester/ (Développement)

**But** : Contient tous les fichiers nécessaires au développement de l'application web.

### Structure
- **`src/`** : Code source de l'application
  - Backend (FastAPI/Flask)
  - Frontend (React/Vue/Svelte)
  - Configuration
  
- **`tests/`** : Tests et scripts de validation
  - Tests unitaires
  - Tests d'intégration
  - Scripts de test manuels

- **`docs/`** : Documentation de développement
  - Architecture
  - Guide de contribution
  - Notes de développement

- **`scripts/`** : Scripts utilitaires
  - `prepare_release.py` : Prépare la version finale

### Fichiers temporaires
Les fichiers temporaires créés pendant le développement sont automatiquement exclus par `.gitignore`.

## 📦 Dossier release/ (Version finale)

**But** : Contient uniquement les fichiers nécessaires pour utiliser l'application.

### Contenu
- Code source final (nettoyé)
- Documentation utilisateur
- Fichiers de configuration nécessaires
- `requirements.txt` pour les dépendances

### Mise à jour
Utilisez le script `prepare_release.py` pour copier automatiquement les fichiers nécessaires :

```bash
python AlignTester/scripts/prepare_release.py
```

## 🔄 Workflow recommandé

### 1. Développement
```bash
# Travailler dans AlignTester/
cd AlignTester/src
# ... développement ...
```

### 2. Tests
```bash
# Exécuter les tests
cd AlignTester/tests
python test_*.py
```

### 3. Préparation de la release
```bash
# Préparer la version finale
python AlignTester/scripts/prepare_release.py
```

### 4. Vérification
```bash
# Vérifier le contenu de release/
ls release/
# Tester depuis release/
cd release
python app.py  # ou selon votre structure
```

### 5. Publication
```bash
# Commiter uniquement release/ (ou tout le projet selon votre choix)
git add release/
git commit -m "Release v1.0"
git push
```

## 🎯 Avantages de cette structure

✅ **Séparation claire** : Développement vs. version finale  
✅ **GitHub propre** : Seuls les fichiers nécessaires sont publiés  
✅ **Fichiers temporaires exclus** : `.gitignore` gère automatiquement  
✅ **Script automatisé** : `prepare_release.py` simplifie la préparation  
✅ **Flexibilité** : Vous pouvez développer librement dans `AlignTester/`

## 🔧 Alternative : Structure standard

Si vous préférez une structure plus standard, voici une alternative :

```
Aligntester/
├── src/                   # Code source
├── tests/                 # Tests
├── docs/                  # Documentation
├── dist/                  # Build final (généré)
└── .gitignore             # Exclut dist/ et fichiers temporaires
```

**Avantages** :
- Structure plus classique
- `dist/` généré automatiquement (pas besoin de copier manuellement)

**Inconvénients** :
- Moins de contrôle sur ce qui est publié
- Nécessite un système de build

## 📝 Notes

- Le dossier `release/` peut être versionné dans Git ou ignoré (selon votre préférence)
- Vous pouvez créer un `.gitignore` dans `release/` si vous voulez exclure certains fichiers même de la release
- Le script `prepare_release.py` peut être personnalisé selon vos besoins

