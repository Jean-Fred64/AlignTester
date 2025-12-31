#!/usr/bin/env python3
"""
Script pour préparer la version de publication dans le dossier release/

Ce script copie uniquement les fichiers nécessaires depuis AlignTester/
vers release/, en excluant les fichiers temporaires et de développement.
"""

import os
import shutil
from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent.parent
ALIGNTESTER_DIR = PROJECT_ROOT / "AlignTester"
RELEASE_DIR = PROJECT_ROOT / "release"

# Fichiers et dossiers à copier
FILES_TO_COPY = [
    "src/",
    "requirements.txt",
    "README.md",
    "LICENSE",  # Si présent
]

# Extensions de fichiers à copier depuis src/
ALLOWED_EXTENSIONS = {
    ".py", ".html", ".css", ".js", ".json", ".md", ".txt",
    ".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2"
}

# Dossiers à exclure
EXCLUDE_DIRS = {
    "__pycache__", ".pytest_cache", "node_modules", ".git",
    "venv", "env", ".venv", "dist", "build", ".vscode", ".idea"
}

# Fichiers à exclure
EXCLUDE_FILES = {
    ".gitkeep", ".DS_Store", "*.pyc", "*.pyo", "*.log",
    ".env", ".env.local", "config.local.py"
}


def should_exclude(path: Path) -> bool:
    """Vérifie si un fichier/dossier doit être exclu."""
    # Vérifier les dossiers exclus
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    
    # Vérifier les fichiers exclus
    if path.name in EXCLUDE_FILES:
        return True
    
    # Vérifier les extensions
    if path.suffix and path.suffix not in ALLOWED_EXTENSIONS:
        return False  # On copie les fichiers sans extension aussi
    
    return False


def copy_file_or_dir(src: Path, dst: Path):
    """Copie un fichier ou un dossier."""
    if should_exclude(src):
        print(f"  ⏭️  Exclu: {src.relative_to(PROJECT_ROOT)}")
        return
    
    if src.is_dir():
        if not dst.exists():
            dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            copy_file_or_dir(item, dst / item.name)
    else:
        if not dst.parent.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  ✅ Copié: {src.relative_to(PROJECT_ROOT)} -> {dst.relative_to(PROJECT_ROOT)}")


def prepare_release():
    """Prépare la version de publication."""
    print("🚀 Préparation de la version de publication...")
    print(f"📁 Source: {ALIGNTESTER_DIR}")
    print(f"📁 Destination: {RELEASE_DIR}\n")
    
    # Créer le dossier release s'il n'existe pas
    RELEASE_DIR.mkdir(exist_ok=True)
    
    # Nettoyer le dossier release (optionnel - commenté pour sécurité)
    # print("⚠️  Nettoyage du dossier release...")
    # if RELEASE_DIR.exists():
    #     shutil.rmtree(RELEASE_DIR)
    # RELEASE_DIR.mkdir()
    
    # Copier les fichiers et dossiers spécifiés
    for item in FILES_TO_COPY:
        src = ALIGNTESTER_DIR / item
        dst = RELEASE_DIR / item
        
        if not src.exists():
            print(f"⚠️  Fichier/dossier non trouvé: {src}")
            continue
        
        print(f"📦 Copie de {item}...")
        copy_file_or_dir(src, dst)
    
    # Copier les fichiers à la racine d'AlignTester si nécessaire
    root_files = ["requirements.txt", "README.md", "LICENSE", "setup.py"]
    for file in root_files:
        src = ALIGNTESTER_DIR / file
        if src.exists():
            dst = RELEASE_DIR / file
            if not should_exclude(src):
                shutil.copy2(src, dst)
                print(f"  ✅ Copié: {file}")
    
    print("\n✅ Version de publication préparée avec succès!")
    print(f"📁 Fichiers disponibles dans: {RELEASE_DIR}")
    print("\n💡 Prochaines étapes:")
    print("   1. Vérifier le contenu de release/")
    print("   2. Tester l'application depuis release/")
    print("   3. Commiter et pousser sur GitHub")


if __name__ == "__main__":
    prepare_release()

