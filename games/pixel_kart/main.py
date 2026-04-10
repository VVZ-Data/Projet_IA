import tkinter as tk
from .game_controller import GameController

def run_game():
    """
    Lance le jeu Pixel Kart. 
    Appelé par le menu principal GameCollectionApp.
    """
    # Création d'une nouvelle racine car l'ancienne a été détruite
    game_root = tk.Tk()
    
    # Lancement du contrôleur
    controller = GameController(game_root)
    
    # Boucle principale
    game_root.mainloop()

def train():
    """
    Fonction pour l'entraînement intensif sans interface (V2).
    """
    print("Mode entraînement activé (V2)...")
    # Implémenter ici une boucle de 1000 courses sans tk.Tk()

if __name__ == "__main__":
    # Permet de lancer le jeu en direct : python -m games.pixel_kart.main
    run_game()