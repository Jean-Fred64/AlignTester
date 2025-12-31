# Fonctionnalités de Base - Documentation

## 📋 Vue d'ensemble

Ce document décrit les fonctionnalités de base implémentées pour AlignTester.

---

## ✅ Fonctionnalités Backend

### 1. Exécution de la commande align

**Fichier**: `api/greaseweazle.py`

- ✅ Exécution asynchrone de la commande `gw align`
- ✅ Streaming en temps réel de la sortie
- ✅ Détection automatique de la plateforme (Windows/Linux/macOS)
- ✅ Support des callbacks pour traitement ligne par ligne

**Classe principale**: `GreaseweazleExecutor`

```python
executor = GreaseweazleExecutor()
result = await executor.run_align(cylinders=80, retries=3, on_output=callback)
```

### 2. Parsing des résultats

**Fichier**: `api/alignment_parser.py`

- ✅ Extraction des valeurs de pourcentage depuis la sortie
- ✅ Parsing des numéros de piste (format XX.Y)
- ✅ Extraction des valeurs de base et bandes
- ✅ Calcul des statistiques (moyenne, min, max)
- ✅ Classification de la qualité (Perfect, Good, Average, Poor)

**Format supporté**:
```
00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
```

**Classe principale**: `AlignmentParser`

```python
parser = AlignmentParser()
values = parser.parse_output(output)
statistics = parser.calculate_statistics(values, limit=160)
quality = parser.get_alignment_quality(statistics["average"])
```

### 3. Gestion de l'état

**Fichier**: `api/alignment_state.py`

- ✅ État global de l'alignement (IDLE, RUNNING, COMPLETED, ERROR, CANCELLED)
- ✅ Suivi de la progression en temps réel
- ✅ Stockage des valeurs collectées
- ✅ Gestion thread-safe avec asyncio.Lock

**Classe principale**: `AlignmentStateManager`

```python
await alignment_state_manager.start_alignment(cylinders=80, retries=3, process_task=task)
await alignment_state_manager.add_value(value)
await alignment_state_manager.complete_alignment(statistics)
```

### 4. WebSocket pour temps réel

**Fichier**: `api/websocket.py`

- ✅ Diffusion des mises à jour en temps réel
- ✅ Support de multiples connexions
- ✅ Gestion automatique des déconnexions
- ✅ Messages typés (alignment_update, alignment_complete, etc.)

**Messages WebSocket**:
- `alignment_started`: Notification de démarrage
- `alignment_update`: Nouvelle valeur d'alignement
- `alignment_complete`: Résultats finaux
- `alignment_cancelled`: Annulation
- `alignment_error`: Erreur

### 5. API REST

**Fichier**: `api/routes.py`

**Endpoints**:

- `GET /api/info`: Informations sur Greaseweazle
  ```json
  {
    "platform": "Windows",
    "gw_path": "gw.exe",
    "version": "1.0.0",
    "align_available": true
  }
  ```

- `POST /api/align`: Démarrer un alignement
  ```json
  {
    "cylinders": 80,
    "retries": 3
  }
  ```

- `POST /api/align/cancel`: Annuler l'alignement en cours

- `GET /api/status`: Statut actuel
  ```json
  {
    "status": "running",
    "cylinders": 80,
    "retries": 3,
    "progress_percentage": 45.5,
    "values_count": 73,
    "current_cylinder": 36
  }
  ```

---

## ✅ Fonctionnalités Frontend

### 1. Interface principale

**Fichier**: `src/App.tsx`

- ✅ Affichage des informations Greaseweazle
- ✅ Intégration des composants d'alignement
- ✅ Gestion des erreurs de connexion
- ✅ Rafraîchissement automatique du statut

### 2. Contrôle d'alignement

**Fichier**: `src/components/AlignmentControl.tsx`

- ✅ Formulaire pour démarrer un alignement
  - Nombre de cylindres (1-160)
  - Nombre de tentatives (1-10)
- ✅ Bouton de démarrage/annulation
- ✅ Affichage du statut en temps réel
- ✅ Barre de progression
- ✅ Messages d'erreur contextuels

**Fonctionnalités**:
- Validation des paramètres
- Désactivation du formulaire pendant l'exécution
- Affichage des résultats intermédiaires

### 3. Résultats d'alignement

**Fichier**: `src/components/AlignmentResults.tsx`

- ✅ Affichage des statistiques finales
  - Moyenne, Min, Max
  - Qualité (Perfect/Good/Average/Poor)
  - Nombre de valeurs
  - Piste maximale
- ✅ Graphique en ligne : Évolution du pourcentage
- ✅ Graphique en barres : Répartition par qualité
- ✅ Mise à jour en temps réel via WebSocket

**Graphiques** (Recharts):
- LineChart pour l'évolution temporelle
- BarChart pour la répartition par qualité
- Design dark theme avec TailwindCSS

### 4. Hook WebSocket

**Fichier**: `src/hooks/useWebSocket.ts`

- ✅ Connexion automatique au WebSocket
- ✅ Reconnexion automatique en cas de déconnexion
- ✅ Gestion des messages typés
- ✅ État de connexion (isConnected)

**Utilisation**:
```typescript
const { isConnected, lastMessage } = useWebSocket('ws://localhost:8000/ws');
```

---

## 🔄 Flux de Données

### Démarrage d'un alignement

1. **Frontend** → `POST /api/align` avec paramètres
2. **Backend** → Vérifie disponibilité de `gw align`
3. **Backend** → Crée une tâche asynchrone
4. **Backend** → Envoie `alignment_started` via WebSocket
5. **Backend** → Exécute `gw align` avec callback
6. **Backend** → Parse chaque ligne de sortie
7. **Backend** → Envoie `alignment_update` pour chaque valeur
8. **Frontend** → Reçoit et affiche les mises à jour en temps réel
9. **Backend** → Calcule les statistiques finales
10. **Backend** → Envoie `alignment_complete` avec résultats
11. **Frontend** → Affiche les graphiques et statistiques

### WebSocket Messages

```typescript
// Démarrage
{ type: "alignment_started", cylinders: 80, retries: 3 }

// Mise à jour (pour chaque valeur)
{ 
  type: "alignment_update",
  data: {
    type: "value",
    value: {
      track: "00.0",
      percentage: 99.911,
      base: 1.000,
      bands: [2.002, 3.001, 4.006],
      line_number: 8
    }
  }
}

// Fin
{
  type: "alignment_complete",
  results: {
    success: true,
    statistics: {
      average: 99.523,
      min: 97.234,
      max: 99.999,
      quality: "Perfect",
      total_values: 170,
      used_values: 160,
      track_max: "79.1",
      track_normal: 80.0
    }
  }
}
```

---

## 🎨 Design et UX

### Thème

- **Couleur de fond**: Dark (`bg-gray-900`)
- **Cartes**: `bg-gray-800` avec bordures arrondies
- **Couleurs d'état**:
  - Success: `text-green-400`
  - Warning: `text-yellow-400`
  - Error: `text-red-400`
  - Info: `text-blue-400`

### Composants

- **Formulaire**: Inputs avec style dark, désactivation pendant exécution
- **Boutons**: Couleurs contextuelles (blue pour démarrer, red pour annuler)
- **Graphiques**: Style dark avec grille, tooltips personnalisés
- **Statistiques**: Cards avec grande typographie pour les valeurs importantes

---

## 📊 Statistiques Calculées

### Valeurs extraites

- **Pourcentage d'alignement**: `[XX.XXX%]`
- **Numéro de piste**: `XX.Y` (format track.face)
- **Valeur de base**: `base: X.XXX us`
- **Bandes**: `band: X.XXX us, Y.YYY us, ...`

### Statistiques finales

- **Moyenne**: Moyenne des pourcentages (limite: 160 valeurs par défaut)
- **Minimum**: Valeur minimale
- **Maximum**: Valeur maximale
- **Qualité**: Classification basée sur la moyenne
  - Perfect: ≥ 99.0%
  - Good: 97.0% - 98.9%
  - Average: 96.0% - 96.9%
  - Poor: < 96.0%

---

## 🔧 Configuration

### Backend

- **Port**: 8000 (par défaut)
- **CORS**: Autorise `localhost:3000` et `localhost:5173`
- **WebSocket**: `/ws`

### Frontend

- **API URL**: `http://localhost:8000`
- **WebSocket URL**: `ws://localhost:8000/ws`
- **Dev Server**: Vite sur port 5173 (par défaut)

---

## 🚀 Utilisation

### Démarrage Backend

```bash
cd AlignTester/src/backend
python main.py
# ou
uvicorn main:app --reload
```

### Démarrage Frontend

```bash
cd AlignTester/src/frontend
npm install  # Si première fois
npm run dev
```

### Démarrage complet

Utiliser les scripts dans `AlignTester/scripts/`:
- `start_dev.sh` (Linux/macOS)
- `start_dev.bat` (Windows)

---

## 📝 Notes

- La commande `gw align` doit être disponible (PR #592 de Greaseweazle)
- Le parsing supporte plusieurs formats de sortie
- Les graphiques nécessitent au moins une valeur pour s'afficher
- La connexion WebSocket se reconnecte automatiquement en cas de déconnexion

## 🔗 Ressources Greaseweazle

Voir la documentation complète : `docs/INTEGRATION_GREASEWEAZLE.md`

**Ressources disponibles** :
- Binaire Windows : `/home/jean-fred/Aligntester/greaseweazle-1.23/`
- Sources Python : `/home/jean-fred/Aligntester/AlignTester/src/greaseweazle-1.23/`

---

**Dernière mise à jour**: Développement des fonctionnalités de base terminé

