# 🎮 Game Collection — Projet de Conception IA

> Collection de jeux avec agents d'Intelligence Artificielle à apprentissage autonome.  
> Développé dans le cadre du cursus **IN252** à l'**HENaLLux**.

---

## 📋 Table des Matières

- [Jeux disponibles](#-jeux-disponibles)
- [Architecture globale](#-architecture-globale)
- [Guide d'installation](#-guide-dinstallation--lancement)
- [Jeu des Allumettes](#-jeu-des-allumettes)
- [Cubee](#-cubee)
- [Pixel Kart](#-pixel-kart)
- [Tests](#-tests)
- [Auteurs](#-auteurs--crédits)

---

## 🕹️ Jeux disponibles

| Jeu | Statut | IA disponible |
|-----|--------|--------------|
| 🔥 **Jeu des Allumettes** | ✅ Complet | Q-Learning (V-Function) |
| 🎮 **Cubee** | ✅ Complet | Q-Learning + UI training |
| 🎲 **Pixel Kart** | ✅ V2 (IA Q-Learning) | Q-Learning entraînable depuis l'UI |

---

## 🏗️ Architecture globale

L'application démarre depuis `main.py` (racine) qui affiche la page d'accueil.
Chaque jeu possède son propre sous-dossier dans `games/` et expose une fonction `run_game()` appelée par l'accueil.

```
Projet_IA/
├── main.py                    # Point d'entrée — page d'accueil
├── language_manager.py        # Singleton de gestion de la langue (EN/FR)
├── translations.py            # Dictionnaire complet des traductions
├── views/
│   └── home_view.py           # Hub de sélection des jeux
├── games/
│   ├── allumette/             # Jeu des Allumettes
│   │   ├── main.py            # MatchstickGameApp + run_game()
│   │   ├── game_model.py
│   │   ├── game_controller.py
│   │   ├── player.py          # Player (random), Human, AI (Q-Learning)
│   │   └── views/
│   │       ├── matchstick_menu_view.py
│   │       ├── game_view.py
│   │       └── training_view.py
│   ├── cubee/                 # Cubee — jeu de territoire
│   │   ├── main.py            # CubeeApp + run_game() + train()
│   │   ├── game_model.py
│   │   ├── game_controller.py
│   │   ├── game_view.py       # Frame insérée dans CubeeApp
│   │   ├── player.py          # Player, Human, AI (Q-Learning)
│   │   ├── ai_train.py        # train_with_progress() pour l'UI
│   │   ├── views/
│   │   │   ├── menu_view.py   # Cartes Play / Train
│   │   │   └── training_view.py
│   │   └── dao/               # Persistance Q-table (SQLAlchemy)
│   └── pixel_kart/            # Pixel Kart — jeu de course
│       ├── main.py            # PixelKartApp + run_game()
│       ├── game_model.py      # Circuit, Kart, Race + DTOs
│       ├── game_controller.py
│       ├── player.py          # Human, RandomAI, QLearningAI
│       ├── ai_state.py        # encode_state + compute_reward + actions
│       ├── ai_train.py        # create_run + train + run_episode
│       ├── views/
│       │   ├── menu_view.py   # Cartes Play (Solo/IA/Humain) + Training
│       │   ├── race_view.py   # Course avec karts directionnels
│       │   └── training_view.py  # Configuration et suivi entraînement Q-learning
│       ├── editor/            # Éditeur de circuits
│       │   ├── map_editor.py
│       │   ├── frames.py
│       │   ├── map_dao.py
│       │   └── circuits.txt   # Circuits sauvegardés
│       └── dao/               # Persistance Q-table (SQLAlchemy 3 tables)
│           ├── base.py        # Base + PRAGMA foreign_keys=ON
│           ├── q_table.py     # Run / QValue / EpisodeLog (FK CASCADE)
│           ├── q_table_repository.py  # RAM-first avec dirty tracking
│           └── data/
│               ├── pixelkart.db     # Base SQLite (créée au 1er lancement)
│               └── README.md        # Schéma + requêtes utiles
├── tests/                     # Tests pytest (ai_state + e2e PixelKart)
└── requirements.txt
```

### Conventions partagées
- **MVC strict** : modèle, vue (Tkinter), contrôleur séparés dans tous les jeux
- **Fenêtre unique par jeu** (`tk.Tk`) avec swap de frames pour la navigation
- **Bouton Back en haut à gauche** de chaque vue pour revenir au menu ou à l'accueil
- **Système multilingue** FR/EN via `LanguageManager` (pattern Observer)
- **run_game()** : point d'entrée public de chaque module jeu
- **Persistance Q-table** : SQLAlchemy + SQLite (séparée par jeu : `cubee.db`, `pixelkart.db`)

---

## ⚙️ Guide d'installation & Lancement

### Prérequis
- **Python 3.10+**
- `tkinter` (inclus par défaut dans la plupart des distributions Python)

### Installation

```bash
# 1. Clonage du dépôt
git clone https://github.com/VVZ-Data/Projet_IA.git
cd Projet_IA

# 2. Activation de l'environnement virtuel
.\env\Scripts\activate          # Windows
# source env/bin/activate       # Linux/macOS

# 3. Installation des dépendances
pip install -r requirements.txt
```

### Lancement

```bash
python main.py
```

---

## 🔥 Jeu des Allumettes

Variante **Misère du Jeu de Nim** : le joueur qui retire la dernière allumette **perd**.

| Étape | Description |
|-------|-------------|
| **Initialisation** | 15 allumettes sur le plateau |
| **Déroulement** | Chaque joueur retire 1, 2 ou 3 allumettes à tour de rôle |
| **Victoire** | Le joueur qui prend la **dernière allumette perd** |

### Modes de jeu
- **vs IA 1 / IA 2** — Affrontez une IA entraînée
- **vs Random** — Mode détente contre un algorithme aléatoire

### Entraînement
| Paramètre | Valeur recommandée |
|-----------|-------------------|
| Nombre de parties | ≥ 100 000 |
| Learning Rate | `0.3` |
| Epsilon Decay | `5000` |

---

## 🎮 Cubee

Jeu de territoire : deux joueurs se déplacent sur une grille et capturent des cases.

### Modes de jeu
- **vs IA** — Humain contre IA Q-learning entraînée
- **vs Random** — Humain contre joueur aléatoire
- **vs Human** — Deux humains sur la même machine

Contrôles : flèches du clavier ou pavé directionnel à l'écran.

### Entraînement (UI dédiée)
Accessible depuis le menu Cubee → carte **🤖 Train AI**.
| Paramètre | Valeur par défaut |
|-----------|-------------------|
| Nombre de parties | `10 000` |
| Gamma (γ) | `0.9` |
| Learning rate (α) | `0.1` |
| Epsilon initial (ε) | `0.9` |
| Adversaire | Random ou Self-play (IA contre IA) |

L'entraînement affiche une barre de progression et un récapitulatif final (victoires, défaites, durée).

---

## 🎲 Pixel Kart

Course de karts sur une grille de pixels.  
Chaque kart possède une **position**, une **direction** (N/E/S/O) et une **vitesse** (-1 à 2, marche arrière incluse).

### Règles
| Terrain | Effet |
|---------|-------|
| 🟫 Route | Vitesse normale |
| 🟩 Herbe | Vitesse divisée par 2 |
| ⬛ Mur | Kart éliminé |
| 🟨 Ligne d'arrivée | Doit être franchie vers l'**EST**, après avoir touché le checkpoint opposé, pour compter un tour |

**Actions disponibles par tour :** Accélérer · Freiner · Tourner gauche · Tourner droite · Passer

### Modes de jeu
- **Solo** — Un seul humain pour s'entraîner sur le circuit
- **vs IA** — Humain contre IA Q-learning (random tant qu'aucun run n'est entraîné, exploitation de la Q-table sinon)
- **vs Humain** — Deux humains, chacun à son tour sur le même écran

### IA Q-Learning (V2)

L'IA apprend par renforcement à finir le circuit le plus vite possible. Caractéristiques :

- **État compact (5 caractères)** : 3 distances de "vision" (avant / gauche / droite, relatives à la direction du kart, saturées à 3 cases route), terrain courant (route/herbe), vitesse remappée. Total : ~512 états théoriques.
- **5 actions** encodées sur 1 caractère : `A`ccélérer, `B`raker, `L`eft, `R`ight, `P`ass.
- **Récompense dense** : coût-temps fixe + bonus vitesse + malus herbe + crash (-100) + bonus de tour (+50/+100/+200 selon avancement).
- **Anti-exploit ligne d'arrivée** : un tour ne compte que si le kart a visité la moitié opposée du circuit ("checkpoint"). Empêche les allers-retours sur la ligne.

### Entraînement (UI dédiée)

Accessible depuis le menu Pixel Kart → carte **🤖 Training**.

| Paramètre | Valeur par défaut |
|-----------|-------------------|
| Nom du run | `default` |
| Circuit | `Basic` (sélectionnable) |
| Nombre de tours | `1` |
| Épisodes | `10 000` |
| Gamma (γ) | `0.9` |
| Learning rate (α) | `0.1` |
| Epsilon start / end | `1.0` → `0.05` (décroissance linéaire) |

L'entraînement affiche :
- Une **barre de progression** mise à jour toutes les 500 épisodes (flush DB).
- Un **récapitulatif final** : nombre d'épisodes terminés, nombre de crashs, récompense moyenne sur la dernière fenêtre, durée totale.

Plusieurs runs peuvent coexister dans la même base : la course en mode "vs AI" charge automatiquement le **dernier run** créé.

### Persistance (DAO 3 tables)
- `runs` : un enregistrement par configuration d'entraînement (γ, α, ε, circuit, notes, date).
- `q_values` : valeurs Q apprises, clé composite `(run_id, state, action)`.
- `episode_log` : statistiques par épisode (récompense, ticks, terminé, crashed) pour tracer les courbes d'apprentissage.

`PRAGMA foreign_keys=ON` est activé à chaque connexion : supprimer un run efface automatiquement ses Q-values et ses logs (CASCADE).

### Éditeur de circuits
Accessible depuis le menu ou via "Open circuit editor".  
Circuits disponibles : Basic, Large, Petit, Masque, Basic inverse, Large inverse, TTT.

### Karts à l'écran
Chaque kart est affiché avec :
- Sa **couleur** unique (rouge, bleu, orange, violet…)
- Sa **lettre initiale** + une **flèche directionnelle** (▲ ▶ ▼ ◀)

---

## 🧪 Tests

La suite pytest couvre l'IA Pixel Kart (encodage d'état, récompense, scénarios end-to-end).

```bash
python -m pytest tests/ -v
```

| Fichier | Couverture |
|---------|------------|
| `tests/test_ai_state.py` | 26 tests : encodage d'état, distances saturées, directions relatives, récompense (vitesse / terrain / crash / tours), encodage des actions, timeout |
| `tests/test_pixel_kart_e2e.py` | 8 tests : modes Solo/Humain/IA, fallback RandomAI quand DB vide, sélection du dernier run, cycle complet entraînement → exploitation |

---

## 👥 Auteurs & Crédits

| Nom | GitHub |
|-----|--------|
| **Victor Van Zieghem** | [@VVZ-Data](https://github.com/VVZ-Data) |
| **Ethan Nickels** | [@Etrix425](https://github.com/Etrix425) |

**Institution** : HENaLLux (B3 Info)  
**Année Académique** : 2025–2026

---

> *Ce projet est réalisé à des fins pédagogiques. Tous droits réservés.*
