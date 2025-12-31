@echo off
REM Script de test rapide pour AlignTester (Windows)
REM Vérifie que le backend et le frontend sont accessibles

echo 🧪 Test de l'application AlignTester
echo.

REM Test 1: Backend Health Check
echo Test 1: Vérification du backend...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend accessible
    curl -s http://localhost:8000/api/health
) else (
    echo ❌ Backend non accessible
    echo    Assurez-vous que le backend est démarré: cd src\backend ^&^& python main.py
    exit /b 1
)
echo.
echo.

REM Test 2: Backend Info
echo Test 2: Informations Greaseweazle...
curl -s http://localhost:8000/api/info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Endpoint /api/info accessible
    curl -s http://localhost:8000/api/info
) else (
    echo ⚠️  Endpoint /api/info non accessible
)
echo.
echo.

REM Test 3: Backend Status
echo Test 3: Statut de l'alignement...
curl -s http://localhost:8000/api/status >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Endpoint /api/status accessible
    curl -s http://localhost:8000/api/status
) else (
    echo ⚠️  Endpoint /api/status non accessible
)
echo.
echo.

REM Test 4: Frontend
echo Test 4: Vérification du frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend accessible
    echo    Ouvrez http://localhost:3000 dans votre navigateur
) else (
    echo ⚠️  Frontend non accessible
    echo    Assurez-vous que le frontend est démarré: cd src\frontend ^&^& npm run dev
)
echo.
echo.

REM Test 5: WebSocket
echo Test 5: Test WebSocket...
echo ⚠️  Test WebSocket nécessite un outil spécialisé
echo    Pour tester manuellement, ouvrez la console du navigateur (F12)
echo    et vérifiez que 'WebSocket connecté' apparaît
echo.

echo ✅ Tests de base terminés!
echo.
echo 📝 Prochaines étapes:
echo    1. Ouvrez http://localhost:3000 dans votre navigateur
echo    2. Vérifiez que les informations Greaseweazle s'affichent
echo    3. Testez un alignement (si Greaseweazle est connecté)
echo    4. Consultez docs\GUIDE_TEST.md pour les tests détaillés
echo.
pause

