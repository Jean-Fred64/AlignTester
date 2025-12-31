#!/bin/bash
# Script de démarrage pour le développement AlignTester

echo "🚀 Démarrage d'AlignTester en mode développement..."
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "src/backend" ] || [ ! -d "src/frontend" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le dossier AlignTester/"
    exit 1
fi

# Fonction pour arrêter les processus sur un port
stop_port() {
    local port=$1
    local name=$2
    
    # Trouver les processus qui utilisent le port
    # Essayer différentes méthodes selon le système
    local pids=""
    
    # Méthode 1: lsof (Linux/Mac)
    if command -v lsof >/dev/null 2>&1; then
        pids=$(lsof -ti:$port 2>/dev/null || echo "")
    fi
    
    # Méthode 2: fuser (Linux)
    if [ -z "$pids" ] && command -v fuser >/dev/null 2>&1; then
        pids=$(fuser $port/tcp 2>/dev/null | awk '{print $1}' || echo "")
    fi
    
    # Méthode 3: ss/netstat (Linux)
    if [ -z "$pids" ] && command -v ss >/dev/null 2>&1; then
        pids=$(ss -ltnp 2>/dev/null | grep ":$port " | awk '{print $6}' | cut -d',' -f2 | cut -d'=' -f2 | sort -u || echo "")
    fi
    
    if [ -n "$pids" ]; then
        echo "🛑 Arrêt des processus $name sur le port $port..."
        for pid in $pids; do
            # Nettoyer les espaces et caractères non numériques
            pid=$(echo "$pid" | tr -d '[:space:]' | grep -o '[0-9]*' | head -1)
            if [ -n "$pid" ] && [ "$pid" -gt 0 ] 2>/dev/null && kill -0 $pid 2>/dev/null; then
                echo "   Arrêt du processus PID $pid..."
                kill -TERM $pid 2>/dev/null
                sleep 1
                # Si le processus est toujours actif, forcer l'arrêt
                if kill -0 $pid 2>/dev/null; then
                    echo "   Force l'arrêt du processus PID $pid..."
                    kill -KILL $pid 2>/dev/null
                fi
            fi
        done
        sleep 1
    fi
}

# Fonction pour arrêter les processus par nom
stop_process() {
    local pattern=$1
    local name=$2
    
    # Trouver les processus correspondant au pattern
    local pids=$(pgrep -f "$pattern" 2>/dev/null || echo "")
    
    if [ -n "$pids" ]; then
        echo "🛑 Arrêt des processus $name..."
        for pid in $pids; do
            if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
                echo "   Arrêt du processus PID $pid ($name)..."
                kill -TERM $pid 2>/dev/null
                sleep 1
                # Si le processus est toujours actif, forcer l'arrêt
                if kill -0 $pid 2>/dev/null; then
                    echo "   Force l'arrêt du processus PID $pid..."
                    kill -KILL $pid 2>/dev/null
                fi
            fi
        done
        sleep 1
    fi
}

# Vérifier et arrêter les serveurs existants
echo "🔍 Vérification des serveurs existants..."
echo ""

# Arrêter les processus sur le port 8000 (backend)
stop_port 8000 "Backend (FastAPI)"

# Arrêter les processus sur le port 5173 (frontend Vite)
stop_port 5173 "Frontend (Vite)"

# Arrêter les processus sur le port 3000 (frontend alternatif)
stop_port 3000 "Frontend (alternatif)"

# Arrêter les processus Python (main.py, uvicorn)
stop_process "main.py" "Backend Python"
stop_process "uvicorn.*main:app" "Uvicorn"

# Arrêter les processus Node/Vite
stop_process "vite" "Vite dev server"
stop_process "node.*vite" "Node Vite"

echo "✅ Vérification terminée"
echo ""

# Activer le venv si disponible
VENV_PYTHON="python3"
if [ -d "venv" ]; then
    echo "🔧 Activation de l'environnement virtuel..."
    source venv/bin/activate
    VENV_PYTHON="$(which python)"
    echo "   Python: $VENV_PYTHON"
fi

# Démarrer le backend en arrière-plan
echo "📡 Démarrage du backend FastAPI..."
cd src/backend

# Vérifier que les dépendances sont installées
if ! $VENV_PYTHON -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "❌ Erreur: Les dépendances Python ne sont pas installées"
    echo "   Exécutez: pip install -r requirements.txt"
    cd ../..
    exit 1
fi

# Créer un fichier de log pour le backend
BACKEND_LOG="../../backend.log"
echo "   Logs du backend: $BACKEND_LOG"

# Démarrer le backend avec uvicorn directement (plus fiable)
$VENV_PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
cd ../..

# Attendre que le backend démarre et vérifier qu'il répond
echo "   Attente du démarrage du backend..."
MAX_WAIT=10
WAIT_COUNT=0
BACKEND_READY=false

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    
    # Vérifier si le processus est toujours actif
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Erreur: Le backend s'est arrêté immédiatement"
        echo "   Vérifiez les logs: $BACKEND_LOG"
        if [ -f "$BACKEND_LOG" ]; then
            echo "   Dernières lignes du log:"
            tail -20 "$BACKEND_LOG" | sed 's/^/   /'
        fi
        exit 1
    fi
    
    # Vérifier si le backend répond
    # Essayer curl d'abord, puis wget, puis python
    if command -v curl >/dev/null 2>&1; then
        if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
            BACKEND_READY=true
            break
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget -q -O /dev/null http://localhost:8000/api/health 2>/dev/null; then
            BACKEND_READY=true
            break
        fi
    elif $VENV_PYTHON -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" 2>/dev/null; then
        BACKEND_READY=true
        break
    fi
done

if [ "$BACKEND_READY" = false ]; then
    echo "❌ Erreur: Le backend ne répond pas après ${MAX_WAIT} secondes"
    echo "   Vérifiez les logs: $BACKEND_LOG"
    if [ -f "$BACKEND_LOG" ]; then
        echo "   Dernières lignes du log:"
        tail -20 "$BACKEND_LOG" | sed 's/^/   /'
    fi
    # Arrêter le processus
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend démarré avec succès (PID: $BACKEND_PID)"

# Démarrer le frontend
echo "🎨 Démarrage du frontend React..."
cd src/frontend

# Vérifier que npm est installé
if ! command -v npm >/dev/null 2>&1; then
    echo "❌ Erreur: npm n'est pas installé"
    cd ../..
    exit 1
fi

# Vérifier que node_modules existe
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules n'existe pas, installation des dépendances..."
    npm install
fi

# Créer un fichier de log pour le frontend
FRONTEND_LOG="../../frontend.log"
echo "   Logs du frontend: $FRONTEND_LOG"

npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd ../..

# Attendre un peu pour que le frontend démarre
sleep 2

# Vérifier que le frontend est toujours actif
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Erreur: Le frontend s'est arrêté immédiatement"
    echo "   Vérifiez les logs: $FRONTEND_LOG"
    if [ -f "$FRONTEND_LOG" ]; then
        echo "   Dernières lignes du log:"
        tail -20 "$FRONTEND_LOG" | sed 's/^/   /'
    fi
    # Arrêter le backend
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend démarré avec succès (PID: $FRONTEND_PID)"

echo ""
echo "✅ Serveurs démarrés!"
echo "   📡 Backend:  http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🎨 Frontend: http://localhost:3000"
echo ""
echo "💡 Le mode manuel est disponible dans l'onglet 'Mode Manuel'"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter les serveurs"

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    echo "🛑 Arrêt des serveurs..."
    
    # Arrêter le backend
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   Arrêt du backend (PID $BACKEND_PID)..."
        kill -TERM $BACKEND_PID 2>/dev/null
        sleep 1
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -KILL $BACKEND_PID 2>/dev/null
        fi
    fi
    
    # Arrêter le frontend
    if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "   Arrêt du frontend (PID $FRONTEND_PID)..."
        kill -TERM $FRONTEND_PID 2>/dev/null
        sleep 1
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill -KILL $FRONTEND_PID 2>/dev/null
        fi
    fi
    
    # Nettoyer les processus restants sur les ports
    stop_port 8000 "Backend"
    stop_port 3000 "Frontend"
    stop_port 5173 "Frontend (Vite alternatif)"
    
    # Supprimer les fichiers de log
    if [ -f "backend.log" ]; then
        rm -f "backend.log"
    fi
    if [ -f "frontend.log" ]; then
        rm -f "frontend.log"
    fi
    
    echo "✅ Serveurs arrêtés"
    exit 0
}

# Attendre l'interruption
trap cleanup INT TERM
wait

