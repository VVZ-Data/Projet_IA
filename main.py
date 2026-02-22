"""
Point d'entrée principal du jeu des allumettes.
Lance une partie avec interface graphique Tkinter.
"""
from player import Player, Human, AI
from game_controller import GameController
from game_model import GameModel

"""
def main() -> None:
    """
    #Point d'entrée du programme. Crée les joueurs, le contrôleur et démarre le jeu.
"""
    # Création des joueurs
    human = Human("Player 1")
    random_bot = AI("Random Bot")

    # Lancement du jeu via le contrôleur (15 allumettes par défaut)
    controller = GameController(human, random_bot, total_matches=15)
    controller.start()
"""
def training(ai1, ai2, nb_games, nb_epsilon):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games
    training_game = GameModel(12, ai1, ai2, displayable = False)
    for i in range(0, nb_games):
        if i % nb_epsilon == 0:
            if type(ai1)==AI : ai1.next_epsilon()
            if type(ai2)==AI : ai2.next_epsilon()

        training_game.play()
        if type(ai1)==AI : ai1.train()
        if type(ai2)==AI : ai2.train()

        training_game.reset()

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

    all_v_dict = {key : [ai.value_function.get(key,0) for ai in ais] for key in ais[0].value_function.keys()}
    sorted_v = lambda v_dict : sorted(filter(lambda x : type(x[0])==int ,v_dict.items()))
    for state, values in sorted_v(all_v_dict):
        print(f"{state:2} :", end='')
        for value in values:
            print(f"{value:^15.3}", end='')
        print()

def testing(ai, random_player, nb_games):
    test_game = GameModel(12, ai, random_player, displayable=False)
    wins = 0
    for i in range(nb_games):
        test_game.play()
        # ai.train() ← NE PAS appeler
        if test_game.get_winner() == ai:
            wins +=1 
        test_game.reset()

    print(f"{wins/nb_games*100:.2f}%")

if __name__ == "__main__":
    #main()

    ai1 = AI("1", 0.9, 0.3)
    ai2 = AI("2", 0.9, 0.3)
    random_player = Player("3")

    ai1.download("AI_save_1")
    #ai2.download("AI_save_2")
    
    training(ai1, ai2, 100_000, 9500)

    compare_ai(ai1, ai2)
    
    epsilon_save = ai1.epsilon
    epsilon_save_2 = ai2.epsilon
    ai1.epsilon = 0
    ai2.epsilon = 0
    testing(ai1, random_player, 100_000)
    compare_ai(ai1)
    ai1.epsilon = epsilon_save
    ai2.epsilon = epsilon_save_2
    ai1.upload("AI_save_1")
    ai2.upload("AI_save_2")
    print("save")