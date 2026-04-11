"""
Module de gestion des traductions pour l'application multilingue.
Contient tous les textes en français et en anglais.
"""

# Dictionnaire complet des traductions
# Chaque clé correspond à un texte utilisé dans l'interface
TRANSLATIONS = {
    "en": {
        # Page d'accueil
        "title": "Game Collection",
        "matchstick_game": "Matchstick Game",
        "cubee_game": "Cubee",
        "pixelKart_game": "Pixel Kart",
        "coming_soon": "Coming Soon",
        "select_game": "Select a game to play",

        # Menu cubee
        "cubee_menu_title": "Cubee",

        # Menu pixelKart
        "pixel_kart_menu_title": "Pixel Kart - Menu",
        "pk_play": "Play",
        "pk_training": "Training",
        "pk_vs_ai": "vs AI",
        "pk_vs_human": "vs Human",
        "pk_settings": "Race settings",
        "pk_choose_circuit": "Circuit:",
        "pk_nb_turns": "Number of turns:",
        "pk_open_editor": "Open circuit editor",
        "pk_race_title": "Pixel Kart - Race",
        "pk_time": "Time",
        "pk_turns_to_do": "Turns to do",
        "pk_stop": "⏹ Stop & back to menu",
        "pk_position": "Position",
        "pk_direction": "Direction",
        "pk_speed": "Speed",
        "pk_turns_done": "Turns done",
        "pk_accelerate": "Accelerate",
        "pk_brake": "Brake",
        "pk_turn_left": "Turn Left",
        "pk_turn_right": "Turn Right",
        "pk_pass": "Pass",
        "pk_winner": "🏆 {} wins!",
        "pk_no_winner": "No winner — all karts crashed.",

        # Menu du jeu des allumettes
        "menu_title": "Matchstick Game - Menu",
        "play": "Play",
        "train_ai1": "Train AI 1",
        "train_ai": "Train AI",
        "train_ai2": "Train AI 2",
        "back": "Back",
        "vs_ai1": "vs AI 1",
        "vs_ai2": "vs AI 2",
        "vs_random": "vs Random",
        
        # Partie en cours
        "game_title": "Matchstick Game",
        "player_turn": "{}'s turn",
        "winner": "🏆 {} wins!",
        "take_1": "1",
        "take_2": "2",
        "take_3": "3",
        "matches_remaining": "{} matches remaining",
        "play_again": "Play Again",
        "quit": "Quit",
        
        # Entraînement
        "training_title": "Training - {}",
        "nb_games": "Number of games:",
        "epsilon_decay": "Epsilon decay every:",
        "learning_rate": "Learning rate:",
        "opponent": "Opponent:",
        "start_training": "Start Training",
        "training_progress": "Training Progress",
        "games_played": "Games played: {}/{}",
        "training_complete": "Training Complete!",
        "ai_wins": "{} wins: {} ({}%)",
        "opp_wins": "Opponent wins: {} ({}%)",
        "analysis": "Analysis: {}",
        "save_results": "Save to File",
        
        # Analyses
        "balanced": "The training was balanced.",
        "ai_dominates": "{} dominates with {}% win rate.",
        "opp_dominates": "Opponent dominates with {}% win rate.",
    },
    
    "fr": {
        # Page d'accueil
        "title": "Collection de Jeux",
        "matchstick_game": "Jeu des Allumettes",
        "cubee_game": "Cubee",
        "pixelKart_game": "Pixel Kart",
        "coming_soon": "Bientôt Disponible",
        "select_game": "Sélectionnez un jeu pour jouer",

        # Menu cubee
        "cubee_menu_title": "Cubee",

        # Menu pixelKart
        "pixel_kart_menu_title": "Pixel Kart - Menu",
        "pk_play": "Jouer",
        "pk_training": "Entraînement",
        "pk_vs_ai": "contre IA",
        "pk_vs_human": "contre Humain",
        "pk_settings": "Paramètres de la course",
        "pk_choose_circuit": "Circuit :",
        "pk_nb_turns": "Nombre de tours :",
        "pk_open_editor": "Ouvrir l'éditeur de circuit",
        "pk_race_title": "Pixel Kart - Course",
        "pk_time": "Temps",
        "pk_turns_to_do": "Tours à faire",
        "pk_stop": "⏹ Arrêter et retour au menu",
        "pk_position": "Position",
        "pk_direction": "Direction",
        "pk_speed": "Vitesse",
        "pk_turns_done": "Tours effectués",
        "pk_accelerate": "Accélérer",
        "pk_brake": "Freiner",
        "pk_turn_left": "Gauche",
        "pk_turn_right": "Droite",
        "pk_pass": "Passer",
        "pk_winner": "🏆 {} gagne !",
        "pk_no_winner": "Aucun vainqueur — tous les karts ont crashé.",

        # Menu du jeu des allumettes
        "menu_title": "Jeu des Allumettes - Menu",
        "play": "Jouer",
        "train_ai1": "Entraîner l'IA 1",
        "train_ai": "Entraîner une IA",
        "train_ai2": "Entraîner l'IA 2",
        "back": "Retour",
        "vs_ai1": "contre IA 1",
        "vs_ai2": "contre IA 2",
        "vs_random": "contre Random",
        
        # Partie en cours
        "game_title": "Jeu des Allumettes",
        "player_turn": "Tour de {}",
        "winner": "🏆 {} gagne !",
        "take_1": "1",
        "take_2": "2",
        "take_3": "3",
        "matches_remaining": "{} allumettes restantes",
        "play_again": "Rejouer",
        "quit": "Quitter",
        
        # Entraînement
        "training_title": "Entraînement - {}",
        "nb_games": "Nombre de parties :",
        "epsilon_decay": "Diminution epsilon tous les :",
        "learning_rate": "Taux d'apprentissage :",
        "opponent": "Adversaire :",
        "start_training": "Lancer l'Entraînement",
        "training_progress": "Progression de l'Entraînement",
        "games_played": "Parties jouées : {}/{}",
        "training_complete": "Entraînement Terminé !",
        "ai_wins": "Victoires {} : {} ({}%)",
        "opp_wins": "Victoires Adversaire : {} ({}%)",
        "analysis": "Analyse : {}",
        "save_results": "Sauvegarder les Résultats",
        
        # Analyses
        "balanced": "Les résultats sont équilibrés.",
        "ai_dominates": "{} domine avec {}% de victoires.",
        "opp_dominates": "L'adversaire domine avec {}% de victoires.",
    }
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """
    Récupère un texte traduit selon la langue sélectionnée.
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text