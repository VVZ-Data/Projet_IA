"""
Module contenant la vue d'entraînement de l'IA.
"""

import tkinter as tk
from tkinter import Frame, ttk
from language_manager import lang_manager


class TrainingView(Frame):
    """
    Interface d'entraînement de l'IA.
    """
    
    BG_COLOR = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#E74C3C"
    TEXT_COLOR = "#2C3E50"
    SUCCESS_COLOR = "#27AE60"
    
    def __init__(self, master, ai_target="ai1", on_start_training=None, on_back=None):
        super().__init__(master, bg=self.BG_COLOR)
        self.ai_target = ai_target
        self.on_start_training = on_start_training
        self.on_back = on_back
        
        self.params_entries = {}
        self.progress_var = tk.IntVar(value=0)
        
        lang_manager.register_observer(self)
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        header_frame = Frame(self, bg=self.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 10))
        
        self.back_btn = tk.Button(
            header_frame, text="← " + lang_manager.get_text("back"), font=("Helvetica", 12),
            bg=self.BG_COLOR, fg=self.TEXT_COLOR, relief=tk.FLAT, command=self.on_back
        )
        self.back_btn.pack(side=tk.LEFT)
        
        target_name = "IA 1" if self.ai_target == "ai1" else "IA 2"
        self.title_label = tk.Label(
            header_frame, text=lang_manager.get_text("training_title").format(target_name),
            font=("Helvetica", 28, "bold"), bg=self.BG_COLOR, fg=self.TEXT_COLOR
        )
        self.title_label.pack(side=tk.LEFT, padx=100)
        
        self._create_params_card()
        self._create_progress_section()
        self._create_results_section()
    
    def _create_params_card(self) -> None:
        self.params_card = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        self.params_card.pack(fill=tk.BOTH, padx=60, pady=20)
        
        form_frame = Frame(self.params_card, bg=self.CARD_BG)
        form_frame.pack(pady=20, padx=40)
        
        params = [
            ("nb_games", lang_manager.get_text("nb_games"), "100000"),
            ("epsilon_decay", lang_manager.get_text("epsilon_decay"), "5000"),
            ("learning_rate", lang_manager.get_text("learning_rate"), "0.3")
        ]
        
        for i, (key, label_text, default_value) in enumerate(params):
            tk.Label(form_frame, text=label_text, font=("Helvetica", 12), bg=self.CARD_BG).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(form_frame, font=("Helvetica", 12), width=10)
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.params_entries[key] = entry
            
        tk.Label(form_frame, text=lang_manager.get_text("opponent"), font=("Helvetica", 12), bg=self.CARD_BG).grid(row=3, column=0, sticky="w", pady=10)
        self.opponent_var = tk.StringVar(value="other_ai")
        opp_name = "IA 2" if self.ai_target == "ai1" else "IA 1"
        tk.Radiobutton(form_frame, text=opp_name, variable=self.opponent_var, value="other_ai", bg=self.CARD_BG).grid(row=3, column=1, sticky="w")
        tk.Radiobutton(form_frame, text="Random", variable=self.opponent_var, value="random", bg=self.CARD_BG).grid(row=4, column=1, sticky="w")

        self.start_btn = tk.Button(
            self.params_card, text=lang_manager.get_text("start_training"), font=("Helvetica", 14, "bold"),
            bg=self.PRIMARY_COLOR, fg="white", command=self._on_start_click
        )
        self.start_btn.pack(pady=20)
    
    def _create_progress_section(self) -> None:
        self.progress_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(pady=20, padx=20)
        self.progress_label = tk.Label(self.progress_frame, text="", bg=self.CARD_BG)
        self.progress_label.pack(pady=10)

    def _create_results_section(self) -> None:
        self.results_frame = Frame(self, bg=self.CARD_BG, relief=tk.RAISED, bd=3)
        tk.Label(self.results_frame, text=lang_manager.get_text("training_complete"), font=("Helvetica", 16, "bold"), fg=self.SUCCESS_COLOR, bg=self.CARD_BG).pack(pady=10)
        
        self.ai_stats_label = tk.Label(self.results_frame, text="", bg=self.CARD_BG)
        self.ai_stats_label.pack()
        self.opp_stats_label = tk.Label(self.results_frame, text="", bg=self.CARD_BG)
        self.opp_stats_label.pack()
        
        self.analysis_label = tk.Label(self.results_frame, text="", font=("Helvetica", 10, "italic"), bg=self.CARD_BG, wraplength=600)
        self.analysis_label.pack(pady=10)
        
        self.save_btn = tk.Button(
            self.results_frame, text=lang_manager.get_text("save_results"),
            bg=self.SUCCESS_COLOR, fg="white", font=("Helvetica", 12, "bold")
        )
        self.save_btn.pack(pady=10)

    def _on_start_click(self) -> None:
        try:
            nb = int(self.params_entries["nb_games"].get())
            dec = int(self.params_entries["epsilon_decay"].get())
            lr = float(self.params_entries["learning_rate"].get())
            opp = self.opponent_var.get()
        except: return
        
        self.params_card.pack_forget()
        self.progress_frame.pack(pady=20)
        if self.on_start_training:
            self.on_start_training(nb, dec, lr, opp)

    def update_progress(self, current: int, total: int) -> None:
        self.progress_var.set(int((current / total) * 100))
        self.progress_label.config(text=lang_manager.get_text("games_played").format(current, total))
        self.update_idletasks()

    def show_results(self, w_ai, w_opp, total, on_save_callback):
        self.progress_frame.pack_forget()
        self.results_frame.pack(pady=20)
        
        p_ai, p_opp = (w_ai/total)*100, (w_opp/total)*100
        target_name = "IA 1" if self.ai_target == "ai1" else "IA 2"
        
        self.ai_stats_label.config(text=lang_manager.get_text("ai_wins").format(target_name, w_ai, f"{p_ai:.1f}"))
        self.opp_stats_label.config(text=lang_manager.get_text("opp_wins").format(w_opp, f"{p_opp:.1f}"))
        
        analysis = lang_manager.get_text("balanced")
        if p_ai > p_opp + 5: analysis = lang_manager.get_text("ai_dominates").format(target_name, f"{p_ai:.1f}")
        elif p_opp > p_ai + 5: analysis = lang_manager.get_text("opp_dominates").format(f"{p_opp:.1f}")
        self.analysis_label.config(text=lang_manager.get_text("analysis").format(analysis))
        
        self.save_btn.config(command=on_save_callback)

    def update_language(self) -> None:
        target_name = "IA 1" if self.ai_target == "ai1" else "IA 2"
        self.title_label.config(text=lang_manager.get_text("training_title").format(target_name))
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        self.start_btn.config(text=lang_manager.get_text("start_training"))
        self.save_btn.config(text=lang_manager.get_text("save_results"))