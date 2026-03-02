"""
Module contenant le contrôleur du jeu des allumettes.
Fait le lien entre le modèle (logique) et la vue (interface).
"""

from player import Player, Human
from game_model import GameModel
from language_manager import lang_manager


class GameController:
    """
    Contrôleur MVC du jeu des allumettes.
    
    Responsabilités :
    - Gérer les interactions utilisateur (clics sur les boutons)
    - Mettre à jour le modèle selon les actions
    - Notifier la vue des changements d'état
    - Fournir des informations à la vue (nombre d'allumettes, message)
    
    Attributes:
        model (GameModel): Modèle contenant la logique du jeu.
        view: Vue associée (interface graphique).
        on_quit (callable): Callback appelé quand l'utilisateur quitte.
    """
    
    def __init__(self, p1: Player, p2: Player, total_matches: int, view=None, on_quit=None):
        """
        Initialise le contrôleur avec deux joueurs et un nombre d'allumettes.
        
        Precondition: Au moins un des deux joueurs doit être humain (Human).
        
        Args:
            p1 (Player): Premier joueur.
            p2 (Player): Second joueur.
            total_matches (int): Nombre d'allumettes au départ.
            view: Vue associée (sera set après création).
            on_quit (callable): Fonction appelée quand l'utilisateur quitte.
        
        Raises:
            ValueError: Si aucun des deux joueurs n'est humain.
        """
        # Vérifier qu'au moins un joueur est humain
        # (nécessaire pour l'interface graphique)
        if not isinstance(p1, Human) and not isinstance(p2, Human):
            raise ValueError("At least one player must be a Human for GUI mode.")
        
        # Créer le modèle de jeu
        self.model = GameModel(total_matches, p1, p2, displayable=False)
        
        # Stocker la vue (sera utilisée pour les mises à jour)
        self.view = view
        
        # Callback pour quitter vers le menu
        self.on_quit = on_quit
        
        # Si l'IA commence, la faire jouer immédiatement
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()
    
    def set_view(self, view) -> None:
        """
        Associe une vue au contrôleur.
        
        Args:
            view: Vue (interface graphique) à associer.
        """
        self.view = view
        
        # Si l'IA commence, la faire jouer maintenant que la vue existe
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()
    
    def get_nb_matches(self) -> int:
        """
        Retourne le nombre d'allumettes restantes dans le jeu.
        
        Returns:
            int: Nombre d'allumettes actuelles.
        """
        return self.model.nb
    
    def get_status_message(self) -> str:
        """
        Génère le message d'état à afficher (tour du joueur ou gagnant).
        
        Returns:
            str: Message traduit dans la langue courante.
        """
        if self.model.is_game_over():
            # Partie terminée : afficher le gagnant
            winner = self.model.get_winner()
            if winner:
                # Utiliser la traduction "winner" avec le nom du joueur
                return lang_manager.get_text("winner").format(winner.name)
            return "Game Over"
        else:
            # Partie en cours : afficher le tour du joueur
            current_player = self.model.get_current_player()
            # Utiliser la traduction "player_turn" avec le nom du joueur
            return lang_manager.get_text("player_turn").format(current_player.name)
    
    def reset_game(self) -> None:
        """
        Réinitialise la partie pour rejouer.
        
        Actions :
        - Remet les allumettes au nombre initial
        - Mélange l'ordre des joueurs
        - Recrée les boutons d'action dans la vue
        - Fait jouer l'IA si elle commence
        """
        # Réinitialiser le modèle
        self.model.reset()
        
        # Réinitialiser la vue
        if self.view:
            self.view.reset()
        
        # Si l'IA commence après le reset, la faire jouer
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()
    
    def quit_to_menu(self) -> None:
        """
        Quitte la partie en cours et retourne au menu principal.
        
        Appelle le callback on_quit si défini.
        """
        if self.on_quit:
            self.on_quit()
    
    def handle_human_move(self, nb: int) -> None:
        """
        Gère un coup joué par l'humain (clic sur un bouton).
        
        Workflow :
        1. Vérifier que c'est bien au tour de l'humain
        2. Appliquer le coup au modèle
        3. Vérifier si la partie est terminée
        4. Sinon, passer au joueur suivant
        5. Si c'est l'IA, la faire jouer automatiquement
        6. Mettre à jour l'affichage
        
        Args:
            nb (int): Nombre d'allumettes prises (1, 2 ou 3).
        
        Precondition: Le joueur actuel doit être un Human.
        """
        # Vérifier que c'est bien au tour de l'humain
        # (sécurité pour éviter que l'humain joue pendant le tour de l'IA)
        if not isinstance(self.model.get_current_player(), Human):
            return
        
        # Appliquer le coup au modèle
        self.model.step(nb)
        
        # Vérifier si la partie est terminée
        if self.model.is_game_over():
            self.handle_end_game()
        else:
            # Passer au joueur suivant
            self.model.switch_player()
            
            # Si c'est une IA, la faire jouer automatiquement
            if not isinstance(self.model.get_current_player(), Human):
                self.handle_ai_move()
        
        # Mettre à jour l'affichage
        if self.view:
            self.view.update_view()
    
    def handle_ai_move(self) -> None:
        """
        Gère un coup joué automatiquement par l'IA.
        
        Workflow :
        1. Demander à l'IA de choisir son coup
        2. Appliquer le coup au modèle
        3. Vérifier si la partie est terminée
        4. Sinon, passer au joueur suivant
        5. Mettre à jour l'affichage
        
        Precondition: Le joueur actuel doit être une IA (pas Human).
        """
        # Récupérer le coup choisi par l'IA
        current_player = self.model.get_current_player()
        action = current_player.play()
        
        # Appliquer le coup
        self.model.step(action)
        
        # Vérifier la fin de partie
        if self.model.is_game_over():
            self.handle_end_game()
        else:
            # Passer au joueur suivant
            self.model.switch_player()
        
        # Mettre à jour l'affichage
        if self.view:
            self.view.update_view()
    
    def handle_end_game(self) -> None:
        """
        Gère la fin de la partie.
        
        Actions :
        1. Mettre à jour les statistiques des joueurs (win/lose)
        2. Notifier la vue pour afficher l'écran de fin
        """
        # Récupérer le gagnant et le perdant
        winner = self.model.get_winner()
        loser = self.model.get_loser()
        
        # Mettre à jour leurs statistiques
        if winner:
            winner.win()
        if loser:
            loser.lose()
        
        # Notifier la vue pour afficher l'écran de fin
        if self.view:
            self.view.end_game()
