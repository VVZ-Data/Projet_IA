"""
    model db move
"""
from models.base import Base
from models.enums import Direction
from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

class Move(Base):
    """
        Représente un coup joué par un joueur dans une partie.

        Chaque déplacement du cube génère un Move.
        Permet de retracer l'historique complet d'une partie
        et d'entraîner l'IA via les positions visitées.
    """

    __tablename__ = "moves"

    """Identifiant unique du coup."""
    id = Column(Integer, primary_key=True)

    """Id de la participation joueur/partie qui a effectué ce coup."""
    game_player_id = Column(Integer, ForeignKey('game_players.id'))

    """Numéro du coup dans la partie, commence à 1."""
    move_number = Column(Integer)

    """Direction du déplacement : UP, DOWN, LEFT ou RIGHT."""
    direction = Column(Enum(Direction))

    """Position X du cube après le déplacement."""
    to_x = Column(Integer)

    """Position Y du cube après le déplacement."""
    to_y = Column(Integer)

    """Participation joueur/partie associée à ce coup."""
    game_player = relationship("GamePlayer", uselist=False)