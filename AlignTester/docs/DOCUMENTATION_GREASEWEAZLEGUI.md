# Documentation Technique - Interfaces Graphiques pour Greaseweazle

## Vue d'ensemble

Ce document présente les principales interfaces graphiques (GUI) disponibles pour Greaseweazle, permettant d'utiliser les fonctionnalités de Greaseweazle sans passer par la ligne de commande.

**Deux GUI principales sont disponibles** :
1. **GreaseweazleGUI-dotNET** - Interface C#/.NET (Don Mankin)
2. **FluxMyFluffyFloppy** - Interface Pascal/Delphi (FrankieTheFluff)

Ces interfaces servent de **référence d'implémentation** pour votre projet d'interface web.

---

# Partie 1 : GreaseweazleGUI-dotNET

## Vue d'ensemble

**GreaseweazleGUI-dotNET** est une interface graphique (GUI) développée en C# et .NET pour faciliter l'utilisation de Greaseweazle. Cette application offre une interface utilisateur conviviale pour accéder aux fonctionnalités de Greaseweazle sans avoir à utiliser la ligne de commande.

**Dépôt GitHub** : https://github.com/Foosie/GreaseweazleGUI-dotNET  
**Auteur** : Don Mankin  
**Site web** : https://desertsagesolutions.com/greaseweazlegui/  
**Licence** : MIT

## Caractéristiques principales

### Avantages de l'interface graphique

- ✅ **Interface intuitive** : Pas besoin de connaître la syntaxe des commandes
- ✅ **Sélection visuelle** : Menus et boutons pour toutes les opérations
- ✅ **Gestion des fichiers** : Sélection de fichiers via des dialogues standards
- ✅ **Affichage en temps réel** : Visualisation des opérations en cours
- ✅ **Gestion d'erreurs** : Messages d'erreur clairs et compréhensibles

### Technologies utilisées

- **Langage** : C#
- **Framework** : .NET Framework
- **IDE** : Visual Studio 2015 Community (ou plus récent)
- **Plateforme** : Windows uniquement

## Installation

### Prérequis

1. **Greaseweazle Host Tools** : L'application nécessite que les outils hôtes de Greaseweazle soient installés
   - Télécharger depuis : https://github.com/keirf/greaseweazle/releases
   - Décompresser dans un dossier (doit contenir `gw.exe` ou `gw.py`)

2. **.NET Framework** : Version compatible avec Visual Studio 2015 ou plus récent
   - Généralement .NET Framework 4.5 ou supérieur

3. **Carte Greaseweazle** : Matériel connecté et reconnu par Windows

### Installation de l'application

#### Méthode 1 : Téléchargement de l'exécutable (recommandé)

1. Télécharger depuis : https://desertsagesolutions.com/greaseweazlegui/
2. Décompresser l'archive
3. **Important** : Placer le contenu dans le **même dossier** que les Greaseweazle Host Tools
   - Le dossier doit contenir `gw.exe` (ou `gw.py`)
   - Le dossier doit contenir les fichiers `diskdef*.cfg`

#### Méthode 2 : Compilation depuis les sources

```bash
# Cloner le dépôt
git clone https://github.com/Foosie/GreaseweazleGUI-dotNET.git
cd GreaseweazleGUI-dotNET

# Ouvrir dans Visual Studio
# Ouvrir : VS 2015 Solution/GreaseweazleGUI.sln

# Compiler le projet
# Build > Build Solution (ou F6)
```

**Structure du projet** :
```
GreaseweazleGUI-dotNET/
├── VS 2015 Solution/     # Solution Visual Studio
│   └── GreaseweazleGUI.sln
├── README.md
└── LICENSE
```

### Configuration initiale

1. **Placer dans le bon dossier** :
   - L'application doit être dans le même dossier que `gw.exe`
   - Ce dossier doit contenir les fichiers de configuration `diskdef*.cfg`

2. **Mettre à jour les fichiers diskdef** :
   - Les fichiers `diskdef*.cfg` peuvent être obsolètes
   - Télécharger les versions à jour depuis :
     https://github.com/keirf/greaseweazle/tree/master/src/greaseweazle/data
   - Remplacer les anciens fichiers dans le dossier

3. **Vérifier la compatibilité** :
   - S'assurer que la version des Host Tools correspond au firmware de la carte
   - Si versions incompatibles, il y aura des erreurs lors de l'exécution

## Architecture de l'application

### Structure générale

L'application fonctionne comme un **wrapper GUI** autour de `gw.exe` :

```
┌─────────────────────┐
│  GreaseweazleGUI    │
│   (Interface .NET)  │
└──────────┬──────────┘
           │ Appels subprocess
           ▼
┌─────────────────────┐
│     gw.exe          │
│  (Greaseweazle CLI) │
└──────────┬──────────┘
           │ USB Serial
           ▼
┌─────────────────────┐
│  Carte Greaseweazle │
└─────────────────────┘
```

### Communication avec Greaseweazle

L'application communique avec Greaseweazle via :
- **Subprocess** : Exécution de `gw.exe` en arrière-plan
- **Parsing de sortie** : Analyse de la sortie texte de `gw.exe`
- **Gestion d'erreurs** : Capture et affichage des erreurs

## Fonctionnalités principales

### 1. Lecture de disquette (Read)

**Description** : Lit une disquette et crée un fichier image.

**Fonctionnalités** :
- Sélection du format de disquette
- Choix des pistes à lire
- Sélection de la tête (0 ou 1)
- Options de flux brut
- Nombre de révolutions

### 2. Écriture sur disquette (Write)

**Description** : Écrit une image de disquette sur une disquette physique.

**Fonctionnalités** :
- Sélection du fichier image
- Format de disquette
- Options de vérification
- Options d'effacement préalable

### 3. Effacement de disquette (Erase)

**Description** : Efface le contenu d'une disquette.

**Fonctionnalités** :
- Effacement complet
- Effacement de pistes spécifiques
- Sélection de la tête

### 4. Informations sur la carte (Info)

**Description** : Affiche les informations sur la carte Greaseweazle connectée.

**Informations affichées** :
- Modèle de la carte
- Version du firmware
- Numéro de série
- Statut de connexion

### 5. Positionnement de la tête (Seek)

**Description** : Positionne la tête de lecture/écriture sur une piste spécifique.

**Fonctionnalités** :
- Sélection du cylindre
- Sélection de la tête
- Vérification de position

### 6. Tests de diagnostic

**Description** : Effectue des tests sur la carte et le lecteur.

**Tests disponibles** :
- Test de vitesse de rotation (RPM)
- Test de pistes
- Test général de fonctionnement

### 7. Gestion des formats

**Description** : Gestion des fichiers de définition de formats (`diskdef*.cfg`).

**Fonctionnalités** :
- Chargement des formats disponibles
- Mise à jour des fichiers de définition
- Sélection du format approprié

## Commandes supportées

### Commandes de base

| Commande | Description | Interface GUI |
|----------|-------------|---------------|
| `info` | Informations sur la carte | Bouton "Info" |
| `read` | Lecture de disquette | Bouton "Read" |
| `write` | Écriture sur disquette | Bouton "Write" |
| `erase` | Effacement | Bouton "Erase" |
| `seek` | Positionnement | Option dans menu |
| `rpm` | Mesure RPM | Option de test |
| `test` | Tests de diagnostic | Menu Tests |

## Limitations et considérations

### Limitations connues

1. **Plateforme** : Windows uniquement (nécessite .NET Framework)
2. **Dépendance aux Host Tools** : Doit être dans le même dossier que `gw.exe`
3. **Version des Host Tools** : Doit correspondre au firmware de la carte
4. **Fichiers diskdef** : Peuvent être obsolètes, nécessitent mise à jour manuelle

### Points d'attention

1. **Compatibilité des versions** :
   - Les Host Tools et le firmware doivent être compatibles
   - Vérifier avant chaque utilisation importante

2. **Gestion des erreurs** :
   - L'application peut ne pas prévenir toutes les combinaisons invalides
   - Les formats changent fréquemment dans Greaseweazle
   - Toujours vérifier les messages d'erreur

3. **Performance** :
   - L'interface graphique ajoute une couche d'abstraction
   - Les opérations peuvent être légèrement plus lentes qu'en ligne de commande
   - Acceptable pour un usage normal

## Utilisation pour l'alignement

### Support de l'alignement dans GreaseweazleGUI-dotNET

**État actuel** :
- L'application utilise `gw.exe` en arrière-plan
- Si `gw.exe` supporte `align`, l'application peut l'utiliser
- Nécessite que la commande soit disponible dans les Host Tools

**Pour utiliser la commande `align` (PR #592)** :

1. **Compiler gw.exe avec le PR #592** :
   ```bash
   # Suivre les instructions de compilation
   # Créer gw.exe avec la commande align
   ```

2. **Remplacer gw.exe** :
   - Remplacer `gw.exe` dans le dossier de l'application
   - Par votre version compilée avec `align`

3. **Utilisation dans l'interface** :
   - L'interface peut ne pas avoir de bouton dédié pour `align`
   - Peut nécessiter l'ajout d'une fonctionnalité dans le code source
   - Ou utiliser via une option "Commande personnalisée" si disponible

## Structure du code source

### Organisation typique (inférée)

```
GreaseweazleGUI/
├── Forms/              # Formulaires Windows Forms
│   ├── MainForm.cs     # Formulaire principal
│   ├── ReadForm.cs     # Formulaire de lecture
│   └── WriteForm.cs    # Formulaire d'écriture
├── Classes/            # Classes utilitaires
│   ├── GwCommand.cs    # Gestion des commandes gw.exe
│   ├── FormatManager.cs # Gestion des formats
│   └── OutputParser.cs # Parsing de la sortie
├── Resources/          # Ressources (icônes, etc.)
└── Properties/         # Propriétés du projet
```

### Points clés du code

1. **Exécution de gw.exe** :
```csharp
ProcessStartInfo startInfo = new ProcessStartInfo
{
    FileName = "gw.exe",
    Arguments = commandLine,
    UseShellExecute = false,
    RedirectStandardOutput = true,
    RedirectStandardError = true
};

Process process = Process.Start(startInfo);
string output = process.StandardOutput.ReadToEnd();
```

2. **Gestion des formats** :
```csharp
// Chargement des fichiers diskdef*.cfg
string[] cfgFiles = Directory.GetFiles(".", "diskdef*.cfg");
foreach (string file in cfgFiles)
{
    // Parser et charger les formats
}
```

## Dépannage

### Problèmes courants

#### 1. Erreur "gw.exe not found"

**Solution** :
- Vérifier que `gw.exe` est dans le même dossier que l'application
- Vérifier le chemin dans les paramètres de l'application

#### 2. Erreur de format inconnu

**Solution** :
- Mettre à jour les fichiers `diskdef*.cfg`
- Télécharger depuis : https://github.com/keirf/greaseweazle/tree/master/src/greaseweazle/data

#### 3. Incompatibilité firmware/Host Tools

**Solution** :
- Vérifier la version du firmware : `gw.exe info`
- Télécharger la version correspondante des Host Tools
- Mettre à jour le firmware si nécessaire : `gw.exe update`

#### 4. Carte non détectée

**Solution** :
- Vérifier la connexion USB
- Vérifier les pilotes Windows
- Essayer un autre port USB
- Vérifier avec `gw.exe info` en ligne de commande

## Ressources

- **Dépôt GitHub** : https://github.com/Foosie/GreaseweazleGUI-dotNET
- **Site officiel** : https://desertsagesolutions.com/greaseweazlegui/

---

# Partie 2 : FluxMyFluffyFloppy

## Vue d'ensemble

**FluxMyFluffyFloppy** (FMFF) est une interface graphique moderne et active pour les outils hôtes de Greaseweazle, développée en Pascal/Delphi pour Microsoft Windows. Cette application offre une interface utilisateur complète et régulièrement mise à jour pour faciliter l'utilisation de Greaseweazle.

**Dépôt GitHub** : https://github.com/FrankieTheFluff/FluxMyFluffyFloppy  
**Auteur** : FrankieTheFluff  
**Version actuelle** : 5.2.6 (2025-12-05)  
**Licence** : GPL-2.0  
**Email** : fluxmyfluffyfloppy@mail.de

## Caractéristiques principales

### Avantages de l'interface graphique

- ✅ **Interface moderne** : Interface utilisateur soignée et intuitive
- ✅ **Activement maintenue** : Dernière version récente (décembre 2025)
- ✅ **Terminal intégré** : Contient du code de UnTerminal pour l'affichage des sorties
- ✅ **Gestion complète** : Support de toutes les opérations Greaseweazle
- ✅ **Multi-formats** : Support de nombreux formats de disquettes

### Technologies utilisées

- **Langage** : Pascal (Delphi/Lazarus)
- **Framework** : VCL (Visual Component Library) ou LCL (Lazarus Component Library)
- **Plateforme** : Windows uniquement
- **Dépendances** : Greaseweazle Host Tools

## Installation

### Prérequis

1. **Greaseweazle Host Tools** : L'application nécessite que les outils hôtes de Greaseweazle soient installés
   - Télécharger depuis : https://github.com/keirf/greaseweazle/releases
   - Décompresser dans un dossier (doit contenir `gw.exe`)

2. **Windows** : Microsoft Windows (version récente recommandée)

3. **Carte Greaseweazle** : Matériel connecté et reconnu par Windows

### Installation de l'application

#### Méthode 1 : Téléchargement de l'exécutable (recommandé)

1. Télécharger depuis : https://github.com/FrankieTheFluff/FluxMyFluffyFloppy/releases
2. Décompresser l'archive
3. **Important** : Placer l'exécutable dans le **même dossier** que les Greaseweazle Host Tools
   - Le dossier doit contenir `gw.exe`
   - Le dossier doit contenir les fichiers `diskdef*.cfg` (optionnel mais recommandé)

#### Méthode 2 : Compilation depuis les sources

```bash
# Cloner le dépôt
git clone https://github.com/FrankieTheFluff/FluxMyFluffyFloppy.git
cd FluxMyFluffyFloppy

# Ouvrir dans Delphi ou Lazarus
# Compiler le projet depuis l'IDE
```

**Structure du projet** :
```
FluxMyFluffyFloppy/
├── source/              # Code source Pascal
│   ├── *.pas            # Fichiers source
│   └── *.dfm            # Formulaires (Delphi)
├── ! Release notes !.txt # Notes de version
├── README.md
└── LICENSE.TXT
```

### Configuration initiale

1. **Placer dans le bon dossier** :
   - L'application doit être dans le même dossier que `gw.exe`
   - Ce dossier peut contenir les fichiers `diskdef*.cfg` (optionnel)

2. **Mettre à jour les fichiers diskdef** :
   - Les fichiers `diskdef*.cfg` peuvent être mis à jour depuis :
     https://github.com/keirf/greaseweazle/tree/master/src/greaseweazle/data
   - Placer dans le même dossier que `gw.exe`

3. **Vérifier la compatibilité** :
   - S'assurer que la version des Host Tools correspond au firmware de la carte
   - Vérifier avec `gw.exe info`

## Architecture de l'application

### Structure générale

L'application fonctionne comme un **wrapper GUI** autour de `gw.exe` avec un terminal intégré :

```
┌──────────────────────────┐
│  FluxMyFluffyFloppy      │
│  (Interface Pascal)      │
│  + Terminal intégré     │
└──────────┬───────────────┘
           │ Appels subprocess
           ▼
┌──────────────────────────┐
│     gw.exe               │
│  (Greaseweazle CLI)      │
└──────────┬───────────────┘
           │ USB Serial
           ▼
┌──────────────────────────┐
│  Carte Greaseweazle      │
└──────────────────────────┘
```

### Communication avec Greaseweazle

L'application communique avec Greaseweazle via :
- **Subprocess** : Exécution de `gw.exe` en arrière-plan
- **Terminal intégré** : Affichage en temps réel de la sortie (basé sur UnTerminal)
- **Parsing de sortie** : Analyse de la sortie texte de `gw.exe`
- **Gestion d'erreurs** : Capture et affichage des erreurs

### Terminal intégré

**Basé sur UnTerminal 1.0** par Tito Hinostroza :
- Affichage en temps réel des commandes
- Coloration syntaxique possible
- Scroll automatique
- Capture de la sortie standard et erreur

## Fonctionnalités principales

### 1. Lecture de disquette (Read)

**Description** : Lit une disquette et crée un fichier image.

**Fonctionnalités** :
- Sélection du format de disquette
- Choix des pistes à lire
- Sélection de la tête (0 ou 1)
- Options de flux brut
- Nombre de révolutions
- Affichage en temps réel dans le terminal

### 2. Écriture sur disquette (Write)

**Description** : Écrit une image de disquette sur une disquette physique.

**Fonctionnalités** :
- Sélection du fichier image
- Format de disquette
- Options de vérification
- Options d'effacement préalable
- Progression visible dans le terminal

### 3. Effacement de disquette (Erase)

**Description** : Efface le contenu d'une disquette.

**Fonctionnalités** :
- Effacement complet
- Effacement de pistes spécifiques
- Sélection de la tête
- Confirmation avant effacement

### 4. Informations sur la carte (Info)

**Description** : Affiche les informations sur la carte Greaseweazle connectée.

**Informations affichées** :
- Modèle de la carte
- Version du firmware
- Numéro de série
- Statut de connexion

### 5. Positionnement de la tête (Seek)

**Description** : Positionne la tête de lecture/écriture sur une piste spécifique.

**Fonctionnalités** :
- Sélection du cylindre
- Sélection de la tête
- Vérification de position
- Feedback visuel

### 6. Tests de diagnostic

**Description** : Effectue des tests sur la carte et le lecteur.

**Tests disponibles** :
- Test de vitesse de rotation (RPM)
- Test de pistes
- Test général de fonctionnement
- Affichage des résultats dans le terminal

### 7. Gestion des formats

**Description** : Gestion des fichiers de définition de formats (`diskdef*.cfg`).

**Fonctionnalités** :
- Chargement automatique des formats disponibles
- Détection des formats depuis les fichiers `diskdef*.cfg`
- Sélection du format approprié
- Support de formats personnalisés

### 8. Terminal intégré

**Description** : Affichage en temps réel des commandes et résultats.

**Fonctionnalités** :
- Affichage des commandes exécutées
- Sortie en temps réel de `gw.exe`
- Messages d'erreur visibles
- Historique des commandes
- Scroll automatique

## Commandes supportées

### Commandes de base

| Commande | Description | Interface GUI |
|----------|-------------|---------------|
| `info` | Informations sur la carte | Bouton/Menu "Info" |
| `read` | Lecture de disquette | Bouton/Menu "Read" |
| `write` | Écriture sur disquette | Bouton/Menu "Write" |
| `erase` | Effacement | Bouton/Menu "Erase" |
| `seek` | Positionnement | Option dans menu |
| `rpm` | Mesure RPM | Option de test |
| `test` | Tests de diagnostic | Menu Tests |
| `update` | Mise à jour firmware | Option dans menu |

### Options disponibles

Les options de chaque commande sont accessibles via :
- **Cases à cocher** : Pour les options booléennes
- **Champs de texte** : Pour les valeurs numériques
- **Listes déroulantes** : Pour les sélections (format, tête, etc.)
- **Boutons de parcours** : Pour la sélection de fichiers
- **Terminal** : Affichage de toutes les sorties

## Gestion des fichiers

### Formats d'image supportés

L'application supporte tous les formats supportés par Greaseweazle :
- **Images brutes** : `.img`, `.raw`
- **Flux bruts** : `.flux`
- **Formats spécifiques** : Selon les `diskdef*.cfg` disponibles

### Fichiers de configuration

**diskdef*.cfg** :
- Définitions de formats de disquettes
- Optionnels mais recommandés
- Peuvent être dans le même dossier que `gw.exe`
- Peuvent être mis à jour depuis le dépôt GitHub

**Mise à jour recommandée** :
1. Télécharger depuis : https://github.com/keirf/greaseweazle/tree/master/src/greaseweazle/data
2. Placer dans le dossier de l'application
3. Redémarrer l'application

## Limitations et considérations

### Limitations connues

1. **Plateforme** : Windows uniquement
2. **Dépendance aux Host Tools** : Doit être dans le même dossier que `gw.exe`
3. **Version des Host Tools** : Doit correspondre au firmware de la carte
4. **Fichiers diskdef** : Optionnels mais recommandés pour meilleure expérience

### Points d'attention

1. **Compatibilité des versions** :
   - Les Host Tools et le firmware doivent être compatibles
   - Vérifier avant chaque utilisation importante

2. **Gestion des erreurs** :
   - Les erreurs sont affichées dans le terminal intégré
   - Toujours vérifier les messages d'erreur dans le terminal

3. **Performance** :
   - L'interface graphique ajoute une couche d'abstraction
   - Les opérations peuvent être légèrement plus lentes qu'en ligne de commande
   - Acceptable pour un usage normal

## Utilisation pour l'alignement

### Support de l'alignement dans FluxMyFluffyFloppy

**État actuel** :
- L'application utilise `gw.exe` en arrière-plan
- Si `gw.exe` supporte `align`, l'application peut l'utiliser
- Nécessite que la commande soit disponible dans les Host Tools
- Le terminal intégré permet de voir la sortie en temps réel

**Pour utiliser la commande `align` (PR #592)** :

1. **Compiler gw.exe avec le PR #592** :
   ```bash
   # Suivre les instructions de compilation
   # Créer gw.exe avec la commande align
   ```

2. **Remplacer gw.exe** :
   - Remplacer `gw.exe` dans le dossier de l'application
   - Par votre version compilée avec `align`

3. **Utilisation dans l'interface** :
   - L'interface peut avoir une option pour exécuter des commandes personnalisées
   - Le terminal intégré affichera la sortie en temps réel
   - Permet de voir les résultats de chaque lecture d'alignement

**Avantage du terminal intégré** :
- Affichage en temps réel des résultats de `gw align`
- Permet de voir chaque lecture et ses statistiques
- Facilite l'analyse des résultats d'alignement

## Structure du code source

### Organisation typique (inférée)

```
FluxMyFluffyFloppy/
├── source/
│   ├── MainForm.pas     # Formulaire principal
│   ├── ReadForm.pas      # Formulaire de lecture
│   ├── WriteForm.pas     # Formulaire d'écriture
│   ├── Terminal.pas      # Terminal intégré (UnTerminal)
│   ├── GwCommand.pas     # Gestion des commandes gw.exe
│   ├── FormatManager.pas # Gestion des formats
│   └── OutputParser.pas  # Parsing de la sortie
├── Resources/            # Ressources (icônes, etc.)
└── Config/               # Fichiers de configuration
```

### Points clés du code

1. **Exécution de gw.exe** :
```pascal
// Exemple typique en Pascal
procedure ExecuteGwCommand(const Command: string);
var
  Process: TProcess;
begin
  Process := TProcess.Create(nil);
  try
    Process.Executable := 'gw.exe';
    Process.Parameters.Add(Command);
    Process.Options := [poUsePipes, poNoConsole];
    Process.Execute;
    // Lire la sortie...
  finally
    Process.Free;
  end;
end;
```

2. **Terminal intégré** :
```pascal
// Utilisation du terminal UnTerminal
// Affichage en temps réel de la sortie
Terminal.AppendText(Output);
Terminal.ScrollToEnd;
```

## Dépannage

### Problèmes courants

#### 1. Erreur "gw.exe not found"

**Solution** :
- Vérifier que `gw.exe` est dans le même dossier que l'application
- Vérifier le chemin dans les paramètres de l'application

#### 2. Erreur de format inconnu

**Solution** :
- Mettre à jour les fichiers `diskdef*.cfg`
- Télécharger depuis : https://github.com/keirf/greaseweazle/tree/master/src/greaseweazle/data
- Vérifier les messages dans le terminal intégré

#### 3. Incompatibilité firmware/Host Tools

**Solution** :
- Vérifier la version du firmware : `gw.exe info`
- Télécharger la version correspondante des Host Tools
- Mettre à jour le firmware si nécessaire : `gw.exe update`

#### 4. Carte non détectée

**Solution** :
- Vérifier la connexion USB
- Vérifier les pilotes Windows
- Essayer un autre port USB
- Vérifier avec `gw.exe info` en ligne de commande
- Consulter le terminal intégré pour les messages d'erreur

#### 5. Terminal ne s'affiche pas correctement

**Solution** :
- Vérifier que le terminal est activé dans les options
- Redémarrer l'application
- Vérifier les paramètres d'affichage

## Ressources

- **Dépôt GitHub** : https://github.com/FrankieTheFluff/FluxMyFluffyFloppy
- **Releases** : https://github.com/FrankieTheFluff/FluxMyFluffyFloppy/releases
- **UnTerminal** : https://github.com/t-edson/UnTerminal (code intégré)

---

# Partie 3 : Comparaison des GUI

## Tableau comparatif

| Aspect | GreaseweazleGUI-dotNET | FluxMyFluffyFloppy |
|--------|------------------------|-------------------|
| **Auteur** | Don Mankin | FrankieTheFluff |
| **Langage** | C# | Pascal (Delphi/Lazarus) |
| **Framework** | .NET Framework | VCL/LCL |
| **Licence** | MIT | GPL-2.0 |
| **Version actuelle** | ? | 5.2.6 (2025-12-05) |
| **Dernière mise à jour** | ? | Décembre 2025 |
| **Terminal intégré** | ❌ Non | ✅ Oui (UnTerminal) |
| **Activement maintenu** | ? | ✅ Oui |
| **Complexité** | Moyenne | Moyenne à élevée |
| **Documentation** | Basique | Basique |

## Points communs

1. **Architecture similaire** :
   - Toutes deux fonctionnent comme wrapper autour de `gw.exe`
   - Utilisation de subprocess pour exécuter les commandes
   - Parsing de la sortie texte

2. **Fonctionnalités de base** :
   - Read, Write, Erase
   - Info, Seek
   - Tests de diagnostic
   - Gestion des formats

3. **Limitations** :
   - Windows uniquement
   - Dépendance aux Host Tools
   - Nécessitent `gw.exe` dans le même dossier

## Différences principales

### GreaseweazleGUI-dotNET

**Avantages** :
- ✅ Licence MIT (plus permissive)
- ✅ Technologie .NET moderne
- ✅ Code source accessible

**Inconvénients** :
- ❌ Pas de terminal intégré
- ❌ Statut de maintenance incertain

### FluxMyFluffyFloppy

**Avantages** :
- ✅ Terminal intégré (affichage temps réel)
- ✅ Activement maintenu (dernière version récente)
- ✅ Version récente (5.2.6)
- ✅ Code UnTerminal intégré

**Inconvénients** :
- ❌ Licence GPL-2.0 (contraintes de redistribution)
- ❌ Pascal moins courant que C#

## Recommandation d'utilisation

### Pour l'alignement

**FluxMyFluffyFloppy** est recommandé car :
- Terminal intégré permet de voir les résultats en temps réel
- Activement maintenu
- Version récente avec support des dernières fonctionnalités

### Pour le développement

**Les deux** peuvent servir de référence :
- **GreaseweazleGUI-dotNET** : Pour comprendre l'architecture .NET
- **FluxMyFluffyFloppy** : Pour voir l'intégration d'un terminal

---

# Partie 4 : Intégration avec votre projet

## Utilisation comme référence

Les deux GUI peuvent servir de **référence d'implémentation** pour votre interface web :

### Points d'apprentissage communs

1. **Structure des commandes** :
   - Comment organiser les commandes Greaseweazle
   - Quelles options exposer à l'utilisateur
   - Comment gérer les paramètres

2. **Gestion des formats** :
   - Comment charger et utiliser les `diskdef*.cfg`
   - Comment présenter les formats disponibles
   - Comment valider les sélections

3. **Interface utilisateur** :
   - Organisation des contrôles
   - Workflow utilisateur
   - Gestion des erreurs

4. **Communication avec gw.exe** :
   - Exécution de subprocess
   - Parsing de la sortie
   - Gestion des erreurs

### Points spécifiques à FluxMyFluffyFloppy

1. **Terminal intégré** :
   - Comment afficher la sortie en temps réel
   - Utilisation de WebSocket pour votre interface web
   - Affichage progressif des résultats

2. **Affichage temps réel** :
   - Pour l'alignement, très utile de voir chaque lecture
   - Permet de suivre la progression
   - Facilite l'analyse des résultats

### Exemple d'implémentation pour votre interface web

```python
# Backend Flask/FastAPI inspiré des deux GUI
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess
import os
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Chemin vers gw.exe (ou gw sur Linux)
GW_CMD = 'gw.exe' if os.name == 'nt' else 'gw'

@app.route('/api/read', methods=['POST'])
def read_disk():
    """Lit une disquette - équivalent du bouton Read dans GUI"""
    data = request.json
    format_type = data.get('format', 'ibm.1440')
    output_file = data.get('output', 'disk.img')
    tracks = data.get('tracks', None)
    
    cmd = [GW_CMD, 'read', '--format', format_type, output_file]
    if tracks:
        cmd.extend(['--tracks', tracks])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return jsonify({
        'success': result.returncode == 0,
        'stdout': result.stdout,
        'stderr': result.stderr
    })

@app.route('/api/align', methods=['POST'])
def align():
    """Test d'alignement avec affichage temps réel (inspiré de FluxMyFluffyFloppy)"""
    data = request.json
    cyl = data.get('cylinder', 0)
    head = data.get('head', 0)
    reads = data.get('reads', 10)
    revs = data.get('revolutions', 3)
    
    def run_align():
        cmd = [GW_CMD, 'align', '--tracks', f'c={cyl}:h={head}',
               '--reads', str(reads), '--revs', str(revs), '--raw']
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Envoyer chaque ligne en temps réel (comme le terminal intégré)
        for line in process.stdout:
            socketio.emit('align_output', {'line': line.strip()})
        
        process.wait()
        socketio.emit('align_complete', {'returncode': process.returncode})
    
    # Lancer dans un thread séparé
    thread = threading.Thread(target=run_align)
    thread.start()
    
    return jsonify({'status': 'started'})

@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'Connected to alignment stream'})
```

## Comparaison avec votre interface web

### Avantages de votre approche web

| Aspect | GUI Windows | Votre Interface Web |
|--------|-------------|---------------------|
| **Plateforme** | Windows uniquement | Multi-plateforme (navigateur) |
| **Technologie** | C#/.NET ou Pascal | Python / Flask/FastAPI + HTML/JS |
| **Installation** | Exécutable Windows | Serveur web accessible |
| **Accès** | Local uniquement | À distance possible |
| **Mise à jour** | Téléchargement manuel | Mise à jour serveur |
| **Terminal temps réel** | FluxMyFluffyFloppy uniquement | WebSocket possible |
| **Commande align** | Dépend de gw.exe | Peut intégrer PR #592 directement |
| **Extensibilité** | Nécessite recompilation | Facile à étendre |

### Fonctionnalités à implémenter

1. **Terminal intégré (inspiré de FluxMyFluffyFloppy)** :
   - Utiliser WebSocket pour l'affichage temps réel
   - Afficher chaque ligne de sortie de `gw align`
   - Permettre de suivre la progression

2. **Gestion des formats** :
   - Charger les `diskdef*.cfg` côté serveur
   - Exposer via API REST
   - Permettre la sélection dans l'interface

3. **Interface d'alignement dédiée** :
   - Formulaire pour les paramètres (cylindre, tête, reads, revs)
   - Affichage temps réel des résultats
   - Graphiques de progression
   - Statistiques finales

## Conclusion

Les deux GUI Windows servent d'excellentes **références d'implémentation** pour votre interface web :

✅ **GreaseweazleGUI-dotNET** :
- Montre l'architecture de base
- Gestion des commandes
- Organisation de l'interface

✅ **FluxMyFluffyFloppy** :
- Terminal intégré pour temps réel
- Affichage progressif
- Version active et maintenue

**Votre interface web aura l'avantage** :
- ✅ Multi-plateforme
- ✅ Accessible à distance
- ✅ Plus facilement extensible
- ✅ Intégrable avec le PR #592 directement
- ✅ WebSocket pour temps réel (comme le terminal de FluxMyFluffyFloppy)

## Ressources supplémentaires

### Liens communs

- **Greaseweazle principal** : https://github.com/keirf/greaseweazle
- **Wiki Greaseweazle** : https://github.com/keirf/greaseweazle/wiki
- **Fichiers diskdef** : https://github.com/keirf/greaseweazle/tree/master/src/greaseweazle/data
- **Forum Facebook** : https://www.facebook.com/groups/greaseweazle/

### Documentation spécifique

- **GreaseweazleGUI-dotNET** : https://github.com/Foosie/GreaseweazleGUI-dotNET
- **FluxMyFluffyFloppy** : https://github.com/FrankieTheFluff/FluxMyFluffyFloppy
- **UnTerminal** : https://github.com/t-edson/UnTerminal
