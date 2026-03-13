"""
Contrôleur du jeu Cubee.
Fait le lien entre GameModel (logique métier) et GameView (interface graphique).
"""

from typing import Optional

from .game_dto import GameStateDTO
from .game_model import GameModel
from .game_view import GameView
from .player import Player, Human


class GameController:
    """
    Contrôleur principal du jeu Cubee.

    Reçoit les actions de l'utilisateur depuis la Vue,
    délègue la logique au Modèle, puis rafraîchit la Vue.

    Si le joueur courant est un Player (IA), son coup est déclenché
    automatiquement. Si c'est un Human, on attend l'input clavier/bouton.
    """

    def __init__(
        self,
        player1: Player,
        player2: Player,
        size: int = 5
    ) -> None:
        """
        Initialise le contrôleur, le modèle et la vue.

        Args:
            player1: Joueur 1 — instance de Player (IA) ou Human.
            player2: Joueur 2 — instance de Player (IA) ou Human.
            size:    Taille du plateau (par défaut 5).

        Example:
            # Humain vs IA
            GameController(Human("Alice"), Player("Bot")).run()

            # IA vs IA
            GameController(Player("Bot 1"), Player("Bot 2")).run()

            # Humain vs Humain
            GameController(Human("Alice"), Human("Bob")).run()
        """
        self.players = {1: player1, 2: player2}
        self.model = GameModel(player1, player2, size)

        # Lier chaque joueur au modèle pour que play() fonctionne
        player1.game = self.model
        player2.game = self.model

        self.view = GameView(self)
        self._refresh_view()

        # Déclencher l'IA si le premier joueur n'est pas humain
        self._maybe_ia_move()

    # ──────────────────────────────────────────────────────────────────────────
    # Démarrage & réinitialisation
    # ──────────────────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Démarre une nouvelle partie et lance la boucle Tkinter."""
        self.model.shuffle()
        self.model.reset()
        self._refresh_view()
        self.run()

    def handle_new_game(self) -> None:
        """Réinitialise le modèle et rafraîchit la vue pour une nouvelle partie."""
        self.model.shuffle()
        self.model.reset()
        self._refresh_view()
        self._maybe_ia_move()

    # ──────────────────────────────────────────────────────────────────────────
    # Gestionnaires d'actions
    # ──────────────────────────────────────────────────────────────────────────

    def handle_move(self, direction: str) -> None:
        """
        Traite un déplacement manuel (clavier/bouton).

        Ignoré si le joueur courant est une IA ou si la partie est finie.

        Args:
            direction: Direction souhaitée ('up','down','left','right').
        """
        if self.model.is_game_over():
            return

        current = self.model.players[self.model.player_turn]
        if not current.is_human():
            return  # Ce n'est pas le tour d'un humain

        success = self.model.move(direction)
        if not success:
            self.view.flash_invalid_move()
            self.model.next_player()
            self._refresh_view()
            self._maybe_ia_move()
        else:
            self._refresh_view()
            if self.model.is_game_over():
                self.view.after(200, self.handle_end_game)
            else:
                # Vérifier si le joueur suivant est une IA
                self._maybe_ia_move()

    def handle_ia_move(self) -> None:
        """
        Joue automatiquement le coup du joueur courant (IA).

        Appelé par _maybe_ia_move() avec un délai via view.after().
        Enchaîne sur le joueur suivant s'il est aussi une IA.
        """
        if self.model.is_game_over():
            return
        
        current = self.model.players[self.model.player_turn]
        if current.is_human():
            return  # Sécurité : ne pas jouer à la place d'un humain

        success = current.play()
        if not success:
            self.handle_end_game()
            return

        self._refresh_view()

        if self.model.is_game_over():
            self.view.after(200, self.handle_end_game)
        else:
            self._maybe_ia_move()

    def handle_end_game(self) -> None:
        """Gère la fin de partie et affiche le résultat."""
        self.model.end_game()
        winner_id = self.model.get_winner()
        winner_name: Optional[str] = (
            self.model.players[winner_id].name if winner_id else None
        )
        self.view.show_game_over(winner_name)


    # ──────────────────────────────────────────────────────────────────────────
    # Informations d'état
    # ──────────────────────────────────────────────────────────────────────────

    def get_status_message(self) -> str:
        """Retourne le message de statut courant de la partie."""
        if self.model.is_game_over():
            winner_id = self.model.get_winner()
            if winner_id:
                return f"Partie terminée — {self.model.players[winner_id].name} a gagné !"
            return "Partie terminée — Égalité !"
        current_name = self.model.players[self.model.player_turn].name
        return f"Tour de {current_name}."

    def get_state_dto(self) -> GameStateDTO:
        """Retourne un DTO décrivant l'état courant complet de la partie."""
        return self.model.get_state_dto()

    # ──────────────────────────────────────────────────────────────────────────
    # Interne
    # ──────────────────────────────────────────────────────────────────────────

    def _maybe_ia_move(self) -> None:
        """
        Déclenche le coup de l'IA avec un délai si le joueur courant n'est pas humain.

        Utilise view.after() pour ne pas bloquer la boucle Tkinter.
        """
        current = self.model.players[self.model.player_turn]
        if not current.is_human():
            self.view.after(400, self.handle_ia_move)

    def _refresh_view(self) -> None:
        """Synchronise la Vue avec l'état courant du Modèle."""
        dto = self.model.get_state_dto()
        players_positions = {1: (dto.position_player1), 2: (dto.position_player2)}
        self.view.update_board(
            dto.board,
            players_positions,
            dto.size
        )
        self.view.update_scores(
            dto.scores,
            dto.turn,
            dto.player_names
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Lancement
    # ──────────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Lance la boucle principale Tkinter via la Vue."""
        self.view.run()