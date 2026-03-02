# 🎮 Matchstick Game — Jeu des Allumettes

Application Python multi-jeux avec interface graphique Tkinter et système multilingue (FR/EN).
Développé dans le cadre du cours **IN252 - Projet de conception IA** (HENaLLux).

---

## 📋 Description

Le jeu des allumettes se joue à deux. Au départ, un certain nombre d'allumettes sont posées sur la table. 
Chaque joueur retire à son tour 1, 2 ou 3 allumettes. **Le joueur qui prend la dernière allumette perd.**

### Types de joueurs disponibles
- **Human** : joueur humain interagissant via l'interface graphique
- **AI** : intelligence artificielle entraînable par renforcement (Q-learning)
- **Player (Random)** : joueur aléatoire

---

## ✨ Fonctionnalités

- 🌍 **Interface multilingue** (Français / English) avec changement à la volée
- 🎮 **3 modes de jeu** : Humain vs IA, Humain vs Random, IA vs IA
- 🤖 **Entraînement d'IA** par apprentissage par renforcement avec :
  - Configuration des paramètres (nombre de parties, learning rate, epsilon decay)
  - Barre de progression en temps réel
  - Analyse des résultats et statistiques détaillées
  - Sauvegarde/chargement des modèles entraînés
- 🎨 **Interface moderne** avec design épuré et animations
- 📊 **Architecture MVC** stricte avec séparation modèle/vue/contrôleur

---

## 🏗️ Architecture

```
matchstick_refactored/
├── main.py                  # Point d'entrée et navigation
├── translations.py          # Dictionnaire de traductions FR/EN
├── language_manager.py      # Gestionnaire de langue (Singleton)
├── player.py                # Classes Player, Human, AI
├── game_model.py            # Logique du jeu (Modèle)
├── game_controller.py       # Contrôleur MVC
├── views/
│   ├── __init__.py
│   ├── home_view.py         # Page d'accueil (sélection de jeux)
│   ├── matchstick_menu_view.py  # Menu (Jouer / Entraîner)
│   ├── game_view.py         # Interface de jeu
│   └── training_view.py     # Interface d'entraînement
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### Prérequis
- Python 3.8 ou supérieur → https://www.python.org/downloads/
- `tkinter` (inclus avec Python)

### Étapes

#### 1. Télécharger le projet

```bash
git clone https://github.com/VVZ-Data/Projet_IA.git
cd Projet_IA
```

Ou télécharger le ZIP depuis GitHub → Code → Download ZIP

#### 2. Créer l'environnement virtuel (optionnel mais recommandé)

```bash
python -m venv env

# Windows
env\Scripts\activate

# Unix / macOS
source env/bin/activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Lancer l'application

```bash
python main.py
```

---

## 🎲 Guide d'utilisation

### Page d'accueil
- Cliquez sur **"Jeu des Allumettes"** pour y jouer
- Changez de langue avec le bouton **EN/FR** en haut à droite

### Menu du jeu
- **Jouer** : Choisissez "vs IA" ou "vs Random"
- **Entraîner l'IA** : Lancez un entraînement personnalisé

### Pendant le jeu
- Cliquez sur **"Take 1"**, **"Take 2"** ou **"Take 3"** pour prendre des allumettes
- Le joueur qui prend la **dernière allumette perd**
- Cliquez sur **"Rejouer"** pour une nouvelle partie
- Cliquez sur **"Quitter"** pour retourner au menu

### Entraînement de l'IA
1. Configurez les paramètres :
   - **Nombre de parties** : plus il y en a, meilleure est l'IA (100 000 recommandé)
   - **Diminution epsilon** : fréquence de passage exploitation/exploration (tous les 5000)
   - **Learning rate** : vitesse d'apprentissage (0.3 recommandé)
2. Cliquez sur **"Lancer l'Entraînement"**
3. Attendez la fin (barre de progression)
4. Analysez les résultats affichés
5. Les modèles entraînés sont sauvegardés automatiquement

---

## 🧹 Qualité du code

Le code respecte :
- ✅ **PEP 8** (style Python standard)
- ✅ **Clean Code** : fonctions < 20 lignes, noms explicites, DRY
- ✅ **Type Hinting** complet
- ✅ **Docstrings** détaillées sur TOUTES les fonctions/classes/méthodes
- ✅ **Commentaires explicatifs** en français dans tout le code
- ✅ **Architecture MVC** avec séparation stricte des responsabilités
- ✅ **Pattern Observer** pour le système de traductions
- ✅ **Pattern Singleton** pour le gestionnaire de langue

---

## 🤖 Algorithme d'apprentissage

L'IA utilise **Q-Learning** (apprentissage par renforcement) :

- **V-function** : dictionnaire {état → valeur}
- **Exploration/Exploitation** : politique ε-greedy
- **TD-Learning** : mise à jour des valeurs après chaque partie
- **Epsilon decay** : réduction progressive de l'exploration

Stratégie optimale découverte par l'IA : laisser toujours un multiple de 4 allumettes à l'adversaire.

---

## 👥 Auteurs

- **Victor Van Zieleghem**
- **Ethan Nickels**

Groupe : B3 Info — HENaLLux 2025-2026

---

## 📄 Licence

Projet académique — Tous droits réservés
