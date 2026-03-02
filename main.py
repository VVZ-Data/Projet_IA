"""
Point d'entrée principal de l'application.
Gère la navigation entre les différentes vues.
"""

import tkinter as tk
from tkinter import Tk
from player import Player, Human, AI
from game_model import GameModel
from game_controller import GameController
from views.home_view import HomeView
from views.matchstick_menu_view import MatchstickMenuView
from views.game_view import GameView
from views.training_view import TrainingView
from language_manager import lang_manager


class MainApplication(Tk):
    """
    Application principale gérant toutes les vues.
    
    Cette classe orchestre la navigation entre :
    - La page d'accueil (sélection de jeu)
    - Le menu du jeu des allumettes
    - Le jeu lui-même
    - La page d'entraînement de l'IA
    
    Attributes:
        current_view (Frame): Vue actuellement affichée.
        game_controller (GameController): Contrôleur du jeu (créé à la demande).
    """
    
    def __init__(self):
        """
        Initialise l'application et affiche la page d'accueil.
        """
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("Game Collection")
        self.geometry("900x700")  # Taille de la fenêtre
        self.configure(bg="#F5F7FA")  # Couleur de fond
        self.resizable(False, False)  # Empêcher le redimensionnement
        
        # Variables d'état
        self.current_view = None  # Vue actuellement affichée
        self.game_controller = None  # Contrôleur du jeu (créé quand nécessaire)
        
        # Afficher la page d'accueil
        self.show_home()
    
    def clear_view(self) -> None:
        """
        Supprime la vue actuellement affichée.
        
        Permet de nettoyer l'interface avant d'afficher une nouvelle vue.
        """
        if self.current_view:
            self.current_view.pack_forget()  # Masquer la vue
            self.current_view.destroy()  # Détruire les widgets
            self.current_view = None
    
    def show_home(self) -> None:
        """
        Affiche la page d'accueil avec la sélection des jeux.
        """
        self.clear_view()
        
        # Créer et afficher la vue d'accueil
        self.current_view = HomeView(
            self,
            on_game_selected=self.on_game_selected
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def on_game_selected(self, game_name: str) -> None:
        """
        Gère la sélection d'un jeu depuis la page d'accueil.
        
        Args:
            game_name (str): Identifiant du jeu sélectionné.
        """
        if game_name == "matchstick":
            # Afficher le menu du jeu des allumettes
            self.show_matchstick_menu()
        # Ici, ajouter d'autres jeux dans le futur
    
    def show_matchstick_menu(self) -> None:
        """
        Affiche le menu du jeu des allumettes (Jouer / Entraîner).
        """
        self.clear_view()
        
        # Créer et afficher le menu
        self.current_view = MatchstickMenuView(
            self,
            on_play_selected=self.on_play_selected,
            on_train_selected=self.show_training,
            on_back=self.show_home
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def on_play_selected(self, mode: str) -> None:
        """
        Gère le lancement d'une partie.
        
        Args:
            mode (str): Mode de jeu ("ai" ou "random").
        """
        # Créer les joueurs selon le mode choisi
        human = Human("Player 1")
        
        if mode == "ai":
            # Charger une IA entraînée si possible
            opponent = AI("AI", epsilon=0.1, learning_rate=0.3)
            try:
                opponent.download("AI_save_1")  # Charger les poids entraînés
            except FileNotFoundError:
                # Si pas de sauvegarde, utiliser une IA vierge
                pass
        else:  # mode == "random"
            opponent = Player("Random Bot")
        
        # Lancer le jeu
        self.start_game(human, opponent)
    
    def start_game(self, p1: Player, p2: Player, total_matches: int = 15) -> None:
        """
        Lance une partie de jeu des allumettes.
        
        Args:
            p1 (Player): Premier joueur.
            p2 (Player): Second joueur.
            total_matches (int): Nombre d'allumettes (par défaut 15).
        """
        self.clear_view()
        
        # Créer le contrôleur de jeu
        self.game_controller = GameController(
            p1, p2, total_matches,
            on_quit=self.show_matchstick_menu
        )
        
        # Créer et afficher la vue du jeu
        game_view = GameView(self, self.game_controller)
        self.game_controller.set_view(game_view)  # Lier la vue au contrôleur
        
        self.current_view = game_view
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def show_training(self) -> None:
        """
        Affiche la page d'entraînement de l'IA.
        """
        self.clear_view()
        
        # Créer et afficher la vue d'entraînement
        self.current_view = TrainingView(
            self,
            on_start_training=self.start_training,
            on_back=self.show_matchstick_menu
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def start_training(self, nb_games: int, epsilon_decay: int, learning_rate: float) -> None:
        """
        Lance l'entraînement de deux IA.
        
        Args:
            nb_games (int): Nombre de parties à jouer.
            epsilon_decay (int): Fréquence de diminution d'epsilon.
            learning_rate (float): Taux d'apprentissage.
        """
        # Créer deux IA à entraîner
        ai1 = AI("AI 1", epsilon=0.9, learning_rate=learning_rate)
        ai2 = AI("AI 2", epsilon=0.9, learning_rate=learning_rate)
        
        # Créer un modèle de jeu pour l'entraînement (sans affichage)
        training_game = GameModel(12, ai1, ai2, displayable=False)
        
        # Lancer l'entraînement avec mise à jour de la progression
        for i in range(nb_games):
            # Diminuer epsilon régulièrement
            if i % epsilon_decay == 0 and i > 0:
                ai1.next_epsilon()
                ai2.next_epsilon()
            
            # Jouer une partie
            training_game.play()
            
            # Entraîner les deux IA sur cette partie
            ai1.train()
            ai2.train()
            
            # Réinitialiser pour la prochaine partie
            training_game.reset()
            
            # Mettre à jour la barre de progression toutes les 1000 parties
            if i % 1000 == 0 or i == nb_games - 1:
                if isinstance(self.current_view, TrainingView):
                    self.current_view.update_progress(i + 1, nb_games)
                    self.current_view.update()  # Forcer le rafraîchissement
        
        # Afficher les résultats finaux
        if isinstance(self.current_view, TrainingView):
            self.current_view.show_results(
                ai1.nb_wins,
                ai2.nb_wins,
                nb_games
            )
        
        # Sauvegarder les IA entraînées
        ai1.upload("AI_save_1")
        ai2.upload("AI_save_2")


def main() -> None:
    """
    Point d'entrée du programme.
    Crée et lance l'application principale.
    """
    # Créer l'application
    app = MainApplication()
    
    # Lancer la boucle principale Tkinter
    app.mainloop()


if __name__ == "__main__":
    main()
