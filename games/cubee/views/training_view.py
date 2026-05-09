"""
Vue d'entraînement de l'IA pour Cubee.

L'utilisateur configure les hyperparamètres (gamma, alpha, epsilon, nb parties,
type d'adversaire) puis lance l'entraînement. La vue affiche une barre de
progression pendant l'entraînement, puis un récapitulatif à la fin.

Architecture :
- Carte des paramètres (avant lancement)
- Barre de progression (pendant l'entraînement)
- Carte des résultats (après l'entraînement)

Le calcul de l'entraînement lui-même est délégué au callback `on_start_training`
fourni par l'application principale.
"""

import tkinter as tk
from tkinter import Frame, ttk

from language_manager import lang_manager


class CubeeTrainingView(Frame):
    """
    Frame de configuration et de suivi de l'entraînement IA Cubee.

    Callbacks :
        on_start_training(params: dict)
            Lance l'entraînement avec les hyperparamètres choisis.
            params = {nb_games, gamma, alpha, epsilon, opponent}
        on_back()
            Retour au menu Cubee.
    """

    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#E74C3C"
    TEXT_COLOR = "#2C3E50"
    SUCCESS_COLOR = "#27AE60"

    # Valeurs par défaut des champs du formulaire
    DEFAULT_NB_GAMES = "10000"
    DEFAULT_GAMMA = "0.9"
    DEFAULT_ALPHA = "0.1"
    DEFAULT_EPSILON = "0.9"

    def __init__(self, master, on_start_training=None, on_back=None) -> None:
        """
        Construit la frame d'entraînement.

        Args:
            master:            Fenêtre Tkinter parente (CubeeApp).
            on_start_training: Callback(dict) appelé au clic sur "Start".
            on_back:           Callback() pour revenir au menu.
        """
        super().__init__(master, bg=self.BG_COLOR)
        self.on_start_training = on_start_training
        self.on_back = on_back

        # Variables Tkinter pour les champs et la progression
        self.nb_games_var = tk.StringVar(value=self.DEFAULT_NB_GAMES)
        self.gamma_var = tk.StringVar(value=self.DEFAULT_GAMMA)
        self.alpha_var = tk.StringVar(value=self.DEFAULT_ALPHA)
        self.epsilon_var = tk.StringVar(value=self.DEFAULT_EPSILON)
        self.opponent_var = tk.StringVar(value="random")
        self.progress_var = tk.IntVar(value=0)

        lang_manager.register_observer(self)
        self._create_widgets()

    # ──────────────────────────────────────────────────────────────────────────
    # Construction de l'UI
    # ──────────────────────────────────────────────────────────────────────────

    def _create_widgets(self) -> None:
        """Construit le header, la carte de paramètres et les sections progression/résultats."""
        self._create_header()
        self._create_params_card()
        self._create_progress_section()
        self._create_results_section()

    def _create_header(self) -> None:
        """Header avec bouton back + titre."""
        header = Frame(self, bg=self.BG_COLOR)
        header.pack(fill=tk.X, padx=40, pady=(30, 10))

        self.back_btn = tk.Button(
            header,
            text="← " + lang_manager.get_text("back"),
            font=("Helvetica", 12),
            bg=self.BG_COLOR, fg=self.TEXT_COLOR,
            relief=tk.FLAT, command=self._on_back,
        )
        self.back_btn.pack(side=tk.LEFT)

        self.title_label = tk.Label(
            header,
            text=lang_manager.get_text("cubee_train_title"),
            font=("Helvetica", 24, "bold"),
            bg=self.BG_COLOR, fg=self.TEXT_COLOR,
        )
        self.title_label.pack(side=tk.LEFT, padx=80)

    def _create_params_card(self) -> None:
        """Carte de configuration des hyperparamètres."""
        self.params_card = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        self.params_card.pack(fill=tk.X, padx=60, pady=15)

        form = Frame(self.params_card, bg=self.CARD_BG)
        form.pack(pady=20, padx=40)

        # (clé du label, variable Tk)
        rows = [
            ("cubee_train_nb_games", self.nb_games_var),
            ("cubee_train_gamma",    self.gamma_var),
            ("cubee_train_alpha",    self.alpha_var),
            ("cubee_train_epsilon",  self.epsilon_var),
        ]
        self.row_labels = []  # gardés pour le multilingue
        for i, (key, var) in enumerate(rows):
            label = tk.Label(form, text=lang_manager.get_text(key),
                             font=("Helvetica", 12), bg=self.CARD_BG)
            label.grid(row=i, column=0, sticky="w", pady=5)
            self.row_labels.append((label, key))

            entry = tk.Entry(form, textvariable=var, font=("Helvetica", 12), width=12)
            entry.grid(row=i, column=1, padx=10, pady=5)

        # Sélecteur du type d'adversaire
        self.opp_label = tk.Label(form, text=lang_manager.get_text("cubee_train_opponent"),
                                  font=("Helvetica", 12), bg=self.CARD_BG)
        self.opp_label.grid(row=len(rows), column=0, sticky="w", pady=10)

        self.opp_random_radio = tk.Radiobutton(
            form, text=lang_manager.get_text("cubee_train_opponent_random"),
            variable=self.opponent_var, value="random", bg=self.CARD_BG,
        )
        self.opp_random_radio.grid(row=len(rows), column=1, sticky="w")
        self.opp_self_radio = tk.Radiobutton(
            form, text=lang_manager.get_text("cubee_train_opponent_self"),
            variable=self.opponent_var, value="self", bg=self.CARD_BG,
        )
        self.opp_self_radio.grid(row=len(rows) + 1, column=1, sticky="w")

        self.start_btn = tk.Button(
            self.params_card,
            text=lang_manager.get_text("cubee_train_start"),
            font=("Helvetica", 14, "bold"),
            bg=self.PRIMARY_COLOR, fg="white",
            command=self._on_start_click,
        )
        self.start_btn.pack(pady=20)

    def _create_progress_section(self) -> None:
        """Section affichée pendant l'entraînement (barre de progression)."""
        self.progress_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)

        self.progress_title = tk.Label(
            self.progress_frame,
            text=lang_manager.get_text("cubee_train_progress"),
            font=("Helvetica", 14, "bold"),
            bg=self.CARD_BG, fg=self.TEXT_COLOR,
        )
        self.progress_title.pack(pady=(15, 5))

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, variable=self.progress_var,
            maximum=100, length=400,
        )
        self.progress_bar.pack(pady=10, padx=20)

        self.progress_label = tk.Label(
            self.progress_frame, text="",
            bg=self.CARD_BG, font=("Helvetica", 11),
        )
        self.progress_label.pack(pady=(5, 15))

    def _create_results_section(self) -> None:
        """Section affichée à la fin de l'entraînement (statistiques)."""
        self.results_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)

        self.results_title = tk.Label(
            self.results_frame,
            text=lang_manager.get_text("cubee_train_complete"),
            font=("Helvetica", 16, "bold"),
            bg=self.CARD_BG, fg=self.SUCCESS_COLOR,
        )
        self.results_title.pack(pady=10)

        self.wins_label = tk.Label(self.results_frame, text="",
                                   bg=self.CARD_BG, font=("Helvetica", 12))
        self.wins_label.pack(pady=2)
        self.losses_label = tk.Label(self.results_frame, text="",
                                     bg=self.CARD_BG, font=("Helvetica", 12))
        self.losses_label.pack(pady=2)
        self.elapsed_label = tk.Label(self.results_frame, text="",
                                      bg=self.CARD_BG, font=("Helvetica", 11, "italic"))
        self.elapsed_label.pack(pady=(2, 15))

    # ──────────────────────────────────────────────────────────────────────────
    # Callbacks utilisateur
    # ──────────────────────────────────────────────────────────────────────────

    def _on_start_click(self) -> None:
        """
        Lit les champs, valide les valeurs et déclenche l'entraînement.

        En cas de valeur invalide, on revient en silence (pas de popup pour
        garder l'UX simple — les valeurs par défaut sont déjà sensées).
        """
        try:
            params = {
                "nb_games": max(1, int(self.nb_games_var.get())),
                "gamma":    float(self.gamma_var.get()),
                "alpha":    float(self.alpha_var.get()),
                "epsilon":  float(self.epsilon_var.get()),
                "opponent": self.opponent_var.get(),
            }
        except ValueError:
            return

        # Cacher la carte des paramètres et afficher la progression
        self.params_card.pack_forget()
        self.progress_frame.pack(pady=20, padx=60, fill="x")

        if self.on_start_training:
            self.on_start_training(params)

    def _on_back(self) -> None:
        """Délègue le retour au menu à l'application."""
        if self.on_back:
            self.on_back()

    # ──────────────────────────────────────────────────────────────────────────
    # API appelée depuis le contrôleur d'entraînement
    # ──────────────────────────────────────────────────────────────────────────

    def update_progress(self, current: int, total: int) -> None:
        """
        Met à jour la barre de progression et le compteur de parties jouées.

        Args:
            current: Nombre de parties terminées.
            total:   Nombre total de parties à jouer.
        """
        if total <= 0:
            return
        percent = int((current / total) * 100)
        self.progress_var.set(percent)
        self.progress_label.config(
            text=lang_manager.get_text("cubee_train_games_played").format(current, total)
        )
        # Force le rafraîchissement Tkinter pendant la boucle d'entraînement
        self.update_idletasks()

    def show_results(self, wins: int, losses: int, total: int, elapsed_s: float) -> None:
        """
        Affiche le récapitulatif final après l'entraînement.

        Args:
            wins:      Nombre de victoires de l'IA en cours d'entraînement.
            losses:    Nombre de victoires de l'adversaire.
            total:     Nombre total de parties jouées.
            elapsed_s: Durée totale de l'entraînement en secondes.
        """
        self.progress_frame.pack_forget()
        self.results_frame.pack(pady=20, padx=60, fill="x")

        win_pct = (wins / total * 100) if total else 0.0
        loss_pct = (losses / total * 100) if total else 0.0

        self.wins_label.config(
            text=lang_manager.get_text("cubee_train_wins").format(wins, f"{win_pct:.1f}")
        )
        self.losses_label.config(
            text=lang_manager.get_text("cubee_train_losses").format(losses, f"{loss_pct:.1f}")
        )
        self.elapsed_label.config(
            text=lang_manager.get_text("cubee_train_elapsed").format(f"{elapsed_s:.1f}")
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Multilingue
    # ──────────────────────────────────────────────────────────────────────────

    def update_language(self) -> None:
        """Recharge tous les libellés dynamiques depuis le LanguageManager."""
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        self.title_label.config(text=lang_manager.get_text("cubee_train_title"))
        for label, key in self.row_labels:
            label.config(text=lang_manager.get_text(key))
        self.opp_label.config(text=lang_manager.get_text("cubee_train_opponent"))
        self.opp_random_radio.config(text=lang_manager.get_text("cubee_train_opponent_random"))
        self.opp_self_radio.config(text=lang_manager.get_text("cubee_train_opponent_self"))
        self.start_btn.config(text=lang_manager.get_text("cubee_train_start"))
        self.progress_title.config(text=lang_manager.get_text("cubee_train_progress"))
        self.results_title.config(text=lang_manager.get_text("cubee_train_complete"))
