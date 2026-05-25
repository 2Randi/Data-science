<div align="center">

| [**← Phase 4b**](phase4b_analyse_exploratoire.md) | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 5b →**](phase5b_analyse_multidimensionnelle.md) |
| :---: | :---: | :---: |

</div>

# Phase 5 — Économétrie

> **Fichier notebook :** `econometrie/phase5_econometrie.ipynb`  
> **Données en entrée :** `data/dataset_complet.csv` (98 935 × 34)  
> **Objectif :** Modéliser la durée de traitement (`duree_totale_h`) par régression OLS

---

## Variable dépendante

`duree_totale_h` — durée totale de traitement d'un dossier en heures  
*(transformée log si distribution fortement asymétrique)*

---

## Variables indépendantes candidates

| Variable | Type | Transformation |
|----------|------|---------------|
| `agent_experience_j` | numérique | numérique (brut) |
| `agent_duree_travail_j` | numérique | numérique (brut) |
| `delai_survenance_ouverture_j` | numérique | numérique (brut) |
| `agent_lieu_travail` | catégoriel | variable binaire — dummy (SITE=réf.) |
| `agent_contrat` | catégoriel | variable binaire — dummy (CDI=réf.) |
| `agent_population` | catégoriel | variable binaire — dummy (CAS=réf.) |
| `Cause.intervention` | catégoriel | variable binaire — dummy (modalité la plus fréquente=réf.) |
| `Type.d.energie` | catégoriel | variable binaire — dummy |
| `mois_ouverture` | numérique | numérique (brut) ou variable binaire — à tester |
| `annee_ouverture` | catégoriel | variable binaire — dummy |

---

## Décisions de modélisation

### E1 — Traitement des NaN avant régression
**Décision :** `dropna()` sur les colonnes utilisées dans chaque modèle.  
**Justification :** Les NaN correspondent à des dossiers sans intervention `temps` (2.2%) ou sans données agent (7.5%). Les exclure est préférable à une imputation qui biaiserait les coefficients.

### E2 — Transformation logarithmique de `duree_totale_h`
**Décision :** Si le coefficient d'asymétrie (`skewness`) > 1, utiliser `log(duree_totale_h + 1)`.  
**Justification :** Une distribution très asymétrique viole l'hypothèse de normalité des résidus. La transformation log stabilise la variance et améliore la normalité.

### E3 — Choix de la modalité de référence pour les dummies
**Décision :** CDI pour `agent_contrat`, SITE pour `agent_lieu_travail`, CAS pour `agent_population`.  
**Justification :** Ces modalités sont les plus fréquentes — elles constituent une référence interprétable.

### E4 — Seuil de significativité
**Décision :** α = 5% (p-value < 0.05 pour conserver une variable).  
**Justification :** Seuil standard en économétrie académique.

### E5 — Pourquoi OLS et pas GLM ?

Nous avons considéré les modèles alternatifs avant de choisir OLS. Voici notre raisonnement :

- **GLM Poisson** : adapté aux données de comptage (nombre entier d'événements). Notre variable `duree_totale_h` est une durée continue en heures — ce n'est pas un comptage. Nous avons quand même testé GLM Poisson dans le notebook pour vérifier, mais les résidus confirmaient l'inadéquation.

- **GLM Gamma** : adapté aux variables continues positives asymétriques. Théoriquement envisageable pour une durée. Cependant, la transformation logarithmique de `duree_totale_h` dans le modèle OLS donne des résultats très proches, avec l'avantage que les coefficients s'interprètent directement comme des semi-élasticités (variation en % de la durée pour une unité de plus de la variable explicative) — ce qui est plus utile économiquement.

- **OLS log-linéaire retenu** pour trois raisons :
  1. La transformation `log(duree)` corrige l'asymétrie de la distribution et rapproche les résidus de la normalité.
  2. Les erreurs robustes HC3 (correction de White) prennent en charge l'hétéroscédasticité confirmée par le test de Breusch-Pagan, sans changer le cadre du modèle.
  3. C'est le modèle enseigné dans le cours d'économétrie, ce qui nous permet de mobiliser directement les outils vus en TD.

---

## Plan d'exécution

```
Section 0  — Initialisation et chargement
Section 1  — Statistiques descriptives (describe, histogrammes)
Section 2  — Matrice de corrélation (heatmap)
Section 3  — Préparation des données (exclusion NaN, dummies, log-transform)
Section 4  — Régression OLS simple (duree_totale_h ~ agent_experience_j)
Section 5  — Régression OLS multiple (toutes variables significatives)
Section 6  — Tests hypothèses classiques
             6a Normalité résidus (Shapiro-Wilk + Q-Q plot)
             6b Homoscédasticité (Breusch-Pagan)
             6c Multicolinéarité (VIF)
             6d Autocorrélation (Durbin-Watson)
Section 7  — Interprétation et conclusion
```
