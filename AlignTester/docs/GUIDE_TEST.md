# Guide de Test - AlignTester

Ce guide vous aide à tester l'application AlignTester étape par étape.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

1. **Python 3.11+** installé
2. **Node.js 18+** et npm installés
3. **Greaseweazle** disponible (gw.exe ou gw)
4. **Environnement virtuel Python** activé (si utilisé)

---

## 🚀 Démarrage Rapide

### Option 1 : Scripts de démarrage automatique

#### Linux/macOS/WSL
```bash
cd /home/jean-fred/Aligntester/AlignTester
bash scripts/start_dev.sh
```

#### Windows
```cmd
cd Aligntester\AlignTester
scripts\start_dev.bat
```

### Option 2 : Démarrage manuel

#### 1. Démarrer le Backend

```bash
cd AlignTester/src/backend
python main.py
```

Vous devriez voir :
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 2. Démarrer le Frontend (dans un autre terminal)

```bash
cd AlignTester/src/frontend
npm install  # Si première fois
npm run dev
```

Vous devriez voir :
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

## ✅ Tests de Base

### Test 1 : Vérifier que le Backend démarre

1. Ouvrez un navigateur ou utilisez curl :
```bash
curl http://localhost:8000/api/health
```

Résultat attendu :
```json
{
  "status": "ok",
  "message": "AlignTester API is running"
}
```

### Test 2 : Vérifier les informations Greaseweazle

```bash
curl http://localhost:8000/api/info
```

Résultat attendu :
```json
{
  "platform": "Windows",
  "gw_path": "gw.exe",
  "version": "1.23",
  "align_available": true,
  "device": {
    "port": "COM3",
    "model": "Greaseweazle",
    "connected": true,
    ...
  }
}
```

### Test 3 : Vérifier le Frontend

1. Ouvrez votre navigateur : `http://localhost:3000`
2. Vous devriez voir :
   - Le titre "AlignTester"
   - Les informations Greaseweazle
   - Le formulaire de test d'alignement

### Test 4 : Vérifier la connexion WebSocket

1. Ouvrez la console du navigateur (F12)
2. Vous devriez voir : `WebSocket connecté`
3. Vérifiez qu'il n'y a pas d'erreurs de connexion

---

## 🧪 Tests Fonctionnels

### Test 5 : Test d'alignement complet

**Prérequis** : Greaseweazle connecté et commande `align` disponible

1. Dans l'interface web :
   - Vérifiez que "Commande align disponible" est à "✓ Oui"
   - Vérifiez que "Greaseweazle connecté" est affiché

2. Configurez les paramètres :
   - Nombre de cylindres : 10 (pour un test rapide)
   - Nombre de tentatives : 1

3. Cliquez sur "Démarrer l'alignement"

4. Vérifiez :
   - ✅ La barre de progression s'affiche
   - ✅ Le pourcentage de progression augmente
   - ✅ Les valeurs collectées augmentent
   - ✅ Le statut passe à "running"

5. Attendez la fin (ou annulez avec le bouton "Annuler")

6. Vérifiez les résultats :
   - ✅ Le statut passe à "completed"
   - ✅ Les statistiques s'affichent (moyenne, min, max, qualité)
   - ✅ Les graphiques s'affichent
   - ✅ Le graphique en ligne montre l'évolution
   - ✅ Le graphique en barres montre la répartition par qualité

### Test 6 : Test d'annulation

1. Démarrez un alignement avec 80 cylindres
2. Après quelques secondes, cliquez sur "Annuler"
3. Vérifiez :
   - ✅ Le statut passe à "cancelled"
   - ✅ Un message d'annulation s'affiche
   - ✅ Le formulaire redevient actif

### Test 7 : Test de gestion d'erreurs

1. Débranchez Greaseweazle (ou simulez une erreur)
2. Démarrez un alignement
3. Vérifiez :
   - ✅ Un message d'erreur s'affiche
   - ✅ Le statut passe à "error"
   - ✅ Le message d'erreur est clair

---

## 🔍 Tests de Validation

### Test 8 : Validation des paramètres

1. Testez avec des valeurs invalides :
   - Cylindres : 0 → Doit être rejeté
   - Cylindres : 200 → Doit être limité à 160
   - Tentatives : 0 → Doit être rejeté
   - Tentatives : 20 → Doit être limité à 10

2. Vérifiez que les valeurs sont correctement validées

### Test 9 : Test de rafraîchissement automatique

1. Démarrez un alignement
2. Ouvrez l'application dans un autre onglet
3. Vérifiez :
   - ✅ Les deux onglets affichent le même statut
   - ✅ Les mises à jour WebSocket fonctionnent dans les deux onglets

### Test 10 : Test de reconnexion WebSocket

1. Démarrez l'application
2. Déconnectez temporairement le réseau (ou arrêtez le backend)
3. Reconnectez
4. Vérifiez :
   - ✅ La reconnexion automatique fonctionne
   - ✅ Les données sont récupérées correctement

---

## 📊 Tests de Performance

### Test 11 : Test avec beaucoup de données

1. Démarrez un alignement avec 80 cylindres
2. Vérifiez :
   - ✅ L'application reste réactive
   - ✅ Les graphiques se mettent à jour sans lag
   - ✅ La mémoire ne sature pas

### Test 12 : Test de stress WebSocket

1. Ouvrez plusieurs onglets (5-10)
2. Démarrez un alignement
3. Vérifiez :
   - ✅ Tous les onglets reçoivent les mises à jour
   - ✅ Aucune déconnexion inattendue

---

## 🐛 Tests de Cas Limites

### Test 13 : Test sans Greaseweazle

1. Assurez-vous que Greaseweazle n'est pas connecté
2. Ouvrez l'application
3. Vérifiez :
   - ✅ Un message indique que Greaseweazle n'est pas connecté
   - ✅ Le bouton de démarrage est désactivé si `align_available` est false

### Test 14 : Test avec commande align non disponible

1. Utilisez une version de gw.exe sans la commande `align`
2. Vérifiez :
   - ✅ `align_available` est à false
   - ✅ Un message d'erreur clair s'affiche
   - ✅ Le bouton de démarrage est désactivé

### Test 15 : Test de double démarrage

1. Démarrez un alignement
2. Essayez de démarrer un autre alignement (sans annuler le premier)
3. Vérifiez :
   - ✅ Une erreur indique qu'un alignement est déjà en cours
   - ✅ Le deuxième démarrage est rejeté

---

## 📝 Checklist de Test Complète

Utilisez cette checklist pour valider tous les aspects :

### Backend
- [ ] Le serveur démarre sans erreur
- [ ] L'endpoint `/api/health` répond
- [ ] L'endpoint `/api/info` retourne les bonnes informations
- [ ] L'endpoint `/api/status` retourne l'état actuel
- [ ] L'endpoint `/api/align` démarre un alignement
- [ ] L'endpoint `/api/align/cancel` annule correctement
- [ ] Le WebSocket `/ws` accepte les connexions
- [ ] Les messages WebSocket sont envoyés correctement

### Frontend
- [ ] L'application se charge sans erreur
- [ ] Les informations Greaseweazle s'affichent
- [ ] Le formulaire fonctionne correctement
- [ ] La validation des paramètres fonctionne
- [ ] La barre de progression s'affiche
- [ ] Les graphiques s'affichent correctement
- [ ] Les statistiques sont calculées correctement
- [ ] Les messages d'erreur sont clairs
- [ ] La connexion WebSocket fonctionne
- [ ] La reconnexion automatique fonctionne

### Intégration
- [ ] Le backend et frontend communiquent correctement
- [ ] Les mises à jour en temps réel fonctionnent
- [ ] L'annulation fonctionne de bout en bout
- [ ] Les erreurs sont gérées correctement
- [ ] Les données persistent pendant l'alignement

---

## 🛠️ Dépannage

### Problème : Le backend ne démarre pas

**Solutions** :
1. Vérifiez que Python est installé : `python --version`
2. Vérifiez que les dépendances sont installées : `pip install -r requirements.txt`
3. Vérifiez que le port 8000 n'est pas utilisé : `netstat -an | grep 8000`
4. Vérifiez les erreurs dans la console

### Problème : Le frontend ne démarre pas

**Solutions** :
1. Vérifiez que Node.js est installé : `node --version`
2. Installez les dépendances : `npm install`
3. Vérifiez que le port 3000 n'est pas utilisé
4. Vérifiez les erreurs dans la console

### Problème : Erreur CORS

**Solutions** :
1. Vérifiez que le frontend utilise le bon port (3000)
2. Vérifiez la configuration CORS dans `main.py`
3. Vérifiez que les URLs correspondent

### Problème : WebSocket ne se connecte pas

**Solutions** :
1. Vérifiez que le backend est démarré
2. Vérifiez l'URL WebSocket : `ws://localhost:8000/ws`
3. Ouvrez la console du navigateur pour voir les erreurs
4. Vérifiez que le proxy Vite est configuré correctement

### Problème : Greaseweazle non détecté

**Solutions** :
1. Vérifiez que gw.exe/gw est dans le PATH ou accessible
2. Vérifiez que Greaseweazle est connecté
3. Testez manuellement : `gw.exe --version`
4. Vérifiez les chemins dans `greaseweazle.py`

---

## 📚 Ressources

- Documentation API : `http://localhost:8000/docs` (Swagger UI)
- Documentation ReDoc : `http://localhost:8000/redoc`
- Console navigateur : F12 → Console
- Logs backend : Console où `python main.py` est lancé

---

**Dernière mise à jour** : Après complétion de l'implémentation backend/frontend

