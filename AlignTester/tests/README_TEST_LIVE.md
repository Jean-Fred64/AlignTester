# Guide de Test en Direct du Mode Direct

## 🎯 Objectif

Tester le Mode Direct avec une **vraie disquette** pour vérifier :
- La latence réelle des lectures
- Le feedback en temps réel
- La précision du calcul de pourcentage
- L'expérience utilisateur pour le réglage en direct

---

## 📋 Prérequis

1. **Greaseweazle connecté** et accessible
2. **Disquette formatée** insérée dans le lecteur
3. **Venv activé** avec les dépendances installées

---

## 🚀 Test Simple

### Test par défaut (Piste 40, Tête 0, Format IBM 1.44MB)

```bash
cd /home/jean-fred/Aligntester/AlignTester
source venv/bin/activate
python3 tests/test_mode_direct_live.py
```

Le test va :
- Vérifier la connexion Greaseweazle
- Démarrer le Mode Direct sur la piste 40, tête 0
- Lire en continu pendant 30 secondes
- Afficher les résultats en temps réel avec la latence
- Afficher les statistiques à la fin

### Test avec paramètres personnalisés

```bash
# Tester la piste 0, tête 0
python3 tests/test_mode_direct_live.py --track 0 --head 0

# Tester la piste 79, tête 1
python3 tests/test_mode_direct_live.py --track 79 --head 1

# Tester avec un format différent (IBM 720KB)
python3 tests/test_mode_direct_live.py --format ibm.720

# Tester la piste 40, tête 0, format IBM 1.2MB
python3 tests/test_mode_direct_live.py --track 40 --head 0 --format ibm.1200
```

---

## 📊 Affichage en Temps Réel

Le script affiche en temps réel :

```
[  1] T40.0 | 18/18 secteurs | 100.0% | ✓ excellent  | ████████████ | Latence: 152.3ms
[  2] T40.0 | 18/18 secteurs | 100.0% | ✓ excellent  | ████████████ | Latence: 148.7ms
[  3] T40.0 | 17/18 secteurs |  94.4% | ○ good       | ███████████░ | Latence: 151.2ms
```

**Informations affichées** :
- Numéro de lecture
- Piste et tête
- Secteurs détectés / attendus
- Pourcentage d'alignement
- Symbole et statut (✓ excellent, ○ good, △ caution, ✗ warning)
- Barres visuelles
- Latence en millisecondes

---

## 📈 Statistiques Finales

À la fin du test, les statistiques sont affichées :

```
STATISTIQUES
======================================================================

Nombre de lectures: 45

Pourcentage d'alignement:
  - Moyenne: 98.5%
  - Minimum: 94.4%
  - Maximum: 100.0%

Latence:
  - Moyenne: 150.2ms
  - Minimum: 145.1ms
  - Maximum: 165.3ms
  ✅ Latence excellente (< 300ms)
```

---

## 🎮 Utilisation pour Réglage en Direct

### Scénario 1 : Réglage Grossier

1. **Démarrer le test** :
   ```bash
   python3 tests/test_mode_direct_live.py --track 40 --head 0
   ```

2. **Observer les résultats** en temps réel

3. **Ajuster les vis de réglage** du lecteur pendant que le test tourne

4. **Observer l'impact immédiat** des ajustements (latence ~150-200ms)

5. **Arrêter avec Ctrl+C** quand l'alignement est satisfaisant

### Scénario 2 : Test de Plusieurs Pistes

1. **Tester la piste 0** (bord extérieur) :
   ```bash
   python3 tests/test_mode_direct_live.py --track 0 --head 0
   ```

2. **Tester la piste 40** (centre) :
   ```bash
   python3 tests/test_mode_direct_live.py --track 40 --head 0
   ```

3. **Tester la piste 79** (bord intérieur) :
   ```bash
   python3 tests/test_mode_direct_live.py --track 79 --head 0
   ```

4. **Comparer les résultats** pour vérifier la cohérence

---

## ⚙️ Paramètres Disponibles

| Paramètre | Description | Valeurs | Défaut |
|-----------|-------------|---------|--------|
| `--track` | Numéro de piste | 0-79 | 40 |
| `--head` | Numéro de tête | 0 ou 1 | 0 |
| `--format` | Format de disquette | ibm.1440, ibm.720, ibm.1200, etc. | ibm.1440 |

---

## 🔍 Interprétation des Résultats

### Latence

- **< 200ms** : ✅ Excellente (objectif atteint)
- **200-300ms** : ✅ Bonne (acceptable)
- **300-500ms** : ⚠️ Modérée (peut être améliorée)
- **> 500ms** : ❌ Élevée (problème à investiguer)

### Pourcentage d'Alignement

- **99.0-100%** : ✅ Parfait
- **97.0-98.9%** : ✅ Bon
- **96.0-96.9%** : ⚠️ Moyen
- **< 96.0%** : ❌ Faible (ajustement nécessaire)

### Stabilité

Si les pourcentages varient beaucoup entre les lectures :
- **Variation < 2%** : ✅ Très stable
- **Variation 2-5%** : ⚠️ Instable (peut indiquer un problème)
- **Variation > 5%** : ❌ Très instable (problème probable)

---

## 🐛 Dépannage

### Erreur : "Greaseweazle non connecté"

1. Vérifiez la connexion USB
2. Exécutez le diagnostic :
   ```bash
   python3 tests/diagnose_greaseweazle.py
   ```

### Erreur : "Commande align non disponible"

Vous devez utiliser une version de Greaseweazle compilée depuis la PR #592.

### Latence trop élevée

- Vérifiez la connexion USB (utilisez un port USB 2.0 ou 3.0 direct)
- Vérifiez que le lecteur de disquette fonctionne correctement
- Réduisez la charge système

### Pas de secteurs détectés

- Vérifiez que la disquette est bien insérée
- Vérifiez que le format sélectionné correspond à la disquette
- Testez avec un autre format (ex: `--format ibm.720`)

---

## 📝 Notes

- Le test s'arrête automatiquement après 30 secondes
- Vous pouvez arrêter manuellement avec **Ctrl+C** à tout moment
- Les statistiques sont affichées même si le test est interrompu
- Le Mode Direct utilise 1 lecture par itération avec 50ms d'attente

---

## ✅ Validation

Si le test fonctionne correctement, vous devriez voir :
- ✅ Latence moyenne < 300ms
- ✅ Pourcentages cohérents (variation < 5%)
- ✅ Feedback en temps réel fluide
- ✅ Possibilité d'ajuster les vis et voir l'impact immédiatement

Le Mode Direct est alors prêt pour le réglage en direct ! 🎉

