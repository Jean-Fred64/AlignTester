# Diagnostic Terminal - Comparaison Projets

**Date :** 21 décembre 2025  
**Projet fonctionnel :** Pauline (`/home/jean-fred/Pauline`)  
**Projet à diagnostiquer :** Aligntester (`/home/jean-fred/Aligntester`)

---

## 🔍 Analyse Comparative

### Environnement Fonctionnel (Pauline)

D'après `RAPPORT_DIAGNOSTIC_TERMINAL.md` :

- ✅ **Répertoire** : `/home/jean-fred/Pauline`
- ✅ **Permissions** : `drwxr-xr-x` (755)
- ✅ **Shell** : `bash 5.2.15`
- ✅ **PATH** : Complet avec chemins Cursor (`/home/jean-fred/.cursor-server/bin/...`)
- ✅ **Variables** : HOME, USER, SHELL, PATH, TERM toutes présentes
- ✅ **Terminal Cursor AI** : Fonctionnel

### Environnement Problématique (Aligntester)

- ⚠️ **Répertoire** : `/home/jean-fred/Aligntester` (même structure)
- ⚠️ **Chemin workspace** : `\\wsl.localhost\Debian\home\jean-fred\Aligntester` (UNC)
- ⚠️ **Configuration** : `.vscode/settings.json` avec `terminal.integrated.automationProfile.windows`
- ❌ **Terminal Cursor AI** : Échec - tente d'utiliser PowerShell (ENOENT)

---

## 🎯 Différences Identifiées

### 1. Méthode d'ouverture du workspace

**Pauline (fonctionnel)** :
- Probablement ouvert depuis WSL directement ou via chemin Linux normal
- Pas de chemin UNC Windows visible dans le rapport

**Aligntester (problématique)** :
- Ouvert via chemin UNC Windows : `\\wsl.localhost\Debian\...`
- Cursor détecte probablement cela comme un workspace Windows

### 2. Configuration .vscode/settings.json

**Aligntester a** :
- `terminal.integrated.defaultProfile.windows`: "WSL"
- `terminal.integrated.automationProfile.windows`: configuré avec WSL
- Cela pourrait interférer avec la détection automatique

**Pauline (probable)** :
- Pas de configuration forcée, utilisation des paramètres par défaut de Cursor
- Ou configuration plus simple

### 3. Chemin du workspace

Le chemin UNC `\\wsl.localhost\...` pourrait faire que :
- Cursor pense que le workspace est "Windows"
- Les outils automatisés utilisent PowerShell au lieu de WSL
- Le `automationProfile` n'est pas pris en compte correctement

---

## 🔧 Solutions Proposées

### Solution 1 : Ouvrir le projet depuis WSL (Recommandé)

Au lieu d'ouvrir via `\\wsl.localhost\...`, ouvrir depuis WSL directement :

```bash
# Depuis un terminal WSL
cd ~/Aligntester
code .  # ou cursor .
```

**Avantages** :
- Cursor détecte automatiquement WSL comme environnement
- Les outils automatisés utilisent WSL directement
- Même comportement que le projet Pauline

### Solution 2 : Simplifier .vscode/settings.json

Retirer la configuration `automationProfile` qui pourrait interférer :

```json
{
  "files.eol": "\n"
  // Retirer toute configuration terminal
}
```

Laissez Cursor détecter automatiquement l'environnement.

### Solution 3 : Utiliser un chemin Windows mappé

Si vous devez absolument ouvrir depuis Windows, mapper le chemin WSL :

Dans PowerShell Windows :
```powershell
# Créer un lien symbolique ou mapper le réseau
# Puis ouvrir Cursor depuis le chemin mappé
```

**Note** : Moins recommandé, peut causer des problèmes de permissions.

---

## 📋 Script de Diagnostic

Un script de diagnostic a été créé : `AlignTester/scripts/diagnose_terminal.sh`

### Utilisation :

```bash
cd ~/Aligntester/AlignTester
bash scripts/diagnose_terminal.sh > diagnostic_aligntester.txt
```

### Comparer avec le projet fonctionnel :

```bash
cd ~/Pauline
# Exécuter les mêmes commandes de diagnostic
# Comparer les sorties
```

---

## 🔬 Tests à Effectuer Manuellement

### Test 1 : Vérifier l'environnement de base

Dans votre terminal Cursor (manuel) :

```bash
echo "=== Test Environnement ==="
pwd
uname -a
whoami
echo "HOME=$HOME"
echo "USER=$USER"
echo "SHELL=$SHELL"
echo "PATH=$PATH"
```

**Comparer avec le rapport Pauline** : Les valeurs doivent être similaires.

### Test 2 : Vérifier les permissions

```bash
ls -ld ~/Aligntester
ls -ld ~/Pauline
```

**Comparer** : Les permissions doivent être identiques (`drwxr-xr-x`).

### Test 3 : Vérifier bash

```bash
which bash
bash --version
test -x $(which bash) && echo "OK" || echo "PROBLÈME"
```

**Comparer** : Même version et même exécutabilité.

---

## 🎯 Hypothèse Principale

**Le problème vient probablement de la méthode d'ouverture du workspace :**

1. **Projet Pauline** : Ouvrt depuis WSL → Cursor détecte WSL → Terminal fonctionne
2. **Projet Aligntester** : Ouvrt via UNC Windows → Cursor pense "Windows" → Tente PowerShell → Échec

**Solution la plus simple** : Réouvrir Aligntester depuis WSL :

```bash
# Dans un terminal WSL
cd ~/Aligntester
cursor .
# Ou depuis le menu Cursor : File > Open Folder > Naviguer vers /home/jean-fred/Aligntester
```

---

## 📝 Actions Recommandées

1. ✅ **Fermer complètement Cursor**
2. ✅ **Ouvrir un terminal WSL** (depuis Windows ou directement)
3. ✅ **Naviguer vers le projet** : `cd ~/Aligntester`
4. ✅ **Ouvrir avec Cursor** : `cursor .`
5. ✅ **Tester les outils de terminal AI** dans le nouveau workspace
6. ✅ **Si ça fonctionne** : Comparer les chemins de workspace pour confirmer l'hypothèse

---

## 🔍 Vérifications Supplémentaires

### Si la solution 1 ne fonctionne pas :

1. **Comparer les fichiers .vscode/settings.json** :
   ```bash
   diff ~/Pauline/.vscode/settings.json ~/Aligntester/.vscode/settings.json
   ```

2. **Vérifier les extensions Cursor** :
   - S'assurer que les mêmes extensions sont installées
   - Vérifier qu'aucune extension ne force PowerShell

3. **Vérifier les paramètres utilisateur Cursor** :
   - Comparer `settings.json` utilisateur entre les deux projets
   - Vérifier s'il y a des différences

---

## ✅ Checklist de Résolution

- [ ] Fermer complètement Cursor
- [ ] Ouvrir le projet depuis WSL (`cursor .` depuis `~/Aligntester`)
- [ ] Vérifier que le terminal manuel fonctionne
- [ ] Tester les outils de terminal AI
- [ ] Si échec : Exécuter `diagnose_terminal.sh` et comparer avec Pauline
- [ ] Si échec : Simplifier `.vscode/settings.json`
- [ ] Si échec : Comparer toutes les configurations entre les deux projets

---

**Note** : Ce diagnostic est basé sur l'hypothèse que le projet Pauline fonctionne correctement. Si les outils de terminal AI fonctionnent après réouverture depuis WSL, cela confirmera que le problème vient de la méthode d'ouverture du workspace.

