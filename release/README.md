# AlignTester - Version de publication

Ce dossier contient uniquement les fichiers nécessaires pour utiliser l'application AlignTester.

## Contenu

Les fichiers présents ici sont ceux qui seront publiés sur GitHub et utilisés par les utilisateurs finaux.

## Structure attendue

```
release/
├── README.md              # Documentation utilisateur
├── requirements.txt       # Dépendances Python
├── app.py                 # Application principale (si applicable)
├── src/                   # Code source final
├── static/                # Fichiers statiques (CSS, JS, images)
├── templates/             # Templates HTML (si applicable)
└── docs/                  # Documentation utilisateur
```

## Mise à jour

Ce dossier est mis à jour via le script `prepare_release.py` qui copie uniquement les fichiers nécessaires depuis `AlignTester/`.

