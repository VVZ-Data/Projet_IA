"""
Point d'entrée principal de l'application Game Collection.

Ce fichier lance l'interface d'accueil qui permet de sélectionner
parmi les jeux disponibles. Chaque jeu a ensuite son propre cycle de vie
géré par son main.py dédié.

Architecture du flux :
    main.py (racine) → home_view → games/jeux_X/main.py::run_game()
    
Auteurs: Victor Van Zieleghem, Ethan Nickels
Projet: IN252 - Projet de Conception IA - HENaLLux 2025-2026
"""

import tkinter as tk
from views.home_view import HomeView
from language_manager import lang_manager


class GameCollectionApp(tk.Tk):
    """
    Application racine affichant le menu de sélection des jeux.
    
    Cette classe ne gère QUE l'écran d'accueil. Une fois qu'un jeu
    est sélectionné, elle ferme sa fenêtre et transfère le contrôle
    au main.py du jeu concerné.
    
    Responsabilités :
    - Afficher la page d'accueil (home_view)
    - Gérer le bouton de changement de langue
    - Transférer le contrôle au jeu sélectionné
    
    Attributes:
        home_view (HomeView): Vue de la page d'accueil avec les cartes de jeux.
    """
    
    def __init__(self):
        """
        Initialise la fenêtre principale de sélection de jeux.
        
        Configure la fenêtre Tkinter et affiche la page d'accueil.
        """
        super().__init__()
        
        # === CONFIGURATION DE LA FENÊTRE ===
        self.title(lang_manager.get_text("title"))
        self.geometry("900x700")
        self.configure(bg="#ADB1BE")
        self.resizable(False, False)
        
        # === CRÉER ET AFFICHER LA PAGE D'ACCUEIL ===
        # La home_view contient les cartes cliquables des jeux disponibles
        self.home_view = HomeView(
            self, 
            on_game_selected=self._on_game_selected
        )
        self.home_view.pack(fill=tk.BOTH, expand=True)
    
    def _on_game_selected(self, game_name: str) -> None:
        """
        Callback appelé quand un jeu est sélectionné depuis home_view.
        
        Workflow :
        1. Ferme cette fenêtre principale
        2. Importe dynamiquement le module du jeu sélectionné
        3. Lance la fonction run_game() du jeu
        
        Args:
            game_name (str): Identifiant du jeu sélectionné 
                           ("matchstick", "game2", "game3", etc.).
        
        Example:
            >>> self._on_game_selected("matchstick")
            # Ferme home_view et lance games.jeux_1.main.run_game()
        """
        # === MAPPING DES JEUX VERS LEURS MODULES ===
        # Ajouter ici les futurs jeux au fur et à mesure
        game_modules = {
            "matchstick": "games.jeux_1.main",
            "Cubee": "games.jeux_2.main",
            "Kart": "games.jeux_3.main",
            # "game3": "games.jeux_3.main",
        }
        
        # === VÉRIFICATION ===
        # S'assurer que le jeu existe bien dans le mapping
        if game_name not in game_modules:
            print(f"⚠️  Jeu '{game_name}' non implémenté")
            return
        
        # === FERMER LA FENÊTRE D'ACCUEIL ===
        # Libère les ressources Tkinter de cette fenêtre
        self.destroy()
        
        # === LANCER LE JEU SÉLECTIONNÉ ===
        try:
            # Import dynamique du module du jeu
            # fromlist=["run_game"] force l'import du module complet
            module_path = game_modules[game_name]
            game_module = __import__(module_path, fromlist=["run_game"])
            
            # Appeler la fonction run_game() du jeu
            # Cette fonction doit créer sa propre fenêtre Tkinter
            game_module.run_game()
            
        except ImportError as e:
            print(f"❌ Erreur lors du chargement du jeu : {e}")
        except AttributeError:
            print(f"❌ Le module {module_path} doit avoir une fonction run_game()")


def main():
    """
    Point d'entrée principal de l'application.
    
    Crée et lance l'interface de sélection des jeux.
    Cette fonction est appelée quand on exécute : python main.py
    """
    app = GameCollectionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
