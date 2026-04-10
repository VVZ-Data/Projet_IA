"""
Définit les types de joueurs pour Pixel Kart.

- Human : ne choisit rien automatiquement (les actions viennent de l'UI)
- RandomAI : choisit une action aléatoire à chaque tour
"""

import random
from games.pixel_kart.game_model import Kart, Race


class Human(Kart):
    """Kart contrôlé par un humain via l'interface graphique."""

    def __init__(self, name: str, color: str):
        super().__init__(name=name, color=color, is_ai=False)


class RandomAI(Kart):
    """Kart contrôlé par une IA qui joue des actions aléatoires."""

    def __init__(self, name: str, color: str):
        super().__init__(name=name, color=color, is_ai=True)

    def choose_action(self, race: Race) -> str:
        """Retourne une action aléatoire parmi les actions valides."""
        return random.choice(Race.ACTIONS)
