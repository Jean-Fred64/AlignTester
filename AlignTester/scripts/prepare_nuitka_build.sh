#!/bin/bash
# Script pour préparer l'environnement et compiler avec Nuitka
# Usage: ./scripts/prepare_nuitka_build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GW_SOURCE_DIR="$PROJECT_ROOT/src/greaseweazle-1.23b"
BUILD_OUTPUT_DIR="$PROJECT_ROOT/build/greaseweazle-1.23b-windows"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_section "Préparation de l'environnement pour Nuitka"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_info "Python: $PYTHON_VERSION"

# Vérifier MinGW-w64
print_info "Vérification de MinGW-w64..."
if ! command -v x86_64-w64-mingw32-gcc &> /dev/null; then
    print_warn "MinGW-w64 n'est pas installé"
    print_info "Installation de MinGW-w64..."
    print_info "Exécutez cette commande (nécessite sudo):"
    echo ""
    echo -e "${YELLOW}sudo apt update && sudo apt install -y mingw-w64${NC}"
    echo ""
    read -p "Appuyez sur Entrée après avoir installé MinGW-w64, ou Ctrl+C pour annuler..."
    
    # Vérifier à nouveau
    if ! command -v x86_64-w64-mingw32-gcc &> /dev/null; then
        print_error "MinGW-w64 n'est toujours pas installé"
        exit 1
    fi
fi

MINGW_VERSION=$(x86_64-w64-mingw32-gcc --version | head -1)
print_info "MinGW-w64 trouvé: $MINGW_VERSION"

# Installer Nuitka
print_info "Vérification de Nuitka..."
if ! python3 -c "import nuitka" 2>/dev/null; then
    print_info "Installation de Nuitka..."
    python3 -m pip install --upgrade nuitka
else
    NUITKA_VERSION=$(python3 -c "import nuitka; print(nuitka.__version__)" 2>/dev/null)
    print_info "Nuitka trouvé: $NUITKA_VERSION"
fi

# Vérifier que le dossier source existe
if [ ! -d "$GW_SOURCE_DIR" ]; then
    print_error "Dossier source introuvable: $GW_SOURCE_DIR"
    exit 1
fi

print_info "Dossier source: $GW_SOURCE_DIR"

# Installer les dépendances Python de Greaseweazle
print_section "Installation des dépendances"
print_info "Installation des dépendances de build..."
python3 -m pip install --upgrade pip setuptools wheel setuptools-scm

print_info "Installation des dépendances Greaseweazle..."
cd "$GW_SOURCE_DIR"
export SETUPTOOLS_SCM_PRETEND_VERSION="1.23b"
python3 -m pip install -e . || python3 -m pip install .

print_section "Environnement prêt!"
print_info "MinGW-w64: ✅"
print_info "Nuitka: ✅"
print_info "Dépendances: ✅"
echo ""

# Lancer la compilation
print_section "Lancement de la compilation avec Nuitka"
print_info "Compilation de la version Windows..."

# Créer le dossier de sortie
mkdir -p "$BUILD_OUTPUT_DIR/greaseweazle-1.23b"

# Compiler avec Nuitka
print_info "Nuitka va compiler pour Windows (cela peut prendre plusieurs minutes)..."
python3 -m nuitka \
    --standalone \
    --onefile \
    --windows-console-mode \
    --mingw64 \
    --include-module=greaseweazle \
    --include-module=greaseweazle.tools \
    --include-module=greaseweazle.tools.align \
    --include-package-data=greaseweazle \
    --include-data-dir="$GW_SOURCE_DIR/src/greaseweazle/data=greaseweazle/data" \
    --output-dir="$BUILD_OUTPUT_DIR/greaseweazle-1.23b" \
    --output-filename=gw.exe \
    src/greaseweazle/cli.py

if [ $? -eq 0 ]; then
    print_section "Compilation réussie!"
    print_info "Fichiers générés dans: $BUILD_OUTPUT_DIR/greaseweazle-1.23b/"
    
    # Vérifier que gw.exe existe
    if [ -f "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/gw.exe" ]; then
        print_info "✅ gw.exe créé avec succès!"
        ls -lh "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/gw.exe"
    else
        print_warn "gw.exe non trouvé, mais la compilation semble réussie"
        print_info "Fichiers dans le dossier de sortie:"
        ls -la "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/" || true
    fi
else
    print_error "Échec de la compilation"
    exit 1
fi

print_section "Terminé!"
print_info "Vous pouvez maintenant copier les fichiers sur Windows"
print_info "Dossier: $BUILD_OUTPUT_DIR/greaseweazle-1.23b/"

