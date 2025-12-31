# Guide de Test d'Alignement via l'API

Ce guide vous montre comment tester les fonctionnalités d'alignement directement via l'API REST.

---

## 🚀 Démarrage Rapide

### 1. Vérifier que le backend est démarré

```bash
curl http://localhost:8000/api/health
```

Résultat attendu :
```json
{"status":"ok","message":"AlignTester API is running"}
```

### 2. Vérifier les informations Greaseweazle

```bash
curl http://localhost:8000/api/info
```

Résultat attendu :
```json
{
  "platform": "Linux",
  "gw_path": "/mnt/s/Divers SSD M2/Test D7/Greaseweazle/greaseweazle-1.23b/gw.exe",
  "version": "...",
  "align_available": true,
  "device": {...}
}
```

**Important** : Vérifiez que `align_available` est `true` avant de continuer.

---

## 🧪 Test d'Alignement Complet

### Étape 1 : Vérifier le statut initial

```bash
curl http://localhost:8000/api/status
```

Résultat attendu :
```json
{
  "status": "idle",
  "cylinders": 80,
  "retries": 3,
  "progress_percentage": 0.0,
  "values_count": 0
}
```

### Étape 2 : Démarrer un alignement

**Test rapide (10 cylindres, 1 tentative) :**
```bash
curl -X POST http://localhost:8000/api/align \
  -H "Content-Type: application/json" \
  -d '{"cylinders": 10, "retries": 1}'
```

**Test complet (80 cylindres, 3 tentatives) :**
```bash
curl -X POST http://localhost:8000/api/align \
  -H "Content-Type: application/json" \
  -d '{"cylinders": 80, "retries": 3}'
```

Résultat attendu :
```json
{
  "status": "started",
  "message": "Test d'alignement démarré avec 10 cylindres",
  "cylinders": 10,
  "retries": 1
}
```

### Étape 3 : Suivre la progression

**Dans un terminal, surveillez le statut :**
```bash
# Surveiller toutes les 2 secondes
watch -n 2 'curl -s http://localhost:8000/api/status | python3 -m json.tool'
```

**Ou manuellement :**
```bash
curl http://localhost:8000/api/status | python3 -m json.tool
```

Pendant l'exécution, vous verrez :
```json
{
  "status": "running",
  "cylinders": 10,
  "retries": 1,
  "progress_percentage": 45.5,
  "values_count": 9,
  "current_cylinder": 4
}
```

### Étape 4 : Vérifier les résultats finaux

Une fois terminé :
```bash
curl http://localhost:8000/api/status | python3 -m json.tool
```

Résultat attendu :
```json
{
  "status": "completed",
  "cylinders": 10,
  "retries": 1,
  "progress_percentage": 100.0,
  "values_count": 20,
  "statistics": {
    "average": 99.523,
    "min": 97.234,
    "max": 99.999,
    "quality": "Perfect",
    "total_values": 20,
    "used_values": 20,
    "track_max": "9.1",
    "track_normal": 10.0
  }
}
```

---

## 🔄 Test d'Annulation

### Démarrer un alignement long

```bash
curl -X POST http://localhost:8000/api/align \
  -H "Content-Type: application/json" \
  -d '{"cylinders": 80, "retries": 3}'
```

### Annuler après quelques secondes

```bash
curl -X POST http://localhost:8000/api/align/cancel
```

Résultat attendu :
```json
{
  "status": "cancelled",
  "message": "Alignement annulé"
}
```

Vérifier le statut :
```bash
curl http://localhost:8000/api/status | python3 -m json.tool
```

---

## 📡 Test WebSocket (Mises à jour en temps réel)

### Option 1 : Utiliser websocat

```bash
# Installer websocat (si nécessaire)
# Sur Ubuntu/Debian: sudo apt install websocat
# Ou via cargo: cargo install websocat

# Se connecter au WebSocket
websocat ws://localhost:8000/ws
```

### Option 2 : Script Python simple

Créez `test_websocket.py` :
```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print("✅ Connecté au WebSocket")
        
        # Écouter les messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Message reçu: {json.dumps(data, indent=2)}")

asyncio.run(test_websocket())
```

Exécuter :
```bash
pip install websockets
python test_websocket.py
```

### Option 3 : Extension navigateur

1. Installez une extension WebSocket (ex: "WebSocket King" pour Chrome)
2. Connectez-vous à : `ws://localhost:8000/ws`
3. Démarrez un alignement dans un autre terminal
4. Observez les messages en temps réel

---

## 🐛 Gestion des Erreurs

### Test avec Greaseweazle non connecté

Si Greaseweazle n'est pas connecté, vous obtiendrez une erreur :
```bash
curl -X POST http://localhost:8000/api/align \
  -H "Content-Type: application/json" \
  -d '{"cylinders": 10, "retries": 1}'
```

Résultat possible :
```json
{
  "detail": "Erreur lors de l'exécution de la commande align"
}
```

Vérifier le statut d'erreur :
```bash
curl http://localhost:8000/api/status | python3 -m json.tool
```

```json
{
  "status": "error",
  "error_message": "Description de l'erreur"
}
```

### Test de double démarrage

Essayer de démarrer deux alignements en même temps :
```bash
# Terminal 1
curl -X POST http://localhost:8000/api/align \
  -H "Content-Type: application/json" \
  -d '{"cylinders": 10, "retries": 1}'

# Terminal 2 (immédiatement après)
curl -X POST http://localhost:8000/api/align \
  -H "Content-Type: application/json" \
  -d '{"cylinders": 10, "retries": 1}'
```

Résultat attendu pour le deuxième :
```json
{
  "detail": "Un alignement est déjà en cours. Veuillez attendre ou annuler."
}
```

---

## 📊 Script de Test Automatique

Créez `test_alignment.sh` :
```bash
#!/bin/bash

echo "🧪 Test d'alignement AlignTester"
echo ""

# 1. Vérifier le backend
echo "1. Vérification du backend..."
HEALTH=$(curl -s http://localhost:8000/api/health)
if [[ $HEALTH == *"ok"* ]]; then
    echo "✅ Backend OK"
else
    echo "❌ Backend non accessible"
    exit 1
fi

# 2. Vérifier align_available
echo "2. Vérification de la disponibilité d'align..."
INFO=$(curl -s http://localhost:8000/api/info)
ALIGN_AVAILABLE=$(echo $INFO | python3 -c "import sys, json; print(json.load(sys.stdin)['align_available'])")
if [[ $ALIGN_AVAILABLE == "True" ]]; then
    echo "✅ Commande align disponible"
else
    echo "❌ Commande align non disponible"
    exit 1
fi

# 3. Démarrer un alignement
echo "3. Démarrage d'un alignement (10 cylindres, 1 tentative)..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/align \
  -H "Content-Type: application/json" \
  -d '{"cylinders": 10, "retries": 1}')
echo "Réponse: $RESPONSE"

# 4. Attendre la fin
echo "4. Attente de la fin de l'alignement..."
while true; do
    STATUS=$(curl -s http://localhost:8000/api/status)
    STATE=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
    
    if [[ $STATE == "completed" ]]; then
        echo "✅ Alignement terminé!"
        echo $STATUS | python3 -m json.tool
        break
    elif [[ $STATE == "error" ]]; then
        echo "❌ Erreur lors de l'alignement"
        echo $STATUS | python3 -m json.tool
        exit 1
    else
        PROGRESS=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['progress_percentage'])")
        VALUES=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['values_count'])")
        echo "   Progression: ${PROGRESS}% - Valeurs: ${VALUES}"
    fi
    
    sleep 2
done

echo ""
echo "✅ Test terminé avec succès!"
```

Rendre exécutable et lancer :
```bash
chmod +x test_alignment.sh
./test_alignment.sh
```

---

## 🎯 Checklist de Test

- [ ] Backend accessible (`/api/health`)
- [ ] Informations Greaseweazle récupérées (`/api/info`)
- [ ] `align_available` est `true`
- [ ] Alignement démarré avec succès (`/api/align`)
- [ ] Progression suivie en temps réel (`/api/status`)
- [ ] Statistiques finales récupérées
- [ ] Annulation fonctionne (`/api/align/cancel`)
- [ ] WebSocket reçoit les mises à jour
- [ ] Gestion des erreurs fonctionne
- [ ] Double démarrage rejeté

---

## 📚 Ressources

- **Documentation API** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Health Check** : http://localhost:8000/api/health

---

**Dernière mise à jour** : Après complétion de l'implémentation backend/frontend

