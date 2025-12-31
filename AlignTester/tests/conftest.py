"""
Configuration pytest pour les tests AlignTester
"""

import sys
from pathlib import Path
import pytest
from typing import AsyncGenerator

# Ajouter le chemin du backend aux imports
BACKEND_DIR = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

@pytest.fixture
def sample_alignment_output():
    """Fichier de sortie d'alignement de test"""
    return """00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us
00.1    : base: 1.004 us [99.742%], band: 2.005 us, 3.003 us
01.0    : base: 1.001 us [99.856%], band: 2.003 us, 3.002 us, 4.007 us
01.1    : base: 0.998 us [99.923%], band: 2.001 us, 3.000 us
02.0    : base: 1.002 us [99.789%], band: 2.004 us, 3.004 us"""

@pytest.fixture
def sample_alignment_lines():
    """Lignes d'alignement de test"""
    return [
        "00.0    : base: 1.000 us [99.911%], band: 2.002 us, 3.001 us, 4.006 us",
        "00.1    : base: 1.004 us [99.742%], band: 2.005 us, 3.003 us",
        "01.0    : base: 1.001 us [99.856%], band: 2.003 us, 3.002 us, 4.007 us",
        "01.1    : base: 0.998 us [99.923%], band: 2.001 us, 3.000 us",
        "02.0    : base: 1.002 us [99.789%], band: 2.004 us, 3.004 us",
    ]

@pytest.fixture
def sample_alignment_output_incomplete():
    """Sortie d'alignement incomplète (pour tester les cas limites)"""
    return """00.0    : base: 1.000 us [99.911%]
[95.5%]
Track 01.0: [98.2%]"""

@pytest.fixture
def sample_statistics():
    """Statistiques d'alignement de test"""
    return {
        "total_values": 5,
        "used_values": 5,
        "average": 99.644,
        "min": 99.742,
        "max": 99.923,
        "track_max": "02.0",
        "track_normal": 2.5,
        "values": []
    }

# Note: pytest-asyncio gère automatiquement l'event loop
# Pas besoin de fixture event_loop personnalisée si pytest-asyncio est installé

