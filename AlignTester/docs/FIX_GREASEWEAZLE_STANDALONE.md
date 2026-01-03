# Intégration Greaseweazle dans le standalone - Abandonnée

## ⚠️ Statut : Abandonné

L'intégration de Greaseweazle directement dans le package standalone Windows a été **abandonnée** car :
- Tous les fichiers nécessaires n'étaient pas correctement intégrés dans le fichier zip
- La gestion des dépendances (DLLs, modules Python) était complexe et peu fiable
- L'approche ne fonctionnait pas de manière satisfaisante

## ✅ Solution actuelle

Greaseweazle n'est **pas inclus** dans le package standalone. L'utilisateur doit :

1. **Installer Greaseweazle séparément** :
   - **Windows** : Télécharger et installer `gw.exe` depuis [GitHub Greaseweazle](https://github.com/keirf/greaseweazle/releases)
   - **Linux/macOS** : Installer via `pip install greaseweazle` ou via le gestionnaire de paquets

2. **Configurer le chemin dans l'application** :
   - L'application détecte automatiquement `gw.exe` ou `gw` dans le PATH
   - Sinon, l'utilisateur peut spécifier le chemin manuellement dans les paramètres

## 📝 Historique

Cette approche d'intégration avait été tentée pour simplifier l'installation, mais s'est révélée problématique. L'approche actuelle (installation séparée) est plus fiable et standard.
