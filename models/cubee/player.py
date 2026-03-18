"""
    model db player
"""

from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

class Player(Base):
    """
        Représente un joueur dans le jeu Cubee.
    
        Un joueur peut être humain ou une IA (is_human=False).
        Il peut participer à plusieurs parties via GamePlayers.
        Si c'est une IA, il possède une QTable associée.
    """

    __tablename__ = "player"

    """Identifiant unique du joueur."""
    id = Column(Integer, primary_key=True)

    """Nom d'utilisateur du joueur."""
    user_name = Column(String(100))

    """True si le joueur est humain, False si c'est une IA."""
    is_human = Column(Boolean, default=True) 

    """Liste des participations du joueur dans les parties."""
    game_players = relationship("GamePlayer", back_populates="player")

    """Q-table associée au joueur IA. None si le joueur est humain."""
    q_table = relationship("QTable", back_populates="player", uselist=False) 
