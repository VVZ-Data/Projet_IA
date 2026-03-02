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
        "coming_soon": "Coming Soon",
        "select_game": "Select a game to play",
        
        # Menu du jeu des allumettes
        "menu_title": "Matchstick Game - Menu",
        "play": "Play",
        "train": "Train AI",
        "back": "Back",
        "vs_ai": "Play vs AI",
        "vs_random": "Play vs Random",
        
        # Partie en cours
        "game_title": "Matchstick Game",
        "player_turn": "{}'s turn",
        "winner": "🏆 {} wins!",
        "take": "Take {}",
        "matches_remaining": "{} matches remaining",
        "play_again": "Play Again",
        "quit": "Quit",
        
        # Entraînement
        "training_title": "AI Training",
        "nb_games": "Number of games:",
        "epsilon_decay": "Epsilon decay every:",
        "learning_rate": "Learning rate:",
        "start_training": "Start Training",
        "training_progress": "Training Progress",
        "games_played": "Games played: {}/{}",
        "training_complete": "Training Complete!",
        "ai1_wins": "AI 1 wins: {} ({}%)",
        "ai2_wins": "AI 2 wins: {} ({}%)",
        "analysis": "Analysis: {}",
        "save_results": "Save Results",
        
        # Analyses
        "balanced": "The AIs are balanced - both won approximately 50% of games.",
        "ai1_dominates": "AI 1 dominates with {}% win rate. It found a better strategy.",
        "ai2_dominates": "AI 2 dominates with {}% win rate. It found a better strategy.",
    },
    
    "fr": {
        # Page d'accueil
        "title": "Collection de Jeux",
        "matchstick_game": "Jeu des Allumettes",
        "coming_soon": "Bientôt Disponible",
        "select_game": "Sélectionnez un jeu pour jouer",
        
        # Menu du jeu des allumettes
        "menu_title": "Jeu des Allumettes - Menu",
        "play": "Jouer",
        "train": "Entraîner l'IA",
        "back": "Retour",
        "vs_ai": "Jouer contre l'IA",
        "vs_random": "Jouer contre Random",
        
        # Partie en cours
        "game_title": "Jeu des Allumettes",
        "player_turn": "Tour de {}",
        "winner": "🏆 {} gagne !",
        "take": "Prendre {}",
        "matches_remaining": "{} allumettes restantes",
        "play_again": "Rejouer",
        "quit": "Quitter",
        
        # Entraînement
        "training_title": "Entraînement de l'IA",
        "nb_games": "Nombre de parties :",
        "epsilon_decay": "Diminution epsilon tous les :",
        "learning_rate": "Taux d'apprentissage :",
        "start_training": "Lancer l'Entraînement",
        "training_progress": "Progression de l'Entraînement",
        "games_played": "Parties jouées : {}/{}",
        "training_complete": "Entraînement Terminé !",
        "ai1_wins": "Victoires IA 1 : {} ({}%)",
        "ai2_wins": "Victoires IA 2 : {} ({}%)",
        "analysis": "Analyse : {}",
        "save_results": "Sauvegarder les Résultats",
        
        # Analyses
        "balanced": "Les IA sont équilibrées - chacune a gagné environ 50% des parties.",
        "ai1_dominates": "L'IA 1 domine avec {}% de victoires. Elle a trouvé une meilleure stratégie.",
        "ai2_dominates": "L'IA 2 domine avec {}% de victoires. Elle a trouvé une meilleure stratégie.",
    }
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """
    Récupère un texte traduit selon la langue sélectionnée.
    
    Args:
        key (str): Clé du texte à récupérer dans le dictionnaire.
        lang (str): Code de la langue ("en" ou "fr"). Par défaut "en".
        **kwargs: Paramètres pour le formatage (ex: format avec {}).
    
    Returns:
        str: Le texte traduit, formaté si nécessaire.
        
    Example:
        >>> get_text("player_turn", "fr", player="Alice")
        "Tour de Alice"
    """
    # Récupérer le texte dans la langue demandée
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    
    # Formatter le texte si des paramètres sont fournis
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            # Si le formatage échoue, retourner le texte brut
            pass
    
    return text
