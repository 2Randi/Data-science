"""
Dashboard interactif — Projet Big Data
Université de Montpellier — Faculté d'Économie
Équipe : Randriamisaina Tsiory-Fanomezana · SHIRALI POUR Amir

Objectif : présenter les résultats des 7 phases du projet (exploration,
nettoyage, intégration, économétrie, machine learning) dans une interface
interactive navigable par onglets, conformément aux exigences du cours.
"""
import sys
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
import joblib


# --- Localisation de la racine
def _racine() -> Path:
    rep = Path(__file__).resolve().parent
    while True:
        if any((rep / m).exists() for m in ['.git', 'requirements.txt']):
            return rep
        if rep.parent == rep:
            return Path(__file__).resolve().parent.parent
        rep = rep.parent

RACINE = _racine()
sys.path.insert(0, str(RACINE / 'src'))

# --- Configuration Streamlit
st.set_page_config(
    page_title="Centre d'Assistance — Tableau de Bord",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Palette
BLEU      = "#4472C4"
ORANGE    = "#ED7D31"
VERT      = "#70AD47"
ROUGE     = "#C00000"

# --- CSS
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
[data-testid="stMetricLabel"] { font-size: 0.85rem; color: #555; }
h1 { color: #1a1a2e; }
h2 { color: #4472C4; border-bottom: 2px solid #4472C4; padding-bottom: .3rem; }
.interpret-box {
    background: #f8f9ff; border-left: 4px solid #4472C4;
    padding: 0.6rem 1rem; border-radius: 0 6px 6px 0;
    margin-top: 0.4rem; font-size: 0.93rem; color: #333;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# CHARGEMENT DES DONNÉES
# Objectif : lire les données depuis SQLite (résultat de sqlite_insert.py)
# et mettre en cache pour éviter les rechargements répétés.
# ------------------------------------------------------------
DB_PATH  = RACINE / 'data' / 'projet.db'
CSV_PATH = RACINE / 'data' / 'dataset_complet.csv'


def _creer_base_sqlite():
    """Crée la base SQLite à partir du CSV si elle n'existe pas encore."""
    if not DB_PATH.exists():
        df_csv = pd.read_csv(CSV_PATH, encoding='utf-8')
        conn = sqlite3.connect(DB_PATH)
        df_csv.to_sql('dossiers', conn, if_exists='replace', index=False)
        conn.close()


@st.cache_data(show_spinner="Chargement des données…")
def charger_dataset() -> pd.DataFrame:
    _creer_base_sqlite()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM dossiers", conn)
    conn.close()
    df['date.ouverture'] = pd.to_datetime(
        df['date.ouverture'], format='%Y/%m/%d', errors='coerce'
    )
    return df


@st.cache_data(show_spinner=False)
def charger_ols_summary() -> str:
    chemin = RACINE / 'data' / 'phase5_ols_summary.txt'
    if chemin.exists():
        return chemin.read_text(encoding='utf-8')
    return "Résumé OLS non disponible. Exécutez d'abord le notebook Phase 5."


@st.cache_data(show_spinner=False)
def img(nom: str):
    p = RACINE / 'data' / nom
    return str(p) if p.exists() else None


@st.cache_resource(show_spinner="Chargement des modèles...")
def charger_modeles():
    try:
        modele_ml  = joblib.load(RACINE / 'data' / 'modele_ml_reg.joblib')
        modele_eco = joblib.load(RACINE / 'data' / 'modele_eco_ols.joblib')
        return modele_ml, modele_eco
    except Exception:
        return None, None


# --- Helpers layout
def get_cols(deux_col: bool):
    """Retourne deux conteneurs côte-à-côte ou empilés selon le toggle."""
    if deux_col:
        return st.columns(2)
    return st.container(), st.container()


def interprete(texte: str):
    st.markdown(
        f'<div class="interpret-box">💡 {texte}</div>',
        unsafe_allow_html=True,
    )


def interprete_pair(gauche: str, droite: str):
    if not gauche and not droite:
        return
    g = (f'<div class="interpret-box" style="flex:1;">💡 {gauche}</div>'
         if gauche else '<div style="flex:1;"></div>')
    d = (f'<div class="interpret-box" style="flex:1;">💡 {droite}</div>'
         if droite else '<div style="flex:1;"></div>')
    st.markdown(
        f'<div style="display:flex;gap:1rem;align-items:stretch;margin-top:0.4rem;">'
        f'{g}{d}</div>',
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# CHARGEMENT INITIAL — une seule fois pour tout le dashboard
# ------------------------------------------------------------
df = charger_dataset()


# ------------------------------------------------------------
# SIDEBAR — Filtres globaux
# Objectif : permettre le filtrage des données via checkboxes (activation)
# + formulaire (sélection) + bouton de réinitialisation, conformément au
# style de navigation recommandé dans le cours gestion_de_mise-en-production.
# ------------------------------------------------------------
def _reset():
    for k in ['f_annee', 'f_lieu', 'f_contrat', 'f_pop']:
        if k in st.session_state:
            st.session_state[k] = False


with st.sidebar:
    st.image(
        "https://www.umontpellier.fr/wp-content/uploads/2022/10/logo_um_2022_rouge_rvb.svg",
        width=180,
    )
    st.caption("Randriamisaina Tsiory-Fanomezana · SHIRALI POUR Amir  \nUniversité de Montpellier — 2025-2026")
    st.markdown('<hr style="margin-top:0.2rem;margin-bottom:0.5rem;">', unsafe_allow_html=True)
    deux_colonnes = st.toggle("Affichage 2 colonnes", value=True)

    st.button(
        "Toutes les données",
        on_click=_reset,
        type="primary",
        use_container_width=True,
    )

    st.markdown("**Filtres**")
    f_annee   = st.checkbox("Filtrer par Année",     key='f_annee')
    f_lieu    = st.checkbox("Filtrer par Lieu",       key='f_lieu')
    f_contrat = st.checkbox("Filtrer par Contrat",    key='f_contrat')
    f_pop     = st.checkbox("Filtrer par Population", key='f_pop')

    with st.form("filtres"):
        annees = st.multiselect(
            "Année", [2021, 2022], default=[2021, 2022],
            disabled=not f_annee,
        )
        lieux = st.multiselect(
            "Lieu", ["SITE", "TELE"], default=["SITE", "TELE"],
            disabled=not f_lieu,
        )
        contrats = st.multiselect(
            "Contrat",
            df['agent_contrat'].dropna().unique().tolist(),
            default=df['agent_contrat'].dropna().unique().tolist(),
            disabled=not f_contrat,
        )
        populations = st.multiselect(
            "Population",
            df['agent_population'].dropna().unique().tolist(),
            default=df['agent_population'].dropna().unique().tolist(),
            disabled=not f_pop,
        )
        st.form_submit_button("Appliquer les filtres", use_container_width=True)



# --- Application des filtres
masque = pd.Series(True, index=df.index)
if f_annee   and annees:
    masque &= df['annee_ouverture'].isin(annees)
if f_lieu    and lieux:
    masque &= df['agent_lieu_travail'].isin(lieux)
if f_contrat and contrats:
    masque &= df['agent_contrat'].isin(contrats)
if f_pop     and populations:
    masque &= df['agent_population'].isin(populations)
df_filtre = df[masque]


# ------------------------------------------------------------
# NAVIGATION PAR ONGLETS
# Objectif : reproduire la navigation st.tabs() recommandée dans le cours.
# ------------------------------------------------------------
onglets = st.tabs([
    "Vue d'ensemble",
    "Qualité des données",
    "Analyse exploratoire",
    "Économétrie (OLS)",
    "Machine Learning",
    "Simulation & Recherche",
])


# ------------------------------------------------------------
# ONGLET 1 — VUE D'ENSEMBLE
# Objectif : synthèse des KPIs et distributions principales (Phases 1–4).
# ------------------------------------------------------------
with onglets[0]:
    st.title("Vue d'ensemble du Centre d'Assistance")
    st.markdown(
        "Tableau de bord synthétique des données après pré-traitement complet (Phases 1–4)."
    )
    st.caption(f"**{len(df_filtre):,}** dossiers sélectionnés sur {len(df):,} total")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Dossiers", f"{len(df_filtre):,}")
    col2.metric("Agents uniques", f"{df_filtre['Matricule.de.traitement'].nunique():,}")
    col3.metric(
        "Période",
        (f"{df_filtre['date.ouverture'].dt.year.min()}–"
         f"{df_filtre['date.ouverture'].dt.year.max()}")
        if len(df_filtre) > 0 else "—",
    )
    col4.metric("Durée médiane", f"{df_filtre['duree_totale_h'].median():.1f} h")
    col5.metric(
        "% NaN (durée)",
        f"{df_filtre['duree_totale_h'].isna().mean() * 100:.1f}%",
    )

    st.markdown("---")

    _T_A = (
        "Le volume de dossiers est plus élevé en 2022 qu'en 2021, ce qui reflète "
        "une croissance de l'activité du centre. Les pics en milieu d'année "
        "correspondent aux périodes de forte demande."
    )
    _T_B = (
        "La Formule F4 domine largement le portefeuille. Cette concentration sur "
        "quelques formules peut simplifier la gestion mais crée une dépendance "
        "commerciale à surveiller."
    )
    col_a, col_b = get_cols(deux_colonnes)

    with col_a:
        st.subheader("Distribution mensuelle des dossiers")
        df_mois = (
            df_filtre.groupby(['annee_ouverture', 'mois_ouverture'])
            .size().reset_index(name='n')
        )
        df_mois['periode'] = (
            df_mois['annee_ouverture'].astype(str)
            + '-M' + df_mois['mois_ouverture'].astype(str).str.zfill(2)
        )
        fig, ax = plt.subplots(figsize=(9, 4))
        couleurs_annee = [BLEU if a == 2021 else ORANGE for a in df_mois['annee_ouverture']]
        ax.bar(df_mois['periode'], df_mois['n'], color=couleurs_annee, edgecolor='white')
        ax.set_xlabel("Période")
        ax.set_ylabel("Nombre de dossiers")
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        from matplotlib.patches import Patch
        ax.legend(handles=[Patch(color=BLEU, label='2021'), Patch(color=ORANGE, label='2022')])
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()
        if not deux_colonnes:
            interprete(_T_A)

    with col_b:
        _dist_formule_full = df_filtre['Formule'].value_counts().dropna()
        _n_formules_total  = len(_dist_formule_full)
        _top10_formule     = _dist_formule_full.head(10)
        st.subheader("Répartition par Formule")
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        _top10_formule.sort_values().plot(kind='barh', ax=ax2, color=BLEU, edgecolor='white')
        ax2.set_xlabel("Nombre de dossiers")
        ax2.set_ylabel("")
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close()
        if _n_formules_total > 10:
            st.caption(
                f"{_n_formules_total} formules uniques au total — "
                f"seules les 10 plus fréquentes sont affichées."
            )
        if not deux_colonnes:
            interprete(_T_B)

    if deux_colonnes:
        interprete_pair(_T_A, _T_B)

    st.markdown("---")

    _T_C = (
        "Les clients C1 et C4 concentrent environ 52 % des dossiers, indiquant "
        "une forte dépendance vis-à-vis de deux grands comptes. Une diversification "
        "du portefeuille client réduirait le risque commercial."
    )
    _T_D = (
        "La quasi-parité SITE / TELE confirme que le télétravail est pleinement "
        "intégré dans l'organisation. L'analyse économétrique (Phase 5) montre que "
        "le télétravail réduit la durée de traitement de 5 %."
    )
    col_c, col_d = get_cols(deux_colonnes)

    with col_c:
        _dist_client_full = df_filtre['Client'].value_counts().dropna()
        _n_clients_total  = len(_dist_client_full)
        _top5_client      = _dist_client_full.head(5)
        _autres_client    = _dist_client_full.iloc[5:].sum() if _n_clients_total > 5 else 0
        if _autres_client > 0:
            _top5_client = pd.concat([_top5_client, pd.Series({'Autres': _autres_client})])
        st.subheader("Répartition par Client")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.pie(
            _top5_client.values, labels=_top5_client.index,
            autopct='%1.1f%%',
            colors=plt.cm.Blues(np.linspace(0.3, 0.9, len(_top5_client))),
        )
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)
        plt.close()
        if _n_clients_total > 5:
            st.caption(
                f"{_n_clients_total} clients uniques au total — "
                f"top 5 affichés, le reste regroupé en « Autres »."
            )
        if not deux_colonnes:
            interprete(_T_C)

    with col_d:
        st.subheader("Répartition par Lieu de travail de l'agent")
        dist_lieu = df_filtre['agent_lieu_travail'].value_counts()
        fig4, ax4 = plt.subplots(figsize=(5, 4))
        ax4.bar(dist_lieu.index, dist_lieu.values, color=[BLEU, ORANGE], edgecolor='white')
        ax4.set_ylabel("Nombre de dossiers")
        for i, v in enumerate(dist_lieu.values):
            ax4.text(i, v + 200, f"{v:,}", ha='center', fontsize=10)
        plt.tight_layout()
        st.pyplot(fig4, use_container_width=True)
        plt.close()
        if not deux_colonnes:
            interprete(_T_D)

    if deux_colonnes:
        interprete_pair(_T_C, _T_D)


# ------------------------------------------------------------
# ONGLET 2 — QUALITÉ DES DONNÉES
# Objectif : bilan des anomalies détectées et corrections appliquées
# dans chaque phase de pré-traitement (Phases 1, 2, 3).
# ------------------------------------------------------------
with onglets[1]:
    st.title("Qualité des Données — Bilan du Pré-traitement")
    st.subheader("Anomalies traitées par source")

    col1, col2, col3 = (
        st.columns(3) if deux_colonnes
        else (st.container(), st.container(), st.container())
    )

    with col1:
        st.markdown("#### dossier.csv (Phase 1)")
        anomalies_dossier = pd.DataFrame([
            {"Code": "A1", "Anomalie": "Doublons ID",            "N": "1 234",  "Action": "Suppression (keep=first)"},
            {"Code": "A2", "Anomalie": "Format date DD/MM/YYYY", "N": "var.",   "Action": "Conversion ISO"},
            {"Code": "A3", "Anomalie": "Dates hors 2021-2022",   "N": "1 065",  "Action": "Suppression"},
            {"Code": "A4", "Anomalie": "Survenance > Ouverture", "N": "1 032",  "Action": "Correction"},
            {"Code": "A5", "Anomalie": "Heure 25:00:00",         "N": "978",    "Action": "→ NaN"},
            {"Code": "A6", "Anomalie": "Valeurs '???'",           "N": "14 681", "Action": "→ NaN"},
            {"Code": "A7", "Anomalie": "'inconnu' (énergie)",     "N": "494",    "Action": "Conservé"},
            {"Code": "A8", "Anomalie": "Matricule orphelin",      "N": "1",      "Action": "Signalé"},
        ])
        st.dataframe(anomalies_dossier, hide_index=True, use_container_width=True)
        st.info("**98 935** lignes après nettoyage (vs 101 234 initiales — 2 299 supprimées)")

    with col2:
        st.markdown("#### ressources.csv (Phase 2)")
        anomalies_res = pd.DataFrame([
            {"Code": "B1", "Anomalie": "Format date DD/MM",    "N": "389 353", "Action": "Conversion ISO"},
            {"Code": "B2", "Anomalie": "Dates hors-période",   "N": "0",       "Action": "Aucune"},
            {"Code": "B3", "Anomalie": "NaN",                  "N": "0",       "Action": "Aucune"},
            {"Code": "B4", "Anomalie": "Valeurs '???'",         "N": "0",       "Action": "Aucune"},
            {"Code": "B5", "Anomalie": "Outliers durée",       "N": "var.",    "Action": "Signalé"},
            {"Code": "B6", "Anomalie": "Temps.travail const.", "N": "—",       "Action": "Non constant"},
            {"Code": "B7", "Anomalie": "Doublons Mat+Date",    "N": "0",       "Action": "Aucune"},
            {"Code": "B8", "Anomalie": "Expérience décroiss.", "N": "0",       "Action": "Aucune"},
        ])
        st.dataframe(anomalies_res, hide_index=True, use_container_width=True)
        st.info("**389 353** lignes — base complète (aucune suppression)")

    with col3:
        st.markdown("#### temps.csv (Phase 3)")
        anomalies_temps = pd.DataFrame([
            {"Code": "C1", "Anomalie": "NaN duree.corrigee",   "N": "47 471", "Action": "Conservé"},
            {"Code": "C2", "Anomalie": "Outliers durée",        "N": "var.",   "Action": "Signalé"},
            {"Code": "C3", "Anomalie": "Dates hors-période",    "N": "0",      "Action": "Aucune"},
            {"Code": "C4", "Anomalie": "Dossiers sans corresp", "N": "10 977", "Action": "Signalé"},
            {"Code": "C5", "Anomalie": "Dossiers sans temps",   "N": "2 180",  "Action": "Signalé"},
            {"Code": "C6", "Anomalie": "Doublons exacts",       "N": "0",      "Action": "Aucune"},
            {"Code": "C7", "Anomalie": "Heures invalides",      "N": "0",      "Action": "Aucune"},
            {"Code": "C8", "Anomalie": "Matricules orphelins",  "N": "var.",   "Action": "Signalé"},
        ])
        st.dataframe(anomalies_temps, hide_index=True, use_container_width=True)
        st.info("**431 598** lignes — 47 471 NaN durée conservés")

    st.markdown("---")
    st.subheader("Impact du nettoyage sur le volume des données")

    fig, ax = plt.subplots(figsize=(10, 4))
    sources = [
        'dossier.csv\n(brut)', 'dossier_nettoye\n(après Phase 1)',
        'ressources.csv\n(brut)', 'ressources_nettoyees\n(après Phase 2)',
        'temps.csv\n(brut)', 'temps_nettoye\n(après Phase 3)',
    ]
    volumes      = [101234, 98935, 389353, 389353, 431598, 431598]
    couleurs_vol = [BLEU, VERT, BLEU, VERT, BLEU, VERT]
    bars = ax.bar(sources, volumes, color=couleurs_vol, edgecolor='white')
    for bar, v in zip(bars, volumes):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 2000,
            f"{v:,}", ha='center', va='bottom', fontsize=9, fontweight='bold',
        )
    ax.set_ylabel("Nombre de lignes")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    from matplotlib.patches import Patch as _Patch
    ax.legend(handles=[_Patch(color=BLEU, label='Avant'), _Patch(color=VERT, label='Après')])
    ax.set_title("Volume des données avant/après nettoyage", fontsize=12, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()
    interprete(
        "Le nettoyage a supprimé seulement 2,3 % des dossiers (2 299 lignes), "
        "ce qui témoigne d'une qualité initiale correcte. Les fichiers ressources "
        "et temps n'ont subi aucune suppression — leur structure était déjà conforme."
    )


# ------------------------------------------------------------
# ONGLET 3 — ANALYSE EXPLORATOIRE
# Objectif : explorer interactivement les distributions, corrélations et
# relations entre variables, avec Hue Modality et statistiques descriptives
# (df.describe()) conformément au cours d'analyse exploratoire.
# ------------------------------------------------------------
