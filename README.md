# AlignTester - Application Web d'Alignement Greaseweazle

Application web moderne et multi-plateforme pour les tests d'alignement de têtes de disquette utilisant la carte Greaseweazle.

![GUI](https://github.com/Jean-Fred64/AlignTester/blob/main/AlignTester/docs/img/AlignTester%20-%20Test%20d'alignement%20Greaseweazle.png)

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

### 📖 Guide d'Utilisation (Recommandé)

**Pour les utilisateurs** : Guides complets d'utilisation avec approche débutant et informations pour experts.

- 🇫🇷 **[Guide d'Utilisation (Français)](AlignTester/docs/GUIDE_UTILISATION_FR.md)** - Guide complet en français
- 🇬🇧 **[User Guide (English)](AlignTester/docs/GUIDE_UTILISATION_EN.md)** - Complete guide in English

Ces guides couvrent :
- Configuration initiale (détection Greaseweazle, sélection du lecteur, format de disquette)
- Mode automatique d'alignement
- Mode manuel d'alignement
- Fonctionnalités avancées
- Dépannage
- Annexes techniques

**📘 Wiki GitHub** : Ces guides sont également disponibles sur le [Wiki GitHub](https://github.com/Jean-Fred64/AlignTester/wiki) du projet.

### Documentation technique

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

Le projet utilise une **version compilée v1.23b de Greaseweazle** qui inclut la commande `align` issue du [Pull Request #592](https://github.com/keirf/greaseweazle/pull/592).

### Sources Greaseweazle v1.23b

Les sources de Greaseweazle v1.23b sont disponibles dans `AlignTester/src/greaseweazle-1.23b.zip` (11MB).

**Téléchargement direct** : [greaseweazle-1.23b.zip](https://github.com/Jean-Fred64/AlignTester/raw/main/AlignTester/src/greaseweazle-1.23b.zip)

**Note** : Le fichier zip doit être décompressé dans `AlignTester/src/greaseweazle-1.23b/` avant d'utiliser les scripts de build standalone.

### Compatibilité par plateforme

| Plateforme | Interface | Mode Automatique (`gw align`) | Mode Manuel (`gw align`) |
|------------|-----------|-------------------------------|-------------------------|
| **Windows** | ✅ Fonctionnelle | ✅ Disponible (v1.23b) | ✅ Disponible (v1.23b) |
| **Linux** | ✅ Fonctionnelle | ❌ Non disponible (v1.22 uniquement) | ❌ Non disponible (v1.22 uniquement) |
| **macOS** | ✅ Fonctionnelle | ❌ Non disponible (v1.22 uniquement) | ❌ Non disponible (v1.22 uniquement) |

**Note importante** :
- L'interface fonctionne correctement sur toutes les plateformes
- Les **deux modes** (automatique et manuel) utilisent la commande `gw align` et nécessitent Greaseweazle v1.23b
- Sous Windows, Greaseweazle v1.23b est disponible avec support de `gw align` (PR #592)
- Sous Linux/macOS, seule la version Greaseweazle v1.22 est disponible, qui ne supporte pas la commande `align`
- Les deux modes d'alignement nécessitent donc Greaseweazle v1.23b (actuellement disponible uniquement sur Windows)

Voir `AlignTester/docs/INTEGRATION_GREASEWEAZLE.md` pour plus de détails.


