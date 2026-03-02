"""
Point d'entrée principal de l'application.
"""

import tkinter as tk
from player import Player, Human, AI
from game_model import GameModel
from game_controller import GameController
from views.home_view import HomeView
from views.matchstick_menu_view import MatchstickMenuView
from views.game_view import GameView
from views.training_view import TrainingView
# from language_manager import lang_manager


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Collection")
        self.geometry("900x700")
        self.configure(bg="#F5F7FA")
        self.current_view = None
        self.show_home()
    
    def clear_view(self) -> None:
        """Supprime la vue actuellement affichée."""
        if self.current_view:
            # AJOUT : Désenregistrer la vue du gestionnaire de langue avant destruction
            from language_manager import lang_manager
            lang_manager.unregister_observer(self.current_view)
            
            self.current_view.pack_forget()
            self.current_view.destroy()
            self.current_view = None
    
    def show_home(self) -> None:
        self.clear_view()
        self.current_view = HomeView(self, on_game_selected=self.on_game_selected)
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def on_game_selected(self, game_name: str) -> None:
        if game_name == "matchstick":
            self.show_matchstick_menu()
    
    def show_matchstick_menu(self) -> None:
        self.clear_view()
        self.current_view = MatchstickMenuView(
            self, on_play_selected=self.on_play_selected,
            on_train_selected=self.show_training, on_back=self.show_home
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def on_play_selected(self, mode: str) -> None:
        human = Human("Player 1")
        if mode == "ai1":
            opponent = AI("AI 1", epsilon=0.1)
            try: opponent.download("AI_save_1")
            except: pass
        elif mode == "ai2":
            opponent = AI("AI 2", epsilon=0.1)
            try: opponent.download("AI_save_2")
            except: pass
        else:
            opponent = Player("Random Bot")
        self.start_game(human, opponent)
    
    def start_game(self, p1: Player, p2: Player) -> None:
        self.clear_view()
        self.game_controller = GameController(p1, p2, 15, on_quit=self.show_matchstick_menu)
        game_view = GameView(self, self.game_controller)
        self.game_controller.set_view(game_view)
        self.current_view = game_view
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def show_training(self, target: str) -> None:
        self.clear_view()
        self.current_view = TrainingView(
            self, ai_target=target,
            on_start_training=lambda nb, dec, lr, opp: self.start_training(target, nb, dec, lr, opp),
            on_back=self.show_matchstick_menu
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def start_training(self, target, nb, decay, lr, opp_type) -> None:
        # L'IA élève (celle qui apprend)
        student = AI("AI Student", epsilon=0.9, learning_rate=lr)
        save_name = "AI_save_1" if target == "ai1" else "AI_save_2"
        
        # Charger l'état actuel de l'élève s'il existe
        try: student.download(save_name)
        except: pass

        # L'adversaire
        if opp_type == "random":
            opponent = Player("Random")
        else:
            opp_save = "AI_save_2" if target == "ai1" else "AI_save_1"
            opponent = AI("AI Opponent", epsilon=0.1) # L'adversaire explore peu
            try: opponent.download(opp_save)
            except: pass
        
        training_game = GameModel(12, student, opponent, displayable=False)
        
        for i in range(nb):
            if i % decay == 0 and i > 0:
                student.next_epsilon()
            
            training_game.play()
            student.train()
            # On n'entraîne pas l'adversaire ici, seul l'élève apprend
            
            training_game.reset()
            if i % 1000 == 0 or i == nb - 1:
                self.current_view.update_progress(i + 1, nb)
        
        self.current_view.show_results(
            student.nb_wins, 
            opponent.nb_wins if hasattr(opponent, 'nb_wins') else 0, 
            nb, 
            on_save_callback=lambda: student.upload(save_name)
        )


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()