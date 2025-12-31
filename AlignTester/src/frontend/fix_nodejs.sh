#!/bin/bash
# Script pour corriger l'installation de Node.js

echo "🔧 Correction de l'installation Node.js..."

# Désinstaller la version actuelle problématique
echo "📦 Désinstallation de Node.js v24.12.0..."
nvm uninstall 24.12.0 2>/dev/null || echo "Version déjà désinstallée ou non trouvée"

# Installer Node.js 20.x LTS (version stable)
echo "📥 Installation de Node.js 20.x LTS..."
nvm install 20

# Utiliser cette version
echo "✅ Activation de Node.js 20..."
nvm use 20

# Définir comme version par défaut
echo "🔗 Définition comme version par défaut..."
nvm alias default 20

# Vérifier l'installation
echo ""
echo "✅ Vérification de l'installation..."
echo "Version Node.js:"
node --version

echo ""
echo "Version npm:"
npm --version

echo ""
echo "✅ Installation terminée!"
echo "Vous pouvez maintenant exécuter: npm install"

