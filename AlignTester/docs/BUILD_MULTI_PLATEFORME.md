# Build Multi-Plateforme - AlignTester

Ce document explique comment créer des builds standalone pour Windows, Linux et macOS.

## 🎯 Options disponibles

### Option 1 : Build local (plateforme actuelle uniquement)

Vous pouvez créer un build pour votre plateforme actuelle :

```bash
# Installer les dépendances
pip install -r AlignTester/requirements.txt

# Builder le frontend
cd AlignTester/src/frontend
npm install
npm run build
cd ../../..

# Lancer le build standalone
python AlignTester/scripts/build_standalone.py
```

Le build sera créé dans `build_standalone/dist/[plateforme]/aligntester/`

### Option 2 : GitHub Actions (recommandé pour multi-plateforme)

Un workflow GitHub Actions est disponible pour créer automatiquement les builds pour toutes les plateformes.

#### Utilisation

1. **Push un tag** pour déclencher le build :
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **Ou utilisez l'interface GitHub** :
   - Allez dans l'onglet "Actions"
   - Sélectionnez "Build Standalone"
   - Cliquez sur "Run workflow"

#### Résultat

Les builds seront disponibles :
- En tant qu'**artifacts** dans l'onglet Actions
- En tant que **release assets** si vous créez une release GitHub

### Option 3 : Build manuel sur chaque plateforme

Pour créer des builds pour toutes les plateformes, vous devez :

1. **Windows** : Exécuter le script sur une machine Windows
2. **Linux** : Exécuter le script sur une machine Linux
3. **macOS** : Exécuter le script sur une machine macOS

## 📦 Structure des builds

Chaque build contient :

```
aligntester/
├── aligntester.exe          # (Windows) ou aligntester (Linux/macOS)
├── _internal/               # Bibliothèques Python compilées
│   ├── python311.dll       # (Windows uniquement)
│   ├── lib/                # Bibliothèques Python
│   └── ...
├── frontend/                # Frontend React buildé
│   └── dist/
│       ├── index.html
│       ├── assets/
│       └── ...
├── backend/                 # Code backend Python
│   ├── main.py
│   ├── api/
│   └── ...
└── README_STANDALONE.txt    # Guide d'utilisation
```

## 🚀 Workflow GitHub Actions

Le workflow `.github/workflows/build-standalone.yml` :

1. ✅ Vérifie le code
2. ✅ Configure Python 3.11
3. ✅ Configure Node.js 18
4. ✅ Installe les dépendances
5. ✅ Build le frontend
6. ✅ Crée l'exécutable standalone
7. ✅ Compresse le package
8. ✅ Upload les artifacts
9. ✅ Crée une release si tag présent

## 📋 Prérequis pour GitHub Actions

Aucun prérequis supplémentaire ! Le workflow utilise les runners GitHub qui ont déjà :
- Python 3.11
- Node.js 18
- Toutes les dépendances système nécessaires

## 🔧 Dépannage

### Build échoue sur GitHub Actions

1. Vérifiez les logs dans l'onglet Actions
2. Vérifiez que toutes les dépendances sont dans `requirements.txt`
3. Vérifiez que le frontend build correctement

### Build local échoue

Voir `BUILD_STANDALONE.md` pour le dépannage détaillé.

## 📝 Notes

- Les builds GitHub Actions sont automatiques et gratuits pour les repos publics
- Les artifacts sont conservés 30 jours
- Pour une conservation permanente, créez une release GitHub

---

**Dernière mise à jour** : 2024
