"""
Contrôleur d'une course Pixel Kart.

Responsabilités :
- Recevoir les actions de l'utilisateur depuis la vue (clics sur les boutons d'un kart)
- Appliquer ces actions sur le modèle Race
- Rafraîchir la vue après chaque action
- Faire jouer automatiquement les IA via after()
- Gérer le retour au menu (callback on_quit)
"""

from .game_model import Race


class GameController:
    """Contrôleur d'une course en cours."""

    AI_DELAY_MS = 500  # délai entre deux actions de l'IA pour rester lisible

    def __init__(self, race: Race, on_quit):
        """
        Args:
            race    : modèle de la course (déjà construit)
            on_quit : callback appelé pour revenir au menu
                      (typiquement PixelKartApp.show_menu)
        """
        self.race = race
        self.on_quit = on_quit
        self.view = None  # injecté plus tard via set_view()
        self._stopped = False

    def set_view(self, view) -> None:
        """Lie une vue (PixelKartRaceView) au contrôleur."""
        self.view = view

    def start(self) -> None:
        """À appeler une fois la vue prête : déclenche éventuellement le 1er tour IA."""
        if self.view is None:
            return
        self.view.update_view(self.race)
        self._maybe_play_ai()

    # ---------- Callbacks venant de la vue ----------

    def handle_action(self, kart_index: int, action: str) -> None:
        """Traitement d'un clic sur un bouton d'action humain."""
        if self._stopped or self.race.is_finished():
            return
        if kart_index != self.race.current_kart_index:
            return  # ce n'est pas le tour de ce kart

        self.race.play_action(action)
        if self.view is not None:
            self.view.update_view(self.race)
        self._maybe_play_ai()

    def handle_quit(self) -> None:
        """Bouton back/stop : on revient au menu."""
        self._stopped = True
        if self.on_quit:
            self.on_quit()

    # ---------- Tour des IA ----------

    def _maybe_play_ai(self) -> None:
        """Si le kart courant est une IA, planifie son action après un délai."""
        if self._stopped or self.race.is_finished():
            return
        kart = self.race.current_kart
        if kart.is_ai and self.view is not None:
            self.view.after(self.AI_DELAY_MS, self._play_ai_turn)

    def _play_ai_turn(self) -> None:
        """Exécute une action de l'IA courante puis enchaîne si besoin."""
        if self._stopped or self.race.is_finished():
            return
        # La vue peut avoir été détruite entre-temps (back ou quit)
        if self.view is None:
            return
        try:
            self.view.winfo_exists()
        except Exception:
            return

        kart = self.race.current_kart
        if not kart.is_ai:
            return

        action = kart.choose_action(self.race)
        self.race.play_action(action)
        self.view.update_view(self.race)
        self._maybe_play_ai()
