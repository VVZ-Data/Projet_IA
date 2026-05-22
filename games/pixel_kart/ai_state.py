"""
Encodage de l'état et des actions pour l'IA Q-learning de Pixel Kart.

Contient uniquement la représentation de l'état :
- ACTION_TO_CHAR / CHAR_TO_ACTION : encodage 1 caractère des actions
- encode_state : transforme un (Kart, Circuit) en clé string de 6 chars

Format d'état : "{front}{left}{right}{back}{terrain}{speed}"
    front/left/right/back ∈ {0,1,2,3} : cases route consécutives dans la
                                         direction relative, saturé à 3.
    terrain               ∈ {0,1}     : 0 si route ou finish, 1 si herbe.
    speed                 ∈ {0,1,2,3} : vitesse remappée (-1→0, 0→1, 1→2, 2→3).

Les sensors sont RELATIFS à la direction du kart, ce qui permet à l'IA de
réutiliser ce qu'elle apprend quelle que soit l'orientation absolue.
"""

from games.pixel_kart.game_model import (
    DIRECTION_ORDER,
    DIRECTIONS,
    Circuit,
    Kart,
)


# ──────────────────────────────────────────────────────────────────────────
# Encodage des actions
# ──────────────────────────────────────────────────────────────────────────

ACTION_TO_CHAR: dict[str, str] = {
    "ACCELERATE": "A",
    "BRAKE":      "B",
    "TURN_LEFT":  "L",
    "TURN_RIGHT": "R",
    "PASS":       "P",
}
"""Mapping action publique (Race.ACTIONS) -> caractère 1 char pour la DB."""

CHAR_TO_ACTION: dict[str, str] = {v: k for k, v in ACTION_TO_CHAR.items()}
"""Mapping inverse : 1 caractère DB -> action publique."""


# ──────────────────────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────────────────────

_MAX_DISTANCE: int = 3
"""Distance maximale renvoyée par les sensors (saturation)."""

_TERRAIN_ROAD: str = "0"
_TERRAIN_GRASS: str = "1"

_DIR_INDEX: dict[str, int] = {d: i for i, d in enumerate(DIRECTION_ORDER)}


# ──────────────────────────────────────────────────────────────────────────
# Helpers privés
# ──────────────────────────────────────────────────────────────────────────


def _relative_direction(kart_direction: str, offset: int) -> str:
    """
    Retourne la direction absolue obtenue en tournant `offset` fois à droite.

    offset: 0=devant, -1=gauche, +1=droite, +2=derrière.
    """
    idx = _DIR_INDEX[kart_direction]
    return DIRECTION_ORDER[(idx + offset) % 4]


def _scan_distance(kart: Kart, circuit: Circuit, direction: str) -> int:
    """
    Compte les cases ROUTE consécutives depuis la position du kart dans
    `direction`, avant de rencontrer un mur, de l'herbe ou le bord.

    La ligne d'arrivée (F) est traitée comme de la route.
    Retourne un entier dans [0, _MAX_DISTANCE].
    """
    dr, dc = DIRECTIONS[direction]
    r, c = kart.position
    distance = 0
    for _ in range(_MAX_DISTANCE):
        r += dr
        c += dc
        if not circuit.is_inside(r, c):
            break
        cell = circuit.cell(r, c)
        if cell == Circuit.LETTER_WALL or cell == Circuit.LETTER_GRASS:
            break
        distance += 1
    return distance


def _encode_speed(speed: int) -> str:
    """Remappe la vitesse [-1, 2] sur [0, 3]."""
    return str(speed + 1)


# ──────────────────────────────────────────────────────────────────────────
# API publique
# ──────────────────────────────────────────────────────────────────────────


def encode_state(kart: Kart, circuit: Circuit) -> str:
    """
    Encode l'état de jeu en string de 6 caractères pour la Q-table.

    Format : "{front}{left}{right}{back}{terrain}{speed}"

    Retourne une chaîne de 6 caractères ASCII. Exemples : "321002", "000013".
    """
    front_dir = kart.direction
    left_dir  = _relative_direction(kart.direction, -1)
    right_dir = _relative_direction(kart.direction, +1)
    back_dir  = _relative_direction(kart.direction, +2)

    front = _scan_distance(kart, circuit, front_dir)
    left  = _scan_distance(kart, circuit, left_dir)
    right = _scan_distance(kart, circuit, right_dir)
    back  = _scan_distance(kart, circuit, back_dir)

    cell = circuit.cell(*kart.position)
    terrain = _TERRAIN_GRASS if cell == Circuit.LETTER_GRASS else _TERRAIN_ROAD
    speed = _encode_speed(kart.speed)

    return f"{front}{left}{right}{back}{terrain}{speed}"
