"""
[IA-Claude] Tests end-to-end pour Pixel Kart V2.

Couvre les scénarios principaux de la phase 5 :
- Le mode "vs AI" retombe sur un RandomAI quand la base est vide.
- Le mode "vs AI" utilise un QLearningAI (training=False, epsilon=0)
  après qu'au moins un Run a été créé en base.
- Les modes "Solo" et "vs Human" produisent les bons karts (1 humain
  pour Solo, 2 humains pour vs Human).
- Un cycle d'entraînement complet (petit) populate Q-values + episode_log
  et le mode "vs AI" exploite ensuite la Q-table apprise.

Les tests utilisent une base SQLite temporaire pour ne pas polluer la
vraie `pixelkart.db` du projet.
"""

import os
import tempfile
from typing import Any

import pytest

from games.pixel_kart import main as pk_main
from games.pixel_kart.ai_train import create_run, train
from games.pixel_kart.dao.q_table import EpisodeLog, QValue, Run
from games.pixel_kart.editor import map_dao
from games.pixel_kart.game_model import Circuit
from games.pixel_kart.player import Human, QLearningAI, RandomAI


# ──────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def _module_app():
    """
    Crée UNE seule PixelKartApp pour toute la durée du module de tests.

    Tkinter sur Windows a tendance à échouer (`TclError: couldn't read
    file auto.tcl`) quand on enchaîne create→destroy rapidement plusieurs
    Tk dans un même process. On contourne en réutilisant une seule app
    et en nettoyant la base SQLite entre les tests.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    pk_main._DB_PATH = tmp.name  # redirection de la DB
    application = pk_main.PixelKartApp()
    application.withdraw()
    yield application
    try:
        application.destroy()
    except Exception:
        pass
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


@pytest.fixture
def app(_module_app):
    """
    Renvoie l'app du module après nettoyage des tables SQLite.

    Ce truncate par-test permet que chaque test parte d'une base vide
    sans avoir à recréer une nouvelle PixelKartApp (cf. _module_app).
    """
    # Truncate dans l'ordre enfants → parent pour respecter les FK
    _module_app.session.query(EpisodeLog).delete()
    _module_app.session.query(QValue).delete()
    _module_app.session.query(Run).delete()
    _module_app.session.commit()
    return _module_app


@pytest.fixture
def basic_circuit() -> Circuit:
    """Charge le circuit 'Basic' depuis les ressources de l'éditeur."""
    circuits = map_dao.get_all()
    name = "Basic" if "Basic" in circuits else next(iter(circuits))
    return Circuit(name=name, raw=circuits[name])


# ──────────────────────────────────────────────────────────────────────────
# Mode "vs AI" — fallback RandomAI / utilisation de QLearningAI
# ──────────────────────────────────────────────────────────────────────────


def test_vs_ai_falls_back_to_random_when_db_empty(app: Any) -> None:
    """Aucun Run en base → l'adversaire IA est un RandomAI."""
    opponent = app._build_ai_opponent("Randy")
    assert isinstance(opponent, RandomAI)
    assert opponent.is_ai is True


def test_vs_ai_uses_qlearning_after_run_exists(app: Any, basic_circuit: Circuit) -> None:
    """Un Run existe → l'adversaire IA est un QLearningAI exploitatif."""
    create_run(
        session=app.session,
        name="t",
        gamma=0.9,
        alpha=0.1,
        epsilon_start=1.0,
        epsilon_end=0.05,
        circuit_name=basic_circuit.name,
    )

    opponent = app._build_ai_opponent("Randy")
    assert isinstance(opponent, QLearningAI)
    # En mode "play", l'IA doit exploiter sa connaissance, pas explorer
    assert opponent.training is False
    assert opponent.epsilon == 0.0


def test_vs_ai_picks_latest_run(app: Any, basic_circuit: Circuit) -> None:
    """Si plusieurs runs existent, on charge la Q-table du plus récent."""
    create_run(
        session=app.session, name="old", gamma=0.5, alpha=0.5,
        epsilon_start=1.0, epsilon_end=0.1, circuit_name=basic_circuit.name,
    )
    last_id = create_run(
        session=app.session, name="recent", gamma=0.95, alpha=0.05,
        epsilon_start=0.5, epsilon_end=0.01, circuit_name=basic_circuit.name,
    )

    opponent = app._build_ai_opponent("Randy")
    assert isinstance(opponent, QLearningAI)
    # Le QLearningAI doit avoir hérité des hyperparamètres du run le plus récent
    assert opponent.gamma == 0.95
    assert opponent.alpha == 0.05
    assert opponent.repository.run_id == last_id


# ──────────────────────────────────────────────────────────────────────────
# Modes "Solo" et "vs Human" — cartographie des karts
# ──────────────────────────────────────────────────────────────────────────


def test_solo_mode_creates_single_human_kart(app: Any, basic_circuit: Circuit, monkeypatch) -> None:
    """Mode "solo" : la course est lancée avec exactement 1 kart humain."""
    captured: dict[str, Any] = {}

    def fake_start_race(self, race) -> None:
        captured["race"] = race

    monkeypatch.setattr(pk_main.PixelKartApp, "_start_race", fake_start_race)

    app._on_play_selected({
        "mode": "solo",
        "circuit": basic_circuit.name,
        "nb_turns": 1,
    })

    race = captured["race"]
    assert len(race.karts) == 1
    assert isinstance(race.karts[0], Human)


def test_vs_human_mode_creates_two_humans(app: Any, basic_circuit: Circuit, monkeypatch) -> None:
    """Mode "human" : la course est lancée avec 2 karts humains."""
    captured: dict[str, Any] = {}

    def fake_start_race(self, race) -> None:
        captured["race"] = race

    monkeypatch.setattr(pk_main.PixelKartApp, "_start_race", fake_start_race)

    app._on_play_selected({
        "mode": "human",
        "circuit": basic_circuit.name,
        "nb_turns": 1,
    })

    race = captured["race"]
    assert len(race.karts) == 2
    assert all(isinstance(k, Human) for k in race.karts)


def test_vs_ai_mode_creates_one_human_and_one_ai(
    app: Any, basic_circuit: Circuit, monkeypatch
) -> None:
    """Mode "ai" : la course a 1 humain et 1 kart IA (Random ou QLearning)."""
    captured: dict[str, Any] = {}

    def fake_start_race(self, race) -> None:
        captured["race"] = race

    monkeypatch.setattr(pk_main.PixelKartApp, "_start_race", fake_start_race)

    app._on_play_selected({
        "mode": "ai",
        "circuit": basic_circuit.name,
        "nb_turns": 1,
    })

    race = captured["race"]
    assert len(race.karts) == 2
    assert isinstance(race.karts[0], Human)
    assert race.karts[1].is_ai is True


# ──────────────────────────────────────────────────────────────────────────
# Cycle complet : entraînement → exploitation
# ──────────────────────────────────────────────────────────────────────────


def test_training_populates_q_values_and_episode_log(
    app: Any, basic_circuit: Circuit
) -> None:
    """Un train() de quelques épisodes peuple bien les deux tables."""
    run_id = create_run(
        session=app.session,
        name="phase5",
        gamma=0.9,
        alpha=0.1,
        epsilon_start=1.0,
        epsilon_end=0.05,
        circuit_name=basic_circuit.name,
    )

    train(
        session=app.session,
        run_id=run_id,
        nb_episodes=20,
        circuit=basic_circuit,
        nb_turns=1,
    )

    nb_qv = app.session.query(QValue).filter_by(run_id=run_id).count()
    nb_log = app.session.query(EpisodeLog).filter_by(run_id=run_id).count()
    run = app.session.get(Run, run_id)

    assert nb_qv > 0, "Au moins une Q-value doit avoir été apprise"
    assert nb_log == 20
    assert run.episodes_done == 20


def test_vs_ai_after_training_exploits_q_table(
    app: Any, basic_circuit: Circuit
) -> None:
    """
    Après un entraînement réel, le mode "vs AI" charge bien la Q-table
    apprise (cache RAM non vide).
    """
    run_id = create_run(
        session=app.session,
        name="phase5-exploit",
        gamma=0.9,
        alpha=0.1,
        epsilon_start=1.0,
        epsilon_end=0.05,
        circuit_name=basic_circuit.name,
    )
    train(
        session=app.session,
        run_id=run_id,
        nb_episodes=20,
        circuit=basic_circuit,
        nb_turns=1,
    )

    opponent = app._build_ai_opponent("Randy")
    assert isinstance(opponent, QLearningAI)
    # Le repository a chargé en RAM les Q-values du run
    assert len(opponent.repository.q_values) > 0
    # On exploite, on n'apprend plus
    assert opponent.training is False
