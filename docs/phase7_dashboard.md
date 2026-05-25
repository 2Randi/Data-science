<div align="center">

| [**← Phase 6**](phase6_machine_learning.md) | [**🏠 Architecture**](phase0_architecture.md) | &nbsp; |
| :---: | :---: | :---: |

</div>

# Phase 7 — Mise en Production : Dashboard Streamlit

> **Fichier :** `mise_en_production/dashboard.py`  
> **Lancement :** `uv run main.py`  
> **Données :** `data/projet.db` (SQLite alimenté par `sqlite_insert.py`)  
> **Modèles :** `data/modele_ml_reg.joblib` · `data/modele_eco_ols.joblib`

---

## Objectif

Présenter les résultats de toutes les phases dans une interface interactive et navigable,
adaptée à une démonstration académique, en suivant les bonnes pratiques du cours
*gestion_de_mise-en-production*.

---

## Lancement

```bash
uv run main.py
```

`main.py` gère automatiquement les trois étapes :
1. Création de `data/projet.db` si la base n'existe pas encore
2. Entraînement et sauvegarde des modèles si les fichiers `.joblib` sont absents
3. Lancement du dashboard Streamlit

---

## Structure des onglets (`st.tabs`)

| Onglet | Contenu |
|--------|---------|
| **Vue d'ensemble** | KPIs, distribution mensuelle, répartitions (Formule, Client, Lieu) |
| **Qualité des données** | Anomalies traitées par source + impact du nettoyage |
| **Analyse exploratoire** | `df.describe()`, distributions, corrélations, Hue Modality |
| **Économétrie (OLS)** | Résumé OLS, tests Gauss-Markov, table des coefficients |
| **Machine Learning** | Comparaison des modèles, feature importance, métriques |
| **Simulation & Recherche** | Recherche de dossiers + simulateur dual (ML + OLS) |

---

## Décisions techniques

| Décision | Justification |
|----------|--------------|
| `st.tabs()` | Navigation recommandée dans le cours |
| `@st.cache_data` | Performance — données chargées une seule fois |
| SQLite (`projet.db`) | Bonne pratique mise en production : données séparées du code |
| Checkboxes + `st.form` | Filtre activable par l'utilisateur, reset via session_state |
| Bouton "Toutes les données" | Réinitialise tous les filtres en un clic |
| `st.toggle` layout | Bascule entre affichage 1 et 2 colonnes pour tous les graphiques |
| Bloc `interpret-box` (CSS) | Interprétation pédagogique sous chaque graphique |

---

## Filtres globaux (sidebar)

Les filtres s'appliquent à toutes les pages simultanément :

- **Checkbox** pour activer un filtre (Année / Lieu / Contrat / Population)
- **`st.form`** avec multiselect pour la sélection des valeurs
- **Bouton "Toutes les données"** : réinitialise tous les checkboxes via `st.session_state`

---

## Hue Modality (Analyse exploratoire)

Sélecteur permettant de colorier les graphiques par une variable catégorielle.
Les colonnes disponibles sont **détectées automatiquement** :

```python
cols_cat = df_filtre.select_dtypes(exclude=['int64', 'float64']).columns.tolist()
```

Pour les colonnes à forte cardinalité (ex. Client avec 70+ valeurs), les modalités
sont regroupées automatiquement : **top 10 conservées, reste agrégé en "Autres"**.

---

## Statistiques descriptives (`df.describe`)

L'onglet *Analyse exploratoire* affiche un résumé statistique complet :

```python
# Variables numériques
df_filtre.describe().round(2)

# Variables catégorielles
df_filtre.select_dtypes(exclude=['int64', 'float64']).describe()
```

---

## Modèles de simulation

| Modèle | Cible d'entraînement | Back-transform |
|--------|-----------------------|----------------|
| GradientBoostingRegressor | `duree_totale_h` (brute) | aucune |
| LinearRegression (OLS) | `log(1 + duree_totale_h)` | `np.expm1()` |

Les deux modèles sont générés par `mise_en_production/train_and_save_models.py`
et sauvegardés au format `joblib`.
