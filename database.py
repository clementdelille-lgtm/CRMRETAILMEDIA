# database.py
import streamlit as st
import pandas as pd
import sqlalchemy
import os

def get_db_connection():
    """Crée et retourne une connexion à la base de données Supabase."""
    try:
        connection_string = st.secrets["SUPABASE_CONNECTION_STRING"]
        engine = sqlalchemy.create_engine(connection_string)
        return engine.connect()
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return None

# --- Fonctions de Lecture (SELECT) ---

def get_all_comptes():
    con = get_db_connection()
    if con:
        return pd.read_sql("SELECT id, nom FROM comptes ORDER BY nom", con)
    return pd.DataFrame()

def get_compte_details(compte_id):
    con = get_db_connection()
    if con:
        query = sqlalchemy.text("SELECT * FROM comptes WHERE id = :id")
        return pd.read_sql(query, con, params={"id": compte_id}).iloc[0]
    return pd.Series()

def get_contacts_for_compte(compte_id):
    con = get_db_connection()
    if con:
        query = sqlalchemy.text("SELECT id, prenom, nom, role, email, statut_prospection FROM contacts WHERE compte_id = :id ORDER BY nom")
        return pd.read_sql(query, con, params={"id": compte_id})
    return pd.DataFrame()

def get_contact_details(contact_id):
    con = get_db_connection()
    if con:
        query = sqlalchemy.text("SELECT * FROM contacts WHERE id = :id")
        return pd.read_sql(query, con, params={"id": contact_id}).iloc[0]
    return pd.Series()

def get_stats():
    con = get_db_connection()
    if con:
        total_comptes = pd.read_sql("SELECT COUNT(*) FROM comptes", con).iloc[0, 0]
        total_contacts = pd.read_sql("SELECT COUNT(*) FROM contacts", con).iloc[0, 0]
        return {"total_comptes": total_comptes, "total_contacts": total_contacts}
    return {"total_comptes": 0, "total_contacts": 0}

def get_actions_a_mener(date_limite):
    con = get_db_connection()
    if con:
        query = sqlalchemy.text("SELECT c.prenom, c.nom, co.nom as compte, c.prochaine_action_notes, c.date_prochaine_action FROM contacts c JOIN comptes co ON c.compte_id = co.id WHERE c.date_prochaine_action <= :limit ORDER BY c.date_prochaine_action ASC")
        return pd.read_sql(query, con, params={"limit": date_limite})
    return pd.DataFrame()

def get_funnel_data():
    con = get_db_connection()
    if con:
        return pd.read_sql("SELECT statut, COUNT(id) as count FROM comptes GROUP BY statut", con)
    return pd.DataFrame()

def get_interactions_for_contact(contact_id):
    con = get_db_connection()
    if con:
        query = sqlalchemy.text("SELECT date_interaction, type_interaction, notes FROM interactions WHERE contact_id = :id ORDER BY date_interaction DESC")
        return pd.read_sql(query, con, params={"id": contact_id})
    return pd.DataFrame()

def get_interaction_counts_by_type():
    con = get_db_connection()
    if con:
        return pd.read_sql("SELECT type_interaction, COUNT(id) as count FROM interactions GROUP BY type_interaction", con)
    return pd.DataFrame()

def get_interactions_over_time():
    con = get_db_connection()
    if con:
        return pd.read_sql("SELECT date_interaction FROM interactions", con)
    return pd.DataFrame()

def count_contacts_for_compte(compte_id):
    con = get_db_connection()
    if con:
        result = con.execute(sqlalchemy.text("SELECT COUNT(id) FROM contacts WHERE compte_id = :id"), {"id": compte_id})
        return result.scalar_one()
    return 0

# --- Fonctions d'Écriture (INSERT, UPDATE, DELETE) ---

def add_compte(nom, statut, notes, lien_hubspot, client_converteo):
    con = get_db_connection()
    if con:
        result = con.execute(sqlalchemy.text("""
            INSERT INTO comptes (nom, statut, notes, lien_hubspot, client_converteo) 
            VALUES (:nom, :statut, :notes, :lien_hubspot, :client_converteo)
            RETURNING id
        """), {"nom": nom, "statut": statut, "notes": notes, "lien_hubspot": lien_hubspot, "client_converteo": client_converteo})
        new_id = result.scalar_one()
        con.commit()
        return new_id
    return None

# J'ai ajouté 'statut_prospection' dans cette fonction
def add_contact(prenom, nom, role, email, linkedin, statut_prospection, derniere_action, compte_id):
    con = get_db_connection()
    if con:
        con.execute(sqlalchemy.text("""
            INSERT INTO contacts (prenom, nom, role, email, linkedin, statut_prospection, derniere_action, compte_id) 
            VALUES (:prenom, :nom, :role, :email, :linkedin, :statut_prospection, :derniere_action, :compte_id)
        """), {"prenom": prenom, "nom": nom, "role": role, "email": email, "linkedin": linkedin, "statut_prospection": statut_prospection, "derniere_action": derniere_action, "compte_id": compte_id})
        con.commit()

def update_compte(compte_id, nom, statut, notes, lien_hubspot, client_converteo):
    con = get_db_connection()
    if con:
        con.execute(sqlalchemy.text("""
            UPDATE comptes 
            SET nom=:nom, statut=:statut, notes=:notes, lien_hubspot=:lien_hubspot, client_converteo=:client_converteo 
            WHERE id=:id
        """), {"nom": nom, "statut": statut, "notes": notes, "lien_hubspot": lien_hubspot, "client_converteo": client_converteo, "id": compte_id})
        con.commit()

# J'ai ajouté 'statut_prospection' dans cette fonction
def update_contact(contact_id, prenom, nom, role, email, linkedin, derniere_action, date_prochaine_action, prochaine_action_notes, statut_prospection):
    con = get_db_connection()
    if con:
        con.execute(sqlalchemy.text("""
            UPDATE contacts 
            SET prenom=:prenom, nom=:nom, role=:role, email=:email, linkedin=:linkedin, 
                derniere_action=:derniere_action, date_prochaine_action=:date_prochaine_action, 
                prochaine_action_notes=:prochaine_action_notes, statut_prospection=:statut_prospection
            WHERE id=:id
        """), {
            "prenom": prenom, "nom": nom, "role": role, "email": email, "linkedin": linkedin,
            "derniere_action": derniere_action, "date_prochaine_action": date_prochaine_action,
            "prochaine_action_notes": prochaine_action_notes, "statut_prospection": statut_prospection, "id": contact_id
        })
        con.commit()

def delete_compte(compte_id):
    con = get_db_connection()
    if con:
        con.execute(sqlalchemy.text("DELETE FROM comptes WHERE id = :id"), {"id": compte_id})
        con.commit()

def delete_contact(contact_id):
    con = get_db_connection()
    if con:
        con.execute(sqlalchemy.text("DELETE FROM contacts WHERE id = :id"), {"id": contact_id})
        con.commit()

def add_interaction(contact_id, date_interaction, type_interaction, notes):
    """
    Ajoute une nouvelle interaction et met à jour la date de la dernière
    interaction sur la fiche du contact.
    """
    con = get_db_connection()
    if con:
        # 1. Ajoute la nouvelle interaction dans la table 'interactions'
        con.execute(sqlalchemy.text("""
            INSERT INTO interactions (contact_id, date_interaction, type_interaction, notes)
            VALUES (:contact_id, :date_interaction, :type_interaction, :notes)
        """), {"contact_id": contact_id, "date_interaction": date_interaction, "type_interaction": type_interaction, "notes": notes})

        # 2. Met à jour la date de dernière interaction sur le contact
        con.execute(sqlalchemy.text("""
            UPDATE contacts
            SET date_derniere_interaction = :date_interaction
            WHERE id = :contact_id
        """), {"date_interaction": date_interaction, "contact_id": contact_id})
        
        con.commit()

def get_contact_for_ai(contact_id):
    """Récupère les détails d'un contact et le nom du compte pour l'assistant IA."""
    con = get_db_connection()
    if con:
        query = sqlalchemy.text("""
            SELECT
                c.prenom,
                c.nom,
                c.role,
                c.derniere_action,
                c.date_derniere_interaction,
                c.prochaine_action_notes,
                c.date_prochaine_action,
                co.nom AS nom_compte
            FROM
                contacts c
            JOIN
                comptes co ON c.compte_id = co.id
            WHERE
                c.id = :id
        """)
        return pd.read_sql(query, con, params={"id": contact_id}).iloc[0]
    return pd.Series()

def get_contacts_with_compte():
    """
    Retrieves all contacts along with their associated company name.
    """
    con = get_db_connection()
    if con:
        query = """
            SELECT
                c.id,
                c.prenom,
                c.nom,
                co.nom AS compte_nom
            FROM
                contacts c
            JOIN
                comptes co ON c.compte_id = co.id
            ORDER BY
                c.nom, c.prenom
        """
        df = pd.read_sql(query, con)
        con.close()
        return df
    return pd.DataFrame()