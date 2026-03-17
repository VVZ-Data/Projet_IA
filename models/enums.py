"""
    model qui empêche les valeurs invalides
"""

import enum

class GameStatus(str, enum.Enum):
    WAITING     = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED    = "finished"

class Direction(str, enum.Enum):
    UP    = "up"
    DOWN  = "down"
    LEFT  = "left"
    RIGHT = "right"