#!/usr/bin/env python3
"""
Script pour réorganiser le projet selon la structure définie dans RULES.md
"""

import os
import shutil
from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent.parent
ALIGNTESTER_DIR = PROJECT_ROOT / "AlignTester"

# Mapping des fichiers à déplacer
REORGANIZATION_MAP = {
    # Fichiers Python de développement -> src/legacy/
    "aligntester.py": ALIGNTESTER_DIR / "src" / "legacy",
    "aligntester_bargraph.py": ALIGNTESTER_DIR / "src" / "legacy",
    "aligntester_bargraph_data.py": ALIGNTESTER_DIR / "src" / "legacy",
    "aligntester_final.py": ALIGNTESTER_DIR / "src" / "legacy",
    "aligntester_finalfin.py": ALIGNTESTER_DIR / "src" / "legacy",
    "aligntester_Kryoflux.py": ALIGNTESTER_DIR / "src" / "legacy",
    "aligntester_Kryoflux_EN.py": ALIGNTESTER_DIR / "src" / "legacy",
    "aligntester_Kryoflux_FR.py": ALIGNTESTER_DIR / "src" / "legacy",
    "extraction_pourcentage.py": ALIGNTESTER_DIR / "src" / "legacy",
    
    # Documentation de développement -> docs/
    "ANALYSE_STRATEGIE_DEVELOPPEMENT.md": ALIGNTESTER_DIR / "docs",
    "DOCUMENTATION.md": ALIGNTESTER_DIR / "docs",
    "DOCUMENTATION_GREASEWEAZLE.md": ALIGNTESTER_DIR / "docs",
    "DOCUMENTATION_GREASEWEAZLEGUI.md": ALIGNTESTER_DIR / "docs",
    
    # Fichiers de données de test -> tests/data/
    "donnees.txt": ALIGNTESTER_DIR / "tests" / "data",
    "dungeon.txt": ALIGNTESTER_DIR / "tests" / "data",
    "D359T5.txt": ALIGNTESTER_DIR / "tests" / "data",
    "Pauline.txt": ALIGNTESTER_DIR / "tests" / "data",
}

# Fichiers à ignorer (fichiers système, etc.)
IGNORE_FILES = {
    "dungeon - Copie.txtZone.Identifier",  # Fichier système Windows
}

# Dossiers à garder à la racine
KEEP_AT_ROOT = {
    "imd120sc",  # Dépendance externe
    "AlignTester",
    "release",
    ".git",
}


def create_directories():
    """Crée les dossiers nécessaires."""
    dirs_to_create = [
        ALIGNTESTER_DIR / "src" / "legacy",
        ALIGNTESTER_DIR / "tests" / "data",
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Dossier créé/vérifié: {dir_path.relative_to(PROJECT_ROOT)}")


def move_file(src_path: Path, dst_dir: Path):
    """Déplace un fichier vers un dossier de destination."""
    if not src_path.exists():
        print(f"⚠️  Fichier non trouvé: {src_path.name}")
        return False
    
    dst_path = dst_dir / src_path.name
    
    # Si le fichier existe déjà à la destination, créer un backup
    if dst_path.exists():
        backup_path = dst_path.with_suffix(dst_path.suffix + ".backup")
        print(f"⚠️  Fichier existe déjà, création backup: {backup_path.name}")
        shutil.copy2(dst_path, backup_path)
    
    try:
        shutil.move(str(src_path), str(dst_path))
        print(f"✅ Déplacé: {src_path.name} -> {dst_dir.relative_to(PROJECT_ROOT)}/")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du déplacement de {src_path.name}: {e}")
        return False


def reorganize():
    """Réorganise les fichiers selon la structure définie."""
    print("🔄 Réorganisation du projet selon la structure définie...\n")
    
    # Créer les dossiers nécessaires
    print("📁 Création des dossiers...")
    create_directories()
    print()
    
    # Déplacer les fichiers
    print("📦 Déplacement des fichiers...")
    moved_count = 0
    skipped_count = 0
    
    for filename, dst_dir in REORGANIZATION_MAP.items():
        src_path = PROJECT_ROOT / filename
        
        if src_path.exists():
            if move_file(src_path, dst_dir):
                moved_count += 1
            else:
                skipped_count += 1
        else:
            print(f"⏭️  Fichier non trouvé (peut-être déjà déplacé): {filename}")
            skipped_count += 1
    
    print(f"\n✅ Réorganisation terminée!")
    print(f"   - Fichiers déplacés: {moved_count}")
    print(f"   - Fichiers ignorés/sautés: {skipped_count}")
    
    # Afficher les fichiers restants à la racine
    print("\n📋 Fichiers restants à la racine:")
    remaining = []
    for item in PROJECT_ROOT.iterdir():
        if item.is_file() and item.name not in IGNORE_FILES:
            if item.name not in [f.name for f in REORGANIZATION_MAP.keys()]:
                # Vérifier si c'est un fichier de configuration du projet
                config_files = {".gitignore", ".cursorrules", "RULES.md", "STRUCTURE_PROJET.md", "README.md"}
                if item.name not in config_files:
                    remaining.append(item.name)
    
    if remaining:
        for filename in sorted(remaining):
            print(f"   - {filename}")
        print("\n💡 Ces fichiers peuvent être:")
        print("   - Des fichiers de configuration du projet (à garder)")
        print("   - Des fichiers à déplacer manuellement")
        print("   - Des fichiers à supprimer")
    else:
        print("   ✅ Aucun fichier restant (sauf fichiers de configuration)")


if __name__ == "__main__":
    reorganize()

