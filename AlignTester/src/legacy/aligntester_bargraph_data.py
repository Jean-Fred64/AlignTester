
import re
import math

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
                
                print(f"Nombre total de valeurs trouvées : {len(valeurs_avec_details)}")
                print(f"Nombre de valeurs utilisées pour la moyenne : {len(valeurs_utilisees)}")
                
                # Afficher les détails des valeurs utilisées
                print("\nDétails des valeurs utilisées :")
                for detail in valeurs_utilisees:
                    print(f"Ligne {detail['numero_ligne']} - Numéro {detail['numero']} : {detail['ligne_originale']} (Valeur : {detail['valeur']}%)")
                
                print("\nReprésentation graphique :")
                print(calculer_barre_graphique(moyenne))
            else:
                print("Aucune valeur en pourcentage trouvée.")
    
    except FileNotFoundError:
        print(f"Erreur : Le fichier {nom_fichier} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    
    return valeurs_avec_details

# Exemple d'utilisation
nom_fichier = 'donnees.txt'
resultats = extraire_valeurs_pourcentage(nom_fichier)

