"""
Contrôleur du jeu Pixel Kart.

Orchestre :
1. L'affichage du menu (MenuView)
2. La création du modèle Race à partir de la configuration
3. L'affichage de la course (RaceView)
4. La boucle de jeu (humains via clics, IA via after())
"""

import games.pixel_kart.editor.map_dao as map_dao
from games.pixel_kart.game_model import Circuit, Race
from games.pixel_kart.game_view import MenuView, RaceView
from games.pixel_kart.player import Human, RandomAI


class GameController:
    """Contrôleur principal de Pixel Kart."""

    AI_DELAY_MS = 500  # délai entre deux actions de l'IA

    def __init__(self):
        self.menu: MenuView | None = None
        self.race_view: RaceView | None = None
        self.race: Race | None = None

    # ---------- Menu ----------

    def run(self) -> None:
        """Lance le menu principal puis la mainloop Tkinter."""
        self.menu = MenuView(
            on_play=self._on_play_clicked,
            on_open_editor=lambda: None,  # géré directement par le menu
        )
        self.menu.mainloop()

    def _on_play_clicked(self, config: dict) -> None:
        """Crée la course et lance la fenêtre de course."""
        circuits = map_dao.get_all()
        raw = circuits.get(config["circuit"])
        if raw is None:
            print(f"Circuit '{config['circuit']}' introuvable.")
            return

        circuit = Circuit(name=config["circuit"], raw=raw)

        karts = []
        if config["human"]:
            karts.append(Human("Bob", "red"))
        if config["ai"]:
            karts.append(RandomAI("Randy", "blue"))

        self.race = Race(circuit=circuit, karts=karts, nb_turns=config["nb_turns"])

        # Fermer le menu et ouvrir la course
        self.menu.destroy()

        self.race_view = RaceView(self.race, on_action=self._on_action)
        self.race_view.update_view(self.race)

        # Si le 1er kart est une IA, on déclenche le tour
        self._maybe_play_ai()

        self.race_view.mainloop()

    # ---------- Boucle de jeu ----------

    def _on_action(self, kart_index: int, action: str) -> None:
        """Callback appelé quand un humain clique sur un bouton d'action."""
        if self.race is None or self.race.is_finished():
            return
        if kart_index != self.race.current_kart_index:
            return  # ce n'est pas son tour

        self.race.play_action(action)
        self.race_view.update_view(self.race)
        self._maybe_play_ai()

    def _maybe_play_ai(self) -> None:
        """
        Si la course est en cours et que le kart courant est une IA,
        planifie son action après un petit délai pour que l'humain voie ce qui se passe.
        """
        if self.race is None or self.race.is_finished():
            return
        kart = self.race.current_kart
        if kart.is_ai:
            self.race_view.after(self.AI_DELAY_MS, self._play_ai_turn)

    def _play_ai_turn(self) -> None:
        """Fait jouer l'IA courante."""
        if self.race is None or self.race.is_finished():
            return
        kart = self.race.current_kart
        if not kart.is_ai:
            return
        action = kart.choose_action(self.race)
        self.race.play_action(action)
        self.race_view.update_view(self.race)
        self._maybe_play_ai()
