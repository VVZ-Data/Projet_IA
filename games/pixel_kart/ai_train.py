"""
[IA-Claude] Boucle d'entraînement Q-learning pour Pixel Kart.

Trois fonctions publiques :

- `create_run` : crée une nouvelle ligne `runs` en base et renvoie son ID.
- `train`     : lance N épisodes pour un run donné, en flushant la
                Q-table périodiquement et en notifiant l'UI via callback.
- `run_episode` : joue un épisode complet (un kart seul sur le circuit)
                  et renvoie ses statistiques.

Architecture :
- L'IA est instanciée localement à `train()` ; elle n'est pas exposée hors
  de cette boucle (la vue d'entraînement n'a pas à connaître `QLearningAI`).
- La récompense est calculée par `ai_state.compute_reward`, qui n'est
  exposée nulle part dans le modèle de jeu (séparation MVC stricte).
- Le repository `QTableRepository` cache les Q-values en RAM et flushe
  par batch de `FLUSH_INTERVAL` épisodes.
"""

from typing import Callable, Optional

from sqlalchemy.orm import Session

from games.pixel_kart.ai_state import (
    compute_reward,
    compute_timeout,
    encode_state,
)
from games.pixel_kart.dao.q_table import EpisodeLog, Run
from games.pixel_kart.dao.q_table_repository import QTableRepository
from games.pixel_kart.game_model import Circuit, Race
from games.pixel_kart.player import QLearningAI


FLUSH_INTERVAL: int = 500
"""Nombre d'épisodes entre deux flushes en base (Q-values + logs)."""

TIMEOUT_PENALTY: float = -500.0
"""
Malus appliqué quand un épisode se termine par timeout (boucle ou stagnation).

Volontairement plus fort que le crash (-100) : crasher peut résulter d'une
tentative légitime d'aller vite, tandis que tourner en rond sans finir est
la pire politique possible.
"""


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
        epsilon_start: ε au tout début de l'entraînement (exploration max).
        epsilon_end: ε en fin d'entraînement (exploitation quasi pure).
        circuit_name: Nom du circuit utilisé pour cet entraînement.
        notes: Texte libre pour décrire le run (visible en base).

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
            les `FLUSH_INTERVAL` épisodes pour rafraîchir l'UI. None pour
            désactiver.
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
        # Décroissance linéaire d'epsilon
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

        # Flush périodique
        if (episode + 1) % FLUSH_INTERVAL == 0:
            repository.flush(episode_logs=pending_logs)
            repository.update_episodes_done(base_episodes_done + episode + 1)
            pending_logs.clear()
            if progress_callback is not None:
                progress_callback(episode + 1, nb_episodes)

    # Flush final pour les épisodes qui n'ont pas atteint un FLUSH_INTERVAL
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
    - capture du DTO avant l'action,
    - choix de l'action (politique courante du kart, ε-greedy si training),
    - application via `race.play_action`,
    - capture du DTO après,
    - calcul de la récompense via `compute_reward`,
    - mise à jour Q via `ai_kart.update_q`.

    L'épisode s'arrête si la course est finie, si le kart crashe, ou si le
    nombre de tics atteint le `timeout` (anti-boucle infinie).

    Cas timeout sans victoire ni crash : on applique `TIMEOUT_PENALTY` à la
    dernière transition mémorisée. Sans ce signal, l'IA peut converger vers
    une politique de stagnation (tourner en rond accumule du tic_reward
    légèrement positif sans risque) qui ne finit jamais la course.

    Args:
        ai_kart: Agent à entraîner (déjà construit, branché à un repository).
        circuit: Circuit en cours.
        nb_turns: Nombre de tours requis pour finir.
        timeout: Borne max de tics (cf. `compute_timeout`).

    Returns:
        Tuple (total_reward, ticks, finished, crashed) :
            - total_reward : somme cumulée des récompenses (float)
            - ticks        : nombre de tics joués
            - finished     : course terminée (tous tours faits) sans crash
            - crashed      : kart sorti de la course par crash mur
    """
    race = Race(circuit=circuit, karts=[ai_kart], nb_turns=nb_turns)
    ai_kart.reset_memory()

    total_reward = 0.0
    ticks = 0
    crashed = False

    while ticks < timeout and not race.is_finished():
        # Capturer l'état avant l'action pour calculer la récompense
        kart_before_dto = ai_kart.to_dto()

        # L'IA choisit, le modèle applique
        action = ai_kart.choose_action(race)
        race.play_action(action)

        kart_after_dto = ai_kart.to_dto()

        # Détecter un crash sur cette transition (et seulement celui-là)
        was_crashed = (not ai_kart.is_alive) and (not crashed)
        crashed = crashed or was_crashed

        reward = compute_reward(
            kart_before=kart_before_dto,
            kart_after=kart_after_dto,
            circuit=circuit,
            nb_turns_total=nb_turns,
            crashed=was_crashed,
        )
        total_reward += reward

        # Pour l'update Q : "" si terminal, sinon l'état courant encodé
        terminal = was_crashed or race.is_finished()
        new_state = "" if terminal else encode_state(ai_kart, circuit)
        ai_kart.update_q(reward, new_state, terminal=terminal)

        ticks += 1
        if was_crashed:
            break

    finished = race.is_finished() and not crashed

    # Timeout sans victoire ni crash : pénaliser la stagnation pour que
    # l'IA n'apprenne pas à tourner en rond.
    if not finished and not crashed:
        # DEBUG TEMPORAIRE : confirmer que le bloc timeout est bien atteint
        # pendant l'entraînement. À retirer une fois la convergence vérifiée.
        print(
            f"[ai_train] timeout penalty applied "
            f"(ticks={ticks}, total_reward_before={total_reward:.1f})",
            flush=True,
        )
        total_reward += TIMEOUT_PENALTY
        ai_kart.update_q(TIMEOUT_PENALTY, "", terminal=True)

    return total_reward, ticks, finished, crashed
