"""
    model db q_table
"""
from base import Base
from sqlalchemy import Column, Integer, Float, String, Tuple


class QTable(Base):
    """
        Représente la q-table du joueur IA de Cubee.

        Chaque ligne correspond à un état possible du plateau,
        défini par la position du cube (cube_x, cube_y).
        Les valeurs Q indiquent la qualité estimée de chaque action
        depuis cet état. Plus la valeur est haute, meilleure est l'action.
        L'IA met à jour ces valeurs après chaque partie.
    """

    __tablename__ = 'q_table'

    """Identifiant unique de l'entrée."""
    id = Column(Tuple, primary_key=True)

    """Etat"""
    state = Column(String(1000))

    """Valeur Q pour l'action aller en haut depuis cet état."""
    action_up = Column(Float)

    """Valeur Q pour l'action aller en bas depuis cet état."""
    action_down = Column(Float)

    """Valeur Q pour l'action aller à droite depuis cet état."""
    action_right = Column(Float)

    """Valeur Q pour l'action aller à gauche depuis cet état."""
    action_left = Column(Float)
