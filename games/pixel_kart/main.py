"""
Point d'entrée du jeu Pixel Kart.

Appelé par main.py racine via run_game().
"""

from games.pixel_kart.game_controller import GameController


def run_game() -> None:
    """
    Lance le jeu Pixel Kart.

    Crée le contrôleur, qui ouvre le menu de configuration,
    puis la fenêtre de course, puis gère la mainloop Tkinter.
    """
    GameController().run()


if __name__ == "__main__":
    run_game()
