#!/bin/bash
# Script pour compiler les routines optimisées de Greaseweazle
# Usage: ./scripts/setup.sh [--venv PATH] [--system]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GW_SOURCE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Options
USE_VENV=true
VENV_PATH="$PROJECT_ROOT/venv"
INSTALL_MODE="venv"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

usage() {
    cat << EOF
Usage: $0 [options]

Options:
    --venv PATH     Chemin vers l'environnement virtuel (défaut: ../venv)
    --system       Installer dans le système Python au lieu du venv
    --help         Afficher cette aide

Ce script compile les routines optimisées (extensions C) de Greaseweazle.
Les routines optimisées améliorent les performances lors de la lecture/écriture de disquettes.

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --venv)
            VENV_PATH="$2"
            shift 2
            ;;
        --system)
            USE_VENV=false
            INSTALL_MODE="system"
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            print_error "Option inconnue: $1"
            usage
            exit 1
            ;;
    esac
done

print_info "Compilation des routines optimisées de Greaseweazle"
print_info "Dossier source: $GW_SOURCE_DIR"

# Vérifier que le dossier source existe
if [ ! -d "$GW_SOURCE_DIR" ]; then
    print_error "Dossier source introuvable: $GW_SOURCE_DIR"
    exit 1
fi

# Vérifier que setup.py existe
if [ ! -f "$GW_SOURCE_DIR/setup.py" ]; then
    print_error "setup.py introuvable dans: $GW_SOURCE_DIR"
    exit 1
fi

# Préparer l'environnement Python
if [ "$USE_VENV" = true ]; then
    if [ ! -d "$VENV_PATH" ]; then
        print_warn "Environnement virtuel introuvable: $VENV_PATH"
        print_info "Création de l'environnement virtuel..."
        python3 -m venv "$VENV_PATH"
    fi
    
    print_info "Activation de l'environnement virtuel: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
    PYTHON_EXEC="python"
else
    PYTHON_EXEC="python3"
    print_info "Utilisation du Python système"
fi

# Vérifier Python
if ! command -v "$PYTHON_EXEC" &> /dev/null; then
    print_error "Python non trouvé: $PYTHON_EXEC"
    exit 1
fi

PYTHON_VERSION=$("$PYTHON_EXEC" --version)
print_info "Python: $PYTHON_VERSION"

# Vérifier les dépendances de build
print_info "Vérification des dépendances de build..."
"$PYTHON_EXEC" -m pip install -U pip setuptools wheel setuptools-scm > /dev/null 2>&1 || {
    print_error "Échec de l'installation des dépendances de build"
    exit 1
}

# Vérifier le compilateur C
if ! command -v gcc &> /dev/null; then
    print_warn "GCC non trouvé. Les routines optimisées nécessitent un compilateur C."
    print_info "Sur Ubuntu/Debian: sudo apt install gcc"
    print_info "Sur Fedora: sudo dnf install gcc"
    print_info "Sur macOS: xcode-select --install"
    exit 1
fi

print_info "Compilateur C trouvé: $(gcc --version | head -1)"

# Aller dans le dossier source
cd "$GW_SOURCE_DIR"

# Nettoyer les anciens builds si nécessaire
if [ -d "build" ]; then
    print_info "Nettoyage des anciens builds..."
    rm -rf build dist *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
fi

# Compiler et installer les extensions
print_info "Compilation des extensions C optimisées..."
"$PYTHON_EXEC" -m pip install -e . --force-reinstall --no-deps > /dev/null 2>&1 || {
    print_error "Échec de la compilation"
    print_info "Tentative avec installation complète..."
    "$PYTHON_EXEC" -m pip install . --force-reinstall || {
        print_error "Échec de l'installation"
        exit 1
    }
}

# Vérifier que les routines optimisées sont disponibles
print_info "Vérification des routines optimisées..."
"$PYTHON_EXEC" -c "from greaseweazle.optimised import optimised; print('✅ Routines optimisées compilées et disponibles')" 2>&1 || {
    print_error "Les routines optimisées ne sont toujours pas disponibles"
    print_info "Vérifiez les erreurs de compilation ci-dessus"
    exit 1
}

print_info "✅ Compilation terminée avec succès!"
print_info "Les routines optimisées sont maintenant disponibles."

# Afficher la version
if command -v gw &> /dev/null; then
    print_info "Version Greaseweazle:"
    gw --version 2>&1 | head -5 || true
fi

