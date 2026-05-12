"""
[IA-Claude] Encodage d'état et fonction de récompense pour l'IA Q-learning de Pixel Kart.

Module sans effet de bord. Contient :
- ACTION_TO_CHAR / CHAR_TO_ACTION : encodage 1 caractère des actions
- encode_state : transforme un (Kart, Circuit) en clé string compacte de 5 chars
- compute_reward : calcule la récompense d'une transition (avant -> après)
- compute_timeout : estime un nombre maximum de tics par épisode
- count_road_cells : helper utilisé pour le timeout

Le format d'état string est volontairement minimal pour limiter la taille
de la Q-table et favoriser la généralisation entre circuits :
    "{front}{left}{right}{terrain}{speed}"
    front/left/right ∈ {0,1,2,3} : nombre de cases route consécutives
                                   dans la direction (relative au kart),
                                   saturé à 3.
    terrain          ∈ {0,1}     : 0 si route ou finish, 1 si herbe.
    speed            ∈ {0,1,2,3} : speed remappé (-1 -> 0, 0 -> 1, 1 -> 2, 2 -> 3).

Les sensors sont RELATIFS à la direction du kart : ce qui est "devant"
dépend de `kart.direction`. Cela permet à l'IA de réutiliser ce qu'elle
apprend quelle que soit l'orientation absolue du kart.
"""

from games.pixel_kart.game_model import (
    DIRECTION_ORDER,
    DIRECTIONS,
    Circuit,
    Kart,
    KartDTO,
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
"""Mapping inverse de ACTION_TO_CHAR : 1 caractère DB -> action publique."""


# ──────────────────────────────────────────────────────────────────────────
# Constantes internes
# ──────────────────────────────────────────────────────────────────────────

_MAX_DISTANCE: int = 3
"""Distance maximale renvoyée par les sensors (saturation)."""

_TERRAIN_ROAD: str = "0"
_TERRAIN_GRASS: str = "1"

# Index dans DIRECTION_ORDER pour calcul des directions relatives
_DIR_INDEX: dict[str, int] = {d: i for i, d in enumerate(DIRECTION_ORDER)}


# ──────────────────────────────────────────────────────────────────────────
# Helpers privés
# ──────────────────────────────────────────────────────────────────────────


def _relative_direction(kart_direction: str, offset: int) -> str:
    """
    Calcule la direction absolue obtenue en tournant `offset` fois à droite.

    Args:
        kart_direction: Direction courante du kart (NORTH/EAST/SOUTH/WEST).
        offset: Décalage : 0 = devant, -1 = gauche relative, +1 = droite relative.

    Returns:
        La direction absolue résultante.
    """
    idx = _DIR_INDEX[kart_direction]
    return DIRECTION_ORDER[(idx + offset) % 4]


def _scan_distance(kart: Kart, circuit: Circuit, direction: str) -> int:
    """
    Compte le nombre de cases ROUTE consécutives à partir de la position du
    kart dans la direction donnée, avant de rencontrer mur/herbe/bord.

    Note : la ligne d'arrivée (F) est traitée comme de la route (parcourable).

    Args:
        kart: Kart dont on part (sa position est utilisée).
        circuit: Circuit en cours.
        direction: Direction absolue du scan (NORTH/EAST/SOUTH/WEST).

    Returns:
        Distance entière dans [0, _MAX_DISTANCE].
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
        # ROAD ('R') ou FINISH ('F') : on incrémente
        distance += 1
    return distance


def _encode_speed(speed: int) -> str:
    """
    Remappe la vitesse [-1, 2] sur [0, 3] pour tenir sur 1 caractère.

    Args:
        speed: Vitesse du kart, attendue dans [-1, 2].

    Returns:
        Caractère ASCII '0'..'3'.
    """
    return str(speed + 1)


def _tick_reward(kart_after: KartDTO, circuit: Circuit) -> float:
    """
    Récompense de base appliquée à chaque tic non terminal.

    Composantes :
    - Coût temps fixe : -0.5
    - Bonus vitesse : +0.1 si speed=1, +0.2 si speed=2, sinon 0
    - Malus terrain : -2.0 sur herbe, 0 sur route/finish

    Les bonus de vitesse sont volontairement faibles (auparavant +0.5/+1.5)
    pour éviter que l'IA "finance" des crashs intentionnels en accumulant
    du bonus avant d'aller percuter un mur. Le signal principal reste
    le bonus de complétion de tour.

    Args:
        kart_after: État du kart après l'action.
        circuit: Circuit en cours.

    Returns:
        Récompense flottante.
    """
    base = -0.5

    speed = kart_after.speed
    if speed == 1:
        speed_bonus = 0.1
    elif speed == 2:
        speed_bonus = 0.2
    else:
        speed_bonus = 0.0

    if circuit.is_inside(*kart_after.position):
        cell = circuit.cell(*kart_after.position)
    else:
        cell = Circuit.LETTER_ROAD  # cas de bord, ne devrait pas arriver
    terrain_malus = -2.0 if cell == Circuit.LETTER_GRASS else 0.0

    return base + speed_bonus + terrain_malus


def _lap_bonus(turn_just_done: int, nb_turns_total: int) -> float:
    """
    Récompense pour la complétion d'un tour, selon le total de tours requis.

    La récompense croît avec l'avancement : finir le dernier tour vaut
    toujours +200, tandis qu'un tour intermédiaire vaut moins.

    Args:
        turn_just_done: Numéro du tour qui vient d'être validé (>=1).
        nb_turns_total: Nombre total de tours à effectuer pour finir.

    Returns:
        Récompense flottante (toujours positive).
    """
    if nb_turns_total == 1:
        return 200.0
    if nb_turns_total == 2:
        return 200.0 if turn_just_done >= 2 else 100.0
    # nb_turns_total >= 3
    if turn_just_done == 1:
        return 50.0
    if turn_just_done == 2:
        return 100.0
    return 200.0


# ──────────────────────────────────────────────────────────────────────────
# API publique
# ──────────────────────────────────────────────────────────────────────────


def encode_state(kart: Kart, circuit: Circuit) -> str:
    """
    Encode l'état de jeu en string de 5 caractères pour la Q-table.

    Le résultat est de la forme "{front}{left}{right}{terrain}{speed}".

    Args:
        kart: Kart dont on encode l'état (position, direction, vitesse).
        circuit: Circuit en cours, utilisé pour calculer les distances.

    Returns:
        Chaîne de 5 caractères ASCII. Exemples : "32102", "00013".
    """
    front_dir = kart.direction
    left_dir = _relative_direction(kart.direction, -1)
    right_dir = _relative_direction(kart.direction, +1)

    front = _scan_distance(kart, circuit, front_dir)
    left = _scan_distance(kart, circuit, left_dir)
    right = _scan_distance(kart, circuit, right_dir)

    cell = circuit.cell(*kart.position)
    terrain = _TERRAIN_GRASS if cell == Circuit.LETTER_GRASS else _TERRAIN_ROAD
    speed = _encode_speed(kart.speed)

    return f"{front}{left}{right}{terrain}{speed}"


def count_road_cells(circuit: Circuit) -> int:
    """
    Compte le nombre de cases parcourables (route + ligne d'arrivée).

    Args:
        circuit: Circuit à analyser.

    Returns:
        Nombre total de cases R + F.
    """
    count = 0
    for row in circuit.grid:
        for cell in row:
            if cell == Circuit.LETTER_ROAD or cell == Circuit.LETTER_FINISH:
                count += 1
    return count


def compute_timeout(circuit: Circuit, nb_turns: int) -> int:
    """
    Calcule le nombre maximum de tics autorisés pour un épisode.

    Heuristique : `max(500, nb_road_cells * nb_turns * 3)`. Le 3 reflète
    le fait qu'à vitesse 0 ou avec des allers-retours l'IA peut prendre
    plusieurs tics par case avant d'apprendre un trajet efficace.

    Args:
        circuit: Circuit en cours.
        nb_turns: Nombre de tours à effectuer.

    Returns:
        Nombre maximum de tics autorisés.
    """
    return max(500, count_road_cells(circuit) * nb_turns * 3)


_REVERSE_FINISH_PENALTY: float = 30.0
"""Malus appliqué à chaque franchissement de la ligne d'arrivée à contresens."""


def compute_reward(
    kart_before: KartDTO,
    kart_after: KartDTO,
    circuit: Circuit,
    nb_turns_total: int,
    crashed: bool,
) -> float:
    """
    Calcule la récompense entre l'état avant et l'état après une action.

    En cas de crash, la récompense est terminale (-100) et aucune autre
    composante n'est ajoutée. Sinon, on cumule :
    - la récompense par tic (coût temps + bonus vitesse + malus terrain)
    - un bonus de tour si `turns_done` a augmenté (franchissement EST normal)
    - un malus de -30 par tour "perdu" si `turns_done` a diminué
      (franchissement OUEST, à contresens)

    Le malus `turns_diff * 30` se généralise au cas théorique où plusieurs
    franchissements à contresens arriveraient dans le même tic (vitesse
    élevée et ligne traversée plusieurs fois).

    Args:
        kart_before: État du kart avant l'action.
        kart_after: État du kart après l'action.
        circuit: Circuit en cours.
        nb_turns_total: Nombre total de tours requis pour finir la course.
        crashed: True si le kart vient de crasher dans un mur.

    Returns:
        Récompense flottante (peut être négative ou positive).
    """
    if crashed:
        # -1000 (et non -100) pour garantir que crasher reste pire que
        # le malus de timeout (-500). Avant ce changement, l'IA pouvait
        # rationnellement préférer un crash à un timeout, ce qui menait
        # à des taux de crash > 95 %.
        return -1000.0

    reward = _tick_reward(kart_after, circuit)

    turns_diff = kart_after.turns_done - kart_before.turns_done
    if turns_diff > 0:
        reward += _lap_bonus(kart_after.turns_done, nb_turns_total)
    elif turns_diff < 0:
        # Franchissement à contresens : turns_diff est négatif,
        # le produit reste donc négatif et applique un malus.
        reward += turns_diff * _REVERSE_FINISH_PENALTY

    return reward
