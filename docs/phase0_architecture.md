# Architecture du Projet — Guide d'Exécution

> | [**Phase 1**](phase1_dossier.md) | [**Phase 2**](phase2_ressources.md) | [**Phase 3**](phase3_temps.md) | [**Phase 4**](phase4_integration.md) | [**Phase 4b**](phase4b_analyse_exploratoire.md) | [**Phase 5**](phase5_econometrie.md) | [**Phase 5b**](phase5b_analyse_multidimensionnelle.md) | [**Phase 6**](phase6_machine_learning.md) | [**Phase 7**](phase7_dashboard.md) |
> | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |

> **Projet :** Traitement de Données Big Data  
> **Université :** Université de Montpellier — Faculté d'Économie  
> **Equipe :**  
> Randriamisaina Tsiory-Fanomezana  
> SHIRALI POUR Amir

---

## 1. Environnement Technique

| Elément | Valeur |
|---------|--------|
| Gestionnaire Python | `uv` |
| Version Python | 3.11 |
| Lancement dashboard | `uv run main.py` |

### Packages principaux

```
pandas, numpy, matplotlib, seaborn, scipy, statsmodels,
scikit-learn, nbformat, nbconvert, ipykernel, streamlit
```

---

## 2. Inventaire des Données

### 2.1 Fichiers bruts

| Fichier | Lignes | Colonnes | Encoding | Séparateur | Particularité |
|---------|--------|----------|----------|------------|---------------|
| `data/dossier.csv` | ~101 234 | 17 | utf-8 | `,` | guillemets doubles imbriqués (voir ci-dessous) |
| `data/ressources.csv` | 389 353 | 9 | latin-1 | `,` | dates en DD/MM/YYYY |
| `data/temps.csv` | 431 598 | 5 | latin-1 | `,` | dates en YYYY/MM/DD |

#### Problème de format dans dossier.csv

Quand on a ouvert `dossier.csv` pour la première fois, on a vu deux problèmes de format
qui rendaient le fichier illisible avec `pd.read_csv()` classique :

1. **Toutes les valeurs entre guillemets** : chaque cellule du fichier était entourée
   de guillemets doubles, par exemple `"valeur"` au lieu de `valeur`.

2. **Noms de colonnes avec guillemets doubles** : les en-têtes avaient quatre guillemets,
   comme `""column1""`, `""column2""`, etc.

On a corrigé ces deux problèmes au début du notebook phase 1, avant toute autre analyse.
Le code de correction est commenté en détail dans la cellule concernée.

### 2.2 Fichiers produits (pipeline)

| Fichier | Produit par | Lignes |
|---------|-------------|--------|
| `data/dossier_nettoye.csv` | [Phase 1](phase1_dossier.md) | 98 935 |
| `data/ressources_nettoyees.csv` | [Phase 2](phase2_ressources.md) | 389 353 |
| `data/temps_nettoye.csv` | [Phase 3](phase3_temps.md) | 431 598 |
| `data/dataset_complet.csv` | [Phase 4](phase4_integration.md) | 98 935 |
| `data/projet.db` | `sqlite_insert.py` (phase 7) | — |

**Passage au SQLite :** jusqu'à la phase 4, on travaille avec des fichiers CSV.
A partir de la phase 7 (dashboard), les données sont chargées dans une base SQLite
(`data/projet.db`) pour faciliter les requêtes dans l'interface Streamlit.

### 2.3 Colonnes détaillées par source

#### `dossier_nettoye.csv` (98 935 × 17)

| Colonne | Type | NaN restants | Notes |
|---------|------|-------------|-------|
| `Numero_dossier_ID` | int64 | 0 | Clé primaire — unique après phase 1 |
| `Client` | object | 0 | Ex: C1, C2, ... C16 |
| `Formule` | object | 5 834 | NaN = ??? remplacés |
| `date.ouverture` | object | 0 | Format YYYY/MM/DD, plage 2021-2022 |
| `heure.ouverture` | object | 978 | NaN = 25:00:00 remplacés |
| `Matricule.de.traitement` | int64 | 0 | Clé étrangère vers ressources.Matricule |
| `Cause.intervention` | object | 973 | Ex: Accident, Panne mécanique, ... |
| `date.de.survenance` | object | 0 | Format YYYY/MM/DD, inférieure à date.ouverture |
| `Type.d.energie` | object | 970 | Diesel, Essence, Hybride, inconnu (conservé) |
| `Outil.d.assistance` | object | 0 | Ex: MCS, Higgins |
| `Assistance.ou.Administratif` | object | 9 773 | NaN = ??? remplacés |
| `TOP.D.R` | int64 | 0 | 0 ou 1 |
| `TOP.VR` | int64 | 0 | 0 ou 1 |
| `TOP.Rappat.valide` | int64 | 0 | 0 ou 1 |
| `TOP.Poursuite` | int64 | 0 | 0 ou 1 |
| `TOP.Recup` | int64 | 0 | 0 ou 1 |
| `TOP.Autres.Garanties` | int64 | 0 | 0 ou 1 |

#### `ressources_nettoyees.csv` (389 353 × 9)

| Colonne | Type | NaN | Notes |
|---------|------|-----|-------|
| `Matricule` | int64 | 0 | Clé primaire — 2 507 agents uniques |
| `Date.presence` | object | 0 | Format YYYY/MM/DD (converti en phase 2) |
| `Lieu.travail` | object | 0 | TELE ou SITE |
| `Population` | object | 0 | CAS ou CAC |
| `Site` | object | 0 | A, B, C, ... |
| `Type.de.contrat` | object | 0 | CDI, CDD, CDS |
| `Duree.travail` | float64 | 0 | Heures travaillées — min=0.017, max=23.42 |
| `Temps.travail` | int64 | 0 | 9 valeurs différentes (100, 80, 60, 70, 50...) |
| `Experience` | int64 | 0 | Jours cumulés d'expérience par agent |

#### `temps.csv` (431 598 × 5) — brut, avant nettoyage

| Colonne | Type | NaN | Notes |
|---------|------|-----|-------|
| `Numero.dossier` | int64 | 0 | Clé étrangère vers dossier.Numero_dossier_ID |
| `Matricule` | int64 | 0 | Clé étrangère vers ressources.Matricule |
| `Date.debut.traitement` | object | 0 | Format YYYY/MM/DD |
| `heure.debut.traitement` | object | 0 | Format HH:MM:SS |
| `duree.corrigee` | float64 | 47 471 | Durée en minutes — médiane=188, max=253 014 |

### 2.4 Clés de jointure entre sources

| Jointure | Clé gauche | Clé droite | Type |
|----------|------------|------------|------|
| dossier → temps | `Numero_dossier_ID` | `Numero.dossier` | LEFT JOIN |
| dossier → ressources | `Matricule.de.traitement` | `Matricule` | LEFT JOIN |
| temps → ressources | `Matricule` | `Matricule` | INNER JOIN |

- Dossiers absents de temps : 2 180
- Dossiers dans temps absents de dossier : 10 977
- Matricule dans dossier absent de ressources : 1

---

## 3. Plan de travail par phase

### [Phase 1](phase1_dossier.md) — Nettoyage `dossier.csv`

**Notebook :** `traitement_de_donnees/phase1_dossier_nettoyage.ipynb`
**Sortie :** `data/dossier_nettoye.csv` (98 935 × 17)

Anomalies traitées : doublons sur ID, format date, dossiers hors période, incohérence temporelle, heure 25:00:00 remplacée par NaN, valeurs ??? remplacées par NaN, matricule orphelin signalé.

---

### [Phase 2](phase2_ressources.md) — Nettoyage `ressources.csv`

**Notebook :** `traitement_de_donnees/phase2_ressources_nettoyage.ipynb`
**Sortie :** `data/ressources_nettoyees.csv` (389 353 × 9)

Anomalies traitées : conversion dates DD/MM vers ISO, plage temporelle vérifiée, valeurs aberrantes sur Duree.travail signalées, Temps.travail non constant documenté, doublons vérifiés, experience croissante vérifiée.

---

### [Phase 3](phase3_temps.md) — Nettoyage `temps.csv`

**Notebook :** `traitement_de_donnees/phase3_temps_nettoyage.ipynb`
**Sortie :** `data/temps_nettoye.csv`

| Code | Problème | Colonne | Décision |
|------|----------|---------|----------|
| C1 | 47 471 NaN dans duree.corrigee (11%) | `duree.corrigee` | Conservé avec NaN |
| C2 | Valeur max = 253 014 min (4 215 h) | `duree.corrigee` | Signalé, seuil > 1 440 min |
| C3 | Dates hors 2021-2022 | `Date.debut.traitement` | Supprimés |
| C4 | 10 977 dossiers dans temps absents de dossier | `Numero.dossier` | Signalé, conservé |
| C5 | 2 180 dossiers sans intervention temps | `Numero.dossier` | Signalé |
| C6 | Doublons Numero.dossier + Matricule | composite | Valides (plusieurs interventions) |
| C7 | Format heure | `heure.debut.traitement` | Vérifié regex HH:MM:SS |
| C8 | Matricules absents de ressources | `Matricule` | Quantifié et signalé |

---

### [Phase 4](phase4_integration.md) — Intégration et Contrôles

**Notebook :** `traitement_de_donnees/phase4_integration_sources.ipynb`
**Sortie :** `data/dataset_complet.csv`

```
4.1 Agrégation de temps par dossier (nb agents, durée totale, durée moyenne)
4.2 Agrégation de ressources par agent sur la période du dossier
4.3 Jointure principale (LEFT JOIN depuis dossier)
4.4 Vérification des NaN introduits par les jointures
4.5 Variables finales pour modélisation
4.6 Export dataset_complet.csv
```

---

### Analyse exploratoire (Phase 4b)

**Notebook :** `traitement_de_donnees/phase4b_analyse_exploratoire.ipynb`

Analyse faite après l'intégration : distributions, corrélations, boxplots par groupe.
Sert de base pour choisir les variables des phases 5 et 6.

---

### [Phase 5](phase5_econometrie.md) — Econométrie

**Notebook :** `econometrie/phase5_econometrie.ipynb`
**Analyse complémentaire :** `econometrie/phase5b_analyse_multidimensionnelle.ipynb`

**Variable dépendante :** `duree_totale_min`

| Variable | Source | Transformation |
|----------|--------|----------------|
| `Experience` | ressources | Numérique brut |
| `Duree.travail` | ressources | Numérique brut |
| `Lieu.travail` | ressources | Variable binaire (TELE=1, SITE=0) |
| `Type.de.contrat` | ressources | Variable binaire (CDI référence) |
| `Population` | ressources | Variable binaire |
| `nb_interventions` | agrégation temps | Numérique brut |
| `Cause.intervention` | dossier | Variable binaire |
| `Type.d.energie` | dossier | Variable binaire |
| `Formule` | dossier | A regrouper si trop de modalités |

```
5.1 Statistiques descriptives
5.2 Matrice de corrélation
5.3 Régression OLS simple (duree ~ Experience)
5.4 Régression OLS multiple
5.5 Tests des hypothèses : normalité, homoscédasticité, multicolinéarité, autocorrélation
5.6 Interprétation économétrique
```

---

### Analyse multidimensionnelle (Phase 5b)

**Notebook :** `econometrie/phase5b_analyse_multidimensionnelle.ipynb`

Après le modèle OLS principal, nous avons réalisé une analyse complémentaire pour
explorer les relations entre variables de façon plus visuelle : ACP, clustering,
visualisations multivariées. Ce travail nous a aidés à mieux interpréter les résultats
du modèle et à identifier des groupes d'agents aux comportements similaires.

---

### [Phase 6](phase6_machine_learning.md) — Machine Learning

**Notebook :** `machine_learning/phase6_machine_learning.ipynb`

**Tâche 1 — Régression** (prédire `duree_totale_min`) :
- Modèles : LinearRegression (base), RandomForestRegressor, GradientBoostingRegressor
- Métriques : RMSE, MAE, R²
- Validation croisée : KFold 5 plis

**Tâche 2 — Classification** (prédire `Cause.intervention`) :
- Modalités rares (< 1%) regroupées en 'Autres'
- Modèles : LogisticRegression (base), RandomForestClassifier, GradientBoostingClassifier
- Métriques : Accuracy, F1-macro, matrice de confusion

---

### [Phase 7](phase7_dashboard.md) — Dashboard Streamlit

**Fichier :** `mise_en_production/dashboard.py`
**Lancement :** `uv run main.py`
**Base de données :** `data/projet.db` (SQLite — généré par `sqlite_insert.py`)
**Modèles :** `data/modele_ml_reg.joblib` · `data/modele_eco_ols.joblib`

| Onglet | Contenu |
|--------|---------|
| Vue d'ensemble | KPIs, distributions, répartitions |
| Qualité des données | Anomalies avant/après nettoyage |
| Analyse exploratoire | df.describe(), sélecteur de couleur, corrélations |
| Econométrie (OLS) | Résumé OLS, tests Gauss-Markov, coefficients |
| Machine Learning | Comparaison des modèles, importance des variables |
| Simulation | Recherche de dossiers + simulateur ML+OLS |

---

## 5. Structure des notebooks

Chaque notebook suit la même organisation :

```
Section 0  — Imports + chargement des données + copie _original
Section 1  — Vue d'ensemble (info, types, anomalies par colonne)
Section 2+ — Une section par anomalie (Constat, Décision, Action, Vérification)
Section N-1 — Synthèse des transformations
Section N   — Export CSV
```
