"""
[IA-Claude] Vue d'entraînement de l'IA Q-learning pour Pixel Kart.

Layout calqué sur les autres vues du projet :
- Header (back button + titre)
- Carte de configuration (formulaire des hyperparamètres + bouton Start)
- Section progression (barre + label "x / N")
- Section résultats (statistiques finales : tours finis, crashs, récompense
  moyenne sur la dernière fenêtre, durée)

L'entraînement lui-même n'est PAS lancé par cette vue — la vue se contente
de collecter les paramètres et d'appeler `on_start_training(params)`. C'est
l'application principale (`PixelKartApp`) qui orchestre la session DB et la
boucle d'entraînement, ce qui garde la vue pure côté présentation.
"""

import tkinter as tk
from tkinter import Frame, ttk

import games.pixel_kart.editor.map_dao as map_dao
from language_manager import lang_manager


class PixelKartTrainingView(Frame):
    """
    Frame de configuration et de suivi de l'entraînement IA pour Pixel Kart.

    Callbacks attendus :
        on_start_training(params: dict)
            Lance l'entraînement avec les hyperparamètres collectés.
            params = {name, circuit, nb_turns, nb_episodes, gamma, alpha,
                      epsilon_start, epsilon_end}
        on_back()
            Retour au menu Pixel Kart.
    """

    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#E74C3C"
    TEXT_COLOR = "#2C3E50"
    SUCCESS_COLOR = "#27AE60"

    # Valeurs par défaut sensées pour un premier entraînement utilisable
    DEFAULTS: dict[str, str] = {
        "name": "default",
        "nb_turns": "1",
        "nb_episodes": "10000",
        "gamma": "0.9",
        "alpha": "0.1",
        "epsilon_start": "1.0",
        "epsilon_end": "0.05",
    }

    def __init__(self, master, on_start_training=None, on_back=None) -> None:
        """
        Construit la frame d'entraînement.

        Args:
            master: Fenêtre Tkinter parente (PixelKartApp).
            on_start_training: Callback(dict) appelé au clic sur "Start".
            on_back: Callback() pour revenir au menu.
        """
        super().__init__(master, bg=self.BG_COLOR)
        self.on_start_training = on_start_training
        self.on_back = on_back

        # Variables Tkinter du formulaire
        self.name_var = tk.StringVar(value=self.DEFAULTS["name"])
        self.circuit_var = tk.StringVar()
        self.nb_turns_var = tk.StringVar(value=self.DEFAULTS["nb_turns"])
        self.nb_episodes_var = tk.StringVar(value=self.DEFAULTS["nb_episodes"])
        self.gamma_var = tk.StringVar(value=self.DEFAULTS["gamma"])
        self.alpha_var = tk.StringVar(value=self.DEFAULTS["alpha"])
        self.epsilon_start_var = tk.StringVar(value=self.DEFAULTS["epsilon_start"])
        self.epsilon_end_var = tk.StringVar(value=self.DEFAULTS["epsilon_end"])
        self.progress_var = tk.IntVar(value=0)

        # Le dropdown circuit est reconstruit dynamiquement (cf. menu_view)
        self.circuit_dropdown: tk.OptionMenu | None = None
        self._row_labels: list[tuple[tk.Label, str]] = []

        lang_manager.register_observer(self)
        self._create_widgets()
        self._refresh_circuits()

    # ──────────────────────────────────────────────────────────────────────
    # Construction de l'UI
    # ──────────────────────────────────────────────────────────────────────

    def _create_widgets(self) -> None:
        """Construit l'ensemble des widgets de la vue."""
        self._create_header()
        self._create_params_card()
        self._create_progress_section()
        self._create_results_section()

    def _create_header(self) -> None:
        """Header : bouton back + titre."""
        header = Frame(self, bg=self.BG_COLOR)
        header.pack(fill=tk.X, padx=40, pady=(30, 10))

        self.back_btn = tk.Button(
            header,
            text="← " + lang_manager.get_text("back"),
            font=("Helvetica", 12),
            bg=self.BG_COLOR, fg=self.TEXT_COLOR,
            relief=tk.FLAT, command=self._on_back_click,
        )
        self.back_btn.pack(side=tk.LEFT)

        self.title_label = tk.Label(
            header,
            text=lang_manager.get_text("pk_train_title"),
            font=("Helvetica", 24, "bold"),
            bg=self.BG_COLOR, fg=self.TEXT_COLOR,
        )
        self.title_label.pack(side=tk.LEFT, padx=80)

    def _create_params_card(self) -> None:
        """Carte de configuration des hyperparamètres + bouton Start."""
        self.params_card = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        self.params_card.pack(fill=tk.X, padx=60, pady=15)

        form = Frame(self.params_card, bg=self.CARD_BG)
        form.pack(pady=20, padx=40)

        # Lignes de label + entry classiques
        rows: list[tuple[str, tk.StringVar]] = [
            ("pk_train_run_name",       self.name_var),
            ("pk_train_nb_turns",       self.nb_turns_var),
            ("pk_train_episodes",       self.nb_episodes_var),
            ("pk_train_gamma",          self.gamma_var),
            ("pk_train_alpha",          self.alpha_var),
            ("pk_train_epsilon_start",  self.epsilon_start_var),
            ("pk_train_epsilon_end",    self.epsilon_end_var),
        ]
        for i, (key, var) in enumerate(rows):
            label = tk.Label(form, text=lang_manager.get_text(key),
                             font=("Helvetica", 12), bg=self.CARD_BG)
            label.grid(row=i, column=0, sticky="w", pady=4)
            self._row_labels.append((label, key))

            entry = tk.Entry(form, textvariable=var, font=("Helvetica", 12), width=14)
            entry.grid(row=i, column=1, padx=10, pady=4)

        # Ligne dédiée pour le dropdown circuit (créé par _refresh_circuits)
        self.circuit_label = tk.Label(form, text=lang_manager.get_text("pk_train_circuit"),
                                      font=("Helvetica", 12), bg=self.CARD_BG)
        self.circuit_label.grid(row=len(rows), column=0, sticky="w", pady=4)
        self._circuit_row = form  # le dropdown sera packé ici, col 1 row=len(rows)
        self._circuit_row_index = len(rows)

        self.no_circuit_label = tk.Label(
            self.params_card,
            text="",
            font=("Helvetica", 10, "italic"),
            bg=self.CARD_BG, fg=self.PRIMARY_COLOR,
        )
        self.no_circuit_label.pack(pady=(0, 5))

        self.start_btn = tk.Button(
            self.params_card,
            text=lang_manager.get_text("pk_train_start"),
            font=("Helvetica", 14, "bold"),
            bg=self.PRIMARY_COLOR, fg="white",
            command=self._on_start_click,
        )
        self.start_btn.pack(pady=20)

    def _create_progress_section(self) -> None:
        """Section progression : titre + barre + label '%'."""
        self.progress_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)

        self.progress_title = tk.Label(
            self.progress_frame,
            text=lang_manager.get_text("pk_train_progress"),
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
        """Section résultats finale, masquée tant que l'entraînement n'est pas terminé."""
        self.results_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)

        self.results_title = tk.Label(
            self.results_frame,
            text=lang_manager.get_text("pk_train_complete"),
            font=("Helvetica", 16, "bold"),
            bg=self.CARD_BG, fg=self.SUCCESS_COLOR,
        )
        self.results_title.pack(pady=10)

        self.finished_label = tk.Label(self.results_frame, text="",
                                       bg=self.CARD_BG, font=("Helvetica", 12))
        self.finished_label.pack(pady=2)
        self.crashed_label = tk.Label(self.results_frame, text="",
                                      bg=self.CARD_BG, font=("Helvetica", 12))
        self.crashed_label.pack(pady=2)
        self.avg_reward_label = tk.Label(self.results_frame, text="",
                                         bg=self.CARD_BG, font=("Helvetica", 12))
        self.avg_reward_label.pack(pady=2)
        self.elapsed_label = tk.Label(self.results_frame, text="",
                                      bg=self.CARD_BG,
                                      font=("Helvetica", 11, "italic"))
        self.elapsed_label.pack(pady=(2, 15))

    # ──────────────────────────────────────────────────────────────────────
    # Logique du dropdown circuit
    # ──────────────────────────────────────────────────────────────────────

    def _refresh_circuits(self) -> None:
        """
        Recharge la liste des circuits depuis le DAO et reconstruit le dropdown.

        Si aucun circuit n'est disponible, on affiche un message d'avertissement
        et on désactive le bouton Start.
        """
        circuits = map_dao.get_all()
        names = list(circuits.keys())

        if self.circuit_dropdown is not None:
            self.circuit_dropdown.destroy()
            self.circuit_dropdown = None

        if not names:
            self.circuit_var.set("")
            self.no_circuit_label.config(text=lang_manager.get_text("pk_train_no_circuit"))
            self.start_btn.config(state="disabled")
            return

        if self.circuit_var.get() not in names:
            self.circuit_var.set(names[0])
        self.circuit_dropdown = tk.OptionMenu(
            self._circuit_row, self.circuit_var, *names
        )
        self.circuit_dropdown.grid(
            row=self._circuit_row_index, column=1, padx=10, pady=4, sticky="w"
        )
        self.no_circuit_label.config(text="")
        self.start_btn.config(state="normal")

    # ──────────────────────────────────────────────────────────────────────
    # Callbacks utilisateur
    # ──────────────────────────────────────────────────────────────────────

    def _on_start_click(self) -> None:
        """
        Lit les champs du formulaire et déclenche l'entraînement.

        Les valeurs invalides (entiers / floats mal formés) sont silencieusement
        ignorées : le bouton ne réagit simplement pas. C'est volontaire pour
        garder l'UX simple — les valeurs par défaut sont déjà sensées.
        """
        try:
            params = {
                "name": self.name_var.get().strip() or "default",
                "circuit": self.circuit_var.get(),
                "nb_turns": max(1, int(self.nb_turns_var.get())),
                "nb_episodes": max(1, int(self.nb_episodes_var.get())),
                "gamma": float(self.gamma_var.get()),
                "alpha": float(self.alpha_var.get()),
                "epsilon_start": float(self.epsilon_start_var.get()),
                "epsilon_end": float(self.epsilon_end_var.get()),
            }
        except ValueError:
            return

        if not params["circuit"]:
            return  # pas de circuit sélectionné

        # Cacher la carte des paramètres, afficher la progression
        self.params_card.pack_forget()
        self.progress_frame.pack(pady=20, padx=60, fill="x")

        if self.on_start_training:
            self.on_start_training(params)

    def _on_back_click(self) -> None:
        """Délègue le retour au menu à l'application."""
        if self.on_back:
            self.on_back()

    # ──────────────────────────────────────────────────────────────────────
    # API appelée par le contrôleur d'entraînement
    # ──────────────────────────────────────────────────────────────────────

    def update_progress(self, current: int, total: int) -> None:
        """
        Met à jour la barre de progression et le label "x / N".

        Args:
            current: Épisodes joués jusqu'à présent.
            total: Total d'épisodes prévus.
        """
        if total <= 0:
            return
        percent = int((current / total) * 100)
        self.progress_var.set(percent)
        self.progress_label.config(
            text=lang_manager.get_text("pk_train_progress_label").format(current, total)
        )
        self.update_idletasks()

    def show_results(
        self,
        nb_finished: int,
        nb_crashed: int,
        total: int,
        avg_reward: float,
        elapsed_s: float,
    ) -> None:
        """
        Affiche le récapitulatif final.

        Args:
            nb_finished: Nombre d'épisodes terminés (course finie sans crash).
            nb_crashed:  Nombre d'épisodes ayant crashé contre un mur.
            total:       Nombre total d'épisodes joués.
            avg_reward:  Récompense moyenne sur la dernière fenêtre.
            elapsed_s:   Durée totale de l'entraînement en secondes.
        """
        self.progress_frame.pack_forget()
        self.results_frame.pack(pady=20, padx=60, fill="x")

        finished_pct = (nb_finished / total * 100) if total else 0.0
        crashed_pct = (nb_crashed / total * 100) if total else 0.0

        self.finished_label.config(
            text=lang_manager.get_text("pk_train_finished_pct").format(
                nb_finished, f"{finished_pct:.1f}"
            )
        )
        self.crashed_label.config(
            text=lang_manager.get_text("pk_train_crashed_pct").format(
                nb_crashed, f"{crashed_pct:.1f}"
            )
        )
        self.avg_reward_label.config(
            text=lang_manager.get_text("pk_train_avg_reward").format(f"{avg_reward:.1f}")
        )
        self.elapsed_label.config(
            text=lang_manager.get_text("pk_train_elapsed").format(f"{elapsed_s:.1f}")
        )

    # ──────────────────────────────────────────────────────────────────────
    # Multilingue
    # ──────────────────────────────────────────────────────────────────────

    def update_language(self) -> None:
        """Recharge tous les libellés depuis le LanguageManager."""
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        self.title_label.config(text=lang_manager.get_text("pk_train_title"))
        for label, key in self._row_labels:
            label.config(text=lang_manager.get_text(key))
        self.circuit_label.config(text=lang_manager.get_text("pk_train_circuit"))
        self.start_btn.config(text=lang_manager.get_text("pk_train_start"))
        self.progress_title.config(text=lang_manager.get_text("pk_train_progress"))
        self.results_title.config(text=lang_manager.get_text("pk_train_complete"))
