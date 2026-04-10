"""
Data Transfer Objects pour PixelKart.

Contient les structures de données sérialisables pour :
- Circuit : représentation du tracé
- Kart : état d'un kart (position, vitesse, direction)
- Race : état de la course complète
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from enum import Enum


class CellType(Enum):
    """Type de cellule du circuit."""
    ROAD = 0        # Route normale
    GRASS = 1       # Herbe (vitesse /2)
    WALL = 2        # Mur (game over)
    START_LINE = 3  # Ligne départ/arrivée


class Direction(Enum):
    """Direction du kart."""
    NORTH = 0  # Haut
    EAST = 1   # Droite
    SOUTH = 2  # Bas
    WEST = 3   # Gauche
    
    def turn_left(self) -> "Direction":
        """Retourne la direction après rotation à gauche."""
        return Direction((self.value - 1) % 4)
    
    def turn_right(self) -> "Direction":
        """Retourne la direction après rotation à droite."""
        return Direction((self.value + 1) % 4)
    
    def get_delta(self) -> Tuple[int, int]:
        """Retourne le déplacement (dx, dy) dans cette direction."""
        deltas = {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1),
            Direction.WEST: (-1, 0),
        }
        return deltas[self]


@dataclass
class CircuitDTO:
    """
    Représentation d'un circuit de course.
    
    Attributes:
        name: Nom du circuit.
        width: Largeur en pixels.
        height: Hauteur en pixels.
        grid: Matrice [hauteur][largeur] de CellType.
        start_positions: Liste des positions (x, y) de la ligne de départ.
    """
    name: str
    width: int
    height: int
    grid: List[List[int]]  # Valeurs de CellType.value
    start_positions: List[Tuple[int, int]] = field(default_factory=list)
    
    def to_string(self) -> str:
        """
        Sérialise le circuit en chaîne de caractères.
        
        Format : "width,height,cellules_aplaties"
        
        Returns:
            Chaîne représentant le circuit.
        """
        flat = "".join(str(cell) for row in self.grid for cell in row)
        return f"{self.width},{self.height},{flat}"
    
    @classmethod
    def from_string(cls, name: str, data: str) -> "CircuitDTO":
        """
        Désérialise un circuit depuis une chaîne.
        
        Args:
            name: Nom du circuit.
            data: Chaîne au format "width,height,cellules".
            
        Returns:
            Instance de CircuitDTO.
        """
        parts = data.split(',')
        width, height = int(parts[0]), int(parts[1])
        flat = parts[2]
        
        grid = [
            [int(flat[y * width + x]) for x in range(width)]
            for y in range(height)
        ]
        
        # Trouver les positions de départ
        start_positions = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if grid[y][x] == CellType.START_LINE.value
        ]
        
        return cls(
            name=name,
            width=width,
            height=height,
            grid=grid,
            start_positions=start_positions
        )


@dataclass
class KartDTO:
    """
    État d'un kart à un instant donné.
    
    Attributes:
        name: Nom du pilote.
        position: (x, y) sur le circuit.
        direction: Direction du kart (North, East, South, West).
        speed: Vitesse en cases/tour (-1 à 2).
        laps_completed: Nombre de tours complétés.
        is_finished: True si le kart a terminé la course.
        is_crashed: True si le kart a percuté un mur.
        total_time: Temps total (en tours de jeu).
    """
    name: str
    position: Tuple[int, int]
    direction: Direction
    speed: int = 0
    laps_completed: int = 0
    is_finished: bool = False
    is_crashed: bool = False
    total_time: int = 0
    
    def to_dict(self) -> dict:
        """Sérialise en dictionnaire."""
        return {
            "name": self.name,
            "position": list(self.position),
            "direction": self.direction.value,
            "speed": self.speed,
            "laps_completed": self.laps_completed,
            "is_finished": self.is_finished,
            "is_crashed": self.is_crashed,
            "total_time": self.total_time,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "KartDTO":
        """Désérialise depuis un dictionnaire."""
        return cls(
            name=data["name"],
            position=tuple(data["position"]),
            direction=Direction(data["direction"]),
            speed=data["speed"],
            laps_completed=data["laps_completed"],
            is_finished=data["is_finished"],
            is_crashed=data["is_crashed"],
            total_time=data["total_time"],
        )


@dataclass
class RaceStateDTO:
    """
    État complet d'une course.
    
    Attributes:
        circuit: Circuit de la course.
        karts: Liste des états de tous les karts.
        total_laps: Nombre de tours à effectuer.
        current_turn: Tour de jeu actuel.
        current_kart_index: Indice du kart dont c'est le tour.
        is_race_over: True si la course est terminée.
    """
    circuit: CircuitDTO
    karts: List[KartDTO]
    total_laps: int
    current_turn: int = 0
    current_kart_index: int = 0
    is_race_over: bool = False
    
    def to_dict(self) -> dict:
        """Sérialise en dictionnaire."""
        return {
            "circuit": {
                "name": self.circuit.name,
                "data": self.circuit.to_string()
            },
            "karts": [k.to_dict() for k in self.karts],
            "total_laps": self.total_laps,
            "current_turn": self.current_turn,
            "current_kart_index": self.current_kart_index,
            "is_race_over": self.is_race_over,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RaceStateDTO":
        """Désérialise depuis un dictionnaire."""
        circuit = CircuitDTO.from_string(
            data["circuit"]["name"],
            data["circuit"]["data"]
        )
        karts = [KartDTO.from_dict(k) for k in data["karts"]]
        
        return cls(
            circuit=circuit,
            karts=karts,
            total_laps=data["total_laps"],
            current_turn=data["current_turn"],
            current_kart_index=data["current_kart_index"],
            is_race_over=data["is_race_over"],
        )