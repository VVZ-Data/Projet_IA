"""
Module contenant la classe GameController — contrôleur MVC du jeu des allumettes.
"""
from player import Player, Human
from game_model import GameModel
from game_view import GameView


class GameController:
    """
    Contrôleur du jeu des allumettes reliant le modèle et la vue.

    Gère les interactions utilisateur, met à jour le modèle
    et notifie la vue des changements d'état.

    Attributes:
        model (GameModel): Le modèle de jeu.
        view (GameView): L'interface graphique.
    """

    def __init__(self, p1: Player, p2: Player, total_matches: int) -> None:
        """
        Initialise le contrôleur avec deux joueurs et un nombre d'allumettes.

        Precondition: Au moins un des deux joueurs doit être un humain (Human).

        Args:
            p1 (Player): Le premier joueur.
            p2 (Player): Le second joueur.
            total_matches (int): Le nombre d'allumettes de départ.

        Raises:
            ValueError: Si aucun des deux joueurs n'est un humain.
        """
        # Vérifier qu'au moins un joueur est humain
        if not isinstance(p1, Human) and not isinstance(p2, Human):
            raise ValueError("At least one player must be a Human.")

        self.model = GameModel(total_matches, p1, p2, displayable=False)
        self.view = GameView(self)

        # Si l'IA commence, la faire jouer immédiatement
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()

    def start(self) -> None:
        """
        Lance la boucle principale de la fenêtre Tkinter.
        """
        self.view.mainloop()

    def get_nb_matches(self) -> int:
        """
        Retourne le nombre d'allumettes restantes dans le jeu.

        Returns:
            int: Nombre d'allumettes actuelles.
        """
        return self.model.nb

    def get_status_message(self) -> str:
        """
        Retourne un message décrivant l'état actuel du jeu.

        Returns:
            str: Nom du joueur actuel si en cours, ou nom du gagnant si terminé.
        """
        if self.model.is_game_over():
            winner = self.model.get_winner()
            return f"🏆 {winner.name} wins!" if winner else "Game Over"
        current = self.model.get_current_player()
        return f"{current.name}'s turn"

    def reset_game(self) -> None:
        """
        Réinitialise la partie via le modèle et la vue.
        Fait jouer l'IA en premier si elle est joueur actuel après le mélange.
        """
        self.model.reset()
        self.view.reset()

        # Si l'IA commence après le reset, la faire jouer
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()

    def handle_human_move(self, nb: int) -> None:
        """
        Gère le mouvement d'un joueur humain lors d'un clic sur un bouton.

        Args:
            nb (int): Nombre d'allumettes choisies par l'humain (1, 2 ou 3).

        Precondition: Le joueur actuel doit être une instance de Human.
        """
        # Vérifier que c'est bien au tour de l'humain
        if not isinstance(self.model.get_current_player(), Human):
            return

        # Jouer l'étape et vérifier la fin de partie
        self.model.step(nb)
        if self.model.is_game_over():
            self.handle_end_game()
        else:
            self.model.switch_player()
            # Si le joueur suivant est une IA, la faire jouer
            if not isinstance(self.model.get_current_player(), Human):
                self.handle_ai_move()

        self.view.update_view()

    def handle_ai_move(self) -> None:
        """
        Gère le mouvement automatique d'une IA.

        Precondition: Le joueur actuel doit être une IA (Player mais pas Human).
        """
        # Récupérer le coup de l'IA et l'appliquer
        action = self.model.get_current_player().play()
        self.model.step(action)

        if self.model.is_game_over():
            self.handle_end_game()
        else:
            self.model.switch_player()

    def handle_end_game(self) -> None:
        """
        Gère la fin de la partie : met à jour les statistiques
        et signale à la vue d'afficher l'écran de fin.
        """
        winner = self.model.get_winner()
        loser = self.model.get_loser()

        if winner:
            winner.win()
        if loser:
            loser.lose()

        self.view.end_game()
