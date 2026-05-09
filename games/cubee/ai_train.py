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

def train_with_progress(student, opponent, nb_games, size=5, progress_callback=None,
                        progress_step=200):
    """
    Lance un entraînement d'une IA contre un adversaire avec retour de progression.

    Cette variante de `training()` est destinée à être appelée depuis l'UI :
    elle prend un `progress_callback(current, total)` invoqué périodiquement
    pour rafraîchir la barre de progression Tkinter.

    Args:
        student: IA en cours d'apprentissage (instance de AI).
        opponent: Adversaire (Player aléatoire ou autre IA).
        nb_games: Nombre total de parties à jouer.
        size: Taille du plateau Cubee (défaut 5).
        progress_callback: Fonction(current: int, total: int). Si None, pas
            de retour visuel. Appelée toutes les `progress_step` parties et
            une dernière fois à la fin.
        progress_step: Intervalle (en parties) entre deux callbacks. Plus
            l'intervalle est petit, plus l'UI reste fluide mais plus c'est lent.

    Returns:
        Tuple (wins, losses, draws) du student après l'entraînement.
    """
    nb_epsilon = max(1, int(nb_games / _NB_STEPS))
    ais_with_qtable = [a for a in (student, opponent) if hasattr(a, 'q_table') and a.q_table is not None]
    commit_interval = max(1000, nb_games // 10)

    training_game = GameModel(student, opponent, size, displayable=False)

    # Réinitialiser les compteurs pour ne mesurer que ce run
    for player in (student, opponent):
        player.nb_wins = 0
        player.nb_loses = 0
        player.nb_draws = 0

    for i in range(nb_games):
        # Décroissance d'epsilon (exploration → exploitation)
        if i % nb_epsilon == 0 and i > 0:
            if hasattr(student, 'next_epsilon'):
                student.next_epsilon()
            if hasattr(opponent, 'next_epsilon'):
                opponent.next_epsilon()

        training_game.play()
        training_game.reset()

        # Commit périodique pour persister la Q-table sans saturer la DB
        if i % commit_interval == 0 and i > 0:
            for ai in ais_with_qtable:
                ai.q_table.commit()

        # Callback UI périodique
        if progress_callback is not None and (i % progress_step == 0):
            progress_callback(i, nb_games)

    # Commit final + callback final pour atteindre 100%
    for ai in ais_with_qtable:
        ai.q_table.commit()
    if progress_callback is not None:
        progress_callback(nb_games, nb_games)

    return student.nb_wins, student.nb_loses, student.nb_draws


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
