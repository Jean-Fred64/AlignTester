# Dépannage - Mode Manuel

## Problème : Les onglets "Mode Automatique" / "Mode Manuel" ne sont pas visibles

### Solutions

1. **Vérifier que le frontend est bien démarré**
   ```bash
   cd AlignTester/src/frontend
   npm run dev
   ```

2. **Vérifier que le backend est démarré**
   ```bash
   cd AlignTester/src/backend
   python main.py
   ```

3. **Vider le cache du navigateur**
   - Appuyez sur `Ctrl+Shift+R` (ou `Cmd+Shift+R` sur Mac) pour forcer le rechargement
   - Ou ouvrez les outils de développement (F12) et videz le cache

4. **Vérifier la console du navigateur**
   - Ouvrez les outils de développement (F12)
   - Allez dans l'onglet "Console"
   - Vérifiez s'il y a des erreurs JavaScript

5. **Vérifier que le fichier ManualAlignment.tsx existe**
   ```bash
   ls -la AlignTester/src/frontend/src/components/ManualAlignment.tsx
   ```

6. **Recompiler le frontend**
   ```bash
   cd AlignTester/src/frontend
   npm run build
   ```

7. **Vérifier les imports dans App.tsx**
   Le fichier `App.tsx` doit contenir :
   ```typescript
   import { ManualAlignment } from './components/ManualAlignment'
   ```

8. **Vérifier que activeTab est initialisé**
   Le fichier `App.tsx` doit contenir :
   ```typescript
   const [activeTab, setActiveTab] = useState<'auto' | 'manual'>('auto')
   ```

### Où devraient apparaître les onglets ?

Les onglets "Mode Automatique" et "Mode Manuel" devraient apparaître :
- **Juste après** la section "Informations Greaseweazle"
- **Avant** le composant `AlignmentControl` ou `ManualAlignment`
- Avec un style de bordure en bas (border-b border-gray-700)

### Structure attendue de l'interface

```
┌─────────────────────────────────────┐
│  Informations Greaseweazle          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  [Mode Automatique] [Mode Manuel]  │  ← Onglets ici
├─────────────────────────────────────┤
│                                     │
│  Contenu selon l'onglet actif      │
│                                     │
└─────────────────────────────────────┘
```

### Si les onglets ne s'affichent toujours pas

1. **Vérifier dans les outils de développement**
   - Ouvrez les outils de développement (F12)
   - Allez dans l'onglet "Éléments" (Elements)
   - Cherchez `<div className="flex gap-2 mb-4 border-b border-gray-700">`
   - Si vous ne le trouvez pas, il y a un problème de rendu

2. **Vérifier les erreurs TypeScript**
   ```bash
   cd AlignTester/src/frontend
   npm run build
   ```
   - Si des erreurs apparaissent, corrigez-les

3. **Vérifier que le serveur de développement est bien démarré**
   - Le serveur devrait être sur `http://localhost:5173` (Vite)
   - Ou `http://localhost:3000` (Create React App)

4. **Vérifier la version de Node.js**
   ```bash
   node --version
   ```
   - Doit être >= 16.0.0

### Test rapide

Pour vérifier que le composant est bien importé, ajoutez temporairement ceci dans `App.tsx` :

```typescript
console.log('ManualAlignment component:', ManualAlignment);
```

Si vous voyez `undefined` dans la console, il y a un problème d'import.

