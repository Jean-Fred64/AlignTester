# Comparaison des Méthodes d'Alignement

Ce document compare les différentes méthodes d'alignement de têtes de disquette utilisées dans les outils de référence et notre implémentation AlignTester.

---

## 📋 Outils Analysés

1. **ImageDisk** - Outil DOS classique pour l'alignement
2. **dtc (KryoFlux)** - Outil moderne avec calcul automatique de pourcentages
3. **Greaseweazle `gw align`** - Commande d'alignement de Greaseweazle
4. **Amiga Test Kit** - Suite de tests pour Amiga, incluant un test d'alignement
5. **AlignTester** - Notre implémentation

---

## 🔍 Méthode 1 : ImageDisk

### Principe

ImageDisk accède directement au contrôleur de disquette (FDC 765) et lit les IDs de secteurs.

### Processus

```c
// Pseudo-code ImageDisk
void align(int cylinder, int head) {
    for (int i = 0; i < num_reads; i++) {
        seek(cylinder, head);
        sector_ids = readid();  // Lit les IDs de secteurs (C, H, R, N)
        analyze(sector_ids);     // Analyse la cohérence
        display_results();
        delay(100ms);
    }
}
```

### Format de Sortie

```
Cylinder 40, Head 0:
  Read 1: 18 sectors, IDs: 40,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
  Read 2: 18 sectors, IDs: 40,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
  Read 3: 18 sectors, IDs: 40,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
```

### Calcul du Pourcentage

- **Manuel ou par script** : L'utilisateur/script calcule le pourcentage basé sur :
  - Nombre de secteurs détectés correctement
  - Cohérence des IDs entre les lectures
  - Stabilité des lectures

### Avantages

- ✅ Accès direct au matériel
- ✅ Contrôle précis du processus
- ✅ Résultats détaillés (IDs de secteurs)

### Inconvénients

- ❌ Pas de calcul automatique de pourcentage
- ❌ Nécessite un système DOS
- ❌ Format de sortie non standardisé

---

## 🔍 Méthode 2 : dtc (KryoFlux)

### Principe

dtc lit le flux brut (raw flux) et analyse les transitions de flux pour calculer un pourcentage d'alignement.

### Processus

1. Lit le flux brut de la piste
2. Analyse les transitions de flux
3. Détecte les index marks et les secteurs
4. Calcule la cohérence temporelle (timing)
5. Convertit en pourcentage d'alignement

### Format de Sortie

```
00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
00.1    : base: 1.004 us [99.742%], band: 2.003 us, 3.002 us, 4.007 us
01.0    : base: 1.001 us [99.856%], band: 2.001 us, 3.000 us, 4.005 us
```

### Calcul du Pourcentage

Le pourcentage représente :
- **99.911%** = La piste est lue avec 99.911% de cohérence par rapport à une référence idéale
- Basé sur :
  - La stabilité des timings
  - La cohérence des index marks
  - La qualité du signal

### Avantages

- ✅ Calcul automatique de pourcentage
- ✅ Format standardisé `[XX.XXX%]`
- ✅ Analyse très précise du flux brut
- ✅ Valeurs de référence (base, bands)

### Inconvénients

- ❌ Nécessite un KryoFlux
- ❌ Format spécifique à KryoFlux

---

## 🔍 Méthode 3 : Greaseweazle `gw align`

### Principe

Greaseweazle lit le flux brut et décode le format (si spécifié) pour analyser les secteurs.

### Processus

1. Positionne automatiquement la tête
2. Lit le flux brut plusieurs fois (`--reads=N`)
3. Décode le format (si `--format=XXX` est spécifié)
4. Affiche un résumé pour chaque lecture

### Format de Sortie

```
Aligning T0.0, reading 3 times, revs=3
Format ibm.1440
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)
```

### Calcul du Pourcentage

**Actuellement** : Pas de calcul automatique dans `gw align`

**Notre implémentation** : Nous calculons le pourcentage basé sur :
- `secteurs_detected / secteurs_expected * 100`
- Cohérence entre les lectures multiples
- Stabilité des timings (flux transitions, time_per_rev)

### Avantages

- ✅ Support moderne (Greaseweazle)
- ✅ Accès au flux brut
- ✅ Décodage automatique des formats
- ✅ Informations détaillées (secteurs, flux, timing)

### Inconvénients

- ❌ Pas de calcul automatique de pourcentage (dans `gw align` lui-même)
- ❌ Format de sortie différent de dtc
- ⚠️ Nécessite d'adapter le parser

---

## 🔍 Méthode 4 : Amiga Test Kit (Head Calibration Test)

### Principe

Le test d'alignement d'Amiga Test Kit lit les pistes MFM et analyse les en-têtes de secteurs pour déterminer l'alignement.

### Processus

```c
// Code simplifié de drive_cal_test() dans floppy.c
for (;;) {
    // 1. Lire la piste MFM
    disk_read_track(mfmbuf, mfm_bytes);
    disk_wait_dma(is_hd);
    
    // 2. Décoder les secteurs MFM
    nr_secs = mfm_decode_track(mfmbuf, headers, data, mfm_bytes);
    
    // 3. Analyser les en-têtes de secteurs
    for (i = 0; i < 11; i++)
        map[i] = 'X';  // Par défaut : tous les secteurs manquants
    
    while (nr_secs--) {
        struct sec_header *h = &headers[nr_secs];
        if ((h->format == 0xff) && !h->data_csum && (h->sec < 11)) {
            // Comparer le cylindre détecté avec le cylindre attendu
            map[h->sec] = (((h->trk>>1) > cyl) ? '+' :  // Cylindre trop haut
                          ((h->trk>>1) < cyl) ? '-' :  // Cylindre trop bas
                          '.');                        // Cylindre correct
        }
    }
    
    // 4. Compter les secteurs valides
    good = 0;
    for (i = 0; i < 11; i++) {
        if (map[i] == '.')
            good++;
    }
    
    // 5. Afficher le résultat
    sprintf(s, "Cyl %u Head %u: %s (%u/11 okay)", cyl, head, map, good);
}
```

### Format de Sortie

```
Cyl 40 Head 0 (Lower): ........... (11/11 okay)
Cyl 40 Head 1 (Upper): ........... (11/11 okay)
Cyl 40 Head 0 (Lower): ...X....... (10/11 okay)  // Un secteur manquant
Cyl 40 Head 0 (Lower): ..-........ (10/11 okay)   // Un secteur du cylindre inférieur
```

### Calcul du Pourcentage

- **Affichage** : `(X/11 okay)` pour les disques Amiga (11 secteurs par piste)
- **Indicateurs visuels** :
  - `.` = Secteur correct (cylindre attendu)
  - `X` = Secteur manquant
  - `+` = Secteur du cylindre supérieur (tête trop haute)
  - `-` = Secteur du cylindre inférieur (tête trop basse)

### Caractéristiques Spécifiques

1. **Re-seek automatique** : Peut re-seek périodiquement pour réinitialiser la position
2. **Sélection de tête** : Peut tester une seule tête ou les deux
3. **Navigation manuelle** : L'utilisateur peut changer de cylindre manuellement
4. **Feedback en temps réel** : Affichage continu pendant l'ajustement

### Avantages

- ✅ Feedback visuel immédiat (`.`, `X`, `+`, `-`)
- ✅ Test continu (pas de limite de lectures)
- ✅ Permet l'ajustement manuel en temps réel
- ✅ Détecte les problèmes de positionnement (tête trop haute/basse)
- ✅ Spécifique aux disques Amiga (11 secteurs)

### Inconvénients

- ❌ Spécifique aux disques Amiga (11 secteurs par piste)
- ❌ Nécessite un Amiga pour fonctionner
- ❌ Pas de calcul de pourcentage numérique standardisé
- ❌ Format de sortie non standardisé

---

## 🔍 Méthode 5 : AlignTester (Notre Implémentation)

### Principe

AlignTester utilise Greaseweazle `gw align` et calcule les pourcentages basés sur les secteurs détectés.

### Processus

1. Exécute `gw align --tracks=c=X:h=Y --reads=N --format=XXX`
2. Parse la sortie pour extraire :
   - Nombre de secteurs détectés vs attendus
   - Nombre de transitions de flux
   - Temps par révolution
3. Calcule le pourcentage : `secteurs_detected / secteurs_expected * 100`
4. Groupe les lectures multiples par piste et calcule une moyenne
5. Calcule les statistiques (moyenne, min, max)

### Format de Sortie

```json
{
  "total_values": 6,
  "used_values": 2,
  "average": 99.07,
  "min": 98.15,
  "max": 100.0,
  "track_max": "0.1",
  "track_normal": 2.0,
  "values": [
    {
      "track": "0.0",
      "percentage": 100.0,
      "sectors_detected": 18,
      "sectors_expected": 18,
      "flux_transitions": 227901,
      "time_per_rev": 599.10,
      "format_type": "ibm.1440"
    },
    {
      "track": "0.1",
      "percentage": 98.15,
      "sectors_detected": 17.67,  // Moyenne de 3 lectures
      "sectors_expected": 18,
      "flux_transitions": 227867,
      "time_per_rev": 599.23
    }
  ]
}
```

### Calcul du Pourcentage

**Méthode actuelle** :
```python
percentage = (secteurs_detected / secteurs_expected) * 100.0
```

**Améliorations possibles** (basées sur les autres méthodes) :
1. **Cohérence entre lectures** : Réduire le pourcentage si les lectures varient
2. **Stabilité des timings** : Prendre en compte la variation de `time_per_rev`
3. **Analyse des flux transitions** : Détecter les anomalies dans le flux

### Avantages

- ✅ Interface web moderne
- ✅ Calcul automatique de pourcentage
- ✅ Support de multiples pistes
- ✅ Statistiques détaillées
- ✅ Support de Greaseweazle (matériel moderne)
- ✅ Compatible avec différents formats (IBM MFM, Amiga, etc.)

### Inconvénients

- ⚠️ Calcul de pourcentage simplifié (basé uniquement sur les secteurs)
- ⚠️ Pas d'analyse de cohérence temporelle comme dtc
- ⚠️ Pas de détection de positionnement (tête trop haute/basse) comme Amiga Test Kit

---

## 📊 Tableau Comparatif

| Caractéristique | ImageDisk | dtc (KryoFlux) | gw align | Amiga Test Kit | AlignTester |
|----------------|-----------|----------------|----------|----------------|------------|
| **Calcul auto %** | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Format standardisé** | ❌ | ✅ | ❌ | ❌ | ✅ (JSON) |
| **Analyse flux brut** | ❌ | ✅ | ✅ | ✅ | ✅ (via gw) |
| **Détection position** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Feedback temps réel** | ❌ | ❌ | ❌ | ✅ | ✅ (WebSocket) |
| **Multi-pistes** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Multi-lectures** | ✅ | ❌ | ✅ | ✅ (continu) | ✅ |
| **Interface moderne** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Matériel requis** | FDC 765 | KryoFlux | Greaseweazle | Amiga | Greaseweazle |

---

## 💡 Améliorations Possibles pour AlignTester

### 1. Détection de Positionnement (inspiré d'Amiga Test Kit)

Actuellement, nous ne détectons que le nombre de secteurs. Nous pourrions analyser les IDs de secteurs pour détecter :
- **Tête trop haute** : Secteurs du cylindre supérieur détectés
- **Tête trop basse** : Secteurs du cylindre inférieur détectés
- **Tête correcte** : Secteurs du cylindre attendu uniquement

**Implémentation possible** :
```python
# Analyser les IDs de secteurs dans la sortie de gw align
# Si disponible, extraire les IDs (C, H, R, N) et comparer avec le cylindre attendu
if detected_cylinder > expected_cylinder:
    status = "head_too_high"
elif detected_cylinder < expected_cylinder:
    status = "head_too_low"
else:
    status = "head_correct"
```

### 2. Analyse de Cohérence (inspiré de dtc)

Calculer la cohérence entre les lectures multiples :
```python
# Calculer l'écart-type des pourcentages entre lectures
readings = [100.0, 100.0, 94.44, 100.0]  # Exemple
mean = sum(readings) / len(readings)
std_dev = sqrt(sum((x - mean)**2 for x in readings) / len(readings))

# Réduire le pourcentage si la cohérence est faible
if std_dev > threshold:
    percentage *= (1 - std_dev / 100)
```

### 3. Analyse de Stabilité des Timings

Prendre en compte la variation de `time_per_rev` :
```python
# Si time_per_rev varie beaucoup entre lectures, réduire le pourcentage
readings_time = [599.11, 599.09, 599.09]
mean_time = sum(readings_time) / len(readings_time)
time_variance = max(readings_time) - min(readings_time)

# Réduire le pourcentage si la variance est élevée
if time_variance > threshold:
    percentage *= (1 - time_variance / mean_time)
```

### 4. Feedback Visuel (inspiré d'Amiga Test Kit)

Ajouter des indicateurs visuels dans l'interface :
- ✅ Vert : Secteur correct
- ❌ Rouge : Secteur manquant
- ⬆️ Flèche haut : Tête trop haute
- ⬇️ Flèche bas : Tête trop basse

---

## 🎯 Conclusion

Chaque méthode a ses avantages :

- **ImageDisk** : Accès direct au matériel, contrôle précis
- **dtc (KryoFlux)** : Calcul automatique précis basé sur le flux brut
- **Greaseweazle `gw align`** : Support moderne, accès au flux brut
- **Amiga Test Kit** : Feedback visuel excellent, détection de positionnement
- **AlignTester** : Interface moderne, calcul automatique, support multi-pistes

**Notre implémentation actuelle** combine les avantages de plusieurs méthodes :
- Utilise Greaseweazle (comme `gw align`)
- Calcule automatiquement les pourcentages (comme dtc)
- Fournit un feedback en temps réel (comme Amiga Test Kit)
- Interface web moderne (unique à AlignTester)

**Améliorations futures** pourraient inclure :
- Détection de positionnement (tête trop haute/basse)
- Analyse de cohérence entre lectures
- Analyse de stabilité des timings
- Feedback visuel amélioré

---

## 📚 Références

- **ImageDisk** : Documentation et code source
- **KryoFlux dtc** : Documentation officielle
- **Greaseweazle** : Documentation et code source (PR #592 pour `gw align`)
- **Amiga Test Kit** : Code source dans `testkit/floppy.c`, fonction `drive_cal_test()`
- **AlignTester** : Notre implémentation dans `AlignTester/src/backend/api/`

