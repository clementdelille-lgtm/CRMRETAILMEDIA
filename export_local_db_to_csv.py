# export_local_db_to_csv.py
import pandas as pd
import sqlalchemy
import os

# --- CONFIGURATION ---
DB_FILE = "prospection.db"

def get_local_sqlite_connection():
    """Crée et retourne une connexion à la base de données SQLite locale."""
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(f"Le fichier de base de données '{DB_FILE}' est introuvable.")
    
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_FILE}")
    return engine.connect()

def export_tables_to_csv():
    """Exporte les tables 'comptes' et 'contacts' du fichier local en CSV."""
    print(f"Tentative de connexion au fichier local '{DB_FILE}'...")
    try:
        with get_local_sqlite_connection() as con:
            print("✅ Connexion réussie.")
            
            # --- Exporter la table 'comptes' ---
            print("Exportation de la table 'comptes'...")
            df_comptes = pd.read_sql("SELECT * FROM comptes", con)
            # La fonction to_csv inclut les en-têtes par défaut (header=True)
            df_comptes.to_csv("comptes_export.csv", index=False, encoding='utf-8-sig')
            print(f"-> Fichier 'comptes_export.csv' créé avec {len(df_comptes)} lignes.")

            # --- Exporter la table 'contacts' ---
            print("\nExportation de la table 'contacts'...")
            df_contacts = pd.read_sql("SELECT * FROM contacts", con)
            # La fonction to_csv inclut les en-têtes par défaut (header=True)
            df_contacts.to_csv("contacts_export.csv", index=False, encoding='utf-8-sig')
            print(f"-> Fichier 'contacts_export.csv' créé avec {len(df_contacts)} lignes.")
            
            print("\n🎉 Exportation terminée avec succès !")

    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")

if __name__ == "__main__":
    export_tables_to_csv()