# Résolution du Problème Node.js dans WSL

## 🔴 Problème

Erreur lors de l'exécution de `npm run dev` :
```
/home/jean-fred/.nvm/versions/node/v24.12.0/bin/node: 1: Syntax error: ")" unexpected
```

## 🔍 Diagnostic

Le binaire Node.js est présent mais ne s'exécute pas correctement dans WSL. Cela peut être dû à :
- Binaire corrompu
- Problème de compatibilité WSL1/WSL2
- Problème avec nvm

## ✅ Solutions

### Solution 1 : Réinstaller Node.js via nvm

```bash
# Charger nvm
source ~/.nvm/nvm.sh

# Désinstaller la version actuelle
nvm uninstall v24.12.0

# Réinstaller Node.js LTS
nvm install --lts

# Utiliser la nouvelle version
nvm use --lts

# Vérifier
node --version
npm --version
```

### Solution 2 : Installer Node.js via le gestionnaire de paquets système

```bash
# Mettre à jour les paquets
sudo apt update

# Installer Node.js et npm
sudo apt install nodejs npm

# Vérifier
node --version
npm --version
```

### Solution 3 : Utiliser Node.js Windows (si disponible)

Si vous avez Node.js installé sur Windows, vous pouvez l'utiliser depuis WSL :

```bash
# Trouver le chemin Node.js Windows
/mnt/c/Program\ Files/nodejs/node.exe --version

# Créer un alias
alias node='/mnt/c/Program\ Files/nodejs/node.exe'
alias npm='/mnt/c/Program\ Files/nodejs/npm.cmd'
```

### Solution 4 : Tester le Backend Seul

En attendant de résoudre le problème Node.js, vous pouvez tester les améliorations via l'API :

```bash
# Démarrer le backend
cd /home/jean-fred/Aligntester/AlignTester
source venv/bin/activate
cd src/backend
python main.py

# Dans un autre terminal, tester l'API
curl http://localhost:8000/api/info
curl http://localhost:8000/api/status
```

## 🧪 Test du Parser Sans Frontend

Vous pouvez tester le parser directement en Python :

```bash
cd /home/jean-fred/Aligntester/AlignTester
source venv/bin/activate
cd src/backend

python -c "
from api.alignment_parser import AlignmentParser

parser = AlignmentParser()
test_output = '''T0.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)'''

values = parser.parse_output(test_output)
stats = parser.calculate_statistics(values)

print('Résultats:')
for v in stats['values']:
    print(f\"Piste {v['track']}: {v['percentage']:.2f}% (cohérence: {v.get('consistency', 'N/A')}, stabilité: {v.get('stability', 'N/A')})\")
"
```

## 📝 Recommandation

**Pour WSL**, je recommande la **Solution 2** (gestionnaire de paquets système) car :
- Plus stable dans WSL
- Mieux intégré avec le système
- Moins de problèmes de compatibilité

## 🔄 Après Installation

Une fois Node.js fonctionnel :

```bash
cd /home/jean-fred/Aligntester/AlignTester/src/frontend
npm install  # Si nécessaire
npm run dev
```

## 🆘 Si le Problème Persiste

1. Vérifier la version de WSL : `wsl --version` (Windows) ou `cat /proc/version` (WSL)
2. Vérifier l'architecture : `uname -m` (doit être x86_64)
3. Vérifier les permissions : `ls -la $(which node)`
4. Essayer avec un autre shell : `bash` au lieu de `zsh` ou vice versa

