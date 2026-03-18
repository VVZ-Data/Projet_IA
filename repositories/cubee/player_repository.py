"""
    Repository pour les opérations sur les joueurs
"""
from models.cubee.player import Player

class PlayerRepository:

    def __init__(self, session):
        """
            Initialise le repository avec une session SQLAlchemy.
        """
        self.session = session

    def create(self, username, is_human=True):
        """
            Crée et retourne un joueur 
        """
        player = Player(user_name = username, is_human = is_human)
        self.session.add(player)
        self.session.commit()

        return player
    
    def get_by_id(self, id):
        """
            Retourne un joueur en fonction de son id, None si inexistant 
        """

        return self.session.get(Player, id)
    
    def get_all(self):
        """
            Retourne tous les joueurs.
        """
        return self.session.query(Player).all()
