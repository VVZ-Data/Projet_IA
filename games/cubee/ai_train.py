from .game_model import GameModel
from .player import Player
from time import time
from math import log

_NB_STEPS = log(0.05 / 0.9) / log(0.95) 

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

    print(f"{'-'*4}{'-'*len(ais)*15}")     


def training(ai1, ai2, nb_games, nb_epsilon, size):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games
    ais_with_qtable = [a for a in [ai1, ai2] if hasattr(a, 'q_table')]
    commit_interval = max(1000, nb_games // 10)  # adaptatif selon nb_games

    training_game = GameModel(ai1, ai2, size, displayable = False)
    for i in range(0, nb_games):
        if i % nb_epsilon == 0:
            if ai1.type =='AI' : ai1.next_epsilon()
            if ai2.type =='AI' : ai2.next_epsilon()

        training_game.play()
        training_game.reset()

        if i % commit_interval == 0 and i > 0:
            for ai in ais_with_qtable:  # ✅ commit tous les AIs
                ai.q_table.commit()

    for ai in ais_with_qtable:
        ai.q_table.commit()
            
def testing(*ais, nb_games):
    random_player = Player("random")
    for ai in ais:
        test_game = GameModel(ai, random_player, displayable=False)
        wins = 0
        for i in range(nb_games):
            test_game.play()
            if test_game.get_winner() == ai:
                wins +=1 
            test_game.reset()

        print(f"{wins/nb_games*100:.2f}%")

def train_ai(*ais, nb_games):

    nb_epsilon = int(nb_games / _NB_STEPS)


    start = time()

    for ai1 in ais:
        for ai2 in ais:
            if ai1 != ai2:
                step = time()
                training(ai1, ai2, nb_games, nb_epsilon, 5)
                compare_ai(ai1, ai2)
                
                end_step = time()

                elapsed_step = end_step - step

                print(f"ai {ai1} vs ai {ai2} train end en {elapsed_step} seconde")
                

        testing(*ais, nb_games=1000)
    compare_ai(*ais)

    end = time()

    elapsed_time = end - start

    print(f"Temps écoulé : {elapsed_time:.2f} secondes")
