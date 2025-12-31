# Guide Utilisateur - AlignTester Standalone

## 📥 Installation

### Windows

1. Téléchargez `aligntester-standalone-windows-x64.zip`
2. Extrayez l'archive dans un dossier de votre choix (ex: `C:\Program Files\AlignTester\`)
3. Double-cliquez sur `aligntester.exe`
4. Le navigateur s'ouvrira automatiquement sur http://127.0.0.1:8000

### Linux

1. Téléchargez `aligntester-standalone-linux-x64.zip`
2. Extrayez l'archive :
   ```bash
   unzip aligntester-standalone-linux-x64.zip
   cd aligntester
   ```
3. Rendez l'exécutable... exécutable :
   ```bash
   chmod +x aligntester
   ```
4. Lancez l'application :
   ```bash
   ./aligntester
   ```
5. Le navigateur s'ouvrira automatiquement sur http://127.0.0.1:8000

### macOS

1. Téléchargez `aligntester-standalone-macos-x64.zip`
2. Extrayez l'archive :
   ```bash
   unzip aligntester-standalone-macos-x64.zip
   cd aligntester
   ```
3. Rendez l'exécutable... exécutable :
   ```bash
   chmod +x aligntester
   ```
4. Lancez l'application :
   ```bash
   ./aligntester
   ```
5. Le navigateur s'ouvrira automatiquement sur http://127.0.0.1:8000

**Note macOS** : Si macOS vous demande de confirmer l'exécution, allez dans :
- **Préférences Système** > **Sécurité et confidentialité** > Autoriser l'exécution

## 🚀 Utilisation

### Première utilisation

1. **Connectez votre Greaseweazle** à votre ordinateur via USB
2. **Lancez AlignTester** (double-clic sur l'exécutable)
3. **Attendez** que le navigateur s'ouvre automatiquement
4. Si le navigateur ne s'ouvre pas, ouvrez manuellement : http://127.0.0.1:8000

### Interface

L'interface web vous permet de :
- ✅ Détecter automatiquement votre Greaseweazle
- ✅ Configurer les paramètres d'alignement
- ✅ Lancer des tests d'alignement
- ✅ Visualiser les résultats en temps réel
- ✅ Sauvegarder et charger des configurations

### Arrêt de l'application

- **Windows** : Fermez la fenêtre de console ou utilisez Ctrl+C
- **Linux/macOS** : Utilisez Ctrl+C dans le terminal, ou fermez la fenêtre de terminal

## 🔧 Dépannage

### Le navigateur ne s'ouvre pas automatiquement

**Solution** : Ouvrez manuellement votre navigateur et allez sur :
- http://127.0.0.1:8000
- Ou regardez dans la console pour voir quel port est utilisé

### Le port 8000 est déjà utilisé

**Solution** : L'application utilisera automatiquement un autre port (8001, 8002, etc.)
Regardez le message dans la console pour connaître le port utilisé.

### Greaseweazle non détecté

**Vérifications** :
1. ✅ Le Greaseweazle est bien connecté via USB
2. ✅ Les drivers USB sont installés
3. ✅ Sur Linux : Vérifiez les permissions USB :
   ```bash
   # Ajouter votre utilisateur au groupe dialout
   sudo usermod -a -G dialout $USER
   # Puis déconnectez/reconnectez-vous
   ```
4. ✅ Sur macOS : Vérifiez les permissions dans **Préférences Système** > **Sécurité et confidentialité**

### Erreur "Permission denied" (Linux/macOS)

**Solution** :
```bash
chmod +x aligntester
```

### L'application ne démarre pas

**Vérifications** :
1. ✅ Tous les fichiers sont présents dans le dossier
2. ✅ Vous avez les permissions d'exécution
3. ✅ Regardez les messages d'erreur dans la console

### Antivirus bloque l'application (Windows)

**Solution** : C'est un faux positif connu avec PyInstaller. Ajoutez une exception dans votre antivirus pour le dossier AlignTester.

## 📋 Prérequis système

### Windows
- Windows 10 ou supérieur
- Greaseweazle installé et configuré
- Navigateur web moderne (Chrome, Firefox, Edge)

### Linux
- Distribution Linux récente (Ubuntu 20.04+, Debian 11+, etc.)
- Greaseweazle installé et configuré
- Navigateur web moderne
- Permissions USB (voir ci-dessus)

### macOS
- macOS 10.15 (Catalina) ou supérieur
- Greaseweazle installé et configuré
- Navigateur web moderne

## 📚 Besoin d'aide ?

- **Documentation complète** : Voir `README_STANDALONE.txt` dans le dossier
- **GitHub** : https://github.com/votre-repo/aligntester
- **Issues** : Signalez les problèmes sur GitHub

## 🔄 Mise à jour

Pour mettre à jour AlignTester :
1. Téléchargez la nouvelle version
2. Arrêtez l'ancienne version
3. Remplacez les fichiers par les nouveaux
4. Relancez l'application

---

**Version** : 0.1.0  
**Dernière mise à jour** : 2024
