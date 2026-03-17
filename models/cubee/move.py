"""
    model db move
"""
from models.base import Base
from models.enums import Direction
from sqlalchemy import Column, Integer, Enum, ForeignKey

class Move(Base):
    __tablename__ = "Move"

    id = Column(Integer, primary_key=True)
    player_move = Column(Integer, ForeignKey('player.id'), ForeignKey('game.id'))
    move_number = Column(Integer)
    direction = Column(Enum(Direction))
    to_x = Column(Integer)
    to_y = Column(Integer)