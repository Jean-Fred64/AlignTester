
import re
import math
import sys

def calculer_barre_graphique(moyenne):
    """
    Génère une représentation graphique de la moyenne avec des conditions spécifiques
    """
    # Définir la longueur totale de la barre
    longueur_totale = 50
    
    # Calculer le nombre de blocs à remplir
    blocs_remplis = math.floor((moyenne / 100) * longueur_totale)
    
    # Déterminer le texte à afficher
    if 99.000 <= moyenne <= 99.999:
        texte_alignement = "Align Perfect"
    elif 97.000 <= moyenne <= 98.999:
        texte_alignement = "Align Good"
    elif 96.000 <= moyenne <= 97.999:
        texte_alignement = "Align Average"
    elif moyenne < 96.000:
        texte_alignement = "Align Poor"
    else:
        texte_alignement = ""
    
    # Construire la barre graphique
    barre = "[" + "█" * blocs_remplis + " " * (longueur_totale - blocs_remplis) + "]"
    
    return f"{barre} {moyenne:.3f}% {texte_alignement}"

def extraire_valeurs_pourcentage(nom_fichier, limite=160):
    """
    Extrait les valeurs numériques entre crochets [] se terminant par %
    et calcule leur moyenne, en limitant à 160 premières valeurs
    avec une précision de 3 chiffres après la virgule
    """
    valeurs_avec_details = []
    
    try:
        # Ouvrir et lire le fichier
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            for numero_ligne, ligne in enumerate(fichier, 1):
                # Expression régulière pour trouver les valeurs entre [] et se terminant par %
                pattern = r'\[(\d+(?:\.\d+)?)\s*%\]'
                
                # Rechercher les correspondances dans la ligne
                resultats = re.findall(pattern, ligne)
                for resultat in resultats:
                    valeur = float(resultat)
                    
                    # Extraire le numéro au début de la ligne (entre 00.0 et 85.1)
                    numero_match = re.search(r'^(\d+\.\d)', ligne)
                    numero = float(numero_match.group(1)) if numero_match else 0.0
                    
                    valeurs_avec_details.append({
                        'valeur': valeur, 
                        'numero_ligne': numero_ligne, 
                        'numero': numero,
                        'ligne_originale': ligne.strip()
                    })
            
            # Trier les valeurs par le numéro trouvé
            valeurs_avec_details.sort(key=lambda x: x['numero'])
            
            # Limiter aux 160 premières valeurs
            valeurs_utilisees = valeurs_avec_details[:limite]
            
            # Calculer et afficher la moyenne
            if valeurs_utilisees:
                valeurs = [v['valeur'] for v in valeurs_utilisees]
                moyenne = sum(valeurs) / len(valeurs)
                
                # Calculer track_max (dernière valeur trouvée)
                track_max = valeurs_avec_details[-1]['numero'] if valeurs_avec_details else 0
                
                # Vérifier si track_max correspond à la moitié du nombre total de valeurs
                nombre_total_valeurs = len(valeurs_avec_details)
                track_max_verification = nombre_total_valeurs / 2
                
                # Calculer track_normal (nombre de valeurs utilisées divisé par 2)
                track_normal = len(valeurs_utilisees) / 2
                
                # Afficher les détails des valeurs utilisées
                print("\nDétails des valeurs utilisées :")
                for detail in valeurs_utilisees:
                    print(f"Ligne {detail['numero_ligne']} - Numéro {detail['numero']} : {detail['ligne_originale']} (Valeur : {detail['valeur']}%)")
                
                # Afficher les informations supplémentaires
                print(f"\nNombre total de valeurs trouvées : {nombre_total_valeurs}")
                print(f"Nombre de valeurs utilisées pour la moyenne : {len(valeurs_utilisees)}")
                print(f"Nombre total de track lues : {track_max}")
                print(f"Nombre total de track pour le calcul de la moyenne : {track_normal}")
                
                print("\nReprésentation graphique :")
                print(calculer_barre_graphique(moyenne))
            else:
                print("Aucune valeur en pourcentage trouvée.")
    
    except FileNotFoundError:
        print(f"Erreur : Le fichier {nom_fichier} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    
    return valeurs_avec_details

# Vérifier si un nom de fichier est fourni en argument
if len(sys.argv) < 2:
    print("Utilisation : python script.py <nom_du_fichier>")
    sys.exit(1)

# Récupérer le nom du fichier à partir des arguments
nom_fichier = sys.argv[1]

# Lancer l'extraction et le calcul
resultats = extraire_valeurs_pourcentage(nom_fichier)

