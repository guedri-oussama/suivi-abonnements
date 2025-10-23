# app.py — GUEDRI Oussama et DRUI Bernard
import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import matplotlib.pyplot as plt

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Suivi des abonnements", page_icon="💳", layout="wide")

# --- FONCTIONS UTILITAIRES ---
def charger_donnees():
    """Charge le fichier CSV ou crée un tableau vide si le fichier n’existe pas"""
    try:
        df = pd.read_csv("abonnements.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Nom", "Prix (€)", "Fréquence", "Date de début", "Catégorie", "Engagement"
        ])
    if not df.empty:
        df["Prix (€)"] = pd.to_numeric(df["Prix (€)"], errors="coerce").fillna(0.0)
        df["Date de début"] = pd.to_datetime(df["Date de début"], errors="coerce").dt.date
        if "Engagement" not in df.columns:
            df["Engagement"] = "Sans engagement"
    return df


def sauvegarder_donnees(df):
    """Sauvegarde les données dans le fichier CSV"""
    df.to_csv("abonnements.csv", index=False)


def cout_mensuel_equiv(prix, frequence):
    """Convertit un abonnement annuel en coût mensuel équivalent"""
    return prix if frequence == "Mensuel" else prix / 12


def prochaine_echeance(date_debut, frequence):
    """Calcule la prochaine échéance FUTURE selon la fréquence de paiement."""
    if pd.isna(date_debut):
        return None

    d = date_debut
    aujourd_hui = date.today()

    if frequence == "Mensuel":
        while d <= aujourd_hui:
            mois = d.month + 1
            annee = d.year + (mois - 1) // 12
            mois = 1 + (mois - 1) % 12
            jour = min(
                d.day,
                [31, 29 if annee % 4 == 0 and (annee % 100 != 0 or annee % 400 == 0) else 28,
                 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mois - 1]
            )
            d = date(annee, mois, jour)
    else:
        while d <= aujourd_hui:
            try:
                d = date(d.year + 1, d.month, d.day)
            except ValueError:
                d = date(d.year + 1, d.month, 28)

    return d


def fin_engagement(date_debut, engagement):
    """Calcule la date de fin d'engagement"""
    if pd.isna(date_debut):
        return None
    if engagement == "12 mois":
        return date_debut + timedelta(days=365)
    elif engagement == "24 mois":
        return date_debut + timedelta(days=730)
    else:
        return None


def statut_abonnement(r):
    """Retourne un statut simplifié et visuel"""
    aujourd_hui = date.today()
    prochaine = r.get("Prochaine échéance")
    fin = r.get("Fin d'engagement")
    engagement = r.get("Engagement")

    if pd.isna(prochaine):
        return "❌ Incomplet"

    if engagement != "Sans engagement":
        if fin and aujourd_hui > fin:
            return "🔴 Terminé"
        else:
            return "🔁 Renouvelé Auto"
    else:
        if prochaine > aujourd_hui:
            return "🟢 Actif"
        elif prochaine == aujourd_hui:
            return "🟡 Aujourd’hui"
        else:
            return "🟠 À surveiller"


# --- CHARGEMENT DES DONNÉES ---
data = charger_donnees()

# --- INTERFACE PRINCIPALE ---
st.title("💳 Suivi des abonnements")
st.caption("Suivez vos abonnements, vos dépenses et les échéances à venir.")

# --- FORMULAIRE D’AJOUT ---
st.subheader("➕ Ajouter un abonnement")
with st.form("form_add", clear_on_submit=True):
    nom = st.text_input("Nom de l’abonnement (ex : Netflix, Spotify...)")
    prix = st.number_input("Prix (€)", min_value=0.0, step=0.5)
    frequence = st.selectbox("Fréquence", ["Mensuel", "Annuel"])
    categorie = st.selectbox("Catégorie", ["Divertissement", "Musique", "Productivité", "Cloud", "Autre"])
    engagement = st.selectbox("Engagement", ["Sans engagement", "12 mois", "24 mois"])
    date_debut = st.date_input("Date de début", datetime.date.today())
    submitted = st.form_submit_button("Ajouter")

    if submitted:
        if nom.strip():
            nouveau = pd.DataFrame([[nom.strip(), prix, frequence, date_debut, categorie, engagement]],
                                   columns=data.columns)
            data = pd.concat([data, nouveau], ignore_index=True)
            sauvegarder_donnees(data)
            st.success(f"✅ Abonnement '{nom}' ajouté avec succès !")
        else:
            st.warning("⚠️ Veuillez entrer un nom d’abonnement valide.")

# --- TRAITEMENT DES DONNÉES ---
if not data.empty:
    data["Mensuel_équiv"] = data.apply(lambda r: cout_mensuel_equiv(r["Prix (€)"], r["Fréquence"]), axis=1)
    data["Prochaine échéance"] = data.apply(lambda r: prochaine_echeance(r["Date de début"], r["Fréquence"]), axis=1)
    data["Fin d'engagement"] = data.apply(lambda r: fin_engagement(r["Date de début"], r["Engagement"]), axis=1)
    data["Statut"] = data.apply(statut_abonnement, axis=1)

    # Supprimer la prochaine échéance pour les abonnements terminés
    data.loc[data["Statut"] == "🔴 Terminé", "Prochaine échéance"] = None

    aujourd_hui = date.today()
    data["Jours restants"] = data["Prochaine échéance"].apply(lambda d: (d - aujourd_hui).days if pd.notna(d) else None)

    # --- BARRE LATÉRALE DE FILTRES ---
    st.sidebar.header("🔍 Filtres")
    filtre = st.sidebar.text_input("Rechercher un abonnement")
    tri = st.sidebar.selectbox("Trier par :", ["Nom", "Prix (€)", "Fréquence", "Catégorie", "Engagement"])
    categorie_filtre = st.sidebar.multiselect("Filtrer par catégorie", data["Catégorie"].unique(),
                                              default=list(data["Catégorie"].unique()))
    engagement_filtre = st.sidebar.multiselect("Filtrer par engagement", data["Engagement"].unique(),
                                               default=list(data["Engagement"].unique()))

    # Application des filtres globaux
    data_filtrée = data[
        data["Nom"].str.contains(filtre, case=False, na=False) &
        data["Catégorie"].isin(categorie_filtre) &
        data["Engagement"].isin(engagement_filtre)
    ].sort_values(by=tri)

    # --- TABLEAU PRINCIPAL ---
    st.subheader("📋 Liste des abonnements filtrés")
    colonnes_affichees = [
        "Nom",
        "Date de début",
        "Engagement",
        "Statut",
        "Prix (€)",
        "Fréquence",
        "Catégorie",
        "Prochaine échéance"
    ]
    st.dataframe(data_filtrée[colonnes_affichees].reset_index(drop=True), use_container_width=True)

    # --- MÉTRIQUES ---
    cout_mensuel = data_filtrée["Mensuel_équiv"].sum()
    cout_annuel = cout_mensuel * 12
    st.sidebar.metric("💰 Coût mensuel total", f"{cout_mensuel:.2f} €")
    st.sidebar.metric("📆 Coût annuel total", f"{cout_annuel:.2f} €")

    # --- GRAPHIQUE BARRES ---
    st.subheader("📊 Répartition des coûts mensuels (filtrés)")
    if not data_filtrée.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(data_filtrée["Nom"], data_filtrée["Mensuel_équiv"], color="skyblue", edgecolor="black")
        ax.set_ylabel("€ / mois")
        plt.xticks(rotation=45, ha="right")
        for i, v in enumerate(data_filtrée["Mensuel_équiv"]):
            ax.text(i, v + 0.3, f"{v:.2f} €", ha="center")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Aucune donnée à afficher pour ce filtre.")

    # --- GRAPHIQUE CAMEMBERT ---
    st.subheader("🥧 Répartition des dépenses par catégorie (filtrées)")
    if not data_filtrée.empty:
        fig2, ax2 = plt.subplots()
        data_cat = data_filtrée.groupby("Catégorie")["Mensuel_équiv"].sum()
        ax2.pie(data_cat, labels=data_cat.index, autopct="%1.1f%%", startangle=90)
        ax2.axis("equal")
        st.pyplot(fig2)
    else:
        st.info("Aucune donnée pour afficher le graphique camembert.")

    # --- ALERTES VISUELLES ---
    bientot = data_filtrée[
        (data_filtrée["Prochaine échéance"].notna()) &
        (data_filtrée["Prochaine échéance"] >= aujourd_hui) &
        (data_filtrée["Prochaine échéance"] <= aujourd_hui + timedelta(days=7))
    ]

    if not bientot.empty:
        st.markdown("### 🚨 Abonnements à échéance cette semaine")

        def couleur_jours(row):
            jours = row["Jours restants"]
            if row["Engagement"] != "Sans engagement":
                return "🔁 Renouvelé Auto"
            if jours <= 2:
                return "🟥 Urgent"
            elif jours <= 5:
                return "🟧 Bientôt"
            else:
                return "🟨 À surveiller"

        bientot["⚠️ Statut"] = bientot.apply(couleur_jours, axis=1)
        alertes = bientot[["Nom", "Prochaine échéance", "Jours restants", "⚠️ Statut", "Engagement", "Mensuel_équiv"]]
        alertes = alertes.rename(columns={
            "Nom": "🧾 Nom",
            "Prochaine échéance": "📅 Échéance",
            "Jours restants": "⏳ Jours restants",
            "Engagement": "📄 Engagement",
            "Mensuel_équiv": "💰 Coût mensuel (€)"
        })
        st.dataframe(alertes.reset_index(drop=True), use_container_width=True)
    else:
        st.success("✅ Aucun abonnement à échéance proche (pour ce filtre).")

    # --- SUPPRESSION ---
    st.subheader("🗑️ Supprimer un abonnement")
    options = (data.index.astype(str) + " — " + data["Nom"].astype(str) +
               " — " + data["Fréquence"].astype(str) + " — " + data["Prix (€)"].astype(str) + "€")
    choix = st.selectbox("Sélectionnez un abonnement à supprimer", options)
    if st.button("Supprimer"):
        idx = int(choix.split(" — ")[0])
        data = data.drop(index=idx).reset_index(drop=True)
        sauvegarder_donnees(data)
        st.success("Abonnement supprimé avec succès ✅")
        st.experimental_rerun()
else:
    st.info("ℹ️ Aucun abonnement enregistré pour le moment.")
