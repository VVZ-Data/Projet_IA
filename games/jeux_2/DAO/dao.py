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