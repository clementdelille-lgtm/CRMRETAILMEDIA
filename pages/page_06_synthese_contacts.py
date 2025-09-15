'''
This module provides a summary view of all contacts in the CRM,
allowing for interactive filtering and searching.
'''

import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

# --- Data Fetching ---

@st.cache_data(ttl=600)
def get_all_contacts_with_compte():
    """
    Retrieves all contacts from the database along with their associated
    company name. The data is cached for 10 minutes.

    Returns:
        pd.DataFrame: A DataFrame containing contact information.
                      Returns an empty DataFrame on error.
    """
    query = '''
        SELECT
            c.id, c.prenom, c.nom, c.statut_prospection,
            c.date_prochaine_action, c.prochaine_action_notes,
            c.date_derniere_interaction, c.email, c.linkedin,
            co.nom AS compte_nom
        FROM contacts c
        JOIN comptes co ON c.compte_id = co.id
        ORDER BY c.nom, c.prenom
    '''
    try:
        con = db.get_db_connection()
        if not con:
            st.error("La connexion à la base de données a échoué.")
            return pd.DataFrame()
        
        df = pd.read_sql(query, con)
        df['date_prochaine_action'] = pd.to_datetime(df['date_prochaine_action'], errors='coerce')
        df['date_derniere_interaction'] = pd.to_datetime(df['date_derniere_interaction'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erreur lors de la récupération des contacts : {e}")
        return pd.DataFrame()
    finally:
        if 'con' in locals() and con:
            con.close()

# --- UI Helper Functions ---

def get_status_tag(status):
    """Returns an HTML styled tag for the contact status."""
    colors = {
        "À Contacter": "2196F3",
        "Contacté": "FFC107",
        "Intéressé": "4CAF50",
        "Non intéressé": "F44336",
    }
    hex_color = colors.get(status, "AAAAAA")
    style = f"background-color:#{hex_color}; color:white; padding: 4px 8px; border-radius: 12px; font-weight: bold;"
    return f"<span style='{style}'>{status}</span>"

def get_next_action_indicator(row):
    """Returns an icon and formatted date for the next action."""
    date_prochaine_action = row['date_prochaine_action']
    if pd.isna(date_prochaine_action):
        return "Pas d'action"

    today = datetime.now().date()
    action_date = date_prochaine_action.date()
    formatted_date = action_date.strftime('%d/%m/%Y')

    if action_date < today:
        color = 'red'
        return f"⏰ <span style='color:{color}; font-weight:bold;'>{formatted_date}</span>"

    color = 'green'
    return f"⏰ <span style='color:{color};'>{formatted_date}</span>"


def format_last_interaction(date_obj):
    """Returns the last interaction date with a 'heat map' color."""
    if pd.isna(date_obj):
        return "<span style='color:red;'>Jamais</span>"

    days_ago = (datetime.now().date() - date_obj.date()).days
    if days_ago <= 7:
        color = "green"
    elif days_ago <= 30:
        color = "orange"
    else:
        color = "red"

    return f"<span style='color:{color};'>{date_obj.strftime('%d/%m/%Y')}</span>"

def display_filters(df):
    """Displays filter widgets and returns the selected filter values."""
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("Rechercher par nom ou prénom")
    with col2:
        comptes = ["Tous les comptes"] + sorted(df['compte_nom'].unique().tolist())
        selected_compte = st.selectbox("Filtrer par compte", comptes)
    with col3:
        status_list = [s for s in df['statut_prospection'].unique() if s is not None]
        status_options = ["Tous les statuts"] + sorted(status_list)
        selected_status = st.selectbox("Filtrer par statut", status_options)

    return search_query, selected_compte, selected_status

def apply_filters(df, search_query, selected_compte, selected_status):
    """Applies filters to the DataFrame."""
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            df['nom'].str.contains(search_query, case=False) |
            df['prenom'].str.contains(search_query, case=False)
        ]
    if selected_compte != "Tous les comptes":
        filtered_df = filtered_df[df['compte_nom'] == selected_compte]
    if selected_status != "Tous les statuts":
        filtered_df = filtered_df[df['statut_prospection'] == selected_status]
    return filtered_df

def format_dataframe_for_display(df):
    """Formats the filtered DataFrame for HTML display."""
    display_df = pd.DataFrame()
    display_df['Contact'] = df['prenom'] + " " + df['nom']
    display_df['Compte'] = df['compte_nom']
    display_df['Statut'] = df['statut_prospection'].apply(get_status_tag)
    display_df['Prochaine Action'] = df.apply(get_next_action_indicator, axis=1)
    display_df['Dernière Interaction'] = df['date_derniere_interaction'].apply(format_last_interaction)
    display_df['Liens'] = df.apply(
        lambda row: f"<a href='mailto:{row['email']}' target='_blank'>📧</a> "
                    f"<a href='{row['linkedin']}' target='_blank'>🔗</a>",
        axis=1
    )
    display_df['Action'] = df['id'].apply(
        lambda x: f"<a href='/page_03_gestion_contacts?contact_id={x}' target='_self'>🖊️</a>"
    )
    return display_df[[
        'Contact', 'Compte', 'Statut', 'Prochaine Action',
        'Dernière Interaction', 'Liens', 'Action'
    ]]

def main():
    """Main function to run the Streamlit page."""
    st.set_page_config(layout="wide")
    st.title("Synthèse Contacts : Le Control Center 🚀")
    st.markdown("Identifiez, triez et gérez tous vos contacts de manière visuelle et interactive.")

    df_contacts = get_all_contacts_with_compte()

    if df_contacts.empty:
        st.info(
            "Aucun contact à afficher. "
            "Veuillez vérifier la connexion à la base de données ou ajouter des contacts."
        )
        return

    search_query, selected_compte, selected_status = display_filters(df_contacts)
    filtered_df = apply_filters(df_contacts, search_query, selected_compte, selected_status)
    display_df = format_dataframe_for_display(filtered_df)

    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
