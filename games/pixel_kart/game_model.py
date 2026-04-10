"""
Modèle du jeu PixelKart.

Contient la logique métier :
- Circuit : représentation du tracé
- Race : gestion d'une course complète
"""

import random
from typing import List, Tuple, Optional
from .dao.race_dao import CircuitDTO, CellType, Direction, RaceStateDTO
from .player import Kart


class Circuit:
    """
    Représente un circuit de course.
    
    Le circuit est une grille de cellules (route, herbe, mur, ligne de départ).
    
    Attributes:
        dto: CircuitDTO contenant les données du circuit.
    """
    
    def __init__(self, dto: CircuitDTO):
        """
        Initialise un circuit depuis un DTO.
        
        Args:
            dto: CircuitDTO contenant les données du circuit.
        """
        self.dto = dto
    
    @property
    def width(self) -> int:
        """Largeur du circuit."""
        return self.dto.width
    
    @property
    def height(self) -> int:
        """Hauteur du circuit."""
        return self.dto.height
    
    def get_cell_type(self, x: int, y: int) -> Optional[CellType]:
        """
        Retourne le type de cellule à la position (x, y).
        
        Args:
            x: Coordonnée X.
            y: Coordonnée Y.
            
        Returns:
            CellType ou None si hors limites.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        return CellType(self.dto.grid[y][x])
    
    def is_out_of_bounds(self, x: int, y: int) -> bool:
        """
        Vérifie si la position est hors du circuit.
        
        Args:
            x: Coordonnée X.
            y: Coordonnée Y.
            
        Returns:
            True si hors limites.
        """
        return not (0 <= x < self.width and 0 <= y < self.height)
    
    def get_random_start_position(self) -> Tuple[int, int]:
        """
        Retourne une position de départ aléatoire sur la ligne de départ.
        
        Returns:
            (x, y) sur la ligne de départ.
        """
        if not self.dto.start_positions:
            # Fallback : position (0, 0)
            return (0, 0)
        return random.choice(self.dto.start_positions)


class Race:
    """
    Représente une course de PixelKart.
    
    Gère l'état de la course, les déplacements des karts,
    et la détection de fin de course.
    
    Attributes:
        circuit: Circuit de la course.
        karts: Liste des karts participants.
        total_laps: Nombre de tours à effectuer.
        current_turn: Tour de jeu actuel.
        current_kart_index: Indice du kart dont c'est le tour.
    """
    
    def __init__(
        self,
        circuit: Circuit,
        karts: List[Kart],
        total_laps: int = 3
    ):
        """
        Initialise une course.
        
        Args:
            circuit: Circuit de la course.
            karts: Liste des karts participants.
            total_laps: Nombre de tours à effectuer.
        """
        self.circuit = circuit
        self.karts = karts
        self.total_laps = total_laps
        
        self.current_turn = 0
        self.current_kart_index = 0
        
        # Initialiser les karts
        for kart in self.karts:
            kart.race = self
            kart.position = circuit.get_random_start_position()
            kart.direction = Direction.EAST
            kart.speed = 0
            kart.laps_completed = 0
            kart.is_finished = False
            kart.is_crashed = False
            kart.total_time = 0
    
    def reset(self):
        """Réinitialise la course."""
        self.__init__(self.circuit, self.karts, self.total_laps)
    
    def is_race_over(self) -> bool:
        """
        Vérifie si la course est terminée.
        
        Returns:
            True si tous les karts ont terminé ou crashé.
        """
        return all(k.is_finished or k.is_crashed for k in self.karts)
    
    def get_current_kart(self) -> Kart:
        """
        Retourne le kart dont c'est le tour.
        
        Returns:
            Kart actif.
        """
        return self.karts[self.current_kart_index]
    
    def next_kart(self):
        """Passe au kart suivant."""
        self.current_kart_index = (self.current_kart_index + 1) % len(self.karts)
        if self.current_kart_index == 0:
            self.current_turn += 1
    
    def execute_action(self, action: str) -> dict:
        """
        Exécute une action pour le kart courant.
        
        Args:
            action: "accelerate", "brake", "turn_left", "turn_right", "pass".
            
        Returns:
            Dictionnaire avec résultat : {
                "success": bool,
                "reward": float,
                "message": str
            }
        """
        kart = self.get_current_kart()
        
        if kart.is_finished or kart.is_crashed:
            return {"success": False, "reward": 0, "message": "Kart déjà hors-course"}
        
        # Appliquer l'action
        if action == "accelerate":
            kart.speed = min(kart.speed + 1, 2)
        elif action == "brake":
            kart.speed = max(kart.speed - 1, -1)
        elif action == "turn_left":
            kart.direction = kart.direction.turn_left()
        elif action == "turn_right":
            kart.direction = kart.direction.turn_right()
        # "pass" ne fait rien
        
        # Déplacer le kart selon sa vitesse
        result = self._move_kart(kart)
        
        # Incrémenter le temps
        kart.total_time += 1
        
        return result
    
    def _move_kart(self, kart: Kart) -> dict:
        """
        Déplace un kart selon sa vitesse et direction.
        
        Args:
            kart: Kart à déplacer.
            
        Returns:
            Résultat du déplacement avec récompense.
        """
        if kart.speed == 0:
            return {"success": True, "reward": -0.1, "message": "Immobile"}
        
        dx, dy = kart.direction.get_delta()
        x, y = kart.position
        reward = 0
        crossed_start_line = False
        
        # Déplacer case par case
        for _ in range(abs(kart.speed)):
            new_x = x + dx
            new_y = y + dy
            
            # Vérifier hors limites
            if self.circuit.is_out_of_bounds(new_x, new_y):
                kart.speed = 0
                reward = -1
                return {"success": False, "reward": reward, "message": "Hors limites"}
            
            # Vérifier le type de cellule
            cell_type = self.circuit.get_cell_type(new_x, new_y)
            
            if cell_type == CellType.WALL:
                kart.is_crashed = True
                reward = -100
                return {"success": False, "reward": reward, "message": "Collision avec un mur"}
            
            if cell_type == CellType.GRASS:
                # Herbe : vitesse divisée par 2
                kart.speed = kart.speed // 2
                reward -= 0.5
            
            if cell_type == CellType.START_LINE:
                # Vérifier si passage vers l'est
                if kart.direction == Direction.EAST:
                    crossed_start_line = True
            
            # Mettre à jour la position
            x, y = new_x, new_y
        
        kart.position = (x, y)
        
        # Vérifier si un tour est complété
        if crossed_start_line:
            kart.laps_completed += 1
            reward += 10
            
            if kart.laps_completed >= self.total_laps:
                kart.is_finished = True
                reward += 100
                return {
                    "success": True,
                    "reward": reward,
                    "message": f"Course terminée en {kart.total_time} tours !"
                }
        
        return {"success": True, "reward": reward, "message": "Déplacement ok"}
    
    def get_state_dto(self) -> RaceStateDTO:
        """
        Retourne l'état complet de la course en DTO.
        
        Returns:
            RaceStateDTO.
        """
        return RaceStateDTO(
            circuit=self.circuit.dto,
            karts=[k.to_dto() for k in self.karts],
            total_laps=self.total_laps,
            current_turn=self.current_turn,
            current_kart_index=self.current_kart_index,
            is_race_over=self.is_race_over(),
        )
    
    def play(self):
        """
        Joue une course complète (mode console).
        
        Utilisé pour l'entraînement de l'IA.
        """
        while not self.is_race_over():
            kart = self.get_current_kart()
            
            if not (kart.is_finished or kart.is_crashed):
                action = kart.play()
                if action:
                    result = self.execute_action(action)
                    
                    # Si c'est une IA, apprendre
                    if hasattr(kart, 'learn'):
                        kart.learn(result["reward"])
            
            self.next_kart()