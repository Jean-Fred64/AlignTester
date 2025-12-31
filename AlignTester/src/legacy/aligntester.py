
import re

def extraire_valeurs_pourcentage(nom_fichier):
    """
    Extrait les valeurs numériques entre crochets [] se terminant par %
    et calcule leur moyenne
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
            
            # Calculer et afficher la moyenne
            if valeurs:
                moyenne = sum(valeurs) / len(valeurs)
                print(f"Valeurs trouvées : {valeurs}")
                print(f"Nombre de valeurs : {len(valeurs)}")
                print(f"Moyenne : {moyenne:.2f}%")
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

