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
        scores:       Dictionnaire {numéro_joueur: score}.
        player_names: Dictionnaire {numéro_joueur: nom}.
        is_game_over: True si la partie est terminée.
        winner:       Numéro du gagnant (1 ou 2), ou None si égalité / en cours.
    """

    size: int
    board: List[List[int]]
    turn: int
    pos_p1: Tuple[int, int]
    pos_p2: Tuple[int, int]
    scores: Dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0})
    player_names: Dict[int, str] = field(
        default_factory=lambda: {1: "Player 1", 2: "Player 2"}
    )
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
                "pos_p1": [0, 1],
                "pos_p2": [1, 2],
                ...
            }
        """
        return {
            "size":         self.size,
            # Plateau aplati en chaîne pour la sérialisation compacte
            "board":        "".join(str(cell) for row in self.board for cell in row),
            "turn":         self.turn,
            "pos_p1":       list(self.pos_p1),
            "pos_p2":       list(self.pos_p2),
            "scores":       {str(k): v for k, v in self.scores.items()},
            "player_names": {str(k): v for k, v in self.player_names.items()},
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
            [int(flat[r * size + c]) for c in range(size)]
            for r in range(size)
        ]
        return cls(
            size=size,
            board=board,
            turn=data["turn"],
            pos_p1=tuple(data["pos_p1"]),
            pos_p2=tuple(data["pos_p2"]),
            scores={int(k): v for k, v in data["scores"].items()},
            player_names={int(k): v for k, v in data["player_names"].items()},
            is_game_over=data.get("is_game_over", False),
            winner=data.get("winner"),
        )