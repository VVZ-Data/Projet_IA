"""
Vue du menu principal du jeu Cubee.

Layout calqué sur celui d'Allumettes :
- Header (bouton back + titre)
- Deux cartes côte à côte : Play (gauche) / Training (droite)

Le bouton Back retourne à la sélection des jeux (page d'accueil).
"""

import tkinter as tk
from tkinter import Frame

from language_manager import lang_manager


class CubeeMenuView(Frame):
    """
    Menu principal du jeu Cubee.

    Callbacks :
        on_play_selected(mode: str)
            mode ∈ {"ai", "random", "human"}
            "ai"     : Humain vs IA Q-learning entraînée
            "random" : Humain vs joueur aléatoire (sans apprentissage)
            "human"  : Humain vs Humain (local, chacun à son tour)
        on_train_selected()
            Affiche la vue de configuration d'entraînement.
        on_back()
            Retour à la sélection des jeux.
    """

    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#3498DB"
    SECONDARY_COLOR = "#2ECC71"
    ACCENT_COLOR = "#E74C3C"
    TEXT_COLOR = "#2C3E50"

    def __init__(
        self,
        master,
        on_play_selected=None,
        on_train_selected=None,
        on_back=None,
    ) -> None:
        """
        Construit le menu et enregistre la frame auprès du gestionnaire de langue.

        Args:
            master:            Fenêtre Tkinter parente (CubeeApp).
            on_play_selected:  Callback(mode: str) appelé quand l'utilisateur
                               clique sur un bouton de la carte Play.
            on_train_selected: Callback() appelé pour passer à la vue training.
            on_back:           Callback() pour revenir à la page d'accueil.
        """
        super().__init__(master, bg=self.BG_COLOR)
        self.on_play_selected = on_play_selected
        self.on_train_selected = on_train_selected
        self.on_back = on_back

        lang_manager.register_observer(self)
        self._create_widgets()

    # ──────────────────────────────────────────────────────────────────────────
    # Construction de l'UI
    # ──────────────────────────────────────────────────────────────────────────

    def _create_widgets(self) -> None:
        """Construit le header et les deux cartes Play / Train."""
        # === Header (back + titre) ===
        header = Frame(self, bg=self.BG_COLOR)
        header.pack(fill=tk.X, padx=40, pady=(30, 10))

        self.back_btn = tk.Button(
            header,
            text="← " + lang_manager.get_text("back"),
            font=("Helvetica", 12),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR,
            relief=tk.FLAT,
            command=self._on_back,
        )
        self.back_btn.pack(side=tk.LEFT)

        self.title_label = tk.Label(
            header,
            text=lang_manager.get_text("cubee_menu_title"),
            font=("Helvetica", 28, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR,
        )
        self.title_label.pack(side=tk.LEFT, padx=100)

        # === Cartes Play / Training ===
        cards = Frame(self, bg=self.BG_COLOR)
        cards.pack(expand=True, fill=tk.BOTH, padx=60, pady=40)
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        self._create_play_card(cards)
        self._create_train_card(cards)

    def _create_play_card(self, parent: Frame) -> None:
        """Crée la carte de gauche : sélection du mode de jeu."""
        play_card = Frame(parent, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        play_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self.play_title = tk.Label(
            play_card,
            text="🎮 " + lang_manager.get_text("cubee_play"),
            font=("Helvetica", 24, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR,
        )
        self.play_title.pack(pady=(20, 10))

        self.vs_ai_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("cubee_vs_ai"),
            font=("Helvetica", 14, "bold"),
            bg=self.PRIMARY_COLOR, fg="white",
            width=18, pady=8,
            command=lambda: self._fire_play("ai"),
        )
        self.vs_ai_btn.pack(pady=5)

        self.vs_random_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("cubee_vs_random"),
            font=("Helvetica", 14, "bold"),
            bg=self.SECONDARY_COLOR, fg="white",
            width=18, pady=8,
            command=lambda: self._fire_play("random"),
        )
        self.vs_random_btn.pack(pady=5)

        self.vs_human_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("cubee_vs_human"),
            font=("Helvetica", 14, "bold"),
            bg="#9B59B6", fg="white",
            width=18, pady=8,
            command=lambda: self._fire_play("human"),
        )
        self.vs_human_btn.pack(pady=(5, 20))

    def _create_train_card(self, parent: Frame) -> None:
        """Crée la carte de droite : entrée vers l'entraînement."""
        train_card = Frame(parent, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        train_card.grid(row=0, column=1, sticky="nsew", padx=(20, 0))

        self.train_title = tk.Label(
            train_card,
            text="🤖 " + lang_manager.get_text("cubee_training"),
            font=("Helvetica", 24, "bold"),
            bg=self.CARD_BG,
            fg=self.ACCENT_COLOR,
        )
        self.train_title.pack(pady=(20, 10))

        self.train_btn = tk.Button(
            train_card,
            text=lang_manager.get_text("cubee_train_start"),
            font=("Helvetica", 14, "bold"),
            bg=self.ACCENT_COLOR, fg="white",
            width=18, pady=10,
            command=self._fire_train,
        )
        self.train_btn.pack(pady=(20, 20))

    # ──────────────────────────────────────────────────────────────────────────
    # Callbacks
    # ──────────────────────────────────────────────────────────────────────────

    def _fire_play(self, mode: str) -> None:
        """Délègue le mode choisi au callback fourni par l'application."""
        if self.on_play_selected:
            self.on_play_selected(mode)

    def _fire_train(self) -> None:
        """Délègue l'entrée dans la vue training à l'application."""
        if self.on_train_selected:
            self.on_train_selected()

    def _on_back(self) -> None:
        """Délègue le retour à la page d'accueil à l'application."""
        if self.on_back:
            self.on_back()

    # ──────────────────────────────────────────────────────────────────────────
    # Multilingue
    # ──────────────────────────────────────────────────────────────────────────

    def update_language(self) -> None:
        """Recharge les libellés depuis le LanguageManager."""
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        self.title_label.config(text=lang_manager.get_text("cubee_menu_title"))
        self.play_title.config(text="🎮 " + lang_manager.get_text("cubee_play"))
        self.train_title.config(text="🤖 " + lang_manager.get_text("cubee_training"))
        self.vs_ai_btn.config(text=lang_manager.get_text("cubee_vs_ai"))
        self.vs_random_btn.config(text=lang_manager.get_text("cubee_vs_random"))
        self.vs_human_btn.config(text=lang_manager.get_text("cubee_vs_human"))
        self.train_btn.config(text=lang_manager.get_text("cubee_train_start"))
