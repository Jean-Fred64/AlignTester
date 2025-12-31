# Proposition : Mode Direct Robuste

**Date :** 21 décembre 2025  
**Problème :** Le mode direct actuel fait planter le frontend à cause d'un trop grand nombre de messages WebSocket  
**Objectif :** Proposer une méthode plus robuste inspirée des outils de référence

---

## 🔍 Analyse du Problème Actuel

### Comportement Actuel du Mode Direct

Le mode direct envoie actuellement des messages WebSocket très fréquemment :

1. **Pendant l'exécution de `gw align`** :
   - Un message `direct_reading` à chaque ligne parsée (ligne ~273 dans `_read_track_direct`)
   - Fréquence : plusieurs messages par seconde pendant ~150-200ms de lecture

2. **À la fin de chaque lecture** :
   - Un message `direct_reading_complete` avec le résultat final (ligne ~367)

3. **Fréquence globale** :
   - Délai entre lectures : **50ms** (configuration `delay_ms`)
   - Lecture complète : ~150-200ms
   - **Total : ~20 lectures/seconde = ~20-40 messages WebSocket/seconde**

### Impact sur le Frontend

- ❌ **Saturation du WebSocket** : Trop de messages à traiter
- ❌ **Re-renders fréquents** : React re-rend trop souvent
- ❌ **Performance dégradée** : UI qui freeze ou plante
- ❌ **Mémoire** : Accumulation de données dans l'historique

---

## 📚 Analyse des Méthodes de Référence

### ImageDisk (Méthode de référence)

**Principe :**
- Lecture séquentielle des IDs de secteurs
- Affichage après chaque lecture complète
- Délai de **100ms** entre lectures
- Pas de notifications en temps réel pendant la lecture

**Code de référence :**
```c
for (int i = 0; i < num_reads; i++) {
    seek(cylinder, head);
    sector_ids = readid();  // Lit tous les IDs
    analyze(sector_ids);     // Analyse la cohérence
    display_results();       // Affiche APRÈS la lecture complète
    delay(100ms);
}
```

**Avantages :**
- ✅ Pas de notifications intermédiaires
- ✅ Affichage uniquement après lecture complète
- ✅ Délai raisonnable (100ms)

### Amiga Test Kit (Feedback temps réel optimisé)

**Principe :**
- Une seule lecture à la fois
- Affichage immédiat après lecture
- Feedback visuel simple (`.`, `X`, `+`, `-`)
- Pas de calculs complexes pendant la boucle

**Code de référence :**
```c
for (;;) {
    disk_read_track(mfmbuf, mfm_bytes);  // Lecture complète
    nr_secs = mfm_decode_track(mfmbuf, headers, data, mfm_bytes);
    
    // Analyse rapide (pas de calculs complexes)
    good = count_valid_sectors(headers);
    
    // Affichage simple (une ligne)
    sprintf(s, "Cyl %u Head %u: %s (%u/11 okay)", cyl, head, map, good);
}
```

**Avantages :**
- ✅ Affichage après lecture complète uniquement
- ✅ Format simple (pas de données volumineuses)
- ✅ Pas de notifications pendant la lecture

---

## 💡 Proposition : Mode Direct Robuste

### Principe Général

1. **Pas de notifications pendant la lecture** : Attendre la fin de `gw align` avant d'envoyer
2. **Throttling côté backend** : Limiter la fréquence d'envoi des messages
3. **Simplification des messages** : Envoyer uniquement les données essentielles
4. **Buffering intelligent** : Regrouper les lectures si nécessaire

### Stratégie 1 : Notification Unique par Lecture (Recommandée)

**Inspirée d'ImageDisk et Amiga Test Kit**

#### Principe

- ✅ Exécuter `gw align` complètement (avec callback pour collecter les lignes)
- ✅ Parser toutes les lignes après la fin de la commande
- ✅ Envoyer UN SEUL message WebSocket avec le résultat final
- ✅ Délai entre lectures : 50ms (conservé pour latence minimale)

#### Implémentation Backend

```python
async def _read_track_direct(self):
    """
    Lit la piste en mode Direct (faible latence)
    Version robuste : notification unique après lecture complète
    """
    track = self.state.current_track
    head = self.state.current_head
    config = MODE_CONFIG[AlignmentMode.DIRECT]
    
    # Collecter toutes les lignes sans notification intermédiaire
    readings_data = []
    
    def on_output(line: str):
        """Callback pour collecter les lignes (sans notifier)"""
        readings_data.append(line)
        # NE PAS notifier ici !
    
    # Exécuter la commande complètement
    result = await self.executor.run_command(args, on_output=on_output, timeout=config["timeout"])
    
    # Parser APRÈS la fin de la commande
    all_readings = AlignmentParser.parse_output("\n".join(readings_data))
    
    if all_readings:
        last_parsed = all_readings[-1]
        percentage = self._calculate_direct_percentage(
            last_parsed.sectors_detected or 0,
            last_parsed.sectors_expected or 18
        )
        
        reading = TrackReading(...)
        
        # UN SEUL message WebSocket avec le résultat final
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

#### Avantages

- ✅ **1 message WebSocket par lecture** (au lieu de 2-10+)
- ✅ **Réduction de 80-90% des messages**
- ✅ **Pas de notifications pendant la lecture** (comme ImageDisk)
- ✅ **Simplification du frontend** (pas besoin de gérer les messages intermédiaires)

#### Délai Optimal

- **50ms** : Conservé pour latence minimale (réglage en temps réel)
- Alternative : **100ms** si 50ms est trop agressif (comme ImageDisk)

### Stratégie 2 : Throttling avec Debouncing (Alternative)

Si on veut garder un feedback pendant la lecture :

#### Principe

- Bufferiser les messages pendant la lecture
- Envoyer uniquement le dernier message toutes les **100-150ms**
- Ignorer les messages intermédiaires

#### Implémentation Backend

```python
class ManualAlignmentMode:
    def __init__(self, ...):
        # ...
        self._direct_reading_buffer: Optional[Dict] = None
        self._direct_reading_timer: Optional[asyncio.Task] = None
        self._direct_throttle_ms = 150  # Max 1 message toutes les 150ms
    
    async def _read_track_direct(self):
        """Version avec throttling"""
        # ...
        
        def on_output(line: str):
            parsed = AlignmentParser.parse_line(line)
            if parsed:
                # Bufferiser au lieu d'envoyer immédiatement
                self._direct_reading_buffer = {
                    "type": "direct_reading",
                    "track": track,
                    "head": head,
                    "percentage": percentage,
                    # ... données essentielles seulement
                }
                # Programmer l'envoi (annule le précédent)
                self._schedule_direct_notification()
        
        # À la fin : envoyer le buffer s'il existe
        if self._direct_reading_buffer:
            self._notify_update(self._direct_reading_buffer)
    
    def _schedule_direct_notification(self):
        """Programme l'envoi du buffer après délai"""
        if self._direct_reading_timer:
            self._direct_reading_timer.cancel()
        
        async def send_buffered():
            await asyncio.sleep(self._direct_throttle_ms / 1000.0)
            if self._direct_reading_buffer:
                self._notify_update(self._direct_reading_buffer)
                self._direct_reading_buffer = None
        
        self._direct_reading_timer = asyncio.create_task(send_buffered())
```

#### Avantages

- ✅ Feedback pendant la lecture (mais limité)
- ✅ Maximum 6-10 messages/seconde (au lieu de 20-40)

#### Inconvénients

- ⚠️ Plus complexe à implémenter
- ⚠️ Toujours plus de messages que la stratégie 1

### Stratégie 3 : Simplification des Messages (Complémentaire)

Réduire la taille des messages WebSocket :

#### Messages Simplifiés

**Actuel (volumineux) :**
```json
{
  "type": "direct_reading",
  "track": 40,
  "head": 0,
  "sectors_detected": 18,
  "sectors_expected": 18,
  "percentage": 100.0,
  "raw_line": "T40.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)",
  "timing": {
    "elapsed_ms": 150.5,
    "timestamp": "2025-12-21T10:30:45.123456",
    "flux_transitions": 227903,
    "time_per_rev_ms": 599.11
  }
}
```

**Proposé (allégé) :**
```json
{
  "type": "direct_reading_complete",
  "t": "40.0",           // track.head (compact)
  "p": 100.0,            // percentage
  "s": "18/18",          // sectors (compact)
  "i": "●●●●●",          // indicator bars (simple)
  "ts": 1703155845123    // timestamp (number, pas string)
}
```

#### Avantages

- ✅ **Réduction de 60-70% de la taille des messages**
- ✅ **Parsing plus rapide côté frontend**
- ✅ **Moins de données JSON à transférer**

---

## 🎯 Recommandation Finale

### Approche Hybrid : Stratégie 1 + Stratégie 3

**Combinaison recommandée :**

1. **Stratégie 1** (Notification unique) : Réduction principale des messages
2. **Stratégie 3** (Simplification) : Réduction de la taille des messages restants

**Résultat attendu :**
- ✅ **1 message WebSocket par lecture** (au lieu de 2-10+)
- ✅ **Messages 60-70% plus petits**
- ✅ **Réduction globale de 85-95% du trafic WebSocket**
- ✅ **Latence maintenue** (50ms entre lectures)
- ✅ **Feedback toujours en temps réel** (mais après lecture complète)

### Comparaison Avant/Après

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Messages/seconde | 20-40 | 2-3 | **85-92%** ↓ |
| Taille message | ~500 bytes | ~150 bytes | **70%** ↓ |
| Trafic WebSocket | ~10-20 KB/s | ~0.3-0.5 KB/s | **95%** ↓ |
| Latence perçue | 50ms | 150-200ms | Acceptable |

**Note :** La latence perçue augmente légèrement (de 50ms à 150-200ms), mais reste excellente pour un réglage en temps réel. Cette augmentation est nécessaire pour éviter la saturation du frontend.

---

## 📝 Implémentation Proposée

### Modifications Backend

1. **Modifier `_read_track_direct()`** :
   - Supprimer les notifications pendant `on_output()`
   - Envoyer uniquement après la fin de la commande
   - Simplifier le format des messages

2. **Simplifier le format des messages** :
   - Utiliser des clés courtes (`t`, `p`, `s`, etc.)
   - Retirer les données redondantes (`raw_line`, etc.)
   - Garder uniquement l'essentiel

3. **Conserver la latence** :
   - Délai de 50ms entre lectures (conservé)
   - La latence perçue sera de 150-200ms (acceptable)

### Modifications Frontend (Optionnelles)

1. **Simplifier le traitement** :
   - Plus besoin de gérer `direct_reading` (messages intermédiaires)
   - Traiter uniquement `direct_reading_complete`

2. **Optimiser les re-renders** :
   - Utiliser `React.memo()` pour les composants d'affichage
   - Éviter les re-renders inutiles

---

## 🧪 Tests de Validation

### Tests à Effectuer

1. **Performance WebSocket** :
   - Mesurer le nombre de messages/seconde
   - Vérifier l'absence de saturation

2. **Latence perçue** :
   - Mesurer le temps entre ajustement et affichage
   - Vérifier que c'est acceptable (< 300ms)

3. **Stabilité frontend** :
   - Tester pendant 5-10 minutes en continu
   - Vérifier l'absence de freeze/plantage

4. **Mémoire** :
   - Vérifier que la mémoire ne monte pas indéfiniment
   - Limiter l'historique si nécessaire

---

## 📚 Références

- **ImageDisk** : Notification après lecture complète, délai 100ms
- **Amiga Test Kit** : Affichage simple après lecture, format compact
- **Document de comparaison** : `COMPARAISON_METHODES_ALIGNEMENT.md`

---

## ✅ Conclusion

La **Stratégie 1 + Stratégie 3** (notification unique + simplification) est la meilleure approche car :

- ✅ **Inspirée des outils de référence** (ImageDisk, Amiga Test Kit)
- ✅ **Réduction massive du trafic WebSocket** (85-95%)
- ✅ **Simplification du code** (moins de complexité)
- ✅ **Latence acceptable** (150-200ms)
- ✅ **Feedback toujours en temps réel** (après chaque lecture)

Cette approche combine les meilleures pratiques des outils de référence avec les contraintes modernes d'une interface web.

