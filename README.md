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
- Python 3.8 ou supérieur → https://www.python.org/downloads/
- `tkinter` est inclus automatiquement avec Python

---

### Étape 1 — Télécharger le projet

1. Aller sur **https://github.com/VVZ-Data/Projet_IA**
2. Cliquer sur le bouton vert **"Code"**
3. Cliquer sur **"Download ZIP"**
4. **Extraire** le fichier ZIP téléchargé dans le dossier de votre choix

---

### Étape 2 — Ouvrir un terminal dans le dossier extrait

- **Windows** : ouvrir le dossier extrait → cliquer dans la barre d'adresse de l'explorateur → taper `cmd` → Entrée
- **ou** : clic droit dans le dossier → *"Ouvrir dans le terminal"*

---

### Étape 3 — Créer l'environnement virtuel

```bash
python -m venv env
```

---

### Étape 4 — Activer l'environnement virtuel

```bash
# Windows
env\Scripts\activate

# Unix / macOS
source env/bin/activate
```

> Vous devriez voir `(env)` apparaître au début de votre ligne de commande.

---

### Étape 5 — Installer les dépendances

```bash
pip install -r requirements.txt
```

---

### Étape 6 — Lancer le jeu

```bash
python main.py
```

---

## 🎲 Règles du jeu

1. La partie commence avec 15 allumettes.
2. Les joueurs sont mélangés aléatoirement au début de chaque partie.
3. À son tour, un joueur clique sur **Take 1**, **Take 2** ou **Take 3**.
4. Le joueur qui prend la **dernière allumette perd**.
5. Cliquez sur **Play Again** pour recommencer.

---

## 🧹 Qualité du code

Le code respecte :
- **PEP 8** (style Python standard)
- **Clean Code** : fonctions courtes, noms explicites
- **Type Hinting** sur toutes les fonctions
- **Docstrings** complètes sur toutes les classes et méthodes
- **Architecture MVC** stricte

---

## 👥 Auteurs

- **[Victor Van Zieleghem]**
- **[Ethan Nickels]**

---

## 📄 Licence

Projet académique — HENaLLux 2025-2026
