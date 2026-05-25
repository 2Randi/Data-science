<div align="center">

| [**← Phase 2**](phase2_ressources.md) | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 4 →**](phase4_integration.md) |
| :---: | :---: | :---: |

</div>

# Phase 3 — Nettoyage et Validation de la Base `temps.csv`

> **Fichier notebook :** `traitement_de_donnees/phase3_temps_nettoyage.ipynb`  
> **Données en entrée :** `data/temps.csv` — 431 598 lignes × 5 colonnes (encoding: latin-1)  
> **Données en sortie :** `data/temps_nettoye.csv`

---

## Contexte de la base `temps`

La base `temps.csv` est le **journal des interventions** : elle enregistre chaque acte de traitement
d'un dossier par un agent. Un même dossier peut avoir **plusieurs lignes** (plusieurs agents, plusieurs sessions).

### Structure des colonnes

| Colonne | Type | NaN | Description |
|---------|------|-----|-------------|
| `Numero.dossier` | int64 | 0 | Clé étrangère → `dossier.Numero_dossier_ID` |
| `Matricule` | int64 | 0 | Clé étrangère → `ressources.Matricule` |
| `Date.debut.traitement` | object | 0 | Date de début (format YYYY/MM/DD — déjà ISO) |
| `heure.debut.traitement` | object | 0 | Heure de début (format HH:MM:SS) |
| `duree.corrigee` | float64 | **47 471** | Durée de traitement en minutes |

### Statistiques clés mesurées

- `duree.corrigee` : min=5 min, médiane=188 min, max=**253 014 min** (≈4 215 heures)
- NaN dans `duree.corrigee` : **47 471 lignes** (11% du total)
- Dossiers uniques dans `temps` : **107 732**
- Dossiers dans `temps` absents de `dossier_nettoye` : **10 977**
- Dossiers dans `dossier_nettoye` absents de `temps` : **2 180**

---

## Anomalies détectées et décisions

### C1 — NaN dans `duree.corrigee` (47 471 lignes — 11%)

| | |
|---|---|
| **Constat** | 47 471 lignes (11%) n'ont pas de durée de traitement enregistrée |
| **Décision** | **Conservation avec NaN** — aucune imputation |
| **Justification** | La durée de traitement est une variable métier précise. L'imputer par la médiane introduirait un biais dans les analyses de performance. Ces lignes restent utiles pour les analyses de présence et de fréquence. Elles seront exclues uniquement des modèles nécessitant cette variable. |

---

### C2 — Valeurs aberrantes dans `duree.corrigee` (max = 253 014 min)

| | |
|---|---|
| **Constat** | Maximum observé : 253 014 minutes ≈ 175 jours. La médiane est 188 min (3h). Le 99ème percentile sera calculé. |
| **Décision** | **Signalement avec seuil de vigilance** — conservation sans suppression |
| **Justification** | Sans règle métier précisant la durée maximale d'une intervention, la suppression serait arbitraire. Un seuil de 1 440 min (24h = 1 journée) est utilisé comme indicateur d'alerte. Les valeurs extrêmes seront traitées comme outliers dans les modèles (Phase 5 & 6). |

---

### C3 — Dates hors de la période 2021–2022

| | |
|---|---|
| **Constat** | La période couverte est 2021–2022. Des interventions hors de cette fenêtre sont incohérentes avec la base `dossier`. |
| **Décision** | **Suppression** des lignes hors période |
| **Justification** | Contrairement à `ressources` (table RH à portée large), `temps` est une table de transactions directement liées aux dossiers. Une intervention hors de la période 2021–2022 est hors-scope par construction. |

---

### C4 — Dossiers dans `temps` absents de `dossier_nettoye` (10 977)

| | |
|---|---|
| **Constat** | 10 977 Numero.dossier dans `temps` n'ont pas de correspondant dans `dossier_nettoye` |
| **Décision** | **Signalement sans suppression** de `temps` |
| **Justification** | Ces dossiers peuvent avoir été supprimés lors du nettoyage de Phase 1 (hors-période, doublons). Supprimer leurs lignes de `temps` réduirait inutilement la base. Ils seront naturellement exclus lors de la jointure LEFT JOIN depuis `dossier` en Phase 4. |

---

### C5 — Dossiers dans `dossier_nettoye` absents de `temps` (2 180)

| | |
|---|---|
| **Constat** | 2 180 dossiers n'ont aucune intervention enregistrée dans `temps` |
| **Décision** | **Signalement uniquement** — ces dossiers restent dans `dossier` |
| **Justification** | Un dossier sans intervention dans `temps` peut être un dossier administratif ou à traitement immédiat. Cette information est pertinente pour l'analyse. La durée sera NaN après jointure, ce qui est informatif. |

---

### C6 — Doublons `Numero.dossier + Matricule + Date`

| | |
|---|---|
| **Constat** | Un agent peut légitimement traiter le même dossier plusieurs fois (reprises). |
| **Décision** | **Vérification** uniquement — pas de suppression a priori |
| **Justification** | Les doublons exacts (même dossier, même matricule, même date, même heure) sont suspects. Les doublons partiels (même dossier, même matricule, dates différentes) sont des reprises légitimes. |

---

### C7 — Validation du format `heure.debut.traitement`

| | |
|---|---|
| **Constat** | Les heures semblent au format HH:MM:SS (ex: 20:04:14). À vérifier systématiquement. |
| **Décision** | **Vérification regex** — remplacement par NaN si invalide |
| **Justification** | Cohérence avec la démarche Phase 1 (heure.ouverture). Toute heure non-parseable est une donnée inutilisable. |

---

### C8 — Matricules dans `temps` absents de `ressources`

| | |
|---|---|
| **Constat** | Des agents dans `temps` peuvent être absents de `ressources_nettoyees`. |
| **Décision** | **Quantification et signalement** |
| **Justification** | Ces agents ont traité des dossiers mais n'ont pas de fiche de présence dans `ressources`. Cela peut indiquer des agents externes, intérimaires, ou une erreur de consolidation. |

---

## Plan d'exécution du notebook

```
Section 0  — Imports, chargement, copie de sécurité
Section 1  — Vue d'ensemble (shape, dtypes, compter_anomalies_par_colonne)
Section 2  — C1 : Analyse des NaN dans duree.corrigee
Section 3  — C2 : Analyse des outliers dans duree.corrigee (boxplot, percentiles)
Section 4  — C3 : Dates hors 2021–2022 → suppression
Section 5  — C4 & C5 : Cross-référence avec dossier_nettoye
Section 6  — C6 : Vérification doublons Numero.dossier + Matricule
Section 7  — C7 : Validation format heure.debut.traitement
Section 8  — C8 : Cross-référence Matricule ↔ ressources
Section 9  — Synthèse bilan et tableau de bord
Section 10 — Export temps_nettoye.csv
```
