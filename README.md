<<<<<<< HEAD
# Projet_IA
mettre en œuvre de l’apprentissage par renforcement à travers trois exemples de jeux accompagnés d’une interface graphique simple via la librairie Tkinter.
=======
# 🎮 Matchstick Game — Jeu des Allumettes

Jeu des allumettes développé en Python avec interface graphique Tkinter, dans le cadre du cours **IN252 - Projet de conception IA** (HENaLLux).

---

## 📋 Description

Le jeu des allumettes se joue à deux. Au départ, un certain nombre d'allumettes sont posées sur la table. Chaque joueur retire à son tour 1, 2 ou 3 allumettes. **Le joueur qui prend la dernière allumette perd.**

### Types de joueurs disponibles
- **Human** : joueur humain interagissant via l'interface graphique
- **Player (Random)** : joueur aléatoire choisissant 1, 2 ou 3 allumettes au hasard

---

## 🏗️ Architecture MVC

```
matchstick_game/
├── main.py               # Point d'entrée
├── player.py             # Classes Player et Human (Modèle)
├── game_model.py         # Classe GameModel — logique du jeu (Modèle)
├── game_view.py          # Classe GameView — interface Tkinter (Vue)
├── game_controller.py    # Classe GameController — lien Modèle/Vue (Contrôleur)
├── requirements.txt      # Dépendances Python
├── .gitignore            # Fichiers ignorés par Git
└── README.md             # Ce fichier
```

---

## ⚙️ Installation

### Prérequis
- Python 3.8 ou supérieur
- `tkinter` (inclus dans la bibliothèque standard Python)

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/matchstick-game.git
cd matchstick-game

# 2. Créer et activer un environnement virtuel
python -m venv env

# Windows
env\Scripts\activate

# Unix / macOS
source env/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## ▶️ Lancement

```bash
python main.py
```

---

## 🎲 Règles du jeu

1. La partie commence avec 15 allumettes (modifiable dans `main.py`).
2. Les joueurs sont mélangés aléatoirement au début de chaque partie.
3. À son tour, un joueur clique sur **Take 1**, **Take 2** ou **Take 3**.
4. Le joueur qui prend la **dernière allumette perd**.
5. Cliquez sur **Play Again** pour recommencer.

---

## 🧹 Qualité du code

Le code respecte :
- **PEP 8** (style Python standard)
- **Clean Code** : fonctions courtes (< 20 lignes), noms explicites
- **Type Hinting** sur toutes les fonctions
- **Docstrings** complètes sur toutes les classes et méthodes
- **Architecture MVC** stricte

Vérification avec Pylint :
```bash
pylint player.py game_model.py game_view.py game_controller.py main.py
```

---

## 🤖 IA Générative

Certaines docstrings ou portions de code ont pu être assistées par IA.
Conformément aux consignes, ces éléments sont marqués `[IA-NOM]` en première ligne de leur spécification.

---

## 👥 Auteurs

- **[Prénom Nom 1]**
- **[Prénom Nom 2]**

---

## 📄 Licence

Projet académique — HENaLLux 2025-2026
>>>>>>> 36c9428 (feat: initialisation du projet)
