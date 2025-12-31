#!/bin/bash
# Script pour corriger le PATH Node.js et désactiver nvm temporairement

# Désactiver nvm
unset NVM_DIR
unset NVM_CD_FLAGS
unset NVM_BIN

# Utiliser la version système de Node.js
export PATH="/usr/bin:/usr/local/bin:$PATH"

# Réinitialiser le cache des commandes
hash -r

echo "✓ nvm désactivé"
echo "✓ Utilisation de Node.js système"
echo ""
echo "Vérification:"
node --version
npm --version

