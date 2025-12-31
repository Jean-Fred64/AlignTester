# Configuration des Tests - AlignTester

## Installation des dépendances

Avant d'exécuter les tests, vous devez installer les dépendances :

```bash
cd AlignTester

# Si vous utilisez un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Vérification de l'installation

Vérifiez que pytest et les dépendances sont installés :

```bash
pytest --version
python -c "import fastapi; print('FastAPI OK')"
python -c "import pytest_asyncio; print('pytest-asyncio OK')"
```

## Résolution des problèmes courants

### ModuleNotFoundError: No module named 'fastapi'

**Solution** : Installez les dépendances :
```bash
pip install -r requirements.txt
```

### ModuleNotFoundError: No module named 'httpx'

**Note** : `httpx` n'est plus nécessaire dans les tests d'intégration. Si vous voyez cette erreur, mettez à jour les tests.

### PytestUnknownMarkWarning: Unknown pytest.mark.asyncio

**Solution** : Installez `pytest-asyncio` :
```bash
pip install pytest-asyncio
```

Ou utilisez `pytest-asyncio>=0.21.0` qui utilise le mode auto sans configuration.

### ImportError lors des tests

Assurez-vous que le chemin Python inclut le dossier `src/backend` :
- Le fichier `conftest.py` le configure automatiquement
- Si vous avez des problèmes, vérifiez que vous êtes dans le dossier `AlignTester`

## Exécution des tests

Une fois les dépendances installées :

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests d'intégration uniquement
pytest tests/integration/
```

