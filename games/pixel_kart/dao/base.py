"""
[IA-Claude] Base SQLAlchemy commune au DAO Pixel Kart.

Définit la classe `Base` (DeclarativeBase) dont héritent tous les modèles,
et active la contrainte `PRAGMA foreign_keys=ON` à chaque connexion SQLite.

Sans cette ligne, SQLite ignore les `ForeignKey(... ondelete="CASCADE")`,
ce qui rendrait inopérantes les relations runs → q_values / episode_log.
"""

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles ORM du module Pixel Kart."""

    pass


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """
    Active les contraintes de clé étrangère sur chaque connexion SQLite.

    SQLAlchemy lève cet event au moment où une connexion est établie. On
    applique `PRAGMA foreign_keys=ON` pour que les `ON DELETE CASCADE`
    déclarés sur les ForeignKey soient respectés (sinon SQLite les ignore).

    L'event est inoffensif pour les autres backends : si la connexion ne
    supporte pas ce PRAGMA, on attrape l'erreur silencieusement plutôt que
    de casser des bases non-SQLite (ex. cubee.db existant).
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    except Exception:
        # Backend non-SQLite ou cursor incapable d'exécuter un PRAGMA :
        # on ne veut pas faire planter l'ouverture de connexion.
        pass
    finally:
        cursor.close()
