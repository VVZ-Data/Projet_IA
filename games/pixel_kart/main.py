"""
[IA-Claude] Point d'entrée du jeu Pixel Kart.

Architecture (calquée sur games/allumette/main.py) :
    - PixelKartApp(tk.Tk) : fenêtre unique avec une vue courante (Frame)
    - clear_view + show_xxx() : navigation entre les vues
    - GameController : logique d'une course en cours

Vues :
    - PixelKartMenuView      : menu principal (Play / Training)
    - PixelKartRaceView      : course en cours
    - PixelKartTrainingView  : configuration et suivi de l'entraînement Q-learning

L'application initialise une session SQLAlchemy (`pixelkart.db` dans
`dao/data/`) qui est partagée par les fonctionnalités IA. Le mode "vs AI"
charge la Q-table du dernier run entraîné ; si la base est vide, on
retombe automatiquement sur un `RandomAI`.
"""

import os
import time
import tkinter as tk

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from language_manager import lang_manager
from .ai_train import create_run, train
from .dao.base import Base
from .dao.q_table import EpisodeLog, Run
from .dao.q_table_repository import QTableRepository
from .editor import map_dao
from .game_controller import GameController
from .game_model import Circuit, Race
from .player import Human, QLearningAI, RandomAI
from .views.menu_view import PixelKartMenuView
from .views.race_view import PixelKartRaceView
from .views.training_view import PixelKartTrainingView


# Chemin par défaut de la base SQLite Pixel Kart (relatif à ce fichier)
_DAO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dao", "data")
_DB_PATH = os.path.join(_DAO_DIR, "pixelkart.db")


class PixelKartApp(tk.Tk):
    """
    Application principale du jeu Pixel Kart.

    Gère la navigation entre :
    - le menu principal (PixelKartMenuView)
    - une course (PixelKartRaceView via GameController)
    - l'entraînement (PixelKartTrainingView)
    - le retour à la sélection des jeux (page d'accueil)
    """

    def __init__(self) -> None:
        """Initialise la fenêtre, la session SQLAlchemy et affiche le menu."""
        super().__init__()
        self.title("Pixel Kart")
        self.geometry("1200x720")
        self.configure(bg="#F5F7FA")

        # Session DB (créée si nécessaire). Chemin local au module pour ne
        # pas dépendre du cwd à l'exécution.
        os.makedirs(_DAO_DIR, exist_ok=True)
        engine = create_engine(f"sqlite:///{_DB_PATH}")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        self.current_view: tk.Frame | None = None
        self.game_controller: GameController | None = None

        self.show_menu()

    # ──────────────────────────────────────────────────────────────────────
    # Navigation
    # ──────────────────────────────────────────────────────────────────────

    def clear_view(self) -> None:
        """Détruit la vue courante en se désabonnant du gestionnaire de langue."""
        if self.current_view is not None:
            lang_manager.unregister_observer(self.current_view)
            self.current_view.pack_forget()
            self.current_view.destroy()
            self.current_view = None
        self.game_controller = None

    def show_menu(self) -> None:
        """Affiche le menu principal du jeu."""
        self.clear_view()
        self.current_view = PixelKartMenuView(
            self,
            on_play_selected=self._on_play_selected,
            on_train_selected=self.show_training,
            on_back=self._quit_to_home,
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def show_training(self) -> None:
        """Affiche la vue d'entraînement de l'IA Q-learning."""
        self.clear_view()
        self.current_view = PixelKartTrainingView(
            self,
            on_start_training=self._start_training,
            on_back=self.show_menu,
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)

    # ──────────────────────────────────────────────────────────────────────
    # Démarrage d'une course
    # ──────────────────────────────────────────────────────────────────────

    def _on_play_selected(self, config: dict) -> None:
        """
        Crée une course en fonction de la config et affiche la vue de course.

        Args:
            config: Dict du menu, clés {mode, circuit, nb_turns}.
                mode ∈ {"solo", "ai", "human"}.
        """
        circuits = map_dao.get_all()
        raw = circuits.get(config["circuit"])
        if raw is None:
            print(f"Circuit '{config['circuit']}' introuvable.")
            return

        circuit = Circuit(name=config["circuit"], raw=raw)

        if config["mode"] == "solo":
            karts = [Human("Bob")]
        elif config["mode"] == "ai":
            karts = [Human("Bob"), self._build_ai_opponent("Randy")]
        else:  # human vs human
            karts = [Human("Bob"), Human("Alice")]

        race = Race(circuit=circuit, karts=karts, nb_turns=config["nb_turns"])
        self._start_race(race)

    def _build_ai_opponent(self, name: str):
        """
        Construit l'adversaire IA pour le mode "vs AI".

        Si un Run a déjà été entraîné en base, on instancie un `QLearningAI`
        en mode exploitation pure (`training=False`, `epsilon=0.0`) branché
        sur la Q-table du dernier run. Sinon, on retombe sur un `RandomAI`
        pour ne pas faire planter le mode "vs AI" sur une base vide.

        Args:
            name: Nom du kart IA à afficher.

        Returns:
            Un Kart prêt à être placé sur la grille (QLearningAI ou RandomAI).
        """
        latest_run: Run | None = (
            self.session.query(Run).order_by(Run.created_at.desc()).first()
        )
        if latest_run is None:
            return RandomAI(name)

        repository = QTableRepository(self.session, run_id=latest_run.id)
        return QLearningAI(
            name=name,
            repository=repository,
            gamma=latest_run.gamma,
            alpha=latest_run.alpha,
            epsilon=0.0,
            training=False,
        )

    def _start_race(self, race: Race) -> None:
        """Affiche la vue de course et instancie le contrôleur."""
        self.clear_view()

        self.game_controller = GameController(
            race=race,
            on_quit=self.show_menu,
        )

        race_view = PixelKartRaceView(
            self,
            race=race,
            on_action=self.game_controller.handle_action,
            on_back=self.game_controller.handle_quit,
        )
        self.game_controller.set_view(race_view)

        self.current_view = race_view
        self.current_view.pack(fill=tk.BOTH, expand=True)

        # Lancer le premier tour si le 1er kart est une IA
        self.game_controller.start()

    # ──────────────────────────────────────────────────────────────────────
    # Entraînement
    # ──────────────────────────────────────────────────────────────────────

    def _start_training(self, params: dict) -> None:
        """
        Lance un entraînement complet déclenché depuis la vue training.

        Args:
            params: Hyperparamètres collectés par PixelKartTrainingView :
                {name, circuit, nb_turns, nb_episodes, gamma, alpha,
                 epsilon_start, epsilon_end}.
        """
        view = self.current_view
        if not isinstance(view, PixelKartTrainingView):
            return  # sécurité — la vue a changé entre temps

        # Construction du Circuit à partir du nom choisi
        circuits = map_dao.get_all()
        raw = circuits.get(params["circuit"])
        if raw is None:
            return
        circuit = Circuit(name=params["circuit"], raw=raw)

        # Création du Run en base
        run_id = create_run(
            session=self.session,
            name=params["name"],
            gamma=params["gamma"],
            alpha=params["alpha"],
            epsilon_start=params["epsilon_start"],
            epsilon_end=params["epsilon_end"],
            circuit_name=params["circuit"],
            notes=f"nb_turns={params['nb_turns']}",
        )

        # Wrapper du callback pour rafraîchir Tkinter pendant la boucle
        def progress(current: int, total: int) -> None:
            view.update_progress(current, total)
            view.update()

        start_ts = time.time()
        train(
            session=self.session,
            run_id=run_id,
            nb_episodes=params["nb_episodes"],
            circuit=circuit,
            nb_turns=params["nb_turns"],
            progress_callback=progress,
        )
        elapsed = time.time() - start_ts

        # Calcul des stats finales depuis la table episode_log
        finished_count, crashed_count, avg_reward = self._summarize_run(
            run_id, params["nb_episodes"]
        )
        view.show_results(
            nb_finished=finished_count,
            nb_crashed=crashed_count,
            total=params["nb_episodes"],
            avg_reward=avg_reward,
            elapsed_s=elapsed,
        )

    def _summarize_run(self, run_id: int, nb_episodes: int) -> tuple[int, int, float]:
        """
        Calcule les stats finales d'un run pour l'affichage des résultats.

        Args:
            run_id: ID du run en base.
            nb_episodes: Nombre d'épisodes joués lors de cet appel `train()`.

        Returns:
            Tuple (nb_finished, nb_crashed, avg_reward_last_window).
            La fenêtre de calcul de la récompense moyenne est de min(500, nb_episodes).
        """
        logs = (
            self.session.query(EpisodeLog)
            .filter(EpisodeLog.run_id == run_id)
            .order_by(EpisodeLog.episode_num.desc())
            .limit(nb_episodes)
            .all()
        )
        if not logs:
            return 0, 0, 0.0

        finished_count = sum(1 for log in logs if log.finished)
        crashed_count = sum(1 for log in logs if log.crashed)

        window = min(500, len(logs))
        avg_reward = sum(log.total_reward for log in logs[:window]) / window

        return finished_count, crashed_count, avg_reward

    # ──────────────────────────────────────────────────────────────────────
    # Sortie vers l'accueil
    # ──────────────────────────────────────────────────────────────────────

    def _quit_to_home(self) -> None:
        """Ferme cette fenêtre et relance le main racine (sélection des jeux)."""
        self.destroy()
        import main as root_main
        root_main.main()


def run_game() -> None:
    """Point d'entrée appelé par le main racine quand on choisit Pixel Kart."""
    app = PixelKartApp()
    app.mainloop()


if __name__ == "__main__":
    run_game()
