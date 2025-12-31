@echo off
REM Script batch pour compiler les routines optimisées de Greaseweazle sous Windows
REM Usage: .\scripts\setup.bat

echo [INFO] Compilation des routines optimisées de Greaseweazle sous Windows
echo.

REM Trouver le dossier source
set "SCRIPT_DIR=%~dp0"
set "GW_SOURCE_DIR=%SCRIPT_DIR%.."
cd /d "%GW_SOURCE_DIR%"

echo [INFO] Dossier source: %CD%
echo.

REM Vérifier que setup.py existe
if not exist "setup.py" (
    echo [ERROR] setup.py introuvable dans: %CD%
    exit /b 1
)

REM Vérifier Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python non trouvé. Installez Python 3.8 ou supérieur.
        echo [INFO] Téléchargez depuis: https://www.python.org/downloads/
        exit /b 1
    )
    set "PYTHON_CMD=py"
) else (
    set "PYTHON_CMD=python"
)

%PYTHON_CMD% --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Impossible d'exécuter Python
    exit /b 1
)

echo.

REM Installer les dépendances de build
echo [INFO] Installation des dépendances de build...
%PYTHON_CMD% -m pip install -U pip setuptools wheel setuptools-scm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Échec de l'installation des dépendances de build
    exit /b 1
)

REM Définir la version pour setuptools-scm
set "SETUPTOOLS_SCM_PRETEND_VERSION=1.23b"

REM Nettoyer les anciens builds si nécessaire
if exist "build" (
    echo [INFO] Nettoyage des anciens builds...
    rmdir /s /q build 2>nul
    rmdir /s /q dist 2>nul
    for /d %%d in (*.egg-info) do rmdir /s /q "%%d" 2>nul
)

REM Compiler et installer les extensions
echo [INFO] Compilation des extensions C optimisées...
echo.

%PYTHON_CMD% -m pip install -e . --force-reinstall
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Échec avec -e, tentative avec installation normale...
    %PYTHON_CMD% -m pip install . --force-reinstall
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Échec de la compilation
        exit /b 1
    )
)

echo.

REM Vérifier que les routines optimisées sont disponibles
echo [INFO] Vérification des routines optimisées...
%PYTHON_CMD% -c "from greaseweazle.optimised import optimised; print('OK')" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Routines optimisées compilées et disponibles!
) else (
    echo [WARN] Les routines optimisées ne sont toujours pas disponibles
    echo [WARN] Cela n'empêche pas l'utilisation de Greaseweazle, mais peut affecter les performances.
)

echo.
echo [INFO] Compilation terminée!

