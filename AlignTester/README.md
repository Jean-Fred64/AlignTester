# AlignTester - Application Web d'Alignement Greaseweazle

Application web moderne pour les tests d'alignement de têtes de disquette utilisant la carte Greaseweazle.

## 🚀 Démarrage rapide

### Prérequis

- Python 3.9 ou supérieur
- Node.js 18 ou supérieur
- Greaseweazle avec la commande `align` (PR #592) ou version officielle quand mergé

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

Le frontend sera accessible sur `http://localhost:3000`

L'interface sera accessible sur `http://localhost:3000`

## 📁 Structure du projet

```
AlignTester/
├── src/
│   ├── backend/          # Backend FastAPI
│   │   ├── main.py       # Point d'entrée
│   │   └── api/          # Routes et logique API
│   └── frontend/         # Frontend React + TypeScript
│       ├── src/
│       └── package.json
├── tests/                # Tests
├── docs/                 # Documentation de développement
├── scripts/              # Scripts utilitaires
└── requirements.txt      # Dépendances Python
```

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

## 📦 Préparation de la release

Utilisez le script pour préparer la version finale :

```bash
python AlignTester/scripts/prepare_release.py
```

## 📚 Documentation

- Documentation de développement : `docs/`
- Analyse stratégique : `docs/ANALYSE_STRATEGIE_DEVELOPPEMENT.md`

## 🔧 Fonctionnalités

- ✅ Détection automatique de la plateforme (Windows/Linux/macOS)
- ✅ Détection de la disponibilité de la commande `align`
- ✅ API REST pour les commandes
- ✅ WebSocket pour affichage temps réel
- ⏳ Interface de test d'alignement (en développement)
- ⏳ Graphiques de visualisation (en développement)

## 📄 Licence

[À définir]
