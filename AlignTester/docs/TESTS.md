# Documentation des Tests - AlignTester

## 📋 Vue d'ensemble

Cette documentation décrit la suite de tests unitaires et d'intégration pour AlignTester.

## 🏗️ Structure des Tests

```
tests/
├── conftest.py              # Configuration pytest et fixtures partagées
├── pytest.ini               # Configuration pytest
├── run_tests.sh             # Script d'exécution des tests
├── README.md                # Guide d'utilisation des tests
├── unit/                    # Tests unitaires
│   ├── test_alignment_parser.py    # Tests du parser
│   ├── test_alignment_state.py     # Tests de gestion d'état
│   ├── test_greaseweazle.py        # Tests de l'exécuteur Greaseweazle
│   └── test_websocket.py           # Tests WebSocket
├── integration/             # Tests d'intégration
│   └── test_api.py                 # Tests de l'API REST
└── data/                    # Données de test
    ├── D359T5.txt
    ├── donnees.txt
    └── ...
```

## 📦 Tests Unitaires

### test_alignment_parser.py

Tests pour le module `alignment_parser.py` qui parse les résultats de la commande align.

**Couverture**:
- ✅ Parsing de lignes complètes avec toutes les informations
- ✅ Parsing avec valeurs manquantes (sans base, sans bandes, etc.)
- ✅ Parsing de sorties multiples lignes
- ✅ Calcul des statistiques (moyenne, min, max)
- ✅ Classification de la qualité (Perfect/Good/Average/Poor)
- ✅ Gestion des cas limites (lignes vides, formats invalides)

**Tests principaux**:
- `test_parse_line_complete_format`: Format complet avec toutes les données
- `test_parse_line_without_base`: Sans valeur de base
- `test_parse_line_without_track`: Sans numéro de piste
- `test_calculate_statistics`: Calcul des statistiques
- `test_get_alignment_quality_*`: Classification par qualité

### test_alignment_state.py

Tests pour le module `alignment_state.py` qui gère l'état de l'alignement.

**Couverture**:
- ✅ Gestion de l'état par défaut
- ✅ Mise à jour de l'état
- ✅ Démarrage d'un alignement
- ✅ Ajout de valeurs
- ✅ Complétion d'un alignement
- ✅ Gestion des erreurs
- ✅ Annulation d'alignement
- ✅ Calcul de progression

**Tests principaux**:
- `test_start_alignment`: Démarrage d'un alignement
- `test_add_value`: Ajout de valeurs avec calcul de progression
- `test_complete_alignment`: Marquage comme terminé
- `test_set_error`: Gestion des erreurs
- `test_cancel_alignment`: Annulation

### test_greaseweazle.py

Tests pour le module `greaseweazle.py` avec mocks pour éviter d'appeler réellement Greaseweazle.

**Couverture**:
- ✅ Détection du chemin Greaseweazle
- ✅ Vérification de version
- ✅ Vérification de disponibilité de la commande align
- ✅ Exécution de commandes asynchrones
- ✅ Streaming de sortie en temps réel
- ✅ Gestion des erreurs d'exécution

**Mocks utilisés**:
- `patch('subprocess.run')`: Pour les commandes synchrones
- `patch('asyncio.create_subprocess_exec')`: Pour les commandes asynchrones

### test_websocket.py

Tests pour le module `websocket.py` qui gère les connexions WebSocket.

**Couverture**:
- ✅ Connexion et déconnexion de clients
- ✅ Envoi de messages personnels
- ✅ Diffusion (broadcast) à tous les clients
- ✅ Gestion des clients déconnectés
- ✅ Messages typés (alignment_update, alignment_complete)

**Tests principaux**:
- `test_connect`: Connexion d'un client
- `test_disconnect`: Déconnexion
- `test_broadcast`: Diffusion à plusieurs clients
- `test_send_alignment_update`: Envoi de mises à jour
- `test_send_alignment_complete`: Envoi de résultats finaux

## 🔗 Tests d'Intégration

### test_api.py

Tests d'intégration pour l'API REST complète.

**Couverture**:
- ✅ Health check (`GET /api/health`)
- ✅ Informations Greaseweazle (`GET /api/info`)
- ✅ Démarrage d'alignement (`POST /api/align`)
- ✅ Statut (`GET /api/status`)
- ✅ Annulation (`POST /api/align/cancel`)
- ✅ Gestion des erreurs
- ✅ Validation des paramètres

**Tests principaux**:
- `test_health_check`: Vérification que l'API répond
- `test_get_info`: Récupération des informations
- `test_start_alignment_success`: Démarrage réussi
- `test_start_alignment_not_available`: Greaseweazle non disponible
- `test_start_alignment_already_running`: Alignement déjà en cours
- `test_get_status_*`: Récupération du statut dans différents états
- `test_cancel_alignment_*`: Annulation

**Client de test**:
Utilise `TestClient` de FastAPI pour tester l'API sans serveur réel.

## 🛠️ Configuration

### pytest.ini

Configuration pytest avec:
- Chemins de recherche des tests
- Marqueurs personnalisés (unit, integration, slow, etc.)
- Mode asyncio automatique
- Dossiers à ignorer

### conftest.py

Fixtures partagées:
- `sample_alignment_output`: Sortie d'alignement complète
- `sample_alignment_lines`: Liste de lignes
- `sample_alignment_output_incomplete`: Cas limites
- `sample_statistics`: Statistiques de test

### Fixtures spécifiques

- `client`: TestClient pour l'API (dans test_api.py)
- `async_client`: AsyncClient pour tests async (optionnel)

## 🚀 Exécution

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

### Avec couverture

```bash
pytest --cov=src/backend --cov-report=html
```

Ouvrir `htmlcov/index.html` pour voir le rapport.

### Tests spécifiques

```bash
# Un fichier
pytest tests/unit/test_alignment_parser.py

# Une classe
pytest tests/unit/test_alignment_parser.py::TestAlignmentParser

# Un test
pytest tests/unit/test_alignment_parser.py::TestAlignmentParser::test_parse_line_complete_format
```

### Avec marqueurs

```bash
# Tests unitaires
pytest -m unit

# Tests d'intégration
pytest -m integration

# Exclure les tests lents
pytest -m "not slow"
```

### Script d'exécution

```bash
./tests/run_tests.sh
```

Ou avec options:

```bash
./tests/run_tests.sh --cov=src/backend --cov-report=term
```

## 📊 Couverture de Code

Objectif: **>80% de couverture**

Modules testés:
- ✅ `alignment_parser.py`: Parsing complet
- ✅ `alignment_state.py`: Gestion d'état complète
- ✅ `greaseweazle.py`: Exécution avec mocks
- ✅ `websocket.py`: Gestion WebSocket
- ✅ `routes.py`: Endpoints API (via tests d'intégration)

## 🔍 Dépendances de Test

Dans `requirements.txt`:
- `pytest>=8.3.0`: Framework de test
- `pytest-asyncio>=0.24.0`: Support async
- `httpx>=0.27.0`: Client HTTP async (optionnel)
- `pytest-cov>=4.1.0`: Couverture de code
- `pytest-mock>=3.12.0`: Mocks améliorés

## 🎯 Bonnes Pratiques

1. **Tests isolés**: Chaque test est indépendant
2. **Mocks appropriés**: Utiliser des mocks pour les dépendances externes
3. **Fixtures partagées**: Réutiliser les fixtures dans conftest.py
4. **Nommage clair**: Noms de tests explicites
5. **Assertions précises**: Vérifier exactement ce qui est attendu
6. **Tests async**: Utiliser `@pytest.mark.asyncio` pour les tests async

## 📝 Ajouter de Nouveaux Tests

### Test unitaire

1. Créer un fichier `test_<module>.py` dans `tests/unit/`
2. Importer le module à tester
3. Créer une classe `Test<Module>`
4. Ajouter des méthodes `test_<scenario>`
5. Utiliser des fixtures si nécessaire

### Test d'intégration

1. Créer dans `tests/integration/`
2. Utiliser `TestClient` ou `AsyncClient`
3. Mocker les dépendances externes
4. Tester les scénarios end-to-end

## ⚠️ Notes Importantes

- Les tests ne nécessitent **pas** Greaseweazle installé (utilisation de mocks)
- Les tests d'intégration mockent les appels externes
- Les tests WebSocket utilisent des mocks pour simuler les connexions
- Les données de test se trouvent dans `tests/data/`

## 🔄 Intégration Continue

Pour CI/CD, ajouter dans le workflow:

```yaml
- name: Install dependencies
  run: |
    cd AlignTester
    pip install -r requirements.txt

- name: Run tests
  run: |
    cd AlignTester
    pytest --cov=src/backend --cov-report=xml --cov-report=term

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

---

**Dernière mise à jour**: Création de la suite de tests complète

