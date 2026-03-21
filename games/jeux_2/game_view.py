"""
Vue principale du jeu Cubee (Tkinter).
Responsable uniquement de l'affichage — aucune logique métier ici.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, List, Optional, Tuple


class GameView(tk.Tk):
    """
    Interface graphique Tkinter du jeu Cubee.

    Affiche le plateau (Canvas), les scores, l'indicateur de tour,
    les boutons de contrôle (New Game) et les flèches directionnelles.
    Toutes les interactions utilisateur sont déléguées au contrôleur.
    """

    # ── Palette de couleurs ──────────────────────────────────────────────────
    COLOR_BG          = "#1A1A2E"   # Fond général
    COLOR_PANEL       = "#16213E"   # Fond des panneaux
    COLOR_EMPTY       = "#E8E8F0"   # Case vide
    COLOR_GRID        = "#0F3460"   # Bordure du canvas
    COLOR_P1          = "#9B59B6"   # Violet — Joueur 1 (cases possédées)
    COLOR_P1_CURRENT  = "#6C3483"   # Violet foncé — position courante J1
    COLOR_P2          = "#00B4D8"   # Cyan  — Joueur 2 (cases possédées)
    COLOR_P2_CURRENT  = "#0077B6"   # Bleu foncé — position courante J2
    COLOR_TEXT        = "#EAEAEA"   # Texte clair
    COLOR_SUBTEXT     = "#7F8C8D"   # Texte secondaire
    COLOR_BTN_NEW     = "#2ECC71"   # Vert  — bouton New Game
    COLOR_BTN_ARROW   = "#2C3E50"   # Gris foncé — flèches de direction

    # ── Dimensions ───────────────────────────────────────────────────────────
    CELL_SIZE    = 80   # Taille d'une case en pixels
    CELL_PADDING = 3    # Espacement entre les cases
    EMOJI_P1     = "😊"
    EMOJI_P2     = "😞"

    def __init__(self, controller) -> None:
        """
        Initialise la fenêtre principale et construit l'interface.

        Args:
            controller: Référence vers le GameController.
        """
        super().__init__()
        self.controller = controller
        self.title("Cubee — Territory Game")
        self.configure(bg=self.COLOR_BG)
        self.resizable(False, False)

        self._build_ui()
        self._bind_keys()

    # ──────────────────────────────────────────────────────────────────────────
    # Construction de l'interface
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Construit l'ensemble des widgets de la fenêtre."""
        self._build_header()
        self._build_board_canvas()
        self._build_arrow_pad()
        self._build_control_buttons()
        self._build_status_bar()

    def _build_header(self) -> None:
        """Crée l'en-tête : titre + panneau des scores."""
        # ── Titre ──────────────────────────────────────────────────────
        title_lbl = tk.Label(
            self, text="CUBEE",
            font=("Helvetica", 28, "bold"),
            bg=self.COLOR_BG, fg=self.COLOR_TEXT
        )
        title_lbl.pack(pady=(15, 5))

        subtitle_lbl = tk.Label(
            self, text="Territory Capture Game",
            font=("Helvetica", 10),
            bg=self.COLOR_BG, fg=self.COLOR_SUBTEXT
        )
        subtitle_lbl.pack(pady=(0, 10))

        # ── Panneau des scores ─────────────────────────────────────────
        score_bar = tk.Frame(self, bg=self.COLOR_BG)
        score_bar.pack(padx=20, fill=tk.X)

        # Score Joueur 1
        self.p1_panel = tk.Frame(score_bar, bg=self.COLOR_P1, padx=20, pady=8)
        self.p1_panel.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.p1_name_lbl = tk.Label(
            self.p1_panel, text="Player 1",
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_P1, fg="white"
        )
        self.p1_name_lbl.pack()

        self.p1_score_lbl = tk.Label(
            self.p1_panel, text="0",
            font=("Helvetica", 22, "bold"),
            bg=self.COLOR_P1, fg="white"
        )
        self.p1_score_lbl.pack()

        # Indicateur de tour (flèche centrale)
        self.turn_indicator = tk.Label(
            score_bar, text="▶",
            font=("Helvetica", 20, "bold"),
            bg=self.COLOR_BG, fg=self.COLOR_P1
        )
        self.turn_indicator.pack(side=tk.LEFT, padx=10)

        # Score Joueur 2
        self.p2_panel = tk.Frame(score_bar, bg=self.COLOR_P2, padx=20, pady=8)
        self.p2_panel.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        self.p2_name_lbl = tk.Label(
            self.p2_panel, text="Player 2",
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_P2, fg="white"
        )
        self.p2_name_lbl.pack()

        self.p2_score_lbl = tk.Label(
            self.p2_panel, text="0",
            font=("Helvetica", 22, "bold"),
            bg=self.COLOR_P2, fg="white"
        )
        self.p2_score_lbl.pack()

    def _build_board_canvas(self) -> None:
        """Crée le Canvas qui accueille le plateau de jeu."""
        board_frame = tk.Frame(self, bg=self.COLOR_GRID, bd=2, relief=tk.RIDGE)
        board_frame.pack(padx=20, pady=15)

        initial_size = 5 * self.CELL_SIZE + 2 * self.CELL_PADDING

        self.canvas = tk.Canvas(
            board_frame,
            width=initial_size,
            height=initial_size,
            bg=self.COLOR_GRID,
            highlightthickness=0
        )
        self.canvas.pack()

    def _build_arrow_pad(self) -> None:
        """
        Crée le pavé directionnel (↑ ← ↓ →) pour jouer sans clavier.

        Pratique pour les démos ou les plateformes sans raccourcis clavier.
        """
        pad_frame = tk.Frame(self, bg=self.COLOR_BG)
        pad_frame.pack(pady=(0, 8))

        btn_cfg = dict(
            font=("Helvetica", 14, "bold"),
            bg=self.COLOR_BTN_ARROW, fg=self.COLOR_TEXT,
            width=3, height=1, relief=tk.FLAT, cursor="hand2",
            activebackground="#3D5A80", activeforeground="white"
        )

        top_row = tk.Frame(pad_frame, bg=self.COLOR_BG)
        top_row.pack()
        tk.Button(top_row, text="↑", **btn_cfg,
                  command=lambda: self.controller.handle_move("up")).pack(padx=2, pady=2)

        mid_row = tk.Frame(pad_frame, bg=self.COLOR_BG)
        mid_row.pack()
        tk.Button(mid_row, text="←", **btn_cfg,
                  command=lambda: self.controller.handle_move("left")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(mid_row, text="↓", **btn_cfg,
                  command=lambda: self.controller.handle_move("down")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(mid_row, text="→", **btn_cfg,
                  command=lambda: self.controller.handle_move("right")).pack(side=tk.LEFT, padx=2, pady=2)

    def _build_control_buttons(self) -> None:
        """Crée les boutons de contrôle de la partie (New Game)."""
        ctrl_frame = tk.Frame(self, bg=self.COLOR_BG)
        ctrl_frame.pack(pady=8)

        self.new_game_btn = tk.Button(
            ctrl_frame,
            text="🔄  New Game",
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_BTN_NEW, fg="white",
            padx=18, pady=6,
            relief=tk.FLAT, cursor="hand2",
            activebackground="#27AE60", activeforeground="white",
            command=self.controller.handle_new_game
        )
        self.new_game_btn.pack(side=tk.LEFT, padx=8)

    def _build_status_bar(self) -> None:
        """Crée la barre de statut en bas de la fenêtre."""
        self.status_lbl = tk.Label(
            self,
            text="Utilisez les flèches du clavier ou les boutons pour vous déplacer.",
            font=("Helvetica", 8),
            bg=self.COLOR_BG, fg=self.COLOR_SUBTEXT
        )
        self.status_lbl.pack(pady=(0, 12))

    # ──────────────────────────────────────────────────────────────────────────
    # Raccourcis clavier
    # ──────────────────────────────────────────────────────────────────────────

    def _bind_keys(self) -> None:
        """Associe les touches du clavier aux actions du contrôleur."""
        self.bind("<Up>",        lambda _e: self.controller.handle_move("up"))
        self.bind("<Down>",      lambda _e: self.controller.handle_move("down"))
        self.bind("<Left>",      lambda _e: self.controller.handle_move("left"))
        self.bind("<Right>",     lambda _e: self.controller.handle_move("right"))
        self.bind("<Control-z>", lambda _e: self.controller.handle_undo())
        self.bind("<u>",         lambda _e: self.controller.handle_undo())
        self.bind("<n>",         lambda _e: self.controller.handle_new_game())
        self.focus_set()

    # ──────────────────────────────────────────────────────────────────────────
    # Méthodes de mise à jour appelées par le contrôleur
    # ──────────────────────────────────────────────────────────────────────────

    def update_board(
        self,
        board: List[List[int]],
        player_pos: Dict[int, Tuple[int, int]],
        size: int
    ) -> None:
        """
        Redessine entièrement le plateau de jeu.

        Chaque case est colorée selon son appartenance.
        La position courante de chaque joueur est affichée avec un emoji.

        Args:
            board:      Matrice représentant l'état du plateau.
            player_pos: Positions {joueur: (ligne, colonne)}.
            size:       Dimension du plateau.
        """
        self.size = size
        canvas_px = size * self.CELL_SIZE + 2 * self.CELL_PADDING
        self.canvas.config(width=canvas_px, height=canvas_px)
        self.canvas.delete("all")

        p1_pos = player_pos[1]
        p2_pos = player_pos[2]

        for row in range(size):
            for col in range(size):
                x1 = col * self.CELL_SIZE + self.CELL_PADDING
                y1 = row * self.CELL_SIZE + self.CELL_PADDING
                x2 = x1 + self.CELL_SIZE - self.CELL_PADDING
                y2 = y1 + self.CELL_SIZE - self.CELL_PADDING
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                cell_val = board[row][col]
                if (row, col) == p1_pos:
                    color = self.COLOR_P1_CURRENT
                elif (row, col) == p2_pos:
                    color = self.COLOR_P2_CURRENT
                elif cell_val == 1:
                    color = self.COLOR_P1
                elif cell_val == 2:
                    color = self.COLOR_P2
                else:
                    color = self.COLOR_EMPTY

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline="#AAAAAA", width=1
                )

                if (row, col) == p1_pos:
                    self.canvas.create_text(
                        cx, cy, text=self.EMOJI_P1,
                        font=("Helvetica", int(self.CELL_SIZE * 0.38))
                    )
                elif (row, col) == p2_pos:
                    self.canvas.create_text(
                        cx, cy, text=self.EMOJI_P2,
                        font=("Helvetica", int(self.CELL_SIZE * 0.38))
                    )

    def update_scores(
        self,
        scores: Dict[int, int],
        player_turn: int,
        player_names: Dict[int, str]
    ) -> None:
        """
        Met à jour les scores, les noms et l'indicateur de tour.

        Args:
            scores:       Dictionnaire {joueur: score}.
            player_turn:  Numéro du joueur actif.
            player_names: Noms des joueurs {numéro: obj}.
        """
        self.p1_score_lbl.config(text=str(scores[1]))
        self.p2_score_lbl.config(text=str(scores[2]))
        self.p1_name_lbl.config(text=player_names[1])
        self.p2_name_lbl.config(text=player_names[2])

        if player_turn == 1:
            self.turn_indicator.config(text="◀", fg=self.COLOR_P1)
            self.p1_panel.config(relief=tk.RAISED, bd=3)
            self.p2_panel.config(relief=tk.FLAT,   bd=0)
            self.status_lbl.config(
                text=f"  Tour de {player_names[1]} — utilisez les flèches ou les boutons."
            )
        else:
            self.turn_indicator.config(text="▶", fg=self.COLOR_P2)
            self.p1_panel.config(relief=tk.FLAT,   bd=0)
            self.p2_panel.config(relief=tk.RAISED, bd=3)
            self.status_lbl.config(
                text=f"  Tour de {player_names[2]} — utilisez les flèches ou les boutons."
            )

    def flash_invalid_move(self) -> None:
        """
        Feedback visuel (flash rouge) quand un déplacement est interdit.

        Évite une popup bloquante en faisant clignoter brièvement le canvas.
        """
        original_bg = self.canvas.cget("bg")
        self.canvas.config(bg="#E74C3C")
        self.after(160, lambda: self.canvas.config(bg=original_bg))

    def reset(self) -> None:
        """
        Réinitialise l'affichage de la vue pour une nouvelle partie.

        Remet la barre de statut à son message par défaut et efface
        toute mise en évidence résiduelle des panneaux de score.
        Délègue le rechargement du plateau au contrôleur via handle_new_game().
        """
        self.status_lbl.config(
            text="Utilisez les flèches du clavier ou les boutons pour vous déplacer."
        )
        self.p1_panel.config(relief=tk.FLAT, bd=0)
        self.p2_panel.config(relief=tk.FLAT, bd=0)

    def end_game(self, winner_name: Optional[str]) -> None:
        """
        Affiche l'écran de fin de partie (alias explicite de show_game_over).

        Nommé end_game() conformément à l'UML pour que le contrôleur
        puisse l'appeler sans connaître le nom interne show_game_over().

        Args:
            winner_name: Nom du gagnant, ou None en cas d'égalité.
        """
        self.show_game_over(winner_name)

    def show_game_over(self, winner_name: Optional[str]) -> None:
        """
        Affiche la fenêtre de fin de partie et propose une nouvelle partie.

        Args:
            winner_name: Nom du gagnant, ou None si égalité.
        """
        if winner_name:
            message = f"🏆  {winner_name} gagne !\n\nVoulez-vous rejouer ?"
        else:
            message = "🤝  Égalité !\n\nVoulez-vous rejouer ?"

        if messagebox.askyesno("Fin de partie", message):
            self.controller.handle_new_game()

    # ──────────────────────────────────────────────────────────────────────────
    # Lancement
    # ──────────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Lance la boucle principale Tkinter."""
        self.mainloop()