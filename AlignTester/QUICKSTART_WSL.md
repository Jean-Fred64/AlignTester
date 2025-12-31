# Guide de démarrage rapide - WSL/Linux

## Installation des dépendances

### 1. Backend Python

```bash
cd ~/Aligntester/AlignTester
python3 -m pip install --user -r requirements.txt
```

Si vous utilisez un environnement virtuel (recommandé) :

```bash
cd ~/Aligntester/AlignTester
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend Node.js

**Si Node.js n'est pas installé**, voir `INSTALL_NODEJS_WSL.md` pour les instructions d'installation.

Une fois Node.js installé :

```bash
cd ~/Aligntester/AlignTester/src/frontend
npm install
```

## Démarrage

### Terminal 1 - Backend

```bash
cd ~/Aligntester/AlignTester/src/backend
python3 main.py
```

Ou avec uvicorn directement :

```bash
cd ~/Aligntester/AlignTester/src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend

```bash
cd ~/Aligntester/AlignTester/src/frontend
npm run dev
```

## Accès

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## Notes WSL

- Utilisez `python3` au lieu de `python`
- Pour accéder depuis Windows, utilisez `localhost` (pas l'IP WSL)
- Si les ports ne sont pas accessibles, vérifiez le port forwarding WSL

