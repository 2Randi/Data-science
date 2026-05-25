<div align="center">

| [**← Phase 1**](phase1_dossier.md) | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 3 →**](phase3_temps.md) |
| :---: | :---: | :---: |

</div>

# Phase 2 — Nettoyage et Validation de la Base `ressources.csv`

> **Fichier notebook :** `traitement_de_donnees/phase2_ressources_nettoyage.ipynb`  
> **Données en entrée :** `data/ressources.csv` — 389 353 lignes × 9 colonnes  
> **Données en sortie :** `data/ressources_nettoyees.csv`

---

## Contexte de la base `ressources`

La base `ressources.csv` représente le **journal de présence quotidienne** des agents du centre d'appel.  
Chaque ligne correspond à **une journée de présence d'un agent** avec ses caractéristiques contractuelles et opérationnelles.

### Structure des colonnes

| Colonne | Type | Description | Valeurs observées |
|---------|------|-------------|-------------------|
| `Matricule` | int64 | Identifiant de l'agent — clé de jointure | 2 507 agents uniques |
| `Date.presence` | object | Date de la journée de présence | Format DD/MM/YYYY |
| `Lieu.travail` | object | Modalité de travail | `TELE`, `SITE` |
| `Population` | object | Catégorie de l'agent | `CAS`, `CAC` |
| `Site` | object | Site d'affectation | `A`, `B`, ... |
| `Type.de.contrat` | object | Contrat de travail | `CDI`, `CDD`, `CDS` |
| `Duree.travail` | float64 | Heures travaillées dans la journée | min=0.017, max=23.42 |
| `Temps.travail` | int64 | Pourcentage du temps de travail | 9 valeurs distinctes (non constant) |
| `Experience` | int64 | Nombre de jours d'expérience cumulés | croissant par agent |

---

## Anomalies détectées et décisions

### B1 — Format de date non-standard dans `Date.presence`

| | |
|---|---|
| **Constat** | Toutes les dates sont au format français `DD/MM/YYYY` |
| **Décision** | **Conversion** vers le format ISO `YYYY/MM/DD` |
| **Justification** | Cohérence avec les autres sources (`dossier`, `temps`) qui utilisent `YYYY/MM/DD`. Facilite les jointures temporelles et les comparaisons chronologiques. |

---

### B2 — Dates hors de la période d'étude 2021–2022

| | |
|---|---|
| **Constat** | La période couverte par `dossier` est 2021–2022. Il faut vérifier si `ressources` contient des présences hors de cette plage. |
| **Décision** | **Signalement** des lignes hors-période. Conservation dans `ressources` (contrairement à `dossier`) car les données de ressources humaines peuvent avoir un horizon plus large. Filtrage uniquement lors de la jointure en Phase 4. |
| **Justification** | `ressources` est une table de référence RH. Supprimer des agents simplement parce qu'ils ont des présences avant/après la période des dossiers réduirait notre population de référence. |

---

### B3 — Valeurs manquantes (NaN)

| | |
|---|---|
| **Constat** | **0 NaN** dans toutes les colonnes — la base est complète |
| **Décision** | **Aucune action** requise |
| **Justification** | La complétude est confirmée par `df.isna().sum()`. Résultat documenté pour traçabilité. |

---

### B4 — Valeurs `???` (données non renseignées)

| | |
|---|---|
| **Constat** | À vérifier pour chaque colonne catégorielle |
| **Décision** | Si présents : **remplacement par NaN** |
| **Justification** | Même convention que Phase 1 — cohérence de traitement entre toutes les sources. |

---

### B5 — Valeurs aberrantes dans `Duree.travail` (outliers)

| | |
|---|---|
| **Constat** | `min=0.017h` (≈1 minute), `max=23.42h`. Moyenne=6.15h, médiane=7.33h |
| **Décision** | **Signalement avec visualisation** — conservation sans suppression |
| **Justification** | Une durée de 1 minute peut être une entrée/sortie tardive légitime ou une erreur de badgeage. Sans validation métier, on ne supprime pas. Les valeurs > 10h méritent attention (ex: 23.42h) mais peuvent correspondre à des gardes de nuit. Ces cas seront traités comme des outliers dans les modèles. |

---

### B6 — Unicité `Temps.travail` = 100

| | |
|---|---|
| **Constat** | À vérifier — si tous les agents sont à 100%, la variable est constante et inutile |
| **Décision** | **Vérification** — si constante : signalement mais conservation (peut être utile pour vérification d'intégrité) |
| **Justification** | Une variable constante n'apporte pas d'information discriminante aux modèles de ML/économétrie. Elle sera exclue si confirmée constante. |

---

### B7 — Doublons `Matricule + Date.presence`

| | |
|---|---|
| **Constat** | Un agent ne devrait avoir qu'une ligne par jour. Des doublons indiqueraient une erreur de saisie. |
| **Décision** | **Vérification** — si présents : suppression de la ligne dupliquée (keep=first) |
| **Justification** | Un double enregistrement de présence fausserait le calcul du temps total travaillé par agent, variable clé pour les analyses futures. |

---

### B8 — Vérification de la cohérence de `Experience`

| | |
|---|---|
| **Constat** | `Experience` représente les jours d'expérience cumulés. Sa valeur doit croître monotonement par agent. |
| **Décision** | **Vérification** — signalement si décroissant pour un agent |
| **Justification** | Une expérience décroissante est physiquement impossible et signalerait une erreur de consolidation. |

---

### B9 — Cross-référence avec `dossier.csv`

| | |
|---|---|
| **Constat** | 1 matricule présent dans `dossier` mais absent de `ressources` (détecté en Phase 1) |
| **Décision** | **Signalement croisé** — confirmation depuis la perspective de `ressources` |
| **Justification** | Vue complémentaire du problème de clé orpheline identifié en Phase 1. |

---

## Plan d'exécution du notebook

```
Section 0  — Imports, chargement, copie de sécurité
Section 1  — Vue d'ensemble (shape, dtypes, valeurs uniques par colonne)
Section 2  — B1 : Normalisation des dates → format ISO YYYY/MM/DD
Section 3  — B2 : Analyse de la plage temporelle (2021–2022 ?)
Section 4  — B3+B4 : Valeurs manquantes NaN et ???
Section 5  — B5 : Analyse des outliers dans Duree.travail
Section 6  — B6 : Vérification Temps.travail (constante ?)
Section 7  — B7 : Doublons Matricule + Date.presence
Section 8  — B8 : Cohérence croissante de Experience par agent
Section 9  — B9 : Cross-référence Matricule ↔ dossier
Section 10 — Synthèse et tableau de bord de qualité
Section 11 — Export ressources_nettoyees.csv
```
