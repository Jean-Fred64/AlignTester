# Guide d'Utilisation - AlignTester

## 📋 Table des Matières

1. [Introduction](#introduction)
2. [Configuration Initiale](#configuration-initiale)
3. [Mode Automatique](#mode-automatique)
4. [Mode Manuel](#mode-manuel)
5. [Fonctionnalités Avancées](#fonctionnalités-avancées)
6. [Dépannage](#dépannage)
7. [Annexes](#annexes)

---

## Introduction

### Qu'est-ce qu'AlignTester ?

AlignTester est une application web moderne pour tester et régler l'alignement des têtes de lecteurs de disquette en utilisant la carte Greaseweazle. L'application offre deux modes d'alignement :

- **Mode automatique** : Alignement automatisé qui teste plusieurs pistes consécutivement
- **Mode manuel** : Alignement interactif avec navigation par pistes et analyse en temps réel

### Prérequis

- **Greaseweazle** : Carte Greaseweazle connectée via USB
- **Lecteur de disquette** : Lecteur compatible connecté à Greaseweazle
- **Disquette de test** : Disquette formatée (recommandée pour de meilleurs résultats)
- **Navigateur web** : Navigateur moderne (Chrome, Firefox, Edge, Safari)
- **Greaseweazle v1.23b** : Requis pour les modes d'alignement (Windows uniquement actuellement)

### Compatibilité

| Plateforme | Interface | Mode Automatique | Mode Manuel |
|------------|-----------|------------------|-------------|
| **Windows** | ✅ Fonctionnelle | ✅ Disponible (v1.23b) | ✅ Disponible (v1.23b) |
| **Linux** | ✅ Fonctionnelle | ❌ Non disponible | ❌ Non disponible |
| **macOS** | ✅ Fonctionnelle | ❌ Non disponible | ❌ Non disponible |

**Note importante** : Les deux modes d'alignement nécessitent Greaseweazle v1.23b qui inclut la commande `align` (PR #592). Cette version est actuellement disponible uniquement sur Windows.

---

## Configuration Initiale

### 1. Détection de Greaseweazle

#### Pour les débutants

1. **Connectez votre carte Greaseweazle** à votre ordinateur via USB
2. **Ouvrez AlignTester** dans votre navigateur
3. **Cliquez sur "🔍 Détecter Greaseweazle"** dans la section "Informations Greaseweazle"
4. Attendez quelques secondes pendant la détection
5. Si Greaseweazle est détecté, vous verrez un indicateur vert avec le port COM utilisé

**💡 Astuce** : Le système se souvient du dernier port utilisé pour accélérer la détection lors des prochaines utilisations.

#### Pour les experts

La détection automatique :
- Scanne jusqu'à 192 ports série (COM1-COM192 sur Windows)
- Identifie Greaseweazle via VID/PID USB (VID: 1209, PID: 0001)
- Teste d'abord le port sauvegardé pour accélérer la détection
- Utilise `gw info` pour valider la connexion
- Timeout adaptatif : 5s pour WSL, 2s pour les autres plateformes

**Détection manuelle** : Si la détection automatique échoue, vous pouvez consulter la liste des ports détectés en cliquant sur "Ports détectés" dans les résultats de détection.

### 2. Configuration du Chemin gw.exe

#### Pour les débutants

1. **Développez la section "Informations Greaseweazle"** en cliquant sur la flèche
2. Dans "Configuration du Chemin gw.exe", vous avez trois options :
   - **Détecter automatiquement** : Cliquez sur "🔍 Détecter automatiquement"
   - **Parcourir** : Cliquez sur "Parcourir..." et sélectionnez le fichier `gw.exe`
   - **Saisir manuellement** : Entrez le chemin complet dans le champ texte

3. **Cliquez sur "Définir le Chemin"** pour sauvegarder

**💡 Astuce** : Vous pouvez saisir soit le chemin vers le fichier `gw.exe`, soit le chemin vers le dossier contenant `gw.exe`. Le système cherchera automatiquement le fichier dans le dossier.

#### Pour les experts

**Format du chemin** :
- **Windows** : `C:\chemin\vers\gw.exe` ou `C:\chemin\vers\dossier`
- **Linux/WSL** : `/chemin/vers/gw` ou `/chemin/vers/dossier`
- **macOS** : `/chemin/vers/gw` ou `/chemin/vers/dossier`

**Détection automatique** : Le système cherche `gw.exe` dans :
- Le répertoire courant
- Les chemins PATH système
- Les emplacements courants (Program Files, etc.)

**Validation** : Le système valide que :
- Le fichier existe
- Le fichier est exécutable (`gw.exe` sur Windows, `gw` sur Linux/macOS)
- Le fichier peut être exécuté (permissions)

### 3. Sélection du Lecteur

#### Pour les débutants

1. **Développez la section "Informations Greaseweazle"**
2. Dans "Sélection du Lecteur", choisissez le type de lecteur :
   - **PC** : Pour les lecteurs IBM/PC (Drive A ou B)
   - **Shugart** : Pour les lecteurs Shugart (DS0, DS1, DS2, DS3)

3. **Sélectionnez le lecteur spécifique** :
   - PC : Drive A ou Drive B
   - Shugart : DS0, DS1, DS2 ou DS3

**💡 Astuce** : Si vous ne savez pas quel type de lecteur vous avez, consultez la section "Informations sur les Lecteurs" en cliquant sur "Afficher les détails".

#### Pour les experts

**Types de lecteurs** :

**IBM/PC (A, B)** :
- Deux lecteurs peuvent être connectés
- Chaque lecteur a une ligne motor-enable indépendante
- Tous les lecteurs PC sont strapés pour DS1 (pin 12)
- **Drive A** : Connecté via un câble avec twist sur les pins 10-16
- **Drive B** : Connecté via un câble droit (straight ribbon cable)

**Shugart (0, 1, 2, 3)** :
- Jusqu'à 4 lecteurs peuvent être connectés
- Lignes de sélection DS0-DS3 sur les pins 10, 12, 14 et 16 respectivement
- Tous les lecteurs partagent un signal motor-select commun sur le pin 16

**Dépannage Track 0** :
- Si erreur "Track 0 not found" avec lecteur Shugart strapé pour DS0 : Utiliser `--drive 0` avec câble droit
- Si erreur "Track 0 not found" avec lecteur PC et câble droit : Utiliser `--drive B`

### 4. Test du Lecteur

#### Pour les débutants

1. **Assurez-vous que Greaseweazle est connecté** (indicateur vert visible)
2. **Cliquez sur "Tester le Lecteur"**
3. Vous devriez entendre le lecteur se déplacer (commande seek vers la piste 20)

**💡 Astuce** : Ce test permet de vérifier que le lecteur répond correctement aux commandes avant de commencer un alignement.

#### Pour les experts

Le test du lecteur envoie une séquence de commandes `gw seek` :
- Seek vers la piste 20
- Retour sonore pour confirmation
- Utilise le lecteur sélectionné dans les paramètres

**Utilisation** : Utile pour diagnostiquer les problèmes de connexion ou de configuration du lecteur.

### 5. Vérification Track 0

#### Pour les débutants

1. **Assurez-vous que Greaseweazle est connecté**
2. **Insérez une disquette dans le lecteur** : Une disquette doit être présente dans le lecteur de disquette pour effectuer la vérification. Si possible, utilisez une disquette formatée usine pour de meilleurs résultats.
3. **Sélectionnez le format de disquette correspondant** : Il est impératif de choisir le bon format de disquette (voir section "Sélection du Format de Disquette") pour que le test soit correctement validé. Le format doit correspondre à la disquette insérée.
4. **Cliquez sur "Vérifier Track 0"**
5. Attendez la fin de la vérification (quelques secondes)
6. Consultez les résultats :
   - **✅ Capteur Track 0 OK** : Tout fonctionne correctement
   - **⚠️ Avertissement Track 0** : Des problèmes mineurs ont été détectés

**💡 Astuce** : Il est recommandé de vérifier Track 0 avant de commencer un alignement, surtout si vous rencontrez des problèmes. Assurez-vous que la disquette est correctement insérée et que le format sélectionné correspond bien à votre disquette.

#### Pour les experts

**Prérequis importants** :
- **Disquette requise** : Une disquette doit être insérée dans le lecteur pour effectuer les tests de lecture. Une disquette formatée usine est recommandée pour garantir des résultats fiables.
- **Format de disquette** : Le format sélectionné est utilisé pour valider les limites de pistes et analyser les résultats. Un format incorrect peut donner des résultats invalides ou trompeurs.

La vérification Track 0 effectue plusieurs tests (selon Section 9.9 du manuel Panasonic) :

**Tests de Seek** :
- Seek depuis différentes pistes vers Track 0
- Vérifie que le capteur Track 0 répond correctement
- Teste la précision du positionnement

**Tests de Lecture** :
- Effectue plusieurs lectures sur Track 0
- Utilise le format sélectionné pour valider les résultats
- Calcule le pourcentage moyen d'alignement
- Analyse la variance des pourcentages

**Interprétation des résultats** :
- **Sensor OK** : Tous les tests réussis, capteur fonctionnel
- **Warnings** : Certains tests ont échoué, mais le capteur peut encore fonctionner
- **Suggestions** : Recommandations pour corriger les problèmes détectés

**Note technique** : Les tests de lecture nécessitent une disquette formatée pour analyser correctement les secteurs et calculer les pourcentages d'alignement. Un format incorrect peut fausser les résultats.

### 6. Sélection du Format de Disquette

#### Pour les débutants

1. **Sélectionnez le format** dans le menu déroulant "Format de Disquette"
2. Les formats sont organisés par type :
   - **IBM** : ibm.1440 (1.44 MB), ibm.1200 (1.2 MB), ibm.720 (720 KB), ibm.360 (360 KB)
   - **Amiga** : amiga.amigados
   - **Apple** : apple2.gcr
   - **Commodore** : c64.gcr
   - Et bien d'autres...

3. **Consultez les détails du format** affichés sous le sélecteur :
   - Nombre de pistes
   - Nombre de têtes
   - Secteurs par piste
   - Capacité

**💡 Astuce** : Le format sélectionné est partagé entre le mode automatique et le mode manuel. Vous pouvez le changer à tout moment.

#### Pour les experts

**Formats supportés** :
- Formats IBM (MFM/FM) : ibm.1440, ibm.1200, ibm.720, ibm.360, etc.
- Formats Amiga : amiga.amigados, amiga.adf, etc.
- Formats Apple : apple2.gcr, mac.gcr, etc.
- Formats Commodore : c64.gcr, etc.
- Formats HP : hp.mmfm
- Formats DEC : dec.rx02
- Et bien d'autres formats définis dans `diskdefs.cfg`

**Validation des limites** :
- Le système valide que les pistes testées sont dans les limites du format
- Affiche des avertissements pour les pistes hors limites
- Exclut automatiquement les pistes hors limites du calcul final

**Détection du formatage** :
- Analyse si la piste est formatée, partiellement formatée ou non formatée
- Calcule un score de confiance basé sur :
  - Ratio de secteurs détectés
  - Nombre de transitions de flux
  - Densité des données

---

## Mode Automatique

### Vue d'ensemble

Le mode automatique effectue un alignement automatisé en testant plusieurs pistes consécutivement. C'est le mode recommandé pour un alignement complet et standardisé.

### Démarrage d'un Alignement Automatique

#### Pour les débutants

1. **Sélectionnez le format de disquette** (voir section Configuration)
2. **Configurez les paramètres** :
   - **Nombre de cylindres** : Nombre de pistes à tester (par défaut : 80)
   - **Nombre de tentatives** : Nombre de lectures par piste (par défaut : 3)

3. **Cliquez sur "Démarrer l'alignement"**
4. **Surveillez la progression** :
   - Barre de progression
   - Nombre de valeurs collectées
   - Cylindre actuel

5. **Attendez la fin** ou cliquez sur "Annuler" pour arrêter

**💡 Astuce** : Utilisez la touche **Espace** pour démarrer/arrêter rapidement l'alignement.

#### Pour les experts

**Paramètres détaillés** :

**Nombre de cylindres (1-160)** :
- Correspond au nombre de pistes à tester
- Chaque piste a deux faces (head 0 et head 1)
- Limite de 160 valeurs utilisées pour le calcul final (80 pistes × 2 faces)
- Valeur recommandée : 80 (pour une disquette 1.44 MB standard)

**Nombre de tentatives (1-10)** :
- Nombre de lectures effectuées par piste
- Plus de tentatives = plus de précision mais plus de temps
- Valeur recommandée : 3 (bon compromis)

**Format de disquette** :
- Utilisé pour valider les limites de pistes
- Influence la détection du formatage
- Peut être changé pendant l'alignement (sera appliqué aux prochaines pistes)

**Commande exécutée** :
```bash
gw align --device <port> --drive <drive> --format <format> --cylinders <cylinders> --retries <retries>
```

### Suivi en Temps Réel

#### Pour les débutants

Pendant l'alignement, vous verrez :
- **Barre de progression** : Pourcentage de complétion
- **Valeurs collectées** : Nombre de pistes testées
- **Cylindre actuel** : Piste en cours de test

**💡 Astuce** : Les résultats sont mis à jour en temps réel via WebSocket. Vous pouvez voir les valeurs s'accumuler au fur et à mesure.

#### Pour les experts

**Communication WebSocket** :
- Messages `alignment_update` : Nouvelle valeur d'alignement détectée
- Messages `alignment_complete` : Alignement terminé avec statistiques finales
- Messages `alignment_cancelled` : Alignement annulé par l'utilisateur
- Messages `alignment_error` : Erreur lors de l'alignement

**Parsing en temps réel** :
- Extraction des valeurs `[XX.XXX%]` depuis la sortie de `gw align`
- Parsing des numéros de piste (format `XX.Y`)
- Calcul des statistiques intermédiaires
- Validation des limites de format

### Résultats de l'Alignement Automatique

#### Pour les débutants

Après la fin de l'alignement, vous verrez :

**Statistiques principales** :
- **Moyenne** : Pourcentage moyen d'alignement (objectif : ≥99%)
- **Minimum** : Valeur la plus basse détectée
- **Maximum** : Valeur la plus haute détectée
- **Qualité** : Classification (Perfect, Good, Average, Poor)

**Interprétation** :
- **Perfect (≥99%)** : Alignement excellent, le lecteur est parfaitement calibré
- **Good (97-98.9%)** : Bon alignement, acceptable pour la plupart des usages
- **Average (96-96.9%)** : Alignement moyen, peut nécessiter un réglage
- **Poor (<96%)** : Mauvais alignement, réglage nécessaire

**💡 Astuce** : Consultez le tableau détaillé pour voir les résultats par piste et identifier les pistes problématiques.

#### Pour les experts

**Statistiques calculées** :

**Valeurs de base** :
- `total_values` : Nombre total de valeurs trouvées
- `used_values` : Nombre de valeurs utilisées pour le calcul (limite : 160)
- `track_max` : Dernière piste lue (format `XX.Y`)
- `track_normal` : Nombre de pistes utilisées (généralement `used_values / 2`)

**Analyse avancée par piste** :
- **Pourcentage d'alignement** : Basé sur les secteurs détectés
- **Cohérence** : Écart-type entre les lectures (objectif : ≥90%)
- **Stabilité** : Variation des timings (objectif : ≥90%)
- **Positionnement** : Statut (correct/unstable/poor)
- **Azimut** : Score et statut (excellent/good/acceptable/poor)
- **Asymétrie** : Score et statut (excellent/good/acceptable/poor)

**Calcul multi-critères** :
- **Poids** : 40% secteurs, 30% qualité, 15% azimut, 15% asymétrie
- **Facteurs de confiance** : Ajustement basé sur la disponibilité des données
- **Pénalités** : Application de pénalités pour valeurs hors limites

**Graphiques** :
- **Évolution du pourcentage** : Graphique linéaire montrant l'évolution par piste
- **Répartition par qualité** : Graphique en barres montrant la distribution

### Annulation d'un Alignement

#### Pour les débutants

1. **Cliquez sur "Annuler"** pendant l'alignement
2. Les données collectées jusqu'à présent sont conservées
3. Vous pouvez consulter les résultats partiels

**💡 Astuce** : Vous pouvez également utiliser la touche **Espace** pour annuler rapidement.

#### Pour les experts

L'annulation :
- Envoie un signal d'interruption au processus `gw align`
- Conserve les données collectées jusqu'à l'annulation
- Met à jour le statut à `cancelled`
- Permet de consulter les statistiques partielles

---

## Mode Manuel

### Vue d'ensemble

Le mode manuel permet un alignement interactif avec navigation par pistes et analyse en temps réel. C'est le mode recommandé pour un réglage précis et ciblé.

### Démarrage du Mode Manuel

#### Pour les débutants

1. **Basculez vers l'onglet "Mode Manuel"**
2. **Sélectionnez le format de disquette** (si nécessaire)
3. **Choisissez le mode d'alignement** :
   - **Mode Direct** : Réglage rapide (~150-200ms par lecture)
   - **Ajustage Fin** : Ajustements précis (~500-700ms par lecture)
   - **Grande Précision** : Validation finale (~2-3s par piste)

4. **Cliquez sur "Démarrer le Mode Manuel"**
5. Le mode démarre et commence les lectures continues automatiquement

**💡 Astuce** : Utilisez la touche **Espace** pour démarrer/arrêter rapidement le mode manuel.

#### Pour les experts

**Modes d'alignement** :

**Mode Direct** :
- **Lectures** : 1
- **Délai** : 0ms
- **Timeout** : 5s
- **Latence estimée** : ~150-200ms
- **Utilisation** : Réglage rapide en temps réel des vis d'alignement
- **Optimisation** : Un seul message WebSocket par lecture (problème de saturation résolu)

**Ajustage Fin** :
- **Lectures** : 3
- **Délai** : 100ms entre lectures
- **Timeout** : 10s
- **Latence estimée** : ~500-700ms
- **Utilisation** : Ajustements précis avec moyenne de plusieurs lectures

**Grande Précision** :
- **Lectures** : 5
- **Délai** : 200ms entre lectures
- **Timeout** : 15s
- **Latence estimée** : ~2-3s par piste
- **Utilisation** : Validation finale avec analyse approfondie

**Commande exécutée** :
```bash
gw align --device <port> --drive <drive> --format <format> --track <track> --head <head> --reads <reads> --delay <delay>
```

### Navigation par Pistes

#### Pour les débutants

**Boutons de navigation** :
- **← -5** : Reculer de 5 pistes
- **← -1** : Reculer d'une piste
- **+1 →** : Avancer d'une piste
- **+5 →** : Avancer de 5 pistes

**Saut rapide** :
- **Boutons 10, 20, 30... 80** : Aller directement à la piste correspondante

**Contrôles spéciaux** :
- **Tête 0/1 (H)** : Changer de tête (face 0 ou face 1)
- **Recalibrer (R)** : Retourner à la piste 0

**💡 Astuce** : Utilisez les raccourcis clavier pour naviguer plus rapidement :
- **+/-** : Avancer/reculer d'une piste
- **1-8** : Aller à la piste 10, 20, 30... 80
- **H** : Changer de tête
- **R** : Recalibrer

#### Pour les experts

**Navigation sans mode démarré** :
- La navigation fonctionne même si le mode manuel n'est pas démarré
- Utilise la commande `gw seek` directement
- La position est sauvegardée dans localStorage
- Permet de positionner la tête avant de démarrer le mode

**Navigation avec mode démarré** :
- Utilise la commande `gw align` avec navigation incrémentale
- Maintient le flux continu de lectures
- Met à jour la position en temps réel
- Synchronise avec le backend via WebSocket

**Commandes utilisées** :
- `gw seek --device <port> --drive <drive> --track <track> --head <head>` : Navigation directe
- `gw align --device <port> --drive <drive> --format <format> --track <track> --head <head>` : Navigation avec alignement

### Analyse Manuelle

#### Pour les débutants

1. **Naviguez vers la piste à analyser** (voir section Navigation)
2. **Cliquez sur "Analyser avec le format sélectionné (A)"**
3. **Attendez la fin de l'analyse** (quelques secondes)
4. **Consultez les résultats** :
   - Pourcentage d'alignement
   - Nombre de secteurs détectés
   - Qualité (Perfect, Good, Average, Poor)
   - Détails du calcul (si disponibles)

**💡 Astuce** : L'analyse fonctionne même si le mode manuel n'est pas démarré. Elle analyse la piste actuelle (ou la piste 0.0 par défaut).

#### Pour les experts

**Fonctionnement de l'analyse** :
- Lit la piste actuelle plusieurs fois (selon le mode d'alignement)
- Utilise le format sélectionné pour valider les limites
- Calcule le pourcentage d'alignement basé sur les secteurs détectés
- Analyse le formatage de la piste
- Calcule la cohérence et la stabilité
- Calcule l'azimut et l'asymétrie (si disponibles)

**Commande exécutée** :
```bash
gw align --device <port> --drive <drive> --format <format> --track <track> --head <head> --reads <reads> --delay <delay>
```

**Résultats détaillés** :
- **Scores bruts** : Secteurs, qualité, azimut, asymétrie
- **Scores après pénalités** : Ajustés selon les limites
- **Poids utilisés** : Répartition des critères (40% secteurs, 30% qualité, 15% azimut, 15% asymétrie)
- **Facteurs de confiance** : Ajustement basé sur la disponibilité des données

### Lectures Continues

#### Pour les débutants

Quand le mode manuel est démarré, les lectures se font automatiquement en continu :
- **Mode Direct** : Une lecture toutes les ~150-200ms
- **Ajustage Fin** : Trois lectures toutes les ~500-700ms
- **Grande Précision** : Cinq lectures toutes les ~2-3s

**Affichage en temps réel** :
- **Dernière lecture** : Pourcentage, secteurs, qualité
- **Historique** : Dernières 5-10 lectures (selon le mode)
- **Timings** : Durée et latence (modes Ajustage Fin et Grande Précision uniquement)

**💡 Astuce** : Utilisez les lectures continues pour ajuster les vis d'alignement en temps réel. Surveillez le pourcentage qui s'affiche et ajustez jusqu'à obtenir ≥99%.

#### Pour les experts

**Flux de données WebSocket** :

**Mode Direct** :
- Message `direct_reading_complete` : Une seule notification par lecture
- Optimisé pour éviter la saturation (problème résolu)
- Latence minimale : ~150-200ms

**Modes Ajustage Fin et Grande Précision** :
- Messages `reading` : Notification pour chaque lecture en cours
- Messages `reading_complete` : Notification quand une série de lectures est terminée
- Historique complet avec timings détaillés

**Données collectées** :
- **Flux transitions** : Nombre de transitions magnétiques détectées
- **Temps/révolution** : Temps pour une révolution complète
- **Latence** : Temps entre deux lectures consécutives
- **Durée** : Temps total de la lecture

**Analyse des timings** :
- **Durée moyenne** : Temps moyen par lecture
- **Latence moyenne** : Temps moyen entre lectures
- **Variance** : Indicateur de stabilité mécanique

### Affichage des Résultats

#### Pour les débutants

**Position actuelle** :
- **Piste** : Numéro de piste actuelle
- **Tête** : Tête actuelle (0 ou 1)
- **Position** : Format `T<track>.<head>`

**Dernière analyse** :
- **Pourcentage** : Pourcentage d'alignement (objectif : ≥99%)
- **Qualité** : Classification (Perfect, Good, Average, Poor)
- **Secteurs** : Nombre de secteurs détectés / attendus

**Historique des lectures** (si mode démarré) :
- Liste des dernières lectures avec pourcentage et secteurs
- Timings (modes Ajustage Fin et Grande Précision uniquement)

**💡 Astuce** : Les résultats sont mis à jour en temps réel. Surveillez le pourcentage pour voir l'effet de vos ajustements.

#### Pour les experts

**Affichage Mode Direct** :
- **Dernière lecture** : Pourcentage, secteurs, indicateur visuel
- **Détails du calcul** : Scores bruts, scores après pénalités, poids, facteurs de confiance
- **Optimisation** : Affichage simplifié pour latence minimale

**Affichage Modes Ajustage Fin et Grande Précision** :
- **Dernière lecture** : Pourcentage, secteurs, timings détaillés
- **Historique** : Dernières 10 lectures avec latence
- **Statistiques** : Durée moyenne, latence moyenne, nombre de lectures
- **Détails du calcul** : Scores complets avec azimut et asymétrie

**Indicateurs visuels** :
- **Barres de progression** : Représentation visuelle du pourcentage
- **Symboles** : ✓ (excellent), ○ (bon), ⚠ (moyen), ✗ (mauvais)
- **Couleurs** : Vert (≥99%), Bleu (≥97%), Jaune (≥96%), Rouge (<96%)

### Arrêt du Mode Manuel

#### Pour les débutants

1. **Cliquez sur "Arrêter le Mode Manuel"**
2. Les lectures continues s'arrêtent
3. Les informations de la dernière analyse restent affichées

**💡 Astuce** : Vous pouvez redémarrer le mode manuel à tout moment. La position actuelle est conservée.

#### Pour les experts

L'arrêt :
- Envoie un signal d'arrêt au backend
- Arrête le flux continu de lectures
- Conserve les données collectées
- Met à jour le statut à `stopped`
- Permet de redémarrer sans perdre la position

---

## Fonctionnalités Avancées

### Réinitialisation des Données

#### Pour les débutants

1. **Cliquez sur "Reset Data"** en haut à droite
2. Les statistiques et graphiques sont réinitialisés
3. Le format sélectionné est conservé

**💡 Astuce** : Utilisez cette fonction pour effacer les résultats d'un alignement précédent avant d'en commencer un nouveau.

#### Pour les experts

**Reset Data** :
- Réinitialise les données d'alignement affichées
- Conserve le format sélectionné
- Conserve les paramètres (lecteur, chemin gw.exe)
- Envoie un message WebSocket `alignment_reset` pour synchroniser tous les clients

**Utilisation** : Utile pour nettoyer l'interface avant un nouvel alignement ou pour comparer plusieurs alignements.

### Hard Reset

#### Pour les débutants

1. **Cliquez sur "HARD RESET"** en haut à droite
2. **Confirmez** dans la boîte de dialogue
3. Le hardware Greaseweazle est réinitialisé

**⚠️ Attention** : Cette opération réinitialise complètement le hardware. Utilisez-la uniquement en cas de problème.

#### Pour les experts

**Hard Reset** :
- Envoie la commande `gw reset` au hardware
- Réinitialise complètement le device Greaseweazle
- Peut résoudre les problèmes de communication ou d'état
- Nécessite une confirmation pour éviter les erreurs

**Commande exécutée** :
```bash
gw reset --device <port>
```

**Utilisation** : En cas de :
- Erreurs de communication persistantes
- État incohérent du device
- Problèmes de détection

### Raccourcis Clavier

#### Pour les débutants

**Mode Automatique** :
- **Espace** : Démarrer/Arrêter l'alignement

**Mode Manuel** :
- **Espace** : Démarrer/Arrêter le mode manuel
- **+/-** : Avancer/Reculer d'une piste
- **1-8** : Aller à la piste 10, 20, 30... 80
- **H** : Changer de tête
- **R** : Recalibrer (retour à la piste 0)
- **A** : Analyser la piste actuelle

**💡 Astuce** : Les raccourcis fonctionnent uniquement quand le focus n'est pas dans un champ de saisie.

#### Pour les experts

**Gestion des événements** :
- Les raccourcis sont gérés via `addEventListener('keydown')`
- Ignore les touches si le focus est dans un input/select/textarea
- Utilise `preventDefault()` pour éviter les comportements par défaut
- Stocke les handlers dans des refs pour éviter les problèmes de dépendances

**Optimisation** :
- Un seul listener par composant
- Nettoyage automatique au démontage
- Gestion asynchrone pour les appels API

### Changement de Langue

#### Pour les débutants

1. **Cliquez sur le drapeau** en haut à droite (🇫🇷 ou 🇬🇧)
2. L'interface change immédiatement de langue
3. La préférence est sauvegardée dans le navigateur

**💡 Astuce** : La langue est détectée automatiquement selon les préférences de votre navigateur.

#### Pour les experts

**Système de traduction** :
- Utilise un hook React `useTranslation`
- Traductions stockées dans `translations.ts`
- Support FR/EN avec détection automatique
- Préférence sauvegardée dans localStorage

**Ajout de nouvelles traductions** :
1. Ajouter la clé dans `translations.ts` (sections `fr` et `en`)
2. Utiliser `t('key')` dans les composants
3. La traduction est automatiquement appliquée

---

## Dépannage

### Greaseweazle Non Détecté

**Symptômes** : Le bouton "Détecter Greaseweazle" ne trouve pas le device.

**Solutions** :
1. **Vérifiez la connexion USB** : Débranchez et rebranchez le câble
2. **Vérifiez les pilotes** : Installez les pilotes USB série si nécessaire
3. **Vérifiez le port** : Consultez la liste des ports détectés pour voir si le port apparaît
4. **Testez manuellement** : Exécutez `gw info` en ligne de commande pour vérifier la connexion
5. **Vérifiez les permissions** : Sur Linux/macOS, assurez-vous d'avoir les permissions pour accéder aux ports série

### Erreur "Commande align non disponible"

**Symptômes** : Le message "La commande 'align' n'est pas disponible" s'affiche.

**Solutions** :
1. **Vérifiez la version de Greaseweazle** : La commande `align` nécessite v1.23b (PR #592)
2. **Vérifiez la plateforme** : v1.23b est actuellement disponible uniquement sur Windows
3. **Vérifiez le chemin gw.exe** : Assurez-vous que le chemin vers `gw.exe` est correct
4. **Testez en ligne de commande** : Exécutez `gw align --help` pour vérifier que la commande est disponible

### Erreurs de Lecture

**Symptômes** : Les lectures échouent ou retournent des valeurs anormales.

**Solutions** :
1. **Vérifiez la disquette** : Assurez-vous que la disquette est correctement insérée
2. **Vérifiez le format** : Sélectionnez le format correspondant à votre disquette
3. **Vérifiez le lecteur** : Testez le lecteur avec "Tester le Lecteur"
4. **Vérifiez Track 0** : Utilisez "Vérifier Track 0" pour diagnostiquer les problèmes de capteur
5. **Vérifiez les connexions** : Assurez-vous que tous les câbles sont bien connectés

### Performances Lentes

**Symptômes** : L'interface est lente ou les lectures prennent trop de temps.

**Solutions** :
1. **Utilisez le Mode Direct** : Pour des lectures plus rapides (~150-200ms)
2. **Réduisez le nombre de tentatives** : En mode automatique, réduisez le nombre de tentatives
3. **Fermez les autres applications** : Libérez des ressources système
4. **Vérifiez la connexion USB** : Utilisez un port USB 2.0 ou supérieur
5. **Vérifiez le navigateur** : Utilisez un navigateur moderne et à jour

### Problèmes de Navigation

**Symptômes** : La navigation par pistes ne fonctionne pas correctement.

**Solutions** :
1. **Vérifiez que Greaseweazle est connecté** : L'indicateur doit être vert
2. **Vérifiez le lecteur sélectionné** : Assurez-vous que le bon lecteur est sélectionné
3. **Recalibrez** : Utilisez "Recalibrer (R)" pour retourner à la piste 0
4. **Vérifiez les limites** : Assurez-vous que la piste demandée est dans les limites du format

### Problèmes d'Affichage

**Symptômes** : Les résultats ne s'affichent pas ou sont incorrects.

**Solutions** :
1. **Rafraîchissez la page** : Appuyez sur F5 pour recharger l'interface
2. **Vérifiez la connexion WebSocket** : Ouvrez la console du navigateur (F12) pour voir les erreurs
3. **Réinitialisez les données** : Utilisez "Reset Data" pour nettoyer l'affichage
4. **Vérifiez le navigateur** : Utilisez un navigateur moderne (Chrome, Firefox, Edge, Safari)

---

## Annexes

### A. Formats de Disquette Supportés

**Formats IBM** :
- ibm.1440 : 1.44 MB (80 pistes, 2 têtes, 18 secteurs/piste)
- ibm.1200 : 1.2 MB (80 pistes, 2 têtes, 15 secteurs/piste)
- ibm.720 : 720 KB (80 pistes, 2 têtes, 9 secteurs/piste)
- ibm.360 : 360 KB (40 pistes, 2 têtes, 9 secteurs/piste)

**Formats Amiga** :
- amiga.amigados : AmigaDOS standard
- amiga.adf : Amiga Disk File

**Formats Apple** :
- apple2.gcr : Apple II GCR
- mac.gcr : Macintosh GCR

**Formats Commodore** :
- c64.gcr : Commodore 64 GCR

**Autres formats** :
- hp.mmfm : HP MMFM
- dec.rx02 : DEC RX02
- Et bien d'autres définis dans `diskdefs.cfg`

### B. Interprétation des Statistiques

**Pourcentage d'alignement** :
- **≥99%** : Excellent, alignement parfait
- **97-98.9%** : Bon, acceptable pour la plupart des usages
- **96-96.9%** : Moyen, peut nécessiter un réglage
- **<96%** : Mauvais, réglage nécessaire

**Cohérence** :
- **≥90%** : Excellente cohérence entre les lectures
- **70-89%** : Bonne cohérence
- **<70%** : Faible cohérence, peut indiquer un problème mécanique

**Stabilité** :
- **≥90%** : Excellente stabilité des timings
- **70-89%** : Bonne stabilité
- **<70%** : Faible stabilité, peut indiquer un problème mécanique

**Azimut** :
- **Excellent (≥95%)** : Azimut parfaitement aligné
- **Good (85-94%)** : Bon azimut
- **Acceptable (75-84%)** : Azimut acceptable
- **Poor (<75%)** : Azimut nécessitant un réglage

**Asymétrie** :
- **Excellent (≥95%)** : Signal parfaitement symétrique
- **Good (85-94%)** : Bonne symétrie
- **Acceptable (75-84%)** : Symétrie acceptable
- **Poor (<75%)** : Asymétrie nécessitant un réglage

### C. Références Techniques

**Greaseweazle** :
- Documentation officielle : https://github.com/keirf/greaseweazle
- PR #592 (commande align) : https://github.com/keirf/greaseweazle/pull/592

**Manuel Panasonic** :
- Section 9.7 : Analyse d'azimut
- Section 9.9 : Vérification Track 0
- Section 9.10 : Analyse d'asymétrie

**AlignTester** :
- Dépôt GitHub : https://github.com/Jean-Fred64/AlignTester
- Documentation technique : Voir `docs/` dans le projet

### D. Glossaire

**Alignement** : Positionnement correct de la tête de lecture/écriture par rapport aux pistes de la disquette.

**Azimut** : Angle d'inclinaison de la tête par rapport à la piste. Un mauvais azimut peut causer des erreurs de lecture.

**Asymétrie** : Déséquilibre du signal magnétique. Une asymétrie élevée peut indiquer un problème mécanique.

**Cohérence** : Mesure de la similarité entre plusieurs lectures de la même piste. Une faible cohérence peut indiquer un problème mécanique.

**Cylindre** : Ensemble de pistes à la même position radiale sur toutes les faces. Pour une disquette double face, un cylindre = 2 pistes.

**Flux transitions** : Nombre de transitions magnétiques détectées lors de la lecture. Indique la densité de données sur la piste.

**Format** : Structure de données d'une disquette (nombre de pistes, secteurs, etc.). Chaque type de disquette a son propre format.

**Piste** : Cercle concentrique sur la disquette où les données sont stockées. Une disquette standard a 80 pistes par face.

**Secteur** : Division d'une piste. Une piste standard a 18 secteurs (pour une disquette 1.44 MB).

**Stabilité** : Mesure de la variation des timings entre les lectures. Une faible stabilité peut indiquer un problème mécanique.

**Track 0** : Piste la plus externe de la disquette. Utilisée comme référence pour le positionnement.

---

**Fin du Guide d'Utilisation**
