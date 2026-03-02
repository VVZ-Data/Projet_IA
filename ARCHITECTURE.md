# 🏗️ Architecture Technique du Projet

## Vue d'Ensemble

Le projet utilise une **architecture MVC (Modèle-Vue-Contrôleur)** stricte avec des **design patterns** modernes.

```
┌─────────────────────────────────────────────────┐
│              ARCHITECTURE MVC                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐     ┌──────────┐                │
│  │   VUE    │────▶│CONTRÔLEUR│                │
│  │ (Tkinter)│◀────│   (MVC)  │                │
│  └──────────┘     └─────┬────┘                │
│       ▲                  │                      │
│       │                  ▼                      │
│       │           ┌──────────┐                 │
│       └───────────│  MODÈLE  │                 │
│                   │ (Logique)│                 │
│                   └──────────┘                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📁 Structure des Fichiers

### Fichiers Principaux

#### `main.py` — Orchestrateur Principal
```python
MainApplication(Tk)
├── show_home()           # Affiche page d'accueil
├── show_matchstick_menu()# Menu du jeu
├── start_game()          # Lance une partie
└── start_training()      # Lance l'entraînement
```

**Rôle** : Gère la navigation entre les vues et orchestre toute l'application.

---

### Système de Traductions

#### `translations.py` — Dictionnaire Multilingue
```python
TRANSLATIONS = {
    "en": {"key": "English text"},
    "fr": {"key": "Texte français"}
}
```

**Rôle** : Contient TOUS les textes de l'interface en FR et EN.

#### `language_manager.py` — Gestionnaire de Langue (Singleton)
```python
class LanguageManager:
    _instance = None          # Instance unique
    current_lang = "en"       # Langue courante
    observers = []            # Vues à notifier
    
    get_text(key)            # Récupère texte traduit
    set_lang(lang)           # Change langue + notifie vues
    register_observer(view)  # Enregistre une vue
```

**Design Pattern** : Singleton + Observer

**Rôle** : 
1. Garantit une seule instance pour toute l'app
2. Notifie automatiquement toutes les vues lors d'un changement de langue

---

### Modèle (Logique Métier)

#### `player.py` — Classes des Joueurs
```python
Player                    # Joueur random de base
├── play()               # Choisit 1, 2 ou 3 aléatoirement
├── win()                # Incrémente victoires
└── lose()               # Incrémente défaites

Human(Player)            # Joueur humain
└── play()               # Attend input utilisateur

AI(Player)               # IA avec apprentissage
├── value_function       # Dict {état: valeur}
├── exploit()           # Choisit meilleure action
├── play()              # ε-greedy (explore/exploit)
├── train()             # TD-Learning
├── upload(file)        # Sauvegarde modèle
└── download(file)      # Charge modèle
```

**Algorithme IA** : Q-Learning avec politique ε-greedy

#### `game_model.py` — Logique du Jeu
```python
GameModel
├── nb                   # Allumettes restantes
├── player1, player2     # Les deux joueurs
├── current_player       # Index joueur actuel
├── step(action)         # Applique une action
├── switch_player()      # Change de joueur
├── is_game_over()       # Vérifie fin de partie
├── get_winner()         # Retourne gagnant
└── play()               # Joue partie complète
```

**Rôle** : Contient toute la logique du jeu (indépendante de l'interface).

---

### Contrôleur

#### `game_controller.py` — Lien Modèle/Vue
```python
GameController
├── model                # GameModel
├── view                 # GameView
├── get_nb_matches()     # Info pour la vue
├── get_status_message() # Message traduit
├── handle_human_move()  # Gère coup humain
├── handle_ai_move()     # Gère coup IA
└── handle_end_game()    # Gère fin de partie
```

**Rôle** : 
- Reçoit les actions de la vue (clics)
- Met à jour le modèle
- Notifie la vue des changements

---

### Vues (Interfaces Graphiques)

#### `views/home_view.py` — Page d'Accueil
```python
HomeView(Frame)
├── GameCard × 3         # Cartes de jeux
├── LanguageButton       # Bouton de langue
└── update_language()    # Observer pattern
```

**Composants** :
- `GameCard` : Carte cliquable avec hover
- `LanguageButton` : Menu déroulant au survol

#### `views/matchstick_menu_view.py` — Menu du Jeu
```python
MatchstickMenuView(Frame)
├── Play Card            # Section "Jouer"
│   ├── vs_ai_btn
│   └── vs_random_btn
└── Train Card           # Section "Entraîner"
    └── train_btn
```

#### `views/game_view.py` — Interface de Jeu
```python
GameView(Frame)
├── canvas               # Zone de dessin
├── message_label        # État du jeu
├── buttons_frame        # Boutons d'action
├── draw_matches(nb)     # Dessine allumettes
├── end_game()           # Affiche fin
└── reset()              # Nouvelle partie
```

**Méthode Clé** : `draw_matches()`
```python
def draw_matches(self, nb: int):
    # Calcule espacement automatique
    spacing = min(45, (CANVAS_WIDTH - 80) // nb)
    
    # Dessine chaque allumette
    for i in range(nb):
        x = start_x + i * spacing
        # Rectangle (corps)
        canvas.create_rectangle(...)
        # Ovale (tête)
        canvas.create_oval(...)
```

#### `views/training_view.py` — Interface d'Entraînement
```python
TrainingView(Frame)
├── params_card          # Formulaire config
├── progress_frame       # Barre progression
├── results_frame        # Résultats finaux
├── update_progress()    # MAJ barre
└── show_results()       # Affiche stats
```

**Workflow** :
1. Configuration → params_card
2. Entraînement → progress_frame (barre animée)
3. Résultats → results_frame (stats + analyse)

---

## 🔄 Flux de Données

### Lancement d'une Partie

```
User clicks "vs IA"
       │
       v
MainApplication.on_play_selected("ai")
       │
       ├─→ Crée Human + AI
       │
       v
MainApplication.start_game(human, ai)
       │
       ├─→ Crée GameController(human, ai)
       ├─→ Crée GameView(controller)
       │
       v
GameView affichée
       │
       v
Si IA commence → controller.handle_ai_move()
```

### Tour de Jeu (Humain)

```
User clicks "Take 2"
       │
       v
GameView → command=lambda: controller.handle_human_move(2)
       │
       v
GameController.handle_human_move(2)
       │
       ├─→ model.step(2)         # Enlève 2 allumettes
       ├─→ model.switch_player() # Change joueur
       │
       ├─→ Si IA → handle_ai_move()
       │
       v
GameView.update_view()
       │
       ├─→ canvas.delete("all")
       ├─→ draw_matches(nb)
       └─→ message_label.config(...)
```

### Changement de Langue

```
User hovers on "EN" → clicks "FR"
       │
       v
LanguageButton._change_lang("fr")
       │
       v
lang_manager.set_lang("fr")
       │
       ├─→ current_lang = "fr"
       │
       v
lang_manager._notify_observers()
       │
       ├─→ Pour chaque vue enregistrée :
       │       view.update_language()
       │
       v
HomeView.update_language()
├─→ title_label.config(text=get_text("title"))
├─→ card1.update_text(get_text("matchstick_game"))
└─→ ...
```

---

## 🎨 Design Patterns Utilisés

### 1. MVC (Model-View-Controller)
- **Modèle** : `game_model.py`, `player.py`
- **Vue** : Tout dans `views/`
- **Contrôleur** : `game_controller.py`

### 2. Singleton
- `LanguageManager` : instance unique partagée

### 3. Observer
- `LanguageManager` notifie les vues des changements

### 4. Strategy
- `Player`, `Human`, `AI` : différentes stratégies de jeu

### 5. State
- `MainApplication` : gère l'état (quelle vue afficher)

---

## 📊 Diagramme de Classes Simplifié

```
┌──────────────┐
│    Player    │
├──────────────┤
│ +play()      │
│ +win()       │
│ +lose()      │
└──────┬───────┘
       │
    ┌──┴──┐
    │     │
┌───▼──┐ ┌▼────┐
│Human │ │ AI  │
└──────┘ └─────┘

┌────────────────┐
│   GameModel    │
├────────────────┤
│ -nb            │
│ -player1       │
│ -player2       │
├────────────────┤
│ +step()        │
│ +is_game_over()│
└────────────────┘

┌─────────────────┐      ┌─────────────┐
│GameController   │─────▶│  GameModel  │
├─────────────────┤      └─────────────┘
│ +handle_move()  │
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │GameView │
    └─────────┘
```

---

## 🧪 Comment Ajouter une Nouvelle Langue

1. **Éditer `translations.py`** :
```python
TRANSLATIONS = {
    "en": {...},
    "fr": {...},
    "es": {  # Nouvelle langue
        "title": "Colección de Juegos",
        ...
    }
}
```

2. **Modifier `LanguageButton`** dans `home_view.py` :
```python
languages = [("EN", "en"), ("FR", "fr"), ("ES", "es")]
```

3. C'est tout ! Le système Observer met à jour automatiquement toutes les vues.

---

## 🚀 Comment Ajouter un Nouveau Jeu

1. **Créer le modèle** : `my_game_model.py`
2. **Créer le contrôleur** : `my_game_controller.py`
3. **Créer la vue** : `views/my_game_view.py`
4. **Ajouter dans `main.py`** :
```python
def on_game_selected(self, game_name):
    if game_name == "matchstick":
        self.show_matchstick_menu()
    elif game_name == "my_new_game":  # Nouveau
        self.show_my_game()
```
5. **Mettre à jour `home_view.py`** : activer la carte du jeu

---

## 💡 Bonnes Pratiques Respectées

✅ **Séparation des responsabilités** : MVC strict
✅ **DRY** : Pas de duplication (traductions centralisées)
✅ **Commentaires explicatifs** : Chaque fonction documentée
✅ **Type Hints** : Tous les paramètres et retours typés
✅ **Fonctions courtes** : < 20 lignes (Clean Code)
✅ **Noms explicites** : `handle_human_move()` vs `hm()`
✅ **Pattern Observer** : Changement de langue automatique

---

**Auteurs** : Victor Van Zieleghem & Ethan Nickels
**Projet** : IN252 - HENaLLux 2025-2026
