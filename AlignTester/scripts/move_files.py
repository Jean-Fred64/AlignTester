#!/usr/bin/env python3
"""Script pour déplacer les fichiers restants vers la structure organisée"""
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Créer les dossiers nécessaires
docs_dir = PROJECT_ROOT / "AlignTester" / "docs"
data_dir = PROJECT_ROOT / "AlignTester" / "tests" / "data"
docs_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)
print("📁 Dossiers créés/vérifiés\n")

# Déplacer les fichiers de documentation
docs_to_move = [
    "ANALYSE_STRATEGIE_DEVELOPPEMENT.md",
    "DOCUMENTATION.md",
    "DOCUMENTATION_GREASEWEAZLE.md",
    "DOCUMENTATION_GREASEWEAZLEGUI.md",
]

# Déplacer les fichiers de données
data_to_move = [
    "donnees.txt",
    "dungeon.txt",
    "D359T5.txt",
    "Pauline.txt",
]

print("Déplacement des fichiers de documentation...")
for filename in docs_to_move:
    src = PROJECT_ROOT / filename
    dst = PROJECT_ROOT / "AlignTester" / "docs" / filename
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  ✅ Copié: {filename}")
    else:
        print(f"  ⏭️  Non trouvé: {filename}")

print("\nDéplacement des fichiers de données...")
for filename in data_to_move:
    src = PROJECT_ROOT / filename
    dst = PROJECT_ROOT / "AlignTester" / "tests" / "data" / filename
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  ✅ Copié: {filename}")
    else:
        print(f"  ⏭️  Non trouvé: {filename}")

print("\nSuppression des originaux de la racine...")
for filename in docs_to_move + data_to_move:
    src = PROJECT_ROOT / filename
    if src.exists():
        src.unlink()
        print(f"  ✅ Supprimé: {filename}")

print("\n✅ Réorganisation terminée!")

