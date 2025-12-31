# AlignTester - Application Web d'Alignement Greaseweazle

Application web moderne et multi-plateforme pour les tests d'alignement de têtes de disquette utilisant la carte Greaseweazle.

## 📁 Structure du projet

```
Aligntester/
├── AlignTester/          # 🛠️  Développement
│   ├── src/              # Code source (backend + frontend)
│   ├── tests/            # Scripts de tests
│   ├── docs/             # Documentation de développement
│   └── scripts/          # Scripts utilitaires
│
├── release/              # 📦 Version finale (GitHub)
│   └── (fichiers finaux uniquement)
│
├── imd120sc/             # Dépendance externe (ImageDisk)
├── RULES.md              # Règles de structure du projet
├── STRUCTURE_PROJET.md   # Documentation de la structure
└── README.md             # Ce fichier
```

## 🚀 Développement

Tous les fichiers de développement se trouvent dans `AlignTester/`.

### Structure de développement

- **`AlignTester/src/`** : Code source de l'application
  - `legacy/` : Anciens scripts Python (référence)
  - `backend/` : API FastAPI/Flask (à créer)
  - `frontend/` : Interface web React/Vue/Svelte (à créer)

- **`AlignTester/tests/`** : Tests et validation
  - `data/` : Fichiers de données de test

- **`AlignTester/docs/`** : Documentation de développement

- **`AlignTester/scripts/`** : Scripts utilitaires
  - `prepare_release.py` : Prépare la version finale
  - `reorganize_project.py` : Réorganise le projet

## 📦 Version finale

Le dossier `release/` contient uniquement les fichiers nécessaires pour utiliser l'application.

Pour préparer une release :
```bash
python AlignTester/scripts/prepare_release.py
```

## 📚 Documentation

- **Structure du projet** : Voir `STRUCTURE_PROJET.md`
- **Règles de développement** : Voir `RULES.md`
- **Documentation technique** : Voir `AlignTester/docs/`

## 🛠️ Technologies

- **Backend** : FastAPI/Flask (Python)
- **Frontend** : React/Vue/Svelte + TypeScript
- **Communication** : WebSocket pour temps réel
- **Hardware** : Greaseweazle (via `gw.exe` / `gw`)

## 📝 Notes

- Ce projet suit une structure stricte pour séparer développement et version finale
- Consultez `RULES.md` pour les règles à suivre pendant le développement
- Les fichiers temporaires sont automatiquement exclus par `.gitignore`

## 🔗 Liens utiles

- **Greaseweazle** : https://github.com/keirf/greaseweazle
- **PR #592 (commande align)** : https://github.com/keirf/greaseweazle/pull/592
- **Documentation intégration Greaseweazle** : Voir `AlignTester/docs/INTEGRATION_GREASEWEAZLE.md`

## 📦 Ressources Greaseweazle

Le projet inclut :
- **Binaire Windows (v1.23)** : `greaseweazle-1.23/gw.exe` + DLLs nécessaires
- **Sources Python (v1.23)** : `AlignTester/src/greaseweazle-1.23/`

Voir `AlignTester/docs/INTEGRATION_GREASEWEAZLE.md` pour plus de détails.

