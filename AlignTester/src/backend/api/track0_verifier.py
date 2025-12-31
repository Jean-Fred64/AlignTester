"""
Module de vérification du capteur Track 0
Basé sur la Section 9.9 du manuel Panasonic JU-253
"""

import asyncio
from typing import Dict, List, Optional, Any
from .greaseweazle import GreaseweazleExecutor
from .alignment_parser import AlignmentParser
from .diskdefs_parser import get_diskdefs_parser


class Track0Verifier:
    """Vérifie le capteur Track 0 du lecteur"""
    
    def __init__(self, executor: GreaseweazleExecutor):
        self.executor = executor
        self.parser = AlignmentParser()
    
    async def verify_track0_sensor(
        self,
        test_positions: Optional[List[int]] = None,
        reads_per_test: int = 5,
        format_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Vérifie le capteur Track 0 (Section 9.9 du manuel Panasonic)
        Teste si le seek vers la piste 0 fonctionne correctement
        
        Args:
            test_positions: Liste des positions de départ pour tester (défaut: [10, 20, 40, 79])
            reads_per_test: Nombre de lectures à effectuer pour chaque test (défaut: 5)
            format_type: Format de disquette à utiliser pour les lectures (défaut: "ibm.1440")
        
        Returns:
            Dict avec:
            - sensor_ok: bool - True si le capteur fonctionne correctement
            - seek_tests: List[Dict] - Résultats des tests de seek
            - read_tests: Dict - Résultats des lectures de piste 0
            - warnings: List[str] - Avertissements détectés
            - suggestions: List[str] - Suggestions d'ajustement
        """
        # Utiliser le format fourni ou "ibm.1440" par défaut
        if format_type is None:
            format_type = "ibm.1440"
        
        # Obtenir le nombre maximum de pistes du format sélectionné
        max_track = 79  # Valeur par défaut pour IBM 1.44MB (80 pistes, 0-79)
        try:
            parser = get_diskdefs_parser()
            format_info = parser.get_format_info(format_type)
            if format_info and format_info.get("cyls"):
                # Le nombre de cylindres est le nombre maximum de pistes (0-indexed, donc max = cyls - 1)
                max_track = int(format_info["cyls"]) - 1
                print(f"[Track0Verifier] Format {format_type}: {format_info['cyls']} cylindres (pistes 0-{max_track})")
            else:
                print(f"[Track0Verifier] Format {format_type} non trouvé, utilisation de la valeur par défaut (80 pistes)")
        except Exception as e:
            print(f"[Track0Verifier] Erreur lors de la récupération des infos du format {format_type}: {e}, utilisation de la valeur par défaut")
        
        # Calculer les positions de test adaptées au format
        # Si test_positions n'est pas fourni, calculer des positions proportionnelles
        if test_positions is None:
            # Positions de test : 25%, 50%, 75%, et max-1 (dernière piste)
            # S'assurer que les positions sont dans la plage valide [0, max_track]
            test_positions = [
                max(1, int(max_track * 0.25)),      # ~25% du maximum
                max(1, int(max_track * 0.50)),      # ~50% du maximum
                max(1, int(max_track * 0.75)),      # ~75% du maximum
                max(1, max_track - 1)                # Avant-dernière piste (max-1)
            ]
            # Supprimer les doublons et trier
            test_positions = sorted(list(set(test_positions)))
            # S'assurer qu'on a au moins 2 positions différentes
            if len(test_positions) < 2:
                test_positions = [max(1, max_track // 2), max(1, max_track - 1)]
        
        # Vérifier que toutes les positions sont valides
        test_positions = [pos for pos in test_positions if 0 <= pos <= max_track]
        if not test_positions:
            # Si aucune position valide, utiliser des valeurs par défaut
            test_positions = [max(1, max_track // 2), max(1, max_track - 1)]
        
        results = {
            'sensor_ok': False,
            'seek_tests': [],
            'read_tests': {},
            'warnings': [],
            'suggestions': []
        }
        
        # Test 1: Seek vers piste 0 depuis différentes positions
        print(f"[Track0Verifier] Début des tests de seek depuis {len(test_positions)} positions: {test_positions} (format: {format_type}, max: {max_track})")
        for start_pos in test_positions:
            try:
                # Seek vers la position de départ avec --motor-on et --force pour activer le moteur
                # Syntaxe: gw seek [--device DEVICE] [--drive DRIVE] [--motor-on] [--force] CYLINDER
                seek_result_start = await self.executor.run_command(
                    ['seek', '--motor-on', '--force', str(start_pos)],
                    timeout=10
                )
                
                if seek_result_start.returncode != 0:
                    results['seek_tests'].append({
                        'from_track': start_pos,
                        'to_track': start_pos,
                        'success': False,
                        'error': f"Impossible de seek vers piste {start_pos}: {seek_result_start.stderr or seek_result_start.stdout}",
                        'step': 'initial_seek'
                    })
                    continue
                
                # Attendre un peu pour que le lecteur se stabilise
                await asyncio.sleep(0.3)
                
                # Seek vers piste 0 avec --motor-on et --force
                seek_result_0 = await self.executor.run_command(
                    ['seek', '--motor-on', '--force', '0'],
                    timeout=10
                )
                
                # Attendre un peu après le seek pour que le lecteur se stabilise
                await asyncio.sleep(0.3)
                
                results['seek_tests'].append({
                    'from_track': start_pos,
                    'to_track': 0,
                    'success': seek_result_0.returncode == 0,
                    'message': seek_result_0.stdout if seek_result_0.returncode == 0 else None,
                    'error': seek_result_0.stderr if seek_result_0.returncode != 0 else None,
                    'step': 'seek_to_track0'
                })
                
            except asyncio.TimeoutError:
                results['seek_tests'].append({
                    'from_track': start_pos,
                    'to_track': 0,
                    'success': False,
                    'error': f"Timeout lors du seek depuis piste {start_pos}",
                    'step': 'seek_to_track0'
                })
            except Exception as e:
                results['seek_tests'].append({
                    'from_track': start_pos,
                    'to_track': 0,
                    'success': False,
                    'error': f"Erreur: {str(e)}",
                    'step': 'seek_to_track0'
                })
        
        # Vérifier si tous les seeks ont réussi
        all_seeks_ok = all(test['success'] for test in results['seek_tests'])
        
        if not all_seeks_ok:
            failed_seeks = [test for test in results['seek_tests'] if not test['success']]
            results['warnings'].append(
                f"{len(failed_seeks)} test(s) de seek ont échoué. "
                "Le capteur Track 0 peut nécessiter un ajustement."
            )
        
        # Test 2: Lecture de la piste 0 (plusieurs lectures pour cohérence)
        print(f"[Track0Verifier] Début des lectures de piste 0 ({reads_per_test} lectures)")
        try:
            # S'assurer qu'on est bien sur la piste 0 avec --motor-on et --force
            await self.executor.run_command(['seek', '--motor-on', '--force', '0'], timeout=10)
            await asyncio.sleep(0.3)
            
            # Effectuer plusieurs lectures de la piste 0
            # Utiliser align avec seulement la piste 0 pour plusieurs lectures
            track0_readings = []
            try:
                # Utiliser align avec plusieurs lectures de la piste 0 uniquement
                # Format: gw align --tracks=c=0:h=0 --reads=N --format=XXX
                # Utiliser run_align avec cylinders=1 (piste 0) et retries=reads_per_test
                align_result = await self.executor.run_align(
                    cylinders=1,  # Seulement la piste 0
                    retries=reads_per_test,  # Nombre de lectures
                    format_type=format_type,  # Format sélectionné par l'utilisateur
                    on_output=None
                )
                
                # Parser les résultats
                # run_align() retourne un dictionnaire, pas un objet avec attributs
                if align_result.get("stdout"):
                    parsed_values = self.parser.parse_output(align_result["stdout"])
                    track0_readings.extend(parsed_values)
                    
            except Exception as e:
                results['warnings'].append(f"Erreur lors des lectures de piste 0: {str(e)}")
            
            # Analyser les lectures
            if track0_readings:
                # Filtrer pour ne garder que les lectures de piste 0
                track0_only = [r for r in track0_readings if r.track == '0.0' or r.track.startswith('0.')]
                
                if track0_only:
                    # Vérifier la cohérence des lectures
                    percentages = [r.percentage for r in track0_only if r.percentage is not None]
                    sectors_detected = [r.sectors_detected for r in track0_only if r.sectors_detected is not None]
                    sectors_expected = [r.sectors_expected for r in track0_only if r.sectors_expected is not None]
                    
                    # Vérifier que toutes les lectures détectent la piste 0
                    all_track0 = all(
                        r.track == '0.0' or r.track.startswith('0.')
                        for r in track0_only
                    )
                    
                    # Vérifier la cohérence des secteurs
                    if sectors_expected:
                        expected = sectors_expected[0]  # Toutes devraient être identiques
                        all_readings_ok = all(
                            s == expected for s in sectors_expected
                        ) and all(
                            s == expected for s in sectors_detected if s is not None
                        )
                    else:
                        all_readings_ok = False
                    
                    # Vérifier la cohérence des pourcentages
                    if percentages:
                        avg_percentage = sum(percentages) / len(percentages)
                        min_percentage = min(percentages)
                        max_percentage = max(percentages)
                        percentage_variance = max_percentage - min_percentage
                        
                        # Si la variance est faible (< 2%), les lectures sont cohérentes
                        percentage_consistent = percentage_variance < 2.0
                    else:
                        percentage_consistent = False
                        avg_percentage = None
                    
                    results['read_tests'] = {
                        'readings_count': len(track0_only),
                        'total_readings': len(track0_readings),
                        'all_readings_ok': all_readings_ok and all_track0,
                        'all_track0': all_track0,
                        'percentage_consistent': percentage_consistent,
                        'avg_percentage': round(avg_percentage, 2) if avg_percentage is not None else None,
                        'percentage_variance': round(percentage_variance, 2) if percentages else None,
                        'readings': [
                            {
                                'track': r.track,
                                'percentage': r.percentage,
                                'sectors_detected': r.sectors_detected,
                                'sectors_expected': r.sectors_expected,
                                'flux_transitions': r.flux_transitions,
                                'time_per_rev': r.time_per_rev
                            }
                            for r in track0_only
                        ]
                    }
                    
                    if not all_readings_ok:
                        results['warnings'].append(
                            "Les lectures de la piste 0 sont incohérentes - "
                            "Le capteur Track 0 peut nécessiter un ajustement"
                        )
                    
                    if not all_track0:
                        results['warnings'].append(
                            "Certaines lectures ne détectent pas la piste 0 - "
                            "Le capteur Track 0 peut être défectueux"
                        )
                    
                    if not percentage_consistent and percentages:
                        results['warnings'].append(
                            f"Les pourcentages varient trop entre les lectures "
                            f"(variance: {percentage_variance:.2f}%) - "
                            "Le capteur Track 0 peut nécessiter un ajustement"
                        )
                else:
                    results['read_tests'] = {
                        'readings_count': 0,
                        'total_readings': len(track0_readings),
                        'all_readings_ok': False,
                        'all_track0': False,
                        'error': 'Aucune lecture de piste 0 détectée'
                    }
                    results['warnings'].append(
                        "Aucune lecture de piste 0 n'a été détectée - "
                        "Le capteur Track 0 peut être défectueux"
                    )
            else:
                results['read_tests'] = {
                    'readings_count': 0,
                    'total_readings': 0,
                    'all_readings_ok': False,
                    'all_track0': False,
                    'error': 'Aucune lecture effectuée'
                }
                results['warnings'].append(
                    "Impossible d'effectuer des lectures de piste 0 - "
                    "Vérifiez la connexion et que la disquette est insérée"
                )
                
        except Exception as e:
            results['warnings'].append(f"Erreur lors des lectures de piste 0: {str(e)}")
            results['read_tests'] = {
                'readings_count': 0,
                'total_readings': 0,
                'all_readings_ok': False,
                'all_track0': False,
                'error': str(e)
            }
        
        # Évaluation finale
        reads_ok = results['read_tests'].get('all_readings_ok', False) and \
                   results['read_tests'].get('all_track0', False)
        
        results['sensor_ok'] = all_seeks_ok and reads_ok
        
        # Générer des suggestions
        if not results['sensor_ok']:
            if not all_seeks_ok:
                results['suggestions'].append(
                    "❌ Certains tests de seek vers piste 0 ont échoué. "
                    "Consultez la Section 9.9 du manuel Panasonic JU-253 pour "
                    "les procédures d'ajustement du capteur Track 0."
                )
            
            if not reads_ok:
                results['suggestions'].append(
                    "❌ Les lectures de piste 0 sont incohérentes. "
                    "Le capteur Track 0 peut nécessiter un ajustement mécanique. "
                    "Vérifiez que le capteur est propre et correctement positionné."
                )
        else:
            results['suggestions'].append(
                "✅ Capteur Track 0 fonctionne correctement"
            )
        
        return results

