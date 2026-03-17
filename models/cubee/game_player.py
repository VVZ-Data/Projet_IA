"""
    model db game_player
"""
from models.base import Base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey

class GamePlayer(Base):
    __tablename__ = "Game_Player"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    score = Column(Integer)
    cube_x = Column(Integer)
    cube_y = Column(Integer)