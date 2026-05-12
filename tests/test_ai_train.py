"""
[IA-Claude] Tests unitaires de games/pixel_kart/ai_train.py.

Couvre `run_episode` :
- Un épisode qui se termine par timeout (pas de victoire, pas de crash)
  applique bien le malus TIMEOUT_PENALTY.
- Un épisode terminé normalement (victoire ou crash) n'applique pas
  ce malus.
"""

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from games.pixel_kart.ai_train import TIMEOUT_PENALTY, create_run, run_episode
from games.pixel_kart.dao.base import Base
from games.pixel_kart.dao.q_table_repository import QTableRepository
from games.pixel_kart.editor import map_dao
from games.pixel_kart.game_model import Circuit
from games.pixel_kart.player import QLearningAI


@pytest.fixture
def repo_and_circuit():
    """
    Construit un repo Q-table sur une base SQLite temporaire et un Circuit
    Basic pour tester `run_episode` en isolation.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    engine = create_engine(f"sqlite:///{tmp.name}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    name = "Basic" if "Basic" in map_dao.get_all() else next(iter(map_dao.get_all()))
    circuit = Circuit(name=name, raw=map_dao.get_all()[name])

    run_id = create_run(
        session=session, name="t",
        gamma=0.9, alpha=0.1,
        epsilon_start=0.0, epsilon_end=0.0,
        circuit_name=name,
    )
    repository = QTableRepository(session, run_id=run_id)

    yield repository, circuit

    session.close()
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


def test_timeout_penalty_applied_when_episode_times_out(
    monkeypatch: pytest.MonkeyPatch, repo_and_circuit
) -> None:
    """
    Kart qui joue toujours PASS : il ne crashe pas, ne finit pas. Au
    timeout, TIMEOUT_PENALTY doit être ajouté à la récompense cumulée.
    """
    repository, circuit = repo_and_circuit
    ai = QLearningAI(
        name="Stagnator", repository=repository,
        gamma=0.9, alpha=0.1, epsilon=0.0, training=True,
    )

    # Forcer l'IA à toujours jouer PASS → le kart ne bouge pas
    monkeypatch.setattr(QLearningAI, "choose_action", lambda self, race: "PASS")

    timeout = 10
    total_reward, ticks, finished, crashed = run_episode(
        ai_kart=ai, circuit=circuit, nb_turns=1, timeout=timeout,
    )

    assert not finished, "PASS pur ne doit jamais terminer la course"
    assert not crashed, "PASS pur ne fait pas crasher"
    assert ticks == timeout, "L'épisode doit aller jusqu'au timeout"
    # tic_reward sur route avec speed=0 = -0.5 ; cumul + malus stagnation
    expected = -0.5 * timeout + TIMEOUT_PENALTY
    assert total_reward == pytest.approx(expected)


def test_no_timeout_penalty_on_crash(
    monkeypatch: pytest.MonkeyPatch, repo_and_circuit
) -> None:
    """
    Un épisode qui se termine par crash ne doit pas recevoir le malus
    timeout (le crash a déjà sa propre récompense -100).
    """
    repository, _ = repo_and_circuit

    # Mini-circuit déterministe : F à (0,0), W juste à l'est → crash garanti
    # au premier ACCELERATE.
    crash_circuit = Circuit(name="crash", raw="FWWWW")

    ai = QLearningAI(
        name="Crasher", repository=repository,
        gamma=0.9, alpha=0.1, epsilon=0.0, training=True,
    )

    # Forcer ACCELERATE → speed 1 EAST → bump into wall en 1 tic
    monkeypatch.setattr(QLearningAI, "choose_action", lambda self, race: "ACCELERATE")

    timeout = 50
    total_reward, ticks, finished, crashed = run_episode(
        ai_kart=ai, circuit=crash_circuit, nb_turns=1, timeout=timeout,
    )

    assert crashed is True
    assert finished is False
    # La récompense du crash est -1000. Le malus de stagnation (-500) ne
    # doit PAS s'y ajouter (sinon total descendrait vers -1500).
    assert total_reward == pytest.approx(-1000.0, abs=10.0)
    # Vérification explicite que le malus timeout n'a pas été appliqué :
    # avec timeout en plus on serait <= -1500, donc on doit rester au-dessus.
    assert total_reward > -1000.0 + TIMEOUT_PENALTY + 10, (
        "Le malus timeout ne doit pas être appliqué après un crash"
    )
