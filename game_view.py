"""
Module contenant la classe GameView — interface graphique Tkinter du jeu des allumettes.
"""
import tkinter as tk
from tkinter import Tk


class GameView(Tk):
    """
    Représente l'interface graphique du jeu des allumettes.

    Hérite de Tk pour constituer la fenêtre principale de l'application.

    Attributes:
        controller: Le contrôleur associé à cette vue.
        canvas (tk.Canvas): Zone de dessin pour les allumettes.
        message_label (tk.Label): Affiche le message d'état du jeu.
        buttons_frame (tk.Frame): Contient les boutons d'action.
    """

    # Constantes de style
    WINDOW_TITLE = "Matchstick Game"
    CANVAS_WIDTH = 600
    CANVAS_HEIGHT = 200
    BG_COLOR = "#FAFAFA"
    MATCH_COLOR = "#C0392B"
    HEAD_COLOR = "#E74C3C"
    BTN_COLOR = "#2C3E50"
    BTN_TXT_COLOR = "white"
    FONT_TITLE = ("Helvetica", 14, "bold")
    FONT_BTN = ("Helvetica", 12)

    def __init__(self, controller) -> None:
        """
        Initialise la fenêtre et les widgets de l'interface graphique.

        Args:
            controller: Le contrôleur qui gère la logique du jeu.
        """
        super().__init__()
        self.controller = controller
        self.title(self.WINDOW_TITLE)
        self.configure(bg=self.BG_COLOR)
        self.resizable(False, False)

        # Création du label d'état
        self.message_label = tk.Label(
            self,
            text="",
            font=self.FONT_TITLE,
            bg=self.BG_COLOR,
            pady=10
        )
        self.message_label.pack()

        # Canvas pour dessiner les allumettes
        self.canvas = tk.Canvas(
            self,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg=self.BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # Frame pour les boutons d'action
        self.buttons_frame = tk.Frame(self, bg=self.BG_COLOR)
        self.buttons_frame.pack(pady=10)

        self._create_action_buttons()
        self.update_view()

    def _create_action_buttons(self) -> None:
        """
        Crée les 3 boutons permettant de prendre 1, 2 ou 3 allumettes.
        """
        for i in range(1, 4):
            btn = tk.Button(
                self.buttons_frame,
                text=f"Take {i}",
                font=self.FONT_BTN,
                bg=self.BTN_COLOR,
                fg=self.BTN_TXT_COLOR,
                width=8,
                padx=6,
                pady=6,
                command=lambda n=i: self.controller.handle_human_move(n)
            )
            btn.pack(side=tk.LEFT, padx=8)

    def update_view(self) -> None:
        """
        Met à jour l'affichage : redessinne les allumettes et le message d'état.
        """
        # Rafraîchir le canvas
        self.canvas.delete("all")
        self.draw_matches(self.controller.get_nb_matches())

        # Mettre à jour le message d'état
        self.message_label.config(text=self.controller.get_status_message())

    def draw_matches(self, nb: int) -> None:
        """
        Dessine un certain nombre d'allumettes sur le canvas.

        Args:
            nb (int): Nombre d'allumettes à dessiner.
        """
        if nb <= 0:
            return

        # Calcul de l'espacement pour centrer les allumettes
        match_width = 12
        spacing = min(40, (self.CANVAS_WIDTH - 40) // nb)
        start_x = (self.CANVAS_WIDTH - spacing * nb) // 2 + spacing // 2

        for i in range(nb):
            x = start_x + i * spacing
            # Tige de l'allumette
            self.canvas.create_rectangle(
                x - 3, 50, x + 3, self.CANVAS_HEIGHT - 30,
                fill=self.MATCH_COLOR, outline=""
            )
            # Tête de l'allumette
            self.canvas.create_oval(
                x - match_width // 2, 30,
                x + match_width // 2, 55,
                fill=self.HEAD_COLOR, outline=""
            )

    def end_game(self) -> None:
        """
        Affiche la fin de partie : supprime les boutons d'action
        et les remplace par un bouton de réinitialisation.
        """
        # Supprimer tous les boutons actuels
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        # Ajouter le bouton de réinitialisation
        reset_btn = tk.Button(
            self.buttons_frame,
            text="Play Again",
            font=self.FONT_BTN,
            bg="#27AE60",
            fg="white",
            width=12,
            pady=6,
            command=self.controller.reset_game
        )
        reset_btn.pack()
        self.update_view()

    def reset(self) -> None:
        """
        Réinitialise l'affichage en remettant les 3 boutons d'action.
        """
        # Supprimer les widgets présents dans la frame
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        # Remettre les boutons d'action
        self._create_action_buttons()
        self.update_view()
