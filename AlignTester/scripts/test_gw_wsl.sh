#!/bin/bash
# Script de test pour utiliser gw.exe Windows depuis WSL

GW_EXE_WINDOWS="/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23/gw.exe"

echo "=== Test d'accès à gw.exe depuis WSL ==="
echo ""

# Vérifier si le fichier existe
if [ ! -f "$GW_EXE_WINDOWS" ]; then
    echo "❌ gw.exe non trouvé à: $GW_EXE_WINDOWS"
    echo ""
    echo "Vérifiez le chemin. Les chemins Windows sont accessibles via /mnt/<lettre>/"
    echo "Par exemple, S:\ devient /mnt/s/"
    exit 1
fi

echo "✅ gw.exe trouvé"
echo ""

# Tester la commande info
echo "=== Test: gw.exe info ==="
"$GW_EXE_WINDOWS" info

echo ""
echo "=== Test: gw.exe align --help ==="
"$GW_EXE_WINDOWS" align --help | head -30

echo ""
echo "=== Pour utiliser avec votre device COM10 ==="
echo "Commande:"
echo "  \"$GW_EXE_WINDOWS\" align --device COM10 --tracks c=40:h=0 --reads 10"

