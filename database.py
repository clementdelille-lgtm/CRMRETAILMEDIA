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
    with get_db_connection() as con:
        return pd.read_sql("SELECT id, nom FROM comptes ORDER BY nom", con)

def get_compte_details(compte_id):
    query = sqlalchemy.text("SELECT * FROM comptes WHERE id = :id")
    with get_db_connection() as con:
        return pd.read_sql(query, con, params={"id": compte_id}).iloc[0]

def get_contacts_for_compte(compte_id):
    query = sqlalchemy.text("SELECT id, prenom, nom, role, email FROM contacts WHERE compte_id = :id ORDER BY nom")
    with get_db_connection() as con:
        # Correction : on utilise 'compte_id', la variable reçue par la fonction
        return pd.read_sql(query, con, params={"id": compte_id})

def get_contact_details(contact_id):
    query = sqlalchemy.text("SELECT * FROM contacts WHERE id = :id")
    with get_db_connection() as con:
        return pd.read_sql(query, con, params={"id": contact_id}).iloc[0]

def get_stats():
    with get_db_connection() as con:
        total_comptes = pd.read_sql("SELECT COUNT(*) FROM comptes", con).iloc[0, 0]
        total_contacts = pd.read_sql("SELECT COUNT(*) FROM contacts", con).iloc[0, 0]
    return {"total_comptes": total_comptes, "total_contacts": total_contacts}

def get_actions_a_mener(date_limite):
    query = sqlalchemy.text("SELECT c.prenom, c.nom, co.nom as compte, c.prochaine_action_notes, c.date_prochaine_action FROM contacts c JOIN comptes co ON c.compte_id = co.id WHERE c.date_prochaine_action <= :limit ORDER BY c.date_prochaine_action ASC")
    with get_db_connection() as con:
        return pd.read_sql(query, con, params={"limit": date_limite})

def get_funnel_data():
    with get_db_connection() as con:
        return pd.read_sql("SELECT statut, COUNT(id) as count FROM comptes GROUP BY statut", con)

def get_interactions_for_contact(contact_id):
    query = sqlalchemy.text("SELECT date_interaction, type_interaction, notes FROM interactions WHERE contact_id = :id ORDER BY date_interaction DESC")
    with get_db_connection() as con:
        return pd.read_sql(query, con, params={"id": contact_id})

def get_interaction_counts_by_type():
    with get_db_connection() as con:
        return pd.read_sql("SELECT type_interaction, COUNT(id) as count FROM interactions GROUP BY type_interaction", con)

def get_interactions_over_time():
    with get_db_connection() as con:
        return pd.read_sql("SELECT date_interaction FROM interactions", con)

def count_contacts_for_compte(compte_id):
    with get_db_connection() as con:
        result = con.execute(sqlalchemy.text("SELECT COUNT(id) FROM contacts WHERE compte_id = :id"), {"id": compte_id})
        return result.scalar_one()

# --- Fonctions d'Écriture (INSERT, UPDATE, DELETE) ---

def add_compte(nom, statut, notes, lien_hubspot, client_converteo):
    """Ajoute un compte et retourne son ID."""
    with get_db_connection() as con:
        result = con.execute(sqlalchemy.text("""
            INSERT INTO comptes (nom, statut, notes, lien_hubspot, client_converteo) 
            VALUES (:nom, :statut, :notes, :lien_hubspot, :client_converteo)
            RETURNING id
        """), {"nom": nom, "statut": statut, "notes": notes, "lien_hubspot": lien_hubspot, "client_converteo": client_converteo})
        new_id = result.scalar_one()
        con.commit()
        return new_id

def update_compte(compte_id, nom, statut, notes, lien_hubspot, client_converteo):
    with get_db_connection() as con:
        con.execute(sqlalchemy.text("""
            UPDATE comptes 
            SET nom=:nom, statut=:statut, notes=:notes, lien_hubspot=:lien_hubspot, client_converteo=:client_converteo 
            WHERE id=:id
        """), {"nom": nom, "statut": statut, "notes": notes, "lien_hubspot": lien_hubspot, "client_converteo": client_converteo, "id": compte_id})
        con.commit()

def delete_compte(compte_id):
    with get_db_connection() as con:
        con.execute(sqlalchemy.text("DELETE FROM comptes WHERE id = :id"), {"id": compte_id})
        con.commit()

def add_contact(prenom, nom, role, email, linkedin, derniere_action, compte_id):
    with get_db_connection() as con:
        con.execute(sqlalchemy.text("""
            INSERT INTO contacts (prenom, nom, role, email, linkedin, derniere_action, compte_id) 
            VALUES (:prenom, :nom, :role, :email, :linkedin, :derniere_action, :compte_id)
        """), {"prenom": prenom, "nom": nom, "role": role, "email": email, "linkedin": linkedin, "derniere_action": derniere_action, "compte_id": compte_id})
        con.commit()

def update_contact(contact_id, prenom, nom, role, email, linkedin, derniere_action, date_prochaine_action, prochaine_action_notes):
    with get_db_connection() as con:
        con.execute(sqlalchemy.text("""
            UPDATE contacts 
            SET prenom=:prenom, nom=:nom, role=:role, email=:email, linkedin=:linkedin, 
                derniere_action=:derniere_action, date_prochaine_action=:date_prochaine_action, 
                prochaine_action_notes=:prochaine_action_notes
            WHERE id=:id
        """), {
            "prenom": prenom, "nom": nom, "role": role, "email": email, "linkedin": linkedin,
            "derniere_action": derniere_action, "date_prochaine_action": date_prochaine_action,
            "prochaine_action_notes": prochaine_action_notes, "id": contact_id
        })
        con.commit()

def delete_contact(contact_id):
    with get_db_connection() as con:
        con.execute(sqlalchemy.text("DELETE FROM contacts WHERE id = :id"), {"id": contact_id})
        con.commit()

def add_interaction(contact_id, date_interaction, type_interaction, notes):
    with get_db_connection() as con:
        con.execute(sqlalchemy.text("""
            INSERT INTO interactions (contact_id, date_interaction, type_interaction, notes)
            VALUES (:contact_id, :date_interaction, :type_interaction, :notes)
        """), {"contact_id": contact_id, "date_interaction": date_interaction, "type_interaction": type_interaction, "notes": notes})
        con.commit()