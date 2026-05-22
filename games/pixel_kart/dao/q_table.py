"""
Modèles SQLAlchemy pour la persistance de la Q-table de Pixel Kart.

Schéma à 3 tables (refonte complète vs l'ancien schéma 1 table de la V1) :

- `runs`        : un enregistrement par configuration d'entraînement
                  (γ, α, ε, circuit, nb épisodes faits, etc.)
- `q_values`    : valeurs Q pour chaque (run, état, action)
                  → CASCADE sur suppression du run
- `episode_log` : statistiques par épisode (récompense, ticks, fini, crashed)
                  → CASCADE sur suppression du run, utile pour tracer les
                  courbes d'apprentissage à la défense orale.

L'utilisation de `Run` comme table parente permet :
- de lancer plusieurs entraînements en parallèle sans collision de Q-values,
- de purger un run raté avec un simple `DELETE FROM runs WHERE id = ?`,
- d'avoir des méta-données (date, notes, circuit) attachées à chaque run.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import Base


class Run(Base):
    """
    Représente un entraînement Q-learning : un set d'hyperparamètres et son
    état d'avancement (nombre d'épisodes joués jusqu'à présent).

    Une nouvelle ligne est créée à chaque `Start Training` lancé depuis l'UI
    (ou depuis un script CLI). Le même run peut être ré-utilisé pour
    poursuivre un entraînement (`episodes_done` est incrémenté à chaque flush).
    """

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    gamma = Column(Float, nullable=False)
    alpha = Column(Float, nullable=False)
    epsilon_start = Column(Float, nullable=False)
    epsilon_end = Column(Float, nullable=False)
    episodes_done = Column(Integer, default=0, nullable=False)
    circuit_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String(500), default="")

    # Relations supprimant en cascade les valeurs Q et les logs liés
    q_values = relationship(
        "QValue",
        back_populates="run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    episodes = relationship(
        "EpisodeLog",
        back_populates="run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class QValue(Base):
    """
    Stocke la valeur Q pour un triplet (run, état, action).

    La clé primaire composite (run_id, state, action) permet d'avoir
    plusieurs runs partageant la même base sans interférence.

    Le format string utilisé pour `state` (6 chars) et `action` (1 char)
    est défini par `games/pixel_kart/ai_state.py`.
    """

    __tablename__ = "q_values"

    run_id = Column(
        Integer,
        ForeignKey("runs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    state = Column(String(6), primary_key=True)
    action = Column(String(1), primary_key=True)
    value = Column(Float, default=0.0, nullable=False)

    run = relationship("Run", back_populates="q_values")


class EpisodeLog(Base):
    """
    Trace une ligne par épisode d'entraînement, pour analyse a posteriori.

    Permet de tracer une courbe d'apprentissage (récompense moyenne par
    fenêtre, taux de réussite, taux de crash, durée des épisodes...).
    Pas de clé composite ici : on utilise un `id` autoincrément, plus simple
    pour les insertions massives via `bulk_insert_mappings`.
    """

    __tablename__ = "episode_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(
        Integer,
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    episode_num = Column(Integer, nullable=False)
    total_reward = Column(Float, nullable=False)
    ticks = Column(Integer, nullable=False)
    finished = Column(Boolean, nullable=False)  # course terminée (tous tours faits) ?
    crashed = Column(Boolean, nullable=False)   # crash mur ?

    run = relationship("Run", back_populates="episodes")
