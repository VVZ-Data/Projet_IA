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
    """
    
    # Variable de classe pour stocker l'instance unique
    _instance = None
    
    def __new__(cls):
        """
        Crée ou retourne l'instance unique du LanguageManager.
        """
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            # Initialisation lors de la première création
            cls._instance.current_lang = "en"  # Langue par défaut : anglais
            cls._instance.observers = []  # Liste des vues à notifier
        return cls._instance
    
    def get_lang(self) -> str:
        """Retourne le code de la langue courante."""
        return self.current_lang
    
    def set_lang(self, lang: str) -> None:
        """Change la langue courante et notifie toutes les vues observatrices."""
        if lang not in ["en", "fr"]:
            return
        
        self.current_lang = lang
        self._notify_observers()
    
    def toggle_lang(self) -> None:
        """Alterne entre anglais et français."""
        new_lang = "fr" if self.current_lang == "en" else "en"
        self.set_lang(new_lang)
    
    def register_observer(self, observer) -> None:
        """Enregistre une vue pour qu'elle soit notifiée."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def unregister_observer(self, observer) -> None:
        """Retire une vue de la liste des observateurs."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self) -> None:
        """
        Notifie tous les observateurs d'un changement de langue.
        Nettoie automatiquement les observateurs dont les widgets sont détruits.
        """
        to_remove = []  # Liste temporaire pour stocker les observateurs invalides
        
        for observer in self.observers:
            try:
                # Vérifier que l'observateur a bien une méthode update_language
                if hasattr(observer, 'update_language'):
                    observer.update_language()
            except Exception:
                # Si une erreur survient (ex: widget Tkinter détruit), 
                # on marque l'observateur pour suppression
                to_remove.append(observer)
        
        # Nettoyage des observateurs invalides après la boucle de notification
        for obs in to_remove:
            self.unregister_observer(obs)
    
    def get_text(self, key: str, **kwargs) -> str:
        """Raccourci pour récupérer un texte traduit."""
        return get_text(key, self.current_lang, **kwargs)


# Instance globale accessible depuis n'importe quel module
lang_manager = LanguageManager()