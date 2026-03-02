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
    """
    
    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#3498DB"
    SECONDARY_COLOR = "#2ECC71"
    TEXT_COLOR = "#2C3E50"
    ACCENT_COLOR = "#E74C3C"
    
    def __init__(self, master, on_play_selected=None, on_train_selected=None, on_back=None):
        super().__init__(master, bg=self.BG_COLOR)
        self.master = master
        self.on_play_selected = on_play_selected
        self.on_train_selected = on_train_selected
        self.on_back = on_back
        
        lang_manager.register_observer(self)
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        header_frame = Frame(self, bg=self.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 10))
        
        self.back_btn = tk.Button(
            header_frame,
            text="← " + lang_manager.get_text("back"),
            font=("Helvetica", 12),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR,
            relief=tk.FLAT,
            command=self.on_back
        )
        self.back_btn.pack(side=tk.LEFT)
        
        self.title_label = tk.Label(
            header_frame,
            text=lang_manager.get_text("menu_title"),
            font=("Helvetica", 28, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.title_label.pack(side=tk.LEFT, padx=100)
        
        content_frame = Frame(self, bg=self.BG_COLOR)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=60, pady=40)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        self._create_play_card(content_frame)
        self._create_train_card(content_frame)
    
    def _create_play_card(self, parent: Frame) -> None:
        play_card = Frame(parent, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        play_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        tk.Label(
            play_card,
            text="🎮 " + lang_manager.get_text("play"),
            font=("Helvetica", 24, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR
        ).pack(pady=(20, 10))
        
        self.vs_ai1_btn = tk.Button(
            play_card, text=lang_manager.get_text("vs_ai1"), font=("Helvetica", 14),
            bg=self.PRIMARY_COLOR, fg="white", width=18, pady=8,
            command=lambda: self.on_play_selected("ai1")
        )
        self.vs_ai1_btn.pack(pady=5)
        
        self.vs_ai2_btn = tk.Button(
            play_card, text=lang_manager.get_text("vs_ai2"), font=("Helvetica", 14),
            bg=self.PRIMARY_COLOR, fg="white", width=18, pady=8,
            command=lambda: self.on_play_selected("ai2")
        )
        self.vs_ai2_btn.pack(pady=5)
        
        self.vs_random_btn = tk.Button(
            play_card, text=lang_manager.get_text("vs_random"), font=("Helvetica", 14),
            bg=self.SECONDARY_COLOR, fg="white", width=18, pady=8,
            command=lambda: self.on_play_selected("random")
        )
        self.vs_random_btn.pack(pady=(5, 20))
    
    def _create_train_card(self, parent: Frame) -> None:
        train_card = Frame(parent, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        train_card.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        
        tk.Label(
            train_card,
            text="🤖 " + lang_manager.get_text("train_ai1"),
            font=("Helvetica", 24, "bold"),
            bg=self.CARD_BG,
            fg=self.ACCENT_COLOR
        ).pack(pady=(20, 10))
        
        self.train_ai1_btn = tk.Button(
            train_card, text=lang_manager.get_text("train_ai1"), font=("Helvetica", 14, "bold"),
            bg=self.ACCENT_COLOR, fg="white", width=18, pady=10,
            command=lambda: self.on_train_selected("ai1")
        )
        self.train_ai1_btn.pack(pady=5)

        self.train_ai2_btn = tk.Button(
            train_card, text=lang_manager.get_text("train_ai2"), font=("Helvetica", 14, "bold"),
            bg=self.ACCENT_COLOR, fg="white", width=18, pady=10,
            command=lambda: self.on_train_selected("ai2")
        )
        self.train_ai2_btn.pack(pady=(5, 20))
    
    def update_language(self) -> None:
        self.title_label.config(text=lang_manager.get_text("menu_title"))
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        self.vs_ai1_btn.config(text=lang_manager.get_text("vs_ai1"))
        self.vs_ai2_btn.config(text=lang_manager.get_text("vs_ai2"))
        self.vs_random_btn.config(text=lang_manager.get_text("vs_random"))
        self.train_ai1_btn.config(text=lang_manager.get_text("train_ai1"))
        self.train_ai2_btn.config(text=lang_manager.get_text("train_ai2"))