# Prochaines Étapes - Configuration Git

## ✅ Ce qui a été fait

1. ✅ Git a été initialisé
2. ✅ L'identité Git a été configurée (Jean-Fred)
3. ✅ Le commit initial a été créé

## 🚀 Prochaines étapes pour utiliser GitHub Actions

### 1. Créer un dépôt sur GitHub

1. Allez sur https://github.com/new
2. Créez un nouveau dépôt (public ou privé)
3. **Ne cochez PAS** "Initialize with README" (le dépôt existe déjà localement)

### 2. Connecter le dépôt local à GitHub

```bash
# Remplacez VOTRE-USERNAME et VOTRE-REPO par vos valeurs
git remote add origin https://github.com/VOTRE-USERNAME/VOTRE-REPO.git
git branch -M main
git push -u origin main
```

### 3. Déclencher les builds multi-plateformes

#### Option A : Avec un tag (recommandé pour releases)

```bash
git tag v0.1.0
git push origin v0.1.0
```

#### Option B : Via l'interface GitHub

1. Allez dans l'onglet **Actions** de votre dépôt GitHub
2. Sélectionnez **Build Standalone**
3. Cliquez sur **Run workflow**
4. Sélectionnez la branche `main` et cliquez sur **Run workflow**

### 4. Télécharger les builds

1. Allez dans l'onglet **Actions**
2. Cliquez sur la dernière exécution du workflow
3. Téléchargez les **artifacts** pour chaque plateforme :
   - `aligntester-standalone-windows-x64`
   - `aligntester-standalone-linux-x64`
   - `aligntester-standalone-macos-x64`

## 📝 Configuration Git (si besoin de modifier)

### Pour ce dépôt uniquement

```bash
git config user.name "Votre Nom"
git config user.email "votre@email.com"
```

### Pour tous les dépôts (global)

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

## 🔧 Commandes utiles

```bash
# Voir l'état actuel
git status

# Voir l'historique
git log --oneline

# Voir les tags
git tag

# Créer un nouveau tag
git tag v0.2.0
git push origin v0.2.0
```

## 📦 Alternative : Builds locaux

Si vous ne voulez pas utiliser GitHub Actions, vous pouvez créer les builds localement :

```bash
# Build pour votre plateforme actuelle
./AlignTester/scripts/build_all_platforms.sh

# Ou manuellement
python AlignTester/scripts/build_standalone.py
```

Le build Linux est déjà disponible dans `build_standalone/dist/linux/aligntester/`

---

**Dernière mise à jour** : 2024
