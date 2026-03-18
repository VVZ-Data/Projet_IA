"""
    Repository game_player
"""

from models.cubee.game_players import GamePlayer

class GamePlayersRepository:

    def __init__(self, session):
        """
            Initialise le repository avec une session SQLAlchemy.
        """        
        self.session = session

    def create(self, game_id, player_id, turn):
        """
            Crée et retourne une participation avec un score initial à 0.
        """   
        game_player = GamePlayer(game_id = game_id, player_id = player_id, turn = turn, score=0)

        self.session.add(game_player)
        self.session.commit()

        return game_player

    def update_position(self, game_player, x, y):
        """
            Met à jour la position du cube d'un joueur.
        """
        game_player.cube_x = x
        game_player.cube_y = y
        self.session.commit()

    def update_score(self, game_player, score):
        """
            Incrémente le score d'un joueur de 1.
        """
        game_player.score = score
        self.session.commit()

    def get_by_game(self, game_id):
        """
            Retourne les 2 participations d'une partie.
        """
        return self.session.query(GamePlayer).filter_by(game_id=game_id).all()