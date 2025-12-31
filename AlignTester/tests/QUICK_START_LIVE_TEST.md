# 🚀 Démarrage Rapide - Test Mode Direct

## Test Simple (30 secondes)

```bash
cd /home/jean-fred/Aligntester/AlignTester
source venv/bin/activate
python3 tests/test_mode_direct_live.py
```

## Test avec Piste Spécifique

```bash
# Piste 40 (centrale, recommandée pour le réglage)
python3 tests/test_mode_direct_live.py --track 40

# Piste 0 (bord extérieur)
python3 tests/test_mode_direct_live.py --track 0

# Piste 79 (bord intérieur)
python3 tests/test_mode_direct_live.py --track 79
```

## Test avec Format Différent

```bash
# IBM 720KB (9 secteurs)
python3 tests/test_mode_direct_live.py --format ibm.720

# IBM 1.2MB (15 secteurs)
python3 tests/test_mode_direct_live.py --format ibm.1200
```

## Arrêter le Test

Appuyez sur **Ctrl+C** pour arrêter le test à tout moment.

## Ce que Vous Devriez Voir

```
[  1] T40.0 | 18/18 secteurs | 100.0% | ✓ excellent  | ████████████ | Latence: 152ms
[  2] T40.0 | 18/18 secteurs | 100.0% | ✓ excellent  | ████████████ | Latence: 148ms
[  3] T40.0 | 17/18 secteurs |  94.4% | ○ good       | ███████████░ | Latence: 151ms
```

## Objectifs de Latence

- ✅ **< 200ms** : Excellent (objectif atteint)
- ✅ **200-300ms** : Bon (acceptable)
- ⚠️ **> 300ms** : À améliorer

## Pour le Réglage en Direct

1. Démarrez le test
2. Ajustez les vis de réglage pendant que le test tourne
3. Observez l'impact immédiat (latence ~150-200ms)
4. Arrêtez avec Ctrl+C quand satisfait

---

📖 Pour plus de détails, voir `README_TEST_LIVE.md`

