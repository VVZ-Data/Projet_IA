"""
Module contenant la vue d'entraînement de l'IA.
Permet de configurer et lancer l'entraînement avec affichage de la progression.
"""

import tkinter as tk
from tkinter import Frame, ttk
from language_manager import lang_manager


class TrainingView(Frame):
    """
    Interface d'entraînement de l'IA.
    
    Permet de :
    - Configurer les paramètres d'entraînement
    - Lancer l'entraînement avec barre de progression
    - Afficher les résultats détaillés et l'analyse
    
    Attributes:
        master: Fenêtre parente.
        on_start_training (callable): Callback pour démarrer l'entraînement.
        on_back (callable): Callback pour retourner au menu.
        params_entries (dict): Dictionnaire des champs de saisie des paramètres.
        progress_var (tk.IntVar): Variable pour la barre de progression.
        progress_bar (ttk.Progressbar): Barre de progression visuelle.
    """
    
    # Constantes de style
    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#E74C3C"
    TEXT_COLOR = "#2C3E50"
    SUCCESS_COLOR = "#27AE60"
    
    def __init__(self, master, on_start_training=None, on_back=None):
        """
        Initialise la vue d'entraînement.
        
        Args:
            master: Fenêtre parente.
            on_start_training (callable): Fonction appelée avec les paramètres
                                         (nb_games, epsilon_decay, learning_rate).
            on_back (callable): Fonction pour retourner au menu.
        """
        super().__init__(master, bg=self.BG_COLOR)
        self.master = master
        self.on_start_training = on_start_training
        self.on_back = on_back
        
        # Dictionnaire pour stocker les champs de saisie
        self.params_entries = {}
        
        # Variables pour la barre de progression
        self.progress_var = tk.IntVar(value=0)
        self.is_training = False  # Indicateur d'entraînement en cours
        
        # S'enregistrer pour les changements de langue
        lang_manager.register_observer(self)
        
        # Créer l'interface
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """
        Crée et positionne tous les widgets de la vue d'entraînement.
        
        Structure :
        - En-tête avec titre et bouton retour
        - Carte de paramètres (formulaire)
        - Zone de progression (barre + statistiques)
        - Zone de résultats (affichée après l'entraînement)
        """
        # === EN-TÊTE ===
        header_frame = Frame(self, bg=self.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 10))
        
        # Bouton retour
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
        
        # Titre
        self.title_label = tk.Label(
            header_frame,
            text=lang_manager.get_text("training_title"),
            font=("Helvetica", 28, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.title_label.pack(side=tk.LEFT, padx=100)
        
        # === CARTE DE PARAMÈTRES ===
        self._create_params_card()
        
        # === ZONE DE PROGRESSION ===
        # Créée mais initialement cachée
        self._create_progress_section()
        
        # === ZONE DE RÉSULTATS ===
        # Créée mais initialement cachée
        self._create_results_section()
    
    def _create_params_card(self) -> None:
        """
        Crée la carte contenant le formulaire de paramètres d'entraînement.
        
        Paramètres configurables :
        - Nombre de parties (par défaut : 100 000)
        - Diminution epsilon tous les X parties (par défaut : 5000)
        - Taux d'apprentissage (par défaut : 0.3)
        """
        # Frame principale de la carte
        self.params_card = Frame(
            self,
            bg=self.CARD_BG,
            relief=tk.RAISED,
            bd=3
        )
        self.params_card.pack(fill=tk.BOTH, padx=60, pady=(20, 10))
        
        # Titre de la section
        title = tk.Label(
            self.params_card,
            text="⚙️ Configuration",
            font=("Helvetica", 20, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR
        )
        title.pack(pady=(20, 15))
        
        # Frame pour le formulaire
        form_frame = Frame(self.params_card, bg=self.CARD_BG)
        form_frame.pack(pady=(10, 20), padx=40)
        
        # === CHAMPS DU FORMULAIRE ===
        # Liste des paramètres : (clé, label, valeur par défaut)
        params = [
            ("nb_games", lang_manager.get_text("nb_games"), "100000"),
            ("epsilon_decay", lang_manager.get_text("epsilon_decay"), "5000"),
            ("learning_rate", lang_manager.get_text("learning_rate"), "0.3")
        ]
        
        # Créer chaque ligne du formulaire
        for i, (key, label_text, default_value) in enumerate(params):
            # Label du paramètre
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Helvetica", 13),
                bg=self.CARD_BG,
                fg=self.TEXT_COLOR,
                anchor="w"
            )
            label.grid(row=i, column=0, sticky="w", pady=10, padx=(0, 20))
            
            # Champ de saisie
            entry = tk.Entry(
                form_frame,
                font=("Helvetica", 13),
                width=15,
                relief=tk.SOLID,
                bd=1
            )
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, pady=10)
            
            # Stocker l'entry pour récupération ultérieure
            self.params_entries[key] = entry
        
        # === BOUTON DE LANCEMENT ===
        self.start_btn = tk.Button(
            self.params_card,
            text=lang_manager.get_text("start_training"),
            font=("Helvetica", 15, "bold"),
            bg=self.PRIMARY_COLOR,
            fg="white",
            width=25,
            pady=12,
            cursor="hand2",
            relief=tk.FLAT,
            command=self._on_start_click
        )
        self.start_btn.pack(pady=(10, 25))
        
        # Effet hover
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#C0392B"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg=self.PRIMARY_COLOR))
    
    def _create_progress_section(self) -> None:
        """
        Crée la section affichant la progression de l'entraînement.
        
        Contient :
        - Titre "Training Progress"
        - Barre de progression
        - Label avec le nombre de parties jouées
        """
        # Frame de progression (initialement cachée)
        self.progress_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        
        # Titre
        self.progress_title = tk.Label(
            self.progress_frame,
            text=lang_manager.get_text("training_progress"),
            font=("Helvetica", 18, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR
        )
        self.progress_title.pack(pady=(15, 10))
        
        # Barre de progression
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", thickness=30)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=500,
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(pady=15)
        
        # Label d'état (ex: "Parties jouées : 5000/100000")
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Helvetica", 12),
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR
        )
        self.progress_label.pack(pady=(5, 15))
    
    def _create_results_section(self) -> None:
        """
        Crée la section affichant les résultats finaux de l'entraînement.
        
        Contient :
        - Titre "Training Complete!"
        - Statistiques des deux IA (victoires, pourcentages)
        - Analyse textuelle des résultats
        - Bouton pour sauvegarder les résultats
        """
        # Frame de résultats (initialement cachée)
        self.results_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        
        # Titre
        self.results_title = tk.Label(
            self.results_frame,
            text="✅ " + lang_manager.get_text("training_complete"),
            font=("Helvetica", 20, "bold"),
            bg=self.CARD_BG,
            fg=self.SUCCESS_COLOR
        )
        self.results_title.pack(pady=(20, 15))
        
        # Frame pour les statistiques
        stats_frame = Frame(self.results_frame, bg=self.CARD_BG)
        stats_frame.pack(pady=10)
        
        # Labels pour les statistiques (seront remplis plus tard)
        self.ai1_stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Helvetica", 14),
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR
        )
        self.ai1_stats_label.pack(pady=5)
        
        self.ai2_stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Helvetica", 14),
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR
        )
        self.ai2_stats_label.pack(pady=5)
        
        # Label d'analyse
        self.analysis_label = tk.Label(
            self.results_frame,
            text="",
            font=("Helvetica", 12, "italic"),
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR,
            wraplength=600,  # Retour à la ligne automatique
            justify=tk.CENTER
        )
        self.analysis_label.pack(pady=20)
        
        # Bouton pour sauvegarder (optionnel)
        save_btn = tk.Button(
            self.results_frame,
            text=lang_manager.get_text("save_results"),
            font=("Helvetica", 12),
            bg=self.SUCCESS_COLOR,
            fg="white",
            width=20,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        )
        save_btn.pack(pady=(10, 20))
    
    def _on_start_click(self) -> None:
        """
        Gère le clic sur le bouton de démarrage de l'entraînement.
        
        Récupère les valeurs des paramètres et appelle le callback.
        """
        # Récupérer les valeurs saisies
        try:
            nb_games = int(self.params_entries["nb_games"].get())
            epsilon_decay = int(self.params_entries["epsilon_decay"].get())
            learning_rate = float(self.params_entries["learning_rate"].get())
        except ValueError:
            # En cas d'erreur de saisie, ne rien faire
            # (dans une vraie app, afficher un message d'erreur)
            return
        
        # Marquer que l'entraînement est en cours
        self.is_training = True
        
        # Masquer la carte de paramètres et afficher la progression
        self.params_card.pack_forget()
        self.progress_frame.pack(fill=tk.BOTH, padx=60, pady=10)
        
        # Réinitialiser la barre de progression
        self.progress_var.set(0)
        
        # Appeler le callback si défini
        if self.on_start_training:
            self.on_start_training(nb_games, epsilon_decay, learning_rate)
    
    def update_progress(self, current: int, total: int) -> None:
        """
        Met à jour la barre de progression pendant l'entraînement.
        
        Args:
            current (int): Nombre de parties jouées.
            total (int): Nombre total de parties.
        """
        # Calculer le pourcentage
        percentage = int((current / total) * 100)
        self.progress_var.set(percentage)
        
        # Mettre à jour le label
        text = lang_manager.get_text("games_played").format(current, total)
        self.progress_label.config(text=text)
        
        # Forcer la mise à jour de l'interface
        self.update_idletasks()
    
    def show_results(self, ai1_wins: int, ai2_wins: int, total_games: int) -> None:
        """
        Affiche les résultats finaux de l'entraînement.
        
        Args:
            ai1_wins (int): Nombre de victoires de l'IA 1.
            ai2_wins (int): Nombre de victoires de l'IA 2.
            total_games (int): Nombre total de parties jouées.
        """
        # Marquer la fin de l'entraînement
        self.is_training = False
        
        # Masquer la barre de progression et afficher les résultats
        self.progress_frame.pack_forget()
        self.results_frame.pack(fill=tk.BOTH, padx=60, pady=10)
        
        # Calculer les pourcentages
        ai1_percent = (ai1_wins / total_games) * 100
        ai2_percent = (ai2_wins / total_games) * 100
        
        # Mettre à jour les statistiques
        ai1_text = lang_manager.get_text("ai1_wins").format(ai1_wins, f"{ai1_percent:.1f}")
        ai2_text = lang_manager.get_text("ai2_wins").format(ai2_wins, f"{ai2_percent:.1f}")
        
        self.ai1_stats_label.config(text=ai1_text)
        self.ai2_stats_label.config(text=ai2_text)
        
        # Générer l'analyse
        analysis = self._generate_analysis(ai1_percent, ai2_percent)
        self.analysis_label.config(text=lang_manager.get_text("analysis").format(analysis))
    
    def _generate_analysis(self, ai1_percent: float, ai2_percent: float) -> str:
        """
        Génère une analyse textuelle des résultats.
        
        Args:
            ai1_percent (float): Pourcentage de victoires de l'IA 1.
            ai2_percent (float): Pourcentage de victoires de l'IA 2.
        
        Returns:
            str: Texte d'analyse traduit.
        """
        # Déterminer le type d'analyse selon les résultats
        if abs(ai1_percent - ai2_percent) < 5:
            # Résultats équilibrés (différence < 5%)
            return lang_manager.get_text("balanced")
        elif ai1_percent > ai2_percent:
            # IA 1 domine
            return lang_manager.get_text("ai1_dominates").format(f"{ai1_percent:.1f}")
        else:
            # IA 2 domine
            return lang_manager.get_text("ai2_dominates").format(f"{ai2_percent:.1f}")
    
    def _on_back_click(self) -> None:
        """Gère le clic sur le bouton retour."""
        if self.on_back:
            self.on_back()
    
    def update_language(self) -> None:
        """
        Met à jour tous les textes suite à un changement de langue.
        """
        # Mettre à jour le titre
        self.title_label.config(text=lang_manager.get_text("training_title"))
        
        # Mettre à jour le bouton retour
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        
        # Mettre à jour les labels du formulaire
        # (récréer complètement serait plus propre, mais plus complexe)
        self.start_btn.config(text=lang_manager.get_text("start_training"))
