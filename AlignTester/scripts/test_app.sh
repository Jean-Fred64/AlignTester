#!/bin/bash
# Script de test rapide pour AlignTester
# Vérifie que le backend et le frontend sont accessibles

echo "🧪 Test de l'application AlignTester"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend Health Check
echo "Test 1: Vérification du backend..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend accessible${NC}"
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
    echo "   Réponse: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Backend non accessible${NC}"
    echo "   Assurez-vous que le backend est démarré: cd src/backend && python main.py"
    exit 1
fi
echo ""

# Test 2: Backend Info
echo "Test 2: Informations Greaseweazle..."
if curl -s http://localhost:8000/api/info > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Endpoint /api/info accessible${NC}"
    INFO_RESPONSE=$(curl -s http://localhost:8000/api/info | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/info)
    echo "   Réponse: $INFO_RESPONSE"
else
    echo -e "${YELLOW}⚠️  Endpoint /api/info non accessible${NC}"
fi
echo ""

# Test 3: Backend Status
echo "Test 3: Statut de l'alignement..."
if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Endpoint /api/status accessible${NC}"
    STATUS_RESPONSE=$(curl -s http://localhost:8000/api/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/status)
    echo "   Réponse: $STATUS_RESPONSE"
else
    echo -e "${YELLOW}⚠️  Endpoint /api/status non accessible${NC}"
fi
echo ""

# Test 4: Frontend
echo "Test 4: Vérification du frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend accessible${NC}"
    echo "   Ouvrez http://localhost:3000 dans votre navigateur"
else
    echo -e "${YELLOW}⚠️  Frontend non accessible${NC}"
    echo "   Assurez-vous que le frontend est démarré: cd src/frontend && npm run dev"
fi
echo ""

# Test 5: WebSocket (test basique)
echo "Test 5: Test WebSocket..."
# Note: Ce test nécessite un outil spécialisé comme websocat ou wscat
echo -e "${YELLOW}⚠️  Test WebSocket nécessite un outil spécialisé${NC}"
echo "   Pour tester manuellement, ouvrez la console du navigateur (F12)"
echo "   et vérifiez que 'WebSocket connecté' apparaît"
echo ""

echo "✅ Tests de base terminés!"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Ouvrez http://localhost:3000 dans votre navigateur"
echo "   2. Vérifiez que les informations Greaseweazle s'affichent"
echo "   3. Testez un alignement (si Greaseweazle est connecté)"
echo "   4. Consultez docs/GUIDE_TEST.md pour les tests détaillés"

