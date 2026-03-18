"""
    model db game
"""

from models.base import Base
from models.enums import GameStatus
from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

class Game(Base):
    """
        Représente une partie de Cubee entre deux joueurs.

        Une partie se joue sur un plateau de taille board_width x board_height.
        Elle passe par les statuts WAITING → IN_PROGRESS → FINISHED.
        Le gagnant est celui qui a capturé le plus de cases à la fin.
    """

    __tablename__ = "game"

    """Identifiant unique de la partie."""
    id = Column(Integer, primary_key=True)

    """Largeur du plateau de jeu."""
    board_width = Column(Integer)

    """Hauteur du plateau de jeu."""
    board_height = Column(Integer)

    """Statut actuel de la partie : WAITING, IN_PROGRESS ou FINISHED."""
    status = Column(Enum(GameStatus))

    """Id du joueur gagnant. None tant que la partie n'est pas terminée."""
    winner_id = Column(Integer, ForeignKey('player.id'))

    """Joueur gagnant de la partie."""
    winner = relationship("Player", back_populates="game", uselist=False)

    """Liste des deux participations joueur/partie."""
    game_players = relationship("GamePlayer", back_populates="game")
