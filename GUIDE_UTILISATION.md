# 🚀 Guide Rapide d'Utilisation

## Lancement

```bash
python main.py
```

---

## Navigation dans l'Application

```
┌─────────────────────────────────────────────────────┐
│           PAGE D'ACCUEIL                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │   🔥     │  │   🎮     │  │   🎲     │         │
│  │ Jeu des  │  │ Bientôt  │  │ Bientôt  │         │
│  │Allumettes│  │Disponible│  │Disponible│         │
│  └────┬─────┘  └──────────┘  └──────────┘         │
│       │                                             │
│       v                                             │
│  ┌─────────────────────────────────┐               │
│  │   MENU JEU DES ALLUMETTES       │               │
│  │  ┌───────────┐  ┌────────────┐  │               │
│  │  │  🎮 JOUER │  │🤖 ENTRAÎNER│  │               │
│  │  └─────┬─────┘  └──────┬─────┘  │               │
│  └────────┼────────────────┼────────┘               │
│           │                │                         │
│           v                v                         │
│  ┌────────────────┐  ┌─────────────────────┐       │
│  │  vs IA         │  │ Configuration        │       │
│  │  vs Random     │  │ - Nb parties         │       │
│  └────┬───────────┘  │ - Learning rate      │       │
│       │              │ - Epsilon decay      │       │
│       v              └──────┬───────────────┘       │
│  ┌──────────────┐          │                        │
│  │   PARTIE     │          v                        │
│  │  EN COURS    │    ┌──────────────────┐          │
│  │              │    │  ENTRAÎNEMENT    │          │
│  │ Take 1/2/3   │    │  [████████░░]80% │          │
│  └──────────────┘    └──────────────────┘          │
└─────────────────────────────────────────────────────┘
```

---

## Fonctionnalités Clés

### 🌍 Changer de Langue

1. Passez la souris sur le bouton **EN** (ou **FR**) en haut à droite
2. Cliquez sur la langue souhaitée
3. Toute l'interface se met à jour instantanément

### 🎮 Jouer contre l'IA

1. Page d'accueil → **Jeu des Allumettes**
2. **Jouer** → **vs IA**
3. Cliquez sur **Take 1**, **Take 2** ou **Take 3** pour jouer
4. L'IA répond automatiquement
5. **Le dernier à prendre une allumette perd !**

### 🤖 Entraîner l'IA

1. Page d'accueil → **Jeu des Allumettes**
2. **Entraîner l'IA**
3. Configurez les paramètres :
   - **100 000 parties** = entraînement long mais efficace
   - **Learning rate 0.3** = vitesse d'apprentissage moyenne
   - **Epsilon decay 5000** = équilibre exploration/exploitation
4. Cliquez sur **Lancer l'Entraînement**
5. Attendez la fin (peut prendre quelques minutes)
6. Analysez les résultats affichés
7. Les modèles sont sauvegardés dans `AI_save_1` et `AI_save_2`

---

## Architecture des Fichiers

```
matchstick_game_final/
├── main.py                    # 🚀 Point d'entrée - LANCEZ CE FICHIER
├── translations.py            # 🌍 Toutes les traductions FR/EN
├── language_manager.py        # 🔄 Gestion de la langue courante
├── player.py                  # 👤 Classes Player, Human, AI
├── game_model.py              # 🎮 Logique du jeu
├── game_controller.py         # 🎛️ Contrôleur MVC
├── views/                     # 📱 Toutes les interfaces graphiques
│   ├── home_view.py           #    Page d'accueil
│   ├── matchstick_menu_view.py#    Menu du jeu
│   ├── game_view.py           #    Interface de jeu
│   └── training_view.py       #    Interface d'entraînement
├── AI_save_1                  # 💾 Sauvegarde IA 1 (généré après entraînement)
├── AI_save_2                  # 💾 Sauvegarde IA 2 (généré après entraînement)
├── README.md                  # 📖 Documentation complète
└── requirements.txt           # 📦 Dépendances Python
```

---

## Raccourcis Clavier

- **Esc** : Retour (sur certaines pages)
- **Alt+F4** : Fermer l'application

---

## Dépannage

### L'application ne se lance pas

```bash
# Vérifier la version de Python
python --version  # Doit être >= 3.8

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur "No module named 'tkinter'"

```bash
# Windows : tkinter est inclus avec Python
# Réinstallez Python depuis python.org

# Linux
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

### L'entraînement est trop lent

- Réduisez le nombre de parties (10 000 au lieu de 100 000)
- L'entraînement s'exécute en arrière-plan, ne fermez pas la fenêtre

---

## Astuces

💡 **Pour une IA performante** : Entraînez avec au moins 100 000 parties

💡 **Stratégie gagnante** : Toujours laisser un multiple de 4 allumettes à l'adversaire

💡 **Sauvegarde automatique** : Les IA entraînées sont sauvegardées automatiquement

💡 **Tester votre IA** : Après l'entraînement, jouez contre elle pour voir si elle a appris !

---

## Support

Pour toute question ou bug, contactez :
- Victor Van Zieleghem
- Ethan Nickels

Projet académique HENaLLux 2025-2026
