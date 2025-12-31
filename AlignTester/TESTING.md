# Guide de Test - AlignTester

## 🚀 Démarrage Rapide

### Option 1 : Scripts automatiques (Recommandé)

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

### Option 2 : Démarrage manuel

**Terminal 1 - Backend:**
```bash
cd AlignTester/src/backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd AlignTester/src/frontend
npm install  # Si première fois
npm run dev
```

### Ouvrir l'application

Ouvrez votre navigateur : **http://localhost:3000**

---

## ✅ Tests Rapides

### 1. Test du backend

```bash
curl http://localhost:8000/api/health
```

Résultat attendu : `{"status":"ok","message":"AlignTester API is running"}`

### 2. Test avec script automatique

**Linux/macOS/WSL:**
```bash
bash scripts/test_app.sh
```

**Windows:**
```cmd
scripts\test_app.bat
```

### 3. Test dans le navigateur

1. Ouvrez http://localhost:3000
2. Vérifiez que les informations Greaseweazle s'affichent
3. Ouvrez la console (F12) et vérifiez "WebSocket connecté"
4. Testez un alignement (si Greaseweazle est connecté)

---

## 📚 Documentation Complète

- **Guide de test détaillé** : `docs/GUIDE_TEST.md`
- **Guide de démarrage rapide** : `docs/QUICKSTART_TEST.md`

---

## 🐛 Dépannage

### Backend ne démarre pas
- Vérifiez Python : `python --version` (doit être 3.11+)
- Installez les dépendances : `pip install -r requirements.txt`
- Vérifiez que le port 8000 est libre

### Frontend ne démarre pas
- Installez les dépendances : `npm install`
- Vérifiez que le port 3000 est libre

### WebSocket ne se connecte pas
- Vérifiez que le backend est démarré
- Ouvrez la console du navigateur (F12) pour voir les erreurs
- Vérifiez l'URL : `ws://localhost:8000/ws`

---

**Pour plus de détails, consultez `docs/GUIDE_TEST.md`**

