<div align="center">

| [**← Phase 5b**](phase5b_analyse_multidimensionnelle.md) | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 7 →**](phase7_dashboard.md) |
| :---: | :---: | :---: |

</div>

# Phase 6 — Machine Learning

> **Fichier notebook :** `machine_learning/phase6_machine_learning.ipynb`  
> **Données en entrée :** `data/dataset_complet.csv`  
> **Objectif :** Prédire la durée de traitement (régression) et la cause d'intervention (classification)

---

## Tâche 1 — Régression : prédire `duree_totale_h`

### Features sélectionnées (issues de Phase 5)

| Feature | Type |
|---------|------|
| `agent_experience_j` | numérique |
| `agent_duree_travail_j` | numérique |
| `agent_temps_travail_pct` | numérique |
| `delai_survenance_ouverture_j` | numérique |
| `nb_interventions` | numérique |
| `nb_agents_distincts` | numérique |
| `mois_ouverture` | numérique |
| `agent_lieu_travail` | catégoriel → OHE |
| `agent_contrat` | catégoriel → OHE |
| `agent_population` | catégoriel → OHE |
| `annee_ouverture` | catégoriel → OHE |

### Modèles comparés

| Modèle | Hyperparamètres |
|--------|----------------|
| LinearRegression | (baseline) |
| RandomForestRegressor | n_estimators=100, random_state=42 |
| GradientBoostingRegressor | n_estimators=100, random_state=42 |

### Métriques : RMSE, MAE, R²

---

## Tâche 2 — Classification : prédire `Cause.intervention`

### Preprocessing spécifique
- Regrouper les modalités rares (< 2%) en `Autres`
- LabelEncoder sur la cible

### Modèles comparés

| Modèle | Hyperparamètres |
|--------|----------------|
| LogisticRegression | max_iter=500 |
| RandomForestClassifier | n_estimators=100, random_state=42 |
| GradientBoostingClassifier | n_estimators=100, random_state=42 |

### Métriques : Accuracy, F1-macro, Matrice de confusion

---

## Décisions ML

### M1 — Séparation train/test
**Décision :** `train_test_split(test_size=0.2, random_state=42, stratify=y)` pour la classification.  
**Justification :** 80/20 est le standard. La stratification garantit la représentativité des classes rares.

### M2 — Pipeline sklearn
**Décision :** Utiliser `sklearn.pipeline.Pipeline` avec `ColumnTransformer`.  
**Justification :** Évite le data leakage (les transformations sont apprises sur train uniquement).

### M3 — Traitement des NaN dans les features
**Décision :** `SimpleImputer(strategy='median')` pour les numériques, `most_frequent` pour les catégoriels.  
**Justification :** Permet de conserver toutes les observations sans supprimer les NaN résiduels.

### M4 — Cross-validation
**Décision :** `KFold(n_splits=5)` pour la régression, `StratifiedKFold(n_splits=5)` pour la classification.  
**Justification :** 5-fold est standard. La version stratifiée garantit l'équilibre des classes.

### M5 — Pourquoi ces modèles et pas d'autres ?

Pour chaque tâche, nous avons sélectionné trois modèles en suivant une logique de complexité croissante :

**Modèle de référence (Régression linéaire / Régression logistique)**
C'est le modèle le plus simple, sans hyperparamètres. Il sert de point de comparaison : si un modèle complexe ne fait pas mieux que la régression linéaire, ce n'est pas la peine de l'utiliser.

**Random Forest**
Nous avons choisi Random Forest parce qu'il gère bien les relations non-linéaires entre variables, qu'il est robuste face à la multicolinéarité (problème identifié en phase 5 avec le VIF), et qu'il fournit directement l'importance des variables — ce qui nous permet de comparer avec les coefficients OLS. C'est aussi un des modèles centraux du cours de M. MICHEL.

**Gradient Boosting**
Le boosting construit les arbres de façon itérative en se concentrant sur les erreurs des arbres précédents, ce qui réduit le biais progressivement. Sur des données tabulaires comme les nôtres (features mixtes numériques + catégorielles), c'est généralement le modèle le plus performant. Nous l'avons inclus pour voir si l'amélioration par rapport au Random Forest justifiait la complexité supplémentaire.

**Ce que nous n'avons pas retenu et pourquoi :**
- *SVM* : trop lent sur 98 000 lignes, et moins interprétable.
- *KNN* : très sensible aux variables non normalisées et à la malédiction de la dimension.
- *Réseaux de neurones* : overfitting probable sur ce volume de données sans tuning approfondi — et hors du périmètre du projet.

---

## Plan d'exécution

```
Section 0  — Imports, chargement, fonctions utilitaires
Section 1  — Préparation des données (features, cibles, split)
Section 2  — Tâche 1 : Régression (3 modèles + comparaison)
Section 3  — Feature Importance (régression)
Section 4  — Tâche 2 : Classification (3 modèles + comparaison)
Section 5  — Matrice de confusion du meilleur modèle
Section 6  — Synthèse finale
```
