# Guide de Démarrage Rapide - Tests AlignTester

Guide rapide pour tester l'application en 5 minutes.

---

## ⚡ Démarrage Ultra-Rapide

### 1. Démarrer les serveurs

**Linux/macOS/WSL:**
```bash
cd /home/jean-fred/Aligntester/AlignTester
bash scripts/start_dev.sh
```

**Windows:**
```cmd
cd Aligntester\AlignTester
scripts\start_dev.bat
```

### 2. Ouvrir l'application

Ouvrez votre navigateur : **http://localhost:3000**

### 3. Vérifier que tout fonctionne

Vous devriez voir :
- ✅ Le titre "AlignTester"
- ✅ Les informations Greaseweazle
- ✅ Le formulaire de test d'alignement

---

## 🧪 Tests Rapides (2 minutes)

### Test 1 : Vérifier le backend

Dans un nouveau terminal :
```bash
curl http://localhost:8000/api/health
```

Résultat attendu : `{"status":"ok","message":"AlignTester API is running"}`

### Test 2 : Vérifier les informations

```bash
curl http://localhost:8000/api/info
```

Résultat attendu : JSON avec les informations Greaseweazle

### Test 3 : Utiliser le script de test

**Linux/macOS/WSL:**
```bash
bash scripts/test_app.sh
```

**Windows:**
```cmd
scripts\test_app.bat
```

---

## ✅ Checklist Rapide

- [ ] Backend démarré (port 8000)
- [ ] Frontend démarré (port 3000)
- [ ] Application accessible dans le navigateur
- [ ] Informations Greaseweazle affichées
- [ ] Pas d'erreurs dans la console du navigateur (F12)
- [ ] WebSocket connecté (voir console navigateur)

---

## 🐛 Problèmes Courants

### Le backend ne démarre pas

```bash
# Vérifier Python
python --version  # Doit être 3.11+

# Installer les dépendances
cd AlignTester/src/backend
pip install -r ../../requirements.txt

# Démarrer manuellement
python main.py
```

### Le frontend ne démarre pas

```bash
# Installer les dépendances
cd AlignTester/src/frontend
npm install

# Démarrer manuellement
npm run dev
```

### Erreur CORS

Vérifiez que le frontend utilise le port 3000 (configuré dans `vite.config.ts`)

### WebSocket ne se connecte pas

1. Ouvrez la console du navigateur (F12)
2. Vérifiez l'URL : `ws://localhost:8000/ws`
3. Vérifiez que le backend est démarré

---

## 📚 Documentation Complète

Pour des tests détaillés, consultez : **`docs/GUIDE_TEST.md`**

---

**Temps estimé** : 5 minutes pour le démarrage et les tests de base

