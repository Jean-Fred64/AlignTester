# Guide de Test des Améliorations d'Alignement

Ce guide vous explique comment tester les nouvelles fonctionnalités d'alignement implémentées dans AlignTester.

---

## 🚀 Démarrage de l'Application

### Option 1 : Script de démarrage automatique

```bash
cd /home/jean-fred/Aligntester/AlignTester
./scripts/start_dev.sh
```

### Option 2 : Démarrage manuel

**Backend** :
```bash
cd /home/jean-fred/Aligntester/AlignTester
source venv/bin/activate
cd src/backend
python main.py
```

**Frontend** (dans un autre terminal) :
```bash
cd /home/jean-fred/Aligntester/AlignTester/src/frontend
npm run dev
```

---

## 🧪 Tests à Effectuer

### Test 1 : Vérification de l'Interface

1. **Ouvrir l'application** : http://localhost:3000 (ou le port affiché par Vite)
2. **Vérifier l'affichage** :
   - Le composant "Test d'alignement" est visible
   - Le composant "Résultats d'alignement" est visible
   - Les champs "Nombre de cylindres" et "Nombre de tentatives" sont présents

### Test 2 : Test d'Alignement avec Lectures Multiples

**Important** : Pour que les nouvelles métriques (cohérence, stabilité, positionnement) soient calculées, il faut **au moins 2 lectures** par piste.

1. **Configurer le test** :
   - **Nombre de cylindres** : `5` (pour un test rapide)
   - **Nombre de tentatives** : `3` (minimum 2 pour calculer la cohérence)

2. **Démarrer l'alignement** :
   - Cliquer sur "Démarrer l'alignement"
   - Observer la barre de progression
   - Attendre la fin du test

3. **Vérifier les résultats** :
   - Le tableau détaillé doit apparaître avec les colonnes :
     - **Piste** : Numéro de piste (ex: 0.0, 0.1, 1.0, ...)
     - **Pourcentage** : Avec icône (✓, ○, ⚠, ✗) et couleur
     - **Secteurs** : Format X/Y (ex: 18/18)
     - **Cohérence** : Score en pourcentage avec couleur
     - **Stabilité** : Score en pourcentage avec couleur
     - **Position** : Icône (✓, ↕, ✗) et statut textuel
     - **Statut** : Cercle coloré + flèches si nécessaire

### Test 3 : Vérification des Indicateurs Visuels

Pour chaque piste dans le tableau, vérifier :

#### Indicateurs de Pourcentage

- **Vert (✓)** : Pourcentage ≥ 99%
- **Bleu (○)** : Pourcentage entre 97% et 98.9%
- **Jaune (⚠)** : Pourcentage entre 96% et 96.9%
- **Rouge (✗)** : Pourcentage < 96%

#### Indicateurs de Cohérence

- **Vert** : Cohérence ≥ 90%
- **Jaune** : Cohérence entre 70% et 89%
- **Rouge** : Cohérence < 70%

#### Indicateurs de Stabilité

- **Vert** : Stabilité ≥ 90%
- **Jaune** : Stabilité entre 70% et 89%
- **Rouge** : Stabilité < 70%

#### Indicateurs de Positionnement

- **✓ (Vert) "Correct"** : Positionnement correct
- **↕ (Jaune) "Instable"** : Positionnement instable
- **✗ (Rouge) "Mauvais"** : Mauvais positionnement

### Test 4 : Test avec Différents Scénarios

#### Scénario A : Alignement Parfait

- **Configuration** : Cylindres = 5, Tentatives = 3
- **Résultat attendu** :
  - Pourcentages ≥ 99% (vert)
  - Cohérence ≥ 90% (vert)
  - Stabilité ≥ 90% (vert)
  - Positionnement "Correct" (✓ vert)

#### Scénario B : Alignement avec Variations

Si vous avez une disquette avec des problèmes d'alignement :

- **Résultat attendu** :
  - Pourcentages variables
  - Cohérence réduite si les lectures varient
  - Stabilité réduite si les timings varient
  - Positionnement "Instable" ou "Mauvais" si l'écart-type est élevé

### Test 5 : Vérification des Statistiques Globales

En haut de la page "Résultats d'alignement", vérifier :

- **Moyenne** : Pourcentage moyen avec qualité (Perfect/Good/Average/Poor)
- **Minimum** : Pourcentage minimum
- **Maximum** : Pourcentage maximum
- **Valeurs totales** : Nombre total de lectures
- **Valeurs utilisées** : Nombre de pistes testées
- **Piste max** : Dernière piste testée

---

## 🔍 Vérification Technique

### Vérifier les Données Backend

**Via l'API** :
```bash
curl http://localhost:8000/api/status | python -m json.tool
```

**Résultat attendu** :
```json
{
  "status": "completed",
  "statistics": {
    "average": 99.07,
    "min": 98.15,
    "max": 100.0,
    "values": [
      {
        "track": "0.0",
        "percentage": 100.0,
        "sectors_detected": 18,
        "sectors_expected": 18,
        "consistency": 95.5,
        "stability": 98.2,
        "positioning_status": "correct"
      }
    ]
  }
}
```

### Vérifier les Logs Backend

Dans le terminal du backend, vous devriez voir :
- Les commandes `gw align` exécutées
- Les valeurs parsées
- Les statistiques calculées

---

## 🐛 Dépannage

### Problème : Les métriques ne s'affichent pas

**Cause** : Le nombre de tentatives est < 2

**Solution** : Augmenter le nombre de tentatives à 2 ou plus

### Problème : Les couleurs ne s'affichent pas correctement

**Cause** : Problème de CSS ou de TailwindCSS

**Solution** : Vérifier que TailwindCSS est bien configuré et que les classes CSS sont correctes

### Problème : Le backend ne démarre pas

**Cause** : Port 8000 déjà utilisé ou erreur Python

**Solution** :
```bash
# Vérifier les processus
ps aux | grep python

# Arrêter les processus
pkill -f "python.*main.py"

# Vérifier les erreurs
cd src/backend
python main.py
```

### Problème : Le frontend ne démarre pas

**Cause** : Port déjà utilisé ou erreur Node.js

**Solution** :
```bash
# Vérifier les processus
ps aux | grep vite

# Arrêter les processus
pkill -f vite

# Vérifier les erreurs
cd src/frontend
npm run dev
```

---

## 📊 Interprétation des Résultats

### Pourcentage d'Alignement

- **≥ 99%** : Alignement parfait, la tête est bien positionnée
- **97-98.9%** : Bon alignement, quelques secteurs peuvent manquer
- **96-96.9%** : Alignement moyen, plusieurs secteurs manquent
- **< 96%** : Mauvais alignement, la tête doit être ajustée

### Cohérence

- **≥ 90%** : Les lectures sont très cohérentes entre elles
- **70-89%** : Les lectures varient un peu, mais restent acceptables
- **< 70%** : Les lectures varient beaucoup, problème de stabilité

### Stabilité

- **≥ 90%** : Les timings sont très stables
- **70-89%** : Les timings varient un peu
- **< 70%** : Les timings varient beaucoup, problème mécanique possible

### Positionnement

- **Correct** : La tête est bien positionnée, pas d'ajustement nécessaire
- **Instable** : La position varie entre les lectures, ajustement recommandé
- **Mauvais** : La position est incorrecte, ajustement nécessaire

---

## ✅ Checklist de Test

- [ ] Backend démarre sans erreur
- [ ] Frontend démarre sans erreur
- [ ] Interface s'affiche correctement
- [ ] Test d'alignement démarre correctement
- [ ] Barre de progression fonctionne
- [ ] Tableau détaillé s'affiche après le test
- [ ] Indicateurs de couleur fonctionnent (vert/bleu/jaune/rouge)
- [ ] Icônes s'affichent correctement (✓, ○, ⚠, ✗, ↕)
- [ ] Scores de cohérence sont calculés et affichés
- [ ] Scores de stabilité sont calculés et affichés
- [ ] Statut de positionnement est affiché
- [ ] Statistiques globales sont correctes
- [ ] Graphiques s'affichent correctement

---

## 🎯 Prochaines Étapes

Après avoir testé les améliorations :

1. **Documenter les résultats** : Noter les valeurs obtenues
2. **Comparer avec les outils de référence** : ImageDisk, dtc, etc.
3. **Ajuster les seuils si nécessaire** : Dans `alignment_parser.py`
4. **Améliorer l'interface** : Si des ajustements sont nécessaires

---

## 📚 Références

- **Documentation des améliorations** : `docs/AMELIORATIONS_ALIGNEMENT.md`
- **Comparaison des méthodes** : `docs/COMPARAISON_METHODES_ALIGNEMENT.md`
- **Documentation ImageDisk** : `docs/IMAGEDISK_ALIGNEMENT.md`

