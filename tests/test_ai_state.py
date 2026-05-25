"""
Tests unitaires de games/pixel_kart/ai_state.py.

Couvre :
- L'encodage de l'état (encode_state) sur cas simples (route longue,
  mur immédiat, route puis herbe, terrain, vitesse, sensor arrière).
- La rotation des sensors selon la direction du kart.
- La fonction de récompense (compute_reward) pour les cas spec.
- Le compactage / inversibilité des codes d'action.
- Le calcul du timeout d'épisode.
"""

import pytest

from games.pixel_kart.ai_state import (
    ACTION_TO_CHAR,
    CHAR_TO_ACTION,
    encode_state,
)
from games.pixel_kart.ai_train import (
    compute_reward,
    compute_timeout,
    count_road_cells,
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
# encode_state — format et indices
# État : {front}{left}{right}{back}{terrain}{speed}  →  indices 0,1,2,3,4,5
# ──────────────────────────────────────────────────────────────────────────


def test_long_road_saturates_front_distance() -> None:
    circuit = _make_circuit(["RRRRR"])
    kart = _make_kart((0, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[0] == "3"


def test_wall_in_front_gives_zero() -> None:
    circuit = _make_circuit(["WRRRR"])
    kart = _make_kart((0, 1), direction="WEST", speed=0)
    state = encode_state(kart, circuit)
    assert state[0] == "0"


def test_two_road_then_grass() -> None:
    circuit = _make_circuit(["RRRG"])
    kart = _make_kart((0, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[0] == "2"


def test_back_sensor_reads_behind_kart() -> None:
    """Sensor arrière : wall derrière → 0."""
    circuit = _make_circuit(["WRRRR"])
    # Kart face EAST : derrière = WEST = (0,0) qui est un mur
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[3] == "0"  # back distance


def test_terrain_grass_encoded_as_1() -> None:
    circuit = _make_circuit(["GGG"])
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[4] == "1"


def test_terrain_road_encoded_as_0() -> None:
    circuit = _make_circuit(["RRR"])
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[4] == "0"


def test_terrain_finish_treated_as_road() -> None:
    circuit = _make_circuit(["RFR"])
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[4] == "0"


def test_speed_minus_one_encoded_as_zero() -> None:
    circuit = _make_circuit(["RRR"])
    kart = _make_kart((0, 1), direction="EAST", speed=-1)
    state = encode_state(kart, circuit)
    assert state[5] == "0"


def test_speed_two_encoded_as_three() -> None:
    circuit = _make_circuit(["RRR"])
    kart = _make_kart((0, 1), direction="EAST", speed=2)
    state = encode_state(kart, circuit)
    assert state[5] == "3"


def test_state_has_six_characters() -> None:
    circuit = _make_circuit(["RRR"])
    kart = _make_kart((0, 1), direction="EAST", speed=0)
    assert len(encode_state(kart, circuit)) == 6


# ──────────────────────────────────────────────────────────────────────────
# encode_state — directions relatives
# ──────────────────────────────────────────────────────────────────────────


def test_north_facing_left_is_west() -> None:
    """Kart face NORTH : sa gauche relative pointe vers le WEST absolu."""
    circuit = _make_circuit([
        "RR",
        "WR",
    ])
    kart = _make_kart((1, 1), direction="NORTH", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"  # left distance


def test_east_facing_left_is_north() -> None:
    """Kart face EAST : sa gauche relative pointe vers le NORTH absolu."""
    circuit = _make_circuit([
        "WR",
        "RR",
    ])
    kart = _make_kart((1, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"


def test_south_facing_left_is_east() -> None:
    """Kart face SOUTH : sa gauche relative pointe vers le EAST absolu."""
    circuit = _make_circuit([
        "RW",
        "RR",
    ])
    kart = _make_kart((0, 0), direction="SOUTH", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"


def test_west_facing_left_is_south() -> None:
    """Kart face WEST : sa gauche relative pointe vers le SOUTH absolu."""
    circuit = _make_circuit([
        "RR",
        "RW",
    ])
    kart = _make_kart((0, 1), direction="WEST", speed=0)
    state = encode_state(kart, circuit)
    assert state[1] == "0"


def test_east_facing_right_is_south() -> None:
    """Kart face EAST : sa droite relative pointe vers le SOUTH absolu."""
    circuit = _make_circuit([
        "RR",
        "WR",
    ])
    kart = _make_kart((0, 0), direction="EAST", speed=0)
    state = encode_state(kart, circuit)
    assert state[2] == "0"  # right distance


# ──────────────────────────────────────────────────────────────────────────
# compute_reward
# ──────────────────────────────────────────────────────────────────────────


def test_reward_speed_2_on_road() -> None:
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=1)
    after = _make_kart_dto(position=(0, 1), speed=2)
    reward = compute_reward(before, after, circuit)
    # -0.5 (tic) + 0.4 (speed 2) + 0 (route) = -0.1
    assert reward == pytest.approx(-0.1)


def test_reward_speed_0_on_grass() -> None:
    circuit = _make_circuit(["GGG"])
    before = _make_kart_dto(position=(0, 1), speed=0)
    after = _make_kart_dto(position=(0, 1), speed=0)
    reward = compute_reward(before, after, circuit)
    # -0.5 + (-0.1) (speed 0) + (-2.0) (herbe) = -2.6
    assert reward == pytest.approx(-2.6)


def test_reward_crash_detected_from_dtos() -> None:
    """Le crash est détecté depuis les DTOs (is_alive avant=True, après=False)."""
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=2)
    after = _make_kart_dto(position=(0, 1), speed=0, is_alive=False)
    reward = compute_reward(before, after, circuit)
    assert reward == -200.0


def test_reward_lap_bonus_is_400() -> None:
    """Tout tour complété dans le bon sens rapporte +400."""
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=1, turns_done=0)
    after = _make_kart_dto(position=(0, 1), speed=1, turns_done=1)
    reward = compute_reward(before, after, circuit)
    # tic = -0.5 + 0.2 (speed 1) = -0.3 ; +400 pour le tour
    assert reward == pytest.approx(399.7)


def test_reward_reverse_finish_applies_penalty() -> None:
    """Franchissement de la ligne à contresens : -30 en plus du tic."""
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 1), speed=1, turns_done=0)
    after = _make_kart_dto(position=(0, 0), speed=1, turns_done=-1)
    reward = compute_reward(before, after, circuit)
    # tic = -0.5 + 0.2 (speed 1) = -0.3 ; malus = -30
    assert reward == pytest.approx(-30.3)


def test_reward_reverse_finish_is_flat_penalty() -> None:
    """Franchissement à contresens : malus fixe de -30 quelle que soit la valeur de turns_diff."""
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 1), speed=0, turns_done=2)
    after = _make_kart_dto(position=(0, 0), speed=0, turns_done=0)
    reward = compute_reward(before, after, circuit)
    # tic = -0.5 + (-0.1) (speed 0) = -0.6 ; malus = -30
    assert reward == pytest.approx(-30.6)


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
    assert count_road_cells(circuit) == 4


def test_compute_timeout_floors_at_500() -> None:
    circuit = _make_circuit(["WW"])
    assert compute_timeout(circuit, nb_turns=1) == 500


def test_compute_timeout_scales_with_road_cells() -> None:
    big = _make_circuit(["R" * 500])
    assert compute_timeout(big, nb_turns=1) == 1500


def test_compute_timeout_multiplies_by_nb_turns() -> None:
    circuit = _make_circuit(["R" * 200])
    assert compute_timeout(circuit, nb_turns=5) == 3000


# ──────────────────────────────────────────────────────────────────────────
# Reward shaping (heat-map)
# ──────────────────────────────────────────────────────────────────────────


def test_shaping_positive_when_progressing_toward_finish() -> None:
    circuit = _make_circuit(["RRFRR"])
    before = _make_kart_dto(position=(0, 0), speed=1)
    after = _make_kart_dto(position=(0, 1), speed=1)
    reward = compute_reward(before, after, circuit)
    # tic = -0.5 + 0.2 (speed 1) = -0.3 ; shaping = +1 ; total = +0.7
    assert reward == pytest.approx(0.7)


def test_shaping_negative_when_going_backwards() -> None:
    circuit = _make_circuit(["RRFRR"])
    before = _make_kart_dto(position=(0, 1), speed=1)
    after = _make_kart_dto(position=(0, 0), speed=1)
    reward = compute_reward(before, after, circuit)
    # tic = -0.3 ; shaping = -1 ; total = -1.3
    assert reward == pytest.approx(-1.3)


def test_shaping_zero_when_circuit_has_no_finish() -> None:
    circuit = _make_circuit(["RRR"])
    before = _make_kart_dto(position=(0, 0), speed=1)
    after = _make_kart_dto(position=(0, 1), speed=1)
    reward = compute_reward(before, after, circuit)
    # tic = -0.3 ; pas de shaping
    assert reward == pytest.approx(-0.3)


def test_shaping_not_applied_on_crash() -> None:
    """Sur un crash, seule la pénalité -200 compte (pas de shaping)."""
    circuit = _make_circuit(["RRFRR"])
    before = _make_kart_dto(position=(0, 0), speed=2)
    after = _make_kart_dto(position=(0, 1), speed=0, is_alive=False)
    reward = compute_reward(before, after, circuit)
    assert reward == -200.0
