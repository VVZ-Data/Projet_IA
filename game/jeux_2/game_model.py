"""
Modèle du jeu Cubee.
Contient toute la logique métier : plateau, mouvements, enclos, scores.
"""

import copy
from collections import deque
from typing import Dict, List, Optional, Tuple


class GameModel:
    """
    Modèle principal du jeu Cubee.

    Gère l'état complet du jeu : plateau, positions des joueurs,
    tours, scores, détection d'enclos (via BFS) et historique (undo).

    Le plateau est représenté par une matrice :
        0 = case vide
        1 = case joueur 1
        2 = case joueur 2
    """

    EMPTY: int = 0
    PLAYER1: int = 1
    PLAYER2: int = 2

    # Déplacements possibles (delta_ligne, delta_colonne)
    DIRECTIONS: Dict[str, Tuple[int, int]] = {
        "up":    (-1,  0),
        "down":  ( 1,  0),
        "left":  ( 0, -1),
        "right": ( 0,  1),
    }

    def __init__(self, player1_name: str, player2_name: str, size: int = 5) -> None:
        """
        Initialise un nouveau modèle de jeu.

        Args:
            player1_name: Nom du joueur 1.
            player2_name: Nom du joueur 2.
            size: Taille du plateau (carré size x size). Par défaut 5.
        """
        self.size: int = size
        self.player_names: Dict[int, str] = {1: player1_name, 2: player2_name}
        # Historique des états pour le bouton "Undo"
        self.history: List[dict] = []
        self._initialize_game()

    # ──────────────────────────────────────────────
    # Initialisation
    # ──────────────────────────────────────────────

    def _initialize_game(self) -> None:
        """
        Initialise (ou réinitialise) le plateau et les positions de départ.
        Joueur 1 → coin supérieur gauche  (0, 0)
        Joueur 2 → coin inférieur droit   (size-1, size-1)
        """
        # Plateau vide
        self.board: List[List[int]] = [
            [self.EMPTY] * self.size for _ in range(self.size)
        ]
        # Positions initiales des joueurs
        self.player_pos: Dict[int, Tuple[int, int]] = {
            1: (0, 0),
            2: (self.size - 1, self.size - 1),
        }
        # Placer les joueurs sur le plateau
        self.board[0][0] = self.PLAYER1
        self.board[self.size - 1][self.size - 1] = self.PLAYER2

        # Le joueur 1 commence
        self.player_turn: int = 1
        # Vider l'historique
        self.history = []

    # ──────────────────────────────────────────────
    # Sérialisation d'état (pour l'historique undo)
    # ──────────────────────────────────────────────

    def get_state(self) -> dict:
        """
        Retourne une copie profonde de l'état courant.

        Returns:
            Dictionnaire contenant board, player_pos et player_turn.
        """
        return {
            "board":       copy.deepcopy(self.board),
            "player_pos":  copy.deepcopy(self.player_pos),
            "player_turn": self.player_turn,
        }

    def _restore_state(self, state: dict) -> None:
        """
        Restaure l'état du jeu depuis un instantané.

        Args:
            state: Dictionnaire produit par get_state().
        """
        self.board       = copy.deepcopy(state["board"])
        self.player_pos  = copy.deepcopy(state["player_pos"])
        self.player_turn = state["player_turn"]

    # ──────────────────────────────────────────────
    # Validation & déplacement
    # ──────────────────────────────────────────────

    def is_valid_move(self, player: int, direction: str) -> bool:
        """
        Vérifie si un déplacement est légal pour un joueur donné.

        Un déplacement est invalide si :
        - la direction est inconnue,
        - la destination sort du plateau,
        - la destination appartient à l'adversaire.

        Args:
            player:    Numéro du joueur (1 ou 2).
            direction: Direction souhaitée ('up','down','left','right').

        Returns:
            True si le déplacement est autorisé, False sinon.
        """
        if direction not in self.DIRECTIONS:
            return False

        dr, dc = self.DIRECTIONS[direction]
        row, col = self.player_pos[player]
        new_row, new_col = row + dr, col + dc

        # Vérifier les bornes du plateau
        if not (0 <= new_row < self.size and 0 <= new_col < self.size):
            return False

        # Vérifier que la case n'appartient pas à l'adversaire
        opponent = 3 - player  # 1→2, 2→1
        if self.board[new_row][new_col] == opponent:
            return False

        return True

    def move(self, direction: str) -> bool:
        """
        Effectue le déplacement du joueur courant dans la direction donnée.

        Si le déplacement est valide :
          1. Sauvegarde l'état dans l'historique (undo).
          2. Met à jour la position et colore la case.
          3. Détecte et capture les éventuels enclos.
          4. Passe la main à l'adversaire.

        Args:
            direction: Direction du déplacement.

        Returns:
            True si le déplacement a été effectué, False sinon.
        """
        if not self.is_valid_move(self.player_turn, direction):
            return False

        # Sauvegarder l'état avant de jouer (pour le undo)
        self.history.append(self.get_state())

        dr, dc = self.DIRECTIONS[direction]
        row, col = self.player_pos[self.player_turn]
        new_row, new_col = row + dr, col + dc

        # Déplacer et colorier la case
        self.player_pos[self.player_turn] = (new_row, new_col)
        self.board[new_row][new_col] = self.player_turn

        # Vérifier les enclos créés par ce déplacement
        self.check_enclosure()

        # Changer de joueur
        self.player_turn = 3 - self.player_turn

        return True

    # ──────────────────────────────────────────────
    # Détection d'enclos (BFS)
    # ──────────────────────────────────────────────

    def check_enclosure(self) -> None:
        """
        Détecte et capture les enclos après un déplacement.

        Algorithme BFS depuis la position de l'adversaire :
        toutes les cases vides atteignables par l'adversaire sont marquées.
        Les cases vides NON atteignables sont capturées par le joueur courant.

        Complexité : O(size²) dans le pire cas.
        """
        current_player = self.player_turn
        opponent       = 3 - current_player

        opp_row, opp_col = self.player_pos[opponent]

        # Grille booléenne : case atteignable par l'adversaire ?
        reachable: List[List[bool]] = [
            [False] * self.size for _ in range(self.size)
        ]

        # BFS — file FIFO initialisée à la position de l'adversaire
        queue: deque = deque()
        reachable[opp_row][opp_col] = True
        queue.append((opp_row, opp_col))

        while queue:
            r, c = queue.popleft()

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc

                # Case valide, non encore visitée, libre OU appartenant à l'adversaire
                if (0 <= nr < self.size and
                        0 <= nc < self.size and
                        not reachable[nr][nc] and
                        self.board[nr][nc] in (self.EMPTY, opponent)):

                    reachable[nr][nc] = True
                    queue.append((nr, nc))

        # Capturer toutes les cases vides non atteignables → enclos du joueur courant
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == self.EMPTY and not reachable[r][c]:
                    self.board[r][c] = current_player

    # ──────────────────────────────────────────────
    # Scores & fin de partie
    # ──────────────────────────────────────────────

    def get_scores(self) -> Dict[int, int]:
        """
        Calcule le score de chaque joueur (nombre de cases possédées).

        Returns:
            Dictionnaire {joueur: score}.
        """
        scores: Dict[int, int] = {1: 0, 2: 0}
        for row in self.board:
            for cell in row:
                if cell in scores:
                    scores[cell] += 1
        return scores

    def is_game_over(self) -> bool:
        """
        Vérifie si la partie est terminée.

        La partie se termine quand :
        - il ne reste plus de case vide, OU
        - le joueur courant n'a plus aucun déplacement possible.

        Returns:
            True si la partie est terminée.
        """
        # Plus de cases vides
        for row in self.board:
            if self.EMPTY in row:
                break
        else:
            return True

        # Le joueur courant n'a plus de coup légal
        if not self.get_valid_moves(self.player_turn):
            return True

        return False

    def get_winner(self) -> Optional[int]:
        """
        Retourne le gagnant de la partie.

        Returns:
            Numéro du joueur gagnant (1 ou 2), ou None en cas d'égalité.
        """
        scores = self.get_scores()
        if scores[1] > scores[2]:
            return 1
        if scores[2] > scores[1]:
            return 2
        return None  # Égalité

    def get_valid_moves(self, player: int) -> List[str]:
        """
        Retourne la liste des déplacements valides pour un joueur.

        Args:
            player: Numéro du joueur.

        Returns:
            Liste des directions autorisées.
        """
        return [d for d in self.DIRECTIONS if self.is_valid_move(player, d)]

    # ──────────────────────────────────────────────
    # Undo & reset
    # ──────────────────────────────────────────────

    def undo(self) -> bool:
        """
        Annule le dernier déplacement (bouton "Undo").

        Returns:
            True si l'annulation a réussi, False si l'historique est vide.
        """
        if not self.history:
            return False
        self._restore_state(self.history.pop())
        return True

    def reset(self) -> None:
        """Réinitialise complètement la partie."""
        self._initialize_game()