'''
This module handles all database interactions for the CRM application,
including connection management and CRUD operations for all tables.
'''

import streamlit as st
import pandas as pd
import sqlalchemy


# --- Database Connection Management ---

@st.cache_resource
def get_db_engine():
    """Creates and returns a SQLAlchemy engine using a cached connection string."""
    try:
        connection_string = st.secrets["SUPABASE_CONNECTION_STRING"]
        return sqlalchemy.create_engine(connection_string)
    except KeyError:
        st.error("Connection string not found in Streamlit secrets.")
        return None

def execute_query(query, params=None, is_read=True):
    """Executes a SQL query and returns the result, handling errors."""
    engine = get_db_engine()
    if not engine:
        return pd.DataFrame() if is_read else False

    try:
        with engine.connect() as connection:
            if is_read:
                return pd.read_sql(sqlalchemy.text(query), connection, params=params)

            with connection.begin() as transaction:
                result = connection.execute(sqlalchemy.text(query), params)
                transaction.commit()
                if result.returns_rows:
                    return result.scalar_one_or_none()
                return True
    except sqlalchemy.exc.SQLAlchemyError as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame() if is_read else False

# --- Account (Comptes) Operations ---

def get_all_comptes():
    """Fetches all accounts, ordered by name."""
    return execute_query("SELECT id, nom FROM comptes ORDER BY nom")

def get_compte_details(compte_id):
    """Fetches detailed information for a single account."""
    df = execute_query("SELECT * FROM comptes WHERE id = :id", {"id": compte_id})
    return df.iloc[0] if not df.empty else pd.Series()

def add_compte(**kwargs):
    """Adds a new account to the database."""
    columns = ", ".join(kwargs)
    placeholders = ", ".join(f":{key}" for key in kwargs)
    query = f"INSERT INTO comptes ({columns}) VALUES ({placeholders}) RETURNING id"
    return execute_query(query, kwargs, is_read=False)

def update_compte(compte_id, **kwargs):
    """Updates an existing account."""
    set_clauses = ", ".join(f"{key}=:{key}" for key in kwargs)
    query = f"UPDATE comptes SET {set_clauses} WHERE id = :compte_id"
    kwargs['compte_id'] = compte_id
    return execute_query(query, kwargs, is_read=False)

def delete_compte(compte_id):
    """Deletes an account and its related contacts."""
    engine = get_db_engine()
    if not engine:
        return False
    try:
        with engine.begin() as connection:
            connection.execute(
                sqlalchemy.text("DELETE FROM contacts WHERE compte_id = :id"),
                {"id": compte_id}
            )
            connection.execute(
                sqlalchemy.text("DELETE FROM comptes WHERE id = :id"),
                {"id": compte_id}
            )
        return True
    except sqlalchemy.exc.SQLAlchemyError as e:
        st.error(f"Error deleting account: {e}")
        return False

# --- Contact Operations ---

def get_contacts_for_compte(compte_id):
    """Fetches all contacts for a given account."""
    query = """
        SELECT id, prenom, nom, role, email, statut_prospection 
        FROM contacts WHERE compte_id = :id ORDER BY nom
    """
    return execute_query(query, {"id": compte_id})

def get_contact_details(contact_id):
    """Fetches detailed information for a single contact."""
    df = execute_query("SELECT * FROM contacts WHERE id = :id", {"id": contact_id})
    return df.iloc[0] if not df.empty else pd.Series()

def add_contact(**kwargs):
    """Adds a new contact."""
    columns = ", ".join(kwargs)
    placeholders = ", ".join(f":{key}" for key in kwargs)
    query = f"INSERT INTO contacts ({columns}) VALUES ({placeholders}) RETURNING id"
    return execute_query(query, kwargs, is_read=False)

def update_contact(contact_id, **kwargs):
    """Updates an existing contact."""
    set_clauses = ", ".join(f"{key}=:{key}" for key in kwargs)
    query = f"UPDATE contacts SET {set_clauses} WHERE id = :contact_id"
    kwargs['contact_id'] = contact_id
    return execute_query(query, kwargs, is_read=False)

def delete_contact(contact_id):
    """Deletes a contact."""
    query = "DELETE FROM contacts WHERE id = :id"
    return execute_query(query, {"id": contact_id}, is_read=False)

# --- Interaction Operations ---

def get_interactions_for_contact(contact_id):
    """Fetches all interactions for a given contact."""
    query = """
        SELECT date_interaction, type_interaction, notes 
        FROM interactions WHERE contact_id = :id ORDER BY date_interaction DESC
    """
    return execute_query(query, {"id": contact_id})

def add_interaction(contact_id, date_interaction, type_interaction, notes):
    """Adds a new interaction and updates the contact's last interaction date."""
    engine = get_db_engine()
    if not engine:
        return False
    try:
        with engine.begin() as connection:
            interaction_query = """
                INSERT INTO interactions 
                (contact_id, date_interaction, type_interaction, notes)
                VALUES (:cid, :date_inter, :type_inter, :notes)
            """
            connection.execute(sqlalchemy.text(interaction_query), {
                "cid": contact_id, "date_inter": date_interaction, 
                "type_inter": type_interaction, "notes": notes
            })
            
            update_contact_query = """
                UPDATE contacts SET date_derniere_interaction = :date_inter 
                WHERE id = :cid
            """
            connection.execute(sqlalchemy.text(update_contact_query), {
                "date_inter": date_interaction, "cid": contact_id
            })
        return True
    except sqlalchemy.exc.SQLAlchemyError as e:
        st.error(f"Error adding interaction: {e}")
        return False

# --- Tag Operations ---

def get_all_tags():
    """Fetches all tags."""
    return execute_query("SELECT id, nom, couleur FROM tags ORDER BY nom")

def add_tag(nom, couleur):
    """Adds a new tag."""
    try:
        query = "INSERT INTO tags (nom, couleur) VALUES (:nom, :couleur)"
        params = {"nom": nom, "couleur": couleur}
        return execute_query(query, params, is_read=False)
    except sqlalchemy.exc.IntegrityError:
        st.warning(f"Le tag '{nom}' existe déjà.")
        return False

def update_tag(tag_id, nom, couleur):
    """Updates a tag."""
    query = "UPDATE tags SET nom = :nom, couleur = :couleur WHERE id = :id"
    params = {"id": tag_id, "nom": nom, "couleur": couleur}
    return execute_query(query, params, is_read=False)

def delete_tag(tag_id):
    """Deletes a tag."""
    return execute_query("DELETE FROM tags WHERE id = :id", {"id": tag_id}, is_read=False)

def get_tags_for_entity(entity_id, entity_type):
    """Fetches tags for a contact or an account."""
    table = f"{entity_type}_tags"
    col = f"{entity_type}_id"
    query = f"""
        SELECT t.id, t.nom, t.couleur FROM tags t
        JOIN {table} ct ON t.id = ct.tag_id WHERE ct.{col} = :entity_id
    """
    return execute_query(query, {"entity_id": entity_id})

def update_tags_for_entity(entity_id, tag_ids, entity_type):
    """Updates the tags associated with a contact or an account."""
    table = f"{entity_type}_tags"
    col = f"{entity_type}_id"

    engine = get_db_engine()
    if not engine:
        return

    try:
        with engine.begin() as connection:
            del_query = f"DELETE FROM {table} WHERE {col} = :id"
            connection.execute(sqlalchemy.text(del_query), {"id": entity_id})
            if tag_ids:
                ins_query = f"INSERT INTO {table} ({col}, tag_id) VALUES (:id, :tag_id)"
                params = [{"id": entity_id, "tag_id": tag_id} for tag_id in tag_ids]
                connection.execute(sqlalchemy.text(ins_query), params)
    except sqlalchemy.exc.SQLAlchemyError as e:
        st.error(f"Error updating tags: {e}")


# --- Statistics and Reporting ---

def get_dashboard_stats():
    """Fetches key performance indicators for the main dashboard."""
    total_comptes = execute_query("SELECT COUNT(*) FROM comptes").iloc[0, 0]
    total_contacts = execute_query("SELECT COUNT(*) FROM contacts").iloc[0, 0]
    return {"total_comptes": total_comptes, "total_contacts": total_contacts}

def get_actions_a_mener(date_limite):
    """Fetches contacts with upcoming actions."""
    query = """
        SELECT c.prenom, c.nom, co.nom as compte, 
               c.prochaine_action_notes, c.date_prochaine_action
        FROM contacts c JOIN comptes co ON c.compte_id = co.id 
        WHERE c.date_prochaine_action <= :limit 
        ORDER BY c.date_prochaine_action ASC
    """
    return execute_query(query, {"limit": date_limite})

def get_funnel_data():
    """Fetches data for the sales funnel chart."""
    query = "SELECT statut, COUNT(id) as count FROM comptes GROUP BY statut"
    return execute_query(query)

def get_interaction_counts_by_type():
    """Fetches interaction counts grouped by type."""
    query = """
        SELECT type_interaction, COUNT(id) as count 
        FROM interactions GROUP BY type_interaction
    """
    return execute_query(query)

def get_interactions_over_time():
    """Fetches timestamps of all interactions for trend analysis."""
    return execute_query("SELECT date_interaction FROM interactions")

def get_contacts_with_compte():
    """Fetches a list of contacts with their associated company name."""
    return execute_query("""
        SELECT c.id, c.prenom, c.nom, co.nom AS compte_nom
        FROM contacts c JOIN comptes co ON c.compte_id = co.id
        ORDER BY c.nom, c.prenom
    """)

def get_contact_summary_for_ai(contact_id):
    """Fetches a summary of a contact's current status for AI analysis."""
    query = """
        SELECT c.prenom, c.nom, c.role, c.derniere_action, 
               c.date_derniere_interaction, c.prochaine_action_notes, 
               c.date_prochaine_action, co.nom AS nom_compte
        FROM contacts c JOIN comptes co ON c.compte_id = co.id
        WHERE c.id = :id
    """
    df = execute_query(query, {"id": contact_id})
    return df.iloc[0] if not df.empty else pd.Series()
