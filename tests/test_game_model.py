"""
[IA-Claude] Tests unitaires de games/pixel_kart/game_model.py.

Couvre les comportements critiques de la logique de course :
- Détection des franchissements de la ligne d'arrivée (EST → +1 tour,
  OUEST → -1 tour, allers-retours).
- Conditions de fin de course : la course se gèle dès qu'un kart finit,
  même si d'autres karts sont encore en jeu.
"""

from games.pixel_kart.game_model import Circuit, Kart, Race
from games.pixel_kart.player import Human


def _make_kart(name: str = "Test") -> Human:
    """Construit un Human kart (pas d'IA, pas de couleur particulière)."""
    return Human(name)


# ──────────────────────────────────────────────────────────────────────────
# Franchissements de la ligne d'arrivée
# ──────────────────────────────────────────────────────────────────────────


def test_east_crossing_increments_turns_done() -> None:
    """Franchir la ligne F vers l'EST → +1 tour."""
    # Circuit : 1 ligne, F en colonne 1, route partout. Kart en (0,0).
    circuit = Circuit("t", "RFRR")
    kart = _make_kart()
    race = Race(circuit=circuit, karts=[kart], nb_turns=10)
    kart.position = (0, 0)
    kart.direction = "EAST"
    kart.speed = 1
    race._move_kart(kart)
    # Le kart est passé de col 0 à col 1, traversant finish_col=1
    assert kart.turns_done == 1
    assert kart.position == (0, 1)


def test_west_crossing_decrements_turns_done() -> None:
    """Franchir la ligne F vers l'OUEST → -1 tour."""
    # Circuit : F en col 1, route partout. On franchit la ligne en passant
    # de col 1 (sur F = côté "droit" du modèle) à col 0 (côté gauche).
    circuit = Circuit("t", "RFRR")
    kart = _make_kart()
    race = Race(circuit=circuit, karts=[kart], nb_turns=10)
    kart.position = (0, 1)
    kart.direction = "WEST"
    kart.speed = 1
    race._move_kart(kart)
    assert kart.turns_done == -1
    assert kart.position == (0, 0)


def test_east_west_east_yields_one_lap() -> None:
    """EST puis OUEST puis EST : turns_done final = 1 (avec malus au passage)."""
    circuit = Circuit("t", "RRFRR")
    kart = _make_kart()
    race = Race(circuit=circuit, karts=[kart], nb_turns=10)

    # Place le kart à gauche, on l'envoie à l'EST
    kart.position = (0, 1)
    kart.direction = "EAST"
    kart.speed = 1
    race._move_kart(kart)
    assert kart.turns_done == 1
    assert kart.position == (0, 2)

    # Demi-tour vers l'OUEST
    kart.direction = "WEST"
    kart.speed = 1
    race._move_kart(kart)
    assert kart.turns_done == 0
    assert kart.position == (0, 1)

    # Re-franchir vers l'EST
    kart.direction = "EAST"
    kart.speed = 1
    race._move_kart(kart)
    assert kart.turns_done == 1


def test_negative_speed_crossing_west_decrements() -> None:
    """
    Vitesse négative : un kart orienté EAST mais à vitesse -1 recule
    vers l'OUEST. Si ce mouvement traverse la ligne, on doit décrémenter.
    """
    circuit = Circuit("t", "RFRR")
    kart = _make_kart()
    race = Race(circuit=circuit, karts=[kart], nb_turns=10)
    kart.position = (0, 1)
    kart.direction = "EAST"   # mais on recule
    kart.speed = -1
    race._move_kart(kart)
    # Mouvement réel : col 1 (sur F) → col 0 (gauche de F), donc franchissement OUEST
    assert kart.turns_done == -1
    assert kart.position == (0, 0)


# ──────────────────────────────────────────────────────────────────────────
# Fin de course (Bug 1)
# ──────────────────────────────────────────────────────────────────────────


def test_race_finished_as_soon_as_one_kart_wins() -> None:
    """
    Dès qu'un kart vivant complète tous ses tours, la course est finie
    pour tout le monde — même si d'autres karts sont encore actifs.
    """
    circuit = Circuit("t", "RRR,RRR,RRR")
    human = _make_kart("Human")
    ai = _make_kart("AI")
    race = Race(circuit=circuit, karts=[human, ai], nb_turns=2)

    # AI gagne, humain encore vivant et pas done
    ai.turns_done = 2
    assert ai.is_alive
    assert human.is_alive
    assert not race._kart_done(human)

    assert race.is_finished() is True
    assert race.winner() is ai


def test_race_finished_when_all_dead_or_done() -> None:
    """Cas dégénéré conservé : tous les karts crashés ou tous ayant fini."""
    circuit = Circuit("t", "RRR")
    k1 = _make_kart("k1")
    k2 = _make_kart("k2")
    race = Race(circuit=circuit, karts=[k1, k2], nb_turns=1)

    k1.is_alive = False
    k2.is_alive = False
    assert race.is_finished() is True
    assert race.winner() is None


def test_race_not_finished_while_someone_can_play() -> None:
    """Tant qu'aucun kart n'a fini et qu'au moins un peut jouer, la course continue."""
    circuit = Circuit("t", "RRR,RRR")
    k1 = _make_kart("k1")
    k2 = _make_kart("k2")
    race = Race(circuit=circuit, karts=[k1, k2], nb_turns=3)
    # Aucun n'a fini, tous vivants
    assert race.is_finished() is False
