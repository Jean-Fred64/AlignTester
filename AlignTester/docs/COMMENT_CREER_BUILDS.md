# Comment Créer les Builds Standalone

Ce guide explique étape par étape comment créer les builds standalone et les voir dans GitHub Actions.

## 🎯 Méthode 1 : Via GitHub Actions (Recommandé)

### Étape 1 : Vérifier que le workflow est sur GitHub

1. Allez sur votre dépôt GitHub
2. Vérifiez que le fichier `.github/workflows/build-standalone.yml` existe
3. Si ce n'est pas le cas, poussez le code :
   ```bash
   git add .github/workflows/build-standalone.yml
   git commit -m "Ajout workflow GitHub Actions pour builds standalone"
   git push origin main
   ```

### Étape 2 : Déclencher le workflow

Vous avez **3 options** pour déclencher le workflow :

#### Option A : Déclenchement manuel (le plus simple)

1. Allez sur votre dépôt GitHub
2. Cliquez sur l'onglet **"Actions"** (en haut de la page)
3. Dans le menu de gauche, sélectionnez **"Build Standalone"**
4. Cliquez sur le bouton **"Run workflow"** (en haut à droite)
5. Sélectionnez la branche `main` (ou `master`)
6. Cliquez sur **"Run workflow"** (bouton vert)

Le workflow va alors créer les builds pour Windows, Linux et macOS en parallèle.

#### Option B : Avec un tag (pour les releases)

```bash
# Créer un tag
git tag v0.1.0

# Pousser le tag sur GitHub
git push origin v0.1.0
```

Le workflow se déclenchera automatiquement.

#### Option C : Créer une release GitHub

1. Allez sur votre dépôt GitHub
2. Cliquez sur **"Releases"** (à droite)
3. Cliquez sur **"Create a new release"**
4. Créez un tag (ex: `v0.1.0`)
5. Cliquez sur **"Publish release"**

Le workflow se déclenchera automatiquement.

### Étape 3 : Voir les builds en cours

1. Allez dans l'onglet **"Actions"**
2. Vous verrez une nouvelle exécution du workflow **"Build Standalone"**
3. Cliquez dessus pour voir la progression
4. Vous verrez 3 jobs en parallèle :
   - `build (ubuntu-latest)` - Build Linux
   - `build (windows-latest)` - Build Windows
   - `build (macos-latest)` - Build macOS

### Étape 4 : Télécharger les builds (Artifacts)

Une fois que tous les jobs sont terminés (coches vertes ✓) :

1. Cliquez sur l'exécution du workflow terminée
2. Faites défiler jusqu'en bas de la page
3. Vous verrez une section **"Artifacts"** avec 3 fichiers :
   - `aligntester-standalone-linux-x64`
   - `aligntester-standalone-windows-x64`
   - `aligntester-standalone-macos-x64`
4. Cliquez sur chaque artifact pour le télécharger

**Note** : Les artifacts sont des fichiers ZIP contenant les builds complets.

## 🔍 Dépannage

### Le workflow n'apparaît pas dans Actions

**Problème** : Le fichier `.github/workflows/build-standalone.yml` n'est pas sur GitHub.

**Solution** :
```bash
# Vérifier que le fichier existe localement
ls -la .github/workflows/build-standalone.yml

# Si oui, pousser sur GitHub
git add .github/workflows/build-standalone.yml
git commit -m "Ajout workflow builds standalone"
git push origin main
```

### Le workflow échoue

1. Cliquez sur l'exécution qui a échoué
2. Cliquez sur le job qui a échoué (il sera marqué en rouge)
3. Regardez les logs pour voir l'erreur
4. Erreurs communes :
   - **Erreur npm** : Vérifiez que `package-lock.json` existe dans `AlignTester/src/frontend/`
   - **Erreur Python** : Vérifiez que `requirements.txt` est à jour
   - **Erreur PyInstaller** : Vérifiez que toutes les dépendances sont dans `requirements.txt`

### Les artifacts n'apparaissent pas

**Vérifications** :
1. Le workflow doit être **terminé avec succès** (tous les jobs verts)
2. Les artifacts sont créés à la fin du workflow
3. Si un job échoue, les artifacts ne seront pas créés pour cette plateforme
4. Les artifacts sont conservés **30 jours** par défaut

### Le workflow ne se déclenche pas automatiquement

Le workflow se déclenche uniquement pour :
- Les tags `v*` (ex: `v0.1.0`, `v1.0.0`)
- Les releases GitHub
- Le déclenchement manuel (`workflow_dispatch`)

Pour un push normal, le workflow **ne se déclenche pas**. Utilisez le déclenchement manuel.

## 🚀 Méthode 2 : Build Local

Si vous voulez créer un build localement (pour votre plateforme uniquement) :

```bash
# Installer les dépendances
pip install -r AlignTester/requirements.txt

# Builder le frontend
cd AlignTester/src/frontend
npm install
npm run build
cd ../../..

# Créer le build standalone
python AlignTester/scripts/build_standalone.py
```

Le build sera dans `build_standalone/dist/[plateforme]/aligntester/`

## 📋 Résumé des étapes

1. ✅ Vérifier que `.github/workflows/build-standalone.yml` est sur GitHub
2. ✅ Aller dans l'onglet **Actions**
3. ✅ Sélectionner **"Build Standalone"**
4. ✅ Cliquer sur **"Run workflow"**
5. ✅ Attendre la fin des builds (5-10 minutes)
6. ✅ Télécharger les artifacts en bas de la page

## 🎯 Exemple de workflow réussi

Quand tout fonctionne, vous verrez :

```
Actions > Build Standalone > [Dernière exécution]
├── build (ubuntu-latest) ✓ (5 min 23s)
├── build (windows-latest) ✓ (6 min 45s)
└── build (macos-latest) ✓ (7 min 12s)

Artifacts:
├── aligntester-standalone-linux-x64 (85.2 MB)
├── aligntester-standalone-windows-x64 (92.1 MB)
└── aligntester-standalone-macos-x64 (88.7 MB)
```

---

**Besoin d'aide ?** Vérifiez les logs dans l'onglet Actions pour voir les erreurs détaillées.
