"""
Représentation des pilotes (karts) dans PixelKart.

Classes :
- Kart : Kart de base avec déplacements aléatoires
- Human : Kart contrôlé par un humain
- AI : Kart contrôlé par Q-Learning
"""

import random
from typing import Optional, Dict, Tuple
from .dao.race_dao import Direction, KartDTO


class Kart:
    """
    Représente un kart dans la course.
    
    Le kart a une position, une direction et une vitesse.
    À chaque tour, il peut accélérer, freiner, tourner ou ne rien faire.
    
    Attributes:
        name: Nom du pilote.
        race: Référence à la course en cours.
        position: (x, y) sur le circuit.
        direction: Direction actuelle (Direction enum).
        speed: Vitesse en cases/tour (-1 à 2).
        laps_completed: Nombre de tours complétés.
        is_finished: True si la course est terminée pour ce kart.
        is_crashed: True si le kart a percuté un mur.
        total_time: Temps total en tours de jeu.
    """
    
    def __init__(self, name: str, race=None):
        """
        Initialise un kart.
        
        Args:
            name: Nom du pilote.
            race: Référence à la Race (optionnel).
        """
        self.name = name
        self.race = race
        
        # État du kart
        self.position: Tuple[int, int] = (0, 0)
        self.direction: Direction = Direction.EAST
        self.speed: int = 0
        self.laps_completed: int = 0
        self.is_finished: bool = False
        self.is_crashed: bool = False
        self.total_time: int = 0
    
    def is_human(self) -> bool:
        """Retourne True si c'est un joueur humain."""
        return False
    
    def play(self) -> Optional[str]:
        """
        Choisit une action aléatoire parmi les actions possibles.
        
        Returns:
            Action choisie : "accelerate", "brake", "turn_left", "turn_right", "pass"
        """
        if self.race is None or self.is_finished or self.is_crashed:
            return "pass"
        
        actions = ["accelerate", "brake", "turn_left", "turn_right", "pass"]
        return random.choice(actions)
    
    def to_dto(self) -> KartDTO:
        """
        Convertit le kart en DTO.
        
        Returns:
            KartDTO représentant l'état actuel.
        """
        return KartDTO(
            name=self.name,
            position=self.position,
            direction=self.direction,
            speed=self.speed,
            laps_completed=self.laps_completed,
            is_finished=self.is_finished,
            is_crashed=self.is_crashed,
            total_time=self.total_time,
        )


class Human(Kart):
    """
    Kart contrôlé par un joueur humain.
    
    Le joueur choisit manuellement son action via l'interface.
    """
    
    def __init__(self, name: str, race=None):
        """
        Initialise un kart humain.
        
        Args:
            name: Nom du joueur.
            race: Référence à la Race.
        """
        super().__init__(name, race)
    
    def is_human(self) -> bool:
        """Retourne True (c'est un humain)."""
        return True
    
    def play(self) -> Optional[str]:
        """
        Ne joue pas automatiquement.
        
        L'action sera fournie par le contrôleur via l'interface.
        
        Returns:
            None (attente de l'input utilisateur).
        """
        return None


class AI(Kart):
    """
    Kart contrôlé par une IA utilisant Q-Learning.
    
    L'IA apprend à naviguer sur le circuit pour minimiser le temps.
    
    Attributes:
        epsilon: Taux d'exploration (0.0 = exploitation pure).
        learning_rate: Taux d'apprentissage (alpha).
        discount_factor: Facteur de discount (gamma).
        q_table: Dictionnaire {état: {action: valeur_Q}}.
        last_state: Dernier état observé.
        last_action: Dernière action effectuée.
    """
    
    def __init__(
        self,
        name: str,
        race=None,
        epsilon: float = 0.1,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9
    ):
        """
        Initialise une IA.
        
        Args:
            name: Nom de l'IA.
            race: Référence à la Race.
            epsilon: Taux d'exploration initial.
            learning_rate: Taux d'apprentissage (alpha).
            discount_factor: Facteur de discount (gamma).
        """
        super().__init__(name, race)
        
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Q-table : {état_str: {action: valeur}}
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Mémoire pour l'apprentissage
        self.last_state: Optional[str] = None
        self.last_action: Optional[str] = None
    
    def _encode_state(self) -> str:
        """
        Encode l'état actuel en chaîne pour la Q-table.
        
        État simplifié : position + direction + vitesse
        (peut être étendu selon les besoins)
        
        Returns:
            Clé unique représentant l'état.
        """
        x, y = self.position
        return f"{x},{y},{self.direction.value},{self.speed}"
    
    def _get_q_value(self, state: str, action: str) -> float:
        """
        Retourne la valeur Q pour un état/action.
        
        Args:
            state: Clé d'état.
            action: Action.
            
        Returns:
            Valeur Q (0.0 si non initialisée).
        """
        return self.q_table.get(state, {}).get(action, 0.0)
    
    def _update_q_value(self, state: str, action: str, value: float):
        """
        Met à jour la valeur Q pour un état/action.
        
        Args:
            state: Clé d'état.
            action: Action.
            value: Nouvelle valeur Q.
        """
        if state not in self.q_table:
            self.q_table[state] = {}
        self.q_table[state][action] = value
    
    def play(self) -> Optional[str]:
        """
        Choisit une action selon la politique ε-greedy.
        
        Returns:
            Action choisie.
        """
        if self.race is None or self.is_finished or self.is_crashed:
            return "pass"
        
        state = self._encode_state()
        actions = ["accelerate", "brake", "turn_left", "turn_right", "pass"]
        
        # Exploration vs exploitation
        if random.random() < self.epsilon:
            # Exploration : action aléatoire
            action = random.choice(actions)
        else:
            # Exploitation : meilleure action
            q_values = {a: self._get_q_value(state, a) for a in actions}
            action = max(q_values, key=q_values.get)
        
        # Mémoriser pour l'apprentissage
        self.last_state = state
        self.last_action = action
        
        return action
    
    def learn(self, reward: float):
        """
        Met à jour la Q-table selon la récompense reçue.
        
        Utilise la formule : Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]
        
        Args:
            reward: Récompense reçue (-1 pour collision, +10 pour tour complété, etc.).
        """
        if self.last_state is None or self.last_action is None:
            return
        
        # État actuel après l'action
        current_state = self._encode_state()
        
        # Meilleure valeur Q pour l'état suivant
        actions = ["accelerate", "brake", "turn_left", "turn_right", "pass"]
        max_future_q = max(self._get_q_value(current_state, a) for a in actions)
        
        # Valeur Q actuelle
        current_q = self._get_q_value(self.last_state, self.last_action)
        
        # Mise à jour Q-Learning
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_future_q - current_q
        )
        
        self._update_q_value(self.last_state, self.last_action, new_q)
    
    def next_epsilon(self, coefficient: float = 0.99, minimum: float = 0.01):
        """
        Réduit epsilon progressivement (décroissance de l'exploration).
        
        Args:
            coefficient: Facteur multiplicatif (default: 0.99).
            minimum: Valeur minimale d'epsilon (default: 0.01).
        """
        self.epsilon = max(self.epsilon * coefficient, minimum)
    
    def upload(self, filename: str):
        """
        Sauvegarde la Q-table dans un fichier JSON.
        
        Args:
            filename: Nom du fichier de sauvegarde.
        """
        import json
        data = {
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "q_table": self.q_table,
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    
    def download(self, filename: str):
        """
        Charge la Q-table depuis un fichier JSON.
        
        Args:
            filename: Nom du fichier à charger.
        """
        import json
        with open(filename, "r") as f:
            data = json.load(f)
        
        self.epsilon = data["epsilon"]
        self.learning_rate = data["learning_rate"]
        self.discount_factor = data["discount_factor"]
        self.q_table = data["q_table"]