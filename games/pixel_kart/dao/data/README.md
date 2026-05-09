# PixelKart — Q-table runs

Base SQLite : `pixelkart.db` (créée automatiquement au premier lancement).

## Structure

| Table | Rôle |
|---|---|
| `runs` | Un enregistrement par configuration d'entraînement (γ, α, ε, circuit, nb épisodes faits, notes). |
| `q_values` | Valeurs Q pour chaque triplet (run, état, action). FK CASCADE sur `runs`. |
| `episode_log` | Statistiques par épisode (récompense totale, ticks, fini, crashed) pour tracer les courbes d'apprentissage. FK CASCADE sur `runs`. |

## Inspection rapide

Lister les runs :
```sql
SELECT id, name, gamma, alpha, episodes_done, circuit_name, created_at
FROM runs
ORDER BY created_at DESC;
```

Voir l'évolution de la récompense moyenne sur les 1000 derniers épisodes d'un run :
```sql
SELECT AVG(total_reward) AS avg_reward
FROM episode_log
WHERE run_id = ?
ORDER BY episode_num DESC
LIMIT 1000;
```

Compter les états visités d'un run :
```sql
SELECT COUNT(DISTINCT state) AS distinct_states
FROM q_values
WHERE run_id = ?;
```

## Suppression d'un run

```sql
DELETE FROM runs WHERE id = ?;
-- Les Q-values et episode_log sont supprimés en cascade (PRAGMA foreign_keys=ON).
```

## Note pour le binôme

Cette base est versionnée sur git pour partager les modèles entraînés.
Toute modification (lancement d'un nouveau run, suppression, etc.) doit être
commitée avec un message clair. Les runs de test peuvent être purgés
régulièrement pour ne garder que ceux pertinents pour la défense orale.
