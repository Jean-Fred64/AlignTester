#!/bin/bash
# Script pour compiler la version Windows de Greaseweazle depuis Linux
# Usage: ./scripts/build_windows_from_linux.sh [--method METHOD]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GW_SOURCE_DIR="$PROJECT_ROOT/src/greaseweazle-1.23b"
BUILD_OUTPUT_DIR="$PROJECT_ROOT/build/greaseweazle-1.23b-windows"

# Méthode par défaut
METHOD="wine"

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

usage() {
    cat << EOF
Usage: $0 [options]

Options:
    --method METHOD    Méthode de compilation (wine, pyinstaller, nuitka, docker)
    --help            Afficher cette aide

Méthodes disponibles:
    wine        - Utiliser Wine + Python Windows + cx_Freeze (recommandé)
    pyinstaller  - Utiliser PyInstaller avec Wine
    nuitka      - Utiliser Nuitka (cross-compilation native)
    docker      - Utiliser Docker avec image Windows

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --method)
            METHOD="$2"
            shift 2
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

print_section "Compilation Windows depuis Linux"
print_info "Méthode sélectionnée: $METHOD"
print_info "Dossier source: $GW_SOURCE_DIR"
echo ""

# Méthode 1: Wine + Python Windows + cx_Freeze
build_with_wine() {
    print_section "Méthode: Wine + Python Windows + cx_Freeze"
    
    # Vérifier Wine
    if ! command -v wine &> /dev/null; then
        print_error "Wine n'est pas installé"
        print_info "Installez Wine:"
        print_info "  Ubuntu/Debian: sudo apt install wine wine64"
        print_info "  Fedora: sudo dnf install wine"
        exit 1
    fi
    
    print_info "Wine trouvé: $(wine --version)"
    
    # Vérifier Python Windows
    if [ ! -f "$HOME/.wine/drive_c/Python*/python.exe" ] && [ ! -f "$HOME/.wine/drive_c/Program Files/Python*/python.exe" ]; then
        print_warn "Python Windows non trouvé dans Wine"
        print_info "Vous devez installer Python Windows dans Wine:"
        print_info "  1. Téléchargez Python 3.11 depuis: https://www.python.org/downloads/"
        print_info "  2. Installez-le dans Wine: wine python-3.11.x.exe"
        print_info "  3. Ou utilisez winetricks: winetricks python311"
        exit 1
    fi
    
    # Trouver Python Windows
    PYTHON_WIN=$(find "$HOME/.wine/drive_c" -name "python.exe" -type f 2>/dev/null | head -1)
    if [ -z "$PYTHON_WIN" ]; then
        print_error "Python Windows non trouvé"
        exit 1
    fi
    
    print_info "Python Windows trouvé: $PYTHON_WIN"
    
    # Créer le dossier de build
    mkdir -p "$BUILD_OUTPUT_DIR"
    
    # Copier les sources vers un dossier Windows accessible
    TEMP_WIN_DIR="$HOME/.wine/drive_c/temp/greaseweazle-build"
    mkdir -p "$TEMP_WIN_DIR"
    print_info "Copie des sources vers: $TEMP_WIN_DIR"
    cp -r "$GW_SOURCE_DIR"/* "$TEMP_WIN_DIR/"
    
    # Installer les dépendances dans Wine
    print_info "Installation des dépendances Python dans Wine..."
    wine "$PYTHON_WIN" -m pip install -U pip setuptools wheel cx_Freeze setuptools-scm
    
    # Compiler
    cd "$TEMP_WIN_DIR"
    export SETUPTOOLS_SCM_PRETEND_VERSION="1.23b"
    
    print_info "Compilation avec cx_Freeze..."
    wine "$PYTHON_WIN" -m pip install -e . || {
        print_warn "Échec avec -e, tentative avec installation normale..."
        wine "$PYTHON_WIN" -m pip install .
    }
    
    cd "$TEMP_WIN_DIR/scripts/win"
    wine "$PYTHON_WIN" setup.py build
    
    # Copier les résultats
    BUILD_DIR=$(find build -type d -name "exe.win*" | head -1)
    if [ -n "$BUILD_DIR" ]; then
        print_info "Copie des fichiers compilés vers: $BUILD_OUTPUT_DIR"
        mkdir -p "$BUILD_OUTPUT_DIR/greaseweazle-1.23b"
        cp -r "$BUILD_DIR"/* "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/"
        print_info "✅ Compilation terminée!"
    else
        print_error "Dossier de build non trouvé"
        exit 1
    fi
}

# Méthode 2: PyInstaller avec Wine
build_with_pyinstaller() {
    print_section "Méthode: PyInstaller avec Wine"
    
    print_warn "Cette méthode nécessite PyInstaller et Wine"
    print_info "Installation de PyInstaller..."
    pip3 install pyinstaller
    
    # Créer un script wrapper pour Windows
    cd "$GW_SOURCE_DIR"
    export SETUPTOOLS_SCM_PRETEND_VERSION="1.23b"
    
    # PyInstaller peut créer des exécutables Windows depuis Linux
    # mais nécessite Wine pour tester
    print_info "Création du spec file..."
    pyinstaller --name=gw \
                --onefile \
                --console \
                --add-data "src/greaseweazle:greaseweazle" \
                src/greaseweazle/cli.py
    
    print_warn "PyInstaller crée un exécutable Linux par défaut"
    print_info "Pour Windows, vous devrez utiliser Wine ou compiler sur Windows"
    print_info "Les fichiers sont dans: dist/"
}

# Méthode 3: Nuitka (cross-compilation)
build_with_nuitka() {
    print_section "Méthode: Nuitka (cross-compilation)"
    
    # Vérifier Nuitka
    if ! command -v nuitka &> /dev/null && ! python3 -c "import nuitka" 2>/dev/null; then
        print_info "Installation de Nuitka..."
        pip3 install nuitka
    fi
    
    # Vérifier MinGW-w64 pour Windows
    if ! command -v x86_64-w64-mingw32-gcc &> /dev/null; then
        print_warn "MinGW-w64 n'est pas installé"
        print_info "Installation de MinGW-w64:"
        print_info "  Ubuntu/Debian: sudo apt install mingw-w64"
        print_info "  Fedora: sudo dnf install mingw64-gcc"
        exit 1
    fi
    
    print_info "MinGW-w64 trouvé: $(x86_64-w64-mingw32-gcc --version | head -1)"
    
    cd "$GW_SOURCE_DIR"
    export SETUPTOOLS_SCM_PRETEND_VERSION="1.23b"
    
    # Installer les dépendances
    print_info "Installation des dépendances..."
    pip3 install -e . || pip3 install .
    
    # Compiler avec Nuitka pour Windows
    print_info "Compilation avec Nuitka pour Windows..."
    python3 -m nuitka \
        --standalone \
        --onefile \
        --windows-console-mode \
        --mingw64 \
        --include-module=greaseweazle \
        --include-package-data=greaseweazle \
        src/greaseweazle/cli.py
    
    mkdir -p "$BUILD_OUTPUT_DIR/greaseweazle-1.23b"
    cp -r cli.dist/* "$BUILD_OUTPUT_DIR/greaseweazle-1.23b/"
    print_info "✅ Compilation terminée!"
}

# Méthode 4: Docker
build_with_docker() {
    print_section "Méthode: Docker"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        print_info "Installez Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    print_warn "Cette méthode nécessite une image Windows Docker"
    print_info "Création d'un Dockerfile pour la compilation..."
    
    # Créer un Dockerfile temporaire
    cat > /tmp/Dockerfile.gw << 'EOF'
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Installer Python
RUN powershell -Command \
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe -OutFile python.exe; \
    Start-Process python.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; \
    Remove-Item python.exe

# Copier les sources
COPY . /greaseweazle
WORKDIR /greaseweazle

# Installer les dépendances et compiler
RUN python -m pip install -U pip setuptools wheel cx_Freeze setuptools-scm
RUN set SETUPTOOLS_SCM_PRETEND_VERSION=1.23b && python -m pip install -e .
RUN cd scripts\win && python setup.py build
EOF
    
    print_info "Construction de l'image Docker..."
    docker build -f /tmp/Dockerfile.gw -t greaseweazle-build "$GW_SOURCE_DIR"
    
    print_info "Extraction des fichiers compilés..."
    docker create --name gw-temp greaseweazle-build
    docker cp gw-temp:/greaseweazle/scripts/win/build "$BUILD_OUTPUT_DIR/"
    docker rm gw-temp
    
    print_info "✅ Compilation terminée!"
}

# Exécuter la méthode sélectionnée
case $METHOD in
    wine)
        build_with_wine
        ;;
    pyinstaller)
        build_with_pyinstaller
        ;;
    nuitka)
        build_with_nuitka
        ;;
    docker)
        build_with_docker
        ;;
    *)
        print_error "Méthode inconnue: $METHOD"
        usage
        exit 1
        ;;
esac

print_section "Résultat"
print_info "Fichiers compilés disponibles dans: $BUILD_OUTPUT_DIR/greaseweazle-1.23b/"
print_info "Vous pouvez maintenant copier ces fichiers sur Windows"

