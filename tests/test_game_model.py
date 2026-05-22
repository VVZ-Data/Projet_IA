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


# ──────────────────────────────────────────────────────────────────────────
# Heat-map de distance (Circuit._compute_distance_map)
# ──────────────────────────────────────────────────────────────────────────


def test_distance_map_finish_cell_is_zero() -> None:
    """Les cases F elles-mêmes ont une distance 0 (le but est atteint)."""
    circuit = Circuit("t", "RRFRR")
    assert circuit.distance_map[(0, 2)] == 0


def test_distance_map_just_west_of_finish_is_one() -> None:
    """La case immédiatement à l'ouest de F est la source du BFS = distance 1."""
    circuit = Circuit("t", "RRFRR")
    assert circuit.distance_map[(0, 1)] == 1
    assert circuit.distance_map[(0, 0)] == 2


def test_distance_map_just_east_of_finish_is_unreachable() -> None:
    """
    Sur un circuit en ligne droite (pas une boucle), les cases à l'est de F
    ne sont pas accessibles via la voie correcte → absentes du map.
    """
    circuit = Circuit("t", "RRFRR")
    # F est traité comme un mur pendant le BFS, donc (0,3) et (0,4) n'ont
    # pas de chemin légal jusqu'à la source ouest.
    assert (0, 3) not in circuit.distance_map
    assert (0, 4) not in circuit.distance_map


def test_distance_map_loop_circuit_east_side_has_high_distance() -> None:
    """
    Petite boucle : F en haut au milieu, route partout autour.
    La case juste à l'est de F doit avoir une distance ÉLEVÉE
    (il faut faire le tour complet pour la rejoindre par la voie correcte).
    """
    circuit = Circuit("t", "RFR,RRR,RRR")
    dmap = circuit.distance_map
    # Case juste ouest de F : la source du BFS = 1
    assert dmap[(0, 0)] == 1
    # Case juste est de F : doit faire le tour, donc distance > 1
    assert (0, 2) in dmap
    assert dmap[(0, 2)] > dmap[(0, 0)]


def test_distance_map_excludes_walls() -> None:
    """Les cases mur ne sont jamais dans le map."""
    circuit = Circuit("t", "RFR,WRW,RRR")
    assert (1, 0) not in circuit.distance_map
    assert (1, 2) not in circuit.distance_map


def test_distance_map_empty_when_no_finish() -> None:
    """Sans ligne d'arrivée, pas de heat-map calculable."""
    circuit = Circuit("t", "RRR")
    assert circuit.distance_map == {}
