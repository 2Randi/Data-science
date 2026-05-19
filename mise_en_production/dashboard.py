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
with onglets[2]:
    st.title("Analyse Exploratoire Interactive")
    st.caption(f"**{len(df_filtre):,}** dossiers sélectionnés sur {len(df):,} total")

    # --- Hue Modality — auto-détection des colonnes catégorielles
    # Objectif : détecter automatiquement les variables catégorielles.
    # Pour les colonnes à forte cardinalité, les modalités rares sont
    # regroupées en "Autres" (top 10 conservées, reste agrégé).
    cols_cat = df_filtre.select_dtypes(exclude=['int64', 'float64']).columns.tolist()
    hue_var = st.selectbox(
        "Colorier par (Hue Modality) :",
        options=[None] + cols_cat,
        format_func=lambda x: "— Aucun —" if x is None else x,
    )

    def _applique_hue(frame: pd.DataFrame, col: str, top_n: int = 10) -> pd.Series:
        """Regroupe les modalités rares en 'Autres' pour limiter la légende."""
        top = frame[col].value_counts().nlargest(top_n).index
        return frame[col].where(frame[col].isin(top), other='Autres').astype(str)

    st.markdown("---")

    # --- Statistiques descriptives (df.describe())
    # Objectif : résumer les variables numériques et catégorielles du jeu filtré.
    st.subheader("Statistiques descriptives")
    col_num, col_cat_desc = get_cols(deux_colonnes)
    with col_num:
        st.markdown("**Variables numériques**")
        st.dataframe(df_filtre.describe().round(2), use_container_width=True)
    with col_cat_desc:
        st.markdown("**Variables catégorielles**")
        df_cat_only = df_filtre.select_dtypes(exclude=['int64', 'float64'])
        st.dataframe(df_cat_only.describe(), use_container_width=True)

    st.markdown("---")

    # --- Distribution de la durée + Durée par cause
    _T1 = (
        "La distribution est fortement asymétrique à droite (queue longue) : "
        "la majorité des dossiers est traitée rapidement (< 20 h), mais quelques "
        "cas extrêmes tirent la moyenne vers le haut. La médiane est donc "
        "l'indicateur central le plus approprié pour ce jeu de données."
    )
    _T2 = (
        "Les causes d'intervention en tête de ce classement requièrent "
        "significativement plus de temps. Cette information est clé pour "
        "prioriser l'allocation de ressources expérimentées aux dossiers complexes."
    )
    col1, col2 = get_cols(deux_colonnes)

    with col1:
        st.subheader("Distribution de la durée de traitement")
        duree_valide = df_filtre['duree_totale_h'].dropna()
        p99 = duree_valide.quantile(0.99)
        fig, ax = plt.subplots(figsize=(7, 4))
        if hue_var:
            df_hist = df_filtre.dropna(subset=['duree_totale_h'])
            df_hist = df_hist[df_hist['duree_totale_h'] <= p99].copy()
            df_hist[hue_var] = _applique_hue(df_hist, hue_var)
            sns.histplot(
                data=df_hist, x='duree_totale_h', hue=hue_var,
                bins=60, ax=ax, alpha=0.7, element='step',
            )
        else:
            duree_p99 = duree_valide[duree_valide <= p99]
            ax.hist(duree_p99, bins=60, color=BLEU, edgecolor='white')
            ax.axvline(
                duree_p99.median(), color=ROUGE, linestyle='--',
                label=f"Médiane : {duree_p99.median():.1f}h",
            )
            ax.legend()
        ax.set_xlabel("Durée totale (heures)")
        ax.set_ylabel("Fréquence")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()
        if not deux_colonnes:
            interprete(_T1)

    with col2:
        st.subheader("Durée médiane par Cause d'intervention")
        df_cause = (
            df_filtre.groupby('Cause.intervention')['duree_totale_h']
            .median().dropna().sort_values(ascending=False).head(10)
        )
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        df_cause.sort_values().plot(kind='barh', ax=ax2, color=BLEU, edgecolor='white')
        ax2.set_xlabel("Durée médiane (heures)")
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close()
        if not deux_colonnes:
            interprete(_T2)

    if deux_colonnes:
        interprete_pair(_T1, _T2)

    st.markdown("---")

    # --- Scatter expérience vs durée + Matrice de corrélation
    _T3 = (
        "L'absence de corrélation visuelle entre l'expérience et la durée de "
        "traitement est confirmée par le modèle OLS (p = 0,134 — non significatif). "
        "D'autres facteurs (type de contrat, population de l'agent) expliquent "
        "davantage la variabilité."
    )
    _chemin_corr = img('phase5_matrice_correlation.png')
    _T4 = (
        "Les corrélations les plus fortes avec la durée de traitement "
        "concernent le nombre d'interventions et le nombre d'agents distincts. "
        "Les variables d'expérience et de durée de travail de l'agent "
        "présentent une corrélation quasi nulle avec la variable cible."
        if _chemin_corr else ""
    )
    col3, col4 = get_cols(deux_colonnes)

    with col3:
        st.subheader("Expérience vs Durée de traitement")
        sample = df_filtre.dropna(
            subset=['agent_experience_j', 'duree_totale_h']
        ).sample(min(3000, len(df_filtre)), random_state=42).copy()
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        if hue_var:
            sample[hue_var] = _applique_hue(sample, hue_var)
            sns.scatterplot(
                data=sample, x='agent_experience_j', y='duree_totale_h',
                hue=hue_var, ax=ax3, alpha=0.4, s=12,
            )
        else:
            ax3.scatter(
                sample['agent_experience_j'], sample['duree_totale_h'],
                alpha=0.25, s=8, color=BLEU,
            )
        ax3.set_xlabel("Expérience (jours)")
        ax3.set_ylabel("Durée totale (heures)")
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)
        plt.close()
        if not deux_colonnes:
            interprete(_T3)

    with col4:
        st.subheader("Matrice de corrélation")
        if _chemin_corr:
            st.image(_chemin_corr, use_container_width=True)
            if not deux_colonnes:
                interprete(_T4)
        else:
            st.info("Exécutez d'abord le notebook Phase 5.")

    if deux_colonnes:
        interprete_pair(_T3, _T4)


# ------------------------------------------------------------
# ONGLET 4 — ÉCONOMÉTRIE (OLS)
# Objectif : présenter les résultats de la régression OLS (Phase 5),
# les tests de Gauss-Markov et l'interprétation des coefficients.
# ------------------------------------------------------------
with onglets[3]:
    st.title("Résultats Économétriques — Régression OLS")
    st.markdown(
        "**Variable dépendante :** `log(1 + duree_totale_h)` (durée log-transformée)  \n"
        "**Méthode :** Ordinary Least Squares (OLS) avec erreurs standard robustes HC3"
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("R²", "0.265")
    col2.metric("R² ajusté", "0.265")
    col3.metric("F-statistic", "2 997")
    col4.metric("Durbin-Watson", "2.010")
    col5.metric("Observations", "91 526")

    st.markdown("---")
    interprete(
        "Un R² de 0,265 signifie que le modèle explique 26,5 % de la variance de la "
        "durée de traitement. C'est modeste mais attendu pour des données comportementales "
        "humaines. La F-statistique très élevée (2 997) confirme que l'ensemble des "
        "variables est globalement significatif."
    )
    st.markdown("---")

    st.subheader("Résumé du modèle OLS")
    ols_txt = charger_ols_summary()
    st.code(ols_txt, language=None)

    st.markdown("---")
    st.subheader("Tests des hypothèses classiques (Gauss-Markov)")

    _p_norm = img('phase5_normalite_residus.png')
    _p_homo = img('phase5_homoscedasticite.png')
    _T_NORM = (
        "Le QQ-plot révèle une légère déviation aux extrêmes (queues lourdes), "
        "ce qui est typique des durées de traitement. Le recours aux erreurs "
        "standard robustes (HC3) permet de corriger l'hétéroscédasticité sans "
        "exclure d'observations." if _p_norm else ""
    )
    _T_HOMO = (
        "Le test de Breusch-Pagan rejette l'homoscédasticité (variance non constante "
        "des résidus). C'est la raison pour laquelle les erreurs standard robustes "
        "HC3 ont été appliquées — les coefficients restent valides, seules les "
        "inférences statistiques sont corrigées." if _p_homo else ""
    )

    col_a, col_b = get_cols(deux_colonnes)
    with col_a:
        if _p_norm:
            st.image(_p_norm, caption="6a — Normalité des résidus", use_container_width=True)
            if not deux_colonnes:
                interprete(_T_NORM)

    with col_b:
        if _p_homo:
            st.image(
                _p_homo, caption="6b — Homoscédasticité (Breusch-Pagan)",
                use_container_width=True,
            )
            if not deux_colonnes:
                interprete(_T_HOMO)

    if deux_colonnes:
        interprete_pair(_T_NORM, _T_HOMO)

    st.markdown("---")
    st.subheader("Interprétation des coefficients significatifs (p < 0.05)")
    coefs = pd.DataFrame([
        {"Variable": "C(agent_population)[T.CAC]",   "Coeff.": -0.5118, "p-value": "0.000", "Interprétation": "Les agents CAC traitent les dossiers 51% plus vite (log-échelle)"},
        {"Variable": "nb_agents_distincts",           "Coeff.": +0.1208, "p-value": "0.000", "Interprétation": "Chaque agent supplémentaire augmente la durée de 12%"},
        {"Variable": "C(agent_contrat)[T.CDS]",       "Coeff.": +0.1423, "p-value": "0.000", "Interprétation": "Les contrats CDS sont associés à +14% de durée"},
        {"Variable": "C(agent_contrat)[T.CDD]",       "Coeff.": +0.0574, "p-value": "0.000", "Interprétation": "Les contrats CDD sont associés à +6% de durée"},
        {"Variable": "nb_interventions",              "Coeff.": +0.0226, "p-value": "0.000", "Interprétation": "Chaque intervention supplémentaire augmente la durée de 2%"},
        {"Variable": "delai_survenance_ouverture_j",  "Coeff.": +0.0024, "p-value": "0.000", "Interprétation": "Un délai plus long → traitement plus long"},
        {"Variable": "C(agent_lieu_travail)[T.TELE]", "Coeff.": -0.0530, "p-value": "0.000", "Interprétation": "Le télétravail réduit la durée de 5%"},
        {"Variable": "C(annee_ouverture)[T.2022]",    "Coeff.": +0.0343, "p-value": "0.000", "Interprétation": "2022 : durées légèrement plus longues qu'en 2021"},
        {"Variable": "mois_ouverture",                "Coeff.": +0.0046, "p-value": "0.000", "Interprétation": "Effet saisonnier léger (+0.5% par mois)"},
    ])
    st.dataframe(coefs, hide_index=True, use_container_width=True)
    st.markdown(
        "> **Variables non significatives (p > 0.05) :**  \n"
        "> `agent_experience_j` (p=0.134) et `agent_duree_travail_j` (p=0.422)  \n"
        "> L'expérience et la durée de travail n'ont pas d'effet significatif sur la durée."
    )
    interprete(
        "Le résultat le plus saillant est l'effet de la population de l'agent : "
        "les agents CAC réduisent la durée de 51 %, ce qui suggère une spécialisation "
        "opérationnelle forte. En revanche, l'expérience accumulée (en jours) n'est "
        "pas significative — c'est contre-intuitif mais cohérent avec une organisation "
        "où la formation initiale prime sur l'ancienneté."
    )


# ------------------------------------------------------------
# ONGLET 5 — MACHINE LEARNING
# Objectif : présenter la comparaison des modèles ML (Phase 6),
# la feature importance et les métriques de performance.
# ------------------------------------------------------------
with onglets[4]:
    st.title("Résultats Machine Learning")

    col1, col2 = get_cols(deux_colonnes)
    _p_reg = img('phase6_regression_comparaison.png')
    _p_imp = img('phase6_feature_importance_regression.png')
    _T_REG = (
        "Gradient Boosting domine (R²=0,63) avec le meilleur équilibre "
        "biais-variance. Random Forest surapprentit fortement "
        "(R²train=0,93 vs R²test=0,61), ce qui le rend moins fiable "
        "sur de nouveaux dossiers." if _p_reg else ""
    )
    _T_IMP = (
        "Les variables les plus importantes confirment les résultats OLS : "
        "le nombre d'interventions et d'agents distincts dominent. "
        "Le modèle ML identifie aussi des interactions non-linéaires "
        "invisibles dans la régression OLS." if _p_imp else ""
    )

    with col1:
        st.subheader("Tâche 1 — Régression : prédire `duree_totale_h`")
        if _p_reg:
            st.image(
                _p_reg, caption="Comparaison des modèles de régression",
                use_container_width=True,
            )
            if not deux_colonnes:
                interprete(_T_REG)

    with col2:
        st.markdown("#### Résultats numériques")
        resultats_reg = pd.DataFrame([
            {"Modèle": "GradientBoostingRegressor", "RMSE": 20.233, "MAE": 9.574,  "R² test": 0.6289, "R² train": 0.5646},
            {"Modèle": "LinearRegression",          "RMSE": 20.579, "MAE": 9.879,  "R² test": 0.6161, "R² train": 0.5188},
            {"Modèle": "RandomForestRegressor",     "RMSE": 20.808, "MAE": 10.279, "R² test": 0.6075, "R² train": 0.9278},
        ])
        st.dataframe(resultats_reg, hide_index=True, use_container_width=True)
        st.success(
            "**GradientBoostingRegressor** — meilleur R² test (0.63) "
            "avec le moins de surapprentissage"
        )
        if _p_imp:
            st.image(
                _p_imp, caption="Top 15 Features — meilleur modèle",
                use_container_width=True,
            )
            if not deux_colonnes:
                interprete(_T_IMP)

    if deux_colonnes:
        interprete_pair(_T_REG, _T_IMP)

    st.markdown("---")
    st.subheader("Tâche 2 — Classification : prédire `Cause.intervention`")

    _p_clf = img('phase6_classification_comparaison.png')
    _p_cm  = img('phase6_matrice_confusion.png')
    _T_CLF = (
        "La classification est une tâche plus difficile : prédire la "
        "cause d'intervention à partir des caractéristiques de l'agent "
        "et du dossier est ambitieux. Les scores reflètent la difficulté "
        "inhérente du problème (classes déséquilibrées)." if _p_clf else ""
    )
    _T_CM  = (
        "La diagonale concentre les bonnes prédictions. Les erreurs "
        "hors-diagonale indiquent les confusions fréquentes entre causes "
        "proches — information utile pour affiner le modèle ou regrouper "
        "des catégories similaires." if _p_cm else ""
    )

    col3, col4 = get_cols(deux_colonnes)
    with col3:
        if _p_clf:
            st.image(
                _p_clf, caption="Comparaison des modèles de classification",
                use_container_width=True,
            )
            if not deux_colonnes:
                interprete(_T_CLF)

    with col4:
        if _p_cm:
            st.image(
                _p_cm, caption="Matrice de confusion — meilleur modèle",
                use_container_width=True,
            )
            if not deux_colonnes:
                interprete(_T_CM)

    if deux_colonnes:
        interprete_pair(_T_CLF, _T_CM)

    st.markdown("---")
    st.subheader("Rappel méthodologique")
    st.markdown("""
| Décision | Justification |
|----------|--------------|
| Pipeline sklearn | Évite le data leakage (transformations apprises sur train uniquement) |
| SimpleImputer(median) | Conserve toutes les observations malgré les NaN résiduels |
| train_test_split 80/20 | Standard — stratifié pour la classification |
| 3 modèles comparés | Baseline linéaire + 2 ensembles pour robustesse |
""")


# ------------------------------------------------------------
# ONGLET 6 — SIMULATION & RECHERCHE
# Objectif : permettre la recherche de dossiers existants par filtres SQL
# et la simulation de durée via les modèles ML (GradientBoosting) et
# OLS (log-linéaire) sauvegardés dans data/.
# ------------------------------------------------------------
with onglets[5]:
    st.title("Recherche et Simulation")
    st.markdown(
        "Recherchez des dossiers existants ou simulez la durée de traitement "
        "pour de nouvelles données."
    )

    modele_ml, modele_eco = charger_modeles()

    st.markdown("---")
    st.header("Recherche de dossiers")

    with st.expander("Filtres de recherche", expanded=False):
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            search_annee = st.multiselect(
                "Année d'ouverture",
                options=sorted(df['annee_ouverture'].dropna().unique()),
            )
            search_mois = st.multiselect(
                "Mois d'ouverture",
                options=sorted(df['mois_ouverture'].dropna().unique()),
            )
        with col_r2:
            search_contrat = st.multiselect(
                "Type de contrat (Agent)",
                options=df['agent_contrat'].dropna().unique(),
            )
            search_lieu = st.multiselect(
                "Lieu de travail (Agent)",
                options=df['agent_lieu_travail'].dropna().unique(),
            )
        with col_r3:
            search_cause = st.multiselect(
                "Cause d'intervention",
                options=df['Cause.intervention'].dropna().unique(),
            )

    df_search = df_filtre.copy()
    if search_annee:
        df_search = df_search[df_search['annee_ouverture'].isin(search_annee)]
    if search_mois:
        df_search = df_search[df_search['mois_ouverture'].isin(search_mois)]
    if search_contrat:
        df_search = df_search[df_search['agent_contrat'].isin(search_contrat)]
    if search_lieu:
        df_search = df_search[df_search['agent_lieu_travail'].isin(search_lieu)]
    if search_cause:
        df_search = df_search[df_search['Cause.intervention'].isin(search_cause)]

    st.write(f"**{len(df_search):,}** résultats trouvés.")
    st.dataframe(df_search.head(100), use_container_width=True)
    if len(df_search) > 100:
        st.caption(
            "Aperçu limité aux 100 premières lignes pour des raisons de performance."
        )

    st.markdown("---")
    st.header("Simulation (Estimation de la durée)")
    st.markdown(
        "Saisissez les informations d'un dossier pour estimer sa "
        "**durée totale de traitement**."
    )

    if modele_ml is None or modele_eco is None:
        st.warning(
            "Les modèles ne sont pas disponibles. "
            "Exécutez le script `mise_en_production/train_and_save_models.py` au préalable."
        )
    else:
        with st.form("form_simulation"):
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                st.subheader("Variables Numériques")
                agent_experience_j = st.number_input(
                    "Expérience de l'agent (en jours)", min_value=0, value=365, step=30,
                )
                agent_duree_travail_j = st.number_input(
                    "Durée de travail de l'agent (en jours)", min_value=0, value=1000, step=30,
                )
                agent_temps_travail_pct = st.number_input(
                    "Temps de travail (%)", min_value=0, max_value=100, value=100,
                )
                delai_survenance_ouverture_j = st.number_input(
                    "Délai survenance - ouverture (jours)", min_value=0, value=2, step=1,
                )
                nb_interventions = st.number_input(
                    "Nombre d'interventions", min_value=1, value=1, step=1,
                )
                nb_agents_distincts = st.number_input(
                    "Nombre d'agents distincts", min_value=1, value=1, step=1,
                )
                mois_ouverture = st.number_input(
                    "Mois d'ouverture (1-12)", min_value=1, max_value=12, value=1,
                )

            with col_f2:
                st.subheader("Variables Catégorielles")
                agent_lieu_travail = st.selectbox(
                    "Lieu de travail",
                    options=df['agent_lieu_travail'].dropna().unique(),
                )
                agent_contrat = st.selectbox(
                    "Type de contrat",
                    options=df['agent_contrat'].dropna().unique(),
                )
                agent_population = st.selectbox(
                    "Population de l'agent",
                    options=df['agent_population'].dropna().unique(),
                )
                annee_ouverture = st.selectbox(
                    "Année d'ouverture",
                    options=['2021', '2022', '2023', '2024'],
                )

            submitted = st.form_submit_button("Estimer la durée")

        if submitted:
            input_data = pd.DataFrame([{
                'agent_experience_j':          agent_experience_j,
                'agent_duree_travail_j':        agent_duree_travail_j,
                'agent_temps_travail_pct':      agent_temps_travail_pct,
                'delai_survenance_ouverture_j': delai_survenance_ouverture_j,
                'nb_interventions':             nb_interventions,
                'nb_agents_distincts':          nb_agents_distincts,
                'mois_ouverture':               mois_ouverture,
                'agent_lieu_travail':           agent_lieu_travail,
                'agent_contrat':                agent_contrat,
                'agent_population':             agent_population,
                'annee_ouverture':              str(annee_ouverture),
            }])

            try:
                # ML prédit la durée brute (heures)
                pred_ml = modele_ml.predict(input_data)[0]

                # OLS prédit log(1 + h) → back-transformation expm1
                pred_eco_log = modele_eco.predict(input_data)[0]
                pred_eco = np.expm1(pred_eco_log)

                st.success("Estimation réussie !")
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric(
                        label="Estimation Machine Learning (Gradient Boosting)",
                        value=f"{pred_ml:.2f} h",
                    )
                    st.caption(
                        "Modèle non-linéaire entraîné sur la durée brute (heures). "
                        "Capture les interactions complexes entre variables."
                    )
                with col_res2:
