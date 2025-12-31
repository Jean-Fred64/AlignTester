#!/bin/bash
# Script pour créer des builds standalone pour toutes les plateformes
# Note: Ce script crée uniquement le build pour la plateforme actuelle
# Pour les autres plateformes, utilisez GitHub Actions ou des machines virtuelles

set -e

echo "============================================================"
echo "🚀 Build Standalone AlignTester - Toutes les plateformes"
echo "============================================================"

# Détecter la plateforme actuelle
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [[ "$PLATFORM" == "linux" ]]; then
    PLATFORM_NAME="linux"
elif [[ "$PLATFORM" == "darwin" ]]; then
    PLATFORM_NAME="macos"
elif [[ "$PLATFORM" == *"mingw"* ]] || [[ "$PLATFORM" == *"msys"* ]]; then
    PLATFORM_NAME="windows"
else
    echo "⚠️  Plateforme non reconnue: $PLATFORM"
    PLATFORM_NAME="unknown"
fi

echo "🖥️  Plateforme détectée: $PLATFORM_NAME ($ARCH)"
echo ""

# Vérifier les prérequis
echo "📋 Vérification des prérequis..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "⚠️  PyInstaller n'est pas installé"
    echo "   Installation de PyInstaller..."
    pip install pyinstaller
fi

echo "✓ Prérequis OK"
echo ""

# Installer les dépendances Python
echo "📦 Installation des dépendances Python..."
pip install -r AlignTester/requirements.txt

# Builder le frontend
echo ""
echo "📦 Build du frontend..."
cd AlignTester/src/frontend
if [ ! -d "node_modules" ]; then
    echo "   Installation des dépendances npm..."
    npm install
fi
npm run build
cd ../../..

# Lancer le build standalone
echo ""
echo "🔨 Build standalone pour $PLATFORM_NAME..."
python AlignTester/scripts/build_standalone.py

# Afficher le résultat
echo ""
echo "============================================================"
echo "✅ Build terminé pour $PLATFORM_NAME!"
echo "============================================================"
echo ""
echo "📁 Exécutable disponible dans:"
echo "   build_standalone/dist/$PLATFORM_NAME/aligntester/"
echo ""
echo "📦 Pour créer les builds pour les autres plateformes:"
echo ""
echo "   Option 1: GitHub Actions (recommandé)"
echo "   1. Initialisez un dépôt Git:"
echo "      git init"
echo "      git add ."
echo "      git commit -m 'Initial commit'"
echo "      git remote add origin <votre-repo-github>"
echo "      git push -u origin main"
echo ""
echo "   2. Créez un tag pour déclencher le build:"
echo "      git tag v0.1.0"
echo "      git push origin v0.1.0"
echo ""
echo "   3. Les builds seront disponibles dans l'onglet Actions"
echo ""
echo "   Option 2: Build manuel"
echo "   - Windows: Exécutez ce script sur une machine Windows"
echo "   - macOS: Exécutez ce script sur une machine macOS"
echo ""
echo "============================================================"
