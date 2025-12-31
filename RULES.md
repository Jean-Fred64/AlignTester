# Règles de Structure du Projet AlignTester

Ce document définit les règles à suivre pour maintenir la structure du projet pendant toute la phase de développement.

## 📋 Structure Obligatoire

```
Aligntester/
├── AlignTester/          # 🛠️  DÉVELOPPEMENT UNIQUEMENT
│   ├── src/              # Code source (backend + frontend)
│   ├── tests/            # Scripts de tests
│   ├── docs/             # Documentation de développement
│   └── scripts/          # Scripts utilitaires
│       └── prepare_release.py
│
└── release/              # 📦 VERSION FINALE (GitHub)
    └── (fichiers finaux uniquement)
```

## 🚫 Règles Strictes

### 1. Fichiers de Développement

✅ **À FAIRE** :
- Placer TOUS les fichiers de développement dans `AlignTester/`
- Créer les fichiers temporaires dans `AlignTester/`
- Organiser le code dans les sous-dossiers appropriés (`src/`, `tests/`, `docs/`, `scripts/`)

❌ **À NE PAS FAIRE** :
- Créer des fichiers de développement à la racine du projet
- Créer des fichiers de développement dans `release/`
- Mélanger les fichiers de développement avec les fichiers finaux

### 2. Fichiers de Release

✅ **À FAIRE** :
- Utiliser `AlignTester/scripts/prepare_release.py` pour préparer la release
- Vérifier le contenu de `release/` avant de commiter
- Maintenir `release/` propre et minimal

❌ **À NE PAS FAIRE** :
- Modifier directement les fichiers dans `release/` pendant le développement
- Commiter des fichiers temporaires dans `release/`
- Copier manuellement des fichiers vers `release/` (utiliser le script)

### 3. Organisation du Code

#### Backend
- **Emplacement** : `AlignTester/src/backend/` ou `AlignTester/src/api/`
- **Contenu** : API FastAPI/Flask, intégration Greaseweazle, WebSocket

#### Frontend
- **Emplacement** : `AlignTester/src/frontend/` ou `AlignTester/src/web/`
- **Contenu** : Interface React/Vue/Svelte, CSS, JavaScript

#### Tests
- **Emplacement** : `AlignTester/tests/`
- **Contenu** : Tests unitaires, tests d'intégration, scripts de validation

#### Documentation
- **Développement** : `AlignTester/docs/`
- **Utilisateur** : `release/docs/` (copiée via le script de release)

### 4. Fichiers Temporaires

✅ **Gestion automatique** :
- Le fichier `.gitignore` exclut automatiquement les fichiers temporaires
- Les extensions suivantes sont ignorées : `.tmp`, `.bak`, `.log`, `.pyc`, etc.

❌ **À NE JAMAIS FAIRE** :
- Commiter des fichiers temporaires
- Créer des fichiers de cache dans `release/`

### 5. Workflow de Développement

1. **Développement** : Travailler dans `AlignTester/`
   ```bash
   cd AlignTester/src
   # ... développement ...
   ```

2. **Tests** : Exécuter les tests dans `AlignTester/tests/`
   ```bash
   cd AlignTester/tests
   python test_*.py
   ```

3. **Préparation Release** : Utiliser le script
   ```bash
   python AlignTester/scripts/prepare_release.py
   ```

4. **Vérification** : Vérifier le contenu de `release/`
   ```bash
   ls -la release/
   ```

5. **Commit** : Commiter les changements
   ```bash
   git add AlignTester/ release/
   git commit -m "Description des changements"
   ```

### 6. Commits Git

✅ **Bonnes pratiques** :
- Commiter les changements dans `AlignTester/` normalement
- Commiter `release/` uniquement après avoir exécuté `prepare_release.py`
- Utiliser des messages de commit clairs

❌ **À ÉVITER** :
- Commiter des fichiers temporaires
- Commiter des fichiers de cache
- Commiter `release/` sans avoir exécuté le script de préparation

### 7. Commandes Sudo et Privilèges Administrateur

⚠️ **RÈGLE IMPORTANTE** : Commandes nécessitant des privilèges administrateur

Lorsque l'IA a besoin d'exécuter une commande nécessitant des privilèges administrateur (commande `sudo`), elle doit :

1. **ARRÊTER son raisonnement** et ne pas tenter d'exécuter la commande
2. **Afficher clairement la commande** à exécuter dans un bloc de code
3. **Expliquer brièvement** pourquoi cette commande est nécessaire
4. **Laisser l'utilisateur** copier-coller et exécuter la commande manuellement dans son terminal

**Exemple** :

```bash
# Cette commande nécessite des privilèges administrateur
# Veuillez l'exécuter manuellement dans votre terminal :
sudo apt install nodejs npm
```

**Raison** : Les commandes `sudo` nécessitent souvent une interaction (mot de passe) et ne peuvent pas être exécutées automatiquement par l'IA.

✅ **À FAIRE** :
- Arrêter l'exécution automatique
- Afficher la commande clairement
- Expliquer le contexte
- Attendre la confirmation de l'utilisateur

❌ **À NE PAS FAIRE** :
- Tenter d'exécuter des commandes `sudo` automatiquement
- Utiliser des options non-interactives sans confirmation explicite de l'utilisateur
- Supposer que l'utilisateur a configuré sudo sans mot de passe

## 📁 Exemples de Placement

### ✅ Correct

```
AlignTester/src/backend/app.py          # Backend
AlignTester/src/frontend/index.html     # Frontend
AlignTester/tests/test_api.py           # Tests
AlignTester/docs/architecture.md        # Doc dev
AlignTester/scripts/build.py             # Script utilitaire
```

### ❌ Incorrect

```
app.py                                  # ❌ À la racine
release/src/app.py                      # ❌ Développement dans release/
AlignTester/temp/test.py                # ❌ Dossier temp non prévu
```

## 🔄 Maintenance de la Structure

### Vérification régulière

Avant chaque commit, vérifier :
- [ ] Tous les fichiers de développement sont dans `AlignTester/`
- [ ] Aucun fichier temporaire n'est présent dans `release/`
- [ ] Le script `prepare_release.py` a été exécuté si nécessaire
- [ ] Le `.gitignore` est à jour

### Correction des erreurs

Si un fichier est au mauvais endroit :
1. Le déplacer dans le bon dossier
2. Mettre à jour les imports/références si nécessaire
3. Vérifier que tout fonctionne encore

## 📝 Notes Importantes

- Cette structure doit être maintenue pendant **TOUTE** la phase de développement
- Le dossier `release/` est destiné uniquement aux fichiers finaux
- Utiliser toujours le script `prepare_release.py` pour préparer les releases
- Ne pas hésiter à créer des sous-dossiers dans `AlignTester/` pour mieux organiser

## 🆘 En cas de doute

Si vous n'êtes pas sûr où placer un fichier :
1. Consultez cette documentation
2. Regardez la structure existante
3. En cas de doute, placez-le dans `AlignTester/` (vous pourrez toujours le déplacer)

---

**Dernière mise à jour** : Ajout de la règle sur les commandes sudo (2025-01-XX)  
**Responsable** : Maintenir cette structure pendant tout le développement

