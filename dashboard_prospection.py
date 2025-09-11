import streamlit as st
import pandas as pd
import sqlite3 # La bibliothèque pour interagir avec SQLite
from sqlalchemy import create_engine # Pour une écriture facile avec Pandas

# --- CONFIGURATION ET CONNEXION À LA BASE DE DONNÉES ---

st.set_page_config(page_title="Suivi Prospection CPG", layout="wide")

DB_FILE = "prospection.db"
TABLE_NAME = "contacts"

# On utilise SQLAlchemy pour que Pandas puisse écrire facilement dans la BDD.
engine = create_engine(f"sqlite:///{DB_FILE}")

@st.cache_data
def load_data_from_db():
    """Charge les données depuis la base de données SQLite et les met en cache."""
    try:
        with sqlite3.connect(DB_FILE) as con:
            print("Chargement des données depuis la base de données...") # Message pour le débogage
            # Utilise Pandas pour lire le résultat d'une requête SQL directement dans un DataFrame
            df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", con)
            return df
    except Exception as e:
        st.error(f"ERREUR : Impossible de lire la base de données '{DB_FILE}'. Détails : {e}")
        return pd.DataFrame()

def add_contact_to_db(new_row_df):
    """Ajoute une nouvelle ligne (DataFrame d'une ligne) à la base de données."""
    try:
        # 'append' ajoute les lignes du DataFrame à la table SQL existante.
        new_row_df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
        print("Contact ajouté à la base de données.")
        return True
    except Exception as e:
        st.error(f"ERREUR lors de l'ajout du contact : {e}")
        return False

# --- INTERFACE UTILISATEUR ---

def main():
    """Fonction principale pour construire la page Streamlit."""
    st.title("📊 Dashboard de Prospection CPG (Base de données SQLite)")

    fmcg_df = load_data_from_db()
    if fmcg_df.empty:
        st.warning("La base de données est vide ou n'a pas pu être chargée.")
        return

    COL_ENTREPRISE = "TOP 40 FMCG"
    
    # --- FILTRES ---
    entreprises = sorted(fmcg_df[COL_ENTREPRISE].dropna().unique())
    if not entreprises:
        st.info("Aucune entreprise à afficher pour le moment.")
        return

    if 'selected_entreprise' not in st.session_state or st.session_state.selected_entreprise not in entreprises:
        st.session_state.selected_entreprise = entreprises[0]

    selected_entreprise = st.selectbox(
        "Sélectionner une entreprise",
        options=entreprises,
        key='selected_entreprise'
    )

    # --- AFFICHAGE DES DONNÉES ---
    st.subheader(f"Contacts pour {selected_entreprise}")
    filtered_df = fmcg_df[fmcg_df[COL_ENTREPRISE] == selected_entreprise]
    st.dataframe(filtered_df)

    # --- FORMULAIRE D'AJOUT ---
    with st.expander("➕ Ajouter un nouveau contact"):
        with st.form("add_contact_form", clear_on_submit=True):
            prenom = st.text_input("Prénom")
            nom = st.text_input("Nom")
            entreprise = st.selectbox("Entreprise", options=entreprises, index=entreprises.index(st.session_state.selected_entreprise))
            role = st.text_input("Rôle")
            contact_envoye = st.selectbox("Contact envoyé", options=["O", "N"])
            contact_accepte = st.selectbox("Contact Accepté O/N", options=["O", "N"])
            prospection = st.selectbox("Prospection (O/N)", options=["O", "N"])
            retour = st.selectbox("Retour (O/N)", options=["O", "N"])
            next_steps = st.text_input("Next steps")
            person_interest = st.text_input("Person of interest")

            submitted = st.form_submit_button("Ajouter le contact")

            if submitted:
                new_row = {
                    "Prénom": [prenom], "Nom": [nom], COL_ENTREPRISE: [entreprise],
                    "Rôle": [role], "Contact envoyé": [contact_envoye], "Contact Accepté O/N": [contact_accepte],
                    "Prospection (O/N)": [prospection], "Retour (O/N)": [retour],
                    "Next steps": [next_steps], "Person of interest": [person_interest]
                }
                new_row_df = pd.DataFrame(new_row)
                
                if add_contact_to_db(new_row_df):
                    st.success("✅ Contact ajouté avec succès à la base de données !")
                    st.cache_data.clear() # Vide le cache pour forcer le rechargement des données

if __name__ == "__main__":
    main()