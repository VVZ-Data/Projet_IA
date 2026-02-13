"""
Module contenant les classes Player et Human pour le jeu des allumettes.
"""
import random


class Player:
    """
    Représente un joueur de base (random) dans le jeu des allumettes.

    Attributes:
        name (str): Le nom du joueur.
        game: La partie en cours (None par défaut).
        nb_wins (int): Nombre de victoires.
        nb_loses (int): Nombre de défaites.
    """

    def __init__(self, name: str, game=None) -> None:
        """
        Initialise un joueur avec un nom et une partie optionnelle.

        Args:
            name (str): Le nom du joueur.
            game: La partie associée au joueur (None par défaut).
        """
        self.name = name
        self.game = game
        self.nb_wins: int = 0
        self.nb_loses: int = 0

    @property
    def nb_games(self) -> int:
        """
        Retourne le nombre total de parties jouées.

        Returns:
            int: Somme des victoires et des défaites.
        """
        return self.nb_wins + self.nb_loses

    @staticmethod
    def play() -> int:
        """
        Choisit aléatoirement un nombre d'allumettes entre 1 et 3.

        Returns:
            int: Un entier aléatoire entre 1 et 3 inclus.
        """
        return random.randint(1, 3)

    def win(self) -> None:
        """
        Incrémente le compteur de victoires du joueur.
        """
        self.nb_wins += 1

    def lose(self) -> None:
        """
        Incrémente le compteur de défaites du joueur.
        """
        self.nb_loses += 1

    def __str__(self) -> str:
        """
        Retourne une représentation textuelle du joueur.

        Returns:
            str: Nom du joueur et ses statistiques.
        """
        return (
            f"{self.name} | Wins: {self.nb_wins} | "
            f"Loses: {self.nb_loses} | Games: {self.nb_games}"
        )


class Human(Player):
    """
    Représente un joueur humain qui saisit son choix via l'interface.

    Hérite de Player et redéfinit uniquement la méthode play()
    pour une utilisation en mode console (hors interface graphique).
    """

    def play(self) -> int:
        """
        Demande à l'humain de choisir un nombre d'allumettes (1 à 3) en console.

        Returns:
            int: Le choix valide de l'utilisateur entre 1 et 3.
        """
        # Boucle jusqu'à obtenir un choix valide
        while True:
            try:
                choice = int(input("How many matches do you want to take? (1, 2 or 3): "))
                if choice in (1, 2, 3):
                    return choice
                print("Please enter 1, 2 or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")
