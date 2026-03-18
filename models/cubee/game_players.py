"""
    model db game_player
"""
from models.base import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class GamePlayer(Base):
    """
        Représente la participation d'un joueur dans une partie.

        Fait le lien entre un joueur et une partie.
        Stocke les données propres à cette participation :
        score, position du cube et ordre de jeu.
        Une partie contient exactement 2 GamePlayers.
    """

    __tablename__ = "game_players"

    """Identifiant unique de la participation."""
    id = Column(Integer, primary_key=True)

    """Id du joueur participant."""
    players_id = Column(Integer, ForeignKey('players.id'))

    """Id de la partie concernée."""
    game_id = Column(Integer, ForeignKey('games.id'))

    """Ordre de jeu du joueur : 1 pour le premier, 2 pour le second."""
    turn = Column(Integer)

    """Nombre de cases capturées par ce joueur dans cette partie."""
    score = Column(Integer)

    """Position X actuelle du cube du joueur sur le plateau."""
    cube_x = Column(Integer)

    """Position Y actuelle du cube du joueur sur le plateau."""
    cube_y = Column(Integer)

    """Joueur associé à cette participation."""
    players = relationship("Players", back_populates="game_players", uselist=False)

    """Partie associée à cette participation."""
    game = relationship("Games", back_populates="gamee_players", uselist=False)