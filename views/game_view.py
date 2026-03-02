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
    """
    
    # === CONSTANTES DE STYLE ===
    WINDOW_TITLE = "Matchstick Game"
    CANVAS_WIDTH = 700
    CANVAS_HEIGHT = 250
    BG_COLOR = "#F5F7FA"
    MATCH_COLOR = "#C0392B"
    HEAD_COLOR = "#E74C3C"
    BTN_COLOR = "#2C3E50"
    BTN_TXT_COLOR = "white"
    FONT_TITLE = ("Helvetica", 16, "bold")
    FONT_BTN = ("Helvetica", 13)
    
    def __init__(self, master, controller) -> None:
        super().__init__(master, bg=self.BG_COLOR)
        self.master = master
        self.controller = controller
        
        lang_manager.register_observer(self)
        self._create_widgets()
        self.update_view()
    
    def _create_widgets(self) -> None:
        self.message_label = tk.Label(
            self,
            text="",
            font=self.FONT_TITLE,
            bg=self.BG_COLOR,
            pady=15
        )
        self.message_label.pack()
        
        self.canvas = tk.Canvas(
            self,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg=self.BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(pady=15)
        
        self.buttons_frame = Frame(self, bg=self.BG_COLOR)
        self.buttons_frame.pack(pady=15)
        
        self._create_action_buttons()
    
    def _create_action_buttons(self) -> None:
        for i in range(1, 4):
            # On utilise les nouvelles clés "take_1", "take_2", "take_3"
            btn_text = lang_manager.get_text(f"take_{i}")
            
            btn = tk.Button(
                self.buttons_frame,
                text=btn_text,
                font=self.FONT_BTN,
                bg=self.BTN_COLOR,
                fg=self.BTN_TXT_COLOR,
                width=10,
                padx=8,
                pady=8,
                cursor="hand2",
                relief=tk.FLAT,
                command=lambda n=i: self.controller.handle_human_move(n)
            )
            btn.pack(side=tk.LEFT, padx=10)
            
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#34495E"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.BTN_COLOR))
    
    def update_view(self) -> None:
        self.canvas.delete("all")
        nb_matches = self.controller.get_nb_matches()
        self.draw_matches(nb_matches)
        status_message = self.controller.get_status_message()
        self.message_label.config(text=status_message)
    
    def draw_matches(self, nb: int) -> None:
        if nb <= 0: return
        match_width = 14
        spacing = min(45, (self.CANVAS_WIDTH - 80) // nb)
        start_x = (self.CANVAS_WIDTH - spacing * nb) // 2 + spacing // 2
        
        for i in range(nb):
            x = start_x + i * spacing
            self.canvas.create_rectangle(
                x - 4, 60,
                x + 4, self.CANVAS_HEIGHT - 40,
                fill=self.MATCH_COLOR,
                outline=""
            )
            self.canvas.create_oval(
                x - match_width // 2, 35,
                x + match_width // 2, 65,
                fill=self.HEAD_COLOR,
                outline=""
            )
    
    def end_game(self) -> None:
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        play_again_btn = tk.Button(
            self.buttons_frame,
            text=lang_manager.get_text("play_again"),
            font=self.FONT_BTN,
            bg="#27AE60",
            fg="white",
            width=12,
            pady=10,
            command=self.controller.reset_game
        )
        play_again_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = tk.Button(
            self.buttons_frame,
            text=lang_manager.get_text("quit"),
            font=self.FONT_BTN,
            bg="#E74C3C",
            fg="white",
            width=12,
            pady=10,
            command=self.controller.quit_to_menu
        )
        quit_btn.pack(side=tk.LEFT, padx=10)
        
        self.update_view()
    
    def reset(self) -> None:
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        self._create_action_buttons()
        self.update_view()
    
    def update_language(self) -> None:
        status_message = self.controller.get_status_message()
        self.message_label.config(text=status_message)
        self.reset()