# 🎮 Matchstick Game — Projet de Conception IA

> Jeu des Allumettes (variante Misère du Jeu de Nim) avec agents d'Intelligence Artificielle à apprentissage autonome.  
> Développé dans le cadre du cursus **IN252** à l'**HENaLLux**.

---

## 📋 Table des Matières

- [Description du Jeu](#-description-du-jeu)
- [Fonctionnalités Clés](#-fonctionnalités-clés)
- [Architecture Logicielle (MVC)](#-architecture-logicielle-mvc)
- [Intelligence Artificielle & Apprentissage](#-intelligence-artificielle--apprentissage)
- [Guide d'Installation & Lancement](#-guide-dinstallation--lancement)
- [Manuel d'Utilisation](#-manuel-dutilisation)
- [Qualité du Code & Standards](#-qualité-du-code--standards)
- [Auteurs & Crédits](#-auteurs--crédits)

---

## 📖 Description du Jeu

Le jeu des allumettes est un **jeu de duel mathématique symétrique** :

| Étape | Description |
|-------|-------------|
| **Initialisation** | Un nombre défini d'allumettes est disposé sur le plateau. |
| **Déroulement** | Chaque joueur retire, à tour de rôle, **1, 2 ou 3 allumettes**. |
| **Victoire** | Variante **Misère** : le joueur qui retire la **dernière allumette perd**. |

---

## ✨ Fonctionnalités Clés

### 🌍 Système Multilingue Dynamique
Bascule instantanée entre **Français** et **Anglais** sans redémarrage, via un gestionnaire d'états centralisé.

### 🎮 Modes de Jeu Versatiles
- **Humain vs IA** — Testez vos capacités contre un modèle entraîné.
- **Humain vs Random** — Mode détente contre un algorithme stochastique.
- **IA vs IA** — Observez deux agents s'affronter pour valider la convergence des stratégies.

### 🤖 Laboratoire d'Entraînement
- Configuration granulaire des hyperparamètres (**Epsilon**, **Learning Rate**).
- Entraînement dissocié des agents (IA 1 ou IA 2).
- Monitoring en temps réel via barre de progression et statistiques de performance.
- Système de **sauvegarde persistante (JSON)** pour conserver les modèles les plus performants.

---

## 🏗️ Architecture Logicielle (MVC)

Le projet adopte une **séparation stricte des préoccupations** grâce au patron Modèle-Vue-Contrôleur.

```
Projet_IA/
├── main.py
├── game_model.py        # Modèle — état du jeu & règles métier
├── player.py            # Modèle — comportements de décision (Random, Q-Learning)
├── game_controller.py   # Contrôleur — médiateur Vue ↔ Modèle
├── views/
│   ├── home_view.py     # Hub de navigation principal
│   ├── game_view.py     # Rendu graphique Canvas des allumettes
│   └── training_view.py # Dashboard de contrôle de l'apprentissage
├── AI_save_1.json       # Sauvegarde persistante agent 1
├── AI_save_2.json       # Sauvegarde persistante agent 2
└── requirements.txt
```

### 1. Le Modèle (`game_model.py`, `player.py`)
Encapsule l'état du système et les règles métier.
- **`GameModel`** — Gère le stock d'allumettes et la validation des coups.
- **`Player` & `AI`** — Définissent les comportements de décision, de l'aléatoire simple au Q-Learning complexe.

### 2. La Vue (`views/`)
Modules Tkinter indépendants pour une interface moderne et réactive.
- **`home_view.py`** — Hub de navigation principal.
- **`game_view.py`** — Rendu graphique dynamique des allumettes sur Canvas.
- **`training_view.py`** — Dashboard de contrôle de l'apprentissage.

### 3. Le Contrôleur (`game_controller.py`)
Agit comme **médiateur**, interceptant les événements utilisateurs de la Vue pour mettre à jour le Modèle.

---

## 🤖 Intelligence Artificielle & Apprentissage

L'agent intelligent repose sur l'algorithme de **Q-Learning** (Reinforcement Learning).

| Composant | Description |
|-----------|-------------|
| **V-Function** | Dictionnaire associant chaque état (nb d'allumettes) à une valeur de récompense attendue. |
| **Politique ε-Greedy** | Alternance entre **Exploration** (coups aléatoires) et **Exploitation** (meilleures connaissances). |
| **Apprentissage TD** | Valeurs mises à jour après chaque action en fonction du résultat (victoire / défaite). |
| **Epsilon Decay** | Réduction progressive du taux d'exploration pour stabiliser la stratégie optimale. |

---

## ⚙️ Guide d'Installation & Lancement

### Prérequis
- **Python 3.8+**
- `tkinter` (inclus par défaut dans la plupart des distributions Python)

### Installation

```bash
# 1. Clonage du dépôt
git clone https://github.com/VVZ-Data/Projet_IA.git
cd Projet_IA

# 2. Installation des dépendances de développement
pip install -r requirements.txt
```

### Lancement

```bash
python main.py
```

---

## 🎲 Manuel d'Utilisation

### Navigation
1. **Accueil** — Sélectionnez *"Jeu des Allumettes"*. Utilisez le bouton **EN/FR** pour changer la langue.
2. **Menu** — Choisissez entre *"Jouer"* (immédiat) ou *"Entraîner"* (configuration).

### Sessions d'Entraînement

Pour obtenir une IA imbattable, suivez ces recommandations :

| Paramètre | Valeur recommandée | Raison |
|-----------|-------------------|--------|
| **Nombre de parties** | ≥ 100 000 | Convergence assurée |
| **Learning Rate** | `0.3` | Équilibre vitesse / stabilité |
| **Epsilon Decay** | `5000` | Exploration suffisante en début d'entraînement |

> **💾 Sauvegarde** — Les résultats ne sont persistés dans `AI_save_1` ou `AI_save_2` que sur **validation manuelle** après analyse des résultats.

---

## 🧹 Qualité du Code & Standards

| Standard | Détail |
|----------|--------|
| ✅ **Architecture MVC** | Découplage total logique / interface. |
| ✅ **Pattern Singleton** | Gestion unique du `LanguageManager`. |
| ✅ **Pattern Observer** | Notification automatique des changements de langue à toutes les vues actives. |
| ✅ **Type Hinting** | Utilisation systématique des indices de type pour une meilleure robustesse. |
| ✅ **Conformité PEP 8** | Code clair, nommé explicitement et documenté via Docstrings. |

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