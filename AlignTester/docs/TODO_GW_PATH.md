# TODO : Refonte de la gestion du chemin gw.exe

## Problème actuel
La gestion du chemin vers gw.exe est trop complexe et ne fonctionne pas correctement :
- Conversion Windows/WSL pas fiable
- Gestion des dossiers vs fichiers confuse
- Messages d'aide pas clairs
- Code dispersé dans plusieurs fichiers

## Objectifs pour la refonte
1. **Simplifier** : Une seule logique claire et simple
2. **Optimiser** : Code plus direct et maintenable
3. **Tester** : S'assurer que ça fonctionne dans tous les cas

## Approche proposée

### Principe de base
- L'utilisateur peut entrer :
  - Un chemin complet vers `gw.exe` (ex: `/mnt/s/.../gw.exe` ou `S:\...\gw.exe`)
  - Un chemin vers un dossier contenant `gw.exe` (ex: `/mnt/s/.../greaseweazle-1.23b`)
  
### Fonctionnalités essentielles
1. **Sauvegarde** : Mémoriser le dernier chemin utilisé
2. **Validation** : Vérifier que le chemin/fichier existe
3. **Normalisation** : Convertir en chemin absolu standardisé
4. **Détection auto** : Optionnel, mais simple si présent

### Simplifications à faire
- [x] Créer une fonction unique `normalize_gw_path(path: str) -> str` qui gère tout
- [x] Séparer clairement :
  - Détection automatique (optionnel)
  - Saisie manuelle (principal)
  - Validation (simple et claire)
- [x] Messages d'erreur clairs et utiles
- [x] Interface simple : un champ de saisie + bouton "Enregistrer"

### Cas à gérer
1. Chemin Windows complet : `S:\Divers SSD M2\...\gw.exe`
2. Chemin WSL complet : `/mnt/s/Divers SSD M2/.../gw.exe`
3. Dossier Windows : `S:\Divers SSD M2\...\greaseweazle-1.23b`
4. Dossier WSL : `/mnt/s/Divers SSD M2/.../greaseweazle-1.23b`
5. Chemin relatif : `gw.exe` (si dans PATH)

### Code à simplifier
- `AlignTester/src/backend/api/greaseweazle.py` : `_detect_gw_path()` et `detect_gw_path_auto()`
- `AlignTester/src/backend/api/routes.py` : `set_gw_path()`
- `AlignTester/src/frontend/src/App.tsx` : `handleFileSelected()` et `handleSetGwPath()`

## Prochaines étapes
1. Analyser tous les cas d'usage réels
2. Créer une fonction de normalisation unique et testable
3. Simplifier l'interface utilisateur
4. Tester avec différents scénarios
5. Documenter clairement le comportement attendu

## ✅ Refonte terminée

### Changements effectués

1. **Fonction unique `normalize_gw_path()` créée** dans `greaseweazle.py` :
   - Gère la conversion Windows → WSL automatiquement
   - Détecte si l'entrée est un dossier ou un fichier
   - Cherche `gw.exe` ou `gw` dans les dossiers automatiquement
   - Valide l'existence des chemins
   - Retourne toujours un chemin absolu normalisé

2. **Code simplifié dans `greaseweazle.py`** :
   - `_detect_gw_path()` utilise maintenant `normalize_gw_path()`
   - `detect_gw_path_auto()` refactorisé pour être plus maintenable
   - Fonction `_is_wsl()` déplacée au niveau module pour réutilisation

3. **Code simplifié dans `routes.py`** :
   - `set_gw_path()` réduit de ~90 lignes à ~20 lignes
   - Toute la logique de normalisation déléguée à `normalize_gw_path()`
   - Messages d'erreur plus clairs et structurés

4. **Code simplifié dans `App.tsx`** :
   - `handleFileSelected()` simplifié avec messages d'aide plus clairs
   - `handleSetGwPath()` avec meilleure gestion des erreurs
   - Messages d'erreur plus explicites selon le type d'erreur

### Fonctionnalités

La fonction `normalize_gw_path()` gère maintenant tous les cas :
- ✅ Chemin Windows complet : `S:\Divers SSD M2\...\gw.exe`
- ✅ Chemin WSL complet : `/mnt/s/Divers SSD M2/.../gw.exe`
- ✅ Dossier Windows : `S:\Divers SSD M2\...\greaseweazle-1.23b`
- ✅ Dossier WSL : `/mnt/s/Divers SSD M2/.../greaseweazle-1.23b`
- ✅ Chemin relatif : `gw.exe` (sera cherché dans PATH)
- ✅ Conversion automatique Windows → WSL quand nécessaire

---
**Créé le** : 2025-01-XX
**Refonte terminée le** : 2025-01-XX
**Statut** : ✅ Terminé
