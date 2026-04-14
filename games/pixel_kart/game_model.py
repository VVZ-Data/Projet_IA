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

    Les lettres des cellules (R/G/W/F) sont centralisées dans
    `editor/const.py:PIXEL_TYPES` pour éviter la duplication.

    Attributes:
        name (str): nom du circuit.
        grid (list[list[str]]): grille de cellules (lettres R/G/W/F).
        rows (int), cols (int): dimensions.
        finish_positions (list[(r,c)]): cellules formant la ligne d'arrivée.
        finish_col (int): colonne de la ligne d'arrivée (verticale).
    """

    # Lettres issues de la configuration centrale des types de pixels
    LETTER_ROAD = PIXEL_TYPES["ROAD"]["letter"]
    LETTER_GRASS = PIXEL_TYPES["GRASS"]["letter"]
    LETTER_WALL = PIXEL_TYPES["WALL"]["letter"]
    LETTER_FINISH = PIXEL_TYPES["FINISH"]["letter"]

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
        """
        Retourne la lettre de la cellule demandée.

        La méthode `_move_kart` vérifie systématiquement `is_inside` avant
        d'appeler `cell`, donc on se contente ici d'accéder à la grille.
        Un `IndexError` remonte si l'appelant néglige la vérification :
        c'est volontaire, cela révèle rapidement un bug côté appelant
        plutôt que de masquer une sortie de grille.
        """
        return self.grid[row][col]

    def is_inside(self, row: int, col: int) -> bool:
        """Vrai si (row, col) est une case valide de la grille."""
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
        # Un tour n'est validé que si le kart est passé par le "checkpoint"
        # (moitié opposée du circuit) avant de retraverser la ligne d'arrivée.
        # Empêche l'exploit consistant à faire des allers-retours sur la ligne.
        self.passed_checkpoint: bool = False

    def reset(self, start_position: Tuple[int, int]) -> None:
        """Place le kart au départ."""
        self.position = start_position
        self.direction = "EAST"
        self.speed = 0
        self.turns_done = 0
        self.is_alive = True
        self.passed_checkpoint = False

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
        Applique une action au kart courant, le fait avancer, puis passe
        au prochain kart encore en jeu (vivant et n'ayant pas fini sa course).
        """
        kart = self.current_kart
        if kart.is_alive and not self._kart_done(kart):
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

        # 3) Passer au prochain kart encore jouable
        self._advance_to_next_playable()

    def _move_kart(self, kart: Kart) -> None:
        """
        Déplace le kart pas à pas selon sa vitesse :
        - Sur l'herbe, la vitesse (en valeur absolue) est divisée par 2.
        - Une vitesse positive déplace le kart dans sa direction.
        - Une vitesse négative fait reculer le kart (direction opposée).
        - Si le kart sort de la grille, sa vitesse est remise à 0.
        - Si le kart percute un mur, il est éliminé.
        - Le passage de la ligne d'arrivée vers l'EST n'incrémente
          `turns_done` que si le kart a touché le checkpoint opposé.
        """
        if kart.speed == 0:
            return

        # Vitesse effective (herbe = |vitesse| / 2, arrondi vers zéro)
        current_cell = self.circuit.cell(*kart.position)
        magnitude = abs(kart.speed)
        if current_cell == Circuit.LETTER_GRASS:
            magnitude = magnitude // 2
        if magnitude == 0:
            return

        # Sens du déplacement : en marche arrière on inverse le vecteur
        dr, dc = DIRECTIONS[kart.direction]
        if kart.speed < 0:
            dr, dc = -dr, -dc

        # Colonne servant de checkpoint (moitié opposée de la ligne d'arrivée)
        checkpoint_col = (self.circuit.cols - 1) - self.circuit.finish_col

        for _ in range(magnitude):
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

            # Franchissement de la ligne d'arrivée vers l'EST :
            # ne valide un tour que si le kart est passé par le checkpoint.
            crossing_east = (
                kart.direction == "EAST" and kart.speed > 0
                and kart.position[1] < self.circuit.finish_col <= new_c
            )
            if crossing_east and kart.passed_checkpoint:
                kart.turns_done += 1
                kart.passed_checkpoint = False

            # Validation du checkpoint (moitié opposée du circuit)
            if abs(new_c - checkpoint_col) <= 1:
                kart.passed_checkpoint = True

            kart.position = (new_r, new_c)

    def _next_kart(self) -> None:
        """Passe au kart suivant et incrémente le temps si tous ont joué."""
        self.current_kart_index = (self.current_kart_index + 1) % len(self.karts)
        if self.current_kart_index == 0:
            self.time += 1

    def _advance_to_next_playable(self) -> None:
        """
        Avance `current_kart_index` jusqu'au prochain kart encore jouable
        (vivant et n'ayant pas terminé). S'arrête si la course est finie
        pour éviter une boucle infinie.
        """
        for _ in range(len(self.karts)):
            self._next_kart()
            if self.is_finished():
                return
            kart = self.current_kart
            if kart.is_alive and not self._kart_done(kart):
                return

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
