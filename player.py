"""
Module contenant les classes Player, Human et AI pour le jeu des allumettes.
"""
import random
import json

class Player:
    """
    Représente un joueur de base (random) dans le jeu des allumettes.

    Attributes:
        name (str): Le nom du joueur.
        game: La partie en cours (None par défaut).
        nb_wins (int): Nombre de victoires.
        nb_loses (int): Nombre de défaites.
    """

    def __init__(self, name: str, game=None) -> None:
        """
        Initialise un joueur avec un nom et une partie optionnelle.

        Args:
            name (str): Le nom du joueur.
            game: La partie associée au joueur (None par défaut).
        """
        self.name = name
        self.game = game
        self.nb_wins: int = 0
        self.nb_loses: int = 0

    @property
    def nb_games(self) -> int:
        """
        Retourne le nombre total de parties jouées.

        Returns:
            int: Somme des victoires et des défaites.
        """
        return self.nb_wins + self.nb_loses

    def play(self) -> int:
        """
        Choisit aléatoirement un nombre d'allumettes entre 1 et le maximum possible.
        Le maximum est min(3, nb_allumettes_restantes) pour ne pas dépasser ce qui est disponible.

        Returns:
            int: Un entier aléatoire entre 1 et min(3, nb restant) inclus.
        """
        # Limiter le choix au nombre d'allumettes restantes
        max_take = min(3, self.game.nb) if self.game else 3
        return random.randint(1, max_take)

    def win(self) -> None:
        """
        Incrémente le compteur de victoires du joueur.
        """
        self.nb_wins += 1

    def lose(self) -> None:
        """
        Incrémente le compteur de défaites du joueur.
        """
        self.nb_loses += 1

    def __str__(self) -> str:
        """
        Retourne une représentation textuelle du joueur.

        Returns:
            str: Nom du joueur et ses statistiques.
        """
        return (
            f"{self.name} | Wins: {self.nb_wins} | "
            f"Loses: {self.nb_loses} | Games: {self.nb_games}"
        )


class Human(Player):
    """
    Représente un joueur humain qui saisit son choix via l'interface.

    Hérite de Player et redéfinit uniquement la méthode play()
    pour une utilisation en mode console (hors interface graphique).
    """

    def play(self) -> int:
        """
        Demande à l'humain de choisir un nombre d'allumettes (1 à 3) en console.

        Returns:
            int: Le choix valide de l'utilisateur entre 1 et 3.
        """
        # Boucle jusqu'à obtenir un choix valide
        while True:
            try:
                choice = int(input("How many matches do you want to take? (1, 2 or 3): "))
                if choice in (1, 2, 3):
                    return choice
                print("Please enter 1, 2 or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

class AI(Player):

    def __init__(self, name, epsilon=0.9, learning_rate=0.01, game=None):
        super().__init__(name, game)
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.history = []
        self.previous_state = None
        self.value_function = {}

        self.value_function["win"] = +1
        self.value_function["lose"] = -1

    def exploit(self):
        current_nb = self.game.nb
        max_take = min(3, current_nb)
        best_action = 1
        best_value = float('inf') # on cherche à minimiser la valeur pour l'adversaire

        for action in range(1, max_take + 1):
            new_state = current_nb - action  # <-- état correct pour le coup
            value = self.value_function.get(new_state, 0)  # 0 si jamais l'état n'est pas encore appris
            if value < best_value:
                best_value = value
                best_action = action

        return best_action

    def play(self):
        current_nb = self.game.nb

        #  Ajouter la transition précédente à l’historique
        if self.previous_state is not None:
            new_state = self.previous_state - current_nb
            self.history.append((new_state, self.previous_state))

        #  Choisir l’action

        if random.random() < self.epsilon:
            action = self.exploit()  # meilleure action selon value-function
        else:
            max_take = min(3, current_nb)
            action = random.randint(1, max_take)  # explore

        #  Mettre à jour l’état précédent pour le prochain tour
        self.previous_state = current_nb # temporaire

        return action
    
    def win(self):
        # Ajouter la dernière transition
        if self.previous_state is not None:
            transition = (self.previous_state, "win")  # état final
            self.history.append(transition)

        #  Appeler la méthode de la super-classe pour le reste
        super().win()

        # Réinitialiser previous_state
        self.previous_state = None


    def lose(self):
        if self.previous_state is not None:
            transition = (self.previous_state, "lose")  # état final
            self.history.append(transition)

        super().lose()
        self.previous_state = None

    def train(self):
            # mise à jour en back-tracking de la value_function
        next_value = None  # valeur à propager, commence par l'état final

        for _, state in reversed(self.history):
            current_value = self.value_function.get(state, 0)

            # Si next_value est None, on prend la valeur existante de l'état final
            if next_value is None:
                next_value = current_value

            # Mise à jour 
            updated_value = current_value + self.learning_rate * (next_value - current_value)
            self.value_function[state] = updated_value

            # Propage vers l'état précédent
            next_value = updated_value

        self.history.clear()

    def next_epsilon(self, coefficient=0.95, minimum=0.05):

        self.epsilon = max(self.epsilon * coefficient, minimum)

    def upload(self, file_name):
        data = {
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate,
            "value_function": self.value_function
        }

        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)
    
    def download(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)

        self.epsilon = data["epsilon"]
        self.learning_rate = data["learning_rate"]
        self.value_function = data["value_function"]