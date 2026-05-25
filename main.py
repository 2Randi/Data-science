import sys
import subprocess
from pathlib import Path
import shutil


def check_uv():
    if not shutil.which("uv"):
        print("Erreur : le gestionnaire de paquets 'uv' n'est pas installe.")
        print("Installez-le avec : curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)


def setup_environment():
    print("Verification de l'environnement...")
    if not Path(".venv").exists():
        print("Creation de l'environnement virtuel...")
        subprocess.run(["uv", "venv"], check=True)
    if Path("requirements.txt").exists():
        subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)


def setup_data():
    if not (Path("data") / "projet.db").exists():
        print("Creation de la base de donnees SQLite...")
        subprocess.run(["uv", "run", "python", "mise_en_production/sqlite_insert.py"], check=True)


def setup_models():
    reg = Path("data") / "modele_ml_reg.joblib"
    eco = Path("data") / "modele_eco_ols.joblib"
    if not reg.exists() or not eco.exists():
        print("Entrainement des modeles...")
        subprocess.run(["uv", "run", "python", "mise_en_production/train_and_save_models.py"], check=True)


def run_dashboard():
    dashboard_path = Path("mise_en_production") / "dashboard.py"
    if not dashboard_path.exists():
        print(f"Erreur : {dashboard_path} introuvable.")
        sys.exit(1)
    try:
        subprocess.run(["uv", "run", "streamlit", "run", str(dashboard_path)])
    except KeyboardInterrupt:
        print("Arret du dashboard.")
    except Exception as e:
        print(f"Erreur : {e}")


def main():
    check_uv()
    setup_environment()
    setup_data()
    setup_models()
    run_dashboard()


if __name__ == "__main__":
    main()
