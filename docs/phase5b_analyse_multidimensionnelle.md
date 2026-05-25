<div align="center">

| [**← Phase 5**](phase5_econometrie.md) | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 6 →**](phase6_machine_learning.md) |
| :---: | :---: | :---: |

</div>

# Phase 5b — Analyse Multidimensionnelle

> **Notebook :** `econometrie/phase5b_analyse_multidimensionnelle.ipynb`  
> **Données :** `data/dataset_complet.csv`  
> **Objectif :** Réduire la dimensionnalité et identifier des profils de dossiers par méthodes non supervisées

---

## Objectif

Compléter l'analyse économétrique (Phase 5) par des méthodes multidimensionnelles :
- **ACP** (Analyse en Composantes Principales) sur les variables numériques
- **ACM** (Analyse des Correspondances Multiples) sur les variables catégorielles
- **Classification non supervisée** (CAH et K-Means) pour identifier des profils de dossiers

---

## Structure du notebook

| Section | Méthode | Librairie |
|---------|---------|-----------|
| **1. Préparation des données** | Standardisation, séparation num/cat | `sklearn.preprocessing` |
| **2. ACP** | Composantes principales, variance expliquée, biplot | `sklearn.decomposition.PCA` |
| **3. ACM** | Correspondances multiples sur variables catégorielles | `prince` |
| **4. CAH** | Classification hiérarchique ascendante, dendrogramme | `scipy.cluster.hierarchy` |
| **5. K-Means** | Clustering, méthode du coude, silhouette | `sklearn.cluster.KMeans` |
| **6. Synthèse** | Profils identifiés, lien avec les résultats OLS |  |

---

## Principaux résultats

**ACP :**
- Les deux premières composantes expliquent la majorité de la variance structurelle
- CP1 est dominée par les variables de durée et de complexité (`duree_totale_h`, `nb_interventions`, `nb_agents_distincts`)
- CP2 oppose les variables d'expérience et de temps de travail de l'agent

**ACM :**
- Les modalités CAC/CAS de `agent_population` se séparent nettement sur le premier axe
- `agent_lieu_travail` contribue au second axe — cohérent avec l'effet TELE (-5%) de l'OLS

**Classification :**
- La CAH et K-Means convergent vers des profils distincts de dossiers
- Profil 1 : dossiers courts, agents CAC, télétravail
- Profil 2 : dossiers longs, multi-agents, forte complexité

---

## Lien avec les autres phases

| Phase | Lien |
|-------|------|
| Phase 5 — OLS | Confirme les variables significatives identifiées par les axes ACP |
| Phase 6 — ML | Les profils K-Means peuvent servir de features supplémentaires |
