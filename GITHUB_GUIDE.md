# 📘 Guide Git/GitHub — Phases du projet Matchstick Game

Ce guide décrit chaque étape du workflow Git à suivre pendant le projet.

---

## 🚀 PHASE 0 — Initialisation du dépôt (Jour 1)

### Responsable : Un seul membre du binôme

```bash
# Créer le dossier et initialiser Git
mkdir matchstick-game && cd matchstick-game
git init

# Créer les fichiers de base
touch README.md .gitignore requirements.txt

# Premier commit
git add .
git commit -m "init: initialisation du projet Matchstick Game"

# Créer le dépôt sur GitHub (via l'interface web GitHub)
# Puis lier le repo local au repo distant
git remote add origin https://github.com/VOTRE_USERNAME/matchstick-game.git
git branch -M main
git push -u origin main
```

### L'autre membre du binôme clone le dépôt

```bash
git clone https://github.com/VOTRE_USERNAME/matchstick-game.git
cd matchstick-game
python -m venv env
source env/bin/activate   # ou env\Scripts\activate sur Windows
pip install -r requirements.txt
```

---

## 🌿 PHASE 1 — Développement de la Partie 1 : Jeu de base

### Workflow recommandé (pair-programming)

```bash
# Créer une branche pour la partie 1
git checkout -b feature/partie1-jeu-base

# Développer player.py, game_model.py, main.py...
# (En pair-programming : alterner driver et navigator)

# Committer régulièrement avec des messages clairs
git add player.py
git commit -m "feat(player): ajout classe Player avec propriété nb_games"

git add game_model.py
git commit -m "feat(model): ajout classe GameModel avec logique de jeu"

git add player.py
git commit -m "feat(player): ajout classe Human avec saisie console"
```

### Avant chaque session de travail

```bash
# Récupérer les modifications de l'équipe AVANT de coder
git pull --rebase origin feature/partie1-jeu-base
```

### Tests et merge vers main

```bash
# Tester le jeu en console
python main.py

# Une fois validé, retourner sur main et merger
git checkout main
git pull origin main
git merge feature/partie1-jeu-base
git push origin main
```

---

## 🖥️ PHASE 2 — Développement de la Partie 2 : Interface graphique (MVC)

```bash
# Créer une nouvelle branche
git checkout -b feature/partie2-interface-mvc

# Développer game_view.py et game_controller.py
git add game_view.py
git commit -m "feat(view): ajout GameView avec canvas et boutons d'action"

git add game_controller.py
git commit -m "feat(controller): ajout GameController — gestion des mouvements"

git add game_model.py
git commit -m "refactor(model): renommage Game → GameModel + méthodes utilitaires"

# Mise à jour du README et requirements
git add README.md requirements.txt
git commit -m "docs: mise à jour README avec instructions d'installation"
```

### Résolution de conflits (si nécessaire)

```bash
# Après un git pull qui génère des conflits
git pull --rebase origin feature/partie2-interface-mvc

# Git vous indiquera les fichiers en conflit
# Ouvrez-les, résolvez les conflits marqués par <<<<<<< HEAD
# Puis :
git add fichier_resolu.py
git rebase --continue
```

### Merge vers main après validation

```bash
git checkout main
git pull origin main
git merge feature/partie2-interface-mvc
git push origin main
```

---

## 🤖 PHASE 3 — Développement de la Partie 3 : IA (Apprentissage par renforcement)

```bash
# Créer une branche dédiée à l'IA
git checkout -b feature/partie3-ia-rl

# Développer ai_player.py (classe AI héritant de Player)
git add ai_player.py
git commit -m "feat(ai): ajout classe AI avec v_function et méthode exploit()"

git add ai_player.py
git commit -m "feat(ai): implémentation méthode train() avec TD-learning"

git add ai_player.py
git commit -m "feat(ai): ajout next_epsilon() pour la politique d'exploration"

# Une fois testée et validée
git checkout main
git merge feature/partie3-ia-rl
git push origin main
```

---

## 📦 PHASE DEADLINES — Vérifications avant remise

```bash
# S'assurer que main est propre et fonctionnelle
git checkout main
git status  # Doit afficher "nothing to commit, working tree clean"

# Vérifier que le code passe Pylint
pylint player.py game_model.py game_view.py game_controller.py main.py

# Vérifier que requirements.txt est à jour
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: mise à jour requirements.txt"
git push origin main
```

---

## 📋 Bonnes pratiques de commit

| Type | Usage | Exemple |
|------|-------|---------|
| `feat` | Nouvelle fonctionnalité | `feat(player): ajout méthode win()` |
| `fix` | Correction de bug | `fix(model): correction step() avec nb=1` |
| `refactor` | Refactoring sans changement de comportement | `refactor(view): extraction _create_buttons()` |
| `docs` | Documentation | `docs: mise à jour README` |
| `chore` | Tâches de maintenance | `chore: mise à jour .gitignore` |
| `test` | Tests unitaires | `test: ajout tests pour GameModel` |

---

## ✅ Checklist avant chaque push vers main

- [ ] Le code tourne sans erreur (`python main.py`)
- [ ] Pylint score > 8/10
- [ ] Toutes les fonctions/méthodes ont une docstring complète
- [ ] requirements.txt est à jour
- [ ] README est à jour
- [ ] Aucun fichier `.env` ou `env/` n'est commité

---

## 🔗 Ressources utiles

- Tutoriel interactif Git : https://learngitbranching.js.org/?locale=fr_FR
- Convention de commits : https://www.conventionalcommits.org/fr/
