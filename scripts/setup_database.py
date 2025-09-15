# setup_database.py
import sqlite3

DB_FILE = "../data/prospection.db"

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
    try:
        cur.execute("ALTER TABLE comptes ADD COLUMN lien_hubspot TEXT")
    except sqlite3.OperationalError: pass
    try:
        cur.execute("ALTER TABLE comptes ADD COLUMN client_converteo TEXT")
    except sqlite3.OperationalError: pass
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
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN email TEXT")
    except sqlite3.OperationalError: pass
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN linkedin TEXT")
    except sqlite3.OperationalError: pass
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN derniere_action TEXT")
    except sqlite3.OperationalError: pass
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN date_prochaine_action DATE")
    except sqlite3.OperationalError: pass
    try:
        cur.execute("ALTER TABLE contacts ADD COLUMN prochaine_action_notes TEXT")
    except sqlite3.OperationalError: pass
    print("Table 'contacts' configurée.")

    # --- Table 'interactions' ---
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

    # --- NOUVELLES TABLES POUR LE SYSTÈME DE TAGS (Feature 1) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            couleur TEXT DEFAULT '#4e8ec6'
        )
    """)
    print("Table 'tags' configurée.")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contact_tags (
            contact_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (contact_id, tag_id),
            FOREIGN KEY (contact_id) REFERENCES contacts (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
        )
    """)
    print("Table 'contact_tags' configurée.")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS compte_tags (
            compte_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (compte_id, tag_id),
            FOREIGN KEY (compte_id) REFERENCES comptes (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
        )
    """)
    print("Table 'compte_tags' configurée.")


    con.commit()
    con.close()
    print("Base de données mise à jour avec succès.")

if __name__ == "__main__":
    setup()
