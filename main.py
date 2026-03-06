from views.home_view import HomeView
# Dans le fichier Projet_IA/main.py
from jeux_1.main import MatchstickApp

class MainApplication(tk.Tk):
    # ...
    def on_game_selected(self, game_name: str) -> None:
        if game_name == "matchstick":
            # On délègue la gestion au module du jeu spécifique
            self.current_game_app = MatchstickApp(self)
            self.current_game_app.show_menu()