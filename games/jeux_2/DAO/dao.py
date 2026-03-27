"""
Objet de transfert de données (DTO) du jeu Cubee.

Fournit un instantané sérialisable de l'état complet de la partie,
utilisé pour la communication entre le modèle et la vue,
ainsi que pour la sauvegarde / l'historique (undo).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class GameStateDTO:
    """
    DTO représentant l'état complet d'une partie Cubee à un instant donné.

    Utilisé par GameModel.get_state_dto() et GameController.get_state_dto()
    pour transmettre l'état à la vue ou à d'autres composants sans exposer
    directement les internals du modèle.

    Attributes:
        size:         Dimension du plateau (size × size).
        board:        Matrice d'entiers représentant les cases
                      (0 = vide, 1 = joueur 1, 2 = joueur 2).
        turn:         Numéro du joueur dont c'est le tour (1 ou 2).
        pos_p1:       Position (ligne, colonne) du joueur 1.
        pos_p2:       Position (ligne, colonne) du joueur 2.
        player_name:  Dictionaire {numéro: nom} 
        scores:       Dictionnaire {numéro_joueur: score}.
        is_game_over: True si la partie est terminée.
        winner:       Numéro du gagnant (1 ou 2), ou None si égalité / en cours.
    """

    size: int
    board: List[List[int]]
    turn: int
    position_player1: Tuple[int, int]
    position_player2: Tuple[int, int]
    player_names: Dict[int, str] = field(default_factory=lambda: {1 : "Player1", 2 : "Player2"})
    scores: Dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0})
    is_game_over: bool = False
    winner: Optional[int] = None

    def to_dict(self) -> dict:
        """
        Sérialise le DTO en dictionnaire JSON-compatible.

        Returns:
            Dictionnaire représentant l'état complet de la partie.

        Example:
            >>> dto.to_dict()
            {
                "size": 3,
                "board": "110002002",
                "turn": 4,
                "position_player1": (0, 1),
                "position_player2": (1, 2),
                ...
            }
        """
        return {
            "size":         self.size,
            # Plateau aplati en chaîne pour la sérialisation compacte
            "board":        "".join(str(cell) for row in self.board for cell in row),
            "turn":         self.turn,
            "position_player1":       list(self.posistion_player1),
            "position_player2":       list(self.posistion_player2),
            "player_names": {str(k): v for k, v in self.player_name.items()},
            "scores":       {str(k): v for k, v in self.scores.items()},
            "is_game_over": self.is_game_over,
            "winner":       self.winner,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameStateDTO":
        """
        Désérialise un dictionnaire (produit par to_dict) en GameStateDTO.

        Args:
            data: Dictionnaire tel que retourné par to_dict().

        Returns:
            Instance de GameStateDTO reconstituée.
        """
        size = data["size"]
        flat = data["board"]
        board = [
            [int(flat[row * size + column]) for column in range(size)]
            for row in range(size)
        ]
        return cls(
            size=size,
            board=board,
            turn=data["turn"],
            position_player1=tuple(data["position_player1"]),
            position_player2=tuple(data["position_player2"]),
            player_names={int(k): p for k, p in data["player_names"].items()},
            scores={int(k): v for k, v in data["scores"].items()},
            is_game_over=data.get("is_game_over", False),
            winner=data.get("winner"),
        )