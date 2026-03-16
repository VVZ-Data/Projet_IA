from .player import Player, Human, AI
from .game_controller import GameController
from .game_model import GameModel

def main():
    choice = input("p = play t = train :")
    if choice == 'p':
        player_1 = AI("Ethan")
        player_2 = Player("Adrien")
    
        GameController(player_1, player_2, size=5).run()
    else:
        player_1 = AI("jean", 0.05, 0.9)
        player_2 = AI("Adrien")

        training(player_1, player_2, 100_000, 100)

        compare_ai(player_1)

def compare_ai(*ais):
    # Print a comparison between the @ais
    names = f"{'':4}"
    stats1 = f"{'':4}"
    stats2 = f"{'':4}"

    for ai in ais :
        names += f"{ai.name:^15}"
        stats1 += f"{str(ai.nb_wins)+'/'+str(ai.nb_games):^15}"
        stats2 += f"{f'{ai.nb_wins/ai.nb_games*100:4.4}'+'%':^15}"

    print(names)
    print(stats1)
    print(stats2)
    print(ai.epsilon)
    print(f"{'-'*4}{'-'*len(ais)*15}")     


def training(ai1, ai2, nb_games, nb_epsilon):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games
    training_game = GameModel(ai1, ai2, displayable = False)
    for i in range(0, nb_games):
        if i % nb_epsilon == 0:
            if type(ai1)==AI : ai1.next_epsilon()
            if type(ai2)==AI : ai2.next_epsilon()

        training_game.play()

        training_game.reset()
