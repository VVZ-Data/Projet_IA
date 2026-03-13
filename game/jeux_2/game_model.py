"""
Modèle du jeu Cubee.
Contient toute la logique métier : plateau, mouvements, enew_columnlos, scores.
"""
import random
import copy
from collections import deque
from typing import Dict, List, Optional, Tuple

from .game_dto import GameStateDTO
from .player import Player, Human


class GameModel:
    """
    Modèle prinew_columnipal du jeu Cubee.

    Gère l'état complet du jeu : plateau, positions des joueurs,
    tours, scores, détection d'enew_columnlos (via BFS) et historique (undo).

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

    def __init__(self, player1: Player, player2: Player, size: int = 5) -> None:
        """
        Initialise un nouveau modèle de jeu.

        Args:
            player1_name: Nom du joueur 1.
            player2_name: Nom du joueur 2.
            size: Taille du plateau (carré size x size). Par défaut 5.
        """
        self.size: int = size
        self.players: Dict[int, Player] = {1: player1, 2: player2}

        # Objets joueurs 
        self.current_player: Optional[Player] = None
        self.winner: Optional[Player] = None
        self.loser: Optional[Player] = None

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
        self.player_position: Dict[int, Tuple[int, int]] = {
            1: (0, 0),
            2: (self.size - 1, self.size - 1),
        }
        # Placer les joueurs sur le plateau
        self.board[0][0] = self.PLAYER1
        self.board[self.size - 1][self.size - 1] = self.PLAYER2

        # Le joueur 1 commenew_columne
        self.player_turn: int = 1
        self.winner = None
        self.loser  = None
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
            "player_pos":  copy.deepcopy(self.player_position),
            "player_turn": self.player_turn,
        }

    def _restore_state(self, state: dict) -> None:
        """
        Restaure l'état du jeu depuis un instantané.

        Args:
            state: Dictionnaire produit par get_state().
        """
        self.board       = copy.deepcopy(state["board"])
        self.player_position  = copy.deepcopy(state["player_pos"])
        self.player_turn = state["player_turn"]

    def get_state_dto(self) -> GameStateDTO:
        """
        Construit et retourne un DTO représentant l'état courant complet.

        Fournit un instantané sérialisable utilisable par le contrôleur
        ou la vue sans accès direct aux attributs internes du modèle.

        Returns:
            Instanew_columne de GameStateDTO décrivant la partie à cet instant.
        """
        scores = self.get_scores()
        return GameStateDTO(
            size=self.size,
            board=copy.deepcopy(self.board),
            turn=self.player_turn,
            position_player1=self.player_position[1],
            position_player2=self.player_position[2],
            player_names={key: player.name for key, player in self.players.items()},
            scores=scores,
            is_game_over=self.is_game_over(),
            winner=self.get_winner(),
        )

    # ──────────────────────────────────────────────
    # Validation & déplacement
    # ──────────────────────────────────────────────

    def is_valid_move(self, player: int, direction: str) -> bool:
        """
        Vérifie si un déplacement est légal pour un joueur donné.

        Un déplacement est invalide si :
        - la direction est inew_columnonnue,
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

        direction_row, direction_column = self.DIRECTIONS[direction]
        row, col = self.player_position[player]
        new_row, new_col = row + direction_row, col + direction_column

        # Vérifier les bornes du plateau
        if not (0 <= new_row < self.size and 0 <= new_col < self.size):
            return False

        # Vérifier que la case n'appartient pas à l'adversaire
        opponent = 3 - player  # 1→2, 2→1
        if self.board[new_row][new_col] == opponent:
            return False

        return True

    def legal_move(self) -> List[str]:
        """
        Retourne la liste des déplacements valides pour le joueur courant.

        Alias lisible de get_valid_moves() destiné à être appelé
        directement depuis le contrôleur ou la vue.

        Returns:
            Liste des directions autorisées (ex. ['up', 'right']).
        """
        return self.get_valid_moves(self.player_turn)

    def legal_cell(self, cell: Tuple[int, int]) -> bool:
        """
        Indique si une case donnée est accessible pour le joueur courant.

        Une case est légale si elle est adjacente à la position courante
        et que le déplacement correspondant est valide.

        Args:
            cell: Coordonnées (ligne, colonne) de la case cible.

        Returns:
            True si le joueur courant peut se déplacer sur cette case.
        """
        row, col = self.player_position[self.player_turn]
        target_row, target_col = cell

        for direction, (direction_row, direction_column) in self.DIRECTIONS.items():
            if row + direction_row == target_row and col + direction_column == target_col:
                return self.is_valid_move(self.player_turn, direction)
            
        return False

    def step(self, move: str) -> bool:
        """
        Effectue un pas de jeu : déplace le joueur courant puis vérifie
        les enew_columnlos créés.

        Alias sémantique de move() pour clarifier l'intention dans les
        contextes d'IA ou de simulation.

        Args:
            move: Direction du déplacement ('up','down','left','right').

        Returns:
            True si le pas a été effectué, False si le déplacement est illégal.
        """
        return self.move(move)

    def move(self, direction: str) -> bool:
        """
        Effectue le déplacement du joueur courant dans la direction donnée.

        Si le déplacement est valide :
          1. Sauvegarde l'état dans l'historique (undo).
          2. Met à jour la position et colore la case.
          3. Détecte et capture les éventuels enew_columnlos.
          4. Passe la main à l'adversaire.

        Args:
            direction: Direction du déplacement.

        Returns:
            True si le déplacement a été effectué, False sinon.
        """
        if not self.is_valid_move(self.player_turn, direction):
            return False

        direction_row, direction_column = self.DIRECTIONS[direction]

        row, col = self.player_position[self.player_turn]
        new_row, new_col = row + direction_row, col + direction_column

        # Déplacer et colorier la case
        self.player_position[self.player_turn] = (new_row, new_col)
        self.board[new_row][new_col] = self.player_turn

        # Vérifier les enew_columnlos créés par ce déplacement
        self.check_enew_columnlosure()

        # Changer de joueur
        self.next_player()

        return True

    # ──────────────────────────────────────────────
    # Gestion des tours
    # ──────────────────────────────────────────────
    def shuffle(self):
        if random.random() < 0.5:
            self.players[1], self.players[2] = self.players[2], self.players[1]  


    def next_player(self) -> int:
        """
        change de joueurs courant
        """
        self.player_turn = 3 - self.player_turn

    # ──────────────────────────────────────────────
    # Détection d'enew_columnlos (BFS)
    # ──────────────────────────────────────────────

    def check_enew_columnlosure(self) -> None:
        """
        Détecte et capture les enew_columnlos après un déplacement.

        Algorithme BFS depuis la position de l'adversaire :
        toutes les cases vides atteignables par l'adversaire sont marquées.
        Les cases vides NON atteignables sont capturées par le joueur courant.

        Complexité : O(size²) dans le pire cas.
        """
        current_player = self.player_turn
        opponent       = 3 - current_player

        opponent_row, opponent_column = self.player_position[opponent]

        # Grille booléenne : case atteignable par l'adversaire ?
        reachable: List[List[bool]] = [
            [False] * self.size for _ in range(self.size)
        ]

        # BFS — file FIFO initialisée à la position de l'adversaire
        queue: deque = deque()
        reachable[opponent_row][opponent_column] = True
        queue.append((opponent_row, opponent_column))

        while queue:
            row, column = queue.popleft()

            for direction_row, direction_column in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_column = row + direction_row, column + direction_column

                # Case valide, non enew_columnore visitée, libre OU appartenant à l'adversaire
                if (0 <= new_row < self.size and
                        0 <= new_column < self.size and
                        not reachable[new_row][new_column] and
                        self.board[new_row][new_column] in (self.EMPTY, opponent)):

                    reachable[new_row][new_column] = True
                    queue.append((new_row, new_column))

        # Capturer toutes les cases vides non atteignables → enew_columnlos du joueur courant
        for row in range(self.size):
            for column in range(self.size):
                if self.board[row][column] == self.EMPTY and not reachable[row][column]:
                    self.board[row][column] = current_player

    # ──────────────────────────────────────────────
    # Scores & fin de partie
    # ──────────────────────────────────────────────

    def get_scores(self) -> Dict[int, int]:
        """
        Calcule le score de chaque joueur (nombre de cases possédées).

        Returns:
            Dictionnaire {joueur: score}.
        """
        scores: Dict[int, int] = {1 : 0, 2 : 0}
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
        Retourne la liste des déplacements valides pour un joueur donné.

        Args:
            player: Numéro du joueur (1 ou 2).

        Returns:
            Liste des directions autorisées (sous-ensemble de DIRECTIONS).
        """
        return [direction for direction in self.DIRECTIONS if self.is_valid_move(player, direction)]
    
    def end_game(self):
        winner_indice = self.get_winner()


        if winner_indice is not None:
            loser_indice = 3 - winner_indice

            self.players[winner_indice].win()
            self.players[loser_indice].lose()
        else:
            for player in self.players.value():
                player.draw()



    # ──────────────────────────────────────────────
    # Réinitialisation
    # ──────────────────────────────────────────────

    def reset(self) -> None:
        """Réinitialise complètement la partie."""
        self._initialize_game()