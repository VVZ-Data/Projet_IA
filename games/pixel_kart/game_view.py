import tkinter as tk
from tkinter import ttk
from .dao.race_dao import CellType, Direction

class RaceView: # Note: On peut aussi ne pas hériter de Toplevel si on utilise la root directement
    def __init__(self, root, state_dto, action_callback):
        self.root = root
        self.root.title("Pixel Kart - Race")
        self.action_callback = action_callback

        # --- INITIALISATION DES COMPOSANTS ---
        self._setup_ui(state_dto)
        
        # --- PREMIER DESSIN ---
        # Très important : on force l'affichage dès l'init
        self.update_display(state_dto)

    def _setup_ui(self, state):
        # Frame principale qui contient TOUT
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True) # <-- CRUCIAL

        # Zone Circuit
        self.canvas_frame = tk.Frame(self.main_container)
        self.canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", 
                               width=state.circuit.width * 20, 
                               height=state.circuit.height * 20)
        self.canvas.pack()

        # Zone Joueurs
        self.side_bar = tk.Frame(self.main_container)
        self.side_bar.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

    def update_display(self, state):
        # Update Info générale
        self.info_label.config(text=f"Temps: {state.current_turn} | Tours à faire: {state.total_laps}")
        
        # Redessiner Circuit
        cs = 20 # Taille cellule
        self.canvas.config(width=state.circuit.width*cs, height=state.circuit.height*cs)
        self.canvas.delete("all")
        
        for y, row in enumerate(state.circuit.grid):
            for x, cell in enumerate(row):
                self.canvas.create_rectangle(x*cs, y*cs, (x+1)*cs, (y+1)*cs, 
                                           fill=self.colors.get(cell, "white"), outline="black")
        
        # Dessiner Karts
        for i, kart in enumerate(state.karts):
            if not kart.is_crashed:
                kx, ky = kart.position
                self.canvas.create_oval(kx*cs+2, ky*cs+2, (kx+1)*cs-2, (ky+1)*cs-2, 
                                      fill=self.kart_colors[i%4], outline="white")

        # Update Panneaux
        for i, kart in enumerate(state.karts):
            w = self.player_widgets[i]
            status = "CRASHED" if kart.is_crashed else ("FINI" if kart.is_finished else "EN COURSE")
            w["stats"].config(text=f"Pos: {kart.position}\nDir: {kart.direction.name}\nVit: {kart.speed}\nTours: {kart.laps_completed}/{state.total_laps}\nEtat: {status}")
            
            # Griser boutons si pas son tour ou pas humain
            is_active = (state.current_kart_index == i and not state.is_race_over and not kart.is_finished)
            for b in w["btns"].values():
                b.config(state=tk.NORMAL if (is_active and not hasattr(state.karts[i], 'epsilon')) else tk.DISABLED)