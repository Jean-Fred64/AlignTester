# Test Rapide des Améliorations

## ✅ État Actuel

- ✅ **Backend** : Démarré sur http://localhost:8000
- ✅ **Parser** : Importé avec succès
- ✅ **Nouvelles métriques** : Implémentées (cohérence, stabilité, positionnement)
- ✅ **Feedback visuel** : Implémenté (couleurs, icônes, tableau)

## 🚀 Démarrage Rapide

### 1. Démarrer le Frontend

Dans un nouveau terminal :

```bash
cd /home/jean-fred/Aligntester/AlignTester/src/frontend
npm run dev
```

Le frontend sera accessible sur http://localhost:5173 (ou le port affiché)

### 2. Ouvrir l'Application

Ouvrir votre navigateur et aller sur : **http://localhost:5173**

### 3. Tester les Améliorations

#### Configuration du Test

1. **Nombre de cylindres** : `5` (pour un test rapide)
2. **Nombre de tentatives** : `3` ⚠️ **IMPORTANT** : Minimum 2 pour calculer la cohérence

#### Démarrage

1. Cliquer sur **"Démarrer l'alignement"**
2. Observer la barre de progression
3. Attendre la fin du test

#### Vérification des Résultats

Après le test, vous devriez voir :

1. **Statistiques globales** en haut :
   - Moyenne, Min, Max
   - Qualité (Perfect/Good/Average/Poor)

2. **Tableau détaillé** avec les colonnes :
   - **Piste** : Numéro (ex: 0.0, 0.1)
   - **Pourcentage** : Avec icône (✓, ○, ⚠, ✗) et couleur
   - **Secteurs** : Format X/Y
   - **Cohérence** : Score avec couleur
   - **Stabilité** : Score avec couleur
   - **Position** : Icône (✓, ↕, ✗) et statut
   - **Statut** : Cercle coloré

## 🎨 Indicateurs Visuels à Vérifier

### Couleurs de Pourcentage
- 🟢 **Vert** : ≥ 99% (parfait)
- 🔵 **Bleu** : 97-98.9% (bon)
- 🟡 **Jaune** : 96-96.9% (moyen)
- 🔴 **Rouge** : < 96% (mauvais)

### Icônes de Positionnement
- ✓ **Vert** : Correct
- ↕ **Jaune** : Instable
- ✗ **Rouge** : Mauvais

## 📊 Exemple de Résultat Attendu

```
Piste | Pourcentage | Secteurs | Cohérence | Stabilité | Position | Statut
------|-------------|----------|-----------|----------|----------|-------
0.0   | ✓ 100.00%   | 18/18    | 95.5%     | 98.2%    | ✓ Correct| 🟢
0.1   | ○ 98.15%    | 17/18    | 87.3%     | 92.1%    | ↕ Instable| 🟡
1.0   | ✓ 99.50%    | 18/18    | 98.1%     | 97.5%    | ✓ Correct| 🟢
```

## 🔍 Vérification API

Tester l'API directement :

```bash
# Vérifier le statut
curl http://localhost:8000/api/status

# Vérifier les infos
curl http://localhost:8000/api/info
```

## ⚠️ Notes Importantes

1. **Nombre de tentatives** : Doit être ≥ 2 pour calculer la cohérence et la stabilité
2. **Disquette requise** : Une disquette doit être insérée dans le lecteur
3. **Greaseweazle** : Doit être connecté et configuré

## 🐛 Dépannage

### Backend ne répond pas
```bash
# Vérifier les processus
ps aux | grep python

# Redémarrer
cd /home/jean-fred/Aligntester/AlignTester
source venv/bin/activate
cd src/backend
python main.py
```

### Frontend ne démarre pas
```bash
cd /home/jean-fred/Aligntester/AlignTester/src/frontend
npm install  # Si nécessaire
npm run dev
```

### Les métriques ne s'affichent pas
- Vérifier que le nombre de tentatives est ≥ 2
- Vérifier les logs du backend pour les erreurs
- Vérifier la console du navigateur (F12)

## 📚 Documentation Complète

- **Guide détaillé** : `docs/GUIDE_TEST_AMELIORATIONS.md`
- **Documentation des améliorations** : `docs/AMELIORATIONS_ALIGNEMENT.md`

