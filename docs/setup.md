# Guide d'Installation du Projet

<div align="right">

[← Retour à la documentation principale](../README.md)

</div>

## Prérequis
- Python 3.11+
- Git
- pip

## Installation

### 1. Cloner le projet
```bash
git clone git@gitlab.etu.umontpellier.fr:e20190009681/du_data-science_projet-data.git
cd du_data-science_projet-data
```

### 2. Installation Automatisée (Recommandé)
Le projet utilise `uv` pour une gestion rapide et automatique de l'environnement. Exécutez simplement :
```bash
python main.py
```
Cette commande va :
1. Créer l'environnement virtuel `.venv`.
2. Installer toutes les dépendances nécessaires.
3. Lancer le Dashboard Streamlit.

### 3. Installation Manuelle (Alternative)
Si vous préférez gérer l'environnement vous-même :
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

##  Vérification

```bash
python -c "import pandas, numpy; print(' Installation réussie!')"
```
