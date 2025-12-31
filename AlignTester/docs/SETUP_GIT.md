# Configuration Git pour les Builds Multi-Plateformes

Si vous voulez utiliser GitHub Actions pour créer automatiquement les builds pour Windows, Linux et macOS, vous devez initialiser un dépôt Git.

## 🚀 Configuration rapide

### 1. Initialiser Git (si pas déjà fait)

```bash
cd /home/jean-fred/Aligntester
git init
git add .
git commit -m "Initial commit - AlignTester avec builds standalone"
```

### 2. Créer un dépôt sur GitHub

1. Allez sur https://github.com/new
2. Créez un nouveau dépôt (public ou privé)
3. **Ne cochez PAS** "Initialize with README" (le dépôt existe déjà)

### 3. Connecter le dépôt local à GitHub

```bash
git remote add origin https://github.com/VOTRE-USERNAME/VOTRE-REPO.git
git branch -M main
git push -u origin main
```

### 4. Déclencher les builds

#### Option A : Avec un tag (recommandé pour releases)

```bash
git tag v0.1.0
git push origin v0.1.0
```

#### Option B : Via l'interface GitHub

1. Allez dans l'onglet **Actions** de votre dépôt GitHub
2. Sélectionnez **Build Standalone**
3. Cliquez sur **Run workflow**
4. Sélectionnez la branche et cliquez sur **Run workflow**

### 5. Télécharger les builds

1. Allez dans l'onglet **Actions**
2. Cliquez sur la dernière exécution du workflow
3. Téléchargez les **artifacts** pour chaque plateforme :
   - `aligntester-standalone-windows-x64`
   - `aligntester-standalone-linux-x64`
   - `aligntester-standalone-macos-x64`

## 📦 Alternative : Builds locaux

Si vous ne voulez pas utiliser GitHub Actions, vous pouvez :

### Build local pour votre plateforme

```bash
# Utiliser le script automatique
./AlignTester/scripts/build_all_platforms.sh

# Ou manuellement
python AlignTester/scripts/build_standalone.py
```

### Builds pour autres plateformes

- **Windows** : Utilisez WSL2, une VM Windows, ou une machine Windows physique
- **macOS** : Utilisez une VM macOS ou une machine Mac physique

## 🔧 Dépannage

### Erreur : "not a git repository"

Vous devez initialiser Git (voir étape 1 ci-dessus).

### Erreur : "remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/VOTRE-USERNAME/VOTRE-REPO.git
```

### Les builds ne se déclenchent pas

1. Vérifiez que le fichier `.github/workflows/build-standalone.yml` existe
2. Vérifiez que vous avez bien poussé le code sur GitHub
3. Vérifiez les logs dans l'onglet Actions

## 📝 Notes

- Les builds GitHub Actions sont **gratuits** pour les repos publics
- Les artifacts sont conservés **30 jours**
- Pour une conservation permanente, créez une **release GitHub**

---

**Dernière mise à jour** : 2024
