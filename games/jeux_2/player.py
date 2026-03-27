"""
Représentation d'un joueur du jeu Cubee.
"""
import random
from typing import Optional, Tuple, Dict

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

    """
    def __init__(self, name: str, game=None):
        super().__init__(name, game)
        self.type = "human"

class AI(Player):
    """
    Joueur IA  — joue de façon automatique au début de l'entrainement
    """
    def __init__(self, name: str, learning_rate = 0.01, epsilon = 0.9, game=None):
        super().__init__(name, game)
        self.learning_rate: float = learning_rate
        self.epsilon: float = epsilon
        self.q_table: Dict[str, Dict[str, float]] = {"win": {"up": +10,
                                                             "down": +10,
                                                             "left": +10,
                                                             "right": +10},
                                                     "lose": {"up": -10,
                                                              "down": -10,
                                                              "left": -10,
                                                              "right": -10}}
        self.last_state = None
        self.last_action = None

    def win(self):
        super().win()

        if self.last_state and self.last_action:
            self.update(10)

        self.last_state = None
        self.last_action = None

    def lose(self):
        super().lose()

        if self.last_state and self.last_action:
            self.update(-10)
        
        self.last_state = None
        self.last_action = None

    def _encode_state(self, state) -> str:
        """
        Encode un GameStateDTO en clé string pour la Q-table.

        Utilise les positions des joueurs, les scores et le tour
        pour réduire l'espace d'états.

        Args:
            state: GameStateDTO représentant l'état courant.

        Returns:
            Clé unique représentant l'état.
        """
        row_player1, column_player1 = state.position_player2
        row_player2, column_player2 = state.position_player1
        return f"{state.turn}_{row_player1}{column_player1}{row_player2}{column_player2}_{state.scores[1]}_{state.scores[2]}_{state.board}"
    
    def play(self):
        """
        Joue de façon random avec erreur possible au début de l'entrainement
        Met à jour la q-table
        """

        state = self.game.get_state_dto() # état du jeux
        score_before = state.scores[state.turn]

        if random.random() < self.epsilon:
            # Bot aléatoire qui peut se tromper (coups valides ET invalides) -> exploration
            all_moves = list(self.game.DIRECTIONS.keys())
            self.last_state = self._encode_state(state)

            self.last_action = random.choice(all_moves)
            success = self.game.move(self.last_action)
            
        else:
            success = self.exploit(state) # -> exploitation

        if success:
            new_state = self.game.get_state_dto()
            reward = new_state.scores[3 - state.turn] - score_before # difference de score apres le mouvement
            self.update(reward) #calcule q-table 

        return success
    @property
    def nb_games(self) -> int:
        """
        Retourne le nombre de game
        """
        return self.nb_loses + self.nb_draws + self.nb_wins
    
    def next_epsilon(self, coefficient=0.95, minimum=0.05):
        """
        Réduit progressivement epsilon (décroissance de l’exploration).

        Args:
            coefficient (float, optional): Facteur multiplicatif appliqué
                à epsilon à chaque appel. Default = 0.95.
            minimum (float, optional): Valeur minimale que epsilon ne peut
                pas dépasser. Default = 0.05.
        """
        self.epsilon = max(self.epsilon * coefficient, minimum)

    def exploit(self, state) -> bool:
        """
        Choisit le coup avec la meilleure valeur Q pour l'état donné.

        Args:
            state: GameStateDTO représentant l'état courant.

        Returns:
            True si le coup a été joué, False si aucun coup possible.
        """
        state_key = self._encode_state(state)
        valid_moves = self.game.legal_move()

        if not valid_moves:
            return False
        
        action = max(valid_moves, key=lambda a: self._get_q(state_key, a)) # a = action

        self.last_state = state_key
        self.last_action = action

        return self.game.move(action)
    
    def _get_q(self, state_key, action):
        """
        retourne la valeur de Q pour un etat et une action donner
        """
        return self.q_table.get(state_key, {}).get(action, 0)
    
    def update(self, reward):
        next_state = self.game.get_state_dto()
        next_state = self._encode_state(next_state)

        state = self.last_state
        action = self.last_action

        all_moves = list(self.game.DIRECTIONS.keys())
        best_q_value = max(self._get_q(next_state, a) for a in all_moves)

        current_q_value = self._get_q(state, action)

        if state not in self.q_table:
            self.q_table[state] = {}

        self.q_table[state][action] = current_q_value + self.learning_rate * (reward + best_q_value - current_q_value)

    

    
    