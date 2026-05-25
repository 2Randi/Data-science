<div align="center">

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | [**🏠 Architecture**](phase0_architecture.md) | [**Phase 2 →**](phase2_ressources.md) |
| :---: | :---: | :---: |

</div>

# Phase 1 — Nettoyage et Validation de `dossier.csv`

> **Fichier :** `traitement_de_donnees/phase1_dossier_nettoyage.ipynb`  
> **Auteurs :** Randriamisaina Tsiory-Fanomezana · SHIRALI POUR Amir

---

## Vue d'ensemble

La base `dossier.csv` contient **101 234 enregistrements** et **17 colonnes**  
couvrant la période 2021–2022. Ce notebook constitue la **première phase**  
du pipeline de traitement : identifier, décider et corriger chaque anomalie  
avant toute analyse statistique ou modélisation.

---

## Anomalies détectées et décisions

### A1 — Doublons sur `Numero_dossier_ID` (1 234 lignes)

| | |
|---|---|
| **Constat** | 101 234 lignes mais 100 000 IDs uniques → 1 234 doublons |
| **Décision** | **Suppression** — `keep='first'` |
| **Justification** | `Numero_dossier_ID` est une clé primaire. Sans information supplémentaire pour distinguer la "vraie" occurrence, on retient la première entrée (convention standard). Aucune donnée utile n'est perdue : les 100 000 dossiers distincts sont intacts. |

---

### A2 — Format de date non-standard dans `date.ouverture` (10 lignes)

| | |
|---|---|
| **Constat** | 10 dates au format français `DD/MM/YYYY` au lieu de `YYYY/MM/DD` |
| **Décision** | **Conversion** vers format ISO `YYYY/MM/DD` |
| **Justification** | La date réelle est récupérable sans ambiguïté. Le format ISO permet des comparaisons directes sous forme de chaînes. |

---

### A3 — Dates hors période 2021–2022 (1 010 lignes)

| | |
|---|---|
| **Constat** | `date.ouverture` : 10 lignes en 2020 ; `date.de.survenance` : 1 000 lignes avec `2023` |
| **Décision** | **Suppression** de toutes les lignes hors `[2021/01/01 – 2022/12/31]` |
| **Justification** | Le glossaire spécifie que la base couvre 2021–2022. Les dates 2020 (converties depuis `01/01/2020`) et 2023 sont des données hors-scope. La valeur `2023` seule (sans mois/jour) est de plus inutilisable pour toute analyse temporelle. |

---

### A4 — Cohérence `date.de.survenance` > `date.ouverture`

| | |
|---|---|
| **Constat** | Certaines lignes ont une date de survenance **postérieure** à l'ouverture du dossier |
| **Décision** | **Correction** : `date.de.survenance` ← `date.ouverture` quand survenance > ouverture |
| **Justification** | Un sinistre ne peut pas survenir après l'ouverture du dossier. Il s'agit d'une erreur de saisie. On choisit la valeur conservative : la date d'ouverture. La ligne est conservée car toutes ses autres informations sont exploitables. |

---

### A5 — Heures invalides dans `heure.ouverture` (1 000 lignes)

| | |
|---|---|
| **Constat** | 1 000 valeurs `25:00:00` — heure impossible (max `23:59:59`) |
| **Décision** | **Remplacement par `NaN`** |
| **Justification** | `25:00:00` est une valeur sentinelle signalant une heure non saisie. On ne peut pas deviner l'heure réelle. On conserve la ligne (les autres champs sont valides) et on marque l'heure comme manquante. |

---

### A6 — Valeurs `???` (données non renseignées)

| Colonne | Nombre | Décision |
|---------|--------|----------|
| `Formule` | 5 000 | Remplacement par `NaN` |
| `Assistance.ou.Administratif` | 10 000 | Remplacement par `NaN` |

**Justification commune :** `???` est un marqueur de substitution pour valeur inconnue.  
Le conserver comme chaîne fausserait les distributions et les modèles.  
On ne supprime pas les lignes — la perte serait trop importante (5% et 10% du total).  
Le traitement par imputation est reporté à la phase de modélisation si nécessaire.

---

### A7 — `Type.d.energie` : valeur `'inconnu'` (500 lignes)

| | |
|---|---|
| **Constat** | 500 valeurs `'inconnu'` en plus de 994 `NaN` |
| **Décision** | **Conservation** de `'inconnu'` comme modalité distincte |
| **Justification** | `NaN` = donnée absente (non collectée). `'inconnu'` = saisie volontaire de l'opérateur signifiant que le type n'est pas déterminable. Ces deux situations ont une sémantique différente et ne doivent pas être confondues. |

---

### A8 — Intégrité référentielle `Matricule.de.traitement` (1 matricule orphelin)

| | |
|---|---|
| **Constat** | 1 matricule présent dans `dossier` mais absent de `ressources.csv` |
| **Décision** | **Signalement** sans suppression |
| **Justification** | Un matricule orphelin peut correspondre à un agent ayant quitté l'entreprise (données historiques valides) ou à une erreur de saisie. Sans confirmation métier, la suppression est trop agressive. Le problème est documenté pour investigation future. |

---

## Plan d'exécution du notebook

```
Section 0  — Imports, chargement, copie de sécurité
Section 1  — Vue d'ensemble (shape, dtypes, tableau d'anomalies)
Section 2  — A1 : Doublons ID → suppression
Section 3  — A2+A3 : Dates → normalisation + suppression hors-période
Section 4  — A4 : Cohérence temporelle survenance/ouverture
Section 5  — A5 : Heures invalides → NaN
Section 6  — A6 : ??? → NaN
Section 7  — A7 : 'inconnu' dans Type.d.energie → conservation
Section 8  — A8 : Intégrité référentielle matricule
Section 9  — Synthèse finale + visualisation
Section 10 — Export dossier_nettoye.csv
```

