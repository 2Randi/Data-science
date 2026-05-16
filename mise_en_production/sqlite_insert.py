"""
Script de chargement des données dans SQLite.
A exécuter une seule fois avant de lancer le dashboard.

Objectif : importer le CSV produit par la Phase 4 (intégration)
dans une base SQLite locale afin que le dashboard puisse
interroger les données via des requêtes SQL, conformément
aux bonnes pratiques de mise en production.

Usage :
    python mise_en_production/sqlite_insert.py
"""
import sqlite3
import pandas as pd
from pathlib import Path

# --- Chemins
RACINE   = Path(__file__).resolve().parent.parent
CSV_PATH = RACINE / 'data' / 'dataset_complet.csv'
DB_PATH  = RACINE / 'data' / 'projet.db'

# --- Chargement et insertion
data = pd.read_csv(CSV_PATH, encoding='utf-8')
print(f"{len(data)} lignes chargées depuis {CSV_PATH.name}")
print(data.columns.tolist())

try:
    with sqlite3.connect(DB_PATH) as conn:
        data.to_sql('dossiers', conn, if_exists='replace', index=False)
        conn.commit()
    print(f"Base SQLite créée : {DB_PATH}")
    print(f"Table 'dossiers' : {len(data)} enregistrements insérés.")
except sqlite3.OperationalError as e:
    print(f"Erreur SQLite : {e}")
