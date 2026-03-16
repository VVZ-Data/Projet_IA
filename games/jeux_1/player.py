"""
Module contenant les classes Player, Human et AI pour le jeu des allumettes.
"""
import random
import json
from pathlib import Path


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

    def play(self, state) -> int:
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

    def play(self, state) -> int:
        """
        Demande à l'humain de choisir un nombre d'allumettes (1 à 3) en console.

        Returns:
            int: Le choix valide de l'utilisateur entre 1 et 3.
        """
        # Boucle jusqu'à obtenir un choix valide
        choice = 0

        while choice not in (1, 2, 3):
            try:
                choice = int(input("How many matches do you want to take? (1, 2 or 3): "))
                if choice not in (1, 2, 3):
                    print("Please enter 1, 2 or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        return choice

class AI(Player):
    """"
    Initialise un joueur IA utilisant une stratégie d'apprentissage par renforcement.

    Args:
        name (str): Nom du joueur.
        epsilon (float, optional): Probabilité d'exploration (stratégie epsilon-greedy).
            Plus epsilon est grand, plus l'agent explore aléatoirement.
            Default = 0.9.
        learning_rate (float, optional): Taux d’apprentissage utilisé pour
            mettre à jour la fonction de valeur. Default = 0.01.
        game (Game, optional): Instance du jeu associée au joueur.
    """

    def __init__(self, name, epsilon=0.9, learning_rate=0.01, game=None):
        super().__init__(name, game)
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.history = []
        self.previous_state = None
        self.value_function = {"win": +1, "lose": -1}


    def exploit(self, state):
        """
        Sélectionne la meilleure action possible selon la value_function actuelle.

        L’IA teste toutes les actions possibles (prendre entre 1 et 3 objets,
        ou moins si le nombre restant est inférieur à 3) et choisit celle
        menant à l’état ayant la plus petite valeur estimée.

        Returns:
            int: Nombre d’objets à prendre.
        """
        max_take = min(3, state)
        best_action = 1
        best_value = float('inf')

        for action in range(1, max_take + 1):
            new_state = state - action
            value = self.value_function.get(new_state, 0)
            if value < best_value:
                best_value = value
                best_action = action
        return best_action

    def play(self, state):
        """
        Choisit une action à jouer selon la stratégie epsilon-greedy.

        - Ajoute la transition précédente dans l’historique.
        - Avec une probabilité epsilon : exploration (action aléatoire).
        - Sinon : exploitation (meilleure action connue).

        Met à jour l’état précédent pour permettre l’apprentissage futur.

        Returns:
            int: Nombre d’objets à prendre.
        """

        #  Ajouter la transition précédente à l’historique
        if self.previous_state is not None:
            self.history.append((self.previous_state, state))

        #  Choisir l’action
        if random.random() < self.epsilon:
            max_take = min(3, state)
            action = random.randint(1, max_take)  # explore
        else:
            action = self.exploit(state)  # meilleure action selon value-function


        #  Mettre à jour l’état précédent pour le prochain tour
        self.previous_state = state 
        return action
    
    def win(self):
        """
        Méthode appelée lorsque l’IA gagne la partie.

        - Ajoute la dernière transition vers l’état terminal "win".
        - Appelle la méthode win() de la super-classe.
        - Réinitialise l’état précédent.
        """
        # Ajouter la dernière transition
        if self.previous_state is not None:
            transition = (self.previous_state, "win")  # état final
            self.history.append(transition)

        #  Appeler la méthode de la super-classe pour le reste
        super().win()

        # Réinitialiser previous_state
        self.previous_state = None


    def lose(self):
        """
        Méthode appelée lorsque l’IA perd la partie.

        - Ajoute la dernière transition vers l’état terminal "lose".
        - Appelle la méthode lose() de la super-classe.
        - Réinitialise l’état précédent.
        """
        if self.previous_state is not None:

            transition = (self.previous_state, "lose")  # état final
            self.history.append(transition)

        super().lose()
        self.previous_state = None

    def train(self):
        """
        Met à jour la fonction de valeur (value_function) en parcourant
        l’historique des transitions dans l’ordre inverse.

        Applique une mise à jour de type Temporal Difference (TD(0)) :

            V(s) ← V(s) + learning_rate * (V(s') - V(s))

        À la fin de l’entraînement, l’historique est vidé.
        """
        for s, s_prime in reversed(self.history):

            value_s = self.value_function.get(s, 0)
            value_s_prime = self.value_function.get(s_prime, 0)

            self.value_function[s] = value_s + self.learning_rate * (value_s_prime - value_s)
        self.history.clear()


    def next_epsilon(self, coefficient=0.95, minimum=0.05):
        """
        Réduit progressivement epsilon (décroissance de l’exploration).

        Args:
            coefficient (float, optional): Facteur multiplicatif appliqué
                à epsilon à chaque appel. Default = 0.95.
            minimum (float, optional): Valeur minimale que epsilon ne peut
                pas dépasser. Default = 0.05.
        """
        self.epsilon = max(self.epsilon * coefficient, minimum)

    def upload(self, ai_number):
        """
        Sauvegarde les paramètres de l’IA dans un fichier JSON.

        Les éléments sauvegardés sont :
            - epsilon
            - learning_rate
            - value_function

        Args:
            file_name (str): Nom du fichier de sauvegarde.
        """
        BASE_DIR = Path(__file__).parent
        save_path = BASE_DIR / f"AI_save_{ai_number}.json"

        data = {
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate,
            "value_function": self.value_function
        }

        with open(save_path, "w") as f:
            json.dump(data, f, indent=4)
    
    def download(self, ai_number):
        """
        Charge les paramètres de l’IA depuis un fichier JSON.

        Restaure :
            - epsilon
            - learning_rate
            - value_function

        Args:
            filename (str): Nom du fichier à charger.
        """
        BASE_DIR = Path(__file__).parent
        save_path = BASE_DIR / f"AI_save_{ai_number}.json"

        with open(save_path, "r") as f:
            data = json.load(f)

        self.epsilon = data["epsilon"]
        self.learning_rate = data["learning_rate"]
        self.value_function = data["value_function"]

            # Convertir les clés string en int
        self.value_function = {}
        for k, v in data["value_function"].items():
            try:
                self.value_function[int(k)] = v  # '8' → 8
            except ValueError:
                self.value_function[k] = v  # garder 'win' et 'lose' comme strings
