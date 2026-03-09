"""
Module contenant la vue de la page d'accueil de l'application.
Affiche une sélection de jeux disponibles.
"""

import tkinter as tk
from tkinter import Frame
from language_manager import lang_manager


class HomeView(Frame):
    """
    Page d'accueil affichant les jeux disponibles.
    
    Cette vue présente trois cartes de jeux :
    - Jeu des allumettes (cliquable)
    - Deux jeux "à venir" (non cliquables pour le moment)
    
    Attributes:
        master: Fenêtre parente Tkinter.
        on_game_selected (callable): Callback appelé quand un jeu est sélectionné.
        lang_button (LanguageButton): Bouton de sélection de langue.
    """
    
    # Constantes de style pour une interface moderne
    BG_COLOR = "#92B6EB"  # Gris très clair pour le fond
    CARD_BG = "#FFFFFF"  # Blanc pour les cartes
    CARD_DISABLED = "#E8EDF2"  # Gris pour les cartes désactivées
    PRIMARY_COLOR = "#3498DB"  # Bleu pour les éléments actifs
    TEXT_COLOR = "#2C3E50"  # Gris foncé pour le texte
    DISABLED_TEXT = "#95A5A6"  # Gris clair pour texte désactivé
    SHADOW = "#BDC3C7"  # Couleur pour l'ombre des cartes
    
    def __init__(self, master, on_game_selected=None):
        """
        Initialise la page d'accueil.
        
        Args:
            master: Fenêtre parente Tkinter.
            on_game_selected (callable): Fonction appelée avec le nom du jeu
                                        quand l'utilisateur clique dessus.
        """
        super().__init__(master, bg=self.BG_COLOR)
        self.master = master
        self.on_game_selected = on_game_selected
        
        # S'enregistrer comme observateur pour les changements de langue
        lang_manager.register_observer(self)
        
        # Créer l'interface
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """
        Crée et positionne tous les widgets de la page d'accueil.
        
        Structure :
        - En-tête avec titre et bouton de langue
        - Description
        - Grille de 3 cartes de jeux
        """
        # === EN-TÊTE ===
        header_frame = Frame(self, bg=self.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 10))
        
        # Titre de l'application
        self.title_label = tk.Label(
            header_frame,
            text=lang_manager.get_text("title"),
            font=("Helvetica", 32, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Bouton de sélection de langue (en haut à droite)
        self.lang_button = LanguageButton(header_frame)
        self.lang_button.pack(side=tk.RIGHT)
        
        # === DESCRIPTION ===
        self.desc_label = tk.Label(
            self,
            text=lang_manager.get_text("select_game"),
            font=("Helvetica", 14),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.desc_label.pack(pady=(0, 30))
        
        # === GRILLE DE JEUX ===
        games_frame = Frame(self, bg=self.BG_COLOR)
        games_frame.pack(expand=True, fill=tk.BOTH, padx=40)
        
        # Configurer la grille pour centrer les cartes
        for i in range(3):
            games_frame.columnconfigure(i, weight=1)
        
        # Créer les 3 cartes de jeux
        self._create_game_cards(games_frame)
    
    def _create_game_cards(self, parent: Frame) -> None:
        """
        Crée les 3 cartes de jeux (1 active, 2 désactivées).
        
        Args:
            parent (Frame): Frame parent où placer les cartes.
        """
        # Jeu 1 : Allumettes (disponible)
        self.card1 = GameCard(
            parent,
            title=lang_manager.get_text("matchstick_game"),
            emoji="🔥",
            enabled=True,
            on_click=lambda: self._on_game_click("matchstick")
        )
        self.card1.grid(row=0, column=0, padx=15, pady=20, sticky="nsew")
        
        # Jeu 2 : À venir
        self.card2 = GameCard(
            parent,
            title=lang_manager.get_text("coming_soon"),
            emoji="🎮",
            enabled=False
        )
        self.card2.grid(row=0, column=1, padx=15, pady=20, sticky="nsew")
        
        # Jeu 3 : À venir
        self.card3 = GameCard(
            parent,
            title=lang_manager.get_text("coming_soon"),
            emoji="🎲",
            enabled=False
        )
        self.card3.grid(row=0, column=2, padx=15, pady=20, sticky="nsew")
    
    def _on_game_click(self, game_name: str) -> None:
        """
        Gère le clic sur une carte de jeu.
        
        Args:
            game_name (str): Identifiant du jeu sélectionné.
        """
        if self.on_game_selected:
            self.on_game_selected(game_name)
    
    def update_language(self) -> None:
        """
        Met à jour tous les textes suite à un changement de langue.
        Appelée automatiquement par le LanguageManager.
        """
        # Mettre à jour le titre
        self.title_label.config(text=lang_manager.get_text("title"))
        
        # Mettre à jour la description
        self.desc_label.config(text=lang_manager.get_text("select_game"))
        
        # Mettre à jour les cartes
        self.card1.update_text(lang_manager.get_text("matchstick_game"))
        self.card2.update_text(lang_manager.get_text("coming_soon"))
        self.card3.update_text(lang_manager.get_text("coming_soon"))


class GameCard(Frame):
    """
    Carte cliquable représentant un jeu.
    
    Affiche un emoji, un titre et change d'apparence au survol
    si la carte est active.
    
    Attributes:
        enabled (bool): Indique si la carte est cliquable.
        on_click (callable): Fonction appelée lors d'un clic.
        emoji_label (tk.Label): Label affichant l'emoji du jeu.
        title_label (tk.Label): Label affichant le titre du jeu.
    """
    
    def __init__(self, master, title: str, emoji: str, enabled: bool = True, on_click=None):
        """
        Initialise une carte de jeu.
        
        Args:
            master: Widget parent.
            title (str): Titre du jeu.
            emoji (str): Emoji représentant le jeu.
            enabled (bool): Si True, la carte est cliquable.
            on_click (callable): Fonction appelée lors d'un clic.
        """
        # Couleur de fond selon l'état (actif/désactivé)
        bg_color = HomeView.CARD_BG if enabled else HomeView.CARD_DISABLED
        
        super().__init__(
            master,
            bg=bg_color,
            relief=tk.RAISED if enabled else tk.FLAT,
            bd=2,
            cursor="hand2" if enabled else "arrow"
        )
        
        self.enabled = enabled
        self.on_click = on_click
        self._is_hovered = False
        
        # === EMOJI ===
        self.emoji_label = tk.Label(
            self,
            text=emoji,
            font=("Helvetica", 64),
            bg=bg_color
        )
        self.emoji_label.pack(pady=(40, 20))
        
        # === TITRE ===
        text_color = HomeView.TEXT_COLOR if enabled else HomeView.DISABLED_TEXT
        self.title_label = tk.Label(
            self,
            text=title,
            font=("Helvetica", 18, "bold" if enabled else "normal"),
            bg=bg_color,
            fg=text_color
        )
        self.title_label.pack(pady=(0, 40))
        
        # Lier les événements si la carte est active
        if self.enabled:
            self._bind_events()
    
    def _bind_events(self) -> None:
        """
        Lie les événements de souris pour l'interactivité.
        """
        # Lier le clic
        self.bind("<Button-1>", lambda e: self._on_click())
        self.emoji_label.bind("<Button-1>", lambda e: self._on_click())
        self.title_label.bind("<Button-1>", lambda e: self._on_click())
        
        # Lier le survol (hover)
        self.bind("<Enter>", lambda e: self._on_hover())
        self.bind("<Leave>", lambda e: self._on_leave())
    
    def _on_click(self) -> None:
        """Gère le clic sur la carte."""
        if self.enabled and self.on_click:
            self.on_click()
    
    def _on_hover(self) -> None:
        """Change l'apparence au survol de la souris."""
        self._is_hovered = True
        self.config(bg=HomeView.PRIMARY_COLOR, relief=tk.RIDGE)
        self.emoji_label.config(bg=HomeView.PRIMARY_COLOR)
        self.title_label.config(bg=HomeView.PRIMARY_COLOR, fg="white")
    
    def _on_leave(self) -> None:
        """Restaure l'apparence normale."""
        self._is_hovered = False
        self.config(bg=HomeView.CARD_BG, relief=tk.RAISED)
        self.emoji_label.config(bg=HomeView.CARD_BG)
        self.title_label.config(bg=HomeView.CARD_BG, fg=HomeView.TEXT_COLOR)
    
    def update_text(self, new_title: str) -> None:
        """
        Met à jour le titre de la carte (pour changement de langue).
        
        Args:
            new_title (str): Nouveau titre à afficher.
        """
        self.title_label.config(text=new_title)


class LanguageButton(Frame):
    """
    Bouton de sélection de langue avec menu déroulant au survol.
    
    Affiche la langue courante et révèle les options au survol.
    
    Attributes:
        current_label (tk.Label): Label affichant la langue courante.
        options_frame (Frame): Frame contenant les options de langue.
    """
    
    def __init__(self, master):
        """
        Initialise le bouton de langue.
        
        Args:
            master: Widget parent.
        """
        super().__init__(master, bg=HomeView.BG_COLOR)
        
        # Label affichant la langue courante (ex: "EN", "FR")
        self.current_label = tk.Label(
            self,
            text=lang_manager.get_lang().upper(),
            font=("Helvetica", 14, "bold"),
            bg=HomeView.PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.current_label.pack(side=tk.LEFT)
        
        # Frame des options (initialement cachée)
        self.options_frame = Frame(self, bg=HomeView.BG_COLOR)
        
        # Créer les boutons de langue
        self._create_lang_options()
        
        # Lier les événements de survol
        self.current_label.bind("<Enter>", lambda e: self._show_options())
        self.bind("<Leave>", lambda e: self._hide_options())
    
    def _create_lang_options(self) -> None:
        """Crée les boutons pour chaque langue disponible."""
        languages = [("EN", "en"), ("FR", "fr")]
        
        for lang_display, lang_code in languages:
            btn = tk.Label(
                self.options_frame,
                text=lang_display,
                font=("Helvetica", 12),
                bg="white",
                fg=HomeView.TEXT_COLOR,
                padx=12,
                pady=6,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=2)
            
            # Lier le clic pour changer de langue
            btn.bind("<Button-1>", lambda e, code=lang_code: self._change_lang(code))
            
            # Effet hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=HomeView.PRIMARY_COLOR, fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="white", fg=HomeView.TEXT_COLOR))
    
    def _show_options(self) -> None:
        """Affiche les options de langue."""
        self.options_frame.pack(side=tk.LEFT, padx=(5, 0))
    
    def _hide_options(self) -> None:
        """Masque les options de langue."""
        self.options_frame.pack_forget()
    
    def _change_lang(self, lang_code: str) -> None:
        """
        Change la langue de l'application.
        
        Args:
            lang_code (str): Code de la nouvelle langue ("en" ou "fr").
        """
        lang_manager.set_lang(lang_code)
        # Mettre à jour le label courant
        self.current_label.config(text=lang_code.upper())
