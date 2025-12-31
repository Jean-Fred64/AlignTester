# Guide Rapide - Créer les Builds Standalone

## 🚀 En 3 étapes simples

### 1. Vérifier que le workflow est sur GitHub

```bash
# Vérifier que le fichier existe
ls -la .github/workflows/build-standalone.yml

# Si vous avez fait des changements, pousser sur GitHub
git add .github/workflows/build-standalone.yml
git commit -m "Workflow builds standalone"
git push origin main
```

### 2. Déclencher le workflow sur GitHub

1. **Allez sur votre dépôt GitHub** (ex: `https://github.com/VOTRE-USERNAME/VOTRE-REPO`)
2. **Cliquez sur l'onglet "Actions"** (en haut de la page)
3. **Dans le menu de gauche**, cliquez sur **"Build Standalone"**
4. **Cliquez sur "Run workflow"** (bouton en haut à droite)
5. **Sélectionnez la branche** `main` (ou `master`)
6. **Cliquez sur "Run workflow"** (bouton vert)

### 3. Télécharger les builds

**Attendez 5-10 minutes** que les builds se terminent, puis :

1. **Cliquez sur l'exécution terminée** (coches vertes ✓)
2. **Faites défiler jusqu'en bas** de la page
3. **Section "Artifacts"** : vous verrez 3 fichiers ZIP
4. **Cliquez sur chaque fichier** pour le télécharger :
   - `aligntester-standalone-linux-x64.zip`
   - `aligntester-standalone-windows-x64.zip`
   - `aligntester-standalone-macos-x64.zip`

## ⚠️ Problèmes courants

### "Je ne vois pas l'onglet Actions"

- Vérifiez que vous êtes sur votre dépôt GitHub (pas en local)
- L'onglet "Actions" est en haut de la page, à côté de "Code", "Issues", etc.

### "Je ne vois pas 'Build Standalone' dans le menu"

- Le workflow n'a peut-être pas été poussé sur GitHub
- Vérifiez : `git push origin main`
- Attendez quelques secondes et rafraîchissez la page

### "Le workflow échoue"

- Cliquez sur l'exécution qui a échoué
- Cliquez sur le job en rouge
- Regardez les logs pour voir l'erreur
- Erreurs communes : dépendances manquantes, erreurs de build frontend

### "Je ne vois pas les Artifacts"

- Les artifacts n'apparaissent qu'**après** la fin du workflow
- Tous les jobs doivent être **verts** (✓)
- Si un job échoue, les artifacts ne seront pas créés pour cette plateforme
- Les artifacts sont en **bas de la page** de l'exécution

## 📸 À quoi ça ressemble

```
GitHub Repository
├── Code
├── Issues
├── Actions  ← Cliquez ici
│   └── Build Standalone  ← Cliquez ici
│       └── Run workflow  ← Cliquez ici
│           └── [Sélectionnez main] → Run workflow
│
└── [Après 5-10 min]
    └── [Exécution terminée]
        └── Artifacts (en bas)
            ├── aligntester-standalone-linux-x64.zip
            ├── aligntester-standalone-windows-x64.zip
            └── aligntester-standalone-macos-x64.zip
```

## 🎯 Alternative : Build Local

Si vous voulez juste tester localement (votre plateforme uniquement) :

```bash
python AlignTester/scripts/build_standalone.py
```

Le build sera dans `build_standalone/dist/[plateforme]/aligntester/`

---

**Besoin de plus de détails ?** Voir `COMMENT_CREER_BUILDS.md`
