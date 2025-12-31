#!/bin/bash
# Script pour vérifier et installer les dépendances

cd "$(dirname "$0")/.."

echo "🔍 Vérification des dépendances AlignTester..."
echo ""

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    echo "📦 Activation de l'environnement virtuel..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 Activation de l'environnement virtuel..."
    source .venv/bin/activate
fi

echo ""
echo "📋 État actuel des dépendances:"
echo ""

# Fonction pour vérifier un module
check_module() {
    python3 -c "import $1; print('  ✓ $1:', $1.__version__)" 2>/dev/null || echo "  ✗ $1 non installé"
}

check_module fastapi
check_module pytest
check_module pytest_asyncio
check_module uvicorn
check_module websockets
check_module pydantic
python3 -c "import httpx; print('  ✓ httpx:', httpx.__version__)" 2>/dev/null || echo "  ✗ httpx non installé (optionnel)"
python3 -c "import pytest_cov; print('  ✓ pytest-cov:', pytest_cov.__version__)" 2>/dev/null || echo "  ✗ pytest-cov non installé (optionnel)"

echo ""
echo "💡 Pour installer les dépendances manquantes:"
echo "   pip install -r requirements.txt"
echo ""

