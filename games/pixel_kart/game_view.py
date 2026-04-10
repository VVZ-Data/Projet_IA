"""
Vues Tkinter du jeu Pixel Kart.

Contient :
- MenuView : fenêtre principale (Tk) pour configurer la partie
- RaceView : fenêtre principale (Tk) qui affiche la course
- KartFrame : sous-frame qui affiche l'état d'un kart et les boutons d'action
"""

import tkinter as tk
from tkinter import ttk

from games.pixel_kart.editor.map_editor import CircuitEditor
import games.pixel_kart.editor.map_dao as map_dao
from games.pixel_kart.editor.frames import CircuitRaceFrame


# === MENU PRINCIPAL ===

class MenuView(tk.Tk):
    """
    Fenêtre de configuration de la partie.

    L'utilisateur choisit :
    - les joueurs (humain et/ou IA)
    - le circuit
    - le nombre de tours
    Puis lance la partie via le bouton Play.
    """

    def __init__(self, on_play, on_open_editor):
        super().__init__()
        self.title("Pixel Kart - Main Menu")
        self.geometry("400x420")
        self.resizable(False, False)

        self.on_play = on_play
        self.on_open_editor = on_open_editor

        # Variables liées aux widgets
        self.human_var = tk.BooleanVar(value=True)
        self.ai_var = tk.BooleanVar(value=False)
        self.circuit_var = tk.StringVar()
        self.turns_var = tk.StringVar(value="3")

        self._build_ui()
        self._refresh_circuits()

    def _build_ui(self) -> None:
        settings = ttk.LabelFrame(self, text="Settings")
        settings.pack(padx=15, pady=15, fill="both", expand=True)

        # --- Joueurs ---
        players = ttk.LabelFrame(settings, text="Players")
        players.pack(padx=10, pady=10, fill="x")
        ttk.Checkbutton(players, text="Human", variable=self.human_var).pack(side="left", padx=10, pady=5)
        ttk.Checkbutton(players, text="AI", variable=self.ai_var).pack(side="left", padx=10, pady=5)

        # --- Circuit ---
        circuit = ttk.LabelFrame(settings, text="Circuit")
        circuit.pack(padx=10, pady=10, fill="x")

        row1 = ttk.Frame(circuit)
        row1.pack(fill="x", pady=5)
        ttk.Label(row1, text="Choose Circuit :").pack(side="left", padx=5)
        self.circuit_dropdown = ttk.OptionMenu(row1, self.circuit_var, "")
        self.circuit_dropdown.pack(side="right", padx=5)

        row2 = ttk.Frame(circuit)
        row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="Number of turns :").pack(side="left", padx=5)
        ttk.Entry(row2, textvariable=self.turns_var, width=5).pack(side="right", padx=5)

        ttk.Button(
            circuit,
            text="Open circuit editor",
            command=self._open_editor
        ).pack(fill="x", padx=5, pady=5)

        # --- Bouton Play ---
        play_btn = tk.Button(
            self,
            text="Play",
            bg="blue",
            fg="white",
            font=("Helvetica", 14, "bold"),
            command=self._play
        )
        play_btn.pack(padx=15, pady=10, fill="x")

    def _refresh_circuits(self) -> None:
        """Recharge la liste des circuits depuis le DAO."""
        circuits = map_dao.get_all()
        names = list(circuits.keys())
        menu = self.circuit_dropdown["menu"]
        menu.delete(0, "end")
        for name in names:
            menu.add_command(
                label=name,
                command=tk._setit(self.circuit_var, name)
            )
        if names:
            self.circuit_var.set(names[0])

    def _open_editor(self) -> None:
        """Ouvre l'éditeur de circuit en tant que Toplevel."""
        editor = CircuitEditor(self, callback=self._on_editor_chose)
        # Au cas où l'utilisateur sauverait un nouveau circuit
        editor.bind("<Destroy>", lambda e: self._refresh_circuits())

    def _on_editor_chose(self, circuit_name: str) -> None:
        """Callback du Chose de l'éditeur : sélectionne le circuit choisi."""
        self._refresh_circuits()
        if circuit_name:
            self.circuit_var.set(circuit_name)

    def _play(self) -> None:
        """Valide le formulaire et appelle le callback on_play."""
        try:
            nb_turns = int(self.turns_var.get())
        except ValueError:
            nb_turns = 3
        config = {
            "human": self.human_var.get(),
            "ai": self.ai_var.get(),
            "circuit": self.circuit_var.get(),
            "nb_turns": max(1, nb_turns),
        }
        if not config["human"] and not config["ai"]:
            return  # rien à faire si aucun joueur sélectionné
        if not config["circuit"]:
            return
        self.on_play(config)


# === FRAME D'UN KART ===

class KartFrame(ttk.LabelFrame):
    """
    Affiche les infos d'un kart et ses boutons d'action.

    Les boutons appellent le callback `on_action(kart_index, action)`
    fourni par le contrôleur.
    """

    def __init__(self, parent, title: str, border_color: str,
                 kart_index: int, on_action):
        super().__init__(parent, text=title)
        self.kart_index = kart_index
        self.on_action = on_action
        self.border_color = border_color

        self.position_label = ttk.Label(self, text="Position : (0, 0)")
        self.position_label.pack(pady=2)
        self.direction_label = ttk.Label(self, text="Direction : EAST")
        self.direction_label.pack(pady=2)
        self.speed_label = ttk.Label(self, text="Speed : 0")
        self.speed_label.pack(pady=2)
        self.turns_label = ttk.Label(self, text="Turns done : 0")
        self.turns_label.pack(pady=2)

        play_frame = ttk.LabelFrame(self, text="Play")
        play_frame.pack(padx=10, pady=10, fill="x")

        self.accel_btn = tk.Button(
            play_frame, text="Accelerate", bg="#90EE90",
            command=lambda: self._click("ACCELERATE"))
        self.accel_btn.pack(pady=3)

        turns_row = ttk.Frame(play_frame)
        turns_row.pack(pady=3)
        self.left_btn = tk.Button(
            turns_row, text="Turn Left", fg="blue",
            command=lambda: self._click("TURN_LEFT"))
        self.left_btn.pack(side="left", padx=2)
        self.right_btn = tk.Button(
            turns_row, text="Turn Right", fg="blue",
            command=lambda: self._click("TURN_RIGHT"))
        self.right_btn.pack(side="left", padx=2)

        self.brake_btn = tk.Button(
            play_frame, text="Brake", bg="#FFB6B6",
            command=lambda: self._click("BRAKE"))
        self.brake_btn.pack(pady=3)

        self.pass_btn = tk.Button(
            play_frame, text="Pass",
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
        """
        Met à jour les labels et l'état des boutons.
        - active : c'est le tour de ce kart
        - controllable : ce kart est humain (sinon on désactive les boutons)
        """
        self.position_label.config(text=f"Position : {kart_dto.position}")
        self.direction_label.config(text=f"Direction : {kart_dto.direction}")
        self.speed_label.config(text=f"Speed : {kart_dto.speed}")
        self.turns_label.config(text=f"Turns done : {kart_dto.turns_done}")

        enable = active and controllable and kart_dto.is_alive
        state = "normal" if enable else "disabled"
        for btn in self.buttons:
            btn.config(state=state)


# === FENÊTRE DE COURSE ===

class RaceView(tk.Tk):
    """
    Fenêtre principale de la course.

    Affiche le circuit (à gauche) et un KartFrame par kart (à droite).
    """

    def __init__(self, race, on_action):
        super().__init__()
        self.title("Pixel Kart - Race")
        self.geometry("1400x650")
        self.on_action = on_action

        # === Frame circuit (gauche) ===
        race_frame = ttk.LabelFrame(self, text="Race")
        race_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        info_frame = ttk.Frame(race_frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        self.time_label = ttk.Label(info_frame, text="Time: 0", font=("Helvetica", 12))
        self.time_label.pack(side="left", padx=20)
        self.turns_label = ttk.Label(info_frame, text="Turns to do: 0", font=("Helvetica", 12))
        self.turns_label.pack(side="right", padx=20)

        self.circuit_frame = CircuitRaceFrame(
            race_frame,
            circuit=race.circuit.raw,
            rows=race.circuit.rows,
            cols=race.circuit.cols,
        )
        self.circuit_frame.pack(padx=5, pady=5, fill="both", expand=True)

        # === Frames karts (droite) ===
        self.kart_frames = []
        colors = ["red", "blue"]
        for idx, kart in enumerate(race.karts):
            color = colors[idx % len(colors)]
            kart_frame = KartFrame(
                self,
                title=f"Kart {kart.name}",
                border_color=color,
                kart_index=idx,
                on_action=self.on_action,
            )
            kart_frame.pack(side="left", padx=10, pady=10, fill="y")
            self.kart_frames.append(kart_frame)

        self.status_label = ttk.Label(self, text="", font=("Helvetica", 14, "bold"))
        self.status_label.pack(side="bottom", pady=5)

    def update_view(self, race) -> None:
        """Rafraîchit toute la vue à partir de l'état de la course."""
        self.time_label.config(text=f"Time: {race.time}")
        self.turns_label.config(text=f"Turns to do: {race.nb_turns}")

        # Mettre à jour la position des karts sur le circuit
        karts_dict = {
            kart.position: kart.color
            for kart in race.karts
            if kart.is_alive
        }
        self.circuit_frame.update_view(karts_dict)

        # Mettre à jour chaque KartFrame
        for idx, kart in enumerate(race.karts):
            active = (idx == race.current_kart_index) and not race.is_finished()
            controllable = not kart.is_ai
            self.kart_frames[idx].update_kart(kart.to_dto(), active, controllable)

        # Statut final
        if race.is_finished():
            winner = race.winner()
            if winner is None:
                self.status_label.config(text="No winner — all karts crashed.")
            else:
                self.status_label.config(text=f"🏆 {winner.name} wins!")
