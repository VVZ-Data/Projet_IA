"""
Module contenant la classe GameModel représentant la logique du jeu des allumettes.
"""
import random
from typing import Optional
from player import Player, Human


class GameModel:
    """
    Représente la logique du jeu des allumettes.

    Attributes:
        nb (int): Nombre d'allumettes restantes.
        original_nb (int): Nombre d'allumettes de départ.
        displayable (bool): Indique si le jeu doit afficher son état.
        player1 (Player): Le premier joueur.
        player2 (Player): Le second joueur.
        current_player (int): Indice du joueur actuel (0 ou 1).
    """

    def __init__(
        self,
        nb: int,
        player1: Player,
        player2: Player,
        displayable: bool = True
    ) -> None:
        """
        Initialise une partie avec un nombre d'allumettes et deux joueurs.

        Args:
            nb (int): Nombre d'allumettes au départ.
            player1 (Player): Le premier joueur.
            player2 (Player): Le second joueur.
            displayable (bool): Afficher ou non l'état du jeu (True par défaut).
        """
        self.nb = nb
        self.original_nb = nb
        self.displayable = displayable
        self.player1 = player1
        self.player2 = player2
        self.current_player: int = 0

        # Associer cette partie aux joueurs
        self.player1.game = self
        self.player2.game = self

        self.shuffle()

    @property
    def players(self) -> list:
        """
        Retourne la liste des deux joueurs.

        Returns:
            list: Liste contenant player1 et player2.
        """
        return [self.player1, self.player2]

    def shuffle(self) -> None:
        """
        Mélange aléatoirement l'ordre des joueurs.
        """
        if random.random() < 0.5:
            self.player1, self.player2 = self.player2, self.player1
        self.current_player = 0

    def reset(self) -> None:
        """
        Remet la partie à son état initial et mélange les joueurs.
        """
        self.nb = self.original_nb
        self.shuffle()

    def display(self) -> None:
        """
        Affiche l'état actuel du jeu si displayable est True.
        """
        if self.displayable:
            print(f"\nMatches remaining: {self.nb}")
            print(f"Current player: {self.get_current_player().name}")

    def step(self, action: int) -> None:
        """
        Applique une action (retrait d'allumettes) sur la partie.

        Args:
            action (int): Nombre d'allumettes à retirer (1, 2 ou 3).

        Raises:
            ValueError: Si l'action n'est pas entre 1 et min(3, nb).
        """
        if action < 1 or action > min(3, self.nb):
            raise ValueError(f"Invalid action: {action}. Must be between 1 and {min(3, self.nb)}.")
        self.nb -= action

    def switch_player(self) -> None:
        """
        Passe au joueur suivant en alternant entre 0 et 1.
        """
        self.current_player = 1 - self.current_player

    def is_game_over(self) -> bool:
        """
        Indique si la partie est terminée (plus aucune allumette).

        Returns:
            bool: True si le jeu est terminé, False sinon.
        """
        return self.nb <= 0

    def get_current_player(self) -> Player:
        """
        Retourne le joueur dont c'est le tour.

        Returns:
            Player: Le joueur actuel.
        """
        return self.players[self.current_player]

    def get_winner(self) -> Optional[Player]:
        """
        Retourne le gagnant si la partie est terminée.

        Precondition: is_game_over() doit être True.

        Returns:
            Optional[Player]: Le joueur qui a gagné, ou None si la partie n'est pas finie.
        """
        if not self.is_game_over():
            return None
        # Celui qui a pris la dernière allumette perd — donc l'autre gagne
        return self.players[1 - self.current_player]

    def get_loser(self) -> Optional[Player]:
        """
        Retourne le perdant si la partie est terminée.

        Precondition: is_game_over() doit être True.

        Returns:
            Optional[Player]: Le joueur qui a perdu, ou None si la partie n'est pas finie.
        """
        if not self.is_game_over():
            return None
        # Le joueur actuel a pris la dernière allumette → il perd
        return self.get_current_player()

    def play(self) -> None:
        """
        Lance une partie complète en mode console.
        Appelle win() et lose() sur les joueurs appropriés à la fin.
        """
        self.reset()
        while not self.is_game_over():
            self.display()
            current = self.get_current_player()
            action = current.play()
            self.step(action)
            if not self.is_game_over():
                self.switch_player()

        # Fin de partie
        winner = self.get_winner()
        loser = self.get_loser()
        if winner and loser:
            winner.win()
            loser.lose()
            if self.displayable:
                print(f"\nGame over! {winner.name} wins!")
