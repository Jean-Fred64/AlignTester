#!/usr/bin/env python3
"""
Script de démonstration des améliorations d'alignement
Teste le parser et affiche les nouvelles métriques sans avoir besoin du frontend
"""

import sys
import os

# Ajouter le chemin du backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from api.alignment_parser import AlignmentParser

def print_colored(text, color_code):
    """Affiche du texte coloré (ANSI)"""
    colors = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    print(f"{colors.get(color_code, '')}{text}{colors['reset']}")

def get_percentage_color(percentage):
    """Retourne la couleur selon le pourcentage"""
    if percentage >= 99:
        return 'green'
    elif percentage >= 97:
        return 'blue'
    elif percentage >= 96:
        return 'yellow'
    else:
        return 'red'

def get_percentage_icon(percentage):
    """Retourne l'icône selon le pourcentage"""
    if percentage >= 99:
        return '✓'
    elif percentage >= 97:
        return '○'
    elif percentage >= 96:
        return '⚠'
    else:
        return '✗'

def get_metric_color(value):
    """Retourne la couleur selon la valeur de métrique (0-100)"""
    if value is None:
        return 'reset'
    if value >= 90:
        return 'green'
    elif value >= 70:
        return 'yellow'
    else:
        return 'red'

def get_positioning_icon(status):
    """Retourne l'icône selon le statut de positionnement"""
    if status == 'correct':
        return '✓'
    elif status == 'unstable':
        return '↕'
    elif status == 'poor':
        return '✗'
    return '○'

def main():
    print_colored("=" * 80, 'bold')
    print_colored("DÉMONSTRATION DES AMÉLIORATIONS D'ALIGNEMENT", 'bold')
    print_colored("=" * 80, 'bold')
    print()
    
    # Simuler des données de test (plusieurs lectures par piste)
    test_output = """T0.0: IBM MFM (18/18 sectors) from Raw Flux (227903 flux in 599.11ms)
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)
T0.0: IBM MFM (18/18 sectors) from Raw Flux (227900 flux in 599.09ms)
T0.1: IBM MFM (18/18 sectors) from Raw Flux (228000 flux in 600.00ms)
T0.1: IBM MFM (17/18 sectors) from Raw Flux (227500 flux in 599.50ms)
T0.1: IBM MFM (18/18 sectors) from Raw Flux (228100 flux in 600.10ms)
T1.0: IBM MFM (18/18 sectors) from Raw Flux (227950 flux in 599.20ms)
T1.0: IBM MFM (18/18 sectors) from Raw Flux (227955 flux in 599.21ms)
T1.0: IBM MFM (18/18 sectors) from Raw Flux (227960 flux in 599.22ms)
T1.1: IBM MFM (16/18 sectors) from Raw Flux (227000 flux in 598.00ms)
T1.1: IBM MFM (17/18 sectors) from Raw Flux (227200 flux in 598.50ms)
T1.1: IBM MFM (16/18 sectors) from Raw Flux (227100 flux in 598.20ms)"""
    
    print_colored("📊 Analyse des données d'alignement...", 'blue')
    print()
    
    # Parser les données
    parser = AlignmentParser()
    values = parser.parse_output(test_output)
    stats = parser.calculate_statistics(values)
    
    # Afficher les statistiques globales
    print_colored("📈 STATISTIQUES GLOBALES", 'bold')
    print(f"  Valeurs totales parsées: {stats['total_values']}")
    print(f"  Pistes analysées: {stats['used_values']}")
    print_colored(f"  Moyenne: {stats['average']:.2f}%", get_percentage_color(stats['average']))
    print_colored(f"  Minimum: {stats['min']:.2f}%", get_percentage_color(stats['min']))
    print_colored(f"  Maximum: {stats['max']:.2f}%", get_percentage_color(stats['max']))
    print()
    
    # Afficher le tableau détaillé
    print_colored("📋 DÉTAILS PAR PISTE (avec nouvelles métriques)", 'bold')
    print()
    print(f"{'Piste':<8} {'%':<10} {'Secteurs':<12} {'Cohérence':<12} {'Stabilité':<12} {'Position':<12} {'Statut':<10}")
    print("-" * 80)
    
    for value in stats['values']:
        track = value['track']
        percentage = value['percentage']
        sectors = f"{value.get('sectors_detected', '-')}/{value.get('sectors_expected', '-')}"
        consistency = value.get('consistency')
        stability = value.get('stability')
        positioning = value.get('positioning_status', 'N/A')
        
        # Formatage avec couleurs
        pct_str = f"{get_percentage_icon(percentage)} {percentage:.2f}%"
        cons_str = f"{consistency:.1f}%" if consistency is not None else "-"
        stab_str = f"{stability:.1f}%" if stability is not None else "-"
        pos_str = f"{get_positioning_icon(positioning)} {positioning}"
        
        print(f"{track:<8} ", end='')
        print_colored(f"{pct_str:<10}", get_percentage_color(percentage))
        print(f" {sectors:<12} ", end='')
        print_colored(f"{cons_str:<12}", get_metric_color(consistency))
        print(f" ", end='')
        print_colored(f"{stab_str:<12}", get_metric_color(stability))
        print(f" ", end='')
        print_colored(f"{pos_str:<12}", get_metric_color(90 if positioning == 'correct' else 70 if positioning == 'unstable' else 50))
        print()
    
    print()
    print_colored("=" * 80, 'bold')
    print_colored("✅ AMÉLIORATIONS DÉMONTRÉES", 'bold')
    print_colored("=" * 80, 'bold')
    print()
    print("✓ Détection de positionnement : correct/unstable/poor")
    print("✓ Analyse de cohérence : calculée entre les lectures multiples")
    print("✓ Analyse de stabilité : basée sur les timings et flux transitions")
    print("✓ Feedback visuel : couleurs et icônes (simulé ici)")
    print()
    print_colored("💡 Ces métriques sont maintenant disponibles dans l'API backend !", 'blue')
    print_colored("   Une fois Node.js résolu, elles seront visibles dans le frontend.", 'blue')
    print()

if __name__ == '__main__':
    main()

