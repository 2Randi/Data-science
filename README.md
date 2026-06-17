![Logo Université de Montpellier](docs/logo_um.png)

# Projet Data

DU Big Data, Data Science et Analyse des Risques sous Python

Université de Montpellier - Faculté d'Économie - 2025-2026

---

## Equipe

| Membre | Role |
|--------|------|
| RANDRIAMISAINA Tsiory | Traitement de données, Econométrie |
| SHIRALI POUR Amir | Traitement de données, Machine Learning |

Nous avons travaillé ensemble sur la mise en production (phase 7).

## Encadrants

| Module | Professeur |
|--------|------------|
| Traitement de données | Samuel STOCKSIEKER |
| Econométrie | Samuel STOCKSIEKER |
| Machine Learning | Gilles MICHEL |
| Mise en Production | Nicolas BARTHES |

---

## Description

Pour ce projet, nous avons analysé le système de gestion de dossiers d'un centre d'assistance.
Notre travail couvre tout le pipeline data science : nettoyage des données brutes, intégration
des sources, modélisation économétrique (OLS), machine learning et mise en production
avec un dashboard Streamlit interactif.

**Données :** 3 fichiers CSV (dossier, ressources, temps) — environ 98 000 dossiers sur 2021-2022
**Variable cible :** `duree_totale_h` — durée totale de traitement d'un dossier (en heures)

---

## Lancement du dashboard

Une seule commande suffit :

```bash
uv run main.py
```

Cette commande prend en charge automatiquement toutes les étapes :
1. Création de l'environnement virtuel et installation des dépendances
2. Création de la base de données SQLite (si elle n'existe pas encore)
3. Entrainement et sauvegarde des modèles (si les fichiers `.joblib` sont absents)
4. Lancement du dashboard Streamlit

Vous n'avez pas besoin de configurer quoi que ce soit manuellement.

---

## Structure du projet

```
projet_big_data/
|-- data/                            # Données brutes et fichiers produits
|   |-- dossier.csv                  # Source brute 1
|   |-- ressources.csv               # Source brute 2
|   |-- temps.csv                    # Source brute 3
|   |-- dossier_nettoye.csv          # Produit par phase 1
|   |-- ressources_nettoyees.csv     # Produit par phase 2
|   |-- temps_nettoye.csv            # Produit par phase 3
|   |-- dataset_complet.csv          # Fichier final (phase 4)
|   |-- projet.db                    # Base SQLite (produit automatiquement)
|   |-- modele_ml_reg.joblib         # Modèle Gradient Boosting (phase 6)
|   `-- modele_eco_ols.joblib        # Modèle OLS (phase 5)
|-- traitement_de_donnees/           # Notebooks phases 1 à 4
|   |-- phase1_dossier_nettoyage.ipynb
|   |-- phase2_ressources_nettoyage.ipynb
|   |-- phase3_temps_nettoyage.ipynb
|   |-- phase4_integration_sources.ipynb
|   `-- phase4b_analyse_exploratoire.ipynb
|-- econometrie/                     # Notebooks phase 5
|   |-- phase5_econometrie.ipynb
|   `-- phase5b_analyse_multidimensionnelle.ipynb
|-- machine_learning/                # Notebook phase 6
|   `-- phase6_machine_learning.ipynb
|-- mise_en_production/              # Phase 7 — dashboard et scripts
|   |-- dashboard.py
|   |-- sqlite_insert.py
|   `-- train_and_save_models.py
|-- docs/                            # Documentation par phase
|   |-- phase0_architecture.md       # Vue globale du projet
|   |-- phase1_dossier.md
|   |-- phase2_ressources.md
|   |-- phase3_temps.md
|   |-- phase4_integration.md
|   |-- phase4b_analyse_exploratoire.md
|   |-- phase5_econometrie.md
|   |-- phase5b_analyse_multidimensionnelle.md
|   |-- phase6_machine_learning.md
|   `-- phase7_dashboard.md
|-- src/utils/dataframe_styler.py    # Classe pour l'affichage des DataFrames
|-- main.py                          # Point d'entrée — lance tout automatiquement
`-- requirements.txt
```

---

## Phases du projet

| Phase | Notebook | Documentation |
|-------|----------|---------------|
| Phase 0 | — | [Architecture générale](docs/phase0_architecture.md) |
| Phase 1 | `traitement_de_donnees/phase1_dossier_nettoyage.ipynb` | [Guide Phase 1](docs/phase1_dossier.md) |
| Phase 2 | `traitement_de_donnees/phase2_ressources_nettoyage.ipynb` | [Guide Phase 2](docs/phase2_ressources.md) |
| Phase 3 | `traitement_de_donnees/phase3_temps_nettoyage.ipynb` | [Guide Phase 3](docs/phase3_temps.md) |
| Phase 4 | `traitement_de_donnees/phase4_integration_sources.ipynb` | [Guide Phase 4](docs/phase4_integration.md) |
| Phase 4b | `traitement_de_donnees/phase4b_analyse_exploratoire.ipynb` | [Guide Phase 4b](docs/phase4b_analyse_exploratoire.md) |
| Phase 5 | `econometrie/phase5_econometrie.ipynb` | [Guide Phase 5](docs/phase5_econometrie.md) |
| Phase 5b | `econometrie/phase5b_analyse_multidimensionnelle.ipynb` | [Guide Phase 5b](docs/phase5b_analyse_multidimensionnelle.md) |
| Phase 6 | `machine_learning/phase6_machine_learning.ipynb` | [Guide Phase 6](docs/phase6_machine_learning.md) |
| Phase 7 | `mise_en_production/dashboard.py` | [Guide Phase 7](docs/phase7_dashboard.md) |

---

## Résultats principaux

**OLS (Phase 5)**
- R² = 0,265 — F-stat = 2 997 (p < 0,001)
- Variables significatives : population agent (CAC : -51 %), lieu (TELE : -5 %), nb_agents_distincts (+12 % par agent)
- Erreurs standard robustes HC3 appliquées (hétéroscédasticité confirmée par Breusch-Pagan)

**Machine Learning (Phase 6)**
- Meilleur modèle : GradientBoostingRegressor — R²=0,63, RMSE=20,2 h
- Random Forest en sur-apprentissage (R²train=0,93 vs R²test=0,61)

---

## Organisation du travail

Nous avons suivi une méthode de travail Agile avec deux réunions hebdomadaires :

**Reunions hebdomadaires :**
- Samedi de 10h à 18h
- Mardi de 19h à 23h

**Ordre du jour de chaque séance :**
- Revue du travail de la semaine
- Planification des tâches à venir
- Discussion des blocages et solutions

---

## Note sur l'affichage des DataFrames

Pour mieux visualiser les données dans les notebooks, nous avons écrit une petite classe
`DataFrameStyler` dans `src/utils/dataframe_styler.py`. Elle permet de mettre en évidence
les doublons et les valeurs particulières. Voici comment on l'utilise :

```python
from utils.dataframe_styler import style_duplicates

df.head(10).style_duplicates()
df[masque].head(5).style_duplicates(highlight_mask=masque)
df.head(10).style_duplicates(id_column='Matricule')
```

---

## Ressources techniques

- [Guide d'installation](docs/setup.md) — installation manuelle, prérequis
- [Guide Git](docs/git.md) — commandes Git utilisées dans le projet
- [Configuration SSH GitLab](docs/ssh.md) — connexion au dépôt distant
