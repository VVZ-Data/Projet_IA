"""
Point d'entrée du jeu des allumettes (Matchstick Game).

Ce module gère l'application complète du jeu des allumettes,
incluant le menu, les parties, et l'entraînement des IA.

Architecture MVC:
    - Modèle: player.py, game_model.py
    - Vue: views/game_view.py, views/matchstick_menu_view.py, views/training_view.py
    - Contrôleur: game_controller.py

Flux de navigation:
    Menu → Jouer/Entraîner → Partie/Entraînement → Retour Menu → Retour Accueil

Auteurs: Victor Van Zieleghem, Ethan Nickels
Projet: IN252 - HENaLLux 2025-2026
"""

import tkinter as tk
from .player import Player, Human, AI
from .game_model import GameModel
from .game_controller import GameController
from .views.matchstick_menu_view import MatchstickMenuView
from .views.game_view import GameView
from .views.training_view import TrainingView
from language_manager import lang_manager


class MatchstickGameApp(tk.Tk):
    """
    Application principale du jeu des allumettes.
    
    Gère la navigation entre les différentes vues du jeu :
    - Menu principal (jouer / entraîner)
    - Interface de jeu (humain vs IA/Random)
    - Interface d'entraînement (configuration + résultats)
    
    Cette classe remplace le MainApplication qui mélangeait
    l'accueil général et le jeu des allumettes.
    
    Attributes:
        current_view (Frame): Vue actuellement affichée à l'écran.
        game_controller (GameController): Contrôleur actif lors d'une partie.
    """
    
    def __init__(self):
        """
        Initialise l'application du jeu des allumettes.
        
        Configure la fenêtre et affiche le menu principal du jeu.
        """
        super().__init__()
        
        # === CONFIGURATION DE LA FENÊTRE ===
        self.title("Matchstick Game")
        self.geometry("900x700")
        self.configure(bg="#F5F7FA")
        self.resizable(False, False)
        
        # === VARIABLES D'ÉTAT ===
        self.current_view = None  # Vue actuellement affichée
        self.game_controller = None  # Contrôleur du jeu actif
        
        # === AFFICHER LE MENU PRINCIPAL ===
        self.show_matchstick_menu()
    
    def clear_view(self) -> None:
        """
        Supprime la vue actuellement affichée.
        
        Actions effectuées :
        1. Désenregistre la vue du gestionnaire de langue
           (évite les fuites mémoire et erreurs sur widgets détruits)
        2. Masque la vue (pack_forget)
        3. Détruit tous ses widgets enfants
        4. Réinitialise current_view à None
        
        Précondition: Peut être appelée même si current_view est None.
        """
        if self.current_view:
            # Désenregistrer du gestionnaire de langue pour éviter
            # que des callbacks soient appelés sur des widgets détruits
            lang_manager.unregister_observer(self.current_view)
            
            # Masquer et détruire la vue
            self.current_view.pack_forget()
            self.current_view.destroy()
            self.current_view = None
    
    def show_matchstick_menu(self) -> None:
        """
        Affiche le menu principal du jeu des allumettes.
        
        Le menu présente deux cartes :
        - 🎮 Jouer : Choix de l'adversaire (IA 1, IA 2, Random)
        - 🤖 Entraîner : Choix de l'IA à entraîner (IA 1 ou IA 2)
        
        Cette vue est le hub central du jeu, accessible depuis
        toutes les autres vues via le bouton "Retour".
        """
        self.clear_view()
        
        # Créer la vue du menu avec les callbacks appropriés
        self.current_view = MatchstickMenuView(
            self,
            on_play_selected=self._on_play_selected,  # Lancer une partie
            on_train_selected=self._show_training,     # Afficher config entraînement
            on_back=self._quit_to_home                 # Retour à l'accueil général
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def _on_play_selected(self, mode: str) -> None:
        """
        Gère le lancement d'une partie selon le mode choisi.
        
        Crée les deux joueurs (humain + adversaire) et lance la partie.
        
        Args:
            mode (str): Mode de jeu sélectionné.
                       Valeurs possibles : "ai1", "ai2", "random"
        
        Workflow:
            1. Créer le joueur humain (Player 1)
            2. Créer l'adversaire selon le mode :
               - "ai1" : IA 1 avec epsilon faible (exploitation)
               - "ai2" : IA 2 avec epsilon faible
               - "random" : Joueur aléatoire simple
            3. Charger le modèle sauvegardé de l'IA si disponible
            4. Lancer la partie
        """
        # === CRÉER LE JOUEUR HUMAIN ===
        human = Human("Player 1")
        
        # === CRÉER L'ADVERSAIRE SELON LE MODE ===
        if mode == "ai1":
            # IA 1 avec faible exploration (epsilon=0.1)
            # pour jouer de manière optimale
            opponent = AI("AI 1", epsilon=0.1)
            try:
                # Charger le modèle entraîné depuis AI_save_1
                opponent.download("AI_save_1")
            except FileNotFoundError:
                # Si pas de sauvegarde, utiliser une IA non entraînée
                pass
                
        elif mode == "ai2":
            # IA 2 avec faible exploration
            opponent = AI("AI 2", epsilon=0.1)
            try:
                opponent.download("AI_save_2")
            except FileNotFoundError:
                pass
                
        else:  # mode == "random"
            # Joueur aléatoire simple (classe Player de base)
            opponent = Player("Random Bot")
        
        # === LANCER LA PARTIE ===
        self._start_game(human, opponent)
    
    def _start_game(
        self, 
        p1: Player, 
        p2: Player, 
        total_matches: int = 15
    ) -> None:
        """
        Lance une partie de jeu des allumettes.
        
        Crée le contrôleur MVC et la vue du jeu, puis affiche le plateau.
        
        Args:
            p1 (Player): Premier joueur (généralement l'humain).
            p2 (Player): Second joueur (IA ou Random).
            total_matches (int): Nombre d'allumettes au départ (défaut: 15).
        
        Architecture:
            - GameController : Gère la logique et les événements
            - GameView : Affiche le plateau et les boutons
            - GameModel : État du jeu (nombre d'allumettes, tour actuel)
        """
        self.clear_view()
        
        # === CRÉER LE CONTRÔLEUR DE JEU ===
        # Le contrôleur gère toute la logique métier
        self.game_controller = GameController(
            p1, p2, total_matches,
            on_quit=self.show_matchstick_menu  # Callback pour retour au menu
        )
        
        # === CRÉER LA VUE DU JEU ===
        # La vue affiche le plateau (Canvas) et les boutons d'action
        game_view = GameView(self, self.game_controller)
        
        # Associer la vue au contrôleur (relation bidirectionnelle)
        self.game_controller.set_view(game_view)
        
        # === AFFICHER LA VUE ===
        self.current_view = game_view
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def _show_training(self, target: str) -> None:
        """
        Affiche l'interface d'entraînement pour une IA spécifique.
        
        L'interface permet de configurer :
        - Nombre de parties d'entraînement
        - Fréquence de diminution d'epsilon
        - Taux d'apprentissage (learning rate)
        - Type d'adversaire (Random ou autre IA)
        
        Args:
            target (str): Identifiant de l'IA à entraîner.
                         Valeurs possibles : "ai1", "ai2"
        """
        self.clear_view()
        
        # Créer la vue d'entraînement avec les callbacks
        self.current_view = TrainingView(
            self,
            ai_target=target,
            on_start_training=lambda nb, dec, lr, opp: self._start_training(
                target, nb, dec, lr, opp
            ),
            on_back=self.show_matchstick_menu
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def _start_training(
        self,
        target: str,
        nb_games: int,
        epsilon_decay: int,
        learning_rate: float,
        opponent_type: str
    ) -> None:
        """
        Lance l'entraînement d'une IA avec les paramètres donnés.
        
        L'entraînement fonctionne par itérations :
        1. L'IA "élève" joue contre un adversaire
        2. Après chaque partie, l'élève met à jour sa value-function
        3. Epsilon diminue progressivement (exploration → exploitation)
        4. Les résultats sont affichés et peuvent être sauvegardés
        
        Args:
            target (str): IA à entraîner ("ai1" ou "ai2").
            nb_games (int): Nombre de parties d'entraînement.
            epsilon_decay (int): Fréquence de diminution d'epsilon.
                                (ex: 5000 = diminuer tous les 5000 parties)
            learning_rate (float): Taux d'apprentissage (0.0 à 1.0).
                                  Plus élevé = apprentissage rapide mais instable.
            opponent_type (str): Type d'adversaire.
                                Valeurs : "random" ou "other_ai"
        
        Side Effects:
            - Met à jour la barre de progression dans la vue
            - Affiche les résultats finaux avec analyse
            - Permet la sauvegarde du modèle entraîné
        """
        # === CRÉER L'IA ÉLÈVE (celle qui apprend) ===
        # Epsilon élevé au départ pour explorer les stratégies
        student = AI("AI Student", epsilon=0.9, learning_rate=learning_rate)
        save_name = "AI_save_1" if target == "ai1" else "AI_save_2"
        
        # Charger l'état actuel de l'élève s'il existe
        # (permet de reprendre un entraînement)
        try:
            student.download(save_name)
        except FileNotFoundError:
            # Commencer avec une IA vierge
            pass
        
        # === CRÉER L'ADVERSAIRE ===
        if opponent_type == "random":
            # Adversaire aléatoire simple
            opponent = Player("Random")
        else:
            # L'autre IA (avec faible exploration pour être stable)
            opp_save = "AI_save_2" if target == "ai1" else "AI_save_1"
            opponent = AI("AI Opponent", epsilon=0.1)
            try:
                opponent.download(opp_save)
            except FileNotFoundError:
                pass
        
        # === CRÉER LE JEU D'ENTRAÎNEMENT ===
        # displayable=False car pas besoin d'affichage console
        training_game = GameModel(12, student, opponent, displayable=False)
        
        # === BOUCLE D'ENTRAÎNEMENT ===
        for i in range(nb_games):
            # Diminuer epsilon régulièrement pour réduire l'exploration
            if i % epsilon_decay == 0 and i > 0:
                student.next_epsilon()
            
            # Jouer une partie complète
            training_game.play()
            
            # Entraîner uniquement l'élève (pas l'adversaire)
            # Met à jour la value-function avec TD-Learning
            student.train()
            
            # Réinitialiser pour la partie suivante
            training_game.reset()
            
            # Mettre à jour la barre de progression
            # (rafraîchissement tous les 1000 parties pour performance)
            if i % 1000 == 0 or i == nb_games - 1:
                self.current_view.update_progress(i + 1, nb_games)
                self.current_view.update()  # Forcer le rafraîchissement Tkinter
        
        # === AFFICHER LES RÉSULTATS ===
        # Récupérer le nombre de victoires de l'adversaire
        opponent_wins = opponent.nb_wins if hasattr(opponent, 'nb_wins') else 0
        
        # Afficher l'écran de résultats avec statistiques et analyse
        self.current_view.show_results(
            student.nb_wins,      # Victoires de l'élève
            opponent_wins,        # Victoires de l'adversaire
            nb_games,            # Nombre total de parties
            on_save_callback=lambda: student.upload(save_name)  # Sauvegarde
        )
    
    def _quit_to_home(self) -> None:
        """
        Quitte le jeu et retourne à la page d'accueil principale.
        
        Workflow:
        1. Ferme cette fenêtre (MatchstickGameApp)
        2. Libère les ressources Tkinter
        3. Relance le main.py racine pour afficher home_view
        
        Cette méthode permet de revenir à la sélection de jeux
        sans avoir à redémarrer toute l'application.
        """
        # Fermer cette fenêtre
        self.destroy()
        
        # Relancer le main racine pour revenir à l'accueil
        import main as root_main
        root_main.main()


def run_game():
    """
    Fonction d'entrée pour lancer le jeu des allumettes.
    
    Cette fonction est appelée par le main.py racine quand
    l'utilisateur sélectionne ce jeu depuis la page d'accueil.
    
    Crée et lance l'application Tkinter du jeu.
    Elle constitue le point d'entrée public de ce module.
    
    Example:
        >>> # Depuis le main racine
        >>> from games.jeux_1 import main as game1
        >>> game1.run_game()  # Lance le jeu des allumettes
    """
    app = MatchstickGameApp()
    app.mainloop()


# Permettre l'exécution directe du jeu sans passer par l'accueil
# Utile pour le développement et les tests
if __name__ == "__main__":
    run_game()