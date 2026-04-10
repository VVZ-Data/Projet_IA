"""
    model db q_table
"""
from .base import Base
from sqlalchemy import Column, Integer, Float, String, UniqueConstraint


class QTable(Base):
    """
        Représente la q-table du joueur IA de Cubee.
    """

    __tablename__ = 'q_table'

    """gama clés composite"""
    gama = Column(String(10), primary_key=True)

    """alpha ou learning rate clés composite"""
    learning_rate  = Column(String(10), primary_key=True)

    """Etat"""
    state = Column(String(1000), primary_key=True, index=True)

    """Valeur Q pour l'action aller en haut depuis cet état."""
    speed_up = Column(Float)

    """Valeur Q pour l'action aller en bas depuis cet état."""
    slow_down = Column(Float)

    """Valeur Q pour l'action aller à droite depuis cet état."""
    right = Column(Float)

    """Valeur Q pour l'action aller à gauche depuis cet état."""
    left = Column(Float)

