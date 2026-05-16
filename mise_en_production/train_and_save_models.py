import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

# Définition des chemins
RACINE = Path(__file__).resolve().parent.parent
DATA_PATH = RACINE / 'data' / 'dataset_complet.csv'
MODEL_ML_PATH = RACINE / 'data' / 'modele_ml_reg.joblib'
MODEL_ECO_PATH = RACINE / 'data' / 'modele_eco_ols.joblib'

# Variables
FEATURES_NUMERIQUES = [
    'agent_experience_j', 'agent_duree_travail_j', 'agent_temps_travail_pct',
    'delai_survenance_ouverture_j', 'nb_interventions', 'nb_agents_distincts',
    'mois_ouverture'
]
FEATURES_CATEGORIELLES = [
    'agent_lieu_travail', 'agent_contrat', 'agent_population', 'annee_ouverture'
]
TOUTES_FEATURES = FEATURES_NUMERIQUES + FEATURES_CATEGORIELLES

def main():
    print("Chargement des données...")
    dataset = pd.read_csv(DATA_PATH, encoding='utf-8')
    
    # Préparation
    df_reg = dataset[TOUTES_FEATURES + ['duree_totale_h']].copy()
    df_reg = df_reg.dropna(subset=['duree_totale_h'])
    df_reg['annee_ouverture'] = df_reg['annee_ouverture'].astype(str)
    
    X = df_reg[TOUTES_FEATURES]
    y = df_reg['duree_totale_h']
    y_log = np.log1p(y)  # log(1 + h) — cohérent avec Phase 5

    # Création du préprocesseur
    preprocessor = ColumnTransformer(transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), FEATURES_NUMERIQUES),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ]), FEATURES_CATEGORIELLES)
    ], remainder='drop')

    # Modèle ML (Gradient Boosting) — cible : durée brute en heures
    print("Entraînement du modèle Machine Learning (GradientBoosting)...")
    pipeline_ml = Pipeline([
        ('preprocessing', preprocessor),
        ('modele', GradientBoostingRegressor(n_estimators=100, random_state=42))
    ])
    pipeline_ml.fit(X, y)

    # Modèle Économétrique (OLS) — cible : log(1 + duree), cohérent avec Phase 5
    # La back-transformation expm1() est appliquée dans le dashboard.
    print("Entraînement du modèle Économétrique (LinearRegression sur log-scale)...")
    pipeline_eco = Pipeline([
        ('preprocessing', preprocessor),
        ('modele', LinearRegression())
    ])
    pipeline_eco.fit(X, y_log)
    
    # Sauvegarde
    print(f"Sauvegarde des modèles dans {RACINE / 'data'} ...")
    joblib.dump(pipeline_ml, MODEL_ML_PATH)
    joblib.dump(pipeline_eco, MODEL_ECO_PATH)
    print("Terminé avec succès !")

if __name__ == '__main__':
    main()
