#!/bin/bash
# Script de démarrage du backend AlignTester

echo "🚀 Démarrage du backend AlignTester..."

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: python3 n'est pas installé"
    exit 1
fi

echo "✅ Python 3 trouvé: $(python3 --version)"

# Vérifier si les dépendances sont installées
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Les dépendances ne semblent pas installées."
    echo "📦 Installation des dépendances..."
    cd ../..
    python3 -m pip install --user -r requirements.txt
    cd src/backend
fi

# Démarrer le serveur
echo "📡 Démarrage du serveur FastAPI sur http://localhost:8000"
echo "📚 Documentation API: http://localhost:8000/docs"
echo ""
python3 main.py

