# Installation des Dépendances pour les Tests

## Problème : ModuleNotFoundError

Si vous voyez des erreurs comme :
- `ModuleNotFoundError: No module named 'fastapi'`
- `ModuleNotFoundError: No module named 'httpx'`
- `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio`

Cela signifie que les dépendances ne sont pas installées.

## Solution : Installation

### 1. Installer les dépendances

```bash
cd AlignTester
pip install -r requirements.txt
```

### 2. Vérifier l'installation

```bash
# Vérifier pytest
pytest --version

# Vérifier les modules Python
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import pytest_asyncio; print('pytest-asyncio OK')"
```

### 3. Exécuter les tests

```bash
pytest
```

## Si vous utilisez un environnement virtuel (recommandé)

```bash
cd AlignTester

# Créer l'environnement virtuel
python -m venv venv

# Activer (Linux/macOS)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Exécuter les tests
pytest
```

## Dépendances requises pour les tests

D'après `requirements.txt` :
- `pytest>=8.3.0` - Framework de test
- `pytest-asyncio>=0.24.0` - Support async (élimine les warnings asyncio)
- `httpx>=0.27.0` - Client HTTP (optionnel, non utilisé dans les tests actuels)
- `pytest-cov>=4.1.0` - Couverture de code (optionnel)
- `pytest-mock>=3.12.0` - Mocks améliorés (optionnel)
- `fastapi>=0.115.0` - Framework web (nécessaire pour les tests d'intégration)

## Note importante

Les tests d'intégration nécessitent FastAPI pour importer `main.py`. 
Si FastAPI n'est pas installé, les tests d'intégration ne peuvent pas être collectés.

