# Correction de l'erreur Zone.Identifier

## 🐛 Problème

L'erreur suivante apparaît lors du build sur GitHub Actions Windows :

```
Error: error: invalid path 'AlignTester/src/greaseweazle-1.23 sources/greaseweazle-1.23/src/greaseweazle/tools/align.py:Zone.Identifier'
Error: The process 'C:\Program Files\Git\bin\git.exe' failed with exit code 128
```

## 🔍 Cause

Les fichiers `Zone.Identifier` sont des métadonnées créées par Windows quand vous téléchargez des fichiers depuis Internet. Ils contiennent un caractère `:` dans leur nom, ce qui est **interdit sur Windows** (sauf pour les lecteurs comme `C:`).

## ✅ Solution appliquée

1. **Suppression des fichiers Zone.Identifier du dépôt Git**
   ```bash
   git rm --cached "AlignTester/src/greaseweazle-1.23 sources/greaseweazle-1.23/src/greaseweazle/tools/align.py:Zone.Identifier"
   git rm --cached "AlignTester/src/greaseweazle-1.23b/src/greaseweazle/tools/align.py:Zone.Identifier"
   ```

2. **Ajout au .gitignore** pour éviter qu'ils soient ajoutés à nouveau
   ```
   *:Zone.Identifier
   **/*:Zone.Identifier
   ```

3. **Commit et push**
   ```bash
   git add .gitignore
   git commit -m "Suppression des fichiers Zone.Identifier"
   git push origin main
   ```

## 🔧 Si le problème persiste

Si vous avez d'autres fichiers Zone.Identifier :

```bash
# Trouver tous les fichiers Zone.Identifier
find . -name "*Zone.Identifier" -type f

# Les supprimer du dépôt Git
git rm --cached $(find . -name "*Zone.Identifier" -type f)

# Commit
git commit -m "Suppression de tous les fichiers Zone.Identifier"
git push origin main
```

## 📝 Note

Les fichiers Zone.Identifier sont des métadonnées Windows qui indiquent que le fichier vient d'une "zone" Internet. Ils ne sont pas nécessaires pour le fonctionnement du projet et peuvent être ignorés en toute sécurité.

---

**Dernière mise à jour** : 2024
