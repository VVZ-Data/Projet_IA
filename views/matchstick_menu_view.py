"""
Module contenant la vue du menu du jeu des allumettes.
Permet de choisir entre jouer ou entraîner l'IA.
"""

import tkinter as tk
from tkinter import Frame
from language_manager import lang_manager


class MatchstickMenuView(Frame):
    """
    Menu principal du jeu des allumettes.
    
    Propose deux sections :
    - JOUER : avec options "vs IA" et "vs Random"
    - ENTRAÎNER : avec un bouton pour lancer l'entraînement
    
    Attributes:
        master: Fenêtre parente.
        on_play_selected (callable): Callback pour jouer (reçoit "ai" ou "random").
        on_train_selected (callable): Callback pour entraîner.
        on_back (callable): Callback pour retourner à l'accueil.
    """
    
    # Constantes de style
    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#3498DB"
    SECONDARY_COLOR = "#2ECC71"
    TEXT_COLOR = "#2C3E50"
    ACCENT_COLOR = "#E74C3C"
    
    def __init__(self, master, on_play_selected=None, on_train_selected=None, on_back=None):
        """
        Initialise le menu du jeu des allumettes.
        
        Args:
            master: Fenêtre parente.
            on_play_selected (callable): Fonction appelée avec le mode ("ai"/"random").
            on_train_selected (callable): Fonction appelée pour lancer l'entraînement.
            on_back (callable): Fonction appelée pour retourner à l'accueil.
        """
        super().__init__(master, bg=self.BG_COLOR)
        self.master = master
        self.on_play_selected = on_play_selected
        self.on_train_selected = on_train_selected
        self.on_back = on_back
        
        # S'enregistrer pour les changements de langue
        lang_manager.register_observer(self)
        
        # Créer l'interface
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """
        Crée et positionne tous les widgets du menu.
        
        Structure :
        - En-tête avec titre et bouton retour
        - Deux grandes cartes : "Jouer" et "Entraîner"
        """
        # === EN-TÊTE ===
        header_frame = Frame(self, bg=self.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 10))
        
        # Bouton retour (à gauche)
        self.back_btn = tk.Button(
            header_frame,
            text="← " + lang_manager.get_text("back"),
            font=("Helvetica", 12),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_back_click
        )
        self.back_btn.pack(side=tk.LEFT)
        
        # Titre centré
        self.title_label = tk.Label(
            header_frame,
            text=lang_manager.get_text("menu_title"),
            font=("Helvetica", 28, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.title_label.pack(side=tk.LEFT, padx=100)
        
        # === CONTENU PRINCIPAL ===
        content_frame = Frame(self, bg=self.BG_COLOR)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=60, pady=40)
        
        # Configurer la grille (2 colonnes)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # === CARTE "JOUER" ===
        self._create_play_card(content_frame)
        
        # === CARTE "ENTRAÎNER" ===
        self._create_train_card(content_frame)
    
    def _create_play_card(self, parent: Frame) -> None:
        """
        Crée la carte "Jouer" avec les options vs IA et vs Random.
        
        Args:
            parent (Frame): Frame parent où placer la carte.
        """
        # Frame de la carte
        play_card = Frame(
            parent,
            bg=self.CARD_BG,
            relief=tk.RAISED,
            bd=3
        )
        play_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Titre de la carte
        self.play_title = tk.Label(
            play_card,
            text="🎮 " + lang_manager.get_text("play"),
            font=("Helvetica", 24, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR
        )
        self.play_title.pack(pady=(40, 30))
        
        # Bouton "vs IA"
        self.vs_ai_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("vs_ai"),
            font=("Helvetica", 16),
            bg=self.PRIMARY_COLOR,
            fg="white",
            width=20,
            pady=15,
            cursor="hand2",
            relief=tk.FLAT,
            command=lambda: self._on_play_click("ai")
        )
        self.vs_ai_btn.pack(pady=15)
        
        # Effet hover sur le bouton IA
        self.vs_ai_btn.bind("<Enter>", lambda e: self.vs_ai_btn.config(bg="#2980B9"))
        self.vs_ai_btn.bind("<Leave>", lambda e: self.vs_ai_btn.config(bg=self.PRIMARY_COLOR))
        
        # Bouton "vs Random"
        self.vs_random_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("vs_random"),
            font=("Helvetica", 16),
            bg=self.SECONDARY_COLOR,
            fg="white",
            width=20,
            pady=15,
            cursor="hand2",
            relief=tk.FLAT,
            command=lambda: self._on_play_click("random")
        )
        self.vs_random_btn.pack(pady=(15, 40))
        
        # Effet hover sur le bouton Random
        self.vs_random_btn.bind("<Enter>", lambda e: self.vs_random_btn.config(bg="#27AE60"))
        self.vs_random_btn.bind("<Leave>", lambda e: self.vs_random_btn.config(bg=self.SECONDARY_COLOR))
    
    def _create_train_card(self, parent: Frame) -> None:
        """
        Crée la carte "Entraîner" pour lancer l'entraînement de l'IA.
        
        Args:
            parent (Frame): Frame parent où placer la carte.
        """
        # Frame de la carte
        train_card = Frame(
            parent,
            bg=self.CARD_BG,
            relief=tk.RAISED,
            bd=3
        )
        train_card.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        
        # Titre de la carte
        self.train_title = tk.Label(
            train_card,
            text="🤖 " + lang_manager.get_text("train"),
            font=("Helvetica", 24, "bold"),
            bg=self.CARD_BG,
            fg=self.ACCENT_COLOR
        )
        self.train_title.pack(pady=(40, 30))
        
        # Description
        desc_text = ("Entraîner deux IA à jouer l'une contre l'autre\n"
                    "pour améliorer leurs stratégies")
        if lang_manager.get_lang() == "fr":
            desc_text = ("Entraîner deux IA à jouer l'une contre l'autre\n"
                        "pour améliorer leurs stratégies")
        
        desc_label = tk.Label(
            train_card,
            text=desc_text,
            font=("Helvetica", 12),
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR,
            justify=tk.CENTER
        )
        desc_label.pack(pady=20)
        
        # Bouton "Entraîner"
        self.train_btn = tk.Button(
            train_card,
            text=lang_manager.get_text("start_training"),
            font=("Helvetica", 16, "bold"),
            bg=self.ACCENT_COLOR,
            fg="white",
            width=20,
            pady=20,
            cursor="hand2",
            relief=tk.FLAT,
            command=self._on_train_click
        )
        self.train_btn.pack(pady=(30, 40))
        
        # Effet hover
        self.train_btn.bind("<Enter>", lambda e: self.train_btn.config(bg="#C0392B"))
        self.train_btn.bind("<Leave>", lambda e: self.train_btn.config(bg=self.ACCENT_COLOR))
    
    def _on_play_click(self, mode: str) -> None:
        """
        Gère le clic sur un bouton de jeu.
        
        Args:
            mode (str): Mode de jeu ("ai" ou "random").
        """
        if self.on_play_selected:
            self.on_play_selected(mode)
    
    def _on_train_click(self) -> None:
        """Gère le clic sur le bouton d'entraînement."""
        if self.on_train_selected:
            self.on_train_selected()
    
    def _on_back_click(self) -> None:
        """Gère le clic sur le bouton retour."""
        if self.on_back:
            self.on_back()
    
    def update_language(self) -> None:
        """
        Met à jour tous les textes suite à un changement de langue.
        Appelée automatiquement par le LanguageManager.
        """
        # Mettre à jour le titre
        self.title_label.config(text=lang_manager.get_text("menu_title"))
        
        # Mettre à jour le bouton retour
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        
        # Mettre à jour les cartes
        self.play_title.config(text="🎮 " + lang_manager.get_text("play"))
        self.vs_ai_btn.config(text=lang_manager.get_text("vs_ai"))
        self.vs_random_btn.config(text=lang_manager.get_text("vs_random"))
        
        self.train_title.config(text="🤖 " + lang_manager.get_text("train"))
        self.train_btn.config(text=lang_manager.get_text("start_training"))
