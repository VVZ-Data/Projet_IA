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
- [Auteurs](#-auteurs--crédits)

---

## 🕹️ Jeux disponibles

| Jeu | Statut | IA disponible |
|-----|--------|--------------|
| 🔥 **Jeu des Allumettes** | ✅ Complet | Q-Learning (V-Function) |
| 🎮 **Cubee** | ✅ Complet | Q-Learning |
| 🎲 **Pixel Kart** | 🚧 V1 (IA random) | IA random — Q-Learning à venir |

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
│   │   ├── main.py            # run_game()
│   │   ├── game_model.py
│   │   ├── game_controller.py
│   │   ├── game_view.py
│   │   └── player.py
│   └── pixel_kart/            # Pixel Kart — jeu de course
│       ├── main.py            # PixelKartApp + run_game()
│       ├── game_model.py      # Circuit, Kart, Race + DTOs
│       ├── game_controller.py
│       ├── player.py          # Human, RandomAI
│       ├── views/
│       │   ├── menu_view.py   # Menu Play / Training
│       │   └── race_view.py   # Course avec karts directionnels
│       └── editor/            # Éditeur de circuits
│           ├── map_editor.py
│           ├── frames.py
│           ├── map_dao.py
│           └── circuits.txt   # Circuits sauvegardés
└── requirements.txt
```

### Conventions partagées
- **MVC strict** : modèle, vue (Tkinter), contrôleur séparés dans tous les jeux
- **Fenêtre unique par jeu** (`tk.Tk`) avec swap de frames pour la navigation
- **Bouton Back en haut à gauche** de chaque vue pour revenir au menu ou à l'accueil
- **Système multilingue** FR/EN via `LanguageManager` (pattern Observer)
- **run_game()** : point d'entrée public de chaque module jeu

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

### Mode de jeu
- Humain vs IA (Q-Learning)
- Contrôles : flèches du clavier ou pavé directionnel

---

## 🎲 Pixel Kart

Course de karts sur une grille de pixels.  
Chaque kart possède une **position**, une **direction** (N/E/S/O) et une **vitesse** (-1 à 2).

### Règles
| Terrain | Effet |
|---------|-------|
| 🟫 Route | Vitesse normale |
| 🟩 Herbe | Vitesse divisée par 2 |
| ⬛ Mur | Kart éliminé |
| 🟨 Ligne d'arrivée | Doit être franchie vers l'**EST** pour compter un tour |

**Actions disponibles par tour :** Accélérer · Freiner · Tourner gauche · Tourner droite · Passer

### Modes de jeu
- **vs IA** — Humain + IA random (IA Q-Learning prévue en V2)
- **vs Humain** — Deux humains, chacun à son tour sur le même écran

### Éditeur de circuits
Accessible depuis le menu ou via "Open circuit editor".  
Circuits disponibles : Basic, Large, Petit, Masque, Basic inverse, Large inverse.

### Karts à l'écran
Chaque kart est affiché avec :
- Sa **couleur** unique (rouge, bleu, orange, violet…)
- Sa **lettre initiale** + une **flèche directionnelle** (▲ ▶ ▼ ◀)

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
