#!/bin/bash
# Script pour compiler la version Windows avec Nuitka depuis Linux
# Usage: ./scripts/build_windows_nuitka.sh

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

print_section "Compilation Windows avec Nuitka depuis Linux"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_info "Python: $PYTHON_VERSION"

# Activer le venv si disponible
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    print_info "Environnement virtuel activé"
fi

# Vérifier MinGW-w64
print_info "Vérification de MinGW-w64..."
if ! command -v x86_64-w64-mingw32-gcc &> /dev/null; then
    print_error "MinGW-w64 n'est pas installé"
    echo ""
    print_info "Pour installer MinGW-w64, exécutez:"
    echo -e "${YELLOW}sudo apt update && sudo apt install -y mingw-w64${NC}"
    echo ""
    print_info "Ou sur Fedora:"
    echo -e "${YELLOW}sudo dnf install -y mingw64-gcc${NC}"
    echo ""
    print_warn "MinGW-w64 est nécessaire pour compiler pour Windows"
    exit 1
fi

MINGW_VERSION=$(x86_64-w64-mingw32-gcc --version | head -1)
print_info "✅ MinGW-w64 trouvé: $MINGW_VERSION"

# Vérifier patchelf (nécessaire pour standalone)
print_info "Vérification de patchelf..."
if ! command -v patchelf &> /dev/null; then
    print_error "patchelf n'est pas installé"
    echo ""
    print_info "Pour installer patchelf, exécutez:"
    echo -e "${YELLOW}sudo apt install -y patchelf${NC}"
    echo ""
    print_info "Ou sur Fedora:"
    echo -e "${YELLOW}sudo dnf install -y patchelf${NC}"
    echo ""
    print_warn "patchelf est nécessaire pour le mode standalone"
    exit 1
fi

print_info "✅ patchelf trouvé: $(patchelf --version 2>/dev/null || echo 'installé')"

# Vérifier Nuitka
print_info "Vérification de Nuitka..."
if ! python3 -c "import nuitka" 2>/dev/null; then
    print_warn "Nuitka n'est pas installé"
    print_info "Installation de Nuitka..."
    python3 -m pip install --upgrade nuitka
else
    print_info "✅ Nuitka trouvé"
fi

NUITKA_VERSION=$(python3 -m nuitka --version 2>/dev/null || echo "version inconnue")
print_info "Nuitka version: $NUITKA_VERSION"

# Vérifier que le dossier source existe
if [ ! -d "$GW_SOURCE_DIR" ]; then
    print_error "Dossier source introuvable: $GW_SOURCE_DIR"
    exit 1
fi

print_info "Dossier source: $GW_SOURCE_DIR"

# Installer les dépendances
print_section "Installation des dépendances"
print_info "Mise à jour de pip, setuptools, wheel..."
python3 -m pip install --upgrade pip setuptools wheel setuptools-scm

print_info "Installation des dépendances Greaseweazle..."
cd "$GW_SOURCE_DIR"
export SETUPTOOLS_SCM_PRETEND_VERSION="1.23b"

# Installer Greaseweazle en mode développement
if python3 -m pip install -e . 2>&1 | tee /tmp/gw_install.log; then
    print_info "✅ Greaseweazle installé en mode développement"
else
    print_warn "Échec avec -e, tentative avec installation normale..."
    python3 -m pip install . || {
        print_error "Échec de l'installation de Greaseweazle"
        exit 1
    }
fi

# Vérifier que greaseweazle est importable
if ! python3 -c "import greaseweazle" 2>/dev/null; then
    print_error "Greaseweazle n'est pas importable"
    exit 1
fi

print_info "✅ Greaseweazle importable"

# Créer le dossier de sortie
mkdir -p "$BUILD_OUTPUT_DIR/greaseweazle-1.23b"

# Compiler avec Nuitka
print_section "Compilation avec Nuitka"
print_info "Cette étape peut prendre plusieurs minutes..."
print_info "Nuitka va compiler pour Windows 64-bit..."

cd "$GW_SOURCE_DIR"

# Trouver le chemin vers les données
DATA_DIR="$GW_SOURCE_DIR/src/greaseweazle/data"
if [ ! -d "$DATA_DIR" ]; then
    print_warn "Dossier data non trouvé: $DATA_DIR"
    DATA_DIR=""
fi

# Options de compilation Nuitka
NUITKA_OPTS=(
    --standalone
    --onefile
    --mingw64
    --include-module=greaseweazle
    --include-module=greaseweazle.tools
    --include-module=greaseweazle.tools.align
    --include-module=greaseweazle.optimised
    --include-package-data=greaseweazle
    --output-dir="$BUILD_OUTPUT_DIR/greaseweazle-1.23b"
    --output-filename=gw.exe
    --assume-yes-for-downloads
)

# Ajouter le dossier data si il existe
if [ -n "$DATA_DIR" ] && [ -d "$DATA_DIR" ]; then
    NUITKA_OPTS+=(--include-data-dir="$DATA_DIR=greaseweazle/data")
fi

# Compiler
print_info "Commande: python3 -m nuitka ${NUITKA_OPTS[*]} src/greaseweazle/cli.py"
echo ""

python3 -m nuitka "${NUITKA_OPTS[@]}" src/greaseweazle/cli.py

if [ $? -eq 0 ]; then
    print_section "✅ Compilation réussie!"
    
    # Vérifier que gw.exe existe
    if [ -f "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/gw.exe" ]; then
        print_info "✅ gw.exe créé avec succès!"
        FILE_SIZE=$(du -h "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/gw.exe" | cut -f1)
        print_info "Taille: $FILE_SIZE"
        print_info "Emplacement: $BUILD_OUTPUT_DIR/greaseweazle-1.23b/gw.exe"
    else
        print_warn "gw.exe non trouvé dans le dossier attendu"
        print_info "Recherche dans le dossier de sortie..."
        find "$BUILD_OUTPUT_DIR" -name "gw.exe" -o -name "cli.exe" 2>/dev/null || {
            print_info "Fichiers dans le dossier de sortie:"
            ls -la "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/" 2>/dev/null || true
        }
    fi
    
    print_section "Terminé!"
    print_info "Fichiers disponibles dans: $BUILD_OUTPUT_DIR/greaseweazle-1.23b/"
    print_info "Vous pouvez maintenant copier ces fichiers sur Windows pour les tester"
    
else
    print_error "❌ Échec de la compilation"
    exit 1
fi

