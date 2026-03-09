from .player import Player, Human
from .game_controller import GameController

def main():
    player_1 = Human("Ethan")
    player_2 = Player("Adrien")
    
    GameController(player_1, player_2, size=5).run()
