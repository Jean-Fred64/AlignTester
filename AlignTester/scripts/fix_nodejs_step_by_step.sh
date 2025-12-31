#!/bin/bash
# Script pas à pas pour résoudre le problème Node.js dans WSL1

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "RÉSOLUTION DU PROBLÈME NODE.JS - ÉTAPE PAR ÉTAPE"
echo "=========================================="
echo ""

# ÉTAPE 1 : Désactiver nvm complètement
echo "ÉTAPE 1 : Désactivation de nvm..."
unset NVM_DIR
unset NVM_CD_FLAGS
unset NVM_BIN
unset NVM_NODEJS_ORG_MIRROR
unset NVM_IOJS_ORG_MIRROR

# Retirer nvm du PATH
export PATH=$(echo $PATH | tr ':' '\n' | grep -v nvm | tr '\n' ':' | sed 's/:$//')

echo "✓ nvm désactivé"
echo ""

# ÉTAPE 2 : Vérifier l'état actuel
echo "ÉTAPE 2 : Vérification de l'état actuel..."
echo "  Architecture système: $(uname -m)"
echo "  WSL Version: $(cat /proc/version | grep -o 'Microsoft' | head -1)"
echo "  Node.js installé: $(dpkg -l | grep -q '^ii.*nodejs' && echo 'Oui' || echo 'Non')"
echo "  npm installé: $(dpkg -l | grep -q '^ii.*npm' && echo 'Oui' || echo 'Non')"
echo ""

# ÉTAPE 3 : Nettoyer complètement
echo "ÉTAPE 3 : Nettoyage complet de Node.js et npm..."
echo "  ⚠️  Cette étape nécessite sudo"
echo "  Commande à exécuter :"
echo "  sudo apt remove --purge nodejs npm -y"
echo "  sudo apt autoremove -y"
echo ""

# ÉTAPE 4 : Réinstaller proprement
echo "ÉTAPE 4 : Réinstallation de Node.js et npm..."
echo "  ⚠️  Cette étape nécessite sudo"
echo "  Commande à exécuter :"
echo "  sudo apt update"
echo "  sudo apt install nodejs npm -y"
echo ""

# ÉTAPE 5 : Vérifier l'installation
echo "ÉTAPE 5 : Vérification de l'installation..."
echo "  Après installation, exécuter :"
echo "  /usr/bin/node --version"
echo "  /usr/bin/npm --version"
echo ""

# ÉTAPE 6 : Configurer le PATH
echo "ÉTAPE 6 : Configuration du PATH..."
echo "  Ajouter dans ~/.bashrc :"
echo "  export PATH=\"/usr/bin:\$PATH\""
echo ""

echo "=========================================="
echo "INSTRUCTIONS COMPLÈTES"
echo "=========================================="
echo ""
echo "1. Exécuter ce script pour voir les étapes"
echo "2. Suivre les commandes sudo indiquées"
echo "3. Valider chaque étape avant de passer à la suivante"
echo ""

