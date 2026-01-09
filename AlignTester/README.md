# AlignTester - Application Web d'Alignement Greaseweazle

Application web moderne pour les tests d'alignement de têtes de disquette utilisant la carte Greaseweazle.

## 📋 Vue d'ensemble

AlignTester est une application web complète qui permet de tester et régler l'alignement des têtes de lecteurs de disquette en utilisant la carte Greaseweazle. L'application offre deux modes d'alignement :

- **Mode automatique** : Alignement automatisé avec la commande `gw align` (disponible uniquement sur Windows avec Greaseweazle v1.23b)
- **Mode manuel** : Alignement manuel avec navigation par pistes utilisant également `gw align` (disponible uniquement sur Windows avec Greaseweazle v1.23b)

## ⚠️ Compatibilité Greaseweazle

### Version utilisée

AlignTester utilise une **version compilée v1.23b de Greaseweazle** qui inclut la commande `align` issue du [Pull Request #592](https://github.com/keirf/greaseweazle/pull/592). Les sources de cette version sont disponibles dans `AlignTester/src/greaseweazle-1.23b.zip`.

### Compatibilité par plateforme

| Plateforme | Interface | Mode Automatique (`gw align`) | Mode Manuel (`gw align`) |
|------------|-----------|-------------------------------|-------------------------|
| **Windows** | ✅ Fonctionnelle | ✅ Disponible (v1.23b) | ✅ Disponible (v1.23b) |
| **Linux** | ✅ Fonctionnelle | ❌ Non disponible (v1.22 uniquement) | ❌ Non disponible (v1.22 uniquement) |
| **macOS** | ✅ Fonctionnelle | ❌ Non disponible (v1.22 uniquement) | ❌ Non disponible (v1.22 uniquement) |

**Note importante** :
- L'interface fonctionne correctement sur toutes les plateformes
- Les **deux modes** (automatique et manuel) utilisent la commande `gw align` et nécessitent Greaseweazle v1.23b
- Sous Windows, Greaseweazle v1.23b est disponible avec support de `gw align` (PR #592)
- Sous Linux/macOS, seule la version Greaseweazle v1.22 est disponible, qui ne supporte pas la commande `align`
- Les deux modes d'alignement nécessitent donc Greaseweazle v1.23b (actuellement disponible uniquement sur Windows)

## 🚀 Démarrage rapide

### Prérequis

- Python 3.9 ou supérieur
- Node.js 18 ou supérieur
- **Greaseweazle** :
- **Windows** : Greaseweazle v1.23b avec commande `align` (PR #592) - **Requis pour les modes d'alignement**
- **Linux/macOS** : Greaseweazle v1.22+ (interface fonctionnelle, mais modes d'alignement non disponibles sans v1.23+)

### Installation

1. **Installer les dépendances Python (backend)**

```bash
cd AlignTester
python3 -m pip install -r requirements.txt
```

2. **Installer les dépendances Node.js (frontend)**

```bash
cd src/frontend
npm install
```

### Lancement

#### Option 1 : Script de démarrage automatique (recommandé)

**Sur Linux/WSL :**
```bash
cd AlignTester
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

**Sur Windows :**
```cmd
cd AlignTester
scripts\start_dev.bat
```

Le script démarre automatiquement le backend et le frontend.

#### Option 2 : Démarrage manuel

1. **Démarrer le backend**

```bash
cd AlignTester/src/backend
python3 main.py
```

Ou avec uvicorn directement :
```bash
cd AlignTester/src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur `http://localhost:8000`

2. **Démarrer le frontend** (dans un autre terminal)

```bash
cd AlignTester/src/frontend
npm run dev
```

Le frontend sera accessible sur `http://localhost:3000` (ou `http://localhost:5173` selon la configuration Vite)

## 📁 Structure du projet

```
AlignTester/
├── src/
│   ├── backend/                    # Backend FastAPI
│   │   ├── main.py                # Point d'entrée
│   │   └── api/                   # Routes et logique API
│   ├── frontend/                   # Frontend React + TypeScript
│   │   ├── src/
│   │   └── package.json
│   └── greaseweazle-1.23b.zip     # Sources Greaseweazle v1.23b (PR #592)
├── tests/                          # Tests unitaires et d'intégration
├── docs/                           # Documentation de développement
├── scripts/                        # Scripts utilitaires
│   ├── build_standalone.py         # Build standalone
│   └── launcher_standalone.py      # Launcher standalone
└── requirements.txt                # Dépendances Python
```

### Sources Greaseweazle

Le projet utilise les sources de Greaseweazle v1.23b (PR #592) pour le build standalone Windows. Les sources sont disponibles dans `AlignTester/src/greaseweazle-1.23b.zip` (11MB).

**Téléchargement direct** : [greaseweazle-1.23b.zip](https://github.com/Jean-Fred64/AlignTester/raw/main/AlignTester/src/greaseweazle-1.23b.zip)

**Note** : Le fichier zip doit être décompressé dans `AlignTester/src/greaseweazle-1.23b/` avant d'utiliser les scripts de build standalone.

**Référence** : [Greaseweazle PR #592](https://github.com/keirf/greaseweazle/pull/592)

## 🛠️ Développement

### Backend

Le backend utilise FastAPI avec support WebSocket pour l'affichage temps réel.

- API REST : `http://localhost:8000/api`
- WebSocket : `ws://localhost:8000/ws`
- Documentation auto : `http://localhost:8000/docs`

### Frontend

Le frontend utilise React + TypeScript + Vite + Tailwind CSS.

- Dev server : `http://localhost:3000`
- Build : `npm run build`

## 📝 Configuration

Copiez `.env.example` vers `.env` et modifiez selon vos besoins :

```bash
cp .env.example .env
```

## 🧪 Tests

```bash
cd AlignTester/tests
pytest
```

## 📦 Version Standalone

AlignTester est disponible en version standalone (autonome) pour Windows, Linux et macOS. Cette version ne nécessite pas d'installation de Python ou Node.js.

### Téléchargement

Les builds standalone sont disponibles dans les [GitHub Releases](https://github.com/Jean-Fred64/AlignTester/releases) ou via les artefacts GitHub Actions.

### Build depuis les sources

Pour créer votre propre build standalone :

```bash
cd AlignTester
python scripts/build_standalone.py
```

**Note** : Le build standalone Windows utilise Greaseweazle v1.23b compilé depuis le PR #592. Les sources sont disponibles dans `AlignTester/src/greaseweazle-1.23b.zip`.

## 📦 Préparation de la release

Utilisez le script pour préparer la version finale :

```bash
python AlignTester/scripts/prepare_release.py
```

## 📚 Documentation

### Documentation principale

- **État du projet** : `docs/ETAT_PROJET.md` - État complet du développement
- **Documentation Greaseweazle** : `docs/DOCUMENTATION_GREASEWEAZLE.md` - Guide complet d'utilisation
- **Mode manuel** : `docs/MODE_MANUEL.md` - Guide du mode manuel d'alignement
- **Build standalone** : `docs/BUILD_STANDALONE.md` - Guide de build standalone

### Documentation technique

- Documentation de développement : `docs/`
- Analyse stratégique : `docs/ANALYSE_STRATEGIE_DEVELOPPEMENT.md`
- Intégration Greaseweazle : `docs/INTEGRATION_GREASEWEAZLE.md`

## 🔧 Fonctionnalités

### Fonctionnalités principales

- ✅ **Détection automatique** de Greaseweazle (Windows/Linux/macOS/WSL)
- ✅ **Mode automatique d'alignement** : Alignement automatisé avec `gw align` (Windows uniquement, v1.23+)
- ✅ **Mode manuel d'alignement** : Navigation par pistes avec lecture continue utilisant `gw align` (Windows uniquement, v1.23+)
- ✅ **API REST complète** pour toutes les commandes
- ✅ **WebSocket** pour affichage en temps réel
- ✅ **Interface moderne** avec React + TypeScript + TailwindCSS
- ✅ **Multilingue** : Support FR/EN avec détection automatique
- ✅ **Graphiques de visualisation** : Affichage des résultats avec Recharts
- ✅ **Analyse avancée** : Cohérence, stabilité, positionnement, azimut, asymétrie
- ✅ **Vérification Track 0** : Tests de capteur Track 0 selon manuel Panasonic
- ✅ **Sélection de format** : Support de nombreux formats de disquette (IBM, Amiga, Apple, Commodore, etc.)
- ✅ **Modes d'alignement multiples** : Direct, Ajustage Fin, Grande Précision
- ✅ **Version standalone** : Application autonome pour Windows/Linux/macOS

### Limitations connues

- ⚠️ **Les deux modes d'alignement** : Disponibles uniquement sur Windows avec Greaseweazle v1.23b (les deux utilisent `gw align`)
- ⚠️ **Linux/macOS** : Seule la version Greaseweazle v1.22 est disponible, sans support de `gw align`
- ⚠️ Les modes d'alignement nécessitent Greaseweazle v1.23b (actuellement disponible uniquement sur Windows)

## 📄 Licence

[À définir]
