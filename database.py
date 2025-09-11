# database.py (extraits des fonctions modifiées)
import sqlite3
import pandas as pd

DB_FILE = "prospection.db"

def get_db_connection():
    return sqlite3.connect(DB_FILE)

# --- Fonctions pour les Comptes ---
def get_compte_details(compte_id):
    with get_db_connection() as con:
        # Assure-toi que la requête peut gérer les colonnes qui n'existent pas encore partout
        return pd.read_sql(f"SELECT * FROM comptes WHERE id = {compte_id}", con).iloc[0]

def update_compte(compte_id, nom, statut, notes, lien_hubspot, client_converteo):
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE comptes 
            SET nom=?, statut=?, notes=?, lien_hubspot=?, client_converteo=? 
            WHERE id=?
        """, (nom, statut, notes, lien_hubspot, client_converteo, compte_id))
        con.commit()

def add_compte(nom, statut, notes, lien_hubspot, client_converteo):
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO comptes (nom, statut, notes, lien_hubspot, client_converteo) 
            VALUES (?, ?, ?, ?, ?)
        """, (nom, statut, notes, lien_hubspot, client_converteo))
        con.commit()

# --- Fonctions pour les Contacts ---
def get_contact_details(contact_id):
    with get_db_connection() as con:
        return pd.read_sql(f"SELECT * FROM contacts WHERE id = {contact_id}", con).iloc[0]

def add_contact(prenom, nom, role, email, linkedin, derniere_action, compte_id):
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO contacts (prenom, nom, role, email, linkedin, derniere_action, compte_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (prenom, nom, role, email, linkedin, derniere_action, compte_id))
        con.commit()

def update_contact(contact_id, prenom, nom, role, email, linkedin, derniere_action):
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE contacts 
            SET prenom=?, nom=?, role=?, email=?, linkedin=?, derniere_action=? 
            WHERE id=?
        """, (prenom, nom, role, email, linkedin, derniere_action, contact_id))
        con.commit()

# --- Le reste des fonctions (get_all_comptes, get_contacts_for_compte, etc.) reste identique ---
# (Assurez-vous que les fonctions non modifiées sont toujours dans votre fichier)
def get_all_comptes():
    with get_db_connection() as con:
        return pd.read_sql("SELECT id, nom FROM comptes ORDER BY nom", con)

def get_contacts_for_compte(compte_id):
    with get_db_connection() as con:
        return pd.read_sql(f"SELECT id, prenom, nom, role, email FROM contacts WHERE compte_id = {compte_id} ORDER BY nom", con)

def get_stats():
    with get_db_connection() as con:
        total_comptes = pd.read_sql("SELECT COUNT(*) FROM comptes", con).iloc[0, 0]
        total_contacts = pd.read_sql("SELECT COUNT(*) FROM contacts", con).iloc[0, 0]
    return {"total_comptes": total_comptes, "total_contacts": total_contacts}

# --- Fonctions pour les Contacts (MISES À JOUR) ---

def update_contact(contact_id, prenom, nom, role, email, linkedin, derniere_action, date_prochaine_action, prochaine_action_notes):
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE contacts 
            SET prenom=?, nom=?, role=?, email=?, linkedin=?, derniere_action=?,
                date_prochaine_action=?, prochaine_action_notes=?
            WHERE id=?
        """, (prenom, nom, role, email, linkedin, derniere_action, date_prochaine_action, prochaine_action_notes, contact_id))
        con.commit()

# --- Fonctions pour le Dashboard (NOUVELLE) ---
def get_actions_a_mener(date_limite):
    query = """
        SELECT
            c.prenom, c.nom, co.nom as compte,
            c.prochaine_action_notes, c.date_prochaine_action
        FROM contacts c
        JOIN comptes co ON c.compte_id = co.id
        WHERE c.date_prochaine_action <= ?
        ORDER BY c.date_prochaine_action ASC
    """
    with get_db_connection() as con:
        df = pd.read_sql(query, con, params=(date_limite,))
    return df

# --- Fonctions pour les Interactions (NOUVELLES) ---
def add_interaction(contact_id, date_interaction, type_interaction, notes):
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO interactions (contact_id, date_interaction, type_interaction, notes)
            VALUES (?, ?, ?, ?)
        """, (contact_id, date_interaction, type_interaction, notes))
        con.commit()

def get_interactions_for_contact(contact_id):
    query = """
        SELECT date_interaction, type_interaction, notes 
        FROM interactions 
        WHERE contact_id = ? 
        ORDER BY date_interaction DESC
    """
    with get_db_connection() as con:
        df = pd.read_sql(query, con, params=(contact_id,))
    return df

# --- NOUVELLE Fonction pour la vue Funnel ---
def get_funnel_data():
    """Compte le nombre de comptes pour chaque statut pour le graphique funnel."""
    query = """
        SELECT statut, COUNT(id) as count
        FROM comptes
        GROUP BY statut
    """
    with get_db_connection() as con:
        df = pd.read_sql(query, con)
    return df


# --- NOUVELLES Fonctions pour la page de statistiques ---
# (À AJOUTER À LA FIN DE VOTRE FICHIER DATABASE.PY)

def get_interaction_counts_by_type():
    """Compte le nombre d'interactions pour chaque type."""
    query = "SELECT type_interaction, COUNT(id) as count FROM interactions GROUP BY type_interaction"
    with get_db_connection() as con:
        df = pd.read_sql(query, con)
    return df

def get_interactions_over_time():
    """Récupère toutes les interactions avec leur date."""
    query = "SELECT date_interaction FROM interactions"
    with get_db_connection() as con:
        df = pd.read_sql(query, con)
    return df