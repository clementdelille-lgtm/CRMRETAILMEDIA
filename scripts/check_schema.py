# check_schema.py
import sqlite3

DB_FILE = "../data/prospection.db"
print(f"--- Vérification du schéma de '{DB_FILE}' ---")
try:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    
    print("\nColonnes de la table 'comptes':")
    cur.execute("PRAGMA table_info(comptes);")
    for col in cur.fetchall():
        print(f"- {col[1]} ({col[2]})")

    print("\nColonnes de la table 'contacts':")
    cur.execute("PRAGMA table_info(contacts);")
    for col in cur.fetchall():
        print(f"- {col[1]} ({col[2]})")
        
    con.close()
except Exception as e:
    print(f"Une erreur est survenue : {e}")