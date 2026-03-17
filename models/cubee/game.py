"""
    model db game
"""

from models.base import Base
from models.enums import GameStatus
from sqlalchemy import Column, Integer, Enum, ForeignKey

class Game(Base):
    __tablename__ = "Games"

    id = Column(Integer, primary_key=True)
    board_width = Column(Integer)
    board_height = Column(Integer)
    status = Column(Enum(GameStatus))
    winner_id = Column(Integer, ForeignKey('player.id'))

