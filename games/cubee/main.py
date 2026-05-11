"""
Point d'entrée du jeu Cubee.

Architecture (calquée sur games/allumette/main.py) :
    - CubeeApp(tk.Tk) : fenêtre unique avec une vue courante (Frame)
    - clear_view + show_xxx() : navigation entre les vues
    - GameController : logique d'une partie en cours

Vues :
    - CubeeMenuView      : menu principal (Play / Train)
    - GameView           : partie en cours (insérée par GameController)
    - CubeeTrainingView  : interface d'entraînement
"""

import time
import tkinter as tk

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from language_manager import lang_manager
from .ai_train import train_with_progress
from .dao.base import Base
from .dao.q_table_repository import QTableRepo
from .game_controller import GameController
from .player import AI, Human, Player
from .views.menu_view import CubeeMenuView
from .views.training_view import CubeeTrainingView


# ──────────────────────────────────────────────────────────────────────────
# Application principale
# ──────────────────────────────────────────────────────────────────────────


class CubeeApp(tk.Tk):
    """
    Application principale du jeu Cubee.

    Gère la navigation entre :
    - le menu principal (CubeeMenuView)
    - une partie (GameView via GameController)
    - l'entraînement (CubeeTrainingView)
    - le retour à la sélection des jeux (page d'accueil)
    """

    def __init__(self) -> None:
        """Initialise la fenêtre, la session SQLAlchemy et affiche le menu."""
        super().__init__()

        self.title("Cubee — Territory Game")
        self.geometry("900x700")
        self.configure(bg="#F5F7FA")

        # Session DB partagée par toutes les vues qui en ont besoin
        engine = create_engine("sqlite:///cubee.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.db_q_table = QTableRepo(self.session)

        self.current_view: tk.Frame | None = None
        self.game_controller: GameController | None = None

        self.show_menu()

    # ──────────────────────────────────────────────────────────────────────
    # Navigation
    # ──────────────────────────────────────────────────────────────────────

    def clear_view(self) -> None:
        """
        Détruit la vue courante après désinscription du gestionnaire de langue.

        Si la vue courante est une `GameView`, on retire en plus ses bindings
        clavier globaux (sinon ils resteraient actifs sur la nouvelle vue).
        """
        if self.current_view is not None:
            if hasattr(self.current_view, "unbind_keys"):
                self.current_view.unbind_keys()
            lang_manager.unregister_observer(self.current_view)
            self.current_view.pack_forget()
            self.current_view.destroy()
            self.current_view = None
        self.game_controller = None

    def show_menu(self) -> None:
        """Affiche le menu principal."""
        self.clear_view()
        self.current_view = CubeeMenuView(
            self,
            on_play_selected=self._on_play_selected,
            on_train_selected=self.show_training,
            on_back=self._quit_to_home,
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def show_training(self) -> None:
        """Affiche la vue d'entraînement."""
        self.clear_view()
        self.current_view = CubeeTrainingView(
            self,
            on_start_training=self._start_training,
            on_back=self.show_menu,
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)

    # ──────────────────────────────────────────────────────────────────────
    # Démarrage d'une partie
    # ──────────────────────────────────────────────────────────────────────

    def _on_play_selected(self, mode: str) -> None:
        """
        Lance une partie en fonction du mode choisi dans le menu.

        Args:
            mode: "ai" (humain vs IA Q-learning), "random" (humain vs random)
                  ou "human" (humain vs humain local).
        """
        human_player = Human("You")

        if mode == "ai":
            ai_player = AI("Cubee AI", gama=0.9, learning_rate=0.1, epsilon=0.05)
            ai_player.q_table = self.db_q_table
            ai_player.init_db()
            opponent: Player = ai_player
        elif mode == "random":
            opponent = Player("Random Bot")
        else:  # mode == "human"
            opponent = Human("Player 2")

        self._start_game(human_player, opponent)

    def _start_game(self, player1: Player, player2: Player) -> None:
        """
        Crée le GameController + GameView et affiche la partie.

        Args:
            player1: Premier joueur (généralement humain).
            player2: Second joueur (humain, IA ou random).
        """
        self.clear_view()

        self.game_controller = GameController(
            self, player1, player2, size=5, on_back=self.show_menu,
        )
        self.current_view = self.game_controller.view
        self.current_view.pack(fill=tk.BOTH, expand=True)

    # ──────────────────────────────────────────────────────────────────────
    # Entraînement
    # ──────────────────────────────────────────────────────────────────────

    def _start_training(self, params: dict) -> None:
        """
        Lance l'entraînement IA depuis la vue training.

        Args:
            params: Dictionnaire des hyperparamètres lus dans la vue :
                {nb_games, gamma, alpha, epsilon, opponent}
        """
        view = self.current_view
        if not isinstance(view, CubeeTrainingView):
            return  # sécurité — la vue a changé entre temps

        # Construction de l'IA "élève" et de l'adversaire
        student = AI("Trainee",
                     gama=params["gamma"],
                     learning_rate=params["alpha"],
                     epsilon=params["epsilon"])
        student.q_table = self.db_q_table
        student.init_db()

        if params["opponent"] == "self":
            opponent: Player = AI("Sparring Partner",
                                  gama=params["gamma"],
                                  learning_rate=params["alpha"],
                                  epsilon=params["epsilon"])
            opponent.q_table = self.db_q_table
            opponent.init_db()
        else:
            opponent = Player("Random")

        # Wrapper du callback pour forcer le rafraîchissement Tkinter
        def progress(current: int, total: int) -> None:
            view.update_progress(current, total)
            view.update()

        # Lancement de l'entraînement (bloquant — l'UI est rafraîchie via progress)
        start_ts = time.time()
        wins, losses, _draws = train_with_progress(
            student=student,
            opponent=opponent,
            nb_games=params["nb_games"],
            progress_callback=progress,
        )
        elapsed = time.time() - start_ts

        view.show_results(wins, losses, params["nb_games"], elapsed)

    # ──────────────────────────────────────────────────────────────────────
    # Sortie vers l'accueil
    # ──────────────────────────────────────────────────────────────────────

    def _quit_to_home(self) -> None:
        """Ferme la fenêtre Cubee et relance la page d'accueil principale."""
        self.destroy()
        import main as root_main
        root_main.main()


# ──────────────────────────────────────────────────────────────────────────
# Points d'entrée publics
# ──────────────────────────────────────────────────────────────────────────


def run_game() -> None:
    """
    Point d'entrée appelé par le main racine quand l'utilisateur sélectionne Cubee.

    Crée et lance l'application Tkinter du jeu.
    """
    app = CubeeApp()
    app.mainloop()


def train() -> None:
    """
    Point d'entrée console pour lancer un entraînement IA vs IA sans UI.

    Conserve la possibilité de tester rapidement l'apprentissage depuis le shell :
        python -c "from games.cubee.main import train; train()"
    """
    engine = create_engine("sqlite:///cubee.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    db_q_table = QTableRepo(session)

    student = AI("Trainee", gama=0.9, learning_rate=0.1, epsilon=0.9)
    student.q_table = db_q_table
    student.init_db()

    sparring = AI("Sparring", gama=0.9, learning_rate=0.1, epsilon=0.9)
    sparring.q_table = db_q_table
    sparring.init_db()

    train_with_progress(
        student=student, opponent=sparring,
        nb_games=10_000,
        progress_callback=lambda c, t: print(f"\rGames: {c}/{t}", end="", flush=True),
        progress_step=500,
    )
    print()


if __name__ == "__main__":
    run_game()
