from .game_controller import GameController

def main():
    GameController(player1_name="Player 1", player2_name="Player 2", size=5).run()

if __name__ == "__main__":
    main()