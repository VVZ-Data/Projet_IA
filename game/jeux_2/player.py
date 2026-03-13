"""
Représentation d'un joueur du jeu Cubee.
"""
import random
from typing import Optional, Tuple

class Player:
    """
    Représente un joueur dans le jeu Cubee.

    Stocke le nom, la couleur, la position courante sur le plateau,
    ainsi que les statistiques de parties (victoires, défaites, matchs nuls).
    """

    def __init__(self, name: str, game = None):
        """
        Initialise un joueur.

        Args:
            name:  Nom affiché du joueur.
            game:  Référence optionnelle à la partie en cours.
        """
        self.name: str = name
        self.game = game
        self.position: Optional[Tuple[int, int]] = None # (ligne, colonne)
        self.type = "bot"

        #statistique partie
        self.nb_wins: int = 0
        self.nb_loses: int = 0
        self.nb_draws: int = 0

    def win(self) -> None:
        """Incrémente le compteur de victoires du joueur."""
        self.nb_wins += 1

    def lose(self) -> None:
        """Incrémente le compteur de défaites du joueur."""
        self.nb_loses += 1

    def draw(self) -> None:
        """Incrémente le compteur de matchs nuls du joueur."""
        self.nb_draws += 1
    
    # ──────────────────────────────────────────────
    # Jeu
    # ──────────────────────────────────────────────

    def play(self) -> bool:
        """
        Joue un coup aléatoire parmi les déplacements légaux disponibles.

        Returns:
            True si le coup a été joué, False si aucun coup n'est possible.
        """
        if self.game is None:
            return False
        
        # bot qui ne fait que des choix valide
        valid_moves = self.game.legal_move()
        if not valid_moves:
            return False
        return self.game.move(random.choice(valid_moves))
    
        # Bot aléatoire qui peut se tromper (coups valides ET invalides)
        # all_moves = list(self.game.DIRECTIONS.keys())
        # return self.game.move(random.choice(all_moves))

    def is_human(self) -> bool:
        """Retourne False ou True en fonction du type de joueurs."""
        return self.type == "human"



class Human(Player):
    """
    Joueur humain — ne joue pas automatiquement.

    Surcharge play() pour ne rien faire : c'est le contrôleur qui attend
    l'input clavier/bouton et appelle handle_move() à la place.
    """
    def __init__(self, name: str, game=None):
        super().__init__(name, game)
        self.type = "human"
    