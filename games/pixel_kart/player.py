"""
Définit les types de joueurs pour Pixel Kart.

- Human       : ne choisit rien automatiquement (les actions viennent de l'UI)
- RandomAI    : choisit une action aléatoire à chaque tour
- QLearningAI : choisit selon une politique ε-greedy sur une Q-table persistée
"""

import random

from games.pixel_kart.ai_state import (
    ACTION_TO_CHAR,
    CHAR_TO_ACTION,
    encode_state,
)
from games.pixel_kart.dao.q_table_repository import QTableRepository
from games.pixel_kart.game_model import Kart, Race


class Human(Kart):
    """Kart contrôlé par un humain via l'interface graphique."""

    def __init__(self, name: str, color: str = "grey"):
        super().__init__(name=name, color=color, is_ai=False)


class RandomAI(Kart):
    """Kart contrôlé par une IA qui joue des actions aléatoires."""

    def __init__(self, name: str, color: str = "grey"):
        super().__init__(name=name, color=color, is_ai=True)

    def choose_action(self, race: Race) -> str:
        """Retourne une action aléatoire parmi les actions valides."""
        return random.choice(Race.ACTIONS)


class QLearningAI(Kart):
    """
    [IA-Claude] Kart contrôlé par une IA Q-learning.

    Modes de fonctionnement contrôlés par le flag `training` :

    - `training=True`  : politique ε-greedy (exploration) et chaque coup
                         mémorise (state, action) pour qu'une mise à jour
                         Q-learning puisse être appliquée par la boucle
                         d'entraînement via `update_q`.

    - `training=False` : politique greedy pure (ε ignoré), aucune mise à
                         jour de la Q-table. C'est le mode utilisé en jeu
                         pour affronter un humain.

    L'agent ne touche pas directement à la base : il dialogue avec un
    `QTableRepository` qui s'occupe du cache RAM et du flush par batch.
    """

    def __init__(
        self,
        name: str,
        repository: QTableRepository,
        gamma: float = 0.9,
        alpha: float = 0.1,
        epsilon: float = 0.0,
        training: bool = False,
        color: str = "grey",
    ) -> None:
        """
        Initialise l'agent Q-learning.

        Args:
            name: Nom affiché du kart.
            repository: Repository RAM-first donnant accès à la Q-table.
            gamma: Facteur d'escompte γ ∈ [0, 1[. Élevé (~0.9–0.99) pour
                un environnement où la récompense de fin est lointaine.
            alpha: Taux d'apprentissage α ∈ ]0, 1]. ~0.1 par défaut.
            epsilon: Probabilité de jouer aléatoirement (exploration). Ignoré
                si `training=False`.
            training: Active la politique ε-greedy + la mémorisation de la
                transition pour `update_q`.
            color: Couleur d'affichage du kart sur la vue.
        """
        super().__init__(name=name, color=color, is_ai=True)
        self.repository = repository
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.training = training

        # Mémoire de la dernière transition (utilisée par update_q)
        self.last_state: str | None = None
        self.last_action: str | None = None

    # ──────────────────────────────────────────────────────────────────────
    # Politique
    # ──────────────────────────────────────────────────────────────────────

    def choose_action(self, race: Race) -> str:
        """
        Choisit la prochaine action selon la politique courante.

        Encode l'état courant via `ai_state.encode_state`, puis :
        - tire au sort en cas d'exploration (training + ε),
        - sinon choisit l'action de meilleure Q-value (greedy).

        Mémorise (state, action) sur le kart pour que la boucle
        d'entraînement puisse appeler `update_q` avec la récompense.

        Args:
            race: Course en cours (utile pour accéder au circuit).

        Returns:
            Une action publique parmi `Race.ACTIONS`.
        """
        current_state = encode_state(self, race.circuit)
        action_chars = list(CHAR_TO_ACTION.keys())

        if self.training and random.random() < self.epsilon:
            action_str = random.choice(Race.ACTIONS)
            action_char = ACTION_TO_CHAR[action_str]
        else:
            action_char = self.repository.best_action(current_state, action_chars)
            action_str = CHAR_TO_ACTION[action_char]

        self.last_state = current_state
        self.last_action = action_char
        return action_str

    # ──────────────────────────────────────────────────────────────────────
    # Mise à jour Q
    # ──────────────────────────────────────────────────────────────────────

    def update_q(self, reward: float, new_state: str, terminal: bool = False) -> None:
        """
        Applique une mise à jour Q-learning sur la dernière transition.

        Formule :
            Q(s,a) ← Q(s,a) + α · [ r + γ · max_a' Q(s',a') − Q(s,a) ]

        Pour un état terminal (crash ou course finie), `max_a' Q(s',a') = 0`
        car aucune action future n'est possible.

        Args:
            reward: Récompense reçue après l'action mémorisée.
            new_state: État résultant (string ai_state) ou "" si terminal.
            terminal: True si la transition mène à un état terminal.
        """
        if self.last_state is None or self.last_action is None:
            return

        current_q = self.repository.get_q(self.last_state, self.last_action)

        if terminal:
            future_value = 0.0
        else:
            action_chars = list(CHAR_TO_ACTION.keys())
            future_value = self.repository.best_q(new_state, action_chars)

        new_q = current_q + self.alpha * (reward + self.gamma * future_value - current_q)
        self.repository.set_q(self.last_state, self.last_action, new_q)

    def reset_memory(self) -> None:
        """
        Réinitialise la mémoire (state, action) avant un nouvel épisode.

        Sans cet appel, la première mise à jour d'un nouvel épisode pourrait
        utiliser des valeurs orphelines de l'épisode précédent.
        """
        self.last_state = None
        self.last_action = None
