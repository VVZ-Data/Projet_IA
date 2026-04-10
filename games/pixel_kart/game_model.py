"""
Modèles du jeu Pixel Kart : Circuit, Kart et Race.

Architecture MVC :
- Circuit : représente la grille du circuit (route, herbe, mur, ligne d'arrivée)
- Kart : représente un kart (position, direction, vitesse)
- Race : représente une course (circuit + karts + état du jeu)
"""

import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from games.pixel_kart.editor.const import PIXEL_TYPES


# === DIRECTIONS ===
# Chaque direction est un vecteur (delta_row, delta_col)
DIRECTIONS = {
    "NORTH": (-1, 0),
    "EAST":  (0, 1),
    "SOUTH": (1, 0),
    "WEST":  (0, -1),
}
DIRECTION_ORDER = ["NORTH", "EAST", "SOUTH", "WEST"]


# === DTOs ===

@dataclass
class CircuitDTO:
    """Représentation transportable d'un circuit."""
    name: str
    raw: str  # Format "RGW,RGW,..." identique au DAO de l'éditeur


@dataclass
class KartDTO:
    """Représentation transportable d'un kart."""
    name: str
    color: str
    position: Tuple[int, int]
    direction: str
    speed: int
    turns_done: int
    is_alive: bool
    is_ai: bool


@dataclass
class RaceDTO:
    """Représentation transportable d'une course."""
    circuit_name: str
    karts: List[KartDTO]
    time: int
    nb_turns: int
    current_kart_index: int
    finished: bool


# === MODÈLES ===

class Circuit:
    """
    Représente un circuit de course sous forme de grille.

    Attributes:
        name (str): nom du circuit.
        grid (list[list[str]]): grille de cellules (lettres R/G/W/F).
        rows (int), cols (int): dimensions.
        finish_positions (list[(r,c)]): cellules formant la ligne d'arrivée.
        finish_col (int): colonne de la ligne d'arrivée (verticale).
    """

    LETTER_ROAD = "R"
    LETTER_GRASS = "G"
    LETTER_WALL = "W"
    LETTER_FINISH = "F"

    def __init__(self, name: str, raw: str):
        self.name = name
        self.raw = raw
        rows = raw.split(",")
        self.grid = [list(row) for row in rows]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows else 0
        self.finish_positions = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c] == self.LETTER_FINISH
        ]
        # On suppose une ligne d'arrivée verticale (toutes les F sur la même colonne)
        self.finish_col = self.finish_positions[0][1] if self.finish_positions else 0

    def cell(self, row: int, col: int) -> str:
        """Retourne la lettre de la cellule, ou 'W' si hors-grille."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return self.LETTER_WALL

    def is_inside(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def random_start(self) -> Tuple[int, int]:
        """Choisit aléatoirement une case de départ sur la ligne d'arrivée."""
        if not self.finish_positions:
            return (0, 0)
        return random.choice(self.finish_positions)

    def to_dto(self) -> CircuitDTO:
        return CircuitDTO(name=self.name, raw=self.raw)


class Kart:
    """
    Représente un kart sur le circuit.

    Attributes:
        name (str): nom du joueur.
        color (str): couleur du kart sur la vue.
        position (tuple[int,int]): (row, col).
        direction (str): NORTH/EAST/SOUTH/WEST.
        speed (int): vitesse en pixels/tour (entre -1 et 2).
        turns_done (int): nombre de tours terminés.
        is_alive (bool): faux si crash dans un mur.
        is_ai (bool): True si IA, False si humain.
    """

    MIN_SPEED = -1
    MAX_SPEED = 2

    def __init__(self, name: str, color: str = "grey", is_ai: bool = False):
        self.name = name
        self.color = color
        self.is_ai = is_ai
        self.position: Tuple[int, int] = (0, 0)
        self.direction: str = "EAST"
        self.speed: int = 0
        self.turns_done: int = 0
        self.is_alive: bool = True

    def reset(self, start_position: Tuple[int, int]) -> None:
        """Place le kart au départ."""
        self.position = start_position
        self.direction = "EAST"
        self.speed = 0
        self.turns_done = 0
        self.is_alive = True

    def accelerate(self) -> None:
        if self.speed < self.MAX_SPEED:
            self.speed += 1

    def brake(self) -> None:
        if self.speed > self.MIN_SPEED:
            self.speed -= 1

    def turn_left(self) -> None:
        idx = DIRECTION_ORDER.index(self.direction)
        self.direction = DIRECTION_ORDER[(idx - 1) % 4]

    def turn_right(self) -> None:
        idx = DIRECTION_ORDER.index(self.direction)
        self.direction = DIRECTION_ORDER[(idx + 1) % 4]

    def to_dto(self) -> KartDTO:
        return KartDTO(
            name=self.name,
            color=self.color,
            position=self.position,
            direction=self.direction,
            speed=self.speed,
            turns_done=self.turns_done,
            is_alive=self.is_alive,
            is_ai=self.is_ai,
        )


class Race:
    """
    Gère le déroulement d'une course.

    Attributes:
        circuit (Circuit)
        karts (list[Kart])
        nb_turns (int) : nombre de tours à effectuer
        time (int) : nombre de tours de jeu écoulés
        current_kart_index (int) : index du kart qui doit jouer
    """

    ACTIONS = ["ACCELERATE", "BRAKE", "TURN_LEFT", "TURN_RIGHT", "PASS"]

    def __init__(self, circuit: Circuit, karts: List[Kart], nb_turns: int = 3):
        self.circuit = circuit
        self.karts = karts
        self.nb_turns = nb_turns
        self.time = 0
        self.current_kart_index = 0
        for kart in self.karts:
            kart.reset(circuit.random_start())

    # ---------- Cycle de jeu ----------

    @property
    def current_kart(self) -> Kart:
        return self.karts[self.current_kart_index]

    def play_action(self, action: str) -> None:
        """
        Applique une action au kart courant, puis fait avancer le kart,
        et enfin passe au kart suivant.
        """
        kart = self.current_kart
        if not kart.is_alive or self._kart_done(kart):
            self._next_kart()
            return

        # 1) Appliquer l'action choisie
        if action == "ACCELERATE":
            kart.accelerate()
        elif action == "BRAKE":
            kart.brake()
        elif action == "TURN_LEFT":
            kart.turn_left()
        elif action == "TURN_RIGHT":
            kart.turn_right()
        # PASS ne change rien

        # 2) Faire avancer le kart en fonction de sa vitesse et de sa direction
        self._move_kart(kart)

        # 3) Passer au kart suivant
        self._next_kart()

    def _move_kart(self, kart: Kart) -> None:
        """
        Déplace le kart pas à pas selon sa vitesse :
        - Sur l'herbe la vitesse est divisée par 2 (arrondie en dessous)
        - Si le kart sort de la grille, sa vitesse est remise à 0
        - Si le kart percute un mur, il est éliminé
        - Si le kart franchit la ligne d'arrivée vers l'EST, on incrémente turns_done
        """
        # Vitesse effective (herbe = vitesse / 2)
        current_cell = self.circuit.cell(*kart.position)
        effective_speed = kart.speed
        if current_cell == Circuit.LETTER_GRASS and effective_speed > 0:
            effective_speed = effective_speed // 2

        if effective_speed <= 0:
            # Pas de mouvement (la vitesse négative ne déplace pas en V1)
            return

        dr, dc = DIRECTIONS[kart.direction]
        for _ in range(effective_speed):
            new_r = kart.position[0] + dr
            new_c = kart.position[1] + dc

            # Sortie de grille => vitesse = 0
            if not self.circuit.is_inside(new_r, new_c):
                kart.speed = 0
                return

            cell = self.circuit.cell(new_r, new_c)

            # Mur => crash
            if cell == Circuit.LETTER_WALL:
                kart.is_alive = False
                kart.speed = 0
                return

            # Détection franchissement ligne d'arrivée vers l'EST
            if (
                kart.direction == "EAST"
                and kart.position[1] < self.circuit.finish_col <= new_c
            ):
                kart.turns_done += 1

            kart.position = (new_r, new_c)

    def _next_kart(self) -> None:
        """Passe au kart suivant et incrémente le temps si tous ont joué."""
        self.current_kart_index = (self.current_kart_index + 1) % len(self.karts)
        if self.current_kart_index == 0:
            self.time += 1

    def _kart_done(self, kart: Kart) -> bool:
        return kart.turns_done >= self.nb_turns

    def is_finished(self) -> bool:
        """La course est finie si tous les karts ont fini ou sont morts."""
        return all(
            (not kart.is_alive) or self._kart_done(kart)
            for kart in self.karts
        )

    def winner(self) -> Optional[Kart]:
        """Retourne le premier kart à avoir terminé la course (ou None)."""
        finishers = [k for k in self.karts if k.is_alive and self._kart_done(k)]
        if not finishers:
            return None
        # Le premier à avoir fini : pour V1 simple on prend celui avec le plus de tours
        return max(finishers, key=lambda k: k.turns_done)

    def to_dto(self) -> RaceDTO:
        return RaceDTO(
            circuit_name=self.circuit.name,
            karts=[k.to_dto() for k in self.karts],
            time=self.time,
            nb_turns=self.nb_turns,
            current_kart_index=self.current_kart_index,
            finished=self.is_finished(),
        )
