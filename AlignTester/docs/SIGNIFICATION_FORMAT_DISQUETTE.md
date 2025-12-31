# Signification des Paramètres de Format de Disquette

## Exemple : `disk 360`

```cfg
disk 360
    cyls = 40
    heads = 2
    tracks * ibm.mfm
        secs = 9
        bps = 512
        gap3 = 84
        rate = 250
    end
end
```

## Signification de chaque paramètre

### Paramètres de structure du disque

#### `cyls = 40` (Cylindres/Pistes)
- **Signification** : Nombre de pistes (cylindres) sur le disque
- **Exemple** : 40 pistes = disque 5.25" standard
- **Valeurs courantes** : 35, 40, 77, 80
- **Impact** : Détermine la capacité totale du disque

#### `heads = 2` (Têtes/Faces)
- **Signification** : Nombre de faces du disque
- **Exemple** : 2 = disque double face
- **Valeurs courantes** : 1 (simple face), 2 (double face)
- **Impact** : Double la capacité si 2 faces

### Paramètres de format de piste

#### `tracks * ibm.mfm` (Format de piste)
- **Signification** : Type d'encodage utilisé
- **Valeurs courantes** :
  - `ibm.mfm` : Modified Frequency Modulation (standard PC)
  - `ibm.fm` : Frequency Modulation (ancien format)
  - `ibm.scan` : Mode scan automatique
- **Impact** : Détermine comment les données sont encodées magnétiquement

#### `secs = 9` (Secteurs par piste)
- **Signification** : Nombre de secteurs sur chaque piste
- **Exemple** : 9 secteurs = format 360KB (5.25" DD)
- **Valeurs courantes** : 8, 9, 15, 18, 21, 26, 36
- **Impact** : Plus de secteurs = plus de capacité par piste

#### `bps = 512` (Bytes per Sector)
- **Signification** : Taille d'un secteur en octets
- **Exemple** : 512 octets = standard PC
- **Valeurs courantes** : 128, 256, 512, 1024
- **Impact** : Détermine la taille de chaque bloc de données

#### `gap3 = 84` (Gap 3)
- **Signification** : Espace entre les secteurs (en octets)
- **Exemple** : 84 octets = espace standard pour format 360KB
- **Valeurs courantes** : 12, 26, 30, 84, 108
- **Impact** : Permet au contrôleur de synchroniser la lecture
- **Note** : Gap post-DAM (Data Address Mark)

#### `rate = 250` (Data Rate)
- **Signification** : Vitesse de transfert des données en kbps (kilobits par seconde)
- **Exemple** : 250 kbps = Double Density (DD)
- **Valeurs courantes** :
  - `250 kbps` = MFM Double Density (DD) - 5.25" et 3.5" DD
  - `500 kbps` = MFM High Density (HD) - 5.25" HD et 3.5" HD
  - `1000 kbps` = MFM Extended Density (ED) - 3.5" ED
- **Impact** : Détermine la vitesse de rotation et la densité d'enregistrement

#### `rpm = 300` (Revolutions Per Minute) - Optionnel
- **Signification** : Vitesse de rotation du disque en tours par minute
- **Exemple** : 300 RPM = standard pour 5.25"
- **Valeurs courantes** : 300 (5.25"), 360 (3.5")
- **Impact** : Détermine le temps d'accès et la vitesse de lecture

## Calcul de la capacité

**Formule** : `Capacité = cyls × heads × secs × bps`

**Exemple pour `disk 360`** :
- 40 pistes × 2 têtes × 9 secteurs × 512 octets
- = 40 × 2 × 9 × 512
- = 368,640 octets
- = 360 KB (arrondi)

## Affichage dans l'interface

L'interface affiche maintenant ces informations de manière compacte :

```
Détails du format:
  Pistes: 40          Têtes: 2
  Secteurs/piste: 9  Octets/secteur: 512
  Débit: 250 kbps (DD)  Format: MFM
```

Les informations sont affichées dans une grille 2 colonnes pour une lecture facile sans surcharger l'interface.

