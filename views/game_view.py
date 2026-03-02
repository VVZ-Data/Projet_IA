"""
Module contenant la vue du jeu des allumettes.
Interface graphique pour jouer contre l'IA ou un joueur random.
"""

import tkinter as tk
from tkinter import Frame
from language_manager import lang_manager


class GameView(Frame):
    """
    Interface graphique du jeu des allumettes.
    
    Affiche :
    - Le nombre d'allumettes restantes (dessinées sur un canvas)
    - Le message d'état (tour du joueur ou gagnant)
    - Les boutons pour prendre 1, 2 ou 3 allumettes
    - Un bouton pour rejouer ou quitter
    
    Attributes:
        controller: Contrôleur du jeu (gère la logique).
        canvas (tk.Canvas): Zone de dessin pour les allumettes.
        message_label (tk.Label): Affiche l'état du jeu.
        buttons_frame (Frame): Contient les boutons d'action.
    """
    
    # === CONSTANTES DE STYLE ===
    # Ces valeurs définissent l'apparence visuelle de l'interface
    WINDOW_TITLE = "Matchstick Game"
    CANVAS_WIDTH = 700  # Largeur du canvas (zone de dessin)
    CANVAS_HEIGHT = 250  # Hauteur du canvas
    BG_COLOR = "#F5F7FA"  # Couleur de fond principale
    MATCH_COLOR = "#C0392B"  # Couleur du corps de l'allumette (rouge foncé)
    HEAD_COLOR = "#E74C3C"  # Couleur de la tête de l'allumette (rouge vif)
    BTN_COLOR = "#2C3E50"  # Couleur des boutons (gris foncé)
    BTN_TXT_COLOR = "white"  # Couleur du texte des boutons
    FONT_TITLE = ("Helvetica", 16, "bold")
    FONT_BTN = ("Helvetica", 13)
    
    def __init__(self, master, controller) -> None:
        """
        Initialise la vue du jeu.
        
        Args:
            master: Fenêtre parente Tkinter.
            controller: Contrôleur du jeu (gère la logique métier).
        """
        super().__init__(master, bg=self.BG_COLOR)
        self.master = master
        self.controller = controller
        
        # S'enregistrer pour recevoir les notifications de changement de langue
        lang_manager.register_observer(self)
        
        # Créer tous les widgets de l'interface
        self._create_widgets()
        
        # Mettre à jour l'affichage initial
        self.update_view()
    
    def _create_widgets(self) -> None:
        """
        Crée et positionne tous les widgets de l'interface de jeu.
        
        Organisation verticale :
        1. Message d'état (qui joue / qui a gagné)
        2. Canvas avec les allumettes dessinées
        3. Frame avec les boutons d'action
        """
        # === MESSAGE D'ÉTAT ===
        # Label affichant le tour du joueur ou le gagnant
        self.message_label = tk.Label(
            self,
            text="",  # Le texte sera rempli par update_view()
            font=self.FONT_TITLE,
            bg=self.BG_COLOR,
            pady=15
        )
        self.message_label.pack()
        
        # === CANVAS POUR DESSINER LES ALLUMETTES ===
        # Zone de dessin graphique où seront affichées les allumettes
        self.canvas = tk.Canvas(
            self,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg=self.BG_COLOR,
            highlightthickness=0  # Pas de bordure
        )
        self.canvas.pack(pady=15)
        
        # === BOUTONS D'ACTION ===
        # Frame contenant les boutons (prendre 1/2/3 ou rejouer/quitter)
        self.buttons_frame = Frame(self, bg=self.BG_COLOR)
        self.buttons_frame.pack(pady=15)
        
        # Créer les 3 boutons "Take 1", "Take 2", "Take 3"
        self._create_action_buttons()
    
    def _create_action_buttons(self) -> None:
        """
        Crée les 3 boutons permettant de prendre 1, 2 ou 3 allumettes.
        
        Ces boutons sont créés dans une boucle pour éviter la répétition de code.
        Chaque bouton appelle controller.handle_human_move(n) avec le nombre choisi.
        """
        # Boucle pour créer les boutons "Take 1", "Take 2", "Take 3"
        for i in range(1, 4):
            # Texte du bouton dans la langue courante
            btn_text = lang_manager.get_text("take", number=i)
            
            # Créer le bouton
            btn = tk.Button(
                self.buttons_frame,
                text=btn_text,
                font=self.FONT_BTN,
                bg=self.BTN_COLOR,
                fg=self.BTN_TXT_COLOR,
                width=10,
                padx=8,
                pady=8,
                cursor="hand2",  # Curseur main au survol
                relief=tk.FLAT,
                # Commande : appeler le contrôleur avec le nombre d'allumettes
                command=lambda n=i: self.controller.handle_human_move(n)
            )
            btn.pack(side=tk.LEFT, padx=10)
            
            # Effet visuel au survol (hover)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#34495E"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.BTN_COLOR))
    
    def update_view(self) -> None:
        """
        Met à jour l'affichage complet du jeu.
        
        Cette méthode est appelée :
        - À l'initialisation
        - Après chaque coup joué
        - Lors d'un changement de langue
        
        Actions effectuées :
        1. Efface et redessine les allumettes sur le canvas
        2. Met à jour le message d'état (qui joue ou qui a gagné)
        """
        # Effacer tout ce qui est sur le canvas
        self.canvas.delete("all")
        
        # Dessiner le nombre actuel d'allumettes
        nb_matches = self.controller.get_nb_matches()
        self.draw_matches(nb_matches)
        
        # Mettre à jour le message d'état
        status_message = self.controller.get_status_message()
        self.message_label.config(text=status_message)
    
    def draw_matches(self, nb: int) -> None:
        """
        Dessine un certain nombre d'allumettes sur le canvas.
        
        Chaque allumette est composée de :
        - Un rectangle vertical (corps de l'allumette)
        - Un ovale en haut (tête de l'allumette)
        
        Les allumettes sont automatiquement espacées et centrées.
        
        Args:
            nb (int): Nombre d'allumettes à dessiner.
        """
        # Si plus aucune allumette, ne rien dessiner
        if nb <= 0:
            return
        
        # === CALCUL DE L'ESPACEMENT ===
        match_width = 14  # Largeur d'une allumette
        
        # Espacement entre les allumettes (minimum 30px, réduit si trop d'allumettes)
        spacing = min(45, (self.CANVAS_WIDTH - 80) // nb)
        
        # Position X de départ pour centrer toutes les allumettes
        start_x = (self.CANVAS_WIDTH - spacing * nb) // 2 + spacing // 2
        
        # === DESSIN DES ALLUMETTES ===
        for i in range(nb):
            # Position X de cette allumette
            x = start_x + i * spacing
            
            # Dessiner le corps de l'allumette (rectangle vertical)
            self.canvas.create_rectangle(
                x - 4, 60,  # Coin supérieur gauche
                x + 4, self.CANVAS_HEIGHT - 40,  # Coin inférieur droit
                fill=self.MATCH_COLOR,
                outline=""  # Pas de contour
            )
            
            # Dessiner la tête de l'allumette (ovale)
            self.canvas.create_oval(
                x - match_width // 2, 35,  # Coin supérieur gauche
                x + match_width // 2, 65,  # Coin inférieur droit
                fill=self.HEAD_COLOR,
                outline=""
            )
    
    def end_game(self) -> None:
        """
        Affiche l'écran de fin de partie.
        
        Actions :
        1. Supprime les boutons "Take 1/2/3"
        2. Affiche un bouton "Rejouer" et un bouton "Quitter"
        """
        # Supprimer tous les boutons présents dans la frame
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        # === BOUTON REJOUER ===
        play_again_btn = tk.Button(
            self.buttons_frame,
            text=lang_manager.get_text("play_again"),
            font=self.FONT_BTN,
            bg="#27AE60",  # Vert
            fg="white",
            width=12,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT,
            command=self.controller.reset_game
        )
        play_again_btn.pack(side=tk.LEFT, padx=10)
        
        # Effet hover
        play_again_btn.bind("<Enter>", lambda e: play_again_btn.config(bg="#229954"))
        play_again_btn.bind("<Leave>", lambda e: play_again_btn.config(bg="#27AE60"))
        
        # === BOUTON QUITTER ===
        quit_btn = tk.Button(
            self.buttons_frame,
            text=lang_manager.get_text("quit"),
            font=self.FONT_BTN,
            bg="#E74C3C",  # Rouge
            fg="white",
            width=12,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT,
            command=self.controller.quit_to_menu
        )
        quit_btn.pack(side=tk.LEFT, padx=10)
        
        # Effet hover
        quit_btn.bind("<Enter>", lambda e: quit_btn.config(bg="#C0392B"))
        quit_btn.bind("<Leave>", lambda e: quit_btn.config(bg="#E74C3C"))
        
        # Rafraîchir l'affichage
        self.update_view()
    
    def reset(self) -> None:
        """
        Réinitialise l'affichage pour une nouvelle partie.
        
        Actions :
        1. Supprime les boutons "Rejouer" et "Quitter"
        2. Recrée les 3 boutons "Take 1/2/3"
        """
        # Supprimer tous les widgets de la frame de boutons
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        # Recréer les boutons d'action pour une nouvelle partie
        self._create_action_buttons()
        
        # Rafraîchir l'affichage
        self.update_view()
    
    def update_language(self) -> None:
        """
        Met à jour tous les textes de l'interface après un changement de langue.
        
        Appelée automatiquement par le LanguageManager quand l'utilisateur
        change de langue via le bouton EN/FR.
        """
        # Mettre à jour le message d'état
        status_message = self.controller.get_status_message()
        self.message_label.config(text=status_message)
        
        # Recréer les boutons avec les nouveaux textes
        # (seule façon simple de mettre à jour le texte des boutons)
        self.reset()
