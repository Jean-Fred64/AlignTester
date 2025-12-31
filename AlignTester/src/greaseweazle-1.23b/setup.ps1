# Script PowerShell pour compiler les routines optimisées de Greaseweazle sous Windows
# Usage: powershell -ExecutionPolicy Bypass -File .\setup.ps1

$ErrorActionPreference = "Stop"

# Couleurs
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

Write-Info "Compilation des routines optimisées de Greaseweazle sous Windows"
Write-Host ""

# Trouver le dossier source (où se trouve ce script)
$gwSourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$gwSourceDir = Resolve-Path $gwSourceDir

Write-Info "Dossier source: $gwSourceDir"
Write-Host ""

# Vérifier que setup.py existe
if (-not (Test-Path (Join-Path $gwSourceDir "setup.py"))) {
    Write-Error "setup.py introuvable dans: $gwSourceDir"
    exit 1
}

# Vérifier Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Error "Python non trouvé. Installez Python 3.8 ou supérieur."
        Write-Info "Téléchargez depuis: https://www.python.org/downloads/"
        exit 1
    }
    $pythonCmd = "py"
} else {
    $pythonCmd = "python"
}

$pythonVersion = & $pythonCmd --version 2>&1
Write-Info "Python: $pythonVersion"
Write-Host ""

# Vérifier le compilateur C/C++
$hasCompiler = $false
$compilerInfo = ""

# Vérifier Visual Studio Build Tools
$vsPaths = @(
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools",
    "${env:ProgramFiles}\Microsoft Visual Studio\2019\BuildTools",
    "${env:ProgramFiles}\Microsoft Visual Studio\2022\BuildTools"
)

foreach ($vsPath in $vsPaths) {
    if (Test-Path $vsPath) {
        $hasCompiler = $true
        $compilerInfo = "Visual Studio Build Tools trouvé: $vsPath"
        break
    }
}

# Vérifier MinGW si Visual Studio n'est pas trouvé
if (-not $hasCompiler) {
    $mingw = Get-Command gcc -ErrorAction SilentlyContinue
    if ($mingw) {
        $hasCompiler = $true
        $compilerInfo = "MinGW/GCC trouvé: $($mingw.Source)"
    }
}

if (-not $hasCompiler) {
    Write-Warn "Aucun compilateur C/C++ trouvé."
    Write-Host ""
    Write-Info "Pour compiler les routines optimisées, vous devez installer:"
    Write-Host "  1. Visual Studio Build Tools (recommandé):"
    Write-Host "     https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022"
    Write-Host "     Installez 'C++ build tools' dans les composants"
    Write-Host ""
    Write-Host "  2. Ou MinGW-w64:"
    Write-Host "     https://www.mingw-w64.org/downloads/"
    Write-Host ""
    Write-Warn "Sans compilateur, les routines optimisées ne peuvent pas être compilées."
    Write-Warn "Greaseweazle fonctionnera toujours, mais avec des performances réduites."
    Write-Host ""
    $response = Read-Host "Continuer quand même? (O/N)"
    if ($response -ne "O" -and $response -ne "o") {
        exit 1
    }
} else {
    Write-Info $compilerInfo
    Write-Host ""
}

# Installer les dépendances de build
Write-Info "Installation des dépendances de build..."
& $pythonCmd -m pip install -U pip setuptools wheel setuptools-scm | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Échec de l'installation des dépendances de build"
    exit 1
}

# Aller dans le dossier source
Set-Location $gwSourceDir

# Définir la version pour setuptools-scm
$env:SETUPTOOLS_SCM_PRETEND_VERSION = "1.23b"

# Nettoyer les anciens builds si nécessaire
if (Test-Path "build") {
    Write-Info "Nettoyage des anciens builds..."
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
    Get-ChildItem -Filter "*.egg-info" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

# Compiler et installer les extensions
Write-Info "Compilation des extensions C optimisées..."
Write-Host ""

# Essayer d'abord avec installation en mode développement
$buildOutput = & $pythonCmd -m pip install -e . --force-reinstall 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Échec avec -e, tentative avec installation normale..."
    $buildOutput = & $pythonCmd -m pip install . --force-reinstall 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Échec de la compilation"
        Write-Host ""
        Write-Host "Sortie de la compilation:" -ForegroundColor Yellow
        Write-Host $buildOutput
        exit 1
    }
}

Write-Host ""

# Vérifier que les routines optimisées sont disponibles
Write-Info "Vérification des routines optimisées..."
$testResult = & $pythonCmd -c "from greaseweazle.optimised import optimised; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0 -and $testResult -match "OK") {
    Write-Info "✅ Routines optimisées compilées et disponibles!"
} else {
    Write-Warn "⚠️  Les routines optimisées ne sont toujours pas disponibles"
    Write-Warn "Cela n'empêche pas l'utilisation de Greaseweazle, mais peut affecter les performances."
    if ($testResult) {
        Write-Host ""
        Write-Host "Sortie du test:" -ForegroundColor Yellow
        Write-Host $testResult
    }
}

Write-Host ""

# Afficher la version
if (Get-Command gw -ErrorAction SilentlyContinue) {
    Write-Info "Version Greaseweazle:"
    gw --version 2>&1 | Select-Object -First 5
} else {
    Write-Info "Pour utiliser gw, exécutez: $pythonCmd -m greaseweazle.cli"
}

Write-Host ""
Write-Info "✅ Compilation terminée!"

