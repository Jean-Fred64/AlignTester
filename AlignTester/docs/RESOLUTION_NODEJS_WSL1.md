# Résolution du Problème Node.js dans WSL1 - Guide Pas à Pas

## 🔍 Diagnostic

- **Système** : WSL1 (Linux version 4.4.0-19041-Microsoft)
- **Architecture** : amd64 (x86_64)
- **Problème** : Les binaires Node.js ne s'exécutent pas (erreur "cannot execute binary file")
- **Cause probable** : Incompatibilité WSL1 ou binaires corrompus

## 📋 Plan d'Action - Étape par Étape

### ÉTAPE 1 : Désactiver nvm complètement

```bash
# Désactiver nvm
unset NVM_DIR
unset NVM_CD_FLAGS
unset NVM_BIN

# Retirer nvm du PATH temporairement
export PATH=$(echo $PATH | tr ':' '\n' | grep -v nvm | tr '\n' ':' | sed 's/:$//')

# Vérifier
which node
# Doit afficher /usr/bin/node (pas ~/.nvm/...)
```

**✅ Validation** : `which node` doit afficher `/usr/bin/node`

---

### ÉTAPE 2 : Nettoyer complètement Node.js et npm

**⚠️ Commande nécessitant sudo - À exécuter manuellement :**

```bash
# Supprimer complètement Node.js et npm
sudo apt remove --purge nodejs npm -y

# Nettoyer les dépendances inutiles
sudo apt autoremove -y

# Nettoyer le cache
sudo apt clean
```

**✅ Validation** : 
```bash
dpkg -l | grep -E "nodejs|npm"
# Ne doit rien afficher (ou seulement des packages liés, pas nodejs/npm)
```

---

### ÉTAPE 3 : Mettre à jour les dépôts

**⚠️ Commande nécessitant sudo - À exécuter manuellement :**

```bash
sudo apt update
```

**✅ Validation** : La commande doit se terminer sans erreur

---

### ÉTAPE 4 : Réinstaller Node.js et npm

**⚠️ Commande nécessitant sudo - À exécuter manuellement :**

```bash
sudo apt install nodejs npm -y
```

**✅ Validation** :
```bash
dpkg -l | grep -E "^ii.*nodejs|^ii.*npm"
# Doit afficher nodejs et npm installés
```

---

### ÉTAPE 5 : Tester le binaire directement

```bash
# Tester avec le chemin absolu
/usr/bin/node --version

# Si ça fonctionne, tester npm
/usr/bin/npm --version
```

**✅ Validation** : Les deux commandes doivent afficher des numéros de version

**❌ Si ça ne fonctionne pas** : Passer à l'ÉTAPE 6 (Solution alternative)

---

### ÉTAPE 6 : Solution Alternative - NodeSource (si apt ne fonctionne pas)

Si `/usr/bin/node --version` ne fonctionne toujours pas après réinstallation :

**⚠️ Commandes nécessitant sudo - À exécuter manuellement :**

```bash
# Installer Node.js 18.x LTS via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**✅ Validation** :
```bash
node --version
npm --version
```

---

### ÉTAPE 7 : Configurer le PATH définitivement

Une fois que Node.js fonctionne, ajouter dans `~/.bashrc` :

```bash
# Ajouter en fin de fichier
export PATH="/usr/bin:$PATH"

# Désactiver nvm au démarrage (optionnel)
# Commenter ou supprimer les lignes qui chargent nvm
```

Puis recharger :
```bash
source ~/.bashrc
```

**✅ Validation** :
```bash
which node
# Doit afficher /usr/bin/node
node --version
# Doit fonctionner
```

---

### ÉTAPE 8 : Tester avec le projet

```bash
cd /home/jean-fred/Aligntester/AlignTester/src/frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
```

**✅ Validation** : Le serveur doit démarrer et afficher une URL (ex: http://localhost:5173)

---

## 🐛 Dépannage

### Problème : "cannot execute binary file" persiste

**Solution 1** : Vérifier l'interpréteur dynamique
```bash
readelf -l /usr/bin/node | grep interpreter
# Doit afficher : [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
```

**Solution 2** : Vérifier que les bibliothèques sont présentes
```bash
ldd /usr/bin/node
# Toutes les bibliothèques doivent être résolues (pas de "not found")
```

**Solution 3** : Utiliser NodeSource (ÉTAPE 6)

### Problème : nvm se réactive automatiquement

**Solution** : Modifier `~/.bashrc` ou `~/.zshrc` pour commenter les lignes nvm :
```bash
# Commenter ces lignes :
# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

---

## ✅ Checklist de Validation

- [ ] ÉTAPE 1 : nvm désactivé, `which node` = `/usr/bin/node`
- [ ] ÉTAPE 2 : Node.js et npm complètement supprimés
- [ ] ÉTAPE 3 : `apt update` réussi
- [ ] ÉTAPE 4 : Node.js et npm réinstallés
- [ ] ÉTAPE 5 : `/usr/bin/node --version` fonctionne
- [ ] ÉTAPE 6 : (Si nécessaire) NodeSource installé
- [ ] ÉTAPE 7 : PATH configuré, `node --version` fonctionne
- [ ] ÉTAPE 8 : `npm run dev` démarre le frontend

---

## 📝 Notes

- **WSL1** a des limitations connues avec certains binaires
- Si le problème persiste après toutes ces étapes, considérer une migration vers **WSL2**
- Les binaires Node.js doivent être compilés pour Linux x86_64, pas Windows

---

**Dernière mise à jour** : Guide créé pour résolution méthodique

