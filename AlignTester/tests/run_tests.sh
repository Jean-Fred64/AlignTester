#!/bin/bash
# Script helper pour exécuter les tests du Mode Direct
# Active automatiquement le venv et exécute les tests

set -e  # Arrêter en cas d'erreur

# Aller dans le répertoire du projet
cd "$(dirname "$0")/.."

# Activer le venv
if [ -f "venv/bin/activate" ]; then
    echo "🔧 Activation du venv..."
    source venv/bin/activate
else
    echo "❌ Erreur: venv non trouvé dans $(pwd)/venv"
    echo "   Créez le venv avec: python3 -m venv venv"
    exit 1
fi

# Vérifier quel test exécuter
if [ "$1" == "api" ]; then
    echo "🌐 Exécution des tests API..."
    python3 tests/test_mode_direct_api.py
elif [ "$1" == "unit" ] || [ "$1" == "" ]; then
    echo "🧪 Exécution des tests unitaires..."
    python3 tests/test_mode_direct.py
else
    echo "Usage: $0 [unit|api]"
    echo "  unit  - Tests unitaires (par défaut)"
    echo "  api   - Tests API (nécessite le serveur démarré)"
    exit 1
fi
