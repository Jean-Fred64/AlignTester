# Configuration de l'environnement virtuel Python

## Création de l'environnement virtuel

```bash
cd ~/Aligntester/AlignTester
python3 -m venv venv
```

## Activation de l'environnement virtuel

```bash
source venv/bin/activate
```

Vous devriez voir `(venv)` apparaître dans votre prompt.

## Installation des dépendances

Une fois l'environnement activé :

```bash
pip install -r requirements.txt
```

## Démarrage du serveur

```bash
cd src/backend
python main.py
```

## Désactivation de l'environnement virtuel

Quand vous avez terminé :

```bash
deactivate
```

## Note importante

**N'oubliez pas d'activer l'environnement virtuel à chaque fois** que vous voulez travailler sur le projet :

```bash
cd ~/Aligntester/AlignTester
source venv/bin/activate
```

