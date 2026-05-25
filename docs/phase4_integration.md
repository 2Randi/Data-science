<div align="center">

| [**← Phase 3**](phase3_temps.md) | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 4b →**](phase4b_analyse_exploratoire.md) |
| :---: | :---: | :---: |

</div>

# Phase 4 — Intégration et Contrôles Inter-sources

> **Fichier notebook :** `traitement_de_donnees/phase4_integration_sources.ipynb`  
> **Données en entrée :** `dossier_nettoye.csv`, `ressources_nettoyees.csv`, `temps_nettoye.csv`  
> **Données en sortie :** `data/dataset_complet.csv`

---

## Objectif

Construire le **dataset analytique final** en fusionnant les trois sources nettoyées.  
Ce dataset sera la base unique pour toutes les analyses (Phases 5 & 6).

---

## Schéma des jointures

```
dossier_nettoye (98 935 lignes)          ← unité d'analyse : 1 dossier
    │
    ├── LEFT JOIN temps_nettoye          ← agrégat des interventions par dossier
    │   clé : Numero_dossier_ID = Numero.dossier
    │
    └── LEFT JOIN ressources_nettoyees   ← caractéristiques de l'agent traitant
        clé : Matricule.de.traitement = Matricule
        via : date.ouverture (date de présence la plus proche)
```

---

## Étapes de construction

### D1 — Agrégation de `temps_nettoye` par dossier

**Logique :** regrouper toutes les interventions d'un dossier pour obtenir des indicateurs synthétiques.

**Variables produites :**

| Variable | Calcul | Description |
|----------|--------|-------------|
| `nb_interventions` | `count(Matricule)` | Nombre d'agents ayant traité le dossier |
| `nb_agents_distincts` | `nunique(Matricule)` | Nombre d'agents uniques |
| `duree_totale_min` | `sum(duree.corrigee)` | Durée totale de traitement (minutes) |
| `duree_moyenne_min` | `mean(duree.corrigee)` | Durée moyenne par intervention |
| `date_premiere_intervention` | `min(Date.debut.traitement)` | Date du premier contact |
| `date_derniere_intervention` | `max(Date.debut.traitement)` | Date du dernier contact |

**Décision :** LEFT JOIN — les 2 180 dossiers sans intervention dans `temps` obtiendront des NaN pour toutes ces variables (informatif : durée inconnue ≠ durée nulle).

---

### D2 — Extraction des caractéristiques de l'agent traitant depuis `ressources_nettoyees`

**Logique :** récupérer les caractéristiques de l'agent (`Matricule.de.traitement`) à la date d'ouverture du dossier.

**Stratégie :** jointure sur `Matricule` + filtre `Date.presence == date.ouverture`.  
Si aucune présence exacte ce jour-là → prendre la ligne la plus récente avant cette date.

**Variables récupérées :**

| Variable source | Alias dans dataset_complet | Description |
|----------------|---------------------------|-------------|
| `Lieu.travail` | `agent_lieu_travail` | TELE ou SITE |
| `Population` | `agent_population` | CAS ou CAC |
| `Site` | `agent_site` | Site d'affectation |
| `Type.de.contrat` | `agent_contrat` | CDI, CDD, CDS |
| `Duree.travail` | `agent_duree_travail_j` | Heures travaillées ce jour |
| `Temps.travail` | `agent_temps_travail_pct` | % temps de travail |
| `Experience` | `agent_experience_j` | Jours d'expérience |

**Décision :** si aucune présence trouvée pour un agent à la date du dossier → NaN (1 matricule orphelin connu).

---

### D3 — Contrôles inter-sources post-jointure

Après la construction du dataset, vérifier :

| Contrôle | Attendu |
|----------|---------|
| Nombre de lignes = dossier_nettoye | 98 935 (jointure LEFT garantit l'unicité) |
| % NaN dans `duree_totale_min` | ≈ 2.2% (2 180 dossiers sans temps) |
| % NaN dans `agent_experience_j` | ≈ 0.001% (1 matricule orphelin) |
| Aucune duplication de dossiers | `Numero_dossier_ID` toujours unique |

---

## Variables finales du `dataset_complet`

### Depuis `dossier_nettoye` (17 colonnes)
Toutes les colonnes originales conservées.

### Depuis agrégation `temps` (+6 colonnes)
`nb_interventions`, `nb_agents_distincts`, `duree_totale_min`, `duree_moyenne_min`,  
`date_premiere_intervention`, `date_derniere_intervention`

### Depuis `ressources` (+7 colonnes)
`agent_lieu_travail`, `agent_population`, `agent_site`, `agent_contrat`,  
`agent_duree_travail_j`, `agent_temps_travail_pct`, `agent_experience_j`

### Variables calculées (+3 colonnes)
| Variable | Calcul |
|----------|--------|
| `delai_survenance_ouverture` | `date.ouverture - date.de.survenance` (jours) |
| `mois_ouverture` | Mois de `date.ouverture` (1–12) |
| `annee_ouverture` | Année de `date.ouverture` (2021 ou 2022) |

**Total attendu : ~33 colonnes**

---

## Plan d'exécution du notebook

```
Section 0  — Imports, chargement des 3 bases nettoyées
Section 1  — D1 : Agrégation temps par dossier
Section 2  — D2 : Extraction caractéristiques agent depuis ressources
Section 3  — Jointure principale (LEFT JOIN)
Section 4  — D3 : Contrôles post-jointure et NaN introduits
Section 5  — Calcul des variables dérivées
Section 6  — Bilan final et statistiques descriptives
Section 7  — Export dataset_complet.csv
```
