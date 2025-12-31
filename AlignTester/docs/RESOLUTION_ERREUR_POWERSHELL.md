# Résolution de l'erreur PowerShell

## 🔴 Problème

Erreur affichée :
```
Unable to find PowerShell! Do you have it installed? You can also configure custom installations with the 'powershell.powerShellAdditionalExePaths' setting.
```

## 🔍 Cause

L'extension PowerShell de VS Code/Cursor essaie de s'initialiser même sur Linux/WSL où PowerShell n'est pas disponible.

## ✅ Solutions appliquées

### 1. Configuration du terminal Linux

Le fichier `.vscode/settings.json` a été mis à jour pour :
- Utiliser bash comme terminal par défaut sur Linux
- Configurer le profil d'automatisation pour utiliser bash
- Désactiver toutes les fonctionnalités PowerShell

### 2. Désactivation de l'extension PowerShell

- Création de `.vscode/extensions.json` pour marquer PowerShell comme extension non recommandée
- Ajout de `extensions.disabled` dans `settings.json` pour désactiver l'extension dans ce workspace

## 🛠️ Si l'erreur persiste

### Méthode 1 : Désactiver manuellement l'extension (Recommandé)

1. **Ouvrir la palette de commandes** : `Ctrl+Shift+P` (ou `Cmd+Shift+P` sur Mac)
2. **Taper** : `Extensions: Show Installed Extensions`
3. **Chercher** : "PowerShell"
4. **Cliquer sur l'engrenage** ⚙️ à côté de l'extension PowerShell
5. **Sélectionner** : "Disable (Workspace)" ou "Disable"

### Méthode 2 : Désactiver via l'interface

1. **Ouvrir le panneau Extensions** : `Ctrl+Shift+X`
2. **Chercher** : "PowerShell"
3. **Cliquer sur "Disable"** pour ce workspace uniquement

### Méthode 3 : Réouvrir le projet depuis WSL

Si vous ouvrez le projet via un chemin UNC Windows (`\\wsl.localhost\...`), Cursor peut détecter l'environnement comme Windows.

**Solution** : Ouvrir depuis WSL directement :

```bash
# Dans un terminal WSL
cd ~/Aligntester
cursor .
```

## 📋 Vérifications

Après avoir désactivé l'extension :

1. **Redémarrer Cursor complètement**
2. **Vérifier que l'erreur a disparu** dans la sortie (Output)
3. **Tester le terminal** : Ouvrir un terminal intégré et vérifier qu'il utilise bash

## 🔧 Configuration actuelle

Le fichier `.vscode/settings.json` contient maintenant :

- ✅ Terminal Linux configuré pour bash
- ✅ Terminal Windows configuré pour WSL
- ✅ Toutes les fonctionnalités PowerShell désactivées
- ✅ Extension PowerShell désactivée dans le workspace

## 📝 Notes

- Ces configurations n'affectent que ce workspace spécifique
- Les autres projets ne seront pas affectés
- Si vous avez besoin de PowerShell pour d'autres projets, vous pouvez le réactiver globalement

---

**Date de résolution** : 31 décembre 2025
