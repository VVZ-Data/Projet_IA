"""
Vue de la course du jeu Pixel Kart.

Layout :
- Header (bouton back en haut à gauche + titre + temps + tours)
- Frame circuit (gauche) qui dessine la grille et les karts
- Pour chaque kart, une frame à droite avec position/direction/vitesse/tours
  + boutons d'action (Accélérer, Freiner, Tourner, Passer)

Les karts sont visuellement distinguables :
- couleur de fond unique par kart
- une flèche directionnelle (▲ ▶ ▼ ◀)
- la première lettre du nom du kart en surimpression
"""

import tkinter as tk
from tkinter import Frame, messagebox, ttk

from language_manager import lang_manager
from games.pixel_kart.editor.frames import CircuitFrame


# Symboles directionnels affichés dans la cellule du kart
DIRECTION_SYMBOL = {
    "NORTH": "▲",
    "EAST":  "▶",
    "SOUTH": "▼",
    "WEST":  "◀",
}


class KartCircuitFrame(CircuitFrame):
    """
    Spécialisation de CircuitFrame qui affiche les karts avec une flèche
    directionnelle et la première lettre de leur nom.

    update_view(karts_info) attend une liste de dicts :
        [{"position": (r,c), "color": str, "direction": str, "name": str}, ...]
    """

    def __init__(self, container, circuit=None, rows=12, cols=20):
        super().__init__(container, circuit, rows, cols)
        self.kart_widgets = []

    def update_view(self, karts_info) -> None:
        # Effacer les anciens karts
        for widget in self.kart_widgets:
            widget.destroy()
        self.kart_widgets.clear()

        # Réafficher chaque kart
        for info in karts_info:
            r, c = info["position"]
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                continue
            symbol = DIRECTION_SYMBOL.get(info["direction"], "?")
            initial = info["name"][:1].upper() if info.get("name") else ""
            text = f"{initial}{symbol}"

            label = tk.Label(
                self,
                text=text,
                bg=info["color"],
                fg="white",
                font=("Helvetica", 9, "bold"),
                width=2,
                height=1,
                borderwidth=2,
                relief="raised",
            )
            label.grid(row=r, column=c, sticky="nsew")
            self.kart_widgets.append(label)


class KartFrame(ttk.LabelFrame):
    """
    Affiche les infos d'un kart et ses boutons d'action.
    Les boutons appellent on_action(kart_index, action).
    """

    def __init__(self, parent, title: str, kart_index: int, on_action):
        super().__init__(parent, text=title)
        self.kart_index = kart_index
        self.on_action = on_action

        self.position_label = ttk.Label(self, text="")
        self.position_label.pack(pady=2)
        self.direction_label = ttk.Label(self, text="")
        self.direction_label.pack(pady=2)
        self.speed_label = ttk.Label(self, text="")
        self.speed_label.pack(pady=2)
        self.turns_label = ttk.Label(self, text="")
        self.turns_label.pack(pady=2)

        play_frame = ttk.LabelFrame(self, text=lang_manager.get_text("pk_play"))
        play_frame.pack(padx=10, pady=10, fill="x")

        self.accel_btn = tk.Button(
            play_frame, text=lang_manager.get_text("pk_accelerate"), bg="#90EE90",
            command=lambda: self._click("ACCELERATE"))
        self.accel_btn.pack(pady=3)

        turns_row = ttk.Frame(play_frame)
        turns_row.pack(pady=3)
        self.left_btn = tk.Button(
            turns_row, text=lang_manager.get_text("pk_turn_left"), fg="blue",
            command=lambda: self._click("TURN_LEFT"))
        self.left_btn.pack(side="left", padx=2)
        self.right_btn = tk.Button(
            turns_row, text=lang_manager.get_text("pk_turn_right"), fg="blue",
            command=lambda: self._click("TURN_RIGHT"))
        self.right_btn.pack(side="left", padx=2)

        self.brake_btn = tk.Button(
            play_frame, text=lang_manager.get_text("pk_brake"), bg="#FFB6B6",
            command=lambda: self._click("BRAKE"))
        self.brake_btn.pack(pady=3)

        self.pass_btn = tk.Button(
            play_frame, text=lang_manager.get_text("pk_pass"),
            command=lambda: self._click("PASS"))
        self.pass_btn.pack(pady=3)

        self.buttons = [
            self.accel_btn, self.left_btn, self.right_btn,
            self.brake_btn, self.pass_btn,
        ]

    def _click(self, action: str) -> None:
        if self.on_action:
            self.on_action(self.kart_index, action)

    def update_kart(self, kart_dto, active: bool, controllable: bool) -> None:
        self.position_label.config(
            text=f"{lang_manager.get_text('pk_position')} : {kart_dto.position}"
        )
        self.direction_label.config(
            text=f"{lang_manager.get_text('pk_direction')} : {kart_dto.direction}"
        )
        self.speed_label.config(
            text=f"{lang_manager.get_text('pk_speed')} : {kart_dto.speed}"
        )
        self.turns_label.config(
            text=f"{lang_manager.get_text('pk_turns_done')} : {kart_dto.turns_done}"
        )

        enable = active and controllable and kart_dto.is_alive
        state = "normal" if enable else "disabled"
        for btn in self.buttons:
            btn.config(state=state)


class PixelKartRaceView(Frame):
    """
    Vue principale de la course (Frame qui s'insère dans PixelKartApp).

    Callbacks :
        on_action(kart_index, action) : appelée par les boutons des KartFrame
        on_back() : bouton "stop & retour menu" en haut à gauche
    """

    BG_COLOR = "#F5F7FA"
    TEXT_COLOR = "#2C3E50"
    KART_COLORS = ["#E74C3C", "#3498DB", "#F39C12", "#9B59B6"]  # rouge, bleu, orange, violet

    def __init__(self, master, race, on_action=None, on_back=None):
        super().__init__(master, bg=self.BG_COLOR)
        self.race = race
        self.on_action = on_action
        self.on_back = on_back

        self._end_message_shown = False
        lang_manager.register_observer(self)
        self._build_ui()

    def _build_ui(self) -> None:
        # === Header (back + titre + infos course) ===
        header = Frame(self, bg=self.BG_COLOR)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

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
            text=lang_manager.get_text("pk_race_title"),
            font=("Helvetica", 20, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.title_label.pack(side=tk.LEFT, padx=40)

        self.time_label = tk.Label(
            header, text="", font=("Helvetica", 12),
            bg=self.BG_COLOR, fg=self.TEXT_COLOR
        )
        self.time_label.pack(side=tk.LEFT, padx=20)

        self.turns_label = tk.Label(
            header, text="", font=("Helvetica", 12),
            bg=self.BG_COLOR, fg=self.TEXT_COLOR
        )
        self.turns_label.pack(side=tk.LEFT, padx=20)

        # === Body : circuit à gauche, karts à droite ===
        body = Frame(self, bg=self.BG_COLOR)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        circuit_wrap = ttk.LabelFrame(body, text="Race")
        circuit_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.circuit_frame = KartCircuitFrame(
            circuit_wrap,
            circuit=self.race.circuit.raw,
            rows=self.race.circuit.rows,
            cols=self.race.circuit.cols,
        )
        self.circuit_frame.pack(padx=5, pady=5, fill="both", expand=True)

        # Karts
        karts_wrap = Frame(body, bg=self.BG_COLOR)
        karts_wrap.pack(side=tk.LEFT, fill=tk.Y)

        self.kart_frames = []
        for idx, kart in enumerate(self.race.karts):
            color = self.KART_COLORS[idx % len(self.KART_COLORS)]
            kart.color = color  # synchroniser la couleur du modèle avec la vue
            kart_frame = KartFrame(
                karts_wrap,
                title=f"Kart {kart.name}",
                kart_index=idx,
                on_action=self.on_action,
            )
            kart_frame.pack(padx=5, pady=5, fill="x")
            self.kart_frames.append(kart_frame)

        # === Status (gagnant en bas) ===
        self.status_label = tk.Label(
            self, text="",
            font=("Helvetica", 14, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        self.status_label.pack(pady=10)

    def _back(self) -> None:
        if self.on_back:
            self.on_back()

    def update_view(self, race=None) -> None:
        """Rafraîchit toute la vue à partir de l'état de la course."""
        if race is not None:
            self.race = race
        race = self.race

        self.time_label.config(
            text=f"{lang_manager.get_text('pk_time')} : {race.time}"
        )
        self.turns_label.config(
            text=f"{lang_manager.get_text('pk_turns_to_do')} : {race.nb_turns}"
        )

        # Karts sur le circuit (avec direction)
        karts_info = [
            {
                "position": kart.position,
                "color": kart.color,
                "direction": kart.direction,
                "name": kart.name,
            }
            for kart in race.karts if kart.is_alive
        ]
        self.circuit_frame.update_view(karts_info)

        # Mise à jour des frames karts
        for idx, kart in enumerate(race.karts):
            active = (idx == race.current_kart_index) and not race.is_finished()
            controllable = not kart.is_ai
            self.kart_frames[idx].update_kart(kart.to_dto(), active, controllable)

        # Statut de fin + popup (une seule fois)
        if race.is_finished():
            winner = race.winner()
            if winner is None:
                msg = lang_manager.get_text("pk_no_winner")
            else:
                msg = lang_manager.get_text("pk_winner").format(winner.name)
            self.status_label.config(text=msg)
            if not self._end_message_shown:
                self._end_message_shown = True
                self.after(200, lambda m=msg: messagebox.showinfo(
                    lang_manager.get_text("pk_race_over_title"), m, parent=self
                ))
        else:
            self.status_label.config(text="")

    def update_language(self) -> None:
        self.back_btn.config(text="← " + lang_manager.get_text("back"))
        self.title_label.config(text=lang_manager.get_text("pk_race_title"))
        self.update_view()
