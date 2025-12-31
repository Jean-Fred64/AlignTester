# Implémentation du Mode Direct - Approche Détaillée

## 🎯 Objectif du Mode Direct

Le Mode Direct vise à permettre un **réglage en temps réel** avec un **feedback immédiat**, inspiré des méthodes d'**ImageDisk** et d'**Amiga Test Kit** documentées dans `IMAGEDISK_ALIGNEMENT.md`.

---

## 📚 Inspiration des Méthodes Documentées

### 1. ImageDisk - Lecture Simple et Répétée

**Ce que fait ImageDisk** (lignes 18-42 de la doc) :
```c
void align(int cylinder, int head) {
    for (int i = 0; i < num_reads; i++) {
        seek(cylinder, head);
        sector_ids = readid();  // Lit les IDs de secteurs
        analyze(sector_ids);     // Analyse la cohérence
        display_results();       // Affiche les résultats
        delay(100ms);
    }
}
```

**Points clés pour le Mode Direct** :
- ✅ **Lecture simple** : Une seule lecture rapide (`readid()`)
- ✅ **Affichage immédiat** : Résultats affichés dès la lecture terminée
- ✅ **Délai minimal** : 100ms entre lectures (on réduira à 50ms)

**Ce qu'on adapte** :
- Au lieu de plusieurs lectures, on fait **1 lecture par itération**
- On affiche **immédiatement** le résultat (secteurs détectés)
- On calcule un **pourcentage basique** : `secteurs_detected / sectors_expected * 100`

---

### 2. Amiga Test Kit - Affichage Temps Réel

**Ce que fait le Testkit** (lignes 345-357 de la doc) :
```
Cyl 40 Head 0 (Lower): ........... (11/11 okay)
```

**Points clés pour le Mode Direct** :
- ✅ **Affichage continu** : Met à jour en temps réel (ligne 383)
- ✅ **Feedback visuel** : Carte des secteurs (`...........`)
- ✅ **Score simple** : `(11/11 okay)` = ratio secteurs valides / attendus

**Ce qu'on adapte** :
- Affichage **continu** avec mise à jour immédiate
- **Indicateur visuel simple** : Barre de qualité ou ratio secteurs
- **Pas de calcul complexe** : Juste le ratio de base

---

## 🔧 Approche d'Implémentation

### Étape 1 : Modifier la Boucle Continue

**Code actuel** (`manual_alignment.py` ligne 118-163) :
```python
async def _continuous_reading_loop(self):
    while self.state.is_running:
        # ...
        await self._read_track_once()  # Lit avec --reads=1
        await asyncio.sleep(0.1)  # 100ms d'attente
```

**Problème** : 
- `_read_track_once()` utilise `--reads=1` mais fait quand même une lecture complète (~600ms)
- L'attente de 100ms est correcte mais la lecture est trop lente

**Solution - Mode Direct** :
```python
async def _continuous_reading_loop(self, mode: AlignmentMode = AlignmentMode.DIRECT):
    """
    Boucle continue adaptée selon le mode
    Mode Direct : Latence minimale, précision basique
    """
    config = MODE_CONFIG[mode]
    
    while self.state.is_running:
        try:
            if self._reading_paused:
                await asyncio.sleep(0.05)  # Attente réduite en mode Direct
                continue
            
            async with self._operation_lock:
                if not self.state.is_running:
                    break
                
                # Lecture adaptée au mode
                if mode == AlignmentMode.DIRECT:
                    await self._read_track_direct()  # Nouvelle méthode optimisée
                else:
                    await self._read_track_once()
            
            # Attente adaptée au mode
            await asyncio.sleep(config["delay_ms"] / 1000.0)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            # Gestion d'erreur...
```

---

### Étape 2 : Créer la Méthode `_read_track_direct()`

**Inspiration ImageDisk** : Lecture simple, affichage immédiat

```python
async def _read_track_direct(self):
    """
    Lit la piste en mode Direct (faible latence)
    Inspiré d'ImageDisk : lecture simple, affichage immédiat
    """
    track = self.state.current_track
    head = self.state.current_head
    
    try:
        # Commande optimisée pour le mode Direct
        tracks_spec = f"c={track}:h={head}"
        args = [
            "align",
            f"--tracks={tracks_spec}",
            "--reads=1",  # Une seule lecture (comme ImageDisk readid())
            f"--format={self.state.format_type}",
            "--revs=2"  # Réduire les révolutions si possible (à tester)
        ]
        
        # Pas de timeout long, on veut une réponse rapide
        readings_data = []
        
        def on_output(line: str):
            """
            Callback pour collecter les lignes (SANS notification)
            ⚠️ IMPORTANT : Ne pas envoyer de notification ici pour éviter la saturation du frontend
            Inspiré d'ImageDisk : affichage APRÈS la lecture complète
            """
            readings_data.append(line)
            # ❌ NE PAS notifier ici - juste collecter les données
            # Les notifications seront envoyées APRÈS la lecture complète
        
        # Exécution avec timeout réduit
        result = await self.executor.run_command(args, on_output=on_output, timeout=5)
        
        # Parser les résultats même si la commande a échoué partiellement
        all_readings = AlignmentParser.parse_output("\n".join(readings_data))
        
        if all_readings:
            last_parsed = all_readings[-1]
            
            # Calcul basique (comme ImageDisk)
            expected_sectors = last_parsed.sectors_expected or 18
            sectors_detected = last_parsed.sectors_detected or 0
            percentage = (sectors_detected / expected_sectors * 100.0) if expected_sectors > 0 else 0.0
            
            # Créer un TrackReading simplifié (pas de calculs complexes)
            reading = TrackReading(
                track=track,
                head=head,
                percentage=round(percentage, 1),  # 1 décimale suffit en mode Direct
                sectors_detected=sectors_detected,
                sectors_expected=expected_sectors,
                quality=self._get_quality_from_percentage(percentage),
                raw_output="\n".join(readings_data)
            )
            
            # Ajouter à l'historique (garder seulement les 20 dernières pour le mode Direct)
            self.state.readings.append(reading)
            if len(self.state.readings) > 20:
                self.state.readings = self.state.readings[-20:]
            
            self.state.last_reading = reading
            
            # ✅ UN SEUL message WebSocket avec le résultat final (comme ImageDisk et Testkit)
            # Cela évite la saturation du frontend (20-40 messages/seconde → 2-3 messages/seconde)
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
            
    except Exception as e:
        # Erreur silencieuse pour ne pas interrompre la boucle
        print(f"[ManualAlignment] Erreur mode Direct: {e}")
        self._notify_update({
            "type": "reading_error",
            "error": str(e),
            "state": self._get_state_dict()
        })
```

---

### Étape 3 : Calcul de Pourcentage Basique (Inspiré ImageDisk)

**ImageDisk** (lignes 116-119) :
- Si 18/18 secteurs → ~100%
- Si 17/18 secteurs → ~94.4%
- Si les IDs varient → pourcentage réduit

**Notre implémentation Mode Direct** :
```python
def _calculate_direct_percentage(self, sectors_detected: int, sectors_expected: int) -> float:
    """
    Calcul basique du pourcentage (Mode Direct)
    Inspiré d'ImageDisk : simple ratio secteurs détectés / attendus
    """
    if sectors_expected == 0:
        return 0.0
    
    percentage = (sectors_detected / sectors_expected) * 100.0
    
    # Arrondir à 1 décimale (suffisant pour le mode Direct)
    return round(percentage, 1)
```

**Pas de calcul complexe** :
- ❌ Pas de médiane
- ❌ Pas d'analyse de cohérence
- ❌ Pas de calcul de stabilité
- ✅ Juste le ratio simple

---

### Étape 4 : Affichage Visuel (Inspiré Testkit)

**Testkit** affiche (ligne 345) :
```
Cyl 40 Head 0 (Lower): ........... (11/11 okay)
```

**Notre affichage Mode Direct** :
```python
def _get_direct_indicator(self, reading: TrackReading) -> Dict:
    """
    Génère un indicateur visuel simple (Mode Direct)
    Inspiré du Testkit : affichage visuel clair
    """
    percentage = reading.percentage
    sectors_ratio = f"{reading.sectors_detected}/{reading.sectors_expected}"
    
    # Barre simple (comme Testkit)
    bar_count = int((percentage / 100.0) * 12)
    bars = "█" * bar_count + "░" * (12 - bar_count)
    
    # Statut simple
    if percentage >= 99.0:
        status = "excellent"
        symbol = "✓"
    elif percentage >= 95.0:
        status = "good"
        symbol = "○"
    elif percentage >= 90.0:
        status = "caution"
        symbol = "△"
    else:
        status = "warning"
        symbol = "✗"
    
    return {
        "percentage": percentage,
        "sectors_ratio": sectors_ratio,
        "bars": bars,
        "status": status,
        "symbol": symbol,
        "message": f"{sectors_ratio} secteurs ({percentage}%)"
    }
```

---

### Étape 5 : Configuration du Mode

**Ajout dans `manual_alignment.py`** :
```python
from enum import Enum

class AlignmentMode(Enum):
    DIRECT = "direct"
    FINE_TUNE = "fine_tune"
    HIGH_PRECISION = "high_precision"

MODE_CONFIG = {
    AlignmentMode.DIRECT: {
        "reads": 1,
        "delay_ms": 50,  # Réduit de 100ms à 50ms
        "timeout": 5,  # Timeout réduit
        "calculate_consistency": False,
        "calculate_stability": False,
        "decimal_places": 1,  # 1 décimale suffit
    },
    # ... autres modes
}
```

**Modification de `ManualAlignmentState`** :
```python
@dataclass
class ManualAlignmentState:
    # ... champs existants
    alignment_mode: AlignmentMode = AlignmentMode.DIRECT  # Nouveau champ
```

---

## 📊 Comparaison : Avant / Après

### Avant (Mode Actuel)

```
Latence totale : ~700ms
├─ Lecture : ~600ms (--reads=1 mais lecture complète)
└─ Attente : 100ms

Calcul : Basique mais avec tous les champs
Affichage : Complet mais peut être lent
```

### Après (Mode Direct)

```
Latence totale : ~150-200ms (objectif)
├─ Lecture : ~100-150ms (optimisée)
└─ Attente : 50ms

Calcul : Ultra-simple (juste ratio)
Affichage : Minimal mais immédiat
```

---

## 🎨 Interface Utilisateur

### Sélection du Mode

**Bouton dans l'interface** :
```tsx
<button
  onClick={() => setMode(AlignmentMode.DIRECT)}
  className={mode === AlignmentMode.DIRECT ? "active" : ""}
>
  ⚡ Mode Direct (Latence: ~150ms)
</button>
```

### Affichage Mode Direct

**Simplifié** (inspiré Testkit) :
```tsx
<div className="direct-mode-display">
  <div className="track-info">
    T{track}.{head}
  </div>
  <div className="sectors-ratio">
    {sectors_detected}/{sectors_expected} secteurs
  </div>
  <div className="percentage">
    {percentage}%
  </div>
  <div className="bars">
    {bars}
  </div>
  <div className="status">
    {symbol} {status}
  </div>
</div>
```

---

## ✅ Avantages de cette Approche

1. **Inspiré des méthodes éprouvées** :
   - ImageDisk : lecture simple, calcul basique
   - Testkit : affichage temps réel, feedback visuel

2. **Latence minimale** :
   - Réduction de ~700ms à ~150-200ms
   - Permet le réglage en direct

3. **Simplicité** :
   - Pas de calculs complexes
   - Affichage immédiat
   - Facile à comprendre

4. **Compatibilité** :
   - S'intègre dans l'architecture existante
   - Peut coexister avec les autres modes

---

## 🚀 Plan d'Implémentation

1. **Étape 1** : Ajouter `AlignmentMode` enum et `MODE_CONFIG`
2. **Étape 2** : Créer `_read_track_direct()` méthode
3. **Étape 3** : Modifier `_continuous_reading_loop()` pour supporter les modes
4. **Étape 4** : Ajouter `_calculate_direct_percentage()` et `_get_direct_indicator()`
5. **Étape 5** : Modifier l'interface utilisateur pour sélectionner le mode
6. **Étape 6** : Tester la latence réelle et ajuster si nécessaire

---

## 📝 Notes Techniques

### ⚠️ Problème Important Identifié

L'implémentation initiale (lignes 137-156) envoyait des notifications **pendant** la lecture, ce qui causait la saturation du frontend (20-40 messages/seconde).

**Correction appliquée** : Envoyer uniquement **UN SEUL message** après la lecture complète, comme ImageDisk et Amiga Test Kit.

Voir `AMELIORATIONS_MODE_DIRECT.md` pour plus de détails sur les améliorations.

### Optimisations Possibles

1. **Réduire les révolutions** :
   - Tester `--revs=1` au lieu de `--revs=2` (si supporté)
   - Peut réduire la latence de ~50-100ms

2. **Simplification des messages** :
   - Utiliser des clés courtes (`t`, `p`, `s`, etc.)
   - Réduire la taille des messages de 60-70%
   - Voir `AMELIORATIONS_MODE_DIRECT.md` pour le format proposé

3. **Cache des résultats** :
   - Garder les 5-10 dernières lectures en mémoire
   - Permet de voir la tendance rapidement

### Limitations

- **Précision limitée** : Suffisante pour voir la direction, pas pour validation finale
- **Pas de cohérence** : Ne détecte pas les variations subtiles
- **Dépend du format** : Nécessite un format valide pour fonctionner

---

## 🔄 Intégration avec les Autres Modes

Le Mode Direct peut être **combiné** avec les autres modes :

1. **Réglage grossier** : Mode Direct (trouver la direction)
2. **Ajustage fin** : Mode Ajustage Fin (affiner)
3. **Validation** : Mode Grande Précision (vérifier)

L'utilisateur peut **changer de mode** à tout moment pendant le réglage.

---

## 📚 Documentation Complémentaire

- **Améliorations proposées** : Voir `AMELIORATIONS_MODE_DIRECT.md` pour des améliorations supplémentaires
- **Comparaison avec outils de référence** : Voir `COMPARAISON_METHODES_ALIGNEMENT.md`
- **Proposition robuste** : Voir `PROPOSITION_MODE_DIRECT_ROBUSTE.md`

