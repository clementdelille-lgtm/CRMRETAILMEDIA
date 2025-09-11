# setup_database.py
import sqlite3

DB_FILE = "prospection.db"

def setup():
    """Crée ou met à jour les tables de la base de données."""
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    # --- Table 'comptes' ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comptes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            statut TEXT,
            notes TEXT
        )
    """)
    # Ajout des colonnes à 'comptes'
    try:
        cur.execute("ALTER TABLE comptes ADD COLUMN lien_hubspot TEXT")
    except sqlite3.OperationalError:
        pass # La colonne existe déjà
    try:
        cur.execute("ALTER TABLE comptes ADD COLUMN client_converteo TEXT") # O/N
    except sqlite3.OperationalError:
        pass # La colonne existe déjà
    print("Table 'comptes' configurée.")

    # --- Table 'contacts' ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prenom TEXT, nom TEXT, role TEXT,
            contact_envoye TEXT, contact_accepte TEXT,
            prospection TEXT, retour TEXT,
            next_steps TEXT, person_interest TEXT,
            compte_id INTEGER,
            FOREIGN KEY (compte_id) REFERENCES comptes (id)
        )
    """)
    # Ajout des colonnes à 'contacts'
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN linkedin TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN derniere_action TEXT")
    except sqlite3.OperationalError:
        pass
    print("Table 'contacts' configurée.")

# Ajout des nouveaux champs pour la Feature 1
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN date_prochaine_action DATE")
    except sqlite3.OperationalError: pass
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN prochaine_action_notes TEXT")
    except sqlite3.OperationalError: pass
    print("Table 'contacts' configurée.")

    # --- NOUVELLE TABLE 'interactions' pour la Feature 3 ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            date_interaction DATE NOT NULL,
            type_interaction TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    """)
    print("Table 'interactions' configurée.")


    con.commit()
    con.close()
    print("Base de données mise à jour avec succès.")

if __name__ == "__main__":
    setup()