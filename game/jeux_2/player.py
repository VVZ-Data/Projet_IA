

class Player:

    def __init__(self, name, game = None):
        self.name = name
        self.game = game
        self.nb_wins: int = 0
        self.nb_loses: int = 0

    
    