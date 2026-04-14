"""
Vue du menu principal du jeu Pixel Kart.

Layout identique aux autres jeux :
- Header (back button + titre)
- Deux cartes côte à côte : Play (gauche) / Training (droite)
- Sous les cartes : panneau "Settings" pour le circuit et le nombre de tours

Le bouton Back retourne à la sélection des jeux (page d'accueil).
"""

import tkinter as tk
from tkinter import Frame, ttk

from language_manager import lang_manager
import games.pixel_kart.editor.map_dao as map_dao
from games.pixel_kart.editor.map_editor import CircuitEditor


class PixelKartMenuView(Frame):
    """
    Menu principal du jeu Pixel Kart.

    Callbacks :
        on_play_selected(mode: str)
            mode ∈ {"ai", "human"}
            "ai"   : Humain vs IA random
            "human": Humain vs Humain (local, chacun à son tour)
        on_back()
            Retour à la sélection des jeux.

    L'utilisateur peut aussi configurer ici :
    - Le circuit (dropdown)
    - Le nombre de tours (entry)
    - Ouvrir l'éditeur de circuit
    Ces paramètres sont relus par get_config() au moment du Play.
    """

    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#3498DB"
    SECONDARY_COLOR = "#2ECC71"
    TEXT_COLOR = "#2C3E50"
    DISABLED_TEXT = "#95A5A6"
    ACCENT_COLOR = "#E74C3C"
    DISABLED_BG = "#E8EDF2"

    def __init__(self, master, on_play_selected=None, on_back=None):
        super().__init__(master, bg=self.BG_COLOR)
        self.master = master
        self.on_play_selected = on_play_selected
        self.on_back = on_back

        self.circuit_var = tk.StringVar()
        self.turns_var = tk.StringVar(value="3")
        self.circuit_dropdown = None  # créé/rebuilt par _refresh_circuits

        lang_manager.register_observer(self)
        self._create_widgets()
        self._refresh_circuits()

    # ---------- Construction de l'UI ----------

    def _create_widgets(self) -> None:
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
            command=self._back
        )
        self.back_btn.pack(side=tk.LEFT)

        self.title_label = tk.Label(
            header,
            text=lang_manager.get_text("pixel_kart_menu_title"),
            font=("Helvetica", 28, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.title_label.pack(side=tk.LEFT, padx=80)

        # === Cartes Play / Training ===
        cards = Frame(self, bg=self.BG_COLOR)
        cards.pack(fill=tk.X, padx=60, pady=(10, 20))
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        self._create_play_card(cards)
        self._create_train_card(cards)

        # === Settings (circuit + tours) ===
        self._create_settings_panel()

    def _create_play_card(self, parent: Frame) -> None:
        play_card = Frame(parent, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        play_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        self.play_title = tk.Label(
            play_card,
            text="🎮 " + lang_manager.get_text("pk_play"),
            font=("Helvetica", 22, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR
        )
        self.play_title.pack(pady=(20, 15))

        self.solo_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("pk_solo"),
            font=("Helvetica", 14, "bold"),
            bg=self.ACCENT_COLOR,
            fg="white",
            width=18,
            pady=10,
            command=lambda: self._on_play_clicked("solo")
        )
        self.solo_btn.pack(pady=8)

        self.vs_ai_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("pk_vs_ai"),
            font=("Helvetica", 14, "bold"),
            bg=self.PRIMARY_COLOR,
            fg="white",
            width=18,
            pady=10,
            command=lambda: self._on_play_clicked("ai")
        )
        self.vs_ai_btn.pack(pady=8)

        self.vs_human_btn = tk.Button(
            play_card,
            text=lang_manager.get_text("pk_vs_human"),
            font=("Helvetica", 14, "bold"),
            bg=self.SECONDARY_COLOR,
            fg="white",
            width=18,
            pady=10,
            command=lambda: self._on_play_clicked("human")
        )
        self.vs_human_btn.pack(pady=(8, 20))

    def _create_train_card(self, parent: Frame) -> None:
        train_card = Frame(parent, bg=self.DISABLED_BG, relief=tk.FLAT, bd=3)
        train_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        self.train_title = tk.Label(
            train_card,
            text="🤖 " + lang_manager.get_text("pk_training"),
            font=("Helvetica", 22, "bold"),
            bg=self.DISABLED_BG,
            fg=self.DISABLED_TEXT
        )
        self.train_title.pack(pady=(20, 15))

        self.coming_soon_label = tk.Label(
            train_card,
            text=lang_manager.get_text("coming_soon"),
            font=("Helvetica", 14, "italic"),
            bg=self.DISABLED_BG,
            fg=self.DISABLED_TEXT,
            pady=20
        )
        self.coming_soon_label.pack(pady=(8, 20))

    def _create_settings_panel(self) -> None:
        self.settings_frame = ttk.LabelFrame(
            self, text=lang_manager.get_text("pk_settings")
        )
        self.settings_frame.pack(padx=60, pady=10, fill="x")

        # Ligne circuit
        self.circuit_row = ttk.Frame(self.settings_frame)
        self.circuit_row.pack(fill="x", padx=10, pady=8)
        self.circuit_label = ttk.Label(
            self.circuit_row, text=lang_manager.get_text("pk_choose_circuit")
        )
        self.circuit_label.pack(side="left", padx=5)
        # Le dropdown est créé dans _refresh_circuits

        # Ligne nombre de tours
        turns_row = ttk.Frame(self.settings_frame)
        turns_row.pack(fill="x", padx=10, pady=8)
        self.turns_label = ttk.Label(
            turns_row, text=lang_manager.get_text("pk_nb_turns")
        )
        self.turns_label.pack(side="left", padx=5)
        ttk.Entry(turns_row, textvariable=self.turns_var, width=5).pack(side="left", padx=5)

        # Bouton ouvrir l'éditeur
        self.editor_btn = ttk.Button(
            self.settings_frame,
            text=lang_manager.get_text("pk_open_editor"),
            command=self._open_editor
        )
        self.editor_btn.pack(fill="x", padx=10, pady=(0, 10))

    # ---------- Logique ----------

    def _refresh_circuits(self) -> None:
        """Recharge la liste des circuits depuis le DAO et reconstruit le dropdown."""
        circuits = map_dao.get_all()
        names = list(circuits.keys())

        if self.circuit_dropdown is not None:
            self.circuit_dropdown.destroy()

        if not names:
            self.circuit_var.set("")
            self.circuit_dropdown = tk.OptionMenu(self.circuit_row, self.circuit_var, "")
        else:
            current = self.circuit_var.get()
            if current not in names:
                self.circuit_var.set(names[0])
            self.circuit_dropdown = tk.OptionMenu(self.circuit_row, self.circuit_var, *names)
        self.circuit_dropdown.pack(side="left", padx=5)

    def _open_editor(self) -> None:
        """Ouvre l'éditeur de circuit en Toplevel."""
        editor = CircuitEditor(self.master, callback=self._on_editor_chose)
        editor.bind("<Destroy>", lambda e: self._refresh_circuits())

    def _on_editor_chose(self, circuit_name: str) -> None:
        self._refresh_circuits()
        if circuit_name:
            self.circuit_var.set(circuit_name)

    def _back(self) -> None:
        if self.on_back:
            self.on_back()

    def _on_play_clicked(self, mode: str) -> None:
        config = self.get_config()
        if not config["circuit"]:
            return  # rien à faire si aucun circuit dispo
        config["mode"] = mode
        if self.on_play_selected:
            self.on_play_selected(config)

    def get_config(self) -> dict:
        try:
            nb_turns = int(self.turns_var.get())
        except ValueError:
            nb_turns = 3
        return {
            "circuit": self.circuit_var.get(),
            "nb_turns": max(1, nb_turns),
        }

    # ---------- Multilingue ----------

    def update_language(self) -> None:
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        self.title_label.config(text=lang_manager.get_text("pixel_kart_menu_title"))
        self.play_title.config(text="🎮 " + lang_manager.get_text("pk_play"))
        self.solo_btn.config(text=lang_manager.get_text("pk_solo"))
        self.vs_ai_btn.config(text=lang_manager.get_text("pk_vs_ai"))
        self.vs_human_btn.config(text=lang_manager.get_text("pk_vs_human"))
        self.train_title.config(text="🤖 " + lang_manager.get_text("pk_training"))
        self.coming_soon_label.config(text=lang_manager.get_text("coming_soon"))
        self.settings_frame.config(text=lang_manager.get_text("pk_settings"))
        self.circuit_label.config(text=lang_manager.get_text("pk_choose_circuit"))
        self.turns_label.config(text=lang_manager.get_text("pk_nb_turns"))
        self.editor_btn.config(text=lang_manager.get_text("pk_open_editor"))
