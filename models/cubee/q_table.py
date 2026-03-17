"""
    model db q_table
"""
from models.base import Base
from sqlalchemy import Column, Integer, Float, ForeignKey

class QTable(Base):
    __tablename__ = 'Q_table'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    state_x = Column(Integer)
    state_y = Column(Integer)
    action_up = Column(Float)
    action_down = Column(Float)
    action_right = Column(Float)
    action_left = Column(Float)