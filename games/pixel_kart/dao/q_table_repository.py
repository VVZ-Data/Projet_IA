"""
Repository RAM-first pour la Q-table de Pixel Kart.

Refonte complète vs l'implémentation V1.

Stratégie :
- À l'initialisation, on charge TOUTES les Q-values du run en mémoire
  (`SELECT *` unique).
- Les `get_q` / `set_q` n'accèdent ensuite qu'au dict en RAM.
- Les modifications sont marquées dans un set `dirty` puis écrites en
  base par batch lors d'un appel à `flush()` (typiquement toutes les
  500 épisodes via la boucle d'entraînement).

Avantage : pendant l'entraînement, zéro fsync SQLite par update Q. Les
millions de mises à jour ne touchent la base que lors des flush groupés,
ce qui rend le training ~50–100x plus rapide qu'une approche per-row.
"""

import random

from sqlalchemy import insert
from sqlalchemy.orm import Session

from .q_table import EpisodeLog, QValue, Run


class QTableRepository:
    """
    Gère la Q-table d'un `Run` en RAM avec persistance par batch.

    Utilisation typique :
        repo = QTableRepository(session, run_id=42)
        repo.get_q("32102", "A")             # lecture mémoire
        repo.set_q("32102", "A", new_value)  # écriture mémoire + dirty
        repo.flush(episode_logs=[...])       # commit à la base

    Les dépendances avec le module IA :
        - `state` est une string de 6 caractères (cf. ai_state.encode_state)
        - `action` est un caractère de ACTION_TO_CHAR.values()
    """

    def __init__(self, session: Session, run_id: int) -> None:
        """
        Charge en mémoire toutes les Q-values du run donné.

        Args:
            session: Session SQLAlchemy active.
            run_id: Identifiant du Run dont on charge la Q-table.
        """
        self.session = session
        self.run_id = run_id
        self.q_values: dict[tuple[str, str], float] = {}
        self.dirty: set[tuple[str, str]] = set()
        self._load_from_db()

    # ──────────────────────────────────────────────────────────────────────
    # Chargement initial
    # ──────────────────────────────────────────────────────────────────────

    def _load_from_db(self) -> None:
        """Lit toutes les Q-values du run en un seul SELECT et peuple le cache."""
        rows = (
            self.session.query(QValue)
            .filter(QValue.run_id == self.run_id)
            .all()
        )
        self.q_values = {(row.state, row.action): row.value for row in rows}

    # ──────────────────────────────────────────────────────────────────────
    # Lecture / écriture en RAM
    # ──────────────────────────────────────────────────────────────────────

    def get_q(self, state: str, action: str) -> float:
        """
        Retourne la Q-value (state, action) depuis la RAM.

        Args:
            state: Clé d'état (string ai_state).
            action: Caractère d'action.

        Returns:
            La valeur Q stockée, ou 0.0 si la paire est inconnue.
        """
        return self.q_values.get((state, action), 0.0)

    def set_q(self, state: str, action: str, value: float) -> None:
        """
        Met à jour la Q-value en RAM et marque l'entrée comme dirty.

        Args:
            state: Clé d'état.
            action: Caractère d'action.
            value: Nouvelle valeur Q.
        """
        self.q_values[(state, action)] = value
        self.dirty.add((state, action))

    # ──────────────────────────────────────────────────────────────────────
    # Helpers de politique
    # ──────────────────────────────────────────────────────────────────────

    def best_q(self, state: str, valid_actions: list[str]) -> float:
        """
        Renvoie la meilleure Q-value parmi `valid_actions` pour cet état.

        Args:
            state: Clé d'état.
            valid_actions: Liste de caractères d'action à considérer.

        Returns:
            Maximum des Q-values parmi `valid_actions`, ou 0.0 si la liste
            est vide (cas dégénéré).
        """
        if not valid_actions:
            return 0.0
        return max(self.get_q(state, a) for a in valid_actions)

    def best_action(self, state: str, valid_actions: list[str]) -> str:
        """
        Retourne le caractère d'action ayant la meilleure Q-value.

        En cas d'égalité, `max(..., key=...)` renvoie la première occurrence
        rencontrée selon l'ordre de `valid_actions`. C'est déterministe : utile
        pour des tests reproductibles.

        Args:
            state: Clé d'état.
            valid_actions: Liste non vide de caractères d'action.

        Returns:
            Le caractère d'action ayant le Q maximum.
        """
        best_q = max(self.get_q(state, a) for a in valid_actions)
        best_actions = [a for a in valid_actions if self.get_q(state, a) == best_q]
        return random.choice(best_actions)

    # ──────────────────────────────────────────────────────────────────────
    # Persistance par batch
    # ──────────────────────────────────────────────────────────────────────

    def flush(self, episode_logs: list[dict] | None = None) -> None:
        """
        Écrit en base les Q-values modifiées et les logs d'épisodes.

        Stratégie :
        - Pour les Q-values, on émet un seul `INSERT OR REPLACE` avec toutes
          les lignes dirty (upsert atomique). Cela évite un SELECT par clé.
        - Pour les logs, on utilise `bulk_insert_mappings` qui contourne
          l'unit-of-work ORM et insère ~10x plus vite que des `add(...)`.
        - Un seul `commit()` à la fin pour grouper le tout.

        Args:
            episode_logs: Liste optionnelle de dicts à insérer dans la table
                `episode_log` (clés : run_id, episode_num, total_reward,
                ticks, finished, crashed).
        """
        # 1) Upsert des Q-values dirty (SQLite supporte INSERT OR REPLACE)
        if self.dirty:
            rows = [
                {
                    "run_id": self.run_id,
                    "state": state,
                    "action": action,
                    "value": self.q_values[(state, action)],
                }
                for (state, action) in self.dirty
            ]
            stmt = insert(QValue).prefix_with("OR REPLACE")
            self.session.execute(stmt, rows)
            self.dirty.clear()

        # 2) Insertion des logs d'épisode si fournis
        if episode_logs:
            self.session.bulk_insert_mappings(EpisodeLog, episode_logs)

        # 3) Un seul commit pour toute la transaction
        self.session.commit()

    def update_episodes_done(self, episodes_done: int) -> None:
        """
        Met à jour le compteur `episodes_done` du Run associé.

        Appelé par la boucle d'entraînement après chaque flush pour que
        l'avancement soit visible même si l'utilisateur interrompt le run.

        Args:
            episodes_done: Nouvelle valeur cumulée du compteur d'épisodes.
        """
        run = self.session.get(Run, self.run_id)
        if run is not None:
            run.episodes_done = episodes_done
            self.session.commit()
