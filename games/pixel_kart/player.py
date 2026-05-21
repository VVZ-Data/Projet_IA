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
    Kart contrôlé par une IA Q-learning.

    `training=True`  : politique ε-greedy (exploration + apprentissage).
    `training=False` : exploitation pure, ε ignoré.

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
        super().__init__(name=name, color=color, is_ai=True)
        self.repository = repository
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.training = training

    # ──────────────────────────────────────────────────────────────────────
    # Politique
    # ──────────────────────────────────────────────────────────────────────

    def choose_action(self, state: str) -> str:
        """
        Choisit la prochaine action selon la politique courante.

        En mode training, joue aléatoirement avec probabilité ε (exploration).
        Sinon, choisit l'action de meilleure Q-value (greedy).

        Args:
            state: État courant encodé (string ai_state).

        Returns:
            Une action publique parmi `Race.ACTIONS`.
        """
        if self.training and random.random() < self.epsilon:
            return random.choice(Race.ACTIONS)

        action_chars = list(CHAR_TO_ACTION.keys())
        action_char = self.repository.best_action(state, action_chars)
        return CHAR_TO_ACTION[action_char]

    # ──────────────────────────────────────────────────────────────────────
    # Mise à jour Q
    # ──────────────────────────────────────────────────────────────────────

    def update_q(
        self,
        state: str,
        action_char: str,
        reward: float,
        new_state: str,
        terminal: bool = False,
    ) -> None:
        """
        Applique une mise à jour Q-learning sur la transition (state, action).

        Formule :
            Q(s,a) ← Q(s,a) + α · [ r + γ · max_a' Q(s',a') − Q(s,a) ]

        Pour un état terminal, `max_a' Q(s',a') = 0`.

        Args:
            state: État avant l'action (string ai_state).
            action_char: Caractère d'action (ACTION_TO_CHAR).
            reward: Récompense reçue.
            new_state: État résultant, ou "" si terminal.
            terminal: True si la transition mène à un état terminal.
        """
        current_q = self.repository.get_q(state, action_char)

        if terminal:
            future_value = 0.0
        else:
            action_chars = list(CHAR_TO_ACTION.keys())
            future_value = self.repository.best_q(new_state, action_chars)

        new_q = current_q + self.alpha * (reward + self.gamma * future_value - current_q)
        self.repository.set_q(state, action_char, new_q)
