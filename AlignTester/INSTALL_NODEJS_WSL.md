# Installation de Node.js dans WSL/Debian

## Méthode 1 : Via apt (simple, version stable)

```bash
sudo apt update
sudo apt install -y nodejs npm
```

Vérifiez l'installation :
```bash
node --version
npm --version
```

**Note** : Cette méthode installe souvent une version plus ancienne de Node.js. Si vous avez besoin d'une version plus récente, utilisez la méthode 2.

## Méthode 2 : Via NodeSource (recommandé - version récente)

### Installation de Node.js 20.x (LTS)

```bash
# Télécharger et exécuter le script d'installation
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Installer Node.js
sudo apt install -y nodejs
```

Vérifiez l'installation :
```bash
node --version  # Devrait afficher v20.x.x
npm --version
```

## Méthode 3 : Via nvm (Node Version Manager - plus flexible)

### Installation de nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

Rechargez votre shell :
```bash
source ~/.bashrc
```

### Installation de Node.js via nvm

```bash
# Installer la dernière version LTS
nvm install --lts

# Utiliser cette version
nvm use --lts

# Vérifier
node --version
npm --version
```

## Après l'installation

Une fois Node.js installé, vous pouvez installer les dépendances du frontend :

```bash
cd ~/Aligntester/AlignTester/src/frontend
npm install
```

Puis démarrer le serveur de développement :

```bash
npm run dev
```

## Vérification

Pour vérifier que tout fonctionne :

```bash
node --version   # Devrait afficher v18.x.x ou supérieur
npm --version    # Devrait afficher 9.x.x ou supérieur
```

