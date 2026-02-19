"""
Point d'entrée principal du jeu des allumettes.
Lance une partie avec interface graphique Tkinter.
"""
from player import Player, Human, AI
from game_controller import GameController
from game_model import GameModel


def main() -> None:
    """
    #Point d'entrée du programme. Crée les joueurs, le contrôleur et démarre le jeu.
    """
    # Création des joueurs
    human = Human("Player 1")
    random_bot = AI("Random Bot")

    # Lancement du jeu via le contrôleur (15 allumettes par défaut)
    controller = GameController(human, random_bot, total_matches=15)
    controller.start()


if __name__ == "__main__":
    main()
