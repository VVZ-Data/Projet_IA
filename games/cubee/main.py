from .player import Player, Human, AI
from .game_controller import GameController
from .game_model import GameModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect
from .dao.q_table_repository import QTableRepo
from .dao.base import Base
from .ai_train import train_ai

def main():

    engine = create_engine('sqlite:///cubee.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    db_q_table = QTableRepo(session)
    print("table cree")

    choice = input("p = play t = train :")
    if choice == 'p':
        player_1 = Human("Ethan")
        player_2 = Player("Adrien")
    
        GameController(player_1, player_2, size=5).run()
    else:
        player_1 = AI("jean", 0.05, 0.05, 0.9)
        player_2 = AI("Adrien", 0.05, 0.05, 0.9)

        player_1.q_table = db_q_table
        player_2.q_table = db_q_table

        player_1.init_db()
        player_2.init_db()



def train():
    engine = create_engine('sqlite:///cubee.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    db_q_table = QTableRepo(session)

    ai1 = AI("Jean", 0.05, 0.05)
    ai2 = AI("Jean2", 0.05, 0.05)

    ai3 = AI("Adrien", 0.1, 0.05)
    ai4 = AI("Adrien2", 0.1, 0.05)

    ai5 = AI("aeneas", 0.05, 0.1)
    ai6 = AI("aeneas2", 0.05, 0.1)

    ai7 = AI("Snow", 0.005, 0.005)
    ai8 = AI("snow2", 0.005, 0.005)

    ai9 = AI("ambre", 0.001, 0.001)
    ai10 = AI("ambre2", 0.001, 0.001)

    ai1.q_table = db_q_table
    ai2.q_table = db_q_table
    ai3.q_table = db_q_table
    ai4.q_table = db_q_table
    ai5.q_table = db_q_table
    ai6.q_table = db_q_table
    ai7.q_table = db_q_table
    ai8.q_table = db_q_table
    ai9.q_table = db_q_table
    ai10.q_table = db_q_table


    train_ai(ai1, ai2, ai3, ai4, ai5, ai6, ai7, ai8, ai9, ai10, nb_games=100_000)




def run_game():
    """
    Fonction d'entrée pour lancer le jeu cubee.
    
    Cette fonction est appelée par le main.py racine quand
    l'utilisateur sélectionne ce jeu depuis la page d'accueil.
    
    Crée et lance l'application Tkinter du jeu.
    Elle constitue le point d'entrée public de ce module.
    
    Example:
        >>> # Depuis le main racine
        >>> from games.jeux_1 import main as game1
        >>> game1.run_game()  # Lance le jeu des allumettes
    """

    engine = create_engine('sqlite:///cubee.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    db_q_table = QTableRepo(session)


    player1 = AI("jean")
    player1.q_table = db_q_table
    player1.init_db()
    
    player2 = Human("moi")
    app = GameController(player1, player2)
    mainloop()

