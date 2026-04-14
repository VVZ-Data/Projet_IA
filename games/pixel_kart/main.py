"""
Point d'entrée du jeu Pixel Kart.

Architecture (identique à games/allumette/main.py) :
    - PixelKartApp(tk.Tk) : fenêtre unique avec une vue courante (Frame)
    - clear_view + show_xxx() : navigation entre les vues
    - GameController : logique d'une course en cours

Vues :
    - PixelKartMenuView : menu principal (Play / Training)
    - PixelKartRaceView : course en cours
"""

import tkinter as tk

from language_manager import lang_manager
from .game_controller import GameController
from .game_model import Circuit, Race
from .player import Human, RandomAI
from .views.menu_view import PixelKartMenuView
from .views.race_view import PixelKartRaceView
from .editor import map_dao


class PixelKartApp(tk.Tk):
    """
    Application principale du jeu Pixel Kart.

    Gère la navigation entre :
    - le menu principal (PixelKartMenuView)
    - la course (PixelKartRaceView) via GameController
    - le retour à la sélection des jeux (page d'accueil)
    """

    def __init__(self):
        super().__init__()
        self.title("Pixel Kart")
        self.geometry("1200x720")
        self.configure(bg="#F5F7FA")

        self.current_view = None
        self.game_controller: GameController | None = None

        self.show_menu()

    # ---------- Navigation ----------

    def clear_view(self) -> None:
        """Détruit la vue courante en se désabonnant du gestionnaire de langue."""
        if self.current_view is not None:
            lang_manager.unregister_observer(self.current_view)
            self.current_view.pack_forget()
            self.current_view.destroy()
            self.current_view = None
        self.game_controller = None

    def show_menu(self) -> None:
        """Affiche le menu principal du jeu."""
        self.clear_view()
        self.current_view = PixelKartMenuView(
            self,
            on_play_selected=self._on_play_selected,
            on_back=self._quit_to_home,
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _on_play_selected(self, config: dict) -> None:
        """
        Crée une course en fonction de la config et affiche la vue de course.

        config : {"mode": "solo"|"ai"|"human", "circuit": str, "nb_turns": int}
        """
        circuits = map_dao.get_all()
        raw = circuits.get(config["circuit"])
        if raw is None:
            print(f"Circuit '{config['circuit']}' introuvable.")
            return

        circuit = Circuit(name=config["circuit"], raw=raw)

        if config["mode"] == "solo":
            karts = [Human("Bob")]
        elif config["mode"] == "ai":
            karts = [Human("Bob"), RandomAI("Randy")]
        else:  # human vs human
            karts = [Human("Bob"), Human("Alice")]

        race = Race(circuit=circuit, karts=karts, nb_turns=config["nb_turns"])
        self._start_race(race)

    def _start_race(self, race: Race) -> None:
        """Affiche la vue de course et instancie le contrôleur."""
        self.clear_view()

        self.game_controller = GameController(
            race=race,
            on_quit=self.show_menu,
        )

        race_view = PixelKartRaceView(
            self,
            race=race,
            on_action=self.game_controller.handle_action,
            on_back=self.game_controller.handle_quit,
        )
        self.game_controller.set_view(race_view)

        self.current_view = race_view
        self.current_view.pack(fill=tk.BOTH, expand=True)

        # Lancer le premier tour si le 1er kart est une IA
        self.game_controller.start()

    # ---------- Sortie vers l'accueil ----------

    def _quit_to_home(self) -> None:
        """Ferme cette fenêtre et relance le main racine (sélection des jeux)."""
        self.destroy()
        import main as root_main
        root_main.main()


def run_game() -> None:
    """Point d'entrée appelé par le main racine quand on choisit Pixel Kart."""
    app = PixelKartApp()
    app.mainloop()


if __name__ == "__main__":
    run_game()
