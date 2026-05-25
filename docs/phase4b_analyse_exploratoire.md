<div align="center">

| [**← Phase 4**](phase4_integration.md) | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 5 →**](phase5_econometrie.md) |
| :---: | :---: | :---: |

</div>

# Phase 4b — Analyse Exploratoire

> **Notebook :** `traitement_de_donnees/phase4b_analyse_exploratoire.ipynb`  
> **Données :** `data/dataset_complet.csv` (produit par Phase 4)  
> **Objectif :** Explorer les distributions, relations et patterns avant la modélisation (Phases 5 et 6)

---

## Objectif

Réaliser une analyse exploratoire complète du dataset intégré afin de :
- comprendre les distributions des variables numériques et catégorielles
- identifier les relations entre la variable cible (`duree_totale_h`) et les variables explicatives
- détecter les effets saisonniers et temporels
- orienter le choix des variables pour l'économétrie (Phase 5) et le Machine Learning (Phase 6)

---

## Structure du notebook

| Section | Contenu |
|---------|---------|
| **1. Chargement et aperçu global** | `df.shape`, `df.info()`, `df.describe()`, taux de NaN |
| **2. Analyse univariée — numériques** | Histogramme + boxplot + test de normalité (Shapiro) par variable |
| **3. Analyse univariée — catégorielles** | Fréquences, bar charts, top modalités |
| **4. Analyse bivariée** | `duree_totale_h` vs chaque variable explicative (boxplot par groupe, scatter, corrélation) |
| **5. Analyse temporelle** | Distribution mensuelle, saisonnalité, effet année |
| **6. Synthèse et conclusions** | Enseignements clés, variables retenues pour la modélisation |

---

## Principaux enseignements

**Variable cible (`duree_totale_h`) :**
- Distribution fortement asymétrique à droite — justifie la transformation `log(1 + h)` en Phase 5
- Médiane ≈ 15 h, mais queue longue (certains dossiers > 100 h)
- Non-normale confirmée par le test de Shapiro

**Variables explicatives les plus discriminantes :**
- `agent_population` (CAC vs CAS) — forte différence de durée médiane
- `nb_interventions` et `nb_agents_distincts` — corrélation positive avec la durée
- `agent_lieu_travail` (SITE vs TELE) — effet mesurable confirmé en Phase 5
- `agent_contrat` — différences significatives entre CDI, CDS, CDD

**Variables peu informatives :**
- `agent_experience_j` — corrélation quasi nulle avec la durée (confirmé OLS p = 0,134)
- `agent_duree_travail_j` — idem (OLS p = 0,422)

---

## Lien avec les phases suivantes

| Phase | Utilisation des résultats |
|-------|--------------------------|
| Phase 5 — OLS | Variables sélectionnées ici, transformation log(1+h) justifiée |
| Phase 6 — ML | Même sélection de features, même pipeline de prétraitement |
| Phase 7 — Dashboard | Onglet "Analyse exploratoire" reproduit les graphiques clés |
