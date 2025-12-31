# Améliorations du Mode Direct

**Date :** 21 décembre 2025  
**Basé sur :** `MODE_DIRECT_IMPLEMENTATION.md` + `PROPOSITION_MODE_DIRECT_ROBUSTE.md`  
**Objectif :** Proposer des améliorations pour rendre le mode direct plus robuste et performant

---

## 🔍 Analyse de l'Implémentation Actuelle

### Problème Principal Identifié

L'implémentation actuelle (lignes 255-286 de `manual_alignment.py`) envoie des messages WebSocket **pendant** l'exécution de `gw align` :

```python
def on_output(line: str):
    """Callback pour traiter la sortie en temps réel"""
    readings_data.append(line)
    parsed = AlignmentParser.parse_line(line)
    if parsed:
        # ⚠️ PROBLÈME : Notification envoyée à chaque ligne parsée
        self._notify_update({
            "type": "direct_reading",
            # ... données ...
        })
```

**Impact :**
- ❌ **20-40 messages WebSocket/seconde** (saturation du frontend)
- ❌ **Re-renders fréquents** (React qui freeze)
- ❌ **Performance dégradée** (UI qui plante)

### Comparaison avec les Outils de Référence

**ImageDisk** : Affiche **APRÈS** la lecture complète
**Amiga Test Kit** : Affiche **APRÈS** la lecture complète  
**Mode Direct Actuel** : Affiche **PENDANT** la lecture (❌ Problème)

---

## ✅ Amélioration 1 : Notification Unique (Priorité Haute)

### Principe

Envoyer **un seul message WebSocket** après la lecture complète, comme ImageDisk et Amiga Test Kit.

### Modification du Code

**Avant (problématique) :**
```python
def on_output(line: str):
    """Callback pour traiter la sortie en temps réel"""
    readings_data.append(line)
    parsed = AlignmentParser.parse_line(line)
    if parsed:
        # ❌ Notification pendant la lecture
        self._notify_update({
            "type": "direct_reading",
            # ...
        })

result = await self.executor.run_command(args, on_output=on_output, timeout=config["timeout"])
# ✅ Notification finale
self._notify_update({
    "type": "direct_reading_complete",
    # ...
})
```

**Après (corrigé) :**
```python
def on_output(line: str):
    """Callback pour collecter les lignes (SANS notification)"""
    readings_data.append(line)
    # ✅ NE PAS notifier ici - juste collecter

# Exécuter la commande complètement
result = await self.executor.run_command(args, on_output=on_output, timeout=config["timeout"])

# Parser APRÈS la fin de la commande
all_readings = AlignmentParser.parse_output("\n".join(readings_data))

if all_readings:
    last_parsed = all_readings[-1]
    # ... calculs ...
    
    # ✅ UN SEUL message WebSocket avec le résultat final
    self._notify_update({
        "type": "direct_reading_complete",
        "reading": self._reading_to_dict(reading),
        "indicator": self._get_direct_indicator(reading),
        "timing": {
            "command_duration_ms": round(command_duration, 1),
            "timestamp": datetime.now().isoformat()
        },
        "state": self._get_state_dict()
    })
```

### Résultat Attendu

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Messages/lecture | 2-10+ | 1 | **85-95%** ↓ |
| Messages/seconde | 20-40 | 2-3 | **85-92%** ↓ |
| Latence perçue | 50ms | 150-200ms | Acceptable |

**Note :** La latence perçue augmente légèrement (de 50ms à 150-200ms), mais reste excellente pour un réglage en temps réel. Cette augmentation est nécessaire pour éviter la saturation du frontend.

---

## ✅ Amélioration 2 : Simplification des Messages (Priorité Moyenne)

### Principe

Réduire la taille des messages WebSocket en utilisant des clés courtes et en supprimant les données redondantes.

### Format Actuel (Volumineux)

```json
{
  "type": "direct_reading_complete",
  "reading": {
    "track": 40,
    "head": 0,
    "percentage": 100.0,
    "sectors_detected": 18,
    "sectors_expected": 18,
    "quality": "PERFECT",
    "flux_transitions": 227903,
    "time_per_rev": 599.11,
    "raw_output": "T40.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)"
  },
  "indicator": {
    "percentage": 100.0,
    "sectors_ratio": "18/18",
    "bars": "████████████",
    "status": "excellent",
    "symbol": "✓",
    "color": "green",
    "message": "18/18 secteurs (100.0%)"
  },
  "timing": {
    "command_duration_ms": 150.5,
    "total_latency_ms": 200.5,
    "delay_ms": 50,
    "timestamp": "2025-12-21T10:30:45.123456",
    "flux_transitions": 227903,
    "time_per_rev_ms": 599.11
  },
  "state": { /* ... état complet ... */ }
}
```

**Taille :** ~500-800 bytes

### Format Proposé (Allégé)

```json
{
  "type": "direct_reading_complete",
  "t": "40.0",           // track.head (compact)
  "p": 100.0,            // percentage
  "s": "18/18",          // sectors (compact)
  "q": "P",              // quality (P=Perfect, G=Good, A=Average, R=Poor)
  "i": "████████████",   // indicator bars
  "st": "✓",             // status symbol
  "ts": 1703155845123,   // timestamp (number, pas string)
  "d": 150               // command_duration_ms (arrondi)
}
```

**Taille :** ~150-200 bytes

### Résultat Attendu

- ✅ **Réduction de 60-70% de la taille des messages**
- ✅ **Parsing plus rapide côté frontend**
- ✅ **Moins de données JSON à transférer**

### Mapping Frontend

Le frontend peut créer un mapping pour convertir les clés courtes :

```typescript
interface DirectReadingCompact {
  type: "direct_reading_complete";
  t: string;    // track.head
  p: number;    // percentage
  s: string;    // sectors ratio
  q: "P" | "G" | "A" | "R";  // quality
  i: string;    // indicator bars
  st: string;   // status symbol
  ts: number;   // timestamp
  d: number;    // duration_ms
}

// Conversion côté frontend
function expandDirectReading(compact: DirectReadingCompact) {
  const [track, head] = compact.t.split('.').map(Number);
  const [detected, expected] = compact.s.split('/').map(Number);
  const qualityMap = { P: "PERFECT", G: "GOOD", A: "AVERAGE", R: "POOR" };
  
  return {
    track,
    head,
    percentage: compact.p,
    sectors_detected: detected,
    sectors_expected: expected,
    quality: qualityMap[compact.q],
    indicator: {
      bars: compact.i,
      symbol: compact.st
    },
    timestamp: new Date(compact.ts),
    duration_ms: compact.d
  };
}
```

---

## ✅ Amélioration 3 : Optimisation de la Commande gw align (Priorité Basse)

### Option A : Réduire les Révolutions

**Test** : Utiliser `--revs=1` au lieu de `--revs=2` (si supporté)

```python
args = [
    "align",
    f"--tracks={tracks_spec}",
    f"--reads={config['reads']}",  # 1 lecture
    f"--format={self.state.format_type}",
    "--revs=1"  # ✅ Tester si cela réduit la latence
]
```

**Résultat attendu :** Réduction de 50-100ms de latence

**Risque :** Peut réduire la précision si `--revs=1` n'est pas suffisant

### Option B : Optimiser le Timeout

**Actuel :** `timeout=5` (5 secondes)

**Proposé :** `timeout=3` (3 secondes) pour le mode Direct

```python
config = MODE_CONFIG[AlignmentMode.DIRECT]
result = await self.executor.run_command(args, on_output=on_output, timeout=config["timeout"])  # 3s au lieu de 5s
```

**Justification :** Une lecture en mode Direct devrait être rapide (~150-200ms). Un timeout de 3s est largement suffisant et permet de détecter les problèmes plus rapidement.

---

## ✅ Amélioration 4 : Cache des Dernières Lectures (Priorité Basse)

### Principe

Conserver les 5-10 dernières lectures en mémoire pour afficher une tendance rapide.

### Implémentation

```python
class ManualAlignmentMode:
    def __init__(self, ...):
        # ...
        self._recent_readings_cache: List[TrackReading] = []  # Cache des dernières lectures
        self._cache_size = 10  # Garder les 10 dernières
    
    async def _read_track_direct(self):
        # ... lecture normale ...
        
        if all_readings:
            reading = TrackReading(...)
            
            # Ajouter au cache
            self._recent_readings_cache.append(reading)
            if len(self._recent_readings_cache) > self._cache_size:
                self._recent_readings_cache = self._recent_readings_cache[-self._cache_size:]
            
            # Calculer la tendance (optionnel)
            if len(self._recent_readings_cache) >= 3:
                recent_percentages = [r.percentage for r in self._recent_readings_cache[-3:]]
                trend = "stable"
                if recent_percentages[-1] > recent_percentages[0]:
                    trend = "improving"
                elif recent_percentages[-1] < recent_percentages[0]:
                    trend = "degrading"
                
                self._notify_update({
                    "type": "direct_reading_complete",
                    # ... données normales ...
                    "trend": trend,  # ✅ Indication de tendance
                    "recent_avg": sum(recent_percentages) / len(recent_percentages)
                })
```

**Avantages :**
- ✅ Indication visuelle de la tendance (amélioration/dégradation)
- ✅ Pas d'impact sur la performance (calcul simple)
- ✅ Aide l'utilisateur à voir si l'ajustement va dans la bonne direction

---

## ✅ Amélioration 5 : Gestion d'Erreur Améliorée (Priorité Moyenne)

### Principe

Gérer les erreurs de manière plus robuste sans interrompre la boucle continue.

### Implémentation

```python
async def _read_track_direct(self):
    track = self.state.current_track
    head = self.state.current_head
    config = MODE_CONFIG[AlignmentMode.DIRECT]
    
    try:
        # ... commande normale ...
        
    except asyncio.TimeoutError:
        # ✅ Timeout spécifique
        print(f"[ManualAlignment] Timeout en mode Direct sur T{track}.{head}")
        self._notify_update({
            "type": "reading_error",
            "error": "Timeout lors de la lecture",
            "track": track,
            "head": head,
            "state": self._get_state_dict()
        })
        # Ne pas interrompre la boucle - continuer après le délai
    
    except subprocess.SubprocessError as e:
        # ✅ Erreur de sous-processus
        print(f"[ManualAlignment] Erreur sous-processus en mode Direct: {e}")
        self._notify_update({
            "type": "reading_error",
            "error": f"Erreur sous-processus: {str(e)}",
            "track": track,
            "head": head,
            "state": self._get_state_dict()
        })
    
    except Exception as e:
        # ✅ Erreur générale
        print(f"[ManualAlignment] Erreur mode Direct: {e}")
        import traceback
        traceback.print_exc()  # Log détaillé pour debug
        self._notify_update({
            "type": "reading_error",
            "error": str(e),
            "state": self._get_state_dict()
        })
    
    # ✅ Toujours continuer - ne jamais interrompre la boucle sauf arrêt explicite
```

**Avantages :**
- ✅ Meilleur diagnostic des erreurs
- ✅ Robustesse accrue (la boucle continue même en cas d'erreur)
- ✅ Logging détaillé pour le debug

---

## 📊 Résumé des Améliorations

| Amélioration | Priorité | Impact | Complexité | Effort |
|--------------|----------|--------|------------|--------|
| 1. Notification unique | 🔴 Haute | Très élevé | Faible | Faible |
| 2. Simplification messages | 🟡 Moyenne | Élevé | Moyenne | Moyen |
| 3. Optimisation commande | 🟢 Basse | Moyen | Faible | Faible |
| 4. Cache des lectures | 🟢 Basse | Faible | Faible | Faible |
| 5. Gestion d'erreur | 🟡 Moyenne | Moyen | Moyenne | Moyen |

### Recommandation d'Implémentation

1. **Étape 1 (Urgent)** : Implémenter l'Amélioration 1 (Notification unique)
   - Impact immédiat sur la stabilité
   - Effort minimal
   - Résout le problème principal

2. **Étape 2 (Important)** : Implémenter l'Amélioration 2 (Simplification messages)
   - Réduction supplémentaire du trafic
   - Amélioration de la performance

3. **Étape 3 (Optionnel)** : Implémenter les autres améliorations selon les besoins

---

## 🎯 Résultat Final Attendu

Avec toutes les améliorations (surtout les 2 premières) :

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Messages/seconde | 20-40 | 2-3 | **85-92%** ↓ |
| Taille message | ~500 bytes | ~150 bytes | **70%** ↓ |
| Trafic WebSocket | ~10-20 KB/s | ~0.3-0.5 KB/s | **95%** ↓ |
| Latence perçue | 50ms | 150-200ms | Acceptable |
| Stabilité frontend | ❌ Plante | ✅ Stable | **100%** ↑ |

---

## 📝 Notes Techniques

### Compatibilité

- ✅ **Rétrocompatible** : Le frontend peut gérer les deux formats (actuel et simplifié)
- ✅ **Migration progressive** : Peut être déployé progressivement
- ✅ **Rollback facile** : Si problème, revenir à l'ancien format

### Tests Recommandés

1. **Test de performance** :
   - Mesurer le nombre de messages/seconde
   - Vérifier l'absence de saturation WebSocket

2. **Test de latence** :
   - Mesurer le temps entre ajustement et affichage
   - Vérifier que < 300ms est acceptable

3. **Test de stabilité** :
   - Exécuter le mode Direct pendant 5-10 minutes
   - Vérifier l'absence de freeze/plantage

4. **Test de mémoire** :
   - Vérifier que la mémoire ne monte pas indéfiniment
   - Limiter l'historique si nécessaire

---

## 🔗 Références

- **Document d'implémentation original** : `MODE_DIRECT_IMPLEMENTATION.md`
- **Proposition robuste** : `PROPOSITION_MODE_DIRECT_ROBUSTE.md`
- **Comparaison méthodes** : `COMPARAISON_METHODES_ALIGNEMENT.md`
- **Code actuel** : `src/backend/api/manual_alignment.py` (lignes 212-388)

