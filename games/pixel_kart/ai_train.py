"""
Boucle d'entraînement Q-learning pour Pixel Kart.

Trois fonctions publiques :

- `create_run`  : crée une nouvelle ligne `runs` en base et renvoie son ID.
- `train`       : lance N épisodes pour un run donné, en flushant la
                  Q-table périodiquement et en notifiant l'UI via callback.
- `run_episode` : joue un épisode complet (un kart seul sur le circuit)
                  et renvoie ses statistiques.

Utilitaires d'entraînement également définis ici :

- `count_road_cells` : nombre de cases parcourables d'un circuit.
- `compute_timeout`  : borne max de tics par épisode.
- `compute_reward`   : récompense d'une transition (avant → après).

Architecture :
- L'IA est instanciée localement à `train()` ; elle n'est pas exposée hors
  de cette boucle (la vue d'entraînement n'a pas à connaître `QLearningAI`).
- La récompense est calculée ici, séparée du modèle de jeu (MVC strict).
- Le repository `QTableRepository` cache les Q-values en RAM et flushe
  par batch de `_FLUSH_INTERVAL` épisodes.
"""

from typing import Callable, Optional

from sqlalchemy.orm import Session

from games.pixel_kart.ai_state import (
    ACTION_TO_CHAR,
    encode_state,
)
from games.pixel_kart.dao.q_table import EpisodeLog, Run
from games.pixel_kart.dao.q_table_repository import QTableRepository
from games.pixel_kart.game_model import Circuit, KartDTO, Race
from games.pixel_kart.player import QLearningAI


_FLUSH_INTERVAL: int = 500
"""Nombre d'épisodes entre deux flushes en base (Q-values + logs)."""

TIMEOUT_PENALTY: float = -2000.0
"""
Malus appliqué quand un épisode se termine par timeout.

Strictement plus sévère que le crash (-200) pour que l'IA préfère
tenter d'avancer plutôt que stagner.
"""

_CRASH_PENALTY: float = -200.0
"""Malus appliqué lors d'un crash dans un mur."""

_LAP_BONUS: float = 400.0
"""Récompense fixe accordée à chaque tour complété dans le bon sens."""

_REVERSE_FINISH_PENALTY: float = 30.0
"""Malus appliqué lors d'un franchissement de la ligne d'arrivée à contresens."""



# ──────────────────────────────────────────────────────────────────────────
# Utilitaires de récompense (privés)
# ──────────────────────────────────────────────────────────────────────────


def _tick_reward(kart_after: KartDTO, circuit: Circuit) -> float:
    """
    Récompense de base appliquée à chaque tic non terminal.

    - Coût temps fixe : -0.5
    - Bonus vitesse : +0.1 si speed=1, +0.2 si speed=2
    - Malus terrain : -2.0 sur herbe
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
        cell = Circuit.LETTER_ROAD
    terrain_malus = -2.0 if cell == Circuit.LETTER_GRASS else 0.0

    return base + speed_bonus + terrain_malus


def _lap_bonus(turns_done: int) -> float:
    """Retourne le bonus fixe pour un tour complété dans le bon sens (0 si pas de progrès)."""
    return _LAP_BONUS if turns_done > 0 else 0.0


# ──────────────────────────────────────────────────────────────────────────
# API publique — utilitaires d'entraînement
# ──────────────────────────────────────────────────────────────────────────


def count_road_cells(circuit: Circuit) -> int:
    """Compte le nombre de cases parcourables (route + ligne d'arrivée)."""
    count = 0
    for row in circuit.grid:
        for cell in row:
            if cell == Circuit.LETTER_ROAD or cell == Circuit.LETTER_FINISH:
                count += 1
    return count


def compute_timeout(circuit: Circuit, nb_turns: int) -> int:
    """
    Calcule le nombre maximum de tics autorisés pour un épisode.

    Heuristique : `max(500, nb_road_cells * nb_turns * 3)`.
    """
    return max(500, count_road_cells(circuit) * nb_turns * 3)


def compute_reward(
    kart_before: KartDTO,
    kart_after: KartDTO,
    circuit: Circuit,
) -> float:
    """
    Calcule la récompense entre l'état avant et l'état après une action.

    En cas de crash (kart vivant avant, mort après), retourne -200 directement.
    Sinon, cumule :
    - la récompense par tic (coût temps + bonus vitesse + malus herbe)
    - +400 si la ligne d'arrivée est franchie dans le bon sens
    - -30 si la ligne d'arrivée est franchie à contresens
    """
    crashed = kart_before.is_alive and not kart_after.is_alive
    if crashed:
        return _CRASH_PENALTY

    reward = _tick_reward(kart_after, circuit)

    turns_diff = kart_after.turns_done - kart_before.turns_done
    if turns_diff > 0:
        reward += _lap_bonus(kart_after.turns_done)
    elif turns_diff < 0:
        reward -= _REVERSE_FINISH_PENALTY

    return reward


# ──────────────────────────────────────────────────────────────────────────
# Création / récupération d'un run
# ──────────────────────────────────────────────────────────────────────────


def create_run(
    session: Session,
    name: str,
    gamma: float,
    alpha: float,
    epsilon_start: float,
    epsilon_end: float,
    circuit_name: str,
    notes: str = "",
) -> int:
    """
    Crée un nouveau Run en base et renvoie son ID.

    Args:
        session: Session SQLAlchemy active.
        name: Nom lisible du run.
        gamma: Facteur d'escompte γ.
        alpha: Taux d'apprentissage α.
        epsilon_start: ε au début de l'entraînement (exploration max).
        epsilon_end: ε en fin d'entraînement (exploitation quasi pure).
        circuit_name: Nom du circuit utilisé pour cet entraînement.
        notes: Texte libre pour décrire le run.

    Returns:
        Identifiant entier auto-incrément du Run créé.
    """
    run = Run(
        name=name,
        gamma=gamma,
        alpha=alpha,
        epsilon_start=epsilon_start,
        epsilon_end=epsilon_end,
        circuit_name=circuit_name,
        notes=notes,
    )
    session.add(run)
    session.commit()
    return run.id


# ──────────────────────────────────────────────────────────────────────────
# Boucle d'entraînement
# ──────────────────────────────────────────────────────────────────────────


def train(
    session: Session,
    run_id: int,
    nb_episodes: int,
    circuit: Circuit,
    nb_turns: int,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """
    Lance un entraînement de N épisodes pour le run donné.

    Décroissance d'epsilon linéaire : ε(i) = max(end, start − (start−end)·i/N).
    À chaque flush, la Q-table dirty est upsertée et le compteur
    `episodes_done` est mis à jour pour permettre la reprise.

    Args:
        session: Session SQLAlchemy active.
        run_id: ID du Run en base (créé via `create_run`).
        nb_episodes: Nombre d'épisodes à jouer dans cet appel.
        circuit: Circuit sur lequel entraîner l'IA.
        nb_turns: Nombre de tours par course.
        progress_callback: Fonction(episodes_done, total) appelée toutes
            les `_FLUSH_INTERVAL` épisodes. None pour désactiver.
    """
    run = session.get(Run, run_id)
    if run is None:
        raise ValueError(f"Run {run_id} introuvable en base")

    repository = QTableRepository(session, run_id)
    ai_kart = QLearningAI(
        name="Trainee",
        repository=repository,
        gamma=run.gamma,
        alpha=run.alpha,
        epsilon=run.epsilon_start,
        training=True,
    )

    timeout = compute_timeout(circuit, nb_turns)
    pending_logs: list[dict] = []
    base_episodes_done = run.episodes_done

    for episode in range(nb_episodes):
        ratio = episode / nb_episodes if nb_episodes > 0 else 1.0
        ai_kart.epsilon = max(
            run.epsilon_end,
            run.epsilon_start - (run.epsilon_start - run.epsilon_end) * ratio,
        )

        total_reward, ticks, finished, crashed = run_episode(
            ai_kart=ai_kart,
            circuit=circuit,
            nb_turns=nb_turns,
            timeout=timeout,
        )

        pending_logs.append(
            {
                "run_id": run_id,
                "episode_num": base_episodes_done + episode + 1,
                "total_reward": total_reward,
                "ticks": ticks,
                "finished": finished,
                "crashed": crashed,
            }
        )

        if (episode + 1) % _FLUSH_INTERVAL == 0:
            repository.flush(episode_logs=pending_logs)
            repository.update_episodes_done(base_episodes_done + episode + 1)
            pending_logs.clear()
            if progress_callback is not None:
                progress_callback(episode + 1, nb_episodes)

    repository.flush(episode_logs=pending_logs)
    repository.update_episodes_done(base_episodes_done + nb_episodes)
    if progress_callback is not None:
        progress_callback(nb_episodes, nb_episodes)


# ──────────────────────────────────────────────────────────────────────────
# Un épisode
# ──────────────────────────────────────────────────────────────────────────


def run_episode(
    ai_kart: QLearningAI,
    circuit: Circuit,
    nb_turns: int,
    timeout: int,
) -> tuple[float, int, bool, bool]:
    """
    Joue un épisode complet : un kart seul sur le circuit.

    À chaque tic :
    - encodage de l'état courant,
    - choix de l'action (politique ε-greedy si training),
    - application via `race.play_action`,
    - calcul de la récompense,
    - mise à jour Q.

    L'épisode s'arrête si la course est finie, si le kart crashe, ou si
    le nombre de tics atteint `timeout`.

    En cas de timeout, `TIMEOUT_PENALTY` est appliqué sur la dernière
    transition pour décourager la stagnation.

    Returns:
        Tuple (total_reward, ticks, finished, crashed).
    """
    race = Race(circuit=circuit, karts=[ai_kart], nb_turns=nb_turns)

    total_reward = 0.0
    ticks = 0
    crashed = False
    last_state: str = ""
    last_action_char: str = ""

    while ticks < timeout and not race.is_finished():
        kart_before_dto = ai_kart.to_dto()
        current_state = encode_state(ai_kart, circuit)

        action = ai_kart.choose_action(current_state)
        action_char = ACTION_TO_CHAR[action]
        last_state = current_state
        last_action_char = action_char

        race.play_action(action)
        kart_after_dto = ai_kart.to_dto()

        was_crashed = (not ai_kart.is_alive) and (not crashed)
        crashed = crashed or was_crashed

        reward = compute_reward(
            kart_before=kart_before_dto,
            kart_after=kart_after_dto,
            circuit=circuit,
        )
        total_reward += reward

        terminal = was_crashed or race.is_finished()
        new_state = "" if terminal else encode_state(ai_kart, circuit)
        ai_kart.update_q(current_state, action_char, reward, new_state, terminal=terminal)

        ticks += 1
        if was_crashed:
            break

    finished = race.is_finished() and not crashed

    if not finished and not crashed and last_state:
        total_reward += TIMEOUT_PENALTY
        ai_kart.update_q(last_state, last_action_char, TIMEOUT_PENALTY, "", terminal=True)

    return total_reward, ticks, finished, crashed
