import tkinter as tk
from .game_model import Race, Circuit
from .player import Human, AI
from .game_view import RaceView
from .dao.race_dao import CircuitDTO, CellType

class GameController:
    def __init__(self, root):
        self.root = root
        self.race = None
        self.view = None
        
        # Initialisation directe d'une course pour la V1
        self.setup_game()

    def setup_game(self):
        # 1. Création d'un circuit 15x10 par défaut
        grid = [[CellType.ROAD.value for _ in range(15)] for _ in range(10)]
        # Murs extérieurs
        for x in range(15):
            grid[0][x] = CellType.WALL.value
            grid[9][x] = CellType.WALL.value
        for y in range(10):
            grid[y][0] = CellType.WALL.value
            grid[y][14] = CellType.WALL.value
            
        # Ligne de départ
        grid[5][2] = CellType.START_LINE.value
        
        c_dto = CircuitDTO(grid, 15, 10, [(2, 5)])
        circuit = Circuit(c_dto)
        
        # 2. Joueurs (1 Humain, 1 IA)
        players = [
            Human("Joueur 1"),
            AI("Robot-Kart", epsilon=0.1)
        ]
        
        # 3. Création de la course
        self.race = Race(circuit, players, total_laps=2)
        
        # 4. Création de la vue
        self.view = RaceView(self.root, self.race.get_state_dto(), self.handle_player_action)
        
        # Vérification si le premier joueur est une IA
        self.check_ai_turn()

    def handle_player_action(self, action):
        # Exécute l'action de l'humain
        self.race.execute_action(action)
        self.race.next_kart()
        self.refresh()
        
        # Après l'humain, on vérifie si c'est au tour de l'IA
        self.check_ai_turn()

    def check_ai_turn(self):
        if self.race.is_race_over():
            return
            
        current_kart = self.race.get_current_kart()
        # Si le kart actuel a une méthode 'learn' ou n'est pas humain
        if isinstance(current_kart, AI):
            # Délai de 500ms pour voir l'action
            self.root.after(500, self.execute_ai_move)

    def execute_ai_move(self):
        kart = self.race.get_current_kart()
        action = kart.play() # Choix via Q-Table
        
        if action:
            result = self.race.execute_action(action)
            # Apprentissage V2
            if hasattr(kart, 'learn'):
                kart.learn(result["reward"])
        
        self.race.next_kart()
        self.refresh()
        
        # Boucle si le suivant est aussi une IA
        self.check_ai_turn()

    def refresh(self):
        if self.view:
            self.view.update_display(self.race.get_state_dto())