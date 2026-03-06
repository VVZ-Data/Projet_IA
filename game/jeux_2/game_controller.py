"""
Contrôleur du jeu Cubee.
Fait le lien entre GameModel (logique métier) et GameView (interface graphique).
"""

from .game_model import GameModel
from .game_view import GameView


class GameController:
    """
    Contrôleur principal du jeu Cubee.

    Reçoit les actions de l'utilisateur depuis la Vue,
    délègue la logique au Modèle, puis rafraîchit la Vue.
    Il ne contient ni logique de jeu, ni code d'affichage.
    """

    def __init__(
        self,
        player1_name: str = "Player 1",
        player2_name: str = "Player 2",
        size: int = 5
    ) -> None:
        """
        Initialise le contrôleur, le modèle et la vue.

        Args:
            player1_name: Nom du joueur 1 (par défaut "Player 1").
            player2_name: Nom du joueur 2 (par défaut "Player 2").
            size:         Taille du plateau (par défaut 5).
        """
        self.model = GameModel(player1_name, player2_name, size)
        self.view  = GameView(self)
        # Premier affichage
        self._refresh_view()

    # ──────────────────────────────────────────────────────────────────────────
    # Gestionnaires d'actions (appelés par la Vue)
    # ──────────────────────────────────────────────────────────────────────────

    def handle_move(self, direction: str) -> None:
        """
        Traite une demande de déplacement du joueur courant.

        Si la partie est terminée, ignore l'action.
        Si le déplacement est invalide, déclenche un feedback visuel.
        Sinon, effectue le coup et vérifie la fin de partie.

        Args:
            direction: Direction souhaitée ('up','down','left','right').
        """
        # Ignorer les actions si la partie est finie
        if self.model.is_game_over():
            return

        success = self.model.move(direction)

        if not success:
            # Mouvement interdit → flash rouge dans la vue
            self.view.flash_invalid_move()
        else:
            self._refresh_view()
            # Vérifier si la partie vient de se terminer
            if self.model.is_game_over():
                winner = self.model.get_winner()
                winner_name = (
                    self.model.player_names[winner] if winner else None
                )
                # Décaler légèrement pour laisser le dessin se finaliser
                self.view.after(200, lambda: self.view.show_game_over(winner_name))



    def handle_new_game(self) -> None:
        """Réinitialise le modèle et rafraîchit la vue pour une nouvelle partie."""
        self.model.reset()
        self._refresh_view()

    # ──────────────────────────────────────────────────────────────────────────
    # Rafraîchissement de la Vue
    # ──────────────────────────────────────────────────────────────────────────

    def _refresh_view(self) -> None:
        """
        Synchronise la Vue avec l'état courant du Modèle.

        Met à jour le plateau et les scores.
        """
        self.view.update_board(
            self.model.board,
            self.model.player_pos,
            self.model.size
        )
        self.view.update_scores(
            self.model.get_scores(),
            self.model.player_turn,
            self.model.player_names
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Lancement de l'application
    # ──────────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Lance la boucle principale Tkinter via la Vue."""
        self.view.run()