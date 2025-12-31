# Debug Frontend Standalone

## Problème

Le serveur démarre correctement mais le frontend n'est pas trouvé dans le build standalone.

## Diagnostic

### Vérifications à faire

1. **Vérifier que le frontend est buildé avant le build PyInstaller**
   ```bash
   cd AlignTester/src/frontend
   npm run build
   ls -la dist/
   ```

2. **Vérifier que le frontend est inclus dans le spec file**
   - Le script `build_standalone.py` devrait afficher : `[OK] Frontend ajoute: ... (X fichiers)`
   - Si ce message n'apparaît pas, le frontend n'est pas inclus

3. **Vérifier où PyInstaller place les fichiers**
   - Les fichiers `datas` sont placés dans `_internal/` par PyInstaller
   - Le launcher cherche dans plusieurs emplacements

### Emplacements où le launcher cherche le frontend

1. `_internal/frontend/dist/`
2. `_internal/frontend/`
3. `frontend/dist/` (à côté de l'exécutable)
4. `frontend/` (à côté de l'exécutable)
5. `BASE_DIR/frontend/dist/`
6. `BASE_DIR/frontend/`

### Solution temporaire : Mode API uniquement

Si le frontend n'est pas disponible, l'application fonctionne en mode API uniquement :
- Accédez à `http://127.0.0.1:8000/api/health` pour vérifier que l'API fonctionne
- Utilisez un client REST (Postman, curl, etc.) pour tester l'API

### Solution : Vérifier l'inclusion du frontend

Le problème est probablement que :
1. Le frontend n'a pas été buildé avant le build PyInstaller
2. Le frontend n'est pas inclus dans les `datas` du spec file

**Vérification** :
- Regardez les logs du build PyInstaller
- Vérifiez que `[OK] Frontend ajoute: ...` apparaît
- Si non, le frontend n'est pas inclus

**Solution** :
- S'assurer que `npm run build` est exécuté avant `build_standalone.py`
- Vérifier que `frontend_dist` n'est pas `None` dans `create_spec_file()`

---

**Dernière mise à jour** : 2024
