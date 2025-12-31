# Correction de nvm pour x86_64

## Problème
Même avec une architecture x86_64, nvm a peut-être installé une version incompatible.

## Solution : Réinstaller avec version explicite x64

### 1. Désinstaller la version actuelle

```bash
nvm uninstall 24.12.0
```

### 2. Installer une version LTS stable (20.x) explicitement pour x64

```bash
nvm install 20.11.0
nvm use 20.11.0
```

### 3. Vérifier

```bash
node --version
npm --version
```

### 4. Si ça ne fonctionne toujours pas, essayer Node.js 18.x

```bash
nvm install 18.20.0
nvm use 18.20.0
node --version
```

### 5. Alternative : Réinstaller nvm complètement

Si le problème persiste :

```bash
# Supprimer nvm
rm -rf ~/.nvm

# Réinstaller nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# Installer Node.js 20 LTS
nvm install 20
nvm use 20
```

