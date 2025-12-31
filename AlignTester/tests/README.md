# Tests AlignTester

## Structure

```
tests/
├── conftest.py              # Configuration pytest et fixtures
├── pytest.ini               # Configuration pytest
├── unit/                    # Tests unitaires
│   ├── test_alignment_parser.py
│   ├── test_alignment_state.py
│   ├── test_greaseweazle.py
│   └── test_websocket.py
├── integration/             # Tests d'intégration
│   └── test_api.py
└── data/                    # Données de test
    ├── D359T5.txt
    └── ...
```

## Exécution des tests

### Tous les tests

```bash
cd AlignTester
pytest
```

### Tests unitaires uniquement

```bash
pytest tests/unit/
```

### Tests d'intégration uniquement

```bash
pytest tests/integration/
```

### Tests avec couverture

```bash
pytest --cov=src/backend --cov-report=html
```

Le rapport de couverture sera généré dans `htmlcov/index.html`.

### Tests spécifiques

```bash
# Un fichier spécifique
pytest tests/unit/test_alignment_parser.py

# Une classe de test
pytest tests/unit/test_alignment_parser.py::TestAlignmentParser

# Un test spécifique
pytest tests/unit/test_alignment_parser.py::TestAlignmentParser::test_parse_line_complete_format
```

### Tests avec marqueurs

```bash
# Tests unitaires uniquement
pytest -m unit

# Tests d'intégration uniquement
pytest -m integration

# Exclure les tests lents
pytest -m "not slow"
```

## Marqueurs disponibles

- `@pytest.mark.unit`: Tests unitaires
- `@pytest.mark.integration`: Tests d'intégration
- `@pytest.mark.slow`: Tests lents
- `@pytest.mark.websocket`: Tests WebSocket
- `@pytest.mark.api`: Tests API

## Fixtures disponibles

### `sample_alignment_output`
Sortie d'alignement de test avec plusieurs lignes complètes.

### `sample_alignment_lines`
Liste de lignes d'alignement de test.

### `sample_alignment_output_incomplete`
Sortie d'alignement incomplète pour tester les cas limites.

### `sample_statistics`
Statistiques d'alignement de test.

## Notes

- Les tests utilisent `pytest-asyncio` pour les tests asynchrones
- Les tests d'intégration mockent les appels externes (Greaseweazle)
- Les tests WebSocket utilisent des mocks pour simuler les connexions
- Les données de test se trouvent dans `tests/data/`

## Dépendances de test

Les dépendances de test sont dans `requirements.txt`:
- `pytest>=8.3.0`
- `pytest-asyncio>=0.24.0`
- `httpx>=0.27.0`
- `pytest-cov>=4.1.0`
- `pytest-mock>=3.12.0`

## Configuration CI/CD

Pour une intégration continue, ajoutez dans votre workflow:

```yaml
- name: Run tests
  run: |
    cd AlignTester
    pip install -r requirements.txt
    pytest --cov=src/backend --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

