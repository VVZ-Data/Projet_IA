"""
Module de gestion de la langue courante de l'application.
Utilise le pattern Singleton pour garantir une instance unique.
"""

from translations import get_text


class LanguageManager:
    """
    Gestionnaire global de la langue de l'interface.
    
    Utilise le pattern Singleton pour s'assurer qu'il n'existe
    qu'une seule instance partagée par toute l'application.
    
    Attributes:
        _instance (LanguageManager): Instance unique du gestionnaire.
        current_lang (str): Code de la langue courante ("en" ou "fr").
        observers (list): Liste des vues à notifier lors d'un changement de langue.
    """
    
    # Variable de classe pour stocker l'instance unique
    _instance = None
    
    def __new__(cls):
        """
        Crée ou retourne l'instance unique du LanguageManager.
        
        Pattern Singleton : si une instance existe déjà, on la retourne.
        Sinon, on en crée une nouvelle.
        
        Returns:
            LanguageManager: L'instance unique du gestionnaire.
        """
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            # Initialisation lors de la première création
            cls._instance.current_lang = "en"  # Langue par défaut : anglais
            cls._instance.observers = []  # Liste des vues à notifier
        return cls._instance
    
    def get_lang(self) -> str:
        """
        Retourne le code de la langue courante.
        
        Returns:
            str: "en" pour anglais ou "fr" pour français.
        """
        return self.current_lang
    
    def set_lang(self, lang: str) -> None:
        """
        Change la langue courante et notifie toutes les vues observatrices.
        
        Args:
            lang (str): Nouveau code de langue ("en" ou "fr").
        """
        # Vérifier que la langue demandée est valide
        if lang not in ["en", "fr"]:
            return
        
        # Mettre à jour la langue
        self.current_lang = lang
        
        # Notifier toutes les vues enregistrées du changement
        self._notify_observers()
    
    def toggle_lang(self) -> None:
        """
        Alterne entre anglais et français.
        Pratique pour un bouton de changement rapide.
        """
        # Si on est en anglais, passer au français et vice-versa
        new_lang = "fr" if self.current_lang == "en" else "en"
        self.set_lang(new_lang)
    
    def register_observer(self, observer) -> None:
        """
        Enregistre une vue pour qu'elle soit notifiée des changements de langue.
        
        La vue doit implémenter une méthode update_language() qui sera
        appelée automatiquement lors d'un changement de langue.
        
        Args:
            observer: Objet (généralement une vue) à notifier.
        """
        if observer not in self.observers:
            self.observers.append(observer)
    
    def unregister_observer(self, observer) -> None:
        """
        Retire une vue de la liste des observateurs.
        
        Args:
            observer: Objet à retirer de la liste.
        """
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self) -> None:
        """
        Notifie tous les observateurs d'un changement de langue.
        
        Appelle la méthode update_language() de chaque vue enregistrée.
        Si une vue n'a pas cette méthode, elle est ignorée.
        """
        for observer in self.observers:
            # Vérifier que l'observateur a bien une méthode update_language
            if hasattr(observer, 'update_language'):
                observer.update_language()
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        Raccourci pour récupérer un texte traduit dans la langue courante.
        
        Args:
            key (str): Clé du texte dans le dictionnaire de traductions.
            **kwargs: Paramètres de formatage optionnels.
        
        Returns:
            str: Texte traduit dans la langue courante.
            
        Example:
            >>> lang_manager = LanguageManager()
            >>> lang_manager.set_lang("fr")
            >>> lang_manager.get_text("player_turn", player="Alice")
            "Tour de Alice"
        """
        return get_text(key, self.current_lang, **kwargs)


# Instance globale accessible depuis n'importe quel module
# Utilisation : from language_manager import lang_manager
lang_manager = LanguageManager()
