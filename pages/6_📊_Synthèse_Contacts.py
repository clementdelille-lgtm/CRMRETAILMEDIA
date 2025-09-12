# 6_📊_Synthèse_Contacts.py
import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

# --- Page Configuration ---
st.set_page_config(layout="wide")
st.title("Synthèse Contacts : Le Control Center 🚀")
st.markdown("Identifiez, triez et gérez tous vos contacts de manière visuelle et interactive.")

# --- Fonctions de récupération et de mise en forme des données ---
@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def get_all_contacts_with_compte():
    """Retrieves all contacts along with their associated company name."""
    try:
        query = """
            SELECT
                c.id,
                c.prenom,
                c.nom,
                c.statut_prospection,
                c.date_prochaine_action,
                c.prochaine_action_notes,
                c.date_derniere_interaction,
                c.email,
                c.linkedin,
                co.nom AS compte_nom
            FROM
                contacts c
            JOIN
                comptes co ON c.compte_id = co.id
            ORDER BY
                c.nom, c.prenom
        """
        # Obtenir la connexion et vérifier si elle est valide
        con = db.get_db_connection()
        if con:
            df = pd.read_sql(query, con)
            # Important : fermer la connexion
            con.close()
        else:
            df = pd.DataFrame()
        
        # Convert date columns to datetime objects, with NaT for null values
        df['date_prochaine_action'] = pd.to_datetime(df['date_prochaine_action'], errors='coerce')
        df['date_derniere_interaction'] = pd.to_datetime(df['date_derniere_interaction'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erreur lors de la récupération des contacts : {e}")
        return pd.DataFrame()

def get_status_tag(status):
    """Returns an HTML styled tag for the contact status."""
    colors = {
        "À Contacter": "2196F3",
        "Contacté": "FFC107",
        "Intéressé": "4CAF50",
        "Non intéressé": "F44336",
    }
    hex_color = colors.get(status, "AAAAAA")
    return f"<span style='background-color:#{hex_color}; color:white; padding: 4px 8px; border-radius: 12px; font-weight: bold;'>{status}</span>"

def get_next_action_indicator(row):
    """Returns an icon and formatted date for the next action, handling NaT."""
    date_prochaine_action = row['date_prochaine_action']
    
    if pd.isna(date_prochaine_action):
        return "Pas d'action"
    
    today = datetime.now().date()
    
    if date_prochaine_action.date() < today:
        color = 'red'
        formatted_date = date_prochaine_action.strftime('%d/%m/%Y')
        return f"⏰ <span style='color:{color}; font-weight:bold;'>{formatted_date}</span>"
    else:
        color = 'green'
        formatted_date = date_prochaine_action.strftime('%d/%m/%Y')
        return f"⏰ <span style='color:{color};'>{formatted_date}</span>"

def format_last_interaction(date_obj):
    """Returns the last interaction date with a 'heat map' color, handling NaT."""
    if pd.isna(date_obj):
        return "<span style='color:red;'>Jamais</span>"

    today = datetime.now().date()
    days_ago = (today - date_obj.date()).days
    
    if days_ago <= 7:
        color = "green"
    elif days_ago <= 30:
        color = "orange"
    else:
        color = "red"
        
    return f"<span style='color:{color};'>{date_obj.strftime('%d/%m/%Y')}</span>"

# --- Main Page Content ---
df_contacts = get_all_contacts_with_compte()

if not df_contacts.empty:
    
    # --- Data Filtering and Search ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Rechercher par nom ou prénom")
    with col2:
        selected_compte = st.selectbox("Filtrer par compte", ["Tous les comptes"] + sorted(df_contacts['compte_nom'].unique().tolist()))
    with col3:
        status_list = df_contacts['statut_prospection'].unique().tolist()
        status_list_filtered = [s for s in status_list if s is not None]
        selected_status = st.selectbox("Filtrer par statut", ["Tous les statuts"] + sorted(status_list_filtered))

    filtered_df = df_contacts.copy()

    # Apply filters
    if search_query:
        filtered_df = filtered_df[filtered_df['nom'].str.contains(search_query, case=False) | 
                                 filtered_df['prenom'].str.contains(search_query, case=False)]
    if selected_compte != "Tous les comptes":
        filtered_df = filtered_df[filtered_df['compte_nom'] == selected_compte]
    if selected_status != "Tous les statuts":
        filtered_df = filtered_df[filtered_df['statut_prospection'] == selected_status]

    # --- Data formatting for display ---
    filtered_df['Contact'] = filtered_df['prenom'] + " " + filtered_df['nom']
    filtered_df['Compte'] = filtered_df['compte_nom']
    filtered_df['Statut'] = filtered_df['statut_prospection'].apply(get_status_tag)
    
    filtered_df['Prochaine Action'] = filtered_df.apply(get_next_action_indicator, axis=1)
    filtered_df['Dernière Interaction'] = filtered_df['date_derniere_interaction'].apply(format_last_interaction)
    
    filtered_df['Liens'] = filtered_df.apply(
        lambda row: f"<a href='mailto:{row['email']}' target='_blank'>📧</a> <a href='{row['linkedin']}' target='_blank'>🔗</a>",
        axis=1
    )
    
    # Add a link to the detailed contact page
    filtered_df['Action'] = filtered_df['id'].apply(
        lambda x: f"<a href='/Gestion_Contacts?contact_id={x}' target='_self'>🖊️</a>"
    )

    # Reorder and select columns for display
    display_df = filtered_df[['Contact', 'Compte', 'Statut', 'Prochaine Action', 'Dernière Interaction', 'Liens']]
    
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

else:
    st.info("Aucun contact à afficher. Veuillez vérifier votre connexion à la base de données ou ajouter de nouveaux contacts via la page 'Gestion des Comptes'.")