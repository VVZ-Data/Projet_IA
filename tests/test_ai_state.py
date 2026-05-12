"""
[IA-Claude] Tests unitaires de games/pixel_kart/ai_state.py.

Couvre :
- L'encodage de l'état (encode_state) sur cas simples (route longue,
  mur immédiat, route puis herbe, terrain, vitesse).
- La rotation des sensors selon la direction du kart.
- La fonction de récompense (compute_reward) pour les cas spec.
- Le compactage / inversibilité des codes d'action.
- Le calcul du timeout d'épisode.
"""

import pytest

from games.pixel_kart.ai_state import (
    ACTION_TO_CHAR,
    CHAR_TO_ACTION,
    compute_reward,
    compute_timeout,
    count_road_cells,
    encode_state,
)
from games.pixel_kart.game_model import Circuit, Kart, KartDTO


# ──────────────────────────────────────────────────────────────────────────
# Helpers de fabrication
# ──────────────────────────────────────────────────────────────────────────


def _make_kart(position: tuple[int, int], direction: str = "EAST", speed: int = 0) -> Kart:
    """Construit un Kart minimal positionné pour les tests."""
    kart = Kart(name="Test")
    kart.position = position
    kart.direction = direction
    kart.speed = speed
    return kart


def _make_circuit(rows: list[str]) -> Circuit:
    """
    Construit un Circuit à partir d'une liste de lignes de lettres.

    Exemple : `_make_circuit(["RRGG", "WWRR"])` → 2 lignes, 4 colonnes.
    """
    raw = ",".join(rows)
    return Circuit(name="test", raw=raw)


def _make_kart_dto(
    position: tuple[int, int] = (0, 0),
    speed: int = 0,
    turns_done: int = 0,
    is_alive: bool = True,
) -> KartDTO:
    """Construit un KartDTO avec valeurs par défaut sensées pour les tests reward."""
    return KartDTO(
        name="t",
        color="grey",
        position=position,
        direction="EAST",
        speed=speed,
        turns_done=turns_done,
        is_alive=is_alive,
        is_ai=True,
    )


# ──────────────────────────────────────────────────────────────────────────
# encode_state — cas simples
# ──────────────────────────────────────────────────────────────────────────


def test_long_road_saturates_front_distance() -> None:
    circuit = _make_circuit(["RRRRR"])
    kart = _make_kart((0, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    # 4 cases route devant, saturé à 3
    assert state[0] == "3"


def test_wall_in_front_gives_zero() -> None:
    # Kart à (0,1), face WEST, mur à (0,0)
    circuit = _make_circuit(["WRRRR"])
    kart = _make_kart((0, 1), direction="WEST", speed=0)
    state = encode_state(kart, circuit)
    assert state[0] == "0"


def test_two_road_then_grass() -> None:
    # Kart en (0,0). Devant lui : (0,1)=R, (0,2)=R, (0,3)=G.
    # Le scanner doit compter 2 cases route puis s'arrêter à l'herbe.
    circuit = _make_circuit(["RRRG"])
    kart = _make_kart((0, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[0] == "2"


def test_terrain_grass_encoded_as_1() -> None:
    circuit = _make_circuit(["GGG"])
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[3] == "1"


def test_terrain_road_encoded_as_0() -> None:
    circuit = _make_circuit(["RRR"])
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[3] == "0"


def test_terrain_finish_treated_as_road() -> None:
    circuit = _make_circuit(["RFR"])
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    # F est traité comme une route pour le terrain
    assert state[3] == "0"


def test_speed_minus_one_encoded_as_zero() -> None:
    circuit = _make_circuit(["RRR"])
    kart = _make_kart((0, 1), direction="EAST", speed=-1)
    state = encode_state(kart, circuit)
    assert state[4] == "0"


def test_speed_two_encoded_as_three() -> None:
    circuit = _make_circuit(["RRR"])
    kart = _make_kart((0, 1), direction="EAST", speed=2)
    state = encode_state(kart, circuit)
    assert state[4] == "3"


# ──────────────────────────────────────────────────────────────────────────
# encode_state — directions relatives
# ──────────────────────────────────────────────────────────────────────────


def test_north_facing_left_is_west() -> None:
    """Kart face NORTH : sa gauche relative pointe vers le WEST absolu."""
    # Mur en (1,0), kart en (1,1) : le WEST absolu (donc gauche relative) est mur
    circuit = _make_circuit([
        "RR",
        "WR",
    ])
    kart = _make_kart((1, 1), direction="NORTH", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"  # left distance


def test_east_facing_left_is_north() -> None:
    """Kart face EAST : sa gauche relative pointe vers le NORTH absolu."""
    # Mur en (0,0), kart en (1,0) : le NORTH absolu (gauche relative) est mur
    circuit = _make_circuit([
        "WR",
        "RR",
    ])
    kart = _make_kart((1, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"


def test_south_facing_left_is_east() -> None:
    """Kart face SOUTH : sa gauche relative pointe vers le EAST absolu."""
    # Mur en (0,1), kart en (0,0) : le EAST absolu (gauche relative) est mur
    circuit = _make_circuit([
        "RW",
        "RR",
    ])
    kart = _make_kart((0, 0), direction="SOUTH", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"


def test_west_facing_left_is_south() -> None:
    """Kart face WEST : sa gauche relative pointe vers le SOUTH absolu."""
    # Mur en (1,1), kart en (0,1) : le SOUTH absolu (gauche relative) est mur
    circuit = _make_circuit([
        "RR",
        "RW",
    ])
    kart = _make_kart((0, 1), direction="WEST", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"


def test_east_facing_right_is_south() -> None:
    """Kart face EAST : sa droite relative pointe vers le SOUTH absolu."""
    # Mur en (1,0), kart en (0,0)
    circuit = _make_circuit([
        "RR",
        "WR",
    ])
    kart = _make_kart((0, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    # state = front, left, right, ...
    assert state[2] == "0"  # right distance


# ──────────────────────────────────────────────────────────────────────────
# compute_reward
# ──────────────────────────────────────────────────────────────────────────


def test_reward_speed_2_on_road() -> None:
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=1)
    after = _make_kart_dto(position=(0, 1), speed=2)
    reward = compute_reward(before, after, circuit, nb_turns_total=3, crashed=False)
    # -0.5 (tic) + 0.2 (speed 2 réduit) + 0 (route) = -0.3
    assert reward == pytest.approx(-0.3)


def test_reward_speed_0_on_grass_is_minus_2_5() -> None:
    circuit = _make_circuit(["GGG"])
    before = _make_kart_dto(position=(0, 1), speed=0)
    after = _make_kart_dto(position=(0, 1), speed=0)
    reward = compute_reward(before, after, circuit, nb_turns_total=3, crashed=False)
    # -0.5 + 0 + (-2.0) = -2.5
    assert reward == pytest.approx(-2.5)


def test_reward_crash_is_minus_1000_only() -> None:
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=2)
    after = _make_kart_dto(position=(0, 1), speed=0, is_alive=False)
    reward = compute_reward(before, after, circuit, nb_turns_total=3, crashed=True)
    # Crash terminal : -1000, pas d'autre composante.
    # Renforcé de -100 à -1000 pour que crasher reste pire que timeout (-500).
    assert reward == -1000.0


def test_reward_first_lap_on_3_turn_race() -> None:
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=1, turns_done=0)
    after = _make_kart_dto(position=(0, 1), speed=1, turns_done=1)
    reward = compute_reward(before, after, circuit, nb_turns_total=3, crashed=False)
    # tic = -0.5 + 0.1 (speed 1 réduit) + 0 = -0.4 ; +50 pour lap 1
    assert reward == pytest.approx(49.6)


def test_reward_final_lap_on_1_turn_race() -> None:
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=1, turns_done=0)
    after = _make_kart_dto(position=(0, 1), speed=1, turns_done=1)
    reward = compute_reward(before, after, circuit, nb_turns_total=1, crashed=False)
    # tic = -0.4 ; +200 pour le tour final
    assert reward == pytest.approx(199.6)


def test_reward_lap2_on_2_turn_race_is_final() -> None:
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=0, turns_done=1)
    after = _make_kart_dto(position=(0, 1), speed=0, turns_done=2)
    reward = compute_reward(before, after, circuit, nb_turns_total=2, crashed=False)
    # tic = -0.5 (speed 0) ; +200 (final lap)
    assert reward == pytest.approx(199.5)


def test_reward_reverse_finish_applies_penalty() -> None:
    """Franchissement de la ligne à contresens : -30 en plus du tic."""
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 1), speed=1, turns_done=0)
    after = _make_kart_dto(position=(0, 0), speed=1, turns_done=-1)
    reward = compute_reward(before, after, circuit, nb_turns_total=3, crashed=False)
    # tic = -0.5 + 0.1 (speed 1) + 0 = -0.4 ; malus = -30
    assert reward == pytest.approx(-30.4)


def test_reward_double_reverse_doubles_penalty() -> None:
    """Cas théorique : deux franchissements OUEST dans le même tic = -60."""
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 1), speed=0, turns_done=2)
    after = _make_kart_dto(position=(0, 0), speed=0, turns_done=0)
    reward = compute_reward(before, after, circuit, nb_turns_total=3, crashed=False)
    # tic = -0.5 + 0 + 0 ; malus = (-2) * 30 = -60
    assert reward == pytest.approx(-60.5)


# ──────────────────────────────────────────────────────────────────────────
# Encodage des actions
# ──────────────────────────────────────────────────────────────────────────


def test_action_chars_unique() -> None:
    chars = list(ACTION_TO_CHAR.values())
    assert len(set(chars)) == len(chars)


def test_action_invertible() -> None:
    for action, char in ACTION_TO_CHAR.items():
        assert CHAR_TO_ACTION[char] == action


def test_all_race_actions_have_a_char() -> None:
    """Toutes les actions exposées par Race sont encodables."""
    from games.pixel_kart.game_model import Race
    for action in Race.ACTIONS:
        assert action in ACTION_TO_CHAR


# ──────────────────────────────────────────────────────────────────────────
# count_road_cells / compute_timeout
# ──────────────────────────────────────────────────────────────────────────


def test_count_road_cells_counts_r_and_f() -> None:
    circuit = _make_circuit(["RFG", "WRR"])
    # R, F, R, R = 4 cases parcourables
    assert count_road_cells(circuit) == 4


def test_compute_timeout_floors_at_500() -> None:
    circuit = _make_circuit(["WW"])  # zéro case route
    assert compute_timeout(circuit, nb_turns=1) == 500


def test_compute_timeout_scales_with_road_cells() -> None:
    # 500 cases route * 1 tour * 3 = 1500 (au-dessus du plancher)
    big = _make_circuit(["R" * 500])
    assert compute_timeout(big, nb_turns=1) == 1500


def test_compute_timeout_multiplies_by_nb_turns() -> None:
    circuit = _make_circuit(["R" * 200])
    # 200 * 5 * 3 = 3000
    assert compute_timeout(circuit, nb_turns=5) == 3000
