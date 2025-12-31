#!/bin/bash
# Script de build pour Greaseweazle version 1.23b Windows
# Ce script doit être exécuté depuis WSL mais prépare le build Windows
# Usage: ./scripts/build_greaseweazle_windows.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GW_SOURCE_DIR="$PROJECT_ROOT/src/greaseweazle-1.23b"
BUILD_OUTPUT_DIR="$PROJECT_ROOT/build/greaseweazle-1.23b-windows"

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

# Vérifier qu'on est dans WSL
if [ ! -f /proc/version ] || ! grep -qi "microsoft\|wsl" /proc/version; then
    print_warn "Ce script est conçu pour WSL. Il prépare les fichiers pour build Windows."
fi

print_info "Préparation du build Windows pour Greaseweazle 1.23b"
print_info "Dossier source: $GW_SOURCE_DIR"

# Vérifier que le dossier source existe
if [ ! -d "$GW_SOURCE_DIR" ]; then
    print_error "Dossier source introuvable: $GW_SOURCE_DIR"
    exit 1
fi

# Vérifier que align.py est présent
if [ ! -f "$GW_SOURCE_DIR/src/greaseweazle/tools/align.py" ]; then
    print_error "align.py non trouvé dans les sources"
    exit 1
fi

# Vérifier que align est dans cli.py
if ! grep -q "'align'" "$GW_SOURCE_DIR/src/greaseweazle/cli.py"; then
    print_error "La commande 'align' n'est pas dans cli.py"
    exit 1
fi

print_info "✅ Sources vérifiées"

# Créer le dossier de sortie
mkdir -p "$BUILD_OUTPUT_DIR"

print_info ""
print_info "=== Instructions pour compiler sur Windows ==="
print_info ""
print_info "1. Ouvrez PowerShell en tant qu'administrateur sur Windows"
print_info "2. Naviguez vers le dossier source:"
print_info "   cd \"$GW_SOURCE_DIR\""
print_info ""
print_info "3. Installez les dépendances Python (si nécessaire):"
print_info "   python -m pip install -U pip setuptools wheel cx_Freeze setuptools-scm"
print_info ""
print_info "4. Compilez avec cx_Freeze:"
print_info "   cd scripts/win"
print_info "   python setup.py build"
print_info ""
print_info "5. Les fichiers compilés seront dans:"
print_info "   scripts/win/build/exe.win-amd64/"
print_info ""
print_info "6. Copiez les fichiers nécessaires:"
print_info "   - gw.exe"
print_info "   - Toutes les DLLs"
print_info "   - Le dossier greaseweazle.data/"
print_info ""
print_info "=== Alternative: Utiliser le Makefile ==="
print_info ""
print_info "Si vous avez Make installé (via WSL ou autre):"
print_info "   cd \"$GW_SOURCE_DIR\""
print_info "   make windist"
print_info ""
print_info "Cela créera un dossier greaseweazle-1.23b/ avec tous les fichiers"
print_info ""

# Créer un script PowerShell pour faciliter le build
cat > "$BUILD_OUTPUT_DIR/build_windows.ps1" << 'EOF'
# Script PowerShell pour compiler Greaseweazle 1.23b Windows
# Exécutez ce script dans PowerShell en tant qu'administrateur

$ErrorActionPreference = "Stop"

Write-Host "=== Build Greaseweazle 1.23b Windows ===" -ForegroundColor Green

# Vérifier Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python non trouvé. Installez Python 3.8 ou supérieur." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Python trouvé: $($python.Version)" -ForegroundColor Green

# Installer les dépendances
Write-Host "`nInstallation des dépendances..." -ForegroundColor Yellow
python -m pip install -U pip setuptools wheel cx_Freeze setuptools-scm

# Aller dans le dossier source
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceDir = Join-Path $scriptPath ".." ".." "src" "greaseweazle-1.23b"

if (-not (Test-Path $sourceDir)) {
    Write-Host "❌ Dossier source non trouvé: $sourceDir" -ForegroundColor Red
    exit 1
}

Set-Location $sourceDir

# Définir la version
$env:SETUPTOOLS_SCM_PRETEND_VERSION = "1.23b"

# Build avec cx_Freeze
Write-Host "`nCompilation avec cx_Freeze..." -ForegroundColor Yellow
Set-Location scripts\win
python setup.py build

Write-Host "`n✅ Build terminé!" -ForegroundColor Green
Write-Host "Les fichiers sont dans: scripts\win\build\exe.win-amd64\" -ForegroundColor Cyan
EOF

print_info "✅ Script PowerShell créé: $BUILD_OUTPUT_DIR/build_windows.ps1"
print_info ""
print_info "Pour compiler, exécutez sur Windows:"
print_info "  powershell -ExecutionPolicy Bypass -File \"$BUILD_OUTPUT_DIR/build_windows.ps1\""

