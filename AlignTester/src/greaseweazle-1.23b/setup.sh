#!/bin/bash
# Script pour compiler les routines optimisées de Greaseweazle
# Usage: ./setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GW_SOURCE_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

print_info "Compilation des routines optimisées de Greaseweazle"

# Vérifier que setup.py existe
if [ ! -f "$GW_SOURCE_DIR/setup.py" ]; then
    print_error "setup.py introuvable dans: $GW_SOURCE_DIR"
    exit 1
fi

# Utiliser le venv s'il existe, sinon le Python système
if [ -d "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/activate" ]; then
    print_info "Utilisation de l'environnement virtuel: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
    PYTHON_EXEC="python"
else
    print_warn "Environnement virtuel non trouvé, utilisation du Python système"
    PYTHON_EXEC="python3"
fi

# Vérifier Python
if ! command -v "$PYTHON_EXEC" &> /dev/null; then
    print_error "Python non trouvé: $PYTHON_EXEC"
    exit 1
fi

PYTHON_VERSION=$("$PYTHON_EXEC" --version)
print_info "Python: $PYTHON_VERSION"

# Vérifier le compilateur C
if ! command -v gcc &> /dev/null; then
    print_error "GCC non trouvé. Les routines optimisées nécessitent un compilateur C."
    print_info "Sur Ubuntu/Debian: sudo apt install gcc"
    print_info "Sur Fedora: sudo dnf install gcc"
    exit 1
fi

# Installer les dépendances de build
print_info "Installation des dépendances de build..."
"$PYTHON_EXEC" -m pip install -U pip setuptools wheel setuptools-scm > /dev/null 2>&1

# Aller dans le dossier source
cd "$GW_SOURCE_DIR"

# Compiler et installer
print_info "Compilation des extensions C optimisées..."
"$PYTHON_EXEC" -m pip install -e . --force-reinstall > /dev/null 2>&1 || {
    print_warn "Échec avec -e, tentative avec installation normale..."
    "$PYTHON_EXEC" -m pip install . --force-reinstall || {
        print_error "Échec de la compilation"
        exit 1
    }
}

# Vérifier
print_info "Vérification des routines optimisées..."
if "$PYTHON_EXEC" -c "from greaseweazle.optimised import optimised" 2>/dev/null; then
    print_info "✅ Routines optimisées compilées avec succès!"
else
    print_warn "⚠️  Les routines optimisées ne sont pas disponibles"
    print_info "Cela n'empêche pas l'utilisation de Greaseweazle, mais peut affecter les performances."
fi

