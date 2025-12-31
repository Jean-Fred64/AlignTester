# Explication des Valeurs Flux Transitions et Temps/Révolution

## 📊 Vue d'ensemble

Ces deux valeurs techniques sont affichées dans la fenêtre "Timings" pour les modes **Ajustage Fin** et **Grande Précision**. Elles fournissent des informations importantes sur la qualité de la lecture et la stabilité mécanique du lecteur de disquette.

---

## 🔍 Flux Transitions (Transitions de flux)

### Qu'est-ce que c'est ?

Le **flux transitions** (ou transitions de flux magnétique) est le nombre de changements de polarité magnétique détectés sur la piste lors de la lecture.

### Comment ça fonctionne ?

1. **Lecture du signal brut** : Greaseweazle lit le signal magnétique brut de la piste
2. **Détection des transitions** : Chaque changement de polarité magnétique (nord→sud ou sud→nord) est compté comme une "transition"
3. **Comptage total** : Le nombre total de transitions est compté pour toute la piste

### Signification pratique

- **Densité de données** : Plus il y a de transitions, plus la piste contient de données
- **Piste formatée vs non formatée** :
  - **Piste formatée** : ~200 000 - 250 000 transitions (exemple : 227 903)
  - **Piste non formatée** : Très peu de transitions (~0-50 000)
- **Qualité de la lecture** : Si la valeur est stable entre plusieurs lectures, cela indique une bonne qualité de lecture

### Exemples de valeurs

| Type de piste | Valeur typique | Signification |
|---------------|----------------|---------------|
| Piste formatée (1.44MB) | ~200 000 - 250 000 | Piste normale avec données |
| Piste formatée (720KB) | ~100 000 - 150 000 | Piste double densité |
| Piste non formatée | ~0 - 50 000 | Piste vierge ou problème |
| Problème de lecture | Variable/incohérent | Alignement défectueux |

### Utilité pour l'alignement

- ✅ **Valeur stable** entre lectures = bon alignement
- ⚠️ **Valeur qui varie beaucoup** = problème d'alignement ou instabilité mécanique
- ❌ **Valeur très faible** = piste non formatée ou problème majeur

---

## ⏱️ Temps/Révolution (Time per Revolution)

### Qu'est-ce que c'est ?

Le **temps/révolution** (ou `time_per_rev`) est le temps nécessaire à la disquette pour effectuer une révolution complète, mesuré en millisecondes.

### Comment ça fonctionne ?

1. **Détection de l'index** : Greaseweazle détecte le marqueur d'index sur la disquette
2. **Mesure du temps** : Le temps entre deux passages du marqueur d'index est mesuré
3. **Moyenne** : Pour plusieurs révolutions, une moyenne est calculée

### Signification pratique

- **Vitesse de rotation** : Indique la vitesse de rotation du disque
- **Stabilité mécanique** : Si la valeur varie, cela peut indiquer un problème mécanique

### Valeurs de référence

| Vitesse de rotation | Temps/révolution | Type de disquette |
|---------------------|------------------|-------------------|
| 300 RPM | ~200 ms | Standard (3.5" et 5.25") |
| 360 RPM | ~166.67 ms | Plus rare |
| 288 RPM | ~208 ms | Quelques lecteurs anciens |

**Formule de conversion** :
```
Temps/révolution (ms) = (60 / RPM) × 1000
Exemple: 300 RPM = (60 / 300) × 1000 = 200 ms
```

### Exemples de valeurs

| Valeur | RPM calculé | État |
|--------|-------------|------|
| 199-201 ms | ~300 RPM | ✅ Normal |
| 166-168 ms | ~360 RPM | ✅ Normal (rare) |
| 195-205 ms | Variable | ⚠️ Légère variation (acceptable) |
| < 190 ms ou > 210 ms | Variable | ❌ Problème mécanique |

### Utilité pour l'alignement

- ✅ **Valeur stable** autour de 200ms = disque tourne correctement
- ⚠️ **Légères variations** (±2-3ms) = acceptable, normal
- ❌ **Variations importantes** (>5-10ms) = problème mécanique du lecteur (moteur instable, courroie usée, etc.)

---

## 🔗 Relation entre les deux valeurs

Ces deux valeurs sont liées :

1. **Plus de révolutions lues** = plus de temps total de lecture
2. **Temps/révolution stable** = conditions de lecture stables
3. **Flux transitions stable** = signal magnétique cohérent

### Exemple d'interprétation

```
Lecture 1: flux_transitions = 227903, time_per_rev = 199.5ms  ✅
Lecture 2: flux_transitions = 227901, time_per_rev = 199.8ms  ✅
Lecture 3: flux_transitions = 227900, time_per_rev = 199.6ms  ✅
```
→ **Bon alignement** : valeurs stables, cohérentes

```
Lecture 1: flux_transitions = 227903, time_per_rev = 199.5ms  ✅
Lecture 2: flux_transitions = 180000, time_per_rev = 205.2ms  ⚠️
Lecture 3: flux_transitions = 240000, time_per_rev = 195.1ms  ⚠️
```
→ **Problème d'alignement** : valeurs incohérentes, instables

---

## 📍 Où sont-elles affichées ?

Ces valeurs sont affichées dans la **fenêtre "Timings"** pour les modes :
- ✅ **Ajustage Fin** (Fine Tune)
- ✅ **Grande Précision** (High Precision)
- ❌ **Mode Direct** : Non affichées (affichage simplifié)

### Emplacement dans l'interface

Dans la section "Dernière lecture", après les valeurs de durée et latence, vous trouverez :
- **Flux transitions** : Nombre avec séparateur de milliers (ex: "227,903")
- **Temps/rev** : Valeur en millisecondes avec 1 décimale (ex: "199.5ms")

### Tooltips explicatifs

En passant la souris sur ces valeurs, vous verrez une explication détaillée dans un tooltip.

---

## 💡 Conseils d'utilisation

### Pour l'alignement

1. **Vérifiez la stabilité** : Les valeurs doivent être cohérentes entre plusieurs lectures
2. **Flux transitions** : Doit rester dans une plage normale pour le type de disquette
3. **Temps/révolution** : Doit être stable autour de 200ms (±2-3ms est acceptable)

### Signaux d'alarme

- **Flux transitions très variable** : Alignement défectueux ou problème de piste
- **Temps/révolution très variable** : Problème mécanique du lecteur (moteur, courroie)
- **Valeurs très différentes entre lectures** : Problème sérieux à investiguer

---

## 📚 Références techniques

- **Greaseweazle** : Ces valeurs proviennent de la commande `gw align` et représentent le flux brut lu
- **Format de sortie** : `T0.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)`
  - `227903` = flux_transitions
  - `599.11ms` = temps total de lecture (pour plusieurs révolutions)
  - `time_per_rev` = temps par révolution (calculé : 599.11ms / nombre de révolutions)

---

## ✅ Résumé

| Valeur | Indique | Utile pour |
|--------|---------|------------|
| **Flux transitions** | Densité de données sur la piste | Vérifier la qualité de la lecture, détecter les pistes formatées |
| **Temps/révolution** | Vitesse de rotation du disque | Vérifier la stabilité mécanique du lecteur |

Ces deux valeurs complètent les informations de pourcentage et de secteurs pour donner une vision complète de la qualité de l'alignement.

