#!/bin/bash
# Script de build pour Greaseweazle version 1.23b avec commande align
# Usage: ./scripts/build_greaseweazle_1.23b.sh [options]

set -e  # Arrêter en cas d'erreur

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GW_SOURCE_DIR="$PROJECT_ROOT/src/greaseweazle-1.23b"
VENV_DIR="$PROJECT_ROOT/venv"

# Options
INSTALL_MODE="venv"  # local, system, venv
CLEAN_BUILD=false
TEST_ALIGN=false

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    --install-mode MODE    Mode d'installation: local, system, venv (défaut: venv)
    --clean               Nettoyer avant le build
    --test-align          Tester la commande align après le build
    --help                Afficher cette aide

Modes d'installation:
    local   - Installation dans un dossier local
    system  - Installation dans le système Python
    venv    - Installation dans l'environnement virtuel (défaut)

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-mode)
            INSTALL_MODE="$2"
            shift 2
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --test-align)
            TEST_ALIGN=true
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

# Vérifier que le dossier source existe
if [ ! -d "$GW_SOURCE_DIR" ]; then
    print_error "Dossier source introuvable: $GW_SOURCE_DIR"
    exit 1
fi

print_info "Dossier source: $GW_SOURCE_DIR"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_info "Python: $PYTHON_VERSION"

# Préparer l'environnement selon le mode
case $INSTALL_MODE in
    venv)
        if [ ! -d "$VENV_DIR" ]; then
            print_info "Création de l'environnement virtuel..."
            python3 -m venv "$VENV_DIR"
        fi
        print_info "Activation de l'environnement virtuel..."
        source "$VENV_DIR/bin/activate"
        PYTHON_EXEC="python"
        ;;
    system)
        PYTHON_EXEC="python3"
        print_warn "Installation dans le système Python (peut nécessiter sudo)"
        ;;
    local)
        PYTHON_EXEC="python3"
        print_info "Installation locale"
        ;;
    *)
        print_error "Mode d'installation invalide: $INSTALL_MODE"
        exit 1
        ;;
esac

# Nettoyer si demandé
if [ "$CLEAN_BUILD" = true ]; then
    print_info "Nettoyage des fichiers de build..."
    cd "$GW_SOURCE_DIR"
    if [ -f Makefile ]; then
        make clean 2>/dev/null || true
    fi
    rm -rf build dist *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
fi

# Installer les dépendances de build
print_info "Installation des dépendances de build..."
$PYTHON_EXEC -m pip install -U pip setuptools wheel setuptools-scm > /dev/null 2>&1 || {
    print_error "Échec de l'installation des dépendances de build"
    exit 1
}

# Vérifier les dépendances du projet
print_info "Vérification des dépendances Greaseweazle..."
cd "$GW_SOURCE_DIR"
MISSING_DEPS=()
for dep in crcmod bitarray pyserial requests; do
    if ! $PYTHON_EXEC -c "import ${dep//-/_}" 2>/dev/null; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_warn "Dépendances manquantes: ${MISSING_DEPS[*]}"
    print_info "Installation des dépendances..."
    $PYTHON_EXEC -m pip install "${MISSING_DEPS[@]}" || {
        print_error "Échec de l'installation des dépendances"
        exit 1
    }
fi

# Installer depuis les sources avec version 1.23b
print_info "Installation de Greaseweazle 1.23b depuis les sources..."
cd "$GW_SOURCE_DIR"
export SETUPTOOLS_SCM_PRETEND_VERSION="1.23b"
$PYTHON_EXEC -m pip install . || {
    print_error "Échec de l'installation"
    exit 1
}

print_info "Installation terminée avec succès!"

# Afficher la version
print_info "Version installée:"
if command -v gw &> /dev/null; then
    python3 -c "import greaseweazle; print('  ' + greaseweazle.__version__)" 2>&1
    gw --help 2>&1 | grep -A 15 "Actions:" | head -20
else
    $PYTHON_EXEC -c "import greaseweazle; print('  ' + greaseweazle.__version__)" 2>&1 || true
fi

# Tester la commande align si demandé
if [ "$TEST_ALIGN" = true ]; then
    print_info "Test de la commande align..."
    if command -v gw &> /dev/null; then
        if gw align --help &> /dev/null; then
            print_info "✅ La commande align est disponible!"
            gw align --help | head -25
        else
            print_warn "❌ La commande align n'est pas disponible"
        fi
    else
        print_warn "Impossible de tester (gw non trouvé dans PATH)"
    fi
fi

print_info "Build terminé avec succès!"
print_info "Pour utiliser gw, exécutez: gw"

