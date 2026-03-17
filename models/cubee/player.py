"""
    model db player
"""

from models.base import Base
from sqlalchemy import Column, Integer, String

class Player(Base):
    __tablename__ = "Player"

    id = Column(Integer, primary_key=True)
    user_name = Column(String(100))
