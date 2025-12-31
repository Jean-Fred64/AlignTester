# Mode d'Alignement Manuel

Ce document décrit le mode d'alignement manuel interactif, inspiré d'ImageDisk et AmigaTestKit.

---

## 🎯 Vue d'ensemble

Le mode manuel permet de naviguer manuellement entre les pistes d'une disquette et d'analyser l'alignement en temps réel. Il fonctionne comme un système en boucle qui affiche continuellement les résultats de la piste lue et de la tête activée.

---

## 🚀 Fonctionnalités

### Contrôles Disponibles

#### Navigation par Piste
- **`+`** : Avancer d'une piste (+1)
- **`-`** : Reculer d'une piste (-1)
- **`1` à `8`** : Sauter vers les pistes 10, 20, 30, 40, 50, 60, 70, 80

#### Contrôle de la Tête
- **`H`** : Changer de tête (0 ↔ 1)

#### Fonctions Spéciales
- **`R`** : Recalibrer (seek vers track 0)
- **Analyse automatique** : Analyse la piste après chaque déplacement (configurable)

---

## 📡 API REST

### Démarrer le Mode Manuel

```http
POST /api/manual/start
Content-Type: application/json

{
  "initial_track": 0,
  "initial_head": 0
}
```

**Réponse** :
```json
{
  "success": true,
  "state": {
    "is_running": true,
    "current_track": 0,
    "current_head": 0,
    "auto_analyze": true,
    "num_reads": 3,
    "format_type": "ibm.1440"
  }
}
```

### Arrêter le Mode Manuel

```http
POST /api/manual/stop
```

### Déplacer la Tête

#### Seek vers une Piste Spécifique
```http
POST /api/manual/seek
Content-Type: application/json

{
  "track": 40,
  "head": 0
}
```

#### Déplacer d'une Piste
```http
POST /api/manual/move
Content-Type: application/json

{
  "delta": 1  // +1 pour avancer, -1 pour reculer
}
```

#### Sauter vers une Piste
```http
POST /api/manual/jump
Content-Type: application/json

{
  "track_number": 4  // 1-8 pour tracks 10, 20, 30, 40, 50, 60, 70, 80
}
```

### Changer de Tête

```http
POST /api/manual/head
Content-Type: application/json

{
  "head": 1  // 0 ou 1
}
```

### Recalibrer

```http
POST /api/manual/recal
```

### Analyser la Piste Actuelle

```http
POST /api/manual/analyze
```

**Réponse** :
```json
{
  "success": true,
  "reading": {
    "track": 40,
    "head": 0,
    "percentage": 99.5,
    "sectors_detected": 18,
    "sectors_expected": 18,
    "quality": "Perfect",
    "indicator": {
      "percentage": 99.5,
      "quality": "Perfect",
      "distance_from_ideal": 0.5,
      "direction": "stable",
      "bars": "████████████",
      "status": "excellent",
      "sectors_ratio": "18/18",
      "recommendation": "Alignement parfait, aucune action nécessaire"
    }
  },
  "statistics": {
    "average": 99.5,
    "min": 99.2,
    "max": 99.8
  }
}
```

### Récupérer l'État

```http
GET /api/manual/state
```

### Configurer les Paramètres

```http
POST /api/manual/settings
Content-Type: application/json

{
  "auto_analyze": true,
  "num_reads": 5,
  "format_type": "ibm.1440"
}
```

---

## 🔌 WebSocket

Le mode manuel envoie des mises à jour en temps réel via WebSocket.

### Connexion

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Messages Reçus

#### Démarrage
```json
{
  "type": "manual_alignment_update",
  "data": {
    "type": "started",
    "track": 0,
    "head": 0,
    "state": { ... }
  }
}
```

#### Déplacement (Seek)
```json
{
  "type": "manual_alignment_update",
  "data": {
    "type": "seek",
    "track": 40,
    "head": 0,
    "state": { ... }
  }
}
```

#### Lecture en Cours
```json
{
  "type": "manual_alignment_update",
  "data": {
    "type": "reading",
    "line": "T40.0: IBM MFM (18/18 sectors) from Raw Flux (227897 flux in 599.09ms)",
    "parsed": {
      "track": "40.0",
      "percentage": 100.0,
      "sectors_detected": 18,
      "sectors_expected": 18
    }
  }
}
```

#### Analyse Complète
```json
{
  "type": "manual_alignment_update",
  "data": {
    "type": "analysis_complete",
    "reading": {
      "track": 40,
      "head": 0,
      "percentage": 99.5,
      "quality": "Perfect",
      "indicator": { ... }
    },
    "state": { ... }
  }
}
```

#### Recalibration
```json
{
  "type": "manual_alignment_update",
  "data": {
    "type": "recalibrated",
    "state": { ... }
  }
}
```

#### Arrêt
```json
{
  "type": "manual_alignment_update",
  "data": {
    "type": "stopped",
    "state": { ... }
  }
}
```

---

## 📊 Indicateurs Visuels

Le mode manuel génère des indicateurs visuels similaires à AmigaTestKit pour indiquer la qualité d'alignement.

### Barres de Qualité

- **Perfect** (99.0% - 100%) : `████████████` (12 barres)
- **Good** (97.0% - 98.9%) : `██████████░░` (10 barres)
- **Average** (96.0% - 96.9%) : `████████░░░░` (8 barres)
- **Poor** (< 96.0%) : `██████░░░░░░` (6 barres)

### Statuts

- **excellent** : Alignement parfait
- **ok** : Alignement bon
- **caution** : Alignement moyen
- **warning** : Alignement faible

### Direction

- **improving** : Le pourcentage s'améliore par rapport à la lecture précédente
- **degrading** : Le pourcentage se dégrade par rapport à la lecture précédente
- **stable** : Le pourcentage reste stable

---

## 🔧 Implémentation Technique

### Fonctions Greaseweazle Utilisées

Le mode manuel utilise les commandes suivantes de Greaseweazle :

1. **`gw seek <track>`** : Déplace la tête vers une piste spécifique
2. **`gw align --tracks=c=X:h=Y --reads=N --format=ibm.1440`** : Analyse une piste

### Processus d'Analyse

1. **Positionnement** : `gw seek` positionne la tête sur la piste
2. **Lecture répétée** : `gw align` lit la piste plusieurs fois (par défaut 3)
3. **Analyse** : Le parser extrait les informations de chaque lecture
4. **Calcul des métriques** :
   - Pourcentage basé sur les secteurs détectés
   - Cohérence entre les lectures
   - Stabilité des timings
5. **Génération des indicateurs** : Création des barres et recommandations

### Comparaison avec ImageDisk

| Fonctionnalité | ImageDisk | Mode Manuel |
|----------------|-----------|-------------|
| Seek | ✅ `seek(cylindre)` | ✅ `gw seek` |
| Head Selection | ✅ | ✅ `gw seek` avec head |
| Recal | ✅ | ✅ `gw seek 0` |
| Lecture répétée | ✅ `readid()` | ✅ `gw align --reads=N` |
| Analyse des IDs | ✅ | ✅ Parser des secteurs |
| Calcul de pourcentage | ⚠️ Manuel | ✅ Automatique |
| Indicateurs visuels | ❌ | ✅ Barres et statuts |

---

## 💡 Exemple d'Utilisation

### Workflow Typique

1. **Démarrer le mode manuel** :
   ```bash
   POST /api/manual/start
   { "initial_track": 0, "initial_head": 0 }
   ```

2. **Naviguer vers la piste 40** :
   ```bash
   POST /api/manual/jump
   { "track_number": 4 }  # Track 40
   ```

3. **Analyser la piste** :
   ```bash
   POST /api/manual/analyze
   ```

4. **Ajuster finement** :
   ```bash
   POST /api/manual/move
   { "delta": 1 }  # Avancer d'une piste
   ```

5. **Changer de tête** :
   ```bash
   POST /api/manual/head
   { "head": 1 }
   ```

6. **Recalibrer si nécessaire** :
   ```bash
   POST /api/manual/recal
   ```

---

## 🎨 Interface Utilisateur Recommandée

Pour une expérience optimale, l'interface utilisateur devrait :

1. **Afficher en temps réel** :
   - Piste actuelle (track.head)
   - Pourcentage d'alignement
   - Barres de qualité
   - Secteurs détectés/attendus
   - Recommandations

2. **Contrôles clavier** :
   - `+` / `-` : Navigation par piste
   - `1-8` : Saut rapide
   - `H` : Changer de tête
   - `R` : Recalibrer
   - `A` : Analyser manuellement

3. **Indicateurs visuels** :
   - Barres de qualité colorées
   - Flèches de direction (amélioration/dégradation)
   - Messages de statut

---

## 📝 Notes

- Le mode manuel utilise `gw align` pour analyser les pistes, ce qui nécessite que la commande `align` soit disponible (PR #592 de Greaseweazle)
- L'analyse automatique peut être désactivée pour un contrôle manuel complet
- Le nombre de lectures par analyse peut être configuré (1-20, par défaut 3)
- Les résultats sont conservés dans l'historique (100 dernières lectures)

---

## 🔗 Références

- [Documentation ImageDisk](AlignTester/docs/IMAGEDISK_ALIGNEMENT.md)
- [Greaseweazle PR #592](https://github.com/keirf/greaseweazle/pull/592)
- [AmigaTestKit](https://github.com/keirf/amigatestkit)

