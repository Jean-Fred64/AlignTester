#!/bin/bash
# Script pour connecter le device Greaseweazle à WSL via usbipd
# Usage: ./scripts/connect_greaseweazle_wsl.sh

set -e

echo "=== Connexion du device Greaseweazle à WSL ==="
echo ""

# Vérifier si usbip est installé
if ! command -v usbip &> /dev/null; then
    echo "❌ usbip n'est pas installé"
    echo ""
    echo "Installez-le avec:"
    echo "  sudo apt update"
    echo "  sudo apt install usbip hwdata"
    exit 1
fi

echo "✅ usbip est installé"
echo ""

# Instructions pour Windows
echo "📋 Étapes à suivre:"
echo ""
echo "1. Sur Windows, ouvrez PowerShell en tant qu'administrateur"
echo ""
echo "2. Installez usbipd si ce n'est pas déjà fait:"
echo "   winget install usbipd"
echo ""
echo "3. Listez les devices USB disponibles:"
echo "   usbipd list"
echo ""
echo "4. Trouvez votre device Greaseweazle dans la liste (recherchez 'Greaseweazle' ou 'COM10')"
echo ""
echo "5. Notez le BUSID (par exemple: 1-5)"
echo ""
echo "6. Attachez le device à WSL:"
echo "   usbipd attach --wsl --busid <BUSID>"
echo ""
echo "7. Revenez dans ce terminal et vérifiez:"
echo "   ls -la /dev/ttyACM*"
echo ""

# Vérifier si le device est déjà connecté
if ls /dev/ttyACM* &> /dev/null; then
    echo "✅ Device détecté:"
    ls -la /dev/ttyACM*
    echo ""
    echo "Vous pouvez maintenant utiliser:"
    echo "  gw info"
    echo "  gw align --device /dev/ttyACM0 --tracks c=40:h=0 --reads 10"
else
    echo "⚠️  Aucun device /dev/ttyACM* trouvé"
    echo ""
    echo "Assurez-vous d'avoir:"
    echo "  1. Exécuté 'usbipd attach --wsl --busid <BUSID>' sur Windows"
    echo "  2. Attendu quelques secondes pour que le device soit détecté"
fi

echo ""
echo "=== Pour détacher le device ==="
echo "Sur Windows (PowerShell admin):"
echo "  usbipd detach --busid <BUSID>"

