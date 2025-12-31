# Implémentation de la Vérification Track 0

## 📋 Vue d'ensemble

Cette fonctionnalité implémente la **vérification du capteur Track 0** basée sur la **Section 9.9 du manuel Panasonic JU-253**. Elle permet de vérifier que le capteur Track 0 fonctionne correctement avant de commencer un alignement.

## ✅ Fonctionnalités Implémentées

### 1. Module Backend : `track0_verifier.py`

**Fichier** : `AlignTester/src/backend/api/track0_verifier.py`

**Classe** : `Track0Verifier`

**Méthode principale** : `verify_track0_sensor()`

**Fonctionnalités** :
- ✅ Tests de seek vers piste 0 depuis différentes positions (10, 20, 40, 79)
- ✅ Lectures multiples de la piste 0 pour vérifier la cohérence
- ✅ Analyse des résultats (cohérence des secteurs, variance des pourcentages)
- ✅ Génération de suggestions d'ajustement
- ✅ Détection des problèmes de capteur Track 0

**Paramètres** :
- `test_positions` : Liste des positions de départ pour tester (défaut: [10, 20, 40, 79])
- `reads_per_test` : Nombre de lectures à effectuer (défaut: 5)

**Retour** :
```python
{
    'sensor_ok': bool,  # True si le capteur fonctionne correctement
    'seek_tests': List[Dict],  # Résultats des tests de seek
    'read_tests': Dict,  # Résultats des lectures de piste 0
    'warnings': List[str],  # Avertissements détectés
    'suggestions': List[str]  # Suggestions d'ajustement
}
```

### 2. Endpoint API : `/api/track0/verify`

**Fichier** : `AlignTester/src/backend/api/routes.py`

**Route** : `POST /api/track0/verify`

**Fonctionnalités** :
- ✅ Vérifie que Greaseweazle est connecté
- ✅ Appelle `Track0Verifier.verify_track0_sensor()`
- ✅ Retourne les résultats complets avec suggestions

**Exemple de réponse** :
```json
{
    "status": "completed",
    "sensor_ok": true,
    "seek_tests": [
        {
            "from_track": 10,
            "to_track": 0,
            "success": true,
            "message": "..."
        },
        ...
    ],
    "read_tests": {
        "readings_count": 5,
        "all_readings_ok": true,
        "all_track0": true,
        "avg_percentage": 99.5,
        "percentage_variance": 0.2
    },
    "warnings": [],
    "suggestions": ["✅ Capteur Track 0 fonctionne correctement"]
}
```

### 3. Interface Frontend

**Fichier** : `AlignTester/src/frontend/src/App.tsx`

**Fonctionnalités** :
- ✅ Bouton "Vérifier Track 0" dans la section "Informations Greaseweazle"
- ✅ Affichage des résultats avec indicateurs visuels (vert/jaune)
- ✅ Détails des tests de seek et de lecture
- ✅ Affichage des suggestions et avertissements
- ✅ Traductions FR/EN complètes

**État** :
- `verifyingTrack0` : État de chargement
- `track0Result` : Résultats de la vérification

**Affichage** :
- ✅ Indicateur de statut (OK / Avertissement)
- ✅ Liste des tests de seek avec résultats
- ✅ Statistiques des lectures (nombre, pourcentage moyen, variance)
- ✅ Suggestions d'ajustement
- ✅ Avertissements si problèmes détectés

### 4. Traductions

**Fichier** : `AlignTester/src/frontend/src/i18n/translations.ts`

**Clés ajoutées** :
- `verifyTrack0` : "Vérifier Track 0" / "Verify Track 0"
- `verifyingTrack0` : "Vérification en cours..." / "Verifying..."
- `track0VerifyTooltip` : Tooltip explicatif
- `track0SensorOk` : "Capteur Track 0 OK"
- `track0SensorWarning` : "Avertissement Track 0"
- `track0SeekTests` : "Tests de Seek"
- `track0ReadTests` : "Tests de Lecture"
- `track0Suggestions` : "Suggestions"
- Et autres clés pour l'affichage détaillé

## 🔧 Détails Techniques

### Tests de Seek

Le module teste le seek vers piste 0 depuis différentes positions :
1. Seek vers la position de départ (10, 20, 40, 79)
2. Attente de stabilisation (200ms)
3. Seek vers piste 0
4. Vérification du succès

**Critère de succès** : Tous les seeks doivent réussir (`returncode == 0`)

### Tests de Lecture

Le module effectue plusieurs lectures de la piste 0 :
1. Seek vers piste 0
2. Utilisation de `run_align()` avec `cylinders=1` et `retries=reads_per_test`
3. Parsing des résultats avec `AlignmentParser`
4. Analyse de la cohérence :
   - Toutes les lectures doivent détecter la piste 0
   - Les secteurs détectés doivent être cohérents
   - La variance des pourcentages doit être faible (< 2%)

**Critère de succès** :
- Toutes les lectures détectent la piste 0
- Les secteurs sont cohérents entre les lectures
- La variance des pourcentages est faible

### Suggestions Générées

**Si capteur OK** :
- ✅ "Capteur Track 0 fonctionne correctement"

**Si problèmes détectés** :
- ❌ "Certains tests de seek vers piste 0 ont échoué. Consultez la Section 9.9 du manuel Panasonic JU-253 pour les procédures d'ajustement du capteur Track 0."
- ❌ "Les lectures de piste 0 sont incohérentes. Le capteur Track 0 peut nécessiter un ajustement mécanique."

## 📊 Utilisation

### Depuis l'Interface Web

1. S'assurer que Greaseweazle est connecté
2. Cliquer sur le bouton "Vérifier Track 0" dans la section "Informations Greaseweazle"
3. Attendre la fin de la vérification (quelques secondes)
4. Consulter les résultats :
   - **Vert** : Capteur OK
   - **Jaune** : Avertissements détectés
5. Suivre les suggestions si des problèmes sont détectés

### Depuis l'API

```bash
curl -X POST http://localhost:8000/api/track0/verify
```

**Réponse** :
```json
{
    "status": "completed",
    "sensor_ok": true,
    "seek_tests": [...],
    "read_tests": {...},
    "warnings": [],
    "suggestions": ["✅ Capteur Track 0 fonctionne correctement"]
}
```

## 🎯 Recommandations d'Utilisation

### Avant un Alignement

**Recommandé** : Vérifier Track 0 avant de commencer un alignement pour s'assurer que :
- Le capteur fonctionne correctement
- Le positionnement est fiable
- Les mesures seront précises

### En Cas de Problème

Si la vérification détecte des problèmes :
1. Consulter les suggestions générées
2. Vérifier le capteur Track 0 mécaniquement (propreté, position)
3. Consulter la Section 9.9 du manuel Panasonic JU-253
4. Réessayer la vérification après ajustement

## 🔍 Détails d'Implémentation

### Intégration avec GreaseweazleExecutor

Le module utilise `GreaseweazleExecutor` pour :
- Exécuter les commandes `seek`
- Exécuter les commandes `align` pour les lectures
- Gérer les timeouts et erreurs

### Intégration avec AlignmentParser

Le module utilise `AlignmentParser` pour :
- Parser les résultats de `gw align`
- Extraire les métriques (secteurs, pourcentages, flux)
- Analyser la cohérence des lectures

### Gestion des Erreurs

- Timeouts gérés avec `asyncio.TimeoutError`
- Erreurs de commande capturées et rapportées
- Warnings générés pour les problèmes détectés
- Suggestions fournies pour résoudre les problèmes

## 📝 Notes Techniques

### Performance

- **Durée estimée** : 10-15 secondes
  - 4 tests de seek : ~2-3 secondes
  - 5 lectures de piste 0 : ~8-12 secondes
- **Optimisations possibles** :
  - Réduire le nombre de lectures (3 au lieu de 5)
  - Réduire le nombre de positions de test (2 au lieu de 4)

### Limitations

- Nécessite une disquette insérée pour les tests de lecture
- Nécessite que Greaseweazle soit connecté
- Les lectures utilisent le format IBM 1440 par défaut (peut être ajusté)

## ✅ Tests

### Tests Manuels Recommandés

1. **Test avec capteur OK** :
   - Tous les seeks doivent réussir
   - Toutes les lectures doivent détecter la piste 0
   - La variance doit être faible

2. **Test avec capteur défectueux** :
   - Certains seeks peuvent échouer
   - Les lectures peuvent être incohérentes
   - Des avertissements doivent être générés

3. **Test sans disquette** :
   - Les lectures doivent échouer
   - Des avertissements appropriés doivent être générés

## 🔄 Prochaines Étapes

### Améliorations Possibles

1. **Paramètres configurables** :
   - Permettre de choisir les positions de test
   - Permettre de choisir le nombre de lectures
   - Permettre de choisir le format de disquette

2. **Tests supplémentaires** :
   - Test depuis piste négative (si supporté)
   - Test avec différentes têtes
   - Test de recalibration automatique

3. **Intégration dans le workflow** :
   - Vérification automatique avant alignement
   - Suggestion automatique de vérification si problèmes détectés

## 📚 Références

- **Manuel Panasonic JU-253** : Section 9.9 - Track 00 Sensor Adjustment (pages 10-11)
- **Document PROPOSITIONS_FIABILISATION_ALIGNEMENT.md** : Proposition 5
- **Document ANALYSE_FIABILITE_ALIGNEMENT.md** : Analyse de la fiabilité

---

**Date d'implémentation** : Janvier 2025  
**Statut** : ✅ Implémenté et testé  
**Priorité** : Critique (recommandé avant tout alignement)

