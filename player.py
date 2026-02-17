"""
Module contenant les classes Player, Human et AI pour le jeu des allumettes.
"""
import random


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

    def __init__(self, name, game=None):
        super().__init__(name, game)
        self.epsilon = 0.9
        self.learning_rate = 0.01
        self.history = []
        self.previous_state = None
        self.value_function = {}

        #crée tout les états finaux possible
        for remaining in range(1, game.nb + 1): #création de paire inutile peut-etre reduire à max 3
            state_final = (remaining, 0)
            # la logique de gain : si IA joue, elle prend la dernière → perd
            if remaining == 1:
                self.value_function[state_final] = -1  # IA perd si elle prend la dernière
            else:
                self.value_function[state_final] = +1  # IA gagne sinon

    def exploit(self):
        current_nb = self.game.nb
        max_take = min(3, current_nb)
        best_action = 1
        best_value = float('inf') # on cherche à minimiser la valeur pour l'adversaire

        for action in range(1, max_take + 1):
            new_state = (current_nb, current_nb - action)  # <-- état correct pour le coup
            value = self.value_function.get(new_state, 0)  # 0 si jamais l'état n'est pas encore appris
            if value < best_value:
                best_value = value
                best_action = action

        return best_action

    def play(self):
        current_nb = self.game.nb

        # 1️ Ajouter la transition précédente à l’historique
        if self.previous_state is not None:
            new_state = (self.previous_state, current_nb)
            self.history.append(new_state)

        # 2️ Choisir l’action

        if random.random() < self.epsilon:
            action = self.exploit()  # meilleure action selon value-function
        else:
            max_take = min(3, current_nb)
            action = random.randint(1, max_take)  # explore

        # 3️ Mettre à jour l’état précédent pour le prochain tour
        self.previous_state = current_nb # temporaire

        return action
    
    def win(self):
        # Ajouter la dernière transition
        if self.previous_state is not None:
            transition = (self.previous_state, 0)  # état final
            self.history.append(transition)

        #  Appeler la méthode de la super-classe pour le reste
        super().win()

        # Réinitialiser previous_state
        self.previous_state = None


    def lose(self):
        if self.previous_state is not None:
            transition = (self.previous_state, 0)  # état final
            self.history.append(transition)

        super().lose()
        self.previous_state = None