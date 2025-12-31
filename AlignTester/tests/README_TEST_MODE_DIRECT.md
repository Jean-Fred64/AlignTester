# Guide de Test du Mode Direct

## 📋 Résumé des Tests

Deux scripts de test ont été créés pour valider le Mode Direct :

1. **`test_mode_direct.py`** : Tests unitaires du backend (sans API)
2. **`test_mode_direct_api.py`** : Tests de l'API REST

---

## 🧪 Test 1 : Tests Unitaires (Backend)

### Exécution (Méthode Simple)

```bash
cd /home/jean-fred/Aligntester/AlignTester
./tests/run_tests.sh unit
```

Le script active automatiquement le venv et exécute les tests.

### Exécution (Méthode Manuelle)

```bash
cd /home/jean-fred/Aligntester
source AlignTester/venv/bin/activate  # Activer le venv
python3 AlignTester/tests/test_mode_direct.py
```

**Note** : Il est important d'activer le venv avant d'exécuter les tests pour avoir accès aux dépendances Python.

### Ce qui est testé

✅ **Configuration des modes** : Vérifie que les 3 modes sont correctement configurés
✅ **Création d'instance** : Vérifie que le mode par défaut est DIRECT
✅ **Calcul de pourcentage** : Teste le calcul basique (ratio secteurs)
✅ **Génération d'indicateur** : Teste l'affichage visuel (barres, symboles)
✅ **Dictionnaire d'état** : Vérifie que l'état contient les informations du mode
✅ **Connexion Greaseweazle** : Vérifie si le matériel est connecté (optionnel)

### Résultats attendus

Tous les tests doivent passer avec ✅. Le dernier test (connexion Greaseweazle) peut afficher ⚠️ si le matériel n'est pas connecté, ce qui est normal.

---

## 🌐 Test 2 : Tests API (REST)

### Prérequis

Le serveur backend doit être démarré :

```bash
cd /home/jean-fred/Aligntester
source AlignTester/venv/bin/activate  # Activer le venv
cd AlignTester/src/backend
python main.py
```

Le serveur devrait être accessible sur `http://localhost:8000`

### Exécution (Méthode Simple)

```bash
cd /home/jean-fred/Aligntester/AlignTester
./tests/run_tests.sh api
```

Le script active automatiquement le venv et exécute les tests.

### Exécution (Méthode Manuelle)

```bash
cd /home/jean-fred/Aligntester
source AlignTester/venv/bin/activate  # Activer le venv
python3 AlignTester/tests/test_mode_direct_api.py
```

### Ce qui est testé

✅ **Endpoint /info** : Vérifie que Greaseweazle est disponible
✅ **Endpoint /manual/state** : Récupère l'état actuel
✅ **Changement de mode** : Teste le changement vers chaque mode
✅ **Mode invalide** : Vérifie que les modes invalides sont rejetés
✅ **Retour au mode Direct** : Vérifie que le mode Direct peut être restauré

### Résultats attendus

Tous les tests doivent passer avec ✅. Si la commande `align` n'est pas disponible, certains tests peuvent échouer.

---

## 🔍 Tests Manuels (Optionnel)

### Test avec le Mode Direct actif

1. **Démarrer le serveur backend** :
   ```bash
   cd /home/jean-fred/Aligntester
   source AlignTester/venv/bin/activate  # Activer le venv
   cd AlignTester/src/backend
   python main.py
   ```

2. **Démarrer le frontend** (dans un autre terminal) :
   ```bash
   cd AlignTester/src/frontend
   npm run dev
   ```

3. **Tester via l'interface web** :
   - Ouvrir `http://localhost:5173` (ou le port du frontend)
   - Aller dans le mode manuel
   - Vérifier que le mode Direct est actif par défaut
   - Observer la latence des lectures (devrait être ~150-200ms)

### Test via curl (API directe)

```bash
# Récupérer l'état
curl http://localhost:8000/api/manual/state

# Changer vers le mode Direct
curl -X POST http://localhost:8000/api/manual/settings \
  -H "Content-Type: application/json" \
  -d '{"alignment_mode": "direct"}'

# Changer vers le mode Fine Tune
curl -X POST http://localhost:8000/api/manual/settings \
  -H "Content-Type: application/json" \
  -d '{"alignment_mode": "fine_tune"}'

# Changer vers le mode High Precision
curl -X POST http://localhost:8000/api/manual/settings \
  -H "Content-Type: application/json" \
  -d '{"alignment_mode": "high_precision"}'
```

---

## 📊 Résultats des Tests

### Tests Unitaires ✅

```
✅ Configuration des modes: OK
✅ Mode par défaut: direct
✅ Changement de mode vers FINE_TUNE: OK
✅ Changement de mode vers DIRECT: OK
✅ Calcul de pourcentage: OK (18/18=100%, 17/18=94.4%, etc.)
✅ Génération d'indicateur: OK (symboles, barres, statuts)
✅ Dictionnaire d'état: OK
✅ TOUS LES TESTS SONT PASSÉS
```

### Tests API (à exécuter)

Les tests API nécessitent que le serveur soit démarré. Exécutez-les pour vérifier que l'API fonctionne correctement.

---

## 🐛 Dépannage

### Erreur : "Module not found"

Assurez-vous d'être dans le bon répertoire et que les chemins Python sont corrects.

### Erreur : "Connection refused" (tests API)

Le serveur backend n'est pas démarré. Démarrez-le avec :
```bash
cd AlignTester/src/backend
python main.py
```

### Erreur : "align command not available"

La commande `align` de Greaseweazle n'est pas disponible. Vérifiez que vous utilisez une version de Greaseweazle compilée depuis la PR #592.

### Tests passent mais latence élevée

La latence réelle dépend du matériel. Le Mode Direct devrait réduire la latence, mais elle peut varier selon :
- La vitesse du lecteur de disquette
- La connexion USB
- La charge du système

---

## ✅ Validation

Si tous les tests passent, le Mode Direct est correctement implémenté et prêt à être utilisé !

