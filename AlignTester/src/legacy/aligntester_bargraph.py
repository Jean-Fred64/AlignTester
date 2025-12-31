
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
    valeurs = []
    
    try:
        # Ouvrir et lire le fichier
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()
            
            # Expression régulière pour trouver les valeurs entre [] et se terminant par %
            pattern = r'\[(\d+(?:\.\d+)?)\s*%\]'
            
            # Rechercher toutes les correspondances
            resultats = re.findall(pattern, contenu)
            
            # Convertir les valeurs trouvées en nombres réels
            for resultat in resultats:
                valeurs.append(float(resultat))
            
            # Limiter aux 160 premières valeurs
            valeurs_utilisees = valeurs[:limite]
            
            # Calculer et afficher la moyenne
            if valeurs_utilisees:
                moyenne = sum(valeurs_utilisees) / len(valeurs_utilisees)
                print(f"Nombre total de valeurs trouvées : {len(valeurs)}")
                print(f"Nombre de valeurs utilisées pour la moyenne : {len(valeurs_utilisees)}")
                print("Représentation graphique :")
                print(calculer_barre_graphique(moyenne))
            else:
                print("Aucune valeur en pourcentage trouvée.")
    
    except FileNotFoundError:
        print(f"Erreur : Le fichier {nom_fichier} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    
    return valeurs

# Exemple d'utilisation
nom_fichier = 'donnees.txt'
resultats = extraire_valeurs_pourcentage(nom_fichier)

