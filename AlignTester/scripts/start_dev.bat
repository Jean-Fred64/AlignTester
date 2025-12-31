@echo off
REM Script de démarrage pour le développement AlignTester (Windows)

echo 🚀 Démarrage d'AlignTester en mode développement...
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "src\backend" (
    echo ❌ Erreur: Ce script doit être exécuté depuis le dossier AlignTester\
    exit /b 1
)

REM Démarrer le backend
echo 📡 Démarrage du backend FastAPI...
start "AlignTester Backend" cmd /k "cd src\backend && python main.py"

REM Attendre un peu
timeout /t 2 /nobreak >nul

REM Démarrer le frontend
echo 🎨 Démarrage du frontend React...
start "AlignTester Frontend" cmd /k "cd src\frontend && npm run dev"

echo.
echo ✅ Serveurs démarrés dans des fenêtres séparées!
echo    📡 Backend:  http://localhost:8000
echo    📚 API Docs: http://localhost:8000/docs
echo    🎨 Frontend: http://localhost:3000
echo.
echo 💡 Le mode manuel est disponible dans l'onglet 'Mode Manuel'
echo.
pause

